#!/usr/bin/env python3
"""
Generate ElevenLabs audio for the coda.c narration section of -08.md only.
Splices the result into the existing audio/minus08/minus08.mp3 at the
timestamp where the old coda narration begins.

Usage:
    .venv/bin/python tools/gen_coda_narration.py

Splice point (from cues.jsonl, cue i=175):
    start: 2350.733067 s  — "Then the binary deletes its own executable..."
    The old narration ran from 2350.73 to 2383.46.

The new narration is longer (step-by-step). This script:
    1. Extracts the coda narration paragraphs from -08.md.
    2. Sends them to ElevenLabs (Narrator voice).
    3. Cuts the original mp3 at the splice start.
    4. Cuts the tail (everything after the old narration ends) from the original.
    5. Concatenates: head + new narration + tail → minus08_updated.mp3.
"""

import os, re, sys, time, subprocess, tempfile
from pathlib import Path

_env_file = Path(__file__).resolve().parent.parent / ".env"
if _env_file.exists():
    for _line in _env_file.read_text().splitlines():
        _line = _line.strip()
        if _line and not _line.startswith("#") and "=" in _line:
            _k, _, _v = _line.partition("=")
            os.environ.setdefault(_k.strip(), _v.strip())

API_KEY = os.environ.get("ELEVENLABS_API_KEY", "").strip()
if not API_KEY:
    sys.exit("Set ELEVENLABS_API_KEY in .env and re-run.")

try:
    import requests
except ImportError:
    sys.exit(".venv/bin/pip install requests")

BASE      = Path(__file__).resolve().parent.parent
SRC       = BASE / "src" / "phase2"
AUDIO_DIR = BASE / "audio" / "minus08"
OUT_DIR   = AUDIO_DIR
OUT_DIR.mkdir(parents=True, exist_ok=True)

NARRATOR_ID = "onwK4e9ZLuTAKqWW03F9"   # Daniel — warm British narrator
NARRATOR_SETTINGS = {
    "stability": 0.50,
    "similarity_boost": 0.75,
    "style": 0.20,
    "use_speaker_boost": True,
}
ELEVEN_BASE = "https://api.elevenlabs.io/v1"
HEADERS     = {"xi-api-key": API_KEY, "Content-Type": "application/json"}

# ── Splice coordinates (verified from audio/minus08/cues.jsonl) ────────────
# i=168  2204.500–2212.023  Lisbeth: "Ieg vil lade en Mynt snurre..."  (Danish)
# i=169  2212.023–2217.770  Narrator: "I will let a coin spin..."       (translation)
# i=170  2217.770–2235.977  Narrator: "The coin spins. While..."        ← CUT START
# ...coda narration (C binary) + old bash script narration (i=176-188)...
# i=189  2508.460–2510.498  Lisbeth: "Yield er icke Overgiffuelse."     ← TAIL START
#
# We keep the head through i=169 (translation), then replace i=170–188
# (all narration of the old C + bash block) with the new step-by-step narration.
HEAD_END_S   = 2217.770   # end of translation line; start of first narration cue
TAIL_START_S = 2508.460   # start of "Yield er icke Overgiffuelse"


def clean(t):
    t = re.sub(r"\*\*([^*]+)\*\*", r"\1", t)
    t = re.sub(r"\*([^*]+)\*",     r"\1", t)
    t = re.sub(r"`([^`]+)`",       r"\1", t)
    t = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", t)
    return t.strip()


def extract_coda_narration(path):
    """
    Extract the italic narration paragraphs for the coda.c section from -08.md.
    These are the lines between the coin-spin Lisbeth line and
    'Lisbeth: Yield er icke Overgiffuelse.'
    """
    text = path.read_text(encoding="utf-8")
    # Find the section between the two Lisbeth lines
    # The translation "I will let a coin spin..." is already in the audio head.
    # Start extraction from the first coda narration paragraph proper.
    start_marker = "The coin spins. While it is still spinning"
    end_marker   = "Yield er icke Overgiffuelse"
    s = text.find(start_marker)
    e = text.find(end_marker, s)
    if s == -1 or e == -1:
        sys.exit("Could not locate coda narration section in -08.md")
    section = text[s:e]

    paragraphs = []
    in_code = False
    for line in section.splitlines():
        stripped = line.strip()
        if stripped.startswith("```"):
            in_code = not in_code
            continue
        if in_code or not stripped:
            continue
        # italic prose line: *...*
        if re.match(r"^\*[^*].+[^*]\*$", stripped):
            inner = stripped[1:-1].strip()
            if inner:
                paragraphs.append(clean(inner))
        # translation line (not italic, not dialogue)
        elif stripped.startswith("**"):
            continue  # skip dialogue
        elif stripped.startswith("#") or stripped.startswith(">") or stripped.startswith("|"):
            continue
    return paragraphs


