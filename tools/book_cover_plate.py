#!/usr/bin/env python3
"""Render REALITY_USER_MANUAL.pdf page 1 → web/book/assets/cover.png via pdftoppm."""
from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PDF = ROOT / "REALITY_USER_MANUAL.pdf"
OUT_DIR = ROOT / "web" / "book" / "assets"
OUT = OUT_DIR / "cover.png"


def main() -> int:
    if not PDF.exists():
        print(f"missing {PDF}", file=sys.stderr)
        return 1
    if not shutil.which("pdftoppm"):
        print("pdftoppm not found (poppler-utils)", file=sys.stderr)
        return 1
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    stem = OUT_DIR / "cover"
    subprocess.run(
        ["pdftoppm", "-png", "-f", "1", "-l", "1", "-r", "150", str(PDF), str(stem)],
        check=True,
    )
    # pdftoppm writes cover-1.png or cover-001.png depending on version
    candidates = sorted(OUT_DIR.glob("cover-*.png"))
    if not candidates:
        print("pdftoppm did not write cover-*.png", file=sys.stderr)
        return 1
    generated = candidates[0]
    generated.replace(OUT)
    print(f"✓ {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
