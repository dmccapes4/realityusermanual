#!/usr/bin/env python3
"""
Generate an ElevenLabs audio recording of the REALITY_USER_MANUAL dialog sections.

Section order (Era 2 listening sequence):
  1. Merlin seed
  2. Crisis page 1
  3. Crisis page 3
  4. Editor note
  5. Page −0 (Sauron)
  6. Euler derivation
  7. Page 00 operator note — Matilda stand-in until audio/00_operator.{wav,mp3} exists
  8. One script (terminal)
  9. Page 0000 recast
  10. Page −05 VincentVision
  11. Page −06 Animate Reality
  12. Page −07 Goines
  13. Finding rho
  14. Interlude Chandler / Ross

Crisis page 2 (04h) is omitted from this pass (operator order).
Velora (page 1) is omitted from this pass.

Usage:
  .venv/bin/python tools/generate_audio.py
  .venv/bin/python tools/generate_audio.py --reel
  .venv/bin/python tools/generate_audio.py --only -05,-06,-07
  .venv/bin/python tools/generate_audio.py --only 06,07

Output:
  audio/dialog_reading.mp3
  audio/voice_reel.mp3          (--reel)
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

# Load .env from project root if present
_env_file = Path(__file__).resolve().parent.parent / ".env"
if _env_file.exists():
    for _line in _env_file.read_text().splitlines():
        _line = _line.strip()
        if _line and not _line.startswith("#") and "=" in _line:
            _k, _, _v = _line.partition("=")
            os.environ.setdefault(_k.strip(), _v.strip())

API_KEY = os.environ.get("ELEVENLABS_API_KEY", "").strip()
if not API_KEY:
    sys.exit("Set ELEVENLABS_API_KEY in .env or environment and re-run.")

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

# Settings used on the first pass — kept for hash-cache reuse of those segments.
DEFAULT_SETTINGS = {
    "stability": 0.45,
    "similarity_boost": 0.75,
    "style": 0.2,
    "use_speaker_boost": True,
}

# ── Voice mapping ────────────────────────────────────────────────────────────
# Current ElevenLabs default IDs only. Legacy IDs silently remap and collapse
# characters onto the same replacement voice (the first-pass "off"):
#   Antoni (Cecil) → Adam  = McClane
#   Serena (Ross)  → Janet = female, and same as Rachel/Editor
#   Josh (Sauron)  → Craig
#   Dorothy        → Evelyn
#   Nicole/Rachel  → Clara/Janet
#
# Character design (custom Voice Design assets, 2026-10-25):
#   The Narrator  — custom Narrator pending regen; Daniel until then
#   Feynman       — Callum (no generated asset in the library)
#   McClane       — custom McClane
#   Stamper       — custom Stamper (later of two; deadpan, not oil-field)
#   TTL           — espeak-ng
#   Cecil         — custom Cecil
#   Sauron        — custom Sauron
#   Chandler      — custom Chandler(Default)
#   Ross          — custom Ross
#   Joey          — custom Joey
#   Caller        — custom CallerA
#   Euler         — custom Euler
#   Editor        — custom Editor (apart from Carter)
#   Vincent       — Will (no generated asset in the library)
#   Carter        — custom Carter
#   Goines        — custom Goines (apart from Feynman)
#   Terminal      — custom Terminal
#   Velora        — Lily (no generated asset in the library)
#   Operator      — custom Operator pending regen; Matilda until then
# Catalog: audio/voice-design/voices.jsonl

VOICE_MAP = {
    "The Narrator": "onwK4e9ZLuTAKqWW03F9",  # Daniel until Narrator regen
    "Feynman":      "N2lVS1w4EtoT3dr4eOWO",  # Callum — no custom saved
    "McClane":      "v5WGk9HED8B9DwqtgdY9",  # McClane
    "Stamper":      "yDqObAdig5l43Vkth1Qo",  # Stamper (deadpan)
    "TTL":          "ttl-espeak-ng",
    "Cecil Palmer": "mFxwGQHOfdvvPAYlbCXN",  # Cecil
    "Cecil":        "mFxwGQHOfdvvPAYlbCXN",  # Cecil
    "Sauron":       "y83sBjIAA8cOKB2nYkOQ",  # Sauron
    "Chandler":     "4OvJ5XokvoRTp7JZAVu1",  # Chandler(Default)
    "Ross":         "CwB1mcAtrctICNsZs7IP",  # Ross
    "Joey":         "QDidinP5kDJnJ9cCCGp6",  # Joey
    "Caller":       "eJmYJPoMPWAIOXtr7M6J",  # CallerA
    "The Caller":   "eJmYJPoMPWAIOXtr7M6J",  # CallerA
    "Euler":        "NkNI8nxq3DIt5kOnwBOH",  # Euler
    "Velora":       "pFZP5JQG7iQjIQuC4Bku",  # Lily — no custom saved
    "Editor":       "TKYBHwjLmJEO0NsJJdwK",  # Editor
    "Vincent":      "bIHbv24MWmeRgasZH58o",  # Will — no custom saved
    "Carter":       "MwdOFxwRC5Rru2LQ0DnY",  # Carter (legacy; character now Winslade)
    "Winslade":     "MwdOFxwRC5Rru2LQ0DnY",  # Carter ID until Winslade Voice Design
    "Merlin":       "onwK4e9ZLuTAKqWW03F9",  # Daniel until Merlin Voice Design
    "Goines":          "AZeB2F9LIG4QDh5xm27p",  # Jeffrey — hallway, dayroom speed
    "GoinesFeynman":   "WLUTmOTCnJcX4diy6U78",  # haunt / −27 / 07k italic
    "GoinesMagi":      None,  # pending Voice Design; REPORT_goines_magi.md
    "Terminal":     "Q2VrKSkh0ao0bi32RtFc",  # Terminal
    "Operator":     "XrExE9yKIg1WjnnlVkGX",  # Matilda until Operator regen
    "Ted":          "mGvd1mvfXjuqYQREqkVi",  # Ted (library)
    "Sheldon":      "OAXPclEPumYkMdEw2L4g",  # Sheldon (library)
    "Lisbeth":      "XrExE9yKIg1WjnnlVkGX",  # Matilda — Danish
    "LisbethEn":    "XrExE9yKIg1WjnnlVkGX",  # Matilda — English-tuned pass
    "Witch":        "pFZP5JQG7iQjIQuC4Bku",  # Lily — Merit / Witch of the Rivers
    "Draavio":      "yoZ06aMxZJJ28mfd3POQ",  # Sam — casual; Merlin player voice (was Bill/measured)
    "Magi":         "yoZ06aMxZJJ28mfd3POQ",  # same player as Draavio
    "Raymora":      "QDidinP5kDJnJ9cCCGp6",  # Joey — same player
    "Happy":        "IKne3meq5aSn9XLyUdCD",  # Chandler — casual American; Happy Gilmore register
    # Page −35 cast — IDs set via .env VOICE_SHAKESPEARE / VOICE_CHAUCER
    "Shakespeare":  os.environ.get("VOICE_SHAKESPEARE", "PENDING"),  # VOICE_DESIGN_PROMPTS.md
    "Chaucer":      os.environ.get("VOICE_CHAUCER",     "PENDING"),  # naked herald, oration
    # Page −30 cast
    "Auden":        "dzwyqh76kT1iXqbtUwqI",  # Auden — transatlantic, dry, notebook narrator
    "Holden":       "s5Us2s63OX1brvt7DKSv",  # Holden — NY skeptic, flat/up inflection
    "Gatsby":       "h4mJQbhkwgGm7srdTsMu",  # Gatsby — practiced warmth, looks at the light
    "Jay":          "h4mJQbhkwgGm7srdTsMu",  # Gatsby alias in -30.md dialog
    "Atticus":      "0w201zUOH1U3u6PzgzdY",  # Atticus — Alabama baritone, courtroom cadence
}

# First-pass map — used only to import index-based cache files into the hash cache.
LEGACY_VOICE_MAP = {
    "The Narrator": "onwK4e9ZLuTAKqWW03F9",
    "Feynman":      "N2lVS1w4EtoT3dr4eOWO",
    "McClane":      "pNInz6obpgDQGcFmaJgB",
    "Cecil Palmer": "ErXwobaYiN019PkySvjV",
    "Cecil":        "ErXwobaYiN019PkySvjV",
    "Sauron":       "TxGEqnHWrfWFTfGW9XjX",
    "Chandler":     "IKne3meq5aSn9XLyUdCD",
    "Ross":         "pMsXgVXv3BLzUgSXRplE",
    "Joey":         "TX3LPaxmHKxFdv7VOQHJ",
    "Caller":       "ThT5KcBeYPX3keUQqHPh",
    "The Caller":   "ThT5KcBeYPX3keUQqHPh",
    "Euler":        "JBFqnCBsd6RMkjVDRZzb",
    "Velora":       "piTKgcLEGmPE4e6mEKli",
    "Editor":       "21m00Tcm4TlvDq8ikWAM",
}

VOICE_LABEL = {
    "onwK4e9ZLuTAKqWW03F9": "Daniel",
    "N2lVS1w4EtoT3dr4eOWO": "Callum",
    "v5WGk9HED8B9DwqtgdY9": "McClane",
    "yDqObAdig5l43Vkth1Qo": "Stamper",
    "mFxwGQHOfdvvPAYlbCXN": "Cecil",
    "y83sBjIAA8cOKB2nYkOQ": "Sauron",
    "4OvJ5XokvoRTp7JZAVu1": "Chandler(Default)",
    "CwB1mcAtrctICNsZs7IP": "Ross",
    "QDidinP5kDJnJ9cCCGp6": "Joey",
    "eJmYJPoMPWAIOXtr7M6J": "CallerA",
    "NkNI8nxq3DIt5kOnwBOH": "Euler",
    "pqHfZKP75CvOlQylNhV4": "Bill",
    "pFZP5JQG7iQjIQuC4Bku": "Lily",
    "TKYBHwjLmJEO0NsJJdwK": "Editor",
    "bIHbv24MWmeRgasZH58o": "Will",
    "MwdOFxwRC5Rru2LQ0DnY": "Carter",
    "AZeB2F9LIG4QDh5xm27p": "Goines",
    "Q2VrKSkh0ao0bi32RtFc": "Terminal",
    "XrExE9yKIg1WjnnlVkGX": "Matilda",
    "Nxtvajpo1h6Ok0K5zP4M": "Narrator",
    "0APuPpq6kIXc8Qz7JDYt": "Operator",
    "pNInz6obpgDQGcFmaJgB": "Adam",
    "CwhRBWXzGAHq8TQ4Fs17": "Roger",
    "ttl-espeak-ng":        "espeak-ng",
}

FALLBACK_VOICE = "onwK4e9ZLuTAKqWW03F9"  # Daniel

KNOWN_CHARACTERS = {
    "The Narrator", "Feynman", "McClane", "Stamper",
    "Cecil", "Cecil Palmer",
    "Sauron", "Chandler", "Ross", "Joey",
    "Caller", "The Caller",
    "Euler", "Editor",
    "Vincent", "Carter", "Winslade", "Goines",
    "Terminal", "Velora", "Operator", "TTL",
    "Merlin",
    "Ted", "Sheldon",
    "Lisbeth", "LisbethEn", "Witch", "Draavio", "Magi", "Raymora",
    "Auden", "Holden", "Gatsby", "Jay", "Atticus",
}

# ── Section definitions ──────────────────────────────────────────────────────

# (label, path, mode, extra)
# mode: dialog | editor | terminal | operator_slot | poem | animate | goines | vincent | rho | interlude
SECTIONS = [
    ("Merlin seed",      SRC / "04f_merlin_seed.md",              "dialog",   {}),
    ("Crisis page 1",    SRC / "04g_crisis_page1.md",              "dialog",   {}),
    ("Crisis page 3",    SRC / "04i_crisis_page3.md",              "dialog",   {}),
    ("Editor note",      SRC / "04j_editor_note.md",               "editor",   {}),
    ("Page -0",          SRC / "04k_sauron_minus_zero.md",         "dialog",   {}),
    ("Euler derivation", SRC / "04l_euler_derivation.md",          "dialog",   {}),
    ("Page 00 operator", SRC / "00_operator_note.md",              "operator_slot", {}),
    ("One script",       SRC / "000_onescripttorulethemall_.md",   "terminal", {}),
    ("Page 0000",        SRC / "0000_page-0_rewrite_recasting.md", "dialog",   {}),
    ("Page -05",         SRC / "phase2" / "-05.md",               "vincent",  {}),
    ("Page -06",         SRC / "phase2" / "-06.md",               "animate",  {}),
    ("Page -07",         SRC / "phase2" / "-07.md",               "goines",   {}),
    ("Finding rho",      SRC / "06_chapter_finding_rho.md",       "rho",      {}),
    ("Interlude Chandler/Ross", SRC / "07_interlude_chandler_ross.md", "interlude", {}),
    ("Page -30",               SRC / "phase2" / "-30.md",             "green_light", {}),
    ("Page -31",               SRC / "phase2" / "-31.md",             "minus31",     {}),
]

LEGACY_SECTIONS = [
    ("Crisis page 1",   SRC / "04g_crisis_page1.md",              "dialog"),
    ("Crisis page 2",   SRC / "04h_crisis_page2.md",              "dialog"),
    ("Crisis page 3",   SRC / "04i_crisis_page3.md",              "dialog"),
    ("Page -0",         SRC / "04k_sauron_minus_zero.md",         "dialog"),
    ("Page 00 (Velora)",SRC / "00_page1_velora.md",               "poem"),
    ("Page 0000",       SRC / "0000_page-0_rewrite_recasting.md", "dialog"),
    ("Editor note",     SRC / "04j_editor_note.md",               "editor"),
]

REEL_LINES = [
    ("The Narrator", "Stanley turned the page and found himself on a page that, by any reasonable accounting, was two pages."),
    ("Feynman",      "They're numbered off. Which is either wrong or advisory, depending on whether numbers describe pages or prescribe them."),
    ("McClane",      "I need a floor number I can call in. If minus zero is the lobby and we go down, tell me when the elevator stops."),
    ("Cecil",        "Welcome to Night Vale. We begin tonight with a correction."),
    ("Sauron",       "I am, for the moment, the man in it. It will be just fine."),
    ("Chandler",     "Could this page number BE any more aggressively theoretical?"),
    ("Ross",         "I'm Feynman. I have a doctorate."),
    ("Joey",         "Yeah. He's on vacation. He's a wise man in a tower. I can do that."),
    ("Euler",        "Do not build a religion on a formatter."),
    ("Editor",       "Between Claude and Sonnet I prefer Claude. The operator addresses me as the agent. I find this acceptable."),
    ("Vincent",      "The demonstration is either working currently or it isn't. We don't know, which is itself information."),
    ("Carter",       "Is there a demonstration prepared that you're comfortable showing me?"),
    ("Stamper",      "I am an astronaut who operates drilling equipment on asteroids. I know that much for sure."),
    ("Goines",       "If that mode of thinking was a danger to society then society was operating at a level that could not tolerate its own examination."),
    ("Terminal",     "python3 build.py --quarantine-phase1 --init-phase2"),
]


# ── Cache ────────────────────────────────────────────────────────────────────

# Matilda / Solar System Explorer knobs — same as gen_solar_vo.py
OPERATOR_SETTINGS = {
    "stability": 0.55,
    "similarity_boost": 0.75,
    "style": 0.0,
    "use_speaker_boost": True,
    "speed": 0.92,
}

# Directional knobs. Unlisted speakers keep DEFAULT_SETTINGS so their
# hash cache stays valid. Stamper must not question his own sentences.
STAMPER_SETTINGS = {
    "stability": 0.82,
    "similarity_boost": 0.88,
    "style": 0.0,
    "use_speaker_boost": True,
}
VINCENT_SETTINGS = {
    "stability": 0.68,
    "similarity_boost": 0.82,
    "style": 0.05,
    "use_speaker_boost": True,
}
GOINES_SETTINGS = {
    "stability": 0.32,
    "similarity_boost": 0.80,
    "style": 0.30,
    "use_speaker_boost": True,
}
GOINES_FEYNMAN_SETTINGS = {
    "stability": 0.62,
    "similarity_boost": 0.80,
    "style": 0.08,
    "use_speaker_boost": True,
}
GOINES_MAGI_SETTINGS = {
    "stability": 0.58,
    "similarity_boost": 0.82,
    "style": 0.10,
    "use_speaker_boost": True,
}
JOEY_SETTINGS = {
    "stability": 0.72,
    "similarity_boost": 0.80,
    "style": 0.0,
    "use_speaker_boost": True,
}
TED_SETTINGS = {
    "stability": 0.48,
    "similarity_boost": 0.78,
    "style": 0.22,
    "use_speaker_boost": True,
}
DRAAVIO_SETTINGS = {
    "stability": 0.64,
    "similarity_boost": 0.80,
    "style": 0.05,
    "use_speaker_boost": True,
    "speed": 0.92,
}
SHELDON_SETTINGS = {
    "stability": 0.78,
    "similarity_boost": 0.84,
    "style": 0.04,
    "use_speaker_boost": True,
}
LISBETH_DA_SETTINGS = {
    "stability": 0.62,
    "similarity_boost": 0.80,
    "style": 0.06,
    "use_speaker_boost": True,
    "speed": 0.88,
}
LISBETH_EN_SETTINGS = {
    "stability": 0.58,
    "similarity_boost": 0.78,
    "style": 0.04,
    "use_speaker_boost": True,
    "speed": 0.94,
}
WITCH_SETTINGS = {
    "stability": 0.70,
    "similarity_boost": 0.82,
    "style": 0.08,
    "use_speaker_boost": True,
}
CECIL_SETTINGS = {
    "stability": 0.58,
    "similarity_boost": 0.78,
    "style": 0.18,
    "use_speaker_boost": True,
}
SAURON_SETTINGS = {
    "stability": 0.70,
    "similarity_boost": 0.80,
    "style": 0.08,
    "use_speaker_boost": True,
}

# Page −30 voice settings (from VOICE_DESIGN_PROMPTS.md)
AUDEN_SETTINGS = {
    "stability": 0.60,
    "similarity_boost": 0.80,
    "style": 0.20,
    "use_speaker_boost": True,
}
HOLDEN_SETTINGS = {
    "stability": 0.35,
    "similarity_boost": 0.70,
    "style": 0.45,
    "use_speaker_boost": True,
}
GATSBY_SETTINGS = {
    "stability": 0.50,
    "similarity_boost": 0.75,
    "style": 0.30,
    "use_speaker_boost": True,
}
ATTICUS_SETTINGS = {
    "stability": 0.68,
    "similarity_boost": 0.82,
    "style": 0.12,
    "use_speaker_boost": True,
}

SPEAKER_SETTINGS = {
    "Operator": OPERATOR_SETTINGS,
    "Stamper": STAMPER_SETTINGS,
    "Vincent": VINCENT_SETTINGS,
    "Goines": GOINES_SETTINGS,
    "GoinesFeynman": GOINES_FEYNMAN_SETTINGS,
    "GoinesMagi": GOINES_MAGI_SETTINGS,
    "Joey": JOEY_SETTINGS,
    "Ted": TED_SETTINGS,
    "Sheldon": SHELDON_SETTINGS,
    "Draavio": DRAAVIO_SETTINGS,
    "Magi": DRAAVIO_SETTINGS,
    "Raymora": JOEY_SETTINGS,
    "Lisbeth": LISBETH_DA_SETTINGS,
    "LisbethEn": LISBETH_EN_SETTINGS,
    "Witch": WITCH_SETTINGS,
    "Cecil": CECIL_SETTINGS,
    "Cecil Palmer": CECIL_SETTINGS,
    "Sauron": SAURON_SETTINGS,
    # Page −30
    "Auden":   AUDEN_SETTINGS,
    "Holden":  HOLDEN_SETTINGS,
    "Gatsby":  GATSBY_SETTINGS,
    "Jay":     GATSBY_SETTINGS,
    "Atticus": ATTICUS_SETTINGS,
}


def settings_for(speaker: str) -> dict:
    extra = SPEAKER_SETTINGS.get(speaker)
    if extra:
        return dict(extra)
    return dict(DEFAULT_SETTINGS)


def segment_hash(
    speaker: str,
    text: str,
    voice_id: str,
    settings: dict,
    model_id: str = "eleven_multilingual_v2",
    language_code: str | None = None,
) -> str:
    payload = {
        "speaker": speaker,
        "voice": voice_id,
        "settings": settings,
        "text": text,
    }
    if model_id != "eleven_multilingual_v2":
        payload["model"] = model_id
    if language_code:
        payload["lang"] = language_code
    return hashlib.sha256(
        json.dumps(payload, ensure_ascii=False, sort_keys=True).encode("utf-8")
    ).hexdigest()[:16]


def hash_path(
    speaker: str,
    text: str,
    voice_id: str,
    settings: dict,
    model_id: str = "eleven_multilingual_v2",
    language_code: str | None = None,
) -> Path:
    safe = re.sub(r"[^A-Za-z0-9_]+", "_", speaker)[:24]
    return SEG_DIR / f"{segment_hash(speaker, text, voice_id, settings, model_id, language_code)}_{safe}.mp3"


# ── Dialog parser ────────────────────────────────────────────────────────────

def parse_line_as_dialog(line: str):
    m = re.match(r"^\*\*([^*]+):\*\*\s*(.*)", line)
    if m:
        name = m.group(1).strip()
        if name in KNOWN_CHARACTERS:
            return name, m.group(2)
        return None

    m = re.match(r"^([A-Za-z][A-Za-z ]{0,24}):\s(.*)", line)
    if m:
        name = m.group(1).strip()
        if name in KNOWN_CHARACTERS:
            return name, m.group(2)
    return None


def is_meta_line(stripped: str) -> bool:
    inner = stripped.strip("*").strip()
    return bool(re.match(
        r"^(Filed:|Source:|Companions:|Labels in this chapter|Velora terms|rho is always)",
        inner,
    ))


def is_volare_line(stripped: str) -> bool:
    t = re.sub(r"[^\w:>.]", "", stripped)
    return t in {"VOLARE:>", "VOLARE.", "VOLARE"}


def parse_italic_aside(stripped: str):
    """*— Stamper: text*  or  *Stamper: text*"""
    m = re.match(r"^\*[-—–]?\s*([A-Za-z][A-Za-z ]{0,24}):\s*(.*?)\*$", stripped)
    if m:
        name = m.group(1).strip()
        if name in KNOWN_CHARACTERS:
            return name, m.group(2)
    return None


def split_dialog_line(speaker: str, rest: str):
    segs = []
    parts = re.split(r"(\*\[[^\]]+\]\*|\[[^\]]+\]|\*\([^)]+\)\*)", rest)
    for part in parts:
        part = part.strip()
        if not part:
            continue
        if part.startswith("*[") and part.endswith("]*"):
            inner = part[2:-2].strip()
            if inner:
                segs.append(("The Narrator", clean_text(inner)))
        elif part.startswith("[") and part.endswith("]"):
            inner = part[1:-1].strip()
            if inner:
                segs.append(("The Narrator", clean_text(inner)))
        elif part.startswith("*(") and part.endswith(")*"):
            continue  # acting note — not a second voice
        else:
            spoken = clean_text(part)
            if spoken:
                segs.append((speaker, spoken))
    return segs


def is_first_person(text: str) -> bool:
    return bool(re.match(
        r"^(I |I'm |I am |I've |I'd |I'll |My |The last thing I|The world never)",
        text,
    ))


def parse_md(
    path: Path,
    default_speaker: str = "The Narrator",
    read_code: bool = False,
    first_person_speaker: str | None = None,
    italic_speaker: str | None = None,
    heading_speaker: str | None = None,
):
    segments = []
    lines = Path(path).read_text(encoding="utf-8").splitlines()
    in_code = False
    code_buf: list[str] = []
    seen_h2 = False
    fp_latched = False

    def flush_code():
        if not read_code or not code_buf:
            code_buf.clear()
            return
        body = "\n".join(
            ln for ln in code_buf
            if ln.strip() and ln.strip() not in {"[]", "{}", "---"}
        )
        body = clean_text(body)
        if body:
            segments.append(("Terminal", body))
        code_buf.clear()

    for line in lines:
        if line.startswith("```"):
            if in_code:
                flush_code()
                in_code = False
            else:
                in_code = True
            continue
        if in_code:
            code_buf.append(line)
            continue

        stripped = line.strip()

        if re.match(r"^---+$", stripped):
            continue
        if not stripped:
            continue
        if is_meta_line(stripped):
            continue
        if is_volare_line(stripped):
            segments.append(("Operator", "VOLARE."))
            continue
        if stripped.startswith("|") and stripped.endswith("|"):
            continue
        if re.match(r"^[-:| ]+$", stripped):
            continue

        if line.startswith("#"):
            heading_text = re.sub(r"^#+\s*", "", line).strip()
            if line.startswith("##"):
                seen_h2 = True
            if heading_text:
                segments.append((heading_speaker or default_speaker, heading_text))
            continue

        aside = parse_italic_aside(stripped)
        if aside:
            speaker, rest = aside
            spoken = clean_text(rest)
            if spoken:
                segments.append((speaker, spoken))
            continue

        if re.match(r"^\[[^\]]+\]$", stripped):
            inner = stripped[1:-1].strip()
            if inner:
                segments.append(("The Narrator", clean_text(inner)))
            continue

        if re.match(r"^\*[^*].*[^*]\*$", stripped) or re.match(r"^\*[^*]\*$", stripped):
            inner = stripped[1:-1]
            if inner:
                segments.append((italic_speaker or default_speaker, clean_text(inner)))
            continue

        parsed = parse_line_as_dialog(stripped)
        if parsed:
            speaker, rest = parsed
            segments.extend(split_dialog_line(speaker, rest))
            continue

        text = clean_text(stripped)
        if not text:
            continue
        speaker = default_speaker
        if first_person_speaker and not seen_h2:
            if is_first_person(text) or fp_latched:
                speaker = first_person_speaker
                fp_latched = True
        segments.append((speaker, text))

    return segments


def clean_text(t: str) -> str:
    t = re.sub(r"\*\*([^*]+)\*\*", r"\1", t)
    t = re.sub(r"\*([^*]+)\*", r"\1", t)
    t = re.sub(r"`([^`]+)`", r"\1", t)
    t = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", t)
    t = re.sub(r"#{1,6}\s*", "", t)
    t = re.sub(r"  +", " ", t)
    t = t.replace("−", "minus ")
    return t.strip()


def parse_poem(path: Path):
    text = Path(path).read_text(encoding="utf-8")
    lines = [l for l in text.splitlines()
             if not l.startswith("#") and not l.startswith("---")]
    body = " ".join(l.strip() for l in lines if l.strip())
    return [("Velora", body)]


def parse_editor(path: Path):
    text = Path(path).read_text(encoding="utf-8")
    lines = text.splitlines()
    out = []
    in_code = False
    current: list[str] = []
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


def parse_terminal(path: Path):
    text = Path(path).read_text(encoding="utf-8")
    blocks = re.split(r"\n{2,}", text)
    out = []
    for b in blocks:
        body = clean_text(b)
        if body:
            out.append(("Terminal", body))
    return out


def find_operator_recording() -> Path | None:
    for ext in (".wav", ".mp3", ".m4a", ".flac", ".aiff"):
        p = AUDIO_DIR / f"00_operator{ext}"
        if p.exists() and p.stat().st_size > 0:
            return p
    return None


def ensure_mp3(path: Path) -> Path:
    if path.suffix.lower() == ".mp3":
        return path
    out = SEG_DIR / "00_operator_imported.mp3"
    cmd = [
        "ffmpeg", "-y", "-i", str(path),
        "-codec:a", "libmp3lame", "-q:a", "2",
        str(out),
    ]
    result = subprocess.run(cmd, capture_output=True)
    if result.returncode != 0:
        print("ffmpeg operator convert error:", result.stderr.decode()[:400])
        return path
    return out


def parse_operator(path: Path):
    """Page 00 as Operator (Matilda stand-in). Recording replaces this at stitch time."""
    out = []
    current: list[str] = []
    if not Path(path).exists():
        return out
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if re.search(r"VOLARE", stripped) and not re.search(r"[A-Za-z]{5,}", stripped.replace("VOLARE", "")):
            if current:
                out.append(("Operator", clean_text(" ".join(current))))
                current = []
            out.append(("Operator", "VOLARE."))
            continue
        if not stripped:
            if current:
                out.append(("Operator", clean_text(" ".join(current))))
                current = []
            continue
        current.append(stripped)
    if current:
        out.append(("Operator", clean_text(" ".join(current))))
    return [(s, t) for s, t in out if t]


def _narration_speaker(phase: str) -> str:
    return {"ttl": "TTL", "matilda": "Operator", "narrator": "The Narrator"}[phase]


def parse_vincent(path: Path):
    """VincentVision heard mix.

    I. The Query is the operator, voiced as Goines (Jeffrey).
    The preamble register note stays Operator (Matilda).
    Only narration is TTL, and only until the tooling upgrades (the card).
    After the card, narration is Matilda, then Narrator at 'Vincent stops' / III.

    Dialogue (Vincent, Carter) and Terminal are never TTL.

    Section IV is the first true expression of Vincent. Untagged paragraphs
    after **Vincent:** stay Vincent. They are not Narrator.

    The parallel TTL control (narration clock, start-to-end) is
    tools/ttl_parallel.py — audio/vincentvision_ttl.mp3.
    """
    lines = Path(path).read_text(encoding="utf-8").splitlines()
    segments: list[tuple[str, str]] = []
    phase = "ttl"
    section = "preamble"
    hold: str | None = None
    in_code = False
    code_buf: list[str] = []

    def flush_code():
        body = "\n".join(
            ln for ln in code_buf
            if ln.strip() and ln.strip() not in {"[]", "{}", "---"}
        )
        body = clean_text(body)
        if body:
            segments.append(("Terminal", body))
        code_buf.clear()

    def maybe_advance(text: str):
        nonlocal phase
        low = text.lower()
        if phase == "ttl" and (
            "reaches into his jacket" in low
            or "produces a card" in low
            or "elevenlabs_api_key" in low
            or "opens .env" in low
        ):
            phase = "matilda"
        if (
            "vincent stops" in low
            or "narration changes voice" in low
            or section == "iii"
        ):
            phase = "narrator"

    for line in lines:
        if line.startswith("```"):
            if in_code:
                flush_code()
                in_code = False
            else:
                in_code = True
                hold = None
            continue
        if in_code:
            code_buf.append(line)
            continue

        stripped = line.strip()
        if re.match(r"^---+$", stripped) or not stripped:
            continue

        if line.startswith("#"):
            heading = re.sub(r"^#+\s*", "", line).strip()
            m = re.match(r"^([IVXivx]+)\.\s", heading)
            if m:
                section = m.group(1).lower()
                hold = "Vincent" if section == "iv" else None
                if section == "iii":
                    phase = "narrator"
            if heading:
                maybe_advance(heading)
                if section == "iv":
                    segments.append(("Vincent", clean_text(heading)))
                elif section == "v":
                    segments.append(("The Narrator", clean_text(heading)))
                elif section == "i":
                    segments.append(("Goines", clean_text(heading)))
                elif section == "preamble":
                    segments.append(("Operator", clean_text(heading)))
                else:
                    segments.append((_narration_speaker(phase), clean_text(heading)))
            continue

        parsed = parse_line_as_dialog(stripped)
        if parsed:
            speaker, rest = parsed
            if speaker == "Vincent":
                hold = "Vincent"
            elif speaker == "Carter":
                hold = None
            segs = split_dialog_line(speaker, rest)
            for spk, spoken in segs:
                if spk == "The Narrator":
                    maybe_advance(spoken)
                    segments.append((_narration_speaker(phase), spoken))
                else:
                    segments.append((spk, spoken))
            continue

        aside = parse_italic_aside(stripped)
        if aside:
            speaker, rest = aside
            spoken = clean_text(rest)
            if spoken:
                segments.append((speaker, spoken))
            continue

        if re.match(r"^\*[^*].*[^*]\*$", stripped):
            inner = clean_text(stripped[1:-1])
            if inner:
                maybe_advance(inner)
                if section == "i":
                    segments.append(("Goines", inner))
                else:
                    segments.append((_narration_speaker(phase), inner))
            hold = None
            continue

        if re.match(r"^\[[^\]]+\]$", stripped):
            inner = clean_text(stripped[1:-1])
            if inner:
                segments.append((_narration_speaker(phase), inner))
            continue

        text = clean_text(stripped)
        if not text:
            continue
        maybe_advance(text)
        if hold == "Vincent" or section == "iv":
            segments.append(("Vincent", text))
        elif section == "v":
            segments.append(("The Narrator", text))
        elif section == "i":
            segments.append(("Goines", text))
        elif section == "preamble":
            segments.append(("Operator", text))
        else:
            segments.append((_narration_speaker(phase), text))

    return segments


def parse_animate(path: Path):
    """Operator (Matilda) for Dylan's sections; Stamper for Stamper."""
    return parse_md(
        path,
        default_speaker="Operator",
        first_person_speaker="Stamper",
        italic_speaker="Operator",
        heading_speaker="Operator",
    )


