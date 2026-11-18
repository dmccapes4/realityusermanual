#!/usr/bin/env python3
"""
Renderer for REALITY_USER_MANUAL video plates.

Does not invent shots. Reads a shot JSONL and calls the image API.

  Character plates  → OpenAI gpt-image-1, background=transparent, PNG
  Background plates → OpenAI gpt-image-1, background=opaque, 16:9 PNG

Style lock + stamper face reference are prepended to every prompt.
Default is --dry-run (writes the request payload, spends nothing).

  OPENAI_API_KEY=... .venv/bin/python tools/render_stills.py --dry-run
  OPENAI_API_KEY=... .venv/bin/python tools/render_stills.py --shot video/catalogs/shots.jsonl --only oak_grimoire
  OPENAI_API_KEY=... .venv/bin/python tools/render_stills.py --shot video/catalogs/shots.jsonl

Get a key at https://platform.openai.com/api-keys
gpt-image-1 is the renderer because transparent PNG is a first-class
parameter — characters must composite. Recraft remains the fallback if
we later need a locked style_id; do not add a second look before the
shot list is finished.
"""

from __future__ import annotations

import argparse
import base64
import json
import os
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
VIDEO = BASE / "video"
LOCK_PATH = VIDEO / "STYLE_LOCK.md"
STAMPER = VIDEO / "stills" / "characters" / "stamper.png"
SHOTS_DEFAULT = VIDEO / "catalogs" / "shots.jsonl"

# Load .env without printing values
_env = BASE / ".env"
if _env.exists():
    for line in _env.read_text().splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, _, v = line.partition("=")
            os.environ.setdefault(k.strip(), v.strip())

OPENAI = "https://api.openai.com/v1/images/generations"
OPENAI_EDITS = "https://api.openai.com/v1/images/edits"
MODEL = "gpt-image-1.5"

STYLE_PREFIX = """Cartoon but realistic. Refined Samurai Jack still.
Bold lampblack ink, flat limited palette, paper-tooth grit.
Lifted cream/bone midtones — daylight or soft interior light, not crushed noir.
Cream/bone, rust, one accent only. Outdoor green allowed for Numenor hill.
Refined ink face (astronaut-Jack register): readable features, not photoreal, not a slit-mask.
No anime eyes, no glossy CGI, no cinematic blur, no collage of film stills.
"""


def load_jsonl(path: Path) -> list[dict]:
    if not path.exists():
        return []
    return [json.loads(l) for l in path.read_text().splitlines() if l.strip()]


def locked_prompt(row: dict) -> str:
    parts = [STYLE_PREFIX, row.get("prompt", "").strip()]
    if row.get("resemble"):
        parts.append(f"The figure must resemble {row['resemble']}. Recognizable. Not a generic type.")
    if row.get("layer") == "character":
        parts.append("Full figure or 3/4 on a TRANSPARENT background. No floor, no room, no drop shadow that implies a set. PNG cutout for compositing.")
    if row.get("layer") == "background":
        parts.append("16:9 place. Empty of speaking characters. Architecture and light only.")
    if row.get("layer") in {"prop", "fx"}:
        parts.append("Single object or effect on a TRANSPARENT background. No environment.")
    if row.get("text_in_frame"):
        parts.append(f"In-frame text exactly: {row['text_in_frame']}")
    if row.get("unnumbered"):
        parts.append("No page number, no folio, no running header.")
    return "\n".join(p for p in parts if p)


def payload_for(row: dict) -> dict:
    layer = row.get("layer", "character")
    if layer == "background":
        size = row.get("size", "1536x1024")
        background = "opaque"
    else:
        size = row.get("size", "1024x1536")
        background = "transparent"
    return {
        "model": MODEL,
        "prompt": locked_prompt(row),
        "size": size,
        "background": background,
        "quality": row.get("quality", "high"),
        "output_format": "png",
        "n": 1,
    }


def dest_for(row: dict) -> Path:
    rel = row.get("file")
    if not rel:
        raise SystemExit(f"shot {row.get('id')} has no file")
    return BASE / rel


def ref_path(row: dict) -> Path | None:
    rel = row.get("edit_from")
    if rel:
        p = BASE / rel
        return p if p.exists() else None
    if row.get("character") == "stamper" and STAMPER.exists():
        return STAMPER
    return None


