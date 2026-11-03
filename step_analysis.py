"""離線步驟分析：用監控同一套判斷（手部、物件、物品模型、狀態機）把整支示範影片跑一遍，記下
每一輪的開始／結束、每一步什麼時候完成、哪幾步沒看到，以及每一格附近「正在做哪一步」。

結果存在 <專案>/items/analysis.json；影片、模型或步驟改了就算過期，要重跑。
給預覽燈箱的時間軸、標紅的漏看步驟，以及標記頁的「下一個要補框的地方」用。
"""
from __future__ import annotations

import hashlib
import json
import os
import time

import item_recognizer as items

ANALYSIS_FILE = os.path.join(items.ITEMS_DIR, "analysis.json")
VERSION = 1


def fingerprint(project) -> str:
    """影片（大小＋修改時間）、實際用的模型（路徑＋修改時間）、步驟清單、桌面範圍，任一變了就要重跑。"""
    parts = []
    for path in (project.video_path, items.model_path(project)):
        try:
            st = os.stat(path)
            parts.append(f"{os.path.abspath(path)}|{st.st_size}|{int(st.st_mtime)}")
        except OSError:
            parts.append(f"{path}|missing")
    steps = [(s.step_index, s.step_name, s.type, s.label, s.object, s.dwell_time_sec, s.required, s.continuous) for s in project.steps]
    parts.append(json.dumps(steps, ensure_ascii=False))
    parts.append(json.dumps(project.state_fixed))
    return hashlib.md5("\n".join(parts).encode("utf-8")).hexdigest()


def load(project) -> dict | None:
    try:
        with open(os.path.join(project.dir_path, ANALYSIS_FILE), "r", encoding="utf-8") as f:
            d = json.load(f)
    except (OSError, ValueError):
        return None
    d["stale"] = d.get("fingerprint") != fingerprint(project) or d.get("version") != VERSION
    return d


class RoundBuilder:
    """把狀態機的事件串成「輪」：第一步完成（或狀態機開始一輪）就開一輪；cycle_done＝完成、alert_missing＝漏做、
    cycle_discarded＝太短丟掉；影片結束還沒結算＝未完成。"""

    def __init__(self, steps, fps: float):
        self.steps = list(steps); self.fps = fps
        self.rounds: list[dict] = []; self.cur: dict | None = None

    def _open(self, start_t: float) -> None:
        self.cur = {"start_t": round(start_t, 2), "done": {}, "status": None}

    def on_frame(self, fsm) -> None:
        if fsm.mode != "checklist":
            return
        if fsm.cycle_active:
            if self.cur is None:
                self._open(fsm.cycle_started_at)
            else:
                self.cur["start_t"] = round(fsm.cycle_started_at, 2)    # 狀態機第一步完成時可能把開始時間往後挪

    def on_event(self, ev: dict, fsm) -> None:
        et = ev["event_type"]; t = float(ev["t"])
        if et == "step_done":
            if self.cur is None:
                self._open(fsm.cycle_started_at if fsm.cycle_active else t)
            if ev["step_index"] != "" and str(ev["step_index"]) not in self.cur["done"]:
                self.cur["done"][str(ev["step_index"])] = round(t, 2)
        elif et in ("cycle_done", "alert_missing", "alert_timeout") and self.cur is not None:
            self._close(t, {"cycle_done": "完成", "alert_missing": "漏做", "alert_timeout": "超時"}[et])
        elif et == "cycle_discarded":
            self.cur = None

    def _close(self, t: float, status: str) -> None:
        r = self.cur; self.cur = None
        r["end_t"] = round(t, 2); r["status"] = status
        self.rounds.append(r)

    def finish(self, t_end: float) -> list[dict]:
        if self.cur is not None and self.cur["done"]:
            self._close(t_end, "未完成")
        order = typical_order(self.rounds, self.steps)
        out = []
        for k, r in enumerate(self.rounds):
            r = dict(r, no=k + 1, start=int(round(r["start_t"] * self.fps)), end=int(round(r["end_t"] * self.fps)))
            r["missing"] = missing_windows(r, self.steps, self.fps, order) if r["status"] != "完成" else []
            out.append(r)
        return out


