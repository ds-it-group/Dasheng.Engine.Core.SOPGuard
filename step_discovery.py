"""自動找候選步驟（標記頁第 1 步的輔助）：示範影片裡每一輪都會重複的動作片段，就是候選步驟。

流程（全部不需要標註）：
  1. 取樣：用 items/trace.json 的手部位置（每 TRACE_STEP 格一筆），只留「手在桌面範圍內、而且有在動」的格
  2. 特徵：CLIP 看手的周圍（寬、窄兩種裁切，窄的看得到貼紙這種小東西），前後幾格平均成一小段動作
  3. 分群：KMeans 分得比實際步驟多（N_CLUSTERS），寧可把同一個動作拆開
  4. 合併：兩群的片段在時間上交錯（同一個動作被拆開的兩群會在同一段時間來回出現）而且平均畫面很像 → 同一個候選
  5. 標記：手移動很快、而且每次長短差很多 → 「可能是過場動作」（伸手拿東西、轉身），讓使用者一眼知道可以刪
  6. 預設名稱：其他專案取過名的步驟當「步驟庫」，候選的每一格去步驟庫找最像的一格投票，多數像哪一步就預填那個名字
結果寫在 items/discovery.json；使用者勾選、取名後 apply_candidates() 把每次出現寫成標記頁時間軸上的一段（物品），
那一段的格寫成自動框（框＝手的周圍），在標記頁看得到、可以一段一段刪，接著照原本的流程訓練。

門檻是在 310237 示範影片上定的（離線驗證：使用者標的 4 步各對到 1 個候選，沒有合併錯），換產線可能要再調。
"""
from __future__ import annotations

import json
import os

import cv2
import numpy as np

import item_recognizer as items

DISCOVERY_FILE = os.path.join(items.ITEMS_DIR, "discovery.json")
N_CLUSTERS = 12
PCA_DIM = 32
WINDOW = 3                    # 前後平均幾個取樣（6 fps 取樣時約 0.5 秒）
MOTION_MIN = 0.01             # 桌面範圍內變動像素比例，低於這個又手沒在動＝閒置
HAND_MOVE_MIN = 8.0           # 手部關鍵點每個取樣平均移動幾 px 算有在動
EPISODE_GAP_SEC = 1.5         # 同一群相隔這麼久以內算同一次出現
MERGE_INTERLEAVE = 0.03       # 兩群出現時間重疊的比例（對較短的那一群）
MERGE_COS = 0.95              # 兩群平均特徵的相似度；310237 上「翻轉鞋盒」跟「貼型體紙」是 0.941，要分開
TRANSITION_SPEED = 0.6        # 手速（桌面範圍短邊／秒）超過這個…
TRANSITION_CV = 0.6           # …而且每次長短的變異係數超過這個 → 可能是過場動作
PREVIEW_N = 8
LIB_FILE = os.path.join(items.ITEMS_DIR, "step_library.npz")
LIB_VERSION = 1               # 特徵或取樣方式改了就加一，舊的步驟庫快取會重建
LIB_PER_NAME = 40             # 每個步驟最多取幾格當範例
LIB_NEG = 80                  # 「不是步驟」的範例格數（手在畫面上、但離所有標記都遠）
LIB_HAND_PAD = 40             # 手的關鍵點在物品框外擴這麼多 px 以內才算「正在處理這樣物品」
SUGGEST_STEP_SHARE = 0.2      # 候選裡至少這個比例的格最像「某一步」（不是「不是步驟」）…
SUGGEST_PURITY = 0.6          # …而且這些格至少這個比例像同一步，才預填名字。310237：步驟候選 0.26～0.88／0.77～1.0，
                              # 過場候選 0.02～0.52／0.33～0.5（長的步驟像「型體紙」6 秒，中間有一大半是等待，所以第一個門檻要低）


def discovery_path(project) -> str:
    return os.path.join(project.dir_path, DISCOVERY_FILE)


def load_discovery(project) -> dict | None:
    p = discovery_path(project)
    if not os.path.isfile(p):
        return None
    with open(p, "r", encoding="utf-8") as f:
        return json.load(f)


