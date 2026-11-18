"""Tesseract helpers (stage 1 header/status, stage 3 thread crops)."""

from __future__ import annotations

import re
import shutil
import sys

from PIL import Image

ENGINE = "tesseract"

_NOT_NAMES = re.compile(
    r"^(Mint|Verizon|T-Mobile|AT&T|Wi-Fi|FaceTime|iMessage|Read|Delivered|Today|Yesterday|"
    r"Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday)$",
    re.I,
)


def ensure_tesseract() -> None:
    if not shutil.which("tesseract"):
        print(
            "tesseract not found. Install on the host, e.g.:\n  sudo apt-get install -y tesseract-ocr",
            file=sys.stderr,
        )
        raise SystemExit(1)


def ocr_image(img: Image.Image, psm: int = 6) -> str:
    import pytesseract

    return pytesseract.image_to_string(img, config=f"--psm {psm}").strip()


def ocr_confidence(img: Image.Image) -> float | None:
    import pytesseract

    try:
        data = pytesseract.image_to_data(img, output_type=pytesseract.Output.DICT)
        confs = [int(c) for c in data["conf"] if str(c).lstrip("-").isdigit() and int(c) >= 0]
        return round(sum(confs) / len(confs) / 100.0, 3) if confs else None
    except Exception:
        return None


def parse_status_bar_time(text: str) -> str | None:
    m = re.search(r"(\d{1,2}:\d{2}\s*(?:AM|PM|am|pm))", text or "")
    return re.sub(r"\s+", " ", m.group(1).upper()) if m else None


def looks_like_contact_name(name: str | None) -> bool:
    if not name or len(name) > 32:
        return False
    name = name.strip()
    if _NOT_NAMES.match(name):
        return False
    if re.search(r"[\d\[\]<>@:]", name):
        return False
    return bool(re.match(r"^[A-Z][A-Za-z'\-]*(\s[A-Z][A-Za-z'\-]*){0,2}$", name))


def parse_contact_header(text: str) -> tuple[str | None, str | None]:
    """(contact_name, locality) from the header pill OCR ('Justin >' / 'Roseville, CA')."""
    lines = [ln.strip() for ln in (text or "").splitlines() if ln.strip()]
    name = None
    locality = None
    for ln in lines:
        if re.match(r"^\d{1,2}:\d{2}", ln):
            continue
        if re.search(r",\s*[A-Z]{2}\b", ln):
            locality = re.sub(r"\s+", " ", ln)
            continue
        # iMessage header always prints "Name ›"; the pill sits over blurred bubbles, so the
        # chevron is the only reliable anchor. Lines without it are noise.
        m = re.search(r"([A-Z][a-z]{1,20}(?:\s[A-Z][a-z]{1,20}){0,2})\s*[>›»\u203a)]", ln)
        if name is None and m and looks_like_contact_name(m.group(1)):
            name = m.group(1)
    return name, locality


DATE_PILL_RE = re.compile(
    r"(?:(Yesterday|Today)\s+\d{1,2}:\d{2}\s*(?:AM|PM))"
    r"|(?:\b(Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday)\s+\d{1,2}:\d{2}\s*(?:AM|PM))"
    r"|(?:\b(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s+\d{1,2},?\s+\d{4})",
    re.I,
)


def extract_thread_markers(ocr_text: str) -> str:
    found = []
    for line in (ocr_text or "").splitlines():
        line = line.strip()
        if DATE_PILL_RE.search(line) or re.match(r"^Read\s+\d", line, re.I):
            found.append(line)
    return "\n".join(found)
