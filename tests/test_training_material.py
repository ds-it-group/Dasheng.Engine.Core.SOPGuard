"""訓練素材：分段、篩框、留驗證段、合併資料集、離線驗證、刪框、web 路由。不訓練模型。"""
from __future__ import annotations

import json
import os

import numpy as np
import pytest

import item_recognizer as ir
import training_material as tm


class _P:
    def __init__(self, d, fps=10.0, fixed=(0, 0, 40, 30)):
        self.dir_path = str(d); self.fps = fps; self.state_fixed = list(fixed) if fixed else None
        self.video_path = os.path.join(self.dir_path, "demo.avi"); self.packaging = None


def _seeds(d, rows):
    os.makedirs(os.path.join(d, "items"), exist_ok=True)
    with open(os.path.join(d, "items", "seeds.json"), "w", encoding="utf-8") as f:
        json.dump({"order": ["盒", "貼紙"], "refs": [], "closed": [], "seeds": [
            {"name": n, "frame": fr, "rect": [1, 1, 10, 10], "auto": a, "group": 1} for n, fr, a in rows]}, f, ensure_ascii=False)
    return ir.ItemSeeds(str(d))


def test_segments_split_by_gap_and_counts(tmp_path):
    s = _seeds(tmp_path, [("盒", 10, False), ("盒", 12, True), ("貼紙", 20, False), ("盒", 80, True), ("貼紙", 85, False)])
    segs = tm.segments(_P(tmp_path), s)                       # fps 10 → 3 秒 = 30 格
    assert [(x["start"], x["end"]) for x in segs] == [(10, 20), (80, 85)]
    assert segs[0]["items"] == {"盒": {"manual": 1, "auto": 1}, "貼紙": {"manual": 1, "auto": 0}} and segs[0]["manual"] == 2
    assert segs[1]["key"]["盒"]["auto"] is True and segs[1]["key"]["貼紙"]["frame"] == 85
    f = tm.filtered_seeds(s, [(0, 30), (70, 90)], [(70, 90)])
    assert [x.frame for x in f.seeds] == [10, 12, 20] and len(s.seeds) == 5
    f.save()                                                   # 篩過的不會寫回檔案
    assert len(ir.ItemSeeds(str(tmp_path)).seeds) == 5


def test_pick_holdout_keeps_last_per_color_only_if_two():
    sel = [{"project": "a", "start": 10, "end": 20, "color": "黑白"}, {"project": "a", "start": 80, "end": 90, "color": "黑白"},
           {"project": "b", "start": 5, "end": 9, "color": "全白"}]
    hold = tm.pick_holdout(sel)
    assert hold == [{"project": "a", "start": 80, "end": 90, "color": "黑白"}]


def test_merge_datasets_remaps_classes(tmp_path):
    def ds(name, names, label):
        d = tmp_path / name
        for s in ("train", "val"):
            (d / "images" / s).mkdir(parents=True); (d / "labels" / s).mkdir(parents=True)
        (d / "images" / "train" / "f000001.jpg").write_bytes(b"x")
        (d / "labels" / "train" / "f000001.txt").write_text(label, encoding="utf-8")
        return str(d), names
    a = ds("a", ["盒", "貼紙"], "1 0.5 0.5 0.1 0.1\n")
    b = ds("b", ["鞋子", "盒"], "0 0.5 0.5 0.2 0.2\n1 0.4 0.4 0.1 0.1\n")
    out = tmp_path / "mix"
    st = tm.merge_datasets([a, b], str(out), ["盒", "貼紙", "鞋子"])
    assert st["train"] == 2
    assert (out / "labels" / "train" / "p0_f000001.txt").read_text(encoding="utf-8").split()[0] == "1"
    rows = (out / "labels" / "train" / "p1_f000001.txt").read_text(encoding="utf-8").splitlines()
    assert [r.split()[0] for r in rows] == ["2", "0"]
    assert "2: 鞋子" in (out / "data.yaml").read_text(encoding="utf-8")


