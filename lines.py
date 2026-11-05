"""產線設定（lines.json，只留在這台電腦：相機網址可能含密碼）與換線紀錄（logs/line_switch.csv）。

一條產線記：相機、桌面範圍（跟著相機位置走，所以放產線不放包裝方式）、目前用哪個包裝方式（專案）、配色、換線時間。
"""
from __future__ import annotations

import csv
import json
import os
import re
import threading
from dataclasses import asdict, dataclass
from datetime import datetime

import packing_methods as pkg
from project_store import app_base_dir, load_project, rect_inside

LINES_FILE = "lines.json"
SWITCH_LOG = os.path.join("logs", "line_switch.csv")
_lock = threading.Lock()


@dataclass
class Line:
    id: str
    name: str
    factory: str = ""
    camera: str = ""                        # 相機來源：編號（0）或 rtsp 網址；網頁上會遮掉密碼
    table_region: list[int] | None = None   # [x, y, w, h]；None＝用包裝方式自己的桌面範圍
    project: str | None = None              # 目前的包裝方式（專案名稱）
    color: str = ""                         # 目前做的配色；"__new"＝模型沒看過的新配色
    switched_at: str = ""                   # YYYY/MM/DD HH:MM
    enabled: bool = True
    eip_department_id: int | None = None    # EIP 產線（部門檔 DepartmentID）；None＝沒接 EIP。廠別用上面的 factory
    eip_department_name: str = ""           # 顯示用（選的時候記下來，連不上 EIP 也看得到）
    station_label: str = ""                 # 這台電腦的顯示名稱（例如 A 站），只在這台顯示；上傳用電腦名稱


def computer_name() -> str:
    """站別＝這台電腦的名稱（自動帶、不用填；一條 EIP 產線接多台電腦時靠它分開）。"""
    import socket
    return os.environ.get("COMPUTERNAME") or socket.gethostname() or "unknown"


def _path() -> str:
    return os.path.join(app_base_dir(), LINES_FILE)


def _default_lines() -> list[Line]:
    """第一次用：把舊的 camera_source.txt 當成「包裝 1 線」的相機。"""
    cam = ""
    try:
        with open(os.path.join(app_base_dir(), "camera_source.txt"), "r", encoding="utf-8-sig") as f:
            cam = f.read().strip()
    except OSError:
        pass
    return [Line(id="L1", name="包裝 1 線", camera=cam)]


def load_lines() -> list[Line]:
    with _lock:
        try:
            with open(_path(), "r", encoding="utf-8-sig") as f:
                raw = json.load(f)
        except FileNotFoundError:
            return _default_lines()
    out = []
    for r in raw.get("lines", []):
        reg = r.get("table_region")
        out.append(Line(id=str(r["id"]), name=str(r.get("name", r["id"])), factory=str(r.get("factory", "")), camera=str(r.get("camera", "")),
                        table_region=[int(v) for v in reg] if isinstance(reg, list) and len(reg) == 4 else None,
                        project=r.get("project") or None, color=str(r.get("color", "")), switched_at=str(r.get("switched_at", "")),
                        enabled=bool(r.get("enabled", True)),
                        eip_department_id=int(r["eip_department_id"]) if str(r.get("eip_department_id") or "").isdigit() else None,
                        eip_department_name=str(r.get("eip_department_name", "") or ""), station_label=str(r.get("station_label", "") or "")))
    return out


def save_lines(lines: list[Line]) -> None:
    with _lock:
        tmp = _path() + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump({"lines": [asdict(l) for l in lines]}, f, ensure_ascii=False, indent=2)
        os.replace(tmp, _path())


def get_line(line_id: str) -> Line:
    for l in load_lines():
        if l.id == line_id:
            return l
    raise ValueError(f"找不到產線「{line_id}」")


def mask_camera(src: str) -> str:
    """rtsp://帳號:密碼@主機 → rtsp://帳號:***@主機（網頁只顯示遮過的）。"""
    return re.sub(r"(//[^:/@\s]+:)[^@/\s]+@", r"\1***@", src or "")


def lines_by_project(lines: list[Line] | None = None) -> dict[str, list[str]]:
    out: dict[str, list[str]] = {}
    for l in lines if lines is not None else load_lines():
        if l.project:
            out.setdefault(l.project, []).append(l.name)
    return out


