#!/usr/bin/env python3
"""Render Scratch utterances from wood/hiss/glottal assets.

Claw = Kenney cardPlace / dieThrow, pitched by digit.
Glottal = chipsCollide, shortened.
Scrape = cardSlide + dieShuffle.
Hiss = baked pink/brown noise in assets/scratch/hiss/, then varied.

Every token gets a hash-seeded variation so the same word does not
click the same way twice.
"""
from __future__ import annotations

import hashlib
import re
import subprocess
import tempfile
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
KENNEY = BASE / "assets" / "scratch" / "kenney"
HISS = BASE / "assets" / "scratch" / "hiss"
CACHE = BASE / "audio" / "scratch"
CACHE.mkdir(parents=True, exist_ok=True)

PHONEME = {
    "g": "glottal",
    "glottal": "glottal",
    "click": "glottal",
    "c1": "claw1",
    "claw1": "claw1",
    "c2": "claw2",
    "claw2": "claw2",
    "c3": "claw3",
    "claw3": "claw3",
    "c4": "claw4",
    "claw4": "claw4",
    "c5": "claw5",
    "claw5": "claw5",
    "s": "sharp",
    "sharp": "sharp",
    "m": "mid",
    "mid": "mid",
    "b": "breath",
    "breath": "breath",
    "beat": "beat",
    "(beat)": "beat",
    "yes": "yes",
    "scrape": "yes",
    "no": "sharp",
}

CLAW_SRC = {
    1: ["cardPlace1.ogg", "cardPlace2.ogg"],
    2: ["cardPlace2.ogg", "cardPlace3.ogg"],
    3: ["cardPlace3.ogg", "dieThrow1.ogg"],
    4: ["dieThrow1.ogg", "dieThrow2.ogg"],
    5: ["dieThrow2.ogg", "cardPlace1.ogg"],
}
CLAW_PITCH = {1: 4, 2: 2, 3: 0, 4: -2, 5: -4}  # semitones; thumb is higher
GLOTTAL_SRC = ["chipsCollide1.ogg", "chipsCollide2.ogg", "chipsCollide3.ogg"]
SCRAPE_SRC = ["cardSlide1.ogg", "cardSlide2.ogg", "cardSlide3.ogg", "dieShuffle1.ogg"]


def _hash(s: str) -> str:
    return hashlib.sha1(s.encode()).hexdigest()[:12]


def _rng(seed: str) -> int:
    return int(_hash(seed), 16)


def _phones(token: str) -> list[str]:
    token = token.strip(".,;:").strip()
    if not token:
        return []
    parts = re.split(r"[·\-]", token) if ("·" in token or (token.count("-") and not token.startswith("claw"))) else [token]
    out = []
    for p in parts:
        key = p.strip().lower()
        if key in PHONEME:
            out.append(PHONEME[key])
    return out


def tokenize_utterance(text: str) -> list[list[str]]:
    """Return a list of words, each a list of phonemes.

    Verbose card lines (claw1 · glottal · breath) are one word per line.
    Compact vault lines (G·C4·M) are words separated by middot or space.
    """
    words: list[list[str]] = []
    compact: list[str] = []
    for raw in text.splitlines():
        line = raw.strip()
        if not line:
            continue
        if re.match(r"^(SCRATCH|slots|doctor|archivist|particles|claw 1)", line, re.I):
            continue
        if re.match(r"^\d+\s+claw", line, re.I):
            continue
        parts = re.split(r"\s{2,}|\t", line, maxsplit=1)
        if len(parts) == 2 and re.match(
            r"^(verb|noun|adj|the|no|yes|blood|search|time|clear)", parts[1], re.I
        ):
            line = parts[0].strip()
        if not line:
            continue
        compact_line = bool(re.fullmatch(r"[GCMBS0-9·.\s\-]+", line, re.I))
        if not compact_line:
            phones: list[str] = []
            for tok in re.split(r"\s*·\s*|\s+", line):
                phones.extend(_phones(tok))
            if phones:
                words.append(phones)
        else:
            compact.append(line)
    if compact:
        blob = " · ".join(compact)
        for chunk in re.split(r"\s+·\s+", blob):
            for tok in chunk.split():
                phones = _phones(tok)
                if phones:
                    words.append(phones)
    return words


