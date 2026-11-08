#!/usr/bin/env python3
"""
tools/sync_minus08_audio.py
Rebuild audio/minus08 cues and concat list from -08_narration.md, in narration order.

A paragraph whose text one voice has already spoken reuses that segment (or the run
of consecutive segments that spell it). Only new or changed paragraphs go to ElevenLabs.
Every cue carries act, break, frame and the ~~STATE:k=v~~ in force, so the video
reads who is on screen from the script, not from clock times.

Run from REALITY_USER_MANUAL/:
    .venv/bin/python tools/sync_minus08_audio.py            # dry run: report only
    .venv/bin/python tools/sync_minus08_audio.py --write    # TTS + write cues/concat + mp3
"""
import argparse
import hashlib
import json
import math
import os
import re
import subprocess
import sys
import time
import wave
from pathlib import Path

BASE      = Path(__file__).resolve().parent.parent
SRC       = BASE / "src" / "phase2" / "-08_narration.md"
AUDIO_DIR = BASE / "audio" / "minus08"
SEG_DIR   = AUDIO_DIR / "segments"
CUES_F    = AUDIO_DIR / "cues.jsonl"
CONCAT_F  = AUDIO_DIR / "concat_segs.txt"
MP3_OUT   = AUDIO_DIR / "minus08.mp3"
DUR_CACHE = SEG_DIR / "durations.json"

sys.path.insert(0, str(Path(__file__).resolve().parent))
from extend_minus08_audio import VOICE_MAP, SPEAKER_SHORT, ELEVEN_KEY, MODEL_ID  # noqa: E402

# Narration label → (cue speaker, voice)
LABELS: dict[str, tuple[str, str]] = {
    "NARRATOR":   ("Narrator",  "Narrator"),
    "DRAAVIO":    ("Draavio",   "Draavio"),
    "MAGI":       ("Magi",      "Draavio"),
    "MERLIN":     ("Merlin",    "Draavio"),
    "FEYNMAN":    ("Feynman",   "Feynman"),
    "SHELDON":    ("Sheldon",   "Sheldon"),
    "PYRRHON":    ("Pyrrhon",   "Sheldon"),
    "LISBETH":    ("Lisbeth",   "Lisbeth"),
    "LISBETH_EN": ("LisbethEn", "LisbethEn"),
    "WITCH":      ("Witch",     "Witch"),
    "MERIT":      ("Merit",     "Merit"),
    "JOEY":       ("Joey",      "Joey"),
    "RAYMORA":    ("Raymora",   "Joey"),
    "VINCENT":    ("Vincent",   "Vincent"),
    "GOAT":       ("Goat",      "Goat"),
    "OPERATOR":   ("Operator",  "Operator"),
    "ARCHIVIST":  ("Archivist", "Archivist"),
    "SNAKE":      ("Snake",     "Snake"),
    "SAURON":     ("Sauron",    "Sauron"),
    "NARRATOR_EN":  ("Narrator", "Narrator"),
    "SCAPE":        ("Goat",     "Goat"),
    "DOCTOR_DRAKE": ("Raymora",  "Joey"),
}

VOICE_OF = {spk: voice for spk, voice in LABELS.values()}

# Old cues were keyed by the voice that spoke them. Voices that share an ElevenLabs id
# can reuse each other's audio for identical text.
VOICE_CLASS = {"LisbethEn": "Lisbeth", "Merit": "Witch", "Archivist": "Narrator"}

VOICE_SETTINGS = {
    "Narrator":  {"stability": 0.55, "similarity_boost": 0.80, "style": 0.25, "use_speaker_boost": True},
    "Draavio":   {"stability": 0.55, "similarity_boost": 0.80, "style": 0.25, "use_speaker_boost": True},
    "Feynman":   {"stability": 0.45, "similarity_boost": 0.75, "style": 0.35, "use_speaker_boost": True},
    "Sheldon":   {"stability": 0.50, "similarity_boost": 0.75, "style": 0.30, "use_speaker_boost": True},
    "Lisbeth":   {"stability": 0.68, "similarity_boost": 0.82, "style": 0.12, "use_speaker_boost": False},
    "LisbethEn": {"stability": 0.68, "similarity_boost": 0.82, "style": 0.12, "use_speaker_boost": False},
    "Witch":     {"stability": 0.52, "similarity_boost": 0.78, "style": 0.35, "use_speaker_boost": True},
    "Merit":     {"stability": 0.58, "similarity_boost": 0.78, "style": 0.20, "use_speaker_boost": True},
    "Joey":      {"stability": 0.40, "similarity_boost": 0.75, "style": 0.50, "use_speaker_boost": True},
    "Vincent":   {"stability": 0.72, "similarity_boost": 0.80, "style": 0.08, "use_speaker_boost": False},
    "Goat":      {"stability": 0.95, "similarity_boost": 0.50, "style": 0.00, "use_speaker_boost": False},
}

