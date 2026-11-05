"""訓練完用新模型重判動作：模型認得被碰的物品＝對得上；認不到或判成別的＝警示；重存動作就清掉舊結果。不跑真的模型。"""
from __future__ import annotations

import os
from types import SimpleNamespace as NS

import numpy as np

import action_recheck as ar
import item_recognizer as ir
import label_segments as ls


class Reader:
    def __init__(self, path): pass
    def get_frame(self, f): return np.zeros((240, 400, 3), np.uint8)
    def release(self): pass


def _proj(tmp_path):
    os.makedirs(tmp_path / "items", exist_ok=True)
    segs = ls.Segments(str(tmp_path))
    segs.add_name("鞋舌", "object"); segs.add_name("鞋子", "object"); segs.add_name("檢查鞋舌", "action")
    s = segs.add("檢查鞋舌", 0, 20, 100); segs.mark_saved(s.id, touch="鞋舌"); segs.save()
    return NS(dir_path=str(tmp_path), state_fixed=[50, 20, 300, 200], video_path=str(tmp_path / "demo.avi"))


HAND = [(120.0, 70.0), (130.0, 75.0), (140.0, 80.0), (135.0, 85.0)]          # 畫面座標，落在鞋舌（畫面 110,60,50,40）裡
HANDS = {f: HAND for f in range(0, 21, ir.TRACE_STEP)}


class SeesTongue:
    def detect(self, crop):                                                   # 裁圖座標：畫面 x−50、y−20
        return [ir.ItemHit("鞋子", 0.9, (40, 30, 160, 100)), ir.ItemHit("鞋舌", 0.8, (60, 40, 50, 40))]


class SeesOnlyShoe:
    def detect(self, crop):
        return [ir.ItemHit("鞋子", 0.9, (40, 30, 160, 100))]


class SeesNothing:
    def detect(self, crop):
        return []


def test_recheck_ok_wrong_and_missing(tmp_path):
    p = _proj(tmp_path)
    r = ar.recheck(p, "best.pt", detector=SeesTongue(), reader_factory=Reader, hands=HANDS)
    assert r["skipped"] is None and r["rows"][0]["ok"] and r["rows"][0]["model"] == "鞋舌"          # 平手取小框：鞋舌
    r = ar.recheck(p, "best.pt", detector=SeesOnlyShoe(), reader_factory=Reader, hands=HANDS)
    assert not r["rows"][0]["ok"] and r["rows"][0]["model"] == "鞋子" and "判成碰到「鞋子」" in r["rows"][0]["note"]
    r = ar.recheck(p, "best.pt", detector=SeesNothing(), reader_factory=Reader, hands=HANDS)
    assert not r["rows"][0]["ok"] and r["rows"][0]["model"] is None and "認不到" in r["rows"][0]["note"]
    assert ar.load(p)["rows"][0]["ok"] is False                                                       # 存檔
    ar.forget(p, "檢查鞋舌")
    assert ar.load(p)["rows"] == []


def test_recheck_skips(tmp_path):
    p = _proj(tmp_path)
    assert ar.recheck(p, "x.pt", detector=SeesTongue(), reader_factory=Reader, hands={})["skipped"].startswith("沒有手")
    p2 = NS(**{**p.__dict__, "state_fixed": None})
    assert ar.recheck(p2, "x.pt", detector=SeesTongue(), reader_factory=Reader, hands=HANDS)["skipped"] == "盒內模式不重判"
