#!/usr/bin/env python3
"""Page −25 — The Night of the Tesseract Turn.

Single source: src/phase2/-25.md (no separate narration file).

Voices:
  Matilda   — header / abstraction intro / scene heading / metacommentary
  Goat      — educational code walkthrough (VOICE_GOAT design winner)
  Goines    — scene oration (Jeffrey; Operator clone held until it works)

  .venv/bin/python tools/build_minus25_video.py audio
  .venv/bin/python tools/build_minus25_video.py stills --render
  .venv/bin/python tools/build_minus25_video.py frames
  .venv/bin/python tools/build_minus25_video.py assemble
  .venv/bin/python tools/build_minus25_video.py all --render
"""
from __future__ import annotations

import argparse
import base64
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
SRC = BASE / "src" / "phase2" / "-25.md"
AUDIO = BASE / "audio" / "minus25"
GOAT_TERMINAL_SPOKEN = AUDIO / "goat_terminal_spoken.txt"
OUT = BASE / "video" / "minus25"
STILLS = OUT / "stills"
CHARS = STILLS / "characters"
FRAMES = OUT / "frames"
SEG = AUDIO / "segments"

_env = BASE / ".env"
if _env.exists():
    for _l in _env.read_text().splitlines():
        _l = _l.strip()
        if _l and not _l.startswith("#") and "=" in _l:
            k, _, v = _l.partition("=")
            os.environ.setdefault(k.strip(), v.strip())

W, H, FPS = 1280, 720, 30
BONE = (230, 220, 200)
INK = (11, 11, 12)
CHALK = (216, 210, 192)
NIGHT = (8, 12, 18)

ELEVEN = "https://api.elevenlabs.io/v1"

VOICE_MAP = {
    "Matilda": os.environ.get("VOICE_MATILDA", "XrExE9yKIg1WjnnlVkGX"),
    # Voice Design winner (prompts); .env VOICE_GOAT overrides.
    "Goat": os.environ.get("VOICE_GOAT", "pWXtviCtpMHM8A80ox1D"),
    "Goines": os.environ.get("VOICE_GOINES", "AZeB2F9LIG4QDh5xm27p"),
}

VOICE_SETTINGS = {
    "Matilda": {
        "stability": 0.50,
        "similarity_boost": 0.75,
        "style": 0.20,
        "use_speaker_boost": True,
    },
    "Goat": {
        "stability": 0.92,
        "similarity_boost": 0.48,
        "style": 0.00,
        "use_speaker_boost": False,
    },
    "Goines": {
        "stability": 0.32,
        "similarity_boost": 0.80,
        "style": 0.30,
        "use_speaker_boost": True,
    },
}

HEADER = re.compile(r"^\*\*(MATILDA|GOAT|GOINES|OPERATOR):\*\*\s*$", re.M)

STYLE_DD = (
    "High-contrast ink illustration. Bold lampblack with deep shadow pools. "
    "Side-profile framing. Single torch-source lighting: warm rust from one side, "
    "cold deep shadow on the other. Rust #8C3A2A and bone #E6DCC8 palette. "
    "Gothic weight. Refined ink faces. Ink planes, no gradients. "
    "No anime eyes. No CGI gloss. No photography. No captions or text. "
)

# ── Parse ─────────────────────────────────────────────────────────────────────

def _strip_code_fences(t: str) -> str:
    """Drop fenced blocks from printable md; Goat uses goat_terminal_spoken.txt."""
    return re.sub(r"```.*?```", "\n", t, flags=re.S)


def _goat_narration(block: str) -> str:
    """Terminal transcript stays on the page; ElevenLabs gets phonetic walkthrough."""
    block = re.sub(r"```text\s*.*?```", "", block, flags=re.S).strip()
    if GOAT_TERMINAL_SPOKEN.exists():
        return GOAT_TERMINAL_SPOKEN.read_text(encoding="utf-8").strip()
    return _strip_code_fences(block).strip()


