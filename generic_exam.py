"""通用辨識考試：拿使用者框好的段落考 YOLO-World，決定一個名稱能不能不訓練、直接用通用辨識。

上線後不接語言模型，所以「用不用通用辨識、提示詞與門檻多少」全部照這裡的固定規則決定，同一份資料跑幾次結果都一樣：
- 提示詞不翻譯：固定的英文候選清單（VOCAB）每個名稱都全部試，用分數挑。
- 一個候選＝提示詞 × 最低信心 × 最小面積（佔桌面範圍的比例，不用像素，換相機距離也通用）。
- 有框的格子（正例）：要在使用者框的位置找到（IoU ≥ IOU_HIT）；東西不在的格子（反例）：桌面範圍內要什麼都找不到。
- 前面的段落拿來挑、最後一段留著驗收（候選多了總有一個湊巧考得好，換一段再考才可靠）。
- 單獨考不過的，再試「疊在另一個已經考過的名稱上」（例如鞋子要疊在盒子上才算「鞋子在盒上」）。
- 資料不夠、或驗收沒過，一律保守用自己訓練的模型。
所有矩形都是畫面座標 [x, y, w, h]。
"""
from __future__ import annotations

from dataclasses import dataclass, field

VOCAB = ["box", "blue box", "cardboard box", "shoe box", "carton", "lid",
         "shoe", "sneaker", "footwear",
         "sticker", "label", "barcode label", "white label", "tag", "paper", "tissue paper"]
CONF_GRID = (0.05, 0.1, 0.15, 0.2, 0.25, 0.3, 0.4, 0.5)
AREA_GRID = (0.0, 0.005, 0.01, 0.02, 0.04, 0.08)
IOU_HIT = 0.5            # 正例：找到的框跟使用者的框 IoU 要到這麼多才算找到
ON_TOP_MIN = 0.5         # 關係「疊在上面」：這個框至少一半面積落在另一個東西的框裡
PASS_HIT = 0.90          # 驗收：找到率門檻
PASS_FP = 0.05           # 驗收：誤報率上限
MIN_SEGMENTS = 3         # 少於這麼多段不判斷
MIN_VERIFY_POS = 10      # 驗收段至少要有這麼多張正例
MIN_VERIFY_NEG = 20      # 驗收至少要有這麼多張反例


@dataclass(frozen=True)
class Det:
    prompt: str
    conf: float
    rect: tuple            # [x, y, w, h]


@dataclass
class Example:
    frame: int
    positive: bool
    verify: bool                       # True＝驗收用；False＝挑選用
    rect: tuple | None = None          # 正例：使用者框的位置


@dataclass(frozen=True)
class Candidate:
    prompt: str
    conf: float
    area: float                        # 最小面積，佔桌面範圍的比例
    on: str | None = None              # 關係：要疊在哪個名稱上
    on_cand: "Candidate | None" = None  # 那個名稱考過的設定

    def text(self) -> str:
        s = f"「{self.prompt}」信心 ≥ {self.conf:g}、面積 ≥ 桌面 {self.area * 100:g}%"
        return s + (f"，而且要疊在「{self.on}」上" if self.on else "")

    def to_dict(self) -> dict:
        d = {"prompt": self.prompt, "conf": self.conf, "area": self.area}
        if self.on:
            d["on"] = self.on; d["on_config"] = self.on_cand.to_dict()
        return d


@dataclass
class Score:
    hits: int = 0
    pos: int = 0
    false: int = 0
    neg: int = 0

    @property
    def hit_rate(self) -> float:
        return self.hits / self.pos if self.pos else 0.0

    @property
    def fp_rate(self) -> float:
        return self.false / self.neg if self.neg else 0.0

    @property
    def j(self) -> float:
        return self.hit_rate - self.fp_rate

    def passed(self) -> bool:
        return self.hit_rate >= PASS_HIT and self.fp_rate <= PASS_FP

    def to_dict(self) -> dict:
        return {"hits": self.hits, "pos": self.pos, "false": self.false, "neg": self.neg,
                "hit_rate": round(self.hit_rate, 4), "fp_rate": round(self.fp_rate, 4)}


def iou(a, b) -> float:
    ax, ay, aw, ah = a; bx, by, bw, bh = b
    ix = max(0.0, min(ax + aw, bx + bw) - max(ax, bx)); iy = max(0.0, min(ay + ah, by + bh) - max(ay, by))
    inter = ix * iy; union = aw * ah + bw * bh - inter
    return inter / union if union > 0 else 0.0


def inside_ratio(a, b) -> float:
    """a 有多少比例的面積落在 b 裡。"""
    ax, ay, aw, ah = a; bx, by, bw, bh = b
    ix = max(0.0, min(ax + aw, bx + bw) - max(ax, bx)); iy = max(0.0, min(ay + ah, by + bh) - max(ay, by))
    return ix * iy / (aw * ah) if aw * ah > 0 else 0.0


def _center_in(rect, region) -> bool:
    x, y, w, h = rect; rx, ry, rw, rh = region
    cx, cy = x + w / 2, y + h / 2
    return rx <= cx <= rx + rw and ry <= cy <= ry + rh


