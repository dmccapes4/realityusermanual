#!/usr/bin/env python3
"""
Page −16 — Logos at the Workbench.

Faculty room. Pyramid model on the table. Three speakers:
  Oppenheimer, Keating, Yeshua (Merlin / Feynman / Chaucer registers).
Narration (stage / acts): GoinesFeynman — caption only; bodies stay at rest.

Same cut as −0000 / −30: unique stills held for cue duration, ffmpeg concat,
mux audio. No per-frame game loop.

  .venv/bin/python tools/build_minus16_video.py stills
  .venv/bin/python tools/build_minus16_video.py stills --render
  .venv/bin/python tools/build_minus16_video.py frames
  .venv/bin/python tools/build_minus16_video.py assemble
  .venv/bin/python tools/build_minus16_video.py all --render
"""

from __future__ import annotations

import argparse
import base64
import json
import os
import subprocess
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageEnhance, ImageFont

BASE = Path(__file__).resolve().parent.parent
OUT = BASE / "video" / "minus16"
STILLS = OUT / "stills"
FRAMES = OUT / "frames"
AUDIO = BASE / "audio" / "minus16" / "minus16.mp3"
CUES = BASE / "audio" / "minus16" / "cues.jsonl"

_env = BASE / ".env"
if _env.exists():
    for _l in _env.read_text().splitlines():
        _l = _l.strip()
        if _l and not _l.startswith("#") and "=" in _l:
            k, _, v = _l.partition("=")
            os.environ.setdefault(k.strip(), v.strip())

W, H = 1280, 720
BONE = (232, 220, 196)
INK = (18, 16, 14)

STYLE = (
    "Refined Samurai Jack still, gritty bizarre sci-fi noir. "
    "Bold lampblack ink silhouettes, flat limited palette, paper-tooth grit, hard noir shadows. "
    "Cream/bone ground, rust, one accent only. "
    "No photorealism, no anime eyes, no 3D render, no glossy CGI, no collage of existing actors. "
    "Soft in construction (few large shapes), heavy in presence. "
)

# (x, y, w, h) at rest. Speaker drawn last, slightly larger.
SEATS = {
    "oppenheimer": (40, 260, 360, 460),
    "keating": (460, 250, 360, 470),
    "yeshua": (860, 240, 380, 480),
}

FOCUS = {
    "oppenheimer": "Oppenheimer",
    "keating": "Keating",
    "yeshua": "Yeshua",
}

# Backgrounds — opaque
BG_PROMPTS = {
    "room": (
        "Wide establishing still of a late-evening faculty workbench room. "
        "Long wooden table center. On it: a wooden pyramidal model with one side removed, "
        "small stone blocks around a central shaft, a pressure gauge chamber, "
        "a copper-colored double helix on a dark cylinder, an oscilloscope, mineral specimens. "
        "Chalkboard on the back wall, mostly empty grid. Cream walls, one fluorescent tube. "
        "Empty chairs. No people. Architectural slab, ink noir.",
        False,
    ),
    "room_dark": (
        "Same faculty workbench room as before, but darker. The oscilloscope screen "
        "shows a faint horizontal line beginning to twitch. Pyramid model silhouette. "
        "No people. Ink noir, bone accents only on the scope glow (one rust/green accent).",
        False,
    ),
}