def _clean(t: str) -> str:
    t = _strip_code_fences(t)
    t = re.sub(r"^#{1,6}\s+", "", t, flags=re.M)
    t = re.sub(r"^\|.*\|$", "", t, flags=re.M)
    t = re.sub(r"^[-*+]\s+", "", t, flags=re.M)
    t = re.sub(r"\*\*([^*]+)\*\*", r"\1", t)
    t = re.sub(r"\*([^*]+)\*", r"\1", t)
    t = re.sub(r"`([^`]+)`", r"\1", t)
    t = t.replace("−", "minus ").replace("√2", "square root of two").replace("π", "pi")
    t = t.replace("α CMi", "alpha Canis Minoris").replace("α Dra", "alpha Draconis")
    t = t.replace("°", " degrees")
    t = re.sub(r"\bM44\b", "M forty-four", t)
    t = re.sub(r"\s*\[measured[^\]]*\]\s*", " ", t)
    t = re.sub(r"\s+:", ":", t)
    t = re.sub(r"\b([A-Za-z0-9]+)_([A-Za-z0-9_]+)\b",
               lambda m: m.group(0).replace("_", " "), t)
    t = re.sub(r"[ \t]+", " ", t)
    t = re.sub(r"\n{3,}", "\n\n", t)
    return t.strip()


def _is_heading(u: str) -> bool:
    u = u.strip()
    if len(u) > 72:
        return False
    if u.endswith((".", "!", "?")):
        return False
    # Section titles / addendum labels — not free prose.
    return bool(re.match(
        r"^(Metacommentary|The Three Frames|The Wooden Block|The Chair|The Tesseract|"
        r"Addendum\b|On equality:?|On the capital|The geometric reason|"
        r"The page number|The resolution is presence|This runs through|"
        r"Technical Correction\b|Filed for provenance)",
        u, re.I,
    )) or (u.endswith(":") and len(u) < 60)


def _split_chunks(text: str, limit: int = 900) -> list[str]:
    text = _clean(text)
    if not text:
        return []
    paras = [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]
    units: list[str] = []
    for para in paras or [text]:
        para = re.sub(r"\s+", " ", para).strip()
        # Keep short headings as their own unit (merged below).
        if _is_heading(para) or (len(para) < 80 and not re.search(r"[.!?]", para)):
            units.append(para)
            continue
        parts = re.split(r"(?<=[.!?])\s+", para)
        chunks, buf = [], ""
        for p in parts:
            if not p.strip():
                continue
            if len(buf) + len(p) + 1 > limit and buf:
                chunks.append(buf.strip())
                buf = p
            else:
                buf = (buf + " " + p).strip() if buf else p
        if buf:
            chunks.append(buf.strip())
        units.extend(chunks)
    # Fold bare headings (including consecutive titles) into the next prose.
    merged: list[str] = []
    i = 0
    while i < len(units):
        if _is_heading(units[i]):
            titles = []
            while i < len(units) and _is_heading(units[i]):
                titles.append(units[i].rstrip(":"))
                i += 1
            head = ". ".join(titles)
            if i < len(units):
                merged.append(f"{head}. {units[i]}".strip())
                i += 1
            else:
                merged.append(head)
            continue
        merged.append(units[i])
        i += 1
    return merged or [text]


def parse_script() -> list[dict]:
    raw = SRC.read_text(encoding="utf-8")
    # Drop the title line before the first speaker tag (spoken by Matilda block).
    matches = list(HEADER.finditer(raw))
    if not matches:
        sys.exit(f"No speaker headers in {SRC}")
    segs: list[dict] = []
    act = 0
    last = None
    name = {"MATILDA": "Matilda", "GOAT": "Goat", "GOINES": "Goines", "OPERATOR": "Goines"}
    for i, m in enumerate(matches):
        speaker = name[m.group(1)]
        start, end = m.end(), (matches[i + 1].start() if i + 1 < len(matches) else len(raw))
        block = raw[start:end]
        block = re.sub(r"^---+$", "", block, flags=re.M)
        if speaker == "Goat":
            block = _goat_narration(block)
        if last and last != speaker:
            act += 1
        if not block.strip():
            continue
        for chunk in _split_chunks(block):
            segs.append({"speaker": speaker, "text": chunk, "act": act})
        last = speaker
    return segs


