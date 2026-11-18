const ListenDesk = (() => {
  const SHELVES = [
    { kind: "page", title: "Page films" },
    { kind: "audio", title: "Book and page audio" },
    { kind: "quarantine", title: "Quarantine — multi-page mixes" },
  ];

  function fmtDur(sec) {
    sec = Math.max(0, Math.round(Number(sec) || 0));
    const h = Math.floor(sec / 3600);
    const m = Math.floor((sec % 3600) / 60);
    const s = sec % 60;
    if (h) return `${h}:${String(m).padStart(2, "0")}:${String(s).padStart(2, "0")}`;
    return `${m}:${String(s).padStart(2, "0")}`;
  }

  function fmtCue(sec) {
    sec = Math.max(0, Number(sec) || 0);
    const h = Math.floor(sec / 3600);
    const m = Math.floor((sec % 3600) / 60);
    const s = Math.floor(sec % 60);
    if (h) return `${h}:${String(m).padStart(2, "0")}:${String(s).padStart(2, "0")}`;
    return `${m}:${String(s).padStart(2, "0")}`;
  }

  function catalog() {
    return fetch("/listen/catalog.json", { cache: "no-store" }).then((r) => r.json());
  }

  /** Keep WebVTT off until the participant enables CC in the native controls. */
  function muteTextTracks(media) {
    const disable = () => {
      try {
        for (const t of media.textTracks || []) t.mode = "disabled";
      } catch (_) {}
    };
    disable();
    media.addEventListener("loadedmetadata", disable);
    media.addEventListener("play", disable, { once: true });
  }

  function index() {
    catalog().then((data) => {
      const host = document.getElementById("shelves");
      for (const shelf of SHELVES) {
        const items = data.items.filter((it) => it.kind === shelf.kind);
        if (!items.length) continue;
        const wrap = document.createElement("section");
        wrap.className = "shelf";
        wrap.innerHTML = `<h2>${shelf.title}</h2>`;
        for (const it of items) {
          const a = document.createElement("a");
          a.className = "listen-card";
          a.href = `/listen/play.html?id=${encodeURIComponent(it.id)}`;
          const bits = [];
          if (it.video) bits.push("film");
          if (it.still) bits.push("still");
          if (it.audio) bits.push("audio");
          bits.push(`${(it.transcript && it.transcript.lines) || 0} lines`);
          const label = it.page ? `${it.page} — ${it.title}` : it.title;
          a.innerHTML =
            `<span class="page">${it.page || "mix"}</span>` +
            `<span><strong>${label}</strong><div class="meta">${it.voices} · ${bits.join(" · ")}</div></span>` +
            `<span class="dur">${fmtDur(it.duration)}</span>`;
          wrap.appendChild(a);
        }
        host.appendChild(wrap);
      }
    });
  }

  function play() {
    const id = new URLSearchParams(location.search).get("id");
    if (!id) {
      location.href = "/listen/";
      return;
    }
    catalog().then((data) => {
      const item = data.items.find((it) => it.id === id);
      if (!item) {
        document.getElementById("play-title").textContent = "Not on the desk";
        return;
      }
      const playLabel = item.page ? `${item.page} — ${item.title}` : item.title;
      document.title = `${playLabel} — Listen`;
      document.getElementById("play-title").textContent = playLabel;
      document.getElementById("play-stamp").textContent = item.page || item.kind;
      const stage = document.getElementById("stage");
      const takes = document.getElementById("takes");
      let media;
      const stageWrap = document.createElement("div");
      stageWrap.className = "stage-stack";
      if (item.still) {
        const img = document.createElement("img");
        img.className = "stage-still";
        img.src = item.still;
        img.alt = playLabel;
        stageWrap.appendChild(img);
      }
      if (item.video) {
        media = document.createElement("video");
        media.controls = true;
        media.preload = "auto";
        media.src = item.video;
        if (item.transcript && item.transcript.vtt) {
          const track = document.createElement("track");
          track.kind = "subtitles";
          track.label = "Transcript";
          track.srclang = "en";
          track.src = `${item.transcript.vtt}?v=${item.transcript.lines || 0}`;
          // Off by default — CC is available in the player menu; on-screen cues dominate film.
          track.default = false;
          media.appendChild(track);
        }
        muteTextTracks(media);
        stageWrap.appendChild(media);
      } else if (item.audio) {
        media = document.createElement("audio");
        media.controls = true;
        media.preload = "auto";
        media.src = item.audio;
        if (item.still && item.transcript && item.transcript.vtt) {
          const track = document.createElement("track");
          track.kind = "subtitles";
          track.label = "Transcript";
          track.srclang = "en";
          track.src = `${item.transcript.vtt}?v=${item.transcript.lines || 0}`;
          track.default = false;
          media.appendChild(track);
        }
        muteTextTracks(media);
        stageWrap.appendChild(media);
      }
      stage.appendChild(stageWrap);
      const tr = item.transcript || {};
      const links = [];
      if (item.read) links.push(["Read page", item.read]);
      if (item.still) links.push(["Download still", item.still]);
      if (item.video) links.push(["Download film", item.video]);
      if (item.audio) links.push(["Download audio", item.audio]);
      if (tr.txt) links.push(["Transcript .txt", tr.txt]);
      if (tr.vtt) links.push(["Captions .vtt", tr.vtt]);
      if (tr.json) links.push(["Cues .json", tr.json]);
      for (const [label, href] of links) {
        const a = document.createElement("a");
        a.href = href;
        a.download = "";
        a.textContent = label;
        takes.appendChild(a);
      }
      if (tr.lines) {
        const jump = document.createElement("a");
        jump.href = "#transcript";
        jump.textContent = `Transcript (${tr.lines} lines)`;
        takes.appendChild(jump);
      }
      loadTranscript(media, tr);
    });
  }

  function loadTranscript(media, tr) {
    const pane = document.getElementById("transcript");
    pane.replaceChildren();
    const lineCount = document.getElementById("line-count");
    if (!tr || !tr.json) {
      lineCount.textContent = "missing";
      pane.textContent =
        "No transcript registered for this item. Re-run tools/build_listen_desk.py and deploy.";
      return;
    }
    const url = `${tr.json}?v=${encodeURIComponent(tr.lines || 0)}`;
    fetch(url, { cache: "no-store" })
      .then((r) => {
        if (!r.ok) throw new Error(`HTTP ${r.status} for ${url}`);
        return r.json();
      })
      .then((payload) => bindTranscript(media, payload.cues || []))
      .catch((err) => {
        lineCount.textContent = "error";
        pane.textContent = `Transcript failed to load: ${err.message}. Hard-refresh (Ctrl+Shift+R) or open ${tr.json}`;
      });
  }

  function bindTranscript(media, cues) {
    const pane = document.getElementById("transcript");
    pane.replaceChildren();
    document.getElementById("line-count").textContent = `${cues.length} lines`;
    const nodes = [];
    for (const cue of cues) {
      const btn = document.createElement("button");
      btn.type = "button";
      btn.className = "cue";
      btn.innerHTML =
        `<span class="when">${fmtCue(cue.start)}</span>` +
        `<span class="who">${cue.speaker || "Voice"}</span>` +
        `<span class="said"></span>`;
      btn.querySelector(".said").textContent = cue.text || "";
      btn.addEventListener("click", () => {
        if (!media) return;
        const t = Number(cue.start) || 0;
        const go = () => {
          media.currentTime = t;
          media.play();
        };
        if (media.seekable.length && media.seekable.end(media.seekable.length - 1) > t) go();
        else media.addEventListener("canplay", go, { once: true });
      });
      pane.appendChild(btn);
      nodes.push({ cue, btn });
    }
    if (!media) return;
    let last = -1;
    media.addEventListener("timeupdate", () => {
      const t = media.currentTime;
      let idx = -1;
      for (let i = 0; i < cues.length; i++) {
        const c = cues[i];
        if (t >= (c.start || 0) && t < (c.end || c.start + 1)) idx = i;
        else if (idx < 0 && t >= (c.start || 0)) idx = i;
      }
      if (idx === last) return;
      if (last >= 0) nodes[last].btn.classList.remove("active");
      if (idx >= 0) {
        nodes[idx].btn.classList.add("active");
        nodes[idx].btn.scrollIntoView({ block: "nearest" });
      }
      last = idx;
    });
  }

  return { index, play };
})();
