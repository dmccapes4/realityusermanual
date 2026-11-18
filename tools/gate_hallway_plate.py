#!/usr/bin/env python3
"""Copy −10b ink hall into web/gate/assets and record vanishing point (center)."""
from __future__ import annotations

import json
import shutil
from pathlib import Path

from PIL import Image

BASE = Path(__file__).resolve().parent.parent
SRC = BASE / "video" / "minus10b" / "stills" / "hall_indefinite.jpg"
ALT = BASE / "video" / "minus10" / "stills" / "hall_01.png"
OUT = BASE / "web" / "gate" / "assets"
W, H = 1920, 1080


def main() -> None:
    src = SRC if SRC.exists() else ALT
    if not src.exists():
        raise SystemExit(f"no hallway still at {SRC} or {ALT}")
    OUT.mkdir(parents=True, exist_ok=True)
    im = Image.open(src).convert("RGB")
    # cover 16:9
    sw, sh = im.size
    scale = max(W / sw, H / sh)
    nw, nh = int(sw * scale), int(sh * scale)
    im = im.resize((nw, nh), Image.Resampling.LANCZOS)
    left = (nw - W) // 2
    top = (nh - H) // 2
    im = im.crop((left, top, left + W, top + H))
    dest = OUT / "hallway.png"
    im.save(dest, "PNG")
    # one-point plates are centered
    vp = {"x": W // 2, "y": H // 2, "w": W, "h": H, "source": str(src.relative_to(BASE))}
    (OUT / "vanishing_point.json").write_text(json.dumps(vp, indent=2) + "\n")
    # also copy into hall assets for land page
    hall_assets = BASE / "web" / "hall" / "assets"
    hall_assets.mkdir(parents=True, exist_ok=True)
    shutil.copy2(dest, hall_assets / "hallway.png")
    print(f"wrote {dest} from {src.name}")
    print(f"vanishing_point {vp['x']},{vp['y']}")


if __name__ == "__main__":
    main()
