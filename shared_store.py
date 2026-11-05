"""共用硬碟（NAS）：把專案上傳上去、從上面載入，別台電腦不用重框、不用重訓。

共用硬碟的結構（2026-11-05 使用者要「最好管理的架構」）：
    <共用資料夾>\\<專案>\\
        current.txt        一行字，例如 v3：大家載入哪一版只看這個，發布和退回都只是改這一行
        v1\\ v2\\ v3\\      每一版一個資料夾，只增不改：config.json、items\\…、version.json
        video\\<影片檔>     示範影片只放一份，不跟著每一版複製（選配）
- version.json：版本號、上傳時間（UTC）、哪台電腦、從哪一版改的、模型訓練時間、程式版本、備註。每一版自帶，不另放歷史表。
- 上傳：先複製到 _uploading_<電腦>，全部複製完才改名成新版本，最後才改 current.txt（複製到一半斷線，別台看不到半套）。
  兩台同時上傳時版本號撞到就用下一號，兩份都留。這台當初載入的不是現在的 current（別人在這之間傳過）→ 要使用者確認才發布。
- 載入：複製那一版的檔案到本機（保留修改時間），本機的 version.json 就記著「我是 v 幾」。載入不重算桌面範圍、不碰框，
  模型和它的 model_info.json 一起過來，所以載入後不用重訓。參考別的專案模型的，被參考的專案一起載。
- 本機改過沒上傳：本機 config.json／items/seeds.json／items/model/best.pt 有任何一個比本機 version.json 新（同一台電腦自己比，沒有時鐘問題）。
共用資料夾路徑存在這台電腦的 shared_root.txt（不進 git）。
"""
from __future__ import annotations

import json
import os
import re
import shutil
import socket
import subprocess
import time
import zipfile
from datetime import datetime, timezone

from project_store import app_base_dir, load_project, projects_dir

ROOT_FILE = "shared_root.txt"
VERSION_FILE = "version.json"
CURRENT_FILE = "current.txt"
VIDEO_DIR = "video"
_SKIP_RE = re.compile(r"^(seeds_before_.*|seeds_v\d+_backup.*|best_prev_.*|best_gpu_.*|candidate.*|trace\.json|exam_.*\.tmp)$")
_VER_RE = re.compile(r"^v(\d+)$")
CHANGE_KEYS = ("config.json", os.path.join("items", "seeds.json"), os.path.join("items", "model", "best.pt"))


# ---------------------------------------------------------------- 路徑

def get_root() -> str:
    try:
        with open(os.path.join(app_base_dir(), ROOT_FILE), "r", encoding="utf-8-sig") as f:
            return f.read().strip()
    except OSError:
        return ""


def set_root(path: str) -> str:
    path = (path or "").strip().strip('"')
    if not path:
        raise ValueError("請填共用硬碟資料夾")
    if not os.path.isdir(path):
        raise ValueError(f"連不到 {path}，檢查網路或路徑")
    with open(os.path.join(app_base_dir(), ROOT_FILE), "w", encoding="utf-8") as f:
        f.write(path)
    return path


def _root(root: str | None) -> str:
    r = root if root is not None else get_root()
    if not r:
        raise ValueError("還沒設定共用硬碟資料夾")
    if not os.path.isdir(r):
        raise ValueError(f"連不到 {r}，檢查網路或路徑")
    return r


def computer_name() -> str:
    return os.environ.get("COMPUTERNAME") or socket.gethostname() or "unknown"


def program_version() -> str:
    try:
        r = subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=app_base_dir(), capture_output=True, text=True, timeout=5)
        return r.stdout.strip() if r.returncode == 0 else ""
    except (OSError, subprocess.SubprocessError):
        return ""


# ---------------------------------------------------------------- 讀

def versions(root: str, name: str) -> list[int]:
    d = os.path.join(root, name)
    if not os.path.isdir(d):
        return []
    return sorted(int(m.group(1)) for x in os.listdir(d) if (m := _VER_RE.match(x)) and os.path.isdir(os.path.join(d, x)))


def current(root: str, name: str) -> int | None:
    try:
        with open(os.path.join(root, name, CURRENT_FILE), "r", encoding="utf-8-sig") as f:
            m = _VER_RE.match(f.read().strip())
            return int(m.group(1)) if m else None
    except OSError:
        return None


def _read_json(path: str) -> dict:
    try:
        with open(path, "r", encoding="utf-8-sig") as f:
            d = json.load(f)
        return d if isinstance(d, dict) else {}
    except (OSError, ValueError):
        return {}


def version_info(root: str, name: str, v: int) -> dict:
    return _read_json(os.path.join(root, name, f"v{v}", VERSION_FILE))


def local_version(project_dir: str) -> dict:
    return _read_json(os.path.join(project_dir, VERSION_FILE))


def local_changed(project_dir: str) -> bool:
    """本機改過還沒上傳：追蹤的檔案有任何一個比 version.json 新。沒有 version.json＝還沒上傳過（算改過）。"""
    vp = os.path.join(project_dir, VERSION_FILE)
    if not os.path.isfile(vp):
        return True
    base = os.path.getmtime(vp)
    return any(os.path.isfile(p) and os.path.getmtime(p) > base + 1.0 for p in (os.path.join(project_dir, k) for k in CHANGE_KEYS))


