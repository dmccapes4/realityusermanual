#!/usr/bin/env python3
"""Build the −08 character-sheet stills from the Paizo Core Rulebook sheet.

The sheet is the official PZO1110 PDF (assets/paizo), rendered as-is. Every value
written on it comes from the sheet blocks in src/phase2/-08.md; a box the block does
not fill stays empty. Coordinates are PDF points, top-left origin, taken from the
PDF's own text layer (pdftotext -bbox).

    .venv/bin/python tools/build_minus08_sheets.py            # all five
    .venv/bin/python tools/build_minus08_sheets.py raymora --debug
"""
from __future__ import annotations

import argparse
import math
import random
import subprocess
import sys
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parent.parent
PDF = ROOT / "assets/paizo/PZO1110-CharacterSheet.pdf"
HANDS = ROOT / "assets/fonts/hands"
CACHE = ROOT / "video/minus08/stills/sheets_src"
OUT = ROOT / "video/minus08/stills/backgrounds/act00_the_table"

DPI = 216
S = DPI / 72.0          # px per PDF point
OUT_W, OUT_H = 2560, 1440


# ── Sheet geometry (PDF points) ──────────────────────────────────────────────
# Ruled lines are measured from the rendered page; the text layer sits a little off them.
HEAD = {  # field: (x0, x1, ruled line)
    "character": (240, 368, 49.7), "alignment": (372, 417, 49.7), "player": (421, 578, 49.7),
    "class_level": (240, 417, 68.8), "deity": (421, 497, 68.8), "homeland": (501, 578, 68.8),
    "race": (240, 327, 88.2), "size": (331, 356, 88.2), "gender": (359, 389, 88.2),
    "age": (393, 417, 88.2), "height": (421, 454, 88.2), "weight": (458, 491, 88.2),
    "hair": (495, 528, 88.2), "eyes": (532, 578, 88.2),
}
ABIL_ROW = {"STR": 121, "DEX": 139, "CON": 157, "INT": 174, "WIS": 191, "CHA": 208}
ABIL_COL = {"score": 77, "mod": 100}
SAVE_ROW = {"fort": 296, "ref": 314, "will": 332}
SAVE_COL = {"total": 114, "base": 141, "ability": 169, "magic": 197, "misc": 224, "temp": 251}
BOX = {  # single boxes: (cx, cy)
    "hp": (246, 117), "init": (244, 208),
    "ac": (76, 237), "touch": (76, 264), "flat": (163, 264),
    "bab": (186, 352), "sr": (287, 352),
    "cmb": (139, 374), "cmd": (139, 402),
}
WOUNDS = (180, 133, 309, 167)
WEAPON_TOP = [422, 485, 549, 611, 674]
SKILL_TOP = {
    "Acrobatics": 194, "Appraise": 205, "Bluff": 217, "Climb": 228, "Craft 1": 239,
    "Craft 2": 251, "Craft 3": 262, "Diplomacy": 273, "Disable Device": 284,
    "Disguise": 295, "Escape Artist": 307, "Fly": 318, "Handle Animal": 329, "Heal": 341,
    "Intimidate": 352, "Knowledge (arcana)": 363, "Knowledge (dungeoneering)": 373,
    "Knowledge (engineering)": 385, "Knowledge (geography)": 397,
    "Knowledge (history)": 409, "Knowledge (local)": 420, "Knowledge (nature)": 431,
    "Knowledge (nobility)": 443, "Knowledge (planes)": 454, "Knowledge (religion)": 465,
    "Linguistics": 477, "Perception": 488, "Perform 1": 499, "Perform 2": 511,
    "Profession 1": 522, "Profession 2": 533, "Ride": 545, "Sense Motive": 556,
    "Sleight of Hand": 567, "Spellcraft": 579, "Stealth": 590, "Survival": 601,
    "Swim": 613, "Use Magic Device": 624,
}
SKILL_COL = {"total": 440, "ranks": 522, "box": 320}
COND_LINES = [665.8, 677.3]
LANG_LINES = [705.3, 716.7, 727.8]

# page 2
ACI_ROWS = [72, 90, 108, 126, 144]
ACI_COL = {"item": (35, 145), "bonus": 162, "type": 204}
GEAR_ROWS = [217.7, 231.5, 246.0, 262.5, 277.2, 290.8, 305.5, 319.5, 334.2, 347.8, 362.5,
             379.0, 393.7, 407.3, 422.0, 436.5, 451.0, 464.8, 479.3, 496.0, 510.5, 524.3,
             538.8, 552.8, 567.5, 583.8]
