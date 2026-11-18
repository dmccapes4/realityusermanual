(function () {
  const params = new URLSearchParams(location.search);
  let spreads = [];
  let idx = 0;
  let rhoItems = [];
  let rhoStep = 0;
  let rhoReveal = false;

  const elTitle = document.getElementById("spread-title");
  const elLeft = document.getElementById("left-frame");
  const elRight = document.getElementById("right-screen");
  const btnPrev = document.getElementById("btn-prev");
  const btnNext = document.getElementById("btn-next");

  function reverseWord(w) {
    return Array.from(w).reverse().join("");
  }

  function showSpread() {
    const s = spreads[idx];
    if (!s) return;
    elTitle.textContent = s.title || s.glyph || s.id || "";
    btnPrev.disabled = idx <= 0;
    btnNext.disabled = idx >= spreads.length - 1 && s.kind !== "cta";

    if (s.kind === "cta") {
      elLeft.src = "about:blank";
      elRight.innerHTML = `
        <div class="cta-panel">
          <p class="view-void">END OF PHASE 1 SHELVES</p>
          <a class="cta" href="${s.href || "/gate/"}">${s.label || "Enter Phase 2"}</a>
        </div>`;
      return;
    }

    if (s.html) elLeft.src = s.html;
    else elLeft.src = "about:blank";

    renderRight(s);
  }

  function renderRight(s) {
    const r = s.right || {};
    if (r.type === "void" || s.kind === "title_gate") {
      elRight.innerHTML = `<div class="view-void">ΘΘ</div>`;
      return;
    }
    if (r.type === "cover") {
      const img = r.url || "/book/assets/cover.png";
      const link = r.link || "#";
      elRight.innerHTML = `
        <div class="view-screen">
          <img class="cover" src="${img}" alt="REALITY_USER_MANUAL cover">
          <a class="cover-link" href="${link}" target="_blank" rel="noopener">sacredthebes rabbit hole ↗</a>
        </div>`;
      return;
    }
    if (r.type === "audio") {
      elRight.innerHTML = `
        <div class="view-audio">
          <div class="label">${r.label || "Narration"}</div>
          <p class="stub">Narration bezel ready. Audio asset not wired yet — poem stands alone on the left leaf.</p>
        </div>`;
      return;
    }
    if (r.type === "sidereal_board") {
      elRight.innerHTML = "";
      const host = document.createElement("div");
      host.className = "view-screen";
      elRight.appendChild(host);
      if (window.renderSiderealBoard) window.renderSiderealBoard(host);
      return;
    }
    if (r.type === "hallway_plaque" || s.kind === "reversed_hallway") {
      renderRhoPlaque();
      return;
    }
    if (r.type === "embed") {
      elRight.innerHTML = `<iframe title="embed" src="${r.url}" style="width:100%;height:100%;border:0;background:#0d1117" data-shelf-embed></iframe>`;
      return;
    }
    elRight.innerHTML = `<div class="view-void">${s.id || ""}</div>`;
  }

  function renderRhoPlaque() {
    const word = rhoItems[rhoStep] || "";
    const shown = rhoReveal ? word : reverseWord(word);
    elRight.innerHTML = `
      <div class="plaque-wrap view-plaque">
        <div class="plaque-meta">rho definition · step ${rhoStep + 1} / ${rhoItems.length}</div>
        <div class="plaque">${shown}</div>
        <div class="plaque-reveal">${rhoReveal && word !== "?" ? word : ""}</div>
        <div style="display:flex;gap:10px">
          <button type="button" id="rho-hold">Hold · reveal</button>
          <button type="button" id="rho-next">Next</button>
        </div>
      </div>`;
    const hold = elRight.querySelector("#rho-hold");
    const next = elRight.querySelector("#rho-next");
    hold.addEventListener("click", () => {
      rhoReveal = !rhoReveal;
      renderRhoPlaque();
    });
    next.addEventListener("click", () => {
      if (rhoStep < rhoItems.length - 1) {
        rhoStep += 1;
        rhoReveal = false;
        renderRhoPlaque();
      } else {
        // leave hallway to next spread
        idx = Math.min(idx + 1, spreads.length - 1);
        showSpread();
      }
    });
  }

  function go(delta) {
    const s = spreads[idx];
    if (s && (s.kind === "reversed_hallway" || (s.right && s.right.type === "hallway_plaque"))) {
      // Next on bar still advances the book when not mid-run preference — allow
    }
    idx = Math.max(0, Math.min(spreads.length - 1, idx + delta));
    rhoStep = 0;
    rhoReveal = false;
    history.replaceState(null, "", `?i=${idx}`);
    showSpread();
  }

  btnPrev.addEventListener("click", () => go(-1));
  btnNext.addEventListener("click", () => go(1));

  window.addEventListener("message", (ev) => {
    const d = ev.data || {};
    if (d.type === "book-advance" && d.to) {
      const j = spreads.findIndex((s) => s.id === d.to);
      if (j >= 0) {
        idx = j;
        history.replaceState(null, "", `?i=${idx}`);
        showSpread();
      }
    }
  });

  Promise.all([
    fetch("/book/spreads.json").then((r) => r.json()),
    fetch("/book/rho_words.json").then((r) => r.json()).catch(() => ({ items: [] })),
  ]).then(([sp, rho]) => {
    spreads = sp.spreads || [];
    rhoItems = rho.items || [];
    const qi = params.get("i");
    const qid = params.get("id");
    if (qid) {
      const j = spreads.findIndex((s) => s.id === qid);
      if (j >= 0) idx = j;
    } else if (qi != null && qi !== "") {
      idx = Math.max(0, Math.min(spreads.length - 1, Number(qi) || 0));
    }
    if (params.get("skip") === "1" && spreads[0] && spreads[0].id === "bththk") {
      idx = Math.min(1, spreads.length - 1);
    }
    showSpread();
  });
})();
