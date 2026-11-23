(() => {
  "use strict";

  const state = {
    chapters: [],
    index: 0,
    startedAudio: false,
    rates: [1, 1.15, 1.3, 0.85],
    rateIndex: 0,
  };

  const $ = (id) => document.getElementById(id);
  const els = {
    label: $("chapter-label"),
    title: $("chapter-title"),
    page: $("chapter-page"),
    pageLabel: $("page-label"),
    pageTitle: $("page-title"),
    pageMeta: $("page-meta"),
    body: $("chapter-body"),
    source: $("page-source"),
    number: $("page-number"),
    progress: $("read-progress"),
    toc: $("toc-panel"),
    tocList: $("toc-list"),
    tocToggle: $("toc-toggle"),
    tocClose: $("toc-close"),
    tocScrim: $("toc-scrim"),
    previous: $("previous-chapter"),
    next: $("next-chapter"),
    bottomPrevious: $("bottom-previous"),
    bottomNext: $("bottom-next"),
    narration: $("narration"),
    narrationPlay: $("narration-play"),
    narrationTitle: $("narration-title"),
    narrationTime: $("narration-time"),
    narrationSeek: $("narration-seek"),
    narrationSpeed: $("narration-speed"),
    continueReading: $("continue-reading"),
    audio: $("chapter-audio"),
  };

  function chapterFromLocation() {
    const params = new URLSearchParams(location.search);
    const requested = params.get("chapter") || location.hash.replace(/^#/, "");
    if (requested) {
      const found = state.chapters.findIndex((chapter) => chapter.id === requested);
      if (found >= 0) return found;
    }
    const saved = localStorage.getItem("rum-book-chapter");
    const found = state.chapters.findIndex((chapter) => chapter.id === saved);
    return found >= 0 ? found : 0;
  }

  function setLocation(chapter) {
    const url = new URL(location.href);
    url.searchParams.set("chapter", chapter.id);
    url.hash = "";
    history.replaceState({ chapter: chapter.id }, "", url);
    localStorage.setItem("rum-book-chapter", chapter.id);
  }

  function makeToc() {
    const fragment = document.createDocumentFragment();
    state.chapters.forEach((chapter, index) => {
      const button = document.createElement("button");
      button.type = "button";
      button.className = "toc-entry";
      button.dataset.index = String(index);
      button.innerHTML = `
        <span>${String(index + 1).padStart(2, "0")}</span>
        <div><strong>${chapter.title}</strong><small>${chapter.label}</small></div>`;
      button.addEventListener("click", () => {
        showChapter(index);
        toggleToc(false);
      });
      fragment.appendChild(button);
    });
    els.tocList.replaceChildren(fragment);
  }

  function toggleToc(open) {
    document.body.classList.toggle("toc-open", open);
    els.tocToggle.setAttribute("aria-expanded", String(open));
    if (open) {
      const active = els.tocList.querySelector(".active");
      active?.scrollIntoView({ block: "center" });
    }
  }

  function resetAudio(chapter, shouldPlay = false) {
    els.audio.pause();
    els.audio.removeAttribute("src");
    els.audio.load();
    els.narrationTitle.textContent = chapter.audio
      ? chapter.title
      : `${chapter.title} · narration pending`;
    els.narration.classList.toggle("unavailable", !chapter.audio);
    els.narrationPlay.disabled = !chapter.audio;
    els.narrationPlay.textContent = "▶";
    els.narrationSeek.value = "0";
    els.narrationTime.textContent = "00:00 / 00:00";
    if (!chapter.audio) return;
    els.audio.src = chapter.audio;
    els.audio.playbackRate = state.rates[state.rateIndex];
    els.audio.load();
    if (shouldPlay) {
      els.audio.play().catch(() => {});
    }
  }

  function showChapter(nextIndex, options = {}) {
    if (!state.chapters.length) return;
    const index = Math.max(0, Math.min(state.chapters.length - 1, nextIndex));
    const chapter = state.chapters[index];
    const continueAudio = Boolean(options.continueAudio);
    state.index = index;
    document.title = `${chapter.title} — REALITY_USER_MANUAL`;
    els.label.textContent = chapter.label;
    els.title.textContent = chapter.title;
    els.pageLabel.textContent = chapter.label;
    els.pageTitle.textContent = chapter.title;
    els.pageMeta.textContent = `${chapter.words.toLocaleString()} words · ${chapter.minutes} min read`;
    els.body.innerHTML = chapter.html;
    els.source.textContent = chapter.source;
    els.number.textContent = `${String(index + 1).padStart(2, "0")} / ${String(state.chapters.length).padStart(2, "0")}`;

    const atStart = index === 0;
    for (const button of [els.previous, els.bottomPrevious]) button.disabled = atStart;
    for (const button of [els.next, els.bottomNext]) {
      button.disabled = false;
      if (index === state.chapters.length - 1 && button === els.bottomNext) button.textContent = "Phase 2 →";
      else if (button === els.bottomNext) button.textContent = "Next →";
    }
    els.tocList.querySelectorAll(".toc-entry").forEach((entry, entryIndex) => {
      entry.classList.toggle("active", entryIndex === index);
      if (entryIndex === index) entry.setAttribute("aria-current", "page");
      else entry.removeAttribute("aria-current");
    });
    setLocation(chapter);
    resetAudio(chapter, continueAudio);
    window.scrollTo({ top: 0, behavior: options.instant ? "auto" : "smooth" });
    els.page.focus({ preventScroll: true });
    updateProgress();
  }

  function move(delta, options = {}) {
    const target = state.index + delta;
    if (target >= state.chapters.length) {
      location.href = "/gate/";
      return;
    }
    if (target < 0) return;
    showChapter(target, options);
  }

  function formatTime(value) {
    if (!Number.isFinite(value) || value < 0) return "00:00";
    const hours = Math.floor(value / 3600);
    const minutes = Math.floor((value % 3600) / 60);
    const seconds = Math.floor(value % 60);
    return hours
      ? `${hours}:${String(minutes).padStart(2, "0")}:${String(seconds).padStart(2, "0")}`
      : `${String(minutes).padStart(2, "0")}:${String(seconds).padStart(2, "0")}`;
  }

  function updateAudio() {
    const duration = els.audio.duration || 0;
    const current = els.audio.currentTime || 0;
    els.narrationSeek.value = duration ? String(Math.round((current / duration) * 1000)) : "0";
    els.narrationTime.textContent = `${formatTime(current)} / ${formatTime(duration)}`;
    els.narrationPlay.textContent = els.audio.paused ? "▶" : "❚❚";
  }

  function updateProgress() {
    const root = document.documentElement;
    const available = root.scrollHeight - root.clientHeight;
    const percent = available > 0 ? Math.min(100, Math.max(0, (root.scrollTop / available) * 100)) : 0;
    els.progress.style.width = `${percent}%`;
  }

  els.tocToggle.addEventListener("click", () => toggleToc(!document.body.classList.contains("toc-open")));
  els.tocClose.addEventListener("click", () => toggleToc(false));
  els.tocScrim.addEventListener("click", () => toggleToc(false));
  els.previous.addEventListener("click", () => move(-1));
  els.next.addEventListener("click", () => move(1));
  els.bottomPrevious.addEventListener("click", () => move(-1));
  els.bottomNext.addEventListener("click", () => move(1));

  els.narrationPlay.addEventListener("click", () => {
    state.startedAudio = true;
    if (els.audio.paused) els.audio.play().catch(() => {});
    else els.audio.pause();
  });
  els.narrationSeek.addEventListener("input", () => {
    if (els.audio.duration) {
      els.audio.currentTime = (Number(els.narrationSeek.value) / 1000) * els.audio.duration;
    }
  });
  els.narrationSpeed.addEventListener("click", () => {
    state.rateIndex = (state.rateIndex + 1) % state.rates.length;
    const rate = state.rates[state.rateIndex];
    els.audio.playbackRate = rate;
    els.narrationSpeed.textContent = `${rate}×`;
  });
  els.audio.addEventListener("play", updateAudio);
  els.audio.addEventListener("pause", updateAudio);
  els.audio.addEventListener("timeupdate", updateAudio);
  els.audio.addEventListener("loadedmetadata", updateAudio);
  els.audio.addEventListener("ended", () => {
    updateAudio();
    if (els.continueReading.checked) {
      move(1, { continueAudio: true });
    }
  });
  window.addEventListener("scroll", updateProgress, { passive: true });
  window.addEventListener("keydown", (event) => {
    if (event.key === "Escape") toggleToc(false);
    if (event.target instanceof HTMLInputElement || event.target instanceof HTMLButtonElement) return;
    if (event.key === "ArrowLeft" && event.altKey) move(-1);
    if (event.key === "ArrowRight" && event.altKey) move(1);
  });
  window.addEventListener("popstate", () => showChapter(chapterFromLocation(), { instant: true }));

  fetch("/book/chapters.json")
    .then((response) => {
      if (!response.ok) throw new Error(`chapters.json: ${response.status}`);
      return response.json();
    })
    .then((data) => {
      state.chapters = data.chapters || [];
      makeToc();
      showChapter(chapterFromLocation(), { instant: true });
    })
    .catch((error) => {
      els.pageTitle.textContent = "The book did not bind";
      els.body.innerHTML = `<p>${error.message}</p>`;
      els.narration.classList.add("unavailable");
    });
})();