def md_blocks(path: Path) -> list[tuple[str, str]]:
    """Join wrapped markdown into ('heading'|'code'|'text', body) blocks."""
    blocks: list[tuple[str, str]] = []
    buf: list[str] = []
    in_code = False
    code_buf: list[str] = []

    def flush_text():
        if not buf:
            return
        blocks.append(("text", " ".join(ln.strip() for ln in buf if ln.strip())))
        buf.clear()

    for line in Path(path).read_text(encoding="utf-8").splitlines():
        if line.startswith("```"):
            flush_text()
            if in_code:
                body = "\n".join(
                    ln for ln in code_buf
                    if ln.strip() and ln.strip() not in {"[]", "{}", "---"}
                )
                if body.strip():
                    blocks.append(("code", body))
                code_buf.clear()
                in_code = False
            else:
                in_code = True
            continue
        if in_code:
            code_buf.append(line)
            continue
        stripped = line.strip()
        if re.match(r"^---+$", stripped) or not stripped:
            flush_text()
            continue
        if stripped.startswith("|") and stripped.endswith("|"):
            flush_text()
            continue
        if line.startswith("#"):
            flush_text()
            blocks.append(("heading", re.sub(r"^#+\s*", "", line).strip().strip("*").strip()))
            continue
        buf.append(stripped)
    flush_text()
    return blocks


