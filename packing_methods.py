"""包裝方式目錄：每個專案（sop_projects/<名稱>）就是一個包裝方式，身分記在 config.json 的 packaging（型體＋地區）。

- 主鍵＝型體（不含配色）＋地區，全部專案中不可重複
- 步驟清單永遠用自己的；辨識模型可以用自己的，或參考另一個型體地區（model_source）
- 配色不進主鍵：packaging.colors 記錄模型驗證過哪些配色；沒驗證過的配色可以監控，但算「試跑」
"""
from __future__ import annotations

import json
import os
import shutil
from datetime import datetime

import item_recognizer as items
from project_store import (COLOR_STATUSES, ColorCheck, ProjectConfigError, Step, list_projects, load_project, parse_packaging,
                           projects_dir, save_project, validate_project_name)

NEW_COLOR = "__new"         # 換線時選「新配色（模型沒看過）」
STYLE_RULE_TEXT = "型體要照規定：6 碼數字＋空一格＋2 碼數字，例如 310222 01"


def normalize_style(s: str) -> str:
    """型體代碼照公司規定「6 碼＋空白＋2 碼」（例 310222 01）。31022201、310222-01、310222_01、多個空白都整理成標準寫法；
    其他格式丟 ValueError。"""
    import re
    raw = (s or "").strip()
    m = re.fullmatch(r"(\d{6})[\s\-_]*(\d{2})", raw)
    if not m:
        raise ValueError(f"{STYLE_RULE_TEXT}（你輸入的是「{raw}」）")
    return f"{m.group(1)} {m.group(2)}"


def _checked_style(new: str, current: str | None) -> str:
    """新填或改過的型體才檢查格式；沒改（舊資料、規定之前建的）照原樣保留。"""
    if current is not None and (new or "").strip() == current:
        return current
    return normalize_style(new)


def _try_load(name: str):
    try:
        return load_project(name)
    except Exception:
        return None


def model_trained_at(path: str) -> str | None:
    return datetime.fromtimestamp(os.path.getmtime(path)).strftime("%Y/%m/%d %H:%M") if os.path.isfile(path) else None


def model_items(project) -> list[str]:
    """模型認得的物品名稱：用訓練它的專案的種子檔（不必載入模型）。"""
    src = project.packaging.model_source if project.packaging and project.packaging.model_source else None
    d = os.path.join(projects_dir(), src) if src else project.dir_path
    try:
        return list(items.ItemSeeds(d).order)
    except Exception:
        return []


def method_row(p, lines_by_project: dict | None = None) -> dict:
    pk = p.packaging
    mp = items.model_path(p); own = items.own_model_path(p)
    item_steps = [s for s in p.steps if s.type in ("item", "hand_on_object")]
    return {
        "name": p.project_name,
        "style": pk.style if pk else "", "region": pk.region if pk else "",
        "style_name": pk.style_name if pk else "", "customer": pk.customer if pk else "",
        "enabled": pk.enabled if pk else True, "has_packaging": pk is not None,
        "model_source": pk.model_source if pk else None,
        "model_trained_at": model_trained_at(mp), "own_model": os.path.isfile(own),
        "model_stale": items.model_stale_reason(p),       # 訓練後桌面範圍改了 → 要重新訓練（不擋監控）
        "steps": len(p.steps), "item_steps": len(item_steps),
        "colors": [{"name": c.name, "status": c.status, "checked_at": c.checked_at, "note": c.note} for c in pk.colors] if pk else [],
        "lines": (lines_by_project or {}).get(p.project_name, []),
        "has_video": os.path.isfile(p.video_path),
    }


def list_methods(lines_by_project: dict | None = None) -> list[dict]:
    rows = []
    for n in list_projects():
        p = _try_load(n)
        if p is None:
            rows.append({"name": n, "error": "設定檔有問題", "has_packaging": False, "steps": 0})
            continue
        rows.append(method_row(p, lines_by_project))
    rows.sort(key=lambda r: (not r.get("has_packaging"), r.get("style", ""), r.get("region", ""), r["name"]))
    return rows


