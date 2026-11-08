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
SKILL_COL = {"total": 440, "ability": 490, "ranks": 522, "misc": 552, "box": 320}
# Component boxes, centres measured from the rendered page.
AC_COL = {"armor": 125.5, "shield": 154.5, "dex": 183.5, "size": 212, "natural": 241,
          "deflection": 270, "misc": 299}
SAVE_PART = {"base": 141, "ability": 169, "magic": 197, "misc": 224.5}
CMB_COL = {"bab": 170, "str": 200, "size": 230}
CMD_COL = {"bab": 170, "str": 200, "dex": 230, "size": 261}
INIT_COL = {"dex": 272, "misc": 299}
SPEED = {"base": (378, 116), "armor": (455, 116)}
WEAPON_COL = {"type": (25, 58), "range": (58, 105.7), "ammo": (105.7, 206.7), "dmg": (206.7, 310)}
COND_LINES = [665.8, 677.3]
LANG_LINES = [705.3, 716.7, 727.8]

# page 2
ACI_ROWS = [78, 96, 114, 132, 150]
ACI_TOTAL = 166
ACI_COL = {"item": (35, 145), "bonus": 163, "type": 204, "acp": 253, "asf": 300, "wt": 341,
           "props": (361, 408)}
GEAR_WT = 157.6
GEAR_ROWS = [217.7, 231.5, 246.0, 262.5, 277.2, 290.8, 305.5, 319.5, 334.2, 347.8, 362.5,
             379.0, 393.7, 407.3, 422.0, 436.5, 451.0, 464.8, 479.3, 496.0, 510.5, 524.3,
             538.8, 552.8, 567.5, 583.8]
GEAR_X = (35, 148)
FEAT_ROWS = [213.5 + 14.67 * i for i in range(12)]
SPEC_ROWS = [417.5 + 14.67 * i for i in range(20)]
TEXT_X = (180, 410)
SPELL_ROW = [93.2, 109.5, 127.5, 144.2, 162.5, 178.9, 196.9, 213.7, 231.9, 248.5]
SPELL_COL = {"known": 439, "dc": 469, "day": 531, "bonus": 561}
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


# ── What a player at the table works out (Pathfinder 1e Core Rulebook) ───────
# The totals above are the sheet blocks. The parts below are the arithmetic a player writes
# beside them: class base saves, BAB, size, armor, skill columns, spells per day.
# Where a part does not add up to the block's total, the total stands and the box that
# would balance it stays empty.
SKILL_ABIL = {
    "Acrobatics": "DEX", "Appraise": "INT", "Bluff": "CHA", "Climb": "STR", "Craft 1": "INT",
    "Craft 2": "INT", "Craft 3": "INT", "Diplomacy": "CHA", "Disable Device": "DEX",
    "Disguise": "CHA", "Escape Artist": "DEX", "Fly": "DEX", "Handle Animal": "CHA",
    "Heal": "WIS", "Intimidate": "CHA", "Linguistics": "INT", "Perception": "WIS",
    "Perform 1": "CHA", "Perform 2": "CHA", "Profession 1": "WIS", "Profession 2": "WIS",
    "Ride": "DEX", "Sense Motive": "WIS", "Sleight of Hand": "DEX", "Spellcraft": "INT",
    "Stealth": "DEX", "Survival": "WIS", "Swim": "STR", "Use Magic Device": "CHA",
}
SKILL_ABIL.update({k: "INT" for k in SKILL_TOP if k.startswith("Knowledge")})
TRAINED_ONLY = {"Disable Device", "Handle Animal", "Linguistics", "Profession 1", "Profession 2",
                "Sleight of Hand", "Spellcraft", "Use Magic Device"} | \
               {k for k in SKILL_TOP if k.startswith("Knowledge")}
K = "Knowledge ({})".format
CLASS_SKILLS = {
    "ranger": {"Climb", "Craft 1", "Handle Animal", "Heal", "Intimidate", K("dungeoneering"),
               K("geography"), K("nature"), "Perception", "Profession 1", "Ride", "Spellcraft",
               "Stealth", "Survival", "Swim"},
    "alchemist": {"Appraise", "Craft 1", "Disable Device", "Fly", "Heal", K("arcana"), K("nature"),
                  "Perception", "Profession 1", "Sleight of Hand", "Spellcraft", "Survival",
                  "Use Magic Device"},
    "wizard": {"Appraise", "Craft 1", "Fly", "Linguistics", "Profession 1", "Spellcraft"} |
              {k for k in SKILL_TOP if k.startswith("Knowledge")},
    "rogue": {"Acrobatics", "Appraise", "Bluff", "Climb", "Craft 1", "Diplomacy", "Disable Device",
              "Disguise", "Escape Artist", "Intimidate", K("dungeoneering"), K("local"),
              "Linguistics", "Perception", "Perform 1", "Profession 1", "Sense Motive",
              "Sleight of Hand", "Stealth", "Swim", "Use Magic Device"},
    "witch": {"Craft 1", "Fly", "Heal", "Intimidate", K("arcana"), K("history"), K("nature"),
              K("planes"), "Profession 1", "Spellcraft", "Use Magic Device"},
    "paladin": {"Craft 1", "Diplomacy", "Handle Animal", "Heal", K("nobility"), K("religion"),
                "Profession 1", "Ride", "Sense Motive", "Spellcraft", "Climb"},  # Climb: Fey Thoughts
    "druid": {"Climb", "Craft 1", "Fly", "Handle Animal", "Heal", K("geography"), K("nature"),
              "Perception", "Profession 1", "Ride", "Spellcraft", "Survival", "Swim"},
}

