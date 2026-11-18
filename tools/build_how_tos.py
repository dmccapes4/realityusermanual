#!/usr/bin/env python3
"""
The HOW_TO stack as one page: index, search bar, all 22 documents inline.

The PDF used to reprint the 22 HOW_TOs in full (~54,000 words, ~300 pages).
It now carries a desk-stamp page (src/-09_received_how_tos.md) and this
HTML travels two ways:

  1. the live desk:  https://realityusermanual.dylanmccapes.systems/m/how-tos/
  2. hidden in the PDF as a file attachment (HOW_TOS.html), for readers
     that have a paperclip pane. build.py does the attaching.

Order and scores come from docs/MANIFEST_HOW_TO_PORTALVISION_20261024.md
(d20 roll, declared and auditable). Source paths are the canonical
PortalVision files; nothing is rewritten.

  .venv/bin/python tools/build_how_tos.py
"""

from __future__ import annotations

import html
import json
import re
from datetime import date
from pathlib import Path

import markdown

BASE = Path(__file__).resolve().parent.parent
SRC = BASE / "src"
WEB = BASE / "web"
OUT_DIR = WEB / "m" / "how-tos"
OUT = OUT_DIR / "index.html"
MANIFEST = BASE / "docs" / "MANIFEST_HOW_TO_PORTALVISION_20261024.md"

PV = Path("/home/dylanmccapes/dev/PORTAL_VISION_LUCIFER")
PV0 = Path("/home/dylanmccapes/dev/PORTAL_VISION_V0.1")

# d20 order. Mirrors the list that used to live in build.py.
HOW_TOS_D20 = [
    PV / "data/artifacts/HOW_TO_SEE.md",                                     # pos 1  roll 20
    PV / "docs/HOW_TO_PARENT_ANIMALS.md",                                    # pos 2  roll 19
    PV / "data/artifacts/HOW_TO_NOT_FLY.md",                                 # pos 3  roll 18
    PV / "distributions/for_azazel_and_hilariousmarcupial/HOW_TO_LEARN_PROGRAMMING_LANGUAGES.md",  # pos 4 roll 17
    PV / "data/artifacts/HOW_TO_EAT_MEATS_IF_YOU_MUST.md",                   # pos 5  roll 16
    PV / "game_plans/HOW_TO_CHOOSE_A_CO_NAVIGATOR.md",                       # pos 6  roll 15
    PV / "misc/HOW_TO_USE_3Pi$73MiC87MLV4ULT.md",                            # pos 7  roll 14
    PV / "projects/dylans_artifacts/youtube_copyright/HOW_TO_RUN_THIS_INVESTIGATION_FOR_YOUTUBE_COPYRIGHT_TEAM.md",  # pos 8 roll 13
    PV / "game_plans/HOW_TO_PARENT_ALPHA_GENERATION.md",                     # pos 9  roll 12
    PV / "game_plans/HOW_TO_MENTOR.md",                                      # pos 10 roll 11
    PV / "data/artifacts/HOW_TO_FLY.md",                                     # pos 11 roll 10
    PV / "data/artifacts/HOW_TO_EAT_FOODS.md",                               # pos 12 roll 9
    PV0 / "HOW_TO_BREATHE_BACKWARDS.md",                                     # pos 13 roll 8a
    PV / "docs/HOW_TO_USE_TOOLS.md",                                         # pos 14 roll 8b
    PV / "data/artifacts/HOW_TO_TOUCH.md",                                   # pos 15 roll 7
    PV / "docs/HOW_TO_PROVIDE_OPTIONS.md",                                   # pos 16 roll 6
    PV / "projects/on_interplanar_travel/HOW_TO_NOT_MESS_WITH_CATS.md",      # pos 17 roll 5
    PV / "data/artifacts/HOW_TO_LIVE_WITH_OVEREXCITABLES.md",                # pos 18 roll 4
    PV / "game_plans/HOW_TO_FILE_DOCUMENTS_PLAYBOOK.md",                     # pos 19 roll 3
    PV / "game_plans/HOW_TO_COLLECT_GARBAGE.md",                             # pos 20 roll 2
    PV / "game_plans/HOW_TO_USE_THE_INTERNET.md",                            # pos 21 roll 1a
    PV / "books/addiction_topology/HOW_TO_BE_NEUROMAJOR.md",                 # pos 22 roll 1b
]


