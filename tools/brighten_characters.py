#!/usr/bin/env python3
"""Midtone-lift character PNGs; keep ink blacks and alpha.

  .venv/bin/python tools/brighten_characters.py
  .venv/bin/python tools/brighten_characters.py --dry-run
"""
from __future__ import annotations

import argparse
import shutil
import statistics as st
from pathlib import Path

import numpy as np
from PIL import Image

BASE = Path(__file__).resolve().parent.parent
CHARS = BASE / "video" / "stills" / "layers" / "characters"
BACKUP = CHARS / "_pre_brighten"


def brighten_np(im: Image.Image, gain: float = 1.32, black_keep: float = 22) -> Image.Image:
    arr = np.array(im.convert("RGBA"))
    rgb = arr[..., :3].astype(np.float32)
    a = arr[..., 3]
    lum = 0.2126 * rgb[..., 0] + 0.7152 * rgb[..., 1] + 0.0722 * rgb[..., 2]
    t = np.clip(lum / 255.0, 0, 1)
    lift = 1.0 + (gain - 1.0) * (4 * t * (1 - t))
    rgb2 = np.clip(rgb * lift[..., None], 0, 255)
    rgb2[lum <= black_keep] = rgb[lum <= black_keep]
    cream = (lum > 90) & (lum < 220)
    rgb2[cream] = np.clip(rgb2[cream] * 1.06, 0, 255)
    return Image.fromarray(np.dstack([rgb2.astype(np.uint8), a]), "RGBA")


def mean_l(im: Image.Image) -> float:
    vals = [0.2126 * r + 0.7152 * g + 0.0722 * b for r, g, b, a in im.getdata() if a > 200]
    return float(st.mean(vals)) if vals else 0.0


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--gain", type=float, default=1.32)
    args = ap.parse_args()

    paths = sorted(p for p in CHARS.glob("*.png") if p.is_file())
    if not args.dry_run:
        BACKUP.mkdir(exist_ok=True)
        for p in paths:
            dest = BACKUP / p.name
            if not dest.exists():
                shutil.copy2(p, dest)

    for p in paths:
        im = Image.open(p).convert("RGBA")
        before = mean_l(im)
        out = brighten_np(im, gain=args.gain)
        after = mean_l(out)
        print(f"{p.name:40} {before:5.1f} -> {after:5.1f}")
        if not args.dry_run:
            out.save(p)


if __name__ == "__main__":
    main()
