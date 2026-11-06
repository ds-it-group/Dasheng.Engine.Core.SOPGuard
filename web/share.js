/* 共用硬碟（NAS）對話框：載入到這台電腦／上傳這台電腦的專案／看版本、退回。後端 shared_store.py（/api/share/*）。
   共用硬碟上每個專案：v1、v2…版本資料夾只增不改，current.txt 指「目前版本」；載入不用重訓（模型與框一起過來）。
   由包裝明細頁（methods.html）載入；用到 window.sopgMethods（toast、reload）與 window.sopgHead（表頭）。 */
(function () {
  const $ = (id) => document.getElementById(id);
  const el = (tag, cls, text) => { const e = document.createElement(tag); if (cls) e.className = cls; if (text != null) e.textContent = text; return e; };
  const api = async (path, body) => { const r = await fetch(path, body ? { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body) } : {}); return r.json(); };
  const M = () => window.sopgMethods;
  let data = null, tab = "load", openVer = null;
  const ST = { none: ["off", "本機沒有"], same: ["ok", "同版本"], shared_newer: ["warn", "共用硬碟有新版"], local_changed: ["warn", "本機改過，還沒上傳"],
               other: ["off", "本機不是目前版本"], not_on_share: ["off", "共用硬碟沒有"] };
  const utc = (s) => { if (!s) return ""; const d = new Date(s); if (isNaN(d)) return s; const p = (x) => String(x).padStart(2, "0"); return `${d.getMonth() + 1}/${d.getDate()} ${p(d.getHours())}:${p(d.getMinutes())}`; };
  const vtxt = (v) => (v == null ? "–" : "v" + v);

  function build() {
    if ($("shDlg")) return;
    const s = el("div", "scrim"); s.id = "shDlg"; s.hidden = true;
    s.innerHTML = '<div class="dialog large" role="dialog" aria-modal="true" aria-labelledby="shTitle">'
      + '<div class="dt"><span class="mi mark">cloud</span><h4 id="shTitle">共用硬碟</h4><span class="sum n" id="shSum"></span></div>'
      + '<div class="dc" style="gap:12px">'
      + '<div class="frow" style="align-items:flex-end"><div class="fld w320"><label for="shRoot">共用硬碟資料夾（這台電腦記住，之後不用再填）</label><input id="shRoot" placeholder="例如 \\\\NAS01\\SOP-Guard\\projects"></div>'
      + '<button class="btn btn-secondary raised" id="shSaveRoot" style="height:30px">儲存並讀取</button>'
      + '<label style="display:inline-flex;gap:6px;align-items:center;padding-bottom:6px"><input type="checkbox" id="shVideo"> 連示範影片一起（要在別台補框或訓練才需要）</label></div>'
      + '<div class="tabs" role="tablist" id="shTabs"><button data-stab="load" class="on">載入到這台電腦</button><button data-stab="up">上傳這台電腦的專案</button></div>'
      + '<div id="shPaneLoad"><div class="gridwrap" style="min-height:160px;max-height:46vh"><table class="grid" id="shGrid"></table></div>'
      + '<div class="note info">載入＝把共用硬碟上那一版的設定、步驟、框、辨識模型複製到這台電腦，不用重訓。載入後到監控畫面「操作 → 換包裝方式」就能選。共用硬碟的檔案不會被改。</div></div>'
      + '<div id="shPaneUp" hidden><div class="frow"><div class="fld" style="width:100%"><label for="shNote">這版改了什麼（選填，寫進版本紀錄）</label><input id="shNote" placeholder="例如 加了白鞋的框"></div></div>'
      + '<div class="gridwrap" style="min-height:160px;max-height:40vh"><table class="grid" id="upGrid"></table></div>'
      + '<div class="note info">上傳＝在共用硬碟新增一版（舊版都留著，不會被蓋掉），並設成目前版本。別人在你載入之後又傳過時，會先問要不要設成目前版本。沒有模型的專案也能上傳，讓別台電腦拿去訓練。</div></div>'
      + '<div class="note warn" id="shConfirm" hidden style="align-items:center;gap:10px"><span id="shConfirmText" style="flex:1"></span><button class="btn btn-primary raised" id="shConfirmOk" style="height:28px">設成目前版本</button><button class="btn btn-cancel" id="shConfirmNo" style="height:28px">先不要</button></div>'
      + '<div class="note info" id="shProgress" hidden></div><div class="note danger" id="shErr" hidden></div>'
      + '</div><div class="da"><button class="btn btn-cancel" id="shClose">關閉</button><span></span></div></div>';
    document.body.appendChild(s);
    $("shClose").onclick = () => { s.hidden = true; };
    s.addEventListener("click", (e) => { if (e.target === s) s.hidden = true; });
    document.addEventListener("keydown", (e) => { if (e.key === "Escape") s.hidden = true; });
    $("shTabs").onclick = (ev) => { const b = ev.target.closest("[data-stab]"); if (b) setTab(b.dataset.stab); };
    $("shSaveRoot").onclick = async () => {
      const r = await api("/api/share/root", { path: $("shRoot").value });
      if (!r.ok) { err(r.error); return; } M().toast("已記住共用硬碟資料夾"); refresh();
    };
  }
  const err = (t) => { $("shErr").textContent = t || ""; $("shErr").hidden = !t; };
  const busy = (t) => { $("shProgress").textContent = t || ""; $("shProgress").hidden = !t; };
  function setTab(v) {
    tab = v; document.querySelectorAll("#shTabs button").forEach((b) => b.classList.toggle("on", b.dataset.stab === v));
    $("shPaneLoad").hidden = v !== "load"; $("shPaneUp").hidden = v !== "up"; $("shConfirm").hidden = true; render();
  }
  async function refresh() {
    data = await api("/api/share/list"); $("shRoot").value = data.root || "";
    err(data.error || ""); render();
    if (window.sopgShareRefresh) window.sopgShareRefresh(data);
  }
  function chip(st) { const [c, t] = ST[st] || ["off", st]; return el("span", "chip " + c, t); }
  function render() {
    if (!data) return;
    const shared = data.shared || [], local = data.local || [];
    $("shSum").textContent = data.root ? `共用硬碟上有 ${shared.length} 個專案` : "還沒設定共用硬碟資料夾";
    if (tab === "load") renderLoad(shared); else renderUp(local);
  }
  function renderLoad(rows) {
    const t = $("shGrid"); t.innerHTML = "";
    window.sopgHead(t, [["型體", 100, "pinL"], ["地區", 80], ["專案", 140], ["目前版本", 160], ["模型訓練", 130], ["步驟", 50, "r"], ["大小", 70, "r"], ["本機", 170], ["操作", 100, "pinR c"]], 2, 0, null);
    const tb = el("tbody");
    for (const r of rows) {
      const tr = el("tr", r.status === "shared_newer" ? "t-warn" : "");
      const cur = r.versions.find((v) => v.version === r.current) || r.versions[0] || {};
      [[r.style || "（未設定）", "pinL"], [r.region || ""], [r.name], [`${vtxt(r.current)}・${utc(cur.uploaded_at)}・${cur.by || ""}`, "n"], [r.model_trained_at || "還沒訓練", "n"],
       [String(r.steps), "r n"], [r.size_mb + " MB", "r n"]].forEach(([v, c]) => tr.appendChild(el("td", c || "", v)));
      const st = el("td"); st.appendChild(chip(r.status)); if (r.local_version != null) st.appendChild(el("small", null, `　本機 ${vtxt(r.local_version)}`)); tr.appendChild(st);
      const op = el("td", "pinR c"), box = el("span", "ops");
      if (r.status !== "same") box.appendChild(EIP.iconBtn(r.status === "none" ? "file_download" : "sync", "c-edit", r.status === "none" ? "載入目前版本到這台電腦" : "用共用硬碟的目前版本換掉本機的", () => doLoad(r, null)));
      box.appendChild(EIP.iconBtn("history", "c-sec", "看所有版本（載入指定版本、設成目前版本）", () => { openVer = openVer === r.name ? null : r.name; render(); }));
      op.appendChild(box); tr.appendChild(op); tb.appendChild(tr);
      if (openVer === r.name) {
        for (const v of r.versions) {
          const vr = el("tr"); vr.style.background = "var(--grid-head)";
          const td = el("td", "pinL"); td.colSpan = 8;
          td.textContent = `　${vtxt(v.version)}${v.version === r.current ? "（目前版本）" : ""}　${utc(v.uploaded_at)}　${v.by || ""}　模型 ${v.model_trained_at || "–"}　${v.note || ""}`;
          vr.appendChild(td);
          const o2 = el("td", "pinR c"), b2 = el("span", "ops");
          b2.appendChild(EIP.iconBtn("file_download", "c-edit", `只有這台電腦載入 ${vtxt(v.version)}（試跑用，不改目前版本）`, () => doLoad(r, v.version)));
          if (v.version !== r.current) b2.appendChild(EIP.iconBtn("flag", "c-warn", `把 ${vtxt(v.version)} 設成目前版本（大家之後載入這一版）`, () => setCurrent(r, v.version)));
          o2.appendChild(b2); vr.appendChild(o2); tb.appendChild(vr);
        }
      }
    }
    if (!rows.length) { const tr = el("tr", "empty"), td = el("td", null, data.root ? "共用硬碟上還沒有專案" : "先在上面填共用硬碟資料夾"); td.colSpan = 9; tr.appendChild(td); tb.appendChild(tr); }
    t.appendChild(tb);
  }
  function renderUp(rows) {
    const t = $("upGrid"); t.innerHTML = "";
    window.sopgHead(t, [["型體", 100, "pinL"], ["地區", 80], ["專案", 140], ["本機版本", 80], ["共用硬碟目前", 100], ["模型", 70, "c"], ["狀態", 160], ["操作", 80, "pinR c"]], 2, 0, null);
    const tb = el("tbody");
    for (const r of rows) {
      const tr = el("tr", r.status === "local_changed" ? "t-warn" : "");
      [[r.style || "（未設定）", "pinL"], [r.region || ""], [r.name], [vtxt(r.local_version), "n"], [vtxt(r.current), "n"], [r.has_model ? "有" : "沒有", "c"]].forEach(([v, c]) => tr.appendChild(el("td", c || "", v)));
      const st = el("td"); st.appendChild(chip(r.status)); tr.appendChild(st);
      const op = el("td", "pinR c");
      if (r.status !== "same") op.appendChild(EIP.iconBtn("cloud_upload", "c-edit", "上傳成共用硬碟的新版本", () => doUpload(r)));
      tr.appendChild(op); tb.appendChild(tr);
    }
    if (!rows.length) { const tr = el("tr", "empty"), td = el("td", null, "這台電腦還沒有專案"); td.colSpan = 8; tr.appendChild(td); tb.appendChild(tr); }
    t.appendChild(tb);
  }
  async function doLoad(r, version) {
    err(""); busy(`正在複製「${r.name}」${version ? " " + vtxt(version) : "目前版本"}…`);
    const d = await api("/api/share/load", { name: r.name, version, video: $("shVideo").checked });
    busy("");
    if (!d.ok) { err(d.error); return; }
    const more = d.loaded.length > 1 ? `（連同參考的模型：${d.loaded.slice(1).map((x) => x.name).join("、")}）` : "";
    M().toast(`已載入「${r.name}」${vtxt(d.version)}${more}。到監控畫面「操作 → 換包裝方式」就能選`);
    await refresh(); M().reload();
  }
  async function doUpload(r, confirmed) {
    err(""); $("shConfirm").hidden = true; busy(`正在上傳「${r.name}」…`);
    const d = await api("/api/share/upload", { name: r.name, note: $("shNote").value, video: $("shVideo").checked, publish: true });
    busy("");
    if (!d.ok) { err(d.error); return; }
    if (d.needs_confirm) {
      $("shConfirmText").textContent = `已存成 ${vtxt(d.version)}。但共用硬碟目前是 ${vtxt(d.current)}，是你載入之後別人傳的。要把你的 ${vtxt(d.version)} 設成目前版本嗎？選「先不要」就只存著，大家還是載入 ${vtxt(d.current)}。`;
      $("shConfirm").hidden = false;
      $("shConfirmOk").onclick = async () => { await setCurrent({ name: r.name }, d.version); $("shConfirm").hidden = true; };
      $("shConfirmNo").onclick = () => { $("shConfirm").hidden = true; };
    } else M().toast(`已上傳「${r.name}」成 ${vtxt(d.version)}，並設成目前版本`);
    $("shNote").value = ""; await refresh(); M().reload();
  }
  async function setCurrent(r, v) {
    const d = await api("/api/share/current", { name: r.name, version: v });
    if (!d.ok) { err(d.error); return; }
    M().toast(`「${r.name}」的目前版本改成 ${vtxt(v)}`); await refresh();
  }
  window.sopgShare = { open: async (t) => { build(); $("shDlg").hidden = false; setTab(t || "load"); await refresh(); }, refresh: async () => { build(); await refresh(); } };
})();
