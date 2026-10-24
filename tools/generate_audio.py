#!/usr/bin/env python3
"""
Generate an ElevenLabs audio recording of the REALITY_USER_MANUAL dialog sections.

Sections (in order):
  1. Unnumbered page crisis (04g, 04h, 04i)
  2. Page -0 / Sauron (04k)
  3. Page 00 / Velora poem (00_page1_velora.md)  ← read as single narration
  4. Page 0000 / The fired cast second attempt (0000_page-0_rewrite_recasting.md)
  5. Editor note (04j) — included as a short coda

Usage:
  ELEVENLABS_API_KEY=sk_... python3 tools/generate_audio.py

Output:
  audio/dialog_reading.mp3
"""

import os
import re
import sys
import json
import time
import subprocess
import tempfile
from pathlib import Path

API_KEY = os.environ.get("ELEVENLABS_API_KEY", "").strip()
if not API_KEY:
    sys.exit("Set ELEVENLABS_API_KEY in your environment and re-run.")

try:
    import requests
except ImportError:
    sys.exit("requests not installed. Run: .venv/bin/pip install requests")

BASE = Path(__file__).resolve().parent.parent
SRC = BASE / "src"
AUDIO_DIR = BASE / "audio"
SEG_DIR = AUDIO_DIR / "segments"
SEG_DIR.mkdir(parents=True, exist_ok=True)

ELEVEN_BASE = "https://api.elevenlabs.io/v1"
HEADERS = {"xi-api-key": API_KEY, "Content-Type": "application/json"}


# ── Voice mapping ────────────────────────────────────────────────────────────
# Preferred voice names in priority order for each character.
# The script fetches your account's available voices and picks the first match.
# Add your own voice names (from your ElevenLabs library) at the front of each list.

VOICE_PREFS = {
    "The Narrator":  ["Aria", "Rachel", "Dorothy", "Charlotte", "Callum", "Daniel", "Antoni"],
    "Feynman":       ["Daniel", "Callum", "Arnold", "Adam", "Bill", "Antoni"],
    "McClane":       ["Adam", "Josh", "Sam", "Marcus", "Harry"],
    "Cecil":         ["Callum", "Daniel", "Rachel", "Aria", "Grace"],
    "Cecil Palmer":  ["Callum", "Daniel", "Rachel", "Aria", "Grace"],
    "Sauron":        ["Josh", "Clyde", "Dave", "Thomas", "Arnold"],
    "Chandler":      ["Sam", "Charlie", "Harry", "Antoni"],
    "Ross":          ["Antoni", "Daniel", "Arnold", "Bill", "Callum"],
    "Joey":          ["Charlie", "Marcus", "Callum", "Sam", "Josh"],
    "The Caller":    ["Bella", "Grace", "Dorothy", "Rachel"],
    "Caller":        ["Bella", "Grace", "Dorothy", "Rachel"],
    "Euler":         ["Arnold", "Bill", "Clyde", "Thomas", "Adam"],
    "Velora":        ["Rachel", "Grace", "Dorothy", "Aria"],   # Velora poem
    "Editor":        ["Rachel", "Aria", "Dorothy", "Charlotte"],
}

# Fallback if nothing preferred is found — just use whatever comes first in the account
FALLBACK_VOICE = None  # assigned after voice fetch


def fetch_voices():
    """Return {name: voice_id} for all voices in the account."""
    r = requests.get(f"{ELEVEN_BASE}/voices", headers=HEADERS, timeout=15)
    r.raise_for_status()
    return {v["name"]: v["voice_id"] for v in r.json()["voices"]}


def assign_voices(available):
    """Build speaker → voice_id map."""
    global FALLBACK_VOICE
    name_to_id = available
    # Case-insensitive lookup
    lower = {k.lower(): v for k, v in available.items()}

    if available:
        FALLBACK_VOICE = next(iter(available.values()))

    mapping = {}
    for speaker, prefs in VOICE_PREFS.items():
        chosen = None
        for pref in prefs:
            if pref in name_to_id:
                chosen = name_to_id[pref]
                break
            if pref.lower() in lower:
                chosen = lower[pref.lower()]
                break
        mapping[speaker] = chosen or FALLBACK_VOICE
    return mapping


# ── Dialog parser ────────────────────────────────────────────────────────────

# Characters whose name alone at the start of a line (no bold) signals dialog
KNOWN_CHARACTERS = {
    "The Narrator", "Feynman", "McClane", "Cecil", "Cecil Palmer",
    "Sauron", "Chandler", "Ross", "Joey", "Caller", "The Caller",
    "Euler", "Editor",
}