def find_method(style: str, region: str, exclude: str | None = None) -> str | None:
    for n in list_projects():
        if n == exclude:
            continue
        p = _try_load(n)
        if p is not None and p.packaging and p.packaging.style == style.strip() and p.packaging.region == region.strip():
            return n
    return None


def check_model_source(project_name: str, source: str | None) -> None:
    if not source:
        return
    if source == project_name:
        raise ValueError("不能參考自己的模型")
    src = _try_load(source)
    if src is None:
        raise ValueError(f"找不到參考來源「{source}」")
    if not os.path.isfile(items.own_model_path(src)):
        raise ValueError(f"參考來源「{source}」自己還沒有訓練好的模型")


def set_packaging(project_name: str, data: dict) -> dict:
    """新增或修改型體地區（主鍵不可重複）。data 只要給要改的欄位；colors 不在這裡改（用 set_color）。"""
    p = load_project(project_name)
    cur = p.packaging
    if "style" in data:
        data = dict(data, style=_checked_style(str(data["style"]), cur.style if cur else None))
    merged = {"style": data.get("style", cur.style if cur else ""), "region": data.get("region", cur.region if cur else ""),
              "style_name": data.get("style_name", cur.style_name if cur else ""), "customer": data.get("customer", cur.customer if cur else ""),
              "model_source": data.get("model_source", cur.model_source if cur else None) or None,
              "enabled": data.get("enabled", cur.enabled if cur else True),
              "colors": [c.__dict__ for c in cur.colors] if cur else []}
    try:
        pk = parse_packaging(merged, p.project_name)
    except ProjectConfigError as e:
        raise ValueError(str(e))
    other = find_method(pk.style, pk.region, exclude=p.project_name)
    if other:
        raise ValueError(f"型體 {pk.style}／{pk.region} 已經有包裝方式了（{other}）")
    check_model_source(p.project_name, pk.model_source)
    p.packaging = pk
    save_project(p)
    return method_row(p)


def delete_methods(names: list[str], lines_by_project: dict | None = None, busy: tuple = ()) -> list[str]:
    """刪掉停用的包裝方式（整個專案資料夾，不能復原；共用硬碟上的版本不動）。
    只能刪停用的；產線正在用、別的包裝方式參考它的模型、正在監控／訓練／錄影的不能刪。先全部檢查過才動手，有一個不行就全部不刪。"""
    names = [str(n) for n in dict.fromkeys(names or [])]
    if not names:
        raise ValueError("請勾選要刪除的包裝方式")
    used = lines_by_project or {}
    refs = {}
    for n in list_projects():
        p = _try_load(n)
        if p is not None and p.packaging and p.packaging.model_source:
            refs.setdefault(p.packaging.model_source, []).append(n)
    for n in names:
        validate_project_name(n)
        p = _try_load(n)
        if p is None:
            raise ValueError(f"找不到「{n}」")
        if p.packaging is None or p.packaging.enabled:
            raise ValueError(f"「{n}」沒有停用，不能刪除")
        if used.get(n):
            raise ValueError(f"「{n}」產線 {'、'.join(used[n])} 正在用，不能刪除")
        if n in busy:
            raise ValueError(f"「{n}」正在監控、訓練或錄影，不能刪除")
        other = [r for r in refs.get(n, []) if r not in names]
        if other:
            raise ValueError(f"「{n}」的模型被 {'、'.join(other)} 參考，不能刪除")
    for n in names:
        shutil.rmtree(os.path.join(projects_dir(), n))
    return names


def set_color(project_name: str, color: str, status: str, note: str = "") -> dict:
    p = load_project(project_name)
    if p.packaging is None:
        raise ValueError("這個專案還沒設定型體地區")
    color = (color or "").strip()
    if not color or color == NEW_COLOR:
        raise ValueError("請輸入配色名稱")
    if status == "remove":
        p.packaging.colors = [c for c in p.packaging.colors if c.name != color]
    else:
        if status not in COLOR_STATUSES:
            raise ValueError(f"驗證結果只能是 {COLOR_STATUSES}")
        hit = next((c for c in p.packaging.colors if c.name == color), None)
        day = datetime.now().strftime("%Y/%m/%d") if status != "unverified" else ""
        if hit is None:
            p.packaging.colors.append(ColorCheck(color, status, day, note))
        else:
            hit.status = status; hit.checked_at = day if status != "unverified" else hit.checked_at; hit.note = note or hit.note
    save_project(p)
    return method_row(p)


