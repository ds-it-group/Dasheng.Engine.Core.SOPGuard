"""參照現有包裝方式：空專案一次帶入步驟、偵測設定、框選設定與模型；來源可以是沒設型體地區的舊專案。"""
from __future__ import annotations

import json
import os

import pytest

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


def _empty(base, name, res=(400, 240)):
    d = base / name; d.mkdir()
    with open(d / "config.json", "w", encoding="utf-8") as f:
        json.dump({"schema_version": 2, "project_name": name, "video_file": "demo.avi", "resolution": list(res), "fps": 30.0,
                   "anchors": [], "zones": [], "steps": []}, f)
    return str(d)


def test_adopt_into_empty_project_from_legacy_source(base):
    _proj(base, "legacy", None, model=True)                       # 舊專案：沒有型體地區、有自己的模型
    with open(base / "legacy" / "items" / "seeds.json", "w", encoding="utf-8") as f:
        json.dump({"order": ["藍盒", "貼紙"], "refs": [3], "closed": [], "seeds": [{"name": "藍盒", "frame": 3, "rect": [1, 1, 9, 9]}],
                   "region": [0, 0, 400, 240], "box_labels": ["藍盒"], "hand_steps": [{"name": "檢查", "prompt": "shoe", "dwell": 0.7}]}, f, ensure_ascii=False)
    _empty(base, "123456")
    r = pkg.adopt_method("123456", "legacy", {"style": "31022201", "region": "歐洲"})
    p = project_store.load_project("123456")
    assert [s.step_name for s in p.steps] == ["藍盒", "貼紙"] and p.state_fixed == [0, 0, 400, 240]
    assert p.packaging.style == "310222 01" and p.packaging.model_source == "legacy" and r["warnings"] == []
    assert ir.model_path(p).endswith(os.path.join("legacy", "items", "model", "best.pt")) and r["method"]["model_trained_at"]
    sd = ir.ItemSeeds(p.dir_path)
    assert sd.order == ["藍盒", "貼紙"] and sd.box_labels == ["藍盒"] and sd.region == [0, 0, 400, 240] and sd.seeds == [] and sd.refs == []
    assert sd.hand_steps[0]["name"] == "檢查"


def test_adopt_checks_and_resolution_mismatch(base):
    _proj(base, "src", {"style": "310222 01", "region": "歐洲"}, model=True)
    _empty(base, "big", res=(800, 600))
    with pytest.raises(ValueError, match="已經有包裝方式"):
        pkg.adopt_method("big", "src", {"style": "310222 01", "region": "歐洲"})
    with pytest.raises(ValueError, match="自己"):
        pkg.adopt_method("src", "src", {"style": "310222 02", "region": "x"})
    with pytest.raises(ValueError, match="型體"):
        pkg.adopt_method("big", "src", {"style": "", "region": "歐洲"})
    r = pkg.adopt_method("big", "src", {"style": "310222 02", "region": "歐洲"})
    p = project_store.load_project("big")
    assert p.state_fixed is None and p.steps == [] and len(r["warnings"]) == 2       # 畫面大小不同：桌面範圍與物品步驟都先不帶
    assert p.packaging.model_source == "src"
    # 只用模型、不帶步驟
    _empty(base, "m_only")
    pkg.adopt_method("m_only", "src", {"style": "310222 03", "region": "歐洲"}, copy_steps=False)
    assert project_store.load_project("m_only").steps == [] and project_store.load_project("m_only").packaging.model_source == "src"
