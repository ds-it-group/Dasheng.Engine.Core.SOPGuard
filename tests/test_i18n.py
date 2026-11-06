"""介面語言：字典格式、佔位一致、使用者常取的名稱不收；這台電腦的語言存讀。翻譯本身在瀏覽器（web/i18n.js）。"""
from __future__ import annotations

import json
import os
import re

import pytest

import web_server

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _dict() -> dict:
    s = open(os.path.join(ROOT, "web", "i18n_dict.js"), encoding="utf-8").read()
    return json.loads(s[s.index("{"):s.rindex("}") + 1])


def test_dict_shape_and_placeholders():
    d = _dict()
    assert len(d) > 900
    for k, v in d.items():
        assert isinstance(v, list) and len(v) == 2 and all(isinstance(x, str) and x for x in v), k
        ph = sorted(re.findall(r"\{\d+\}", k))
        assert all(sorted(re.findall(r"\{\d+\}", x)) == ph for x in v), k
    for must in ("目前包裝方式", "這台電腦的產線", "製程類別", "前往監控", "第 {0} 輪進行中"):
        assert must in d
    for name in ("藍盒", "鞋子", "檢查鞋舌"):              # 使用者自己取的步驟名稱不能被換掉
        assert name not in d


def test_ui_lang_saved_per_computer(tmp_path, monkeypatch):
    import project_store
    monkeypatch.setattr(project_store, "app_base_dir", lambda: str(tmp_path))
    assert web_server._ui_lang() == "zh"                    # 沒設＝繁中
    assert web_server._ui_lang("id") == "id" and web_server._ui_lang() == "id"
    with pytest.raises(ValueError):
        web_server._ui_lang("vi")
