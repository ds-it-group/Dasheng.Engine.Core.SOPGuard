"""標記頁的時間軸資料（<專案>/items/segments.json）：名稱分「物品」與「動作」兩種，每個名稱有幾段「頭尾格」。

- 物品：一段裡畫一個框，存檔時程式把這個框沿整段自動追蹤（CSRT），每隔 TRACK_STEP 格記一個框寫進 seeds.json
  （手框那一格＋追出來的自動框同一組），訓練直接拿這些框當標籤。段落跟 seeds 用組號（group）對起來。
- 動作：只有頭尾、不畫框。存檔時看這幾秒手的關鍵點落在哪個已框物品裡最多，就當「手碰到那個物品」；監控時變成
  hand_on_object 步驟，區域＝那個物品被訓練出來的框。判斷是固定規則（TOUCH_MIN_RATIO／TOUCH_MIN_FRAMES），同資料同結果。
- 同一個名稱的段落不能重疊；刪掉的段落（連同它的框）先放進垃圾桶，可以復原。
所有矩形都是畫面座標 [x, y, w, h]，時間一律用「格」（整數、含頭尾）。
"""
from __future__ import annotations

import json
import os
from dataclasses import asdict, dataclass

import cv2
import numpy as np

SEGMENTS_FILE = os.path.join("items", "segments.json")
KINDS = ("object", "action")
PALETTE = ["#1e5fbf", "#b85400", "#00796b", "#7b1fa2", "#ad1457", "#2e7d32", "#5d4037", "#0277bd", "#558b2f", "#c2185b", "#455a64", "#6a1b9a", "#e65100"]
TRASH_MAX = 20
ACTION_DWELL_SEC = 0.7       # 動作：手連續碰著物品這麼久才算做過（現場翻鞋舌檢查的實測值，見 README）
TOUCH_MIN_RATIO = 0.3        # 動作段落裡「有手」的取樣格，至少這個比例手在同一個物品框內才算碰到它
TOUCH_MIN_FRAMES = 2         # 而且至少要有這麼多格
TRACK_MAX_SIDE = 960         # 追蹤時影格長邊縮到這麼大（1080p 直接跑 CSRT 一格要 80 ms）
TRACK_MAX_MISS = 4           # 連續這麼多格顏色對不上（被遮住、追丟）就停，後面的格不標
TRACK_AREA_RANGE = (0.33, 3.0)   # 追到的框面積相對手框那一格超出這個倍數就當追丟

Rect = tuple[int, int, int, int]


@dataclass
class NameDef:
    name: str
    kind: str = "object"
    color: str = ""
    touch: str | None = None          # 動作：存檔時判斷出來「手碰到的物品」


@dataclass
class Segment:
    id: int
    name: str
    start: int                        # 含
    end: int                          # 含
    box: list[int] | None = None      # 物品：使用者畫的框（畫面座標）
    box_frame: int | None = None      # 框是在哪一格畫的
    saved: bool = False
    group: int = 0                    # seeds.json 的組號（存檔後才有）
    tracked: int = 0                  # 存檔時追出幾格（含手框那一格）
    touch: str | None = None          # 動作：這一段判斷出來手碰到的物品

    @property
    def frames(self) -> int:
        return self.end - self.start + 1


