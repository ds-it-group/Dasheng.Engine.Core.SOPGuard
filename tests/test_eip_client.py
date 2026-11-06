"""EIP 看板（只讀）：產線清單、轉數表照型體分組、整線目標與報工、連不上回最後一次的資料、產線的 EIP 欄位。不連真的 EIP。"""
from __future__ import annotations

import io
import json
import urllib.error

import pytest

import eip_client as eip
import lines as line_store


class _Resp(io.BytesIO):
    def __enter__(self): return self
    def __exit__(self, *a): self.close()


def _opener(routes, calls=None):
    def op(req, timeout=None):
        if calls is not None:
            calls.append((req.get_method(), req.full_url, json.loads(req.data) if req.data else None))
        for k, v in routes.items():
            if k in req.full_url:
                if isinstance(v, Exception):
                    raise v
                return _Resp(json.dumps(v).encode("utf-8"))
        raise urllib.error.URLError("no route")
    return op


@pytest.fixture(autouse=True)
def base(tmp_path, monkeypatch):
    monkeypatch.setattr(eip, "app_base_dir", lambda: str(tmp_path))
    monkeypatch.setattr(line_store, "app_base_dir", lambda: str(tmp_path))
    eip.clear_cache()
    eip.set_api_base("http://eip.example/")
    return tmp_path


ORDERS = [
    {"orderCode": "CB-1", "specificationCode": "310222 01", "totalQuantity": 400, "timeStart": "07:00"},
    {"OrderCode": "CB-2", "SpecificationCode": "310222 01", "TotalQuantity": 150, "TimeStart": "07:00"},     # PascalCase 也讀得到
    {"orderCode": "CB-3", "specificationCode": "310222 02", "totalQuantity": 800, "timeStart": "10:00"},
    {"orderCode": "CB-4", "specificationCode": "415118 02,415118 05", "totalQuantity": 600, "timeStart": None},
]
DETAILS = [{"timeStart": "07:00", "quantity": 500, "completedQuantity": 300}, {"timeStart": "10:00", "quantity": 460, "completedQuantity": 240}]


def test_api_base_and_departments():
    assert eip.api_base() == "http://eip.example"
    with pytest.raises(ValueError, match="http"):
        eip.set_api_base("eip.example")
    calls = []
    rows = eip.departments("BYI", opener=_opener({"GetDepartmentsByDepartmentType/BYI/170": [
        {"departmentID": 1493, "departmentCode": "A03", "departmentNameTC": "成型 3 線"}, {"departmentCode": "x"}]}, calls))
    assert rows == [{"id": 1493, "code": "A03", "name": "成型 3 線"}] and calls[0][0] == "GET"
    rows = eip.departments("BYI", 160, opener=_opener({"GetDepartmentsByDepartmentType/BYI/160": [      # 製程類別：針車
        {"departmentID": 77, "departmentCode": "S01", "departmentNameTC": "針車 1 線", "departmentType": 160, "isVendor": False, "endAt": "2999-12-31T00:00:00"},
        {"departmentID": 90, "departmentCode": "V1", "departmentNameTC": "外包廠", "departmentType": 0, "isVendor": True},             # 廠商不算產線
        {"departmentID": 91, "departmentCode": "S09", "departmentNameTC": "針車 9 線", "departmentType": 160, "endAt": "2020-01-01T00:00:00"}]}, calls))   # 已停用
    assert rows == [{"id": 77, "code": "S01", "name": "針車 1 線"}]


def test_line_keeps_process_type(tmp_path, monkeypatch):
    import lines as ls
    monkeypatch.setattr(ls, "_path", lambda: str(tmp_path / "lines.json"))
    assert ls.Line(id="L1", name="包裝 1 線").eip_department_type == 170                 # 預設成型
    l = ls.save_line({"name": "針車 1 線", "factory": "BYI", "eip_department_type": 160, "eip_department_id": 77, "eip_department_name": "針車 1 線"})
    assert l.eip_department_type == 160 and next(x for x in ls.load_lines() if x.id == l.id).eip_department_type == 160


def test_group_orders_by_style():
    g = eip.group_orders(ORDERS)
    assert [x["style"] for x in g] == ["310222 01", "310222 02", "415118 02", "415118 05"]      # 照時段，沒時段排最後
    assert g[0]["qty"] == 550 and g[0]["orders"] == ["CB-1", "CB-2"]
    assert g[2]["qty"] == 0 and g[2]["orders"] == ["CB-4"]                                       # 一張單多個型體：數量分不出來


def test_today_caches_and_falls_back_when_offline():
    calls = []
    ok = _opener({"GetDashboardOrdersForPanel": ORDERS, "GetDashboardOrderDetailsForPanel": DETAILS}, calls)
    d = eip.today("BYI", 1493, opener=ok, now=1000.0)
    assert d["ok"] and d["target"] == 960 and d["eip_done"] == 540 and d["styles"][0]["style"] == "310222 01"
    assert calls[0][2]["departmentID"] == 1493 and calls[0][2]["factoryCode"] == "BYI" and "timeZone" in calls[0][2]
    assert eip.today("BYI", 1493, opener=_opener({}), now=1010.0)["ok"]                           # 25 秒內用快取，不重打
    bad = _opener({"GetDashboardOrdersForPanel": urllib.error.URLError("timed out")})
    d = eip.today("BYI", 1493, opener=bad, now=1100.0)
    assert not d["ok"] and d["ago_sec"] == 100 and d["target"] == 960 and "timed out" in d["error"]  # 連不上：留最後一次
    eip.clear_cache()
    d = eip.today("BYI", 1493, opener=bad, now=2000.0)
    assert not d["ok"] and d["styles"] == [] and d["ago_sec"] is None


def test_line_eip_fields_roundtrip():
    l = line_store.save_line({"name": "包裝 3 線", "factory": "BYI", "eip_department_id": "1493", "eip_department_name": "成型 3 線", "station_label": "A 站"})
    got = line_store.get_line(l.id)
    assert got.eip_department_id == 1493 and got.eip_department_name == "成型 3 線" and got.station_label == "A 站"
    pub = line_store.line_public(got)
    assert pub["station"] and pub["eip_department_id"] == 1493
    line_store.save_line({"id": l.id, "eip_department_id": None})
    assert line_store.get_line(l.id).eip_department_id is None and line_store.get_line(l.id).eip_department_name == ""
    with pytest.raises(ValueError, match="廠別"):
        line_store.save_line({"name": "包裝 4 線", "eip_department_id": 5})
