#!/usr/bin/env python3
"""Page −30 — The Green Light.

Darkest Dungeon visual language. Dock at night. Green light across the water.

Rules:
  - Auden is always on the left. He never goes away.
  - Right side: the character who last spoke or was described stays up
    until a different character takes over. No blinking. No narrator competing.
  - Green light blinks on/off with the click cues.
  - Book photo at open (poem) and close. Screenshots for the review section.

  .venv/bin/python tools/build_minus30_video.py stills           # dry-run
  .venv/bin/python tools/build_minus30_video.py stills --render  # call API
  .venv/bin/python tools/build_minus30_video.py pygame           # preview
  .venv/bin/python tools/build_minus30_video.py frames           # export frames
  .venv/bin/python tools/build_minus30_video.py assemble         # ffmpeg -> mp4
  .venv/bin/python tools/build_minus30_video.py all
"""
from __future__ import annotations

import argparse
import base64
import json
import os
import subprocess
import sys
from pathlib import Path

BASE   = Path(__file__).resolve().parent.parent
AUDIO  = BASE / "audio" / "minus30"
OUT    = BASE / "video" / "minus30"
STILLS = OUT / "stills"
FRAMES = OUT / "frames"
CHARS  = BASE / "video" / "stills" / "characters"

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
GREEN_RGB = (0,   180, 80)

# ── Green light click events ──────────────────────────────────────────────────
# Timestamps in cue-time (from cues.jsonl).
# Pattern: click1 ON, click2 OFF, click3 ON (sustained).
# End: dark from ~779s, final click ON at ~789.8s.
LIGHT_EVENTS: list[tuple[float, bool]] = [
    (156.4, True),   # click 1 — ON
    (157.2, False),  # click 2 — OFF
    (158.1, True),   # click 3 — ON (sustained through scene)
    (779.0, False),  # light fades as notebook closes
    (787.1, True),   # final click — ON  (cue [160] "click.")
]

def light_on(cue_t: float) -> bool:
    state = False
    for et, es in LIGHT_EVENTS:
        if cue_t >= et:
            state = es
        else:
            break
    return state

# ── Background phases (cue-time) ──────────────────────────────────────────────
# book_photo and screenshot_* are static full-screen images from STILLS.
PHASES: list[tuple[float, float, str]] = [
    (0.0,    31.7,   "book_photo"),        # poem (Hölderlin)
    (31.7,   75.0,   "dock_establishing"),
    (75.0,   154.5,  "dock_behind_men"),
    (154.5,  156.4,  "dock_midpoint"),
    (156.4,  157.2,  "green_on"),
    (157.2,  158.1,  "green_off"),
    (158.1,  164.0,  "green_on"),
    (164.0,  249.2,  "dock_behind_men"),
    (249.2,  389.3,  "dock_midpoint"),
    (389.3,  459.0,  "dock_behind_men"),
    (459.0,  572.3,  "dock_midpoint"),
    # ── Review section ──────────────────────────────────────────────────────
    # screenshot_1: "They is plural" → before "vain" note
    # screenshot_2: "vain" note (highlighted) → "Grade: present."
    # Switch at cue [140] start = 659.5s: "Gentle fetters = appropriate constraint."
    (572.3,  659.5,  "screenshot_1"),
    (659.5,  779.0,  "screenshot_2"),
    # ── End ─────────────────────────────────────────────────────────────────
    (779.0,  787.1,  "green_off"),         # light dark after notebook closes
    (787.1,  800.0,  "book_photo"),        # final click ON → poem stays 10 s
]
STATIC = {"book_photo", "screenshot_1", "screenshot_2"}

def phase_at(cue_t: float) -> str:
    for s, e, name in PHASES:
        if s <= cue_t < e:
            return name
    return PHASES[-1][2]

# ── Audio → cue-time conversion ───────────────────────────────────────────────
# cues.jsonl total is slightly longer than the actual MP3 (MP3 encoding pads
# each segment; padding accumulates). Convert audio playback position to
# cue-time by linear proportion.
#
# If images appear EARLY relative to narration, increase AUDIO_OFFSET.
# If images appear LATE, decrease it (or set negative).
AUDIO_OFFSET = 0.3   # seconds: delay cue lookup this much after audio position

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
         "-of", "default=noprint_wrappers=1:nokey=1", str(AUDIO / "minus30.mp3")],
        capture_output=True, text=True,
    )
    try:
        mp3_dur = float(r.stdout.strip())
    except Exception:
        mp3_dur = cue_dur
    # At audio fraction f, cue position is f * cue_dur
    # scale = cue_dur / mp3_dur
    _cue_scale_cache = cue_dur / mp3_dur if mp3_dur > 0 else 1.0
    return _cue_scale_cache