def test_recolor_augment_and_gpu_package(tmp_path):
    import cv2, zipfile
    d = tmp_path / "ds"
    for s in ("train", "val"):
        (d / "images" / s).mkdir(parents=True); (d / "labels" / s).mkdir(parents=True)
    img = np.full((100, 100, 3), (200, 120, 30), np.uint8)          # 藍色背景（飽和）
    img[30:70, 30:70] = (20, 20, 20)                                  # 黑鞋
    cv2.imencode(".jpg", img)[1].tofile(str(d / "images" / "train" / "f1.jpg"))
    (d / "labels" / "train" / "f1.txt").write_text("1 0.5 0.5 0.6 0.6\n", encoding="utf-8")
    cv2.imencode(".jpg", img)[1].tofile(str(d / "images" / "train" / "f2.jpg"))
    (d / "labels" / "train" / "f2.txt").write_text("0 0.5 0.5 0.2 0.2\n", encoding="utf-8")   # 沒有鞋子類 → 不做
    r = tm.recolor_augment(str(d), ["盒", "鞋子在盒上"], ["鞋子在盒上"], per_image=2)
    assert r["added"] == 2 and sum(r["per_mode"].values()) == 2
    made = sorted(p.name for p in (d / "images" / "train").iterdir() if p.name.startswith("rc_"))
    assert len(made) == 2 and all((d / "labels" / "train" / (os.path.splitext(m)[0] + ".txt")).is_file() for m in made)
    out = cv2.imdecode(np.fromfile(str(d / "images" / "train" / made[0]), np.uint8), cv2.IMREAD_COLOR)
    assert abs(int(out[50, 50].mean()) - 20) > 25                       # 鞋子顏色變了
    assert np.abs(out[5, 5].astype(int) - np.array([200, 120, 30])).max() < 20     # 框外的藍色沒動
    assert tm.recolor_augment(str(d), ["盒"], ["鞋子在盒上"])["added"] == 0
    assert tm.default_recolor_classes(["藍盒", "鞋子在盒上", "檢查鞋舌"]) == ["鞋子在盒上"]
    script = tmp_path / "train_items.py"; script.write_text("print(1)", encoding="utf-8")
    z = tm.write_gpu_package(str(d), str(tmp_path / "pkg.zip"), str(tmp_path / "none.pt"), str(script),
                             {"names": ["盒", "鞋子在盒上"], "holdout": [], "recolor_classes": ["鞋子在盒上"], "recolor_added": 2}, 30, 960)
    with zipfile.ZipFile(z) as zf:
        names = zf.namelist()
        yaml = zf.read("dataset/data.yaml").decode("utf-8")
    assert "dataset/images/train/f1.jpg" in names and "train_items.py" in names and "plan.json" in names and all("\\" not in n for n in names)
    assert "path:" not in yaml and "1: 鞋子在盒上" in yaml


def test_import_model_requires_plan(tmp_path, monkeypatch):
    import label_service
    d = tmp_path / "p"; (d / "items" / "model").mkdir(parents=True)
    from types import SimpleNamespace as NS
    monkeypatch.setattr(label_service, "load_project", lambda n: NS(project_name=n, dir_path=str(d), packaging=None))
    job = label_service.TrainJob()
    with pytest.raises(ValueError, match="計畫"):
        job.start_import("p", b"PK" + b"x" * 200_000)
    (d / "items" / "model" / "candidate_plan.json").write_text(json.dumps({"holdout": [], "train_images": 5}), encoding="utf-8")
    with pytest.raises(ValueError, match="best.pt"):
        job.start_import("p", b"not a model")
    monkeypatch.setattr(label_service.TrainJob, "_validate_install", lambda self, t, m, h: None)
    assert job.start_import("p", b"PK" + b"x" * 200_000) == {"holdout": []}
    job._thread.join(2)
    assert (d / "items" / "model" / "candidate.pt").is_file()


def test_validate_holdout_with_fake_detector(tmp_path):
    class Det:
        def detect(self, crop):
            return [ir.ItemHit("盒", 0.9, (0, 0, 5, 5))]

    class Reader:
        def __init__(self, path): pass
        def get_frame(self, f): return np.zeros((30, 40, 3), np.uint8)
        def release(self): pass

    segs = [{"start": 0, "end": 20, "color": "黑白", "items": {"盒": {}, "貼紙": {}}}]
    r = tm.validate_holdout(_P(tmp_path), "x.pt", segs, detector=Det(), reader_factory=Reader)
    assert r[0]["ok"] is False and r[0]["missing"] == ["貼紙"] and r[0]["hits"]["盒"] == 5
    r = tm.validate_holdout(_P(tmp_path, fixed=None), "x.pt", segs, detector=Det(), reader_factory=Reader)
    assert r[0]["ok"] is None                                  # 盒內模式不支援