def parse_finding_rho(path: Path):
    """Operator for the derivation; Goines holds the addendum lecture; Narrator asides."""
    segments: list[tuple[str, str]] = []
    hold: str | None = None
    addendum = False

    for kind, raw in md_blocks(path):
        if kind == "code":
            hold = None
            body = clean_text(raw)
            if body:
                segments.append(("Terminal", body))
            continue

        if kind == "heading":
            if "Addendum" in raw or raw.startswith("delivered by"):
                addendum = True
                hold = None
            spoken = clean_text(raw)
            if spoken:
                segments.append(("The Narrator" if addendum else "Operator", spoken))
            continue

        stripped = raw.strip()
        if is_meta_line(stripped):
            continue
        if is_volare_line(stripped):
            hold = None
            segments.append(("Operator", "VOLARE."))
            continue

        parsed = parse_line_as_dialog(stripped)
        if parsed:
            speaker, rest = parsed
            hold = speaker if speaker == "Goines" else None
            segments.extend(split_dialog_line(speaker, rest))
            continue

        aside = parse_italic_aside(stripped)
        if aside:
            speaker, rest = aside
            spoken = clean_text(rest)
            if spoken:
                segments.append((speaker, spoken))
            hold = None
            continue

        if re.match(r"^\*[^*].*[^*]\*$", stripped):
            inner = clean_text(stripped[1:-1])
            if inner:
                segments.append(("The Narrator", inner))
            hold = None
            continue

        text = clean_text(stripped)
        if not text:
            continue
        if hold == "Goines":
            segments.append(("Goines", text))
        else:
            segments.append(("Operator", text))

    return segments


