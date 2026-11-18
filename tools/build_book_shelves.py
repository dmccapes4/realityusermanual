#!/usr/bin/env python3
"""Build book shelf spreads: How_tos + Manuscripts before Phase 2.

Left leaf = scrollable TOC with 1–2 sentence blurbs from data.json.
Right leaf = embed of how_tos/index.html and manuscripts/index.html
copied under web/book/embed/ so deploy (web/ sync) serves them.

Run: .venv/bin/python tools/build_book_shelves.py
"""
from __future__ import annotations

import json
import re
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BOOK = ROOT / "web" / "book"
LEAVES = BOOK / "leaves"
EMBED = BOOK / "embed"

HOWTO_SRC = ROOT / "how_tos"
MS_SRC = ROOT / "manuscripts"

META_SKIP = re.compile(
    r"^\*\*(Type|Status|Date|Audience|Author|Perspective|Context|"
    r"Classification|Subtitle|Version|Package|Tone|Where|What|Source|"
    r"Filed|Operator)\*\*",
    re.I,
)


def sentences(text: str, n: int = 2, max_chars: int = 280) -> str:
    """Take up to n sentences; strip markdown noise."""
    if not text:
        return ""
    lines = []
    for raw in text.replace("\r\n", "\n").split("\n"):
        line = raw.strip()
        if not line:
            if lines:
                break
            continue
        if META_SKIP.match(line):
            continue
        if line.startswith("#"):
            continue
        if line.startswith("---"):
            continue
        line = re.sub(r"\*\*([^*]+)\*\*", r"\1", line)
        line = re.sub(r"\*([^*]+)\*", r"\1", line)
        line = re.sub(r"`([^`]+)`", r"\1", line)
        line = line.strip(" \t-•")
        if line:
            lines.append(line)
    blob = " ".join(lines)
    parts = re.split(r"(?<=[.!?])\s+", blob)
    out = " ".join(parts[:n]).strip()
    if len(out) > max_chars:
        cut = out[: max_chars - 1].rsplit(" ", 1)[0]
        out = cut + "…"
    return out


def humanize_howto(name: str) -> str:
    return name.replace("HOW_TO_", "").replace("_", " ").strip().lower()


LEAF_CSS = """
:root {
  --ink: #1a1410;
  --parchment: #f3ead7;
  --rule: #c4b59a;
  --accent: #6b3a22;
  --muted: #6a5c4a;
  --font: "Palatino Linotype", "Book Antiqua", Palatino, Georgia, serif;
}
* { box-sizing: border-box; }
html, body {
  margin: 0; height: 100%;
  background: var(--parchment); color: var(--ink);
  font: 15px/1.55 var(--font);
}
header {
  position: sticky; top: 0; z-index: 2;
  background: var(--parchment);
  border-bottom: 1px solid var(--rule);
  padding: 14px 18px 10px;
}
header .stamp {
  font-size: 10px; letter-spacing: 0.22em; text-transform: uppercase;
  color: var(--accent);
}
header h1 {
  margin: 4px 0 0; font-size: 18px; font-weight: 600; letter-spacing: 0.04em;
}
header p {
  margin: 6px 0 0; font-size: 13px; color: var(--muted); max-width: 36em;
}
.toc { padding: 8px 12px 48px; }
.row {
  display: block; width: 100%; text-align: left;
  border: 1px solid transparent; border-bottom-color: var(--rule);
  background: transparent; color: inherit; font: inherit;
  padding: 12px 10px; cursor: pointer;
}
.row:hover, .row.active {
  border-color: var(--accent); background: rgba(107, 58, 34, 0.06);
}
.row .title {
  color: var(--accent); font-size: 14px; letter-spacing: 0.03em;
}
.row .venue {
  font-size: 11px; color: var(--muted); letter-spacing: 0.08em;
  text-transform: uppercase; margin-top: 2px;
}
.row .blurb {
  margin-top: 6px; font-size: 13px; color: var(--ink); opacity: 0.88;
}
"""


def write_toc_leaf(
    path: Path,
    *,
    stamp: str,
    title: str,
    intro: str,
    rows: list[dict],
    embed_path: str,
) -> None:
    items = []
    for r in rows:
        venue = f'<div class="venue">{_esc(r.get("venue") or "")}</div>' if r.get("venue") else ""
        items.append(
            f'<button type="button" class="row" data-id="{_esc(r["id"])}">'
            f'<div class="title">{_esc(r["title"])}</div>'
            f"{venue}"
            f'<div class="blurb">{_esc(r["blurb"])}</div>'
            f"</button>"
        )
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{_esc(title)} — book shelf TOC</title>
<style>{LEAF_CSS}</style>
</head>
<body>
<header>
  <div class="stamp">{_esc(stamp)}</div>
  <h1>{_esc(title)}</h1>
  <p>{_esc(intro)}</p>
