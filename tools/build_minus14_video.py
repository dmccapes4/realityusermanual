#!/usr/bin/env python3
"""
La Jetée photo-roman of src/07k_ted_ross_sheldon_goines_scene.md only.

Dialog as written. Images are 1962 still photographs, not the ink book.
One moving shot at the end: the Eye opening.

  .venv/bin/python tools/build_minus14_video.py parse
  .venv/bin/python tools/build_minus14_video.py stills --render
  .venv/bin/python tools/build_minus14_video.py audio
  .venv/bin/python tools/build_minus14_video.py assemble
  .venv/bin/python tools/build_minus14_video.py all
"""

from __future__ import annotations

import argparse
import base64
import json
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
SRC = BASE / "src" / "07k_ted_ross_sheldon_goines_scene.md"
LJ = BASE / "video" / "minus14"
SHOTS = LJ / "shots.jsonl"
STILLS = LJ / "stills"
AUDIO_DIR = BASE / "audio" / "minus14"
OUT = LJ / "out"
SEG_DIR = AUDIO_DIR / "segments"

_env = BASE / ".env"
if _env.exists():
    for line in _env.read_text().splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, _, v = line.partition("=")
            os.environ.setdefault(k.strip(), v.strip())

sys.path.insert(0, str(BASE / "tools"))

PHOTO_PREFIX = """1962 black-and-white still photograph. Photo-roman. Silver gelatin grain.
High contrast. Slightly soft edges. No color. No digital smoothness.
No comic ink. No cinematic color grade. A single held photograph.
Available light. 3:2 frame.
"""

KNOWN = {"Ted", "Ross", "Sheldon", "Goines"}


def voice_name(speaker: str) -> str:
    """07k italic and spoken Goines are the haunt, not Jeffrey."""
    return "GoinesFeynman" if speaker == "Goines" else speaker

BLOCK_STILLS = {
    "1": ["room_from_door", "wall_sign", "painted_window", "table_inlaid",
          "ted_drawing", "ross_couch", "tooth", "sheldon_door", "drive_squared"],
    "2": ["sheldon_ticks", "chi_bracket", "ted_listen", "ross_page"],
    "3": ["ted_rectangles", "ted_couch", "table_inlaid"],
    "4": ["ross_looks_up", "ross_paper", "two_fragments"],
    "5": ["tv_east", "long_hair", "airport_tv"],
    "5b": ["ross_looks_up", "sallier_gap", "tv_east"],
    "5c": ["dictionary", "crescent"],
    "5d": ["thomkun", "sheldon_across"],
    "5e": ["painted_window", "crescent", "table_inlaid"],
    "6": ["napkin_drive", "drive_port", "room_still", "empty_air"],
    "7": ["sheldon_across", "empty_air"],
    "8": ["giraffe", "bridge", "ted_listen"],
    "9": ["ross_paper", "welded_window"],
    "10": ["anklet", "pen_coil"],
    "11": ["tce", "chi_bracket"],
    "12": ["ted_form", "ted_drawing"],
    "13": ["board_full", "hand_table"],
    "14": ["swords", "painted_window", "room_from_door"],
}

BLUEPRINT = LJ / "blueprint"

