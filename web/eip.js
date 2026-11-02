/* SOP-Guard 網頁共用小工具：圖示、grid 欄寬可拖拉並記住（每台瀏覽器各自記，存在 localStorage）、側欄收合。 */
(function () {
  const EIP = {};
  EIP.mi = function (name, cls) { const s = document.createElement("span"); s.className = "mi" + (cls ? " " + cls : ""); s.textContent = name; s.setAttribute("aria-hidden", "true"); return s; };
  /* 列操作鈕：圖示＋tooltip（規範 §3.11：同一動作同一圖示同一顏色） */
  EIP.iconBtn = function (icon, cls, tip, onClick) {
    const b = document.createElement("button"); b.className = "ib " + (cls || ""); b.title = tip; b.setAttribute("aria-label", tip);
    b.appendChild(EIP.mi(icon)); if (onClick) b.onclick = onClick; return b;
  };
  function load(key) { try { return JSON.parse(localStorage.getItem("sopg-cols-" + key) || "null") || {}; } catch (e) { return {}; } }
  function save(key, v) { try { localStorage.setItem("sopg-cols-" + key, JSON.stringify(v)); } catch (e) {} }
  /* 欄寬：表頭第一列每一格右緣可拖拉；放開就記住，下次 render 自動套回（規範 §4.8 欄位狀態持久化，這裡只做欄寬） */
  EIP.resizable = function (table, key) {
    const row = table.querySelector("thead tr"); if (!row) return;
    const widths = load(key);
    [...row.children].forEach((th, i) => {
      const id = (th.textContent || "").trim() || "#" + i;
      if (widths[id]) { th.style.width = widths[id] + "px"; th.style.minWidth = widths[id] + "px"; th.style.maxWidth = widths[id] + "px"; }
      if (th.classList.contains("pinR") || !th.textContent.trim()) return;
      const h = document.createElement("span"); h.className = "rz"; h.title = "拖拉調整欄寬（雙擊恢復預設）";
      h.onpointerdown = (ev) => {
        ev.preventDefault(); ev.stopPropagation(); h.setPointerCapture(ev.pointerId); h.classList.add("on");
        const x0 = ev.clientX, w0 = th.getBoundingClientRect().width;
        h.onpointermove = (e) => { const w = Math.max(40, Math.round(w0 + e.clientX - x0)); th.style.width = th.style.minWidth = th.style.maxWidth = w + "px"; };
        h.onpointerup = () => { h.onpointermove = null; h.classList.remove("on"); const v = load(key); v[id] = Math.round(th.getBoundingClientRect().width); save(key, v); };
      };
      h.ondblclick = (ev) => { ev.stopPropagation(); const v = load(key); delete v[id]; save(key, v); th.style.width = th.style.maxWidth = ""; th.style.minWidth = ""; };
      th.appendChild(h);
    });
  };
  EIP.compactToggle = function (btn) {
    try { if (localStorage.getItem("sopg-compact") === "1") document.body.classList.add("compact"); } catch (e) {}
    if (btn) btn.onclick = () => { document.body.classList.toggle("compact"); try { localStorage.setItem("sopg-compact", document.body.classList.contains("compact") ? "1" : "0"); } catch (e) {} };
  };
  window.EIP = EIP;
})();
