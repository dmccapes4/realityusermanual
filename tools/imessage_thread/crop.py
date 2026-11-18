"""Stage 2: fixed thread crop (below contact header, above composer)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from PIL import Image


def load_profile(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _box(b: dict[str, int]) -> tuple[int, int, int, int]:
    return (b["left"], b["top"], b["right"], b["bottom"])


def crop_thread(image_path: Path, profile: dict[str, Any]) -> tuple[Image.Image, str, list[int], str | None]:
    """
    Returns (thread_image, mode, crop_box, note).
    mode: "cropped" (full screenshot → box), "precropped" (already thread-sized), "as_is" (unknown size).
    """
    img = Image.open(image_path).convert("RGB")
    w, h = img.size
    shot = tuple(profile["screenshot_size_px"])
    target = tuple(profile.get("thread_crop_size_px") or [])
    box = _box(profile["thread_crop_px"])
    if (w, h) == shot:
        return img.crop(box), "cropped", list(box), None
    if target and (w, h) == target:
        return img, "precropped", [0, 0, w, h], None
    note = f"unexpected size {w}x{h}; expected {shot[0]}x{shot[1]} or {target}; used as-is"
    return img, "as_is", [0, 0, w, h], note


def crop_header(image_path: Path, profile: dict[str, Any]) -> Image.Image | None:
    img = Image.open(image_path).convert("RGB")
    if tuple(img.size) != tuple(profile["screenshot_size_px"]):
        return None
    return img.crop(_box(profile["header_crop_px"]))


def crop_status_bar(image_path: Path, profile: dict[str, Any]) -> Image.Image | None:
    img = Image.open(image_path).convert("RGB")
    if tuple(img.size) != tuple(profile["screenshot_size_px"]):
        return None
    return img.crop(_box(profile["status_bar_crop_px"]))