def sync_files(project_dir: str) -> list[str]:
    """要同步的檔（相對路徑）：config.json＋整個 items/，不含追蹤快取 trace.json、備份檔、訓練暫存。"""
    out = []
    if os.path.isfile(os.path.join(project_dir, "config.json")):
        out.append("config.json")
    items_dir = os.path.join(project_dir, "items")
    for dp, dns, fns in os.walk(items_dir):
        dns[:] = [d for d in dns if not d.startswith("_")]
        for fn in fns:
            if _SKIP_RE.match(fn):
                continue
            out.append(os.path.relpath(os.path.join(dp, fn), project_dir))
    return sorted(out)


def _size_mb(d: str) -> float:
    n = 0
    for dp, _, fns in os.walk(d):
        n += sum(os.path.getsize(os.path.join(dp, f)) for f in fns)
    return round(n / 1048576, 1)


def _summary(cfg: dict) -> dict:
    pk = cfg.get("packaging") or {}
    return {"style": pk.get("style", ""), "region": pk.get("region", ""), "style_name": pk.get("style_name", ""),
            "customer": pk.get("customer", ""), "steps": len(cfg.get("steps") or []), "model_source": pk.get("model_source")}


def _status(local_dir: str, cur: int | None) -> tuple[str, int | None]:
    """本機跟共用硬碟目前版本的關係：none（本機沒有）／same／shared_newer／local_changed／other（本機是別的版本）。"""
    if not os.path.isdir(local_dir):
        return "none", None
    lv = local_version(local_dir).get("version")
    lv = int(lv) if isinstance(lv, int) or (isinstance(lv, str) and lv.isdigit()) else None
    if local_changed(local_dir):
        return "local_changed", lv
    if lv is None or cur is None:
        return "local_changed", lv
    if lv == cur:
        return "same", lv
    return ("shared_newer" if lv < cur else "other"), lv


def list_shared(root: str | None = None) -> list[dict]:
    """共用硬碟上的每個專案：目前版本、所有版本、本機狀態。"""
    root = _root(root)
    rows = []
    for name in sorted(os.listdir(root)):
        d = os.path.join(root, name)
        if name.startswith(("_", ".")) or not os.path.isdir(d):
            continue
        vs = versions(root, name)
        if not vs:
            continue
        cur = current(root, name)
        show = cur if cur in vs else vs[-1]
        cfg = _read_json(os.path.join(d, f"v{show}", "config.json"))
        info = version_info(root, name, show)
        st, lv = _status(os.path.join(projects_dir(), name), cur)
        rows.append({"name": name, **_summary(cfg), "current": cur, "versions": [{"version": v, **version_info(root, name, v)} for v in reversed(vs)],
                     "model_trained_at": info.get("model_trained_at"), "uploaded_at": info.get("uploaded_at"), "by": info.get("by"),
                     "size_mb": _size_mb(os.path.join(d, f"v{show}")), "has_video": os.path.isdir(os.path.join(d, VIDEO_DIR)),
                     "status": st, "local_version": lv})
    return rows


def list_local(root: str | None = None) -> list[dict]:
    """這台電腦的每個專案跟共用硬碟比：沒上傳過／同版本／本機改過／共用有新版。"""
    root = _root(root)
    rows = []
    base = projects_dir()
    for name in sorted(os.listdir(base)):
        d = os.path.join(base, name)
        if not os.path.isfile(os.path.join(d, "config.json")):
            continue
        cur = current(root, name)
        st, lv = _status(d, cur)
        if cur is None and not versions(root, name):
            st = "not_on_share"
        rows.append({"name": name, **_summary(_read_json(os.path.join(d, "config.json"))), "local_version": lv, "current": cur, "status": st,
                     "has_model": os.path.isfile(os.path.join(d, "items", "model", "best.pt"))})
    return rows


# ---------------------------------------------------------------- 寫

def _copy(src: str, dst: str) -> None:
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    shutil.copy2(src, dst)                     # 保留修改時間：版本比對、「訓練 …」時間都靠它


def _model_time(project_dir: str) -> str:
    p = os.path.join(project_dir, "items", "model", "best.pt")
    return datetime.fromtimestamp(os.path.getmtime(p)).strftime("%Y/%m/%d %H:%M") if os.path.isfile(p) else ""


