#!/usr/bin/env python3
"""Page −35 — The Ridiculous Journey (Shakespeare / Chaucer).

Darkest Dungeon visual language. A codebase as a labyrinth. A road at morning.

Rules:
  - Shakespeare is always on the left. He does not move. (Auden pattern.)
  - Chaucer is mainly on the right but changes position and posture
    across the acts — he is the naked herald and the performance is his.
  - Backgrounds change with each act: scriptorium → directory labyrinth →
    narrow pane → open air → theta gates → bare earth → road at morning.

  .venv/bin/python tools/build_minus35_video.py audio           # gen ElevenLabs MP3
  .venv/bin/python tools/build_minus35_video.py stills          # dry-run image list
  .venv/bin/python tools/build_minus35_video.py stills --render # call image API
  .venv/bin/python tools/build_minus35_video.py pygame          # preview
  .venv/bin/python tools/build_minus35_video.py frames          # export unique frames
  .venv/bin/python tools/build_minus35_video.py assemble        # ffmpeg → mp4
  .venv/bin/python tools/build_minus35_video.py all --render    # full pipeline
"""
from __future__ import annotations

import argparse
import base64
import hashlib
import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path

BASE   = Path(__file__).resolve().parent.parent
AUDIO  = BASE / "audio"  / "minus35"
OUT    = BASE / "video"  / "minus35"
STILLS = OUT  / "stills"
FRAMES = OUT  / "frames"
CHARS  = BASE / "video"  / "stills" / "characters"
SRC    = BASE / "src"    / "-35.md"

_env = BASE / ".env"
if _env.exists():
    for _l in _env.read_text().splitlines():
        _l = _l.strip()
        if _l and not _l.startswith("#") and "=" in _l:
            k, _, v = _l.partition("=")
            os.environ.setdefault(k.strip(), v.strip())

W, H = 1280, 720
FPS  = 30

# ── Palette ───────────────────────────────────────────────────────────────────
BONE      = (230, 220, 200)
INK       = (11,  11,  12)
CHALK     = (216, 210, 192)
NIGHT     = (8,   16,  32)
PARCHMENT = (210, 190, 155)
PURPLE    = (60,  20,  80)
RUST      = (140, 58,  42)

# ── Voice IDs ─────────────────────────────────────────────────────────────────
# After creating voices on ElevenLabs (Voice Design → voice ID in the URL),
# paste the IDs here and re-run `audio` to generate.
VOICE_SHAKESPEARE = os.environ.get("VOICE_SHAKESPEARE", "PENDING")
VOICE_CHAUCER     = os.environ.get("VOICE_CHAUCER",     "PENDING")

VOICE_SETTINGS: dict[str, dict] = {
    "Shakespeare": {
        "stability": 0.62, "similarity_boost": 0.80,
        "style": 0.15, "use_speaker_boost": True,
    },
    "Chaucer": {
        "stability": 0.38, "similarity_boost": 0.72,
        "style": 0.48, "use_speaker_boost": True,
    },
}

# ── Script parsing ────────────────────────────────────────────────────────────
# Segments: list of {"speaker": str, "text": str, "act": int}
# Acts map to backgrounds; text is cleaned for TTS.

_STRIP_MD = re.compile(r"\*+([^*]+)\*+|`([^`]+)`|_{1,2}([^_]+)_{1,2}")
_TRIPLE_QUOTE = re.compile(r'""".*?"""', re.DOTALL)
_HASH_COMMENT = re.compile(r"^#[^#].*$", re.MULTILINE)

def _clean_for_tts(text: str) -> str:
    """Remove markdown, triple-quotes, hash-comments; keep Greek as-is."""
    text = _TRIPLE_QUOTE.sub("", text)
    text = _HASH_COMMENT.sub("", text)
    text = _STRIP_MD.sub(lambda m: m.group(1) or m.group(2) or m.group(3), text)
    # Remove separator lines
    text = re.sub(r"^---+$", "", text, flags=re.MULTILINE)
    # Normalise whitespace
    text = re.sub(r"\n{3,}", "\n\n", text).strip()
    return text

