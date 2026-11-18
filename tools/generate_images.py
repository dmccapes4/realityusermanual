#!/usr/bin/env python3
"""Generate background and portrait images for the −08 viewer.

Reads images/minus08/scenes.jsonl and images/minus08/portraits.jsonl.
For each record: hash-checks the output path, skips if file exists.
Otherwise calls OpenAI DALL-E 3.

Usage:
  .venv/bin/python tools/generate_images.py               # all
  .venv/bin/python tools/generate_images.py --portraits   # portraits only
  .venv/bin/python tools/generate_images.py --scenes      # backgrounds only
  .venv/bin/python tools/generate_images.py --dry-run     # print prompts, no API call
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent

# Load .env
_env = BASE / ".env"
if _env.exists():
    for _line in _env.read_text().splitlines():
        _line = _line.strip()
        if _line and not _line.startswith("#") and "=" in _line:
            k, _, v = _line.partition("=")
            os.environ.setdefault(k.strip(), v.strip())

API_KEY = os.environ.get("OPENAI_API_KEY", "").strip()
if not API_KEY:
    sys.exit("Set OPENAI_API_KEY in .env or environment.")

try:
    import requests
except ImportError:
    sys.exit("requests not installed: .venv/bin/pip install requests")

IMG_DIR = BASE / "images" / "minus08"
SCENES_PATH = IMG_DIR / "scenes.jsonl"
PORTRAITS_PATH = IMG_DIR / "portraits.jsonl"

OPENAI_URL = "https://api.openai.com/v1/images/generations"
HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json",
}


def load_jsonl(path: Path) -> list[dict]:
    if not path.exists():
        return []
    return [json.loads(l) for l in path.read_text().splitlines() if l.strip()]


def generate_image(
    prompt: str,
    out_path: Path,
    size: str = "1792x1024",
    dry_run: bool = False,
) -> bool:
    """Generate one image. Returns True on success, False on skip."""
    if out_path.exists() and out_path.stat().st_size > 10_000:
        print(f"  [cached] {out_path.name}")
        return True

    if dry_run:
        print(f"  [dry-run] {out_path.name}")
        print(f"    prompt: {prompt[:120]}...")
        return True

    payload = {
        "model": "chatgpt-image-latest",
        "prompt": prompt,
        "n": 1,
        "size": size,
        "quality": "high",
    }

    for attempt in range(3):
        try:
            r = requests.post(OPENAI_URL, headers=HEADERS, json=payload, timeout=300)
        except (requests.exceptions.Timeout,
                requests.exceptions.ConnectionError,
                requests.exceptions.ChunkedEncodingError) as exc:
            print(f"  [timeout/conn attempt {attempt+1}] {exc.__class__.__name__}")
            time.sleep(15 * (attempt + 1))
            continue

        if r.status_code == 200:
            import base64
            data = r.json()
            item = data["data"][0]
            if item.get("b64_json"):
                raw = base64.b64decode(item["b64_json"])
                out_path.write_bytes(raw)
                print(f"  [new] {out_path.name}  ({len(raw)//1024}KB)")
            elif item.get("url"):
                img_r = requests.get(item["url"], timeout=60)
                if img_r.status_code == 200:
                    out_path.write_bytes(img_r.content)
                    print(f"  [new] {out_path.name}  ({len(img_r.content)//1024}KB)")
                else:
                    print(f"  [WARN] image download failed: {img_r.status_code}")
                    return False
            else:
                print(f"  [WARN] no image data in response")
                return False
            time.sleep(0.5)
            return True

        elif r.status_code == 400:
            err = r.json().get("error", {}).get("message", r.text[:200])
            if "content_policy" in err.lower() or "safety" in err.lower():
                print(f"  [SAFETY] {out_path.name}: {err[:120]}")
                return False
            print(f"  [400] {err[:200]}")
            return False

        elif r.status_code == 429:
            wait = 30 * (attempt + 1)
            print(f"  [429 rate limit] waiting {wait}s...")
            time.sleep(wait)
            continue

        else:
            print(f"  [WARN] {r.status_code}: {r.text[:200]}")
            time.sleep(2)

    print(f"  [FAIL] {out_path.name} after 3 attempts")
    return False


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--scenes", action="store_true")
    ap.add_argument("--portraits", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--id", type=int, default=None, help="Generate single scene by id")
    args = ap.parse_args()

    do_scenes = args.scenes or (not args.scenes and not args.portraits)
    do_portraits = args.portraits or (not args.scenes and not args.portraits)

    scenes = load_jsonl(SCENES_PATH)
    portraits = load_jsonl(PORTRAITS_PATH)

    if not scenes and not portraits:
        sys.exit(f"No scenes/portraits found. Run: .venv/bin/python tools/scene_tracker.py first.")

    # chatgpt-image-latest supported sizes: 1024x1024, 1024x1536, 1536x1024, auto
    BG_SIZE = "1536x1024"   # landscape
    PORT_SIZE = "1024x1024" # square

    if do_portraits:
        print(f"\n=== Portraits ({len(portraits)}) ===")
        for p in portraits:
            out = BASE / p["path"]
            out.parent.mkdir(parents=True, exist_ok=True)
            print(f"  {p['key']}  [{p['label']}]")
            generate_image(p["prompt"], out, size=PORT_SIZE, dry_run=args.dry_run)

    if do_scenes:
        print(f"\n=== Backgrounds ({len(scenes)}) ===")
        for s in scenes:
            if args.id is not None and s["id"] != args.id:
                continue
            out = BASE / s["bg_path"]
            out.parent.mkdir(parents=True, exist_ok=True)
            dur = (s["end_ms"] - s["start_ms"]) / 1000
            print(f"  [{s['id']:03d}] {s['setting']:<20} ({dur:.0f}s)")
            generate_image(s["prompt"], out, size=BG_SIZE, dry_run=args.dry_run)

    print("\nDone.")


if __name__ == "__main__":
    main()