# ── Audio ─────────────────────────────────────────────────────────────────────

def _seg_hash(speaker: str, text: str) -> str:
    settings = json.dumps(VOICE_SETTINGS[speaker], sort_keys=True)
    return hashlib.sha256(
        f"{speaker}|{text}|{VOICE_MAP[speaker]}|{settings}".encode()
    ).hexdigest()[:16]


def _gen_segment(speaker: str, text: str, dest: Path) -> float:
    if dest.exists() and dest.stat().st_size > 500:
        r = subprocess.run(
            ["ffprobe", "-v", "error", "-show_entries", "format=duration",
             "-of", "default=noprint_wrappers=1:nokey=1", str(dest)],
            capture_output=True, text=True,
        )
        try:
            return float(r.stdout.strip())
        except Exception:
            pass
    key = os.environ.get("ELEVENLABS_API_KEY", "").strip()
    if not key:
        sys.exit("Set ELEVENLABS_API_KEY")
    import requests
    vid = VOICE_MAP[speaker]
    payload = {
        "text": text,
        "model_id": "eleven_multilingual_v2",
        "voice_settings": VOICE_SETTINGS[speaker],
    }
    for attempt in range(3):
        r = requests.post(
            f"{ELEVEN}/text-to-speech/{vid}",
            headers={"xi-api-key": key, "Accept": "audio/mpeg"},
            json=payload,
            timeout=120,
        )
        if r.status_code == 200:
            dest.write_bytes(r.content)
            break
        if r.status_code == 429:
            time.sleep(2 ** (attempt + 2))
            continue
        sys.exit(f"TTS {speaker} {r.status_code}: {r.text[:300]}")
    else:
        sys.exit(f"TTS failed for {speaker}")
    time.sleep(0.2)
    r = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1", str(dest)],
        capture_output=True, text=True,
    )
    try:
        return float(r.stdout.strip())
    except Exception:
        return 3.0


def cmd_audio() -> None:
    AUDIO.mkdir(parents=True, exist_ok=True)
    SEG.mkdir(parents=True, exist_ok=True)
    # Reuse any prior segment with the same content hash (index may shift).
    by_hash: dict[str, Path] = {}
    for p in SEG.glob("*.mp3"):
        stem = p.stem
        h = stem.rsplit("_", 1)[-1]
        if len(h) == 16:
            by_hash.setdefault(h, p)
    segments = parse_script()
    print(f"Script → {len(segments)} segments")
    cues, files, t = [], [], 0.0
    for i, seg in enumerate(segments):
        h = _seg_hash(seg["speaker"], seg["text"])
        dest = SEG / f"{i:04d}_{seg['speaker'][:3]}_{h}.mp3"
        if h in by_hash and by_hash[h].exists() and not dest.exists():
            shutil.copy2(by_hash[h], dest)
        print(f"  [{i:3d}] {seg['speaker']:<10} {seg['text'][:56]!r}")
        dur = _gen_segment(seg["speaker"], seg["text"], dest)
        files.append(dest)
        by_hash[h] = dest
        cues.append({
            "start": round(t, 4),
            "end": round(t + dur, 4),
            "dur": round(dur, 4),
            "speaker": seg["speaker"],
            "act": seg["act"],
            "text": seg["text"],
        })
        t += dur
    lst = AUDIO / "concat_segs.txt"
    lst.write_text("".join(f"file '{f.resolve()}'\n" for f in files))
    mp3 = AUDIO / "minus25.mp3"
    subprocess.run(
        ["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(lst),
         "-c:a", "libmp3lame", "-b:a", "192k", str(mp3)],
        check=True,
    )
    (AUDIO / "cues.jsonl").write_text(
        "\n".join(json.dumps(c, ensure_ascii=False) for c in cues) + "\n"
    )
    print(f"Audio → {mp3} ({mp3.stat().st_size // 1024} KB)  {t:.1f}s")


