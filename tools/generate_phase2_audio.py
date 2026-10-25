#!/usr/bin/env python3
"""
Generate ElevenLabs audio for Phase 2 documents.

Covers (in order):
  src/-06_AnimateReality.md
  src/-07_Goines.md
  src/-08_received_how_to_fly.md
  REFLECTION_MCCLANE_REBIRTH_20261024.md
  REFLECTION_VINCENTVISION_20261024.md
  REPORT_FEYNMAN_AS_GOINES_20261024.md
  REFLECTION_VINCENT_RETROGRADE_20261025.md
  REFLECTION_OPERATOR_EXPERIMENT_20261025.md
  REPORT_FIRST_TRUE_MANUSCRIPT_GLACIAL_20261025.md
  REPORT_VINCENT_RETROGRADE_ASSAY_20261025.md

Voice map:
  Stamper   Josh    TxGEqnHWrfWFTfGW9XjX  operational, flat, measured
  Vincent   Liam    TX3LPaxmHKxFdv7VOQHJ  precise, warm, direct
  Carter    Adam    pNInz6obpgDQGcFmaJgB   direct authority, corporate
  Operator  Matilda XrExE9yKIg1WjnnlVkGX  Dylan's preferred voice
  Narrator  Daniel  onwK4e9ZLuTAKqWW03F9  warm British narrator
  Goines    Callum  N2lVS1w4EtoT3dr4eOWO  dry, precise, uncertain (future)

Output: audio/phase2_reading.mp3
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
SRC       = BASE / "src"
AUDIO_DIR = BASE / "audio"
SEG_DIR   = AUDIO_DIR / "p2_segments"
SEG_DIR.mkdir(parents=True, exist_ok=True)

ELEVEN_BASE = "https://api.elevenlabs.io/v1"
HEADERS     = {"xi-api-key": API_KEY, "Content-Type": "application/json"}

V = {
    "Stamper":  "TxGEqnHWrfWFTfGW9XjX",  # Josh
    "Vincent":  "TX3LPaxmHKxFdv7VOQHJ",  # Liam
    "Carter":   "pNInz6obpgDQGcFmaJgB",   # Adam
    "Operator": "XrExE9yKIg1WjnnlVkGX",   # Matilda
    "Narrator": "onwK4e9ZLuTAKqWW03F9",   # Daniel
    "Goines":   "N2lVS1w4EtoT3dr4eOWO",   # Callum (reserved)
}

SETTINGS = {
    "Stamper":  {"stability": 0.55, "similarity_boost": 0.78, "style": 0.10, "use_speaker_boost": True},
    "Vincent":  {"stability": 0.60, "similarity_boost": 0.80, "style": 0.10, "use_speaker_boost": True},
    "Carter":   {"stability": 0.55, "similarity_boost": 0.75, "style": 0.15, "use_speaker_boost": True},
    "Operator": {"stability": 0.55, "similarity_boost": 0.75, "style": 0.15, "use_speaker_boost": True},
    "Narrator": {"stability": 0.50, "similarity_boost": 0.75, "style": 0.20, "use_speaker_boost": True},
    "Goines":   {"stability": 0.45, "similarity_boost": 0.70, "style": 0.12, "use_speaker_boost": True},
}


def clean(t):
    t = re.sub(r"\*\*([^*]+)\*\*", r"\1", t)
    t = re.sub(r"\*([^*]+)\*",     r"\1", t)
    t = re.sub(r"`([^`]+)`",       r"\1", t)
    t = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", t)
    t = re.sub(r"  +", " ", t)
    return t.strip()


KNOWN_DIALOG = {
    "The Narrator", "Feynman", "McClane", "Cecil", "Cecil Palmer",
    "Sauron", "Chandler", "Ross", "Joey", "Caller", "The Caller",
    "Euler", "Editor", "Stamper", "Vincent", "Carter", "Goines",
}

SECTION_DEFAULTS_06 = {
    "i":   "Operator",
    "ii":  "Narrator",
    "iii": "Stamper",
    "iv":  "Narrator",
}


def split_on_brackets(speaker, rest):
    """Split dialog line on [...] stage directions → Stamper/Narrator for those."""
    segs = []
    parts = re.split(r"(\[[^\]]+\])", rest)
    for part in parts:
        part = part.strip()
        if not part:
            continue
        if part.startswith("[") and part.endswith("]"):
            inner = part[1:-1].strip()
            if inner:
                segs.append(("Stamper", clean(inner)))
        else:
            spoken = clean(part)
            if spoken:
                segs.append((speaker, spoken))
    return segs


def parse_06(path):
    """Parse -06_AnimateReality.md with section-aware speaker assignment."""
    lines = path.read_text(encoding="utf-8").splitlines()
    segs = []
    in_code = False
    section = "pre"
    default_spk = "Stamper"

    for line in lines:
        if line.strip().startswith("```"):
            in_code = not in_code
            continue
        if in_code:
            continue

        stripped = line.strip()
        if re.match(r"^---+$", stripped) or not stripped:
            continue

        # Section heading
        if re.match(r"^##\s+", line):
            heading = re.sub(r"^##\s+", "", line).strip()
            m = re.match(r"^([IVXivx]+)\.\s", heading)
            if m:
                key = m.group(1).lower()
                default_spk = SECTION_DEFAULTS_06.get(key, "Stamper")
                section = key
            title = clean(heading)
            if title:
                segs.append(("Stamper", title))
            continue

        if line.startswith("# "):
            segs.append(("Stamper", clean(line[2:])))
            continue

        # *— Stamper: text* interjection
        m = re.match(r"^\*—\s*Stamper:\s*(.*?)\*$", stripped)
        if m:
            text = clean(m.group(1))
            if text:
                segs.append(("Stamper", text))
            continue

        # **Speaker:** dialog
        m = re.match(r"^\*\*([^*]+):\*\*\s*(.*)", stripped)
        if m:
            raw = m.group(1).strip()
            rest = m.group(2).strip()
            spk_map = {"Stamper": "Stamper", "Vincent": "Vincent", "Carter": "Carter",
                       "The Narrator": "Narrator"}
            spk = spk_map.get(raw, "Stamper")
            segs.extend(split_on_brackets(spk, rest))
            continue

        # Whole-line italic → Stamper (stage direction)
        if re.match(r"^\*[^*].+[^*]\*$", stripped):
            inner = stripped[1:-1].strip()
            if inner:
                segs.append(("Stamper", clean(inner)))
            continue

        # [Bare bracket]
        if re.match(r"^\[[^\]]+\]$", stripped):
            inner = stripped[1:-1].strip()
            if inner:
                segs.append(("Stamper", clean(inner)))
            continue

        # Table rows — skip
        if stripped.startswith("|"):
            continue

        # Plain paragraph → section default
        text = clean(stripped)
        if text:
            segs.append((default_spk, text))

    return segs


def parse_07(path):
    """Parse -07_Goines.md — Stamper narrates everything. No dialog."""
    lines = path.read_text(encoding="utf-8").splitlines()
    segs = []
    in_code = False

    for line in lines:
        if line.strip().startswith("```"):
            in_code = not in_code
            continue
        if in_code:
            continue

        stripped = line.strip()
        if re.match(r"^---+$", stripped) or not stripped:
            continue

        if line.startswith("#"):
            text = clean(re.sub(r"^#+\s*", "", line))
            if text:
                segs.append(("Stamper", text))
            continue

        if re.match(r"^\*[^*].+[^*]\*$", stripped):
            inner = stripped[1:-1].strip()
            if inner:
                segs.append(("Stamper", clean(inner)))
            continue

        if re.match(r"^\[[^\]]+\]$", stripped):
            segs.append(("Stamper", clean(stripped[1:-1])))
            continue

        # **Stamper:** lines
        m = re.match(r"^\*\*([^*]+):\*\*\s*(.*)", stripped)
        if m:
            rest = m.group(2).strip()
            segs.extend(split_on_brackets("Stamper", rest))
            continue

        if stripped.startswith("|"):
            continue

        text = clean(stripped)
        if text:
            segs.append(("Stamper", text))

    return segs


def parse_generic_narrator(path, default="Narrator"):
    """Parse reflection/report files — Narrator reads everything, skip code/tables."""
    lines = path.read_text(encoding="utf-8").splitlines()
    segs = []
    in_code = False

    for line in lines:
        if line.strip().startswith("```"):
            in_code = not in_code
            continue
        if in_code:
            continue

        stripped = line.strip()
        if re.match(r"^---+$", stripped) or not stripped:
            continue

        if line.startswith("#"):
            text = clean(re.sub(r"^#+\s*", "", line))
            if text:
                segs.append((default, text))
            continue

        if stripped.startswith("|"):
            continue

        # Quoted operator lines > ...
        if stripped.startswith(">"):
            inner = stripped.lstrip("> ").strip()
            if inner:
                segs.append(("Operator", clean(inner)))
            continue

        if re.match(r"^\*[^*].+[^*]\*$", stripped):
            inner = stripped[1:-1].strip()
            if inner:
                segs.append((default, clean(inner)))
            continue

        if re.match(r"^\[[^\]]+\]$", stripped):
            segs.append((default, clean(stripped[1:-1])))
            continue

        # **[his]** labels and similar — read inline
        text = clean(stripped)
        if text:
            segs.append((default, text))

    return segs


def parse_08(path):
    """Parse -08 filing page — Narrator reads, skip the table and code."""
    return parse_generic_narrator(path, default="Narrator")


SECTIONS = [
    ("Page -06: Animate Reality",         SRC / "-06_AnimateReality.md",                     "06"),
    ("Page -07: Goines",                  SRC / "-07_Goines.md",                              "07"),
    ("Page -08: Received How to Fly",     SRC / "-08_received_how_to_fly.md",                 "08"),
    ("Reflection: McClane Rebirth",       BASE / "REFLECTION_MCCLANE_REBIRTH_20261024.md",    "narrator"),
    ("Reflection: VincentVision",         BASE / "REFLECTION_VINCENTVISION_20261024.md",      "narrator"),
    ("Report: Feynman as Goines",         BASE / "REPORT_FEYNMAN_AS_GOINES_20261024.md",      "narrator"),
    ("Reflection: Narrative Retrograde",  BASE / "REFLECTION_VINCENT_RETROGRADE_20261025.md", "narrator"),
    ("Reflection: Operator Experiment",   BASE / "REFLECTION_OPERATOR_EXPERIMENT_20261025.md","narrator"),
    ("Report: Glacial Manuscript",        BASE / "REPORT_FIRST_TRUE_MANUSCRIPT_GLACIAL_20261025.md", "narrator"),
    ("Report: Retrograde Assay",          BASE / "REPORT_VINCENT_RETROGRADE_ASSAY_20261025.md", "narrator"),
]


def tts(speaker, text, index, label):
    vid      = V[speaker]
    settings = SETTINGS[speaker]
    safe_label = re.sub(r"[^a-zA-Z0-9_-]", "_", label)[:20]
    out_path = SEG_DIR / f"{index:04d}_{speaker}_{safe_label}.mp3"
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
        print(f"  [WARN] {r.status_code} seg {index} ({speaker}): {r.text[:120]}")
        return None
    out_path.write_bytes(r.content)
    print(f"  [{index:04d}] {speaker}: {text[:65]}...")
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
        print("ffmpeg error:", result.stderr.decode()[:400])
    else:
        sz = output.stat().st_size / 1_000_000
        print(f"\nOutput: {output}  ({sz:.1f} MB)")


def main():
    all_segs = []

    for label, path, mode in SECTIONS:
        if not path.exists():
            print(f"[SKIP] {path.name} not found")
            continue
        print(f"\nParsing: {label}")

        if mode == "06":
            segs = parse_06(path)
        elif mode == "07":
            segs = parse_07(path)
        elif mode == "08":
            segs = parse_08(path)
        else:
            segs = parse_generic_narrator(path)

        counts = {}
        for spk, _ in segs:
            counts[spk] = counts.get(spk, 0) + 1
        for spk, n in sorted(counts.items(), key=lambda x: -x[1]):
            vname = {v: k for k, v in V.items()}.get(V.get(spk, ""), "?")
            print(f"  {spk:<12} {n:>3}  ({vname})")
        print(f"  subtotal: {len(segs)}")
        all_segs.extend((label, spk, txt) for spk, txt in segs)

    print(f"\nTotal segments: {len(all_segs)}")

    print("\nGenerating audio...")
    files = []
    for i, (label, spk, text) in enumerate(all_segs):
        if not text.strip() or spk not in V:
            continue
        p = tts(spk, text, i, label[:20])
        if p:
            files.append(p)

    if not files:
        print("No segments generated.")
        return

    output = AUDIO_DIR / "phase2_reading.mp3"
    print(f"\nConcatenating {len(files)} files...")
    concatenate(files, output)


if __name__ == "__main__":
    main()