KEYWORD_STILL = (
    (re.compile(r"Dukas|Ellner|foraging animals", re.I), "ross_dukas"),
    (re.compile(r"Bundesen|theory of visual attention|\bTVA\b", re.I), "ross_bundesen"),
    (re.compile(r"Tversky|Features of Similarity", re.I), "ross_tversky"),
    (re.compile(r"Luce", re.I), "ross_luce"),
    (re.compile(r"\bsoftmax\b|sum to one|the capacity|a budget", re.I), "sheldon_softmax"),
    (re.compile(r"1/t|one over t|half-life|t sub one-half|t_\{1/2\}|width cancel", re.I), "sheldon_halflife"),
    (re.compile(r"\bchi\b|χ|brackets a run", re.I), "chi_bracket"),
    (re.compile(r"leave the tape|past N|marks a cut", re.I), "sheldon_cut"),
    (re.compile(r"bar of the fraction|the bar comes out", re.I), "sheldon_fraction"),
    (re.compile(r"nested rectangles|arrow moved|arrow was not the problem", re.I), "ted_rectangles"),
    (re.compile(r"rectangle around|narrow line|needs an address|same material as the room", re.I), "ted_deed"),
    (re.compile(r"ticks it at even marks|writes finite|\bfinite\b", re.I), "sheldon_ticks"),
    (re.compile(r"\bgiraffe\b", re.I), "giraffe"),
    (re.compile(r"You got them out"), "giraffe"),
    (re.compile(r"\bThomkun\b|THOMKUN"), "thomkun"),
    (re.compile(r"\bSallier\b"), "sallier_gap"),
    (re.compile(r"La Jetée|observation (deck|jetty)|Orly"), "airport_tv"),
    (re.compile(r"painted shut|paint is newer"), "painted_window"),
    (re.compile(r"barcode|anklet|Wheatstone|galvanometer"), "anklet"),
    (re.compile(r"Put your hand|hand on the table|You didn't touch"), "hand_table"),
    (re.compile(r"welded"), "welded_window"),
    (re.compile(r"TOKENIZED CONTINUED|TCE\b"), "tce"),
    (re.compile(r"pushes the drive|inserts the drive"), "drive_port"),
    (re.compile(r"FOR USE DURING|swordplay|Swords on the wall|crossed swords"), "wall_sign"),
    (re.compile(r"napkin"), "napkin_drive"),
    (re.compile(r"fossil|femur|two fragments"), "two_fragments"),
    (re.compile(r"long hair"), "long_hair"),
    (re.compile(r"crescent|monkey on the moon"), "crescent"),
)


def load_shots() -> list[dict]:
    return [json.loads(l) for l in SHOTS.read_text().splitlines() if l.strip()]


def clean_text(t: str) -> str:
    t = re.sub(r"\*\*([^*]+)\*\*", r"\1", t)
    t = re.sub(r"\*([^*]+)\*", r"\1", t)
    t = re.sub(r"`([^`]+)`", r"\1", t)
    t = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", t)
    t = t.replace("−", "minus ")
    t = re.sub(r"  +", " ", t)
    return t.strip()


def parse_07k(path: Path = SRC) -> list[dict]:
    """Dialog as written. Italics and unmarked prose → Goines. **Name:** → that speaker."""
    raw = path.read_text(encoding="utf-8")
    lines = raw.splitlines()
    segs: list[dict] = []
    block = "1"
    started = False
    buf: list[str] = []

    def flush():
        nonlocal buf
        if not buf:
            return
        para = " ".join(x.strip() for x in buf if x.strip()).strip()
        buf = []
        if not para or not started:
            return
        if re.match(r"^[-*_]{3,}$", para):
            return
        if para.startswith(">"):
            return
        if re.match(r"^[A-Z][A-Z0-9 \-]{2,40}$", para):
            return
        m = re.match(r"^\*\*([^*]+):\*\*\s*(.*)$", para)
        if m and m.group(1).strip() in KNOWN:
            text = clean_text(m.group(2))
            if text:
                segs.append({"speaker": m.group(1).strip(), "text": text, "block": block})
            return
        if para.startswith("#"):
            return
        text = clean_text(para)
        if text:
            segs.append({"speaker": "Goines", "text": text, "block": block})

    for line in lines:
        m = re.search(r"v1 BLOCK ([0-9]+[a-z]?)", line)
        if m:
            flush()
            block = m.group(1)
            continue
        if line.strip() == "---":
            flush()
            started = True
            continue
        if not started:
            continue
        if re.match(r"^<!--", line.strip()):
            continue
        if not line.strip():
            flush()
            continue
        buf.append(line)
    flush()
    return segs


def still_for(seg: dict, index_in_block: int) -> str:
    text = seg["text"]
    for rx, sid in KEYWORD_STILL:
        if rx.search(text):
            return sid
    pool = BLOCK_STILLS.get(seg["block"], ["room_from_door"])
    return pool[index_in_block % len(pool)]