CHUNK = 450   # new paragraphs longer than this are split at sentence ends


def vclass(voice: str) -> str:
    return VOICE_CLASS.get(voice, voice)


# The text stays as written; minus08_say.json holds how the voice reads it.
SAY = [tuple(p) for p in json.loads((Path(__file__).resolve().parent / "minus08_say.json").read_text())]


def spoken(t: str) -> str:
    """What the voice says: stage directions and emphasis marks removed."""
    for written, said in SAY:
        t = t.replace(written, said)
    t = re.sub(r"\*\([^*]*?\)\*", " ", t)
    t = t.replace("*", "")
    return re.sub(r"\s+", " ", t).strip()


def key(t: str) -> str:
    return " ".join(re.findall(r"\w+|[?!]", t.lower()))


# ── Narration → paragraphs ────────────────────────────────────────────────────
def parse(path: Path = SRC) -> list[dict]:
    text = path.read_text()
    body = text[text.index("\n## ACT "):]
    act, brk, frame = 0, False, "pre_game_table"
    state: dict[str, str] = {}
    label = "NARRATOR"
    scratch = None
    paras: list[dict] = []
    buf: list[str] = []
    fence = False

    def flush() -> None:
        nonlocal scratch
        text = spoken(" ".join(buf))
        buf.clear()
        if not text:
            return
        spk, voice = LABELS.get(label, (label.title(), label.title()))
        p = {"act": act, "brk": brk, "frame": frame, "state": dict(state),
             "label": label, "speaker": spk, "voice": voice, "text": text}
        if scratch:
            p["scratch"] = scratch
            scratch = None
        paras.append(p)

    for line in body.splitlines():
        s = line.strip()
        if s.startswith("```") or s == '"""':
            flush()
            fence = not fence
            continue
        if fence:
            continue
        m = re.match(r"^## ACT (\d+|---)(?:\s|$)(.*)", s)
        if m:
            flush()
            if m.group(1) == "---":
                brk = True
            else:
                # An act titled THE BREAK is at the table until ~~STATE:break=off~~.
                act, brk = int(m.group(1)), "BREAK" in m.group(2).upper()
            continue
        if s.startswith("#"):
            continue
        m = re.fullmatch(r"~~(FRAME|STATE|SCRATCH):([^~]+)~~", s)
        if m:
            flush()
            kind, val = m.groups()
            if kind == "FRAME":
                frame = val.strip()
            elif kind == "STATE":
                k, _, v = val.partition("=")
                if k.strip() == "break":
                    brk = v.strip() == "on"
                else:
                    state[k.strip()] = v.strip()
            else:
                scratch = val.strip()
            continue
        m = re.match(r"^\*\*([A-Za-z_]+):\*\*\s*(.*)$", s)
        if m:
            flush()
            label = m.group(1).upper()
            if m.group(2):
                buf.append(m.group(2))
            continue
        if s == "---" or not s:
            flush()
            continue
        buf.append(s)
    flush()
    return paras


# ── Old cues → reusable segments ──────────────────────────────────────────────
def load_old() -> list[dict]:
    cues = [json.loads(l) for l in CUES_F.read_text().splitlines() if l.strip()]
    segs = [l.split("'")[1] for l in CONCAT_F.read_text().splitlines() if l.strip()]
    if len(cues) != len(segs):
        sys.exit(f"cues {len(cues)} != concat {len(segs)}")
    for c, sp in zip(cues, segs):
        c["seg"] = Path(sp).name
        c["k"] = key(c["text"])
        c["vc"] = vclass(VOICE_OF.get(c["speaker"], c["speaker"]))
    return cues


def match(p: dict, old: list[dict], hint: int) -> list[int] | None:
    """Old cues of the same voice whose texts, in order, spell the paragraph.

    The pieces need not be adjacent in the old list: earlier splices put other lines
    between the halves of one paragraph.
    """
    vc = vclass(p["voice"])

    def heads(rest: str, near: int) -> list[int]:
        out = [i for i, c in enumerate(old)
               if c["vc"] == vc and c["k"] and rest.startswith(c["k"])
               and (len(c["k"]) == len(rest) or rest[len(c["k"])] == " ")]
        return sorted(out, key=lambda i: (i < near, abs(i - near)))

    def walk(rest: str, near: int, depth: int) -> list[int] | None:
        if not rest:
            return []
        if depth > 40:
            return None
        for i in heads(rest, near):
            tail = walk(rest[len(old[i]["k"]):].lstrip(), i + 1, depth + 1)
            if tail is not None:
                return [i] + tail
        return None

    target = key(p["text"])
    return walk(target, hint, 0) if target else None