# ── Stills ────────────────────────────────────────────────────────────────────

BG_PROMPTS = {
    "terminal_code": (
        "A dark terminal screen in a stone scriptorium at night. Green monospaced code "
        "glowing faintly. No readable letters — abstract glyph blocks only. Ink illustration.",
        "dd",
    ),
    "quebec_porch": (
        "Winter night on a wooden outpost porch in Quebec. A British colonial figure in velvet "
        "chews tobacco, looking over animal skins on stakes. Cold moonlight. Spit on the wood. "
        "False authority. Ink illustration, side view.",
        "dd",
    ),
    "magi_aperture": (
        "A Babylonian magi in chains tends a wooden stone aperture at night. Paint wells carved "
        "in stone. Glucose and scratch before him. Barcode-like marks on the ankle chain. "
        "Torch light. Precise instrument. Ink illustration.",
        "dd",
    ),
    "woman_tower": (
        "A short yellow-skinned woman with epicanthic folds and blue marks on her face stands "
        "in a southern stone tower at night. Crude scope on a stand. Beer cup. Warm breeze. "
        "Mars red and large in the sky. Final night of October. Ink illustration.",
        "dd",
    ),
    "wooden_block": (
        "Close view of a wooden right-angle block on a tower desk. Yog by yog. Hypotenuse "
        "inscribed thaim-or-eth burned with iron. Slight 7 degree off-true. Mars light. Ink.",
        "dd",
    ),
    "chair_mars": (
        "Woman of the triad seated in a simple chair in a tower, beer in hand, eyes on red Mars. "
        "Scope set aside. Natural aperture. Quiet giggle of recognition. Ink illustration.",
        "dd",
    ),
    "triad_relief": (
        "Egyptian Old Kingdom relief of a triad: left short red worker, center tall bearded "
        "administrator, right short yellow-skinned Nome with hawk association. Balanced. Ink.",
        "dd",
    ),
    "drought_sky": (
        "Wide arid landscape under a hard sky — 4.2 kiloyear drought. Empty monuments. "
        "No figures. The fall from outside. Ink illustration.",
        "dd",
    ),
    "precession": (
        "Night sky over Dancer constellation near the ecliptic. Mars as a red gem near a flower "
        "of stars. Precession implied by shifted seasonal frame. Ink illustration.",
        "dd",
    ),
}

CHAR_PROMPTS = {
    "matilda": (
        "Full body side profile, transparent background. A precise woman librarian-explorer. "
        "Facing right. Holding a filed note. Calm authority. Ink planes.",
        "dd",
    ),
    "goat_ttl": (
        "Full body side profile, transparent background. A goat with a red collar, facing right. "
        "Flat affect. Ledger animal. Ink planes. Not cute — documentary.",
        "dd",
    ),
    "operator_clone": (
        "Full body side profile, transparent background. A man in contemporary clothes holding "
        "a wooden right-angle block. Facing left. Quiet. Ink planes.",
        "dd",
    ),
    "slaver": (
        "Full body side profile, transparent background. British colonial slaver in warm velvet. "
        "Facing left. Tobacco. Contempt. Ink planes.",
        "dd",
    ),
    "magi": (
        "Full body side profile, transparent background. Babylonian magi in ankle chain. "
        "Facing left toward an unseen aperture. Precise. Ink planes.",
        "dd",
    ),
    "woman_nome": (
        "Full body side profile, transparent background. Short yellow-skinned woman, blue face marks, "
        "epicanthic folds, beer in hand. Facing left toward Mars. Focused attention. Ink planes.",
        "dd",
    ),
    "narrator_book": (
        "Full body side profile, transparent background. The Narrator — scholarly man with notebook. "
        "Facing right. Keeper of the record. Ink planes.",
        "dd",
    ),
}


