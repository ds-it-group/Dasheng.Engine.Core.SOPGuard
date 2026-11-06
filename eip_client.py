"""讀 EIP 看板已經開放、不用登入的 API（電視看板在用的那幾支）：產線清單、今天這條線的轉數表（型體、數量、時段）、整線報工。只讀，不寫回。

- EIP 網址存在這台電腦的 eip_api.txt（一行，跟手持 APP 連的同一台主機），不進 git。
- 產線清單：GET /api/MES/Organization/GetDepartmentsByDepartmentType/{廠別}/{製程類別}（後端查 org.Departments；製程類別預設 170 成型）
- 今天的轉數表：POST /api/MES/DashboardOrder/GetDashboardOrdersForPanel  {factoryCode, departmentID, timeZone}
  一張訂單一筆：OrderCode、SpecificationCode（型體，尾碼就是配色；逗號隔開＝多個型體）、TotalQuantity、TimeStart
- 整線報工：POST /api/MES/DashboardOrder/GetDashboardOrderDetailsForPanel（同上參數）各時段 Quantity、CompletedQuantity 加總
  （每張訂單的報工不可信：RFID 永遠記到當天 OrderID 最小那張，所以只用整線合計）
- timeZone：跟看板一樣用這台電腦的 UTC 時差（小時）。
- 連不上：回最後一次成功的資料，標 ok=False 與多久以前更新。同一條線 CACHE_SEC 秒內不重打。
"""
from __future__ import annotations

import json
import os
import threading
import time
import urllib.error
import urllib.parse
import urllib.request

from project_store import app_base_dir

API_FILE = "eip_api.txt"
DEPT_TYPE_ASSEMBLY = 170
# 製程類別＝部門檔的 DepartmentType；名稱照資料庫選項檔（cmn.OptionDts，OptionID 7：Department.DepartmentType）
DEPT_TYPES = [(140, "組底"), (150, "裁斷"), (160, "針車"), (170, "成型")]
TIMEOUT_SEC = 5.0
CACHE_SEC = 25.0
_lock = threading.Lock()
_cache: dict[tuple, dict] = {}          # (廠別, 產線) → {"at": 成功時間, "data": ...}
_tried: dict[tuple, float] = {}         # 最後一次打（不論成敗）的時間


def api_base() -> str:
    try:
        with open(os.path.join(app_base_dir(), API_FILE), "r", encoding="utf-8-sig") as f:
            return f.read().strip().rstrip("/")
    except OSError:
        return ""


def set_api_base(url: str) -> str:
    url = (url or "").strip().rstrip("/")
    if url and not url.lower().startswith(("http://", "https://")):
        raise ValueError("EIP 網址要以 http:// 或 https:// 開頭")
    with open(os.path.join(app_base_dir(), API_FILE), "w", encoding="utf-8") as f:
        f.write(url)
    return url


def _tz_hours() -> float:
    off = -(time.altzone if time.localtime().tm_isdst > 0 else time.timezone) / 3600.0
    return int(off) if off == int(off) else off


def _get(d: dict, *keys, default=None):
    """看板回的欄位名稱大小寫不一定（camelCase／PascalCase），不分大小寫取。"""
    low = {str(k).lower(): v for k, v in d.items()}
    for k in keys:
        if k.lower() in low and low[k.lower()] is not None:
            return low[k.lower()]
    return default


def _request(path: str, body: dict | None = None, opener=None):
    base = api_base()
    if not base:
        raise ValueError("還沒設定 EIP 網址（eip_api.txt）")
    url = base + path
    data = None if body is None else json.dumps(body).encode("utf-8")
    req = urllib.request.Request(url, data=data, method="GET" if body is None else "POST",
                                 headers={"Content-Type": "application/json", "Accept": "application/json"})
    with (opener or urllib.request.urlopen)(req, timeout=TIMEOUT_SEC) as r:
        return json.loads(r.read().decode("utf-8") or "null")


