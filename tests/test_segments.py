"""標記頁時間軸：名稱／段落存檔、不重疊、刪除復原；物品段落存檔沿整段追框寫進 seeds；動作段落存檔判斷手碰到哪個物品；
產生步驟時動作變成 hand_on_object（物件＝自己訓練的物品）、監控時物品框併進錨點。"""
from __future__ import annotations

import json
import os
import sys

import cv2
import numpy as np
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import label_segments as ls
from item_recognizer import ItemSeeds


def _video_project(tmp_path, name="v", n=90, moving=True):
    """合成影片：深色背景、一個亮色方塊（moving＝每格往右移 1 px），90 格。回傳專案資料夾。"""
    d = tmp_path / name; d.mkdir()
    wr = cv2.VideoWriter(str(d / "demo.avi"), cv2.VideoWriter_fourcc(*"MJPG"), 30.0, (320, 240))
    for k in range(n):
        fr = np.full((240, 320, 3), 40, np.uint8)
        x = 60 + (k if moving else 0)
        cv2.rectangle(fr, (x, 80), (x + 80, 140), (40, 200, 230), -1)
        cv2.rectangle(fr, (x + 10, 90), (x + 30, 110), (0, 0, 180), -1)      # 方塊裡一個小色塊，追蹤有特徵
        wr.write(fr)
    wr.release()
    cfg = {"schema_version": 2, "project_name": name, "video_file": "demo.avi", "resolution": [320, 240], "fps": 30.0, "anchors": [], "zones": [], "steps": []}
    with open(d / "config.json", "w", encoding="utf-8") as f:
        json.dump(cfg, f)
    return str(d)


# ---------------------------------------------------------------- 資料

def test_segments_store_names_ranges_and_trash(tmp_path):
    s = ls.Segments(str(tmp_path))
    s.add_name("藍盒"); s.add_name("檢查鞋舌", "action")
    with pytest.raises(ValueError):
        s.add_name("藍盒")
    with pytest.raises(ValueError):
        s.add_name("x", "weird")
    a = s.add("藍盒", 10, 40, 300); b = s.add("藍盒", 60, 90, 300)
    with pytest.raises(ValueError):
        s.add("藍盒", 30, 70, 300)                   # 跟第 1、2 段重疊
    s.add("檢查鞋舌", 30, 70, 300)                    # 別的名稱可以同時
    s2 = ls.Segments(str(tmp_path))
    assert [x.name for x in s2.names] == ["藍盒", "檢查鞋舌"] and s2.name("檢查鞋舌").kind == "action"
    assert [(x.start, x.end) for x in s2.by_name("藍盒")] == [(10, 40), (60, 90)]
    seg, changed = s2.update_range(a.id, 5, 59, 300)
    assert changed and (seg.start, seg.end) == (5, 59)
    with pytest.raises(ValueError):
        s2.update_range(a.id, 5, 60, 300)            # 碰到第 2 段
    s2.set_box(a.id, 20, [10, 10, 50, 40])
    assert s2.get(a.id).box == [10, 10, 50, 40] and s2.get(a.id).box_frame == 20
    with pytest.raises(ValueError):
        s2.set_box(a.id, 100, [10, 10, 50, 40])      # 不在範圍裡
    s2.mark_saved(a.id, group=7, tracked=12)
    seg, changed = s2.update_range(a.id, 25, 59, 300)
    assert changed and seg.saved is False and seg.box is None   # 畫框那一格被切掉：框要重畫、要重存
    with pytest.raises(ValueError):
        s2.remove_name("藍盒")                        # 還有段落
    s2.remove(b.id, [{"name": "藍盒", "frame": 60, "rect": [1, 2, 3, 4], "auto": False, "group": 9, "by_model": False}])
    assert len(s2.by_name("藍盒")) == 1 and len(s2.trash) == 1
    s2.add("藍盒", 70, 80, 300)
    with pytest.raises(ValueError):
        s2.restore(300)                              # 位置被佔走
    s2.remove(s2.by_name("藍盒")[-1].id)
    r, rows = s2.restore(300)                        # 先還原剛刪的那一段（空的）
    assert (r.start, r.end) == (70, 80) and rows == []
    s2.remove(r.id)
    r, rows = s2.restore(300)
    assert (r.start, r.end) == (70, 80)
    assert s2.counts() == {"object_segments": 0, "object_frames": 0, "action_segments": 0}   # 改過範圍的那段變成未存
    s2.mark_saved(a.id, group=7, tracked=12)
    assert s2.counts() == {"object_segments": 1, "object_frames": 12, "action_segments": 0}


