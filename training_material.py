"""訓練素材：把專案影片裡的框選分成「片段」、挑片段訓練（可以跨型體地區）、留片段做離線驗證。

- 片段：同一支影片裡框選（手框＋自動追出來的）時間相鄰的一群；相隔超過 SEG_GAP_SEC 就切開。大致等於一輪。
- 配色：一個專案一支示範影片，影片是什麼配色記在 <專案>/items/material.json（{"video_color": "黑白"}）。
- 驗證：每個配色留最後一段不參與訓練；訓練完用新模型掃那幾段，標記過的物品都要被看到才算通過。
"""
from __future__ import annotations

import json
import os
import shutil
from collections import Counter

import item_recognizer as items

SEG_GAP_SEC = 3.0           # 框選間隔超過這麼久就算另一段（現場一輪約 11～17 秒、輪與輪之間 2.7～6 秒）
VALIDATE_STEP = 5           # 驗證時每幾格掃一次（監控也是每 5 格判一次）
VALIDATE_MIN_HITS = 2       # 一段裡至少看到幾次才算有看到
MATERIAL_FILE = os.path.join(items.ITEMS_DIR, "material.json")


def video_color(project) -> str:
    try:
        with open(os.path.join(project.dir_path, MATERIAL_FILE), "r", encoding="utf-8-sig") as f:
            return str(json.load(f).get("video_color", "") or "")
    except (OSError, ValueError):
        return ""


def set_video_color(project, color: str) -> None:
    path = os.path.join(project.dir_path, MATERIAL_FILE)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    try:
        with open(path, "r", encoding="utf-8-sig") as f:
            d = json.load(f)
    except (OSError, ValueError):
        d = {}
    d["video_color"] = (color or "").strip()
    with open(path, "w", encoding="utf-8") as f:
        json.dump(d, f, ensure_ascii=False, indent=2)


def segments(project, seeds: items.ItemSeeds | None = None) -> list[dict]:
    """框選分段。每段：起訖格、秒數、每樣物品手框／自動幾格、每樣物品一個代表框（優先手框）、框在 seeds.seeds 的索引。"""
    seeds = seeds or items.ItemSeeds(project.dir_path)
    fps = float(project.fps or 30.0); gap = int(SEG_GAP_SEC * fps)
    idx = sorted(range(len(seeds.seeds)), key=lambda i: seeds.seeds[i].frame)
    groups: list[list[int]] = []
    for i in idx:
        if groups and seeds.seeds[i].frame - seeds.seeds[groups[-1][-1]].frame <= gap:
            groups[-1].append(i)
        else:
            groups.append([i])
    out = []
    for k, g in enumerate(groups):
        ss = [seeds.seeds[i] for i in g]
        per: dict[str, list[int]] = {}
        key: dict[str, dict] = {}
        for i, s in zip(g, ss):
            c = per.setdefault(s.name, [0, 0]); c[1 if s.auto else 0] += 1
            if s.name not in key or (key[s.name]["auto"] and not s.auto):
                key[s.name] = {"index": i, "frame": s.frame, "rect": list(s.rect), "auto": s.auto}
        a, b = ss[0].frame, ss[-1].frame
        out.append({"no": k + 1, "start": a, "end": b, "start_sec": round(a / fps, 2), "end_sec": round(b / fps, 2),
                    "items": {n: {"manual": v[0], "auto": v[1]} for n, v in per.items()},
                    "key": key, "n": len(g), "manual": sum(v[0] for v in per.values()), "indices": g})
    return out


def in_ranges(frame: int, ranges) -> bool:
    return any(a <= frame <= b for a, b in ranges)


def filtered_seeds(seeds: items.ItemSeeds, keep_ranges, drop_ranges=()) -> items.ItemSeeds:
    """只留選到的片段裡的框（扣掉留做驗證的片段）。只在記憶體裡，不寫回檔案。"""
    import copy
    out = copy.copy(seeds)
    out.seeds = [s for s in seeds.seeds if in_ranges(s.frame, keep_ranges) and not in_ranges(s.frame, drop_ranges)]
    out.save = lambda: None
    return out


def pick_holdout(selected: list[dict]) -> list[dict]:
    """每個配色留最後一段做驗證；某配色只有一段就不留（全部拿去訓練，該配色這次無法驗證）。
    selected：[{project, start, end, color}]。"""
    by_color: dict[str, list[dict]] = {}
    for s in selected:
        by_color.setdefault(s.get("color", ""), []).append(s)
    hold = []
    for color, segs in by_color.items():
        if len(segs) >= 2:
            hold.append(max(segs, key=lambda s: (s["project"], s["start"])))
    return hold