def parse_line_as_dialog(line):
    """
    Try to parse a line as 'Character: rest' (with or without **bold**).
    Returns (speaker, rest) or None.
    """
    # Bold format: **Character:** rest  (colon is inside closing **)
    m = re.match(r"^\*\*([^*]+):\*\*\s*(.*)", line)
    if m:
        return m.group(1).strip(), m.group(2)

    # Plain format: Character: rest — only for known characters
    m = re.match(r"^([A-Za-z][A-Za-z ]{0,24}):\s(.*)", line)
    if m:
        name = m.group(1).strip()
        if name in KNOWN_CHARACTERS:
            return name, m.group(2)

    return None


def split_dialog_line(speaker, rest):
    """
    Given a speaker and the rest of a dialog line, split into segments.
    Stage directions in [...] become Narrator segments.
    Spoken text between/around them stays as the speaker.
    """
    segs = []
    # Find all [...] blocks with their positions
    parts = re.split(r"(\[[^\]]+\])", rest)
    for part in parts:
        part = part.strip()
        if not part:
            continue
        if part.startswith("[") and part.endswith("]"):
            inner = part[1:-1].strip()
            if inner:
                segs.append(("The Narrator", clean_text(inner)))
        else:
            spoken = clean_text(part)
            if spoken:
                segs.append((speaker, spoken))
    return segs


def parse_md(path):
    """
    Return a list of (speaker, text) tuples.
    Handles:
      - **Character:** text  (bold format, crisis pages)
      - Character: text      (plain format, 0000 page — known characters only)
      - [Stage direction.]   (bare bracket lines → Narrator)
      - *italic stage direction*  (whole-line italic → Narrator)
      - code blocks          (skipped)
      - headings             (Narrator, first line only)
    """
    segments = []
    lines = Path(path).read_text(encoding="utf-8").splitlines()
    in_code = False

    for line in lines:
        # Code fence
        if line.startswith("```"):
            in_code = not in_code
            continue
        if in_code:
            continue

        stripped = line.strip()

        # Horizontal rule
        if re.match(r"^---+$", stripped):
            continue

        # Empty line
        if not stripped:
            continue

        # Heading — read as Narrator title card
        if line.startswith("#"):
            heading_text = re.sub(r"^#+\s*", "", line).strip()
            if heading_text:
                segments.append(("The Narrator", heading_text))
            continue

        # Bare stage direction: [A silence.] or [The line was dead. Good night, Night Vale.]
        if re.match(r"^\[[^\]]+\]$", stripped):
            inner = stripped[1:-1].strip()
            if inner:
                segments.append(("The Narrator", clean_text(inner)))
            continue

        # Whole-line italic stage direction: *text*
        if re.match(r"^\*[^*].*[^*]\*$", stripped) or re.match(r"^\*[^*]\*$", stripped):
            inner = stripped[1:-1]
            if inner:
                segments.append(("The Narrator", clean_text(inner)))
            continue

        # Dialog line (bold or plain-character format)
        parsed = parse_line_as_dialog(stripped)
        if parsed:
            speaker, rest = parsed
            segs = split_dialog_line(speaker, rest)
            segments.extend(segs)
            continue

        # Everything else: plain paragraph — read as Narrator
        text = clean_text(stripped)
        if text:
            segments.append(("The Narrator", text))

    return segments


def clean_text(t):
    """Strip markdown emphasis, normalize whitespace."""
    t = re.sub(r"\*\*([^*]+)\*\*", r"\1", t)  # bold
    t = re.sub(r"\*([^*]+)\*", r"\1", t)        # italic
    t = re.sub(r"`([^`]+)`", r"\1", t)          # inline code
    t = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", t)  # links
    t = re.sub(r"  +", " ", t)
    return t.strip()


# ── TTS ──────────────────────────────────────────────────────────────────────

def tts(speaker, text, voice_id, index):
    """Call ElevenLabs TTS, save to SEG_DIR/{index:04d}_{speaker}.mp3."""
    out_path = SEG_DIR / f"{index:04d}_{speaker.replace(' ', '_')}.mp3"
    if out_path.exists():
        print(f"  [cached] {out_path.name}")
        return out_path

    payload = {
        "text": text,
        "model_id": "eleven_multilingual_v2",
        "voice_settings": {
            "stability": 0.45,
            "similarity_boost": 0.75,
            "style": 0.2,
            "use_speaker_boost": True,
        },
    }
    url = f"{ELEVEN_BASE}/text-to-speech/{voice_id}"
    r = requests.post(url, headers={**HEADERS, "Accept": "audio/mpeg"},
                      json=payload, timeout=60)
    if r.status_code != 200:
        print(f"  [WARN] TTS failed for segment {index} ({speaker}): {r.status_code} {r.text[:200]}")
        return None
    out_path.write_bytes(r.content)
    print(f"  [{index:04d}] {speaker}: {text[:60]}...")
    time.sleep(0.25)  # gentle rate-limit buffer
    return out_path


