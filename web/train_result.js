/* 訓練結果：新舊模型考同一份考卷（後端 model_exam），告訴使用者這次比上次變好、差不多還是變差。
   標記頁、包裝方式設定共用。TrainResult.summary(容器, 訓練狀態, 專案, 頁面動作) 畫一行摘要；TrainResult.open(...) 開結果視窗。
   狀態＝/api/train/state 的回傳（compare、candidate、installed）。變差時預設不換，「仍要換上新模型」打 /api/train/install。 */
(function () {
  const LABEL = { better: ["ok", "變好"], same: ["off", "差不多"], worse: ["no", "變差"], first: ["info", "第一次"], new: ["info", "新物品"],
                  skip: ["off", "沒比較"], noexam: ["off", "沒比較"] };
  const el = (tag, cls, text) => { const e = document.createElement(tag); if (cls) e.className = cls; if (text != null) e.textContent = text; return e; };
  const pct = (k, n) => (n ? Math.round(k * 100 / n) + "%" : "－");
  let dlg = null, cur = null;

  function summary(box, s, project, actions) {
    box.innerHTML = ""; const c = s && s.project === project && s.finished ? s.compare : null;
    if (!c) { box.hidden = true; return; }
    box.hidden = false; box.className = "trres";
    const [cls, t] = LABEL[c.verdict] || LABEL.skip;
    if (c.verdict === "first") box.append(el("span", "chip " + cls, t), el("span", null, "沒有上次可比"));
    else if (LABEL[c.verdict] && c.rows && c.rows.length) box.append(el("span", null, "這次比上次"), el("span", "chip " + cls, t));
    else box.append(el("span", "chip " + cls, t), el("span", null, c.reason || ""));
    if (c.rows && c.rows.length) {
      const a = el("a", null, "看結果"); a.tabIndex = 0; a.onclick = () => open(s, project, actions);
      a.onkeydown = (e) => { if (e.key === "Enter") open(s, project, actions); }; box.appendChild(a);
    }
  }

  function ensureDlg() {
    if (dlg) return dlg;
    dlg = el("div", "scrim"); dlg.hidden = true;
    dlg.innerHTML = '<div class="dialog" role="dialog" aria-modal="true" aria-labelledby="trTitle" style="height:auto;width:720px">'
      + '<div class="dt"><span class="mi mark">fact_check</span><h4 id="trTitle"></h4><span class="sum n" id="trWhen"></span></div>'
      + '<div class="dc" style="gap:12px"><div class="note" id="trBanner"></div><div class="note warn" id="trSaw" hidden></div>'
      + '<div style="overflow-x:auto"><table class="grid n" id="trGrid" style="width:100%"></table></div>'
      + '<div class="hint2" id="trExam" style="line-height:1.7"></div>'
      + '<details><summary style="cursor:pointer;color:var(--primary);font-size:13px">怎麼判好壞</summary><div class="hint2" id="trRule" style="line-height:1.7;padding-top:4px"></div></details>'
      + '<details><summary style="cursor:pointer;color:var(--primary);font-size:13px">最近幾次訓練</summary><div style="overflow-x:auto;padding-top:4px"><table class="grid n" id="trHist"></table></div></details>'
      + '</div><div class="da" id="trActs"></div></div>';
    document.body.appendChild(dlg);
    dlg.addEventListener("click", (e) => { if (e.target === dlg) close(); });
    document.addEventListener("keydown", (e) => { if (e.key === "Escape" && !dlg.hidden) close(); });
    return dlg;
  }
  function close() { if (dlg) dlg.hidden = true; }
  const q = (id) => dlg.querySelector("#" + id);

  function cell(k, n) { const d = el("span"); d.append(document.createTextNode(pct(k, n))); if (n) d.appendChild(el("small", "frac", `${k}/${n}`)); return d; }
  function pair(prev, now, n) {
    const td = el("td");
    if (!n) { td.textContent = "－"; return td; }
    if (prev != null) { td.appendChild(cell(prev, n)); td.appendChild(el("span", "arrow", "→")); }
    td.appendChild(cell(now, n)); return td;
  }

  function render(s, project, actions) {
    const c = s.compare; const first = c.verdict === "first";
    q("trTitle").textContent = "訓練結果　" + project; q("trWhen").textContent = c.at || "";
    const b = q("trBanner"); b.innerHTML = "";
    const forced = !!c.forced;
    b.className = "note " + (c.verdict === "better" ? "ok" : c.verdict === "worse" ? (forced ? "warn" : "danger") : "info");
    b.appendChild(EIP.mi({ better: "trending_up", same: "trending_flat", worse: "trending_down" }[c.verdict] || "info"));
    const txt = el("div");
    if (c.verdict === "better") txt.textContent = "比上次好，已換上新模型。上次的模型存成 best_prev_<時間>.pt。";
    else if (c.verdict === "same") txt.textContent = "跟上次差不多，已換上新模型。上次的模型存成 best_prev_<時間>.pt。";
    else if (first) txt.textContent = "第一次訓練，沒有上次可以比，已換上模型。下次訓練會拿這份成績來比。";
    else {
      txt.appendChild(el("div", null, forced || s.installed ? "比上次差，但已照你的選擇換上新模型。上次的模型存成 best_prev_<時間>.pt。"
        : "比上次差，還在用上次的模型。新模型存成 candidate.pt，沒有換上。"));
      const ul = el("ul"); ul.style.cssText = "margin:4px 0 0;padding-left:18px";
      for (const r of c.rows.filter((r) => r.verdict === "worse")) {
        if (r.d_hit <= -c.rules.hit_drop) ul.appendChild(el("li", null, `${r.name}：找到率 ${pct(r.hit_prev, r.n)} → ${pct(r.hit, r.n)}，掉 ${Math.round(-r.d_hit)} 點`));
        if (r.d_fp >= c.rules.fp_rise) ul.appendChild(el("li", null, `${r.name}：空桌誤報 ${r.fp_prev} 格 → ${r.fp} 格（${pct(r.fp_prev, r.empty_n)} → ${pct(r.fp, r.empty_n)}）`));
      }
      txt.appendChild(ul);
    }
    b.appendChild(txt);
    const saw = q("trSaw"); saw.hidden = !(c.prev_saw && c.prev_saw.length && !first);
    saw.textContent = saw.hidden ? "" : `上次的模型訓練時看過這幾項的考題：${c.prev_saw.join("、")}。這次的比較會偏向上次；下一次訓練起就公平。`;

    const g = q("trGrid"); g.innerHTML = "";
    const hr = el("tr"); for (const h of first ? ["名稱", "找到率", "空桌誤報"] : ["名稱", "找到率（上次 → 這次）", "空桌誤報（上次 → 這次）", "比較"]) hr.appendChild(el("th", null, h));
    const th = el("thead"); th.appendChild(hr); g.appendChild(th);
    const tb = el("tbody");
    for (const r of c.rows) {
      const tr = el("tr", r.verdict === "worse" ? "t-bad" : ""); tr.appendChild(el("td", null, r.name));
      tr.appendChild(pair(r.hit_prev, r.hit, r.n)); tr.appendChild(pair(r.fp_prev, r.fp, r.empty_n));
      if (!first) { const td = el("td"); const [cls, t] = LABEL[r.verdict] || LABEL.same; td.appendChild(el("span", "chip " + cls, t)); tr.appendChild(td); }
      tb.appendChild(tr);
    }
    g.appendChild(tb);

    q("trExam").textContent = `考卷：${c.exam_created_at || "這次"} 定的，每個物品取最後一段框，共 ${c.questions} 格，加空桌 ${c.empty_n} 格。這些畫面不拿去訓練，新舊模型考同一份。`
      + (c.new_exam_items && c.new_exam_items.length ? `${c.new_exam_items.join("、")} 是後來才出題的。` : "")
      + (c.prev_trained_at ? `上次的模型：${c.prev_trained_at} 訓練。` : "")
      + (c.empty_n ? "" : "沒有空桌考題（空桌畫面少於 2 格），誤報不比。");
    q("trRule").textContent = `每個物品比兩個數字。找到率：考卷裡有框的畫面，模型在同一個位置認出同一個物品的比例。空桌誤報：空桌畫面裡，模型說看到這個物品的比例。`
      + `任一物品找到率掉 ${c.rules.hit_drop} 點以上，或空桌誤報升 ${c.rules.fp_rise} 點以上，整次算變差。沒有變差、而且至少一項找到率升 ${c.rules.hit_drop} 點以上或誤報降 ${c.rules.fp_rise} 點以上，算變好。其他算差不多。`
      + `新物品上次沒有，只顯示這次的成績，不拿來比。這兩個門檻是先訂的數字，還沒用現場資料驗證；考題 20 格時，差 1 格就差 5 點。`;

    const hg = q("trHist"); hg.innerHTML = "";
    const h2 = el("tr"); for (const h of ["訓練時間", "比上一次", "有沒有換上"]) h2.appendChild(el("th", null, h));
    const hh = el("thead"); hh.appendChild(h2); hg.appendChild(hh);
    const hb = el("tbody");
    for (const h of c.history || []) {
      const tr = el("tr"); tr.appendChild(el("td", null, h.at)); const td = el("td"); const [cls, t] = LABEL[h.verdict] || LABEL.skip;
      td.appendChild(el("span", "chip " + cls, t)); tr.appendChild(td);
      tr.appendChild(el("td", null, h.installed ? (h.forced ? "已換上（自己選的）" : "已換上") : "沒換上")); hb.appendChild(tr);
    }
    hg.appendChild(hb);
    renderActs(s, project, actions, false);
  }

  function renderActs(s, project, actions, confirming) {
    const a = q("trActs"); a.innerHTML = "";
    if (s.compare.verdict === "worse" && s.candidate) {
      if (confirming) {
        a.appendChild(el("span", null, "確定要換上比較差的模型？"));
        const box = el("div"); box.style.cssText = "display:flex;gap:8px";
        const no = el("button", "btn btn-cancel", "取消"); no.onclick = () => renderActs(s, project, actions, false);
        const yes = el("button", "btn btn-danger raised", "換上");
        yes.onclick = async () => {
          yes.disabled = true;
          const r = await fetch("/api/train/install", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ project }) }).then((x) => x.json()).catch((e) => ({ ok: false, error: String(e) }));
          if (!r.ok) { a.innerHTML = ""; a.appendChild(el("span", "err", r.error || "換上失敗")); return; }
          cur = r; render(r, project, actions); if (actions && actions.onChange) actions.onChange(r);
        };
        box.append(no, yes); a.appendChild(box); return;
      }
      const force = el("button", "btn btn-cancel", "仍要換上新模型"); force.style.color = "var(--danger)"; force.onclick = () => renderActs(s, project, actions, true);
      const keep = el("button", "btn btn-primary raised", "保留上次的模型"); keep.onclick = close;
      a.append(force, keep); return;
    }
    const cl = el("button", "btn btn-cancel", "關閉"); cl.onclick = close; a.appendChild(cl);
    if (actions && actions.next) { const n = el("button", "btn btn-secondary raised", actions.next.label); n.onclick = () => { close(); actions.next.run(); }; a.appendChild(n); }
    else a.appendChild(el("span"));
  }

  function open(s, project, actions) {
    if (!s || !s.compare || !s.compare.rows || !s.compare.rows.length) return;
    ensureDlg(); cur = s; render(s, project, actions); dlg.hidden = false;
  }
  window.TrainResult = { summary, open, close };
})();