</header>
<nav class="toc" id="toc">
{"".join(items)}
</nav>
<script>
const EMBED = {json.dumps(embed_path)};
document.getElementById('toc').addEventListener('click', (e) => {{
  const row = e.target.closest('.row');
  if (!row) return;
  document.querySelectorAll('.row').forEach(el => el.classList.toggle('active', el === row));
  // Parent book chrome may listen; also nudge embed via postMessage.
  const id = row.dataset.id;
  window.parent.postMessage({{ type: 'book-shelf-select', shelf: EMBED, id }}, '*');
  try {{
    const frame = window.parent.document.querySelector('iframe[data-shelf-embed]');
    if (frame && frame.contentWindow) {{
      frame.contentWindow.postMessage({{ type: 'book-shelf-select', id }}, '*');
    }}
  }} catch (_) {{}}
}});
</script>
</body>
</html>
"""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(html, encoding="utf-8")


def _esc(s: str) -> str:
    return (
        (s or "")
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def copy_embed(src_dir: Path, dest_dir: Path, files: list[str]) -> None:
    dest_dir.mkdir(parents=True, exist_ok=True)
    for name in files:
        src = src_dir / name
        if not src.exists():
            raise SystemExit(f"missing {src}")
        shutil.copy2(src, dest_dir / name)


def patch_spreads(howto_leaf: str, ms_leaf: str) -> None:
    spreads_path = BOOK / "spreads.json"
    if spreads_path.exists():
        data = json.loads(spreads_path.read_text(encoding="utf-8"))
    else:
        data = {"spreads": []}

    spreads = data.setdefault("spreads", [])
    by_id = {s.get("id"): i for i, s in enumerate(spreads)}

    shelf_how = {
        "id": "how_tos",
        "title": "How_tos",
        "kind": "shelf_toc",
        "html": howto_leaf,
        "right": {"type": "embed", "url": "/book/embed/how_tos/"},
    }
    shelf_ms = {
        "id": "manuscripts",
        "title": "Manuscripts",
        "kind": "shelf_toc",
        "html": ms_leaf,
        "right": {"type": "embed", "url": "/book/embed/manuscripts/"},
    }
    cta = {
        "id": "enter_phase2",
        "kind": "cta",
        "label": "Enter Phase 2",
        "href": "/gate/",
    }

    # Remove old shelf/cta entries then append after 007 (or at end).
    spreads[:] = [
        s
        for s in spreads
        if s.get("id") not in {"how_tos", "manuscripts", "enter_phase2"}
    ]
    insert_at = len(spreads)
    for i, s in enumerate(spreads):
        if s.get("id") == "007":
            insert_at = i + 1
            break
    spreads[insert_at:insert_at] = [shelf_how, shelf_ms, cta]
    spreads_path.parent.mkdir(parents=True, exist_ok=True)
    spreads_path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    howto_data = json.loads((HOWTO_SRC / "data.json").read_text(encoding="utf-8"))
    ms_data = json.loads((MS_SRC / "data.json").read_text(encoding="utf-8"))

    howto_rows = []
    for ht in howto_data["how_tos"]:
        howto_rows.append(
            {
                "id": ht["id"],
                "title": humanize_howto(ht.get("name") or ht["id"]),
                "blurb": sentences(ht.get("description") or "")
                or "Operational document in the how_to stack.",
            }
        )

    ms_rows = []
    for ms in ms_data["manuscripts"]:
        ms_rows.append(
            {
                "id": ms["id"],
                "title": ms.get("name") or ms["id"],
                "venue": ms.get("venue") or "",
                "blurb": sentences(ms.get("description") or "")
                or "Manuscript packet on the receiving desk.",
            }
        )

    write_toc_leaf(
        LEAVES / "how_tos.html",
        stamp="BOOK · AFTER 007 · BEFORE PHASE 2",
        title="How_tos",
        intro="Scrollable catalog. One or two sentences each. The facing leaf is the live index.",
        rows=howto_rows,
        embed_path="/book/embed/how_tos/",
    )
    write_toc_leaf(
        LEAVES / "manuscripts.html",
        stamp="BOOK · LAST SHELF BEFORE PHASE 2",
        title="Manuscripts",
        intro="Venue-shaped packets. Blurbs on this leaf; the facing leaf is the live manuscripts index.",
        rows=ms_rows,
        embed_path="/book/embed/manuscripts/",
    )

    copy_embed(HOWTO_SRC, EMBED / "how_tos", ["index.html", "data.json"])
    # threl.html is linked from how_tos index — copy if present
    if (HOWTO_SRC / "threl.html").exists():
        shutil.copy2(HOWTO_SRC / "threl.html", EMBED / "how_tos" / "threl.html")

    copy_embed(MS_SRC, EMBED / "manuscripts", ["index.html", "data.json"])

    # Fix relative data URLs already correct (data.json beside index).
    patch_spreads("/book/leaves/how_tos.html", "/book/leaves/manuscripts.html")

    blurbs = {
        "how_tos": howto_rows,
        "manuscripts": ms_rows,
    }
    (BOOK / "shelf_blurbs.json").write_text(
        json.dumps(blurbs, indent=2) + "\n", encoding="utf-8"
    )
    print(f"✓ how_tos TOC ({len(howto_rows)}) → {LEAVES / 'how_tos.html'}")
    print(f"✓ manuscripts TOC ({len(ms_rows)}) → {LEAVES / 'manuscripts.html'}")
    print(f"✓ embed → {EMBED / 'how_tos'}, {EMBED / 'manuscripts'}")
    print(f"✓ spreads.json shelves after 007 + enter_phase2 CTA")


if __name__ == "__main__":
    main()