def _vary(src: Path, dest: Path, seed: str, *, pitch: float = 0.0, tempo: float = 1.0, vol: float = 1.0) -> Path:
    h = _rng(seed)
    pitch += ((h % 17) - 8) * 0.18
    tempo *= 1.0 + ((h // 17) % 11 - 5) * 0.012
    vol *= 1.0 + ((h // 187) % 9 - 4) * 0.04
    tempo = max(0.85, min(1.18, tempo))
    af = (
        f"rubberband=pitch={pitch:.2f}:tempo={tempo:.3f},"
        f"volume={vol:.3f}"
    )
    dest.parent.mkdir(parents=True, exist_ok=True)
    wav = dest.with_suffix(".wav")
    r = subprocess.run(
        ["ffmpeg", "-y", "-i", str(src), "-af", af, "-ar", "44100", "-ac", "1",
         str(wav)],
        capture_output=True, text=True,
    )
    if r.returncode != 0 or not wav.exists():
        # rubberband + some sources fail; fall back to rate-shift
        ratio = 2 ** (pitch / 12.0)
        tempo = max(0.51, min(1.99, tempo / ratio))
        af2 = f"asetrate={44100 * ratio:.1f},aresample=44100,atempo={tempo:.3f},volume={vol:.3f}"
        r = subprocess.run(
            ["ffmpeg", "-y", "-i", str(src), "-af", af2, "-ar", "44100", "-ac", "1",
             str(wav)],
            capture_output=True, text=True,
        )
    if r.returncode != 0 or not wav.exists() or wav.stat().st_size < 200:
        raise RuntimeError(f"vary failed {src.name}: {r.stderr[-300:]}")
    subprocess.run(
        ["ffmpeg", "-y", "-i", str(wav), "-c:a", "libmp3lame", "-q:a", "4", str(dest)],
        capture_output=True, check=True,
    )
    wav.unlink(missing_ok=True)
    return dest


def _silence(dest: Path, ms: int) -> Path:
    subprocess.run(
        ["ffmpeg", "-y", "-f", "lavfi", "-i", f"anullsrc=r=44100:cl=mono",
         "-t", f"{ms/1000:.3f}", "-c:a", "libmp3lame", "-q:a", "4", str(dest)],
        capture_output=True, check=True,
    )
    return dest


def render_phone(phone: str, seed: str, harder: bool = False) -> Path:
    dest = CACHE / f"{phone}_{_hash(seed + ('H' if harder else ''))}.mp3"
    if dest.exists() and dest.stat().st_size > 200:
        return dest
    vol = 1.25 if harder else 1.0
    if phone == "beat":
        return _silence(dest, 180 if not harder else 120)
    if phone.startswith("claw"):
        n = int(phone[-1])
        srcs = CLAW_SRC[n]
        src = KENNEY / srcs[_rng(seed) % len(srcs)]
        return _vary(src, dest, seed, pitch=CLAW_PITCH[n], vol=vol * 1.15)
    if phone == "glottal":
        src = KENNEY / GLOTTAL_SRC[_rng(seed) % len(GLOTTAL_SRC)]
        return _vary(src, dest, seed, pitch=6.0, tempo=1.35, vol=vol * 0.95)
    if phone == "yes":
        src = KENNEY / SCRAPE_SRC[_rng(seed) % len(SCRAPE_SRC)]
        return _vary(src, dest, seed, pitch=-1.0, tempo=0.92, vol=vol)
    if phone in {"sharp", "mid", "breath"}:
        src = HISS / f"{phone}.wav"
        pitch = {"sharp": 2.0, "mid": 0.0, "breath": -1.5}[phone]
        return _vary(src, dest, seed, pitch=pitch, vol=vol * 1.1)
    return _silence(dest, 80)


def render_utterance(text: str, *, harder: bool = False, tag: str = "") -> Path:
    words = tokenize_utterance(text)
    if not words:
        raise ValueError(f"no scratch tokens in: {text[:80]!r}")
    key = _hash(text + ("|H" if harder else "") + tag)
    dest = CACHE / f"utt_{key}.mp3"
    if dest.exists() and dest.stat().st_size > 500:
        return dest
    parts: list[Path] = []
    with tempfile.TemporaryDirectory() as td:
        td = Path(td)
        gap_w = _silence(td / "gw.mp3", 70)
        gap_p = _silence(td / "gp.mp3", 28)
        for wi, phones in enumerate(words):
            for pi, phone in enumerate(phones):
                seed = f"{tag}|{text}|{wi}|{pi}|{phone}"
                parts.append(render_phone(phone, seed, harder=harder))
                if pi < len(phones) - 1:
                    parts.append(gap_p)
            if wi < len(words) - 1:
                parts.append(gap_w)
        lst = td / "list.txt"
        lst.write_text("".join(f"file '{p.resolve()}'\n" for p in parts))
        r = subprocess.run(
            ["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(lst),
             "-c:a", "libmp3lame", "-q:a", "3", str(dest)],
            capture_output=True, text=True,
        )
        if r.returncode != 0:
            raise RuntimeError(r.stderr[-400:])
    return dest


def spoken_card(text: str) -> list[str]:
    """Narrator reading the index card, not the iguana."""
    return [
        "Scratch. Built at the top of the cliff. Message carries it. Night. No clock.",
        "Claw one through five, tapped from the thumb. Hiss: sharp, mid, breath. And a glottal.",
        "Glottal first is a noun. Glottal second is a verb. Glottal third is an adjective. Glottal alone is the.",
        "Claw before hiss is positive. Hiss before claw is negative. Absence counts.",
        "All claws scraped is yes. A sharp hiss alone is no.",
        "Numbers: claws counted to five, scrape, count again. Scrape is plus. Sharp hiss is minus.",
        "Sixteen slots on the face of the card. The doctor's extension starts at blood, on the back. The archivist's extension is added later, in the vault.",
        "Particles have no glottal. Mid alone is but. Breath alone is and. A claw without a glottal is a number.",
    ]


if __name__ == "__main__":
    sample = """
claw1 · glottal · breath        verb 11     search
glottal · breath · claw1        noun 16     time / scope
claw5 · (beat) · glottal        adj 5       clear / empty
sharp                           no
"""
    print(tokenize_utterance(sample))
    p = render_utterance(sample, tag="demo")
    print(p, p.stat().st_size)