class Segments:
    def __init__(self, project_dir: str):
        self.path = os.path.join(project_dir, SEGMENTS_FILE)
        self.names: list[NameDef] = []
        self.segs: list[Segment] = []
        self.trash: list[dict] = []
        self.next_id = 1
        self.load()

    # ---- 檔案

    def load(self) -> None:
        self.names, self.segs, self.trash, self.next_id = [], [], [], 1
        if not os.path.isfile(self.path):
            return
        with open(self.path, "r", encoding="utf-8-sig") as f:
            d = json.load(f)
        for n in d.get("names", []):
            if isinstance(n, dict) and n.get("name") and n.get("kind", "object") in KINDS:
                self.names.append(NameDef(str(n["name"]), str(n.get("kind", "object")), str(n.get("color") or ""), n.get("touch") or None))
        for s in d.get("segments", []):
            if not isinstance(s, dict):
                continue
            box = s.get("box")
            self.segs.append(Segment(int(s["id"]), str(s["name"]), int(s["start"]), int(s["end"]),
                                     [int(v) for v in box] if isinstance(box, list) and len(box) == 4 else None,
                                     None if s.get("box_frame") is None else int(s["box_frame"]), bool(s.get("saved", False)),
                                     int(s.get("group", 0) or 0), int(s.get("tracked", 0) or 0), s.get("touch") or None))
        self.trash = [t for t in d.get("trash", []) if isinstance(t, dict) and isinstance(t.get("seg"), dict)]
        self.next_id = max([int(d.get("next_id", 1) or 1)] + [s.id + 1 for s in self.segs] + [int(t["seg"].get("id", 0)) + 1 for t in self.trash])
        self._sort()

    def save(self) -> None:
        os.makedirs(os.path.dirname(self.path), exist_ok=True)
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump({"names": [asdict(n) for n in self.names], "segments": [asdict(s) for s in self.segs],
                       "trash": self.trash, "next_id": self.next_id}, f, ensure_ascii=False, indent=2)

    def to_dict(self) -> dict:
        return {"names": [asdict(n) for n in self.names], "segments": [asdict(s) for s in self.segs], "trash": len(self.trash)}

    def _sort(self) -> None:
        self.segs.sort(key=lambda s: (s.name, s.start, s.id))

    # ---- 名稱

    def name(self, name: str) -> NameDef | None:
        return next((n for n in self.names if n.name == name), None)

    def add_name(self, name: str, kind: str = "object") -> NameDef:
        name = name.strip()
        if not name:
            raise ValueError("請先輸入名稱")
        if kind not in KINDS:
            raise ValueError("種類只能是 物品 或 動作")
        if self.name(name) is not None:
            raise ValueError(f"已經有「{name}」了，直接點它就好")
        n = NameDef(name, kind, PALETTE[len(self.names) % len(PALETTE)])
        self.names.append(n); self.save()
        return n

    def remove_name(self, name: str) -> None:
        if any(s.name == name for s in self.segs):
            raise ValueError(f"「{name}」還有段落，先把段落刪掉才能刪名稱")
        if self.name(name) is None:
            raise ValueError(f"沒有「{name}」這個名稱")
        self.names = [n for n in self.names if n.name != name]; self.save()

    # ---- 段落

    def get(self, sid: int) -> Segment:
        s = next((s for s in self.segs if s.id == sid), None)
        if s is None:
            raise ValueError("這一段已經不存在了，請重新整理")
        return s

    def by_name(self, name: str) -> list[Segment]:
        return [s for s in self.segs if s.name == name]

    def _check_range(self, name: str, start: int, end: int, n_frames: int, skip: int | None = None) -> tuple[int, int]:
        start, end = int(start), int(end)
        if n_frames > 0:
            start = max(0, min(n_frames - 1, start)); end = max(0, min(n_frames - 1, end))
        if end < start:
            raise ValueError("結尾不能在開頭前面")
        for k, s in enumerate(self.by_name(name)):
            if s.id == skip:
                continue
            if start <= s.end and end >= s.start:
                raise ValueError(f"跟「{name}」第 {k + 1} 段重疊了（同一個名稱同一時間只能有一段）")
        return start, end

    def add(self, name: str, start: int, end: int, n_frames: int = 0) -> Segment:
        if self.name(name) is None:
            raise ValueError(f"沒有「{name}」這個名稱，請先新增")
        start, end = self._check_range(name, start, end, n_frames)
        s = Segment(self.next_id, name, start, end); self.next_id += 1
        self.segs.append(s); self._sort(); self.save()
        return s

    def update_range(self, sid: int, start: int, end: int, n_frames: int = 0) -> tuple[Segment, bool]:
        """改頭尾。回傳 (段落, 有沒有變)。範圍變了就要重新存檔（物品要重追、動作要重判）。"""
        s = self.get(sid)
        start, end = self._check_range(s.name, start, end, n_frames, skip=sid)
        changed = (start, end) != (s.start, s.end)
        if changed:
            s.start, s.end = start, end
            if s.box_frame is not None and not (start <= s.box_frame <= end):
                s.box = None; s.box_frame = None          # 畫框的那一格被切掉了：框要重畫
            s.saved = False
            self._sort(); self.save()
        return s, changed

    def set_box(self, sid: int, frame: int | None, rect: list | None) -> Segment:
        s = self.get(sid)
        if self.name(s.name) is not None and self.name(s.name).kind == "action":
            raise ValueError(f"「{s.name}」是動作，不用畫框")
        if rect is None:
            s.box = None; s.box_frame = None
        else:
            if not (isinstance(rect, (list, tuple)) and len(rect) == 4 and rect[2] >= 12 and rect[3] >= 12):
                raise ValueError("請在畫面上拖拉框住物品（框太小）")
            frame = int(frame if frame is not None else s.start)
            if not (s.start <= frame <= s.end):
                raise ValueError("要在這一段的範圍裡畫框")
            s.box = [int(v) for v in rect]; s.box_frame = frame
        s.saved = False; self.save()
        return s

    def mark_saved(self, sid: int, group: int = 0, tracked: int = 0, touch: str | None = None) -> Segment:
        s = self.get(sid)
        s.saved = True; s.group = int(group); s.tracked = int(tracked); s.touch = touch
        self.save()
        return s

    def remove(self, sid: int, seed_rows: list[dict] | None = None) -> Segment:
        """刪段落：連同它在 seeds.json 裡的框（呼叫端傳進來）一起放進垃圾桶，最多留 TRASH_MAX 筆。"""
        s = self.get(sid)
        self.segs = [x for x in self.segs if x.id != sid]
        self.trash.append({"seg": asdict(s), "seeds": list(seed_rows or [])})
        self.trash = self.trash[-TRASH_MAX:]
        self.save()
        return s

    def restore(self, n_frames: int = 0) -> tuple[Segment, list[dict]]:
        """復原最後刪的那一段。名稱已經不在、或位置被別段佔走就不能復原。"""
        if not self.trash:
            raise ValueError("沒有可以復原的段落")
        t = self.trash[-1]; d = t["seg"]
        if self.name(d["name"]) is None:
            raise ValueError(f"名稱「{d['name']}」已經刪掉了，這一段不能復原")
        self._check_range(d["name"], d["start"], d["end"], n_frames)
        self.trash.pop()
        s = Segment(int(d["id"]), str(d["name"]), int(d["start"]), int(d["end"]), d.get("box"), d.get("box_frame"), bool(d.get("saved")),
                    int(d.get("group", 0) or 0), int(d.get("tracked", 0) or 0), d.get("touch"))
        if any(x.id == s.id for x in self.segs):
            s.id = self.next_id; self.next_id += 1
        self.segs.append(s); self._sort(); self.save()
        return s, list(t.get("seeds") or [])

    def counts(self) -> dict:
        """右下角的統計：物品已存幾段（幾格會拿去訓練）、動作已存幾段。"""
        kind = {n.name: n.kind for n in self.names}
        obj = act = frames = 0
        for s in self.segs:
            if not s.saved:
                continue
            if kind.get(s.name) == "action":
                act += 1
            else:
                obj += 1; frames += s.tracked
        return {"object_segments": obj, "object_frames": frames, "action_segments": act}


