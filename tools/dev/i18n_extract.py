"""從 SOP-Guard 網頁與伺服器程式抓出要翻譯的中文字串（給 i18n 字典用）。
網頁：HTML 文字節點、title/placeholder/aria-label、JS 字串（"..." '...' `...`，${...} 換成 {0}{1}…）。
伺服器：raise ValueError/RuntimeError、self._set(...)、stage/reason/note/skipped/error 等回給畫面的字串（f-string 的 {...} 換成 {0}…）。
註解不抓。輸出 JSON：{檔案: [字串...]}。"""
import json, os, re, sys

ROOT = sys.argv[1]
OUT = sys.argv[2]
CJK = re.compile(r"[㐀-鿿！-｠　-〿]")


def strip_js_comments(s):
    out, i, n = [], 0, len(s)
    while i < n:
        c = s[i]
        if c in "\"'`":
            q = c; j = i + 1
            while j < n and s[j] != q:
                if s[j] == "\\":
                    j += 1
                j += 1
            out.append(s[i:j + 1]); i = j + 1
        elif s.startswith("//", i) and (i == 0 or s[i - 1] != ":"):
            j = s.find("\n", i); i = n if j < 0 else j
        elif s.startswith("/*", i):
            j = s.find("*/", i + 2); i = n if j < 0 else j + 2
        else:
            out.append(c); i += 1
    return "".join(out)


def templ(s):
    k = [0]
    def rep(m):
        r = "{%d}" % k[0]; k[0] += 1; return r
    return re.sub(r"\$\{(?:[^{}]|\{[^{}]*\})*\}", rep, s)


def js_strings(src):
    src = strip_js_comments(src)
    res = []
    for m in re.finditer(r'"((?:[^"\\\n]|\\.)*)"|\'((?:[^\'\\\n]|\\.)*)\'|`((?:[^`\\]|\\.)*)`', src):
        s = m.group(1) if m.group(1) is not None else m.group(2) if m.group(2) is not None else templ(m.group(3))
        if CJK.search(s):
            res.append(s)
            if "<" in s and ">" in s:            # JS 裡的一段 HTML：畫面上是拆開的文字節點，也要一段一段收
                for m2 in re.finditer(r'(?:title|placeholder|aria-label)="([^"]*)"', s):
                    if CJK.search(m2.group(1)):
                        res.append(m2.group(1))
                for t in re.findall(r">([^<>]+)<", s):
                    t = " ".join(t.split())
                    if CJK.search(t):
                        res.append(t)
    return res


def html_strings(src):
    res = []
    src = re.sub(r"<!--.*?-->", "", src, flags=re.S)
    scripts = re.findall(r"<script[^>]*>(.*?)</script>", src, flags=re.S)
    body = re.sub(r"<script[^>]*>.*?</script>", "", src, flags=re.S)
    body = re.sub(r"<style[^>]*>.*?</style>", "", body, flags=re.S)
    for m in re.finditer(r'(?:title|placeholder|aria-label)="([^"]*)"', body):
        if CJK.search(m.group(1)):
            res.append(m.group(1))
    for t in re.findall(r">([^<>]+)<", body):
        t = " ".join(t.split())
        if CJK.search(t):
            res.append(t)
    for sc in scripts:
        res += js_strings(sc)
    return res


PY_PAT = re.compile(r'(?:raise (?:ValueError|RuntimeError)\(|_set\(|"(?:stage|reason|note|skipped|error|message|title|detail|msg|hint)"\s*:\s*|stage\s*=\s*|reason\s*=\s*|note\s*=\s*)')


def py_strings(src):
    res = []
    for m in re.finditer(r'(f?)("([^"\\\n]|\\.)*"|\'([^\'\\\n]|\\.)*\')', src):
        s = m.group(2)[1:-1]
        if not CJK.search(s):
            continue
        line_start = src.rfind("\n", 0, m.start()) + 1
        line = src[line_start:m.start()]
        if "#" in line and line.index("#") < len(line):
            # 在註解裡
            code = line.split("#", 1)[0]
            if code.count('"') % 2 == 0 and code.count("'") % 2 == 0:
                continue
        if '"""' in line:
            continue
        if m.group(1):
            k = [0]
            def rep(mm):
                r = "{%d}" % k[0]; k[0] += 1; return r
            s = re.sub(r"\{[^{}]*\}", rep, s)
        res.append(s)
    return res


out = {}
web = os.path.join(ROOT, "web")
for fn in sorted(os.listdir(web)):
    p = os.path.join(web, fn)
    if fn.endswith(".html"):
        out["web/" + fn] = html_strings(open(p, encoding="utf-8").read())
    elif fn.endswith(".js") and not fn.startswith("i18n"):
        out["web/" + fn] = js_strings(open(p, encoding="utf-8").read())
for fn in sorted(os.listdir(ROOT)):
    if fn.endswith(".py") and fn not in ("main_ui.py",):
        src = open(os.path.join(ROOT, fn), encoding="utf-8").read()
        src = re.sub(r'"""(.|\n)*?"""', '""', src)
        ss = py_strings(src)
        if ss:
            out[fn] = ss
uniq = {}
for f, ss in out.items():
    for s in ss:
        uniq.setdefault(s, f)
json.dump({"by_file": {f: sorted(set(v)) for f, v in out.items()}, "unique": len(uniq)}, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
for f, v in out.items():
    print(f, len(set(v)))
print("unique", len(uniq))
