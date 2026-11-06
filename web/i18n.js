/* 介面語言（2026-11-06 使用者裁示：設定裡可以改語言；繁中、English、Bahasa Indonesia；三頁＋伺服器訊息都要翻）。
   做法：不改各頁程式，畫面上出現的中文字（文字、title、placeholder、aria-label）一律拿 i18n_dict.js 的對照表換掉：
   1. 整句對得上 → 直接換；2. 字典裡有 {0}{1} 的句型 → 照句型換，{n} 裡的字也試著翻；
   3. 都對不上 → 按句號、分號、全形空白拆開，一段一段翻。對不到的保持中文。
   畫面後來才長出來或改字的（伺服器回的訊息、輪詢更新），用 MutationObserver 跟著換。
   使用者自己取的名稱（步驟、物品、專案）不在字典裡，不會被換。
   語言存在這台電腦（/api/ui/lang → ui_lang.txt），瀏覽器另存一份 localStorage 讓開頁不閃中文。 */
(function () {
  const KEY = "sopg-lang", LANGS = [["zh", "繁體中文"], ["en", "English"], ["id", "Bahasa Indonesia"]], IDX = { en: 0, id: 1 };
  const CJK = /[㐀-鿿]/;
  let lang = "zh";
  try { lang = localStorage.getItem(KEY) || "zh"; } catch (e) {}
  const D = window.I18N_DICT || {};
  const exact = new Map(), pats = [];
  for (const [k, v] of Object.entries(D)) {
    if (/\{\d+\}/.test(k)) {
      const re = new RegExp("^" + k.replace(/[.*+?^$()|[\]\\]/g, "\\$&").replace(/\{(\d+)\}/g, "(.+?)") + "$");
      const order = [...k.matchAll(/\{(\d+)\}/g)].map((m) => +m[1]);
      pats.push({ re, order, v, len: k.replace(/\{\d+\}/g, "").length });
    } else exact.set(k.trim(), v);
  }
  pats.sort((a, b) => b.len - a.len);
  const cache = new Map();
  const PUNCT = { "。": ". ", "；": "; ", "，": ", ", "、": ", ", "：": ": ", "（": " (", "）": ") ", "「": "\"", "」": "\"", "？": "? ", "！": "! " };
  function pick(v) { const s = v && v[IDX[lang]]; return s == null || s === "" ? null : s; }
  function look(t, depth) {
    const e = exact.get(t); if (e) { const s = pick(e); if (s != null) return s; }
    for (const p of pats) {
      const m = t.match(p.re); if (!m) continue;
      let s = pick(p.v); if (s == null) break;
      const g = {}; p.order.forEach((n, i) => { g[n] = m[i + 1]; });
      s = s.replace(/\{(\d+)\}/g, (_, n) => { const x = g[n] == null ? "" : g[n]; return CJK.test(x) && depth < 2 ? look(x.trim(), depth + 1) : x; });
      return s;
    }
    if (depth > 0) return t;
    const parts = t.split(/([。；！？\n]|　+|｜)/);
    if (parts.length > 1) {
      let changed = false;
      const out = parts.map((x) => {
        if (!x) return x;
        if (PUNCT[x]) return PUNCT[x];
        if (/^　+$/.test(x)) return "  ";
        if (!CJK.test(x)) return x;
        let y = look(x.trim(), 1); if (y === x.trim()) y = runs(y); if (y !== x.trim()) changed = true; return y;
      });
      if (changed) return out.join("").replace(/\s+$/, "");
    }
    return runs(t);
  }
  /* 最後一招：數字、名稱跟中文用 + 黏在一起的（例如「12:30 換線」「6 步」），把每一段連續中文各自整句查；查不到的留著 */
  function runs(t) {
    return t.replace(/[\u3400-\u9fff]+/g, (w) => { const e = exact.get(w); const s = e && pick(e); return s != null ? s : w; });
  }
  function tr(s) {
    if (lang === "zh" || s == null) return s;
    s = String(s); if (!CJK.test(s)) return s;
    if (cache.has(s)) return cache.get(s);
    const lead = s.match(/^\s*/)[0], trail = s.match(/\s*$/)[0], core = s.trim();
    const r = lead + look(core, 0) + trail;
    if (cache.size > 5000) cache.clear();
    cache.set(s, r); return r;
  }
  // ---- 套到畫面上：記住每個文字節點／屬性原本的中文，切回中文或內容被程式改掉時才知道要從哪個原文翻
  const SKIP = "script, style, textarea, [translate=no], .notr";
  const orig = new WeakMap(), shown = new WeakMap();
  const ATTRS = ["title", "placeholder", "aria-label"];
  function doText(n) {
    const p = n.parentElement; if (!p || p.closest(SKIP)) return;
    const cur = n.nodeValue; let src = cur;
    if (orig.has(n) && shown.get(n) === cur) src = orig.get(n); else orig.set(n, cur);
    const out = tr(src); shown.set(n, out);
    if (out !== cur) n.nodeValue = out;
  }
  function doAttrs(el) {
    if (el.closest(SKIP)) return;
    let m = el.__i18n; if (!m) m = el.__i18n = {};
    for (const a of ATTRS) {
      if (!el.hasAttribute(a)) continue;
      const cur = el.getAttribute(a); const r = m[a];
      const src = r && r.l === cur ? r.o : cur;
      const out = tr(src); m[a] = { o: src, l: out };
      if (out !== cur) el.setAttribute(a, out);
    }
  }
  function walk(root) {
    if (!root) return;
    if (root.nodeType === 3) { doText(root); return; }
    if (root.nodeType !== 1 && root.nodeType !== 9 && root.nodeType !== 11) return;
    if (root.nodeType === 1) doAttrs(root);
    const tw = document.createTreeWalker(root, NodeFilter.SHOW_ELEMENT | NodeFilter.SHOW_TEXT);
    let n; while ((n = tw.nextNode())) { if (n.nodeType === 3) doText(n); else doAttrs(n); }
  }
  let obs = null;
  function observe() {
    if (obs) return;
    obs = new MutationObserver((ms) => {
      for (const m of ms) {
        if (m.type === "characterData") doText(m.target);
        else if (m.type === "attributes") doAttrs(m.target);
        else m.addedNodes.forEach(walk);
      }
    });
    obs.observe(document.documentElement, { subtree: true, childList: true, characterData: true, attributes: true, attributeFilter: ATTRS });
  }
  function apply() {
    document.documentElement.lang = lang === "zh" ? "zh-Hant" : lang;
    if (!document.__i18nTitle) document.__i18nTitle = document.title;
    document.title = tr(document.__i18nTitle);
    walk(document.body);
  }
  function setLang(l, persist) {
    if (!(l in IDX)) l = "zh";
    lang = l; cache.clear();
    try { localStorage.setItem(KEY, l); } catch (e) {}
    if (document.body) apply();
    document.dispatchEvent(new CustomEvent("i18n:change"));          // 畫在 canvas 上的字（標記頁的框標籤）要各頁自己重畫
    if (persist) fetch("/api/ui/lang", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ lang: l }) }).catch(() => {});
  }
  function start() {
    apply(); observe();
    fetch("/api/ui/lang").then((r) => r.json()).then((d) => { if (d && d.lang && d.lang !== lang) setLang(d.lang, false); }).catch(() => {});
  }
  window.I18N = { t: tr, setLang, lang: () => lang, LANGS };
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", start); else start();
})();