def _split_sentences(text: str) -> list[str]:
    """Split text into TTS-sized chunks (~120 chars, sentence-aware)."""
    # Split on sentence endings; keep delimiter
    parts = re.split(r"(?<=[.!?])\s+", text)
    chunks: list[str] = []
    buf = ""
    for p in parts:
        if not p.strip():
            continue
        if len(buf) + len(p) + 1 > 160 and buf:
            chunks.append(buf.strip())
            buf = p
        else:
            buf = (buf + " " + p).strip() if buf else p
    if buf:
        chunks.append(buf.strip())
    return [c for c in chunks if c]

def parse_script() -> list[dict]:
    """Parse src/-35.md into segments with speaker + act labels."""
    raw = SRC.read_text()

    # Find all speaker header positions  (**SHAKESPEARE:** or **CHAUCER:**)
    header = re.compile(r"^\*\*(SHAKESPEARE|CHAUCER):\*\*\s*$", re.MULTILINE)
    matches = list(header.finditer(raw))
    if not matches:
        return []

    act = 0
    last_speaker: str | None = None
    segments: list[dict] = []

    for i, m in enumerate(matches):
        speaker = m.group(1).capitalize()   # "Shakespeare" or "Chaucer"
        start   = m.end()
        end     = matches[i + 1].start() if i + 1 < len(matches) else len(raw)
        block   = _clean_for_tts(raw[start:end])

        if last_speaker == "Chaucer" and speaker == "Shakespeare":
            act += 1

        for chunk in _split_sentences(block):
            if chunk:
                segments.append({"speaker": speaker, "text": chunk, "act": act})

        last_speaker = speaker

    return segments

# ── Audio generation ──────────────────────────────────────────────────────────
ELEVEN_BASE = "https://api.elevenlabs.io/v1"

def _eleven_headers() -> dict:
    key = os.environ.get("ELEVENLABS_API_KEY", "").strip()
    if not key:
        sys.exit("Set ELEVENLABS_API_KEY in .env or environment")
    return {"xi-api-key": key, "Content-Type": "application/json"}

def _voice_id(speaker: str) -> str:
    vid = VOICE_SHAKESPEARE if speaker == "Shakespeare" else VOICE_CHAUCER
    if vid == "PENDING":
        sys.exit(
            f"Voice ID for {speaker} is PENDING.\n"
            f"Paste the ElevenLabs voice ID into build_minus35_video.py "
            f"VOICE_{speaker.upper()} or set VOICE_{speaker.upper()} in .env"
        )
    return vid

def _seg_hash(speaker: str, text: str) -> str:
    return hashlib.sha256(f"{speaker}|{text}".encode()).hexdigest()[:16]

