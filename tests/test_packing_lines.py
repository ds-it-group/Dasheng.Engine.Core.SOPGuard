"""型體＋地區包裝方式、模型參考、配色驗證、產線與換線。全部在 tmp 資料夾，不碰 sop_projects。"""
from __future__ import annotations

import json
import os

import pytest

import item_recognizer as ir
import lines as line_store
import packing_methods as pkg
import project_store


def _proj(base, name, packaging=None, steps=True, model=False):
    d = base / name; d.mkdir()
    cfg = {"schema_version": 2, "project_name": name, "video_file": "demo.avi", "resolution": [400, 240], "fps": 30.0,
           "anchors": [], "zones": [], "state_fixed": [0, 0, 400, 240],
           "steps": [{"step_index": 0, "step_name": "藍盒", "dwell_time_sec": 0.5, "timeout_sec": 120, "type": "item", "label": "藍盒"},
                     {"step_index": 1, "step_name": "貼紙", "dwell_time_sec": 0.5, "timeout_sec": 120, "type": "item", "label": "貼紙"}] if steps else []}
    if packaging is not None:
        cfg["packaging"] = packaging
    with open(d / "config.json", "w", encoding="utf-8") as f:
        json.dump(cfg, f, ensure_ascii=False)
    (d / "items").mkdir()
    with open(d / "items" / "seeds.json", "w", encoding="utf-8") as f:
        json.dump({"order": ["藍盒", "貼紙", "鞋子"], "refs": [], "closed": [], "seeds": []}, f, ensure_ascii=False)
    if model:
        (d / "items" / "model").mkdir()
        (d / "items" / "model" / "best.pt").write_bytes(b"x")
    return str(d)


@pytest.fixture
def base(tmp_path, monkeypatch):
    pdir = tmp_path / "sop_projects"; pdir.mkdir()
    monkeypatch.setattr(project_store, "projects_dir", lambda: str(pdir))
    monkeypatch.setattr(pkg, "projects_dir", lambda: str(pdir))
    monkeypatch.setattr(line_store, "app_base_dir", lambda: str(tmp_path))
    return pdir


def test_packaging_roundtrip_and_validation(base):
    _proj(base, "a", {"style": "RN-2601", "region": "歐洲", "customer": "客戶 A", "colors": [{"name": "黑白", "status": "verified"}]})
    p = project_store.load_project("a")
    assert p.packaging.style == "RN-2601" and p.packaging.colors[0].status == "verified"
    project_store.save_project(p)
    with open(base / "a" / "config.json", encoding="utf-8") as f:
        assert json.load(f)["packaging"]["region"] == "歐洲"
    _proj(base, "old")                                                   # 舊專案沒有 packaging
    assert project_store.load_project("old").packaging is None
    with pytest.raises(project_store.ProjectConfigError):
        project_store.parse_packaging({"style": "", "region": "歐洲"})
    with pytest.raises(project_store.ProjectConfigError):
        project_store.parse_packaging({"style": "x", "region": "y", "model_source": "a"}, "a")      # 參考自己
    with pytest.raises(project_store.ProjectConfigError):
        project_store.parse_packaging({"style": "x", "region": "y", "colors": [{"name": "黑", "status": "ok"}]})


def test_unique_key_model_source_and_colors(base):
    _proj(base, "a", {"style": "RN-2601", "region": "歐洲"}, model=True)
    _proj(base, "b", {"style": "RN-2601", "region": "日本"})
    _proj(base, "c", {"style": "CT-3105", "region": "美國"})
    with pytest.raises(ValueError, match="已經有包裝方式"):
        pkg.set_packaging("b", {"region": "歐洲"})
    with pytest.raises(ValueError, match="還沒有訓練好的模型"):
        pkg.set_packaging("a", {"model_source": "c"})
    row = pkg.set_packaging("b", {"model_source": "a"})
    assert row["model_source"] == "a" and row["model_trained_at"] and not row["own_model"]
    b = project_store.load_project("b")
    assert ir.model_path(b).endswith(os.path.join("a", "items", "model", "best.pt")) and ir.own_model_path(b).startswith(str(base / "b"))
    assert pkg.model_items(b) == ["藍盒", "貼紙", "鞋子"]
    assert pkg.color_status(b, "黑白") == "new" and pkg.is_trial(b, "黑白")
    pkg.set_color("b", "黑白", "verified")
    b = project_store.load_project("b")
    assert pkg.color_status(b, "黑白") == "verified" and not pkg.is_trial(b, "黑白") and b.packaging.colors[0].checked_at
    pkg.set_color("b", "黑白", "remove")
    assert project_store.load_project("b").packaging.colors == []
    _proj(base, "legacy")
    assert not pkg.is_trial(project_store.load_project("legacy"), "")     # 舊專案沒有型體地區，不分配色、不算試跑
    assert pkg.color_status(b, "") == "none" and not pkg.is_trial(b, "")  # 沒有配色這層（11-05）：沒指定配色就不算試跑