def line_public(l: Line) -> dict:
    d = asdict(l)
    d["camera"] = mask_camera(l.camera)
    d["has_camera"] = bool(l.camera.strip())
    d["station"] = computer_name()
    d["packaging"] = None
    d["can_run"] = False
    d["problem"] = "停用" if not l.enabled else ("還沒指定包裝方式" if not l.project else "")
    if l.project:
        try:
            p = load_project(l.project)
            row = pkg.method_row(p)
            d["packaging"] = row
            d["color_status"] = pkg.color_status(p, l.color)
            d["trial"] = pkg.is_trial(p, l.color)
            if not row["model_trained_at"]:
                d["problem"] = d["problem"] or "包裝方式的辨識模型還沒訓練"
            elif not p.steps:
                d["problem"] = d["problem"] or "包裝方式還沒有步驟"
            elif row["has_packaging"] and not row["enabled"]:
                d["problem"] = d["problem"] or "包裝方式已停用"
        except Exception as e:
            d["problem"] = d["problem"] or f"包裝方式載入失敗：{e}"
    d["can_run"] = d["problem"] == ""
    return d


def save_line(data: dict) -> Line:
    """新增或修改產線。camera 傳回遮過的字（含 ***）時保留原本的值。"""
    lines = load_lines()
    lid = str(data.get("id") or "").strip()
    cur = next((l for l in lines if l.id == lid), None) if lid else None
    name = str(data.get("name", cur.name if cur else "")).strip()
    if not name:
        raise ValueError("請輸入產線名稱")
    if any(l.name == name and l is not cur for l in lines):
        raise ValueError(f"產線名稱「{name}」重複")
    cam = data.get("camera", cur.camera if cur else "")
    cam = str(cam or "").strip()
    if cur is not None and "***" in cam:
        cam = cur.camera
    reg = data.get("table_region", cur.table_region if cur else None)
    if reg is not None:
        if not (isinstance(reg, list) and len(reg) == 4 and all(isinstance(v, (int, float)) for v in reg) and reg[2] > 0 and reg[3] > 0):
            raise ValueError("桌面範圍要是 [x, y, w, h] 四個數字，寬高大於 0")
        reg = [int(v) for v in reg]
    if cur is None:
        n = 1
        while any(l.id == f"L{n}" for l in lines):
            n += 1
        cur = Line(id=f"L{n}", name=name); lines.append(cur)
    cur.name = name; cur.camera = cam; cur.table_region = reg
    cur.factory = str(data.get("factory", cur.factory)).strip()
    cur.enabled = bool(data.get("enabled", cur.enabled))
    if "eip_department_id" in data:
        v = data.get("eip_department_id")
        cur.eip_department_id = int(v) if v not in (None, "") and str(v).isdigit() else None
        cur.eip_department_name = str(data.get("eip_department_name", "") or "").strip() if cur.eip_department_id else ""
        if cur.eip_department_id and not cur.factory:
            raise ValueError("接 EIP 要先填廠別")
    if "station_label" in data:
        cur.station_label = str(data.get("station_label") or "").strip()
    save_lines(lines)
    return cur


def delete_line(line_id: str) -> None:
    lines = load_lines()
    keep = [l for l in lines if l.id != line_id]
    if len(keep) == len(lines):
        raise ValueError(f"找不到產線「{line_id}」")
    save_lines(keep)


def switch_line(line_id: str, project_name: str, color: str = "") -> Line:
    """換包裝方式：檢查包裝方式能不能用，寫進產線並記一筆換線紀錄。"""
    lines = load_lines()
    l = next((x for x in lines if x.id == line_id), None)
    if l is None:
        raise ValueError(f"找不到產線「{line_id}」")
    if not l.enabled:
        raise ValueError("這條產線已停用")
    p = load_project(project_name)
    if p.packaging is not None and not p.packaging.enabled:
        raise ValueError("這個包裝方式已停用")
    if not p.steps:
        raise ValueError("這個包裝方式還沒有步驟")
    if not os.path.isfile(pkg.items.model_path(p)):
        raise ValueError("這個包裝方式的辨識模型還沒訓練，不能用來監控")
    if l.table_region is not None and not rect_inside(l.table_region, p.resolution[0], p.resolution[1]):
        raise ValueError(f"產線的桌面範圍 {l.table_region} 超出這個包裝方式的畫面大小 {p.resolution}")
    old = l.project
    color = (color or "").strip()
    if p.packaging is not None and color and color != pkg.NEW_COLOR and all(c.name != color for c in p.packaging.colors):
        pkg.set_color(project_name, color, "unverified")     # 第一次做的配色記進清單（未驗證），之後才能驗證
        p = load_project(project_name)
    l.project = project_name; l.color = color; l.switched_at = datetime.now().strftime("%Y/%m/%d %H:%M")
    save_lines(lines)
    _log_switch(l, old, pkg.is_trial(p, l.color))
    return l


def _log_switch(l: Line, old: str | None, trial: bool) -> None:
    path = os.path.join(app_base_dir(), SWITCH_LOG)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    new = not os.path.isfile(path)
    with open(path, "a", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f)
        if new:
            w.writerow(["時間", "產線", "原包裝方式", "新包裝方式", "配色", "試跑"])
        w.writerow([l.switched_at, l.name, old or "", l.project or "", "新配色" if l.color == pkg.NEW_COLOR else l.color, "是" if trial else "否"])