def matches(dets: list[Det], cand: Candidate, region) -> list[tuple]:
    """這一格照 cand 的設定找到的框（中心要在桌面範圍內）。"""
    table = float(region[2] * region[3]) or 1.0
    out = [d.rect for d in dets
           if d.prompt == cand.prompt and d.conf >= cand.conf and d.rect[2] * d.rect[3] / table >= cand.area and _center_in(d.rect, region)]
    if cand.on:
        under = matches(dets, cand.on_cand, region)
        out = [r for r in out if any(inside_ratio(r, u) >= ON_TOP_MIN for u in under)]
    return out


def score(examples: list[Example], dets_by_frame: dict[int, list[Det]], cand: Candidate, region) -> Score:
    s = Score()
    for ex in examples:
        found = matches(dets_by_frame.get(ex.frame, []), cand, region)
        if ex.positive:
            s.pos += 1
            if cand.on:   # 關係題使用者框的是整塊（鞋子＋盒子），找到的東西落在框裡就算
                s.hits += any(inside_ratio(r, ex.rect) >= ON_TOP_MIN for r in found)
            else:
                s.hits += any(iou(r, ex.rect) >= IOU_HIT for r in found)
        else:
            s.neg += 1
            s.false += bool(found)
    return s


def candidates(vocab=VOCAB, on: str | None = None, on_cand: Candidate | None = None):
    for p in vocab:
        for c in CONF_GRID:
            for a in AREA_GRID:
                yield Candidate(p, c, a, on, on_cand)


def best_of(cands, examples, dets_by_frame, region):
    """挑選段上分數最好的候選。排序固定：找到率−誤報率 高 → 找到率高 → 誤報率低 → 候選清單裡的先後。"""
    best = None
    for k, c in enumerate(cands):
        s = score(examples, dets_by_frame, c, region)
        key = (-s.j, -s.hit_rate, s.fp_rate, k)
        if best is None or key < best[0]:
            best = (key, c, s)
    return (best[1], best[2]) if best else (None, None)


def exam_label(label: str, n_segments: int, examples: list[Example], dets_by_frame, region,
               passed: dict[str, Candidate] | None = None) -> dict:
    """考一個名稱。passed＝已經單獨考過的其他名稱（拿來試「疊在上面」）。回傳決定與理由（白話）。"""
    pick = [e for e in examples if not e.verify]
    ver = [e for e in examples if e.verify]
    nvp = sum(e.positive for e in ver); nvn = len(ver) - nvp
    out = {"label": label, "segments": n_segments,
           "pick_pos": sum(e.positive for e in pick), "pick_neg": sum(not e.positive for e in pick),
           "verify_pos": nvp, "verify_neg": nvn}
    if n_segments < MIN_SEGMENTS or nvp < MIN_VERIFY_POS or nvn < MIN_VERIFY_NEG:
        out.update(decision="train", reason=f"資料不夠（{n_segments} 段、驗收正例 {nvp} 張、反例 {nvn} 張；"
                                            f"至少要 {MIN_SEGMENTS} 段、{MIN_VERIFY_POS} 張、{MIN_VERIFY_NEG} 張），先用自己訓練的模型")
        return out
    c, s = best_of(list(candidates()), pick, dets_by_frame, region)
    v = score(ver, dets_by_frame, c, region)
    out["alone"] = {"config": c.to_dict(), "text": c.text(), "pick": s.to_dict(), "verify": v.to_dict()}
    if v.passed():
        out.update(decision="generic", config=c.to_dict(),
                   reason=f"通用辨識可以用：{c.text()}；驗收段找到 {v.hit_rate:.0%}、誤報 {v.fp_rate:.0%}")
        return out
    tried = []
    for other, oc in sorted((passed or {}).items()):
        if other == label:
            continue
        rc, rs = best_of(list(candidates(on=other, on_cand=oc)), pick, dets_by_frame, region)
        rv = score(ver, dets_by_frame, rc, region)
        tried.append({"on": other, "config": rc.to_dict(), "text": rc.text(), "pick": rs.to_dict(), "verify": rv.to_dict(), "_c": rc, "_v": rv})
    ok = [t for t in tried if t["_v"].passed()]
    if ok:
        t = min(ok, key=lambda t: (-t["_v"].j, t["on"]))
        out.update(decision="generic", config=t["config"],
                   reason=f"通用辨識可以用：{t['text']}；驗收段找到 {t['_v'].hit_rate:.0%}、誤報 {t['_v'].fp_rate:.0%}")
    else:
        out.update(decision="train",
                   reason=f"通用辨識考不過（最好的是 {c.text()}：驗收段找到 {v.hit_rate:.0%}、誤報 {v.fp_rate:.0%}；"
                          f"門檻是找到 ≥ {PASS_HIT:.0%}、誤報 ≤ {PASS_FP:.0%}），用自己訓練的模型")
    out["relations"] = [{k: x for k, x in t.items() if not k.startswith("_")} for t in tried]
    return out


def run_exam(labels: list[str], segments: dict[str, int], examples: dict[str, list[Example]], dets_by_frame, region) -> list[dict]:
    """先每個名稱單獨考；單獨考過的，再拿來給考不過的試「疊在上面」。"""
    first = {lb: exam_label(lb, segments.get(lb, 0), examples.get(lb, []), dets_by_frame, region) for lb in labels}
    passed = {lb: Candidate(**r["config"]) for lb, r in first.items() if r["decision"] == "generic" and "on" not in r["config"]}
    out = []
    for lb in labels:
        r = first[lb]
        if r["decision"] == "train" and "alone" in r and passed:
            r = exam_label(lb, segments.get(lb, 0), examples.get(lb, []), dets_by_frame, region, passed)
        out.append(r)
    return out