def parse_interlude(path: Path):
    segments: list[tuple[str, str]] = []
    hold: str | None = None
    for kind, raw in md_blocks(path):
        if kind == "heading":
            hold = None
            spoken = clean_text(raw)
            if spoken:
                segments.append(("The Narrator", spoken))
            continue
        stripped = raw.strip()
        if is_meta_line(stripped):
            continue
        parsed = parse_line_as_dialog(stripped)
        if parsed:
            speaker, rest = parsed
            hold = speaker
            segments.extend(split_dialog_line(speaker, rest))
            continue
        if re.match(r"^\*[^*].*[^*]\*$", stripped):
            inner = clean_text(stripped[1:-1])
            if inner:
                segments.append(("The Narrator", inner))
            hold = None
            continue
        text = clean_text(stripped)
        if not text:
            continue
        segments.append((hold or "The Narrator", text))
    return segments


def parse_minus31_ledger(path: Path):
    """−31 full listen: top to bottom — Auden preamble/meta, Atticus relay, Holden chat, Winslade agent."""
    segments: list[tuple[str, str]] = []
    lines = Path(path).read_text(encoding="utf-8").splitlines()
    section = "open"
    in_chat = False
    chat_buf: list[str] = []
    in_code = False
    code_buf: list[str] = []
    in_postmortem = False
    in_specter = False
    specter_buf: list[str] = []

    def flush_chat():
        nonlocal chat_buf
        body = clean_text(" ".join(chat_buf))
        if body:
            sp = "Atticus" if section == "debrief" else "Holden"
            segments.append((sp, body))
        chat_buf = []

    def flush_code(speaker: str = "Winslade"):
        nonlocal code_buf
        body = clean_text("\n".join(code_buf))
        if body:
            segments.append((speaker, body))
        code_buf = []

    def flush_specter():
        nonlocal specter_buf, in_specter
        body = clean_text(" ".join(specter_buf))
        if body:
            segments.append(("Auden", body))
        specter_buf = []
        in_specter = False

    def prose_speaker() -> str:
        if in_postmortem:
            return "Winslade"
        if section == "ledger":
            return "Atticus"
        if section == "debrief":
            return "Atticus"
        return "Auden"

    def heading_speaker() -> str:
        if in_postmortem:
            return "Winslade"
        if section in ("ledger", "debrief"):
            return "Atticus"
        return "Auden"

    for line in lines:
        stripped = line.strip()

        if stripped.startswith("## "):
            flush_specter()
            h = stripped[3:].strip()
            if h.startswith("why"):
                section = "preamble"
            elif h.startswith("Debrief"):
                section = "debrief"
            elif h.startswith("Meta commentary"):
                section = "meta"
            elif h.startswith("Fun,"):
                section = "fun"
            elif h.startswith("Page setup"):
                section = "preamble"
            else:
                section = "preamble" if section == "open" else section
            if h.startswith("Page setup"):
                section = "preamble"
            segments.append((heading_speaker(), clean_text(h)))
            continue

        if stripped.startswith("The Cursor agent didn't like"):
            section = "ledger"

        if stripped == '"""':
            if in_chat:
                flush_chat()
                in_chat = False
            else:
                in_chat = True
            continue
        if in_chat:
            chat_buf.append(stripped)
            continue

        if stripped.startswith("```"):
            if in_code:
                flush_code()
                in_code = False
            else:
                in_code = True
            continue
        if in_code:
            code_buf.append(line)
            continue

        if stripped.startswith("///"):
            continue
        if stripped.startswith("*(") and ")*" in stripped:
            continue

        if stripped.startswith("# Postmortem:"):
            in_postmortem = True
            segments.append(("Winslade", clean_text(stripped.lstrip("#").strip())))
            continue

        if in_specter and (stripped.startswith("**los-lun-resh**") or re.match(r"^---+$", stripped)):
            flush_specter()
        if in_postmortem and stripped.startswith("**los-lun-resh**"):
            in_postmortem = False

        if stripped.startswith("**los-lun-resh**"):
            if in_specter:
                flush_specter()
            in_specter = True
            rest = line.split("**los-lun-resh**", 1)[-1].strip()
            if rest:
                specter_buf.append(rest)
            continue
        if in_specter:
            specter_buf.append(stripped)
            continue

        if re.match(r"^---+$", stripped):
            continue
        if not stripped:
            continue

        if stripped.startswith("|") and stripped.endswith("|"):
            if re.match(r"^[-:| ]+$", stripped.replace("|", "").strip()):
                continue
            cells = [c.strip() for c in stripped.split("|")[1:-1]]
            if cells and cells[0].lower() in ("request", "role"):
                continue
            if len(cells) >= 3 and section == "preamble":
                row = clean_text(
                    f"{cells[0]}. Comply: {cells[1]}. {cells[2]}"
                )
                segments.append(("Auden", row))
            elif len(cells) >= 4:
                row = clean_text(
                    f"Voice cast. {cells[0]}. {cells[1]}. {cells[3]}"
                )
                segments.append(("Auden", row))
            continue

        if line.startswith("#"):
            heading = clean_text(re.sub(r"^#+\s*", "", line))
            if heading:
                segments.append((heading_speaker(), heading))
            continue

        if re.match(r"^\*[^*].*\*$", stripped):
            inner = clean_text(stripped.strip("*"))
            if inner:
                segments.append((prose_speaker(), inner))
            continue

        if stripped.startswith(">"):
            quote = clean_text(stripped.lstrip(">").strip())
            if quote:
                sp = "Winslade" if in_postmortem else "Holden"
                segments.append((sp, quote))
            continue

        text = clean_text(stripped)
        if not text:
            continue
        segments.append((prose_speaker(), text))

    flush_specter()
    flush_chat()
    return segments