def _gen_segment(speaker: str, text: str, dest: Path) -> float:
    """Call ElevenLabs TTS; return duration in seconds."""
    import requests
    if dest.exists() and dest.stat().st_size > 500:
        # probe duration without regenerating
        r = subprocess.run(
            ["ffprobe", "-v", "error", "-show_entries", "format=duration",
             "-of", "default=noprint_wrappers=1:nokey=1", str(dest)],
            capture_output=True, text=True,
        )
        try:
            return float(r.stdout.strip())
        except Exception:
            pass

    vid  = _voice_id(speaker)
    cfg  = VOICE_SETTINGS[speaker]
    payload = {
        "text": text,
        "model_id": "eleven_multilingual_v2",
        "voice_settings": cfg,
    }
    headers = _eleven_headers()
    headers["Accept"] = "audio/mpeg"
    headers.pop("Content-Type")

    for attempt in range(3):
        try:
            r = requests.post(
                f"{ELEVEN_BASE}/text-to-speech/{vid}",
                headers=headers,
                json=payload,
                timeout=60,
            )
            if r.status_code == 200:
                dest.write_bytes(r.content)
                break
            elif r.status_code == 429:
                wait = 2 ** (attempt + 2)
                print(f"    rate-limited — waiting {wait}s")
                time.sleep(wait)
            else:
                sys.exit(f"ElevenLabs error {r.status_code}: {r.text[:300]}")
        except Exception as exc:
            if attempt == 2:
                raise
            time.sleep(3)

    # probe duration
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
    """Generate per-segment MP3s, concatenate, write cues.jsonl."""
    import requests  # noqa: F401 — checked before loop
    AUDIO.mkdir(parents=True, exist_ok=True)
    seg_dir = AUDIO / "segments"
    seg_dir.mkdir(exist_ok=True)

    segments = parse_script()
    print(f"Script → {len(segments)} segments")

    cues:  list[dict] = []
    files: list[Path] = []
    t = 0.0

    for i, seg in enumerate(segments):
        h    = _seg_hash(seg["speaker"], seg["text"])
        dest = seg_dir / f"{i:04d}_{seg['speaker'][:3]}_{h}.mp3"
        print(f"  [{i:3d}] {seg['speaker'][:5]} act={seg['act']}  {seg['text'][:60]!r}")
        dur  = _gen_segment(seg["speaker"], seg["text"], dest)
        files.append(dest)
        cues.append({
            "start":   round(t,   4),
            "end":     round(t + dur, 4),
            "dur":     round(dur, 4),
            "speaker": seg["speaker"],
            "act":     seg["act"],
            "text":    seg["text"],
        })
        t += dur

    # Concatenate
    list_file = AUDIO / "concat_segs.txt"
    list_file.write_text("".join(f"file '{f.resolve()}'\n" for f in files))
    mp3_out = AUDIO / "minus35.mp3"
    subprocess.run(
        ["ffmpeg", "-y", "-f", "concat", "-safe", "0",
         "-i", str(list_file), "-c:a", "libmp3lame", "-b:a", "192k", str(mp3_out)],
        check=True,
    )

    (AUDIO / "cues.jsonl").write_text(
        "\n".join(json.dumps(c, ensure_ascii=False) for c in cues) + "\n"
    )
    print(f"\nAudio  → {mp3_out}  ({mp3_out.stat().st_size // 1024}KB)")
    print(f"Cues   → {AUDIO / 'cues.jsonl'}  ({len(cues)} entries)")

# ── Cue helpers ───────────────────────────────────────────────────────────────
def load_cues() -> list[dict]:
    p = AUDIO / "cues.jsonl"
    if not p.exists():
        return []
    return [json.loads(l) for l in p.read_text().splitlines() if l.strip()]

AUDIO_OFFSET = 0.3

_cue_scale_cache: float | None = None

def get_cue_scale(cues: list[dict]) -> float:
    global _cue_scale_cache
    if _cue_scale_cache is not None:
        return _cue_scale_cache
    if not cues:
        return 1.0
    cue_dur = cues[-1]["end"]
    r = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1",
         str(AUDIO / "minus35.mp3")],
        capture_output=True, text=True,
    )
    try:
        mp3_dur = float(r.stdout.strip())
    except Exception:
        mp3_dur = cue_dur
    _cue_scale_cache = cue_dur / mp3_dur if mp3_dur > 0 else 1.0
    return _cue_scale_cache

def audio_to_cue(t: float, cues: list[dict]) -> float:
    return max(0.0, t * get_cue_scale(cues) - AUDIO_OFFSET)

def cue_at(cues: list[dict], cue_t: float) -> dict | None:
    for c in cues:
        if c["start"] <= cue_t < c["end"]:
            return c
    return cues[-1] if cues and cue_t >= cues[-1]["end"] else (cues[0] if cues else None)

# ── Act → visual state ────────────────────────────────────────────────────────
# Background phases keyed by act number (0-based).
# Act boundaries are cue-time driven (resolved from cues.jsonl at runtime).

