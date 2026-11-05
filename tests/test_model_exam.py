"""訓練完新舊模型比較（model_exam）：出考卷、考卷畫面不進訓練、考試、判好壞、換上／不換上。不訓練模型。"""
from __future__ import annotations

import json
import os
from types import SimpleNamespace as NS

import numpy as np

import item_recognizer as ir
import model_exam as me


def _proj(d, fixed=(0, 0, 100, 100)):
    os.makedirs(os.path.join(str(d), "items", "model"), exist_ok=True)
    video = os.path.join(str(d), "demo.avi")
    if not os.path.isfile(video):
        with open(video, "wb") as f:
            f.write(b"v" * 10)
    return NS(project_name="p", dir_path=str(d), fps=10.0, state_fixed=list(fixed) if fixed else None, video_path=video,
              resolution=[100, 100], packaging=None)


def _seeds(d, rows, refs=(), order=None):
    with open(os.path.join(str(d), "items", "seeds.json"), "w", encoding="utf-8") as f:
        json.dump({"order": order or sorted({n for n, _ in rows}), "refs": list(refs), "closed": [],
                   "seeds": [{"name": n, "frame": fr, "rect": [10, 10, 20, 20], "auto": False, "group": i + 1} for i, (n, fr) in enumerate(rows)]},
                  f, ensure_ascii=False)
    return ir.ItemSeeds(str(d))


def test_ensure_takes_last_segment_and_freezes(tmp_path):
    p = _proj(tmp_path)        # fps 10 → 同物品相隔 30 格以上算另一段；延伸範圍 FIXED_WINDOW_SEC 2 秒＝20 格
    s = _seeds(tmp_path, [("貼紙", f) for f in (10, 12, 14, 200, 203, 206)] + [("鞋子", 20), ("鞋子", 300)], refs=[1, 2, 3, 4, 5])
    ex = me.ensure(p, s)
    assert set(ex["items"]) == {"貼紙", "鞋子"}
    assert [q[0] for q in ex["items"]["貼紙"]["questions"]] == [200, 203, 206] and ex["items"]["鞋子"]["start"] == 300
    assert ex["empty"] == [4, 5]                                 # 參考格後一半當空桌考題
    t = me.training_seeds(s, ex, me._margin(p))
    assert sorted(x.frame for x in t.seeds) == [10, 12, 14, 20] and t.refs == [1, 2, 3]
    assert len(ir.ItemSeeds(str(tmp_path)).seeds) == 8           # 只在記憶體裡篩，檔案沒動
    # 凍結：之後多框幾段，舊題目不變；新物品有兩段才補題
    s2 = _seeds(tmp_path, [("貼紙", f) for f in (10, 200, 500)] + [("鞋子", 20), ("鞋子", 300), ("防黴片", 30), ("防黴片", 400)], refs=[1, 2, 3, 4, 5])
    ex2 = me.ensure(p, s2)
    assert ex2["items"]["貼紙"]["start"] == 200 and "防黴片" in ex2["items"] and ex2["created_at"] == ex["created_at"]
    # 影片換了：重訂
    with open(p.video_path, "wb") as f:
        f.write(b"x" * 99)
    ex3 = me.ensure(p, s2)
    assert ex3["items"]["貼紙"]["start"] == 500
    assert me.ensure(_proj(tmp_path / "box", fixed=None), s2) is None      # 盒內模式不出考卷


def test_ensure_never_starves_an_item(tmp_path):
    p = _proj(tmp_path)
    # 盒子只有一段、剛好落在貼紙最後一段的範圍裡：貼紙那題不能出，不然盒子沒東西可訓練
    s = _seeds(tmp_path, [("貼紙", 10), ("貼紙", 200), ("盒子", 205)])
    ex = me.ensure(p, s)
    assert ex["items"] == {}
    assert me.question_count(ex) == 0


def test_only_one_segment_no_question(tmp_path):
    p = _proj(tmp_path)
    s = _seeds(tmp_path, [("貼紙", 10), ("貼紙", 12)], refs=[1])
    ex = me.ensure(p, s)
    assert ex["items"] == {} and ex["empty"] == []               # 參考格只有 1 格：留著訓練，不出空桌題


def test_score_with_fake_detector(tmp_path):
    p = _proj(tmp_path, fixed=(5, 5, 90, 90))
    exam = {"items": {"貼紙": {"start": 0, "end": 9, "questions": [[1, [15, 15, 20, 20]], [2, [15, 15, 20, 20]], [3, [60, 60, 10, 10]]]}},
            "empty": [7, 8]}

    class Det:
        names = ["貼紙"]
        def detect(self, crop):
            return [ir.ItemHit("貼紙", 0.9, (10, 10, 20, 20))]       # 裁圖座標＝畫面 (15,15)，跟前兩題重疊

    class Reader:
        def __init__(self, path): pass
        def get_frame(self, f): return np.zeros((100, 100, 3), np.uint8)
        def release(self): pass

    r = me.score(p, "x.pt", exam, detector=Det(), reader_factory=Reader)
    assert r["items"]["貼紙"] == {"n": 3, "hit": 2} and r["empty_n"] == 2 and r["fp"]["貼紙"] == 2


