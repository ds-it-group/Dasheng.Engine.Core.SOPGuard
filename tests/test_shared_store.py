"""共用硬碟：版本資料夾＋current.txt、上傳／載入／退回、本機改過的判斷、撞號、模型檔壞了、參考模型一起載。全部在 tmp。"""
from __future__ import annotations

import json
import os
import time
import zipfile

import pytest

import project_store
import shared_store as sh
from test_packing_lines import _proj


def _zip_model(d):
    os.makedirs(os.path.join(d, "items", "model"), exist_ok=True)
    with zipfile.ZipFile(os.path.join(d, "items", "model", "best.pt"), "w") as z:
        z.writestr("data.pkl", b"x")


@pytest.fixture
def env(tmp_path, monkeypatch):
    pdir = tmp_path / "sop_projects"; pdir.mkdir()
    nas = tmp_path / "nas"; nas.mkdir()
    monkeypatch.setattr(project_store, "projects_dir", lambda: str(pdir))
    monkeypatch.setattr(sh, "projects_dir", lambda: str(pdir))
    monkeypatch.setattr(sh, "app_base_dir", lambda: str(tmp_path))
    monkeypatch.setattr(sh, "program_version", lambda: "abc1234")
    sh.set_root(str(nas))
    return pdir, nas


def test_upload_load_and_rollback(env):
    pdir, nas = env
    d = _proj(pdir, "310222 01_歐洲", {"style": "310222 01", "region": "歐洲"})
    _zip_model(d)
    with open(os.path.join(d, "items", "trace.json"), "w") as f:
        f.write("{}")                                                        # 追蹤快取不上傳
    with open(os.path.join(d, "items", "seeds_before_x.json"), "w") as f:
        f.write("{}")                                                        # 備份不上傳
    r = sh.upload("310222 01_歐洲", note="第一版")
    assert r["version"] == 1 and r["published"] and sh.current(str(nas), "310222 01_歐洲") == 1
    v1 = nas / "310222 01_歐洲" / "v1"
    assert (v1 / "items" / "model" / "best.pt").is_file() and not (v1 / "items" / "trace.json").exists() and not (v1 / "items" / "seeds_before_x.json").exists()
    info = json.loads((v1 / "version.json").read_text(encoding="utf-8"))
    assert info["note"] == "第一版" and info["program"] == "abc1234" and info["based_on"] is None and info["uploaded_at"].endswith("Z")
    assert sh.list_local()[0]["status"] == "same" and not sh.local_changed(d)
    # 本機改了 → 本機改過；再傳是 v2，based_on 1
    time.sleep(1.2)
    with open(os.path.join(d, "items", "seeds.json"), "a", encoding="utf-8") as f:
        f.write(" ")
    assert sh.local_changed(d) and sh.list_local()[0]["status"] == "local_changed"
    r = sh.upload("310222 01_歐洲")
    assert r["version"] == 2 and r["published"] and json.loads((nas / "310222 01_歐洲" / "v2" / "version.json").read_text(encoding="utf-8"))["based_on"] == 1
    # 退回 v1：只改 current.txt；本機是 v2 → 不是目前版本
    sh.set_current("310222 01_歐洲", 1)
    row = sh.list_shared()[0]
    assert row["current"] == 1 and [v["version"] for v in row["versions"]] == [2, 1] and row["status"] == "other" and row["style"] == "310222 01"
    with pytest.raises(ValueError, match="沒有 v9"):
        sh.set_current("310222 01_歐洲", 9)


def test_load_to_other_computer_keeps_model_and_times(env, tmp_path, monkeypatch):
    pdir, nas = env
    d = _proj(pdir, "a", {"style": "S1", "region": "歐洲"}); _zip_model(d)
    with open(os.path.join(d, "items", "segments.json"), "w") as f:
        f.write("{}")
    mt = os.path.getmtime(os.path.join(d, "items", "model", "best.pt"))
    sh.upload("a")
    # 換一台電腦：本機空的
    other = tmp_path / "other"; other.mkdir()
    monkeypatch.setattr(project_store, "projects_dir", lambda: str(other)); monkeypatch.setattr(sh, "projects_dir", lambda: str(other))
    assert sh.list_shared()[0]["status"] == "none"
    r = sh.load("a")
    assert r["version"] == 1 and (other / "a" / "items" / "model" / "best.pt").is_file()
    assert abs(os.path.getmtime(other / "a" / "items" / "model" / "best.pt") - mt) < 2           # 模型時間保留（清單上的「訓練 …」是真的訓練時間）
    assert sh.list_shared()[0]["status"] == "same" and not sh.local_changed(str(other / "a"))
    # 正在監控的不能更新
    with pytest.raises(ValueError, match="正在產線監控"):
        sh.load("a", running=("a",))
    # 載入舊版時，那一版沒有的同步檔要拿掉
    os.remove(os.path.join(d, "items", "segments.json"))
    monkeypatch.setattr(project_store, "projects_dir", lambda: str(pdir)); monkeypatch.setattr(sh, "projects_dir", lambda: str(pdir))
    time.sleep(1.2); open(os.path.join(d, "config.json"), "a").close(); os.utime(os.path.join(d, "config.json"))
    sh.upload("a")                                                                                   # v2 沒有 segments.json
    monkeypatch.setattr(project_store, "projects_dir", lambda: str(other)); monkeypatch.setattr(sh, "projects_dir", lambda: str(other))
    sh.load("a")
    assert not (other / "a" / "items" / "segments.json").exists()


def test_conflict_needs_confirm_and_version_bump(env, monkeypatch):
    pdir, nas = env
    d = _proj(pdir, "a", {"style": "S1", "region": "歐洲"}); _zip_model(d)
    sh.upload("a")                                       # v1
    # 別台傳了 v2（這台還是 v1）
    (nas / "a" / "v2").mkdir(); (nas / "a" / "v2" / "version.json").write_text('{"version": 2}', encoding="utf-8")
    sh.set_current("a", 2)
    time.sleep(1.2); os.utime(os.path.join(d, "config.json"))
    r = sh.upload("a")
    assert r["version"] == 3 and not r["published"] and r["needs_confirm"] and sh.current(str(nas), "a") == 2
    sh.set_current("a", 3)
    assert sh.current(str(nas), "a") == 3
    # 撞號：v4 已經被別台建了（還沒寫完也一樣），這台改用 v5
    (nas / "a" / "v4").mkdir()
    time.sleep(1.2); os.utime(os.path.join(d, "config.json"))
    assert sh.upload("a")["version"] == 5


def test_broken_model_and_referenced_project(env, tmp_path, monkeypatch):
    pdir, nas = env
    a = _proj(pdir, "a", {"style": "S1", "region": "歐洲"}); _zip_model(a)
    b = _proj(pdir, "b", {"style": "S1", "region": "美洲", "model_source": "a"})
    sh.upload("a"); sh.upload("b")
    other = tmp_path / "other"; other.mkdir()
    monkeypatch.setattr(project_store, "projects_dir", lambda: str(other)); monkeypatch.setattr(sh, "projects_dir", lambda: str(other))
    r = sh.load("b")
    assert [x["name"] for x in r["loaded"]] == ["b", "a"] and (other / "a" / "items" / "model" / "best.pt").is_file()   # 參考的模型一起載
    (nas / "a" / "v1" / "items" / "model" / "best.pt").write_bytes(b"broken")
    with pytest.raises(ValueError, match="模型檔壞了"):
        sh.load("a", 1)


def test_root_must_exist(env, tmp_path):
    with pytest.raises(ValueError, match="連不到"):
        sh.set_root(str(tmp_path / "nope"))