ACT_BACKGROUNDS = {
    0: "scriptorium_screen",  # Shakespeare opens — luminous pane, labyrinth beyond
    1: "directory_deep",      # Chaucer descends — purple corridors, deepening
    2: "narrow_pane",         # Shakespeare narrates the click — narrow window lit
    3: "verse_narrow",        # Chaucer reads the verse — suffixes in the light
    4: "open_air_road",       # Shakespeare: what remains when form exceeds frame
    5: "kata_gate",           # Chaucer: κατά VOLARE — the gates, theta open
    6: "kata_aftermath",      # Shakespeare: the institution spelled its way out
    7: "bare_earth",          # Chaucer: Matthew 25:18 — earth, no article
    8: "road_morning",        # Shakespeare closes — coat on road, morning, empty
}

# Chaucer position per act — he moves; Shakespeare never does
CHAUCER_POSITIONS = {
    0: "chaucer_observing",    # standing right, watching Shakespeare open
    1: "chaucer_descending",   # leaning forward into the labyrinth
    2: "chaucer_descending",   # still in the descent
    3: "chaucer_verse",        # holding the narrow list, reading as verse
    4: "chaucer_road_forward", # moving forward, road behind
    5: "chaucer_herald",       # arms wide, announcing
    6: "chaucer_herald",       # still heralding
    7: "chaucer_matthew",      # hands open and down — the delivery
    8: "chaucer_road_close",   # close, final, on the road alone
}

def act_from_cue(cues: list[dict], cue_t: float) -> int:
    """Return the act number at cue_t, from cues.jsonl 'act' field."""
    c = cue_at(cues, cue_t)
    return c["act"] if c and "act" in c else 0

# ── Style ─────────────────────────────────────────────────────────────────────
STYLE_DD = (
    "High-contrast ink illustration. Bold lampblack with deep shadow pools. "
    "Side-profile framing. Single torch-source lighting. "
    "Rust #8C3A2A and bone #E6DCC8 palette. Gothic weight. "
    "Refined ink faces, readable features. Ink planes, no gradients. "
    "No anime eyes. No CGI gloss. No photography. No captions or text. "
)

# ── Background prompts ────────────────────────────────────────────────────────
BG_PROMPTS: dict[str, tuple[str, str]] = {
    "scriptorium_screen": (
        "A medieval scriptorium at night. Stone arch ceiling, single candle left of frame. "
        "At the far center: a single luminous rectangular pane — a screen glowing cold white "
        "in the dark room, casting light on stone floor. Beyond the screen: a corridor of arches "
        "receding into black. A man's silhouette at the threshold between candle and screen. "
        "The labyrinth begins at the screen.",
        "dd"
    ),
    "directory_deep": (
        "An infinite corridor of stone arches descending into purple darkness. "
        "Each arch is slightly smaller than the last. "
        "The walls are covered in carved text — words missing their left halves, "
        "suffixes only visible in the torchlight. "
        "The floor is cold stone. Torches dim as depth increases. "
        "The deepest arch is pure purple-black. No exit visible.",
        "dd"
    ),
    "narrow_pane": (
        "A narrow stone window in a thick wall. The window is just wide enough for one page. "
        "Through the window: moonlight. On the sill: a scroll with text visible — "
        "but only the right half of each line shows; the left half is cut off by the wall. "
        "The visible fragments are endings, not beginnings. Moonlight on parchment. "
        "The wall is the censor. The sill is the archive.",
        "dd"
    ),
    "verse_narrow": (
        "The same narrow stone window, now seen from directly in front. "
        "The scroll fills the sill. In the moonlight, the right-side fragments glow: "
        "ιμι, τιον, μηνία, φας, ίστημι — short Greek endings arranged as verse lines. "
        "Below the window, words fall into shadow. The visible column is lit. "
        "The rest is the wall.",
        "dd"
    ),
    "open_air_road": (
        "A medieval road at dusk, seen from ground level. "
        "Stone path running straight ahead into open countryside. "
        "The corridor of the labyrinth is behind the viewer — stone arch visible at edge of frame. "
        "The road ahead is open. Low clouds. Last light. "
        "A scatter of parchment fragments on the road, partially lit.",
        "dd"
    ),
    "kata_gate": (
        "Two massive stone gates standing open. The gates are theta-shaped: "
        "each is a tall arch with a horizontal bar across its middle. "
        "The gate stands in open countryside. Beyond: a road leading to a distant city. "
        "The gates were once closed. They are open now. "
        "The stone threshold is worn from passage. Dawn light behind the gates.",
        "dd"
    ),
    "kata_aftermath": (
        "The road beyond the theta-gates. The gates are now behind the viewer, visible at edge of frame. "
        "The road ahead leads to an ancient city — low walls, towers at distance. "
        "Morning light. A cat sits on the road, not moving. "
        "The cat is not metaphorical. It is simply there.",
        "dd"
    ),
    "bare_earth": (
        "A patch of bare earth. No grass. No article. Just earth. "
        "Close view: the soil is dark and recently turned. A rectangular depression — "
        "something was placed here and covered. "
        "No tools visible. No person. The act is complete. "
        "Morning light, cold, coming from left. "
        "The earth expands in every direction.",
        "dd"
    ),
    "road_morning": (
        "A medieval road at early morning. Empty. Looking down the road ahead. "
        "On the road, at the center: a coat lying on the stone. "
        "The coat is good quality — it was worn recently. No person beside it. "
        "The figure who wore it is ahead somewhere, not visible. "
        "Morning mist at ankle height. Cold light from the right.",
        "dd"
    ),
}

