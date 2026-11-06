"""自動找候選步驟：合併規則與套用成自動框（不跑 CLIP，用合成資料）。"""
from __future__ import annotations

import json
import os

import numpy as np

import step_discovery as sd
from item_recognizer import ItemSeeds
from project_store import project_from_dict


def _project(tmp_path):
    cfg = {"schema_version": 2, "project_name": "d", "video_file": "demo.avi", "resolution": [400, 240], "fps": 30.0,
           "anchors": [], "zones": [], "state_fixed": [0, 0, 400, 240], "cycle_min_sec": 0.0,
           "cycle_end": {"type": "steps_done", "hold_sec": 6.0}, "steps": []}
    return project_from_dict(cfg, str(tmp_path))


def test_split_clusters_of_one_action_are_merged_but_sequential_steps_are_not():
    # 3 輪，每輪：動作 A（兩種看起來略不同的樣子來回交錯）接著動作 B；A 與 B 前後相接、不交錯
    rng = np.random.RandomState(0); a1, a2, b = rng.randn(3, 64)
    a2 = a1 + 0.15 * a2                       # A 的另一種樣子：很像 A
    X, t = [], []
    for cyc in range(3):
        t0 = cyc * 20.0
        for i in range(30):                   # A：5 秒，兩種樣子每 2 個取樣換一次
            X.append((a1 if (i // 2) % 2 == 0 else a2) + 0.01 * rng.randn(64)); t.append(t0 + i / 6)
        for i in range(30):                   # B：接在 A 後面 5 秒
            X.append(b + 0.01 * rng.randn(64)); t.append(t0 + 5 + i / 6)
    groups = sd.cluster_and_merge(np.array(X), np.array(t), k=3)
    t = np.array(t)
    owner = {}
    for gi, idx in enumerate(groups):
        for i in idx:
            owner[i] = gi
    a_groups = {owner[i] for i in range(len(t)) if (t[i] % 20) < 4.5 and i in owner}
    b_groups = {owner[i] for i in range(len(t)) if (t[i] % 20) > 5.5 and i in owner}
    assert len(a_groups) == 1 and len(b_groups) == 1 and a_groups != b_groups


def test_apply_candidates_writes_auto_boxes_and_replaces_previous(tmp_path):
    p = _project(tmp_path)
    os.makedirs(tmp_path / "items")
    d = {"fingerprint": "", "region": [0, 0, 400, 240], "suggested_refs": [5, 300], "applied_groups": [],
         "candidates": [{"id": 0, "frames": [10, 15], "boxes": [[1, 2, 50, 50], [3, 4, 50, 50]]},
                        {"id": 1, "frames": [40], "boxes": [[5, 6, 60, 60]]},
                        {"id": 2, "frames": [70, 75, 80], "boxes": [[7, 8, 70, 70]] * 3}]}
    json.dump(d, open(sd.discovery_path(p), "w"))
    s = ItemSeeds(str(tmp_path)); s.add_seed("手框的", 500, (0, 0, 40, 40))
    out = sd.apply_candidates(p, [{"id": 0, "name": "翻鞋舌"}, {"id": 1, "name": "翻鞋舌"}, {"id": 2, "name": "貼紙"}])
    assert out["added"] == {"翻鞋舌": 3, "貼紙": 3}
    s = ItemSeeds(str(tmp_path))
    assert s.order == ["手框的", "翻鞋舌", "貼紙"] and s.refs == [5, 300]
    assert s.auto_counts() == {"翻鞋舌": 3, "貼紙": 3} and s.counts() == {"手框的": 1}
    sd.apply_candidates(p, [{"id": 2, "name": "貼紙"}])          # 再套用：上次自動產生的框先移除，手框的保留
    s = ItemSeeds(str(tmp_path))
    assert s.auto_counts() == {"貼紙": 3} and s.counts() == {"手框的": 1} and s.order == ["手框的", "貼紙"]


def _unit(v):
    v = np.asarray(v, float)
    return v / np.linalg.norm(v)


def test_suggest_name_votes_against_library():
    rng = np.random.default_rng(0)
    base = {n: _unit(rng.normal(size=8)) for n in ("A", "B", "idle")}
    feat = lambda n: np.r_[_unit(base[n] + rng.normal(scale=0.05, size=8)), _unit(base[n] + rng.normal(scale=0.05, size=8))]
    names = ["A"] * 10 + ["B"] * 10 + [None] * 10
    lib = {"project": "P", "X": np.stack([feat(n or "idle") for n in names]), "names": names}
    # 3 成像 A、7 成像閒置：像「某一步」的格夠多、而且都像 A → 建議 A
    s = sd.suggest_name(np.stack([feat("A")] * 3 + [feat("idle")] * 7), [lib])
    assert s["name"] == "A" and s["project"] == "P" and s["share"] == 0.3 and s["purity"] == 1.0
    # 幾乎都是閒置 → 不建議
    assert sd.suggest_name(np.stack([feat("A")] + [feat("idle")] * 9), [lib]) is None
    # A、B 各半 → 不夠集中，不建議
    assert sd.suggest_name(np.stack([feat("A")] * 5 + [feat("B")] * 5), [lib]) is None
    # 兩個專案都有建議：比例高的當主建議，另一個放 alts
    lib2 = {"project": "Q", "X": lib["X"], "names": ["甲"] * 10 + ["乙"] * 10 + [None] * 10}
    s = sd.suggest_name(np.stack([feat("A")] * 8 + [feat("B")] * 2), [lib, lib2])
    assert s["name"] in ("A", "甲") and len(s["alts"]) == 1
    assert sd.suggest_name(np.stack([feat("A")] * 3), []) is None
