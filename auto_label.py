"""自動標記：用（參照來的或自己的）辨識模型，把一支新影片先框好一份初版，給人確認後拿去訓練。

做法：
1. 步驟分析（step_analysis）沒有或過期就先跑：得到每一輪、每一步判定完成的時間。
2. 每一輪、每個物品步驟：在判定完成那一格附近（前後各 0.5 秒取 3 格）用模型找那樣物品，取分數最高、≥ MIN_CONF 的框，
   往前後追 2 秒（跟手框一樣），整組標成「模型框」（by_model）。
3. 輪與輪之間畫面上沒有任何物品的時段，每段挑中間一格當「空桌面」參考格（訓練時當背景圖）。
已經有框的物品／格不重複加；模型沒找到的步驟留給人補框（步驟分析會標紅）。
"""
from __future__ import annotations

import os
import time

import item_recognizer as items

MIN_CONF = 0.4              # 自動採納的最低分數（監控門檻 0.3；自動標進訓練資料要更保守）
PROBE_OFFSETS = (0.0, -0.5, 0.5)
TRACK_SEC = 2.0
REF_GAP_SEC = 2.0           # 沒有物品至少連續這麼久，才挑一格當空桌面參考


def pick_refs(timeline: list, rounds: list, fps: float, have: list[int]) -> list[int]:
    """輪與輪之間、畫面上沒有任何物品的時段（連續 ≥ REF_GAP_SEC），每段挑中間一格。"""
    spans = []; cur = None
    def inside(t):
        return any(r["start_t"] - 0.5 <= t <= r["end_t"] + 0.5 for r in rounds)
    for t, seen, _ in timeline:
        empty = not seen and not inside(t)
        if empty and cur is None:
            cur = [t, t]
        elif empty:
            cur[1] = t
        elif cur is not None:
            spans.append(cur); cur = None
    if cur is not None:
        spans.append(cur)
    out = []
    for a, b in spans:
        if b - a >= REF_GAP_SEC:
            f = int(round((a + b) / 2 * fps))
            if all(abs(f - h) > fps for h in have + out):
                out.append(f)
    return out


def auto_label(project, detector, analysis: dict, reader, progress=None, should_stop=None) -> dict:
    """依步驟分析結果自動框選。detector：ItemDetector（測試可換假的）；reader：FrameReader。回傳統計。"""
    fps = float(analysis.get("fps") or project.fps or 30.0)
    reg = tuple(project.state_fixed) if project.state_fixed else None
    if reg is None:
        raise ValueError("自動標記要有桌面範圍（固定範圍）：先在「包裝設定（訓練）」存至少一個物品的框，範圍會自動算")
    seeds = items.ItemSeeds(project.dir_path)
    label_of = {s.step_index: s.label for s in project.steps if s.type == "item" and s.label}
    jobs = []
    for r in analysis.get("rounds", []):
        for k, t in r.get("done", {}).items():
            if int(k) in label_of:
                jobs.append((r["no"], label_of[int(k)], float(t)))
    added = 0; tracked = 0; skipped = 0; missed = []
    for i, (no, label, t) in enumerate(jobs):
        if should_stop is not None and should_stop():
            raise RuntimeError("已取消")
        base = int(round(t * fps))
        if any(s.name == label and abs(s.frame - base) <= int(TRACK_SEC * fps) for s in seeds.seeds):
            skipped += 1; continue                                     # 這一輪這樣東西已經有框
        best = None
        for off in PROBE_OFFSETS:
            f = max(0, min(base + int(round(off * fps)), max(0, getattr(reader, "frame_count", base + 1) - 1)))
            crop = items._crop(reader.get_frame(f), reg)
            for h in detector.detect(crop):
                if h.name == label and h.conf >= MIN_CONF and (best is None or h.conf > best[0]):
                    best = (h.conf, f, (reg[0] + h.rect[0], reg[1] + h.rect[1], h.rect[2], h.rect[3]))
        if best is None:
            missed.append({"round": no, "label": label, "t": round(t, 2)}); continue
        _, f, rect = best
        auto = items.track_seed(project.video_path, f, rect, window_sec=TRACK_SEC, fps=project.fps)
        seeds.add_seed(label, f, rect, auto, by_model=True, save=False)
        added += 1; tracked += len(auto)
        if progress is not None:
            progress(i + 1, len(jobs))
    refs = pick_refs(analysis.get("timeline", []), analysis.get("rounds", []), fps, list(seeds.refs))
    seeds.refs = sorted(set(seeds.refs) | set(refs))
    seeds.save()
    return {"boxes": added, "tracked": tracked, "skipped": skipped, "missed": missed, "refs_added": len(refs), "jobs": len(jobs)}


def run(project, hand_model: str, yolo_weights: str, progress=None, should_stop=None) -> dict:
    """完整流程：需要時先跑步驟分析，再自動框選。progress(stage, done, total)。"""
    import step_analysis
    from video_recorder import FrameReader
    t0 = time.perf_counter()
    an = step_analysis.load(project)
    if an is None or an.get("stale"):
        an = step_analysis.analyze(project, hand_model, yolo_weights, progress=lambda a, b: progress and progress("分析步驟", a, b),
                                   should_stop=should_stop)
    det = items.ItemDetector(items.model_path(project))
    reader = FrameReader(project.video_path)
    try:
        st = auto_label(project, det, an, reader, progress=lambda a, b: progress and progress("自動標記", a, b), should_stop=should_stop)
    finally:
        reader.release()
    rounds = an.get("rounds", [])
    st.update({"rounds": len(rounds), "rounds_ok": sum(1 for r in rounds if r["status"] == "完成"),
               "missing": sum(len(r.get("missing", [])) for r in rounds), "elapsed_sec": round(time.perf_counter() - t0, 1)})
    return st