def cmd_parse(_args):
    segs = parse_07k()
    counts: dict[str, int] = {}
    chars: dict[str, int] = {}
    for s in segs:
        counts[s["speaker"]] = counts.get(s["speaker"], 0) + 1
        chars[s["speaker"]] = chars.get(s["speaker"], 0) + len(s["text"])
    total = sum(chars.values())
    print(f"segments {len(segs)}  spoken chars {total}")
    for name in sorted(chars, key=chars.get, reverse=True):
        print(f"  {name:<10} {counts[name]:4d} segs  {chars[name]:6d} chars")
    AUDIO_DIR.mkdir(parents=True, exist_ok=True)
    (AUDIO_DIR / "segments.jsonl").write_text(
        "".join(json.dumps(s, ensure_ascii=False) + "\n" for s in segs)
    )
    print(f"wrote {AUDIO_DIR / 'segments.jsonl'}")


def render_still(row: dict, force: bool = False) -> Path | None:
    dest = BASE / row["file"]
    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.exists() and dest.stat().st_size > 1000 and not force:
        print(f"  [skip] {row['id']}", flush=True)
        return dest
    key = os.environ.get("OPENAI_API_KEY", "").strip()
    if not key:
        sys.exit("Set OPENAI_API_KEY in .env")
    import requests
    payload = {
        "model": "gpt-image-1.5",
        "prompt": PHOTO_PREFIX + "\n" + row["prompt"],
        "size": "1536x1024",
        "background": "opaque",
        "quality": "high",
        "output_format": "png",
        "n": 1,
    }
    dest.with_suffix(".request.json").write_text(json.dumps(payload, indent=2) + "\n")
    r = requests.post(
        "https://api.openai.com/v1/images/generations",
        headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
        json=payload,
        timeout=180,
    )
    if r.status_code != 200:
        print(f"  [fail] {row['id']}: {r.status_code} {r.text[:300]}", flush=True)
        return None
    b64 = r.json()["data"][0].get("b64_json")
    if not b64:
        print(f"  [fail] {row['id']}: no image", flush=True)
        return None
    dest.write_bytes(base64.b64decode(b64))
    print(f"  [ok] {row['id']}  {dest.stat().st_size} bytes", flush=True)
    if row["id"] == "wall_sign":
        dest.with_name("wall_sign_blank.png").write_bytes(dest.read_bytes())
        print(f"  [blank] {dest.with_name('wall_sign_blank.png')}", flush=True)
    return dest


SIGN_TITLE = "FOR USE DURING CODE COMPILATION ONLY"
SIGN_BODY_WORDS = (
    "The imaginary science community suggests avoiding interpreted languages and running "
    "computationally intensive simulations on CPU without core threading if increased "
    "access to swordplay is desired or required"
)
SIGN_NARROW_BOLD = "/usr/share/fonts/truetype/liberation/LiberationSansNarrow-Bold.ttf"
SIGN_NARROW = "/usr/share/fonts/truetype/liberation/LiberationSansNarrow-Regular.ttf"


def _wrap_words(text: str, font, draw, max_w: int) -> list[str]:
    words = text.split()
    lines: list[str] = []
    cur = ""
    for word in words:
        trial = f"{cur} {word}".strip()
        bb = draw.textbbox((0, 0), trial, font=font)
        if bb[2] - bb[0] <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def _fit_font(path: str, text: str, draw, max_w: int, lo: int, hi: int):
    from PIL import ImageFont
    best = ImageFont.truetype(path, lo)
    for size in range(hi, lo - 1, -1):
        face = ImageFont.truetype(path, size)
        bb = draw.textbbox((0, 0), text, font=face)
        if bb[2] - bb[0] <= max_w:
            return face
        best = face
    return best