# ---------------------------------------------------------------- 物品：一個框沿整段追

def _make_tracker():
    for attr in ("TrackerCSRT_create",):
        fn = getattr(cv2, attr, None)
        if fn is not None:
            return fn()
    legacy = getattr(cv2, "legacy", None)
    if legacy is not None and hasattr(legacy, "TrackerCSRT_create"):
        return legacy.TrackerCSRT_create()
    return None


def _color_sig(img):
    """HSV 色相×飽和度直方圖（正規化），比對用。"""
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    h = cv2.calcHist([hsv], [0, 1], None, [18, 8], [0, 180, 0, 256])
    cv2.normalize(h, h)
    return h


def _crop(img, r):
    x, y, w, h = [int(round(v)) for v in r]
    H, W = img.shape[:2]
    return img[max(0, y):min(H, y + h), max(0, x):min(W, x + w)]


class _Follower:
    """從 img0 上的 rect0 開始，一格一格餵進來追（縮小座標）。每格都檢查顏色跟原框像不像、面積有沒有暴衝；
    連續 TRACK_MAX_MISS 格不像就停（之後 feed 直接回 False）。結果在 out：[(格, rect)]。"""

    def __init__(self, img0, rect0, color_min: float):
        self.out: list[tuple[int, list[int]]] = []
        self.tracker = _make_tracker()
        x, y, w, h = rect0
        if self.tracker is not None:
            self.tracker.init(img0, (int(x), int(y), int(w), int(h)))
        self.sig0 = _color_sig(_crop(img0, rect0)); self.area0 = float(w * h); self.last = tuple(rect0)
        self.tpl = cv2.cvtColor(_crop(img0, rect0), cv2.COLOR_BGR2GRAY); self.color_min = color_min
        self.misses = 0; self.stopped = False

    def feed(self, f: int, img) -> bool:
        if self.stopped:
            return False
        cand = None
        if self.tracker is not None:
            ok, bb = self.tracker.update(img)
            if ok:
                cand = tuple(int(round(v)) for v in bb)
        if cand is None:
            cand = _template_fallback(self.tpl, img, self.last)
        good = False
        if cand is not None and cand[2] > 0 and cand[3] > 0:
            ratio = cand[2] * cand[3] / self.area0
            crop = _crop(img, cand)
            if TRACK_AREA_RANGE[0] <= ratio <= TRACK_AREA_RANGE[1] and crop.size > 0:
                good = cv2.compareHist(self.sig0, _color_sig(crop), cv2.HISTCMP_CORREL) >= self.color_min
        if good:
            self.misses = 0; self.last = cand; self.out.append((f, list(cand)))
        else:
            self.misses += 1
            if self.misses >= TRACK_MAX_MISS:
                self.stopped = True
        return not self.stopped


