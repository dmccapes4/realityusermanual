#!/usr/bin/env python3
"""
−0000 cast rewrite. Three readers at a round table in a dank hall.

Each man has a rest pose he returns to, a speaking pose, and three
specials used only on the lines that earn them. Unique frames, held
across the audio, the same way −30 and −35 are cut.

  .venv/bin/python tools/build_minus0000_video.py frames
  .venv/bin/python tools/build_minus0000_video.py assemble
"""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageEnhance, ImageFont

BASE = Path(__file__).resolve().parent.parent
ASSETS = Path("/home/dylanmccapes/.cursor/projects/home-dylanmccapes-dev/assets")
STILLS = BASE / "video" / "minus0000" / "stills"
FRAMES = BASE / "video" / "minus0000" / "frames"
OUT = BASE / "video" / "minus0000"
AUDIO = BASE / "audio" / "minus0000" / "minus0000.mp3"
CUES = BASE / "audio" / "minus0000" / "cues.jsonl"
W, H = 1280, 720
BONE = (232, 220, 196)
INK = (18, 16, 14)

PLATES = {
    "hall": "hall_round.jpg",
    "door": None,
    "morning": None,
    "chandler_main": "chandler_main.jpg",
    "chandler_speak": "chandler_speak.jpg",
    "chandler_notes": "chandler_notes.jpg",
    "chandler_welcome": "chandler_welcome.jpg",
    "chandler_aside": "chandler_aside.jpg",
    "ross_main": "ross_main.jpg",
    "ross_speak": "ross_speak.jpg",
    "ross_notes": "ross_notes.jpg",
    "ross_fingers": "ross_fingers.jpg",
    "ross_lecture": "ross_lecture.jpg",
    "joey_main": "joey_main.jpg",
    "joey_speak": "joey_speak.jpg",
    "joey_finger": "joey_finger.jpg",
    "joey_stanley": "joey_stanley.jpg",
    "joey_door": "joey_door.jpg",
}

# Existing ending plates, already in the book.
END_PLATES = {
    "door": BASE / "video/stills/layers/backgrounds/recast_door_closed.png",
    "morning": BASE / "video/stills/layers/backgrounds/recast_exterior_morning.png",
    "monarch_open": BASE / "video/stills/layers/fx/monarch_wings_open.png",
    "monarch_closed": BASE / "video/stills/layers/fx/monarch_wings_closed.png",
}

# (x, y, w, h) at rest. The speaker is drawn last, a little larger.
SEATS = {
    "chandler": (30, 300, 340, 420),
    "ross": (450, 270, 370, 450),
    "joey": (860, 300, 360, 420),
}


def ensure_stills() -> None:
    STILLS.mkdir(parents=True, exist_ok=True)
    for name in PLATES.values():
        if not name:
            continue
        dest = STILLS / name
        src = ASSETS / name
        if dest.exists() and dest.stat().st_size > 1000:
            continue
        if not src.exists():
            sys.exit(f"missing plate: {src}")
        shutil.copy(src, dest)


def key_green(im: Image.Image) -> Image.Image:
    im = im.convert("RGBA")
    pix = im.load()
    w, h = im.size
    for y in range(h):
        for x in range(w):
            r, g, b, a = pix[x, y]
            if g > 120 and g > r + 35 and g > b + 35:
                pix[x, y] = (0, 0, 0, 0)
            elif g > 80 and g > r + 18 and g > b + 18:
                pix[x, y] = (r, max(0, g - 40), b, 40)
    return im


def load_plate(key: str, cache: dict) -> Image.Image:
    if key in cache:
        return cache[key]
    if key in END_PLATES:
        im = Image.open(END_PLATES[key]).convert("RGBA")
    else:
        im = key_green(Image.open(STILLS / PLATES[key]))
    cache[key] = im
    return im


def fit(im: Image.Image, size: tuple[int, int], cache: dict, key: str) -> Image.Image:
    ck = (key, size)
    if ck in cache:
        return cache[ck]
    out = im.resize(size, Image.Resampling.LANCZOS)
    cache[ck] = out
    return out


def paste(frame: Image.Image, plate: Image.Image, xy: tuple[int, int], dim: float) -> None:
    if dim < 0.99:
        plate = ImageEnhance.Brightness(plate).enhance(dim)
    frame.paste(plate, xy, plate)


def chandler_pose(text: str) -> str:
    t = text.lower()
    if "welcome to the party" in t:
        return "welcome"
    if "write" in t or "pen " in t or "morality of the negative" in t:
        return "notes"
    if any(n in t for n in ("he's not reading", "low voice", "to ross", "quietly", "butterfly")):
        return "aside"
    return "speak"


def ross_pose(text: str) -> str:
    t = text.lower()
    if "write" in t or "just fine" in t:
        return "notes"
    if any(n in t for n in ("fingers", "five. seven", "calculating", "operationally")):
        return "fingers"
    if any(n in t for n in ("doctorate", "i'm feynman", "saying it first", "gathering", "dignity", "i know")):
        return "lecture"
    return "speak"