def audio_to_cue(t: float, cues: list[dict]) -> float:
    """Convert audio playback position to cue-time, with offset correction."""
    return max(0.0, t * get_cue_scale(cues) - AUDIO_OFFSET)

# ── Right-side character timeline ─────────────────────────────────────────────
# Which character is currently on the right panel (cue-time driven).
# Characters stay up through narration. Only a NEW non-Auden speaker (or
# description override) replaces the current right character.

# Description windows: Auden describes these characters → show them on right.
# (cue-time start, cue-time end, char_key)
DESCRIPTIONS: list[tuple[float, float, str]] = [
    (74.9,   87.0,  "holden_jacket"),
    (87.0,  135.3,  "jay_white"),
    (135.3, 154.4,  "atticus_standing"),
    (249.2, 275.5,  "jay_pink"),
    (389.3, 411.2,  "jay_gold"),
]

# Speaker → character key, with suit-phase breakpoints (cue-time)
def speaker_char(speaker: str, cue_t: float) -> str | None:
    if speaker == "Auden":
        return None
    maps = [
        (249.2, {"Holden": "holden_jacket", "Jay": "jay_white",  "Atticus": "atticus_standing"}),
        (389.3, {"Holden": "holden_phony",  "Jay": "jay_pink",   "Atticus": "atticus_speak"}),
        (1e9,   {"Holden": "holden_smoke",  "Jay": "jay_gold",   "Atticus": "atticus_court"}),
    ]
    for threshold, m in maps:
        if cue_t < threshold:
            return m.get(speaker)
    return None

def description_char(cue_t: float) -> str | None:
    for s, e, c in DESCRIPTIONS:
        if s <= cue_t < e:
            return c
    return None

def build_right_timeline(cues: list[dict]) -> list[tuple[float, str | None]]:
    """Return list of (audio_start_t, char_key) breakpoints.

    char_key is None until the first character appears.
    Characters persist through Auden narration.
    """
    scale = get_cue_scale(cues)
    breaks: list[tuple[float, str | None]] = [(0.0, None)]
    current: str | None = None

    for c in cues:
        cue_t   = (c["start"] + c["end"]) / 2.0
        audio_t = c["start"] / scale + AUDIO_OFFSET  # when image should switch

        desc = description_char(cue_t)
        if desc and desc != current:
            current = desc
            breaks.append((audio_t, current))
        elif c["speaker"] != "Auden":
            ch = speaker_char(c["speaker"], cue_t)
            if ch and ch != current:
                current = ch
                breaks.append((audio_t, current))

    return breaks

def right_char(timeline: list[tuple[float, str | None]], audio_t: float) -> str | None:
    result = None
    for t, ch in timeline:
        if audio_t >= t:
            result = ch
        else:
            break
    return result

# ── Style strings ─────────────────────────────────────────────────────────────
STYLE_DD = (
    "High-contrast ink illustration. Bold lampblack with deep shadow pools. "
    "Side-profile framing. Single torch-source lighting: warm rust from one side, "
    "cold deep shadow on the other. "
    "Rust #8C3A2A and bone #E6DCC8 palette. Gothic weight. "
    "Refined ink faces, readable features. Ink planes, no gradients. "
    "No anime eyes. No CGI gloss. No photography. No captions or text. "
)