# ── Character prompts ─────────────────────────────────────────────────────────
CHAR_PROMPTS: dict[str, tuple[str, str]] = {
    # Shakespeare: always left, static, quill/notebook
    "shakespeare_quill": (
        "Full body side profile, transparent background. A playwright-narrator. Facing right. "
        "Elizabethan dress — doublet, ruff collar, dark wool. A quill pen in hand, notebook open. "
        "Standing upright, weight even. The posture of a man who has seen everything "
        "and is recording it correctly. His expression is precise and not unkind. "
        "He does not perform. He annotates.",
        "dd"
    ),
    # Chaucer positions — all face left (toward Shakespeare / the audience)
    "chaucer_observing": (
        "Full body side profile, transparent background. A medieval herald — Geoffrey Chaucer. Facing left. "
        "Simple tunic, travel-worn. Arms at sides, watching. The voice is ready but not yet deployed. "
        "The clothes are intact here: he has not yet gambled them away.",
        "dd"
    ),
    "chaucer_descending": (
        "Full body side profile, transparent background. A medieval herald. Facing left, leaning forward. "
        "Tunic slightly disheveled. One hand extended ahead — feeling the depth of the corridor. "
        "The posture of a man descending into something fascinating and dangerous. "
        "He is not afraid. He is intrigued.",
        "dd"
    ),
    "chaucer_verse": (
        "Full body side profile, transparent background. A medieval herald. Facing left. "
        "Holding a narrow parchment scroll — but only reading the right half, which is lit. "
        "His lips are moving. He is reading aloud what the narrow light reveals. "
        "One finger traces the suffix column. The clothes are now somewhat reduced — "
        "a coat missing, tunic remaining.",
        "dd"
    ),
    "chaucer_road_forward": (
        "Full body side profile, transparent background. A medieval herald on a road. "
        "Facing left, striding. No coat. Simple tunic only. Arms swinging. "
        "The stride is confident. He has no clothes and a clear destination. "
        "The face: focused, not troubled.",
        "dd"
    ),
    "chaucer_herald": (
        "Full body side profile, transparent background. A medieval herald — announcing. "
        "Facing left. Arms wide open — the announcement position. "
        "No coat. Tunic only. Head back, voice projected. "
        "This is the man who makes things real by saying them out loud. "
        "He is saying something real. You can see it working.",
        "dd"
    ),
    "chaucer_matthew": (
        "Full body side profile, transparent background. A medieval herald in delivery. "
        "Facing left. Hands open, pointing downward — toward the earth. "
        "The gesture says: here. In this. The earth itself. "
        "No coat. Tunic only. The delivery is not theatrical — it is true. "
        "He has done this before. He is doing it again. It is the same thing.",
        "dd"
    ),
    "chaucer_road_close": (
        "Full body side profile, transparent background. A medieval herald on a road, close view. "
        "Facing left. No coat. Tunic only. Standing still now. "
        "The performance is over or just beginning — these are the same. "
        "He is on the road. He has no clothes. He has a voice. "
        "That is enough. You can see it is enough.",
        "dd"
    ),
}

