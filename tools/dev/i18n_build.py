"""把翻譯好的對照表（{中文: [English, Bahasa Indonesia]} 的 JSON，可以多個檔）合併寫成 web/i18n_dict.js。

用法：python tools/dev/i18n_build.py 翻譯1.json 翻譯2.json …
- 已經在 web/i18n_dict.js 的會保留，新檔案裡同一句以新的為準。
- {0}{1}… 句型：譯文的佔位要跟原文一樣多，不一樣的丟掉並列出來。
- 使用者常取的物品／動作名稱（藍盒、鞋子…）不收：監控畫面的步驟名稱是使用者自己取的，不能被換掉。
找還沒翻的字：python tools/dev/i18n_extract.py . out.json，再跟 web/i18n_dict.js 比。"""
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUT = os.path.join(ROOT, "web", "i18n_dict.js")
USER_NAMES = {"藍盒", "鞋子", "盒子", "鞋舌", "盒端貼紙", "盒底貼標", "盒底朝上", "鞋子在盒上", "檢查鞋舌", "貼紙", "標籤", "防黴片", "底部貼紙", "盒底", "盒蓋"}
CJK = re.compile(r"[㐀-鿿]")


def load_existing() -> dict:
    if not os.path.isfile(OUT):
        return {}
    s = open(OUT, encoding="utf-8").read()
    i = s.index("{")
    return json.loads(s[i:s.rindex("}") + 1])


def main(paths: list[str]) -> int:
    d = load_existing()
    bad = []
    for p in paths:
        for k, v in json.load(open(p, encoding="utf-8")).items():
            if not CJK.search(k) or k.strip() in USER_NAMES:
                continue
            if not (isinstance(v, list) and len(v) == 2 and all(isinstance(x, str) for x in v)):
                bad.append((k, "格式")); continue
            ph = sorted(re.findall(r"\{\d+\}", k))
            if any(sorted(re.findall(r"\{\d+\}", x)) != ph for x in v):
                bad.append((k, "佔位不符")); continue
            if k.strip() != k and k.strip() in d:
                continue
            d[k.strip() if not ph else k] = v
    body = json.dumps(dict(sorted(d.items())), ensure_ascii=False, indent=0)
    with open(OUT, "w", encoding="utf-8") as f:
        f.write("/* 介面翻譯對照表：中文 → [English, Bahasa Indonesia]。由 tools/dev/i18n_build.py 產生，用法見 i18n.js。 */\n")
        f.write("window.I18N_DICT = " + body + ";\n")
    print(f"{len(d)} 句寫進 {OUT}")
    for k, why in bad:
        print("丟掉", why, k)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