def departments(factory: str, dept_type: int = DEPT_TYPE_ASSEMBLY, opener=None) -> list[dict]:
    """這個廠某個製程類別的實際產線（部門檔）：[{id, code, name}]。"""
    factory = (factory or "").strip()
    if not factory:
        raise ValueError("先填廠別")
    rows = _request(f"/api/MES/Organization/GetDepartmentsByDepartmentType/{urllib.parse.quote(factory)}/{int(dept_type)}", opener=opener) or []
    out = []
    today = time.strftime("%Y-%m-%d")
    for r in rows:
        did = _get(r, "departmentID")
        if did is None:
            continue
        # 後端會把外包廠商（DepartmentType 0＋IsVendor）一起回，也不擋已停用的；只留這個製程類別、還在用的實際產線
        typ = _get(r, "departmentType")
        if _get(r, "isVendor") is True or (typ is not None and int(typ) != int(dept_type)):
            continue
        end = str(_get(r, "endAt", default="") or "")[:10]
        if end and end < today:
            continue
        code = str(_get(r, "departmentCode", default="") or "")
        out.append({"id": int(did), "code": code, "name": str(_get(r, "departmentNameTC", "departmentName", default="") or code)})
    return out


def group_orders(rows: list[dict]) -> list[dict]:
    """轉數表一張訂單一筆 → 一個型體一筆：數量加總、訂單編號收集；照第一個時段先後排，沒排時段的排最後。"""
    out: dict[str, dict] = {}
    for r in rows or []:
        spec = str(_get(r, "specificationCode", default="") or "")
        styles = [s.strip() for s in spec.split(",") if s.strip()] or ["（沒有型體）"]
        qty = int(_get(r, "totalQuantity", default=0) or 0)
        t0 = _get(r, "timeStart")
        for s in styles:
            g = out.setdefault(s, {"style": s, "qty": 0, "orders": [], "time_start": None})
            g["qty"] += qty if len(styles) == 1 else 0     # 一張單寫了多個型體：數量分不出來，不加
            code = str(_get(r, "orderCode", default="") or "")
            if code and code not in g["orders"]:
                g["orders"].append(code)
            if t0 is not None and (g["time_start"] is None or str(t0) < str(g["time_start"])):
                g["time_start"] = t0
    return sorted(out.values(), key=lambda g: (g["time_start"] is None, str(g["time_start"] or ""), g["style"]))


def today(factory: str, department_id: int, opener=None, now=None) -> dict:
    """今天這條線：{"ok", "updated_at", "ago_sec", "styles", "target", "eip_done", "error"}。連不上回最後一次的資料。"""
    key = (str(factory), int(department_id))
    now = time.time() if now is None else now
    with _lock:
        c = _cache.get(key); last_try = _tried.get(key, 0.0)
    if c and now - last_try < CACHE_SEC:
        return {**c["data"], "ok": c.get("ok", True), "ago_sec": int(now - c["at"]), "error": c.get("error")}
    body = {"factoryCode": factory, "departmentID": int(department_id), "timeZone": _tz_hours()}
    try:
        orders = _request("/api/MES/DashboardOrder/GetDashboardOrdersForPanel", body, opener) or []
        details = _request("/api/MES/DashboardOrder/GetDashboardOrderDetailsForPanel", body, opener) or []
        data = {"styles": group_orders(orders), "target": sum(int(_get(r, "quantity", default=0) or 0) for r in details),
                "eip_done": sum(int(_get(r, "completedQuantity", default=0) or 0) for r in details),
                "updated_at": time.strftime("%H:%M:%S", time.localtime(now))}
        if not data["target"]:
            data["target"] = sum(int(_get(r, "totalQuantity", default=0) or 0) for r in orders)
        with _lock:
            _cache[key] = {"at": now, "data": data, "ok": True}; _tried[key] = now
        return {**data, "ok": True, "ago_sec": 0, "error": None}
    except (OSError, ValueError, urllib.error.URLError) as e:
        msg = str(e.reason) if isinstance(e, urllib.error.URLError) and hasattr(e, "reason") else str(e)
        with _lock:
            _tried[key] = now
            if key in _cache:
                _cache[key]["ok"] = False; _cache[key]["error"] = msg
                c = _cache[key]
        if c:
            return {**c["data"], "ok": False, "ago_sec": int(now - c["at"]), "error": msg}
        return {"ok": False, "styles": [], "target": 0, "eip_done": 0, "updated_at": None, "ago_sec": None, "error": msg}


def clear_cache() -> None:
    with _lock:
        _cache.clear(); _tried.clear()
