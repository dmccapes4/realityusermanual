#!/usr/bin/env python3
"""
build_prompt_walk_video.py

Assembles the Prompt Walk radio broadcast video.

Cast:      Cecil (mFxwGQHOfdvvPAYlbCXN) · Narrator (onwK4e9ZLuTAKqWW03F9) · Sauron (y83sBjIAA8cOKB2nYkOQ)
Source:    REALITY_USER_MANUAL/prompt_walk_page_builder/episodes/episode_NN.json
           REALITY_USER_MANUAL/prompt_walk_page_builder/episodes/which_NN.json
Images:    prompt_walk_page_builder/images/  (screenshots)
           prompt_walk_page_builder/episodes/crops/  (palantir crops)
           star_learning/solar_system_explorer/docs/THEBES_MARS_M44_2400BC/ (Mars intro)
Output:    REALITY_USER_MANUAL/video/minus28/prompt_walk_witch_of_rivers.mp4
Work dir:  REALITY_USER_MANUAL/video/minus28/

Usage:
  .venv/bin/python tools/build_prompt_walk_video.py
  .venv/bin/python tools/build_prompt_walk_video.py --episodes 1,2,3  (subset)
  .venv/bin/python tools/build_prompt_walk_video.py --no-which        (skip which sections)
  .venv/bin/python tools/build_prompt_walk_video.py --dry-run         (audio only, no ffmpeg)
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

BASE   = Path(__file__).resolve().parent.parent           # REALITY_USER_MANUAL/
PW     = BASE / "prompt_walk_page_builder"
EP_DIR = PW / "episodes"
IMG    = PW / "images"
CROPS  = EP_DIR / "crops"
MARS   = BASE.parent / "star_learning" / "solar_system_explorer" / "docs" / "THEBES_MARS_M44_2400BC"

WORK   = BASE / "video" / "minus28"
AUDIO  = WORK / "audio"
FRAMES = WORK / "frames"
OUT    = BASE / "video" / "pages"

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

# ── Voice IDs ──────────────────────────────────────────────────────────────────
V = {
    "CECIL":    "mFxwGQHOfdvvPAYlbCXN",
    "NARRATOR": "onwK4e9ZLuTAKqWW03F9",
    "SAURON":   "y83sBjIAA8cOKB2nYkOQ",
}

# ── Output resolution (match existing videos) ──────────────────────────────────
W, H = 1920, 1080

# ── Title card text ────────────────────────────────────────────────────────────
TITLE_TEXT = (
    "Night Vale Community Radio. Prompt Walk. "
    "The Witch of the Rivers Is Me. Eight episodes, one correction."
)

# ── Intro (Cecil cold open over the Mars retrograde image) ────────────────────
INTRO_LINES = [
    ("NARRATOR", "Thebes. October 31, approximately 2554 BCE. Mars transits the Flower at one point three degrees. Altitude eighty-seven point two degrees. The Witch of the Rivers did not tilt her head. The sky came straight down to her."),
    ("NARRATOR", "Mars retrograde track through M44. The red path. The Flower behind it. The tower watching."),
    ("CECIL",    "Good evening, Night Vale. The eye is open. The palantir is warm. Tonight we walk a prompt."),
    ("NARRATOR", "Eight screenshots. One file. The operator did not stop writing."),
    ("SAURON",   "Nine episodes. The ninth is the rule. The rule was unenforced. It is enforced now."),
]

def speak(speaker: str, text: str, dest: Path) -> tuple[Path, float]:
    """Generate audio for one line. Returns (path, duration_seconds)."""
    dest.parent.mkdir(parents=True, exist_ok=True)
    voice_id = V.get(speaker.upper(), V["NARRATOR"])
    paths = ga.tts(speaker, text, voice_id)
    if not paths:
        raise RuntimeError(f"ElevenLabs returned no audio for: {speaker} / {text[:60]}")
    ga.concatenate(paths, dest)
    return dest, ffprobe_dur(dest)

def prepare_frame(src: Path, dest: Path) -> Path:
    """Scale image to 1920×1080, pad with black, save PNG."""
    dest.parent.mkdir(parents=True, exist_ok=True)
    if not src.exists():
        # Solid black fallback
        subprocess.run([
            "ffmpeg", "-y", "-f", "lavfi", "-i", f"color=black:s={W}x{H}",
            "-frames:v", "1", str(dest)
        ], capture_output=True)
        return dest
    subprocess.run([
        "ffmpeg", "-y", "-i", str(src),
        "-vf", f"scale={W}:{H}:force_original_aspect_ratio=decrease,pad={W}:{H}:(ow-iw)/2:(oh-ih)/2:black",
        "-frames:v", "1", str(dest)
    ], capture_output=True, check=True)
    return dest

def load_ep(n: int) -> dict:
    p = EP_DIR / f"episode_{n:02d}.json"
    return json.loads(p.read_text()) if p.exists() else {}

def load_which(n: int) -> dict:
    p = EP_DIR / f"which_{n:02d}.json"
    return json.loads(p.read_text()) if p.exists() else {}

def crop_path(ep: int, panel: str, third: str) -> Path:
    """Return path to Sauron's palantir crop."""
    return CROPS / f"ep{ep:02d}_{panel}_{third}.png"