def color_status(project, color: str | None) -> str:
    """verified / unverified / failed / new（模型沒看過）/ none（不分配色）。
    沒指定配色＝none：2026-11-05 使用者裁示「沒有配色這層，型體尾碼就是配色」，畫面不再選配色，所以不算試跑。
    只有明確給了沒驗證過的配色（舊資料）才算試跑。"""
    if project.packaging is None or not color:
        return "none"
    if color == NEW_COLOR:
        return "new"
    hit = next((c for c in project.packaging.colors if c.name == color), None)
    return hit.status if hit else "new"


def is_trial(project, color: str | None) -> bool:
    return color_status(project, color) not in ("verified", "none")


def update_steps(project_name: str, rows: list[dict]) -> dict:
    """包裝明細頁改步驟清單：只動物品步驟的名稱、辨識物品、停留秒數、必要；可刪、可調順序、可新增物品步驟。
    非物品步驟（手勢等）原樣保留在原位置之後。"""
    p = load_project(project_name)
    known = set(model_items(p))
    old = {s.step_index: s for s in p.steps}
    new_steps = []
    for k, r in enumerate(rows):
        name = str(r.get("name", "")).strip()
        if not name:
            raise ValueError(f"第 {k + 1} 步沒有名稱")
        try:
            dwell = float(r.get("dwell"))
        except (TypeError, ValueError):
            raise ValueError(f"「{name}」的停留秒數不是數字")
        if not 0.1 <= dwell <= 10:
            raise ValueError(f"「{name}」的停留秒數要在 0.1～10 秒")
        src = old.get(r.get("index")) if r.get("index") is not None else None
        if src is not None and src.type != "item":
            st = src
            st.step_name = name; st.dwell_time_sec = dwell; st.required = bool(r.get("required", True))
        else:
            label = str(r.get("label", "")).strip()
            if known and label not in known:
                raise ValueError(f"「{name}」的辨識物品「{label}」不在模型認得的物品裡（{'、'.join(sorted(known))}）")
            if not label:
                raise ValueError(f"「{name}」要選辨識物品")
            st = Step(step_index=0, step_name=name, dwell_time_sec=dwell, timeout_sec=src.timeout_sec if src else 120.0, type="item",
                      label=label, required=bool(r.get("required", True)), continuous=src.continuous if src else False)
        new_steps.append(st)
    if len({s.step_name for s in new_steps}) != len(new_steps):
        raise ValueError("步驟名稱不能重複")
    for i, s in enumerate(new_steps):
        s.step_index = i
    if p.cycle_end is not None and p.cycle_end.type == "steps_done" and p.cycle_end.label:
        renamed = {old[r.get("index")].step_name: str(r.get("name", "")).strip() for r in rows if r.get("index") in old}
        last = renamed.get(p.cycle_end.label, p.cycle_end.label)
        p.cycle_end.label = last if last in {s.step_name for s in new_steps} else None    # 最後一步被刪了：改回「都做到才結算」
    p.steps = new_steps
    save_project(p)
    return method_row(p)


END_BOX_HOLD = 0.5          # 盒子拿走：沿用 training.apply_item_steps 的去抖秒數與清空秒數
END_BOX_ARM = 0.2
END_STEPS_ARM = 1.0         # 步驟都做到：結算後工作區要清空這麼久才開下一輪（同一雙鞋卡在畫面上不會一直重複計數）
END_IDLE_RANGE = (2.0, 60.0)


