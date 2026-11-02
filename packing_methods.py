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
    """verified / unverified / failed / new（模型沒看過）/ none（舊專案沒有型體地區，不分配色）。"""
    if project.packaging is None:
        return "none"
    if not color or color == NEW_COLOR:
        return "new"
    hit = next((c for c in project.packaging.colors if c.name == color), None)
    return hit.status if hit else "new"


def is_trial(project, color: str | None) -> bool:
    return color_status(project, color) not in ("verified", "none")


def update_steps(project_name: str, rows: list[dict]) -> dict:
    """包裝方式設定頁改步驟清單：只動物品步驟的名稱、辨識物品、停留秒數、必要；可刪、可調順序、可新增物品步驟。
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
    p.steps = new_steps
    save_project(p)
    return method_row(p)


def copy_method(source: str, targets: list[dict]) -> list[str]:
    """把來源的步驟清單複製到其他型體地區（可多筆）。新專案先參考來源的模型（來源自己沒有就沿用來源的參考），
    不複製影片與框選，之後要自己訓練再到標記頁錄影或上傳。回傳新專案名稱。"""
    src = load_project(source)
    if src.packaging is None:
        raise ValueError("來源還沒設定型體地區")
    if not targets:
        raise ValueError("請至少選一個要複製到的型體地區")
    model_src = source if os.path.isfile(items.own_model_path(src)) else src.packaging.model_source
    with open(os.path.join(src.dir_path, "config.json"), "r", encoding="utf-8-sig") as f:
        base_cfg = json.load(f)
    plan = []
    for t in targets:
        style = str(t.get("style", "")).strip(); region = str(t.get("region", "")).strip()
        if not style or not region:
            raise ValueError("每一筆都要有型體和地區")
        other = find_method(style, region)
        if other:
            raise ValueError(f"型體 {style}／{region} 已經有包裝方式了（{other}）")
        name = str(t.get("name") or f"{style}_{region}").strip()
        validate_project_name(name)
        if os.path.exists(os.path.join(projects_dir(), name)) or name in [n for n, _ in plan]:
            raise ValueError(f"專案名稱「{name}」已經存在")
        if (style, region) in [(c["packaging"]["style"], c["packaging"]["region"]) for _, c in plan]:
            raise ValueError(f"型體 {style}／{region} 重複")
        cfg = dict(base_cfg)
        cfg["project_name"] = name
        cfg["packaging"] = {"style": style, "region": region, "style_name": str(t.get("style_name", "")).strip(),
                            "customer": str(t.get("customer", src.packaging.customer)).strip(), "model_source": model_src,
                            "enabled": True, "colors": []}
        plan.append((name, cfg))
    made = []
    for name, cfg in plan:
        d = os.path.join(projects_dir(), name)
        os.makedirs(os.path.join(d, "error_logs"), exist_ok=True)
        with open(os.path.join(d, "config.json"), "w", encoding="utf-8") as f:
            json.dump(cfg, f, ensure_ascii=False, indent=2)
        try:
            load_project(name)
        except Exception:
            shutil.rmtree(d, ignore_errors=True)
            raise
        made.append(name)
    return made


def wizard_name(style: str, region: str) -> str:
    """精靈建專案時的資料夾名稱＝型體_地區（不合法的字元換成 -）。"""
    raw = f"{style.strip()}_{region.strip()}"
    return "".join("-" if c in '\\/:*?"<>|' else c for c in raw).strip(" .")


def suggest_sources(target: str, limit: int = 8) -> list[dict]:
    """「參照」候選：有步驟、有模型的包裝方式，依相似度排序——同客戶、型體代碼開頭相同的長度、同地區、有自己的模型、畫面大小一樣。"""
    tgt = load_project(target); pk = tgt.packaging
    out = []
    for n in list_projects():
        if n == target:
            continue
        p = _try_load(n)
        if p is None or not p.steps:
            continue
        row = method_row(p)
        if not row["model_trained_at"]:
            continue
        score = 0.0; why = []
        if pk and p.packaging:
            if pk.customer and pk.customer == p.packaging.customer:
                score += 3; why.append("同客戶")
            common = len(os.path.commonprefix([pk.style.upper(), p.packaging.style.upper()]))
            if common >= 2:
                score += min(common, 6) * 0.5; why.append(f"型體代碼前 {common} 碼相同")
            if pk.region == p.packaging.region:
                score += 1; why.append("同地區")
        if row["own_model"]:
            score += 1; why.append("有自己訓練的模型")
        if list(p.resolution) == list(tgt.resolution):
            score += 1; why.append("畫面大小一樣（桌面範圍可以直接用）")
        verified = [c.name for c in p.packaging.colors if c.status == "verified"] if p.packaging else []
        out.append({**row, "score": round(score, 1), "why": why, "verified_colors": verified,
                    "step_names": [s.step_name for s in p.steps]})
    out.sort(key=lambda r: (-r["score"], r["name"]))
    return out[:limit]


def wizard_state(name: str) -> dict:
    """精靈要從哪一步繼續：1 基本資料／影片、2 參照、3 自動標記、4 確認。"""
    import step_analysis
    p = load_project(name)
    seeds = items.ItemSeeds(p.dir_path)
    an = step_analysis.load(p)
    has_video = os.path.isfile(p.video_path)
    row = method_row(p)
    if p.packaging is None or not has_video:
        step = 1
    elif not p.steps or not row["model_trained_at"]:
        step = 2
    elif an is None or an.get("stale") or not seeds.seeds:
        step = 3
    else:
        step = 4
    rounds = (an or {}).get("rounds", [])
    return {"name": name, "step": step, "method": row, "has_video": has_video, "resolution": list(p.resolution),
            "boxes": len(seeds.seeds), "model_boxes": sum(1 for s in seeds.seeds if s.by_model), "refs": len(seeds.refs),
            "analysis": None if an is None else {"stale": an.get("stale"), "analyzed_at": an.get("analyzed_at"), "rounds": rounds, "fps": an.get("fps"),
                                                  "steps": an.get("steps", [])}}


ADOPT_KEYS = ("steps", "cycle_end", "cycle_timeout_sec", "cycle_min_sec", "state_anchor", "state_rel", "state_every_n_frames",
              "anchors", "zones", "work_area", "detect_every_n_frames", "skip_alert_sec", "cycle_arm_clear_sec")


def adopt_method(target: str, source: str, packaging: dict, copy_steps: bool = True, use_model: bool = True) -> dict:
    """把已經存在的專案（例如剛建的空專案）參照另一個包裝方式：一次設好型體地區、複製步驟清單與偵測設定、用來源的辨識模型。
    來源不必設過型體地區（舊專案也可以）。不複製影片與框選；桌面範圍只有畫面大小一樣才複製。回傳 {method, warnings}。"""
    from project_store import packaging_to_dict, project_from_dict
    if target == source:
        raise ValueError("不能參照自己")
    tgt = load_project(target); src = load_project(source)
    warnings: list[str] = []
    with open(os.path.join(tgt.dir_path, "config.json"), "r", encoding="utf-8-sig") as f:
        tcfg = json.load(f)
    with open(os.path.join(src.dir_path, "config.json"), "r", encoding="utf-8-sig") as f:
        scfg = json.load(f)
    same_res = list(tgt.resolution) == list(src.resolution)
    if copy_steps:
        if not src.steps:
            raise ValueError(f"「{source}」還沒有步驟可以複製")
        for k in ADOPT_KEYS:
            if k in scfg:
                tcfg[k] = scfg[k]
        if same_res and scfg.get("state_fixed"):
            tcfg["state_fixed"] = scfg["state_fixed"]
        elif scfg.get("state_fixed"):
            tcfg["state_fixed"] = None
            warnings.append(f"畫面大小不同（這支 {tgt.resolution[0]}×{tgt.resolution[1]}、來源 {src.resolution[0]}×{src.resolution[1]}），"
                            "桌面範圍沒有複製，請到「標記物品」框一次桌面範圍")
            if not tcfg.get("state_anchor"):
                kept = [s for s in tcfg.get("steps", []) if s.get("type") not in ("item", "box_state")]
                if len(kept) != len(tcfg.get("steps", [])):
                    for i, s in enumerate(kept):
                        s["step_index"] = i
                    tcfg["steps"] = kept
                    warnings.append("物品步驟要有桌面範圍才能用，先拿掉了；框好桌面範圍後再參照一次就會帶回來")
        # 框選設定（物品名單、盒子的樣子、桌面範圍、手部步驟）跟著過來；框選本身不帶（那是別支影片的格）
        sd_src = items.ItemSeeds(src.dir_path); sd = items.ItemSeeds(tgt.dir_path)
        sd.order = list(dict.fromkeys(list(sd.order) + list(sd_src.order)))
        sd.box_labels = list(dict.fromkeys(list(sd.box_labels) + list(sd_src.box_labels)))
        if same_res and sd_src.region and not sd.region:
            sd.region = list(sd_src.region)
        have = {h["name"] for h in sd.hand_steps}
        sd.hand_steps = list(sd.hand_steps) + [h for h in sd_src.hand_steps if h["name"] not in have]
        sd.save()
    model_src = None
    if use_model:
        if os.path.isfile(items.own_model_path(src)):
            model_src = source
        elif src.packaging is not None and src.packaging.model_source:
            model_src = src.packaging.model_source
        else:
            warnings.append(f"「{source}」還沒有訓練好的模型，這個專案暫時沒有模型可用")
    cur = tgt.packaging
    merged = {"style": packaging.get("style", cur.style if cur else ""), "region": packaging.get("region", cur.region if cur else ""),
              "style_name": packaging.get("style_name", cur.style_name if cur else ""),
              "customer": packaging.get("customer") or (cur.customer if cur else "") or (src.packaging.customer if src.packaging else ""),
              "model_source": model_src if use_model else (cur.model_source if cur else None), "enabled": True,
              "colors": [c.__dict__ for c in cur.colors] if cur else []}
    try:
        pk = parse_packaging(merged, tgt.project_name)
    except ProjectConfigError as e:
        raise ValueError(str(e))
    other = find_method(pk.style, pk.region, exclude=tgt.project_name)
    if other:
        raise ValueError(f"型體 {pk.style}／{pk.region} 已經有包裝方式了（{other}）")
    tcfg["packaging"] = packaging_to_dict(pk)
    try:
        project_from_dict(tcfg, tgt.dir_path)                    # 先驗證，失敗就不寫
    except ProjectConfigError as e:
        raise ValueError(f"參照後的設定不合法：{e}")
    tmp = os.path.join(tgt.dir_path, "config.json.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(tcfg, f, ensure_ascii=False, indent=2)
    os.replace(tmp, os.path.join(tgt.dir_path, "config.json"))
    return {"method": method_row(load_project(target)), "warnings": warnings}


def method_detail(project_name: str, lines_by_project: dict | None = None) -> dict:
    p = load_project(project_name)
    row = method_row(p, lines_by_project)
    row["step_rows"] = [{"index": s.step_index, "name": s.step_name, "type": s.type, "label": s.label or s.object or "",
                         "dwell": s.dwell_time_sec, "required": s.required} for s in p.steps]
    row["model_items"] = model_items(p)
    row["cycle_end"] = p.cycle_end.type if p.cycle_end else None
    row["state_fixed"] = p.state_fixed
    row["resolution"] = list(p.resolution)
    return row
