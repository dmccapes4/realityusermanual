#!/usr/bin/env python3
"""Render PHASE 2 manuscript pages to static HTML under web/p/."""
from __future__ import annotations

import argparse
import html
import re
from pathlib import Path

import markdown

BASE = Path(__file__).resolve().parent.parent
SRC = BASE / "src" / "phase2"
SRC_ROOT = BASE / "src"   # fallback for pages living directly in src/
WEB = BASE / "web" / "p"

SHELL = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title} — REALITY_USER_MANUAL</title>
<link rel="stylesheet" href="/desk.css">
<style>
.page-wrap {{ max-width: 46em; margin: 0 auto; padding: 28px 28px 96px; }}
.page-wrap h1 {{ font-size: 1.1rem; letter-spacing: 0.14em; text-transform: uppercase; }}
.page-wrap h2 {{ font-size: 0.95rem; margin-top: 2em; letter-spacing: 0.1em; }}
.page-nav {{ font-size: 10px; letter-spacing: 0.22em; text-transform: uppercase; margin-bottom: 24px; }}
.page-nav a {{ color: var(--accent); }}
.page-body {{ line-height: 1.55; letter-spacing: 0.02em; }}
.page-body pre {{ overflow: auto; padding: 12px; background: var(--recess); border: 1px solid var(--seam); }}
.page-body code {{ font-size: 0.92em; }}
.page-body table {{ border-collapse: collapse; width: 100%; margin: 1em 0; font-size: 0.92em; }}
.page-body th, .page-body td {{ border: 1px solid var(--seam); padding: 6px 8px; text-align: left; }}
.listen-cta {{ margin-top: 2em; padding: 14px 16px; background: var(--recess); border: 1px solid var(--seam); font-size: 11px; letter-spacing: 0.12em; }}
</style>
</head>
<body>
<div class="page-wrap">
  <p class="page-nav"><a href="/">Station</a> · <a href="/listen/">Listen</a>{listen_link}</p>
  <div class="page-body">
{body}
  </div>
{listen_cta}
</div>
</body>
</html>
"""


def page_id(stem: str) -> str:
    return "minus" + stem.lstrip("-")


SHOWN_AS = {"LISBETH_EN": "Lisbeth (English)", "NARRATOR_EN": "Narrator (English)",
            "DOCTOR_DRAKE": "Doctor Drake", "SCAPE": "SCAPE"}


def readable(text: str) -> str:
    """Narration-format pages: drop the video cues, show speaker labels as names."""
    out, fence = [], False
    for line in text.split("\n"):
        s = line.strip()
        if re.fullmatch(r"```[\w-]*", s):
            fence = not fence
        if not fence:
            if re.fullmatch(r"~~(FRAME|STATE|SCRATCH):[^~]+~~", s):
                continue
            line = re.sub(r"^\*\*([A-Z][A-Z_]+):\*\*",
                          lambda m: f"**{SHOWN_AS.get(m.group(1), m.group(1).title())}:**", line)
        out.append(line)
    return "\n".join(out)


def build(stem: str, listen_id: str | None = None) -> Path:
    if not stem.startswith("-"):
        stem = f"-{stem}"
    src = SRC / f"{stem}.md"
    if not src.exists():
        src = SRC_ROOT / f"{stem}.md"   # try src/ directly (e.g. -35.md)
    if not src.exists():
        raise SystemExit(f"missing {src}")
    text = readable(src.read_text(encoding="utf-8"))
    title_m = re.search(r"^#\s+(.+)$", text, re.M)
    title = title_m.group(1).strip() if title_m else f"Page {stem}"
    body = markdown.markdown(
        text,
        extensions=["tables", "fenced_code", "nl2br", "sane_lists"],
    )
    lid = listen_id or page_id(stem)
    listen_link = f' · <a href="/listen/play.html?id={html.escape(lid)}">Listen</a>'
    listen_cta = (
        f'<p class="listen-cta"><a href="/listen/play.html?id={html.escape(lid)}">'
        f"Listen to page {html.escape(stem)}</a> (still + audio on the desk)</p>"
        if lid
        else ""
    )
    out = WEB / stem / "index.html"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(
        SHELL.format(
            title=html.escape(title),
            body=body,
            listen_link=listen_link,
            listen_cta=listen_cta,
        ),
        encoding="utf-8",
    )
    print(f"  {out.relative_to(BASE)}")
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("pages", nargs="+", help="Page stems, e.g. -31 -30")
    args = ap.parse_args()
    for p in args.pages:
        build(p)


if __name__ == "__main__":
    main()