def test_video_color_and_remove_indices(tmp_path):
    p = _P(tmp_path)
    assert tm.video_color(p) == ""
    tm.set_video_color(p, " 黑白 ")
    assert tm.video_color(p) == "黑白"
    from label_service import LabelService
    import cv2
    d = tmp_path / "v"; d.mkdir()
    wr = cv2.VideoWriter(str(d / "demo.avi"), cv2.VideoWriter_fourcc(*"MJPG"), 30.0, (64, 48))
    for _ in range(10):
        wr.write(np.full((48, 64, 3), 90, np.uint8))
    wr.release()
    with open(d / "config.json", "w", encoding="utf-8") as f:
        json.dump({"schema_version": 2, "project_name": "v", "video_file": "demo.avi", "resolution": [64, 48], "fps": 30.0,
                   "anchors": [], "zones": [], "steps": []}, f)
    _seeds(d, [("盒", 1, False), ("盒", 2, True), ("貼紙", 3, True)])
    svc = LabelService()
    out = svc.seed_action(str(d), {"action": "remove_indices", "indices": [1, 2]})
    assert [s["frame"] for s in out["seeds"]] == [1]
    with pytest.raises(ValueError):
        svc.seed_action(str(d), {"action": "remove_indices", "indices": [5]})
    jpg = svc.frame_jpeg(str(d), 1, 200, box=[10, 10, 20, 20], zoom=True)
    assert jpg[:2] == b"\xff\xd8"


def test_web_lines_and_methods_routes(tmp_path, monkeypatch):
    import threading
    import urllib.request
    import lines as line_store
    import packing_methods as pkg
    import project_store
    import web_server
    from test_web import _StubService, _post
    pdir = tmp_path / "sop_projects"; pdir.mkdir()
    monkeypatch.setattr(project_store, "projects_dir", lambda: str(pdir))
    monkeypatch.setattr(pkg, "projects_dir", lambda: str(pdir))
    monkeypatch.setattr(line_store, "app_base_dir", lambda: str(tmp_path))
    from test_packing_lines import _proj
    _proj(pdir, "a", {"style": "RN-2601", "region": "歐洲"}, model=True)
    srv = web_server.make_server(_StubService(), "127.0.0.1", 0)
    th = threading.Thread(target=srv.serve_forever, daemon=True); th.start()
    base = f"http://127.0.0.1:{srv.server_address[1]}"
    try:
        for page in ("/methods", "/eip.css", "/pcset.js"):
            with urllib.request.urlopen(base + page, timeout=5) as r:
                assert r.status == 200
        for old, to in (("/lines", "/?pcset=1"), ("/new?style=X", "/label?new=1&style=X")):      # 11-06 併掉的頁面轉走
            with urllib.request.urlopen(base + old, timeout=5) as r:
                assert r.status == 200 and r.url == base + to
        st, d = _post(base + "/api/lines/save", {"line": {"name": "包裝 9 線", "camera": "0"}}); assert st == 200 and d["line"]["name"] == "包裝 9 線"
        lid = d["line"]["id"]
        st, d = _post(base + "/api/lines/switch", {"line": lid, "project": "a", "color": "黑白"})
        assert st == 200 and d["line"]["project"] == "a" and d["line"]["trial"] is True and d["restarted"] is False
        with urllib.request.urlopen(base + "/api/methods", timeout=5) as r:
            rows = json.loads(r.read())["methods"]
        assert rows[0]["lines"] == ["包裝 9 線"] and rows[0]["colors"][0]["name"] == "黑白"     # 換線時的新配色自動記成未驗證
        st, d = _post(base + "/api/method/packaging", {"name": "a", "packaging": {"region": ""}}); assert st == 400
        st, d = _post(base + "/api/start", {"line": lid, "source": "camera"}); assert st == 200
        st, d = _post(base + "/api/lines/nope", {}); assert st == 400
    finally:
        srv.shutdown(); srv.server_close()