def cycle_end_row(p) -> dict:
    """給包裝明細看的「一輪怎麼結束」：mode＝box（盒子拿走）／steps（必要步驟都做到）／other（手勢等舊設定，畫面只顯示）。"""
    e = p.cycle_end
    if e is not None and e.type == "steps_done":
        return {"mode": "steps", "last": e.label or "", "idle_sec": e.dwell_time_sec}
    if e is None or e.type == "object_absent":
        return {"mode": "box", "last": "", "idle_sec": None}
    return {"mode": "other", "last": "", "idle_sec": None, "type": e.type}


def set_cycle_end(project_name: str, data: dict) -> dict:
    """包裝明細改「一輪怎麼結束」。box：盒子（state_anchor）拿走 0.5 秒就結算；steps：必要步驟都做到、或做到 last 那一步就結算，
    idle_sec 秒都沒看到任何步驟也結算（報漏做）。之後重新訓練、產生步驟都會保留（training.apply_item_steps）。"""
    p = load_project(project_name)
    mode = str(data.get("mode", ""))
    if mode == "box":
        from training import ensure_state_anchor
        ensure_state_anchor(p)                     # 盒子拿走要有「盒子」錨點；沒有就補（跟訓練時一樣）
        p.cycle_end = Step(step_index=-1, step_name="cycle_end", dwell_time_sec=END_BOX_HOLD, timeout_sec=1.0, type="object_absent",
                           object=p.state_anchor or "box")
        p.cycle_arm_clear_sec = END_BOX_ARM
    elif mode == "steps":
        try:
            idle = float(data.get("idle_sec", 6.0))
        except (TypeError, ValueError):
            raise ValueError("「沒動作幾秒也結算」要填數字")
        if not END_IDLE_RANGE[0] <= idle <= END_IDLE_RANGE[1]:
            raise ValueError(f"「沒動作幾秒也結算」要在 {END_IDLE_RANGE[0]:g}～{END_IDLE_RANGE[1]:g} 秒")
        last = str(data.get("last", "") or "").strip() or None
        if last is not None and last not in [st.step_name for st in p.steps]:
            raise ValueError(f"沒有「{last}」這一步")
        p.cycle_end = Step(step_index=-1, step_name="cycle_end", dwell_time_sec=idle, timeout_sec=1.0, type="steps_done", label=last)
        p.cycle_arm_clear_sec = END_STEPS_ARM
    else:
        raise ValueError("結束方式只能選「盒子拿走」或「必要步驟都做到」")
    save_project(p)
    return method_detail(project_name)


def wizard_name(style: str, region: str) -> str:
    """精靈建專案時的資料夾名稱＝型體_地區（不合法的字元換成 -）。"""
    raw = f"{style.strip()}_{region.strip()}"
    return "".join("-" if c in '\\/:*?"<>|' else c for c in raw).strip(" .")


def wizard_state(name: str) -> dict:
    """精靈的狀態：step 1＝還缺型體地區或示範影片、step 2＝影片有了，到「包裝設定（訓練）」繼續（框選、訓練、產生步驟都在那一頁）。
    每個包裝方式都用自己的影片與模型，不參照別的包裝方式。"""
    p = load_project(name)
    has_video = os.path.isfile(p.video_path)
    step = 1 if p.packaging is None or not has_video else 2
    return {"name": name, "step": step, "method": method_row(p), "has_video": has_video, "resolution": list(p.resolution)}


def method_detail(project_name: str, lines_by_project: dict | None = None) -> dict:
    p = load_project(project_name)
    row = method_row(p, lines_by_project)
    from training import first_segment_starts
    starts = first_segment_starts(p); fps = float(p.fps or 30.0)
    row["step_rows"] = [{"index": s.step_index, "name": s.step_name, "type": s.type, "label": s.label or s.object or "",
                         "dwell": s.dwell_time_sec, "required": s.required,
                         "start_t": round(starts[s.step_name] / fps, 1) if s.step_name in starts else None} for s in p.steps]
    row["model_items"] = model_items(p)
    row["cycle_end"] = p.cycle_end.type if p.cycle_end else None
    row["cycle_end_cfg"] = cycle_end_row(p)
    row["state_fixed"] = p.state_fixed
    row["resolution"] = list(p.resolution)
    return row