def screenshot(ep: int, variant: str = "") -> Path:
    """Return path to the episode screenshot."""
    if ep == 9:
        fn = f"09{'b' if variant == 'after' else 'a'}_rule_{'always' if variant == 'after' else 'apply'}_{'apply' if variant == 'after' else 'manually'}.png"
        return IMG / fn
    return IMG / f"{ep:02d}_prompt_walk.png"

def build_segment(ep_n: int, ep_data: dict, which_data: dict,
                  no_which: bool) -> list[tuple[Path, Path, float]]:
    """Returns list of (frame_path, audio_path, duration)."""
    """
    For one episode, generate all audio and return a list of (frame_path, duration) pairs.
    Frame is the image to show while the audio plays.
    """
    pairs: list[tuple[Path, Path, float]] = []

    def add_lines(lines: list[dict], frame: Path) -> None:
        for i, ln in enumerate(lines):
            sp   = ln.get("speaker", "NARRATOR").upper()
            text = ln.get("line", "").strip()
            if not text:
                continue
            slug = f"ep{ep_n:02d}_{frame.stem}_{i:02d}"
            audio_dest = AUDIO / f"{slug}.mp3"
            apath, dur = speak(sp, text, audio_dest)
            pairs.append((frame, apath, max(1.0, dur)))
            print(f"    {sp[:3]}  {dur:.1f}s  {text[:55]}{'…' if len(text)>55 else ''}")

    ss = screenshot(ep_n)
    ss_frame = prepare_frame(ss, FRAMES / f"ep{ep_n:02d}_full.png")

    # Opening
    print(f"  [ep{ep_n:02d}] opening", flush=True)
    add_lines(ep_data.get("opening", []), ss_frame)

    # File view (directory)
    print(f"  [ep{ep_n:02d}] file view", flush=True)
    for beat in ep_data.get("file_view", []):
        third = beat.get("crop", "top")
        c = crop_path(ep_n, "directory", third)
        frame = prepare_frame(c if c.exists() else ss, FRAMES / f"ep{ep_n:02d}_dir_{third}.png")
        add_lines(beat.get("lines", []), frame)

    # Text view (editor)
    print(f"  [ep{ep_n:02d}] text view", flush=True)
    for beat in ep_data.get("text_view", []):
        third = beat.get("crop", "top")
        c = crop_path(ep_n, "editor", third)
        frame = prepare_frame(c if c.exists() else ss, FRAMES / f"ep{ep_n:02d}_ed_{third}.png")
        add_lines(beat.get("lines", []), frame)

    # Chat view (skip for ep09 which has no chat)
    if ep_data.get("chat_view"):
        print(f"  [ep{ep_n:02d}] chat view", flush=True)
        for beat in ep_data.get("chat_view", []):
            crop_type = beat.get("crop", "full")
            c = crop_path(ep_n, "chat", crop_type)
            frame = prepare_frame(c if c.exists() else ss, FRAMES / f"ep{ep_n:02d}_chat_{crop_type}.png")
            add_lines(beat.get("lines", []), frame)

    # Which / witch section
    if not no_which and which_data:
        print(f"  [ep{ep_n:02d}] which section ({which_data.get('form','?')})", flush=True)
        which_frame = prepare_frame(ss, FRAMES / f"ep{ep_n:02d}_which.png")
        # Debate
        add_lines(which_data.get("debate", []), which_frame)
        # Main section
        add_lines(which_data.get("section", []), which_frame)
        # Grade rationale (deliverer reads it)
        deliverer = which_data.get("deliverer", "NARRATOR").upper()
        gr = which_data.get("grade_rationale", "").strip()
        if gr:
            audio_dest = AUDIO / f"ep{ep_n:02d}_which_grade.mp3"
            apath, dur = speak(deliverer, gr, audio_dest)
            pairs.append((which_frame, apath, max(1.0, dur)))
        # Sauron tally
        tally = which_data.get("sauron_tally", "").strip()
        if tally:
            audio_dest = AUDIO / f"ep{ep_n:02d}_which_tally.mp3"
            apath, dur = speak("SAURON", tally, audio_dest)
            pairs.append((which_frame, apath, max(1.0, dur)))

    # For ep09 which section: use the "after" screenshot
    if ep_n == 9 and which_data:
        after_frame = prepare_frame(screenshot(9, "after"),
                                    FRAMES / "ep09_after.png")
        add_lines(which_data.get("section", []), after_frame)

    return pairs

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--episodes", default="", help="Comma-separated episode numbers, e.g. 1,2,3")
    ap.add_argument("--no-which", action="store_true")
    ap.add_argument("--dry-run", action="store_true", help="Generate audio but skip ffmpeg")
    args = ap.parse_args()

    ep_list = [int(x) for x in args.episodes.split(",") if x.strip()] if args.episodes else list(range(1, 10))

    for d in (WORK, AUDIO, FRAMES, OUT):
        d.mkdir(parents=True, exist_ok=True)

    all_pairs: list[tuple[Path, Path, float]] = []

    # ── Title card ────────────────────────────────────────────────────────────
    print("title card", flush=True)
    title_img = FRAMES / "title.png"
    title_card("PROMPT WALK", title_img, "the witch of the rivers is me")
    title_mp3, title_dur = speak("NARRATOR", TITLE_TEXT, AUDIO / "title.mp3")
    all_pairs.append((title_img, title_mp3, max(4.0, title_dur)))

    # ── Mars intro ────────────────────────────────────────────────────────────
    print("Mars intro", flush=True)
    mars_sky = MARS / "sky_view_thebes_mars_m44.png"
    mars_trk = MARS / "mars_retrograde_track_thebes_2400bc.png"
    sky_frame = prepare_frame(mars_sky, FRAMES / "mars_sky.png")
    trk_frame = prepare_frame(mars_trk, FRAMES / "mars_trk.png")

    # First two intro lines go over sky, next three over track
    intro_imgs = [sky_frame, sky_frame, trk_frame, trk_frame, trk_frame]
    for i, (sp, text) in enumerate(INTRO_LINES):
        audio_dest = AUDIO / f"intro_{i:02d}.mp3"
        apath, dur = speak(sp, text, audio_dest)
        frame = intro_imgs[i] if i < len(intro_imgs) else trk_frame
        all_pairs.append((frame, apath, max(2.0, dur)))

    # ── Episodes ──────────────────────────────────────────────────────────────
    for ep_n in ep_list:
        print(f"\n── Episode {ep_n:02d} ──────────────────", flush=True)
        ep_data    = load_ep(ep_n)
        which_data = load_which(ep_n)
        pairs = build_segment(ep_n, ep_data, which_data, args.no_which)
        all_pairs.extend(pairs)

    if args.dry_run:
        total = sum(d for _, _, d in all_pairs)
        print(f"\ndry-run: {len(all_pairs)} clips, {total:.0f}s (~{total/60:.1f} min)")
        return

    # ── ffmpeg concat ─────────────────────────────────────────────────────────
    print("\nassembling video …", flush=True)

    concat: list[str] = []
    all_mp3s: list[Path] = []
    for frame, mp3, _ in all_pairs:
        dur = ffprobe_dur(mp3)
        concat += [f"file '{frame.resolve()}'", f"duration {max(1.0, dur):.3f}"]
        all_mp3s.append(mp3)
    concat.append(f"file '{all_pairs[-1][0].resolve()}'")

    list_path = WORK / "concat.txt"
    list_path.write_text("\n".join(concat) + "\n")

    mix_path = WORK / "prompt_walk_mix.mp3"
    ga.concatenate(all_mp3s, mix_path)

    dest = OUT / "prompt_walk_witch_of_rivers.mp4"
    subprocess.run([
        "ffmpeg", "-y",
        "-f", "concat", "-safe", "0", "-i", str(list_path),
        "-i", str(mix_path),
        "-c:v", "libx264", "-preset", "slow", "-crf", "18",
        "-tune", "stillimage", "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "192k",
        "-map", "0:v", "-map", "1:a",
        "-shortest",
        str(dest),
    ], check=True)

    total = sum(ffprobe_dur(m) for m in all_mp3s)
    print(f"\n✓  {dest}")
    print(f"   {total:.0f}s ({total/60:.1f} min)")

if __name__ == "__main__":
    main()