def _template_fallback(tpl, img, last):
    """沒有 CSRT 時的備案：上一個位置外擴 50% 內做灰階樣板比對。"""
    from item_recognizer import _track
    g = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    lx, ly, lw, lh = last
    sx1, sy1 = max(0, int(lx - lw * 0.5)), max(0, int(ly - lh * 0.5))
    sx2, sy2 = min(g.shape[1], int(lx + lw * 1.5)), min(g.shape[0], int(ly + lh * 1.5))
    s, r = _track(tpl, g[sy1:sy2, sx1:sx2])
    if r is None or s < 0.5:
        return None
    return (sx1 + r[0], sy1 + r[1], r[2], r[3])


def track_segment(video_path: str, start: int, end: int, box_frame: int, rect, step: int = 3, color_min: float = 0.5,
                  progress=None) -> list[tuple[int, list[int]]]:
    """把 box_frame 上的 rect 沿 [start, end] 往前、往後各追一遍，每 step 格記一個框（畫面座標）。回傳不含 box_frame 那一格。
    影片只循序讀一次：box_frame 之後的格邊讀邊追；之前的格先存成 JPEG（省記憶體）再倒著追。"""
    from video_recorder import open_video_oriented
    cap, rotate, W, H, _ = open_video_oriented(video_path)
    n_total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT) or 0)
    start = max(0, int(start)); end = min(max(n_total - 1, 0), int(end)); box_frame = int(box_frame)
    if not (start <= box_frame <= end):
        cap.release()
        return []
    scale = min(1.0, TRACK_MAX_SIDE / float(max(W, H)))
    sx = lambda v: int(round(v * scale))
    r0 = (sx(rect[0]), sx(rect[1]), max(1, sx(rect[2])), max(1, sx(rect[3])))
    before: list[tuple[int, bytes]] = []; fwd: _Follower | None = None
    cap.set(cv2.CAP_PROP_POS_FRAMES, start); i = start
    while i <= end:
        if fwd is not None and fwd.stopped:
            break                                   # 往後已經追丟，後面不用再讀
        ok, fr = cap.read()
        if not ok:
            break
        if (i - box_frame) % step == 0:
            if rotate is not None:
                fr = cv2.rotate(fr, rotate)
            small = cv2.resize(fr, None, fx=scale, fy=scale, interpolation=cv2.INTER_AREA) if scale < 1.0 else fr
            if i < box_frame:
                ok2, buf = cv2.imencode(".jpg", small, [cv2.IMWRITE_JPEG_QUALITY, 90])
                before.append((i, buf.tobytes()))
            elif i == box_frame:
                fwd = _Follower(small, r0, color_min)
            else:
                fwd.feed(i, small)                  # 往後：邊讀邊追，不堆記憶體
        i += 1
        if progress and (i - start) % 60 == 0:
            progress(i - start, end - start + 1)
    cap.release()
    if fwd is None:
        return []
    img0 = None
    if before:
        # 往前：要同一張起始圖再建一個追蹤器；起始圖從影片再讀一次那一格
        cap, rotate, _, _, _ = open_video_oriented(video_path)
        cap.set(cv2.CAP_PROP_POS_FRAMES, box_frame); ok, fr = cap.read(); cap.release()
        if ok:
            if rotate is not None:
                fr = cv2.rotate(fr, rotate)
            img0 = cv2.resize(fr, None, fx=scale, fy=scale, interpolation=cv2.INTER_AREA) if scale < 1.0 else fr
    back = _Follower(img0, r0, color_min) if img0 is not None else None
    if back is not None:
        for f, b in reversed(before):
            if not back.feed(f, cv2.imdecode(np.frombuffer(b, np.uint8), cv2.IMREAD_COLOR)):
                break
    res = []
    for f, (x, y, w, h) in fwd.out + (back.out if back else []):
        res.append((f, [int(round(x / scale)), int(round(y / scale)), int(round(w / scale)), int(round(h / scale))]))
    res.sort(key=lambda t: t[0])
    return res