def tts(text, index):
    safe = re.sub(r"[^a-zA-Z0-9_-]", "_", text[:24])
    out  = OUT_DIR / f"coda_narration_{index:03d}_{safe}.mp3"
    if out.exists():
        print(f"  [cached] {out.name}")
        return out
    payload = {
        "text": text,
        "model_id": "eleven_multilingual_v2",
        "voice_settings": NARRATOR_SETTINGS,
    }
    url = f"{ELEVEN_BASE}/text-to-speech/{NARRATOR_ID}"
    r   = requests.post(url,
                        headers={**HEADERS, "Accept": "audio/mpeg"},
                        json=payload, timeout=60)
    if r.status_code != 200:
        print(f"  [WARN] {r.status_code}: {r.text[:120]}")
        return None
    out.write_bytes(r.content)
    print(f"  [{index:03d}] {text[:70]}...")
    time.sleep(0.3)
    return out


def ffmpeg_cut(src, start, end, dest):
    cmd = ["ffmpeg", "-y", "-i", str(src),
           "-ss", str(start), "-to", str(end),
           "-c", "copy", str(dest)]
    r = subprocess.run(cmd, capture_output=True)
    if r.returncode != 0:
        print("ffmpeg error:", r.stderr.decode()[:300])


def ffmpeg_cut_head(src, end, dest):
    cmd = ["ffmpeg", "-y", "-i", str(src),
           "-t", str(end),
           "-c", "copy", str(dest)]
    r = subprocess.run(cmd, capture_output=True)
    if r.returncode != 0:
        print("ffmpeg error:", r.stderr.decode()[:300])


def ffmpeg_cut_tail(src, start, dest):
    cmd = ["ffmpeg", "-y", "-i", str(src),
           "-ss", str(start),
           "-c", "copy", str(dest)]
    r = subprocess.run(cmd, capture_output=True)
    if r.returncode != 0:
        print("ffmpeg error:", r.stderr.decode()[:300])


def concatenate(paths, output):
    with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
        for p in paths:
            f.write(f"file '{Path(p).resolve()}'\n")
        lpath = f.name
    r = subprocess.run(
        ["ffmpeg", "-y", "-f", "concat", "-safe", "0",
         "-i", lpath, "-c", "copy", str(output)],
        capture_output=True)
    os.unlink(lpath)
    if r.returncode != 0:
        print("ffmpeg concat error:", r.stderr.decode()[:300])
    else:
        sz = Path(output).stat().st_size / 1_000_000
        print(f"Output: {output}  ({sz:.1f} MB)")


def main():
    md_path = SRC / "-08.md"
    if not md_path.exists():
        sys.exit(f"Not found: {md_path}")

    print("Extracting coda narration paragraphs from -08.md...")
    paragraphs = extract_coda_narration(md_path)
    print(f"  {len(paragraphs)} paragraph(s) to narrate:")
    for i, p in enumerate(paragraphs):
        print(f"  [{i}] {p[:80]}...")

    print("\nGenerating ElevenLabs audio...")
    seg_files = []
    for i, para in enumerate(paragraphs):
        p = tts(para, i)
        if p:
            seg_files.append(p)

    if not seg_files:
        sys.exit("No segments generated.")

    # Concatenate all narration segments into one file
    narration_mp3 = OUT_DIR / "coda_narration_combined.mp3"
    print(f"\nConcatenating {len(seg_files)} narration segment(s)...")
    concatenate(seg_files, narration_mp3)

    # Cut the original mp3
    original = AUDIO_DIR / "minus08.mp3"
    if not original.exists():
        print(f"Original not found at {original}. Narration only saved to {narration_mp3}")
        return

    head_mp3  = OUT_DIR / "_splice_head.mp3"
    tail_mp3  = OUT_DIR / "_splice_tail.mp3"
    updated   = AUDIO_DIR / "minus08_updated.mp3"

    print(f"\nCutting head (0 → {HEAD_END_S}s)...")
    ffmpeg_cut_head(original, HEAD_END_S, head_mp3)

    print(f"Cutting tail ({TAIL_START_S}s → end)...")
    ffmpeg_cut_tail(original, TAIL_START_S, tail_mp3)

    print("Splicing: head + new narration + tail...")
    concatenate([head_mp3, narration_mp3, tail_mp3], updated)

    print(f"\nDone. Splice result: {updated}")
    print("Review it, then rename to minus08.mp3 to publish.")


if __name__ == "__main__":
    main()
