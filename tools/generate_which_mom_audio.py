#!/usr/bin/env python3
"""Generate MP3 for docs/NARRATION_WHICH_FOR_MOM_20261106.md

Voices:
  OPERATOR (DEFAULT) → Operator
  CHAUCER            → Chaucer (VOICE_CHAUCER)
  SAURON (DEFAULT)   → Sauron (Default)

Usage:
  .venv/bin/python tools/generate_which_mom_audio.py
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(Path(__file__).resolve().parent))

import generate_audio as ga  # noqa: E402

SRC = BASE / "docs" / "NARRATION_WHICH_FOR_MOM_20261106.md"
OUT_DIR = BASE / "audio" / "which_mom"
OUT_MP3 = OUT_DIR / "which_for_mom.mp3"
OUT_CUES = OUT_DIR / "cues.jsonl"

SPEAKER_MAP = {
    "OPERATOR": "Operator",
    "CHAUCER": "Chaucer",
    "SAURON": "Sauron (Default)",
}

HEADER = re.compile(
    r"^\*\*(OPERATOR|CHAUCER|SAURON):\*\*\s*$",
    re.MULTILINE,
)

# Chaucer settings from VOICE_DESIGN_PROMPTS.md (−35)
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
    text = re.sub(r"\*([^*]+)\*", r"\1", text)
    text = re.sub(r"`([^`]+)`", r"\1", text)
    text = re.sub(r"\n{3,}", "\n\n", text).strip()
    # Prefer spoken "minus twenty eight" via generate_audio.speak_labels on chunks
    text = text.replace("−", "-")
    return text


def parse_script(path: Path) -> list[tuple[str, str]]:
    raw = path.read_text(encoding="utf-8")
    # Drop title / filed meta before first speaker
    first = HEADER.search(raw)
    if not first:
        sys.exit(f"No speaker headers found in {path}")
    raw = raw[first.start() :]

    matches = list(HEADER.finditer(raw))
    segments: list[tuple[str, str]] = []
    for i, m in enumerate(matches):
        label = m.group(1)
        speaker = SPEAKER_MAP[label]
        start = m.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(raw)
        block = _clean_for_tts(raw[start:end])
        if not block:
            continue
        # One TTS call per speaker block (chunk_text inside tts handles length)
        segments.append((speaker, block))
    return segments


def main() -> None:
    if not SRC.exists():
        sys.exit(f"Missing {SRC}")

    vid_chaucer = ga.VOICE_MAP.get("Chaucer", "PENDING")
    if not vid_chaucer or vid_chaucer == "PENDING":
        sys.exit("VOICE_CHAUCER is PENDING — set it in .env")

    segments = parse_script(SRC)
    print(f"Script → {len(segments)} speaker blocks")
    for sp, text in segments:
        print(f"  {sp:<18} {len(text):5d} chars  {text[:56]!r}...")

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    files: list[Path] = []
    cues: list[dict] = []

    for speaker, text in segments:
        vid = ga.VOICE_MAP.get(speaker)
        if not vid or vid == "PENDING":
            sys.exit(f"No voice ID for {speaker!r}")
        paths = ga.tts(speaker, text, vid)
        files.extend(paths)
        for p in paths:
            cues.append({"speaker": speaker, "path": p.name, "text": text[:200]})

    if not files:
        sys.exit("No segments generated.")

    print(f"\nConcatenating {len(files)} files → {OUT_MP3}")
    ga.concatenate(files, OUT_MP3)
    OUT_CUES.write_text(
        "".join(json.dumps(c, ensure_ascii=False) + "\n" for c in cues),
        encoding="utf-8",
    )
    size_kb = OUT_MP3.stat().st_size // 1024
    print(f"Output: {OUT_MP3} ({size_kb} KB)")
    print(f"Cues:   {OUT_CUES} ({len(cues)})")
    print("Done.")


if __name__ == "__main__":
    main()