def test_infer_touch_rules():
    box = {"鞋子": [(100, 50, 120, 80)], "藍盒": [(300, 150, 100, 80)]}
    on_shoe = [(110.0, 60.0), (130.0, 70.0), (150.0, 80.0), (140.0, 90.0)]
    on_box = [(310.0, 160.0), (330.0, 170.0), (350.0, 180.0), (340.0, 190.0)]
    nowhere = [(10.0, 10.0), (20.0, 20.0), (30.0, 30.0), (40.0, 40.0)]
    hands = {0: on_shoe, 5: on_shoe, 10: on_box, 15: nowhere, 20: [], 25: on_shoe}
    boxes = {f: box for f in hands}
    name, st = ls.infer_touch(hands, boxes)
    assert name == "鞋子" and st["touched"] == {"鞋子": 3, "藍盒": 1} and st["with_hands"] == 5
    assert ls.infer_touch(hands, boxes) == (name, st)                     # 同資料同結果
    # 比例不夠（6 格有手只碰 1 格）→ None，理由說明得出來
    hands2 = {0: on_shoe, 5: nowhere, 10: nowhere, 15: nowhere, 20: nowhere, 25: nowhere}
    name2, st2 = ls.infer_touch(hands2, {f: box for f in hands2})
    assert name2 is None and "格數不夠" in ls.touch_reason(st2, ["鞋子", "藍盒"])
    assert "沒偵測到手" in ls.touch_reason(ls.infer_touch({0: [], 5: []}, {})[1], ["鞋子"])
    assert "沒有任何已框的物品" in ls.touch_reason(st2, [])
    # 平手取名稱排序在前的
    hands3 = {0: on_shoe, 5: on_shoe, 10: on_box, 15: on_box}
    assert ls.infer_touch(hands3, {f: box for f in hands3})[0] == "藍盒"


# ---------------------------------------------------------------- 追蹤

def test_track_segment_follows_moving_box(tmp_path):
    pdir = _video_project(tmp_path)
    out = ls.track_segment(os.path.join(pdir, "demo.avi"), 10, 70, 40, [100, 80, 80, 60], step=3)
    frames = [f for f, _ in out]
    assert 40 not in frames and min(frames) <= 13 and max(frames) >= 67 and len(frames) >= 16
    for f, (x, y, w, h) in out:
        assert abs(x - (60 + f)) <= 8 and abs(y - 80) <= 8 and 60 <= w <= 100 and 45 <= h <= 75, (f, x, y, w, h)


# ---------------------------------------------------------------- 服務：段落 → seeds／hand_steps

def test_service_object_segment_saves_tracked_seeds_and_restores(tmp_path):
    from label_service import LabelService
    pdir = _video_project(tmp_path); svc = LabelService()
    info = svc.project_info(pdir)
    assert info["segments"]["names"] == [] and info["frame_count"] == 90
    d = svc.segment_action(pdir, {"action": "add_name", "name": "藍盒", "kind": "object"})
    assert d["segments"]["names"][0]["kind"] == "object" and d["segments"]["names"][0]["color"]
    d = svc.segment_action(pdir, {"action": "add_segment", "name": "藍盒", "start": 10, "end": 70})
    sid = d["segment"]
    with pytest.raises(ValueError):
        svc.segment_action(pdir, {"action": "save_segment", "id": sid})          # 還沒畫框
    svc.segment_action(pdir, {"action": "set_box", "id": sid, "frame": 40, "rect": [100, 80, 80, 60]})
    d = svc.segment_action(pdir, {"action": "save_segment", "id": sid})
    assert d["tracked"] >= 15 and d["expected"] == 21 and d["region_set"] is True
    seg = d["segments"]["segments"][0]
    assert seg["saved"] and seg["group"] == 1 and seg["tracked"] == d["tracked"]
    seeds = ItemSeeds(pdir)
    assert seeds.region == [0, 0, 320, 240] and seeds.order == ["藍盒"]
    assert len(seeds.seeds) == d["tracked"] and all(s.group == 1 for s in seeds.seeds) and sum(not s.auto for s in seeds.seeds) == 1
    assert all(10 <= s.frame <= 70 for s in seeds.seeds)
    assert d["segments"]["object_segments"] == 1 and d["segments"]["object_frames"] == d["tracked"]
    # 改範圍：範圍外的框先丟掉、段落變未存
    d = svc.segment_action(pdir, {"action": "update_range", "id": sid, "start": 30, "end": 70})
    assert d["changed"] and not d["segments"]["segments"][0]["saved"] and all(30 <= s.frame for s in ItemSeeds(pdir).seeds)
    # 重存：重追
    d = svc.segment_action(pdir, {"action": "save_segment", "id": sid})
    n_after = len(ItemSeeds(pdir).seeds); assert n_after == d["tracked"] and d["expected"] == 14
    # 刪除 → seeds 跟著走；復原 → 回來
    d = svc.segment_action(pdir, {"action": "remove_segment", "id": sid})
    assert d["segments"]["segments"] == [] and ItemSeeds(pdir).seeds == [] and d["segments"]["trash"] == 1
    d = svc.segment_action(pdir, {"action": "restore_segment"})
    assert d["segments"]["segments"][0]["saved"] and len(ItemSeeds(pdir).seeds) == n_after
    # 名稱還有段落不能刪；刪了段落才能刪名稱
    with pytest.raises(ValueError):
        svc.segment_action(pdir, {"action": "remove_name", "name": "藍盒"})
    svc.segment_action(pdir, {"action": "remove_segment", "id": sid})
    d = svc.segment_action(pdir, {"action": "remove_name", "name": "藍盒"})
    assert d["segments"]["names"] == [] and ItemSeeds(pdir).order == []