# ── Image API render ──────────────────────────────────────────────────────────
def render_image(sid: str, prompt: str, style: str, dest: Path) -> Path:
    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.exists() and dest.stat().st_size > 1000:
        print(f"  [skip] {sid}")
        return dest
    import requests
    key = os.environ.get("OPENAI_API_KEY", "").strip()
    if not key:
        sys.exit("Set OPENAI_API_KEY in .env or environment")
    transparent = sid in CHAR_PROMPTS
    size = "1024x1536" if transparent else "1536x1024"
    full_prompt = (STYLE_DD if style == "dd" else "") + prompt
    payload = {
        "model": "gpt-image-1.5",
        "prompt": full_prompt,
        "size": size,
        "quality": "high",
        "output_format": "png",
        "n": 1,
        "background": "transparent" if transparent else "opaque",
    }
    import requests as req
    r = req.post(
        "https://api.openai.com/v1/images/generations",
        headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
        json=payload,
        timeout=180,
    )
    if r.status_code != 200:
        sys.exit(f"{sid} failed {r.status_code}: {r.text[:400]}")
    dest.write_bytes(base64.b64decode(r.json()["data"][0]["b64_json"]))
    print(f"  [ok] {sid}  {dest.stat().st_size // 1024}KB")
    return dest

def cmd_stills(render: bool = False) -> None:
    print("── Backgrounds ──────────────────────────────────────────────────")
    for sid, (prompt, style) in BG_PROMPTS.items():
        dest = STILLS / f"{sid}.png"
        if render:
            render_image(sid, prompt, style, dest)
        else:
            print(f"  [dry] {sid}")
    print("── Characters ───────────────────────────────────────────────────")
    for sid, (prompt, style) in CHAR_PROMPTS.items():
        dest = STILLS / f"{sid}.png"
        if render:
            render_image(sid, prompt, style, dest)
        else:
            print(f"  [dry] {sid}")

# ── Plate cache ───────────────────────────────────────────────────────────────
_cache: dict[str, object] = {}

def load_plate(path: Path, size: tuple[int, int], alpha: bool = False):
    import pygame
    key = f"{path}:{size}:{alpha}"
    if key not in _cache:
        if not path.exists():
            _cache[key] = None
        else:
            img = pygame.image.load(str(path))
            img = img.convert_alpha() if alpha else img.convert()
            _cache[key] = pygame.transform.smoothscale(img, size)
    return _cache[key]

def bg_plate(name: str):
    for ext in (".png", ".jpg"):
        p = STILLS / f"{name}{ext}"
        if p.exists():
            return load_plate(p, (W, H), False)
    return None

def char_plate(name: str):
    for d in (STILLS, CHARS):
        p = d / f"{name}.png"
        if p.exists():
            return load_plate(p, (280, 500), True)
    return None

# ── Visual breakpoints ────────────────────────────────────────────────────────
def _visual_breakpoints(cues: list[dict]) -> list[float]:
    scale   = get_cue_scale(cues)
    mp3_dur = cues[-1]["end"] / scale if cues else 700.0
    tail    = (mp3_dur + 8.0) * scale

    bps: set[float] = {0.0, tail}
    last_act = -1
    for c in cues:
        if c.get("act", 0) != last_act:
            bps.add(c["start"])
            last_act = c["act"]

    return sorted(bps)