# ── Image prompts ─────────────────────────────────────────────────────────────
BG_PROMPTS: dict[str, tuple[str, str]] = {
    "dock_establishing": (
        "A wooden dock extends forty feet over still black water at night. "
        "The planks are old and weathered. No rails. "
        "Cold mist at knee height above the black water. "
        "Far at the dock's end, three silhouetted male figures, very small. "
        "One figure at the midpoint, slightly apart. "
        "Across the water on the far shore: a single small green electric light. "
        "Moonlight on planks. Deep shadow under dock. Side-view. Night, cold, still.",
        "dd"
    ),
    "dock_behind_men": (
        "View from behind three men at the end of a long dock at night. "
        "No rails. Open black water on both sides. "
        "Three backs: left figure in a simple jacket hands in pockets; "
        "center in a formal white suit, gold watch chain at the waist; "
        "right in comfortable cotton clothes, hands at sides. "
        "Ahead across black water: a single green electric light, small, steady. "
        "Mist at knee height. Moonlight. Deep night sky.",
        "dd"
    ),
    "dock_midpoint": (
        "View from midpoint of a long dock at night, looking toward its end. "
        "Three men at the terminus, small silhouettes. "
        "Green electric light far right of frame, a small emerald point. "
        "Weathered planks, no rails, black water both sides. Mist at knee height.",
        "dd"
    ),
    "green_on": (
        "A single green electric dock light ON, iron post above still black water. "
        "Glowing emerald. Green glass lens lit. Green reflection on black water. "
        "Mist above water softly diffuses the glow. Close view, light is the subject.",
        "dd"
    ),
    "green_off": (
        "A single green electric dock light OFF. Same iron post, same angle as ON. "
        "Green glass lens dark. No reflection on black water below. "
        "Cold iron. Moonlight on water. The absence of light is the subject.",
        "dd"
    ),
    "green_above": (
        "View from just above a green electric dock light, looking back toward the dock. "
        "Green glow fills the foreground and obscures the near view. "
        "Beyond the green haze: long dock, three small figures at its far end. "
        "Cold black water below. Night sky.",
        "dd"
    ),
}

CHAR_PROMPTS: dict[str, tuple[str, str]] = {
    "jay_white": (
        "Full body side profile, transparent background. Jay Gatsby. Facing left. "
        "White summer flannel suit, single-breasted. Peaked lapels slightly wider than current fashion. "
        "Presidential breast pocket fold: three points pressed flat. "
        "Gold watch chain crossing waistcoat. Silver shirt. Collar slightly up. "
        "Posture of conviction, not yearning. Looking left toward an unseen light. "
        "Refined ink face. Ink planes.",
        "dd"
    ),
    "jay_pink": (
        "Full body side profile, transparent background. Jay Gatsby. Facing left. Same bearing. "
        "Pink suit: not rose, not salmon. Reconsidered halfway. Same peaked lapels. "
        "Pocket square: soft puff, one edge above pocket. Same gold watch chain. Collar not up. "
        "Looking left. Same man.",
        "dd"
    ),
    "jay_gold": (
        "Full body side profile, transparent background. Jay Gatsby. Facing left. Same bearing. "
        "Gold suit: the gold of late afternoon in fabric, worn at night. "
        "No pocket square. Same gold watch chain. Collar open at top button. Looking left.",
        "dd"
    ),
    "holden_jacket": (
        "Full body side profile, transparent background. Holden Caulfield. Facing left. "
        "Simple jacket. Hands in pockets. Looking at the water, not the light. "
        "Rationing. The face of someone who has been asked this before. Ink planes.",
        "dd"
    ),
    "holden_phony": (
        "Full body side profile, transparent background. Holden Caulfield. Facing right to confront. "
        "Same jacket. One hand extended. The only genuine emotional moment on the dock. "
        "Real feeling, not performance. Ink planes.",
        "dd"
    ),
    "holden_smoke": (
        "Full body side profile, transparent background. Holden Caulfield. Facing left. "
        "Same jacket. Lit cigarette in hand. Now looking at the light. Something shifted. Ink planes.",
        "dd"
    ),
    "atticus_standing": (
        "Full body side profile, transparent background. Atticus Finch. Facing left. "
        "Comfortable clothes: cotton, jacket over it. Hands at sides. Standing slightly apart. "
        "Looking at nothing specific. It is not absence. It is a wider aperture. Ink planes.",
        "dd"
    ),
    "atticus_speak": (
        "Full body side profile, transparent background. Atticus Finch. Facing left. Same clothes. "
        "In mid-speech. Deliberate. The deliberateness is not performance. Ink planes.",
        "dd"
    ),
    "atticus_court": (
        "Full body side profile, transparent background. Atticus Finch. Facing left. Same clothes. "
        "A memory in his posture. He has stood before a judge. Ink planes.",
        "dd"
    ),
    "auden_notebook": (
        "Full body side profile, transparent background. The narrator. Facing right toward the men. "
        "Open notebook in hand. Pen moving. Positioned at the midpoint of the dock to observe. "
        "Scholarly. The keeper of the record. Ink planes.",
        "dd"
    ),
}

