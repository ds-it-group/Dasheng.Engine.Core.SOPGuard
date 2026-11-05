"""當天統計：每條線、每天、每個包裝方式記完成輪數、漏做輪數、超時次數、各步驟的漏做與超時次數；上傳到 EIP 的只有「錯誤原因和次數」。

- 本機檔 logs/daily/<產線>/<YYYY-MM-DD>.json（日期＝這台電腦的當地日，也就是廠區當地日），數字一變就更新；
  記兩個時間：updated_at（最後更新）、uploaded_at（最後上傳成功時 updated_at 是多少）。逐筆紀錄仍在 events.csv／error_logs，不上傳。
- 只記相機監控（示範影片播的不算）。試跑（舊資料裡沒驗證過的配色）不記。
- 上傳：程式一開（背景）、每 UPLOAD_EVERY_SEC 秒、停止監控、換線時，把「最後上傳成功」比「最後更新」舊的檔由舊到新送；
  送成功才記下。不限天數；同一筆重送 EIP 依「日期＋EIP 產線＋站別＋包裝方式＋步驟」覆蓋，不會算兩次。沒接 EIP 的產線只存本機。
- EIP 端（2026-11-05 使用者定案：一張表 mes.PackingGuardDailyErrors，時間記 UTC、日期記當地班日）：
  POST /api/MES/PackingGuard/SetDailyErrors，一站一天一個包裝方式送一包：
  {recordDate, factoryCode, departmentID, station, methodName, errors:[{name, missed, timeout}]}；errors 空＝那天這個包裝方式沒出錯（EIP 清掉舊列）。
  比照看板 API 不用登入、不帶金鑰（使用者裁示 11-05：金鑰一樣能仿冒，意義不大）；哪一台送的看內容裡的 station（電腦名稱）。
  這支 API 要 EIP 那邊開卡做，還沒做好之前上傳會失敗、資料留在本機等。
"""
from __future__ import annotations

import json
import os
import threading
import time
import urllib.error
import urllib.request
from datetime import datetime

from project_store import app_base_dir

DAILY_DIR = os.path.join("logs", "daily")
UPLOAD_PATH = "/api/MES/PackingGuard/SetDailyErrors"
UPLOAD_EVERY_SEC = 600
_lock = threading.Lock()
_state = {"running": False, "done": 0, "total": 0, "current": None, "last_ok_at": None, "last_error": None, "last_try_at": None,
          "backfilled": []}
_kick = threading.Event()
_thread: threading.Thread | None = None


def _dir(line_id: str) -> str:
    return os.path.join(app_base_dir(), DAILY_DIR, line_id)


def _path(line_id: str, day: str) -> str:
    return os.path.join(_dir(line_id), day + ".json")


def _load(path: str) -> dict:
    try:
        with open(path, "r", encoding="utf-8-sig") as f:
            d = json.load(f)
        return d if isinstance(d, dict) else {}
    except (OSError, ValueError):
        return {}


def _save(path: str, d: dict) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(d, f, ensure_ascii=False, indent=1)
    os.replace(tmp, path)


def record(line_id: str, method: str, kind: str, missing: list[str], now: datetime | None = None) -> dict:
    """監控每結算一輪（完成／漏做）或超時提醒一次就記一筆。missing＝漏的（或超時當下還沒做的）步驟名稱。"""
    now = now or datetime.now()
    day = now.strftime("%Y-%m-%d")
    with _lock:
        p = _path(line_id, day); d = _load(p)
        d.setdefault("date", day); d.setdefault("line", line_id)
        m = d.setdefault("methods", {}).setdefault(method, {"cycles": 0, "bad_cycles": 0, "timeouts": 0, "steps": {}})
        if kind == "完成":
            m["cycles"] += 1
        elif kind == "漏做":
            m["bad_cycles"] += 1
            for n in missing:
                m["steps"].setdefault(n, {"missed": 0, "timeout": 0})["missed"] += 1
        elif kind == "超時":
            m["timeouts"] += 1
            for n in missing:
                m["steps"].setdefault(n, {"missed": 0, "timeout": 0})["timeout"] += 1
        else:
            return d
        d["updated_at"] = now.isoformat(timespec="seconds")
        d["rev"] = int(d.get("rev", 0)) + 1            # 每記一筆加 1：比時間可靠（同一秒內上傳又記一筆，時間一樣會漏傳）
        _save(p, d)
    return d


def _is_pending(j: dict) -> bool:
    if "rev" in j:
        return j.get("uploaded_rev") != j["rev"]
    return bool(j.get("updated_at")) and j.get("uploaded_at") != j.get("updated_at")   # 舊檔沒有 rev


def day_file(line_id: str, day: str | None = None) -> dict:
    return _load(_path(line_id, day or datetime.now().strftime("%Y-%m-%d")))


def pending(line_id: str | None = None) -> list[tuple[str, str]]:
    """還沒上傳成功的 (產線, 日期)：最後上傳成功比最後更新舊（或沒傳過），由舊到新。"""
    base = os.path.join(app_base_dir(), DAILY_DIR)
    out = []
    if not os.path.isdir(base):
        return out
    for lid in sorted(os.listdir(base)):
        if line_id and lid != line_id:
            continue
        d = os.path.join(base, lid)
        if not os.path.isdir(d):
            continue
        for fn in sorted(os.listdir(d)):
            if not fn.endswith(".json"):
                continue
            if _is_pending(_load(os.path.join(d, fn))):
                out.append((lid, fn[:-5]))
    return sorted(out, key=lambda x: (x[1], x[0]))


