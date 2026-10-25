#!/usr/bin/env python3
"""
Generate ElevenLabs audio for -05_VincentVision.md.

Voice assignments:
  Operator / Query prose   → Matilda   XrExE9yKIg1WjnnlVkGX  (Dylan's preferred voice)
  The Narrator / stage dir → Daniel    onwK4e9ZLuTAKqWW03F9
  Vincent                  → Liam      TX3LPaxmHKxFdv7VOQHJ
  Carter                   → Adam      pNInz6obpgDQGcFmaJgB
  Narrator (internal)      → Daniel    onwK4e9ZLuTAKqWW03F9  (slightly more intimate)

Output: audio/vincentvision_reading.mp3
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
    sys.exit("pip install requests")

BASE      = Path(__file__).resolve().parent.parent
SRC       = BASE / "src" / "-05_VincentVision.md"
AUDIO_DIR = BASE / "audio"
SEG_DIR   = AUDIO_DIR / "vv_segments"
SEG_DIR.mkdir(parents=True, exist_ok=True)

ELEVEN_BASE = "https://api.elevenlabs.io/v1"
HEADERS     = {"xi-api-key": API_KEY, "Content-Type": "application/json"}

# Voice IDs
V = {
    "Operator":  "XrExE9yKIg1WjnnlVkGX",   # Matilda — Dylan's preferred voice
    "Narrator":  "onwK4e9ZLuTAKqWW03F9",   # Daniel
    "Vincent":   "TX3LPaxmHKxFdv7VOQHJ",   # Liam
    "Carter":    "pNInz6obpgDQGcFmaJgB",    # Adam
}

# Voice settings per speaker
SETTINGS = {
    "Operator": {"stability": 0.55, "similarity_boost": 0.75, "style": 0.15, "use_speaker_boost": True},
    "Narrator": {"stability": 0.50, "similarity_boost": 0.75, "style": 0.20, "use_speaker_boost": True},
    "Vincent":  {"stability": 0.60, "similarity_boost": 0.80, "style": 0.10, "use_speaker_boost": True},
    "Carter":   {"stability": 0.55, "similarity_boost": 0.75, "style": 0.15, "use_speaker_boost": True},
}


def clean(t):
    t = re.sub(r"\*\*([^*]+)\*\*", r"\1", t)
    t = re.sub(r"\*([^*]+)\*",     r"\1", t)
    t = re.sub(r"`([^`]+)`",       r"\1", t)
    t = re.sub(r"  +",             " ",   t)
    return t.strip()


def parse():
    """
    Parse -05_VincentVision.md into (speaker, text) segments.

    Section rules:
      ## I. The Query         → speaker = Operator
      ## II. Phase 2          → speaker = Narrator (stage dirs), dialog tags apply
      ## III. The Return      → Narrator
      ## IV. Vincent's Clarification → Vincent
      ## V. The Narrator Thinks → Narrator
      ## VI. [Terminal Output] → Narrator reads the log entries
      Code blocks             → skipped
      **Name:** lines         → speaker = Name
      *italic*                → Narrator (stage direction)
      [Bare bracket]          → Narrator (stage direction)
    """
    lines        = SRC.read_text(encoding="utf-8").splitlines()
    segments     = []
    section      = "preamble"   # tracks current section
    default_spk  = "Narrator"   # default within section
    in_code      = False

    # Map section headings → default speaker
    SECTION_DEFAULTS = {
        "i":    "Operator",
        "ii":   "Narrator",
        "iii":  "Narrator",
        "iv":   "Vincent",
        "v":    "Narrator",
        "vi":   "Narrator",
    }

    for line in lines:
        # Code fence toggle — skip everything inside
        if line.strip().startswith("```"):
            in_code = not in_code
            continue
        if in_code:
            continue

        stripped = line.strip()

        # Section heading
        if re.match(r"^##\s+", line):
            heading = re.sub(r"^##\s+", "", line).strip()
            # Identify section by roman numeral prefix
            m = re.match(r"^([IVXivx]+)\.\s", heading)
            if m:
                key = m.group(1).lower()
                default_spk = SECTION_DEFAULTS.get(key, "Narrator")
                section = key
            # Read heading aloud as Narrator title card (brief)
            title_text = clean(heading)
            if title_text:
                segments.append(("Narrator", title_text))
            continue

        # Top-level h1 — Narrator reads title
        if line.startswith("# "):
            segments.append(("Narrator", clean(line[2:])))
            continue

        # Horizontal rule / empty
        if re.match(r"^---+$", stripped) or not stripped:
            continue

        # Code block lines (already handled by fence toggle above)

        # **Speaker:** text   (dialog, colon inside closing **)
        m = re.match(r"^\*\*([^*]+):\*\*\s*(.*)", stripped)
        if m:
            raw_spk = m.group(1).strip()
            rest    = m.group(2).strip()
            # Map to known speaker keys
            spk = {
                "Vincent": "Vincent",
                "Carter":  "Carter",
                "The Narrator": "Narrator",
            }.get(raw_spk, "Narrator")
            # Split on [...] stage directions
            parts = re.split(r"(\[[^\]]+\])", rest)
            for part in parts:
                part = part.strip()
                if not part: continue
                if part.startswith("[") and part.endswith("]"):
                    inner = part[1:-1].strip()
                    if inner: segments.append(("Narrator", clean(inner)))
                else:
                    spoken = clean(part)
                    if spoken: segments.append((spk, spoken))
            continue

        # *Italic whole line* — stage direction → Narrator
        if re.match(r"^\*[^*].+[^*]\*$", stripped):
            inner = stripped[1:-1].strip()
            if inner: segments.append(("Narrator", clean(inner)))
            continue

        # [Bare bracket] — stage direction → Narrator
        if re.match(r"^\[[^\]]+\]$", stripped):
            inner = stripped[1:-1].strip()
            if inner: segments.append(("Narrator", clean(inner)))
            continue

        # Plain paragraph — use section default speaker
        text = clean(stripped)
        if text:
            segments.append((default_spk, text))

    return segments


def tts(speaker, text, index):
    vid      = V[speaker]
    settings = SETTINGS[speaker]
    out_path = SEG_DIR / f"{index:04d}_{speaker}.mp3"
    if out_path.exists():
        print(f"  [cached] {out_path.name}")
        return out_path

    payload = {
        "text": text,
        "model_id": "eleven_multilingual_v2",
        "voice_settings": settings,
    }
    url = f"{ELEVEN_BASE}/text-to-speech/{vid}"
    r   = requests.post(url,
                        headers={**HEADERS, "Accept": "audio/mpeg"},
                        json=payload, timeout=60)
    if r.status_code != 200:
        print(f"  [WARN] {r.status_code} for seg {index} ({speaker}): {r.text[:150]}")
        return None
    out_path.write_bytes(r.content)
    print(f"  [{index:04d}] {speaker}: {text[:70]}...")
    time.sleep(0.25)
    return out_path


def concatenate(paths, output):
    with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
        for p in paths:
            f.write(f"file '{p.resolve()}'\n")
        lpath = f.name
    result = subprocess.run(
        ["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", lpath, "-c", "copy", str(output)],
        capture_output=True,
    )
    os.unlink(lpath)
    if result.returncode != 0:
        print("ffmpeg error:", result.stderr.decode()[:500])
    else:
        print(f"\nOutput: {output}")


def main():
    print(f"Parsing {SRC.name}...")
    segments = parse()
    # Show speaker breakdown
    counts = {}
    for spk, _ in segments:
        counts[spk] = counts.get(spk, 0) + 1
    for spk, n in sorted(counts.items(), key=lambda x: -x[1]):
        voice_name = {"Operator":"Matilda","Narrator":"Daniel","Vincent":"Liam","Carter":"Adam"}.get(spk, "?")
        print(f"  {spk:<12} {n:>3} segments  ({voice_name})")
    print(f"  Total: {len(segments)}")

    print("\nGenerating audio...")
    files = []
    for i, (spk, text) in enumerate(segments):
        if not text.strip(): continue
        if spk not in V:
            print(f"  [SKIP] unknown speaker: {spk}")
            continue
        p = tts(spk, text, i)
        if p: files.append(p)

    if not files:
        print("No segments generated.")
        return

    output = AUDIO_DIR / "vincentvision_reading.mp3"
    print(f"\nConcatenating {len(files)} files...")
    concatenate(files, output)
    sz = output.stat().st_size / 1_000_000
    print(f"Done. {sz:.1f} MB")


if __name__ == "__main__":
    main()
