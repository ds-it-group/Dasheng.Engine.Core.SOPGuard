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
                    "elapsed": round(time.perf_counter() - self.started_at) if self.started_at and self.running else None}

    # ---- 挑素材訓練（可以跨型體地區、留片段驗證）

    def start_material(self, target: str, selection: list[dict], epochs: int = 30) -> dict:
        """selection：[{project, start, end}]（片段的起訖格）。回傳這次的計畫（訓練片段、驗證片段）。"""
        import training_material as tm
        if self.running:
            raise ValueError("已經在訓練中，請等它跑完")
        if not selection:
            raise ValueError("請至少勾一段訓練素材")
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
        with self._lock:
            self.project_name = target; self.stage = "準備中"; self.done_n = self.total_n = 0; self.validation = None; self.installed = None
            self.lines = []; self.error = None; self.finished = False; self.stats = None; self.started_at = time.perf_counter()
        self._thread = threading.Thread(target=self._run_material, args=(tgt.project_name, train, hold, epochs), daemon=True); self._thread.start()
        return {"train": train, "holdout": hold}

    def _run_material(self, target: str, train: list[dict], hold: list[dict], epochs: int) -> None:
        import shutil
        from datetime import datetime
        import packing_methods as pkg
        import training_material as tm
        try:
            tgt = load_project(target)
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
                if not seeds.seeds:
                    continue
                tag = f"（{k + 1}/{len(by_proj)} {name}）"
                trace = items.build_trace(sp, HAND_MODEL, YOLO_WEIGHTS, progress=lambda a, b, t=tag: self._set(f"找盒子與手{t}：{a}/{b} 格", a, b))
                st = items.build_dataset(sp, trace, seeds, progress=lambda a, b, t=tag: self._set(f"延伸框選{t}：{a}/{b}", a, b))
                parts.append((items.dataset_dir(sp), list(seeds.order)))
                for n in seeds.order:
                    if n not in names:
                        names.append(n)
            if not parts:
                raise ValueError("勾選的片段裡沒有任何框")
            mix = items.dataset_dir(tgt) + "_mix"
            stats = tm.merge_datasets(parts, mix, names)
            with self._lock:
                self.stats = {**stats, "train_segments": len(train), "holdout_segments": len(hold)}
            if stats["train"] == 0:
                raise ValueError("延伸不出任何訓練圖")
            tmp_model = os.path.join(tgt.dir_path, items.MODEL_DIR, "candidate.pt")
            os.makedirs(os.path.dirname(tmp_model), exist_ok=True)
            if os.path.isfile(tmp_model):
                os.remove(tmp_model)
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
            # 離線驗證：每個配色保留的那一段
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
            own = items.own_model_path(tgt)
            if passed:
                if os.path.isfile(own):
                    shutil.copyfile(own, os.path.join(os.path.dirname(own), f"best_prev_{datetime.now():%Y%m%d_%H%M}.pt"))
                os.replace(tmp_model, own)
                if tgt.packaging is not None and tgt.packaging.model_source:
                    tgt.packaging.model_source = None
                    _save_config(tgt)
            if tgt.packaging is not None:
                for r in results:
                    if r["ok"] is None or not r["color"]:
                        continue
                    note = "" if r["ok"] else "驗證漏看：" + "、".join(r["missing"])
                    pkg.set_color(target, r["color"], "verified" if r["ok"] else "failed", note)
            with self._lock:
                self.installed = passed
                self.finished = True
                self.stage = ("訓練完成，驗證通過，已換上新模型" if results else "訓練完成（沒有保留片段可驗證），已換上新模型") if passed \
                    else "訓練完成但驗證沒過，保留舊模型（新模型存成 candidate.pt）"
        except Exception as e:
            with self._lock:
                self.error = f"{type(e).__name__}: {e}" if not isinstance(e, (ValueError, RuntimeError)) else str(e)
                self.stage = "失敗"
        finally:
            self._proc = None

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
        with self._lock:
            self.project_name = project_name; self.stage = "準備中"; self.done_n = self.total_n = 0
            self.lines = []; self.error = None; self.finished = False; self.stats = None; self.started_at = time.perf_counter()
            self.validation = None; self.installed = None
        self._thread = threading.Thread(target=self._run, args=(project_name,), daemon=True); self._thread.start()

    def _run(self, project_name: str) -> None:
        try:
            project = load_project(project_name)
            training.sync_item_region(project); training.ensure_state_anchor(project)
            project = load_project(project_name)
            seeds = items.ItemSeeds(project.dir_path)
            trace = items.build_trace(project, HAND_MODEL, YOLO_WEIGHTS,
                                      progress=lambda a, b: self._set(f"找盒子與手：{a}/{b} 格", a, b))
            stats = items.build_dataset(project, trace, seeds, progress=lambda a, b: self._set(f"延伸框選：{a}/{b}", a, b))
            with self._lock:
                self.stats = stats
            if stats["train"] == 0:
                raise ValueError("框選的物品延伸不出任何一格；請確認「空盒／空桌面」有標、框選那一格看得到東西")
            self._set("訓練模型中（約 20～60 分鐘）…")
            cmd = items.train_command(project)
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
            mp = items.own_model_path(project)
            if code != 0 or not os.path.isfile(mp):
                raise RuntimeError(f"訓練失敗（結束碼 {code}）：" + " / ".join(self.lines[-3:]))
            project = load_project(project_name)
            if project.packaging is not None and project.packaging.model_source:
                project.packaging.model_source = None          # 自己訓練好了 → 改用自己的模型
                _save_config(project)
            with self._lock:
                self.finished = True; self.stage = "訓練完成"
        except Exception as e:
            with self._lock:
                self.error = f"{type(e).__name__}: {e}" if not isinstance(e, (ValueError, RuntimeError)) else str(e)
                self.stage = "失敗"
        finally:
            self._proc = None


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
        self._lock = threading.Lock()
        self.train = TrainJob(); self.record = RecordJob()

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
        """影格 JPEG。region：裁到桌面範圍；box=[x,y,w,h]：畫框；zoom：以框為中心放大（框外留一倍，10:9）。"""
        p = load_project(project_name); r = self._reader(p)
        if r is None:
            return None
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
        p = load_project(project_name); r = self._reader(p); seeds = items.ItemSeeds(p.dir_path)
        return {"name": p.project_name, "resolution": list(p.resolution), "fps": p.fps, "has_video": r is not None,
                "frame_count": r.frame_count if r else 0, "has_model": os.path.isfile(items.model_path(p)),
                "steps": [s.step_name for s in p.steps], "item_steps": any(s.type in ("item", "hand_on_object") for s in p.steps),
                "seeds": self._seeds_dict(seeds)}

    @staticmethod
    def _seeds_dict(seeds: items.ItemSeeds) -> dict:
        return {"order": list(seeds.order), "refs": list(seeds.refs), "closed": list(seeds.closed), "region": seeds.region,
                "box_labels": list(seeds.box_labels), "hand_steps": list(seeds.hand_steps), "counts": seeds.counts(),
                "auto_counts": seeds.auto_counts(),
                "seeds": [{"name": s.name, "frame": s.frame, "rect": list(s.rect), "auto": s.auto, "group": s.group} for s in seeds.seeds]}

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
            d = self._seeds_dict(seeds)
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
            rect = body.get("rect")
            if rect is not None and not (isinstance(rect, list) and len(rect) == 4):
                raise ValueError("桌面範圍要是 [x, y, w, h]")
            seeds.set_region(None if rect is None else tuple(int(v) for v in rect))
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
            d = self._seeds_dict(seeds)
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
            d = self._seeds_dict(seeds)
            d["batch_result"] = {"added": added, "auto": auto_total, "group": last_g}
            return d
        elif act == "retrack_all":
            sec = float(body.get("track_sec", 2.0) or 0.0)
            stat = items.retrack_seeds(p.video_path, seeds, window_sec=sec, fps=p.fps)
            d = self._seeds_dict(seeds)
            d["retrack"] = stat
            return d
        else:
            raise ValueError(f"不認得的動作：{act}")
        return self._seeds_dict(seeds)

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
