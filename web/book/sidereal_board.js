/** Quenya right-leaf: assemble 42 × sidereal month vs π × year. */
(function () {
  const MONTH = 27.32;
  const YEAR = 365.25;
  const PI = Math.PI;

  function render(host) {
    host.innerHTML = `
      <div class="sidereal view-sidereal">
        <h2>Sidereal board · folio 42</h2>
        <div class="row">
          <label for="n-months">N months</label>
          <input id="n-months" type="number" step="1" min="1" value="42">
        </div>
        <div class="row">
          <label for="year-len">year length (d)</label>
          <input id="year-len" type="number" step="0.01" min="1" value="365.25">
        </div>
        <div class="row">
          <label>sidereal month</label>
          <span>${MONTH} d (fixed)</span>
        </div>
        <div class="out" id="sidereal-out"></div>
        <p class="stub" style="margin-top:14px;opacity:0.65;font-size:11px;line-height:1.5">
          Find when N · 27.32 approaches π · year. No banner spoilers — the board is the pedagogy.
        </p>
      </div>`;
    const nEl = host.querySelector("#n-months");
    const yEl = host.querySelector("#year-len");
    const out = host.querySelector("#sidereal-out");
    const tick = () => {
      const n = Number(nEl.value) || 0;
      const y = Number(yEl.value) || YEAR;
      const left = n * MONTH;
      const right = PI * y;
      const delta = Math.abs(left - right);
      const hit = delta < 0.5;
      out.innerHTML = `
        N · 27.32 = <strong>${left.toFixed(4)}</strong> d<br>
        π · year = <strong>${right.toFixed(4)}</strong> d<br>
        |Δ| = <strong class="${hit ? "hit" : ""}">${delta.toFixed(4)}</strong>
        ${hit ? " · near" : ""}`;
    };
    nEl.addEventListener("input", tick);
    yEl.addEventListener("input", tick);
    tick();
  }

  window.renderSiderealBoard = render;
})();
