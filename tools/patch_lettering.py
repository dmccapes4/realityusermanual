#!/usr/bin/env python3
"""Stamp exact scripts the image model garbled. Measured boxes, DejaVu/Liberation."""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

BASE = Path(__file__).resolve().parent.parent
SERIF = "/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf"
SERIF_I = "/usr/share/fonts/truetype/liberation/LiberationSerif-Italic.ttf"
MONO = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"
SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

GALL = (72, 32, 18)
VELLUM = (196, 181, 142)
BONE = (230, 220, 200)
INK = (11, 11, 12)
CHALK = (228, 214, 176)
BOARD = (38, 38, 28)


def font(path: str, size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(path, size)


def center_lines(draw: ImageDraw.ImageDraw, box, lines, face, fill, leading):
    x0, y0, x1, y1 = box
    heights = []
    widths = []
    for line in lines:
        bb = draw.textbbox((0, 0), line, font=face)
        widths.append(bb[2] - bb[0])
        heights.append(bb[3] - bb[1])
    total = sum(heights) + leading * (len(lines) - 1)
    y = y0 + (y1 - y0 - total) // 2
    for line, w, h in zip(lines, widths, heights):
        x = x0 + (x1 - x0 - w) // 2
        draw.text((x, y), line, font=face, fill=fill)
        y += h + leading


def patch_oak() -> None:
    path = BASE / "video/stills/layers/backgrounds/oak_grimoire.png"
    im = Image.open(path).convert("RGB")
    draw = ImageDraw.Draw(im)
    box = (887, 183, 1413, 635)
    draw.rounded_rectangle(box, radius=6, fill=VELLUM)
    pad = (box[0] + 36, box[1] + 28, box[2] - 36, box[3] - 28)
    center_lines(
        draw,
        pad,
        ["Merlin continued", "through the oak."],
        font(SERIF_I, 42),
        GALL,
        leading=22,
    )
    im.save(path)
    print(f"[ok] oak_grimoire  {path.stat().st_size}")


def patch_volare() -> None:
    path = BASE / "video/stills/layers/fx/volare_glyph.png"
    im = Image.open(path).convert("RGBA")
    draw = ImageDraw.Draw(im)
    # black bar only — wrists sit on y~780
    bar = (104, 776, 918, 962)
    draw.rectangle(bar, fill=INK + (255,))
    face = font(SANS, 72)
    text = "VOLARE:>"
    bb = draw.textbbox((0, 0), text, font=face)
    tw, th = bb[2] - bb[0], bb[3] - bb[1]
    x = bar[0] + (bar[2] - bar[0] - tw) // 2
    y = bar[1] + (bar[3] - bar[1] - th) // 2 - 4
    draw.text((x, y), text, font=face, fill=BONE + (255,))
    im.save(path)
    print(f"[ok] volare_glyph  {path.stat().st_size}")


def patch_euler() -> None:
    path = BASE / "video/stills/layers/backgrounds/euler_study.png"
    im = Image.open(path).convert("RGB")
    draw = ImageDraw.Draw(im)
    # inset of the flooded board so the chalk frame stays
    board = (420, 230, 1170, 640)
    draw.rectangle(board, fill=BOARD)
    face = font(MONO, 28)
    lines = [
        "L(n) = -n",
        "bases  -0  -7  -14",
        "e  ->  i e    (display)",
        "",
        "int a = e;",
        "b = a * n;",
        "return -b;",
    ]
    x, y = 470, 260
    for line in lines:
        draw.text((x, y), line, font=face, fill=CHALK)
        y += 46
    im.save(path)
    print(f"[ok] euler_study  {path.stat().st_size}")


def main() -> None:
    patch_oak()
    patch_volare()
    patch_euler()


if __name__ == "__main__":
    main()