def test_service_action_segment_infers_touch_and_generates_hand_step(tmp_path, monkeypatch):
    from label_service import LabelService
    import training
    from project_store import load_project
    pdir = _video_project(tmp_path, moving=False); svc = LabelService()
    svc.segment_action(pdir, {"action": "add_name", "name": "鞋子"})
    svc.segment_action(pdir, {"action": "add_name", "name": "檢查鞋舌", "kind": "action"})
    sid = svc.segment_action(pdir, {"action": "add_segment", "name": "鞋子", "start": 0, "end": 89})["segment"]
    svc.segment_action(pdir, {"action": "set_box", "id": sid, "frame": 30, "rect": [60, 80, 80, 60]})
    svc.segment_action(pdir, {"action": "save_segment", "id": sid})
    aid = svc.segment_action(pdir, {"action": "add_segment", "name": "檢查鞋舌", "start": 20, "end": 50})["segment"]
    # 手的點：假的（不跑 MediaPipe）。前半在鞋子框內、後半在別處
    on = [(70.0, 90.0), (90.0, 100.0), (110.0, 120.0), (100.0, 110.0)]
    off = [(250.0, 200.0), (260.0, 210.0), (270.0, 220.0), (280.0, 230.0)]
    monkeypatch.setattr(LabelService, "_hands_for_frames", lambda self, p, frames: {f: (on if f <= 40 else off) for f in frames})
    d = svc.segment_action(pdir, {"action": "save_segment", "id": aid})
    assert d["touch"] == "鞋子" and d["stats"]["with_hands"] == 7 and d["stats"]["touched"] == {"鞋子": 5}
    assert d["segments"]["names"][1]["touch"] == "鞋子" and d["segments"]["action_segments"] == 1
    hs = ItemSeeds(pdir).hand_steps
    assert hs == [{"name": "檢查鞋舌", "prompt": "", "dwell": ls.ACTION_DWELL_SEC, "item": "鞋子"}]
    # 手都不在鞋子上 → 擋下來、理由白話
    aid2 = svc.segment_action(pdir, {"action": "add_segment", "name": "檢查鞋舌", "start": 60, "end": 80})["segment"]
    monkeypatch.setattr(LabelService, "_hands_for_frames", lambda self, p, frames: {f: off for f in frames})
    with pytest.raises(ValueError) as ei:
        svc.segment_action(pdir, {"action": "save_segment", "id": aid2})
    assert "沒有落在任何已框的物品上" in str(ei.value)
    # 產生步驟：鞋子＝item、檢查鞋舌＝hand_on_object（object＝鞋子，不加 YOLO-World 錨點）；設定檔讀得回來
    training.apply_item_steps(load_project(pdir), ItemSeeds(pdir).order)
    p = load_project(pdir)
    assert [(s.type, s.step_name) for s in p.steps] == [("item", "鞋子"), ("hand_on_object", "檢查鞋舌")]
    assert p.steps[1].object == "鞋子" and p.steps[1].continuous and p.steps[1].dwell_time_sec == ls.ACTION_DWELL_SEC
    assert [a.name for a in p.anchors] == ["box"] and p.needs_hands
    # 刪掉動作的段落 → 手部步驟也拿掉
    svc.segment_action(pdir, {"action": "remove_segment", "id": aid})
    svc.segment_action(pdir, {"action": "remove_segment", "id": aid2})
    assert ItemSeeds(pdir).hand_steps == []
    svc.segment_action(pdir, {"action": "restore_segment"}); svc.segment_action(pdir, {"action": "restore_segment"})
    assert ItemSeeds(pdir).hand_steps[0]["item"] == "鞋子"