# Characters — transparent
CHAR_PROMPTS = {
    "oppenheimer_main": (
        "Full-body seated man mid-forties, thin precise academic, notebook and three pencils "
        "on his lap, soft-spoken posture at rest. Suit, slight exhaustion. "
        "Ink planes for face — readable, not a celebrity likeness. Transparent background.",
        True,
    ),
    "oppenheimer_speak": (
        "Same man standing slightly forward, chalk or pencil raised toward an unseen board, "
        "speaking with controlled intensity. Soft lisp implied only by composure, not comic. "
        "Ink planes. Transparent background.",
        True,
    ),
    "keating_main": (
        "Full-body man mid-forties, warm mid-baritone teacher energy, sitting astride a wooden "
        "chair turned backward, arms on the chair back, at rest, smile held. "
        "Ink planes — passionate English teacher, not a celebrity likeness. Transparent background.",
        True,
    ),
    "keating_speak": (
        "Same man standing, one foot on a chair rung or desk edge, speaking verse with delight, "
        "hand open. Soft New England classroom presence. Ink planes. Transparent background.",
        True,
    ),
    "yeshua_merlin": (
        "Full-body hooded figure, ageless mid-thirties. Within the hood silhouette: a dark "
        "starfield arranged as a cat's face looking forward, calm. Carpenter's square at his side. "
        "Quiet serious posture. Logos, not costume Jesus. Ink planes, cosmic head. Transparent background.",
        True,
    ),
    "yeshua_feynman": (
        "Same hooded figure, starfield-cat head brighter and sharper. Leaning toward an unseen "
        "board, lecturer posture, one hand explaining. Same instrument, teaching mode. "
        "Ink planes. Transparent background.",
        True,
    ),
    "yeshua_chaucer": (
        "Same hooded figure, starfield-cat head ringing outward like a herald. Oration posture, "
        "arms open, full commitment. Same instrument, announcement mode. "
        "Ink planes. Transparent background.",
        True,
    ),
}


