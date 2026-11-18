#!/usr/bin/env python3
"""Compose the hallway cat-sign PNG: LEGO-C4 fusion aesthetic + preface text.

Base texture: web/hall/assets/cat_sign_base.png (generated)
Output:       web/hall/assets/cat_sign.png (tall scrollable)
              web/hall/assets/cat_sign_sections/*.png (per-section crops)
"""

from __future__ import annotations

import textwrap
from pathlib import Path

from PIL import Image, ImageDraw, ImageEnhance, ImageFont, ImageOps

BASE = Path(__file__).resolve().parent.parent
ASSETS = BASE / "web" / "hall" / "assets"
SRC_MD = BASE / "src" / "002_preface" / "002_02_preface_i.md"
BASE_TEX = ASSETS / "cat_sign_base.png"
OUT = ASSETS / "cat_sign.png"
SEC_DIR = ASSETS / "cat_sign_sections"

W = 900
MARGIN = 56
TEXT_W = W - 2 * MARGIN

SECTIONS = [
    (
        "I",
        "THE INTERNET PHENOMENON",
        "There is a long-standing, near-universal internet rule:\n\n"
        "DO NOT MESS WITH CATS.\n\n"
        "This rule is not written anywhere formal, yet violations reliably "
        "trigger disproportionate backlash. Across platforms, cultures, and "
        "eras of the internet, mistreating cats — real or perceived — produces "
        "immediate, coordinated, and often relentless response.\n\n"
        "Outrage. Investigative crowdsourcing. Doxxing. Platform bans. "
        "Reputational destruction.\n\n"
        "The internet will forgive many things. It does not forgive cruelty to cats.",
    ),
    (
        "II",
        "WHY CATS, SPECIFICALLY?",
        "Cats occupy a unique position in the abstraction stack:\n\n"
        "• Small but not submissive\n"
        "• Domesticated but not obedient\n"
        "• Emotionally legible but not compliant\n"
        "• Present but not owned\n\n"
        "Cats resist instrumentalization. They tolerate humans conditionally.\n\n"
        "This makes cats powerful symbols of autonomy, consent, boundary-setting, "
        "and non-coercive coexistence.",
    ),
    (
        "III",
        "CLASSIC CAT VIDEOS",
        "These aren't just cute. They are boundary lessons disguised as humor.\n\n"
        "Cats asserting limits — swatting a hand that went too far.\n"
        "Cats surviving incompetence — humans failing, cats adapting.\n"
        "Cats choosing affection — delayed trust; earned closeness.\n"
        "Cats remaining unimpressed — refusal to perform.\n\n"
        "The humor lands because the cat never loses dignity.\n"
        "That dignity is the invariant.",
    ),
    (
        "IV",
        "AQUE TIBABE (DEADLY SERIOUS)",
        "Aque Tibabe is an inter-planar traveler who takes the form of cats.\n\n"
        "For the record:\n"
        "• This is a measured fact.\n"
        "• This is a mnemonic device.\n"
        "• This is humor with behavioral teeth.\n\n"
        '"Respect this being. You do not know what it carries."\n\n'
        "Aque Tibabe guides participants by haunting their dreams.\n"
        "That pause is the point.",
    ),
    (
        "V",
        "WHY THE JOKE STUCK",
        "The joke persisted because it worked. It compressed several truths:\n\n"
        "• You cannot assume interiority\n"
        "• You cannot rush consent\n"
        "• You should not dominate what you don't understand\n"
        "• Small beings still have agency\n\n"
        "The internet reinforced the joke by independently arriving at the same "
        "behavioral conclusion: mistreat cats → consequences.",
    ),
    (
        "VI",
        "THE ABSTRACTION SPECTRUM",
        "On the abstraction stack, cats sit in a critical zone:\n\n"
        "Object abstraction → Cat resists use\n"
        "Tool abstraction → Cat withdraws\n"
        "Narrative abstraction → Cat remains opaque\n"
        "Moral abstraction → Internet intervenes\n\n"
        "Cats prevent abstraction collapse by refusing to be reduced.\n"
        "They function as sentinel nodes for respectful modeling.",
    ),
    (
        "VII",
        "THE OPERATIONAL RULE",
        "IF YOU CANNOT RESPECT A CAT'S AGENCY,\n"
        "YOU CANNOT BE TRUSTED WITH MORE COMPLEX SYSTEMS.\n\n"
        "This applies to: people, users, patients, datasets,\n"
        "collaborators, models.\n\n"
        "Cats are not special because they are mystical.\n"
        "They are special because they expose coercion instantly.",
    ),
    (
        "VIII",
        "CLOSING",
        "The joke works because it is funny and correct at the same time.\n\n"
        "You don't mess with cats\n"
        "because cats are a test.\n\n"
        "And the internet, collectively, has already graded it.",
    ),
]


def font(size: int, bold: bool = False) -> ImageFont.ImageFont:
    candidates = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
        "/usr/share/fonts/truetype/freefont/FreeSansBold.ttf" if bold else "/usr/share/fonts/truetype/freefont/FreeSans.ttf",
    ]
    for path in candidates:
        if Path(path).exists():
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()


