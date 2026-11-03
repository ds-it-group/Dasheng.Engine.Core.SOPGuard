"""拿專案已經框好的資料考 YOLO-World（generic_exam 的固定規則），看每個名稱能不能不訓練、直接用通用辨識。
只讀資料、不改專案設定。結果寫在 cache/generic_exam/<專案>/（report.txt、report.json；偵測結果快取 dets.json，改規則重跑不用重新偵測）。

正例＝使用者框的格子（每個名稱依時間分段，間隔超過 3 秒算新的一段，每段平均取最多 20 格），最後一段留著驗收。
反例＝整支影片每 1 秒取一格＋空桌參考格，排除這個名稱任何一個框前後 3 秒，而且目前專案自己訓練的模型也沒看到這個名稱
（舊資料沒有「東西在畫面上的時間」，只好用已經驗收過的模型當反例的依據；新的標註畫面會直接有）。
反例在最後一段開始之後的，當驗收用。

用法：python tools/generic_exam_run.py 巴伯樂包裝1
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

import generic_exam as ge                                    # noqa: E402
import item_recognizer as items                             # noqa: E402
import project_store                                        # noqa: E402
from project_store import app_base_dir                      # noqa: E402

SEG_GAP_SEC = 3.0
PER_SEG = 20
NEG_EVERY_SEC = 1.0
NEG_MARGIN_SEC = 3.0
DET_CONF = 0.03          # 先用很低的門檻存下所有框，門檻交給考試挑


def _segments(frames: list[int], gap: int) -> list[list[int]]:
    segs: list[list[int]] = []
    for f in sorted(set(frames)):
        if segs and f - segs[-1][-1] <= gap:
            segs[-1].append(f)
        else:
            segs.append([f])
    return segs


def _even(xs: list[int], n: int) -> list[int]:
    if len(xs) <= n:
        return list(xs)
    return [xs[round(i * (len(xs) - 1) / (n - 1))] for i in range(n)]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("project")
    ap.add_argument("--imgsz", type=int, default=640, help="YOLO-World 輸入大小（監控用 640）")
    args = ap.parse_args()

    p = project_store.load_project(args.project)
    seeds = items.ItemSeeds(p.dir_path)
    fps = float(p.fps or 30.0)
    region = tuple(p.state_fixed or seeds.region or p.work_area)
    labels = [lb for lb in seeds.order if any(s.name == lb for s in seeds.seeds)]
    out_dir = os.path.join(ROOT, "cache", "generic_exam", p.project_name); os.makedirs(out_dir, exist_ok=True)

    # 正例
    by_label: dict[str, dict[int, tuple]] = {}
    for s in seeds.seeds:
        by_label.setdefault(s.name, {}).setdefault(s.frame, tuple(s.rect))
    segs = {lb: _segments(list(by_label[lb]), int(SEG_GAP_SEC * fps)) for lb in labels}
    pos_frames = {lb: [(f, k == len(segs[lb]) - 1) for k, sg in enumerate(segs[lb]) for f in _even(sg, PER_SEG)] for lb in labels}

    video = os.path.join(p.dir_path, p.video_file)
    from video_recorder import open_video_oriented
    cap, rotate, w, h, vfps = open_video_oriented(video)
    n_frames = int(cap.get(7) or 0)          # CAP_PROP_FRAME_COUNT
    sweep = sorted({int(round(k * NEG_EVERY_SEC * fps)) for k in range(int(n_frames / fps / NEG_EVERY_SEC) + 1)} | set(seeds.refs))
    sweep = [f for f in sweep if f < n_frames]
    need = sorted(set(sweep) | {f for v in pos_frames.values() for f, _ in v})

    key = hashlib.md5(json.dumps([ge.VOCAB, DET_CONF, args.imgsz, need, os.path.getsize(video)]).encode()).hexdigest()[:12]
    cache = os.path.join(out_dir, "dets.json")
    data = None
    if os.path.isfile(cache):
        with open(cache, encoding="utf-8") as f:
            data = json.load(f)
        if data.get("key") != key:
            data = None
    if data is None:
        import cv2
        from core_detector import crop_roi
        from object_detector import ObjectDetector
        world = ObjectDetector(os.path.join(app_base_dir(), "models", "yolov8s-worldv2.pt"), ge.VOCAB, imgsz=args.imgsz, conf=DET_CONF, threads=None)
        trained = items.ItemDetector(items.model_path(p))
        want, sweep_set = set(need), set(sweep)
        dets, model_sees, ms = {}, {}, []
        t0 = time.time()
        for i in range(max(need) + 1):
            if i not in want:
                cap.grab(); continue
            ok, fr = cap.read()
            if not ok:
                break
            if rotate is not None:
                fr = cv2.rotate(fr, rotate)
            a = time.perf_counter()
            dets[str(i)] = [[d.label, round(d.conf, 4), [round(v, 1) for v in d.rect]] for d in world.detect(fr)]
            ms.append((time.perf_counter() - a) * 1000)
            if i in sweep_set:
                model_sees[str(i)] = sorted({hh.name for hh in trained.detect(crop_roi(fr, region))})
            if len(dets) % 50 == 0:
                print(f"  {len(dets)}/{len(need)} 格，{time.time() - t0:.0f} 秒", flush=True)
        data = {"key": key, "dets": dets, "model_sees": model_sees, "world_ms": sum(ms) / max(1, len(ms))}
        with open(cache, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False)
    cap.release()

    dets_by_frame = {int(k): [ge.Det(lb, c, tuple(r)) for lb, c, r in v] for k, v in data["dets"].items()}
    model_sees = {int(k): set(v) for k, v in data["model_sees"].items()}

    examples: dict[str, list[ge.Example]] = {}
    for lb in labels:
        ex = [ge.Example(f, True, ver, by_label[lb][f]) for f, ver in pos_frames[lb]]
        vstart = segs[lb][-1][0]
        margin = NEG_MARGIN_SEC * fps
        seed_fs = sorted(by_label[lb])
        for f in sweep:
            if f not in model_sees or lb in model_sees[f]:
                continue
            if any(abs(f - sf) <= margin for sf in seed_fs):
                continue
            ex.append(ge.Example(f, False, f >= vstart))
        examples[lb] = ex

    results = ge.run_exam(labels, {lb: len(segs[lb]) for lb in labels}, examples, dets_by_frame, region)

    # 跟目前人工調的設定比（只是參考，人工設定原本的用途是錨點，不是認這些名稱）
    table = float(region[2] * region[3])
    manual = []
    for a in p.anchors:
        c = ge.Candidate(a.prompt, a.min_conf, a.min_area / table)
        for lb in labels:
            ex = examples[lb]
            s_all = ge.score(ex, dets_by_frame, c, region)
            manual.append({"anchor": a.name, "config": c.to_dict(), "text": c.text(), "label": lb, "all": s_all.to_dict()})

    report = {"project": p.project_name, "region": region, "world_ms": round(data["world_ms"], 1),
              "rules": {"IOU_HIT": ge.IOU_HIT, "PASS_HIT": ge.PASS_HIT, "PASS_FP": ge.PASS_FP, "MIN_SEGMENTS": ge.MIN_SEGMENTS},
              "segments": {lb: [[round(sg[0] / fps, 1), round(sg[-1] / fps, 1)] for sg in segs[lb]] for lb in labels},
              "results": results, "manual": manual}
    with open(os.path.join(out_dir, "report.json"), "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=1)

    lines = [f"專案：{p.project_name}　桌面範圍 {list(region)}　YOLO-World 每格平均 {data['world_ms']:.0f} ms（imgsz {args.imgsz}）", ""]
    for r in results:
        lines.append(f"■ {r['label']}：{'通用辨識' if r['decision'] == 'generic' else '自己訓練'}")
        lines.append(f"  {r['reason']}")
        lines.append(f"  段落 {report['segments'][r['label']]}；挑選 正例 {r['pick_pos']}／反例 {r['pick_neg']}，驗收 正例 {r['verify_pos']}／反例 {r['verify_neg']}")
        if "alone" in r:
            al = r["alone"]
            lines.append(f"  單獨最好：{al['text']}　挑選段 找到 {al['pick']['hit_rate']:.0%} 誤報 {al['pick']['fp_rate']:.0%}　"
                         f"驗收段 找到 {al['verify']['hit_rate']:.0%} 誤報 {al['verify']['fp_rate']:.0%}")
        for t in r.get("relations", []):
            lines.append(f"  疊在「{t['on']}」上：{t['text']}　驗收段 找到 {t['verify']['hit_rate']:.0%} 誤報 {t['verify']['fp_rate']:.0%}")
        lines.append("")
    lines.append("目前人工調的錨點設定，拿來認各名稱的分數（全部格子，參考用）：")
    for m in manual:
        lines.append(f"  {m['anchor']}（{m['text']}）× {m['label']}：找到 {m['all']['hit_rate']:.0%} 誤報 {m['all']['fp_rate']:.0%}")
    txt = "\n".join(lines)
    with open(os.path.join(out_dir, "report.txt"), "w", encoding="utf-8") as f:
        f.write(txt)
    print(txt)


if __name__ == "__main__":
    main()
