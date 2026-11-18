#!/usr/bin/env python3
"""−10b slideshow. Ink plates. A plate stays up until the picture changes.

The opening is one light. Then the empty hall. Then Vincent, in steps:
barely at the vanishing point, the small far figure, the midway walk,
a closer walk, the approach. While he talks the plate changes with the
line. Pockets and the turn are last.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from PIL import Image

BASE = Path(__file__).resolve().parent.parent
ASSETS = Path("/home/dylanmccapes/.cursor/projects/home-dylanmccapes-dev/assets")
OUT = BASE / "video" / "minus10b"
STILLS = OUT / "stills"
AUDIO = BASE / "audio" / "minus10b" / "minus10b.mp3"
CUES = BASE / "audio" / "minus10b" / "cues.jsonl"
W, H = 1280, 720

PLATES = {
    "fixture": "fixture_gleam.jpg",
    "hall": "hall_indefinite.jpg",
    "speck": "vincent_speck.jpg",
    "far": "vincent_far.jpg",
    "mid": "vincent_mid.jpg",
    "near": "vincent_near.jpg",
    "speaks": "vincent_speaks.jpg",
    "level": "vincent_speak_level.jpg",
    "explain": "vincent_speak_explain.jpg",
    "corner": "vincent_corner.jpg",
}
# Talk plates share a rank so they can replace each other.
# Everything else only moves forward.
RANK = {
    "fixture": 0,
    "hall": 1,
    "speck": 2,
    "far": 3,
    "mid": 4,
    "near": 5,
    "speaks": 6,
    "level": 6,
    "explain": 6,
    "corner": 7,
}


def ensure() -> None:
    STILLS.mkdir(parents=True, exist_ok=True)
    for name in PLATES.values():
        src = ASSETS / name
        dest = STILLS / name
        if src.exists() and (not dest.exists() or dest.stat().st_size == 0):
            dest.write_bytes(src.read_bytes())


def fit(name: str) -> Path:
    src = STILLS / PLATES[name]
    dest = STILLS / f"{name}.png"
    im = Image.open(src).convert("RGB")
    im = im.resize((W, H), Image.Resampling.LANCZOS)
    im.save(dest)
    return dest


def plate_for(text: str, speaker: str, current: str) -> str:
    low = text.lower()
    want = current
    if "indefinitely" in low or "both directions" in low:
        want = "hall"
    if "there is a figure at the vanishing point" in low or "very far away or very small" in low:
        want = "speck"
    if "the frame is not" in low or "frame is invariant" in low:
        want = "far"
    if "he is from a different phase" in low or "imaginary number" in low:
        want = "mid"
    if "not all at once" in low or "by being here" in low or "one suit" in low or "the suit is good" in low:
        want = "near"
    if "speaks to the framing" in low or "close enough" in low:
        want = "speaks"
    if speaker == "Vincent":
        if "somewhere specific" in low:
            want = "corner"
        elif "gleam is what you use" in low or "choice" in low:
            want = "explain"
        elif "you told me" in low or "not a criticism" in low:
            want = "level"
        else:
            want = "speaks"
    if "jacket pockets" in low or "turns toward" in low or "a corner has" in low:
        want = "corner"
    if RANK[want] < RANK[current]:
        return current
    return want


def cue_scale(cues: list[dict]) -> float:
    """Same clock as −08: cue ends sum the clips; the stitched file is shorter."""
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


def main() -> None:
    ensure()
    for name in PLATES:
        fit(name)
    cues = [json.loads(l) for l in CUES.read_text().splitlines() if l.strip()]
    scale = cue_scale(cues)
    print(f"Cue clock {cues[-1]['end']:.2f}s  scale {scale:.6f}")
    current = "fixture"
    concat = ["ffconcat version 1.0"]
    last = ""
    shown = []
    for cue in cues:
        current = plate_for(cue.get("text", ""), cue.get("speaker", ""), current)
        rel = f"stills/{current}.png"
        dur = max(0.04, (float(cue["end"]) - float(cue["start"])) / scale)
        concat.append(f"file '{rel}'")
        concat.append(f"duration {dur:.4f}")
        last = rel
        if not shown or shown[-1] != current:
            shown.append(current)
            print(f"  {cue['start']:7.1f}s  {current}")
    concat.append(f"file '{last}'")
    (OUT / "concat.txt").write_text("\n".join(concat) + "\n")
    mp4 = OUT / "-10b_the_frame_material.mp4"
    subprocess.run(
        [
            "ffmpeg", "-y",
            "-f", "concat", "-safe", "0", "-i", "concat.txt",
            "-i", str(AUDIO),
            "-fps_mode", "vfr",
            "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "20", "-bf", "0",
            "-c:a", "aac", "-b:a", "192k",
            "-shortest", "-movflags", "+faststart",
            str(mp4),
        ],
        check=True,
        cwd=str(OUT),
    )
    print(f"Output: {mp4}  ({mp4.stat().st_size // (1024 * 1024)}MB)")


if __name__ == "__main__":
    main()