def render_image(sid: str, prompt: str, style: str, dest: Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.exists() and dest.stat().st_size > 1000:
        print(f"  [skip] {sid}")
        return
    import requests
    key = os.environ.get("OPENAI_API_KEY", "").strip()
    if not key:
        sys.exit("Set OPENAI_API_KEY")
    transparent = sid in CHAR_PROMPTS
    size = "1024x1536" if transparent else "1536x1024"
    payload = {
        "model": "gpt-image-1.5",
        "prompt": (STYLE_DD if style == "dd" else "") + prompt,
        "size": size,
        "quality": "high",
        "output_format": "png",
        "n": 1,
        "background": "transparent" if transparent else "opaque",
    }
    r = requests.post(
        "https://api.openai.com/v1/images/generations",
        headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
        json=payload,
        timeout=180,
    )
    if r.status_code != 200:
        sys.exit(f"{sid} failed {r.status_code}: {r.text[:400]}")
    dest.write_bytes(base64.b64decode(r.json()["data"][0]["b64_json"]))
    print(f"  [ok] {sid} ({dest.stat().st_size // 1024}KB)")


def cmd_stills(render: bool = False) -> None:
    STILLS.mkdir(parents=True, exist_ok=True)
    CHARS.mkdir(parents=True, exist_ok=True)
    # reuse -27 plates where useful
    reuse = {
        "wooden_block": BASE / "video" / "minus27" / "stills" / "wooden_block.png",
        "chair_mars": BASE / "video" / "minus27" / "stills" / "sit_smile.png",
        "plato_chair": BASE / "video" / "minus27" / "stills" / "plato_chair.png",
        "mars_eighty": BASE / "video" / "minus27" / "stills" / "mars_eighty.png",
        "thaim_still": BASE / "video" / "minus27" / "stills" / "thaim_still.png",
    }
    for name, src in reuse.items():
        dest = STILLS / f"{name}.png"
        if src.exists() and not dest.exists():
            shutil.copy2(src, dest)
            print(f"  [reuse] {name}")
    goat_src = BASE / "video" / "minus08" / "stills" / "enemies" / "talking_goat_dd.png"
    if goat_src.exists():
        dest = CHARS / "goat_ttl.png"
        if not dest.exists():
            shutil.copy2(goat_src, dest)
            print("  [reuse] goat_ttl")
    goines_src = BASE / "video" / "stills" / "characters" / "goines.png"
    if goines_src.exists():
        dest = CHARS / "goines.png"
        if not dest.exists():
            shutil.copy2(goines_src, dest)
            print("  [reuse] goines")
    print("── Backgrounds ──")
    for sid, (prompt, style) in BG_PROMPTS.items():
        dest = STILLS / f"{sid}.png"
        if render:
            render_image(sid, prompt, style, dest)
        else:
            print(f"  [dry] {sid}")
    print("── Characters ──")
    for sid, (prompt, style) in CHAR_PROMPTS.items():
        dest = CHARS / f"{sid}.png"
        if sid == "goat_ttl" and dest.exists():
            print(f"  [skip] {sid}")
            continue
        if render:
            render_image(sid, prompt, style, dest)
        else:
            print(f"  [dry] {sid}")


# ── Visual state ──────────────────────────────────────────────────────────────

SPEAKER_CHAR = {
    "Matilda": "matilda",
    "Goat": "goat_ttl",
    "Goines": "goines",
}

TERMINAL_VISIBLE_LINES = 18

# Keyword → background (and optional right character override while Operator speaks scene)
KEYWORD_BG = [
    (re.compile(r"spits on the wood|Quebec|slaver|velvet", re.I), "quebec_porch", "slaver"),
    (re.compile(r"Babylonian magi|barcode|Castor|Pollux|Prowlscion", re.I), "magi_aperture", "magi"),
    (re.compile(r"yellow skinned|epicanthic|tower|final night of October", re.I), "woman_tower", "woman_nome"),
    (re.compile(r"wooden block|thaim-or-eth|hypotenuse|7\.25", re.I), "wooden_block", "woman_nome"),
    (re.compile(r"sat in the chair|giggle|Sudoku|turn of the tesseract", re.I), "chair_mars", "woman_nome"),
    (re.compile(r"triad|Chadic|Imhotep|Pathos|Logos|ethos|Nome", re.I), "triad_relief", None),
    (re.compile(r"drought|4\.2|kiloyear|collapse", re.I), "drought_sky", None),
    (re.compile(r"precession|January|October 31|Flower|Dancer", re.I), "precession", None),
    (re.compile(r"removingunseenfromrecord|plain_record|unseen_symbols", re.I), "terminal_code", None),
]


def load_terminal_transcript() -> list[str]:
    raw = SRC.read_text(encoding="utf-8")
    block = re.search(r"```text\s*\n(.*?)```", raw, flags=re.S)
    if not block:
        return []
    return [ln.rstrip() for ln in block.group(1).splitlines()]


def goat_terminal_scroll(cues: list[dict], cue_index: int, lines: list[str]) -> int:
    goat_idx = [i for i, c in enumerate(cues) if c["speaker"] == "Goat"]
    if cue_index not in goat_idx or not lines:
        return 0
    pos = goat_idx.index(cue_index)
    window = TERMINAL_VISIBLE_LINES
    max_scroll = max(0, len(lines) - window)
    if len(goat_idx) <= 1:
        return 0
    frac = pos / (len(goat_idx) - 1)
    return int(round(frac * max_scroll))


def load_cues() -> list[dict]:
    p = AUDIO / "cues.jsonl"
    if not p.exists():
        return []
    return [json.loads(l) for l in p.read_text().splitlines() if l.strip()]


def visual_for_cue(
    c: dict,
    *,
    cues: list[dict] | None = None,
    cue_index: int = 0,
    terminal_lines: list[str] | None = None,
) -> tuple[str, str | None, str | None, int]:
    """Return (bg, left_char, right_char, terminal_scroll)."""
    sp = c["speaker"]
    text = c.get("text") or ""
    scroll = 0
    if sp == "Goat" and cues is not None and terminal_lines:
        scroll = goat_terminal_scroll(cues, cue_index, terminal_lines)
        return "terminal_code", "goat_ttl", None, scroll

    bg, right = "triad_relief", None
    for rx, b, rch in KEYWORD_BG:
        if rx.search(text):
            bg = b
            right = rch
            break
    if sp == "Matilda":
        # Header / abstraction intro on the terminal plate; metacommentary follows keywords.
        if not any(
            k.search(text)
            for k in (
                re.compile(r"Metacommentary|simultaneous loci|Wooden Block|Tesseract|slaver|magi|epicanthic|chair has form", re.I),
            )
        ) and not any(rx.search(text) for rx, _, _ in KEYWORD_BG):
            return "terminal_code", "matilda", None, 0
        return bg, "matilda", None, 0
    if sp == "Goines":
        if bg in {"quebec_porch", "magi_aperture", "woman_tower", "chair_mars", "wooden_block"}:
            return bg, None, None, 0
        return bg, None, right or "woman_nome", 0
    return bg, "matilda", None, 0


# ── Frames / assemble ─────────────────────────────────────────────────────────

def _load_scaled(path: Path, size: tuple[int, int], alpha: bool):
    import pygame
    if not path.exists():
        return None
    img = pygame.image.load(str(path))
    img = img.convert_alpha() if alpha else img.convert()
    return pygame.transform.smoothscale(img, size)


def _blit_terminal(screen, font_mono, lines: list[str], scroll: int) -> None:
    import pygame

    panel = pygame.Surface((W - 300, H - 100), pygame.SRCALPHA)
    panel.fill((6, 10, 8, 235))
    screen.blit(panel, (280, 40))
    y = 52
    line_h = 20
    green = (120, 220, 140)
    dim = (90, 160, 110)
    window = lines[scroll : scroll + TERMINAL_VISIBLE_LINES]
    for i, ln in enumerate(window):
        color = green if ln.startswith("$") or ln.startswith(">") else dim
        if len(ln) > 92:
            ln = ln[:89] + "..."
        surf = font_mono.render(ln, True, color)
        screen.blit(surf, (300, y + i * line_h))


def draw_frame(
    screen,
    cue: dict,
    fonts,
    *,
    cues: list[dict] | None = None,
    cue_index: int = 0,
    terminal_lines: list[str] | None = None,
) -> None:
    import pygame
    bg_name, left, right, scroll = visual_for_cue(
        cue, cues=cues, cue_index=cue_index, terminal_lines=terminal_lines
    )
    font, font_mono = fonts
    bg = _load_scaled(STILLS / f"{bg_name}.png", (W, H), False)
    if bg is None and bg_name == "chair_mars":
        bg = _load_scaled(STILLS / "plato_chair.png", (W, H), False)
    if bg is None and bg_name == "triad_relief":
        bg = _load_scaled(STILLS / "woman_tower.png", (W, H), False)
    if bg:
        screen.blit(bg, (0, 0))
    else:
        screen.fill(NIGHT)
        screen.blit(font.render(f"[ {bg_name} ]", True, BONE), (W // 2 - 80, H // 2))

    if left:
        ch = _load_scaled(CHARS / f"{left}.png", (260, 480), True)
        if ch:
            screen.blit(ch, (60, H - 500))
    if right:
        ch = _load_scaled(CHARS / f"{right}.png", (260, 480), True)
        if ch:
            screen.blit(ch, (W - 340, H - 500))

    if cue["speaker"] == "Goat" and terminal_lines:
        _blit_terminal(screen, font_mono, terminal_lines, scroll)

    # Caption bar — dark strip so chalk stays readable on any still.
    bar = pygame.Surface((W, 64), pygame.SRCALPHA)
    bar.fill((8, 10, 14, 210))
    screen.blit(bar, (0, H - 64))
    cap = (cue.get("text") or "")[:95]
    if cue["speaker"] == "Goat":
        cap = cap[:72] + "…" if len(cap) > 72 else cap
    screen.blit(font.render(cue["speaker"], True, BONE), (40, H - 56))
    screen.blit(font_mono.render(cap, True, CHALK), (40, H - 30))


def cmd_frames() -> None:
    """Exclusive still holds (no overlap) + ffconcat for CFR 1fps assemble."""
    import pygame
    os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
    pygame.init()
    pygame.display.set_mode((1, 1))
    screen = pygame.Surface((W, H))
    font = pygame.font.SysFont("serif", 20)
    font_mono = pygame.font.SysFont("monospace", 14)
    cues = load_cues()
    if not cues:
        sys.exit("No cues — run audio first")
    terminal_lines = load_terminal_transcript()
    FRAMES.mkdir(parents=True, exist_ok=True)
    for old in FRAMES.glob("*.png"):
        old.unlink()

    seen: dict[tuple, str] = {}
    holds: list[tuple[str, float, float]] = []
    n = 0
    for i, c in enumerate(cues):
        key = visual_for_cue(
            c, cues=cues, cue_index=i, terminal_lines=terminal_lines
        ) + (c["speaker"],)
        if key not in seen:
            draw_frame(
                screen,
                c,
                (font, font_mono),
                cues=cues,
                cue_index=i,
                terminal_lines=terminal_lines,
            )
            name = f"f{n:04d}.png"
            pygame.image.save(screen, FRAMES / name)
            seen[key] = name
            n += 1
            if n % 10 == 0:
                print(f"  unique {n}")
        rel = f"frames/{seen[key]}"
        start, end = float(c["start"]), float(c["end"])
        if holds and holds[-1][0] == rel:
            holds[-1] = (rel, holds[-1][1], end)
        else:
            holds.append((rel, start, end))

    timeline: list[tuple[str, float]] = []
    t = 0.0
    for rel, start, end in holds:
        dur = max(0.04, end - start)
        timeline.append((rel, dur))
        t += dur

    mp3 = AUDIO / "minus25.mp3"
    audio_dur = float(
        subprocess.run(
            ["ffprobe", "-v", "error", "-show_entries", "format=duration",
             "-of", "default=noprint_wrappers=1:nokey=1", str(mp3)],
            capture_output=True, text=True,
        ).stdout.strip()
        or "0"
    )
    if audio_dur > 0 and timeline:
        drift = audio_dur - t
        name, dur = timeline[-1]
        timeline[-1] = (name, max(0.04, dur + drift))

    (OUT / "holds.json").write_text(
        json.dumps([{"file": rel, "duration": round(dur, 4)} for rel, dur in timeline], indent=1)
        + "\n"
    )
    concat = ["ffconcat version 1.0"]
    last = ""
    for rel, dur in timeline:
        concat.append(f"file '{rel}'")
        concat.append(f"duration {dur:.4f}")
        last = rel
    concat.append(f"file '{last}'")
    (OUT / "concat.txt").write_text("\n".join(concat) + "\n")
    # Keep legacy path for any old tooling that still looks for it.
    (OUT / "frames_concat.txt").write_text("\n".join(concat) + "\n")
    print(
        f"Frames → {FRAMES} ({n} unique, {len(timeline)} holds, "
        f"{sum(d for _, d in timeline):.1f}s vs audio {audio_dur:.1f}s)"
    )


def cmd_assemble() -> None:
    """ffmpeg concat over exclusive holds + audio. CFR 1 fps (same as −16)."""
    mp3 = AUDIO / "minus25.mp3"
    if not mp3.exists():
        sys.exit("missing audio")
    concat = OUT / "concat.txt"
    if not concat.exists():
        sys.exit("missing frames — run frames")
    OUT.mkdir(parents=True, exist_ok=True)
    final = OUT / "-25_the_tesseract_turn.mp4"
    subprocess.run(
        [
            "ffmpeg", "-y",
            "-f", "concat", "-safe", "0", "-i", "concat.txt",
            "-i", str(mp3),
            "-vf", "fps=1,format=yuv420p",
            "-c:v", "libx264", "-tune", "stillimage", "-crf", "20",
            "-g", "30", "-bf", "0",
            "-c:a", "aac", "-b:a", "192k",
            "-shortest", "-movflags", "+faststart",
            str(final),
        ],
        check=True,
        cwd=str(OUT),
    )
    print(f"Video → {final} ({final.stat().st_size // 1024} KB)")


def main() -> None:
    AUDIO.mkdir(parents=True, exist_ok=True)
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["audio", "stills", "frames", "assemble", "all", "parse"])
    ap.add_argument("--render", action="store_true")
    args = ap.parse_args()
    if args.cmd == "parse":
        segs = parse_script()
        print(len(segs), "segments")
        for s in segs[:8]:
            print(s["speaker"], s["text"][:70])
        return
    if args.cmd == "audio":
        cmd_audio()
    elif args.cmd == "stills":
        cmd_stills(render=args.render)
    elif args.cmd == "frames":
        cmd_frames()
    elif args.cmd == "assemble":
        cmd_assemble()
    elif args.cmd == "all":
        cmd_audio()
        cmd_stills(render=args.render)
        cmd_frames()
        cmd_assemble()


if __name__ == "__main__":
    main()
