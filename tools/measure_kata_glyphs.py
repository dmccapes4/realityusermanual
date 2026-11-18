#!/usr/bin/env python3
"""Measure ΚΑΤΑ ΜΑΘΘΑΙΟΝ glyph boxes for the gate. Writes web/gate/glyph_metrics.json."""
from __future__ import annotations

import json
import shutil
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

BASE = Path(__file__).resolve().parent.parent
OUT = BASE / "web" / "gate"
TEXT = "ΚΑΤΑ ΜΑΘΘΑΙΟΝ"
SIZE = 160
FONTS = [
    Path("/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"),
    Path("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"),
    Path("/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf"),
]


def main() -> None:
    font_path = next(p for p in FONTS if p.exists())
    font = ImageFont.truetype(str(font_path), SIZE)
    glyphs = []
    x = 0.0
    for ch in TEXT:
        w = float(font.getlength(ch))
        glyphs.append({"ch": ch, "x": x, "w": w})
        x += w
    total = x
    # ΘΘ are indices of the two thetas in ΜΑΘΘΑΙΟΝ (after space)
    theta_ix = [i for i, g in enumerate(glyphs) if g["ch"] == "Θ"]
    assert len(theta_ix) == 2, f"expected 2 Θ, got {theta_ix}"
    t0, t1 = glyphs[theta_ix[0]], glyphs[theta_ix[1]]
    theta_mid = (t0["x"] + t1["x"] + t1["w"]) / 2.0
    kata_end = next(g["x"] + g["w"] for g in glyphs if g["ch"] == " " )
    payload = {
        "text": TEXT,
        "font": str(font_path),
        "font_css": "DejaVu Serif",
        "size_px": SIZE,
        "total_width": total,
        "glyphs": glyphs,
        "kata": {"start": 0.0, "end": kata_end},
        "theta_pair": {
            "i0": theta_ix[0],
            "i1": theta_ix[1],
            "x0": t0["x"],
            "x1": t1["x"],
            "w": t0["w"],
            "mid": theta_mid,
            "gap": t1["x"] - (t0["x"] + t0["w"]),
        },
        "maththaion_start": kata_end,
    }
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "glyph_metrics.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n")
    # preview strip
    pad = 40
    im = Image.new("RGB", (int(total) + pad * 2, SIZE + pad * 2), (20, 18, 16))
    dr = ImageDraw.Draw(im)
    dr.text((pad, pad), TEXT, font=font, fill=(232, 220, 196))
    for i in theta_ix:
        g = glyphs[i]
        dr.rectangle(
            [pad + g["x"], pad, pad + g["x"] + g["w"], pad + SIZE],
            outline=(140, 58, 42),
            width=2,
        )
    im.save(OUT / "glyph_preview.png")
    # copy font into web/gate/fonts for serving
    fonts_dir = OUT / "fonts"
    fonts_dir.mkdir(exist_ok=True)
    dest = fonts_dir / font_path.name
    if not dest.exists():
        shutil.copy2(font_path, dest)
    print(f"wrote {OUT / 'glyph_metrics.json'}")
    print(f"ΘΘ mid={theta_mid:.1f} / total={total:.1f}  font={font_path.name}")


if __name__ == "__main__":
    main()