def render_image(sid: str, prompt: str, transparent: bool, dest: Path) -> Path:
    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.exists() and dest.stat().st_size > 1000:
        print(f"  [skip] {sid}")
        return dest
    import requests

    key = os.environ.get("OPENAI_API_KEY", "").strip()
    if not key:
        sys.exit("Set OPENAI_API_KEY in .env")
    size = "1024x1536" if transparent else "1536x1024"
    payload = {
        "model": "gpt-image-1.5",
        "prompt": STYLE + prompt,
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
    STILLS.mkdir(parents=True, exist_ok=True)
    print("── Backgrounds ──")
    for sid, (prompt, transparent) in BG_PROMPTS.items():
        dest = STILLS / f"{sid}.png"
        if render:
            render_image(sid, prompt, transparent, dest)
        else:
            print(f"  [dry] {sid}")
    print("── Characters ──")
    for sid, (prompt, transparent) in CHAR_PROMPTS.items():
        dest = STILLS / f"{sid}.png"
        if render:
            render_image(sid, prompt, transparent, dest)
        else:
            print(f"  [dry] {sid}")


def plate_path(key: str) -> Path:
    return STILLS / f"{key}.png"


def load_plate(key: str, cache: dict) -> Image.Image:
    if key in cache:
        return cache[key]
    path = plate_path(key)
    if not path.exists():
        sys.exit(f"missing plate: {path}  (run stills --render)")
    im = Image.open(path).convert("RGBA")
    cache[key] = im
    return im


def fit(im: Image.Image, size: tuple[int, int], cache: dict, key: str) -> Image.Image:
    ck = (key, size)
    if ck in cache:
        return cache[ck]
    out = im.resize(size, Image.Resampling.LANCZOS)
    cache[ck] = out
    return out


def knockout_plate(im: Image.Image, cache: dict, key: str) -> Image.Image:
    """Near-black opaque pixels → transparent so character plates do not
    paint black rectangles over the room (API 'transparent' stills often
    leave a solid black field)."""
    ck = f"ko:{key}"
    if ck in cache:
        return cache[ck]
    im = im.convert("RGBA")
    pix = im.load()
    w, h = im.size
    for y in range(h):
        for x in range(w):
            r, g, b, a = pix[x, y]
            if a < 8:
                continue
            if r < 18 and g < 18 and b < 18:
                pix[x, y] = (0, 0, 0, 0)
    cache[ck] = im
    return im


def paste(frame: Image.Image, plate: Image.Image, xy: tuple[int, int], dim: float) -> None:
    if dim < 0.99:
        plate = ImageEnhance.Brightness(plate).enhance(dim)
    frame.paste(plate, xy, plate)


def who_key(speaker: str) -> str | None:
    if speaker == "Oppenheimer":
        return "oppenheimer"
    if speaker == "Keating":
        return "keating"
    if speaker.startswith("Yeshua"):
        return "yeshua"
    return None


def yeshua_pose(speaker: str) -> str:
    if "Chaucer" in speaker:
        return "chaucer"
    if "Feynman" in speaker:
        return "feynman"
    return "merlin"


def poses_for(speaker: str, text: str) -> dict[str, str]:
    """Rest is the return. Special replaces speak only when the line earns it."""
    poses = {
        "oppenheimer": "main",
        "keating": "main",
        "yeshua": "merlin",
    }
    who = who_key(speaker)
    if who == "oppenheimer":
        poses["oppenheimer"] = "speak"
    elif who == "keating":
        t = text.lower()
        if any(n in t for n in ("seize", "verse", "poetry", "desk", "extraordinary", "captain")):
            poses["keating"] = "speak"
        else:
            poses["keating"] = "speak"
    elif who == "yeshua":
        poses["yeshua"] = yeshua_pose(speaker)
    # Narrator / stage: all rest; Yeshua stays Merlin quiet unless last register sticky —
    # for stills we keep Merlin at rest when GoinesFeynman speaks.
    return poses


def caption_name(speaker: str) -> str:
    if speaker.startswith("Yeshua"):
        return speaker  # Yeshua Merlin / Feynman / Chaucer
    if speaker == "GoinesFeynman":
        return ""  # stage: no name bar noise, or optional "—"
    return speaker


def caption(frame: Image.Image, speaker: str) -> None:
    name = caption_name(speaker)
    if not name:
        return
    draw = ImageDraw.Draw(frame)
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf", 18)
    except OSError:
        font = ImageFont.load_default()
    bar = Image.new("RGBA", (W, 46), (12, 10, 8, 170))
    frame.paste(bar, (0, H - 46), bar)
    draw.text((24, H - 34), name, fill=BONE, font=font)


def mode_at(text: str, speaker: str, prev: str) -> str:
    t = text.lower()
    if "blackout" in t or t.strip() in {"end.", "end"}:
        return "dark"
    if "oscilloscope" in t and ("twitch" in t or "moves" in t or "vibration" in t):
        return "dark"
    if prev == "dark" and speaker == "GoinesFeynman" and ("blackout" in t or "end" in t):
        return "dark"
    return "table"


def compose(mode: str, poses: dict[str, str], speaker: str, cache: dict) -> Image.Image:
    """One still, one figure. No stacked character plates (zero overlap)."""
    bg_key = "room_dark" if mode == "dark" else "room"
    hall = fit(load_plate(bg_key, cache), (W, H), cache, f"{bg_key}-full")
    frame = Image.new("RGBA", (W, H))
    frame.paste(hall, (0, 0))

    focus_who = who_key(speaker)
    if focus_who:
        pose = poses[focus_who]
        key = f"yeshua_{pose}" if focus_who == "yeshua" else f"{focus_who}_{pose}"
        # Single figure, centered over the table — no second plate.
        tw, th = 420, 560
        x = (W - tw) // 2
        y = H - th - 40
        raw = knockout_plate(load_plate(key, cache), cache, key)
        plate = fit(raw, (tw, th), cache, f"{key}-fit-solo")
        paste(frame, plate, (x, y), 1.0)

    caption(frame, speaker)
    return frame.convert("RGB")


def cue_scale(cues: list[dict]) -> float:
    cue_end = float(cues[-1]["end"]) if cues else 0.0
    if cue_end <= 0:
        return 1.0
    r = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1", str(AUDIO)],
        capture_output=True, text=True,
    )
    try:
        mp3 = float(r.stdout.strip())
    except ValueError:
        return 1.0
    return cue_end / mp3 if mp3 > 0 else 1.0


def plan(cues: list[dict]) -> list[dict]:
    mode = "table"
    rows = []
    for cue in cues:
        mode = mode_at(cue["text"], cue["speaker"], mode)
        poses = poses_for(cue["speaker"], cue["text"])
        rows.append({**cue, "mode": mode, "poses": poses})
    return rows