DETAIL: dict[str, dict] = {
    "draavio": {
        "style": "ledger", "levels": {"ranger": 3, "alchemist": 4},
        "head": {"size": "M", "gender": "M"},
        "speed": ("30", "30"), "init": ("+3", "+3", ""),
        "acp": {"armor": "+6", "shield": "+2", "dex": "+3"},
        # Rules give Fort 7+2, Ref 7+3, Will 2+4; the block's +8/+8/+7 stand.
        "saveparts": {"fort": ("+7", "+2", "", ""), "ref": ("+7", "+3", "", ""),
                      "will": ("+2", "+4", "", "")},
        "cmbp": ("+6", "+4", "0"), "cmdp": ("+6", "+4", "+3", "0"),
        "wdetail": [{"type": "S, 2H", "range": "", "ammo": ""},
                    {"type": "P", "range": "110 ft", "ammo": "arrows"},
                    {"type": "P", "atk": "+11/+6", "crit": "19-20/x2"}],
        "skill_over": {K("religion"): ("7", "+6"), "Climb": ("", "")},
        "aci": [("+2 mithral chain shirt", "+6", "light", "0", "10%", "12.5", "max Dex +6"),
                ("Heavy wooden shield", "+2", "shield", "-2", "15%", "10", "")],
        "aci_total": ("+8", "", "-2", "25%", "22.5"),
        "gear_wt": {"Bag of holding (type I):": "15", "Tome of Clear Thought +2": "5"},
        "spellday": {1: ("", "17", "3", "+2"), 2: ("", "18", "1", "+1")},
    },
    "pyrrhon": {
        "style": "pedant", "levels": {"wizard": 7},
        "head": {"size": "M", "gender": "M"},
        "speed": ("30", "30"), "init": ("+3", "+3", "0"),
        # Ring of protection +1 is deflection; the block's touch 13 stands.
        "acp": {"armor": "+2", "shield": "0", "dex": "+3", "size": "0", "natural": "0",
                "deflection": "+1", "misc": "0"},
        "saveparts": {"fort": ("+2", "+2", "0", "0"), "ref": ("+2", "+3", "0", "0"),
                      "will": ("+5", "+1", "0", "0")},
        "cmbp": ("+3", "-1", "0"), "cmdp": ("+3", "-1", "+3", "0"),
        "wdetail": [{"type": "P", "range": "80 ft", "atk": "+6", "crit": "19-20/x2", "dmg": "1d8"}],
        "aci": [("Bracers of armor +2", "+2", "armor", "0", "0%", "1", "force"),
                ("Ring of protection +1", "+1", "deflection", "0", "0%", "", "")],
        "aci_total": ("+3", "", "0", "0%", "1"),
        "gear_wt": {"Cloak of resistance +1": "1", "Spell component pouch": "2",
                    "Spellbook (by school, tabbed)": "3", "Light crossbow, 20 bolts": "6"},
        "spellday": {0: ("", "15", "4", "-"), 1: ("", "16", "4", "+2"), 2: ("", "17", "3", "+1"),
                     3: ("", "18", "2", "+1"), 4: ("", "19", "1", "+1")},
        "school_slot": True,
    },
    "njala": {
        "style": "sparse", "levels": {"rogue": 4, "witch": 3},
        "head": {"size": "M", "gender": "F"},
        "speed": ("30", "30"), "init": ("+4", "+4", ""),
        "acp": {"armor": "+4", "dex": "+4"},
        # Rules give Fort 2+2; the block's +3 stands.
        "saveparts": {"fort": ("+2", "+2", "", ""), "ref": ("+5", "+4", "", ""),
                      "will": ("+4", "+1", "", "")},
        "cmbp": ("+4", "0", "0"), "cmdp": ("+4", "0", "+4", "0"),
        "wdetail": [{"type": "P", "crit": "19-20/x2"}, {"type": "P", "crit": "19-20/x2"}],
        "skill_over": {"Linguistics": ("0", "")},
        "aci": [("+1 studded leather", "+4", "light", "0", "15%", "20", "")],
        "aci_total": ("+4", "", "0", "15%", "20"),
        "spellday": {0: ("", "13", "4", ""), 1: ("", "14", "2", "+1")},
    },
    "merit": {
        "style": "own", "levels": {"paladin": 7},
        "head": {"size": "Small", "gender": "F", "alignment": "LG"},
        "speed": ("20", "15"), "init": ("+1", "+1", ""),
        "acp": {"armor": "+10", "shield": "+3", "dex": "+1", "size": "+1"},
        "saveparts": {"fort": ("+5", "+3", "", "+3"), "ref": ("+2", "+1", "", "+3"),
                      "will": ("+5", "+1", "", "+3")},
        "cmbp": ("+7", "+3", "-1"), "cmdp": ("+7", "+3", "+1", "-1"),
        "wdetail": [{"type": "S"}],
        "aci": [("+1 full plate", "+10", "heavy", "-5", "35%", "25", "max Dex +1"),
                ("+1 heavy steel shield", "+3", "shield", "-1", "15%", "7.5", "")],
        "aci_total": ("+13", "", "-6", "50%", "32.5"),
    },
    "raymora": {
        "style": "loose", "levels": {"druid": 7},
        "head": {"size": "M", "gender": "M"},
        "speed": ("30", "20"), "init": ("+1", "+1", ""),
        "acp": {"armor": "+4", "dex": "+1"},
        "saveparts": {"fort": ("+5", "+2", "", ""), "ref": ("+2", "+1", "", ""),
                      "will": ("+5", "+4", "", "")},
        "cmbp": ("+5", "0", "0"), "cmdp": ("+5", "0", "+1", "0"),
        "wdetail": [{"type": "S", "atk": "+5", "crit": "18-20/x2", "dmg": "1d6"},
                    {"type": "B", "range": "50 ft", "ammo": "bullets", "atk": "+6", "crit": "x2",
                     "dmg": "1d4"}],
        "skill_over": {"Heal": ("7", "+6")},
        "aci": [("Hide armor", "+4", "medium", "-3", "20%", "25", "")],
        "aci_total": ("+4", "", "-3", "20%", "25"),
        "spellday": {0: ("", "", "4", ""), 1: ("", "", "5", ""), 2: ("", "", "4", ""),
                     3: ("", "", "3", ""), 4: ("", "", "2", "")},
    },
}


