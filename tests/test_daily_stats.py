"""當天統計：記一輪、超時、各步驟次數；還沒上傳的由舊到新補送、失敗留著下次、沒接 EIP 不送；上傳內容只有錯誤原因和次數。不連真的 EIP。"""
from __future__ import annotations

import io
import json
import urllib.error
from datetime import datetime

import pytest

import daily_stats as ds
import eip_client
import lines as line_store
from monitor_service import CycleTracker


class _Resp(io.BytesIO):
    def __enter__(self): return self
    def __exit__(self, *a): self.close()


@pytest.fixture(autouse=True)
def base(tmp_path, monkeypatch):
    for m in (ds, line_store, eip_client):
        monkeypatch.setattr(m, "app_base_dir", lambda: str(tmp_path))
    monkeypatch.setattr(line_store, "computer_name", lambda: "PACK01")
    eip_client.set_api_base("http://eip.example")
    ds._state.update(running=False, done=0, total=0, current=None, last_ok_at=None, last_error=None, backfilled=[])
    return tmp_path


def _line(eip=True):
    return line_store.save_line({"name": "包裝 3 線" if eip else "包裝 9 線", "factory": "BYI" if eip else "",
                                 **({"eip_department_id": 1493, "eip_department_name": "成型 3 線"} if eip else {})})


def test_record_counts_per_method_and_step():
    t = datetime(2026, 11, 4, 9, 0)
    ds.record("L1", "310222 01_歐洲", "完成", [], t)
    ds.record("L1", "310222 01_歐洲", "漏做", ["盒端貼紙", "檢查鞋舌"], t)
    ds.record("L1", "310222 01_歐洲", "超時", ["盒端貼紙"], t)
    ds.record("L1", "310222 02_歐洲", "跳步", [], t)                        # 跳步不記
    d = ds.day_file("L1", "2026-11-04")
    m = d["methods"]["310222 01_歐洲"]
    assert (m["cycles"], m["bad_cycles"], m["timeouts"]) == (1, 1, 1)
    assert m["steps"]["盒端貼紙"] == {"missed": 1, "timeout": 1} and m["steps"]["檢查鞋舌"] == {"missed": 1, "timeout": 0}
    assert "310222 02_歐洲" not in d["methods"]
    p = ds.payloads(d, "BYI", 1493, "PACK01")
    assert p == [{"recordDate": "2026-11-04", "factoryCode": "BYI", "departmentID": 1493, "station": "PACK01", "methodName": "310222 01_歐洲",
                  "errors": [{"name": "檢查鞋舌", "missed": 1, "timeout": 0}, {"name": "盒端貼紙", "missed": 1, "timeout": 1}]}]


def test_tracker_calls_on_record():
    got = []
    tr = CycleTracker([]); tr.on_record = lambda kind, missing: got.append((kind, missing))
    tr._record(1.0, False, "漏做", ["貼紙"])
    assert got == [("漏做", ["貼紙"])]
    tr.on_record = lambda kind, missing: 1 / 0                                  # 統計出錯不影響監控
    tr._record(2.0, True, "完成", [])


def test_upload_backlog_oldest_first_fail_then_retry():
    l = _line(); off = _line(eip=False)
    ds.record(l.id, "A", "漏做", ["貼紙"], datetime(2026, 11, 3, 9))
    ds.record(l.id, "A", "完成", [], datetime(2026, 11, 4, 9))
    ds.record(off.id, "A", "漏做", ["貼紙"], datetime(2026, 11, 4, 9))         # 沒接 EIP：只存本機
    assert [d for _, d in ds.pending()] == ["2026-11-03", "2026-11-04", "2026-11-04"]
    sent = []

    def ok(req, timeout=None):
        sent.append((req.full_url, json.loads(req.data), req.headers.get("X-device-key")))
        return _Resp(b"{}")

    def missing(req, timeout=None):
        raise urllib.error.HTTPError(req.full_url, 404, "Not Found", {}, None)

    r = ds.upload_pending(opener=missing)
    assert r["sent"] == [] and "開卡" in r["error"] and ds.status(l.id)["state"] == "fail"
    assert ds.status(l.id)["pending"] == ["2026-11-03", "2026-11-04"] and ds.status(off.id)["state"] == "off"
    with open(f"{ds.app_base_dir()}/eip_device_key.txt", "w", encoding="utf-8") as f:
        f.write("k123")
    r = ds.upload_pending(opener=ok)
    assert r["sent"] == ["2026-11-03", "2026-11-04"] and r["error"] is None
    assert [b["recordDate"] for _, b, _ in sent] == ["2026-11-03", "2026-11-04"] and sent[0][0].endswith("/api/MES/PackingGuard/SetDailyErrors")
    assert sent[1][1]["errors"] == [] and sent[0][2] == "k123"                    # 那天沒出錯：送空的（EIP 清掉舊列）；有金鑰就帶
    assert ds.status(l.id)["pending"] == [] and ds.status(l.id)["state"] == "ok" and ds.status(l.id)["backfilled"] == ["2026-11-03", "2026-11-04"]
    ds.record(l.id, "A", "漏做", ["貼紙"], datetime(2026, 11, 4, 9))            # 傳完又有新的（時間跟上次一樣也要算）：再變成還沒傳
    assert ds.pending(l.id) == [(l.id, "2026-11-04")]