def parse_manifest() -> dict[str, dict]:
    """### N. NAME / **Roll: X | Score: Y/50** / blurb → {NAME: {...}}"""
    text = MANIFEST.read_text(encoding="utf-8")
    out: dict[str, dict] = {}
    blocks = re.split(r"^### (\d+)\. (HOW_TO_\S+)\s*$", text, flags=re.M)
    # blocks: [pre, n, name, body, n, name, body, ...]
    for i in range(1, len(blocks), 3):
        n, name, body = int(blocks[i]), blocks[i + 1], blocks[i + 2]
        m = re.search(r"\*\*Roll:\s*([^|]+)\|\s*Score:\s*(\d+)/50\*\*", body)
        roll = m.group(1).strip() if m else ""
        score = int(m.group(2)) if m else None
        blurb = body
        if m:
            blurb = body[m.end():]
        blurb = blurb.split("\n---", 1)[0].strip()
        out[name] = {"n": n, "roll": roll, "score": score, "blurb": blurb}
    return out


def strip_front_matter(md: str) -> tuple[str, str]:
    """Return (title, body). Title is the first H1; body drops that one line
    (the page prints its own title block) and keeps everything else."""
    m = re.search(r"^#\s+(.+?)\s*$", md, flags=re.M)
    if not m:
        return "", md
    title = m.group(1).strip()
    body = md[: m.start()] + md[m.end():]
    return title, body


_LIST_RE = re.compile(r"^(\s*)([-*+]|\d+[.)])\s+")


def loosen_lists(md: str) -> str:
    """Python-Markdown wants a blank line before a list. The PortalVision
    files often open a list straight under a bold label. Insert the blank
    line; leave fenced code alone."""
    out: list[str] = []
    in_fence = False
    prev = ""
    for line in md.splitlines():
        if line.strip().startswith("```"):
            in_fence = not in_fence
            out.append(line)
            prev = line
            continue
        if (not in_fence and _LIST_RE.match(line) and prev.strip()
                and not _LIST_RE.match(prev) and not prev.startswith("|")):
            out.append("")
        out.append(line)
        prev = line
    return "\n".join(out) + "\n"


def convert(md_text: str) -> str:
    return markdown.markdown(
        loosen_lists(md_text),
        extensions=["tables", "fenced_code", "sane_lists", "toc"],
        extension_configs={"toc": {"permalink": False}},
        output_format="html5",
    )


def build_docs() -> list[dict]:
    meta = parse_manifest()
    docs = []
    for pos, path in enumerate(HOW_TOS_D20, start=1):
        name = path.stem
        if not path.exists():
            raise SystemExit(f"missing: {path}")
        raw = path.read_text(encoding="utf-8")
        title, body = strip_front_matter(raw)
        m = meta.get(name, {})
        if m.get("n") not in (None, pos):
            print(f"  [order] manifest says {m['n']} for {name}, list says {pos}")
        docs.append({
            "id": re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-"),
            "name": name,
            "title": title or name,
            "n": m.get("n", pos),
            "roll": m.get("roll", ""),
            "score": m.get("score"),
            "blurb": m.get("blurb", ""),
            "source": str(path).replace("/home/dylanmccapes/dev/", ""),
            "words": len(raw.split()),
            "html": convert(body),
            "plain": raw,
        })
    docs.sort(key=lambda d: (d["n"] is None, d["n"] or 0))
    return docs