def chunks(text: str) -> list[str]:
    if len(text) <= CHUNK:
        return [text]
    sents = re.split(r"(?<=[.!?])\s+", text)
    out, cur = [], ""
    for s in sents:
        if cur and len(cur) + 1 + len(s) > CHUNK:
            out.append(cur)
            cur = s
        else:
            cur = f"{cur} {s}".strip()
    if cur:
        out.append(cur)
    return out


# ── Audio ─────────────────────────────────────────────────────────────────────
_durs: dict[str, float] = {}


def probe(path: Path) -> float:
    if path.name in _durs:
        return _durs[path.name]
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                        "-of", "default=noprint_wrappers=1:nokey=1", str(path)],
                       capture_output=True, text=True, check=True)
    _durs[path.name] = float(r.stdout.strip())
    return _durs[path.name]


def tts(voice: str, text: str, dest: Path) -> None:
    import urllib.request
    vid = VOICE_MAP.get(voice, "")
    if not vid or not ELEVEN_KEY:
        sys.exit(f"no voice id or key for {voice}")
    body = json.dumps({
        "text": text, "model_id": MODEL_ID,
        "voice_settings": VOICE_SETTINGS.get(voice, {"stability": 0.5, "similarity_boost": 0.75}),
    }).encode()
    req = urllib.request.Request(
        f"https://api.elevenlabs.io/v1/text-to-speech/{vid}", data=body,
        headers={"xi-api-key": ELEVEN_KEY, "Content-Type": "application/json",
                 "Accept": "audio/mpeg"})
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, timeout=120) as r:
                dest.write_bytes(r.read())
            return
        except Exception as e:
            if attempt == 2:
                raise
            print(f"    retry {attempt + 1}: {e}")
            time.sleep(4)


# Scratch, built on the cliff: claws 1–5 tapped from the thumb, three hisses, a glottal.
SR = 44100


def scratch_wav(notation: str, dest: Path) -> None:
    import numpy as np
    rng = np.random.default_rng(int(hashlib.md5(notation.encode()).hexdigest()[:8], 16))

    def noise(sec: float, lo: float, hi: float, amp: float, attack: float) -> "np.ndarray":
        n = int(sec * SR)
        spec = np.fft.rfft(rng.standard_normal(n))
        f = np.fft.rfftfreq(n, 1 / SR)
        spec[(f < lo) | (f > hi)] = 0
        x = np.fft.irfft(spec, n)
        x /= np.max(np.abs(x)) + 1e-9
        env = np.minimum(1, np.arange(n) / max(1, attack * SR)) * np.exp(-np.arange(n) / (n * 0.45))
        return amp * x * env

    def claw(k: int) -> "np.ndarray":
        n = int(0.045 * SR)
        t = np.arange(n) / SR
        f0 = 1500 + 450 * (k - 1)
        x = np.sin(2 * math.pi * f0 * t) * np.exp(-t / 0.006)
        x += 0.5 * rng.standard_normal(n) * np.exp(-t / 0.002)
        return 0.55 * x / np.max(np.abs(x))

    def glottal() -> "np.ndarray":
        n = int(0.07 * SR)
        t = np.arange(n) / SR
        x = np.sign(np.sin(2 * math.pi * 110 * t)) * np.exp(-t / 0.012)
        x = np.convolve(x, np.ones(24) / 24, mode="same")
        return 0.6 * x / np.max(np.abs(x))

    sound = {
        "S": lambda: noise(0.16, 4200, 11000, 0.45, 0.004),
        "M": lambda: noise(0.26, 1500, 4200, 0.40, 0.020),
        "B": lambda: noise(0.42, 250, 1500, 0.32, 0.080),
        "G": glottal,
        "_": lambda: np.zeros(int(0.16 * SR)),
    }
    gap_in, gap_word = np.zeros(int(0.07 * SR)), np.zeros(int(0.34 * SR))
    parts = [np.zeros(int(0.15 * SR))]
    for word in notation.split():
        for tok in word.split("·"):
            tok = tok.strip()
            parts.append(claw(int(tok[1])) if tok.startswith("C") else sound[tok]())
            parts.append(gap_in)
        parts.append(gap_word)
    parts.append(np.zeros(int(0.25 * SR)))
    pcm = (np.clip(np.concatenate(parts), -1, 1) * 32000).astype("<i2")
    tmp = dest.with_suffix(".wav")
    with wave.open(str(tmp), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(pcm.tobytes())
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", str(tmp), "-ar", "44100", "-ac", "1",
                    "-b:a", "128k", str(dest)], check=True)
    tmp.unlink()