def joey_pose(text: str) -> str:
    t = text.lower()
    if any(n in t for n in ("who's got euler", "stan.", "third row", "looked up", "looks up")):
        return "stanley"
    if any(n in t for n in ("prism", "taps the page")):
        return "finger"
    if any(n in t for n in ("door open", "looks at the door", "butterfly")):
        return "door"
    return "speak"


def poses_for(mode: str, speaker: str, text: str) -> dict[str, str]:
    """Rest is the return. A special replaces speak only on the line that earns it."""
    poses = {"chandler": "main", "ross": "main", "joey": "main"}
    if mode == "listen":
        poses["chandler"] = "notes"
        return poses
    if mode == "freeze":
        poses["chandler"] = "notes"
        poses["ross"] = "main"
        return poses
    if mode in ("welcome", "exit"):
        poses["chandler"] = "welcome"
        return poses
    if mode == "butterfly":
        poses = {"chandler": "aside", "ross": "fingers", "joey": "door"}
        return poses
    if mode != "table":
        return poses
    if speaker == "Sauron (Default)":
        speaker = "Joey"
    if speaker == "Chandler":
        poses["chandler"] = chandler_pose(text)
    elif speaker == "Ross":
        poses["ross"] = ross_pose(text)
    elif speaker == "Joey":
        poses["joey"] = joey_pose(text)
    return poses


def mode_at(text: str, prev: str) -> str:
    t = text.lower()
    if prev == "butterfly" or any(n in t for n in (
        "monarch", "let it out", "wing scale", "leave the door open",
        "no answer", "narrator is gone",
    )):
        if prev in ("closed", "butterfly", "morning") or "monarch" in t or "butterfly" in t or "let it out" in t:
            return "butterfly"
    if "swung closed" in t or "pneumatic" in t:
        return "closed"
    if "haze of sunlight" in t or "saturday morning" in t or "smell of grass" in t:
        return "morning"
    if "stood up" in t or "pushed it open" in t:
        return "exit"
    if "cast does not move" in t or "pen he was writing" in t:
        return "freeze"
    if "welcome to the party" in t:
        return "welcome"
    if prev == "welcome":
        return "welcome"
    if "lip of the stage" in t or "stage direction sheet" in t or prev == "listen":
        if "welcome" not in t and "stood up" not in t:
            if prev == "listen" or "lip of the stage" in t or "stage direction sheet" in t or "none of us are real" in t:
                return "listen"
    if prev in ("freeze",):
        return "freeze"
    return "table"


def draw_stanley(frame: Image.Image, at_door: bool) -> None:
    """Back and absence. No face."""
    d = ImageDraw.Draw(frame, "RGBA")
    # Left of the two chairs in the third row. Back of a head, no face.
    # Right-hand chair of the third row, beside the vending machine.
    # Drawn after the readers so the head is not hidden behind Ross.
    x, y = 790, 300
    d.ellipse((x, y, x + 32, y + 28), fill=(22, 18, 16, 240))
    d.polygon([(x - 6, y + 22), (x + 38, y + 22), (x + 32, y + 70), (x + 0, y + 70)], fill=(18, 14, 12, 235))


def room_speaker(speaker: str) -> str:
    if speaker == "Sauron (Default)":
        return "Joey"
    return speaker


def caption(frame: Image.Image, speaker: str, text: str) -> None:
    draw = ImageDraw.Draw(frame)
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf", 18)
    except OSError:
        font = ImageFont.load_default()
    line = text.replace("\n", " ")
    if len(line) > 110:
        line = line[:107] + "..."
    bar = Image.new("RGBA", (W, 46), (12, 10, 8, 170))
    frame.paste(bar, (0, H - 46), bar)
    draw.text((24, H - 34), room_speaker(speaker), fill=BONE, font=font)