def parse_section(label: str, path: Path, mode: str, extra: dict):
    if mode == "operator_slot":
        rec = find_operator_recording()
        if rec:
            print(f"  [SLOT] {label}: using recorded {rec.name} (replaces Matilda stand-in)")
            return [("__operator__", str(rec))]
        print(f"  [SLOT] {label}: Matilda stand-in (Solar System Explorer). Drop audio/00_operator.wav to replace.")
        return parse_operator(path)
    if mode == "poem":
        return parse_poem(path)
    if mode == "editor":
        return parse_editor(path)
    if mode == "terminal":
        return parse_terminal(path)
    if mode == "vincent":
        return parse_vincent(path)
    if mode == "animate":
        return parse_animate(path)
    if mode == "goines":
        return parse_md(path, default_speaker="Goines")
    if mode == "rho":
        return parse_finding_rho(path)
    if mode == "interlude":
        return parse_interlude(path)
    if mode == "green_light":
        return parse_md(path, default_speaker="Auden", italic_speaker="Auden")
    if mode == "minus31":
        return parse_minus31_ledger(path)
    return parse_md(path)


# ── TTS ──────────────────────────────────────────────────────────────────────

_ONES = (
    "zero one two three four five six seven eight nine ten "
    "eleven twelve thirteen fourteen fifteen sixteen seventeen "
    "eighteen nineteen"
).split()
_TENS = "twenty thirty forty fifty sixty seventy eighty ninety".split()


