#!/usr/bin/env python3
"""TUROV dual construction-site signs on pit/excavator background.

  .venv/bin/python tools/compose_turov_sign.py --render   # gen blanks + compose
  .venv/bin/python tools/compose_turov_sign.py              # compose only

Writes video/minus09/stills/sign_blank_template.png (render)
      video/minus09/stills/site_pit_excavator.png (render)
      video/minus09/stills/turov_sign_scene.png (compose)
"""
from __future__ import annotations

import argparse
import base64
import os
import re
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

BASE = Path(__file__).resolve().parent.parent
SRC = BASE / "src" / "phase2" / "-09.md"
STILLS = BASE / "video" / "minus09" / "stills"

FRAME_W, FRAME_H = 1280, 720
SIGN_H = 620
SIGN_W = 540
GAP = 36
SIGN_Y = 42
SIGN_X_LEFT = 48
SIGN_X_RIGHT = SIGN_X_LEFT + SIGN_W + GAP

# Inner face insets as fraction of trimmed sign plate (inside metal, not outer white mat)
FACE_INSET_X = 0.20
FACE_INSET_Y_TOP = 0.145
FACE_INSET_Y_BOTTOM = 0.11
TRIM_WHITE = 246

_env = BASE / ".env"
if _env.exists():
    for _l in _env.read_text().splitlines():
        _l = _l.strip()
        if _l and not _l.startswith("#") and "=" in _l:
            k, _, v = _l.partition("=")
            os.environ.setdefault(k.strip(), v.strip())

BLANK_PROMPT = (
    "Photorealistic empty construction job-site safety bulletin board sign template. "
    "Tall portrait orientation. OSHA-style aluminum frame, scuffed white message panel "
    "completely BLANK — absolutely no text, letters, numbers, logos, watermarks, or graffiti. "
    "Subtle corner screws. Straight-on product shot, even daylight."
)

PIT_BG_PROMPT = (
    "Photorealistic semi-generic construction site wide shot. Deep excavation pit in "
    "foreground, yellow backhoe and orange crawler excavator at work. Dirt berms, orange "
    "safety fencing, portable toilet in far background. Partly cloudy sky. No readable "
    "text on any signage. Daylight, cinematic, no people's faces prominent."
)


def load_font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    names = (
        ["DejaVuSans-Bold.ttf", "LiberationSans-Bold.ttf", "FreeSansBold.ttf"]
        if bold
        else ["DejaVuSans.ttf", "LiberationSans-Regular.ttf", "FreeSans.ttf"]
    )
    roots = (
        Path("/usr/share/fonts/truetype/dejavu"),
        Path("/usr/share/fonts/truetype/liberation"),
        Path("/usr/share/fonts/truetype/freefont"),
    )
    for root in roots:
        for n in names:
            p = root / n
            if p.exists():
                return ImageFont.truetype(str(p), size)
    return ImageFont.load_default()


def render_api(prompt: str, dest: Path, *, size: str) -> None:
    import requests

    key = os.environ.get("OPENAI_API_KEY", "").strip()
    if not key:
        sys.exit("Set OPENAI_API_KEY for --render")
    dest.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "model": "gpt-image-1.5",
        "prompt": prompt,
        "size": size,
        "quality": "high",
        "output_format": "png",
        "n": 1,
    }
    r = requests.post(
        "https://api.openai.com/v1/images/generations",
        headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
        json=payload,
        timeout=180,
    )
    if r.status_code != 200:
        sys.exit(f"image gen failed {r.status_code}: {r.text[:400]}")
    dest.write_bytes(base64.b64decode(r.json()["data"][0]["b64_json"]))
    print(f"  [ok] {dest.name} ({dest.stat().st_size // 1024} KB)")


