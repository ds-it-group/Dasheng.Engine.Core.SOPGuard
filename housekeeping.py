"""舊紀錄只留 KEEP_DAYS 天（設計：error_logs 的截圖和 events.csv 一筆一筆存本機，留 30 天自動刪，不上傳）。

- 每個專案的 error_logs/：截圖等檔案修改時間超過 30 天就刪；events.csv 留 time_iso 在 30 天內的列（表頭保留）。
- 程式一開跑一次，之後每天一次。當天統計（logs/daily）、換線紀錄（logs/line_switch.csv）不刪，檔案很小。
"""
from __future__ import annotations

import csv
import os
import threading
import time
from datetime import datetime, timedelta

KEEP_DAYS = 30
_thread: threading.Thread | None = None


def clean_project(dir_path: str, now: datetime | None = None, keep_days: int = KEEP_DAYS) -> dict:
    now = now or datetime.now()
    cutoff = now - timedelta(days=keep_days)
    d = os.path.join(dir_path, "error_logs")
    out = {"files": 0, "rows": 0}
    if not os.path.isdir(d):
        return out
    for fn in os.listdir(d):
        p = os.path.join(d, fn)
        if fn == "events.csv" or not os.path.isfile(p):
            continue
        if datetime.fromtimestamp(os.path.getmtime(p)) < cutoff:
            try:
                os.remove(p); out["files"] += 1
            except OSError:
                pass
    ev = os.path.join(d, "events.csv")
    if os.path.isfile(ev):
        with open(ev, "r", encoding="utf-8-sig", newline="") as f:
            rows = list(csv.reader(f))
        if rows:
            head, body = rows[0], rows[1:]
            i = head.index("time_iso") if "time_iso" in head else None
            if i is not None:
                keep = []
                for r in body:
                    try:
                        if datetime.fromisoformat(r[i]) < cutoff:
                            continue
                    except (IndexError, ValueError):
                        pass                       # 看不懂時間的列留著
                    keep.append(r)
                if len(keep) < len(body):
                    tmp = ev + ".tmp"
                    with open(tmp, "w", encoding="utf-8-sig", newline="") as f:
                        w = csv.writer(f); w.writerow(head); w.writerows(keep)
                    os.replace(tmp, ev)
                    out["rows"] = len(body) - len(keep)
    return out


def clean_all(now: datetime | None = None) -> dict:
    from project_store import projects_dir
    total = {"files": 0, "rows": 0}
    base = projects_dir()
    for name in os.listdir(base):
        p = os.path.join(base, name)
        if os.path.isdir(p):
            r = clean_project(p, now)
            total["files"] += r["files"]; total["rows"] += r["rows"]
    return total


def start() -> None:
    global _thread
    if _thread is not None and _thread.is_alive():
        return

    def loop():
        while True:
            try:
                clean_all()
            except Exception:
                pass
            time.sleep(24 * 3600)

    _thread = threading.Thread(target=loop, name="housekeeping", daemon=True)
    _thread.start()
