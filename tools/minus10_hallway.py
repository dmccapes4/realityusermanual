#!/usr/bin/env python3
"""PHASE 2 hallway loop + three Vincent approaches. Narrator on the page title."""
from __future__ import annotations

import base64
import json
import os
import subprocess
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
OUT = BASE / "video" / "minus10"
STILLS = OUT / "stills"
AUDIO = BASE / "audio" / "minus10"
sys.path.insert(0, str(BASE / "tools"))

_env = BASE / ".env"
if _env.exists():
    for line in _env.read_text().splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, _, v = line.partition("=")
            os.environ.setdefault(k.strip(), v.strip())

from build_minus14_video import PHOTO_PREFIX, grain, place_still, title_card, ffprobe_dur
import generate_audio as ga

NARRATOR_ID = "Nxtvajpo1h6Ok0K5zP4M"  # library Narrator
TITLE_TEXT = (
    "Page minus ten. The Haunt in the Hallway. "
    "After minus seven. Stamper watched the arm. Goines turned right, into the wing."
)

HALL_LOCK = (
    "Same corridor in every frame. Weyland-Yutani crossed with Gattaca. "
    "One-point perspective, chest-height camera. Recessed fluorescent tubes "
    "in a perfect ceiling grid, every tube the same brightness, none flickering. "
    "Pale walls, pale floor tiles, no signage, no doors, no windows, no people. "
    "Immaculate maintenance. The corridor does not end."
)
HALL = [
    ("hall_01", HALL_LOCK + " Standing at the first station. Vanishing point empty and distant."),
    ("hall_02", HALL_LOCK + " One step closer. Ceiling grid and floor tiles have advanced one bay. Vanishing point still empty."),
    ("hall_03", HALL_LOCK + " Two steps further. Another bay of recessed tubes has passed overhead. Vanishing point still empty."),
    ("hall_04", HALL_LOCK + " Three steps further. Geometry repeats. The end has not arrived. Full-bleed photograph of the corridor itself. No hands. No postcard. No photograph-within-a-photograph. No frame edges."),
    ("hall_05", HALL_LOCK + " Four steps further. Infinite still. No occupant. No corner."),
]
VINCENT_LOCK = (
    "The same man in this same empty PHASE 2 hallway. Mid-thirties. Dark hair "
    "combed back with a short side part. Clean-shaven. High cheekbones, thin nose, "
    "calm dark eyes, Gattaca bone. Excellent dark two-button suit, white shirt, "
    "narrow dark tie, no vest, white pocket square. Walks toward camera, "
    "proportional stride. Recessed fluorescents do not flicker. No other people. "
    "No wall lettering. No signs. No printed words. Not Ethan Hawke. Not Vincent Price. "
    "Not a horror host. No cape. No fangs."
)
VINCENT = [
    ("vincent_far", VINCENT_LOCK + " He is far down the vanishing point, small in the frame, full figure."),
    ("vincent_mid", VINCENT_LOCK + " Mid-distance. Full figure. Face readable. Suit excellent."),
    ("vincent_near", VINCENT_LOCK + " Close. Chest-up, same face, same hair, same suit, no vest. Still walking."),
]


def render(sid: str, prompt: str) -> Path:
    dest = STILLS / f"{sid}.png"
    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.exists() and dest.stat().st_size > 1000:
        print(f"  [skip] {sid}", flush=True)
        return dest
    import requests
    key = os.environ.get("OPENAI_API_KEY", "").strip()
    if not key:
        sys.exit("Set OPENAI_API_KEY")
    payload = {
        "model": "gpt-image-1.5",
        "prompt": PHOTO_PREFIX + "\n" + prompt,
        "size": "1536x1024",
        "background": "opaque",
        "quality": "high",
        "output_format": "png",
        "n": 1,
    }
    dest.with_suffix(".request.json").write_text(json.dumps({"id": sid, "prompt": prompt}, indent=2) + "\n")
    r = requests.post(
        "https://api.openai.com/v1/images/generations",
        headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
        json=payload,
        timeout=180,
    )
    if r.status_code != 200:
        sys.exit(f"{sid} failed {r.status_code} {r.text[:300]}")
    dest.write_bytes(base64.b64decode(r.json()["data"][0]["b64_json"]))
    print(f"  [ok] {sid}  {dest.stat().st_size}", flush=True)
    return dest


def letterbox(src: Path, dest: Path) -> Path:
    return place_still(src, dest)


def speak(speaker: str, text: str, voice_id: str, dest: Path) -> tuple[Path, float]:
    dest.parent.mkdir(parents=True, exist_ok=True)
    paths = ga.tts(speaker, text, voice_id)
    if not paths:
        sys.exit(f"no audio for {speaker}: {text[:60]!r}")
    ga.concatenate(paths, dest)
    return dest, ffprobe_dur(dest)


