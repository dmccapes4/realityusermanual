#!/usr/bin/env python3
"""
Assemble v0.0.1 from cues + plates + dialog_reading.mp3.

Same layout as pygame_sync. One still per cue, concat by duration, mux audio.

  .venv/bin/python tools/assemble_video.py
  .venv/bin/python tools/assemble_video.py --version 0.0.1
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

BASE = Path(__file__).resolve().parent.parent
VIDEO = BASE / "video"
W, H = 1280, 720
BONE = (230, 220, 200)
INK = (11, 11, 12)

ANCHOR = {
    "speak": ((72, 72), (400, 580)),
    "seated": ((0, 0), (240, 340)),
    "back": ((980, 140), (170, 260)),
    "walk": ((500, 130), (280, 520)),
    "fx": ((860, 180), (280, 280)),
    "prop": ((900, 430), (300, 200)),
}
SEATED_ROW = [(80, 280), (340, 280), (600, 280)]


def load_jsonl(path: Path) -> list[dict]:
    return [json.loads(l) for l in path.read_text().splitlines() if l.strip()]


def index_by_id(path: Path) -> dict[str, dict]:
    return {row["id"]: row for row in load_jsonl(path)}


def kind_of(shot: dict) -> str:
    layer = shot.get("layer")
    if layer in {"prop", "fx"}:
        return layer
    if layer == "background":
        return "background"
    state = shot.get("state") or ""
    if "seated" in state or state in {"sit", "lie_drip", "sleep", "work"}:
        return "seated"
    if state in {"walk_door", "exit_outside"}:
        return "walk"
    if shot.get("character") == "stanley":
        return "back"
    return "speak"


def open_rgba(path: Path, size: tuple[int, int]) -> Image.Image | None:
    if not path.exists() or path.stat().st_size < 1000:
        return None
    im = Image.open(path).convert("RGBA")
    return im.resize(size, Image.Resampling.LANCZOS)


def scene_key(cue: dict) -> tuple:
    return (
        cue.get("background"),
        tuple(cue.get("layers") or []),
        bool(cue.get("full_bleed")),
        cue.get("speaker") or "",
        cue.get("camera") or "",
        cue.get("beat") or "",
    )


def compose(cue: dict, shots: dict[str, dict], cache: dict) -> Image.Image:
    frame = Image.new("RGB", (W, H), INK)
    bg_id = cue.get("background")
    bg_shot = shots.get(bg_id or "", {})
    rel = bg_shot.get("file")
    if rel:
        key = ("bg", rel)
        if key not in cache:
            cache[key] = open_rgba(BASE / rel, (W, H))
        bg = cache[key]
        if bg:
            frame.paste(bg.convert("RGB"), (0, 0))

    if not cue.get("full_bleed"):
        seated_i = 0
        for lid in cue.get("layers") or []:
            shot = shots.get(lid, {})
            kind = kind_of(shot)
            if kind == "speak":
                pos, size = ANCHOR["speak"]
            elif kind == "seated":
                pos, size = ANCHOR["seated"]
                pos = SEATED_ROW[seated_i % len(SEATED_ROW)]
                seated_i += 1
            elif kind == "back":
                pos, size = ANCHOR["back"]
            elif kind == "walk":
                pos, size = ANCHOR["walk"]
            elif kind == "fx":
                pos, size = ANCHOR["fx"]
            else:
                pos, size = ANCHOR["prop"]
            rel = shot.get("file")
            if not rel:
                continue
            key = ("fg", rel, size)
            if key not in cache:
                cache[key] = open_rgba(BASE / rel, size)
            plate = cache[key]
            if plate:
                frame.paste(plate, pos, plate)

    draw = ImageDraw.Draw(frame)
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf", 18)
        small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf", 13)
    except OSError:
        font = ImageFont.load_default()
        small = font
    label = f"{cue.get('speaker', '')}   {cue.get('camera') or ''}".strip()
    if label:
        draw.text((40, H - 52), label, fill=BONE, font=font)
    beat = cue.get("beat") or ""
    if beat:
        draw.text((40, H - 28), beat, fill=BONE, font=small)
    return frame


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--version", default="0.0.1")
    ap.add_argument("--audio", default=str(BASE / "audio" / "dialog_reading.mp3"))
    ap.add_argument("--cues", default=str(VIDEO / "cues.jsonl"))
    ap.add_argument("--keep-frames", action="store_true")
    args = ap.parse_args()

    audio = Path(args.audio)
    cues_path = Path(args.cues)
    if not audio.exists():
        sys.exit(f"missing audio: {audio}")
    if not cues_path.exists():
        sys.exit(f"missing cues: {cues_path}")

    shots = index_by_id(VIDEO / "catalogs" / "shots.jsonl")
    cues = load_jsonl(cues_path)
    if not cues:
        sys.exit("no cues")

    missing = []
    for row in shots.values():
        dest = BASE / row["file"]
        if not dest.exists() or dest.stat().st_size < 1000:
            missing.append(row["id"])
    if missing:
        sys.exit(f"plates missing ({len(missing)}): {', '.join(missing)}")

    out_dir = VIDEO / "out"
    frame_dir = out_dir / f"frames_v{args.version}"
    frame_dir.mkdir(parents=True, exist_ok=True)
    dest = out_dir / f"REALITY_USER_MANUAL_v{args.version}.mp4"

    cache: dict = {}
    unique: dict[tuple, Path] = {}
    concat_lines: list[str] = []
    last_path: Path | None = None
    n_unique = 0
    for i, cue in enumerate(cues):
        key = scene_key(cue)
        if key not in unique:
            frame = compose(cue, shots, cache)
            path = frame_dir / f"s{n_unique:04d}.png"
            frame.save(path, "PNG")
            unique[key] = path
            n_unique += 1
            last_path = path
        else:
            last_path = unique[key]
        dur = max(0.04, float(cue["end"]) - float(cue["start"]))
        concat_lines.append(f"file '{last_path.resolve()}'")
        concat_lines.append(f"duration {dur:.6f}")
    if last_path is not None:
        concat_lines.append(f"file '{last_path.resolve()}'")

    list_path = out_dir / f"concat_v{args.version}.txt"
    list_path.write_text("\n".join(concat_lines) + "\n")
    print(f"cues {len(cues)}  unique frames {n_unique}  → {dest}", flush=True)

    cmd = [
        "ffmpeg", "-y",
        "-f", "concat", "-safe", "0", "-i", str(list_path),
        "-i", str(audio),
        "-c:v", "libx264", "-preset", "medium", "-crf", "20",
        "-tune", "stillimage", "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "192k",
        "-shortest",
        "-movflags", "+faststart",
        str(dest),
    ]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        sys.exit(r.stderr[-1200:] if r.stderr else "ffmpeg failed")
    print(f"[ok] {dest}  {dest.stat().st_size} bytes")
    if not args.keep_frames:
        for p in frame_dir.glob("*.png"):
            p.unlink()
        try:
            frame_dir.rmdir()
        except OSError:
            pass


if __name__ == "__main__":
    main()