# ── API render ────────────────────────────────────────────────────────────────
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
    r = requests.post(
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
    for d in (STILLS,):
        for ext in (".png", ".jpg"):
            p = d / f"{name}{ext}"
            if p.exists():
                return load_plate(p, (W, H), False)
    return None

def char_plate(name: str):
    for d in (STILLS, CHARS):
        p = d / f"{name}.png"
        if p.exists():
            return load_plate(p, (280, 500), True)
    return None

# ── Cues ──────────────────────────────────────────────────────────────────────
def load_cues() -> list[dict]:
    p = AUDIO / "cues.jsonl"
    if not p.exists():
        return []
    return [json.loads(l) for l in p.read_text().splitlines() if l.strip()]

def cue_at(cues: list[dict], cue_t: float) -> dict | None:
    for c in cues:
        if c["start"] <= cue_t < c["end"]:
            return c
    return cues[-1] if cues and cue_t >= cues[-1]["end"] else (cues[0] if cues else None)

# ── Draw ──────────────────────────────────────────────────────────────────────
def draw_green_glow(screen, on: bool) -> None:
    import pygame
    if not on:
        return
    glow = pygame.Surface((300, 300), pygame.SRCALPHA)
    for r in range(150, 0, -10):
        a = int(55 * (1 - r / 150))
        pygame.draw.circle(glow, (*GREEN_RGB, a), (150, 150), r)
    screen.blit(glow, (W - 200, H // 2 - 150))

def draw_frame(screen, audio_t: float, cues: list[dict],
               right_timeline: list[tuple[float, str | None]],
               font, font_mono) -> None:
    import pygame
    cue_t = audio_to_cue(audio_t, cues)
    phase = phase_at(cue_t)

    # ── Background ────────────────────────────────────────────────────────────
    bg = bg_plate(phase)
    if bg:
        screen.blit(bg, (0, 0))
    else:
        screen.fill(NIGHT)
        lbl = font.render(f"[ {phase} ]", True, BONE)
        screen.blit(lbl, (W // 2 - lbl.get_width() // 2, H // 2 - 12))

    if phase in STATIC:
        # Static phases: full-screen, no overlays
        tc = f"{int(audio_t // 60):02d}:{int(audio_t % 60):02d}"
        screen.blit(font_mono.render(tc, True, (*CHALK, 160)), (W - 80, 8))
        return

    # ── Green light glow ──────────────────────────────────────────────────────
    if phase not in ("green_on", "green_off"):
        draw_green_glow(screen, light_on(cue_t))

    # ── Auden: always left ────────────────────────────────────────────────────
    auden = char_plate("auden_notebook")
    if auden:
        screen.blit(auden, (80, H - 520))
    else:
        ph = pygame.Surface((260, 480), pygame.SRCALPHA)
        ph.fill((*NIGHT, 180))
        screen.blit(ph, (80, H - 500))

    # ── Right character: persists, no blinking ────────────────────────────────
    rch = right_char(right_timeline, audio_t)
    if rch:
        ch = char_plate(rch)
        if ch:
            screen.blit(ch, (W - 360, H - 520))
        else:
            ph = pygame.Surface((260, 480), pygame.SRCALPHA)
            ph.fill((*NIGHT, 180))
            pl = font.render(rch, True, BONE)
            ph.blit(pl, (10, 230))
            screen.blit(ph, (W - 360, H - 500))

    # ── HUD ───────────────────────────────────────────────────────────────────
    cue = cue_at(cues, cue_t)
    if cue:
        screen.blit(font.render(cue["speaker"], True, BONE), (40, H - 52))
        screen.blit(font_mono.render((cue["text"] or "")[:90], True, CHALK), (40, H - 28))

    # Light indicator dot
    on = light_on(cue_t)
    pygame.draw.circle(screen, GREEN_RGB if on else (40, 40, 40), (W - 24, H - 24), 10)
    pygame.draw.circle(screen, BONE, (W - 24, H - 24), 10, 1)

    # Timecode
    tc = f"{int(audio_t // 60):02d}:{int(audio_t % 60):02d}"
    screen.blit(font_mono.render(tc, True, (*CHALK, 180)), (W - 80, 8))

# ── Pygame preview ────────────────────────────────────────────────────────────
def cmd_pygame(seek: float = 0.0) -> None:
    import pygame
    pygame.init()
    pygame.mixer.init()
    screen = pygame.display.set_mode((W, H))
    pygame.display.set_caption("-30 The Green Light")
    clock = pygame.time.Clock()
    font      = pygame.font.SysFont("serif", 20)
    font_mono = pygame.font.SysFont("monospace", 13)

    cues = load_cues()
    audio = AUDIO / "minus30.mp3"
    if not audio.exists():
        sys.exit(f"missing audio: {audio}")
    pygame.mixer.music.load(str(audio))
    pygame.mixer.music.play(start=max(0.0, seek))

    right_tl = build_right_timeline(cues)

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
        draw_frame(screen, audio_t, cues, right_tl, font, font_mono)
        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()

# ── Unique-frame concat render ────────────────────────────────────────────────
# Every visual state change (phase boundary, character switch, light event)
# produces exactly ONE frame. ffmpeg concat demuxer holds each frame for the
# correct audio duration. For a slideshow this is 60-80 unique frames, not
# 23,000 clock-tick PNGs.

def _visual_breakpoints(cues: list[dict]) -> list[float]:
    """Return sorted list of cue-time breakpoints where the visual state changes."""
    scale = get_cue_scale(cues)
    mp3_dur = cues[-1]["end"] / scale if cues else 800.0
    tail_cue = (mp3_dur + 10.0) * scale   # 10 s tail in cue-time

    bps: set[float] = {0.0, tail_cue}

    # Phase boundaries
    for s, e, _ in PHASES:
        bps.add(s)
        bps.add(min(e, tail_cue))

    # Light events
    for cue_t, _ in LIGHT_EVENTS:
        bps.add(cue_t)

    # Character changes (right_tl is in audio-time → convert to cue-time)
    right_tl = build_right_timeline(cues)
    for audio_t, _ in right_tl:
        # Inverse of audio_to_cue: audio_t = (cue_t + AUDIO_OFFSET) / scale
        ct = (audio_t - AUDIO_OFFSET) * scale
        if 0.0 <= ct <= tail_cue:
            bps.add(ct)

    return sorted(bps)


def cmd_frames() -> None:
    """Render one PNG per unique visual interval and write concat.txt."""
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
    right_tl = build_right_timeline(cues)
    bps   = _visual_breakpoints(cues)

    concat = OUT / "concat.txt"
    lines  = ["ffconcat version 1.0"]
    last_rel = ""

    print(f"Rendering {len(bps) - 1} unique frames ...")
    for i in range(len(bps) - 1):
        cue_start = bps[i]
        cue_end   = bps[i + 1]
        mid_cue_t = (cue_start + cue_end) / 2.0
        dur_audio = (cue_end - cue_start) / scale   # real seconds this frame holds

        # Reconstruct the audio_t that maps to mid_cue_t (inverse of audio_to_cue)
        audio_t = (mid_cue_t + AUDIO_OFFSET) / scale

        screen.fill(INK)
        draw_frame(screen, audio_t, cues, right_tl, font, font_mono)

        fname = f"f{i:05d}.png"
        pygame.image.save(screen, str(FRAMES / fname))

        rel = f"frames/{fname}"
        lines.append(f"file '{rel}'")
        lines.append(f"duration {dur_audio:.4f}")
        last_rel = rel
        print(f"  [{i:3d}] cue={mid_cue_t:6.1f}s  hold={dur_audio:.2f}s  {phase_at(mid_cue_t)}",
              flush=True)

    # ffconcat requires last file listed again (to anchor final duration)
    lines.append(f"file '{last_rel}'")

    concat.write_text("\n".join(lines) + "\n")
    pygame.quit()
    print(f"Done — {len(bps)-1} frames  →  {concat}")


# ── ffmpeg assembly ───────────────────────────────────────────────────────────
def cmd_assemble() -> None:
    mp4    = OUT / "-30_the_green_light.mp4"
    audio  = AUDIO / "minus30.mp3"
    concat = OUT / "concat.txt"
    if not audio.exists():
        sys.exit(f"missing audio: {audio}")
    if not concat.exists():
        sys.exit(f"concat.txt missing — run frames first")
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
    ap.add_argument("cmd", choices=["stills", "pygame", "frames", "assemble", "all"])
    ap.add_argument("--render", action="store_true")
    ap.add_argument("--seek",   type=float, default=0.0)
    ap.add_argument("--end",    type=float, default=None)
    args = ap.parse_args()

    if   args.cmd == "stills":   cmd_stills(render=args.render)
    elif args.cmd == "pygame":   cmd_pygame(seek=args.seek)
    elif args.cmd == "frames":   cmd_frames()
    elif args.cmd == "assemble": cmd_assemble()
    elif args.cmd == "all":
        cmd_stills(render=args.render)
        cmd_frames()
        cmd_assemble()

if __name__ == "__main__":
    main()
