#!/usr/bin/env python3
"""Single desk still for page −31 (listen-only bind)."""
from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

BASE = Path(__file__).resolve().parent.parent
OUT_DIR = BASE / "audio" / "minus31"
OUT = OUT_DIR / "-31_listen_card.png"
W, H = 1280, 720


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    img = Image.new("RGB", (W, H), (12, 14, 18))
    draw = ImageDraw.Draw(img)
    try:
        title_f = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 52)
        sub_f = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 28)
        small_f = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 22)
    except OSError:
        title_f = sub_f = small_f = ImageFont.load_default()

    draw.rectangle((48, 48, W - 48, H - 48), outline=(60, 72, 88), width=2)
    draw.text((80, 100), "−31", fill=(180, 200, 220), font=title_f)
    draw.text((80, 180), "The Postmortem That Named Itself", fill=(220, 225, 230), font=sub_f)
    draw.text((80, 240), "los-lun-resh · listen-only", fill=(140, 160, 180), font=sub_f)
    draw.text((80, 320), "Atticus · relay", fill=(100, 120, 140), font=small_f)
    draw.text((80, 360), "Holden · chat", fill=(100, 120, 140), font=small_f)
    draw.text((80, 400), "Winslade · agent / postmortem", fill=(100, 120, 140), font=small_f)
    draw.text((80, 440), "Auden · los-lun-resh", fill=(100, 120, 140), font=small_f)
    draw.text((80, H - 120), "No slideshow. No live action. Headphones.", fill=(90, 110, 130), font=small_f)
    img.save(OUT, optimize=True)
    print(f"Wrote {OUT}")


if __name__ == "__main__":
    main()