def cmd_frames() -> None:
    """Write exclusive still holds: one PNG per contiguous visual state, no
    time overlap. Assembled later with ffmpeg -loop 1 -t per hold."""
    if not CUES.exists():
        sys.exit(f"missing cues: {CUES}")
    cues = [json.loads(l) for l in CUES.read_text().splitlines() if l.strip()]
    rows = plan(cues)
    FRAMES.mkdir(parents=True, exist_ok=True)
    for old in FRAMES.glob("*.png"):
        old.unlink()
    cache: dict = {}
    seen: dict[tuple, str] = {}
    holds: list[tuple[str, float, float]] = []
    n = 0
    for row in rows:
        key = (
            row["mode"],
            row["poses"]["oppenheimer"],
            row["poses"]["keating"],
            row["poses"]["yeshua"],
            who_key(row["speaker"]) or row["speaker"],
        )
        if key not in seen:
            frame = compose(row["mode"], row["poses"], row["speaker"], cache)
            name = f"f{n:04d}.png"
            frame.save(FRAMES / name)
            seen[key] = name
            n += 1
            print(
                f"  [{n:3d}] {row['start']:7.1f}s  {row['mode']:5}  {row['speaker']:16}  "
                f"solo={who_key(row['speaker']) or 'room'}",
                flush=True,
            )
        rel = f"frames/{seen[key]}"
        start, end = float(row["start"]), float(row["end"])
        if holds and holds[-1][0] == rel:
            holds[-1] = (rel, holds[-1][1], end)
        else:
            holds.append((rel, start, end))
    scale = cue_scale(cues)
    # Exclusive wall-clock holds: abut, never overlap.
    timeline: list[tuple[str, float]] = []
    t = 0.0
    for rel, start, end in holds:
        dur = max(0.04, (end - start) / scale)
        timeline.append((rel, dur))
        t += dur
    audio_dur = float(
        subprocess.run(
            ["ffprobe", "-v", "error", "-show_entries", "format=duration",
             "-of", "default=noprint_wrappers=1:nokey=1", str(AUDIO)],
            capture_output=True, text=True,
        ).stdout.strip()
        or "0"
    )
    if audio_dur > 0 and timeline:
        drift = audio_dur - t
        name, dur = timeline[-1]
        timeline[-1] = (name, max(0.04, dur + drift))
    holds_rows = [{"file": rel, "duration": round(dur, 4)} for rel, dur in timeline]
    (OUT / "holds.json").write_text(json.dumps(holds_rows, indent=1) + "\n")

    # ffconcat: abutting durations only (no overlap, no gap after drift fix).
    concat = ["ffconcat version 1.0"]
    last = ""
    for rel, dur in timeline:
        concat.append(f"file '{rel}'")
        concat.append(f"duration {dur:.4f}")
        last = rel
    concat.append(f"file '{last}'")
    (OUT / "concat.txt").write_text("\n".join(concat) + "\n")

    print(f"Cue clock {cues[-1]['end']:.2f}s  scale {scale:.6f}")
    print(f"Done — {n} unique frames, {len(timeline)} exclusive holds, "
          f"{sum(d for _, d in timeline):.2f}s")


def cmd_assemble() -> None:
    """ffmpeg concat demuxer over exclusive still holds + audio. CFR 1 fps."""
    if not (OUT / "concat.txt").exists():
        sys.exit("run frames first")
    if not AUDIO.exists():
        sys.exit(f"missing audio: {AUDIO}")
    mp4 = OUT / "minus16.mp4"
    cmd = [
        "ffmpeg", "-y",
        "-f", "concat", "-safe", "0", "-i", "concat.txt",
        "-i", str(AUDIO),
        "-vf", "fps=1,format=yuv420p",
        "-c:v", "libx264", "-tune", "stillimage", "-crf", "20",
        "-g", "30", "-bf", "0",
        "-c:a", "aac", "-b:a", "192k",
        "-shortest", "-movflags", "+faststart",
        str(mp4),
    ]
    subprocess.run(cmd, check=True, cwd=str(OUT))
    print(f"Output: {mp4}  ({mp4.stat().st_size // (1024 * 1024)}MB)")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", nargs="?", default="stills",
                    choices=["stills", "frames", "assemble", "all"])
    ap.add_argument("--render", action="store_true")
    args = ap.parse_args()
    if args.cmd == "stills":
        cmd_stills(render=args.render)
    elif args.cmd == "frames":
        cmd_frames()
    elif args.cmd == "assemble":
        cmd_assemble()
    elif args.cmd == "all":
        cmd_stills(render=args.render)
        cmd_frames()
        cmd_assemble()


if __name__ == "__main__":
    main()
