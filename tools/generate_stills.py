#!/usr/bin/env python3
"""
Style-locked stills for REALITY_USER_MANUAL video.

The script does not invent a look per call. Every prompt is STYLE_LOCK + the
catalog row. Soft construction, heavy presence. Refined Samurai Jack / noir.

Usage:
  .venv/bin/python tools/generate_stills.py --verify
  .venv/bin/python tools/generate_stills.py --dump-prompts
  .venv/bin/python tools/generate_stills.py --collect

Images are generated with the locked prompt (Cursor GenerateImage or a later
hook). --collect copies any matching filenames into video/stills/.
--verify fails if a catalog row has no file.
"""

from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
VIDEO = BASE / "video"
CAT = VIDEO / "catalogs"
STILLS = VIDEO / "stills"

STYLE_LOCK = """Refined Samurai Jack still, gritty bizarre sci-fi noir.
Bold lampblack ink silhouettes, flat limited palette, paper-tooth grit, hard noir shadows.
Cream/bone ground, rust, one accent only.
No photorealism, no anime eyes, no 3D render, no glossy CGI, no cinematic blur, no collage of existing actors.
Soft in construction (few large shapes), heavy in presence.
Empty background or one architectural slab."""


def load_jsonl(path: Path) -> list[dict]:
    rows = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line:
            rows.append(json.loads(line))
    return rows


def catalogs() -> dict[str, list[dict]]:
    return {
        "characters": load_jsonl(CAT / "characters.jsonl"),
        "locations": load_jsonl(CAT / "locations.jsonl"),
        "props": load_jsonl(CAT / "props.jsonl"),
    }


def locked_prompt(row: dict) -> str:
    accent = row.get("accent", "")
    text = row.get("text_in_frame", "")
    parts = [STYLE_LOCK, "", "Subject: " + row["prompt"]]
    if accent:
        parts.append(f"Single accent color: {accent}. No second accent.")
    if text:
        parts.append(f"In-frame text exactly: {text}")
    if row.get("unnumbered"):
        parts.append("No page number, no folio, no running header.")
    return "\n".join(parts)


def dump_prompts():
    for kind, rows in catalogs().items():
        print(f"\n## {kind}")
        for row in rows:
            print(f"\n### {row['id']} → {row['file']}")
            print(locked_prompt(row))


def verify() -> int:
    missing = []
    present = []
    for kind, rows in catalogs().items():
        for row in rows:
            path = BASE / row["file"]
            if path.exists() and path.stat().st_size > 1000:
                present.append(row["file"])
            else:
                missing.append(row["file"])
    print(f"present {len(present)}  missing {len(missing)}")
    for m in missing:
        print(f"  MISS {m}")
    return 1 if missing else 0


def collect():
    """Copy generated files into catalog paths by stem (.png or .jpg)."""
    wanted = {}
    for rows in catalogs().values():
        for row in rows:
            dest = BASE / row["file"]
            wanted[dest.stem] = dest
    wanted["style_key"] = STILLS / "style_key.png"

    search_roots = [
        BASE,
        Path.home() / ".cursor" / "projects" / "home-dylanmccapes-dev" / "assets",
    ]
    copied = 0
    for root in search_roots:
        if not root.exists():
            continue
        for found in root.rglob("*"):
            if found.suffix.lower() not in {".png", ".jpg", ".jpeg"}:
                continue
            dest = wanted.get(found.stem)
            if dest is None:
                continue
            dest.parent.mkdir(parents=True, exist_ok=True)
            if found.resolve() == dest.resolve():
                continue
            if found.suffix.lower() != ".png":
                from PIL import Image
                Image.open(found).convert("RGB").save(dest, "PNG")
            else:
                shutil.copy2(found, dest)
            print(f"  collect {found.name} → {dest}")
            copied += 1
    print(f"collected {copied}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--verify", action="store_true")
    ap.add_argument("--dump-prompts", action="store_true")
    ap.add_argument("--collect", action="store_true")
    args = ap.parse_args()
    if args.dump_prompts:
        dump_prompts()
        return
    if args.collect:
        collect()
    code = verify() if args.verify or args.collect else 0
    if not (args.verify or args.dump_prompts or args.collect):
        dump_prompts()
        print("\nGenerate each prompt with the style lock intact, then --collect --verify.")
    sys.exit(code)


if __name__ == "__main__":
    main()