CSS = """
:root{--ink:#1a1c1e;--panel:#e8e2d4;--seam:#c9c3b4;--recess:#f4f0e6;--paper:#f7f3ea;--accent:#8c3a2a;--slot:#d4cfc2;--mark:#f3d78a}
*{box-sizing:border-box}
html,body{margin:0;height:100%;background:var(--panel);color:var(--ink);
 font:14px/1.5 "Futura","Century Gothic","Avenir Next","Gill Sans","Helvetica Neue",sans-serif;letter-spacing:.02em}
header{display:flex;justify-content:space-between;align-items:flex-end;gap:16px;padding:18px 28px 14px;background:var(--recess);border-bottom:1px solid var(--seam);position:relative}
header::after{content:"";position:absolute;left:0;right:0;top:0;height:3px;background:var(--accent)}
header a{color:var(--ink);text-decoration:none;font-size:10px;letter-spacing:.28em;text-transform:uppercase}
header h1{margin:6px 0 0;font-size:15px;font-weight:500;letter-spacing:.16em;text-transform:uppercase}
header .stamp{font-size:10px;letter-spacing:.32em;text-transform:uppercase;color:var(--accent)}
.desk{display:grid;grid-template-columns:320px 1fr;height:calc(100% - 68px)}
nav{overflow:auto;background:var(--recess);border-right:1px solid var(--seam);padding:0 0 32px;display:flex;flex-direction:column}
.search{position:sticky;top:0;background:var(--recess);padding:14px 18px 10px;border-bottom:1px solid var(--seam);z-index:2}
.search input{width:100%;padding:9px 11px;border:1px solid var(--seam);background:var(--paper);color:var(--ink);font:inherit;letter-spacing:.04em}
.search input:focus{outline:1px solid var(--accent);border-color:var(--accent)}
.search .count{margin-top:6px;font-size:10px;letter-spacing:.18em;text-transform:uppercase;color:#5a564c;display:flex;justify-content:space-between}
.search .count button{border:0;background:transparent;color:var(--accent);font:inherit;font-size:10px;letter-spacing:.18em;text-transform:uppercase;cursor:pointer;padding:0}
.dir-name{margin:18px 22px 6px;font-size:10px;letter-spacing:.28em;text-transform:uppercase;color:var(--accent)}
.file-item{display:block;width:100%;text-align:left;border:0;background:transparent;color:var(--ink);padding:7px 22px;cursor:pointer;font:inherit;letter-spacing:.04em;font-size:12px;overflow-wrap:anywhere}
.file-item:hover{background:var(--slot)}
.file-item.active{background:var(--ink);color:var(--paper)}
.file-item.dim{opacity:.35}
.file-item .meta{display:block;font-size:10px;letter-spacing:.12em;opacity:.6}
.file-item .hits{float:right;font-size:10px;letter-spacing:.12em;color:var(--accent)}
.file-item.active .hits{color:var(--mark)}
main{display:flex;flex-direction:column;min-width:0;background:var(--paper)}
#viewer-label{padding:8px 22px;border-bottom:1px solid var(--seam);font-size:10px;letter-spacing:.18em;text-transform:uppercase;color:#5a564c;background:var(--recess);display:flex;justify-content:space-between;gap:12px}
#viewer-label a{color:var(--accent);text-decoration:none}
#pages{flex:1;min-height:0;overflow:auto;padding:0 0 120px}
article{max-width:46em;margin:0 auto;padding:36px 32px 48px;border-bottom:1px solid var(--seam)}
article.hidden{display:none}
article .stamp{font-size:10px;letter-spacing:.3em;text-transform:uppercase;color:var(--accent);margin-bottom:6px}
article .blurb{font-style:italic;color:#4a463e;border-left:2px solid var(--seam);padding-left:12px;margin:10px 0 24px}
article .source{font-size:10px;letter-spacing:.12em;color:#5a564c;margin-bottom:22px;word-break:break-all}
article h1{font-size:20px;font-weight:500;letter-spacing:.06em;line-height:1.3;margin:0 0 6px}
article h2{font-size:15px;font-weight:600;letter-spacing:.08em;text-transform:uppercase;margin:2em 0 .6em;border-bottom:1px solid var(--seam);padding-bottom:4px}
article h3{font-size:14px;font-weight:600;margin:1.6em 0 .5em}
article h4,article h5{font-size:13px;margin:1.3em 0 .4em}
article p,article li{font-size:14px;line-height:1.6}
article pre{background:var(--recess);border:1px solid var(--seam);padding:12px 14px;overflow:auto;font:12px/1.5 "DejaVu Sans Mono",ui-monospace,Menlo,monospace}
article code{font:12px/1.5 "DejaVu Sans Mono",ui-monospace,Menlo,monospace;background:var(--recess);padding:1px 4px}
article pre code{background:transparent;padding:0}
article table{border-collapse:collapse;margin:14px 0;font-size:13px;max-width:100%;display:block;overflow:auto}
article th,article td{border:1px solid var(--seam);padding:5px 9px;vertical-align:top;text-align:left}
article th{background:var(--recess)}
article blockquote{margin:14px 0;padding:2px 14px;border-left:3px solid var(--accent);color:#4a463e}
article hr{border:0;border-top:1px solid var(--seam);margin:28px 0}
article img{max-width:100%}
mark{background:var(--mark);color:inherit;padding:0 1px}
mark.cur{outline:2px solid var(--accent)}
.foot{max-width:46em;margin:0 auto;padding:28px 32px 60px;font-size:11px;letter-spacing:.12em;color:#5a564c}
.foot a{color:var(--ink)}
@media (max-width:820px){.desk{grid-template-columns:1fr;height:auto}nav{max-height:40vh;border-right:0;border-bottom:1px solid var(--seam)}}
"""

