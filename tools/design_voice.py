#!/usr/bin/env python3
"""
design_voice.py — ElevenLabs Voice Design: one description, three previews saved as mp3.

Usage:
    .venv/bin/python tools/design_voice.py --name feynman_v3 \
        --description-file audio/voice-design/feynman_v3/description.txt \
        --text-file audio/voice-design/feynman_v3/preview.txt

Writes audio/voice-design/<name>/preview_{1,2,3}.mp3 and previews.json
(generated_voice_id per preview). Save a winner with tools/save_voice_preview.py.
"""

import argparse
import base64
import json
import os
import sys
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parent.parent


def api_key() -> str:
    key = os.environ.get("ELEVENLABS_API_KEY", "")
    env = ROOT / ".env"
    if not key and env.exists():
        for line in env.read_text().splitlines():
            if line.startswith("ELEVENLABS_API_KEY="):
                key = line.split("=", 1)[1].strip()
    if not key:
        sys.exit("ERROR: ELEVENLABS_API_KEY not found in environment or .env")
    return key


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--name", required=True)
    ap.add_argument("--description-file", required=True)
    ap.add_argument("--text-file", required=True)
    ap.add_argument("--model", default="eleven_ttv_v3")
    ap.add_argument("--guidance", type=float, default=5.0)
    ap.add_argument("--loudness", type=float, default=0.5)
    args = ap.parse_args()

    desc = Path(args.description_file).read_text().strip()
    text = Path(args.text_file).read_text().strip()
    if not 20 <= len(desc) <= 1000:
        sys.exit(f"description is {len(desc)} chars; must be 20–1000")
    if not 100 <= len(text) <= 1000:
        sys.exit(f"preview text is {len(text)} chars; must be 100–1000")

    r = requests.post(
        "https://api.elevenlabs.io/v1/text-to-voice/design",
        headers={"xi-api-key": api_key(), "Content-Type": "application/json"},
        json={"voice_description": desc, "text": text, "model_id": args.model,
              "guidance_scale": args.guidance, "loudness": args.loudness},
        timeout=300,
    )
    if r.status_code != 200:
        sys.exit(f"ERROR {r.status_code}: {r.text[:500]}")

    out = ROOT / "audio" / "voice-design" / args.name
    out.mkdir(parents=True, exist_ok=True)
    meta = []
    for i, p in enumerate(r.json()["previews"], 1):
        f = out / f"preview_{i}.mp3"
        f.write_bytes(base64.b64decode(p["audio_base_64"]))
        meta.append({"file": f.name, "generated_voice_id": p["generated_voice_id"],
                     "duration_secs": p.get("duration_secs")})
        print(f"{f}  {p['generated_voice_id']}")
    (out / "previews.json").write_text(json.dumps(
        {"model": args.model, "guidance": args.guidance, "description": desc,
         "text": text, "previews": meta}, ensure_ascii=False, indent=1) + "\n")


if __name__ == "__main__":
    main()
