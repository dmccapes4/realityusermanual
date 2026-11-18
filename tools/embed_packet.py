#!/usr/bin/env python3
"""
Companion packet PDF: a one-page file list plus embedded inner PDFs.

This is what a PDF can actually do. It is not a browser. Acrobat and
some readers expose a paperclip / attachments pane. Chrome often will
not open the inners from a click. The desk browser is the working UI.

  .venv/bin/python tools/embed_packet.py
"""

from __future__ import annotations

from pathlib import Path

from pypdf import PdfReader, PdfWriter
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas

BASE = Path(__file__).resolve().parent.parent
DESK = BASE / "manuscripts" / "how_to_fly_ajp"
PKG = DESK / "package" / "how_to_fly_aerodynamic_plefr_submission_package"
OUT = DESK / "RECEIVED_PACKET.pdf"

ATTACH = [
    ("01_Main_Manuscript_HOW_TO_FLY.pdf", PKG / "Main_Manuscript_HOW_TO_FLY.pdf"),
    ("02_Supporting_Information_HOW_TO_FLY.pdf", PKG / "Supporting_Information_HOW_TO_FLY.pdf"),
    ("05_OPERATOR_SEED_HOW_TO_FLY.pdf", PKG / "Supplementary" / "OPERATOR_SEED_HOW_TO_FLY.pdf"),
    ("prior_MANIFESTO_MOTHER_EARTH_GOVERNED_FIELD.pdf", DESK / "MANIFESTO_MOTHER_EARTH_GOVERNED_FIELD.pdf"),
]


def cover_page(path: Path, names: list[str]) -> None:
    c = canvas.Canvas(str(path), pagesize=letter)
    w, h = letter
    c.setFillColorRGB(0.10, 0.10, 0.18)
    c.setFont("Times-Bold", 16)
    c.drawString(1.0 * inch, h - 1.1 * inch, "Received packet — How to Fly")
    c.setFont("Times-Italic", 10)
    c.drawString(1.0 * inch, h - 1.35 * inch, "AJP desk copy. Inner PDFs are attachments, not a browser.")
    c.setFont("Times-Roman", 11)
    y = h - 1.9 * inch
    c.drawString(1.0 * inch, y, "Open the paperclip / attachments pane in a reader that has one.")
    y -= 18
    c.drawString(1.0 * inch, y, "Or run:  .venv/bin/python tools/desk_browser.py")
    y -= 32
    c.setFont("Times-Bold", 11)
    c.drawString(1.0 * inch, y, "Embedded files")
    y -= 18
    c.setFont("Times-Roman", 11)
    for name in names:
        c.drawString(1.15 * inch, y, name)
        y -= 16
    c.setFont("Times-Italic", 9)
    c.drawString(1.0 * inch, 0.75 * inch, "Not refereed. Paths not rewritten.")
    c.save()


def main() -> None:
    DESK.mkdir(parents=True, exist_ok=True)
    present = [(n, p) for n, p in ATTACH if p.exists()]
    missing = [n for n, p in ATTACH if not p.exists()]
    tmp = DESK / "_packet_cover.pdf"
    cover_page(tmp, [n for n, _ in present])
    writer = PdfWriter()
    writer.append(PdfReader(str(tmp)))
    for name, path in present:
        writer.add_attachment(name, path.read_bytes())
        print(f"  attached {name}  {path.stat().st_size} bytes")
    with OUT.open("wb") as fh:
        writer.write(fh)
    tmp.unlink(missing_ok=True)
    print(f"Wrote {OUT}  ({OUT.stat().st_size} bytes)")
    if missing:
        print("missing:", ", ".join(missing))


if __name__ == "__main__":
    main()