JS = r"""
(function () {
  const docs = Array.from(document.querySelectorAll("article[data-id]"));
  const items = Array.from(document.querySelectorAll(".file-item[data-id]"));
  const input = document.getElementById("q");
  const countEl = document.getElementById("count");
  const clearBtn = document.getElementById("clear");
  const label = document.getElementById("current");
  const pages = document.getElementById("pages");
  const byId = {};
  docs.forEach((a) => { byId[a.dataset.id] = a; });
  const originals = new Map();
  docs.forEach((a) => originals.set(a, a.querySelector(".body").innerHTML));

  function escapeRe(s) { return s.replace(/[.*+?^${}()|[\]\\]/g, "\\$&"); }

  function clearMarks() {
    docs.forEach((a) => { a.querySelector(".body").innerHTML = originals.get(a); });
  }

  function markText(root, re) {
    let n = 0;
    const walker = document.createTreeWalker(root, NodeFilter.SHOW_TEXT, {
      acceptNode(node) {
        if (!node.nodeValue.trim()) return NodeFilter.FILTER_REJECT;
        const p = node.parentNode;
        if (p && (p.tagName === "SCRIPT" || p.tagName === "STYLE" || p.tagName === "MARK")) return NodeFilter.FILTER_REJECT;
        return NodeFilter.FILTER_ACCEPT;
      }
    });
    const nodes = [];
    while (walker.nextNode()) nodes.push(walker.currentNode);
    for (const node of nodes) {
      const text = node.nodeValue;
      re.lastIndex = 0;
      if (!re.test(text)) continue;
      re.lastIndex = 0;
      const frag = document.createDocumentFragment();
      let last = 0, m;
      while ((m = re.exec(text)) !== null) {
        frag.appendChild(document.createTextNode(text.slice(last, m.index)));
        const mk = document.createElement("mark");
        mk.textContent = m[0];
        frag.appendChild(mk);
        last = m.index + m[0].length;
        n++;
        if (m[0].length === 0) re.lastIndex++;
      }
      frag.appendChild(document.createTextNode(text.slice(last)));
      node.parentNode.replaceChild(frag, node);
    }
    return n;
  }

  let marks = [], cur = -1;

  function search(q) {
    clearMarks();
    marks = []; cur = -1;
    q = q.trim();
    if (!q) {
      docs.forEach((a) => a.classList.remove("hidden"));
      items.forEach((b) => { b.classList.remove("dim"); b.querySelector(".hits").textContent = ""; });
      countEl.textContent = docs.length + " documents";
      return;
    }
    const terms = q.split(/\s+/).filter(Boolean).map(escapeRe);
    const re = new RegExp(terms.join("|"), "gi");
    let total = 0, shown = 0;
    docs.forEach((a) => {
      const n = markText(a.querySelector(".body"), re)
              + markText(a.querySelector("h1"), re);
      const b = items.find((x) => x.dataset.id === a.dataset.id);
      if (n > 0) { a.classList.remove("hidden"); shown++; b.classList.remove("dim"); }
      else { a.classList.add("hidden"); b.classList.add("dim"); }
      b.querySelector(".hits").textContent = n ? n + "" : "";
      total += n;
    });
    marks = Array.from(pages.querySelectorAll("article:not(.hidden) mark"));
    countEl.textContent = total + " hits · " + shown + " of " + docs.length + " documents";
    if (marks.length) go(0);
  }

  // Scroll only the pages pane; scrollIntoView would drag the header away too.
  function reveal(el, where) {
    const pr = pages.getBoundingClientRect();
    const er = el.getBoundingClientRect();
    const offset = where === "center" ? (pages.clientHeight / 2 - er.height / 2) : 12;
    pages.scrollTop += er.top - pr.top - offset;
  }

  function go(i) {
    if (!marks.length) return;
    if (cur >= 0 && marks[cur]) marks[cur].classList.remove("cur");
    cur = (i + marks.length) % marks.length;
    marks[cur].classList.add("cur");
    reveal(marks[cur], "center");
    setCurrent(marks[cur].closest("article"));
  }

  function setCurrent(a) {
    if (!a) return;
    items.forEach((b) => b.classList.toggle("active", b.dataset.id === a.dataset.id));
    label.textContent = a.dataset.name + " · roll " + a.dataset.roll + " · " + a.dataset.score + "/50";
  }

  items.forEach((b) => b.addEventListener("click", () => {
    const a = byId[b.dataset.id];
    a.classList.remove("hidden");
    reveal(a, "start");
    setCurrent(a);
    history.replaceState(null, "", "#" + a.id);
  }));

  let t;
  input.addEventListener("input", () => { clearTimeout(t); t = setTimeout(() => search(input.value), 120); });
  input.addEventListener("keydown", (e) => {
    if (e.key === "Enter") { e.preventDefault(); go(e.shiftKey ? cur - 1 : cur + 1); }
    if (e.key === "Escape") { input.value = ""; search(""); }
  });
  clearBtn.addEventListener("click", () => { input.value = ""; search(""); input.focus(); });
  document.addEventListener("keydown", (e) => {
    if (e.key === "/" && document.activeElement !== input) { e.preventDefault(); input.focus(); }
  });

  // Keep the index in step with scroll position: the last visible article
  // whose top has passed the reading line is the current one.
  let raf = 0;
  pages.addEventListener("scroll", () => {
    if (raf) return;
    raf = requestAnimationFrame(() => {
      raf = 0;
      const line = pages.getBoundingClientRect().top + 80;
      let current = null;
      for (const a of docs) {
        if (a.classList.contains("hidden")) continue;
        if (a.getBoundingClientRect().top <= line) current = a; else break;
      }
      if (current) setCurrent(current);
    });
  }, { passive: true });

  countEl.textContent = docs.length + " documents";
  const q0 = new URLSearchParams(location.search).get("q");
  if (q0) { input.value = q0; search(q0); }
  else if (location.hash) {
    const a = document.getElementById(location.hash.slice(1));
    if (a && a.tagName === "ARTICLE") { reveal(a, "start"); setCurrent(a); }
  } else if (docs[0]) setCurrent(docs[0]);
})();
"""


