"""訓練完自動重判動作：用新模型認出來的框，把已存的動作再判一次「手碰到哪個物品」。

存動作的時候，判的是使用者框的位置（label_service._save_segment）；監控時用的卻是模型認出來的框。
模型認不到被碰的物品（例如鞋舌太小、被手遮住），監控時這個動作就永遠判不到。所以訓練換上新模型後：
- 每個已存的動作段落，取樣格（每 TRACE_STEP 格，最多 MAX_FRAMES 格）用新模型找物品，手的位置用訓練時留下的 trace.json；
- 照 label_segments.infer_touch 同一套規則判碰到哪個；跟存的時候一樣＝對得上，判不出來或判成別的＝在標記頁那個動作旁標警示。
結果存在 <專案>/items/action_check.json。只支援固定桌面範圍（跟考卷一樣）；沒有 trace.json 就不判。
"""
from __future__ import annotations

import json
import os
import time

import item_recognizer as items

CHECK_FILE = os.path.join(items.ITEMS_DIR, "action_check.json")
MAX_FRAMES = 40


def _trace_hands(project) -> dict[int, list] | None:
    path = os.path.join(project.dir_path, items.TRACE_FILE)
    try:
        with open(path, "r", encoding="utf-8") as f:
            d = json.load(f)
        if d.get("fingerprint") != items.trace_fingerprint(project.video_path):
            return None
        return {int(r["f"]): [tuple(pt) for pt in r["hands"]] for r in d.get("rows", []) if "hands" in r}
    except (OSError, ValueError, KeyError):
        return None


def _even(xs: list, n: int) -> list:
    if len(xs) <= n:
        return list(xs)
    return [xs[round(i * (len(xs) - 1) / (n - 1))] for i in range(n)]


def recheck(project, model_file: str, detector=None, reader_factory=None, hands: dict | None = None) -> dict:
    """回傳 {"at", "rows": [{"action", "saved", "model", "ok", "note"}], "skipped": 理由或 None}，並寫檔。"""
    import label_segments as ls
    out = {"at": time.strftime("%Y/%m/%d %H:%M"), "model_file": os.path.basename(model_file), "rows": [], "skipped": None}
    segs = ls.Segments(project.dir_path)
    acts = [(nd, [s for s in segs.by_name(nd.name) if s.saved]) for nd in segs.names if nd.kind == "action"]
    acts = [(nd, ss) for nd, ss in acts if ss]
    if not acts:
        out["skipped"] = "沒有已存的動作"
    elif not items.is_fixed(project):
        out["skipped"] = "盒內模式不重判"
    else:
        hands = hands if hands is not None else _trace_hands(project)
        if not hands:
            out["skipped"] = "沒有手的紀錄（trace.json）"
    if out["skipped"]:
        _save(project, out); return out
    if detector is None:
        detector = items.ItemDetector(model_file)
    if reader_factory is None:
        from video_recorder import FrameReader
        reader_factory = FrameReader
    objects = {nd.name for nd in segs.names if nd.kind == "object"}
    reg = tuple(project.state_fixed)
    reader = reader_factory(project.video_path)
    try:
        for nd, ss in acts:
            saved = next((s.touch for s in ss if s.touch), None) or nd.touch
            frames = _even([f for s in ss for f in range(s.start, s.end + 1) if f % items.TRACE_STEP == 0 and f in hands], MAX_FRAMES)
            boxes: dict[int, dict[str, list]] = {}
            for f in frames:
                row: dict[str, list] = {}
                for h in detector.detect(items._crop(reader.get_frame(f), reg)):
                    if h.name in objects:
                        x, y, w, hh = h.rect
                        row.setdefault(h.name, []).append((x + reg[0], y + reg[1], w, hh))     # 裁圖座標 → 畫面座標（手也是畫面座標）
                if row:
                    boxes[f] = row
            touch, stats = ls.infer_touch({f: hands[f] for f in frames}, boxes)
            ok = touch is not None and touch == saved
            if ok:
                note = f"對得上：模型認得「{saved}」，手碰到它"
            elif touch is None:
                note = (f"模型在這個動作的時間裡認不到手碰的「{saved}」（{stats['touched'].get(saved, 0)}／{stats['with_hands']} 格）。"
                        "監控時這一步可能一直判不到：多框幾段這個物品再訓練，或改成框大一點的東西")
            else:
                note = f"模型判成碰到「{touch}」，存的時候是「{saved}」。監控時會照「{saved}」判，可能判不到；檢查這個動作的範圍或重存一次"
            out["rows"].append({"action": nd.name, "saved": saved, "model": touch, "ok": ok, "note": note,
                                "frames": len(frames), "touched": stats["touched"]})
    finally:
        try:
            reader.release()
        except Exception:
            pass
    _save(project, out)
    return out


def _save(project, d: dict) -> None:
    path = os.path.join(project.dir_path, CHECK_FILE)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(d, f, ensure_ascii=False, indent=1)


def forget(project, action: str) -> None:
    """使用者重存了這個動作：舊的重判結果不算了（下次訓練再判）。"""
    d = load(project)
    if d and any(r.get("action") == action for r in d.get("rows", [])):
        d["rows"] = [r for r in d["rows"] if r.get("action") != action]
        _save(project, d)


def load(project) -> dict | None:
    try:
        with open(os.path.join(project.dir_path, CHECK_FILE), "r", encoding="utf-8-sig") as f:
            return json.load(f)
    except (OSError, ValueError):
        return None