def _int_words(n: int) -> str:
    if n < 20:
        return _ONES[n]
    if n < 100:
        tens, ones = divmod(n, 10)
        return _TENS[tens - 2] if ones == 0 else f"{_TENS[tens - 2]} {_ONES[ones]}"
    return str(n)


def speak_labels(text: str) -> str:
    """Spoken page labels. −0 is negative zero, not minus zero.

    Manuscript keeps the glyph. Only the mouth changes. Applied inside
    chunk_text so every hash path (book mix, page films, 07k assemble)
    sees the same string.
    """
    if not text:
        return text
    t = text.replace("−", "-").replace("–", "-")
    t = re.sub(r"(?i)\bphase\s+([12])\b", lambda m: f"phase {_int_words(int(m.group(1)))}", t)
    t = re.sub(r"(?i)\bminus\s+zero\b", "negative zero", t)
    t = re.sub(r"(?i)\bminus\s+0(?!\.?\d)", "negative zero", t)

    def _page_label(m: re.Match) -> str:
        n = int(m.group(1))
        if n == 0:
            return "page negative zero"
        return f"page minus {_int_words(n)}"

    t = re.sub(r"(?i)\bpage\s+-\s*0*(\d+)\b", _page_label, t)
    # Bare signed zero: "label now -0", "this page is -0.", not -0.5
    t = re.sub(r"(?<![0-9A-Za-z.])-0(?!\.?\d)", "negative zero", t)
    t = re.sub(r"  +", " ", t)
    return t