def merge_datasets(parts: list[tuple[str, list[str]]], out_dir: str, names: list[str]) -> dict:
    """多個 YOLO 資料集合成一個：圖檔加前綴避免撞名、類別編號換成合併後的名單。"""
    shutil.rmtree(out_dir, ignore_errors=True)
    for s in ("train", "val"):
        os.makedirs(os.path.join(out_dir, "images", s)); os.makedirs(os.path.join(out_dir, "labels", s))
    n = Counter()
    for k, (ds, src_names) in enumerate(parts):
        remap = {i: names.index(nm) for i, nm in enumerate(src_names) if nm in names}
        for split in ("train", "val"):
            img_dir = os.path.join(ds, "images", split)
            if not os.path.isdir(img_dir):
                continue
            for fn in os.listdir(img_dir):
                stem = os.path.splitext(fn)[0]
                shutil.copyfile(os.path.join(img_dir, fn), os.path.join(out_dir, "images", split, f"p{k}_{fn}"))
                lab = os.path.join(ds, "labels", split, stem + ".txt")
                if os.path.isfile(lab):
                    rows = []
                    with open(lab, "r", encoding="utf-8") as fh:
                        for line in fh:
                            parts_ = line.split()
                            if parts_ and int(parts_[0]) in remap:
                                rows.append(" ".join([str(remap[int(parts_[0])])] + parts_[1:]))
                    with open(os.path.join(out_dir, "labels", split, f"p{k}_{stem}.txt"), "w", encoding="utf-8") as fh:
                        fh.write("\n".join(rows) + ("\n" if rows else ""))
                n[split] += 1
    with open(os.path.join(out_dir, "data.yaml"), "w", encoding="utf-8") as fh:
        fh.write(f"path: {out_dir}\ntrain: images/train\nval: images/val\nnames:\n" + "".join(f"  {i}: {nm}\n" for i, nm in enumerate(names)))
    return {"train": n["train"], "val": n["val"], "names": names}


def validate_holdout(project, model_file: str, segs: list[dict], detector=None, reader_factory=None) -> list[dict]:
    """用新模型掃保留的片段：片段裡標記過的每樣物品，至少要被看到 VALIDATE_MIN_HITS 次。
    segs：[{start, end, color, items: {名稱: ...}}]（同一個專案）。只支援固定桌面範圍。"""
    if not items.is_fixed(project):
        return [{"start": s["start"], "end": s["end"], "color": s.get("color", ""), "ok": None,
                 "missing": [], "note": "盒內模式不支援自動驗證"} for s in segs]
    if detector is None:
        detector = items.ItemDetector(model_file)
    if reader_factory is None:
        from video_recorder import FrameReader
        reader_factory = FrameReader
    reader = reader_factory(project.video_path)
    reg = tuple(project.state_fixed)
    out = []
    try:
        for s in segs:
            hits = Counter()
            for f in range(s["start"], s["end"] + 1, VALIDATE_STEP):
                crop = items._crop(reader.get_frame(f), reg)
                for h in detector.detect(crop):
                    hits[h.name] += 1
            missing = [n for n in s["items"] if hits[n] < VALIDATE_MIN_HITS]
            out.append({"start": s["start"], "end": s["end"], "color": s.get("color", ""), "ok": not missing, "missing": missing,
                        "hits": dict(hits)})
    finally:
        try:
            reader.release()
        except Exception:
            pass
    return out


def material_rows(project_names: list[str]) -> list[dict]:
    """訓練燈箱的素材清單：每個專案的影片、配色、片段。"""
    from project_store import load_project
    rows = []
    for name in project_names:
        try:
            p = load_project(name)
        except Exception as e:
            rows.append({"project": name, "error": str(e)}); continue
        pk = p.packaging
        seeds = items.ItemSeeds(p.dir_path)
        import step_analysis
        an = step_analysis.load(p)
        rows.append({"analysis": None if an is None else {"rounds": an.get("rounds", []), "stale": an.get("stale"),
                                                          "analyzed_at": an.get("analyzed_at"), "steps": an.get("steps", [])},
                     "steps": [{"index": s.step_index, "name": s.step_name, "type": s.type, "label": s.label or s.object or "",
                                "required": s.required} for s in p.steps],"project": name, "style": pk.style if pk else "", "region": pk.region if pk else "",
                     "style_name": pk.style_name if pk else "", "has_video": os.path.isfile(p.video_path),
                     "fps": p.fps, "color": video_color(p), "region_rect": p.state_fixed or seeds.region,
                     "fixed": items.is_fixed(p), "segments": segments(p, seeds), "item_order": list(seeds.order)})
    return rows
