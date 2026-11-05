"""標記頁的後端（不依賴 Qt）：專案資訊、影格 JPEG、種子檔讀寫、建立訓練資料＋訓練（背景）、產生步驟、
新增專案（錄製示範影片或上傳影片檔）。給 web_server.py 用；資料格式與桌面程式完全相同，兩邊可交替使用同一個專案。
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import threading
import time

import cv2

import item_recognizer as items
import training
from monitor_service import HAND_MODEL, YOLO_WEIGHTS, load_camera_source
from project_store import (ProjectConfigError, app_base_dir, load_project, project_to_dict, projects_dir,
                           validate_project_name)
from video_recorder import CameraSource, FrameReader, Recorder, import_demo_video

PREVIEW_W = 640
JPEG_CACHE_MAX = 600        # 預覽縮圖約 10～40 KB 一張，600 張約十幾 MB


def ls_name(name: str, kind: str, index: int):
    """label_segments.NameDef，顏色照順序從調色盤取。"""
    import label_segments as ls
    return ls.NameDef(name, kind, ls.PALETTE[index % len(ls.PALETTE)])


def create_project(name: str, width: int = 1280, height: int = 720, fps: float = 30.0) -> str:
    """schema 2 空專案（與 main_ui.create_project_with_defaults 相同）；解析度在匯入影片／錄製後會被覆蓋。回傳資料夾。"""
    validate_project_name(name)
    d = os.path.join(projects_dir(), name)
    if os.path.exists(d):
        raise ProjectConfigError(f"專案「{name}」已存在")
    cfg = {"schema_version": 2, "project_name": name, "video_file": "demo.avi", "resolution": [int(width), int(height)],
           "fps": round(float(fps), 2), "skip_alert_sec": 1.0, "cycle_arm_clear_sec": 0.5, "reset_zone": None,
           "reset_dwell_sec": 1.0, "work_area": None, "detect_every_n_frames": 15, "gesture_model": None,
           "gesture_anchors": [], "cycle_end": {"type": "hands_absent", "hold_sec": 3.0}, "cycle_timeout_sec": 120.0,
           "cycle_min_sec": 5.0, "anchors": [], "zones": [], "steps": []}
    os.makedirs(os.path.join(d, "gestures"), exist_ok=True); os.makedirs(os.path.join(d, "error_logs"), exist_ok=True)
    with open(os.path.join(d, "config.json"), "w", encoding="utf-8") as f:
        json.dump(cfg, f, ensure_ascii=False, indent=2)
    return d


def _save_config(project) -> None:
    with open(os.path.join(project.dir_path, "config.json"), "w", encoding="utf-8") as f:
        json.dump(project_to_dict(project), f, ensure_ascii=False, indent=2)


def _jpeg(img, quality: int = 85) -> bytes:
    ok, buf = cv2.imencode(".jpg", img, [cv2.IMWRITE_JPEG_QUALITY, quality])
    return buf.tobytes() if ok else b""


class TrainJob:
    """第 2 步：找盒子與手（trace）→ 延伸資料集 → 子程序 tools/train_items.py。一次一個。"""

    def __init__(self):
        self._lock = threading.Lock(); self._thread = None; self._proc = None
        self.project_name = None; self.stage = ""; self.done_n = 0; self.total_n = 0
        self.lines: list[str] = []; self.error = None; self.finished = False; self.stats = None; self.started_at = 0.0

    @property
    def running(self) -> bool:
        return self._thread is not None and self._thread.is_alive()

    def state(self) -> dict:
        with self._lock:
            return {"running": self.running, "project": self.project_name, "stage": self.stage, "done": self.done_n, "total": self.total_n,
                    "lines": self.lines[-8:], "error": self.error, "finished": self.finished, "stats": self.stats,
                    "validation": getattr(self, "validation", None), "installed": getattr(self, "installed", None),
                    "package": getattr(self, "package", None),
                    "compare": getattr(self, "compare", None),        # 新舊模型考同一份考卷的結果（model_exam.compare）
                    "candidate": getattr(self, "candidate", False),   # 新模型沒換上、還留著 candidate.pt（可以「仍要換上」）
                    "elapsed": round(time.perf_counter() - self.started_at) if self.started_at and self.running else None}

    # ---- 挑素材訓練（可以跨型體地區、留片段驗證）

    def start_material(self, target: str, selection: list[dict], epochs: int = 30, recolor_classes: list[str] | None = None,
                       where: str = "local") -> dict:
        """selection：[{project, start, end}]（片段的起訖格）。recolor_classes：要合成配色的物品（空＝不做）。
        where：local＝在這台訓練；gpu＝只做好資料集、打包成 GPU 訓練包（訓練完再匯入 best.pt 驗證）。回傳這次的計畫。"""
        import training_material as tm
        if self.running:
            raise ValueError("已經在訓練中，請等它跑完")
        if not selection:
            raise ValueError("請至少勾一段訓練素材")
        if where not in ("local", "gpu"):
            raise ValueError("where 只能是 local 或 gpu")
        if not os.path.isfile(YOLO_WEIGHTS):
            raise ValueError(f"找不到 {YOLO_WEIGHTS}，無法找盒子")
        tgt = load_project(target)
        colors = {}
        plan = []
        for s in selection:
            name = str(s.get("project", ""))
            if name not in colors:
                colors[name] = tm.video_color(load_project(name))
            plan.append({"project": name, "start": int(s["start"]), "end": int(s["end"]), "color": colors[name]})
        hold = tm.pick_holdout(plan)
        train = [s for s in plan if s not in hold]
        self._reset_state(target)
        self._thread = threading.Thread(target=self._run_material, args=(tgt.project_name, train, hold, epochs, list(recolor_classes or []), where),
                                        daemon=True)
        self._thread.start()
        return {"train": train, "holdout": hold, "where": where, "recolor_classes": list(recolor_classes or [])}

    def _reset_state(self, target: str) -> None:
        with self._lock:
            self.project_name = target; self.stage = "準備中"; self.done_n = self.total_n = 0; self.validation = None; self.installed = None
            self.lines = []; self.error = None; self.finished = False; self.stats = None; self.started_at = time.perf_counter(); self.package = None
            self.compare = None; self.candidate = False; self._held_out = []

    def _run_material(self, target: str, train: list[dict], hold: list[dict], epochs: int, recolor_classes: list[str], where: str) -> None:
        import json as _json
        import model_exam as me
        import training_material as tm
        try:
            tgt = load_project(target)
            training.sync_item_region(tgt); tgt = load_project(target)
            exam = me.ensure(tgt, items.ItemSeeds(tgt.dir_path))          # 考卷先訂好：考卷的畫面不拿去訓練
            with self._lock:
                self._held_out = list((exam or {}).get("items", {}))
            names: list[str] = list(items.ItemSeeds(tgt.dir_path).order)
            parts = []
            by_proj: dict[str, list] = {}
            for s in train:
                by_proj.setdefault(s["project"], []).append((s["start"], s["end"]))
            hold_by: dict[str, list] = {}
            for s in hold:
                hold_by.setdefault(s["project"], []).append((s["start"], s["end"]))
            for k, (name, ranges) in enumerate(by_proj.items()):
                sp = load_project(name)
                training.sync_item_region(sp); training.ensure_state_anchor(sp); sp = load_project(name)
                seeds = tm.filtered_seeds(items.ItemSeeds(sp.dir_path), ranges, hold_by.get(name, []))
                if name == target and exam:
                    seeds = me.training_seeds(seeds, exam, me._margin(sp))
                if not seeds.seeds:
                    continue
                tag = f"（{k + 1}/{len(by_proj)} {name}）"
                trace = items.build_trace(sp, HAND_MODEL, YOLO_WEIGHTS, progress=lambda a, b, t=tag: self._set(f"找盒子與手{t}：{a}/{b} 格", a, b))
                items.build_dataset(sp, trace, seeds, progress=lambda a, b, t=tag: self._set(f"延伸框選{t}：{a}/{b}", a, b))
                parts.append((items.dataset_dir(sp), list(seeds.order)))
                for n in seeds.order:
                    if n not in names:
                        names.append(n)
            if not parts:
                raise ValueError("勾選的片段裡沒有任何框")
            mix = items.dataset_dir(tgt) + "_mix"
            stats = tm.merge_datasets(parts, mix, names)
            if stats["train"] == 0:
                raise ValueError("延伸不出任何訓練圖")
            rc = {"added": 0, "per_mode": {}}
            if recolor_classes:
                self._set("合成配色中…")
                rc = tm.recolor_augment(mix, names, recolor_classes)
            with self._lock:
                self.stats = {**stats, "train": stats["train"] + rc["added"], "recolor": rc, "recolor_classes": recolor_classes,
                              "train_segments": len(train), "holdout_segments": len(hold)}
            model_dir = os.path.join(tgt.dir_path, items.MODEL_DIR)
            os.makedirs(model_dir, exist_ok=True)
            tmp_model = os.path.join(model_dir, "candidate.pt")
            if os.path.isfile(tmp_model):
                os.remove(tmp_model)
            imgsz = items.FIXED_IMGSZ if items.is_fixed(tgt) else 640
            plan = {"target": target, "names": names, "holdout": hold, "train": train, "epochs": epochs, "imgsz": imgsz,
                    "recolor_classes": recolor_classes, "recolor_added": rc["added"], "train_images": stats["train"] + rc["added"],
                    "val_images": stats["val"], "created_at": time.strftime("%Y/%m/%d %H:%M"), "held_out": self._held_out}
            with open(os.path.join(model_dir, "candidate_plan.json"), "w", encoding="utf-8") as f:
                _json.dump(plan, f, ensure_ascii=False, indent=2)
            if where == "gpu":
                self._set("打包 GPU 訓練包中…")
                out_dir = os.path.join(app_base_dir(), "cache", "gpu_pkg")
                os.makedirs(out_dir, exist_ok=True)
                import hashlib
                safe = "".join(c for c in target if c.isascii() and (c.isalnum() or c in "-_"))   # 中文專案名換成短碼，Linux 好打
                safe = (safe + "_" if safe else "p") + hashlib.md5(target.encode("utf-8")).hexdigest()[:6]
                out = os.path.join(out_dir, f"sopg_train_{safe}_{time.strftime('%Y%m%d_%H%M')}.zip")
                tm.write_gpu_package(mix, out, os.path.join(app_base_dir(), "models", "yolov8n.pt"),
                                     os.path.join(app_base_dir(), "tools", "train_items.py"), plan, epochs, imgsz)
                with self._lock:
                    self.package = out; self.finished = True
                    self.stage = f"GPU 訓練包已產生（{os.path.getsize(out) / 1048576:.0f} MB）：{out}"
                return
            self._set("訓練模型中（約 20～60 分鐘）…")
            cmd = items.train_command(tgt, epochs=epochs, data_yaml=os.path.join(mix, "data.yaml"), copy_to=tmp_model)
            env = dict(os.environ, PYTHONUTF8="1", PYTHONIOENCODING="utf-8")
            self._proc = subprocess.Popen(cmd, cwd=app_base_dir(), stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True,
                                          encoding="utf-8", errors="replace", env=env)
            for line in self._proc.stdout:
                line = line.strip()
                if line and ("epoch" in line or "訓練" in line or "device" in line or "Error" in line or "錯誤" in line):
                    with self._lock:
                        self.lines.append(line)
                    if line.startswith("epoch"):
                        self._set(line)
            code = self._proc.wait()
            if code != 0 or not os.path.isfile(tmp_model):
                raise RuntimeError(f"訓練失敗（結束碼 {code}）：" + " / ".join(self.lines[-3:]))
            self._validate_install(target, tmp_model, hold)
        except Exception as e:
            with self._lock:
                self.error = f"{type(e).__name__}: {e}" if not isinstance(e, (ValueError, RuntimeError)) else str(e)
                self.stage = "失敗"
        finally:
            self._proc = None

    def start_import(self, target: str, data: bytes) -> dict:
        """匯入 GPU 訓練好的 best.pt：存成 candidate.pt，照當初打包時記下的保留段離線驗證，通過才換上。"""
        import json as _json
        if self.running:
            raise ValueError("正在訓練或驗證中，請等它跑完")
        tgt = load_project(target)
        model_dir = os.path.join(tgt.dir_path, items.MODEL_DIR)
        plan_path = os.path.join(model_dir, "candidate_plan.json")
        if not os.path.isfile(plan_path):
            raise ValueError("找不到這個包裝方式的 GPU 訓練計畫（candidate_plan.json），請先在這台產生 GPU 訓練包")
        if len(data) < 100_000 or not data[:2] == b"PK":
            raise ValueError("這不像 YOLO 的 best.pt（檔案太小或格式不對）")
        with open(plan_path, "r", encoding="utf-8") as f:
            plan = _json.load(f)
        tmp_model = os.path.join(model_dir, "candidate.pt")
        with open(tmp_model, "wb") as f:
            f.write(data)
        self._reset_state(target)
        with self._lock:
            self.stats = {"train": plan.get("train_images"), "val": plan.get("val_images"), "recolor": {"added": plan.get("recolor_added", 0)},
                          "recolor_classes": plan.get("recolor_classes"), "holdout_segments": len(plan.get("holdout") or []), "imported": True}
            self._held_out = list(plan.get("held_out") or [])
        self._thread = threading.Thread(target=self._run_import, args=(target, tmp_model, plan.get("holdout") or []), daemon=True)
        self._thread.start()
        return {"holdout": plan.get("holdout") or []}

    def _run_import(self, target: str, tmp_model: str, hold: list[dict]) -> None:
        try:
            self._validate_install(target, tmp_model, hold)
        except Exception as e:
            with self._lock:
                self.error = f"{type(e).__name__}: {e}" if not isinstance(e, (ValueError, RuntimeError)) else str(e)
                self.stage = "失敗"

    def _validate_install(self, target: str, tmp_model: str, hold: list[dict]) -> None:
        """離線驗證每個配色保留的那一段，再跟上次的模型考同一份考卷（model_exam）；保留段都通過、而且沒有比上次差，
        才換上新模型（舊的備份成 best_prev_<時間>.pt）。比較差就不換，新模型留成 candidate.pt，使用者可以「仍要換上」。"""
        import packing_methods as pkg
        import training_material as tm
        hold_by: dict[str, list] = {}
        for s in hold:
            hold_by.setdefault(s["project"], []).append((s["start"], s["end"]))
        results = []
        for name, ranges in hold_by.items():
            sp = load_project(name)
            segs = [dict(s, color=next(h["color"] for h in hold if h["project"] == name and h["start"] == s["start"]))
                    for s in tm.segments(sp) if (s["start"], s["end"]) in [tuple(r) for r in ranges]]
            self._set(f"離線驗證（{name}）…")
            for r in tm.validate_holdout(sp, tmp_model, segs):
                results.append({"project": name, **r})
        passed = all(r["ok"] is not False for r in results)
        with self._lock:
            self.validation = results
        tgt = load_project(target)
        cmp = self._compare(tgt, tmp_model) if passed else None
        worse = bool(cmp and cmp["verdict"] == "worse")
        install = passed and not worse
        if install:
            self._install(target, tmp_model, cmp, forced=False)
        if tgt.packaging is not None:
            for r in results:
                if r["ok"] is None or not r["color"]:
                    continue
                note = "" if r["ok"] else "驗證漏看：" + "、".join(r["missing"])
                pkg.set_color(target, r["color"], "verified" if r["ok"] else "failed", note)
        if cmp is not None:
            import model_exam as me
            cmp["history"] = me.add_history(tgt, {"at": cmp["at"], "verdict": cmp["verdict"], "installed": install, "forced": False})[:5]
        with self._lock:
            self.installed = install
            self.candidate = not install and os.path.isfile(tmp_model)
            self.compare = cmp
            self.finished = True
            if not passed:
                self.stage = "驗證沒過，保留舊模型（新模型存成 candidate.pt）"
            elif worse:
                self.stage = "新模型比上次差，還在用上次的模型（新模型存成 candidate.pt）"
            else:
                self.stage = {"better": "考完，比上次好，已換上新模型", "same": "考完，跟上次差不多，已換上新模型",
                              "first": "訓練完成，已換上模型（第一次，沒有上次可比）"}.get(
                    (cmp or {}).get("verdict"), "訓練完成，已換上新模型" + (f"（{cmp['reason']}）" if cmp and cmp.get("reason") else ""))

    def _compare(self, tgt, tmp_model: str) -> dict | None:
        """新舊模型考同一份考卷（model_exam）。盒內模式、出不了考題、考試出錯都不擋換上，只在結果裡說明。"""
        import model_exam as me
        at = time.strftime("%Y/%m/%d %H:%M")
        base = {"at": at, "rows": [], "verdict": "skip"}
        if not items.is_fixed(tgt):
            return {**base, "reason": "盒內模式不比較"}
        try:
            exam = me.load(tgt) or me.ensure(tgt, items.ItemSeeds(tgt.dir_path))
            if not me.question_count(exam):
                return {**base, "verdict": "noexam", "reason": "每個物品的框都只有一段，出不了考題，沒有比較"}
            own = items.own_model_path(tgt); prev_path = items.model_path(tgt); prev = None; prev_at = None
            if os.path.isfile(prev_path):
                self._set("考試中：上次的模型…")
                prev = me.score(tgt, prev_path, exam)
                prev_at = time.strftime("%Y/%m/%d %H:%M", time.localtime(os.path.getmtime(prev_path)))
            self._set("考試中：這次的模型…")
            new = me.score(tgt, tmp_model, exam)
            # 上次的模型是這個專案自己訓練的、而且訓練時沒扣掉某些考題 → 它看過那些考題，比較會偏向上次
            saw = [n for n in exam["items"] if n not in me.held_out_items(tgt)] if prev is not None and prev_path == own else []
            cmp = me.compare(prev, new, saw)
            new_items = [n for n, e in exam["items"].items() if e.get("added_at") and e.get("added_at") != exam.get("created_at")]
            return {**cmp, "at": at, "prev_trained_at": prev_at, "exam_created_at": exam.get("created_at"),
                    "questions": me.question_count(exam), "empty_n": len(exam.get("empty", [])), "new_exam_items": new_items,
                    "video": me._video_key(tgt), "held_out": list(self._held_out)}
        except Exception as e:                       # 考試失敗不擋：照舊換上，畫面說明
            return {**base, "reason": f"考試失敗（{type(e).__name__}: {e}），沒有比較"}

    def _install(self, target: str, tmp_model: str, cmp: dict | None, forced: bool) -> None:
        """換上新模型：舊的備份成 best_prev_<時間>.pt、改用自己的模型、記下桌面範圍與考卷成績。"""
        import shutil
        from datetime import datetime
        tgt = load_project(target)
        own = items.own_model_path(tgt)
        os.makedirs(os.path.dirname(own), exist_ok=True)
        if os.path.isfile(own):
            shutil.copyfile(own, os.path.join(os.path.dirname(own), f"best_prev_{datetime.now():%Y%m%d_%H%M}.pt"))
        os.replace(tmp_model, own)
        if tgt.packaging is not None and tgt.packaging.model_source:
            tgt.packaging.model_source = None
            _save_config(tgt)
        training.sync_item_region(tgt)
        extra = None
        if cmp and cmp.get("rows"):
            extra = {"exam": {"video": cmp.get("video"), "held_out": cmp.get("held_out", []), "exam_created_at": cmp.get("exam_created_at"),
                              "verdict": cmp["verdict"], "forced": forced, "at": cmp["at"],
                              "scores": [{k: r[k] for k in ("name", "n", "hit", "fp", "empty_n")} for r in cmp["rows"]]}}
        elif self._held_out:
            extra = {"exam": {"video": (cmp or {}).get("video"), "held_out": list(self._held_out)}}
        items.save_model_info(load_project(target), extra)     # 記下換上時的桌面範圍（＋考卷成績）

    def install_candidate(self, project_name: str) -> dict:
        """「仍要換上新模型」：比較差、沒換上的 candidate.pt 照使用者的選擇換上。"""
        import model_exam as me
        if self.running:
            raise ValueError("正在訓練中，請等它跑完")
        p = load_project(project_name)
        tmp_model = os.path.join(p.dir_path, items.MODEL_DIR, "candidate.pt")
        if not os.path.isfile(tmp_model):
            raise ValueError("沒有等著換上的新模型（candidate.pt）")
        cmp = self.compare if self.project_name == project_name else None
        self._install(project_name, tmp_model, cmp, forced=True)
        if cmp:
            me.set_history_installed(p, cmp["at"], True)
            cmp["history"] = me.history(p)[:5]
        with self._lock:
            self.installed = True; self.candidate = False
            if cmp:
                cmp["forced"] = True
            self.stage = "已照你的選擇換上新模型（比上次差）"
        return self.state()

    def _set(self, stage: str, a: int = 0, b: int = 0) -> None:
        with self._lock:
            self.stage, self.done_n, self.total_n = stage, a, b

    def start(self, project_name: str) -> None:
        if self.running:
            raise ValueError("已經在訓練中，請等它跑完")
        project = load_project(project_name)
        seeds = items.ItemSeeds(project.dir_path)
        if not seeds.seeds:
            raise ValueError("還沒有框選任何物品")
        if not os.path.isfile(YOLO_WEIGHTS):
            raise ValueError(f"找不到 {YOLO_WEIGHTS}，無法找盒子")
        self._reset_state(project_name)
        self._thread = threading.Thread(target=self._run, args=(project_name,), daemon=True); self._thread.start()

    def _run(self, project_name: str) -> None:
        import model_exam as me
        try:
            project = load_project(project_name)
            training.sync_item_region(project); training.ensure_state_anchor(project)
            project = load_project(project_name)
            all_seeds = items.ItemSeeds(project.dir_path)
            exam = me.ensure(project, all_seeds)                 # 考卷先訂好：考卷的畫面不拿去訓練，新舊模型才比得公平
            with self._lock:
                self._held_out = list((exam or {}).get("items", {}))
            seeds = me.training_seeds(all_seeds, exam, me._margin(project)) if exam else all_seeds
            trace = items.build_trace(project, HAND_MODEL, YOLO_WEIGHTS,
                                      progress=lambda a, b: self._set(f"找盒子與手：{a}/{b} 格", a, b))
            stats = items.build_dataset(project, trace, seeds, progress=lambda a, b: self._set(f"延伸框選：{a}/{b}", a, b))
            with self._lock:
                self.stats = stats
            if stats["train"] == 0:
                raise ValueError("框選的物品延伸不出任何一格；請確認「空盒／空桌面」有標、框選那一格看得到東西")
            self._set("訓練模型中（約 20～60 分鐘）…")
            tmp_model = os.path.join(project.dir_path, items.MODEL_DIR, "candidate.pt")   # 先寫暫存檔，考完才決定換不換
            os.makedirs(os.path.dirname(tmp_model), exist_ok=True)
            if os.path.isfile(tmp_model):
                os.remove(tmp_model)
            cmd = items.train_command(project, copy_to=tmp_model)
            env = dict(os.environ, PYTHONUTF8="1", PYTHONIOENCODING="utf-8")
            self._proc = subprocess.Popen(cmd, cwd=app_base_dir(), stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True,
                                          encoding="utf-8", errors="replace", env=env)
            for line in self._proc.stdout:
                line = line.strip()
                if line and ("epoch" in line or "訓練" in line or "device" in line or "Error" in line or "錯誤" in line):
                    with self._lock:
                        self.lines.append(line)
                    if line.startswith("epoch"):
                        self._set(line)
            code = self._proc.wait()
            if code != 0 or not os.path.isfile(tmp_model):
                raise RuntimeError(f"訓練失敗（結束碼 {code}）：" + " / ".join(self.lines[-3:]))
            self._proc = None
            self._validate_install(project_name, tmp_model, [])   # 跟上次的模型比；沒變差才換上（換上時改用自己的模型、記桌面範圍）
        except Exception as e:
            with self._lock:
                self.error = f"{type(e).__name__}: {e}" if not isinstance(e, (ValueError, RuntimeError)) else str(e)
                self.stage = "失敗"
        finally:
            self._proc = None


class AnalysisJob:
    """背景跑離線步驟分析（step_analysis.analyze），一次一個；結果存在專案的 items/analysis.json。"""

    def __init__(self):
        self._lock = threading.Lock(); self._thread = None; self._stop = threading.Event()
        self.project_name = None; self.done_n = 0; self.total_n = 0; self.error = None; self.finished = False; self.started_at = 0.0
        self.queue: list[str] = []

    @property
    def running(self) -> bool:
        return self._thread is not None and self._thread.is_alive()

    def state(self) -> dict:
        with self._lock:
            return {"running": self.running, "project": self.project_name, "done": self.done_n, "total": self.total_n, "error": self.error,
                    "finished": self.finished, "queue": list(self.queue),
                    "elapsed": round(time.perf_counter() - self.started_at) if self.started_at and self.running else None}

    def start(self, project_name: str) -> dict:
        """正在跑別的專案就排隊；同一個專案重複按不會重複排。"""
        load_project(project_name)
        with self._lock:
            if self.running:
                if project_name != self.project_name and project_name not in self.queue:
                    self.queue.append(project_name)
                return {"queued": project_name != self.project_name}
        self._begin(project_name)
        return {"queued": False}

    def _begin(self, project_name: str) -> None:
        with self._lock:
            self.project_name = project_name; self.done_n = self.total_n = 0; self.error = None; self.finished = False
            self.started_at = time.perf_counter()
        self._stop.clear()
        self._thread = threading.Thread(target=self._run, args=(project_name,), daemon=True); self._thread.start()

    def cancel(self) -> None:
        with self._lock:
            self.queue = []
        self._stop.set()

    def _run(self, project_name: str) -> None:
        import step_analysis
        try:
            p = load_project(project_name)
            step_analysis.analyze(p, HAND_MODEL, YOLO_WEIGHTS, progress=self._progress, should_stop=self._stop.is_set)
            with self._lock:
                self.finished = True
        except Exception as e:
            with self._lock:
                self.error = str(e) if isinstance(e, (ValueError, RuntimeError)) else f"{type(e).__name__}: {e}"
        nxt = None
        with self._lock:
            if self.queue and not self._stop.is_set():
                nxt = self.queue.pop(0)
        if nxt:
            threading.Thread(target=self._begin, args=(nxt,), daemon=True).start()

    def _progress(self, a: int, b: int) -> None:
        with self._lock:
            self.done_n, self.total_n = a, b


class AutoLabelJob(AnalysisJob):
    """背景跑「自動標記」（auto_label.run：需要時先分析步驟，再用模型框好每一輪的每一步）。一次一個。"""

    def state(self) -> dict:
        d = super().state()
        with self._lock:
            d.update({"stage": getattr(self, "stage", ""), "result": getattr(self, "result", None)})
        return d

    def _begin(self, project_name: str) -> None:
        with self._lock:
            self.stage = "準備中"; self.result = None
        super()._begin(project_name)

    def _run(self, project_name: str) -> None:
        import auto_label
        try:
            p = load_project(project_name)
            res = auto_label.run(p, HAND_MODEL, YOLO_WEIGHTS, progress=self._stage_progress, should_stop=self._stop.is_set)
            with self._lock:
                self.result = res; self.finished = True; self.stage = "完成"
        except Exception as e:
            with self._lock:
                self.error = str(e) if isinstance(e, (ValueError, RuntimeError)) else f"{type(e).__name__}: {e}"
                self.stage = "失敗"

    def _stage_progress(self, stage: str, a: int, b: int) -> None:
        with self._lock:
            self.stage = stage; self.done_n, self.total_n = a, b


class RecordJob:
    """新增專案時錄示範影片：開相機、建專案（用相機的解析度／fps）、寫 demo.avi、給預覽 JPEG。"""

    def __init__(self):
        self._lock = threading.Lock(); self._cond = threading.Condition(self._lock); self._thread = None
        self._stop = threading.Event(); self._rec = Recorder(); self._jpeg = None; self._fid = 0
        self.project_name = None; self.error = None; self.info = ""; self.frames = 0; self.recording = False

    @property
    def running(self) -> bool:
        return self._thread is not None and self._thread.is_alive()

    def state(self) -> dict:
        with self._lock:
            return {"running": self.running, "recording": self.recording, "project": self.project_name, "error": self.error,
                    "info": self.info, "frames": self.frames, "frame_id": self._fid}

    def wait_frame(self, last_id: int, timeout: float = 1.0):
        with self._cond:
            if self._fid <= last_id:
                self._cond.wait(timeout)
            return self._fid, self._jpeg

    def start(self, project_name: str, source: str | None = None) -> None:
        if self.running:
            raise ValueError("相機已在使用中")
        src = (source or load_camera_source()).strip()
        with self._lock:
            self.project_name = project_name; self.error = None; self.info = "開啟相機中…"; self.frames = 0; self.recording = False
        self._stop.clear()
        self._thread = threading.Thread(target=self._run, args=(project_name, src), daemon=True); self._thread.start()

    def begin_recording(self) -> None:
        with self._lock:
            if not self.running or self.error:
                raise ValueError("相機還沒開好")
            if self._rec.recording:
                return
            self._rec.start(self._path, self._res, self._fps); self.recording = True; self.frames = 0

    def end_recording(self) -> int:
        with self._lock:
            n = self._rec.frame_count
            if self._rec.recording:
                self._rec.stop()
            self.recording = False
        return n

    def stop(self) -> None:
        self._stop.set()
        t = self._thread
        if t is not None:
            t.join(5.0)
        self._thread = None

    def _run(self, project_name: str, source: str) -> None:
        try:
            cam = CameraSource(source, 1280, 720, latest_only=False)
        except Exception as e:
            with self._lock:
                self.error = f"相機開不起來：{e}"
            return
        try:
            project = load_project(project_name)
            self._res, self._fps = cam.resolution, cam.fps or 30.0
            self._path = os.path.join(project.dir_path, "demo.avi")
            project.resolution = [int(self._res[0]), int(self._res[1])]; project.fps = round(float(self._fps), 2); project.video_file = "demo.avi"
            _save_config(project)
            with self._lock:
                self.info = f"相機 {self._res[0]}x{self._res[1]} @ {self._fps:.1f} fps，按「開始錄製」"
            n = 0
            while not self._stop.is_set():
                frame = cam.read()
                if frame is None:
                    with self._lock:
                        self.error = "相機斷線"
                    break
                with self._lock:
                    if self._rec.recording:
                        self._rec.write(frame); self.frames = self._rec.frame_count
                n += 1
                if n % 3 == 0:
                    small = cv2.resize(frame, (PREVIEW_W, int(PREVIEW_W * frame.shape[0] / frame.shape[1])))
                    with self._cond:
                        self._jpeg = _jpeg(small, 75); self._fid += 1; self._cond.notify_all()
        finally:
            with self._lock:
                if self._rec.recording:
                    self._rec.stop()
                self.recording = False
            cam.release()


class LabelService:
    def __init__(self):
        self._readers: dict[str, FrameReader] = {}
        self._detectors: dict[str, tuple[float, items.ItemDetector]] = {}
        from collections import OrderedDict
        self._jpegs: OrderedDict = OrderedDict()
        self._lock = threading.Lock()
        self.train = TrainJob(); self.record = RecordJob(); self.analysis = AnalysisJob(); self.autolabel = AutoLabelJob()

    def _detector(self, project) -> items.ItemDetector:
        mp = items.model_path(project)
        if not os.path.isfile(mp):
            raise ValueError("這個專案還沒有訓練好的模型，請先手動框幾個樣本並訓練一次")
        mtime = os.path.getmtime(mp)
        with self._lock:
            cached = self._detectors.get(mp)
            if cached is None or cached[0] != mtime:
                det = items.ItemDetector(mp)
                self._detectors[mp] = (mtime, det)
                return det
            return cached[1]

    # ---- 影格

    def _reader(self, project) -> FrameReader | None:
        if not os.path.isfile(project.video_path):
            return None
        key = project.video_path
        with self._lock:
            r = self._readers.get(key)
            if r is None:
                r = FrameReader(project.video_path); self._readers[key] = r
            return r

    def drop_reader(self, project_name: str) -> None:
        with self._lock:
            for k in [k for k in self._readers if os.sep + project_name + os.sep in k]:
                try:
                    self._readers.pop(k).release()
                except Exception:
                    pass

    def frame_jpeg(self, project_name: str, n: int, max_w: int | None = None, region: bool = False, box=None, zoom: bool = False) -> bytes | None:
        """影格 JPEG。region：裁到桌面範圍；box=[x,y,w,h]：畫框；zoom：以框為中心放大（框外留一倍，10:9）。
        做過的 JPEG 留在記憶體（最多 JPEG_CACHE_MAX 張）：預覽燈箱來回切換同一段不用重新解碼。"""
        p = load_project(project_name); r = self._reader(p)
        if r is None:
            return None
        key = (p.video_path, os.path.getmtime(p.video_path), n, max_w, region, tuple(box) if box else None, zoom)
        with self._lock:
            hit = self._jpegs.get(key)
            if hit is not None:
                self._jpegs.move_to_end(key)
                return hit
        out = self._render_frame(p, r, n, max_w, region, box, zoom)
        with self._lock:
            self._jpegs[key] = out
            while len(self._jpegs) > JPEG_CACHE_MAX:
                self._jpegs.popitem(last=False)
        return out

    def _render_frame(self, p, r, n, max_w, region, box, zoom) -> bytes:
        with self._lock:
            fr = r.get_frame(max(0, min(n, max(r.frame_count - 1, 0)))).copy()
        if box is not None:
            x, y, w, h = [int(v) for v in box]
            cv2.rectangle(fr, (x, y), (x + w, y + h), (255, 140, 0), max(3, fr.shape[1] // 270))
        if zoom and box is not None:
            x, y, w, h = [int(v) for v in box]
            sw = max(w, h * 10 / 9) * 2.0; sh = sw * 0.9; H, W = fr.shape[:2]
            x0 = int(max(0, min(W - sw, x + w / 2 - sw / 2))); y0 = int(max(0, min(H - sh, y + h / 2 - sh / 2)))
            fr = fr[y0:int(y0 + sh), x0:int(x0 + sw)]
        elif region:
            reg = p.state_fixed or items.ItemSeeds(p.dir_path).region
            if reg:
                fr = items._crop(fr, tuple(reg))
        if max_w and fr.shape[1] > max_w:
            fr = cv2.resize(fr, (max_w, int(max_w * fr.shape[0] / fr.shape[1])))
        return _jpeg(fr, 80)

    # ---- 專案資訊

    def project_info(self, project_name: str) -> dict:
        import label_segments as ls
        p = load_project(project_name); r = self._reader(p); seeds = items.ItemSeeds(p.dir_path)
        segs = ls.Segments(p.dir_path); self._sync_names(segs, seeds)
        return {"name": p.project_name, "resolution": list(p.resolution), "fps": p.fps, "has_video": r is not None,
                "frame_count": r.frame_count if r else 0, "has_model": os.path.isfile(items.model_path(p)),
                "steps": [s.step_name for s in p.steps], "item_steps": any(s.type in ("item", "hand_on_object") for s in p.steps),
                "seeds": self._seeds_dict(seeds, p), "segments": self._segments_dict(segs)}

    # ---- 時間軸（名稱／段落）：見 label_segments.py

    @staticmethod
    def _segments_dict(segs) -> dict:
        d = segs.to_dict(); d.update(segs.counts())
        return d

    @staticmethod
    def _sync_names(segs, seeds: items.ItemSeeds) -> None:
        """舊專案（只有 seeds.json）第一次打開時間軸：框過的物品、手部步驟自動變成名稱，不用重新輸入。"""
        changed = False
        for name in seeds.order:
            if segs.name(name) is None:
                segs.names.append(ls_name(name, "object", len(segs.names))); changed = True
        for h in seeds.hand_steps:
            if segs.name(h["name"]) is None:
                nd = ls_name(h["name"], "action", len(segs.names)); nd.touch = h.get("item") or h.get("prompt") or None
                segs.names.append(nd); changed = True
        if changed:
            segs.save()

    def segment_action(self, project_name: str, body: dict) -> dict:
        import label_segments as ls
        p = load_project(project_name); seeds = items.ItemSeeds(p.dir_path); segs = ls.Segments(p.dir_path)
        self._sync_names(segs, seeds)
        act = body.get("action"); r = self._reader(p); n_frames = r.frame_count if r else 0
        extra: dict = {}
        if act == "add_name":
            extra["name"] = segs.add_name(str(body.get("name", "")), str(body.get("kind", "object"))).name
        elif act == "remove_name":
            name = str(body.get("name", ""))
            segs.remove_name(name); seeds.remove_item(name); seeds.remove_hand_step(name)
        elif act == "add_segment":
            extra["segment"] = segs.add(str(body.get("name", "")), int(body.get("start", 0)), int(body.get("end", 0)), n_frames).id
        elif act == "update_range":
            s, changed = segs.update_range(int(body.get("id", 0)), int(body.get("start", 0)), int(body.get("end", 0)), n_frames)
            if changed and s.group:
                # 已存檔的物品段改了範圍：範圍外追出來的框先丟掉（不然訓練還是會用到）；拉長的部分要重新存檔才會補追
                seeds.seeds = [x for x in seeds.seeds if not (x.group == s.group and not (s.start <= x.frame <= s.end))]; seeds.save()
            extra["changed"] = changed
        elif act == "set_box":
            rect = body.get("rect")
            segs.set_box(int(body.get("id", 0)), body.get("frame"), None if rect is None else [int(v) for v in rect])
        elif act == "save_segment":
            extra.update(self._save_segment(p, seeds, segs, int(body.get("id", 0))))
        elif act == "remove_segment":
            s = segs.get(int(body.get("id", 0)))
            rows = [dict(x.__dict__) for x in seeds.seeds if s.group and x.group == s.group]
            if rows:
                seeds.seeds = [x for x in seeds.seeds if x.group != s.group]; seeds.save()
            segs.remove(s.id, rows)
            nd = segs.name(s.name)
            if nd is not None and nd.kind == "action" and not any(x.saved for x in segs.by_name(s.name)):
                seeds.remove_hand_step(s.name); nd.touch = None; segs.save()
        elif act == "restore_segment":
            s, rows = segs.restore(n_frames)
            if rows:
                seeds.seeds.extend(items.Seed(str(x["name"]), int(x["frame"]), [int(v) for v in x["rect"]], bool(x.get("auto")), int(x.get("group", 0) or 0),
                                              bool(x.get("by_model"))) for x in rows)
                if s.name not in seeds.order:
                    seeds.order.append(s.name)
                seeds.save()
            nd = segs.name(s.name)
            if nd is not None and nd.kind == "action" and s.saved and s.touch:
                seeds.add_hand_step(s.name, item=s.touch, dwell=ls.ACTION_DWELL_SEC); nd.touch = s.touch; segs.save()
            extra["segment"] = s.id
        elif act == "set_box_label":
            seeds.set_box_label(str(body.get("name", "")), bool(body.get("is_box", True)))
        elif act == "set_region":
            self._set_region(p, seeds, body.get("rect"))
        else:
            raise ValueError(f"不認得的動作：{act}")
        seeds.sync_auto_region(p.resolution)        # 框有增減就重算自動範圍（手動模式不動）
        return {"segments": self._segments_dict(segs), "seeds": self._seeds_dict(seeds, p), **extra}

    @staticmethod
    def _set_region(p, seeds: items.ItemSeeds, rect) -> None:
        """網頁的「桌面範圍」：給框＝使用者自己框（之後不自動蓋掉）；None＝改回程式自動算。"""
        if rect is None:
            seeds.set_region_auto(p.resolution); return
        if not (isinstance(rect, list) and len(rect) == 4):
            raise ValueError("桌面範圍要是 [x, y, w, h]")
        seeds.set_region(tuple(int(v) for v in rect))

    def _save_segment(self, p, seeds: items.ItemSeeds, segs, sid: int) -> dict:
        """物品：把框沿整段追出來寫進 seeds（同一組）；動作：看手碰到哪個已框物品，寫成 hand_steps（item）。"""
        import label_segments as ls
        s = segs.get(sid); nd = segs.name(s.name)
        if nd is None:
            raise ValueError(f"名稱「{s.name}」不存在，請重新整理")
        if nd.kind == "action":
            frames = [f for f in range(s.start, s.end + 1) if f % items.TRACE_STEP == 0] or [s.start]
            boxes = self._object_boxes(segs, seeds, frames)
            cands = sorted({name for d in boxes.values() for name in d})
            hands = self._hands_for_frames(p, frames) if cands else {f: [] for f in frames}
            touch, stats = ls.infer_touch(hands, boxes)
            if not touch:
                raise ValueError(ls.touch_reason(stats, cands))
            segs.mark_saved(sid, touch=touch); nd.touch = touch; segs.save()
            seeds.add_hand_step(s.name, item=touch, dwell=ls.ACTION_DWELL_SEC)
            return {"touch": touch, "stats": stats}
        if not s.box or s.box_frame is None:
            raise ValueError(f"這一段還沒畫框。把時間移到這一段裡面，在畫面上拖拉框住「{s.name}」")
        if seeds.region is None and seeds.region_mode != "manual":
            seeds.region_mode = "auto"      # 網頁標記頁預設：桌面範圍從全部框自動算（segment_action 結尾 sync_auto_region 會算）
        if s.group:
            seeds.seeds = [x for x in seeds.seeds if x.group != s.group]
        auto = ls.track_segment(p.video_path, s.start, s.end, s.box_frame, s.box, step=items.TRACK_STEP)
        g = seeds.add_seed(s.name, s.box_frame, tuple(s.box), auto)
        segs.mark_saved(sid, group=g, tracked=1 + len(auto))
        return {"tracked": 1 + len(auto), "expected": (s.end - s.start) // items.TRACK_STEP + 1}

    @staticmethod
    def _object_boxes(segs, seeds: items.ItemSeeds, frames: list[int]) -> dict[int, dict[str, list]]:
        """取樣格 → {物品名: [框...]}：已框物品（含舊版框選）在那一格附近（±TRACK_STEP）的位置。"""
        objects = {nd.name for nd in segs.names if nd.kind == "object"}
        by_name: dict[str, list] = {}
        for x in seeds.seeds:
            if x.name in objects:
                by_name.setdefault(x.name, []).append(x)
        out: dict[int, dict[str, list]] = {}
        for f in frames:
            row: dict[str, list] = {}
            for name, rows in by_name.items():
                best = min((abs(x.frame - f) for x in rows), default=None)
                if best is not None and best <= items.TRACK_STEP:
                    row[name] = [tuple(x.rect) for x in rows if abs(x.frame - f) == best]
            if row:
                out[f] = row
        return out

    def _hands_for_frames(self, p, frames: list[int]) -> dict[int, list]:
        """取樣格的手部判定點（每手 4 點）。訓練時留下的 trace.json 指紋相同就直接用；不然只對這些格跑 MediaPipe。"""
        path = os.path.join(p.dir_path, items.TRACE_FILE)
        if os.path.isfile(path):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    d = json.load(f)
                if d.get("fingerprint") == items.trace_fingerprint(p.video_path):
                    rows = {r["f"]: r["hands"] for r in d["rows"] if "hands" in r}
                    if all(f in rows for f in frames):
                        return {f: [tuple(pt) for pt in rows[f]] for f in frames}
            except Exception:
                pass
        if not os.path.isfile(HAND_MODEL):
            raise ValueError(f"找不到手部模型 {HAND_MODEL}，無法判斷這個動作碰到什麼")
        from core_detector import HandTracker
        r = self._reader(p)
        if r is None:
            raise ValueError("找不到示範影片")
        tracker = HandTracker(HAND_MODEL); out: dict[int, list] = {}
        try:
            for f in frames:
                with self._lock:
                    fr = r.get_frame(f)
                out[f] = list(tracker.detect(fr, int(f / float(p.fps or 30.0) * 1000)))
        finally:
            tracker.close()
        return out

    @staticmethod
    def _seeds_dict(seeds: items.ItemSeeds, p=None) -> dict:
        return {"order": list(seeds.order), "refs": list(seeds.refs), "closed": list(seeds.closed), "region": seeds.region,
                "region_mode": seeds.region_mode,
                "model_stale": items.model_stale_reason(p, seeds) if p is not None else None,   # 訓練後桌面範圍改了 → 要重訓
                "box_labels": list(seeds.box_labels), "hand_steps": list(seeds.hand_steps), "counts": seeds.counts(),
                "auto_counts": seeds.auto_counts(),
                "seeds": [{"name": s.name, "frame": s.frame, "rect": list(s.rect), "auto": s.auto, "group": s.group, "by_model": s.by_model}
                          for s in seeds.seeds]}

    # ---- 種子操作

    def seed_action(self, project_name: str, body: dict) -> dict:
        p = load_project(project_name); seeds = items.ItemSeeds(p.dir_path); act = body.get("action")
        frame = int(body.get("frame", 0) or 0)
        if act == "add_ref":
            seeds.add_ref(frame)
        elif act == "remove_ref":
            seeds.refs = [r for r in seeds.refs if r != frame]; seeds.save()
        elif act == "add_closed":
            seeds.add_closed(frame)
        elif act == "remove_closed":
            seeds.closed = [r for r in seeds.closed if r != frame]; seeds.save()
        elif act == "add_seed":
            name = str(body.get("name", "")).strip(); rect = body.get("rect")
            if not name:
                raise ValueError("請輸入物品名稱")
            if not (isinstance(rect, list) and len(rect) == 4 and rect[2] >= 12 and rect[3] >= 12):
                raise ValueError("請先在畫面上拖拉框住物品")
            sec = float(body.get("track_sec", 2.0) or 0.0)
            r = tuple(int(v) for v in rect)
            auto = items.track_seed(p.video_path, frame, r, window_sec=sec, fps=p.fps) if sec > 0 else []
            g = seeds.add_seed(name, frame, r, auto)
            seeds.sync_auto_region(p.resolution)
            d = self._seeds_dict(seeds, p)
            d["last_track"] = {"group": g, "found": len(auto), "frames": [f for f, _ in auto]}
            return d
        elif act == "remove_seed":
            seeds.remove_seed(int(body.get("index", -1)))
        elif act == "remove_indices":
            # 訓練素材預覽：把標成「待刪」的框一次刪掉（只刪那幾格本身，不連帶刪同組的自動框）
            drop = {int(i) for i in body.get("indices") or []}
            if any(i < 0 or i >= len(seeds.seeds) for i in drop):
                raise ValueError("要刪的框不存在，請重新整理後再試")
            seeds.seeds = [s for i, s in enumerate(seeds.seeds) if i not in drop]; seeds.save()
        elif act == "remove_auto_group":
            g = int(body.get("group", 0))
            seeds.seeds = [s for s in seeds.seeds if not (s.auto and s.group == g)]; seeds.save()
        elif act == "remove_item":
            seeds.remove_item(str(body.get("name", "")))
        elif act == "set_region":
            self._set_region(p, seeds, body.get("rect"))
        elif act == "set_box_label":
            seeds.set_box_label(str(body.get("name", "")), bool(body.get("is_box", True)))
        elif act == "add_hand_step":
            name = str(body.get("name", "")).strip(); prompt = str(body.get("prompt", "")).strip()
            if not name or not prompt:
                raise ValueError("請輸入步驟名稱和物件的英文提示（例如 shoe）")
            seeds.add_hand_step(name, prompt, float(body.get("dwell", 0.7) or 0.7))
        elif act == "remove_hand_step":
            seeds.remove_hand_step(str(body.get("name", "")))
        elif act == "predict_frame":
            r = self._reader(p)
            if r is None:
                raise ValueError("找不到示範影片")
            det = self._detector(p)
            with self._lock:
                fr = r.get_frame(max(0, min(frame, max(r.frame_count - 1, 0))))
            reg = tuple(seeds.region) if seeds.region else None
            crop = items._crop(fr, reg) if reg else fr
            rx, ry = (reg[0], reg[1]) if reg else (0, 0)
            hits = det.detect(crop)
            existing = [s for s in seeds.seeds if s.frame == frame]
            preds = []
            for h in hits:
                rect = [int(rx + h.rect[0]), int(ry + h.rect[1]), int(h.rect[2]), int(h.rect[3])]
                if any(s.name == h.name and items._iou(tuple(rect), tuple(s.rect)) > 0.4 for s in existing):
                    continue
                preds.append({"name": h.name, "conf": round(float(h.conf), 2), "rect": rect})
            d = self._seeds_dict(seeds, p)
            d["predictions"] = preds
            return d
        elif act == "add_batch":
            boxes = body.get("boxes") or []
            if not isinstance(boxes, list) or not boxes:
                raise ValueError("沒有要加入的預框")
            sec = float(body.get("track_sec", 2.0) or 0.0)
            added = 0; auto_total = 0; last_g = 0
            for b in boxes:
                name = str(b.get("name", "")).strip(); rect = b.get("rect")
                if not name or not (isinstance(rect, list) and len(rect) == 4 and rect[2] >= 12 and rect[3] >= 12):
                    continue
                r = tuple(int(v) for v in rect)
                auto = items.track_seed(p.video_path, frame, r, window_sec=sec, fps=p.fps) if sec > 0 else []
                last_g = seeds.add_seed(name, frame, r, auto)
                added += 1; auto_total += len(auto)
            seeds.sync_auto_region(p.resolution)
            d = self._seeds_dict(seeds, p)
            d["batch_result"] = {"added": added, "auto": auto_total, "group": last_g}
            return d
        elif act == "retrack_all":
            sec = float(body.get("track_sec", 2.0) or 0.0)
            stat = items.retrack_seeds(p.video_path, seeds, window_sec=sec, fps=p.fps)
            seeds.sync_auto_region(p.resolution)
            d = self._seeds_dict(seeds, p)
            d["retrack"] = stat
            return d
        else:
            raise ValueError(f"不認得的動作：{act}")
        seeds.sync_auto_region(p.resolution)        # 框有增減就重算自動範圍（手動模式不動）
        return self._seeds_dict(seeds, p)

    # ---- 第 3 步

    def generate_steps(self, project_name: str) -> dict:
        p = load_project(project_name); seeds = items.ItemSeeds(p.dir_path)
        if not seeds.order and not seeds.hand_steps:
            raise ValueError("還沒有物品")
        if seeds.order and not os.path.isfile(items.model_path(p)):
            raise ValueError("還沒有訓練好的物品模型，請先回第 2 步訓練")
        names = training.apply_item_steps(p, seeds.order)
        return {"steps": names}

    # ---- 新增專案

    def create(self, name: str) -> dict:
        d = create_project(name.strip())
        return {"name": os.path.basename(d)}

    def import_upload(self, project_name: str, filename: str, data: bytes) -> dict:
        p = load_project(project_name)
        ext = os.path.splitext(filename or "")[1].lower()
        if ext not in (".mp4", ".avi", ".mov", ".mkv"):
            raise ValueError("只接受 mp4／avi／mov／mkv")
        tmp = os.path.join(p.dir_path, "upload_tmp" + ext)
        with open(tmp, "wb") as f:
            f.write(data)
        try:
            vid, w, h, fps = import_demo_video(tmp, p.dir_path)
        finally:
            try:
                os.remove(tmp)
            except OSError:
                pass
        p.video_file = vid; p.resolution = [w, h]; p.fps = fps; _save_config(p)
        self.drop_reader(project_name)
        return {"video": vid, "resolution": [w, h], "fps": fps}

    def record_start(self, project_name: str, source: str | None) -> None:
        load_project(project_name)
        self.drop_reader(project_name)
        self.record.start(project_name, source)

    def record_stop(self) -> dict:
        n = self.record.end_recording(); self.record.stop()
        name = self.record.project_name
        if name:
            self.drop_reader(name)
        return {"frames": n, "project": name}