def parse_minus10() -> tuple[str, str, str]:
    raw = (BASE / "src" / "-10_the_haunt_in_the_hallway.md").read_text()
    body = raw.split("---")[1].strip()
    i = body.find("What is this?")
    walk = body[:i].strip()
    closer = body[i:].strip()
    j = closer.find("Ah a man")
    return walk, closer[:j].strip(), closer[j:].strip()


def hallway_holds(loop_ids: list[str], placed: dict, seconds: float, hold: float) -> list[str]:
    lines = []
    elapsed = 0.0
    i = 0
    while elapsed < seconds - 1e-6:
        sid = loop_ids[i % len(loop_ids)]
        remain = seconds - elapsed
        d = hold if remain > hold else remain
        lines += [f"file '{placed[sid].resolve()}'", f"duration {d:.3f}"]
        elapsed += d
        i += 1
    return lines


def main():
    STILLS.mkdir(parents=True, exist_ok=True)
    AUDIO.mkdir(parents=True, exist_ok=True)
    frames = OUT / "frames"
    frames.mkdir(parents=True, exist_ok=True)

    print("stills", flush=True)
    for sid, prompt in HALL + VINCENT:
        render(sid, prompt)

    walk, pre, man = parse_minus10()
    goines_id = ga.VOICE_MAP["Goines"]  # Jeffrey — the fast one walks the hall

    print("narrator", flush=True)
    ga.VOICE_MAP["The Narrator"] = NARRATOR_ID
    title_mp3, title_dur = speak("The Narrator", TITLE_TEXT, NARRATOR_ID, AUDIO / "title.mp3")
    title_dur = max(4.0, title_dur)

    print("goines walk", flush=True)
    walk_mp3, walk_dur = speak("Goines", walk, goines_id, AUDIO / "walk.mp3")
    print("goines closer", flush=True)
    pre_mp3, pre_dur = speak("Goines", pre, goines_id, AUDIO / "pre.mp3")
    man_mp3, man_dur = speak("Goines", man, goines_id, AUDIO / "man.mp3")

    title_card("PAGE −10", frames / "t00.png", "the haunt in the hallway")

    hall_ids = [s for s, _ in HALL]
    loop_ids = hall_ids + list(reversed(hall_ids[1:-1]))
    placed = {}
    for sid in hall_ids + [s for s, _ in VINCENT]:
        placed[sid] = letterbox(STILLS / f"{sid}.png", frames / f"{sid}.png")

    gif_dir = OUT / "gif_frames"
    gif_dir.mkdir(exist_ok=True)
    from PIL import Image
    for i, sid in enumerate(loop_ids):
        Image.open(placed[sid]).resize((960, 540), Image.Resampling.LANCZOS).save(gif_dir / f"{i:02d}.png")
    gif = OUT / "phase2_hallway_loop.gif"
    subprocess.run(
        ["ffmpeg", "-y", "-framerate", "2", "-i", str(gif_dir / "%02d.png"),
         "-vf", "split[s0][s1];[s0]palettegen=max_colors=64[p];[s1][p]paletteuse",
         "-loop", "0", str(gif)],
        check=True, capture_output=True,
    )
    print(f"[gif] {gif}  {gif.stat().st_size}", flush=True)

    hall_hold = 0.70
    vince_hit = 0.85
    hall_seconds = walk_dur + pre_dur
    near_hold = max(vince_hit, man_dur - 2 * vince_hit)

    concat = []
    concat += [f"file '{(frames / 't00.png').resolve()}'", f"duration {title_dur:.3f}"]
    concat += hallway_holds(loop_ids, placed, hall_seconds, hall_hold)
    concat += [
        f"file '{placed['vincent_far'].resolve()}'", f"duration {vince_hit:.3f}",
        f"file '{placed['vincent_mid'].resolve()}'", f"duration {vince_hit:.3f}",
        f"file '{placed['vincent_near'].resolve()}'", f"duration {near_hold:.3f}",
        f"file '{placed['vincent_near'].resolve()}'",
    ]
    list_path = OUT / "concat.txt"
    list_path.write_text("\n".join(concat) + "\n")

    mix = AUDIO / "minus10.mp3"
    ga.concatenate([title_mp3, walk_mp3, pre_mp3, man_mp3], mix)

    dest = OUT / "minus10_hallway.mp4"
    r = subprocess.run(
        ["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(list_path),
         "-i", str(mix),
         "-c:v", "libx264", "-preset", "medium", "-crf", "20",
         "-tune", "stillimage", "-pix_fmt", "yuv420p",
         "-c:a", "aac", "-b:a", "192k",
         "-shortest", "-movflags", "+faststart", str(dest)],
        capture_output=True, text=True,
    )
    if r.returncode != 0:
        sys.exit(r.stderr[-1200:])
    pages = BASE / "video" / "pages"
    pages.mkdir(parents=True, exist_ok=True)
    page = pages / "-10_the_haunt_in_the_hallway.mp4"
    if page.exists() or page.is_symlink():
        page.unlink()
    page.hardlink_to(dest)
    print(f"[ok] {dest}  {dest.stat().st_size}", flush=True)
    print(f"[page] {page}", flush=True)


if __name__ == "__main__":
    main()