def payloads(d: dict, factory: str, department_id: int, station: str) -> list[dict]:
    """一天的統計檔 → 每個包裝方式一包（只帶錯誤原因和次數）。"""
    out = []
    for name, m in sorted((d.get("methods") or {}).items()):
        errs = [{"name": n, "missed": int(v.get("missed", 0)), "timeout": int(v.get("timeout", 0))}
                for n, v in sorted(m.get("steps", {}).items()) if v.get("missed") or v.get("timeout")]
        out.append({"recordDate": d["date"], "factoryCode": factory, "departmentID": int(department_id), "station": station,
                    "methodName": name, "errors": errs})
    return out


def _post(url: str, body: dict, opener=None) -> None:
    req = urllib.request.Request(url, data=json.dumps(body, ensure_ascii=False).encode("utf-8"), method="POST",
                                 headers={"Content-Type": "application/json"})
    with (opener or urllib.request.urlopen)(req, timeout=10) as r:
        r.read()


def upload_pending(opener=None) -> dict:
    """把還沒傳成功的日子由舊到新送；遇到失敗就停（留到下一次）。沒接 EIP 的產線跳過（只存本機）。"""
    import eip_client
    import lines as line_store
    todo = []
    for lid, day in pending():
        try:
            l = line_store.get_line(lid)
        except ValueError:
            continue
        if l.eip_department_id and l.factory:
            todo.append((l, day))
    base = eip_client.api_base()
    with _lock:
        _state.update(running=True, done=0, total=len(todo), current=None, last_try_at=datetime.now().isoformat(timespec="seconds"))
    sent = []
    try:
        if todo and not base:
            raise ValueError("還沒設定 EIP 網址（eip_api.txt）")
        for l, day in todo:
            with _lock:
                _state["current"] = day
            p = _path(l.id, day)
            with _lock:
                d = _load(p)
            stamp, rev = d.get("updated_at"), d.get("rev")
            for body in payloads(d, l.factory, l.eip_department_id, line_store.computer_name()):
                _post(base + UPLOAD_PATH, body, opener)
            with _lock:                               # 記下送出去的是第幾版；送的時候又多記的，rev 會比較大，下次再送
                d2 = _load(p); d2["uploaded_at"] = stamp; d2["uploaded_rev"] = rev
                d2["uploaded_ok_at"] = datetime.now().isoformat(timespec="seconds"); _save(p, d2)
                _state["done"] += 1
            sent.append(day)
        with _lock:
            _state.update(last_error=None, last_ok_at=datetime.now().isoformat(timespec="seconds") if todo else _state["last_ok_at"])
    except (OSError, ValueError, urllib.error.URLError) as e:
        msg = f"HTTP {e.code}" if isinstance(e, urllib.error.HTTPError) else str(getattr(e, "reason", e))
        if isinstance(e, urllib.error.HTTPError) and e.code == 404:
            msg = "EIP 還沒有上傳統計的 API（要 EIP 那邊開卡）"
        elif isinstance(e, (urllib.error.URLError, OSError)) and not isinstance(e, urllib.error.HTTPError):
            msg = "連不上 EIP"
        with _lock:
            _state["last_error"] = msg
    finally:
        with _lock:
            _state.update(running=False, current=None)
            if sent and len(sent) > 1 or (sent and sent[0] != datetime.now().strftime("%Y-%m-%d")):
                _state["backfilled"] = sent
    return {"sent": sent, "error": _state["last_error"]}


def status(line_id: str) -> dict:
    """網頁上傳狀態：ok／fail／off（沒接 EIP）／backlog（正在補傳）＋還沒傳成功的日子。"""
    import lines as line_store
    try:
        l = line_store.get_line(line_id)
    except ValueError:
        return {"state": "off"}
    with _lock:
        s = dict(_state)
    pend = [day for lid, day in pending(line_id)]
    if not (l.eip_department_id and l.factory):
        st = "off"
    elif s["running"]:
        st = "backlog"
    elif s["last_error"] and pend:
        st = "fail"
    else:
        st = "ok"
    return {"state": st, "pending": pend, "error": s["last_error"], "last_ok_at": s["last_ok_at"], "done": s["done"], "total": s["total"],
            "current": s["current"], "backfilled": s["backfilled"], "every_sec": UPLOAD_EVERY_SEC}


def kick() -> None:
    """馬上上傳一次（停止監控、換線、按「立即上傳」時）。"""
    _kick.set()


def start_uploader() -> None:
    """程式一開就在背景補傳，之後每 UPLOAD_EVERY_SEC 秒一次；kick() 可以提早。"""
    global _thread
    if _thread is not None and _thread.is_alive():
        return

    def loop():
        while True:
            try:
                upload_pending()
            except Exception as e:                  # 背景執行緒不能掛掉
                with _lock:
                    _state["last_error"] = f"{type(e).__name__}: {e}"; _state["running"] = False
            _kick.wait(UPLOAD_EVERY_SEC); _kick.clear()

    _thread = threading.Thread(target=loop, name="daily-upload", daemon=True)
    _thread.start()