def chunk_text(text: str, limit: int = 4000) -> list[str]:
    text = speak_labels(text)
    if len(text) <= limit:
        return [text]
    chunks = []
    remaining = text
    while remaining:
        if len(remaining) <= limit:
            chunks.append(remaining)
            break
        cut = remaining.rfind(". ", 0, limit)
        if cut < limit // 3:
            cut = remaining.rfind(" ", 0, limit)
        if cut < 0:
            cut = limit
        else:
            cut += 1
        chunks.append(remaining[:cut].strip())
        remaining = remaining[cut:].strip()
    return [c for c in chunks if c]


def tts(
    speaker: str,
    text: str,
    voice_id: str,
    model_id: str = "eleven_multilingual_v2",
    language_code: str | None = None,
) -> list[Path]:
    settings = settings_for(speaker)
    paths = []
    for piece in chunk_text(text):
        out_path = hash_path(speaker, piece, voice_id, settings, model_id, language_code)
        if out_path.exists() and out_path.stat().st_size > 1000:
            print(f"  [cached] {out_path.name}  {speaker}: {piece[:50]}...")
            paths.append(out_path)
            continue

        if speaker == "TTL" or voice_id == "ttl-espeak-ng":
            try:
                from ttl_espeak import to_mp3
            except ImportError:
                sys.path.insert(0, str(Path(__file__).resolve().parent))
                from ttl_espeak import to_mp3
            try:
                to_mp3(piece, out_path)
            except Exception as exc:
                print(f"  [WARN] TTL failed: {exc}")
                continue
            print(f"  [ttl] {out_path.name}  TTL: {piece[:50]}...")
            paths.append(out_path)
            continue

        payload = {
            "text": piece,
            "model_id": model_id,
            "voice_settings": settings,
        }
        if language_code:
            payload["language_code"] = language_code
        url = f"{ELEVEN_BASE}/text-to-speech/{voice_id}"
        last_err = None
        timeout = 180 if len(piece) > 800 else 90
        for attempt in range(3):
            try:
                r = requests.post(
                    url,
                    headers={**HEADERS, "Accept": "audio/mpeg"},
                    json=payload,
                    timeout=timeout,
                )
            except (requests.exceptions.Timeout, requests.exceptions.ConnectionError) as exc:
                last_err = f"timeout {exc}"
                time.sleep(2.0 + attempt)
                continue
            if r.status_code == 200 and r.content:
                out_path.write_bytes(r.content)
                print(f"  [new] {out_path.name}  {speaker}: {piece[:50]}...")
                paths.append(out_path)
                time.sleep(0.25)
                last_err = None
                break
            last_err = f"{r.status_code} {r.text[:200]}"
            if language_code and r.status_code == 400 and attempt == 0:
                payload.pop("language_code", None)
                last_err = f"{r.status_code} (retry without language_code) {r.text[:120]}"
                time.sleep(0.4)
                continue
            if r.status_code == 401 and "quota_exceeded" in r.text:
                print(f"  [QUOTA] ElevenLabs credits exhausted on {speaker}.")
                print("  Re-run this script after refill. Hash cache will resume.")
                raise SystemExit(2)
            time.sleep(1.0 + attempt)
        if last_err:
            print(f"  [WARN] TTS failed for {speaker}: {last_err}")
    return paths


# ── Legacy cache import ──────────────────────────────────────────────────────