def typical_order(rounds: list[dict], steps) -> dict[int, float]:
    """實際作業的先後順序：用「完成」的輪，每一步在輪內的相對位置取中位數（現場是先檢查鞋舌、再拿盒子，
    跟步驟清單的順序不一樣）。沒有完成的輪就用步驟清單順序。"""
    pos: dict[int, list[float]] = {}
    for r in rounds:
        if r.get("status") != "完成":
            continue
        dur = max(1e-6, r["end_t"] - r["start_t"])
        for k, t in r["done"].items():
            pos.setdefault(int(k), []).append((t - r["start_t"]) / dur)
    out = {}
    for s in steps:
        v = sorted(pos.get(s.step_index, []))
        out[s.step_index] = v[len(v) // 2] if v else 1.0 + s.step_index / 100.0
    return out


def missing_windows(r: dict, steps, fps: float, order: dict[int, float] | None = None) -> list[dict]:
    """沒看到的必要步驟大概發生在哪：照實際作業的先後順序，夾在「前面最晚完成的那一步」和「後面最早完成的那一步」之間；
    取中間那一格當作跳過去的位置。未完成的輪只算到影片結束。"""
    done = {int(k): v for k, v in r["done"].items()}
    rank = order or {s.step_index: float(s.step_index) for s in steps}
    out = []
    for s in steps:
        if not s.required or s.step_index in done:
            continue
        before = [t for i, t in done.items() if rank.get(i, i) < rank.get(s.step_index, s.step_index)]
        after = [t for i, t in done.items() if rank.get(i, i) > rank.get(s.step_index, s.step_index)]
        a = max(before) if before else r["start_t"]
        b = min(after) if after else r["end_t"]
        if b < a:
            a, b = r["start_t"], r["end_t"]
        mid = (a + b) / 2
        out.append({"index": s.step_index, "name": s.step_name, "type": s.type, "label": s.label or s.object or "",
                    "from_t": round(a, 2), "to_t": round(b, 2), "frame": int(round(mid * fps)),
                    "boxable": s.type == "item"})
    return out


def analyze(project, hand_model: str, yolo_weights: str, progress=None, should_stop=None) -> dict:
    """整支影片照監控的方式跑一遍（同步、不照原速）。progress(done, total)。"""
    from core_detector import (DETECT_EVERY_N_FRAMES, HAND_MIN_INTERVAL_SEC, BoxStateRunner, FrameContext, HandTracker, SOPStateMachine,
                               limit_torch_threads, union_rect)
    from scene import SceneTracker
    from video_recorder import VideoFileSource
    if not project.steps:
        raise ValueError("這個專案還沒有步驟")
    if not os.path.isfile(project.video_path):
        raise ValueError("這個專案沒有示範影片")
    if not os.path.isfile(items.model_path(project)) and any(s.type == "item" for s in project.steps):
        raise ValueError("這個專案還沒有可用的辨識模型")
    t_wall = time.perf_counter()
    fsm = SOPStateMachine(project, error_log_dir=None, sound_enabled=False)
    tracker = HandTracker(hand_model) if project.needs_hands else None
    scene = SceneTracker(project.anchors, tuple(project.work_area) if project.work_area else None)
    detector = None
    if project.anchors:
        from object_detector import ObjectDetector
        detector = ObjectDetector(yolo_weights, [a.prompt for a in project.anchors])
    gesture = None
    if project.gesture_model:
        from gesture_classifier import GestureClassifier, GestureStream, hand_frame_features
        gesture = GestureStream(GestureClassifier.load(os.path.join(project.dir_path, project.gesture_model)))
    runner = BoxStateRunner(project)
    if not runner.enabled:
        runner = None
    limit_torch_threads()
    src = VideoFileSource(project.video_path)
    fps = float(src.fps or project.fps or 30.0)
    total = int(getattr(src, "frame_count", 0) or 0)
    rb = RoundBuilder(project.steps, fps)
    timeline: list[list] = []
    sample_every = max(1, project.state_every_n_frames)
    frames = 0; last_hand_t = -1.0; printed = 0; prev_acc: dict[int, float] = {}; t_now = 0.0
    try:
        while True:
            if should_stop is not None and should_stop():
                raise RuntimeError("已取消")
            frame = src.read()
            if frame is None:
                break
            t_now = src.time_sec
            if tracker is None:
                points = []
            elif frames % DETECT_EVERY_N_FRAMES and t_now - last_hand_t < HAND_MIN_INTERVAL_SEC:
                points = tracker.last_points
            else:
                last_hand_t = t_now
                points = tracker.detect(frame, int(t_now * 1000))
            if detector is not None and frames % max(1, project.detect_every_n_frames) == 0:
                scene.update_detections(detector.detect(frame), t_now)
            anchors = scene.anchors_at(t_now)
            probs = {}
            if gesture is not None:
                refs = [union_rect(anchors.get(n, [])) for n in project.gesture_anchors]
                probs = dict(gesture.push(hand_frame_features(tracker.last_hands_xy if tracker else [], refs, (frame.shape[1], frame.shape[0]))))
            box_state = None
            if runner is not None:
                age = scene.age(project.state_anchor, t_now) if project.state_anchor else None
                box_state = runner.update(frame, anchors, points, anchor_age=age, t_now=t_now)
                anchors = runner.with_items(anchors, t_now)
            ctx = FrameContext(hand_points=points, hands_xy=tracker.last_hands_xy if tracker else [], anchors=anchors, gesture_probs=probs,
                               box_state=box_state, items_present=set(runner.items_present) if runner is not None else set(),
                               box_open=runner.box_open if runner is not None else None,
                               box_seen=runner.box_seen if runner is not None else False)
            fsm.update(frame, ctx, t_now)
            rb.on_frame(fsm)
            while printed < len(fsm.events):
                rb.on_event(fsm.events[printed], fsm); printed += 1
            if fsm.alert_active:
                fsm.reset()                                  # 離線分析：警告記下來就好，馬上解除繼續看下一輪
            if frames % sample_every == 0:
                doing = [i for i, v in fsm.acc_sec.items() if v > prev_acc.get(i, 0.0) + 1e-6] if fsm.mode == "checklist" else []
                prev_acc = dict(fsm.acc_sec)
                timeline.append([round(t_now, 2), sorted(ctx.items_present), sorted(doing)])
            frames += 1
            if progress is not None and frames % 30 == 0:
                progress(frames, total)
    finally:
        if tracker is not None:
            tracker.close()
        src.release()
    mp = items.model_path(project)
    result = {"version": VERSION, "fingerprint": fingerprint(project), "fps": fps, "frames": frames,
              "model": os.path.relpath(mp, os.path.dirname(project.dir_path)).replace("\\", "/") if os.path.isfile(mp) else None,
              "steps": [{"index": s.step_index, "name": s.step_name, "type": s.type, "label": s.label or s.object or "",
                         "required": s.required} for s in project.steps],
              "rounds": rb.finish(t_now), "timeline": timeline,
              "elapsed_sec": round(time.perf_counter() - t_wall, 1), "analyzed_at": time.strftime("%Y/%m/%d %H:%M")}
    path = os.path.join(project.dir_path, ANALYSIS_FILE)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False)
    os.replace(tmp, path)
    result["stale"] = False
    return result
