"""Stage 1: contact name, locality, status-bar time, thread anchor from images[0]."""

from __future__ import annotations

import base64
import io
import json
import re
from pathlib import Path
from typing import Any

from PIL import Image

from crop import crop_header, crop_status_bar, crop_thread
from dates import resolve_pill
from ocr import (
    extract_thread_markers,
    looks_like_contact_name,
    ocr_image,
    parse_contact_header,
    parse_status_bar_time,
)

HEADER_SCHEMA = {
    "type": "object",
    "properties": {
        "contact_name": {"type": ["string", "null"]},
        "contact_locality": {"type": ["string", "null"]},
    },
    "required": ["contact_name", "contact_locality"],
    "additionalProperties": False,
}


def _png_data_url(img: Image.Image) -> str:
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode("ascii")


def _header_via_mini(model: str, img: Image.Image) -> tuple[str | None, str | None]:
    from openai_env import client

    resp = client().chat.completions.create(
        model=model,
        messages=[
            {
                "role": "system",
                "content": "This is the iMessage navigation header. Return the contact name shown (without the '>' chevron) and the locality line under it if any. Nothing else.",
            },
            {
                "role": "user",
                "content": [{"type": "image_url", "image_url": {"url": _png_data_url(img), "detail": "high"}}],
            },
        ],
        response_format={
            "type": "json_schema",
            "json_schema": {"name": "header", "strict": True, "schema": HEADER_SCHEMA},
        },
        max_tokens=200,
        temperature=0,
    )
    data = json.loads(resp.choices[0].message.content or "{}")
    return data.get("contact_name"), data.get("contact_locality")


def slugify(name: str | None) -> str:
    s = re.sub(r"[^a-z0-9]+", "_", (name or "contact").lower()).strip("_")
    return s or "contact"


def extract_contact(
    image_path: Path,
    profile: dict[str, Any],
    *,
    model_fallback: str,
    process_date: str,
    tz: str,
) -> dict[str, Any]:
    header = crop_header(image_path, profile)
    status = crop_status_bar(image_path, profile)
    thread, _mode, _box, _note = crop_thread(image_path, profile)

    if header is not None:
        header = header.resize((header.width * 2, header.height * 2), Image.LANCZOS)
    if status is not None:
        status = status.resize((status.width * 3, status.height * 3), Image.LANCZOS)
    header_text = ocr_image(header, psm=6) if header is not None else ""
    name, locality = parse_contact_header(header_text)
    source = "tesseract"
    if not looks_like_contact_name(name) and header is not None:
        name, locality2 = _header_via_mini(model_fallback, header)
        locality = locality or locality2
        source = model_fallback

    status_text = ocr_image(status, psm=7) if status is not None else ""
    status_time = parse_status_bar_time(status_text)

    markers = extract_thread_markers(ocr_image(thread, psm=6))
    anchor: dict[str, Any] | None = None
    for line in markers.splitlines():
        iso, conf = resolve_pill(line, _date(process_date), _zone(tz))
        if iso:
            anchor = {"raw": line, "timestamp_iso": iso, "timestamp_confidence": conf}
            break
    if anchor is None and markers.strip():
        anchor = {"raw": markers.splitlines()[0], "timestamp_iso": None, "timestamp_confidence": "low"}

    return {
        "contact_name": name,
        "contact_slug": slugify(name),
        "contact_locality": locality,
        "contact_source": source,
        "status_bar_time": status_time,
        "thread_anchor": anchor,
        "header_ocr_text": header_text,
        "source_image": str(image_path),
    }


def _date(s: str):
    import datetime

    y, m, d = (int(x) for x in s.split("-"))
    return datetime.date(y, m, d)


def _zone(name: str):
    from zoneinfo import ZoneInfo

    return ZoneInfo(name)
