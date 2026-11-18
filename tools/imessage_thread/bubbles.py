"""Deterministic bubble geometry from an iMessage dark-mode crop (blue/gray fills on black)."""

from __future__ import annotations

from typing import Any

import numpy as np
from PIL import Image

MIN_ROW_PX = 12       # colored px in a row to count as part of a band
MAX_GAP_ROWS = 2      # tolerate anti-aliasing holes between rows
MIN_BAND_HEIGHT = 8
BADGE_MAX_W = 130     # tapback badge ≈ 65 px round; short bubbles are wider or taller
BADGE_MAX_H = 90
LABEL_MAX_H = 30      # gray system text (date pill, "Read 3:18 PM", "Delivered") is a thin band, no fill
LABEL_MIN_W = 60


def _masks(arr: np.ndarray) -> dict[str, np.ndarray]:
    r, g, b = arr[..., 0].astype(int), arr[..., 1].astype(int), arr[..., 2].astype(int)
    blue = (b > 150) & (b > r + 60) & (g > 80)
    gray = (np.abs(r - g) < 14) & (np.abs(g - b) < 16) & (r >= 24) & (r <= 70)
    return {"blue": blue, "gray": gray}


def _bands(rows: np.ndarray) -> list[tuple[int, int]]:
    out: list[tuple[int, int]] = []
    start = None
    gap = 0
    for y, v in enumerate(rows):
        if v >= MIN_ROW_PX:
            if start is None:
                start = y
            gap = 0
            last = y
        elif start is not None:
            gap += 1
            if gap > MAX_GAP_ROWS:
                out.append((start, last))
                start = None
                gap = 0
    if start is not None:
        out.append((start, last))
    return [(a, b) for a, b in out if b - a + 1 >= MIN_BAND_HEIGHT]


def detect_bubbles(img: Image.Image) -> list[dict[str, Any]]:
    """
    Returns bubbles and tapback badges sorted top→bottom:
      {idx, kind: 'bubble'|'badge', color: 'blue'|'gray', side: 'right'|'left',
       top, bottom, left, right, width, height, clipped_top, clipped_bottom}
    """
    arr = np.array(img.convert("RGB"))
    h, w = arr.shape[:2]
    masks = _masks(arr)
    ink = arr.max(axis=2) > 24          # anything that is not the black background (bubble fill or glyphs)
    white = arr.min(axis=2) > 200       # glyph pixels
    found: list[dict[str, Any]] = []
    for color, mask in masks.items():
        rows = mask.sum(axis=1)
        for top, bottom in _bands(rows):
            cols = mask[top : bottom + 1].any(axis=0)
            xs = np.where(cols)[0]
            if xs.size == 0:
                continue
            left, right = int(xs[0]), int(xs[-1])
            width, height = right - left + 1, bottom - top + 1
            touches_edge = top <= 2 or bottom >= h - 3
            if color == "gray" and height <= LABEL_MAX_H and width >= LABEL_MIN_W and not touches_edge:
                kind = "label"
            elif width <= BADGE_MAX_W and height <= BADGE_MAX_H:
                kind = "badge"
            else:
                kind = "bubble"
            # A bubble is clipped only if it runs at FULL width into the crop edge; a rounded corner at the
            # edge means the bubble merely starts/ends there.
            edge_top_w = int(ink[top : top + 3, left : right + 1].sum(axis=1).max())
            edge_bot_w = int(ink[max(top, bottom - 2) : bottom + 1, left : right + 1].sum(axis=1).max())
            clipped_top = bool(top <= 2 and edge_top_w >= width - 12)
            clipped_bottom = bool(bottom >= h - 3 and edge_bot_w >= width - 12)
            # Distance from the bubble's crop edge to its first / last glyph row (paragraph-break evidence at joins).
            sub = white[top : bottom + 1, left : right + 1]
            glyph_rows = np.where(sub.sum(axis=1) > 2)[0]
            head_gap = int(glyph_rows[0]) if glyph_rows.size else None
            tail_gap = int(height - 1 - glyph_rows[-1]) if glyph_rows.size else None
            found.append(
                {
                    "kind": kind,
                    "color": color,
                    "side": "right" if color == "blue" else "left",
                    "top": int(top),
                    "bottom": int(bottom),
                    "left": left,
                    "right": right,
                    "width": int(width),
                    "height": int(height),
                    "clipped_top": clipped_top,
                    "clipped_bottom": clipped_bottom,
                    "head_gap": head_gap,
                    "tail_gap": tail_gap,
                }
            )
    found.sort(key=lambda b: b["top"])
    counters = {"bubble": 0, "badge": 0, "label": 0}
    for b in found:
        b["idx"] = counters[b["kind"]]
        counters[b["kind"]] += 1
    bubbles = [b for b in found if b["kind"] == "bubble"]
    center = w / 2
    for b in found:
        if b["kind"] == "badge":
            # iOS draws the tapback over the TOP corner of the reacted bubble → it belongs to the bubble below.
            below = [x for x in bubbles if x["top"] >= b["top"] - 5]
            b["target_idx"] = below[0]["idx"] if below else (bubbles[-1]["idx"] if bubbles else None)
        elif b["kind"] == "label":
            mid = (b["left"] + b["right"]) / 2
            if abs(mid - center) <= 0.12 * w:
                b["label_role"] = "pill"          # date pill → belongs to the bubble directly below
                below = [x for x in bubbles if x["top"] >= b["bottom"]]
                b["target_idx"] = below[0]["idx"] if below else None
            elif b["right"] >= 0.75 * w:
                b["label_role"] = "receipt"       # "Read …" / "Delivered" → belongs to the blue bubble directly above
                above = [x for x in bubbles if x["bottom"] <= b["top"] and x["color"] == "blue"]
                b["target_idx"] = above[-1]["idx"] if above else None
            else:
                b["label_role"] = "other"
                b["target_idx"] = None
    return found


def bubble_crop(img: Image.Image, b: dict[str, Any], pad: int = 4) -> Image.Image:
    w, h = img.size
    box = (max(0, b["left"] - pad), max(0, b["top"] - pad), min(w, b["right"] + pad + 1), min(h, b["bottom"] + pad + 1))
    return img.crop(box)
