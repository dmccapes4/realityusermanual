#!/usr/bin/env python3
"""Page −27 — The Magi and the Frowning Chair.
Three-pigment stills. GoinesFeynman reads the page (Jeffrey walks −10).
--voice magi waits on the Voice Design ID in REPORT_goines_magi.md.
No personal names.
"""
from __future__ import annotations

import base64
import json
import os
import subprocess
import sys
import argparse
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
SRC = BASE / "src" / "-27_the_magi_and_the_frowning_chair.md"
OUT = BASE / "video" / "minus27"
STILLS = OUT / "stills"
FRAMES = OUT / "frames"
AUDIO = BASE / "audio" / "minus27"
PAGES = BASE / "video" / "minus27"

_env = BASE / ".env"
if _env.exists():
    for line in _env.read_text().splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, _, v = line.partition("=")
            os.environ.setdefault(k.strip(), v.strip())

sys.path.insert(0, str(BASE / "tools"))
import generate_audio as ga
from build_minus14_video import ffprobe_dur, title_card

TEAL = (47, 122, 116)
PALE_YELLOW = (232, 214, 163)
MAGENTA_ROSE = (180, 74, 98)
PALETTE = [
    TEAL, PALE_YELLOW, MAGENTA_ROSE,
    (138, 154, 92),
    (196, 122, 90),
    (106, 90, 110),
    (107, 78, 58),
    (61, 44, 36),
    (28, 22, 20),
    (196, 184, 154),
]

PALETTE_PREFIX = """Limited three-pigment print. ONLY these inks and the browns they mix:
teal #2F7A74, pale yellow #E8D6A3, magenta-rose #B44A62.
Their mixture is brown (reed, quartzite, silt, beer).
No other hues. No photographic full-spectrum grade. No black-and-white.
Flat painted still, paper tooth, like a plate pulled from three stones.
Mars is the magenta-rose of iron in water. The Nile is teal. Light is pale yellow.
No captions. No names. No modern lettering.
"""

WITCH = (
    "A short woman, precise face, epicanthic folds, pale-yellow pigment skin. "
    "A teal mark on the face — not ceremonial paint, a triad mark, hawk. "
    "Simple linen. Magi of the Nile. The Witch of the Rivers. "
    "Not a Halloween witch. No pointed hat. No green skin. "
    "No celebrity likeness. Not a photograph of a known person. No names."
)

NARRATOR_ID = "Nxtvajpo1h6Ok0K5zP4M"
TITLE_TEXT = "Page minus twenty-seven. The Magi and the Frowning Chair."

SHOTS = [
    ("lean_frown", "Quartzite tower interior. Reed chair. " + WITCH + " She leans slightly forward and frowns."),
    ("deeper_frown", "Same reed chair, closer. " + WITCH + " She frowns deeper, hearing herself narrated."),
    ("wooden_block", "Wooden block on a quartzite ledge, yog by yog, hypotenuse burned thaim-or-eth. " + WITCH + " glances at it."),
    ("cackle_nile", "Tower above the Nile. " + WITCH + " head thrown back, cackling. Teal river toward Thebes."),
    ("time_frown", WITCH + " frowns again. Existential. Reed chair behind her. Teal dusk in the window."),
    ("plato_chair", "She sits again in the reed chair that caused the frown. " + WITCH + " One hand on the brown mesh."),
    ("mesh_force", "Close on reed mesh, quartzite chair legs on the tower floor. Force implied. No face."),
    ("cave_three", "Cave at setting sun. Man on a log, man on a too-tall curved stone, woman cross-legged on warm dirt. Not Greece. No celebrity faces."),
    ("seat_not_chair", WITCH + " leaned back against reed mesh. Bamboo at the neck. A seat, not the concept chair."),
    ("thaim_still", "The wooden block closer. Burned thaim-or-eth. A particle at rest. No people."),
    ("mars_eighty", "Looking up eighty degrees. Mars as magenta-rose iron. Teal dusk. The Flower nearby. October. No city lights."),
    ("editor_note", "Empty quartzite ledge. The wooden block. Pale yellow light. No people. The operator's desk is not shown."),
    ("window_cat", WITCH + " at the railing, chest out, face toward Mars, cackling. From the side and slightly down she resembles a cat."),
    ("beer_veil", WITCH + " empties a clay mug in a radial yog. A film of beer. Mars and the Flower. Kata Cydonia."),
    ("sit_smile", WITCH + " sits back in the reed chair, smiling, enjoying the view."),
]


def body_paras() -> list[str]:
    raw = SRC.read_text()
    body = raw.split("---", 1)[1].strip()
    return [p.strip() for p in body.split("\n\n") if p.strip()]