def render(docs: list[dict]) -> str:
    total_words = sum(d["words"] for d in docs)
    nav = []
    for d in docs:
        nav.append(
            f'<button type="button" class="file-item" data-id="{d["id"]}">'
            f'<span class="hits"></span>'
            f'<span>{d["n"]:02d} · {html.escape(d["name"])}</span>'
            f'<span class="meta">roll {html.escape(d["roll"])} · {d["score"]}/50 · {d["words"]:,} words</span>'
            f'</button>'
        )
    arts = []
    for d in docs:
        arts.append(
            f'<article id="{d["id"]}" data-id="{d["id"]}" data-name="{html.escape(d["name"])}" '
            f'data-roll="{html.escape(d["roll"])}" data-score="{d["score"]}">'
            f'<div class="stamp">{d["n"]:02d} / {len(docs):02d} · roll {html.escape(d["roll"])} · score {d["score"]}/50</div>'
            f'<h1>{html.escape(d["title"])}</h1>'
            f'<div class="source">{html.escape(d["source"])} · {d["words"]:,} words</div>'
            f'<div class="blurb">{html.escape(d["blurb"])}</div>'
            f'<div class="body">{d["html"]}</div>'
            f'</article>'
        )
    today = date.today().isoformat()
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>HOW_TO stack — {len(docs)} documents</title>
<style>{CSS}</style>
</head>
<body>
<header>
  <div>
    <a href="/">Station directory</a>
    <h1>HOW_TO stack</h1>
  </div>
  <div class="stamp">{len(docs)} documents · {total_words:,} words · d20 order · built {today}</div>
</header>
<div class="desk">
  <nav>
    <div class="search">
      <input id="q" type="search" placeholder="search all {len(docs)} HOW_TOs  (/ to focus, Enter = next hit)" autocomplete="off" spellcheck="false">
      <div class="count"><span id="count">{len(docs)} documents</span><button type="button" id="clear">clear</button></div>
    </div>
    <div class="dir-name">Index</div>
    {''.join(nav)}
  </nav>
  <main>
    <div id="viewer-label"><span id="current">HOW_TO stack</span><a href="/m/reality-user-manual/">the book</a></div>
    <div id="pages">
      {''.join(arts)}
      <div class="foot">Order: roll(n) = ((n × 7) + 13) mod 20 + 1, declared in <code>MANIFEST_HOW_TO_PORTALVISION_20261024.md</code>. Scores are the composer reports, median 37.5/50. Sources are the canonical PortalVision files, converted and not rewritten. The bound volume carries the desk stamp (page −09) and this file as an attachment. The live desk is the distribution.</div>
    </div>
  </main>
</div>
<script>{JS}</script>
</body>
</html>
"""


def main() -> Path:
    docs = build_docs()
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    OUT.write_text(render(docs), encoding="utf-8")
    (OUT_DIR / "how_tos.json").write_text(json.dumps([
        {k: d[k] for k in ("n", "name", "title", "roll", "score", "words", "source")}
        for d in docs
    ], indent=2) + "\n", encoding="utf-8")
    words = sum(d["words"] for d in docs)
    print(f"Wrote {OUT.relative_to(BASE)}  ({OUT.stat().st_size:,} bytes, {len(docs)} docs, {words:,} words)")
    return OUT


if __name__ == "__main__":
    main()
