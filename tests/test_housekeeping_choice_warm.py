"""舊紀錄留 30 天、記住上次選的模型、今天的模型先在背景轉好。"""
from __future__ import annotations

import csv
import os
import time
from datetime import datetime, timedelta

import housekeeping
import lines as line_store
import model_warm


def test_clean_project_keeps_30_days(tmp_path):
    d = tmp_path / "p" / "error_logs"; d.mkdir(parents=True)
    now = datetime(2026, 11, 5, 12)
    old_png, new_png = d / "alert_old.jpg", d / "alert_new.jpg"
    old_png.write_bytes(b"x"); new_png.write_bytes(b"x")
    t_old = (now - timedelta(days=31)).timestamp(); os.utime(old_png, (t_old, t_old))
    t_new = (now - timedelta(days=2)).timestamp(); os.utime(new_png, (t_new, t_new))
    with open(d / "events.csv", "w", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f); w.writerow(["t", "time_iso", "event_type", "step_index", "step_name", "message", "screenshot"])
        w.writerow([1, "2026-09-01T08:00:00", "cycle_done", "", "", "#1", ""])
        w.writerow([2, "2026-11-04T08:00:00", "alert_skip", 1, "貼紙", "x", ""])
        w.writerow([3, "看不懂", "cycle_done", "", "", "#3", ""])
    r = housekeeping.clean_project(str(tmp_path / "p"), now)
    assert r == {"files": 1, "rows": 1} and not old_png.exists() and new_png.exists()
    with open(d / "events.csv", encoding="utf-8-sig", newline="") as f:
        rows = list(csv.reader(f))
    assert rows[0][1] == "time_iso" and [x[0] for x in rows[1:]] == ["2", "3"]
    assert housekeeping.clean_project(str(tmp_path / "none"), now) == {"files": 0, "rows": 0}


def test_remember_and_last_choice(tmp_path, monkeypatch):
    monkeypatch.setattr(line_store, "app_base_dir", lambda: str(tmp_path))
    assert line_store.last_choice("310222 01", ["CB-1"]) is None
    line_store.remember_choice("310222 01", ["CB-1", "CB-2"], "310222 01_美洲")
    line_store.remember_choice("310222 01", ["CB-9"], "310222 01_歐洲")
    assert line_store.last_choice("310222 01", ["CB-2"]) == "310222 01_美洲"        # 同一張廠編選過的優先
    assert line_store.last_choice("310222 01", ["CB-5"]) == "310222 01_歐洲"        # 新的單：看這個型體上次選的
    assert line_store.last_choice("415118 02", []) is None


def test_warm_paths_once_per_model(tmp_path, monkeypatch):
    import torch
    monkeypatch.setattr(torch.cuda, "is_available", lambda: False)
    monkeypatch.setattr(model_warm, "_imgsz", lambda p: 960)
    m = tmp_path / "best.pt"; m.write_bytes(b"x")
    got = []
    conv = lambda p, sz: got.append((p, sz)) or "ok"
    assert model_warm.warm_paths([str(m), str(tmp_path / "missing.pt")], conv) == 1
    assert model_warm.warm_paths([str(m)], conv) == 0                               # 轉過的不重排
    for _ in range(50):
        if got:
            break
        time.sleep(0.05)
    assert got == [(str(m), 960)]
    t = time.time() + 5; os.utime(m, (t, t))                                        # 重訓（修改時間變了）：再排一次
    assert model_warm.warm_paths([str(m)], conv) == 1
