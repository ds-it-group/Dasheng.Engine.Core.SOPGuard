"""新增包裝方式精靈：建專案（型體_地區）、參照候選排序、精靈從哪一步繼續、自動標記（假模型、假影片）。"""
from __future__ import annotations

import json
from types import SimpleNamespace as NS

import numpy as np
import pytest

import auto_label as al
import item_recognizer as ir
import packing_methods as pkg
import project_store
from test_packing_lines import _proj


@pytest.fixture
def base(tmp_path, monkeypatch):
    pdir = tmp_path / "sop_projects"; pdir.mkdir()
    monkeypatch.setattr(project_store, "projects_dir", lambda: str(pdir))
    monkeypatch.setattr(pkg, "projects_dir", lambda: str(pdir))
    return pdir


def test_wizard_name_and_suggest_order(base):
    assert pkg.wizard_name("RN-26/03", "歐洲 ") == "RN-26-03_歐洲"
    _proj(base, "a", {"style": "RN-2601", "region": "歐洲", "customer": "客戶 A"}, model=True)
    _proj(base, "b", {"style": "CT-3105", "region": "美國", "customer": "客戶 B"}, model=True)
    _proj(base, "c", {"style": "RN-2602", "region": "日本", "customer": "客戶 A"})                     # 沒模型 → 不列
    _proj(base, "new", {"style": "RN-2603", "region": "歐洲", "customer": "客戶 A"}, steps=False)
    rows = pkg.suggest_sources("new")
    assert [r["name"] for r in rows] == ["a", "b"] and "同客戶" in rows[0]["why"] and rows[0]["score"] > rows[1]["score"]


def test_wizard_state_steps(base, tmp_path):
    _proj(base, "src", {"style": "A", "region": "歐洲"}, model=True)
    _proj(base, "w", {"style": "B", "region": "歐洲"}, steps=False)
    assert pkg.wizard_state("w")["step"] == 1                        # 沒有影片
    (base / "w" / "demo.avi").write_bytes(b"x")
    assert pkg.wizard_state("w")["step"] == 2                        # 沒有步驟
    pkg.adopt_method("w", "src", {})
    assert pkg.wizard_state("w")["step"] == 3                        # 還沒自動標記


def test_pick_refs_between_rounds():
    tl = [[t / 2, [] if (t < 6 or 20 < t < 30) else ["藍盒"], []] for t in range(0, 60)]   # 0～3 秒、10～15 秒沒東西
    rounds = [{"start_t": 3.0, "end_t": 10.0}, {"start_t": 15.0, "end_t": 30.0}]
    refs = al.pick_refs(tl, rounds, 30.0, [])
    assert refs and all(abs(f / 30 - 12.5) < 1.0 or f / 30 < 3 for f in refs)


def test_auto_label_boxes_each_done_step(tmp_path, monkeypatch):
    d = tmp_path / "p"; (d / "items").mkdir(parents=True)
    steps = [NS(step_index=0, type="item", label="藍盒"), NS(step_index=1, type="item", label="貼紙"), NS(step_index=2, type="hand_on_object", label=None)]
    p = NS(dir_path=str(d), fps=10.0, state_fixed=[10, 10, 100, 100], steps=steps, video_path=str(d / "demo.avi"))
    an = {"fps": 10.0, "rounds": [{"no": 1, "start_t": 1.0, "end_t": 5.0, "done": {"0": 2.0, "1": 3.0, "2": 1.5}}],
          "timeline": [[0.0, [], []], [0.5, [], []], [1.0, [], []], [6.0, [], []], [7.0, [], []], [8.5, [], []]]}

    class Det:
        def detect(self, crop):
            return [ir.ItemHit("藍盒", 0.9, (5, 5, 20, 20)), ir.ItemHit("貼紙", 0.2, (1, 1, 5, 5))]   # 貼紙分數太低 → 不採納

    class Reader:
        frame_count = 100
        def get_frame(self, f):
            return np.zeros((200, 200, 3), np.uint8)
    monkeypatch.setattr(ir, "track_seed", lambda path, f, rect, window_sec=2.0, fps=None: [(f + 3, rect), (f + 6, rect)])
    r = al.auto_label(p, Det(), an, Reader())
    assert r["boxes"] == 1 and r["tracked"] == 2 and r["missed"] == [{"round": 1, "label": "貼紙", "t": 3.0}] and r["jobs"] == 2
    sd = ir.ItemSeeds(str(d))
    assert [(s.name, s.by_model, s.auto) for s in sd.seeds] == [("藍盒", True, False), ("藍盒", True, True), ("藍盒", True, True)]
    assert sd.seeds[0].rect == [15, 15, 20, 20]                     # 裁圖座標換回整格座標
    assert sd.refs                                                  # 輪外沒東西的時段挑了空桌面參考
    r2 = al.auto_label(p, Det(), an, Reader())                      # 再跑一次：已經有框的不重複加
    assert r2["boxes"] == 0 and r2["skipped"] == 1
    with pytest.raises(ValueError, match="桌面範圍"):
        al.auto_label(NS(**{**p.__dict__, "state_fixed": None}), Det(), an, Reader())


def test_wizard_create_route(tmp_path, monkeypatch):
    import threading
    import label_service
    import web_server
    from test_web import _StubService, _post
    pdir = tmp_path / "sop_projects"; pdir.mkdir()
    monkeypatch.setattr(project_store, "projects_dir", lambda: str(pdir))
    monkeypatch.setattr(pkg, "projects_dir", lambda: str(pdir))
    monkeypatch.setattr(label_service, "projects_dir", lambda: str(pdir))
    srv = web_server.make_server(_StubService(), "127.0.0.1", 0, label=label_service.LabelService())
    th = threading.Thread(target=srv.serve_forever, daemon=True); th.start()
    base = f"http://127.0.0.1:{srv.server_address[1]}"
    try:
        st, d = _post(base + "/api/wizard/create", {"style": "31022209", "region": "歐洲", "customer": "客戶 A"})
        assert st == 200 and d["name"] == "310222 09_歐洲"
        st, d = _post(base + "/api/wizard/create", {"style": "31022209", "region": "歐洲"}); assert st == 200 and d["resumed"]   # 重新整理再按一次
        st, d = _post(base + "/api/wizard/create", {"style": "", "region": "歐洲"}); assert st == 400
        assert json.load(open(pdir / "310222 09_歐洲" / "config.json", encoding="utf-8"))["packaging"]["customer"] == "客戶 A"
    finally:
        srv.shutdown(); srv.server_close()
