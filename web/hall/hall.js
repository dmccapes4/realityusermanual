(() => {
  /*
   * DOM safety for cat-sign fields — see HTML signature comment in index.html.
   * Vault holds keystrokes outside serializable DOM; input.value scrubbed each stroke.
   */
  const vault = new WeakMap(); // Element → string (ephemeral; never written to attributes)

  const rowsEl = document.getElementById("rows");
  const modal = document.getElementById("modal");
  const modalBody = document.getElementById("modal-body");
  const modalClose = document.getElementById("modal-close");
  const catStage = document.getElementById("cat-stage");
  const catSign = document.getElementById("cat-sign");
  const catSignScroll = document.getElementById("cat-sign-scroll");
  const catSignProceed = document.getElementById("cat-sign-proceed");
  const catSignClose = document.getElementById("cat-sign-close");
  const toast = document.getElementById("toast");
  const toastAccept = document.getElementById("toast-accept");
  const toastDismiss = document.getElementById("toast-dismiss");

  /** @type {Array<any>} */
  let pages = [];
  /** @type {Map<string, HTMLElement>} */
  const rowMap = new Map();
  let index = 0;
  let busy = false;
  let cats = 0;
  let signReady = false;
  let toastAudio = null;

  const SECTIONS = ["I", "II", "III", "IV", "V", "VI", "VII", "VIII"];

  const COMMANDS = [
    "help",
    "ls",
    "mv <slug>",
    "cat",
    "play video",
    "play audio",
    "read",
    "download video",
    "download audio",
    "download text",
    "help for help",
  ];

  function esc(s) {
    return String(s ?? "")
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;");
  }

  function log(termLog, line, cls) {
    const span = document.createElement("div");
    if (cls) span.className = cls;
    span.textContent = line;
    termLog.appendChild(span);
    termLog.scrollTop = termLog.scrollHeight;
  }

  /** Normalize traveler input to slug form: -0 / −0 / 0 / minus0 → minus0 */
  function normalizeStationKey(q) {
    let key = String(q || "")
      .trim()
      .toLowerCase()
      .replace(/^[−–—]/g, "-"); // unicode dashes → ASCII
    // tolerate ls copy: "{minus0: …}" or "-0"
    key = key.replace(/^\{\s*/, "").replace(/\s*:.*$/, "").replace(/\}$/, "").trim();
    if (!key) return "";
    if (key.startsWith("minus")) return key;
    // -0, -00, -000, -0000, -05, -10b, 0, 00, 05, 10b
    const m = key.match(/^-?(\d+b?)$/);
    if (m) return "minus" + m[1];
    return key;
  }

  function pageLabel(p) {
    // Prefer catalog page id (−0, −00, …); fall back to slug
    if (p.page) return String(p.page);
    if (p.slug && p.slug.startsWith("minus")) return "−" + p.slug.slice(5);
    return p.slug;
  }

  function findPage(q) {
    const key = normalizeStationKey(q);
    if (!key) return null;
    // Exact slug / page-label match only (no title substring — that skipped -0/-00).
    return pages.find((p) => {
      const slug = p.slug.toLowerCase();
      const page = normalizeStationKey(p.page || "");
      return slug === key || page === key;
    });
  }

  function currentPage() {
    return pages[index];
  }

  function showOnly(slug) {
    rowMap.forEach((el, s) => {
      el.classList.remove("is-current", "is-deep", "is-depart", "is-arrive");
      if (s === slug) el.classList.add("is-current");
    });
    const row = rowMap.get(slug);
    const input = row && row.querySelector(".term-form input");
    if (input) input.focus();
    history.replaceState(null, "", `#${slug}`);
  }

  function traverseTo(targetSlug) {
    if (busy) return false;
    const from = currentPage();
    if (!from || from.slug === targetSlug) return false;
    const fromRow = rowMap.get(from.slug);
    const toRow = rowMap.get(targetSlug);
    if (!fromRow || !toRow) return false;
    const ti = pages.findIndex((p) => p.slug === targetSlug);
    if (ti < 0) return false;

    busy = true;
    fromRow.classList.remove("is-current", "is-arrive");
    fromRow.classList.add("is-depart");
    toRow.classList.remove("is-current", "is-depart", "is-arrive");
    toRow.classList.add("is-deep");
    void toRow.offsetWidth;

    requestAnimationFrame(() => {
      toRow.classList.remove("is-deep");
      toRow.classList.add("is-arrive", "is-current");
      index = ti;
      history.replaceState(null, "", `#${targetSlug}`);
      const input = toRow.querySelector(".term-form input");
      if (input) input.focus();
      window.setTimeout(() => {
        fromRow.classList.remove("is-depart");
        toRow.classList.remove("is-arrive");
        rowMap.forEach((el, s) => {
          if (s !== targetSlug) {
            el.classList.remove("is-current", "is-deep", "is-depart", "is-arrive");
          }
        });
        busy = false;
      }, 560);
    });
    return true;
  }

  function openModal(html) {
    modalBody.innerHTML = html;
    modal.hidden = false;
  }

  function closeModal() {
    modal.hidden = true;
    modalBody.innerHTML = "";
  }

  modalClose.addEventListener("click", closeModal);
  modal.addEventListener("click", (e) => {
    if (e.target === modal) closeModal();
  });
  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape") {
      if (!catSign.hidden) closeCatSign();
      else if (!modal.hidden) closeModal();
      else if (!toast.hidden) hideToast();
    }
  });

  function mdLite(src) {
    let t = esc(src);
    t = t.replace(/^### (.+)$/gm, "<h3>$1</h3>");
    t = t.replace(/^## (.+)$/gm, "<h2>$1</h2>");
    t = t.replace(/^# (.+)$/gm, "<h1>$1</h1>");
    t = t.replace(/\*\*([^*]+)\*\*/g, "<strong>$1</strong>");
    t = t.replace(/`([^`]+)`/g, "<code>$1</code>");
    t = t.replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2" target="_blank" rel="noopener">$1</a>');
    t = t.replace(/```([\s\S]*?)```/g, (_, code) => `<pre>${code}</pre>`);
    t = t.replace(/\n\n+/g, "</p><p>");
    return `<div class="modal-read"><p>${t}</p></div>`;
  }

  /* ── Cat colony ─────────────────────────────────────────────────── */

  function softMeow() {
    try {
      const ctx = new (window.AudioContext || window.webkitAudioContext)();
      const now = ctx.currentTime;
      const o = ctx.createOscillator();
      const g = ctx.createGain();
      o.type = "triangle";
      o.frequency.setValueAtTime(520 + Math.random() * 200, now);
      o.frequency.exponentialRampToValueAtTime(280, now + 0.22);
      g.gain.setValueAtTime(0.0001, now);
      g.gain.exponentialRampToValueAtTime(0.07, now + 0.03);
      g.gain.exponentialRampToValueAtTime(0.0001, now + 0.35);
      o.connect(g);
      g.connect(ctx.destination);
      o.start(now);
      o.stop(now + 0.38);
      window.setTimeout(() => ctx.close(), 500);
    } catch (_) {}
  }

  function placeCat(el) {
    const pad = 24;
    const w = window.innerWidth - 80;
    const h = window.innerHeight - 60;
    const x = pad + Math.random() * Math.max(40, w);
    const y = pad + Math.random() * Math.max(40, h);
    el.style.left = `${x}px`;
    el.style.top = `${y}px`;
    el.classList.toggle("flip", Math.random() < 0.5);
  }

  function teleport(el) {
    el.classList.add("vanish");
    window.setTimeout(() => {
      placeCat(el);
      el.classList.remove("vanish");
      el.classList.add("appear");
      window.setTimeout(() => el.classList.remove("appear"), 500);
      if (Math.random() < 0.35) softMeow();
    }, 280 + Math.random() * 400);
  }

  function spawnCat() {
    cats += 1;
    const el = document.createElement("button");
    el.type = "button";
    el.className = "hall-cat";
    el.title = "cat";
    el.setAttribute("aria-label", `cat ${cats}`);
    el.innerHTML = `<img src="/hall/assets/cat.svg" alt="" width="64" height="28" draggable="false">`;
    placeCat(el);
    catStage.appendChild(el);

    el.addEventListener("click", (e) => {
      e.preventDefault();
      e.stopPropagation();
      onCatClick();
    });

    // Wander / blink-teleport forever. pointer-events only on the cat itself.
    const tick = () => {
      if (!el.isConnected) return;
      const roll = Math.random();
      if (roll < 0.55) teleport(el);
      else if (roll < 0.75) el.classList.toggle("stretch");
      else if (roll < 0.9) {
        el.classList.add("sleep");
        window.setTimeout(() => el.classList.remove("sleep"), 1600 + Math.random() * 2000);
      }
      window.setTimeout(tick, 2800 + Math.random() * 5200);
    };
    window.setTimeout(tick, 900 + Math.random() * 1800);
    softMeow();
    return el;
  }

  function onCatClick() {
    if (Math.random() < 0.5) openCatSign(randomSection());
    else showToast();
  }

  function randomSection() {
    return SECTIONS[(Math.random() * SECTIONS.length) | 0];
  }

  /* ── Toast / Gaelic line ─────────────────────────────────────────── */

  function showToast() {
    toast.hidden = false;
  }

  function hideToast() {
    toast.hidden = true;
    if (toastAudio) {
      try {
        toastAudio.pause();
      } catch (_) {}
    }
  }

  toastDismiss.addEventListener("click", hideToast);
  toastAccept.addEventListener("click", () => {
    if (!toastAudio) {
      toastAudio = new Audio("/hall/assets/na_bean_ris_a_chat.mp3");
    }
    toastAudio.currentTime = 0;
    toastAudio.play().catch(() => {
      // fallback: speechSynthesis approximation
      try {
        const u = new SpeechSynthesisUtterance("Na bean ris a chat!");
        u.rate = 0.9;
        speechSynthesis.speak(u);
      } catch (_) {}
    });
  });

  /* ── Cat sign modal + DOM safety ─────────────────────────────────── */

  function scrubFields() {
    const form = document.getElementById("cat-sign-form");
    if (!form) return;
    form.querySelectorAll("input[data-vault]").forEach((input) => {
      vault.delete(input);
      input.value = "";
      input.removeAttribute("value");
      const mask = form.querySelector(`.cat-mask[data-for="${input.dataset.vault}"]`);
      if (mask) mask.textContent = "";
      // Drop residual inspector hooks by replacing the node.
      const clean = input.cloneNode(false);
      clean.removeAttribute("value");
      clean.value = "";
      // re-bind safety after clone
      input.replaceWith(clean);
      bindVaultInput(clean);
    });
  }

  function paintMask(input, mask) {
    const live = vault.get(input) || "";
    if (mask) mask.textContent = live ? "·".repeat(Math.min(live.length, 64)) : "";
    input.value = "";
    input.removeAttribute("value");
  }

  function bindVaultInput(input) {
    const key = input.dataset.vault;
    if (!key) return;
    const mask = document.querySelector(`.cat-mask[data-for="${key}"]`);

    // Keystrokes never land in input.value / attributes — only in the WeakMap vault.
    input.addEventListener("keydown", (e) => {
      if (e.key === "Tab" || e.key === "Enter" || e.key === "Escape") return;
      if (e.ctrlKey || e.metaKey || e.altKey) return;
      e.preventDefault();
      let cur = vault.get(input) || "";
      if (e.key === "Backspace") cur = cur.slice(0, -1);
      else if (e.key === "Delete") cur = "";
      else if (e.key.length === 1) cur += e.key;
      else return;
      vault.set(input, cur);
      paintMask(input, mask);
    });

    input.addEventListener("input", () => {
      // Autofill / IME / inspector writes — capture once then scrub.
      const leaked = input.value;
      if (leaked) vault.set(input, (vault.get(input) || "") + leaked);
      paintMask(input, mask);
    });

    input.addEventListener("paste", (e) => {
      e.preventDefault();
      const text = (e.clipboardData || window.clipboardData).getData("text") || "";
      vault.set(input, (vault.get(input) || "") + text);
      paintMask(input, mask);
    });
  }

  function wireCatSignFields() {
    document.querySelectorAll("#cat-sign-form input[data-vault]").forEach(bindVaultInput);
  }

  function checkScrollComplete() {
    const el = catSignScroll;
    const done = el.scrollTop + el.clientHeight >= el.scrollHeight - 8;
    signReady = done;
    catSignProceed.disabled = !done;
    catSignProceed.textContent = done
      ? "Click anywhere to proceed"
      : "Scroll the plaque fully to enable proceed";
  }

  function openCatSign(section) {
    const img = document.getElementById("cat-sign-img");
    if (section) {
      img.src = `/hall/assets/cat_sign_sections/section_${section}.png?v=1`;
      img.alt = `How to Not Mess with Cats — section ${section}`;
    } else {
      img.src = "/hall/assets/cat_sign.png?v=1";
      img.alt = "How to Not Mess with Cats — facility plaque";
    }
    signReady = false;
    catSignProceed.disabled = true;
    catSignProceed.textContent = "Scroll the plaque fully to enable proceed";
    catSign.hidden = false;
    catSignScroll.scrollTop = 0;
    // Full plaque for field-facing flow when no section crop (or still require scroll)
    window.setTimeout(checkScrollComplete, 80);
  }

  function closeCatSign() {
    scrubFields();
    catSign.hidden = true;
    signReady = false;
  }

  catSignScroll.addEventListener("scroll", checkScrollComplete, { passive: true });
  catSignClose.addEventListener("click", closeCatSign);

  catSignProceed.addEventListener("click", () => {
    if (!signReady) return;
    scrubFields();
    closeCatSign();
  });

  // "Click anywhere to proceed" once unlocked — panel background counts
  document.querySelector(".cat-sign-panel").addEventListener("click", (e) => {
    if (!signReady) return;
    if (e.target.closest("input, label, .cat-sign-scroll, .modal-close")) return;
    scrubFields();
    closeCatSign();
  });

  wireCatSignFields();

  /* ── Terminal commands ───────────────────────────────────────────── */

  async function fetchText(url) {
    const r = await fetch(url);
    if (!r.ok) throw new Error(`${r.status}`);
    return r.text();
  }

  function downloadUrl(url, filename) {
    const a = document.createElement("a");
    a.href = url;
    a.download = filename || "";
    a.rel = "noopener";
    document.body.appendChild(a);
    a.click();
    a.remove();
  }

  async function run(cmd, page, termLog, row) {
    const raw = cmd.trim();
    const lower = raw.toLowerCase();
    if (!raw) return;

    if (lower === "help") {
      COMMANDS.forEach((c) => log(termLog, c));
      return;
    }

    if (lower === "help for help") {
      log(termLog, "summoning Chaucer · Cecil · Sauron…", "dim");
      try {
        const md = await fetchText(page.help_for_help);
        openModal(mdLite(md));
        const audioUrl = page.help_for_help_audio;
        const probe = await fetch(audioUrl, { method: "HEAD" }).catch(() => null);
        const ctype = (probe && probe.headers.get("content-type")) || "";
        // SPA try_files can 200 HTML for a missing .mp3 — require a real audio type.
        if (probe && probe.ok && /audio|mpeg|octet-stream/i.test(ctype)) {
          const wrap = document.createElement("div");
          wrap.innerHTML = `<audio controls autoplay src="${esc(audioUrl)}" style="width:100%;margin-bottom:12px"></audio>`;
          modalBody.insertBefore(wrap.firstChild, modalBody.firstChild);
          log(termLog, "playing help for help", "dim");
        } else {
          log(termLog, "script loaded (audio not on host yet)", "dim");
        }
      } catch (e) {
        log(termLog, `help for help unavailable: ${e.message}`, "err");
      }
      return;
    }

    if (lower === "ls") {
      pages.forEach((p, n) => {
        const mark = n === index ? ">" : " ";
        const label = pageLabel(p);
        log(termLog, `${mark} {${label}: ${p.title}}`);
      });
      return;
    }

    if (lower === "cat" || lower === "cats") {
      spawnCat();
      log(termLog, `meow. (${cats} sustained)`, "dim");
      return;
    }

    if (lower === "mv" || lower.startsWith("mv ")) {
      const arg = lower === "mv" ? "" : raw.slice(3).trim();
      let target;
      if (!arg || arg === "next") {
        if (index >= pages.length - 1) {
          log(termLog, "end of hall", "err");
          return;
        }
        target = pages[index + 1];
      } else if (arg === "prev" || arg === "..") {
        if (index <= 0) {
          log(termLog, "start of hall", "err");
          return;
        }
        target = pages[index - 1];
      } else {
        target = findPage(arg);
      }
      if (!target) {
        log(termLog, "no such slug", "err");
        return;
      }
      if (target.slug === page.slug) {
        log(termLog, "already here", "dim");
        return;
      }
      log(termLog, `→ ${target.slug}`, "dim");
      traverseTo(target.slug);
      return;
    }

    if (lower === "play video") {
      if (!page.video) {
        log(termLog, "no video on this row", "err");
        return;
      }
      openModal(
        `<video controls autoplay src="${esc(page.video)}" style="width:100%;max-height:78vh;background:#000"></video>`
      );
      log(termLog, `playing ${page.video}`, "dim");
      return;
    }

    if (lower === "play audio") {
      if (!page.audio) {
        log(termLog, "no audio on this row", "err");
        return;
      }
      const img = page.preview_image || "/hall/assets/hallway.png";
      const text = esc(page.transcript_preview || "(no transcript preview)");
      openModal(
        `<div class="modal-split">
          <div class="top"><img src="${esc(img)}" alt=""></div>
          <div class="bottom">${text}</div>
        </div>
        <audio controls autoplay src="${esc(page.audio)}" style="width:100%;margin-top:12px"></audio>`
      );
      log(termLog, `playing ${page.audio}`, "dim");
      return;
    }

    if (lower === "read") {
      const src = page.source_md || page.transcript_txt;
      if (!src) {
        log(termLog, "no text source", "err");
        return;
      }
      log(termLog, `reading ${src}`, "dim");
      try {
        const md = await fetchText(src);
        openModal(mdLite(md));
      } catch (e) {
        if (page.transcript_txt && src !== page.transcript_txt) {
          try {
            const md = await fetchText(page.transcript_txt);
            openModal(mdLite(md));
            return;
          } catch (_) {}
        }
        log(termLog, `read failed: ${e.message}`, "err");
      }
      return;
    }

    if (lower === "download video") {
      if (!page.video) {
        log(termLog, "no video", "err");
        return;
      }
      downloadUrl(page.video, `${page.slug}.mp4`);
      log(termLog, `download → ${page.video}`, "dim");
      return;
    }

    if (lower === "download audio") {
      if (!page.audio) {
        log(termLog, "no audio", "err");
        return;
      }
      downloadUrl(page.audio, `${page.slug}.mp3`);
      log(termLog, `download → ${page.audio}`, "dim");
      return;
    }

    if (lower === "download text") {
      const src = page.source_md || page.transcript_txt;
      if (!src) {
        log(termLog, "no text", "err");
        return;
      }
      downloadUrl(src, `${page.slug}.md`);
      log(termLog, `download → ${src}`, "dim");
      return;
    }

    if (lower === "clear") {
      termLog.textContent = "";
      return;
    }

    log(termLog, "unknown — type help", "err");
  }

  function buildRow(page) {
    const art = document.createElement("article");
    art.className = "row";
    art.id = `row-${page.slug}`;
    art.dataset.slug = page.slug;

    const previewText = page.transcript_preview || "(no transcript yet)";
    art.innerHTML = `
      <div class="row-head">
        <span class="slug">${esc(pageLabel(page))}</span>
        <span class="title">${esc(page.title)}</span>
        <span class="meta">${esc(page.meta || "")}</span>
      </div>
      <div class="preview">
        <div class="preview-media">
          <img src="${esc(page.preview_image)}" alt="" loading="lazy">
        </div>
        <div class="preview-text">${esc(previewText)}</div>
      </div>
      <div class="term">
        <div class="term-log"></div>
        <form class="term-form" autocomplete="off">
          <span class="prompt">rum&gt;</span>
          <input type="text" spellcheck="false" aria-label="terminal ${esc(page.slug)}" placeholder='type "help for help"'>
        </form>
      </div>
    `;

    const termLog = art.querySelector(".term-log");
    const form = art.querySelector(".term-form");
    const input = art.querySelector("input");

    log(termLog, 'type "help for help"', "dim");
    log(termLog, "mv -0 | mv -00 | mv next | cat | ls", "dim");

    form.addEventListener("submit", (e) => {
      e.preventDefault();
      const v = input.value;
      if (!v.trim()) return;
      log(termLog, `rum> ${v}`, "cmd");
      input.value = "";
      run(v, page, termLog, art);
    });

    rowMap.set(page.slug, art);
    return art;
  }

  async function boot() {
    const data = await fetch("/hall/pages.json?v=20261112a").then((r) => r.json());
    pages = data.pages || [];
    rowsEl.innerHTML = "";
    pages.forEach((p) => rowsEl.appendChild(buildRow(p)));

    // Hall always opens at −0 unless the hash is an exact known station.
    let start = 0;
    const hash = location.hash.replace(/^#/, "");
    if (hash) {
      const hit = findPage(hash);
      if (hit) start = pages.findIndex((p) => p.slug === hit.slug);
      else start = 0; // unknown hash → −0, do not fall through to −05
    }
    index = Math.max(0, start);
    if (pages[index]) showOnly(pages[index].slug);
  }

  boot().catch((e) => {
    rowsEl.innerHTML = `<pre class="term-log" style="padding:24px;color:#e07070">failed to load pages.json\n${esc(e.message)}</pre>`;
  });
})();