def _region(project, W: int, H: int) -> tuple[int, int, int, int]:
    """[x0, y0, x1, y1]；state_fixed／seeds.region 是 [x, y, w, h]，沒有就整張畫面。"""
    reg = project.state_fixed or items.ItemSeeds(project.dir_path).region
    if not reg:
        return 0, 0, W, H
    x, y, w, h = reg
    return int(x), int(y), int(min(W, x + w)), int(min(H, y + h))


def hand_box(hands: list, region: tuple, pad: int = 60, min_side: int = 160) -> list[int]:
    """手部關鍵點外擴成框（[x, y, w, h]，裁在桌面範圍內）：自動框用這個當物品位置。"""
    x0, y0, x1, y1 = region
    p = np.array(hands, float)
    a, b = p.min(0) - pad, p.max(0) + pad
    c = (a + b) / 2; side = np.maximum(b - a, min_side)
    a, b = np.maximum(c - side / 2, [x0, y0]), np.minimum(c + side / 2, [x1, y1])
    return [int(a[0]), int(a[1]), int(b[0] - a[0]), int(b[1] - a[1])]


def _embed_samples(video_path: str, frames: list[int], hands_by_f: dict, region: tuple, progress=None):
    """每個取樣格：CLIP 特徵（手的周圍寬、窄兩種）＋桌面範圍的變動比例。"""
    import torch
    import clip
    from PIL import Image
    from video_recorder import VideoFileSource
    dev = "cuda" if torch.cuda.is_available() else "cpu"
    model, pre = clip.load("ViT-B/32", device=dev)
    x0, y0, x1, y1 = region
    want = set(frames); wide, tight, motion = [], [], []
    src = VideoFileSource(video_path); total = src.frame_count; f = 0; prev = None
    try:
        while True:
            fr = src.read()
            if fr is None:
                break
            if f in want:
                g = cv2.GaussianBlur(cv2.cvtColor(cv2.resize(fr[y0:y1, x0:x1], (250, 195)), cv2.COLOR_BGR2GRAY), (5, 5), 0)
                motion.append(0.0 if prev is None else float((cv2.absdiff(g, prev) > 18).mean()))
                prev = g
                pts = np.array(hands_by_f[f], float); cx, cy = pts.mean(0)
                half = max(200.0, float((pts.max(0) - pts.min(0)).max()) * 0.9)
                crops = (fr[int(max(0, cy - half)):int(cy + half), int(max(0, cx - half)):int(cx + half)],
                         fr[int(max(0, cy - 110)):int(cy + 110), int(max(0, cx - 110)):int(cx + 110)])
                for out, crop in zip((wide, tight), crops):
                    out.append(pre(Image.fromarray(cv2.cvtColor(crop, cv2.COLOR_BGR2RGB))))
            f += 1
            if progress and f % 60 == 0:
                progress(f, total)
    finally:
        src.release()

    def run(batch):
        out = []
        with torch.no_grad():
            for i in range(0, len(batch), 128):
                e = model.encode_image(torch.stack(batch[i:i + 128]).to(dev)).float()
                out.append(torch.nn.functional.normalize(e, dim=-1).cpu().numpy())
        return np.concatenate(out)
    return np.concatenate([run(wide), run(tight)], 1), np.array(motion)


def _episodes(ts: np.ndarray, dt: float) -> tuple[np.ndarray, np.ndarray]:
    br = np.where(np.diff(ts) > EPISODE_GAP_SEC)[0]
    starts, ends = np.r_[ts[0], ts[br + 1]], np.r_[ts[br], ts[-1]]
    return starts, ends + dt