def test_update_steps(base):
    _proj(base, "a", {"style": "310222 01", "region": "歐洲", "customer": "客戶 A"}, model=True)
    assert not hasattr(pkg, "copy_method")                              # 「複製到其他型體」拿掉了：每個包裝方式都用自己的影片與模型
    assert pkg.method_detail("a")["step_rows"][0]["start_t"] is None     # 沒有時間軸段落的舊專案：沒有「第 1 段開始」
    row = pkg.update_steps("a", [{"index": 1, "name": "盒端貼紙", "label": "貼紙", "dwell": 0.3, "required": True},
                                 {"name": "鞋子放上", "label": "鞋子", "dwell": 0.5, "required": False}])
    p = project_store.load_project("a")
    assert row["steps"] == 2 and [s.step_name for s in p.steps] == ["盒端貼紙", "鞋子放上"] and p.steps[1].required is False
    with pytest.raises(ValueError, match="不在模型認得"):
        pkg.update_steps("a", [{"name": "x", "label": "不存在", "dwell": 0.5}])
    with pytest.raises(ValueError, match="重複"):
        pkg.update_steps("a", [{"name": "x", "label": "貼紙", "dwell": 0.5}, {"name": "x", "label": "鞋子", "dwell": 0.5}])
    rows = pkg.list_methods({"a": ["包裝 1 線"]})
    assert rows[0]["style"] == "310222 01" and rows[0]["lines"] == ["包裝 1 線"]


def test_lines_save_switch_mask_and_log(base, tmp_path):
    (tmp_path / "camera_source.txt").write_text("rtsp://admin:secret@192.168.1.10:554/stream1", encoding="utf-8")
    ls = line_store.load_lines()
    assert ls[0].name == "包裝 1 線" and ls[0].camera.startswith("rtsp://")          # 第一次用：沿用 camera_source.txt
    l = line_store.save_line({"id": ls[0].id, "name": "包裝 1 線", "camera": ls[0].camera, "table_region": [10, 10, 300, 200]})
    pub = line_store.line_public(l)
    assert pub["camera"] == "rtsp://admin:***@192.168.1.10:554/stream1" and pub["problem"] == "還沒指定包裝方式" and not pub["can_run"]
    line_store.save_line({"id": l.id, "camera": pub["camera"]})                    # 傳回遮過的字 → 保留原值
    assert line_store.get_line(l.id).camera.endswith("secret@192.168.1.10:554/stream1")
    _proj(base, "a", {"style": "RN-2601", "region": "歐洲", "colors": [{"name": "黑白", "status": "verified"}]}, model=True)
    _proj(base, "nomodel", {"style": "RN-2601", "region": "日本"})
    with pytest.raises(ValueError, match="還沒訓練"):
        line_store.switch_line(l.id, "nomodel")
    l = line_store.switch_line(l.id, "a", "黑白")
    pub = line_store.line_public(l)
    assert pub["can_run"] and pub["trial"] is False and pub["packaging"]["style"] == "RN-2601"
    l = line_store.switch_line(l.id, "a", pkg.NEW_COLOR)
    assert line_store.line_public(l)["trial"] is True
    with open(tmp_path / "logs" / "line_switch.csv", encoding="utf-8-sig") as f:
        rows = f.read().splitlines()
    assert rows[0].startswith("時間") and len(rows) == 3 and rows[2].endswith("新配色,是")
    l2 = line_store.save_line({"name": "包裝 2 線", "table_region": [0, 0, 999, 999]})
    with pytest.raises(ValueError, match="超出"):
        line_store.switch_line(l2.id, "a")
    with pytest.raises(ValueError, match="重複"):
        line_store.save_line({"name": "包裝 2 線"})
    line_store.delete_line(l2.id)
    assert [x.name for x in line_store.load_lines()] == ["包裝 1 線"]
    assert line_store.lines_by_project() == {"a": ["包裝 1 線"]}



def test_normalize_style_follows_company_rule():
    assert pkg.normalize_style("310222 01") == "310222 01"
    assert pkg.normalize_style(" 31022201 ") == "310222 01"
    assert pkg.normalize_style("310222-01") == "310222 01"
    for bad in ["RN-2601", "31022", "3102220", "310222 1", "", "310222 012"]:
        with pytest.raises(ValueError, match="6 碼"):
            pkg.normalize_style(bad)


def test_legacy_style_kept_until_changed(base):
    _proj(base, "old", {"style": "123456", "region": "美國"})
    pkg.set_packaging("old", {"style": "123456", "region": "日本"})           # 型體沒動：舊代碼照留
    assert project_store.load_project("old").packaging.style == "123456"
    with pytest.raises(ValueError, match="310222 01"):
        pkg.set_packaging("old", {"style": "12345", "region": "日本"})


def test_delete_only_disabled_and_unused(base):
    """停用的包裝方式可以刪；沒停用、產線在用、被參考模型、正在跑的都不行，而且有一個不行就全部不刪。"""
    _proj(base, "on", {"style": "111111 01", "region": "歐洲"})
    _proj(base, "off", {"style": "222222 01", "region": "歐洲", "enabled": False}, model=True)
    _proj(base, "off2", {"style": "333333 01", "region": "歐洲", "enabled": False})
    _proj(base, "ref", {"style": "444444 01", "region": "歐洲", "model_source": "off"})
    _proj(base, "bare")                                                        # 沒設定型體地區
    with pytest.raises(ValueError, match="請勾選"):
        pkg.delete_methods([])
    for names, kw, msg in ((["on"], {}, "沒有停用"), (["bare"], {}, "沒有停用"), (["nope"], {}, "找不到"),
                           (["off2"], {"lines_by_project": {"off2": ["包裝 1 線"]}}, "正在用"),
                           (["off2"], {"busy": ("off2",)}, "正在監控"),
                           (["off2", "off"], {}, "被 ref 參考")):
        with pytest.raises(ValueError, match=msg):
            pkg.delete_methods(names, **kw)
    assert (base / "off2").is_dir()                                            # 有一個不行 → off2 也沒被刪
    assert pkg.delete_methods(["off2"]) == ["off2"] and not (base / "off2").exists()
    pkg.set_packaging("ref", {"model_source": None})
    assert pkg.delete_methods(["off"]) == ["off"]
    assert sorted(project_store.list_projects()) == ["bare", "on", "ref"]