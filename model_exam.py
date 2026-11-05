"""訓練完比較新舊模型：每個專案一份固定考卷，新舊模型考同一份，告訴使用者這次比上次變好、差不多還是變差。

- 考卷 <專案>/items/exam.json：每個物品取「最後一段框」最多 EXAM_PER_ITEM 格當考題（框就是正確答案），加上一部分「空桌面」參考格。
  第一次需要時才訂，之後凍結；後來才加的物品，等它有兩段以上的框再補出題。影片換了就重訂。
- 考卷的畫面（含前後 FIXED_WINDOW_SEC 秒）不拿去訓練，新舊模型才比得公平。只有一段框的物品不出題（全部拿去訓練）。
- 判定（固定規則，不用語言模型）：任一物品找到率掉 HIT_DROP 個百分點以上而且至少少 HIT_MIN_FRAMES 格、
  或空桌誤報升 FP_RISE 個百分點以上而且至少多 FP_MIN_FRAMES 格＝變差；沒有變差、至少一項依同樣條件變好＝變好；其他＝差不多。
  上次的模型沒有這個物品＝新物品，不比。
- 只支援固定桌面範圍（跟 training_material.validate_holdout 一樣）；盒內模式不出考卷、不比較。
"""
from __future__ import annotations

import copy
import json
import os
import time

import item_recognizer as items

EXAM_FILE = os.path.join(items.ITEMS_DIR, "exam.json")
HISTORY_FILE = os.path.join(items.MODEL_DIR, "train_history.json")
SEG_GAP_SEC = 3.0           # 同一個物品的框相隔超過這麼久算另一段（跟 training_material.SEG_GAP_SEC 一樣）
EXAM_PER_ITEM = 20          # 每個物品最多幾格考題（從最後一段平均取）
EXAM_EMPTY_MAX = 12         # 空桌面考題最多幾格（取參考格的後一半）
HIT_IOU = 0.3               # 模型的框跟答案框重疊這麼多才算找到
HIT_DROP = 10.0             # 找到率掉（升）這麼多個百分點算變差（變好）。先訂的數字，還沒用現場資料驗證
FP_RISE = 5.0               # 空桌誤報升（降）這麼多個百分點算變差（變好）
HIT_MIN_FRAMES = 3          # 而且找到的格數至少差這麼多格（20 格差 2 格就 10 點，太敏感；現場實測藍盒 20→18 被判變差）
FP_MIN_FRAMES = 2           # 誤報至少差這麼多格（空桌考題常只有幾格，差 1 格就 33 點）
HISTORY_KEEP = 20


# ---------------------------------------------------------------- 考卷

def load(project) -> dict | None:
    try:
        with open(os.path.join(project.dir_path, EXAM_FILE), "r", encoding="utf-8-sig") as f:
            d = json.load(f)
        return d if isinstance(d, dict) and isinstance(d.get("items"), dict) else None
    except (OSError, ValueError):
        return None


def _save(project, exam: dict) -> None:
    path = os.path.join(project.dir_path, EXAM_FILE)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(exam, f, ensure_ascii=False, indent=1)


def _video_key(project) -> str:
    try:
        return items.trace_fingerprint(project.video_path)
    except OSError:
        return ""


def _margin(project) -> int:
    return int(items.FIXED_WINDOW_SEC * float(project.fps or 30.0))


def _segments_of(seeds: items.ItemSeeds, name: str, gap: int, ranges: list[tuple[int, int]] | None = None) -> list[list[items.Seed]]:
    """這個物品的框分成幾段。標記頁時間軸有存段落（ranges）就照使用者存的段分（兩段隔得再近也是兩段，自動使用測試抓到：
    隔 2.8 秒的兩段被 3 秒規則併成一段，出不了考題）；沒有段落的舊專案才用「相隔超過 gap 格算另一段」。"""
    if ranges:
        rs = sorted(ranges)
        groups: list[list[items.Seed]] = [[] for _ in rs]
        for s in sorted((s for s in seeds.seeds if s.name == name), key=lambda s: s.frame):
            k = next((i for i, (a, b) in enumerate(rs) if a <= s.frame <= b), None)
            if k is not None:
                groups[k].append(s)
        return [g for g in groups if g]
    out: list[list[items.Seed]] = []
    for s in sorted((s for s in seeds.seeds if s.name == name), key=lambda s: s.frame):
        if out and s.frame - out[-1][-1].frame <= gap:
            out[-1].append(s)
        else:
            out.append([s])
    return out


def _even(xs: list, n: int) -> list:
    if len(xs) <= n:
        return list(xs)
    return [xs[round(i * (len(xs) - 1) / (n - 1))] for i in range(n)]


def _in(frame: int, ranges) -> bool:
    return any(a <= frame <= b for a, b in ranges)