def mod(sh, ab):
    m = sh["abil"][ab][1]
    return int(m) if m else 0


def skill_rows(sh, det) -> dict[str, tuple[str, str, str, str]]:
    """skill -> (total, ability, ranks, misc). Ranks are what is left after ability and the
    class-skill +3; anything over the character level goes in misc."""
    level = sum(det["levels"].values())
    cls = set().union(*(CLASS_SKILLS[c] for c in det["levels"]))
    over = det.get("skill_over", {})
    rows = {}
    for name, val in sh["skills"].items():
        if isinstance(val, tuple) and name.startswith("Craft"):
            continue
        total, given_ranks = (val, "") if not isinstance(val, tuple) else val
        if total is None:
            continue
        ab = mod(sh, SKILL_ABIL[name])
        abs_ = f"{ab:+d}" if ab else "0"
        if name in over:
            r, m = over[name]
            rows[name] = (total or "", abs_, r, m)
            continue
        if given_ranks and not total:
            rows[name] = ("", abs_, given_ranks, "")
            continue
        t = int(total)
        if given_ranks:
            r = int(given_ranks)
            rest = t - ab - r
            rows[name] = (total, abs_, given_ranks, f"{rest:+d}" if rest else "")
            continue
        cb = 3 if name in cls else 0
        r = t - ab - cb
        if cb and r < 1:
            rows[name] = (total, abs_, "", "")
            continue
        misc = cb
        if r > level:
            misc += r - level
            r = level
        rows[name] = (total, abs_, str(max(r, 0)), f"+{misc}" if misc else "")
    style = det["style"]
    if style in ("ledger", "pedant"):
        for name in SKILL_TOP:
            if name in rows or name.startswith(("Craft", "Perform", "Profession")):
                continue
            if name in sh["skills"]:
                continue
            ab = mod(sh, SKILL_ABIL[name])
            abs_ = f"{ab:+d}" if ab else "0"
            total = "" if (style == "ledger" or name in TRAINED_ONLY) else abs_
            rows[name] = (total, abs_, "", "")
    return rows


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
    det = sh["detail"]
    cp = pt - 0.5
    for k, parts in det["saveparts"].items():
        for col, v in zip(("base", "ability", "magic", "misc"), parts):
            if v:
                pen.center(SAVE_PART[col], SAVE_ROW[k], v, cp, fit=18)
    for col, v in det["acp"].items():
        pen.center(AC_COL[col], BOX["ac"][1], v, cp, fit=18)
    for col, v in zip(("bab", "str", "size"), det["cmbp"]):
        pen.center(CMB_COL[col], BOX["cmb"][1], v, cp, fit=18)
    for col, v in zip(("bab", "str", "dex", "size"), det["cmdp"]):
        pen.center(CMD_COL[col], BOX["cmd"][1], v, cp, fit=18)
    total, dex, misc = det["init"]
    pen.center(*BOX["init"], total, pt + 0.5)
    pen.center(INIT_COL["dex"], BOX["init"][1], dex, cp)
    if misc:
        pen.center(INIT_COL["misc"], BOX["init"][1], misc, cp)
    base, armored = det["speed"]
    pen.text(SPEED["base"][0], SPEED["base"][1], base, pt + 0.5, anchor="rs")
    pen.text(SPEED["armor"][0], SPEED["armor"][1], armored, pt + 0.5, anchor="rs")
    for i, w in enumerate(sh["weapons"][:5]):
        w = {**w, **{k: v for k, v in (det["wdetail"][i] if i < len(det["wdetail"]) else {}).items()
                     if v and not w.get(k)}}
        top = WEAPON_TOP[i]
        pen.line_fill(26, 210, top + 26, w.get("name", ""), pt)
        pen.center(240, top + 21, w.get("atk", ""), pt - 0.5, fit=46)
        pen.center(292, top + 21, w.get("crit", ""), pt - 1, fit=30)
        for col in ("type", "range"):
            x0, x1 = WEAPON_COL[col]
            pen.center((x0 + x1) / 2, top + 47, w.get(col, ""), pt - 1, fit=x1 - x0 - 3)
        pen.line_fill(*WEAPON_COL["ammo"], top + 51, w.get("ammo", ""), pt - 1.5)
        pen.line_fill(*WEAPON_COL["dmg"], top + 51, w.get("dmg", ""), pt - 1)
    det = sh["detail"]
    sp = pt - 0.5
    for name, val in sh["skills"].items():
        if name.startswith("Craft") and isinstance(val, tuple) and not val[1]:
            pen.line_fill(347, 412, SKILL_TOP[name] + 9, val[0], pt - 1)
    for name, (total, ab, ranks, misc) in skill_rows(sh, det).items():
        y = SKILL_TOP[name] + 5.5
        for col, v in (("total", total), ("ability", ab), ("ranks", ranks), ("misc", misc)):
            if v:
                pen.center(SKILL_COL[col], y, v, sp, fit=22)
    cls = set().union(*(CLASS_SKILLS[c] for c in det["levels"]))
    marked = set(sh.get("class_skills", [])) | {n for n in sh["skills"] if n in cls}
    if det["style"] in ("ledger", "pedant"):
        marked |= {n for n in cls if not n.startswith(("Craft", "Profession"))}
    for name in marked:
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
    det = sh["detail"]
    cp = pt - 1
    for i, row in enumerate(det["aci"][:5]):
        item, bonus, typ, acp, asf, wt, props = row
        pen.line_fill(*ACI_COL["item"], ACI_ROWS[i], item, pt - 0.5)
        for col, v in (("bonus", bonus), ("type", typ), ("acp", acp), ("asf", asf), ("wt", wt)):
            if v:
                pen.center(ACI_COL[col], ACI_ROWS[i] - 5, v, cp, fit=40)
        if props:
            pen.line_fill(*ACI_COL["props"], ACI_ROWS[i], props, cp - 0.5)
    for col, v in zip(("bonus", "type", "acp", "asf", "wt"), det["aci_total"]):
        if v:
            pen.center(ACI_COL[col], ACI_TOTAL - 5, v, cp, fit=40)
    wts = det.get("gear_wt", {})
    for i, g in enumerate(sh["gear"][:len(GEAR_ROWS)]):
        pen.line_fill(*GEAR_X, GEAR_ROWS[i], g, pt - 1)
        if g in wts:
            pen.center(GEAR_WT, GEAR_ROWS[i] - 5, wts[g], cp - 0.5, fit=15)
    for lvl, parts in det.get("spellday", {}).items():
        for col, v in zip(("known", "dc", "day", "bonus"), parts):
            if v:
                pen.center(SPELL_COL[col], SPELL_ROW[lvl], v, cp, fit=18)
    if det.get("school_slot"):
        pen.text(432, 277, "+1 evocation slot each level (school)", cp - 1, fit=140)
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
    det = DETAIL[name]
    sh = {**SHEETS[name], "detail": det, "head": {**SHEETS[name]["head"], **det["head"]}}
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
