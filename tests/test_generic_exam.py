"""通用辨識考試：固定規則挑提示詞與門檻、保留段驗收、疊在上面的關係。不跑模型，偵測結果用假資料。"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import generic_exam as ge
from generic_exam import Candidate, Det, Example

REGION = (0, 0, 1000, 1000)
BOX = (300, 300, 400, 300)
SHOE_ON = (350, 250, 250, 150)      # 一半以上在盒子框裡
SHOE_OFF = (750, 700, 200, 120)     # 在桌上別處


def _data(n_seg=3, per_seg=10, neg_per=10, box_conf=0.6, noise=False):
    """藍盒：每段 per_seg 格有框；反例格沒有盒子。最後一段與後段反例當驗收。"""
    dets, ex, f = {}, [], 0
    for k in range(n_seg):
        ver = k == n_seg - 1
        for _ in range(per_seg):
            dets[f] = [Det("box", box_conf, BOX), Det("shoe", 0.5, SHOE_OFF)]
            ex.append(Example(f, True, ver, BOX)); f += 1
        for _ in range(neg_per * (2 if ver else 1)):
            dets[f] = [Det("shoe", 0.5, SHOE_OFF)] + ([Det("box", 0.12, (10, 10, 30, 30))] if noise else [])
            ex.append(Example(f, False, ver)); f += 1
    return dets, ex


def test_geometry():
    assert ge.iou(BOX, BOX) == 1.0 and ge.iou(BOX, (0, 0, 10, 10)) == 0.0
    assert ge.inside_ratio(SHOE_ON, BOX) >= ge.ON_TOP_MIN and ge.inside_ratio(SHOE_OFF, BOX) == 0.0


def test_area_is_ratio_of_table_and_center_must_be_inside():
    d = [Det("box", 0.9, (0, 0, 100, 100))]                     # 1% 的桌面
    assert ge.matches(d, Candidate("box", 0.5, 0.01), REGION) and not ge.matches(d, Candidate("box", 0.5, 0.02), REGION)
    assert not ge.matches([Det("box", 0.9, (1500, 0, 100, 100))], Candidate("box", 0.1, 0.0), REGION)


def test_clear_object_passes_and_picks_strict_enough_threshold():
    dets, ex = _data(noise=True)
    r = ge.exam_label("藍盒", 3, ex, dets, REGION)
    assert r["decision"] == "generic" and r["config"]["prompt"] == "box"
    assert r["config"]["conf"] > 0.12 or r["config"]["area"] > 0.0009          # 小雜訊框被門檻擋掉
    assert r["alone"]["verify"]["hit_rate"] == 1.0 and r["alone"]["verify"]["fp_rate"] == 0.0


def test_same_data_same_result():
    dets, ex = _data(noise=True)
    assert ge.exam_label("藍盒", 3, ex, dets, REGION) == ge.exam_label("藍盒", 3, ex, dets, REGION)


def test_not_enough_data_falls_back_to_training():
    dets, ex = _data(n_seg=2)
    r = ge.exam_label("藍盒", 2, ex, dets, REGION)
    assert r["decision"] == "train" and "資料不夠" in r["reason"]


def test_verify_segment_catches_lucky_pick():
    dets, ex = _data()
    for e in ex:                                              # 驗收段的盒子變得認不出來
        if e.verify and e.positive:
            dets[e.frame] = [Det("box", 0.02, BOX)]
    r = ge.exam_label("藍盒", 3, ex, dets, REGION)
    assert r["decision"] == "train" and r["alone"]["pick"]["hit_rate"] == 1.0 and r["alone"]["verify"]["hit_rate"] == 0.0


def test_shoe_on_box_needs_relation():
    """鞋子單獨考會誤報（桌上別處的鞋子也是 shoe）；疊在盒子上才過。"""
    box_dets, box_ex = _data()
    dets, ex, f = {}, [], 10_000
    for k in range(3):
        ver = k == 2
        for _ in range(10):
            # 使用者框的是鞋子＋盒子整塊，不是只有鞋子
            dets[f] = [Det("box", 0.6, BOX), Det("shoe", 0.5, SHOE_ON)]; ex.append(Example(f, True, ver, (300, 240, 400, 360))); f += 1
        for _ in range(20 if ver else 10):
            dets[f] = [Det("box", 0.6, BOX), Det("shoe", 0.5, SHOE_OFF)]; ex.append(Example(f, False, ver)); f += 1
    dets.update(box_dets)
    out = ge.run_exam(["藍盒", "鞋子在盒上"], {"藍盒": 3, "鞋子在盒上": 3}, {"藍盒": box_ex, "鞋子在盒上": ex}, dets, REGION)
    box, shoe = out
    assert box["decision"] == "generic"
    assert shoe["alone"]["verify"]["fp_rate"] > ge.PASS_FP                      # 單獨考不過
    assert shoe["decision"] == "generic" and shoe["config"]["on"] == "藍盒" and shoe["config"]["prompt"] in ("shoe", "sneaker", "footwear")


def test_nothing_found_means_train():
    dets, ex = _data()
    dets = {f: [] for f in dets}
    r = ge.exam_label("盒端貼紙", 3, ex, dets, REGION)
    assert r["decision"] == "train" and "考不過" in r["reason"]