def _sc(hits, fps, n=20, empty=12, names=None):
    return {"names": names or list(hits), "items": {k: {"n": n, "hit": v} for k, v in hits.items()}, "empty_n": empty, "fp": dict(fps)}


def test_compare_rules():
    prev = _sc({"貼紙": 16, "標籤": 18}, {"貼紙": 0, "標籤": 1})
    assert me.compare(None, prev)["verdict"] == "first"
    c = me.compare(prev, _sc({"貼紙": 19, "標籤": 18}, {"貼紙": 0, "標籤": 1}))
    assert c["verdict"] == "better" and [r["verdict"] for r in c["rows"]] == ["better", "same"]
    assert me.compare(prev, _sc({"貼紙": 17, "標籤": 17}, {"貼紙": 0, "標籤": 1}))["verdict"] == "same"      # 差 5 點不算
    assert me.compare(prev, _sc({"貼紙": 14, "標籤": 18}, {"貼紙": 0, "標籤": 1}))["verdict"] == "same"      # 掉 10 點但只少 2 格：不算
    c = me.compare(prev, _sc({"貼紙": 13, "標籤": 18}, {"貼紙": 0, "標籤": 1}))
    assert c["verdict"] == "worse" and c["rows"][0]["d_hit"] == -15.0 and c["rows"][0]["hit_worse"]          # 少 3 格、掉 15 點
    assert me.compare(prev, _sc({"貼紙": 16, "標籤": 18}, {"貼紙": 0, "標籤": 2}))["verdict"] == "same"       # 誤報只多 1 格：不算
    c = me.compare(prev, _sc({"貼紙": 16, "標籤": 18}, {"貼紙": 0, "標籤": 3}))
    assert c["verdict"] == "worse" and c["rows"][1]["fp_worse"]                                               # 誤報多 2 格（12 格）升 17 點
    c = me.compare(prev, _sc({"貼紙": 16, "標籤": 18, "防黴片": 5}, {}), prev_saw=["貼紙"])
    assert c["rows"][2]["verdict"] == "new" and c["verdict"] == "same" and c["prev_saw"] == ["貼紙"]         # 新物品不比
    c = me.compare(_sc({"貼紙": 16}, {}, names=["貼紙"]), _sc({"貼紙": 16, "防黴片": 3}, {}))
    assert c["rows"][1]["verdict"] == "new"                                                                   # 舊模型不認得的名稱


def _job_env(tmp_path, monkeypatch, prev_score, new_score):
    import label_service
    p = _proj(tmp_path)
    _seeds(tmp_path, [("貼紙", 10), ("貼紙", 200)])
    md = os.path.join(p.dir_path, ir.MODEL_DIR)
    with open(os.path.join(md, "best.pt"), "wb") as f:
        f.write(b"old")
    with open(os.path.join(md, "candidate.pt"), "wb") as f:
        f.write(b"new")
    monkeypatch.setattr(label_service, "load_project", lambda n: p)
    monkeypatch.setattr(label_service.training, "sync_item_region", lambda proj: False)
    monkeypatch.setattr(me, "score", lambda proj, path, exam, **k: prev_score if path.endswith("best.pt") else new_score)
    job = label_service.TrainJob(); job._reset_state("p")
    me.ensure(p, ir.ItemSeeds(p.dir_path)); job._held_out = ["貼紙"]
    return job, p, md


def test_train_job_keeps_old_model_when_worse_then_force(tmp_path, monkeypatch):
    job, p, md = _job_env(tmp_path, monkeypatch, _sc({"貼紙": 16}, {"貼紙": 0}), _sc({"貼紙": 10}, {"貼紙": 0}))
    job._validate_install("p", os.path.join(md, "candidate.pt"), [])
    st = job.state()
    assert st["installed"] is False and st["candidate"] is True and st["compare"]["verdict"] == "worse"
    assert open(os.path.join(md, "best.pt"), "rb").read() == b"old" and "比上次差" in st["stage"]
    assert st["compare"]["history"][0]["installed"] is False
    st = job.install_candidate("p")
    assert st["installed"] is True and open(os.path.join(md, "best.pt"), "rb").read() == b"new"
    assert any(n.startswith("best_prev_") for n in os.listdir(md))
    info = json.load(open(os.path.join(md, "model_info.json"), encoding="utf-8"))
    assert info["exam"]["forced"] is True and info["exam"]["held_out"] == ["貼紙"] and me.history(p)[0]["forced"] is True
    assert me.held_out_items(p) == ["貼紙"]


def test_train_job_installs_when_better(tmp_path, monkeypatch):
    job, p, md = _job_env(tmp_path, monkeypatch, _sc({"貼紙": 16}, {"貼紙": 0}), _sc({"貼紙": 19}, {"貼紙": 0}))
    job._validate_install("p", os.path.join(md, "candidate.pt"), [])
    st = job.state()
    assert st["installed"] is True and st["candidate"] is False and st["compare"]["verdict"] == "better"
    assert st["compare"]["prev_saw"] == ["貼紙"]                 # 舊模型沒記扣掉哪些題：當作看過
    assert open(os.path.join(md, "best.pt"), "rb").read() == b"new" and "比上次好" in st["stage"]