def render(row: dict, dry: bool, skip_existing: bool = True) -> Path | None:
    dest = dest_for(row)
    dest.parent.mkdir(parents=True, exist_ok=True)
    payload = payload_for(row)
    ref = ref_path(row)
    meta = dest.with_suffix(".request.json")
    recorded = dict(payload)
    if ref:
        recorded["edit_from"] = str(ref.relative_to(BASE))
    meta.write_text(json.dumps(recorded, indent=2) + "\n")
    if skip_existing and dest.exists() and dest.stat().st_size > 1000:
        print(f"  [skip] {row.get('id')} → {dest}  already rendered", flush=True)
        return dest
    if dry:
        extra = f"  edit={ref.name}" if ref else ""
        print(f"  [dry] {row.get('id')} → {dest}  ({payload['background']}, {payload['size']}){extra}", flush=True)
        return None

    key = os.environ.get("OPENAI_API_KEY", "").strip()
    if not key:
        sys.exit("Set OPENAI_API_KEY (or put it in .env). Dry-run works without it.")

    try:
        import requests
    except ImportError:
        sys.exit("requests missing. .venv/bin/pip install requests")

    if ref:
        with ref.open("rb") as fh:
            r = requests.post(
                OPENAI_EDITS,
                headers={"Authorization": f"Bearer {key}"},
                data={
                    "model": payload["model"],
                    "prompt": payload["prompt"],
                    "size": payload["size"],
                    "background": payload["background"],
                    "quality": payload["quality"],
                    "output_format": payload["output_format"],
                    "n": "1",
                },
                files={"image": (ref.name, fh, "image/png")},
                timeout=180,
            )
    else:
        r = requests.post(
            OPENAI,
            headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
            json=payload,
            timeout=180,
        )
    if r.status_code != 200:
        print(f"  [fail] {row.get('id')}: {r.status_code} {r.text[:400]}", flush=True)
        return None
    data = r.json()
    b64 = data["data"][0].get("b64_json")
    if not b64:
        print(f"  [fail] {row.get('id')}: no b64_json", flush=True)
        return None
    dest.write_bytes(base64.b64decode(b64))
    print(f"  [ok] {row.get('id')} → {dest}  {dest.stat().st_size} bytes", flush=True)
    return dest


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--shot", type=Path, default=SHOTS_DEFAULT, help="shots.jsonl")
    ap.add_argument("--only", help="comma ids to render")
    ap.add_argument("--priority", type=int, help="only this priority (1 template, 2 bg, 3 state, 4 fx)")
    ap.add_argument("--layer", help="only this layer (character, background, prop, fx)")
    ap.add_argument("--dry-run", action="store_true", help="write payloads only (default if no --render)")
    ap.add_argument("--render", action="store_true", help="call the API (spends credits)")
    ap.add_argument("--force", action="store_true", help="re-render even if the PNG exists")
    args = ap.parse_args()

    dry = not args.render
    rows = load_jsonl(args.shot)
    if not rows:
        print(f"no shots in {args.shot}")
        print("Composer reports land in video/composer-reports/.")
        print("Assemble them into video/catalogs/shots.jsonl before rendering.")
        return

    if args.only:
        want = {s.strip() for s in args.only.split(",")}
        rows = [r for r in rows if r.get("id") in want]
    if args.priority is not None:
        rows = [r for r in rows if r.get("priority") == args.priority]
    if args.layer:
        rows = [r for r in rows if r.get("layer") == args.layer]

    by_p: dict[int, int] = {}
    by_l: dict[str, int] = {}
    for r in rows:
        by_p[r.get("priority", 0)] = by_p.get(r.get("priority", 0), 0) + 1
        by_l[r.get("layer", "?")] = by_l.get(r.get("layer", "?"), 0) + 1
    print(f"{'DRY RUN' if dry else 'RENDER'}  {len(rows)} shot(s)  model={MODEL}")
    print(f"  priority {by_p}  layer {by_l}")
    print(f"  face reference (manual): {STAMPER}")
    print(f"  get a key: https://platform.openai.com/api-keys")
    for row in rows:
        render(row, dry=dry, skip_existing=not args.force)


if __name__ == "__main__":
    main()