def load_turov_words() -> tuple[str, str, list[str]]:
    raw = SRC.read_text(encoding="utf-8")
    m = re.search(r"```\s*\n(╔[\s\S]*?╚[^\n]*)\n```", raw)
    if not m:
        sys.exit("TUROV sign block not found in -09.md")
    header1, header2 = "TUROV CONSTRUCTION LLC", "ADVISORY SITE SAFETY ADVISORY"
    lines: list[str] = []
    for ln in m.group(1).splitlines():
        s = ln.strip()
        if not s or any(s.startswith(c) for c in "╔╚╠═"):
            continue
        s = s.strip("║").strip()
        if not s:
            continue
        if header1 in s or header2 in s:
            continue
        if re.match(r"END OF ADVISORY", s, re.I):
            continue
        lines.append(s)
    text = " ".join(lines)
    text = re.sub(r"\*([^*]+)\*", r"\1", text)
    text = re.sub(r"\s+", " ", text).strip()
    return header1, header2, text.split()


def text_width(draw: ImageDraw.ImageDraw, text: str, font) -> float:
    if hasattr(draw, "textlength"):
        return draw.textlength(text, font=font)
    return font.getsize(text)[0]


def wrap_words(draw: ImageDraw.ImageDraw, font, words: list[str], max_w: float) -> list[str]:
    lines: list[str] = []
    line: list[str] = []
    for w in words:
        trial = " ".join(line + [w])
        if text_width(draw, trial, font) <= max_w or not line:
            line.append(w)
        else:
            lines.append(" ".join(line))
            line = [w]
    if line:
        lines.append(" ".join(line))
    return lines


def words_fitting(
    draw: ImageDraw.ImageDraw,
    font,
    words: list[str],
    max_w: float,
    max_h: float,
    line_gap: int,
) -> int:
    """Return count of words from start that fit in max_h when wrapped."""
    lo, hi, best = 0, len(words), 0
    while lo <= hi:
        mid = (lo + hi) // 2
        lines = wrap_words(draw, font, words[:mid], max_w)
        h = len(lines) * line_gap
        if h <= max_h:
            best = mid
            lo = mid + 1
        else:
            hi = mid - 1
    return best


def pick_body_font(
    draw: ImageDraw.ImageDraw,
    words: list[str],
    inner_w: float,
    body_h: float,
) -> tuple[ImageFont.FreeTypeFont | ImageFont.ImageFont, int, int]:
    for pt in range(17, 9, -1):
        font = load_font(pt)
        line_gap = pt + 4
        n = words_fitting(draw, font, words, inner_w, body_h, line_gap)
        if n >= 12 or pt == 10:
            return font, line_gap, n
    font = load_font(10)
    return font, 14, words_fitting(draw, font, words, inner_w, body_h, 14)


def draw_block(
    draw: ImageDraw.ImageDraw,
    x: float,
    y: float,
    lines: list[str],
    font,
    fill: tuple[int, int, int],
    line_gap: int,
) -> float:
    cy = y
    for ln in lines:
        draw.text((x, cy), ln, font=font, fill=fill)
        cy += line_gap
    return cy


def trim_sign_plate(img: Image.Image) -> Image.Image:
    """Drop the outer white mat from the generated PNG; keep only the sign object."""
    gray = img.convert("L")
    mask = gray.point(lambda p: 255 if p < TRIM_WHITE else 0)
    box = mask.getbbox()
    if not box:
        return img
    return img.crop(box)


def prepare_plate(blank: Image.Image) -> Image.Image:
    return trim_sign_plate(blank).resize((SIGN_W, SIGN_H), Image.Resampling.LANCZOS)


def inner_face_rect(plate: Image.Image) -> tuple[int, int, int, int]:
    """x, y, width, height of writable area inside the metal frame (image pixels)."""
    w, h = plate.size
    x = int(w * FACE_INSET_X)
    y = int(h * FACE_INSET_Y_TOP)
    ww = w - 2 * x
    hh = h - int(h * FACE_INSET_Y_BOTTOM) - y
    return x, y, ww, hh


def draw_centered(
    draw: ImageDraw.ImageDraw,
    box_left: float,
    box_width: float,
    y: float,
    text: str,
    font,
    fill: tuple[int, int, int],
) -> float:
    tw = text_width(draw, text, font)
    draw.text((box_left + max(0, (box_width - tw) / 2), y), text, font=font, fill=fill)
    bbox = draw.textbbox((0, 0), text, font=font)
    return y + (bbox[3] - bbox[1]) + 4


