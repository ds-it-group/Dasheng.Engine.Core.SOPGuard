"""蜂鳴器：有警告就一直叫，警告解除（按「解除警告」或自動解除）才停。

監控迴圈每一格呼叫 Buzzer.set(fsm.alert_active)；只有開／關切換時才做事。設定存在 buzzer.json（這台電腦共用，不分專案）：
  mode     "off"     不響（預設）
           "speaker" 主機喇叭：Windows 用 winsound，Linux 用 paplay／aplay 播一段「嗶嗶嗶」
           "command" 外接蜂鳴器／警示燈：警告開始時執行 on_cmd、結束時執行 off_cmd（例如 USB 繼電器、gpioset 的指令）
  max_sec  最多叫幾秒（0＝警告多久就叫多久）
on_cmd／off_cmd 只能直接改 buzzer.json，網頁改不到：伺服器聽 0.0.0.0，從網頁設指令等於讓區網任何人在這台執行程式。
"""
from __future__ import annotations

import json
import math
import os
import shutil
import struct
import subprocess
import sys
import threading
import time
import wave

from project_store import app_base_dir

SETTINGS_FILE = os.path.join(app_base_dir(), "buzzer.json")
MODES = ("off", "speaker", "command")
DEFAULTS = {"mode": "off", "max_sec": 0, "on_cmd": "", "off_cmd": ""}
BEEP_HZ = 2700            # 一般壓電蜂鳴器的頻率，比 1 kHz 刺耳、在機台噪音裡聽得到
BURST = [(0.18, 0.08)] * 3 + [(0.0, 0.45)]     # 嗶嗶嗶、停一下：(響幾秒, 停幾秒)
CMD_TIMEOUT = 5.0


def load_settings() -> dict:
    s = dict(DEFAULTS)
    try:
        with open(SETTINGS_FILE, encoding="utf-8") as f:
            s.update({k: v for k, v in json.load(f).items() if k in DEFAULTS})
    except (OSError, ValueError):
        pass
    if s["mode"] not in MODES:
        s["mode"] = "off"
    return s


def save_settings(s: dict) -> None:
    with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
        json.dump({k: s.get(k, DEFAULTS[k]) for k in DEFAULTS}, f, ensure_ascii=False, indent=1)


def _burst_wav(path: str, rate: int = 22050) -> str:
    """一次「嗶嗶嗶＋停頓」的 wav（方波帶一點圓角，聽起來像蜂鳴器）。"""
    if os.path.isfile(path):
        return path
    frames = bytearray()
    for on, off in BURST:
        n = int(on * rate)
        for i in range(n):
            v = math.tanh(4 * math.sin(2 * math.pi * BEEP_HZ * i / rate))
            env = min(1.0, i / 200, (n - i) / 200)                  # 頭尾淡入淡出，避免爆音
            frames += struct.pack("<h", int(0.6 * 32767 * v * env))
        frames += b"\x00\x00" * int(off * rate)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with wave.open(path, "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(rate); w.writeframes(bytes(frames))
    return path


def _player() -> list[str] | None:
    for exe, args in (("paplay", []), ("pw-play", []), ("aplay", ["-q"])):
        p = shutil.which(exe)
        if p:
            return [p, *args]
    return None


class Buzzer:
    def __init__(self, settings: dict | None = None):
        self.settings = settings or load_settings()
        self.error: str | None = None
        self._on = False
        self._stop = threading.Event()
        self._thread: threading.Thread | None = None
        self._lock = threading.Lock()

    @property
    def on(self) -> bool:
        return self._on

    def configure(self, settings: dict) -> None:
        was = self._on
        self.set(False)
        self.settings = settings
        if was:
            self.set(True)

    def set(self, on: bool) -> None:
        with self._lock:
            if on == self._on:
                return
            self._on = on
            mode = self.settings.get("mode", "off")
            if on and mode != "off":
                self._stop = threading.Event()        # 每次一個新的：舊執行緒還在收尾時不會被叫回來
                self._thread = threading.Thread(target=self._run, args=(mode, self._stop), daemon=True)
                self._thread.start()
            elif not on:
                self._stop.set()

    def test(self, sec: float = 2.0) -> None:
        """設定頁的「測試」：照目前設定叫 sec 秒。"""
        self.set(True)
        threading.Timer(sec, lambda: self.set(False)).start()

    def _run(self, mode: str, stop: threading.Event) -> None:
        self.error = None
        max_sec = float(self.settings.get("max_sec") or 0)
        try:
            if mode == "command":
                self._shell(self.settings.get("on_cmd", ""))
                stop.wait(max_sec or None)
                self._shell(self.settings.get("off_cmd", ""))
            else:
                self._speaker(stop, max_sec)
        except Exception as e:
            self.error = f"蜂鳴器沒有響：{e}"
            print(f"[蜂鳴器] {self.error}")

    def _speaker(self, stop: threading.Event, max_sec: float) -> None:
        t0 = time.monotonic()
        alive = lambda: not stop.is_set() and not (max_sec and time.monotonic() - t0 >= max_sec)
        if sys.platform == "win32":
            import winsound
            while alive():
                for on, off in BURST:
                    if on:
                        winsound.Beep(BEEP_HZ, int(on * 1000))
                    time.sleep(off)
            return
        player = _player()
        if player is None:
            raise RuntimeError("找不到 paplay／aplay，裝 pulseaudio-utils 或 alsa-utils")
        wav = _burst_wav(os.path.join(app_base_dir(), "cache", "buzzer_burst.wav"))
        while alive():
            p = subprocess.Popen([*player, wav], stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
            while p.poll() is None:
                if not alive():
                    p.terminate(); break
                time.sleep(0.05)
            if p.returncode not in (0, None, -15):
                raise RuntimeError((p.stderr.read() or b"").decode(errors="replace").strip()[:200] or f"播放程式結束碼 {p.returncode}")

    @staticmethod
    def _shell(cmd: str) -> None:
        if not cmd.strip():
            return
        r = subprocess.run(cmd, shell=True, timeout=CMD_TIMEOUT, capture_output=True)
        if r.returncode != 0:
            raise RuntimeError(f"「{cmd}」失敗：{(r.stderr or b'').decode(errors='replace').strip()[:200]}")
