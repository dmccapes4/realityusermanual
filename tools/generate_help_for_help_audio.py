#!/usr/bin/env python3
"""Generate hallway `help for help` MP3s (Chaucer · Cecil · Sauron Default).

Scripts: web/hall/help_for_help/<slug>.md
Output:  web/hall/help_for_help/<slug>.mp3
         audio/help_for_help/<slug>/{segments,cues.jsonl,slug.mp3}

Usage:
  .venv/bin/python tools/generate_help_for_help_audio.py
  .venv/bin/python tools/generate_help_for_help_audio.py --slug minus08
  .venv/bin/python tools/generate_help_for_help_audio.py --slug minus08,minus25
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(Path(__file__).resolve().parent))

import generate_audio as ga  # noqa: E402

SCRIPT_DIR = BASE / "web" / "hall" / "help_for_help"
AUDIO_ROOT = BASE / "audio" / "help_for_help"
WEB_OUT = SCRIPT_DIR  # mp3 next to md for /hall/help_for_help/<slug>.mp3

SPEAKER_MAP = {
    "CHAUCER": "Chaucer",
    "CECIL": "Cecil",
    "SAURON": "Sauron (Default)",
}

HEADER = re.compile(
    r"^\*\*(CHAUCER|CECIL|SAURON):\*\*\s*$",
    re.MULTILINE,
)

ga.SPEAKER_SETTINGS["Chaucer"] = {
    "stability": 0.32,
    "similarity_boost": 0.70,
    "style": 0.58,
    "use_speaker_boost": True,
}


def _clean_for_tts(text: str) -> str:
    text = re.sub(r"^##+\s+.*$", "", text, flags=re.MULTILINE)
    text = re.sub(r"^---+$", "", text, flags=re.MULTILINE)
    text = re.sub(r"\*\*([^*]+)\*\*", r"\1", text)
    text = re.sub(r"(?<!\*)\*([^*]+)\*(?!\*)", r"\1", text)
    text = re.sub(r"`([^`]+)`", r"\1", text)
    text = re.sub(r"\n{3,}", "\n\n", text).strip()
    text = text.replace("−", "-")
    return text


def parse_script(path: Path) -> list[tuple[str, str]]:
    raw = path.read_text(encoding="utf-8")
    first = HEADER.search(raw)
    if not first:
        raise SystemExit(f"No speaker headers in {path}")
    raw = raw[first.start() :]
    matches = list(HEADER.finditer(raw))
    segments: list[tuple[str, str]] = []
    for i, m in enumerate(matches):
        speaker = SPEAKER_MAP[m.group(1)]
        start = m.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(raw)
        block = _clean_for_tts(raw[start:end])
        if block:
            segments.append((speaker, block))
    return segments


def generate_slug(slug: str, force: bool = False) -> Path:
    src = SCRIPT_DIR / f"{slug}.md"
    if not src.exists():
        raise SystemExit(f"Missing script {src}")

    web_mp3 = WEB_OUT / f"{slug}.mp3"
    out_dir = AUDIO_ROOT / slug
    out_mp3 = out_dir / f"{slug}.mp3"
    out_cues = out_dir / "cues.jsonl"

    if web_mp3.exists() and web_mp3.stat().st_size > 10_000 and not force:
        print(f"skip {slug} (exists {web_mp3.stat().st_size // 1024} KB) — pass --force to regen")
        return web_mp3

    for name, key in (
        ("Chaucer", "Chaucer"),
        ("Cecil", "Cecil"),
        ("Sauron (Default)", "Sauron (Default)"),
    ):
        vid = ga.VOICE_MAP.get(key, "PENDING")
        if not vid or vid == "PENDING":
            raise SystemExit(f"VOICE for {name!r} is PENDING — set in .env / VOICE_MAP")

    segments = parse_script(src)
    print(f"\n=== {slug} — {len(segments)} blocks ===")
    for sp, text in segments:
        print(f"  {sp:<18} {len(text):5d} chars  {text[:52]!r}...")

    out_dir.mkdir(parents=True, exist_ok=True)
    # Isolate segment cache per slug so hashes don't collide across pages
    slug_seg = out_dir / "segments"
    slug_seg.mkdir(parents=True, exist_ok=True)
    prev_seg = ga.SEG_DIR
    ga.SEG_DIR = slug_seg

    files: list[Path] = []
    cues: list[dict] = []
    try:
        for speaker, text in segments:
            vid = ga.VOICE_MAP[speaker]
            paths = ga.tts(speaker, text, vid)
            files.extend(paths)
            for p in paths:
                cues.append({"speaker": speaker, "path": p.name, "chars": len(text)})
    finally:
        ga.SEG_DIR = prev_seg

    if not files:
        raise SystemExit(f"No audio for {slug}")

    print(f"Concatenating {len(files)} → {out_mp3}")
    ga.concatenate(files, out_mp3)
    out_cues.write_text(
        "".join(json.dumps(c, ensure_ascii=False) + "\n" for c in cues),
        encoding="utf-8",
    )
    shutil.copy2(out_mp3, web_mp3)
    print(f"Output: {web_mp3} ({web_mp3.stat().st_size // 1024} KB)")
    return web_mp3


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--slug", default="", help="Comma-separated slugs (default: all *.md except README)")
    ap.add_argument("--force", action="store_true")
    args = ap.parse_args()

    if args.slug:
        slugs = [s.strip() for s in args.slug.split(",") if s.strip()]
    else:
        slugs = sorted(
            p.stem for p in SCRIPT_DIR.glob("minus*.md") if p.is_file()
        )

    if not slugs:
        raise SystemExit("No slugs")

    print(f"Generating {len(slugs)} help-for-help dialogs…")
    for slug in slugs:
        generate_slug(slug, force=args.force)
    print("\nDone.")


if __name__ == "__main__":
    main()