# ── Concatenation ────────────────────────────────────────────────────────────

def concatenate(segment_paths, output_path):
    """Use ffmpeg concat demuxer to join mp3 files."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
        for p in segment_paths:
            f.write(f"file '{p.resolve()}'\n")
        list_path = f.name

    cmd = [
        "ffmpeg", "-y", "-f", "concat", "-safe", "0",
        "-i", list_path,
        "-c", "copy",
        str(output_path),
    ]
    result = subprocess.run(cmd, capture_output=True)
    os.unlink(list_path)
    if result.returncode != 0:
        print("ffmpeg error:", result.stderr.decode()[:500])
    else:
        print(f"\nOutput: {output_path}")


# ── Section definitions ──────────────────────────────────────────────────────

SECTIONS = [
    # (label, source_file, parse_mode)
    ("Crisis page 1",   SRC / "04g_crisis_page1.md",              "dialog"),
    ("Crisis page 2",   SRC / "04h_crisis_page2.md",              "dialog"),
    ("Crisis page 3",   SRC / "04i_crisis_page3.md",              "dialog"),
    ("Page -0",         SRC / "04k_sauron_minus_zero.md",         "dialog"),
    ("Page 00 (Velora)",SRC / "00_page1_velora.md",               "poem"),
    ("Page 0000",       SRC / "0000_page-0_rewrite_recasting.md", "dialog"),
    ("Editor note",     SRC / "04j_editor_note.md",               "editor"),
]


def parse_poem(path, voice_id):
    """Return the whole poem as a single narrator segment (constructed language)."""
    text = Path(path).read_text(encoding="utf-8")
    # Strip markdown headings and lines that are clearly meta
    lines = [l for l in text.splitlines()
             if not l.startswith("#") and not l.startswith("---")]
    body = " ".join(l.strip() for l in lines if l.strip())
    return [("Velora", body)]


def parse_editor(path):
    """The editor note is Claude's voice — read as single narrator."""
    text = Path(path).read_text(encoding="utf-8")
    # Take just the prose, skip code blocks and headings details
    lines = text.splitlines()
    out = []
    in_code = False
    current = []
    for line in lines:
        if line.startswith("```"):
            if not in_code:
                if current:
                    out.append(("Editor", clean_text(" ".join(current))))
                    current = []
                in_code = True
            else:
                in_code = False
            continue
        if in_code:
            continue
        if line.startswith("#"):
            if current:
                out.append(("Editor", clean_text(" ".join(current))))
                current = []
            heading = re.sub(r"^#+\s*", "", line).strip()
            if heading:
                out.append(("Editor", heading))
            continue
        if not line.strip():
            if current:
                out.append(("Editor", clean_text(" ".join(current))))
                current = []
            continue
        current.append(line.strip())
    if current:
        out.append(("Editor", clean_text(" ".join(current))))
    return out


# ── Main ─────────────────────────────────────────────────────────────────────

def main():
    print("Fetching voices from ElevenLabs...")
    available = fetch_voices()
    print(f"  {len(available)} voices found: {', '.join(list(available)[:10])}{'...' if len(available)>10 else ''}")

    voice_map = assign_voices(available)
    print("Voice assignments:")
    for speaker, vid in voice_map.items():
        name = next((n for n, i in available.items() if i == vid), "?")
        print(f"  {speaker:<18} → {name}")

    # Parse all segments
    all_segments = []
    for label, path, mode in SECTIONS:
        print(f"\nParsing: {label}")
        if not path.exists():
            print(f"  [SKIP] {path} not found")
            continue
        # Section title as narrator announcement (brief, quiet)
        # (omitted to keep the audio immersive — characters speak without intro card)

        if mode == "poem":
            segs = parse_poem(path, voice_map.get("Velora", FALLBACK_VOICE))
        elif mode == "editor":
            segs = parse_editor(path)
        else:
            segs = parse_md(path)

        all_segments.extend(segs)
        print(f"  {len(segs)} segments")

    print(f"\nTotal segments: {len(all_segments)}")

    # Generate audio for each segment
    print("\nGenerating audio...")
    segment_files = []
    for i, (speaker, text) in enumerate(all_segments):
        if not text.strip():
            continue
        vid = voice_map.get(speaker, FALLBACK_VOICE)
        if not vid:
            print(f"  [SKIP] no voice for {speaker}")
            continue
        p = tts(speaker, text, vid, i)
        if p:
            segment_files.append(p)

    if not segment_files:
        print("No segments generated.")
        return

    output = AUDIO_DIR / "dialog_reading.mp3"
    print(f"\nConcatenating {len(segment_files)} files...")
    concatenate(segment_files, output)
    print("Done.")


if __name__ == "__main__":
    main()
