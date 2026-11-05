"""今天會用到的模型先在背景轉好（OpenVINO），切換包裝方式時不用等轉檔。

監控畫面每次問 EIP 今天這條線的型體（/api/eip/today），就把這些型體在本機的模型排進背景佇列；一個一個轉，轉過的
（快取在 cache/ov_<雜湊>/，模型重訓後會自動重轉）直接跳過。有 GPU（CUDA）的電腦不用 OpenVINO，什麼都不做。
實測：轉檔約 5～11 秒、之後載入快很多；切換還要開模型與相機，所以不保證 3 秒內，但省掉最慢的轉檔。
"""
from __future__ import annotations

import os
import queue
import threading

_q: "queue.Queue[str]" = queue.Queue()
_seen: set[tuple] = set()
_lock = threading.Lock()
_thread: threading.Thread | None = None
warmed: list[str] = []                    # 轉好的模型路徑（測試、除錯用）


def _imgsz(pt_path: str) -> int:
    try:
        from ultralytics import YOLO
        return int((YOLO(pt_path).ckpt or {}).get("train_args", {}).get("imgsz") or 640)
    except Exception:
        return 640


def _worker(convert) -> None:
    while True:
        path = _q.get()
        try:
            if convert(path, _imgsz(path)):
                warmed.append(path)
        except Exception:
            pass                              # 轉不成就算了，切換時照舊（PyTorch 或當場轉）


def warm_paths(paths, convert=None) -> int:
    """把模型檔排進背景轉檔；回傳這次新排了幾個。"""
    global _thread
    try:
        import torch
        if torch.cuda.is_available():
            return 0
    except Exception:
        pass
    if convert is None:
        import item_recognizer as items
        convert = items.openvino_model
    n = 0
    with _lock:
        for p in paths:
            if not os.path.isfile(p):
                continue
            key = (os.path.abspath(p), int(os.path.getmtime(p)))
            if key in _seen:
                continue
            _seen.add(key); _q.put(p); n += 1
        if n and (_thread is None or not _thread.is_alive()):
            _thread = threading.Thread(target=_worker, args=(convert,), name="model-warm", daemon=True)
            _thread.start()
    return n


def warm_styles(styles: list[str]) -> int:
    """這些型體在本機、啟用中、有模型的包裝方式，模型排進背景轉檔。"""
    import item_recognizer as items
    import packing_methods as pkg
    from project_store import load_project
    want = set(styles or [])
    paths = []
    for m in pkg.list_methods({}):
        if m.get("style") in want and m.get("enabled", True) and m.get("model_trained_at"):
            try:
                paths.append(items.model_path(load_project(m["name"])))
            except Exception:
                pass
    return warm_paths(paths)