GEAR_X = (35, 148)
FEAT_ROWS = [213.5 + 14.67 * i for i in range(12)]
SPEC_ROWS = [417.5 + 14.67 * i for i in range(20)]
TEXT_X = (180, 410)
SPELL_ROW = [92, 110, 127, 145, 162, 179, 196, 214, 231, 248]
SPELL_COL = {"known": 439, "dc": 469, "day": 531, "bonus": 562}
SCHOOL_LINE = (428, 576, 307)
SPELL_BLOCK = {0: 331.0, 1: 393.8, 2: 457.3, 3: 511.5, 4: 559.8, 5: 601.2, 6: 635.2, 7: 669.8,
               8: 704.2, 9: 732.3}  # first ruled line under each level
SPELL_LINE_GAP = 6.85
SPELL_PT = 8.0
XP_BOX = (182, 335, 733)


# ── Hands ────────────────────────────────────────────────────────────────────
def hand(file: str):
    return HANDS / file


INK_BLUE = (28, 36, 92)
INK_BLACK = (24, 22, 26)
PENCIL = (62, 62, 68)
HL_ORANGE = (255, 150, 30)
HL_BLUE = (70, 170, 255)
HL_GREEN = (120, 230, 70)


class Pen:
    def __init__(self, img: Image.Image, font: Path, ink, seed: int, pencil=False):
        self.img = img
        self.d = ImageDraw.Draw(img, "RGBA")
        self.font = font
        self.ink = ink
        self.rng = random.Random(seed)
        self.pencil = pencil
        self._f: dict[int, ImageFont.FreeTypeFont] = {}

    def f(self, pt: float):
        px = max(6, int(pt * S))
        if px not in self._f:
            self._f[px] = ImageFont.truetype(str(self.font), px)
        return self._f[px]

    def _alpha(self):
        return self.rng.randint(195, 225) if self.pencil else self.rng.randint(225, 250)

    def text(self, x, base, s, pt=8.5, anchor="ls", ink=None, fit=None):
        """Write s with its baseline at (x, base) in points. fit = max width in points."""
        if not s:
            return
        font = self.f(pt)
        if fit:
            while pt > 4.5 and self.d.textlength(s, font=font) > fit * S:
                pt -= 0.25
                font = self.f(pt)
        jx = self.rng.uniform(-0.4, 0.4) * S
        jy = self.rng.uniform(-0.35, 0.35) * S
        col = (*(ink or self.ink), self._alpha())
        self.d.text((x * S + jx, base * S + jy), s, font=font, fill=col, anchor=anchor)

    def center(self, cx, cy, s, pt=9.0, fit=None):
        self.text(cx, cy, s, pt, anchor="mm", fit=fit)

    def line_fill(self, x0, x1, base, s, pt=8.5):
        self.text(x0 + 1.5, base - 1.6, s, pt, fit=(x1 - x0 - 3))

    def width(self, s, pt):
        return self.d.textlength(s, font=self.f(pt)) / S


# ── Marks ────────────────────────────────────────────────────────────────────
def highlight(img, x0, y0, x1, y1, color, alpha=95, seed=0):
    """Chisel highlighter stroke over a span (points)."""
    rng = random.Random(seed)
    layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    pts = []
    steps = 14
    for i in range(steps + 1):
        x = x0 + (x1 - x0) * i / steps
        pts.append((x * S, (y0 + rng.uniform(-0.3, 0.3)) * S))
    for i in range(steps, -1, -1):
        x = x0 + (x1 - x0) * i / steps
        pts.append((x * S, (y1 + rng.uniform(-0.3, 0.3)) * S))
    d.polygon(pts, fill=(*color, alpha))
    layer = layer.filter(ImageFilter.GaussianBlur(0.6 * S))
    multiply(img, layer)


def underline(img, x0, x1, y, color, width=1.6, alpha=170, seed=0):
    rng = random.Random(seed)
    layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    pts = [((x0 + (x1 - x0) * i / 10) * S, (y + rng.uniform(-0.35, 0.35)) * S) for i in range(11)]
    d.line(pts, fill=(*color, alpha), width=int(width * S), joint="curve")
    multiply(img, layer.filter(ImageFilter.GaussianBlur(0.3 * S)))


def multiply(img: Image.Image, layer: Image.Image):
    """Highlighter ink darkens paper and print; it does not cover them."""
    a = layer.split()[3]
    rgb = Image.new("RGB", img.size, (255, 255, 255))
    rgb.paste(layer.convert("RGB"), mask=a)
    base = img.convert("RGB")
    img.paste(ImageChops.multiply(base, rgb))