def nearest_palette(im):
    try:
        import numpy as np
        arr = np.asarray(im, dtype=np.int16)
        pal = np.array(PALETTE, dtype=np.int16)
        d = ((arr[:, :, None, :] - pal[None, None, :, :]) ** 2).sum(-1)
        idx = d.argmin(-1)
        out = pal[idx].astype("uint8")
        from PIL import Image
        return Image.fromarray(out, "RGB")
    except ImportError:
        px = im.load()
        w, h = im.size
        for y in range(h):
            for x in range(w):
                r, g, b = px[x, y][:3]
                best, bd = PALETTE[0], 1e9
                for pr, pg, pb in PALETTE:
                    d = (r - pr) ** 2 + (g - pg) ** 2 + (b - pb) ** 2
                    if d < bd:
                        bd, best = d, (pr, pg, pb)
                px[x, y] = best
        return im


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
    dest.with_suffix(".request.json").write_text(
        json.dumps({"id": sid, "prompt": prompt}, indent=2) + "\n"
    )
    r = requests.post(
        "https://api.openai.com/v1/images/generations",
        headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
        json={
            "model": "gpt-image-1.5",
            "prompt": PALETTE_PREFIX + "\n" + prompt,
            "size": "1536x1024",
            "background": "opaque",
            "quality": "high",
            "output_format": "png",
            "n": 1,
        },
        timeout=180,
    )
    if r.status_code != 200:
        sys.exit(f"{sid} failed {r.status_code} {r.text[:400]}")
    dest.write_bytes(base64.b64decode(r.json()["data"][0]["b64_json"]))
    print(f"  [ok] {sid}  {dest.stat().st_size}", flush=True)
    return dest


def place(src: Path, dest: Path) -> Path:
    from PIL import Image
    W, H = 1280, 720
    im = Image.open(src).convert("RGB")
    im = nearest_palette(im).resize((W, H), Image.Resampling.LANCZOS)
    dest.parent.mkdir(parents=True, exist_ok=True)
    im.save(dest)
    return dest


def speak(speaker: str, text: str, voice_id: str, dest: Path) -> tuple[Path, float]:
    dest.parent.mkdir(parents=True, exist_ok=True)
    paths = ga.tts(speaker, text, voice_id)
    if not paths:
        sys.exit(f"no audio for {speaker}")
    ga.concatenate(paths, dest)
    return dest, ffprobe_dur(dest)


VOICES = {
    "feynman": "GoinesFeynman",
    "jeffrey": "Goines",
    "magi": "GoinesMagi",
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--voice",
        choices=sorted(VOICES),
        default="feynman",
        help="feynman = haunt (default). jeffrey = fast Goines. magi = pending ID.",
    )
    args = ap.parse_args()
    speaker = VOICES[args.voice]
    goines_id = ga.VOICE_MAP.get(speaker)
    if not goines_id:
        sys.exit(
            f"{speaker} has no saved ElevenLabs id. "
            "Paste a winner from audio/voice-design/REPORT_goines_magi.md "
            "into VOICE_MAP and voices.jsonl first."
        )

    STILLS.mkdir(parents=True, exist_ok=True)
    FRAMES.mkdir(parents=True, exist_ok=True)
    AUDIO.mkdir(parents=True, exist_ok=True)
    PAGES.mkdir(parents=True, exist_ok=True)

    paras = body_paras()
    if len(paras) != len(SHOTS):
        print(f"[warn] {len(paras)} paras vs {len(SHOTS)} shots", flush=True)
    n = min(len(paras), len(SHOTS))

    print("stills", flush=True)
    for sid, prompt in SHOTS:
        render(sid, prompt)

    print("place", flush=True)
    placed = {sid: place(STILLS / f"{sid}.png", FRAMES / f"{sid}.png") for sid, _ in SHOTS}

    print("title", flush=True)
    ga.VOICE_MAP["The Narrator"] = NARRATOR_ID
    title_mp3, title_dur = speak("The Narrator", TITLE_TEXT, NARRATOR_ID, AUDIO / "title.mp3")
    title_card("PAGE −27", FRAMES / "t00.png", "the magi and the frowning chair")

    print(f"goines {speaker}", flush=True)
    segs = [title_mp3]
    durs = []
    for i in range(n):
        dest = AUDIO / f"p{i:02d}_{args.voice}.mp3"
        _, d = speak(speaker, paras[i], goines_id, dest)
        segs.append(dest)
        durs.append(d)
        print(f"  para {i}  {d:.1f}s  {SHOTS[i][0]}", flush=True)
    mix = AUDIO / f"minus27_{args.voice}.mp3"
    ga.concatenate(segs, mix)

    concat = [f"file '{(FRAMES / 't00.png').resolve()}'", f"duration {max(3.0, title_dur):.3f}"]
    for i in range(n):
        sid = SHOTS[i][0]
        concat += [f"file '{placed[sid].resolve()}'", f"duration {max(1.2, durs[i]):.3f}"]
    concat.append(f"file '{placed[SHOTS[n - 1][0]].resolve()}'")
    list_path = OUT / "concat.txt"
    list_path.write_text("\n".join(concat) + "\n")

    dest = OUT / "minus27_magi.mp4"
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
        sys.exit(r.stderr[-1500:])
    page = PAGES / "-27_the_magi_and_the_frowning_chair.mp4"
    if page.exists() or page.is_symlink():
        page.unlink()
    try:
        page.hardlink_to(dest)
    except OSError:
        import shutil
        shutil.copy2(dest, page)
    print(f"[ok] {dest}  {dest.stat().st_size}", flush=True)
    print(f"[page] {page}", flush=True)


if __name__ == "__main__":
    main()