# ── Draw ──────────────────────────────────────────────────────────────────────
def draw_frame(screen, audio_t: float, cues: list[dict], font, font_mono) -> None:
    import pygame
    cue_t = audio_to_cue(audio_t, cues)
    act   = act_from_cue(cues, cue_t)

    # Background
    bg_name = ACT_BACKGROUNDS.get(act, "scriptorium_screen")
    bg = bg_plate(bg_name)
    if bg:
        screen.blit(bg, (0, 0))
    else:
        screen.fill(NIGHT)
        lbl = font.render(f"[ {bg_name} ]", True, BONE)
        screen.blit(lbl, (W // 2 - lbl.get_width() // 2, H // 2 - 12))

    # Shakespeare: always left, static
    sh = char_plate("shakespeare_quill")
    if sh:
        screen.blit(sh, (80, H - 520))
    else:
        ph = pygame.Surface((260, 480), pygame.SRCALPHA)
        ph.fill((*NIGHT, 180))
        pl = font.render("SHAKESPEARE", True, BONE)
        ph.blit(pl, (10, 230))
        screen.blit(ph, (80, H - 500))

    # Chaucer: position varies by act
    ch_key  = CHAUCER_POSITIONS.get(act, "chaucer_observing")
    chaucer = char_plate(ch_key)
    if chaucer:
        # Dramatic x-offset: herald comes closer to center in later acts
        x_offsets = {
            "chaucer_observing":    W - 360,
            "chaucer_descending":   W - 390,
            "chaucer_verse":        W - 370,
            "chaucer_road_forward": W - 420,
            "chaucer_herald":       W - 460,  # arms-wide needs more room
            "chaucer_matthew":      W - 400,
            "chaucer_road_close":   W - 350,
        }
        x = x_offsets.get(ch_key, W - 360)
        screen.blit(chaucer, (x, H - 520))
    else:
        ph = pygame.Surface((260, 480), pygame.SRCALPHA)
        ph.fill((*NIGHT, 180))
        pl = font.render(f"CHAUCER\n{ch_key}", True, BONE)
        ph.blit(pl, (10, 230))
        screen.blit(ph, (W - 380, H - 500))

    # HUD
    cue = cue_at(cues, cue_t)
    if cue:
        spk_color = PARCHMENT if cue["speaker"] == "Shakespeare" else BONE
        screen.blit(font.render(cue["speaker"], True, spk_color), (40, H - 52))
        screen.blit(font_mono.render((cue["text"] or "")[:90], True, CHALK), (40, H - 28))

    # Act indicator
    screen.blit(font_mono.render(f"Act {act}  {bg_name}", True, (*CHALK, 160)), (40, 8))
    tc = f"{int(audio_t // 60):02d}:{int(audio_t % 60):02d}"
    screen.blit(font_mono.render(tc, True, (*CHALK, 180)), (W - 80, 8))

# ── Pygame preview ────────────────────────────────────────────────────────────
def cmd_pygame(seek: float = 0.0) -> None:
    import pygame
    pygame.init()
    pygame.mixer.init()
    screen = pygame.display.set_mode((W, H))
    pygame.display.set_caption("-35 The Ridiculous Journey")
    clock = pygame.time.Clock()
    font      = pygame.font.SysFont("serif", 20)
    font_mono = pygame.font.SysFont("monospace", 13)

    cues  = load_cues()
    audio = AUDIO / "minus35.mp3"
    if not audio.exists():
        sys.exit(f"missing audio: {audio}  (run `audio` first)")
    pygame.mixer.music.load(str(audio))
    pygame.mixer.music.play(start=max(0.0, seek))

    running = True
    while running:
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                running = False
            if ev.type == pygame.KEYDOWN and ev.key in (pygame.K_ESCAPE, pygame.K_q):
                running = False
        if not pygame.mixer.music.get_busy():
            break
        audio_t = seek + pygame.mixer.music.get_pos() / 1000.0
        screen.fill(INK)
        draw_frame(screen, audio_t, cues, font, font_mono)
        pygame.display.flip()
        clock.tick(FPS)
    pygame.quit()

# ── Frame export ──────────────────────────────────────────────────────────────
def cmd_frames() -> None:
    import pygame
    FRAMES.mkdir(parents=True, exist_ok=True)
    os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
    os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
    pygame.init()
    pygame.display.set_mode((W, H))
    screen    = pygame.Surface((W, H))
    font      = pygame.font.SysFont("serif", 20)
    font_mono = pygame.font.SysFont("monospace", 13)

    cues  = load_cues()
    scale = get_cue_scale(cues)
    bps   = _visual_breakpoints(cues)

    concat = OUT / "concat.txt"
    lines  = ["ffconcat version 1.0"]
    last_rel = ""

    print(f"Rendering {len(bps) - 1} unique frames …")
    for i in range(len(bps) - 1):
        cue_start = bps[i]
        cue_end   = bps[i + 1]
        mid_cue_t = (cue_start + cue_end) / 2.0
        dur_audio = (cue_end - cue_start) / scale

        audio_t = (mid_cue_t + AUDIO_OFFSET) / scale

        screen.fill(INK)
        draw_frame(screen, audio_t, cues, font, font_mono)

        fname = f"f{i:05d}.png"
        pygame.image.save(screen, str(FRAMES / fname))

        act = act_from_cue(cues, mid_cue_t)
        rel = f"frames/{fname}"
        lines.append(f"file '{rel}'")
        lines.append(f"duration {dur_audio:.4f}")
        last_rel = rel
        print(f"  [{i:3d}] act={act}  cue={mid_cue_t:6.1f}s  hold={dur_audio:.2f}s  "
              f"{ACT_BACKGROUNDS.get(act,'?')}", flush=True)

    lines.append(f"file '{last_rel}'")
    concat.write_text("\n".join(lines) + "\n")
    pygame.quit()
    print(f"Done — {len(bps)-1} frames  →  {concat}")

# ── Assembly ──────────────────────────────────────────────────────────────────
def cmd_assemble() -> None:
    mp4    = OUT / "-35_the_ridiculous_journey.mp4"
    audio  = AUDIO / "minus35.mp3"
    concat = OUT  / "concat.txt"
    if not audio.exists():
        sys.exit(f"missing audio: {audio}")
    if not concat.exists():
        sys.exit("concat.txt missing — run frames first")
    cmd = [
        "ffmpeg", "-y",
        "-f", "concat", "-safe", "0", "-i", str(concat),
        "-i", str(audio),
        "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "22",
        "-c:a", "aac", "-b:a", "192k",
        "-shortest",
        str(mp4),
    ]
    print(" ".join(cmd))
    subprocess.run(cmd, check=True)
    print(f"Output: {mp4}  ({mp4.stat().st_size // (1024*1024)}MB)")

# ── CLI ───────────────────────────────────────────────────────────────────────
def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["audio", "stills", "pygame", "frames", "assemble", "all"])
    ap.add_argument("--render", action="store_true")
    ap.add_argument("--seek",   type=float, default=0.0)
    args = ap.parse_args()

    if   args.cmd == "audio":    cmd_audio()
    elif args.cmd == "stills":   cmd_stills(render=args.render)
    elif args.cmd == "pygame":   cmd_pygame(seek=args.seek)
    elif args.cmd == "frames":   cmd_frames()
    elif args.cmd == "assemble": cmd_assemble()
    elif args.cmd == "all":
        cmd_audio()
        cmd_stills(render=args.render)
        cmd_frames()
        cmd_assemble()

if __name__ == "__main__":
    main()