def eraser_ghost(img, x0, y0, x1, y1, seed=0):
    """Rubbed paper: a grey smear with graphite strokes worked back into it."""
    rng = random.Random(seed)
    layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    for _ in range(26):
        cx = rng.uniform(x0, x1) * S
        cy = rng.uniform(y0, y1) * S
        rx = rng.uniform(4, 12) * S
        ry = rng.uniform(1.5, 3.5) * S
        d.ellipse((cx - rx, cy - ry, cx + rx, cy + ry), fill=(120, 120, 126, rng.randint(22, 40)))
    for _ in range(18):
        sx = rng.uniform(x0, x1) * S
        sy = rng.uniform(y0, y1) * S
        ex = sx + rng.uniform(-6, 6) * S
        ey = sy + rng.uniform(-3, 3) * S
        d.line((sx, sy, ex, ey), fill=(85, 85, 92, rng.randint(40, 75)), width=int(0.5 * S))
    img.alpha_composite(layer.filter(ImageFilter.GaussianBlur(1.1 * S)))


def stethoscope(img, x, y, ink, scale=1.0):
    """Ear tips at (x, y); tubing down and across to a chest piece."""
    d = ImageDraw.Draw(img, "RGBA")
    col = (*ink, 230)
    w = max(2, int(1.0 * S * scale))

    def P(dx, dy):
        return ((x + dx * scale) * S, (y + dy * scale) * S)

    for dx in (0, 14):
        cx, cy = P(dx, 0)
        r = 1.4 * scale * S
        d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=col)
    d.line([P(0, 0), P(2, 9), P(7, 13)], fill=col, width=w, joint="curve")
    d.line([P(14, 0), P(12, 9), P(7, 13)], fill=col, width=w, joint="curve")
    pts = [P(7 + 40 * t, 13 + 9 * math.sin(t * math.pi) + 2 * math.sin(t * 9))
           for t in (i / 29 for i in range(30))]
    d.line(pts, fill=col, width=w, joint="curve")
    cx, cy = P(49, 13)
    for r, ww in ((4.2, w), (1.7, max(1, w // 2))):
        rr = r * scale * S
        d.ellipse((cx - rr, cy - rr, cx + rr, cy + rr), outline=col, width=ww)


def scribble_lines(pen: Pen, x0, x1, y0, n, gap=11.0):
    """Handwriting too small to read at table distance: loops, not letters."""
    d = pen.d
    rng = pen.rng
    for li in range(n):
        y = y0 + li * gap
        x = x0 + (rng.uniform(6, 14) if li == 0 else 0)
        end = x1 - rng.uniform(0, 30) if li < n - 1 else x0 + (x1 - x0) * rng.uniform(0.3, 0.7)
        pts = []
        while x < end:
            word = rng.uniform(10, 28)
            t0 = x
            while x < min(t0 + word, end):
                h = rng.uniform(1.2, 3.6)
                pts.append((x * S, (y - h) * S))
                x += rng.uniform(1.0, 1.8)
                pts.append((x * S, (y + rng.uniform(-0.3, 0.5)) * S))
                x += rng.uniform(0.6, 1.4)
            if len(pts) > 1:
                d.line(pts, fill=(*pen.ink, 205), width=max(1, int(0.45 * S)), joint="curve")
            pts = []
            x += rng.uniform(2.5, 4.5)


# ── The five sheets (from src/phase2/-08.md) ─────────────────────────────────
SHEETS: dict[str, dict] = {
    "draavio": {
        "font": "Kalam-Regular.ttf", "ink": INK_BLUE, "seed": 7,
        "head": {"character": "Draavio", "player": "Merlin",
                 "class_level": "Ranger 3 / Alchemist (mindchemist) 4", "race": "Half-orc"},
        "abil": {"STR": ("18", "+4"), "DEX": ("16", "+3"), "CON": ("14", "+2"),
                 "INT": ("22", "+6"), "WIS": ("18", "+4"), "CHA": ("10", "")},
        "hp": "68", "wounds": "3d10 + 4d8 + 14",
        "ac": "22", "touch": "13", "flat": "19",
        "saves": {"fort": "+8", "ref": "+8", "will": "+7"},
        "bab": "+6/+1", "cmb": "+10", "cmd": "23",
        "weapons": [
            {"name": "+1 keen falchion", "atk": "+11/+6", "crit": "15-20/x2",
             "dmg": "2d4+7  (2d6 under lead blades)"},
            {"name": "+1 composite longbow (+3)", "atk": "+10/+5", "crit": "x3",
             "dmg": "1d8+4", "ammo": "arrowheads can be poisoned"},
            {"name": "+1 flaming short sword", "dmg": "1d6+5 +1d6 fire"},
        ],
        "skills": {"Climb": "+7", "Craft 1": ("traps", ""), "Knowledge (religion)": "+19",
                   "Perception": "+13", "Spellcraft": "+15", "Survival": "+12"},
        "cond": ["Knowledge (religion) +19 with perfect recall",
                 "Craft (traps): to the player's fidelity, as explained to the GM"],
        "lang": [],
        "special_p1": [],
        "aci": [("+2 mithral chain shirt", "", ""), ("Heavy wooden shield", "", "")],
        "gear": ["Bag of holding (type I):", "  hammer", "  crowbar",
                 "  climbing kit (pink carabiners)", "  alchemist's kit", "  adventurer's kit",
                 "  candles x5", "  scroll case (41 scrolls)",
                 "Tome of Clear Thought +2", "  (binding: SCAPE)",
                 "Headband of Wisdom +4", "  (planned purchase)"],
        "feats": ["Power Attack (combat style, two-handed)", "Furious Focus", "Combat Reflexes",
                  "Endurance", "Track"],
        "special": [
            "Int 20, +2 inherent (Tome of Clear Thought +2).",
            "  Gift from Azazel's goat companion for providing clew. Studied.",
            "Wis 14, +4 enhancement (Headband of Wisdom +4). Planned.",
            "Ranger 3: favored enemy undead +2. Favored terrain underground +2.",
            "  Wild empathy. Caster level 0. Every ranger spell is on his list.",
            "  Simple & martial weapons, light & medium armor, shields.",
            "Alchemist 4 (mindchemist): alchemy, bombs, cognatogen.",
            "  Perfect recall: Int twice on Knowledge. Discoveries as written.",
            "  Extracts are not arcane spells; armor costs nothing.",
            "Darkvision 60 ft.",
        ],
        "ledger": [("Tree Stride", "ranger 4", "DC 5", "13 hours", "priceless",
                    "gift from the Blue Wizard", "oak allows access to farther travel")],
        "school": "Extracts (alchemist 4)",
        "spells": {1: ["lead blades x2, resist energy,", "heightened awareness x2"],
                   2: ["sickening entanglement x2, glide"]},
    },
    "pyrrhon": {
        "font": "ArchitectsDaughter-Regular.ttf", "ink": INK_BLACK, "seed": 11,
        "head": {"character": "Pyrrhon the Thrice-Kindled", "player": "Sheldon Cooper",
                 "class_level": "Wizard 7 (evocation, admixture)", "race": "Human"},
        "abil": {"STR": ("8", "-1"), "DEX": ("16", "+3"), "CON": ("14", "+2"),
                 "INT": ("20", "+5"), "WIS": ("12", "+1"), "CHA": ("10", "")},
        "hp": "45", "wounds": "7d6 + 14",
        "ac": "16", "touch": "13", "flat": "13",
        "saves": {"fort": "+4", "ref": "+5", "will": "+6"},
        "bab": "+3", "cmb": "+2", "cmd": "15",
        "weapons": [{"name": "Light crossbow", "ammo": "20 bolts"}],
        "skills": {"Knowledge (arcana)": "+15", "Knowledge (dungeoneering)": "+9",
                   "Knowledge (engineering)": "+12", "Knowledge (planes)": "+12",
                   "Knowledge (religion)": "+11", "Perception": "+8", "Spellcraft": "+15"},
        "cond": [], "lang": [],
        "aci": [("Bracers of armor +2", "", ""), ("Ring of protection +1", "", "")],
        "gear": ["Cloak of resistance +1", "Gold ring, right hand (bonded)",
                 "Spell component pouch", "Spellbook (by school, tabbed)",
                 "Light crossbow, 20 bolts",
                 "Headband of vast intelligence +2", "  (planned purchase)"],
        "feats": ["Scribe Scroll (wizard 1)", "Spell Focus (evocation)",
                  "Greater Spell Focus (evocation)", "Elemental Focus (fire)",
                  "Spell Penetration", "Greater Spell Penetration",
                  "Point-Blank Shot", "Precise Shot"],
        "special": [
            "Arcane school: evocation (admixture). Intense spells +3.",
            "Versatile evocation 8/day (3 + Int): acid, cold, electricity,",
            "  fire becomes any of the other three, descriptor and all.",
            "Opposition: necromancy, enchantment (two slots each).",
            "Bonded object: gold ring, right hand.",
            "Poison extension: any spell with poisonous properties",
            "  rides the wizard's extension.",
        ],
        "school": "Evocation (admixture) / opp. necromancy, enchantment",
        "spells": {0: ["acid splash, detect magic, prestidigitation,", "ray of frost"],
                   1: ["mage armor, magic missile x2, burning hands,", "shield, grease"],
                   2: ["scorching ray x2, glitterdust, resist energy,", "false life"],
                   3: ["fireball, stinking cloud, haste, dispel magic"],
                   4: ["wall of fire, dimension door"]},
    },
    "njala": {
        "font": "Caveat[wght].ttf", "ink": PENCIL, "seed": 23, "pencil": True, "pt": 10.5,
        "head": {"character": "Njála", "player": "Lisbeth Salander",
                 "class_level": "Witch 3 / Rogue 4", "race": "Human"},
        "abil": {"STR": ("10", ""), "DEX": ("18", "+4"), "CON": ("14", "+2"),
                 "INT": ("16", "+3"), "WIS": ("12", "+1"), "CHA": ("12", "+1")},
        "hp": "48", "wounds": "1d8 + 3d8 + 3d6 + 14",
        "ac": "18", "touch": "14", "flat": "14",
        "saves": {"fort": "+3", "ref": "+9", "will": "+5"},
        "bab": "+4", "cmb": "+4", "cmd": "18",
        "weapons": [{"name": "Short sword", "atk": "+6", "dmg": "1d6"},
                    {"name": "Short sword", "atk": "+6", "dmg": "1d6"}],
        "skills": {"Climb": "+8", "Disable Device": "+13", "Escape Artist": "+10",
                   "Knowledge (local)": "+7", "Linguistics": ("", "0"), "Perception": "+9",
                   "Sense Motive": "+5", "Sleight of Hand": "+11", "Spellcraft": "+9",
                   "Stealth": "+14"},
        "cond": ["+6/+6 = +4 base, +4 Dex, -2 second blade"],
        "lang": ["Danish (1648 dictionary)"],
        "aci": [("+1 studded leather", "", "")],
        "gear": ["Thieves' tools", "The coin", "Vial"],
        "feats": ["Extra Hex", "Weapon Finesse", "Two-Weapon Fighting"],
        "special": [
            "Rogue 4 (first level rogue; favored class rogue):",
            "  sneak attack +2d6, trapfinding, evasion,",
            "  uncanny dodge, trap sense +1.",
            "  Talents: trap spotter; combat trick.",
            "Witch 3. Patron: Deception.",
            "  Hexes: misfortune, slumber, cackle (Extra Hex).",
            "  Familiar.",
        ],
        "school": "Patron: Deception",
        "spells": {0: ["detect magic, guidance, message, stabilize"],
                   1: ["ill omen, mage armor, true strike"]},
    },
    "merit": {
        "font": "Cedarville-Cursive.ttf", "ink": INK_BLACK, "seed": 31, "pt": 9.0,
        "head": {"character": "Merit of the Ford", "player": "the Witch of the Rivers",
                 "class_level": "Paladin 7", "race": "Gnome", "size": "Small"},
        "abil": {"STR": ("16", "+3"), "DEX": ("12", "+1"), "CON": ("16", "+3"),
                 "INT": ("10", ""), "WIS": ("12", "+1"), "CHA": ("16", "+3")},
        "hp": "67", "wounds": "7d10 + 21",
        "ac": "23", "touch": "11", "flat": "22",
        "saves": {"fort": "+11", "ref": "+6", "will": "+9"},
        "bab": "+7/+2", "cmb": "+10", "cmd": "21",
        "weapons": [{"name": "+1 longsword", "atk": "+9/+4", "crit": "19-20/x2", "dmg": "1d8+4"}],
        "skills": {"Climb": None, "Diplomacy": "+13", "Heal": "+5", "Knowledge (religion)": "+10",
                   "Perception": ("+1", "0"), "Sense Motive": "+11"},
        "class_skills": ["Climb"],
        "cond": ["Smite: + Cha to attack, + paladin level to damage"],
        "lang": [],
        "aci": [("+1 full plate", "", ""), ("+1 heavy steel shield", "", "")],
        "gear": ["Ring of climbing", "Bag of holding"],
        "feats": ["Weapon Focus (longsword)", "Shield Focus", "Power Attack",
                  "Extra Lay on Hands"],
        "special": [
            "Fey Thoughts (in place of racial weapon familiarity).",
            "Aura of good. Detect evil at will. Smite evil 3/day.",
            "Divine grace. Lay on hands 3d6, 6/day.",
            "Aura of courage. Divine health.",
            "Channel positive energy 4d6, 3/day (two lay on hands).",
            "Mercy: fatigued, sickened.",
            "Divine bond: the longsword.",
        ],
        "code_on_back": True,
        "school": "",
        "spells": {},
    },
    "raymora": {
        "font": "GochiHand-Regular.ttf", "ink": INK_BLUE, "seed": 43, "pt": 9.5,
        "head": {"character": "Joey Tribianni", "player": "Raymora the Dragon",
                 "class_level": "Druid 7", "race": "Human"},
        "abil": {"STR": ("10", ""), "DEX": ("12", "+1"), "CON": ("14", "+2"),
                 "INT": ("8", "-1"), "WIS": ("18", "+4"), "CHA": ("11", "")},
        "hp": "52", "wounds": "7d8 + 14",
        "ac": "15", "touch": "11", "flat": "14",
        "saves": {"fort": "+7", "ref": "+3", "will": "+9"},
        "bab": "+5", "cmb": "+5", "cmd": "16",
        "weapons": [{"name": "Scimitar"}, {"name": "Sling"}],
        "skills": {"Handle Animal": "+4", "Heal": ("+17", "7"), "Knowledge (nature)": "+3",
                   "Perception": "+8", "Survival": "+10"},
        "class_skills": ["Heal"],
        "cond": [], "lang": [],
        "aci": [("Hide armor", "", "")],
        "gear": ["Holly and mistletoe", "Healer's kit", "Healer's kit", "Healer's kit"],
        "feats": ["Skill Focus (Heal)", "Self-Sufficient", "Toughness", "", ""],
        "special": [
            "Nature bond:",
            "Wild shape: yes. 2/day. animals",
        ],
        "school": "",
        "spells": {0: ["create water, detect magic, detect poison, guidance"],
                   1: ["calm animals, charm animal, cure light wounds,",
                       "detect animals or plants, endure elements"],
                   2: ["animal messenger, animal trance, barkskin"],
                   3: ["call lightning, contagion, cure moderate wounds"],
                   4: ["air walk"]},
        "doctor": True,
    },
}


# ── Rendering ────────────────────────────────────────────────────────────────
PDF_ZIP = "https://downloads.paizo.com/PZOCUP009E_PathfinderRPG_RecordSheets.zip"


def fetch_pdf():
    import io
    import urllib.request
    import zipfile
    req = urllib.request.Request(PDF_ZIP, headers={"User-Agent": "Mozilla/5.0"})
    data = urllib.request.urlopen(req, timeout=60).read()
    PDF.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(io.BytesIO(data)) as z:
        PDF.write_bytes(z.read(PDF.name))


def page_images() -> list[Image.Image]:
    CACHE.mkdir(parents=True, exist_ok=True)
    if not PDF.exists():
        fetch_pdf()
    pages = [CACHE / f"pzo1110-{DPI}-{i}.png" for i in (1, 2)]
    if not all(p.exists() for p in pages):
        subprocess.run(["pdftoppm", "-r", str(DPI), "-png", str(PDF), str(CACHE / f"pzo1110-{DPI}")],
                       check=True)
    return [Image.open(p).convert("RGBA") for p in pages]


def fill_page1(img, sh, pen: Pen):
    pt = sh.get("pt", 8.5)
    for k, v in sh["head"].items():
        x0, x1, b = HEAD[k]
        pen.line_fill(x0, x1, b, v, pt + 1)
    for ab, (score, mod) in sh["abil"].items():
        pen.center(ABIL_COL["score"], ABIL_ROW[ab], score, pt + 1)
        pen.center(ABIL_COL["mod"], ABIL_ROW[ab], mod, pt + 1)
    pen.center(*BOX["hp"], sh["hp"], pt + 1.5)
    x0, y0, x1, y1 = WOUNDS
    pen.text(x0 + 3, y0 + 10, sh["wounds"], pt - 0.5, fit=(x1 - x0 - 6))
    for k in ("ac", "touch", "flat", "bab", "cmb", "cmd"):
        if sh.get(k):
            pen.center(*BOX[k], sh[k], pt + 0.5, fit=34)
    for k, v in sh["saves"].items():
        pen.center(SAVE_COL["total"], SAVE_ROW[k], v, pt + 0.5)
    for i, w in enumerate(sh["weapons"][:5]):
        top = WEAPON_TOP[i]
        pen.line_fill(26, 210, top + 26, w.get("name", ""), pt)
        pen.center(240, top + 21, w.get("atk", ""), pt - 0.5, fit=46)
        pen.center(292, top + 21, w.get("crit", ""), pt - 1, fit=30)
        pen.line_fill(26, 58, top + 51, w.get("type", ""), pt - 1)
        pen.line_fill(108, 205, top + 51, w.get("ammo", ""), pt - 1.5)
        pen.line_fill(207, 310, top + 51, w.get("dmg", ""), pt - 1)
    for name, val in sh["skills"].items():
        top = SKILL_TOP[name]
        base = top + 9
        if name.startswith("Craft") and isinstance(val, tuple) and not val[1]:
            pen.line_fill(347, 412, base, val[0], pt - 1)
            continue
        total, ranks = (val, "") if not isinstance(val, tuple) else val
        if total:
            pen.center(SKILL_COL["total"], base - 3.5, total, pt - 0.5, fit=22)
        if ranks:
            pen.center(SKILL_COL["ranks"], base - 3.5, ranks, pt - 0.5, fit=20)
    for name in sh.get("class_skills", []):
        top = SKILL_TOP[name]
        cx, cy = SKILL_COL["box"], top + 5.5
        pen.d.line([((cx - 2) * S, cy * S), ((cx - 0.5) * S, (cy + 2) * S), ((cx + 3) * S, (cy - 3) * S)],
                   fill=(*pen.ink, 230), width=int(0.8 * S))
    for i, s in enumerate(sh["cond"][:len(COND_LINES)]):
        pen.line_fill(318, 578, COND_LINES[i], s, pt - 1)
    for i, s in enumerate(sh["lang"][:len(LANG_LINES)]):
        pen.line_fill(318, 578, LANG_LINES[i], s, pt)


def fill_page2(img, sh, pen: Pen):
    pt = sh.get("pt", 8.5)
    for i, (item, bonus, typ) in enumerate(sh["aci"][:5]):
        x0, x1 = ACI_COL["item"]
        pen.line_fill(x0, x1, ACI_ROWS[i] + 3, item, pt - 0.5)
    for i, g in enumerate(sh["gear"][:len(GEAR_ROWS)]):
        pen.line_fill(*GEAR_X, GEAR_ROWS[i], g, pt - 1)
    for i, ft in enumerate(sh["feats"][:len(FEAT_ROWS)]):
        pen.line_fill(*TEXT_X, FEAT_ROWS[i], ft, pt)
    rows = SPEC_ROWS
    for i, sp in enumerate(sh["special"][:len(rows)]):
        pen.line_fill(*TEXT_X, rows[i], sp, pt - 1)
    if sh.get("school"):
        pen.line_fill(*SCHOOL_LINE, sh["school"], pt - 1.5)
    for lvl, lines in sh["spells"].items():
        for j, s in enumerate(spell_lines(pen, lines)):
            pen.line_fill(428, 578, spell_rule(lvl, j), s, SPELL_PT)


def spell_rule(lvl: int, j: int) -> float:
    """Every second ruled line, so the hand can be read."""
    return SPELL_BLOCK[lvl] + 2 * j * SPELL_LINE_GAP


def spell_lines(pen: Pen, lines: list[str]) -> list[str]:
    out, cur = [], ""
    for w in " ".join(lines).split():
        nxt = f"{cur} {w}".strip()
        if cur and pen.width(nxt, SPELL_PT) > 144:
            out.append(cur)
            cur = w
        else:
            cur = nxt
    return out + ([cur] if cur else [])


def marks(name, sh, p1, p2, pen1: Pen, pen2: Pen):
    pt = sh.get("pt", 8.5)
    if name == "draavio":
        # The scroll ledger, under the special abilities, in the hand that wrote PLAYER.
        n = len(sh["special"])
        y = SPEC_ROWS[n + 1]
        pen2.line_fill(*TEXT_X, y, "Scroll case: 41 scrolls. On top:", pt - 1)
        for row in sh["ledger"]:
            spell, lvl, dc, dur, cost, origin, notes = row
            pen2.line_fill(*TEXT_X, y + 14.6, f"{spell} | {lvl} | {dc} | {dur} | cost: {cost}", pt - 1)
            pen2.line_fill(*TEXT_X, y + 29.2, f"  | origin: {origin}", pt - 1)
            pen2.line_fill(*TEXT_X, y + 43.8, f"  | notes: {notes}", pt - 1)
    if name == "pyrrhon":
        def span(lvl, phrase):
            ls = spell_lines(pen2, sh["spells"][lvl])
            k = next(i for i, ln in enumerate(ls) if phrase in ln)
            x = 429.5 + pen2.width(ls[k].split(phrase)[0], SPELL_PT)
            return x, x + pen2.width(phrase, SPELL_PT), spell_rule(lvl, k) - 1.6
        # Stinking cloud: underlined in all three highlighters.
        x0, x1, y = span(3, "stinking cloud")
        underline(p2, x0 - 0.5, x1 + 1, y + 1.3, HL_ORANGE, 1.5, 190, seed=2)
        underline(p2, x0, x1 + 1.5, y + 2.9, HL_BLUE, 1.5, 190, seed=3)
        underline(p2, x0 - 1, x1 + 0.5, y + 4.5, HL_GREEN, 1.5, 200, seed=4)
        # False life is necromancy: he wrote the opposition cost in orange highlighter.
        x0, x1, y = span(2, "false life")
        pen2.text(x1 + 3, y, "opposition: 2 slots", SPELL_PT - 0.5, ink=(232, 118, 10), fit=576 - x1 - 3)
        # The three kindlings, in the margin beside the feats.
        for i, s in enumerate(["once for the school", "once for the fire descriptor",
                               "once for versatile evocation"]):
            pen2.text(340, FEAT_ROWS[i] - 2, s, pt - 1.5, fit=70)
        pen2.d.text((334 * S, (FEAT_ROWS[0] - 10) * S), "{", font=pen2.f(30), fill=(*INK_BLACK, 200), anchor="lt")
    if name == "njala":
        # The Witch/Rogue split is where the eraser worked.
        eraser_ghost(p1, 238, 58, 300, 68, seed=7)
        eraser_ghost(p2, 180, SPEC_ROWS[4] - 9, 330, SPEC_ROWS[6] + 2, seed=8)
        eraser_ghost(p2, 427, SPELL_BLOCK[0] - 8, 560, SPELL_BLOCK[1] + 8, seed=9)
    if name == "merit":
        # Code of conduct: on the back, in the same hand as the front.
        y = SPEC_ROWS[len(sh["special"]) + 1]
        pen2.line_fill(*TEXT_X, y, "Code of conduct", pt + 0.5)
        scribble_lines(pen2, 182, 408, y + 14.6, 7, gap=14.6)
    if name == "raymora":
        # He drew a stethoscope over the nature bond line.
        y = SPEC_ROWS[0]
        stethoscope(p2, 228, y - 11, sh["ink"], 1.6)
        # DOCTOR, in the margin, where the sheet has no line for it.
        font = ImageFont.truetype(str(hand("Kalam-Bold.ttf")), int(22 * S))
        txt = Image.new("RGBA", (int(120 * S), int(40 * S)), (0, 0, 0, 0))
        ImageDraw.Draw(txt).text((4 * S, 2 * S), "DOCTOR", font=font, fill=(*INK_BLUE, 235))
        txt = txt.rotate(-4, resample=Image.BICUBIC, expand=True)
        p1.alpha_composite(txt, (int(440 * S), int(738 * S)))


def table_bg(w, h, seed=5) -> Image.Image:
    """A dark oak tabletop under a warm lamp; no props."""
    rng = random.Random(seed)
    img = Image.new("RGB", (w, h), (58, 36, 22))
    d = ImageDraw.Draw(img)
    for y in range(0, h, 3):
        shade = int(10 * math.sin(y * 0.013 + rng.uniform(-0.2, 0.2)) + rng.uniform(-6, 6))
        d.line([(0, y), (w, y + rng.randint(-8, 8))], fill=(62 + shade, 39 + shade // 2, 23 + shade // 3), width=3)
    img = img.filter(ImageFilter.GaussianBlur(1.5))
    vign = Image.new("L", (w, h), 0)
    vd = ImageDraw.Draw(vign)
    for i in range(40):
        a = int(255 * (i / 40))
        vd.ellipse((-w * 0.25 + i * w * 0.012, -h * 0.35 + i * h * 0.014,
                    w * 1.25 - i * w * 0.012, h * 1.35 - i * h * 0.014), fill=a)
    vign = vign.filter(ImageFilter.GaussianBlur(80))
    dark = Image.new("RGB", (w, h), (14, 9, 6))
    return Image.composite(img, dark, vign)


def compose(p1, p2, seed) -> Image.Image:
    rng = random.Random(seed)
    bg = table_bg(OUT_W, OUT_H, seed)
    ph = OUT_H - 175          # the speaker caption keeps the bottom band
    top = 30
    pw = int(p1.width * ph / p1.height)
    gap = 70
    x0 = (OUT_W - (2 * pw + gap)) // 2
    for i, p in enumerate((p1, p2)):
        im = p.resize((pw, ph), Image.LANCZOS)
        paper = Image.new("RGB", im.size, (244, 234, 212))
        rgb = ImageChops.multiply(im.convert("RGB"), paper)
        im = Image.merge("RGBA", (*rgb.split(), im.split()[3]))
        ang = rng.uniform(-1.4, 1.4)
        rot = im.rotate(ang, resample=Image.BICUBIC, expand=True)
        shadow = Image.new("RGBA", rot.size, (0, 0, 0, 0))
        shadow.paste((0, 0, 0, 150), mask=rot.split()[3])
        shadow = shadow.filter(ImageFilter.GaussianBlur(14))
        x = x0 + i * (pw + gap) - (rot.width - pw) // 2
        y = top - (rot.height - ph) // 2
        bg.paste(shadow, (x + 10, y + 14), shadow)
        bg.paste(rot, (x, y), rot)
    return bg


def build(name: str, debug=False) -> Path:
    sh = SHEETS[name]
    p1, p2 = page_images()
    seed = sh["seed"]
    pen1 = Pen(p1, hand(sh["font"]), sh["ink"], seed, sh.get("pencil", False))
    pen2 = Pen(p2, hand(sh["font"]), sh["ink"], seed + 1, sh.get("pencil", False))
    fill_page1(p1, sh, pen1)
    fill_page2(p2, sh, pen2)
    marks(name, sh, p1, p2, pen1, pen2)
    if debug:
        p1.convert("RGB").save(CACHE / f"debug_{name}_p1.png")
        p2.convert("RGB").save(CACHE / f"debug_{name}_p2.png")
    out = OUT / f"sheet_{name}.png"
    compose(p1, p2, seed).save(out)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("names", nargs="*", default=list(SHEETS))
    ap.add_argument("--debug", action="store_true", help="also save each filled page at full size")
    args = ap.parse_args()
    for n in args.names:
        print(build(n, args.debug))


if __name__ == "__main__":
    sys.exit(main())