def upload(name: str, note: str = "", publish: bool = True, with_video: bool = False, root: str | None = None) -> dict:
    """上傳一個本機專案成共用硬碟的新版本。publish＝設成目前版本；這台載入後別人又傳過（current 不是 based_on）時不發布，
    回傳 needs_confirm，使用者確認後帶 publish=True、confirm=True 再呼叫 set_current。"""
    root = _root(root)
    p = load_project(name)
    src = p.dir_path
    lv = local_version(src).get("version")
    based_on = int(lv) if isinstance(lv, int) else None
    cur = current(root, name)
    pdir = os.path.join(root, name)
    os.makedirs(pdir, exist_ok=True)
    tmp = os.path.join(pdir, f"_uploading_{computer_name()}")
    shutil.rmtree(tmp, ignore_errors=True)
    files = sync_files(src)
    for rel in files:
        _copy(os.path.join(src, rel), os.path.join(tmp, rel))
    vs = versions(root, name)
    n = (vs[-1] if vs else 0) + 1
    info = {"version": n, "uploaded_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"), "by": computer_name(),
            "based_on": based_on, "model_trained_at": _model_time(src), "program": program_version(), "note": (note or "").strip(),
            "files": len(files)}
    while True:                                 # 兩台同時傳：撞號就用下一號，兩份都留
        info["version"] = n
        with open(os.path.join(tmp, VERSION_FILE), "w", encoding="utf-8") as f:
            json.dump(info, f, ensure_ascii=False, indent=1)
        try:
            os.rename(tmp, os.path.join(pdir, f"v{n}"))
            break
        except OSError:
            if not os.path.isdir(os.path.join(pdir, f"v{n}")):
                raise
            n += 1
    conflict = cur is not None and based_on != cur
    published = False
    if publish and not conflict:
        set_current(name, n, root)
        published = True
    if with_video and os.path.isfile(p.video_path):
        _copy(p.video_path, os.path.join(pdir, VIDEO_DIR, os.path.basename(p.video_path)))
    # 本機記下「我是 v n」（寫新檔：比追蹤的檔都新，所以本機算「沒改過」）
    with open(os.path.join(src, VERSION_FILE), "w", encoding="utf-8") as f:
        json.dump(info, f, ensure_ascii=False, indent=1)
    return {"name": name, "version": n, "published": published, "needs_confirm": publish and conflict, "current": current(root, name),
            "files": len(files)}


def set_current(name: str, v: int, root: str | None = None) -> int:
    """發布或退回：current.txt 改成這一版（不搬檔）。先寫暫存檔再換，別台讀到的一定是完整的一行。"""
    root = _root(root)
    if int(v) not in versions(root, name):
        raise ValueError(f"共用硬碟上「{name}」沒有 v{v}")
    path = os.path.join(root, name, CURRENT_FILE)
    tmp = path + f".{computer_name()}.tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        f.write(f"v{int(v)}\n")
    os.replace(tmp, path)
    return int(v)


def load(name: str, version: int | None = None, with_video: bool = False, running: tuple = (), root: str | None = None,
         _seen: set | None = None) -> dict:
    """把共用硬碟的某一版（預設目前版本）載入到這台電腦。running：正在監控的專案（不能更新）。"""
    root = _root(root)
    _seen = _seen if _seen is not None else set()
    v = int(version) if version is not None else current(root, name)
    if v is None:
        vs = versions(root, name)
        if not vs:
            raise ValueError(f"共用硬碟上沒有「{name}」")
        v = vs[-1]
    src = os.path.join(root, name, f"v{v}")
    if not os.path.isdir(src):
        raise ValueError(f"共用硬碟上「{name}」沒有 v{v}")
    if name in running:
        raise ValueError(f"「{name}」正在產線監控中，先到監控畫面停止，再載入")
    model = os.path.join(src, "items", "model", "best.pt")
    if os.path.isfile(model) and not zipfile.is_zipfile(model):
        raise ValueError(f"共用硬碟上「{name}」v{v} 的模型檔壞了（best.pt 不是完整的檔案），沒有載入")
    dst = os.path.join(projects_dir(), name)
    files = sync_files(src)
    for rel in files:
        _copy(os.path.join(src, rel), os.path.join(dst, rel))
    gone = [rel for rel in sync_files(dst) if rel not in files]      # 那一版沒有的同步檔（例如舊的 segments.json）拿掉，免得新舊混在一起
    for rel in gone:
        try:
            os.remove(os.path.join(dst, rel))
        except OSError:
            pass
    _copy(os.path.join(src, VERSION_FILE), os.path.join(dst, VERSION_FILE))   # 修改時間＝上傳時間，比其他檔新 → 本機算「沒改過」
    video = False
    if with_video:
        vd = os.path.join(root, name, VIDEO_DIR)
        cfg = _read_json(os.path.join(dst, "config.json"))
        vf = cfg.get("video_file") or ""
        sp = os.path.join(vd, vf)
        if vf and os.path.isfile(sp):
            lp = os.path.join(dst, vf)
            if not os.path.isfile(lp) or os.path.getsize(lp) != os.path.getsize(sp):
                _copy(sp, lp)
            video = True
    loaded = [{"name": name, "version": v}]
    _seen.add(name)
    ref = _summary(_read_json(os.path.join(dst, "config.json"))).get("model_source")
    if ref and ref not in _seen and versions(root, ref):           # 參考別的專案的模型：被參考的一起載，名稱不能改
        st, _ = _status(os.path.join(projects_dir(), ref), current(root, ref))
        if st in ("none", "shared_newer"):
            loaded += load(ref, None, False, running, root, _seen)["loaded"]
    return {"name": name, "version": v, "files": len(files), "video": video, "loaded": loaded}