def render_filled_plate(
    plate: Image.Image,
    body_words: list[str],
    *,
    header1: str | None = None,
    header2: str | None = None,
) -> Image.Image:
    """Draw all text on the sign layer so type stays above the face, not over the frame."""
    layer = plate.copy()
    ink = (16, 18, 22)
    x0, y0, iw, ih = inner_face_rect(plate)
    draw = ImageDraw.Draw(layer)
    body_y = y0 + 4
    body_h = ih - 8

    if header1 and header2:
        title_pt = max(13, int(SIGN_H * 0.026))
        sub_pt = max(9, int(SIGN_H * 0.017))
        title_font = load_font(title_pt, bold=True)
        sub_font = load_font(sub_pt, bold=True)
        y = y0 + 2
        y = draw_centered(draw, x0, iw, y, header1, title_font, ink)
        y = draw_centered(draw, x0, iw, y, header2, sub_font, ink)
        body_y = y + 6
        body_h = (y0 + ih) - body_y

    probe = ImageDraw.Draw(Image.new("RGB", (10, 10)))
    body_font, line_gap, _ = pick_body_font(probe, body_words, iw, body_h)
    draw = ImageDraw.Draw(layer)
    lines = wrap_words(draw, body_font, body_words, iw)
    rpt = getattr(body_font, "size", 11)
    while len(lines) * line_gap > body_h and rpt > 8:
        rpt -= 1
        body_font = load_font(rpt)
        line_gap = rpt + 3
        lines = wrap_words(draw, body_font, body_words, iw)
    draw_block(draw, x0, body_y, lines, body_font, ink, line_gap)
    return layer


def compose(
    blank_path: Path,
    bg_path: Path,
    out_path: Path,
) -> None:
    header1, header2, words = load_turov_words()
    if not blank_path.exists() or not bg_path.exists():
        sys.exit(f"Missing {blank_path.name} or {bg_path.name} — run with --render")

    bg = Image.open(bg_path).convert("RGB")
    bg = bg.resize((FRAME_W, FRAME_H), Image.Resampling.LANCZOS)
    plate = prepare_plate(Image.open(blank_path).convert("RGBA"))

    x0, y0, iw, ih = inner_face_rect(plate)
    title_pt = max(13, int(SIGN_H * 0.026))
    sub_pt = max(9, int(SIGN_H * 0.017))
    header_reserve = title_pt + sub_pt + 22
    body_h_left = ih - header_reserve

    probe = ImageDraw.Draw(Image.new("RGB", (10, 10)))
    body_font, line_gap, n_left = pick_body_font(probe, words, iw, body_h_left)

    left_words = words[:n_left]
    right_words = words[n_left:]
    if not left_words and words:
        left_words = words[:1]
        right_words = words[1:]

    left_plate = render_filled_plate(
        plate, left_words, header1=header1, header2=header2
    )
    right_plate = render_filled_plate(plate, right_words)

    canvas = bg.copy()
    canvas.paste(left_plate, (SIGN_X_LEFT, SIGN_Y), left_plate)
    canvas.paste(right_plate, (SIGN_X_RIGHT, SIGN_Y), right_plate)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(out_path, quality=95)
    print(
        f"  [compose] {out_path.name}: {len(left_words)} + {len(right_words)} words "
        f"(body {body_font.size}pt, face {iw}x{ih}px)"
    )


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--render", action="store_true", help="Generate blank sign + pit background")
    ap.add_argument("--force", action="store_true", help="Regenerate API images even if present")
    args = ap.parse_args()

    STILLS.mkdir(parents=True, exist_ok=True)
    blank = STILLS / "sign_blank_template.png"
    pit = STILLS / "site_pit_excavator.png"
    out = STILLS / "turov_sign_scene.png"

    if args.render or args.force:
        if args.force or not blank.exists():
            print("── blank sign template ──")
            render_api(BLANK_PROMPT, blank, size="1024x1536")
        elif blank.exists():
            print(f"  [skip] {blank.name}")
        if args.force or not pit.exists():
            print("── pit / excavator background ──")
            render_api(PIT_BG_PROMPT, pit, size="1536x1024")
        elif pit.exists():
            print(f"  [skip] {pit.name}")

    compose(blank, pit, out)


if __name__ == "__main__":
    main()