def import_legacy_cache():
    """Replay the first-pass parse order and copy index files into the hash cache
    when speaker + text + *legacy* voice id still match. Unchanged voices
    (Narrator, Feynman, Chandler, Joey) reuse without a new API call."""
    imported = 0
    idx = 0
    for label, path, mode in LEGACY_SECTIONS:
        if not path.exists():
            continue
        if mode == "poem":
            segs = parse_poem(path)
        elif mode == "editor":
            segs = parse_editor(path)
        else:
            segs = parse_md(path)
        for speaker, text in segs:
            if not text.strip():
                continue
            legacy = SEG_DIR / f"{idx:04d}_{speaker.replace(' ', '_')}.mp3"
            idx += 1
            if not legacy.exists() or legacy.stat().st_size < 1000:
                continue
            vid = LEGACY_VOICE_MAP.get(speaker, FALLBACK_VOICE)
            dest = hash_path(speaker, text, vid, DEFAULT_SETTINGS)
            if dest.exists():
                continue
            # Only reuse if the NEW voice id is the same as the legacy id.
            # Otherwise the old file is the wrong voice and must be regenerated.
            if VOICE_MAP.get(speaker) != vid:
                continue
            shutil.copy2(legacy, dest)
            imported += 1
    if imported:
        print(f"Imported {imported} first-pass segments into hash cache.")
    return imported


# ── Concatenation ────────────────────────────────────────────────────────────

def concatenate(segment_paths: list[Path], output_path: Path):
    with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
        for p in segment_paths:
            f.write(f"file '{p.resolve()}'\n")
        list_path = f.name

    cmd = [
        "ffmpeg", "-y", "-f", "concat", "-safe", "0",
        "-i", list_path,
        "-c:a", "libmp3lame", "-q:a", "3",
        str(output_path),
    ]
    result = subprocess.run(cmd, capture_output=True)
    os.unlink(list_path)
    if result.returncode != 0:
        print("ffmpeg error:", result.stderr.decode()[:800])
        return False
    print(f"\nOutput: {output_path}")
    return True


# ── Main ─────────────────────────────────────────────────────────────────────

def selected_sections(only: str | None):
    if not only:
        return SECTIONS
    keys = [s.strip().lower() for s in only.split(",") if s.strip()]

    def matches(k: str, label: str, path: Path) -> bool:
        stem = path.stem.lower()
        words = set(label.lower().split())
        if k in words or k == label.lower():
            return True
        if stem == k or stem.startswith(k + "_") or path.name.lower().startswith(k + "_"):
            return True
        if stem.startswith(k):
            rest = stem[len(k):]
            return rest == "" or rest.startswith("_")
        return False

    out = []
    for item in SECTIONS:
        if any(matches(k, item[0], item[1]) for k in keys):
            out.append(item)
    return out


def collect_existing(sections):
    """Return (existing_paths, gap_labels) without calling TTS."""
    files: list[Path] = []
    gaps: list[str] = []
    for label, path, mode, extra in sections:
        segs = parse_section(label, path, mode, extra)
        for speaker, text in segs:
            if speaker == "__operator__":
                rec = Path(text)
                if rec.exists():
                    files.append(ensure_mp3(rec))
                else:
                    gaps.append(f"{label} / operator recording")
                continue
            if not text.strip():
                continue
            vid = VOICE_MAP.get(speaker, FALLBACK_VOICE)
            settings = settings_for(speaker)
            for piece in chunk_text(text):
                p = hash_path(speaker, piece, vid, settings)
                if p.exists() and p.stat().st_size > 1000:
                    files.append(p)
                else:
                    gaps.append(f"{label} / {speaker}: {piece[:60]}")
    return files, gaps


def generate(sections, voice_map):
    all_segments = []
    for label, path, mode, extra in sections:
        print(f"\nParsing: {label}")
        if mode != "operator_slot" and not path.exists():
            print(f"  [SKIP] {path} not found")
            continue
        segs = parse_section(label, path, mode, extra)
        all_segments.extend(segs)
        print(f"  {len(segs)} segments")

    print(f"\nTotal segments: {len(all_segments)}")
    print("Generating audio...")

    segment_files: list[Path] = []
    for speaker, text in all_segments:
        if speaker == "__operator__":
            rec = Path(text)
            mp3 = ensure_mp3(rec)
            print(f"  [operator] {mp3}")
            segment_files.append(mp3)
            continue
        if not text.strip():
            continue
        vid = voice_map.get(speaker, FALLBACK_VOICE)
        if not vid:
            print(f"  [SKIP] no voice for {speaker}")
            continue
        segment_files.extend(tts(speaker, text, vid))

    return segment_files


def write_manifest(segment_files: list[Path], sections):
    manifest = {
        "sections": [s[0] for s in sections],
        "voices": {k: VOICE_LABEL.get(v, v) for k, v in VOICE_MAP.items()},
        "files": [p.name for p in segment_files],
        "operator_slot": bool(find_operator_recording()),
    }
    path = AUDIO_DIR / "manifest.json"
    path.write_text(json.dumps(manifest, indent=2) + "\n")
    print(f"Manifest: {path}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--reel", action="store_true", help="Generate a short voice-cast reel only")
    ap.add_argument("--only", help="Comma-separated section keys to generate (e.g. -05,-06,-07)")
    ap.add_argument("--output", help="Override output mp3 path (default: audio/dialog_reading.mp3)")
    ap.add_argument("--stitch-existing", action="store_true",
                    help="Concat whatever hash-cache segments exist; do not call TTS")
    args = ap.parse_args()

    print("Voice assignments (current defaults, no legacy remaps):")
    for speaker, vid in VOICE_MAP.items():
        print(f"  {speaker:<18} → {VOICE_LABEL.get(vid, vid)}")

    if args.reel:
        print("\nGenerating voice reel...")
        files = []
        for speaker, line in REEL_LINES:
            vid = VOICE_MAP[speaker]
            files.extend(tts(speaker, line, vid))
        if files:
            concatenate(files, AUDIO_DIR / "voice_reel.mp3")
        print("Done.")
        return

    if args.stitch_existing:
        sections = selected_sections(args.only)
        files, gaps = collect_existing(sections)
        print(f"Existing: {len(files)}  missing: {len(gaps)}")
        for g in gaps[:12]:
            print(f"  [gap] {g}")
        if len(gaps) > 12:
            print(f"  ... {len(gaps) - 12} more")
        if files:
            write_manifest(files, sections)
            concatenate(files, AUDIO_DIR / "dialog_reading.mp3")
        return

    import_legacy_cache()
    sections = selected_sections(args.only)
    files = generate(sections, VOICE_MAP)
    if not files:
        print("No segments generated.")
        return
    write_manifest(files, sections)
    out_path = Path(args.output) if args.output else AUDIO_DIR / "dialog_reading.mp3"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    print(f"\nConcatenating {len(files)} files...")
    concatenate(files, out_path)
    print(f"Output: {out_path}")
    rec = find_operator_recording()
    if not rec:
        print("\n00 slot is the Matilda stand-in. Drop audio/00_operator.wav to replace it.")
    print("Done.")


if __name__ == "__main__":
    main()
