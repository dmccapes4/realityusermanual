#!/usr/bin/env python3
"""Single encapsulation still for page −31 (listen desk: image + audio, not video)."""
from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageFilter

BASE = Path(__file__).resolve().parent.parent
OUT = BASE / "audio" / "minus31" / "-31_debacle_still.png"
W, H = 1920, 1080

GREEN = (45, 168, 100)
GREEN_GLOW = (55, 200, 120, 90)
PANEL_L = (22, 28, 36)
PANEL_R = (18, 24, 32)
INK = (210, 218, 228)
MUTED = (120, 132, 148)
ACCENT = (180, 200, 220)
WARN = (220, 140, 90)
HIGHLIGHT = (255, 230, 120)


def fonts():
    try:
        return (
            ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 56),
            ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 36),
            ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 28),
            ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf", 24),
            ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf", 42),
        )
    except OSError:
        d = ImageFont.load_default()
        return d, d, d, d, d


def draw_notebook_lines(draw: ImageDraw.ImageDraw, x0: int, y0: int, w: int, h: int) -> None:
    draw.rounded_rectangle((x0, y0, x0 + w, y0 + h), radius=8, fill=PANEL_L, outline=(55, 68, 82))
    for i in range(8):
        y = y0 + 48 + i * 34
        draw.line((x0 + 24, y, x0 + w - 24, y), fill=(45, 55, 68), width=1)
    draw.text((x0 + 24, y0 + 12), "AUDEN · LEFT · NEVER LEAVES", fill=MUTED, font=fonts()[2])


def draw_blink_panel(draw: ImageDraw.ImageDraw, x0: int, y0: int, w: int, h: int) -> None:
    draw.rounded_rectangle((x0, y0, x0 + w, y0 + h), radius=8, fill=PANEL_R, outline=(55, 68, 82))
    cx = x0 + w // 2
    # silhouette head/shoulders
    draw.ellipse((cx - 70, y0 + 80, cx + 70, y0 + 220), fill=(35, 42, 52))
    draw.polygon(
        [(cx - 90, y0 + 200), (cx + 90, y0 + 200), (cx + 110, y0 + h - 40), (cx - 110, y0 + h - 40)],
        fill=(35, 42, 52),
    )
    # blink bars — narrator "competing for presence"
    for bx in (x0 + 18, cx - 8, x0 + w - 34):
        draw.rectangle((bx, y0 + 60, bx + 14, y0 + h - 50), fill=(8, 10, 14))
    draw.text((x0 + 24, y0 + 12), "RIGHT · BLINK · EVICTION (WRONG)", fill=WARN, font=fonts()[2])


def main() -> None:
    title_f, sub_f, body_f, mono_f, mono_b = fonts()
    img = Image.new("RGB", (W, H), (10, 12, 16))
    draw = ImageDraw.Draw(img)

    # dock water
    for y in range(int(H * 0.62), H):
        t = (y - H * 0.62) / (H * 0.38)
        c = int(12 + 18 * t)
        draw.line((0, y, W, y), fill=(c, c + 6, c + 10))

    # green light across the water
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gdraw = ImageDraw.Draw(glow)
    gx, gy = int(W * 0.88), int(H * 0.68)
    for r in (120, 80, 45):
        gdraw.ellipse((gx - r, gy - r, gx + r, gy + r), fill=GREEN_GLOW)
    img = Image.alpha_composite(img.convert("RGBA"), glow).convert("RGB")
    draw = ImageDraw.Draw(img)
    draw.ellipse((gx - 10, gy - 10, gx + 10, gy + 10), fill=GREEN)

    draw_notebook_lines(draw, 64, 140, 520, 420)
    draw_blink_panel(draw, W - 584, 140, 520, 420)

    draw.line((W // 2, 120, W // 2, 580), fill=(50, 60, 72), width=2)
    draw.text((W // 2 - 140, 580), "one speaker slot (lie)", fill=MUTED, font=body_f)

    draw.text((64, 48), "−31", fill=ACCENT, font=title_f)
    draw.text((180, 58), "THE POSTMORTEM THAT NAMED ITSELF", fill=INK, font=sub_f)

    # waste → repair
    box_y = 620
    draw.rounded_rectangle((64, box_y, W - 64, box_y + 200), radius=10, fill=(16, 20, 26), outline=(60, 72, 88))
    draw.text((96, box_y + 24), "23,801 PNGs  →  66", fill=INK, font=mono_b)
    draw.text((96, box_y + 82), "40 min render  →  7 sec", fill=MUTED, font=mono_f)
    draw.text((96, box_y + 124), "game clock tick ≠ unique frame", fill=WARN, font=body_f)

    # vain switch (cue 140)
    draw.rounded_rectangle((W - 420, box_y + 36, W - 96, box_y + 160), radius=6, fill=(32, 28, 18), outline=HIGHLIGHT)
    draw.text((W - 400, box_y + 52), "switch @ 659.5 s", fill=MUTED, font=mono_f)
    draw.text((W - 400, box_y + 92), "Vain.", fill=HIGHLIGHT, font=mono_b)
    draw.text((W - 400, box_y + 132), "gentle fetters", fill=MUTED, font=body_f)

    draw.text(
        (64, H - 56),
        "los-lun-resh · listen: still + audio · not a slideshow",
        fill=MUTED,
        font=body_f,
    )

    OUT.parent.mkdir(parents=True, exist_ok=True)
    img.save(OUT, optimize=True)
    print(f"Wrote {OUT} ({OUT.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