def compose(mode: str, poses: dict[str, str], speaker: str, text: str, cache: dict) -> Image.Image:
    if mode == "morning":
        bg = fit(load_plate("morning", cache), (W, H), cache, "morning-full")
        frame = Image.new("RGBA", (W, H))
        frame.paste(bg, (0, 0))
        caption(frame, speaker, text)
        return frame.convert("RGB")
    if mode in ("closed", "butterfly"):
        bg = fit(load_plate("door", cache), (W, H), cache, "door-full")
        frame = Image.new("RGBA", (W, H))
        frame.paste(bg, (0, 0))
        if mode == "butterfly":
            wing = "monarch_closed" if "closed its wings" in text.lower() else "monarch_open"
            bug = fit(load_plate(wing, cache), (220, 180), cache, wing)
            frame.paste(bug, (530, 250), bug)
            small = {"chandler": (40, 430, 240, 280), "ross": (500, 450, 250, 270), "joey": (980, 440, 250, 280)}
            for who in ("chandler", "ross", "joey"):
                key = f"{who}_{poses[who]}"
                plate = fit(load_plate(key, cache), small[who][2:], cache, key)
                dim = 1.0 if speaker.lower() == who else 0.78
                paste(frame, plate, small[who][:2], dim)
        caption(frame, speaker, text)
        return frame.convert("RGB")

    hall = fit(load_plate("hall", cache), (W, H), cache, "hall-full")
    frame = Image.new("RGBA", (W, H))
    frame.paste(hall, (0, 0))
    order = ["chandler", "joey", "ross"]
    focus = {"chandler": "Chandler", "ross": "Ross", "joey": "Joey"}
    speaker = room_speaker(speaker)
    if speaker in focus.values():
        who = next(k for k, v in focus.items() if v == speaker)
        order = [p for p in order if p != who] + [who]
    for who in order:
        x, y, w, h = SEATS[who]
        if speaker == focus[who] and mode == "table":
            w, h = int(w * 1.08), int(h * 1.08)
            x -= 16
            y -= 28
            dim = 1.0
        else:
            dim = 0.82 if mode == "table" and speaker in focus.values() else 1.0
        key = f"{who}_{poses[who]}"
        plate = fit(load_plate(key, cache), (w, h), cache, key)
        paste(frame, plate, (x, y), dim)
    if mode in ("table", "listen", "freeze", "welcome"):
        draw_stanley(frame, at_door=False)
    caption(frame, speaker, text)
    return frame.convert("RGB")


def cue_scale(cues: list[dict]) -> float:
    """Cue ends are the sum of each clip's probed length. The stitched mp3
    is shorter (encoder padding dropped on concat). −08 divides holds by
    this ratio so the picture stays on the voice."""
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
        mode = mode_at(cue["text"], mode)
        poses = poses_for(mode, cue["speaker"], cue["text"])
        rows.append({**cue, "mode": mode, "poses": poses})
    return rows


def cmd_frames() -> None:
    ensure_stills()
    cues = [json.loads(l) for l in CUES.read_text().splitlines() if l.strip()]
    rows = plan(cues)
    FRAMES.mkdir(parents=True, exist_ok=True)
    cache: dict = {}
    concat = ["ffconcat version 1.0"]
    last = ""
    seen: dict[tuple, str] = {}
    holds: list[tuple[str, float, float]] = []
    n = 0
    for row in rows:
        key = (row["mode"], tuple(sorted(row["poses"].items())), row["speaker"] if row["mode"] == "table" else "")
        # Speaker focus changes the frame even when poses match.
        key = (
            row["mode"],
            tuple(row["poses"][k] for k in ("chandler", "ross", "joey")),
            room_speaker(row["speaker"]) if row["mode"] == "table" else row["mode"],
            "wings" if "closed its wings" in row["text"].lower() else "",
        )
        if key not in seen:
            frame = compose(row["mode"], row["poses"], row["speaker"], row["text"], cache)
            name = f"f{n:04d}.png"
            frame.save(FRAMES / name)
            seen[key] = name
            n += 1
            print(
                f"  [{n:3d}] {row['start']:7.1f}s  {row['mode']:10}  {row['speaker']:12}  "
                f"{row['poses']['chandler']:8} {row['poses']['ross']:8} {row['poses']['joey']}",
                flush=True,
            )
        rel = f"frames/{seen[key]}"
        start, end = float(row["start"]), float(row["end"])
        if holds and holds[-1][0] == rel:
            holds[-1] = (rel, holds[-1][1], end)
        else:
            holds.append((rel, start, end))
    scale = cue_scale(cues)
    print(f"Cue clock {cues[-1]['end']:.2f}s  scale {scale:.6f}")
    for rel, start, end in holds:
        dur = max(0.04, (end - start) / scale)
        concat.append(f"file '{rel}'")
        concat.append(f"duration {dur:.4f}")
        last = rel
    concat.append(f"file '{last}'")
    (OUT / "concat.txt").write_text("\n".join(concat) + "\n")
    print(f"Done — {n} frames")


def cmd_assemble() -> None:
    mp4 = OUT / "-0000_cast_rewrite.mp4"
    cmd = [
        "ffmpeg", "-y",
        "-f", "concat", "-safe", "0", "-i", "concat.txt",
        "-i", str(AUDIO),
        "-fps_mode", "vfr",
        "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "20", "-bf", "0",
        "-c:a", "aac", "-b:a", "192k",
        "-shortest", "-movflags", "+faststart",
        str(mp4),
    ]
    subprocess.run(cmd, check=True, cwd=str(OUT))
    print(f"Output: {mp4}  ({mp4.stat().st_size // (1024 * 1024)}MB)")


def main() -> None:
    cmd = sys.argv[1] if len(sys.argv) > 1 else "frames"
    if cmd == "frames":
        cmd_frames()
    elif cmd == "assemble":
        cmd_assemble()
    else:
        sys.exit("use frames or assemble")


if __name__ == "__main__":
    main()