# ---------------------------------------------------------------- 動作：手碰到哪個物品

def infer_touch(hands_by_frame: dict[int, list], boxes_by_frame: dict[int, dict[str, list]]) -> tuple[str | None, dict]:
    """hands_by_frame：取樣格 → 手的判定點（每手 4 點）；boxes_by_frame：取樣格 → {物品名: [框...]}（已框物品在那一格的位置）。
    規則：有手的格裡，某隻手 ≥ 2 點落在物品框內就算這一格碰到它；碰到最多格的物品勝出，但要 ≥ TOUCH_MIN_FRAMES 格、
    且佔有手的格 ≥ TOUCH_MIN_RATIO 才算。平手取名稱排序在前的（結果固定）。回傳 (物品名或 None, 統計)。"""
    from core_detector import hands_in_inner
    touched: dict[str, int] = {}; with_hands = 0
    for f in sorted(hands_by_frame):
        pts = hands_by_frame[f]
        if not pts:
            continue
        with_hands += 1
        for name, rects in boxes_by_frame.get(f, {}).items():
            if any(hands_in_inner(pts, tuple(r), shrink=0.0, need=2) for r in rects):
                touched[name] = touched.get(name, 0) + 1
    best = min(touched, key=lambda n: (-touched[n], n)) if touched else None
    ratio = touched[best] / with_hands if best else 0.0
    ok = best is not None and touched[best] >= TOUCH_MIN_FRAMES and ratio >= TOUCH_MIN_RATIO
    stats = {"frames": len(hands_by_frame), "with_hands": with_hands, "touched": touched, "best": best, "ratio": round(ratio, 3)}
    return (best if ok else None), stats


def touch_reason(stats: dict, candidates: list[str]) -> str:
    """infer_touch 沒判出來時給使用者看的理由（白話）。"""
    if not candidates:
        return "這幾秒畫面上沒有任何已框的物品。先框一個被手碰到的東西（例如 鞋子）並儲存，再存這個動作。"
    if stats["with_hands"] == 0:
        return "這幾秒沒偵測到手。確認範圍有拉到手在做動作的時候、手沒有被遮住。"
    if stats["best"]:
        return (f"手碰到「{stats['best']}」的格數不夠（{stats['touched'][stats['best']]}／{stats['with_hands']} 格有手，"
                f"{stats['ratio']:.0%}，要 ≥ {TOUCH_MIN_RATIO:.0%}）。範圍縮到手真的在碰的那幾秒，或先把被碰的物品框好。")
    return f"手沒有落在任何已框的物品上（這幾秒有框的是：{'、'.join(candidates)}）。先把被手碰到的東西框好再存。"
