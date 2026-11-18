#!/usr/bin/env python3
"""
Pygame loop: play dialog_reading.mp3 and composite plates from cues.

Cues carry a background plus transparent character / prop / fx layers.
Missing plates fall back to ink + speaker label — nothing is invented.

  .venv/bin/python tools/pygame_sync.py
  .venv/bin/python tools/pygame_sync.py --seek 3480
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import pygame

BASE = Path(__file__).resolve().parent.parent
VIDEO = BASE / "video"
W, H = 1280, 720
BONE = (230, 220, 200)
INK = (11, 11, 12)

# Layout for compositing transparent character PNGs onto 16:9.
# Speaking plate is larger; seated extras stay in a row; Stanley stays back.
ANCHOR = {
    "speak": ((72, 72), (400, 580)),
    "seated": ((0, 0), (240, 340)),
    "back": ((980, 140), (170, 260)),
    "fx": ((860, 180), (280, 280)),
    "prop": ((900, 430), (300, 200)),
}

SEATED_ROW = [
    (80, 280),
    (340, 280),
    (600, 280),
]


def load_jsonl(path: Path) -> list[dict]:
    return [json.loads(l) for l in path.read_text().splitlines() if l.strip()]


def index_by_id(path: Path) -> dict[str, dict]:
    return {row["id"]: row for row in load_jsonl(path)}


def cue_at(cues: list[dict], t: float) -> dict | None:
    for c in cues:
        if c["start"] <= t < c["end"]:
            return c
    return cues[-1] if cues and t >= cues[-1]["end"] else (cues[0] if cues else None)


def load_surface(rel: str | None, size: tuple[int, int], alpha: bool) -> pygame.Surface | None:
    if not rel:
        return None
    p = BASE / rel
    if not p.exists():
        return None
    img = pygame.image.load(str(p))
    img = img.convert_alpha() if alpha else img.convert()
    return pygame.transform.smoothscale(img, size)


def kind_of(shot: dict) -> str:
    layer = shot.get("layer")
    if layer in {"prop", "fx"}:
        return layer
    if layer == "background":
        return "background"
    state = shot.get("state") or ""
    if "seated" in state or state in {"sit", "lie_drip", "sleep", "work"}:
        return "seated"
    if shot.get("character") == "stanley":
        return "back"
    return "speak"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--audio", default=str(BASE / "audio" / "dialog_reading.mp3"))
    ap.add_argument("--cues", default=str(VIDEO / "cues.jsonl"))
    ap.add_argument("--seek", type=float, default=0.0, help="start seconds (recast exit ~3480)")
    args = ap.parse_args()

    audio = Path(args.audio)
    cues_path = Path(args.cues)
    if not audio.exists():
        sys.exit(f"missing audio: {audio}")
    if not cues_path.exists():
        sys.exit(f"missing cues: {cues_path}  (run tools/build_cues.py)")

    shots = index_by_id(VIDEO / "catalogs" / "shots.jsonl")
    cues = load_jsonl(cues_path)

    pygame.init()
    pygame.mixer.init()
    screen = pygame.display.set_mode((W, H))
    pygame.display.set_caption("REALITY_USER_MANUAL")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("serif", 20)
    small = pygame.font.SysFont("serif", 14)

    cache: dict[str, pygame.Surface | None] = {}

    def still(rel: str | None, size: tuple[int, int], alpha: bool) -> pygame.Surface | None:
        key = f"{rel}:{size}:{alpha}"
        if key not in cache:
            cache[key] = load_surface(rel, size, alpha)
        return cache[key]

    pygame.mixer.music.load(str(audio))
    pygame.mixer.music.play(start=max(0.0, args.seek))

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN and event.key in (pygame.K_ESCAPE, pygame.K_q):
                running = False

        if not pygame.mixer.music.get_busy():
            running = False
            break

        t = args.seek + pygame.mixer.music.get_pos() / 1000.0
        cue = cue_at(cues, t)
        screen.fill(INK)

        if cue:
            bg_id = cue.get("background")
            bg_shot = shots.get(bg_id or "", {})
            bg = still(bg_shot.get("file"), (W, H), False)
            if bg:
                screen.blit(bg, (0, 0))

            if not cue.get("full_bleed"):
                seated_i = 0
                for lid in cue.get("layers") or []:
                    shot = shots.get(lid, {})
                    kind = kind_of(shot)
                    if kind == "speak":
                        pos, size = ANCHOR["speak"]
                    elif kind == "seated":
                        pos, size = ANCHOR["seated"]
                        pos = SEATED_ROW[seated_i % len(SEATED_ROW)]
                        seated_i += 1
                    elif kind == "back":
                        pos, size = ANCHOR["back"]
                    elif kind == "fx":
                        pos, size = ANCHOR["fx"]
                    else:
                        pos, size = ANCHOR["prop"]
                    plate = still(shot.get("file"), size, True)
                    if plate:
                        screen.blit(plate, pos)

            label = f"{cue.get('speaker', '')}   {cue.get('camera') or ''}"
            screen.blit(font.render(label, True, BONE), (40, H - 52))
            beat = cue.get("beat") or ""
            if beat:
                screen.blit(small.render(beat, True, BONE), (40, H - 28))

        pygame.display.flip()
        clock.tick(30)

    pygame.quit()


if __name__ == "__main__":
    main()
