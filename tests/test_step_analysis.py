"""離線步驟分析：事件串成輪、實際作業順序、沒看到的步驟位置、結果過期判定。不跑影片與模型。"""
from __future__ import annotations

import json
import os
from types import SimpleNamespace as NS

import step_analysis as sa


def _steps():
    mk = lambda i, n, t="item", req=True: NS(step_index=i, step_name=n, type=t, label=n, object=None, required=req, dwell_time_sec=0.5, continuous=False)
    return [mk(0, "藍盒"), mk(1, "貼紙"), mk(2, "朝上", req=False), mk(3, "鞋子"), mk(4, "檢查鞋舌", "hand_on_object")]


class _FSM:
    mode = "checklist"; cycle_active = False; cycle_started_at = 0.0


def _ev(t, et, idx=""):
    return {"t": t, "event_type": et, "step_index": idx}


def test_round_builder_statuses_and_missing():
    rb = sa.RoundBuilder(_steps(), fps=10.0); f = _FSM()
    # 第 1 輪：先檢查鞋舌（清單最後一步）再拿盒子，完成
    for e in [_ev(1.0, "step_done", 4), _ev(2.0, "step_done", 0), _ev(4.0, "step_done", 1), _ev(6.0, "step_done", 3), _ev(7.0, "cycle_done")]:
        rb.on_event(e, f)
    # 太短被丟掉的輪
    for e in [_ev(8.0, "step_done", 0), _ev(8.5, "cycle_discarded")]:
        rb.on_event(e, f)
    # 第 2 輪：沒看到貼紙 → 漏做
    for e in [_ev(10.0, "step_done", 4), _ev(11.0, "step_done", 0), _ev(15.0, "step_done", 3), _ev(16.0, "alert_missing")]:
        rb.on_event(e, f)
    # 第 3 輪：影片結束前沒做完
    rb.on_event(_ev(20.0, "step_done", 4), f)
    rounds = rb.finish(22.0)
    assert [r["status"] for r in rounds] == ["完成", "漏做", "未完成"]
    assert rounds[0]["missing"] == [] and rounds[0]["start"] == 10 and rounds[0]["end"] == 70
    m = {x["name"]: x for x in rounds[1]["missing"]}
    assert set(m) == {"貼紙"}                                  # 選配的「朝上」不算
    assert (m["貼紙"]["from_t"], m["貼紙"]["to_t"]) == (11.0, 15.0) and m["貼紙"]["frame"] == 130 and m["貼紙"]["boxable"] is True
    m3 = {x["name"]: x for x in rounds[2]["missing"]}
    assert set(m3) == {"藍盒", "貼紙", "鞋子"} and m3["鞋子"]["to_t"] == 22.0


def test_typical_order_uses_completed_rounds():
    st = _steps()
    rounds = [{"status": "完成", "start_t": 0.0, "end_t": 10.0, "done": {"4": 0.0, "0": 2.0, "1": 5.0, "3": 9.0}}]
    order = sa.typical_order(rounds, st)
    assert order[4] < order[0] < order[1] < order[3]
    # 沒有完成的輪：照清單順序
    o2 = sa.typical_order([], st)
    assert o2[0] < o2[1] < o2[4]
    # 照清單順序推會夾錯（鞋舌在清單最後但最先做）→ 整輪；照實際順序就夾在藍盒與鞋子之間
    r = {"start_t": 10.0, "end_t": 16.0, "done": {"4": 10.0, "0": 11.0, "3": 15.0}}
    w_list = sa.missing_windows(r, st, 10.0)
    w_real = sa.missing_windows(r, st, 10.0, order)
    assert (w_list[0]["from_t"], w_list[0]["to_t"]) == (10.0, 16.0)
    assert (w_real[0]["from_t"], w_real[0]["to_t"]) == (11.0, 15.0)


def test_fingerprint_and_stale(tmp_path):
    d = tmp_path / "p"; (d / "items" / "model").mkdir(parents=True)
    (d / "demo.mp4").write_bytes(b"v" * 10); (d / "items" / "model" / "best.pt").write_bytes(b"m")
    p = NS(dir_path=str(d), video_path=str(d / "demo.mp4"), steps=_steps(), state_fixed=[0, 0, 10, 10], packaging=None)
    fp = sa.fingerprint(p)
    with open(d / sa.ANALYSIS_FILE, "w", encoding="utf-8") as f:
        json.dump({"version": sa.VERSION, "fingerprint": fp, "rounds": []}, f)
    assert sa.load(p)["stale"] is False
    p.steps[0].dwell_time_sec = 0.8                               # 改了步驟 → 過期
    assert sa.load(p)["stale"] is True
    p.steps[0].dwell_time_sec = 0.5
    os.utime(d / "items" / "model" / "best.pt", (1, 1))           # 模型換了 → 過期
    assert sa.load(p)["stale"] is True


def test_analysis_job_queues_other_projects(monkeypatch):
    import threading
    import label_service
    started = []
    gate = threading.Event()

    def fake_run(self, name):
        started.append(name); gate.wait(2)
    monkeypatch.setattr(label_service, "load_project", lambda n: NS(project_name=n))
    monkeypatch.setattr(label_service.AnalysisJob, "_run", fake_run)
    job = label_service.AnalysisJob()
    assert job.start("a") == {"queued": False}
    assert job.start("b") == {"queued": True} and job.start("b") == {"queued": True} and job.state()["queue"] == ["b"]
    assert job.start("a") == {"queued": False}                    # 同一個正在跑的不重複排
    gate.set()