def tile_base(height: int) -> Image.Image:
    if BASE_TEX.exists():
        tex = Image.open(BASE_TEX).convert("RGB")
        # Crop center content area and stretch vertically by tiling
        tex = ImageOps.fit(tex, (W, max(height // 3, 600)), Image.Resampling.LANCZOS)
        canvas = Image.new("RGB", (W, height), (28, 26, 18))
        y = 0
        while y < height:
            canvas.paste(tex, (0, y))
            y += tex.height - 40  # overlap seam
        # Darken for text readability
        canvas = ImageEnhance.Brightness(canvas).enhance(0.55)
        canvas = ImageEnhance.Contrast(canvas).enhance(1.15)
        return canvas
    # Fallback: procedural hazard board
    canvas = Image.new("RGB", (W, height), (32, 30, 20))
    d = ImageDraw.Draw(canvas)
    for yy in range(0, height, 48):
        for i in range(0, W, 48):
            if ((yy // 48) + (i // 48)) % 2 == 0:
                d.rectangle([i, yy, i + 48, yy + 48], fill=(55, 48, 18))
    # stripe band top/bottom
    for yy in (0, height - 36):
        for i in range(-height, W, 28):
            d.polygon([(i, yy), (i + 14, yy), (i + 28, yy + 36), (i + 14, yy + 36)], fill=(210, 170, 40))
    return canvas


def wrap(draw: ImageDraw.ImageDraw, text: str, fnt: ImageFont.ImageFont, width: int) -> list[str]:
    lines: list[str] = []
    for para in text.split("\n"):
        if not para.strip():
            lines.append("")
            continue
        # manual wrap by pixel width
        words = para.split(" ")
        cur = ""
        for w in words:
            trial = (cur + " " + w).strip()
            if draw.textlength(trial, font=fnt) <= width:
                cur = trial
            else:
                if cur:
                    lines.append(cur)
                cur = w
        if cur:
            lines.append(cur)
    return lines


def draw_frame(d: ImageDraw.ImageDraw, y0: int, y1: int) -> None:
    # brick stud corners
    d.rectangle([18, y0, W - 18, y1], outline=(210, 175, 55), width=4)
    d.rectangle([26, y0 + 8, W - 26, y1 - 8], outline=(90, 80, 40), width=2)
    for cx, cy in [(40, y0 + 22), (W - 40, y0 + 22), (40, y1 - 22), (W - 40, y1 - 22)]:
        d.ellipse([cx - 7, cy - 7, cx + 7, cy + 7], fill=(180, 150, 40), outline=(40, 35, 15))


def compose() -> None:
    ASSETS.mkdir(parents=True, exist_ok=True)
    SEC_DIR.mkdir(parents=True, exist_ok=True)

    # Measure first on a scratch image
    scratch = Image.new("RGB", (W, 200), (0, 0, 0))
    sd = ImageDraw.Draw(scratch)
    title_f = font(34, bold=True)
    head_f = font(22, bold=True)
    body_f = font(18)
    small_f = font(14)

    blocks: list[tuple[str, str, list[str], int]] = []
    total_h = 220  # header
    for num, title, body in SECTIONS:
        lines = wrap(sd, body, body_f, TEXT_W)
        h = 70 + len(lines) * 26 + 48
        blocks.append((num, title, lines, h))
        total_h += h + 24
    total_h += 120  # footer hazard band

    canvas = tile_base(total_h)
    d = ImageDraw.Draw(canvas)

    # Header plate
    d.rectangle([MARGIN - 20, 40, W - MARGIN + 20, 190], fill=(18, 16, 10), outline=(220, 180, 50), width=3)
    d.text((MARGIN, 55), "FACILITY NOTICE · CAT PROTOCOL", font=small_f, fill=(210, 175, 55))
    d.text((MARGIN, 85), "HOW TO NOT MESS WITH CATS", font=title_f, fill=(240, 220, 160))
    d.text(
        (MARGIN, 135),
        "Nuclear-fusion training plaque · LEGO / C4 lattice aesthetic\n"
        "Cultural invariant + disclosure of inter-planar presence",
        font=small_f,
        fill=(180, 160, 100),
    )

    y = 220
    section_crops: list[tuple[str, int, int]] = []
    for num, title, lines, h in blocks:
        y0 = y
        draw_frame(d, y, y + h)
        d.rectangle([36, y + 14, W - 36, y + h - 14], fill=(12, 11, 8, ))
        # PIL RGB — fill solid
        d.rectangle([36, y + 14, W - 36, y + h - 14], fill=(14, 13, 9))
        d.text((MARGIN, y + 28), f"SECTION {num}", font=small_f, fill=(210, 170, 40))
        d.text((MARGIN, y + 52), title, font=head_f, fill=(235, 215, 150))
        ty = y + 90
        for line in lines:
            d.text((MARGIN, ty), line, font=body_f, fill=(200, 190, 165))
            ty += 26
        section_crops.append((num, y0, y + h))
        y += h + 24

    # Footer
    d.rectangle([0, total_h - 70, W, total_h], fill=(200, 160, 35))
    d.text(
        (MARGIN, total_h - 48),
        "END OF PLAQUE — SCROLL COMPLETE TO FACE DECLARATION FIELDS",
        font=head_f,
        fill=(20, 16, 8),
    )

    canvas.save(OUT, "PNG", optimize=True)
    print(f"wrote {OUT} ({OUT.stat().st_size // 1024} KB) {canvas.size}")

    for num, y0, y1 in section_crops:
        crop = canvas.crop((0, max(0, y0 - 8), W, min(total_h, y1 + 8)))
        dest = SEC_DIR / f"section_{num}.png"
        crop.save(dest, "PNG", optimize=True)
        print(f"  {dest.name} {crop.size}")


if __name__ == "__main__":
    compose()
