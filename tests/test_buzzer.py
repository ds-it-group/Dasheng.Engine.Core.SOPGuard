"""蜂鳴器：開關只在切換時做事、外接指令開始／結束各跑一次、max_sec 到了會自己停。"""
import os
import time
import wave

import buzzer


def _wait(cond, sec=3.0):
    t0 = time.monotonic()
    while not cond() and time.monotonic() - t0 < sec:
        time.sleep(0.02)
    return cond()


def test_command_mode_runs_on_and_off_once(tmp_path):
    log = tmp_path / "log.txt"
    b = buzzer.Buzzer({**buzzer.DEFAULTS, "mode": "command", "on_cmd": f"echo on >> {log}", "off_cmd": f"echo off >> {log}"})
    for _ in range(5):
        b.set(True)                                   # 每一格都叫一次 set：只有第一次算
    assert _wait(lambda: log.exists() and log.read_text().split() == ["on"])
    for _ in range(5):
        b.set(False)
    assert _wait(lambda: log.read_text().split() == ["on", "off"])
    assert b.error is None


def test_max_sec_stops_by_itself(tmp_path):
    log = tmp_path / "log.txt"
    b = buzzer.Buzzer({**buzzer.DEFAULTS, "mode": "command", "max_sec": 0.2, "on_cmd": f"echo on >> {log}", "off_cmd": f"echo off >> {log}"})
    b.set(True)
    assert _wait(lambda: log.exists() and log.read_text().split() == ["on", "off"])
    b.set(False)


def test_failed_command_reports_error():
    b = buzzer.Buzzer({**buzzer.DEFAULTS, "mode": "command", "on_cmd": "exit 3"})
    b.set(True)
    assert _wait(lambda: b.error is not None)
    b.set(False)


def test_off_mode_does_nothing():
    b = buzzer.Buzzer({**buzzer.DEFAULTS, "mode": "off"})
    b.set(True)
    assert b._thread is None and b.on
    b.set(False)


def test_burst_wav_and_settings_roundtrip(tmp_path, monkeypatch):
    path = buzzer._burst_wav(str(tmp_path / "b.wav"))
    with wave.open(path) as w:
        dur = w.getnframes() / w.getframerate()
    assert abs(dur - sum(on + off for on, off in buzzer.BURST)) < 0.01
    monkeypatch.setattr(buzzer, "SETTINGS_FILE", str(tmp_path / "buzzer.json"))
    assert buzzer.load_settings()["mode"] == "off"     # 沒有檔案＝預設不響
    buzzer.save_settings({**buzzer.DEFAULTS, "mode": "speaker", "max_sec": 30})
    assert buzzer.load_settings() == {**buzzer.DEFAULTS, "mode": "speaker", "max_sec": 30}
    with open(buzzer.SETTINGS_FILE, "w", encoding="utf-8") as f:
        f.write('{"mode": "lol"}')
    assert buzzer.load_settings()["mode"] == "off"
