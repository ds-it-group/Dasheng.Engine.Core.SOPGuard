/* 這台電腦的產線設定（2026-11-06 使用者裁示：一台電腦一條線；不要獨立的「產線設定」頁，改成每一頁左側欄最下面一個齒輪「這台電腦的產線」）。
   只設產線名稱、廠別、相機、製程類別＋接哪條 EIP 產線（清單由 EIP 查資料庫部門檔，照製程類別給實際產線）、站別顯示名稱；桌面範圍自動算，不在這裡設。
   語言（繁中／English／Bahasa Indonesia）也在這裡選，選了馬上生效（見 i18n.js）。
   存檔走 /api/lines/save（第一條線；沒有就新增）。存好會發 "pcset:saved" 事件，監控畫面據此重讀。 */
(function () {
  const H = (tag, attrs, html) => { const e = document.createElement(tag); Object.assign(e, attrs || {}); if (html != null) e.innerHTML = html; return e; };
  const css = H("style", null, `
    .side a#pcBtn { margin-top: auto; border-top: 1px solid var(--line-soft); }
    .side a#pcBtn.warn .ico { color: var(--accent); }
    #pcDlg .dc { display: flex; flex-direction: column; gap: 10px; } #pcDlg .row2 { display: flex; gap: 10px; flex-wrap: wrap; align-items: flex-end; }
    #pcDlg .ro { min-height: 30px; display: flex; align-items: center; color: var(--ink-2); }`);
  document.head.appendChild(css);
  const btn = H("a", { id: "pcBtn", href: "#", title: "這台電腦的產線設定（相機、EIP）" }, '<span class="mi ico">settings</span><span class="txt">這台電腦的產線</span>');
  const dlg = H("div", { className: "scrim", id: "pcDlg", hidden: true }, `
    <div class="dialog" role="dialog" aria-modal="true" aria-labelledby="pcTitle" style="width:min(640px,calc(100vw - 32px));height:auto">
      <div class="dt"><span class="mi mark">settings</span><h4 id="pcTitle">這台電腦的產線</h4></div>
      <div class="dc">
        <div class="row2">
          <div class="fld w200"><label for="pcLang">語言 / Language / Bahasa</label><select id="pcLang" class="notr"><option value="zh">繁體中文</option><option value="en">English</option><option value="id">Bahasa Indonesia</option></select></div>
        </div>
        <div class="row2">
          <div class="fld w140"><label for="pcName">產線名稱 *</label><input id="pcName" placeholder="例如 包裝 1 線"></div>
          <div class="fld w100"><label for="pcFactory">廠別</label><select id="pcFactory"><option value="">（不接）</option><option>BYI</option><option>GGV</option></select></div>
          <div class="fld w140"><label>站別（電腦名稱，自動帶）</label><div class="ro n" id="pcStation"></div></div>
        </div>
        <div class="fld" style="width:100%"><label for="pcCamera">相機（編號 0、1… 或 rtsp 網址；密碼只存在這台電腦、畫面上遮成 ***）</label><input id="pcCamera" placeholder="rtsp://帳號:密碼@相機位址:554/stream1"></div>
        <div class="row2">
          <div class="fld w100"><label for="pcType">製程類別</label><select id="pcType"><option value="140">組底</option><option value="150">裁斷</option><option value="160">針車</option><option value="170">成型</option></select></div>
          <div class="fld w200"><label for="pcEip">EIP 產線（不選＝不上傳統計）</label><select id="pcEip"><option value="">（不接）</option></select></div>
          <div class="fld w120"><label for="pcLabel">站別顯示名稱</label><input id="pcLabel" placeholder="例如 A 站"></div>
        </div>
        <div class="hint2" id="pcMsg" style="font-size:12.5px;color:var(--ink-2)"></div>
        <div class="note danger" id="pcErr" hidden></div>
      </div>
      <div class="da"><button class="btn btn-cancel" id="pcCancel">取消</button><button class="btn btn-primary raised" id="pcSave">儲存</button></div>
    </div>`);
  const $ = (id) => document.getElementById(id);
  let line = null;
  async function api(path, body) { const r = await fetch(path, body ? { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body) } : {}); return r.json(); }
  async function current() { const d = await api("/api/lines"); return { line: (d.lines || [])[0] || null, station: d.station || ((d.lines || [])[0] || {}).station || "" }; }
  async function loadEip(keep) {
    const f = $("pcFactory").value.trim(), sel = $("pcEip"), msg = $("pcMsg");
    if (!f) { msg.textContent = "選了廠別才讀得到 EIP 產線"; return; }
    msg.textContent = "讀取 EIP 產線清單中…";
    const tp = $("pcType"), tname = tp.selectedOptions[0] ? tp.selectedOptions[0].textContent : "";
    const d = await api("/api/eip/lines?factory=" + encodeURIComponent(f) + "&type=" + encodeURIComponent(tp.value));
    if (!d.ok) { msg.textContent = "讀不到 EIP 產線：" + (d.error || ""); return; }
    const cur = keep != null ? String(keep) : sel.value; sel.innerHTML = ""; sel.appendChild(new Option("（不接）", ""));
    for (const x of d.lines) sel.appendChild(new Option(x.name + (x.code && x.code !== x.name ? `（${x.code}）` : ""), String(x.id)));
    if (cur && ![...sel.options].some((o) => o.value === cur)) sel.appendChild(new Option(`（${cur}，清單裡沒有）`, cur));
    sel.value = cur || ""; msg.textContent = `${f} 有 ${d.lines.length} 條${tname}線`;
  }
  async function open() {
    const c = await current(); line = c.line;
    $("pcName").value = line ? line.name : ""; $("pcFactory").value = line ? line.factory : ""; $("pcCamera").value = line ? line.camera : "";
    $("pcLabel").value = line ? (line.station_label || "") : ""; $("pcType").value = String((line && line.eip_department_type) || 170); $("pcStation").textContent = c.station || (line && line.station) || "";
    const sel = $("pcEip"); sel.innerHTML = ""; sel.appendChild(new Option("（不接）", ""));
    if (line && line.eip_department_id) sel.appendChild(new Option(line.eip_department_name || String(line.eip_department_id), String(line.eip_department_id), true, true));
    if (window.I18N) $("pcLang").value = I18N.lang();
    $("pcErr").hidden = true; $("pcMsg").textContent = ""; dlg.hidden = false; $("pcName").focus();
    loadEip(line ? line.eip_department_id : null);
  }
  async function save() {
    const name = $("pcName").value.trim(); if (!name) { $("pcErr").textContent = "請填產線名稱"; $("pcErr").hidden = false; return; }
    const eip = $("pcEip").value;
    const d = await api("/api/lines/save", { line: { id: line ? line.id : "", name, factory: $("pcFactory").value.trim(), camera: $("pcCamera").value.trim(),
      enabled: true, table_region: line ? line.table_region : null, station_label: $("pcLabel").value.trim(), eip_department_type: Number($("pcType").value),
      eip_department_id: eip || null, eip_department_name: eip ? $("pcEip").selectedOptions[0].textContent.replace(/（\d+，清單裡沒有）$/, "") : "" } });
    if (!d.ok) { $("pcErr").textContent = d.error; $("pcErr").hidden = false; return; }
    dlg.hidden = true; mark(); document.dispatchEvent(new CustomEvent("pcset:saved"));
  }
  async function mark() {          // 還沒設好（沒有線或沒相機）：鍵變橘色提醒
    try { const c = await current(); const bad = !c.line || !c.line.has_camera; btn.classList.toggle("warn", bad); btn.title = bad ? "這台電腦還沒設好產線或相機，按這裡設定" : "這台電腦的產線設定（相機、EIP）"; } catch (e) {}
  }
  function init() {
    (document.querySelector(".side") || document.body).appendChild(btn); document.body.appendChild(dlg);
    btn.onclick = (e) => { e.preventDefault(); open(); }; $("pcCancel").onclick = () => { dlg.hidden = true; }; $("pcSave").onclick = save;
    $("pcLang").addEventListener("change", () => { if (window.I18N) I18N.setLang($("pcLang").value, true); });   // 語言選了馬上換、存在這台電腦，不用按儲存
    $("pcFactory").addEventListener("change", () => loadEip("")); $("pcType").addEventListener("change", () => loadEip(""));   // 換廠別／製程類別：原本選的線不在新清單，清掉重選
    document.addEventListener("keydown", (e) => { if (e.key === "Escape" && !dlg.hidden) dlg.hidden = true; });
    mark();
  }
  window.PcSet = { open };
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", init); else init();
})();