def stamp_wall_sign(path: Path | None = None, box: tuple[int, int, int, int] | None = None) -> Path:
    """Exact 07k advisory painted on the plaster. No plaque. Grain stays in the paint."""
    from PIL import Image, ImageDraw, ImageFont, ImageFilter

    dest = path or (STILLS / "wall_sign.png")
    blank = dest.with_name("wall_sign_blank.png")
    src = blank if blank.exists() else dest
    wall = Image.open(src).convert("RGB")
    w, h = wall.size
    if box is None:
        # Below the blade tips (~480), above the couch (~800). Measured on blank.
        box = (int(w * 0.06), 512, int(w * 0.94), 768)
    x0, y0, x1, y1 = box
    max_w = x1 - x0
    wrap_w = int(max_w * 0.78)
    mask = Image.new("L", (w, h), 0)
    dr = ImageDraw.Draw(mask)
    title_lines = ["FOR USE DURING", "CODE COMPILATION ONLY"]
    title_f = _fit_font(SIGN_NARROW_BOLD, title_lines[1], dr, wrap_w, 28, 52)
    body_f = ImageFont.truetype(SIGN_NARROW_BOLD, 24)
    body_lines = _wrap_words(SIGN_BODY_WORDS, body_f, dr, wrap_w)
    for size in range(28, 18, -1):
        cand = ImageFont.truetype(SIGN_NARROW_BOLD, size)
        lines = _wrap_words(SIGN_BODY_WORDS, cand, dr, wrap_w)
        if 4 <= len(lines) <= 6:
            body_f = cand
            body_lines = lines
            break

    def paint_line(text, font, y):
        bb = dr.textbbox((0, 0), text, font=font)
        tw = bb[2] - bb[0]
        x = x0 + (max_w - tw) // 2
        dr.text((x, y), text, font=font, fill=255)
        return (bb[3] - bb[1])

    y = y0
    for tline in title_lines:
        y += paint_line(tline, title_f, y) + 4
    y += 6
    rule_y = y
    dr.line((x0 + int(max_w * 0.12), rule_y, x1 - int(max_w * 0.12), rule_y), fill=255, width=4)
    y += 14
    for line in body_lines:
        y += paint_line(line, body_f, y) + 6

    # Acrylic: dark paint, plaster tooth still in the stroke. Soft edge, not vinyl.
    mask = mask.filter(ImageFilter.GaussianBlur(radius=0.55))
    wall_l = wall.convert("L")
    painted = Image.eval(wall_l, lambda p: int(p * 0.18))
    out = Image.composite(painted.convert("RGB"), wall, mask)
    out.save(dest)
    print(f"  [stamp] wall_sign acrylic on plaster  {dest.stat().st_size}", flush=True)
    return dest


def cmd_stills(args):
    rows = load_shots()
    if args.only:
        want = {s.strip() for s in args.only.split(",")}
        rows = [r for r in rows if r["id"] in want]
    print(f"{'RENDER' if args.render else 'DRY'}  {len(rows)} stills")
    for row in rows:
        if args.render:
            render_still(row, force=args.force)
        else:
            print(f"  [dry] {row['id']} → {row['file']}")


def cmd_audio(_args):
    import generate_audio as ga
    segs = parse_07k()
    SEG_DIR.mkdir(parents=True, exist_ok=True)
    files: list[Path] = []
    for s in segs:
        name = voice_name(s["speaker"])
        vid = ga.VOICE_MAP.get(name)
        if not vid:
            print(f"  [SKIP] no voice for {name}")
            continue
        paths = ga.tts(name, s["text"], vid)
        files.extend(paths)
    if not files:
        sys.exit("no audio segments")
    out = AUDIO_DIR / "07k_reading.mp3"
    AUDIO_DIR.mkdir(parents=True, exist_ok=True)
    ga.concatenate(files, out)
    (AUDIO_DIR / "files.json").write_text(
        json.dumps([p.name for p in files], indent=2) + "\n"
    )
    print(f"audio files {len(files)}")


def ffprobe_dur(path: Path) -> float:
    r = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1", str(path)],
        capture_output=True, text=True,
    )
    try:
        return float(r.stdout.strip())
    except ValueError:
        return 0.0


def grain(im):
    from PIL import Image, ImageEnhance, ImageFilter
    import random
    g = im.convert("L")
    px = g.load()
    w, h = g.size
    rng = random.Random(1962)
    for y in range(0, h, 2):
        for x in range(0, w, 2):
            n = rng.randint(-18, 18)
            v = max(0, min(255, px[x, y] + n))
            px[x, y] = v
            if x + 1 < w:
                px[x + 1, y] = v
            if y + 1 < h:
                px[x, y + 1] = v
    g = ImageEnhance.Contrast(g).enhance(1.18)
    g = g.filter(ImageFilter.UnsharpMask(radius=0.6, percent=40, threshold=3))
    return g.convert("RGB")


