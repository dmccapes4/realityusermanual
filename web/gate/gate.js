(() => {
  const STAGE = document.getElementById("stage");
  const SKIP = document.getElementById("skip");
  const qs = new URLSearchParams(location.search);
  const force = qs.get("force") === "1";
  const replay = qs.get("replay") === "1";
  const debug = qs.get("debug") === "1";
  const freezeAt = Number(qs.get("freeze") || 0) || 0;

  let beatsDoc = {
    duration_ms: 7200,
    redirect: "/hall/#-0",
    beats: [
      { id: "title_in", start_ms: 0 },
      { id: "kata_to_cat", start_ms: 1200 },
      { id: "cat_exit_left", start_ms: 1800 },
      { id: "maththaion_center", start_ms: 2600 },
      { id: "theta_open", start_ms: 3600 },
      { id: "suck", start_ms: 5000 },
      { id: "land", start_ms: 6800 },
    ],
  };
  let started = 0;
  let raf = 0;
  let current = "boot";
  let finished = false;

  function seen() {
    try {
      return localStorage.getItem("rum_gate_seen") === "1";
    } catch (_) {
      return false;
    }
  }

  function markSeen() {
    try {
      localStorage.setItem("rum_gate_seen", "1");
    } catch (_) {}
  }

  function setBeat(id) {
    if (id === current) return;
    current = id;
    STAGE.className = "stage beat-" + id;
    if (debug) console.log("[gate]", id, (performance.now() - started) | 0);
  }

  function land() {
    if (finished) return;
    finished = true;
    cancelAnimationFrame(raf);
    setBeat("land");
    markSeen();
    const dest = beatsDoc.redirect || "/hall/#-0";
    setTimeout(() => {
      location.href = dest;
    }, 180);
  }

  function tick(now) {
    if (finished) return;
    const t = now - started;
    if (freezeAt && t >= freezeAt) {
      let active = beatsDoc.beats[0].id;
      for (const b of beatsDoc.beats) {
        if (freezeAt >= b.start_ms) active = b.id;
      }
      setBeat(active);
      if (debug) console.log("[gate] frozen", freezeAt, active);
      return;
    }
    let active = beatsDoc.beats[0].id;
    for (const b of beatsDoc.beats) {
      if (t >= b.start_ms) active = b.id;
    }
    setBeat(active);
    if (t >= beatsDoc.duration_ms) {
      land();
      return;
    }
    raf = requestAnimationFrame(tick);
  }

  function start() {
    started = performance.now();
    setBeat("title_in");
    raf = requestAnimationFrame(tick);
  }

  SKIP.addEventListener("click", land);
  window.addEventListener("keydown", (e) => {
    if (e.key === "Escape" || e.key === "Enter" || e.key === " ") {
      e.preventDefault();
      land();
    }
  });

  if (matchMedia("(prefers-reduced-motion: reduce)").matches) {
    land();
    return;
  }

  fetch("/gate/beats.json", { cache: "no-store" })
    .then((r) => r.json())
    .then((doc) => {
      beatsDoc = doc;
      if (seen() && !force && !replay) {
        location.replace(doc.redirect || "/hall/#-0");
        return;
      }
      requestAnimationFrame(() => requestAnimationFrame(start));
    })
    .catch(() => {
      if (seen() && !force && !replay) {
        location.replace("/hall/#-0");
        return;
      }
      start();
    });
})();