# ── Main ──────────────────────────────────────────────────────────────────────
def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true")
    ap.add_argument("--revoice", action="append", default=[],
                    help="voice whose old audio is not reused (its voice id changed)")
    args = ap.parse_args()
    revoice = {vclass(v) for v in args.revoice}

    if DUR_CACHE.exists():
        _durs.update(json.loads(DUR_CACHE.read_text()))
    paras = parse()
    old = [c for c in load_old() if c["vc"] not in revoice]
    by_name = {p.name: p for p in SEG_DIR.glob("*.mp3")}
    next_idx = max(int(n.split("_")[0]) for n in by_name if n[:4].isdigit()) + 1

    plan: list[dict] = []          # one entry per output cue
    reused, new_chars, hint = 0, 0, 0
    for p in paras:
        base = {k: p[k] for k in ("act", "brk", "frame", "state", "speaker")}
        if p.get("scratch"):
            h = hashlib.md5(("scratch:" + p["scratch"]).encode()).hexdigest()[:16]
            plan.append({**base, "text": f"[Scratch] {p['scratch']}", "scratch": p["scratch"],
                         "seg": f"scratch_{h}.mp3", "gen": "scratch"})
        got = match(p, old, hint)
        if got:
            hint = got[-1] + 1
            reused += len(got)
            for i in got:
                plan.append({**base, "text": old[i]["text"], "seg": old[i]["seg"]})
            continue
        for chunk in chunks(p["text"]):
            short = SPEAKER_SHORT.get(p["voice"], p["voice"][:4])
            salt = VOICE_MAP.get(p["voice"], "") + ":" if vclass(p["voice"]) in revoice else ""
            h = hashlib.md5((salt + chunk).encode()).hexdigest()[:16]
            have = next((n for n in by_name if n.endswith(f"_{short}_{h}.mp3")), None)
            if have:
                plan.append({**base, "text": chunk, "seg": have})
                continue
            name = f"{next_idx:04d}_{short}_{h}.mp3"
            next_idx += 1
            new_chars += len(chunk)
            plan.append({**base, "text": chunk, "seg": name, "gen": "tts", "voice": p["voice"]})

    gen = [c for c in plan if c.get("gen")]
    used = {c["seg"] for c in plan}
    dropped = [c for c in old if c["seg"] not in used]
    print(f"paragraphs {len(paras)}  cues {len(plan)}  reused {reused}  "
          f"new {len(gen)} ({new_chars} chars)  old cues no longer used {len(dropped)}")
    for c in gen:
        print(f"  + [{c['act']}{' brk' if c['brk'] else ''}] {c['speaker']:<9} {c['text'][:96]}")
    for c in dropped:
        print(f"  - [{c['act']}] {c['speaker']:<9} {c['text'][:96]}")
    if not args.write:
        return

    for c in gen:
        dest = SEG_DIR / c["seg"]
        if dest.exists() and dest.stat().st_size > 1000:
            continue
        print(f"  [gen] {c['speaker']}: {c['text'][:70]}")
        if c["gen"] == "scratch":
            scratch_wav(c["scratch"], dest)
        else:
            tts(c["voice"], c["text"], dest)

    t = 0.0
    cues = []
    for c in plan:
        d = probe(SEG_DIR / c["seg"])
        cue = {"start": round(t, 6), "end": round(t + d, 6), "dur": round(d, 4),
               "speaker": c["speaker"], "act": c["act"], "brk": c["brk"],
               "frame": c["frame"], "state": c["state"], "text": c["text"], "seg": c["seg"]}
        if c.get("scratch"):
            cue["scratch"] = c["scratch"]
        cues.append(cue)
        t += d
    DUR_CACHE.write_text(json.dumps(_durs))
    CUES_F.write_text("".join(json.dumps(c, ensure_ascii=False) + "\n" for c in cues))
    CONCAT_F.write_text("".join(f"file '{SEG_DIR / c['seg']}'\n" for c in plan))
    print(f"cues.jsonl: {len(cues)} cues, {t / 60:.1f} min")
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0", "-i", str(CONCAT_F),
                    "-c:a", "libmp3lame", "-q:a", "2", str(MP3_OUT)], check=True)
    _durs.pop(MP3_OUT.name, None)
    print(f"{MP3_OUT.name}: {probe(MP3_OUT) / 60:.1f} min")


if __name__ == "__main__":
    main()