def title_card(text: str, dest: Path, sub: str = ""):
    from PIL import Image, ImageDraw, ImageFont
    W, H = 1280, 720
    im = Image.new("RGB", (W, H), (0, 0, 0))
    dr = ImageDraw.Draw(im)
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf", 36)
        small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf", 18)
    except OSError:
        font = ImageFont.load_default()
        small = font
    bbox = dr.textbbox((0, 0), text, font=font)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    dr.text(((W - tw) / 2, (H - th) / 2 - 20), text, fill=(220, 220, 210), font=font)
    if sub:
        sb = dr.textbbox((0, 0), sub, font=small)
        sw = sb[2] - sb[0]
        dr.text(((W - sw) / 2, (H - th) / 2 + 40), sub, fill=(160, 160, 150), font=small)
    dest.parent.mkdir(parents=True, exist_ok=True)
    im.save(dest)
    return dest


def still_src(sid: str) -> Path | None:
    """Blueprint math and citation papers win over the photo-roman plate."""
    for d in (BLUEPRINT, STILLS):
        p = d / f"{sid}.png"
        if p.exists() and p.stat().st_size > 1000:
            return p
    return None


def anim_frames(sid: str) -> list[Path]:
    d = BLUEPRINT / "anim" / sid
    if d.is_dir():
        frames = sorted(p for p in d.glob("*.png") if p.stat().st_size > 1000)
        if frames:
            return frames
    src = still_src(sid)
    return [src] if src else []