def test_legacy_seeds_become_names(tmp_path):
    from label_service import LabelService
    pdir = _video_project(tmp_path)
    s = ItemSeeds(pdir); s.add_seed("標籤", 10, (100, 80, 80, 60)); s.add_hand_step("檢查", "shoe", 0.7)
    info = LabelService().project_info(pdir)
    assert [(n["name"], n["kind"], n["touch"]) for n in info["segments"]["names"]] == [("標籤", "object", None), ("檢查", "action", "shoe")]


# ---------------------------------------------------------------- 監控：物品框併進錨點

def test_runner_with_items_keeps_recent_boxes(tmp_path):
    from core_detector import BoxStateRunner, FrameContext, SOPStateMachine
    from item_recognizer import ItemHit
    from project_store import project_from_dict
    cfg = {"schema_version": 2, "project_name": "r", "video_file": "demo.avi", "resolution": [400, 240], "fps": 30.0,
           "anchors": [{"name": "box", "prompt": "blue box", "max_age_sec": 1.0}], "zones": [], "state_anchor": "box", "state_fixed": [20, 10, 300, 200],
           "state_every_n_frames": 1, "cycle_end": {"type": "object_absent", "object": "box", "hold_sec": 0.5}, "cycle_min_sec": 0.0,
           "steps": [{"step_index": 0, "step_name": "鞋子", "type": "item", "label": "鞋子", "dwell_time_sec": 0.2, "timeout_sec": 60},
                     {"step_index": 1, "step_name": "檢查鞋舌", "type": "hand_on_object", "object": "鞋子", "dwell_time_sec": 0.7, "timeout_sec": 60, "continuous": True}]}
    p = project_from_dict(cfg, str(tmp_path))
    assert p.steps[1].object == "鞋子"                                     # object 可以是 item 步驟的物品
    runner = BoxStateRunner(p)

    class Det:
        def __init__(self): self.hits = []
        def detect(self, crop): return self.hits
    runner.items = Det(); runner.fixed_items = True
    fr = np.zeros((240, 400, 3), np.uint8)
    runner.items.hits = [ItemHit("鞋子", 0.9, (10, 20, 100, 80))]
    runner.update(fr, {}, [], t_now=1.0)
    a = runner.with_items({"box": [(0, 0, 50, 50)]}, 1.0)
    assert a == {"鞋子": [(30, 30, 100, 80)], "box": [(0, 0, 50, 50)]}      # 換算成畫面座標（加上固定範圍的左上角）
    runner.items.hits = []
    runner.update(fr, {}, [], t_now=1.5)
    assert runner.with_items({}, 1.5) == {"鞋子": [(30, 30, 100, 80)]}       # 沒偵測到：1 秒內沿用
    assert runner.with_items({}, 2.5) == {}                                 # 太久沒看到就不給
    # 狀態機：手的點落在鞋子框內連續 0.7 秒 → 檢查鞋舌成立
    fsm = SOPStateMachine(p, sound_enabled=False); t = 0.0
    on = [(40.0, 40.0), (60.0, 50.0), (80.0, 60.0), (70.0, 70.0)]
    for _ in range(30):
        fsm.update(None, FrameContext(anchors={"鞋子": [(30, 30, 100, 80)], "box": [(0, 0, 50, 50)]}, hand_points=on, items_present={"鞋子"}), t); t += 1 / 30
    assert {0, 1} <= fsm.observed


def test_hand_step_rejects_without_object(tmp_path):
    s = ItemSeeds(str(tmp_path))
    with pytest.raises(ValueError):
        s.add_hand_step("x", "", 0.7)
    s.add_hand_step("x", "", 0.7, item="鞋子"); s.add_hand_step("y", "shoe", 0.7)
    assert ItemSeeds(str(tmp_path)).hand_steps == [{"name": "x", "prompt": "", "dwell": 0.7, "item": "鞋子"}, {"name": "y", "prompt": "shoe", "dwell": 0.7}]