def drop_ranges(exam: dict | None, margin: int) -> list[tuple[int, int]]:
    """不拿去訓練的格：每個考題物品那一段，前後再多 margin 格（延伸框選最多往前後找這麼遠）。"""
    if not exam:
        return []
    return [(int(e["start"]) - margin, int(e["end"]) + margin) for e in exam["items"].values()]


def ensure(project, seeds: items.ItemSeeds) -> dict | None:
    """拿考卷；沒有就訂一份，有新物品就補題（舊題目不動）。盒內模式回 None。會寫檔。"""
    if not items.is_fixed(project):
        return None
    vk = _video_key(project)
    exam = load(project)
    if exam is not None and exam.get("video") != vk:
        exam = None                                  # 影片換了：重訂
    if exam is None:
        exam = {"created_at": time.strftime("%Y/%m/%d %H:%M"), "video": vk, "items": {}, "empty": []}
        refs = sorted(seeds.refs)
        if len(refs) >= 2:                           # 一半空桌面格留著訓練（模型要學「桌上沒東西」），後一半當考題
            exam["empty"] = refs[-min(EXAM_EMPTY_MAX, len(refs) // 2):]
    margin = _margin(project); gap = int(SEG_GAP_SEC * float(project.fps or 30.0))
    saved_ranges: dict[str, list[tuple[int, int]]] = {}
    try:
        import label_segments as ls
        for sg in ls.Segments(project.dir_path).segs:
            if sg.saved:
                saved_ranges.setdefault(sg.name, []).append((int(sg.start), int(sg.end)))
    except Exception:
        saved_ranges = {}
    new: dict[str, dict] = {}
    for name in seeds.order:
        if name in exam["items"]:
            continue
        segs = _segments_of(seeds, name, gap, saved_ranges.get(name))
        if len(segs) < 2:
            continue
        last = segs[-1]
        by_frame: dict[int, items.Seed] = {}
        for s in last:                               # 同一格有手框和自動框時用手框
            if s.frame not in by_frame or (by_frame[s.frame].auto and not s.auto):
                by_frame[s.frame] = s
        qs = _even([by_frame[f] for f in sorted(by_frame)], EXAM_PER_ITEM)
        new[name] = {"start": last[0].frame, "end": last[-1].frame, "added_at": time.strftime("%Y/%m/%d %H:%M"),
                     "questions": [[s.frame, list(s.rect)] for s in qs]}
    # 保護：考卷不能把某個物品的框全部拿走（它就沒東西可訓練了）。拿走的話，跟它重疊的新題目不出
    while new:
        ranges = drop_ranges({"items": {**exam["items"], **new}}, margin)
        starved = [n for n in seeds.order if any(s.name == n for s in seeds.seeds)
                   and all(_in(s.frame, ranges) for s in seeds.seeds if s.name == n)]
        if not starved:
            break
        hit = [k for k, e in new.items() if any(_in(s.frame, [(e["start"] - margin, e["end"] + margin)])
                                                for s in seeds.seeds if s.name in starved)]
        if not hit:
            break
        for k in hit:
            new.pop(k)
    if new or load(project) != exam:
        exam["items"].update(new)
        _save(project, exam)
    return exam


def training_seeds(seeds: items.ItemSeeds, exam: dict | None, margin: int, extra_drop=()) -> items.ItemSeeds:
    """訓練用的框：扣掉考卷的畫面（含前後 margin 格）和當考題的空桌面格。只在記憶體裡，不寫回檔案。"""
    ranges = drop_ranges(exam, margin) + [tuple(r) for r in extra_drop]
    out = copy.copy(seeds)
    out.seeds = [s for s in seeds.seeds if not _in(s.frame, ranges)]
    empty = set((exam or {}).get("empty", []))
    out.refs = [r for r in seeds.refs if r not in empty]
    out.save = lambda: None
    return out


def question_count(exam: dict | None) -> int:
    return sum(len(e["questions"]) for e in (exam or {}).get("items", {}).values())


# ---------------------------------------------------------------- 考試

def score(project, model_file: str, exam: dict, detector=None, reader_factory=None) -> dict:
    """用一個模型考考卷。回傳 {"names": 模型認得的名稱, "items": {名稱: {"n", "hit"}}, "empty_n", "fp": {名稱: 誤報格數}}。"""
    if detector is None:
        detector = items.ItemDetector(model_file)
    if reader_factory is None:
        from video_recorder import FrameReader
        reader_factory = FrameReader
    reg = tuple(project.state_fixed)
    names = list(getattr(detector, "names", []) or [])
    want: dict[int, list] = {}
    for name, e in exam["items"].items():
        for f, rect in e["questions"]:
            want.setdefault(int(f), []).append((name, rect))
    empty = [int(f) for f in exam.get("empty", [])]
    res = {"names": names, "items": {n: {"n": len(e["questions"]), "hit": 0} for n, e in exam["items"].items()},
           "empty_n": len(empty), "fp": {n: 0 for n in exam["items"]}}
    reader = reader_factory(project.video_path)
    try:
        for f in sorted(set(want) | set(empty)):
            hits = detector.detect(items._crop(reader.get_frame(f), reg))
            for name, rect in want.get(f, []):
                truth = (rect[0] - reg[0], rect[1] - reg[1], rect[2], rect[3])
                if any(h.name == name and items._iou(h.rect, truth) >= HIT_IOU for h in hits):
                    res["items"][name]["hit"] += 1
            if f in empty:
                for name in {h.name for h in hits}:
                    res["fp"][name] = res["fp"].get(name, 0) + 1
    finally:
        try:
            reader.release()
        except Exception:
            pass
    return res


def _pct(k: int, n: int) -> float | None:
    return k * 100.0 / n if n else None


def compare(prev: dict | None, new: dict, prev_saw: list[str] | None = None) -> dict:
    """新舊成績 → 每個物品一列＋整次結論（first／better／same／worse）。prev None＝第一次訓練（或上次沒有模型）。"""
    rows = []
    for name, s in new["items"].items():
        en = new["empty_n"]
        row = {"name": name, "n": s["n"], "hit": s["hit"], "fp": new["fp"].get(name, 0), "empty_n": en,
               "hit_prev": None, "fp_prev": None, "verdict": "new" if prev is not None else "first"}
        known = prev is not None and name in prev["items"] and (not prev.get("names") or name in prev["names"])
        if known:
            row["hit_prev"] = prev["items"][name]["hit"]; row["fp_prev"] = prev["fp"].get(name, 0)
            dh = _pct(row["hit"], s["n"]) - _pct(row["hit_prev"], s["n"])
            df = (_pct(row["fp"], en) - _pct(row["fp_prev"], en)) if en else 0.0
            row["d_hit"] = round(dh, 1); row["d_fp"] = round(df, 1)
            kh = row["hit"] - row["hit_prev"]; kf = row["fp"] - row["fp_prev"]          # 差幾格
            hit_down = dh <= -HIT_DROP and kh <= -HIT_MIN_FRAMES; hit_up = dh >= HIT_DROP and kh >= HIT_MIN_FRAMES
            fp_up = df >= FP_RISE and kf >= FP_MIN_FRAMES; fp_down = df <= -FP_RISE and kf <= -FP_MIN_FRAMES
            row["hit_worse"] = hit_down; row["fp_worse"] = fp_up
            row["verdict"] = "worse" if hit_down or fp_up else "better" if hit_up or fp_down else "same"
        rows.append(row)
    if prev is None:
        verdict = "first"
    elif any(r["verdict"] == "worse" for r in rows):
        verdict = "worse"
    elif any(r["verdict"] == "better" for r in rows):
        verdict = "better"
    else:
        verdict = "same"
    return {"verdict": verdict, "rows": rows, "prev_saw": list(prev_saw or []),
            "rules": {"hit_drop": HIT_DROP, "fp_rise": FP_RISE, "hit_iou": HIT_IOU, "hit_min": HIT_MIN_FRAMES, "fp_min": FP_MIN_FRAMES}}


# ---------------------------------------------------------------- 紀錄

def history(project) -> list[dict]:
    try:
        with open(os.path.join(project.dir_path, HISTORY_FILE), "r", encoding="utf-8-sig") as f:
            d = json.load(f)
        return d if isinstance(d, list) else []
    except (OSError, ValueError):
        return []


def add_history(project, entry: dict) -> list[dict]:
    rows = [entry] + history(project)
    rows = rows[:HISTORY_KEEP]
    path = os.path.join(project.dir_path, HISTORY_FILE)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(rows, f, ensure_ascii=False, indent=1)
    return rows


def set_history_installed(project, at: str, forced: bool) -> None:
    rows = history(project)
    for r in rows:
        if r.get("at") == at:
            r["installed"] = True; r["forced"] = forced
    path = os.path.join(project.dir_path, HISTORY_FILE)
    if rows:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(rows, f, ensure_ascii=False, indent=1)


def held_out_items(project) -> list[str]:
    """這個專案現在的模型訓練時，哪些物品的考題有扣掉（記在 model_info.json）。舊模型沒記＝空。"""
    try:
        with open(os.path.join(project.dir_path, items.MODEL_INFO_FILE), "r", encoding="utf-8-sig") as f:
            d = json.load(f)
        exam = d.get("exam") or {}
        return [str(x) for x in exam.get("held_out", [])] if exam.get("video") == _video_key(project) else []
    except (OSError, ValueError):
        return []