def place_still(src: Path, dest: Path, *, apply_grain: bool | None = None):
    from PIL import Image
    W, H = 1280, 720
    canvas = Image.new("RGB", (W, H), (0, 0, 0))
    raw = Image.open(src).convert("RGB")
    technical = "blueprint" in Path(src).resolve().parts
    if apply_grain is None:
        apply_grain = not technical
    im = grain(raw) if apply_grain else raw
    if technical:
        im = im.resize((W, H), Image.Resampling.LANCZOS)
        canvas.paste(im, (0, 0))
    else:
        target_h = H
        target_w = int(target_h * 1.5)
        if target_w > W:
            target_w = W
            target_h = int(W / 1.5)
        im = im.resize((target_w, target_h), Image.Resampling.LANCZOS)
        canvas.paste(im, ((W - target_w) // 2, (H - target_h) // 2))
    dest.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(dest)
    return dest


def build_eye_clip(frame_dir: Path) -> Path | None:
    ids = ["eye_closed", "eye_slit", "eye_half", "eye_open"]
    paths = [STILLS / f"{i}.png" for i in ids]
    if not all(p.exists() and p.stat().st_size > 1000 for p in paths):
        print("[eye] stills missing; skip wrench")
        return None
    seq = frame_dir / "eye"
    seq.mkdir(parents=True, exist_ok=True)
    placed = []
    for i, p in enumerate(paths):
        dest = seq / f"{i:02d}.png"
        place_still(p, dest)
        placed.append(dest)
    # hold closed, step through opening, hold open
    list_path = seq / "concat.txt"
    lines = []
    durs = [1.6, 0.35, 0.35, 2.2]
    for p, d in zip(placed, durs):
        lines.append(f"file '{p.resolve()}'")
        lines.append(f"duration {d}")
    lines.append(f"file '{placed[-1].resolve()}'")
    list_path.write_text("\n".join(lines) + "\n")
    dest = OUT / "eye_wrench.mp4"
    cmd = [
        "ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(list_path),
        "filter_complex",
        "[0:v]minterpolate=fps=24:mi_mode=mci:mc_mode=aobmc:me_mode=bidir:vsbmc=1,format=yuv420p[v]",
        "-map", "[v]",
        "-an", "-t", "4.5",
        str(dest),
    ]
    # minterpolate on 4 stills is unreliable; step-cut is more Marker if interp fails
    simple = [
        "ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(list_path),
        "-c:v", "libx264", "-preset", "medium", "-crf", "18",
        "-pix_fmt", "yuv420p", "-r", "24",
        str(dest),
    ]
    r = subprocess.run(simple, capture_output=True, text=True)
    if r.returncode != 0:
        print("[eye] ffmpeg failed:", r.stderr[-400:])
        return None
    print(f"[eye] {dest}")
    return dest


def cmd_assemble(_args):
    from PIL import Image, ImageDraw, ImageFont  # noqa: F401 — title_card imports

    import generate_audio as ga
    segs = parse_07k()
    OUT.mkdir(parents=True, exist_ok=True)
    frames = OUT / "frames"
    frames.mkdir(parents=True, exist_ok=True)

    title_card(
        "TED, ROSS, SHELDON, AND GOINES",
        frames / "t00_title.png",
        "design an LLM",
    )
    title_card("a photo-roman", frames / "t01_form.png")

    # Rebuild audio file list in parse order (hash cache)
    audio_files: list[Path] = []
    cues: list[dict] = []
    t = 0.0
    sign_hang = 16.0
    title_dur = 5.0
    form_dur = 3.0
    t = sign_hang + title_dur + form_dur
    block_i: dict[str, int] = {}
    for s in segs:
        name = voice_name(s["speaker"])
        vid = ga.VOICE_MAP.get(name)
        if not vid:
            continue
        settings = ga.settings_for(name)
        pieces = ga.chunk_text(s["text"])
        for piece in pieces:
            p = ga.hash_path(name, piece, vid, settings)
            if not p.exists() or p.stat().st_size < 1000:
                print(f"  [gap] {s['speaker']}: {piece[:50]}")
                continue
            dur = ffprobe_dur(p)
            if dur <= 0:
                continue
            i = block_i.get(s["block"], 0)
            sid = still_for(s, i)
            block_i[s["block"]] = i + 1
            cues.append({
                "start": t, "end": t + dur,
                "speaker": s["speaker"], "text": piece,
                "still": sid, "block": s["block"],
            })
            audio_files.append(p)
            t += dur

    if not audio_files:
        sys.exit("no cached audio — run audio first")

    # prepend silence so titles play
    silence = AUDIO_DIR / "title_silence.mp3"
    subprocess.run(
        ["ffmpeg", "-y", "-f", "lavfi", "-i", "anullsrc=r=44100:cl=stereo",
         "-t", str(sign_hang + title_dur + form_dur), "-q:a", "9", str(silence)],
        capture_output=True, check=True,
    )
    mix = AUDIO_DIR / "07k_reading.mp3"
    ga.concatenate(audio_files, mix)
    mixed = AUDIO_DIR / "07k_with_titles.mp3"
    ga.concatenate([silence] + audio_files, mixed)

    sign_src = STILLS / "wall_sign.png"
    sign_dest = frames / "t_sign.png"
    if sign_src.exists():
        place_still(sign_src, sign_dest)
    else:
        title_card("wall_sign", sign_dest)
    concat_lines = [
        f"file '{sign_dest.resolve()}'",
        f"duration {sign_hang}",
        f"file '{(frames / 't00_title.png').resolve()}'",
        f"duration {title_dur}",
        f"file '{(frames / 't01_form.png').resolve()}'",
        f"duration {form_dur}",
    ]
    last = None
    n = 0
    placed: dict[str, Path] = {}

    def placed_frame(src: Path, tag: str) -> Path:
        nonlocal n
        key = str(src.resolve())
        if key in placed:
            return placed[key]
        dest = frames / f"s{n:04d}_{tag}.png"
        place_still(src, dest)
        placed[key] = dest
        n += 1
        return dest

    for cue in cues:
        sid = cue["still"]
        seq = anim_frames(sid)
        dur = max(0.04, cue["end"] - cue["start"])
        if not seq:
            dest = frames / "missing.png"
            if dest not in placed.values():
                title_card(sid, dest)
            last = dest
            concat_lines.append(f"file '{last.resolve()}'")
            concat_lines.append(f"duration {dur:.6f}")
            continue
        slice_d = dur / len(seq)
        for i, src in enumerate(seq):
            last = placed_frame(src, f"{sid}_{i:02d}")
            concat_lines.append(f"file '{last.resolve()}'")
            concat_lines.append(f"duration {slice_d:.6f}")
    if last:
        concat_lines.append(f"file '{last.resolve()}'")

    list_path = OUT / "concat.txt"
    list_path.write_text("\n".join(concat_lines) + "\n")
    (LJ / "cues.jsonl").write_text(
        "".join(json.dumps(c, ensure_ascii=False) + "\n" for c in cues)
    )

    body = OUT / "07k_body.mp4"
    cmd = [
        "ffmpeg", "-y",
        "-f", "concat", "-safe", "0", "-i", str(list_path),
        "-i", str(mixed),
        "-c:v", "libx264", "-preset", "medium", "-crf", "20",
        "-tune", "stillimage", "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "192k",
        "-shortest", "-movflags", "+faststart",
        str(body),
    ]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        sys.exit(r.stderr[-1200:] if r.stderr else "ffmpeg body failed")
    print(f"[body] {body}  {body.stat().st_size} bytes")

    eye = build_eye_clip(frames)
    dest = OUT / "-14_ted_ross_sheldon_goines.mp4"
    if eye and eye.exists():
        # append eye with a short black + silent tail
        black = frames / "black.png"
        title_card("", black)
        tail = OUT / "eye_tail.mp4"
        subprocess.run(
            ["ffmpeg", "-y", "-loop", "1", "-i", str(black),
             "-f", "lavfi", "-i", "anullsrc=r=44100:cl=stereo",
             "-t", "2.0", "-c:v", "libx264", "-pix_fmt", "yuv420p",
             "-c:a", "aac", "-shortest", str(tail)],
            capture_output=True, check=True,
        )
        eye_av = OUT / "eye_av.mp4"
        subprocess.run(
            ["ffmpeg", "-y", "-i", str(eye),
             "-f", "lavfi", "-i", "anullsrc=r=44100:cl=stereo",
             "-c:v", "copy", "-c:a", "aac", "-shortest", str(eye_av)],
            capture_output=True, check=True,
        )
        concat = OUT / "final_concat.txt"
        concat.write_text(
            f"file '{body.resolve()}'\nfile '{eye_av.resolve()}'\nfile '{tail.resolve()}'\n"
        )
        r = subprocess.run(
            ["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(concat),
             "-c", "copy", "-movflags", "+faststart", str(dest)],
            capture_output=True, text=True,
        )
        if r.returncode != 0:
            # re-encode if codecs differ
            r = subprocess.run(
                ["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(concat),
                 "-c:v", "libx264", "-crf", "20", "-pix_fmt", "yuv420p",
                 "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart",
                 str(dest)],
                capture_output=True, text=True,
            )
        if r.returncode != 0:
            sys.exit(r.stderr[-800:])
    else:
        body.replace(dest)
    print(f"[ok] {dest}  {dest.stat().st_size} bytes")
    pages = BASE / "video" / "pages"
    pages.mkdir(parents=True, exist_ok=True)
    page = pages / "-14_ted_ross_sheldon_goines.mp4"
    if page.exists() or page.is_symlink():
        page.unlink()
    try:
        page.hardlink_to(dest)
    except OSError:
        import shutil
        shutil.copy2(dest, page)
    print(f"[page] {page}")


def cmd_all(args):
    cmd_parse(args)
    if args.render:
        args.force = getattr(args, "force", False)
        args.only = getattr(args, "only", None)
        cmd_stills(args)
    cmd_audio(args)
    cmd_assemble(args)


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("parse")
    p_st = sub.add_parser("stills")
    p_st.add_argument("--render", action="store_true")
    p_st.add_argument("--force", action="store_true")
    p_st.add_argument("--only")
    sub.add_parser("audio")
    sub.add_parser("assemble")
    p_all = sub.add_parser("all")
    p_all.add_argument("--render", action="store_true")
    args = ap.parse_args()
    {"parse": cmd_parse, "stills": cmd_stills, "audio": cmd_audio,
     "assemble": cmd_assemble, "all": cmd_all}[args.cmd](args)


if __name__ == "__main__":
    main()
