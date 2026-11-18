#!/usr/bin/env python3
"""Emit early book leaves from src markdown + spreads.json spine head."""
from __future__ import annotations

import html
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LEAVES = ROOT / "web" / "book" / "leaves"
SPREADS = ROOT / "web" / "book" / "spreads.json"

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
  margin: 0; min-height: 100%;
  background: var(--parchment); color: var(--ink);
  font: 16px/1.65 var(--font);
}
.leaf { max-width: 38em; margin: 0 auto; padding: 28px 22px 64px; }
.stamp {
  font-size: 10px; letter-spacing: 0.22em; text-transform: uppercase;
  color: var(--accent); margin-bottom: 10px;
}
h1 { font-size: 1.35rem; letter-spacing: 0.04em; margin: 0 0 1em; }
.poem { white-space: pre-wrap; font-size: 1.05rem; }
.prose p { margin: 0 0 0.9em; }
.quiet { font-size: 0.85rem; color: var(--muted); margin-top: 2em; }
.folio { float: right; font-size: 0.8rem; color: var(--muted); }
a { color: var(--accent); }
"""


def wrap(title: str, stamp: str, body: str, folio: str | None = None) -> str:
    folio_html = f'<span class="folio">{html.escape(folio)}</span>' if folio else ""
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(title)}</title>
<style>{LEAF_CSS}</style>
</head>
<body>
<article class="leaf">
  {folio_html}
  <div class="stamp">{html.escape(stamp)}</div>
  <h1>{html.escape(title)}</h1>
  {body}
</article>
</body>
</html>
"""


def md_poem_body(path: Path) -> str:
    raw = path.read_text(encoding="utf-8")
    # Drop HTML comments for display; keep verse as pre
    raw = re.sub(r"<!--.*?-->", "", raw, flags=re.S).strip()
    return f'<div class="poem">{html.escape(raw)}</div>'


def write_bththk() -> None:
    body = """
<div class="prose">
  <p style="text-align:center;font-size:4.5rem;letter-spacing:0.12em;margin:2.5em 0 1em;cursor:pointer"
     id="glyph">BΘΘΚ</p>
  <p class="quiet" style="text-align:center">Click the word. The cover waits on the other side of the threshold.</p>
</div>
<script>
document.getElementById('glyph').addEventListener('click', () => {
  window.parent.postMessage({ type: 'book-advance', to: 'cover' }, '*');
});
</script>
"""
    (LEAVES / "bththk.html").write_text(
        wrap("BΘΘΚ", "BOOK · PRE-COVER", body), encoding="utf-8"
    )


def write_cover_left() -> None:
    body = """
<div class="prose">
  <p><strong>REALITY_USER_MANUAL</strong></p>
  <p>mischievouslittlechicken</p>
  <p>The rabbit hole is on the facing plate. Turn the spread when you are ready for Velora.</p>
  <p class="quiet">Cover still: PDF page 1. Live link on the right leaf.</p>
</div>
"""
    (LEAVES / "cover.html").write_text(
        wrap("Cover", "BOOK · COVER", body), encoding="utf-8"
    )


def merge_spreads_head() -> None:
    head = [
        {"id": "bththk", "kind": "title_gate", "glyph": "BΘΘΚ", "html": "/book/leaves/bththk.html", "right": {"type": "void"}},
        {
            "id": "cover",
            "kind": "cover",
            "html": "/book/leaves/cover.html",
            "right": {
                "type": "cover",
                "url": "/book/assets/cover.png",
                "link": "https://sacredthebes.dylanmccapes.systems?hello-world",
            },
        },
        {
            "id": "000",
            "title": "Velora",
            "html": "/book/leaves/000.html",
            "right": {"type": "audio", "label": "Narration", "url": None},
        },
        {
            "id": "001",
            "title": "Quenya",
            "folio": 42,
            "toc": False,
            "html": "/book/leaves/001.html",
            "right": {"type": "sidereal_board"},
        },
        {
            "id": "rho-run",
            "kind": "reversed_hallway",
            "title": "rho (reversed)",
            "source": "src/003_rho/rho_definition_words.py",
            "html": "/book/leaves/rho_run.html",
            "right": {"type": "hallway_plaque"},
        },
    ]
    if SPREADS.exists():
        data = json.loads(SPREADS.read_text(encoding="utf-8"))
    else:
        data = {"spreads": []}
    spreads = data.setdefault("spreads", [])
    # Drop prior head ids then prepend
    drop = {"bththk", "cover", "000", "001", "rho-run"}
    spreads[:] = [s for s in spreads if s.get("id") not in drop]
    data["spreads"] = head + spreads
    SPREADS.parent.mkdir(parents=True, exist_ok=True)
    SPREADS.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def write_rho_run_stub() -> None:
    # Lightweight leaf; book.js drives the plaque from ITEMS
    body = """
<div class="prose">
  <p>Reversed-word run after page 42. One plaque at a time on the facing corridor.</p>
  <p class="quiet">Source: <code>src/003_rho/rho_definition_words.py</code> — 40 steps. Next advances. Hold reveals upright English for this step only.</p>
</div>
"""
    (LEAVES / "rho_run.html").write_text(
        wrap("rho — reversed hallway", "BOOK · AFTER 42", body), encoding="utf-8"
    )


def main() -> None:
    LEAVES.mkdir(parents=True, exist_ok=True)
    write_bththk()
    write_cover_left()
    velora = ROOT / "src/000_velora/000_velora_poem.md"
    quenya = ROOT / "src/001_quenya/001_quenya_poem.md"
    (LEAVES / "000.html").write_text(
        wrap("Velora", "000 · POEM", md_poem_body(velora)), encoding="utf-8"
    )
    (LEAVES / "001.html").write_text(
        wrap("Quenya", "001 · PAGE 42 (not in TOC)", md_poem_body(quenya), folio="42"),
        encoding="utf-8",
    )
    write_rho_run_stub()
    merge_spreads_head()
    print("✓ leaves: bththk, cover, 000, 001, rho_run")
    print(f"✓ {SPREADS}")


if __name__ == "__main__":
    main()