def cluster_and_merge(X: np.ndarray, t: np.ndarray, k: int = N_CLUSTERS) -> list[np.ndarray]:
    """回傳每個候選的取樣索引（X、t 是已過濾閒置的取樣）。"""
    from sklearn.cluster import KMeans
    from sklearn.decomposition import PCA
    if WINDOW > 1:
        ker = np.ones(WINDOW) / WINDOW
        X = np.stack([np.convolve(X[:, j], ker, mode="same") for j in range(X.shape[1])], 1)
    k = max(2, min(k, len(X) // 5))
    Z = PCA(min(PCA_DIM, X.shape[1], len(X) - 1), random_state=0).fit_transform(X)
    lab = KMeans(k, n_init=10, random_state=0).fit_predict(Z)
    sm = lab.copy()                                   # 前後 2 個取樣多數決，去掉單格跳動
    for i in range(len(lab)):
        sm[i] = np.bincount(lab[max(0, i - 2):i + 3]).argmax()
    lab = sm
    present = [c for c in range(k) if (lab == c).any()]
    dt = float(np.median(np.diff(t))) if len(t) > 1 else 0.2
    spans = {c: list(zip(*_episodes(t[lab == c], dt))) for c in present}
    cent = {c: X[lab == c].mean(0) / (np.linalg.norm(X[lab == c].mean(0)) + 1e-9) for c in present}
    parent = {c: c for c in present}

    def find(a):
        while parent[a] != a:
            a = parent[a]
        return a
    for i in present:
        for j in present:
            if j <= i:
                continue
            ov = sum(max(0.0, min(a[1], b[1]) - max(a[0], b[0])) for a in spans[i] for b in spans[j])
            dur = min(sum(e - s for s, e in spans[i]), sum(e - s for s, e in spans[j])) + 1e-6
            if ov / dur >= MERGE_INTERLEAVE and float(cent[i] @ cent[j]) >= MERGE_COS:
                parent[find(j)] = find(i)
    groups: dict[int, list[int]] = {}
    for c in present:
        groups.setdefault(find(c), []).append(c)
    return [np.where(np.isin(lab, cs))[0] for cs in groups.values()]


def discover(project, trace: dict, progress=None, lib_progress=None) -> dict:
    """跑一次自動找步驟，寫 items/discovery.json 並回傳。trace＝items.build_trace() 的結果（要有手部位置）。
    lib_progress(專案名稱, 目前格, 總格數)：建立其他專案的步驟庫時回報（有快取就不會叫）。"""
    fps = float(trace.get("fps") or project.fps or 30.0)
    hands_by_f = {r["f"]: r["hands"] for r in trace["rows"] if "hands" in r}
    W, H = project.resolution
    region = _region(project, W, H)
    x0, y0, x1, y1 = region
    inside = lambda pts: any(x0 <= x <= x1 and y0 <= y <= y1 for x, y in pts)
    frames = sorted(f for f, h in hands_by_f.items() if h and inside(h))
    if len(frames) < 30:
        raise ValueError("示範影片裡手在桌面範圍內的畫面太少，找不到候選步驟")
    X, motion = _embed_samples(project.video_path, frames, hands_by_f, region, progress)
    F = np.array(frames); t = F / fps
    short = min(x1 - x0, y1 - y0)
    step_sec = float(np.median(np.diff(t)))
    speed = np.zeros(len(F))                          # 手速：桌面短邊／秒
    for i in range(1, len(F)):
        a, b = hands_by_f[F[i - 1]], hands_by_f[F[i]]
        if len(a) == len(b) and F[i] - F[i - 1] == items.TRACE_STEP:
            speed[i] = float(np.linalg.norm(np.array(a) - np.array(b), axis=1).mean()) / short / step_sec
    moving = (motion > MOTION_MIN) | (speed * short * step_sec > HAND_MOVE_MIN)
    keep = np.where(moving)[0]
    groups = cluster_and_merge(X[keep], t[keep])
    cands, feats = [], []
    for idx in groups:
        idx = keep[idx]; ts = t[idx]; feats.append(X[idx])
        starts, ends = _episodes(ts, step_sec)
        L = ends - starts
        sp = float(np.median(speed[idx])); cv = float(L.std() / L.mean()) if L.mean() > 0 else 0.0
        reasons = (["手移動很快"] if sp > TRANSITION_SPEED else []) + (["每次長短不一"] if cv > TRANSITION_CV else [])
        fs = [int(f) for f in F[idx]]
        cands.append({"episodes": int(len(L)), "mean_sec": round(float(L.mean()), 2), "hand_speed": round(sp, 2),
                      "length_cv": round(cv, 2), "likely_transition": len(reasons) == 2, "reasons": reasons,
                      "episode_starts": [int(round(s * fps)) for s in starts],
                      "preview": [fs[i] for i in np.linspace(0, len(fs) - 1, min(PREVIEW_N, len(fs))).astype(int)],
                      "frames": fs, "boxes": [hand_box(hands_by_f[f], region) for f in fs]})
    try:
        libs = load_libraries(project, lib_progress)
    except Exception as e:                            # 步驟庫只是方便取名，壞了不擋分析
        print(f"[步驟庫] 略過：{type(e).__name__}: {e}"); libs = []
    for c, Xc in zip(cands, feats):
        c["suggest"] = suggest_name(Xc, libs)
    cands.sort(key=lambda c: (c["likely_transition"], -c["episodes"]))
    for i, c in enumerate(cands):
        c["id"] = i
    idle = [f for f, h in sorted(hands_by_f.items()) if not h]
    refs = [idle[i] for i in np.linspace(0, len(idle) - 1, 6).astype(int)] if idle else []
    old = load_discovery(project) or {}
    out = {"fingerprint": items.trace_fingerprint(project.video_path), "region": list(region), "candidates": cands,
           "suggested_refs": refs, "applied_groups": old.get("applied_groups", [])}
    os.makedirs(os.path.dirname(discovery_path(project)), exist_ok=True)
    with open(discovery_path(project), "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False)
    return out


# ---------------------------------------------------------------- 步驟庫（預設名稱）

def _hands_near(hands_by_f: dict, f: int) -> list:
    """trace 每 TRACE_STEP 格才有一筆：取最近的一筆。"""
    base = f - f % items.TRACE_STEP
    for g in (base, base + items.TRACE_STEP):
        if abs(g - f) <= items.TRACE_STEP and hands_by_f.get(g):
            return hands_by_f[g]
    return []


def library_rows(project) -> tuple[list[int], dict, list]:
    """一個專案的步驟庫範例：(格號, 那格的手, 名稱或 None)。每一步取「手正在碰那樣物品」的格（手的關鍵點在框附近），
    物品放著沒人碰的格不算；None＝不是步驟的格（手在畫面上但離所有標記都遠）。"""
    path = os.path.join(project.dir_path, items.TRACE_FILE)
    seeds = items.ItemSeeds(project.dir_path)
    if not seeds.seeds or not os.path.isfile(path):
        return [], {}, []
    with open(path, "r", encoding="utf-8") as f:
        hands_by_f = {r["f"]: r["hands"] for r in json.load(f)["rows"] if "hands" in r}
    by_name: dict[str, dict[int, list]] = {}
    for sd in seeds.seeds:
        hs = _hands_near(hands_by_f, sd.frame)
        x, y, w, h = sd.rect; pad = LIB_HAND_PAD
        if any(x - pad <= px <= x + w + pad and y - pad <= py <= y + h + pad for px, py in hs):
            by_name.setdefault(sd.name, {})[sd.frame] = hs
    frames, hands, names = [], {}, []
    for name, fh in by_name.items():
        fs = sorted(fh)
        for i in np.linspace(0, len(fs) - 1, min(LIB_PER_NAME, len(fs))).astype(int):
            frames.append(fs[i]); hands[fs[i]] = fh[fs[i]]; names.append(name)
    neg = [f for f in _negatives(project, sorted(sd.frame for sd in seeds.seeds)) if hands_by_f.get(f)]
    for i in (np.linspace(0, len(neg) - 1, min(LIB_NEG, len(neg))).astype(int) if neg else []):
        f = neg[i]
        if f not in hands:
            frames.append(f); hands[f] = hands_by_f[f]; names.append(None)
    return frames, hands, names


def load_libraries(project, progress=None) -> list[dict]:
    """其他所有專案的步驟庫（自己這個專案不算）。特徵存在各專案的 items/step_library.npz，標記或影片沒變就直接讀。"""
    from project_store import list_projects, load_project
    out = []
    for name in list_projects():
        try:
            other = load_project(name)
        except Exception:
            continue
        if os.path.abspath(other.dir_path) == os.path.abspath(project.dir_path) or not os.path.isfile(other.video_path):
            continue
        seeds_path = os.path.join(other.dir_path, items.SEEDS_FILE)
        if not os.path.isfile(seeds_path):
            continue
        key = f"{LIB_VERSION}|{items.trace_fingerprint(other.video_path)}|{os.path.getmtime(seeds_path)}"
        cache = os.path.join(other.dir_path, LIB_FILE)
        if os.path.isfile(cache):
            z = np.load(cache, allow_pickle=False)
            if str(z["key"]) == key:
                if len(z["X"]):
                    out.append({"project": name, "X": z["X"], "names": json.loads(str(z["names"]))})
                continue
        frames, hands, names = library_rows(other)
        X = np.zeros((0, 1024), np.float32)
        if frames and any(names):
            order = np.argsort(frames); frames = [frames[i] for i in order]; names = [names[i] for i in order]
            W, H = other.resolution
            X, _ = _embed_samples(other.video_path, frames, hands, _region(other, W, H),
                                  (lambda a, b, n=name: progress(n, a, b)) if progress else None)
            X = X.astype(np.float32)
        np.savez(cache, key=np.array(key), X=X, names=np.array(json.dumps(names if len(X) else [], ensure_ascii=False)))
        if len(X):
            out.append({"project": name, "X": X, "names": names})
    return out


def suggest_name(Xc: np.ndarray, libs: list[dict]) -> dict | None:
    """候選的每一格在每個專案的步驟庫裡找最像的一格投票。像「某一步」的格夠多（SUGGEST_STEP_SHARE）、而且大多像同一步
    （SUGGEST_PURITY）就建議那一步；幾個專案都有建議時取比例最高的，其他放 alts。None＝步驟庫裡沒有像的。
    share＝候選裡像這一步的格佔多少，給介面顯示。"""
    import collections
    picks = []
    for lib in libs:
        S = Xc @ lib["X"].T / 2.0                     # 兩段各自正規化的特徵接起來：除以 2 才是平均 cos
        nn = S.argmax(1)
        votes = collections.Counter(lib["names"][j] for j in nn if lib["names"][j] is not None)
        if not votes:
            continue
        top, n = votes.most_common(1)[0]
        step_n = sum(votes.values())
        if step_n / len(nn) < SUGGEST_STEP_SHARE or n / step_n < SUGGEST_PURITY:
            continue
        sel = np.array([i for i, j in enumerate(nn) if lib["names"][j] == top])
        picks.append({"name": top, "project": lib["project"], "share": round(n / len(nn), 2), "purity": round(n / step_n, 2),
                      "score": round(float(np.median(S[sel, nn[sel]])), 3)})
    if not picks:
        return None
    picks.sort(key=lambda p: (-p["purity"] * p["share"], -p["score"]))
    return {**picks[0], "alts": picks[1:]}


NEG_GAP = 15                  # 反例離任何一個標記格至少這麼多格（0.5 秒），避開動作的開頭結尾
NEG_NOHAND_EVERY = 4          # 沒有手的格每幾個取樣取一個


def _negatives(project, labelled: list[int]) -> list[int]:
    """反例格：手在畫面上、但離所有標記格都遠（閒置的手、伸手、轉身），加上一些沒有手的格。只用標記框訓練時，
    模型學到的是「手的周圍」，閒置時手放在桌上也會認成步驟（310237 實測：誤報 4 次；加反例後 2 次）。"""
    import bisect
    path = os.path.join(project.dir_path, items.TRACE_FILE)
    if not os.path.isfile(path) or not labelled:
        return []
    with open(path, "r", encoding="utf-8") as f:
        rows = [r for r in json.load(f)["rows"] if "hands" in r]

    def near(fr):
        i = bisect.bisect_left(labelled, fr - NEG_GAP)
        return i < len(labelled) and labelled[i] <= fr + NEG_GAP
    hand = [r["f"] for r in rows if r["hands"] and not near(r["f"])]
    nohand = [r["f"] for r in rows if not r["hands"] and not near(r["f"])][::NEG_NOHAND_EVERY]
    return sorted(set(hand) | set(nohand))


def _episode_spans(frames: list[int], gap: int) -> list[tuple[int, int]]:
    """排好的格號切成幾次出現（相隔超過 gap 格就是下一次）。"""
    spans: list[list[int]] = []
    for f in sorted(frames):
        if spans and f - spans[-1][1] <= gap:
            spans[-1][1] = f
        else:
            spans.append([f, f])
    return [(a, b) for a, b in spans]


def apply_candidates(project, picks: list[dict]) -> dict:
    """picks＝[{"id": 候選編號, "name": 步驟名稱}, ...]；同名的幾個候選併成同一樣物品。每一次出現寫成標記頁時間軸上的一段
    （label_segments，物品、已存檔），那一段的格寫成同一組自動框（框＝手的周圍），在標記頁可以一段一段刪。
    再套用一次會先移除上次自動產生的段落和框。沒有空桌面參考格就順便加上建議的那幾格。"""
    import label_segments as ls
    d = load_discovery(project)
    if d is None:
        raise ValueError("還沒有自動找步驟的結果")
    by_id = {c["id"]: c for c in d["candidates"]}
    picks = [p for p in picks if str(p.get("name", "")).strip()]
    if not picks:
        raise ValueError("請至少勾選一個候選步驟並取名")
    for p in picks:
        if int(p["id"]) not in by_id:
            raise ValueError(f"沒有候選 {p['id']}")
    seeds = items.ItemSeeds(project.dir_path)
    segs = ls.Segments(project.dir_path)
    old = set(d.get("applied_groups", []))
    seeds.seeds = [s for s in seeds.seeds if s.group not in old]
    segs.segs = [g for g in segs.segs if not (g.saved and g.group in old)]
    left = {s.name for s in seeds.seeds} | {g.name for g in segs.segs}
    stale = [n for n in d.get("applied_names", []) if n not in left]   # 上次自動產生、這次沒選的名稱也拿掉
    seeds.order = [n for n in seeds.order if n not in stale]
    segs.names = [n for n in segs.names if n.name not in stale]
    # 同名的候選併在一起再切成幾次出現：兩個候選的出現時間交錯時，時間軸上同名的段落不能重疊
    by_name: dict[str, dict[int, list[int]]] = {}
    for p in picks:
        c = by_id[int(p["id"])]
        fb = by_name.setdefault(str(p["name"]).strip(), {})
        for f, r in zip(c["frames"], c["boxes"]):
            fb[int(f)] = [int(v) for v in r]
    gap = int(round(EPISODE_GAP_SEC * float(project.fps or 30.0)))
    g = max([s.group for s in seeds.seeds] + [g.group for g in segs.segs] + [0]); groups = []; added: dict[str, int] = {}
    for name, fb in by_name.items():
        if name not in seeds.order:
            seeds.order.append(name)
        if segs.name(name) is None:
            segs.names.append(ls.NameDef(name, "object", ls.PALETTE[len(segs.names) % len(ls.PALETTE)]))
        taken = [(x.start, x.end) for x in segs.by_name(name)]
        for a, b in _episode_spans(list(fb), gap):
            if any(a <= e and b >= s0 for s0, e in taken):    # 使用者自己標過的段落優先，重疊的這一次不加
                continue
            g += 1; groups.append(g)
            fs = [f for f in sorted(fb) if a <= f <= b]
            for f in fs:
                seeds.seeds.append(items.Seed(name, f, fb[f], True, g))
            seg = ls.Segment(segs.next_id, name, a, b, fb[fs[0]], fs[0], True, g, len(fs)); segs.next_id += 1
            segs.segs.append(seg)
            added[name] = added.get(name, 0) + len(fs)
    segs._sort(); segs.save()
    if not seeds.refs:
        seeds.refs = sorted(int(f) for f in d.get("suggested_refs", []))
    seeds.negatives = _negatives(project, sorted(s.frame for s in seeds.seeds))
    if seeds.region is None and project.state_fixed is None:
        x0, y0, x1, y1 = d["region"]
        seeds.region = [x0, y0, x1 - x0, y1 - y0]
    seeds.save()
    d["applied_groups"] = groups; d["applied_names"] = sorted(added)
    with open(discovery_path(project), "w", encoding="utf-8") as f:
        json.dump(d, f, ensure_ascii=False)
    return {"added": added, "segments": len(groups), "refs": seeds.refs, "negatives": len(seeds.negatives)}
