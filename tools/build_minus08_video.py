#!/usr/bin/env python3
"""Page −08 — The Archive at the Mountain (Darkest Dungeon edition).

Nine voices. Twelve acts. Scene-locked frames. Amber glow on the speaking character.

  .venv/bin/python tools/build_minus08_video.py audio             # gen ElevenLabs MP3
  .venv/bin/python tools/build_minus08_video.py stills            # dry-run image list
  .venv/bin/python tools/build_minus08_video.py stills --render   # call image API
  .venv/bin/python tools/build_minus08_video.py pygame            # preview
  .venv/bin/python tools/build_minus08_video.py frames            # export unique frames
  .venv/bin/python tools/build_minus08_video.py assemble          # ffmpeg → mp4
  .venv/bin/python tools/build_minus08_video.py all --render      # full pipeline
  .venv/bin/python tools/build_minus08_video.py cmd_frames        # print frame list (debug)
"""
from __future__ import annotations

import argparse
import base64
import hashlib
import json
import math
import os
import re
import subprocess
import sys
import time
from pathlib import Path

BASE   = Path(__file__).resolve().parent.parent
AUDIO  = BASE / "audio"  / "minus08"
OUT    = BASE / "video"  / "minus08"
STILLS      = OUT / "stills"
BACKGROUNDS = STILLS / "backgrounds"
CHARACTERS  = STILLS / "characters"
ENEMIES     = STILLS / "enemies"
PLAYERS     = STILLS / "players"
FRAMES      = OUT / "frames"
SRC    = BASE / "src" / "phase2" / "-08.md"

_env = BASE / ".env"
if _env.exists():
    for _l in _env.read_text().splitlines():
        _l = _l.strip()
        if _l and not _l.startswith("#") and "=" in _l:
            k, _, v = _l.partition("=")
            os.environ.setdefault(k.strip(), v.strip())

W, H = 1280, 720
FPS  = 30
# Act 00 plays over black before the table. The two thetas open and the
# Phase 2 hallway comes through them. Audio is held by this many seconds
# so the first spoken line lands on the table.
ACT00_LEAD = 6.4
AUDIO_OFFSET = 0.0
HALLWAY_PNG = BASE / "web" / "gate" / "assets" / "hallway.png"

# ── Palette ───────────────────────────────────────────────────────────────────
BONE      = (230, 220, 200)
INK       = (11,  11,  12)
CHALK     = (216, 210, 192)
NIGHT     = (8,   16,  32)
PARCHMENT = (210, 190, 155)
RUST      = (140, 58,  42)
AMBER     = (255, 180,  40)   # speaking-character glow

# ── Voice IDs — set via .env VOICE_* ─────────────────────────────────────────
# See VOICE_DESIGN_PROMPTS.md for prompts to paste into ElevenLabs Voice Design.
VOICE_NARRATOR  = os.environ.get("VOICE_NARRATOR",  "PENDING")
VOICE_MERLIN    = os.environ.get("VOICE_MERLIN",    "PENDING")   # Draavio = same voice
VOICE_FEYNMAN   = os.environ.get("VOICE_FEYNMAN",   "PENDING")
VOICE_SHELDON   = os.environ.get("VOICE_SHELDON",   os.environ.get("VOICE_SHELDON_LIB", "OAXPclEPumYkMdEw2L4g"))
VOICE_LISBETH   = os.environ.get("VOICE_LISBETH",   "PENDING")
VOICE_WITCH     = os.environ.get("VOICE_WITCH",     "PENDING")
VOICE_JOEY      = os.environ.get("VOICE_JOEY",      os.environ.get("VOICE_JOEY_LIB",    "QDidinP5kDJnJ9cCCGp6"))
VOICE_VINCENT   = os.environ.get("VOICE_VINCENT",   "PENDING")
VOICE_GOAT      = os.environ.get("VOICE_GOAT",      "PENDING")
VOICE_OPERATOR  = os.environ.get("VOICE_OPERATOR",  "PENDING")  # operator's own voice clone

# Speaker label → voice ID
# Merit uses Witch voice (same actor, lower register).
# LisbethEn uses Lisbeth voice (English translation blocks).
# Narrator and Draavio share Merlin voice.
# Operator uses the operator's ElevenLabs voice clone (set VOICE_OPERATOR in .env).
VOICE_MAP: dict[str, str] = {
    "Narrator":  VOICE_NARRATOR,
    "Draavio":   VOICE_MERLIN,
    "Magi":      VOICE_MERLIN,
    "Merlin":    VOICE_MERLIN,
    "Feynman":   VOICE_FEYNMAN,
    "Sheldon":   VOICE_SHELDON,
    "Pyrrhon":   VOICE_SHELDON,
    "Raymora":   VOICE_JOEY,
    "Lisbeth":   VOICE_LISBETH,
    "LisbethEn": VOICE_LISBETH,
    "Witch":     VOICE_WITCH,
    "Merit":     VOICE_WITCH,
    "Joey":      VOICE_JOEY,
    "Vincent":   VOICE_VINCENT,
    "Goat":      VOICE_GOAT,
    "Operator":  VOICE_OPERATOR,
    "Archivist": VOICE_NARRATOR,   # Archivist: Narrator voice — the keeper of the record
    "Snake":     os.environ.get("VOICE_SNAKE", "iUex9jQAAsMqYMxYUkK0"),  # Purple snake: RADA-trained ceremonial P-speech
}

VOICE_SETTINGS: dict[str, dict] = {
    "Narrator":  {"stability": 0.55, "similarity_boost": 0.80, "style": 0.25, "use_speaker_boost": True},
    "Draavio":   {"stability": 0.55, "similarity_boost": 0.80, "style": 0.25, "use_speaker_boost": True},
    "Feynman":   {"stability": 0.45, "similarity_boost": 0.75, "style": 0.35, "use_speaker_boost": True},
    "Sheldon":   {"stability": 0.50, "similarity_boost": 0.75, "style": 0.30, "use_speaker_boost": True},
    "Lisbeth":   {"stability": 0.68, "similarity_boost": 0.82, "style": 0.12, "use_speaker_boost": False},
    "LisbethEn": {"stability": 0.68, "similarity_boost": 0.82, "style": 0.12, "use_speaker_boost": False},
    "Witch":     {"stability": 0.52, "similarity_boost": 0.78, "style": 0.35, "use_speaker_boost": True},
    "Merit":     {"stability": 0.58, "similarity_boost": 0.78, "style": 0.20, "use_speaker_boost": True},
    "Joey":      {"stability": 0.40, "similarity_boost": 0.75, "style": 0.50, "use_speaker_boost": True},
    "Vincent":   {"stability": 0.72, "similarity_boost": 0.80, "style": 0.08, "use_speaker_boost": False},
    "Goat":      {"stability": 0.95, "similarity_boost": 0.50, "style": 0.00, "use_speaker_boost": False},
}

# ── Act → background ──────────────────────────────────────────────────────────
# Acts parsed from ## ACT N headers in src/phase2/-08.md.
ACT_BACKGROUNDS: dict[int, str] = {
    0:  "pre_game_table",      # ACT 0  — The Table
    1:  "mountain_road",       # ACT 1  — The Mountain
    2:  "antechamber",         # ACT 2  — The Antechamber
    3:  "gift_room",           # ACT 3  — The Gift Room
    4:  "gift_room",           # ACT 4  — The Gift (coffins, altar, secret door)
    5:  "circle_room",         # ACT 5  — The Circle Room
    6:  "circle_room_trap",    # ACT 6  — The Trap
    7:  "circle_room_trap",    # ACT 7  — The Goat Conversation (trap already set)
    8:  "circle_room_trap",    # ACT 8  — The Wait
    9:  "circle_room_battle",  # ACT 9  — The Battle
    10: "circle_room_trial",   # ACT 10 — The Archivist
    11: "circle_room_trial",   # ACT 11 — The Session Closes
}

# ── Still layout ──────────────────────────────────────────────────────────────
# backgrounds/actNN_<act>/<kind>_<id>.png, filed under the act where the script
# first calls the still. The kind prefix decides how the frame is drawn:
#   table  table-mode plate; players stand at the table over it
#   sheet  character sheet (act 0)
#   loc    location plate, no figures; party and enemy sprites stand on it
#   cut    cut scene; the figures are painted in, so no sprites are drawn
#   prop   reference still; not drawn as a background
# Act None files the still under backgrounds/unused/ (no ~~FRAME~~ calls it).
ACT_SLUGS: dict[int, str] = {
    0: "the_table", 1: "the_mountain", 2: "the_antechamber", 3: "the_gift_room",
    4: "the_gift", 5: "the_circle_room", 6: "the_trap", 7: "the_goat_conversation",
    8: "the_wait", 9: "the_battle", 10: "the_archivist", 11: "the_session_closes",
}
BG_HOME: dict[str, tuple[int | None, str]] = {
    "pre_game_table":     (0,  "table"),
    "sheet_draavio":      (0,  "sheet"),
    "sheet_pyrrhon":      (0,  "sheet"),
    "sheet_njala":        (0,  "sheet"),
    "sheet_merit":        (0,  "sheet"),
    "sheet_raymora":      (0,  "sheet"),
    "mountain_road":      (1,  "loc"),
    "cliff_top_night":    (1,  "loc"),
    "antechamber":        (2,  "loc"),
    "gift_room":          (3,  "loc"),
    "axiomite_screen":    (3,  "prop"),
    "coffin_uncovered":   (4,  "loc"),
    "link_on_altar":      (4,  "cut"),
    "secret_corridor":    (4,  "loc"),
    "circle_room":        (5,  "loc"),
    "circle_room_trap":   (6,  "loc"),
    "outside_grove":      (7,  "loc"),
    "draavio_through_oak": (7, "cut"),
    "iguana_in_tree":     (7,  "cut"),
    "circle_room_battle": (9,  "loc"),
    "njala_down":         (9,  "cut"),
    "iguana_extract":     (9,  "cut"),
    "draavio_returns":    (9,  "cut"),
    "circle_room_trial":  (10, "loc"),
    "archivist_ring":     (None, "cut"),
    "scape_book":         (None, "cut"),
}


def bg_path(sid: str) -> Path:
    act_n, kind = BG_HOME.get(sid, (None, "loc"))
    folder = "unused" if act_n is None else f"act{act_n:02d}_{ACT_SLUGS[act_n]}"
    name = sid if sid.startswith(f"{kind}_") else f"{kind}_{sid}"
    return BACKGROUNDS / folder / f"{name}.png"

# ── DD party layout ───────────────────────────────────────────────────────────
# x, y of the character sprite's bottom-left corner.
# Merit is explicitly shorter (gnome) — her sprite is scaled down.
# Raymora (iguana) is on the wall/tree — higher y, smaller sprite.

_BASE = H - 30   # shared foot-line for all party sprites

CHAR_POSITIONS: dict[str, tuple[int, int]] = {
    # Party — cramped DD line, left third of frame, overlapping slightly.
    # Position 1 (front) → position 5 (back), left to right.
    # Draavio is ALWAYS frontmost in combat — he leads.
    "Draavio":  (20,  _BASE - 520),   # pos 1 — front, tallest
    "Merit":    (120, _BASE - 310),   # pos 2 — gnome, short, behind Draavio
    "Njala":    (240, _BASE - 500),   # pos 3
    "Pyrrhon":  (350, _BASE - 490),   # pos 4
    "Raymora":  (460, _BASE - 200),   # iguana, on the stone
    "raymora_doctor": (480, _BASE - 500),  # the man, same foot-line as the party
    # Non-party / special
    "Feynman":  (W - 240, H - 520),   # fourth-wall frames only
    "Witch":    (W - 300, H - 540),   # Archivist scene / trial
    "Vincent":  (W - 220, H - 560),   # enters from sinkhole (right side)
}

# Sprite scale overrides (width, height) for unusual sizes
CHAR_SIZES: dict[str, tuple[int, int]] = {
    "Merit":         (190, 310),   # gnome — shorter than everyone
    "Raymora":        (130, 200),  # iguana form — small
    "raymora_iguana": (130, 200),
    "raymora_doctor": (260, 500),  # the man stands with the party
    "Feynman":       (260, 460),
    "Vincent":       (290, 510),
    "Witch":         (290, 510),
    "witch_of_the_rivers": (290, 510),
    "Draavio":       (290, 520),
    "draavio":       (290, 520),
    "Njala":         (270, 500),
    "njala":         (270, 500),
    "Pyrrhon":       (275, 490),
    "pyrrhon":       (275, 490),
}

# ── Style strings ─────────────────────────────────────────────────────────────
# The drawing language is described, not named. One pen for everyone.
# STYLE_DD is that pen plus the dungeon (torch, umber, stone).
# _PLAYER is that pen plus a lit room (true colors, clean clothes).
_INK = (
    "Hand-drawn illustration: heavy black brush-ink contour lines of varying weight — "
    "thick where a form turns away from the light, thin on the lit edge. "
    "Shadows are solid hard-edged black shapes, graphic and deliberate, not soft gradients. "
    "Short parallel ink hatching inside the mid-tones. "
    "Color is laid in as flat painted fills with two or three value steps, dry-brush texture visible. "
    "Anatomy is slightly elongated and angular, hands a little large, silhouette readable from across a room. "
    "Faces are drawn, not rendered: carved cheekbones, deep eye sockets, expressive brows. "
    "No airbrush smoothness, no photographic rendering, no anime eyes, no CGI gloss. "
    "No captions or text in image. "
)

STYLE_DD = (
    _INK +
    "Lighting: one warm torch source, low and from the right, everything else falling into black. "
    "Palette compressed to burnt umber, rust red, bone white and near-black; cold blue only in distant light. "
    "Surfaces are rough stone, old wood, worn leather, tarnished metal. "
)

# The rank. Party sprites stand on the left third, enemies on the right third,
# feet on the bottom edge of the 1280×720 frame. A plate that is a tunnel,
# a cliff looked up, or a figure already standing in a rank cannot take them.
_DD_STAGE = (
    "A side-on stage, built so a rank of figures can stand in front of it. "
    "The floor runs edge to edge across the bottom third. "
    "The near edge of the floor is the bottom of the picture. "
    "The left third of the floor is bare. The right third of the floor is bare. "
    "The subject of the place sits in the center, back from the front edge, in the upper two-thirds. "
    "No people. No monsters. No silhouettes in the open floor. "
)

# ── Background prompts ────────────────────────────────────────────────────────
BG_PROMPTS: dict[str, tuple[str, str]] = {
    "pre_game_table": (
        "A round table seen from slightly above. Seven mismatched chairs, one empty. "
        "Character sheets, dice, pencils, stacks of index cards. A folded cardboard GM screen "
        "at the far end — dragon illustration facing outward. On a sideboard: a laptop, fan spinning, "
        "terminal window visible, a compile in progress. Plain room, one lamp, evening light. "
        "Warm, realistic, lived-in. No people.",
        "realistic"
    ),
    "mountain_road": (
        _DD_STAGE +
        "Night. The floor is a wet mountain path. "
        "Behind the path a cliff rises and fills the upper frame — the wall of the stage, not a view looking up the rock. "
        "A small door is cut into the cliff, high and center, a faint light in it. "
        "A guard-post fire is a tiny spark deep in the background, not a figure. "
        "The path is dry flat stone. No water. No lake. No boulders in the left third or the right third. "
        "Stars above the cliff. No people.",
        "dd"
    ),
    "cliff_top_night": (
        _DD_STAGE +
        "The floor is the flat wet stone lip of a cliff at night. "
        "Behind the stone: open sky, a partial moon behind thin cloud, a dark treeline. "
        "The drop is in the background, not under the floor. "
        "Symbols scratched into the stone in the center only — an eye, a star, a ring — large enough to read. "
        "Three parchment cards weighted with small stones, center, back from the front edge. "
        "A torch planted high on the right, behind the bare right floor. "
        "No people.",
        "dd"
    ),
    "antechamber": (
        _DD_STAGE +
        "A rough stone antechamber. "
        "Two niches set back into the side walls. Old bones piled inside the niches only, not on the open floor. "
        "A dark arch in the center. The arch is empty. Nothing stands in it. "
        "One torch high on the right wall. "
        "Do not draw a skeleton. Do not draw a warrior.",
        "dd"
    ),
    "gift_room": (
        _DD_STAGE +
        "A high-ceilinged underground chamber. "
        "A stone altar at the center of the far wall — gold coins, silver candlesticks, a chalice. "
        "A bronze brazier, lit, set back on the altar steps, not in the foreground. "
        "A high stone ledge on the right wall. The ledge is empty. Do not draw a gargoyle. Nothing perches there. "
        "Skulls along the back wall only, not on the open floor. "
        "No creatures.",
        "dd"
    ),
    "secret_corridor": (
        _DD_STAGE +
        "Not a view down a tunnel. The near wall is cut away. "
        "We see the far wall of a narrow hewn-stone corridor, side on, the way a rank would walk it. "
        "The floor is the corridor floor, a wide horizontal band. "
        "A root has broken through the ceiling, upper center. "
        "A torch high on the right wall. Darkness at the far end, center. "
        "The center is empty corridor. No throne. No chair. No seat. No cloth. No furniture. "
        "No people. No figures.",
        "dd"
    ),
    "circle_room": (
        _DD_STAGE +
        "The same wide chamber every time this room appears. "
        "An enormous oak rises through a sinkhole at the center. Canopy lost above. "
        "A chalk circle on the floor at the oak's base, center, back from the front edge. "
        "A wooden goat pen, small, deep in the left background — seven goats inside. Not on the foreground floor. "
        "A pyramid of dark smooth eggs, deep in the right background. "
        "The sinkhole throws cool vertical light. No people.",
        "dd"
    ),
    "circle_room_trap": (
        _DD_STAGE +
        "The same oak-and-sinkhole chamber as the circle room. Painted. Not a woodcut. The oak is still center. "
        "The chalk circle is scuffed and broken. A few smooth stones rest on it, small. "
        "The goat pen is small, deep in the left background. The eggs are deep in the right background. "
        "Cooler, lower light. The room looks empty. "
        "No people. No crouching figures. No silhouettes.",
        "dd"
    ),
    "circle_room_battle": (
        _DD_STAGE +
        "The same oak-and-sinkhole chamber. Painted. Not a woodcut. The oak is center and still. "
        "Gold dust hangs in the air. The sinkhole throws orange light down through the dust. "
        "The chalk circle is scuffed — one arc broken. "
        "A little debris at the center of the floor only, not piled on the left or the right. "
        "The goat pen is small, deep left background. The eggs are deep right background. "
        "Empty room. No people. No soldiers. No fighters. No golem. No silhouettes.",
        "dd"
    ),
    "circle_room_trial": (
        _DD_STAGE +
        "The same oak-and-sinkhole chamber at last light. The oak is center. "
        "The sinkhole throws a ring of orange sun around the oak's base. "
        "The ring of fire-light on the stone is precise — it does not spread to the walls. "
        "The ring sits center, back from the front edge, so the left and right floor stay bare. "
        "The room is quiet. No people. No figures. The light does the work.",
        "dd"
    ),
    "outside_grove": (
        _DD_STAGE +
        "A grove of old oaks, late afternoon. The floor is a dirt path. The trees are the wall behind it. "
        "No sky through the canopy. Slanted golden light from the right. "
        "A red-collared goat, small, in the middle distance at the center of the path, looking left. "
        "Not large. Not in the foreground. Not on the left floor. Not on the right floor. "
        "No people.",
        "dd"
    ),
    "coffin_uncovered": (
        _DD_STAGE +
        "A narrow underground alcove of rough stone. "
        "A stone coffin sits at the center, set back from the front edge. "
        "The lid is shoved aside. The interior is empty. The edges are worn smooth. "
        "In the back wall a secret door stands ajar — a thin seam of a different darkness. "
        "A torch high on the right wall. "
        "The coffin is not in the left foreground. No people.",
        "dd"
    ),
}

# ── Special frame prompts ─────────────────────────────────────────────────────
SPECIAL_FRAME_PROMPTS: dict[str, tuple[str, str]] = {
    "link_on_altar": (
        "A hand holds a small pink carabiner climbing link in warm brazier light. "
        "Below it: a stone altar with scattered gold and silver. The link alone is offered. "
        "Warm amber light from the left. Painterly, intimate.",
        "dd"
    ),
    "draavio_through_oak": (
        "A tall half-orc in ranger gear steps into the hollow of a massive oak. "
        "His back is to the viewer. The tree's interior is a different quality of dark. "
        "In the grove distance: a goat with a red collar. Late afternoon light.",
        "dd"
    ),
    "iguana_in_tree": (
        "The underground chamber with an enormous oak rising through a sinkhole, cool light falling from above. "
        "High on the oak's trunk, a small green iguana clings to the bark, head up, eyes wide, mid-nod. "
        "Far below at the base of the oak, a tall half-orc ranger in a hooded cloak, back to the viewer, "
        "is stepping into the dark hollow of the trunk and is half gone into it. "
        "The chamber floor is otherwise empty. The rest of the party is not in the room. "
        "No other figures. A small wooden goat pen deep in the background.",
        "dd"
    ),
    "njala_down": (
        "The oak-and-sinkhole chamber in battle, gold dust in low orange afternoon light. "
        "A woman in studded leather lies still on the stones, eyes closed. "
        "Beside her hand a small coin is still spinning on its edge. "
        "Over her stands a huge stitched flesh golem made of the dead, arms hanging, regarding her. "
        "No iguana. No other figures.",
        "dd"
    ),
    "iguana_extract": (
        "The oak-and-sinkhole chamber in battle, gold dust in low orange afternoon light. "
        "A small green iguana has just dropped from the oak and landed on the stones "
        "between a woman in studded leather lying still and a huge stitched flesh golem. "
        "The iguana holds an opened glass vial in its front claws and drinks from it. "
        "The golem looks down at the iguana and does not strike. No other figures.",
        "dd"
    ),
    "draavio_returns": (
        "A tall half-orc emerges at the lip of a sinkhole, looking down into a battle. "
        "Beside him: a goat with a red collar. He looks spent, present. "
        "The party below is still fighting. He is here now.",
        "dd"
    ),
    "archivist_ring": (
        "A figure with burning wings stands in a ring of orange sun around an oak's base. "
        "The wings burn but do not touch the bark. "
        "Above him at the sinkhole rim: a goat with a red collar, looking down. "
        "The burning is precise. It does not spread.",
        "dd"
    ),
    "axiomite_screen": (
        "A cardboard GM screen lying flat on a table. The outside of the screen shows a dragon. "
        "Visible on the flat surface: open bestiary text, the Axiomite entry. "
        "Pencil beside it. Index cards. Flat, overhead, warm lamplight. Not a dungeon.",
        "realistic"
    ),
    "scape_book": (
        "A hand holds a leather-bound book, cover facing the viewer. "
        "The cover reads: SCAPE. Nothing else. "
        "Dark background. The book is the whole of the frame.",
        "dd"
    ),
}

# Party sprites. STYLE_DD is prepended when style is "dd".
_DD_CHAR = (
    "Full body figure, head to foot, on a fully transparent background. "
    "Side profile or three-quarter view facing right (toward the enemy side). "
    "Standing still, weight settled — a held pose, not a motion blur. "
    "Gear is worn and used but the figure is a person, not a ruin. "
)

# Players and the GM. Same pen as _INK. A lit room, not a dungeon.
# Style key "player" so STYLE_DD is not prepended.
_PLAYER = (
    _INK +
    "Lighting: soft, even, indoor — a well-lit room. Shadows still graphic black shapes, but small. "
    "Palette: the true colors of the clothes and skin, full range, nothing muted or sepia-washed. "
    "Fabric is clean and pressed; skin is clean; hair is combed. The person is rested and comfortable. "
    "Full standing figure, head to foot, on a fully transparent background. "
    "No props beyond what is listed. Facing slightly left toward camera-center. "
)

_FEYNMAN_LOOK = (
    "Man in his forties, American. Richard Feynman likeness: wide grin lines, bright quick eyes, "
    "dark hair swept back and a little unruly. "
    "White button-up shirt, sleeves rolled to the forearm, top button open, no tie. "
    "Khaki trousers, brown belt, brown leather shoes. "
)
_MERLIN_LOOK = (
    "Man, lean, precise bearing. Syrian features, dark hair flecked with grey, neat short beard. "
    "Dressed as a Magi, not a wizard: a long clean robe in deep plum with a simple cream sash, "
    "a soft rounded cap, plain leather sandals. No pointed hat, no stars, no staff. "
    "Everything pressed and orderly. "
)
_WITCH_LOOK = (
    "Young woman straight out of Ancient Egyptian wall painting and statuary: "
    "warm ochre-yellow skin as Egyptian art renders women, almond eyes with pronounced epicanthic folds, "
    "kohl-lined eyes, straight black shoulder-length hair with a thin gold headband. "
    "White pleated linen sheath dress, broad gold-and-turquoise collar, gold armbands, gold sandals. "
    "The air of someone who has just come from brunch on a balcony over the Nile — relaxed, unbothered. "
)
_LISBETH_LOOK = (
    "Lisbeth Salander as played by Noomi Rapace in the original Swedish Girl with the Dragon Tattoo: "
    "slight, pale, short black hair cut spiky and asymmetric, dark eyeliner, "
    "small nose stud and eyebrow ring. "
    "Black fitted leather jacket zipped partway over a black t-shirt, black jeans, black lace-up boots. "
    "Clean — the clothes are black, not dirty. No exposed midriff, no chains. "
)
_SHELDON_LOOK = (
    "Sheldon Cooper as played by Jim Parsons: very tall, very thin, neat side-parted brown hair, "
    "long face, posture rigidly upright. "
    "Red t-shirt with the Flash logo — yellow lightning bolt inside a white circle — "
    "worn over a long-sleeve blue shirt visible at the collar and cuffs. Khaki trousers. Plain sneakers. "
)
_JOEY_LOOK = (
    "Dr. Drake Ramoray as played by Joey Tribbiani (Matt LeBlanc) on Friends: "
    "handsome, dark hair, strong jaw, easy TV-actor charm. "
    "Crisp white doctor's coat, open, over light blue scrubs. A stethoscope around his neck. "
    "White sneakers. He looks exactly like a soap-opera doctor because he is one. "
)
_VINCENT_LOOK = (
    "Vincent Anton Freeman as played by Ethan Hawke in Gattaca: slim, short neat hair, "
    "composed expression. His black Gattaca suit — slim black single-breasted jacket, "
    "black trousers, white dress shirt, narrow black tie, polished black shoes. "
    "Immaculate. He never wears anything else. "
)

CHAR_PROMPTS: dict[str, tuple[str, str]] = {
    "draavio": (
        _DD_CHAR + "Facing right. Half-orc, tall, powerfully built. "
        "Worn ranger's coat over alchemist's gear — vials and pouches. "
        "A falchion visible on his back. A pink carabiner climbing link on his sling — small, specific. "
        "Expression: patient, observant. He has been in worse rooms.",
        "dd"
    ),
    "njala": (
        _DD_CHAR + "Facing right. Human woman, lean, dark hair, sharp eyes. Studded leather armor, practical. "
        "Two short swords — one at each hip. A silver coin visible between two fingers at her side. "
        "Hood down, face clear. Expression: still, watching, already three moves ahead. "
        "She is a rogue with witch hexes — her silhouette is lean and fast, not robed. "
        "No dress. No flowing cloth. She moves.",
        "dd"
    ),
    "njala_fallen": (
        _DD_CHAR + "Full figure lying on her back on the ground, seen from the side, head to the left, feet to the right. "
        "Human woman, lean, dark hair, studded leather armor, two short swords at her hips. "
        "Eyes closed, still. One hand open at her side; a small silver coin rests beside it. "
        "No ground, no floor, no shadow plane: only the figure.",
        "dd"
    ),
    "draavio_point": (
        _DD_CHAR + "Facing right. Half-orc, tall, powerfully built. "
        "Worn ranger's coat over alchemist's gear — vials and pouches. "
        "A falchion on his back, still sheathed. A pink carabiner climbing link on his sling. "
        "His right arm is fully extended, pointing ahead at a target off the frame to the right. "
        "Expression: fixed, certain. He has chosen.",
        "dd"
    ),
    "merit": (
        _DD_CHAR + "Facing right. Gnome — visibly, explicitly shorter than any other character. "
        "Full plate armor, longsword, heavy shield. The armor is immaculate. "
        "Expression: grave, deliberate. The smallness is the character — she is not performing height.",
        "dd"
    ),
    "pyrrhon": (
        _DD_CHAR + "Facing right. Tall human male in wizard robes — dark, functional, layered. "
        "An unusual detail: three highlighter pens tucked in the breast pocket (orange, blue, green). "
        "Gold ring on the right hand. A spell component pouch. No crossbow. "
        "Expression: precisely attentive, calculating, the numbers already solved. "
        "Robes are clearly wizard robes — long, with arcane embroidery. Tall silhouette.",
        "dd"
    ),
    "raymora_doctor": (
        _DD_CHAR + "Facing right. Human male, medium build, warm confident bearing. "
        "Wearing a fantasy tunic that is undeniably cut like hospital scrubs — "
        "same V-neck, same loose fabric, teal-green color, but made of medieval cloth. "
        "A real metal stethoscope hangs around his neck. This is not subtle — the stethoscope "
        "gleams in torchlight. He is dressed as a doctor in a dungeon and he knows it. "
        "A healer's satchel at his hip. Expression: totally comfortable, moderately amused. "
        "No crossbow. No traditional druid gear.",
        "dd"
    ),
    "raymora_iguana": (
        "Full body, transparent background. "
        "A green iguana — small, realistic anatomy. Facing right. "
        "Both eyes positioned separately — each looking at a different thing. "
        "Claws sharp and precise. Slightly raised on its haunches — alert, not passive.",
        "dd"
    ),
    "feynman": (
        _PLAYER + _FEYNMAN_LOOK +
        "Standing easy, weight on one foot, one hand half-raised as if mid-ruling. "
        "Expression: warm, fast, fully present. He is running the session.",
        "player"
    ),
    "witch_of_the_rivers": (
        _PLAYER + _WITCH_LOOK +
        "Standing at ease, one hand resting on her hip. Expression: she already knows. Amused.",
        "player"
    ),
    "vincent": (
        _PLAYER + _VINCENT_LOOK +
        "Body angled left toward the party, face fully visible to the viewer. "
        "Hands at his sides. Expression: unhurried. Every sentence is already true.",
        "player"
    ),
    # ── Note-taking / listening variants ─────────────────────────────────────
    "draavio_notes": (
        _DD_CHAR + "Facing right. Half-orc, tall. Same ranger/alchemist gear. "
        "Looking DOWN — head bowed slightly over a scroll or large piece of parchment. "
        "A quill or stub of charcoal in his right hand. He is writing. "
        "Left hand holds the scroll flat. Completely absorbed. "
        "The pink carabiner link still visible on his sling. "
        "Expression: focused, careful — the recording is the act.",
        "dd"
    ),
    "njala_listen": (
        _DD_CHAR + "The same woman as the standing rogue: lean, dark hair loose, sharp eyes. "
        "Hood down. Face fully clear. No hood, no cloak, no skirt, no flowing cloth. "
        "Studded leather armor, practical, the same suit. "
        "Two short swords, one sheathed at each hip — not on her back. "
        "Facing right, torso turned a fraction. She is LISTENING. "
        "Head tilted a fraction, eyes fixed on something off to her right. "
        "A silver coin still between two fingers at her side, not running. "
        "Nothing dramatic. The stillness is the tell. "
        "Expression: precise, absorbing every word. Empty background.",
        "dd"
    ),
    # ── Resting / seated variants (camping scene) ─────────────────────────────
    "draavio_rest": (
        _DD_CHAR + "Seated on stone, back against the wall. Knees up, arms resting on knees. "
        "Half-orc, tall even seated. Vials and pouches visible. "
        "He is not asleep — eyes open, watching. Expression: tired but present.",
        "dd"
    ),
    "njala_rest": (
        _DD_CHAR + "Seated cross-legged on stone. Studded leather, hoods down. "
        "The coin rests in her open palm — not running. She is not performing rest. "
        "Expression: flat, conserving.",
        "dd"
    ),
    "merit_rest": (
        _DD_CHAR + "Seated on stone, gnome — shorter even seated. Armor off or loosened at the shoulders. "
        "Longsword propped beside her. Hands in her lap. "
        "Expression: present, observing — a paladin does not fully rest.",
        "dd"
    ),
    "pyrrhon_rest": (
        _DD_CHAR + "Seated, leaning against the wall. Wizard robes pooled around him. "
        "Three highlighters still in the breast pocket. One hand on a spellbook open in his lap. "
        "He may be asleep. The book is still open.",
        "dd"
    ),
}

# ── Enemy / NPC sprite prompts ────────────────────────────────────────────────
# All enemies face LEFT (toward the party). Same DD style.
_DD_ENEMY = (
    "Full body figure, head to foot, on a fully transparent background. "
    "Three-quarter view or side profile facing LEFT (toward the viewer's left — toward the party). "
    "A held pose, weight settled into threat. Silhouette must read at a glance. "
)

ENEMY_PROMPTS: dict[str, tuple[str, str]] = {
    "skeleton_tongue": (
        _DD_ENEMY + "A tall skeleton warrior. Facing left. Figure only. "
        "Empty transparent background. No doorway, no pillar, no floor, no wall, no scenery. "
        "Jaw hangs wide open. An enormous elongated tongue lolls out toward the left. "
        "A rusted sword in one hand, point toward the left. "
        "Hollow eye sockets with a faint amber light. Tattered cloth and scraps of armor on the bones. "
        "The tongue is the detail. Same ink and the same skeleton as the lick and the slam.",
        "dd"
    ),
    "gargoyle_dd": (
        _DD_ENEMY + "A stone gargoyle crouching on a ledge, wings half-spread. Facing left. "
        "Large — nearly fills the right side of the frame. Stone-grey, rough-hewn face. "
        "Claws on the ledge. Blank stone eyes that somehow watch. "
        "Weight on the ledge, about to launch. Not moving yet — worse.",
        "dd"
    ),
    "skeleton_tongue_lick": (
        _DD_ENEMY + "Same skeleton as skeleton_tongue — now in motion. "
        "Extending forward, tongue extended toward the left (toward a character). "
        "Arms wide, leaning in. Mid-lick action pose. Horrifying, comic, specific.",
        "dd"
    ),
    "skeleton_tongue_slam": (
        _DD_ENEMY + "Same skeleton — recoiled, ready to slam. Arms drawn back, "
        "both bone fists raised to strike. The tongue is retracted. Pure aggression now.",
        "dd"
    ),
    "crab_creature": (
        _DD_ENEMY + "A large crab-like creature — segmented shell, multiple legs, two large claws. "
        "Facing left, held in the center of a chalk magic circle. "
        "The circle appears to be a containment boundary — the creature pushes against it. "
        "Ancient, patient, intelligent eyes. It has been there a long time. "
        "Not a monster — a resident.",
        "dd"
    ),
    "flesh_golem_dd": (
        _DD_ENEMY + "An enormous stitched figure. Multiple bodies' worth of parts assembled. "
        "Facing left. Very tall — head would be off-frame if upright; it hunches. "
        "Stitching visible across the skin, coarse thread. "
        "Expression: none — it does not have one. It has a direction.",
        "dd"
    ),
    "were_soldier_human": (
        _DD_ENEMY + "A soldier in partial armor, facing left. Human, composed, standing at attention. "
        "Gold-outlined from glitterdust — a shimmer around the edges. Expression: alert, military.",
        "dd"
    ),
    "were_soldier_scent": (
        _DD_ENEMY + "Same soldier, now changed — both hands clawing at their own eyes, "
        "face contorted. The scent has hit them. Something animalistic breaking through. "
        "Still upright but barely. The gold glitterdust outline still visible.",
        "dd"
    ),
    "were_soldier_crumpled": (
        _DD_ENEMY + "The same soldier collapsed on the ground, crumpled. "
        "Fetal position, glitterdust fading. Down and still.",
        "dd"
    ),
    "peacock_woman": (
        _DD_ENEMY + "A woman in elaborate peacock-patterned dress — iridescent blues and greens. "
        "Facing left, full standing figure. Bearing composed, nothing threatening in her posture. "
        "She is doing nothing wrong that we can see. "
        "Expression: present, guarded, reading the room. Faded flowers — beautiful, overlooked.",
        "dd"
    ),
    "peacock_woman_dust": (
        _DD_ENEMY + "The same woman as the standing peacock, traced only in gold glitterdust. "
        "Empty inside. A silhouette of light on a transparent background. No scenery. "
        "The outline must be her gown: a wide skirt of peacock feathers with eye-spots, "
        "feathers in the hair, a small bouquet of faded flowers in one hand. "
        "Upright, composed, facing left. No sword. No cloak. No armor. No second person.",
        "dd"
    ),
    "talking_goat_dd": (
        "Full body, transparent background. Darkest Dungeon painting style. "
        "A goat with a red collar, facing slightly right (toward the party). "
        "Standing upright on its back legs, foreleg raised in a conversational gesture. "
        "Its mouth is open — it is speaking. "
        "Expression: patient, philosophical. It has been waiting to have this conversation.",
        "dd"
    ),
    "goat_porthole": (
        "Full body, transparent background. Darkest Dungeon painting style. "
        "A goat lying on its side, at rest. Red collar. "
        "Against its flank, tied with a cord: a folded cloth with a circular porthole-cut — "
        "a handkerchief with a round hole. The goat is not distressed. It owns the handkerchief.",
        "dd"
    ),
    "azazel_archivist": (
        _DD_ENEMY + "A powerful male figure with MASSIVE spreading fire wings that fill the entire frame. "
        "The wings are enormous — each spans wider than the figure is tall, spread wide open. "
        "Fire-feathers: each feather is a tongue of flame, orange and white at the root. "
        "The figure stands in a ring of flame at the base of an enormous oak. "
        "He faces LEFT — looking directly at the party. His gaze is direct, unhurried. "
        "Dark formal robes beneath the wings — not armor, not white. An archivist, not a soldier. "
        "The fire is precise: it does not touch the bark. The record is kept.",
        "dd"
    ),
    "gargoyle_dive": (
        _DD_ENEMY + "A stone gargoyle in a full dive — launched from its ledge, wings spread wide, "
        "angled steeply downward toward the left (toward the party). "
        "Claws forward, mouth open. Mid-air, talons leading. "
        "Stone-grey, rough-hewn, the weight of the stone visible in the arc. "
        "This is the moment before impact.",
        "dd"
    ),
    "researcher_1": (
        _DD_ENEMY + "An underground field researcher. Late 30s, lean. "
        "Khaki vest with too many pockets, worn at the elbows. Headlamp pushed up on their forehead. "
        "Notepad in one hand, measuring tape clipped to vest. Boots caked with pale cave mud. "
        "Expression: alert, professional, not quite afraid yet. Facing left.",
        "dd"
    ),
    "researcher_2": (
        _DD_ENEMY + "An underground field researcher. Mid-40s, stocky build. "
        "Dark jacket, geological hammer on belt, sample bags visible. Glasses. "
        "Carbide lamp. Expression: cautious, reading the room. Facing left.",
        "dd"
    ),
    "researcher_3": (
        _DD_ENEMY + "An underground field researcher. Late 20s, athletic. "
        "Technical climbing harness still on, rope coiled at hip. Hard hat, gloves tucked in. "
        "Tablet computer in a waterproof case — she is still logging. Facing left.",
        "dd"
    ),
    "researcher_4": (
        _DD_ENEMY + "An underground field researcher. Early 50s, grey-bearded. "
        "Old-school canvas pack, antiquated survey equipment. Deliberate posture. "
        "This one has been underground before. Facing left.",
        "dd"
    ),
    "researcher_sick": (
        _DD_ENEMY + "The same woman as the hard-hat researcher, now afflicted. Facing left. "
        "Hard hat with the lamp still on it. Climbing harness. Rope still coiled at her hip. "
        "Boots on. The waterproof tablet still in one hand. "
        "The other hand clutches her chest. Face contorted. Skin pale and damp. "
        "Upright, barely. The gear is intact. The body is failing. "
        "Figure only. Transparent background. No scenery.",
        "dd"
    ),
    "researcher_crumpled": (
        _DD_ENEMY + "A researcher collapsed. One of the four, now on the ground. "
        "Fetal position, field gear still on. Sample bags scattered. Headlamp still lit, "
        "pointed sideways at the floor — a detail of the helplessness. Facing left.",
        "dd"
    ),
}

# ── Player standing sprites ───────────────────────────────────────────────────
# Six players + the GM, as themselves, in the clean player register (_PLAYER).
# Two expressions per player (_main, _talk) — they are barely on screen.
# Feynman gets three (_main, _talk, _gesture) — he is on screen all of act 0.
# Old portrait / grimdark standing sprites quarantined 2026-11-06:
#   video/minus08/stills/quarantine_players_20261106/

PLAYER_STANDING_PROMPTS: dict[str, tuple[str, str]] = {
    # ── Feynman (GM) — three variants ────────────────────────────────────────
    "pstand_feynman_main": (
        _PLAYER + _FEYNMAN_LOOK +
        "Arms loose at his sides, weight settled, head slightly tilted. "
        "Expression: the GM watching the table — warm, ready, unhurried.",
        "player"
    ),
    "pstand_feynman_talk": (
        _PLAYER + _FEYNMAN_LOOK +
        "Mouth open mid-sentence, one hand raised palm-out, calling a ruling. "
        "Expression: quick, delighted, precise.",
        "player"
    ),
    "pstand_feynman_gesture": (
        _PLAYER + _FEYNMAN_LOOK +
        "Leaning slightly forward, both hands up and open, shaping an idea in the air. "
        "Expression: the big grin — he has just seen where this is going.",
        "player"
    ),
    # ── Merlin (the Magi) ────────────────────────────────────────────────────
    "pstand_merlin_main": (
        _PLAYER + _MERLIN_LOOK +
        "Hands folded in front of him. Expression: patient, half-watching, three moves ahead.",
        "player"
    ),
    "pstand_merlin_talk": (
        _PLAYER + _MERLIN_LOOK +
        "One finger raised, mouth open. Expression: mid-explanation — unhurried and exact.",
        "player"
    ),
    # ── Sheldon ──────────────────────────────────────────────────────────────
    "pstand_sheldon_main": (
        _PLAYER + _SHELDON_LOOK +
        "Arms straight at his sides. Expression: reading something internally, lips pressed.",
        "player"
    ),
    "pstand_sheldon_talk": (
        _PLAYER + _SHELDON_LOOK +
        "Index finger raised, mouth open. Expression: a category error has been identified.",
        "player"
    ),
    # ── Lisbeth ──────────────────────────────────────────────────────────────
    "pstand_lisbeth_main": (
        _PLAYER + _LISBETH_LOOK +
        "Standing still, hands in jacket pockets. Expression: flat by choice, watching without turning.",
        "player"
    ),
    "pstand_lisbeth_talk": (
        _PLAYER + _LISBETH_LOOK +
        "One hand out of the pocket, held level, mouth open. "
        "Expression: completely serious, no hostility — the objection is formal.",
        "player"
    ),
    # ── Witch of the Rivers ──────────────────────────────────────────────────
    "pstand_witch_main": (
        _PLAYER + _WITCH_LOOK +
        "Standing at ease, one hand resting on her hip. Expression: she already knows. Amused.",
        "player"
    ),
    "pstand_witch_talk": (
        _PLAYER + _WITCH_LOOK +
        "One hand raised, fingers spread, mouth open. Expression: naming something that has no name yet.",
        "player"
    ),
    # ── Joey (Dr. Drake Ramoray) ─────────────────────────────────────────────
    "pstand_joey_main": (
        _PLAYER + _JOEY_LOOK +
        "Hands easy at his sides. Expression: genuine interest in whoever is speaking.",
        "player"
    ),
    "pstand_joey_talk": (
        _PLAYER + _JOEY_LOOK +
        "Leaning slightly forward, hands open, mouth open. Expression: the bit has started. Committed.",
        "player"
    ),
    # ── Vincent ──────────────────────────────────────────────────────────────
    "pstand_vincent_main": (
        _PLAYER + _VINCENT_LOOK +
        "Hands at his sides, perfectly still. Expression: every sentence is already true.",
        "player"
    ),
    "pstand_vincent_talk": (
        _PLAYER + _VINCENT_LOOK +
        "Mouth open, calm, one hand slightly lifted. Expression: stating the fact, not the argument.",
        "player"
    ),
}

# Speaker → dungeon sprite that takes the amber glow. The narrator does not glow.
SPEAKER_CHAR: dict[str, str] = {
    "Draavio":   "draavio",
    "Magi":      "draavio",
    "Merlin":    "draavio",
    "Pyrrhon":   "pyrrhon",
    "Raymora":   "raymora",
    "Lisbeth":   "njala",
    "LisbethEn": "njala",
    "Sheldon":   "pyrrhon",
    "Joey":      "raymora",
    "Merit":     "merit",
    "Vincent":   "vincent",
    "Witch":     "witch",
    "Feynman":   "feynman",
    "Goat":      "",
    "Narrator":  "",
    "Operator":  "",    # operator is offscreen; no character glyph
    "Archivist": "",    # Archivist is the NPC; no player sprite
    "Snake":     "",    # purple snake; no sprite
}

# Speaker name → player standing key prefix (for variant selection)
PLAYER_STANDING_KEY: dict[str, str] = {
    "Feynman":   "pstand_feynman",
    "Narrator":  "pstand_merlin",   # Merlin is also the narrator voice
    "Draavio":   "pstand_merlin",
    "Magi":      "pstand_merlin",
    "Merlin":    "pstand_merlin",
    "Sheldon":   "pstand_sheldon",
    "Pyrrhon":   "pstand_sheldon",
    "Raymora":   "pstand_joey",
    "Lisbeth":   "pstand_lisbeth",
    "LisbethEn": "pstand_lisbeth",
    "Witch":     "pstand_witch",
    "Merit":     "pstand_witch",    # Merit is played by the Witch player
    "Joey":      "pstand_joey",
    "Vincent":   "pstand_vincent",
    "Goat":      "",                # no standing sprite for the goat
}

# Player line (left → right) — Feynman excluded; he renders separately above.
PLAYER_LINE_ORDER = [
    "pstand_lisbeth",
    "pstand_sheldon",
    "pstand_merlin",
    "pstand_joey",
    "pstand_witch",
    "pstand_vincent",
]

# ── Who is in the room during act 0 ───────────────────────────────────────────
# The table starts empty. Merlin is the first person, when he reads the manual.
# Feynman and the other four enter when the Sheldon / Lisbeth exchange begins.
# Vincent's chair stays empty this act.
MERLIN_ALONE_FRAMES = {"merlin_alone", "manual_page"}
PARTY_TABLE_FRAMES  = {"party_table", "axiomite_screen"}
# Frames on which anyone at all is drawn. The open and the sheet readings are empty.
OCCUPIED_TABLE_FRAMES = MERLIN_ALONE_FRAMES | PARTY_TABLE_FRAMES

CUTSCENE_FRAMES: set[str] = {sid for sid, (_, kind) in BG_HOME.items() if kind == "cut"}

# Who is on screen comes from the narration's ~~STATE:k=v~~ marks, stamped on each cue
# by tools/sync_minus08_audio.py: raymora doctor|iguana, draavio present|gone,
# njala up|down, vincent seated (at the table from the end of act 1).
def cue_state(cue: dict | None, k: str, default: str = "") -> str:
    return ((cue or {}).get("state") or {}).get(k, default)


# ── The battle (act 9) ────────────────────────────────────────────────────────
# Party minus Draavio on the left, flesh golem on the right, for the whole golem
# conversation. Draavio and the goat stand in the centre once, normal size, after the
# draavio_returns cut scene. Then he is only seen inside a strike: point → swing →
# down, small, somewhere else on the floor each time, sometimes facing the other way.
BATTLE_FRAMES = {"draavio_returned", "golem_talk", "joey_sheet",
                 "golem_to_hole", "golem_in_hole", "battle_after"}

# seq → x where Draavio points from, x of each soldier, facing (+1 right, -1 left),
# foot-line y. Feet higher on the screen = further back = drawn behind the line.
# The party holds x < ~560 and the golem x > ~920, so strikes use the floor between
# them, the front of the golem's feet, and the back of the room.
STRIKES: dict[str, dict] = {
    "1":  {"x0": 560,  "xs": [820],      "dir": +1, "y": 610},
    "2":  {"x0": 1080, "xs": [760],      "dir": -1, "y": 708},
    "3":  {"x0": 40,   "xs": [250],      "dir": +1, "y": 455},
    "4":  {"x0": 880,  "xs": [630],      "dir": -1, "y": 500},
    "56": {"x0": 720,  "xs": [580, 870], "dir": -1, "y": 650},
    "7":  {"x0": 620,  "xs": [850],      "dir": +1, "y": 545},
}


def strike_scale(y: int) -> float:
    """Further back (feet higher) is smaller: 0.45 at the back wall, 1.0 at the front."""
    return max(0.45, min(1.0, 0.45 + 0.55 * (y - 450) / 270))
STRIKE_SIZES = {
    "draavio":  (210, 315),
    "soldier":  (200, 300),
    "crumpled": (230, 345),
    "goat":     (180, 270),
}
# The Portable Hole, laid out right by the oak; the golem sits in it to the rim.
HOLE_CENTER = (690, 565)
HOLE_SIZE   = (300, 70)


def strike_phase(frame_id: str) -> tuple[str, str] | None:
    m = re.fullmatch(r"strike_(\w+?)_(point|swing|down)", frame_id)
    return (m.group(1), m.group(2)) if m and m.group(1) in STRIKES else None
# Left to right once the exchange starts. Vincent is not in this line.
ACT0_LINE = [
    "pstand_lisbeth",
    "pstand_sheldon",
    "pstand_merlin",
    "pstand_joey",
    "pstand_witch",
]

# ── Climb disappearance state ─────────────────────────────────────────────────
# Maps frame_id → set of DD char keys REMOVED from the party line (climbed to top).
# Characters at the top are no longer in frame (frame is the cliff face).
CLIMB_GONE: dict[str, set[str]] = {
    "climb_njala_top":  {"njala", "pyrrhon"},          # Njála free-climbed; Pyrrhon spider-climbed
    "climb_merit_top":  {"njala", "pyrrhon", "merit"},
    "joey_wildshape":   {"njala", "pyrrhon", "merit"},  # Joey still below as doctor → iguana
    "iguana_on_rope":   {"njala", "pyrrhon", "merit", "draavio"},  # everyone up; only iguana left
}


# ── Frames where party sprites face the OTHER direction (LEFT) ────────────────
# In these frames the party turns to face each other or the scratch surface.
# draw_frame will pygame.transform.flip(img, True, False) for each party sprite.
FLIP_FRAMES: set[str] = {
    "draavio_gesture_njala",    # Draavio gestures to Njála — faces his own party
    "scratch_iguana",           # everyone faces the scratch surface (right wall)
    "language_invent",          # same
}

# ── Frames that use resting sprite variants ───────────────────────────────────
# In these frames draw_frame swaps <char> → <char>_rest when the variant exists.
RESTING_FRAMES: set[str] = {
    "circle_room_trap",         # the long wait — everyone sitting
    "were_soldier_composed",    # still waiting when soldiers arrive
    "were_soldier_breaking",
    "were_soldier_down",
}

# ── Enemy layout ──────────────────────────────────────────────────────────────
# Frame IDs → list of enemy sprite keys to render on the RIGHT side of screen.
_ER = W - 320   # enemy right-edge x
ENEMY_POSITIONS: dict[str, tuple[int, int]] = {
    "skeleton_tongue":       (_ER, H - 520),
    "skeleton_tongue_lick":  (_ER, H - 520),
    "skeleton_tongue_slam":  (_ER, H - 520),
    "gargoyle_dd":           (_ER - 60, H - 460),
    "crab_creature":         (_ER, H - 490),
    "flesh_golem_dd":        (_ER - 80, H - 600),
    "were_soldier_human":    (_ER, H - 510),
    "were_soldier_scent":    (_ER, H - 510),
    "were_soldier_crumpled": (_ER, H - 200),
    "peacock_woman":         (_ER, H - 500),
    "peacock_woman_dust":    (_ER, H - 500),
    "talking_goat_dd":       (_ER, H - 310),
    "goat_porthole":         (_ER, H - 280),
    "azazel_archivist":      (_ER - 80, H - 620),
    "gargoyle_dive":         (_ER - 60, H - 440),
    "researcher_1":          (_ER, H - 510),
    "researcher_2":          (_ER, H - 510),
    "researcher_3":          (_ER, H - 510),
    "researcher_4":          (_ER, H - 510),
    "researcher_sick":       (_ER, H - 510),
    "researcher_crumpled":   (_ER, H - 210),
}

ENEMY_SIZES: dict[str, tuple[int, int]] = {
    "skeleton_tongue":       (240, 490),
    "skeleton_tongue_lick":  (280, 490),
    "skeleton_tongue_slam":  (260, 490),
    "gargoyle_dd":           (320, 420),
    "crab_creature":         (300, 460),
    "flesh_golem_dd":        (360, 580),
    "were_soldier_human":    (240, 490),
    "were_soldier_scent":    (240, 490),
    "were_soldier_crumpled": (280, 200),
    "peacock_woman":         (240, 480),
    "peacock_woman_dust":    (240, 480),
    "talking_goat_dd":       (220, 300),
    "goat_porthole":         (250, 280),
    "azazel_archivist":      (380, 620),
    "gargoyle_dive":         (340, 400),
    "researcher_1":          (230, 490),
    "researcher_2":          (240, 490),
    "researcher_3":          (230, 490),
    "researcher_4":          (240, 490),
    "researcher_sick":       (230, 490),
    "researcher_crumpled":   (270, 210),
}

# Frame → which enemy sprite(s) to show
FRAME_ENEMIES: dict[str, list[str]] = {
    # Antechamber — skeleton sequence
    "antechamber":              ["skeleton_tongue"],
    "antechamber_combat":       ["skeleton_tongue"],
    "skeleton_advance":         ["skeleton_tongue"],
    "skeleton_lick":            ["skeleton_tongue_lick"],
    "skeleton_lick_draavio":    ["skeleton_tongue_lick"],
    "skeleton_slam":            ["skeleton_tongue_slam"],
    "skeleton_slam_1":          ["skeleton_tongue_slam"],
    "skeleton_slam_2":          ["skeleton_tongue_slam"],
    "pyrrhon_scorching":        ["skeleton_tongue_slam"],
    "njala_hex":                ["skeleton_tongue_slam"],
    "draavio_falchion":         ["skeleton_tongue_slam"],
    "antechamber_post":         [],
    # Gift room — gargoyle sequence
    "gift_room":                ["gargoyle_dd"],
    "draavio_bow_miss":         ["gargoyle_dd"],
    "gargoyle_dive":            ["gargoyle_dive"],
    "gargoyle_combat":          ["gargoyle_dd"],
    "gift_room_heal":           [],
    # Circle room — crab creature
    "circle_room":              ["crab_creature"],
    "draavio_gesture_njala":    ["crab_creature"],
    "njala_vial":               ["crab_creature"],
    "draavio_approach":         ["crab_creature"],
    "crab_interact":            ["crab_creature"],
    "circle_room_trap":         [],
    # Were-soldier sequence (camping/waiting)
    "were_soldier_composed":    ["were_soldier_human"],
    "were_soldier_breaking":    ["were_soldier_scent"],
    "were_soldier_down":        ["were_soldier_crumpled"],
    # Researcher sequence
    "researchers_arrive":       ["researcher_1", "researcher_2", "researcher_3", "researcher_4"],
    "researchers_sick":         ["researcher_sick", "researcher_crumpled"],
    # Circle room battle
    "circle_room_battle":       ["flesh_golem_dd"],
    "draavio_returned":         ["flesh_golem_dd"],
    "golem_talk":               ["flesh_golem_dd"],
    "joey_sheet":               ["flesh_golem_dd"],
    "battle_after":             [],
    "peacock_intro":            ["peacock_woman"],
    "peacock_fades":            ["peacock_woman_dust"],
    # Trial / archivist
    "circle_room_trial":        ["azazel_archivist"],
    "archivist_ring":           ["azazel_archivist"],
    "scratch_iguana":           ["azazel_archivist"],
    "language_invent":          ["azazel_archivist"],
    # Goat
    "outside_grove":            [],   # goat is small, center, in the plate
    "goat_pen":                 ["talking_goat_dd"],
    "goat_porthole":            ["goat_porthole"],
}

# ── Character sheet prompts ───────────────────────────────────────────────────
# Realistic render of a filled-out Pathfinder (Paizo) character sheet.
_SHEET = (
    "A filled-out Pathfinder RPG character sheet (Paizo official layout). "
    "Portrait orientation, flat lay, slight angle as if on a table. "
    "Hand-written entries in ink, realistic paper texture. "
    "The sheet is clearly in use — dice nearby, pencil marks, eraser ghosts. "
    "Realistic style, warm overhead light. "
)
SHEET_PROMPTS: dict[str, tuple[str, str]] = {
    "sheet_draavio": (
        _SHEET + "Character name: DRAAVIO. Player: Merlin. Class: Ranger 3 / Alchemist 4. "
        "Half-orc. Hit points 68. Strength 18, Dexterity 16, Constitution 14, Intelligence 22, Wisdom 18. "
        "The sheet has a scroll case drawn in the margin. Pink carabiner note visible. "
        "Two class lines filled — the build is visible as a deliberate financial decision.",
        "realistic"
    ),
    "sheet_pyrrhon": (
        _SHEET + "Character name: PYRRHON THE THRICE-KINDLED. Player: Sheldon Cooper. "
        "Class: Wizard 7 (evocation, admixture). Human. Hit points 45. "
        "Three highlighters — orange, blue, green — used heavily. "
        "STINKING CLOUD underlined in all three colors. FALSE LIFE noted with an orange tax annotation. "
        "Feat list reads like a single argument: every line points the same direction.",
        "realistic"
    ),
    "sheet_njala": (
        _SHEET + "Character name: NJÁLA. Player: Lisbeth Salander. "
        "Class: Witch 3 / Rogue 4. Human. Hit points 48. "
        "Written entirely in pencil. Eraser marks visible on the witch/rogue split line. "
        "LINGUISTICS: 0. The vial line is clean. COMMON is not on the sheet.",
        "realistic"
    ),
    "sheet_merit": (
        _SHEET + "Character name: MERIT OF THE FORD. Player: (blank). "
        "Class: Paladin 7. Gnome. Small. Hit points 67. "
        "No archetype line — not a blank field, the line simply does not exist on this sheet. "
        "Code of conduct written on the back in the same hand as the front. "
        "Spell slots present but empty. The code is not a prepared list.",
        "realistic"
    ),
    "sheet_raymora": (
        _SHEET + "Character name: RAYMORA THE DRAGON. Player: Joey Tribbiani. "
        "The labels are reversed from a standard sheet. "
        "Class: Druid 7. Human. Hit points 52. Heal +17 — more ranks than anyone at the table. "
        "DOCTOR written in the margin where the sheet has no line for it. "
        "Two feat lines blank. He did not know they were his.",
        "realistic"
    ),
}

# ── Table-mode frame IDs (pre-game only — act=0) ─────────────────────────────
# These frames use the table background + player portrait overlays.
# The ONLY gate that matters is act == 0. Any frame in act ≥ 1 is DD mode.
# coda_code and manual_page appear in act=0 AND act=1; act is the authoritative gate.
TABLE_MODE_FRAMES = {
    "pre_game_table", "sheet_draavio", "sheet_pyrrhon", "sheet_njala",
    "sheet_merit", "sheet_raymora",
}

# Frame IDs that need a background fallback because they have no PNG.
# Maps frame_id → bg_id to use when act context alone isn't enough.
FRAME_BG_FALLBACK: dict[str, str] = {
    "coda_code":             "cliff_top_night",
    "manual_page":           "pre_game_table",
    "merlin_alone":          "pre_game_table",
    "party_table":           "pre_game_table",
    "trap_diagram":          "circle_room_trap",
    "note_goat":             "circle_room_trap",
    "goat_pen":              "circle_room",
    "volare_fourth_wall":    "gift_room",
    "axiomite_screen":       "pre_game_table",
    "break_table":           "pre_game_table",
    "joey_drops_wildshape":  "circle_room_trap",
    "draavio_returned":      "circle_room_battle",
    "golem_talk":            "circle_room_battle",
    "golem_to_hole":         "circle_room_battle",
    "golem_in_hole":         "circle_room_battle",
    "battle_after":          "circle_room_battle",
    "archivist_card":        "circle_room_trial",
    "joey_sheet":            "circle_room_battle",
    "extract_handout":       "circle_room_trap",
    "scratch_table":         "cliff_top_night",
    "scratch_decode_1":      "cliff_top_night",
    "scratch_decode_2":      "cliff_top_night",
    "scratch_finale":        "circle_room_trial",
    # Climb sequence — all use mountain_road background
    "climb_njala_top":       "mountain_road",
    "climb_merit_top":       "mountain_road",
    "joey_wildshape":        "mountain_road",
    "iguana_on_rope":        "mountain_road",
    # Combat actions — inherit act background
    "skeleton_lick":         "antechamber",
    "skeleton_slam":         "antechamber",
    "were_soldier_composed": "circle_room_battle",
    "were_soldier_breaking": "circle_room_battle",
    "were_soldier_down":     "circle_room_battle",
    "peacock_intro":         "circle_room_battle",
    "peacock_fades":         "circle_room_battle",
}

# Seat positions for player portraits in the table frame (x%, y% of 1280×720)
# Round table: Feynman at top-center behind screen, players arrayed around.
SEAT_POSITIONS: dict[str, tuple[float, float]] = {
    "Feynman":   (0.50, 0.15),   # top center, behind screen
    "Narrator":  (0.50, 0.15),   # Narrator is Feynman's voice
    "Draavio":   (0.20, 0.30),   # left of Feynman
    "Merlin":    (0.20, 0.30),
    "Sheldon":   (0.35, 0.55),   # Sheldon and Lisbeth sit next to each other
    "Pyrrhon":   (0.35, 0.55),
    "Lisbeth":   (0.50, 0.65),
    "LisbethEn": (0.50, 0.65),
    "Njála":     (0.50, 0.65),
    "Witch":     (0.65, 0.55),
    "Merit":     (0.65, 0.55),
    "Joey":      (0.80, 0.30),
    "Raymora":   (0.80, 0.30),
    "Vincent":   (0.80, 0.65),   # seventh chair
}

# The manual_page "organize a trip" text — shown as a visible page overlay
MANUAL_PAGE_TEXT = [
    "You can also",
    "",
    "    Organize a trip (fares, tickets, places to see, good addresses....)",
    "    Gather classified ads from different sites",
    "    Centralize your favorite recipes",
    "    Compile articles about your passions",
    "    Compare offers and prices",
    "    Gather everything that documents your thesis",
    "    etc.",
    "",
    "How does it work?",
]

# ── Procedurally-rendered frame IDs ──────────────────────────────────────────
# These frames are drawn by draw_frame() directly rather than from a PNG.
# bg_plate() returns None for these; draw_frame() catches that and calls
# the appropriate procedural renderer.
PROCEDURAL_FRAMES = {
    # DD chapter cards — black background, thin serif title
    "chapter_card_table", "chapter_card_mountain", "chapter_card_antechamber",
    "chapter_card_gift", "chapter_card_corridor", "chapter_card_circle",
    "chapter_card_trap", "chapter_card_goat", "chapter_card_wait",
    "chapter_card_battle", "chapter_card_archivist", "chapter_card_close",
    # Initiative displays — DD-style order list
    "initiative_1", "initiative_2", "initiative_3",
    # Overlay frames drawn on top of current background
    "scratch_table", "scratch_decode_1", "scratch_decode_2", "scratch_finale",
    "combat_rolls", "circle_break",
    # manual_page — procedural text overlay of the "organize a trip" page
    "manual_page",
}

# Chapter card titles (frame_id → display text)
CHAPTER_TITLES: dict[str, str] = {
    "chapter_card_table":        "THE TABLE",
    "chapter_card_mountain":     "THE MOUNTAIN",
    "chapter_card_antechamber":  "THE ANTECHAMBER",
    "chapter_card_gift":         "THE GIFT ROOM",
    "chapter_card_corridor":     "THE CORRIDOR",
    "chapter_card_circle":       "THE CIRCLE ROOM",
    "chapter_card_trap":         "THE TRAP",
    "chapter_card_goat":         "THE GOAT CONVERSATION",
    "chapter_card_wait":         "THE WAIT",
    "chapter_card_battle":       "THE BATTLE",
    "chapter_card_archivist":    "THE ARCHIVIST",
    "chapter_card_close":        "THE SESSION CLOSES",
}

# Initiative blocks — rendered as DD-style text overlay
INITIATIVE_BLOCKS: dict[str, list[tuple[str, str]]] = {
    "initiative_1": [
        ("Njála",           "17"),
        ("Pyrrhon",         "15"),
        ("skeleton",        "13"),
        ("Draavio",         "11"),
        ("Merit",           " 8"),
        ("Raymora",         " 6"),
        ("The Archivist",   "delays"),
    ],
    "initiative_2": [
        ("Draavio",         "19"),
        ("Njála",           "17"),
        ("Pyrrhon",         "14"),
        ("Merit",           "12"),
        ("Gargoyle",        "11"),
        ("Raymora",         " 9"),
        ("The Archivist",   "delays"),
    ],
    "initiative_3": [
        ("Njála",           "17"),
        ("Pyrrhon",         "14"),
        ("Merit",           "12"),
        ("peacock woman",   "10"),
        ("flesh golem",     " 8"),
        ("Raymora",         " 6"),
        ("soldiers",        "variable"),
        ("The Archivist",   "delays"),
    ],
}


def _smooth(a: float, b: float, t: float) -> float:
    if t <= a:
        return 0.0
    if t >= b:
        return 1.0
    u = (t - a) / (b - a)
    return u * u * (3.0 - 2.0 * u)


def _theta_leaf() -> object:
    """One capital theta, the same leaf as web/gate/theta_leaf.svg.

    The hinge is on the left. The right door is this surface flipped.
    """
    import pygame
    key = "theta-leaf"
    if key in _cache:
        return _cache[key]
    s = 1.62
    bone = (232, 220, 196)
    rust = (140, 58, 42)
    w, h = int(200 * s), int(240 * s)
    surf = pygame.Surface((w, h), pygame.SRCALPHA)
    cx, cy = 100 * s, 120 * s

    def E(rx, ry):
        return pygame.Rect(int(cx - rx), int(cy - ry), int(rx * 2), int(ry * 2))

    for i in range(24):
        a = i * math.pi / 12
        c, sn = math.cos(a), math.sin(a)
        if abs(c) > 0.88:
            continue
        x1, y1 = cx + c * 86 * s, cy + sn * 104 * s
        x2, y2 = cx + c * 93 * s, cy + sn * 112 * s
        pygame.draw.line(surf, bone, (x1, y1), (x2, y2), max(1, int(1.6 * s)))

    pygame.draw.ellipse(surf, bone, E(72 * s, 88 * s), max(1, int(10 * s)))
    pygame.draw.ellipse(surf, rust, E(60 * s, 74 * s), max(1, int(1.5 * s)))
    pygame.draw.ellipse(surf, (*bone, 140), E(56 * s, 69 * s), max(1, int(s)))
    pygame.draw.rect(surf, bone, pygame.Rect(int(46 * s), int(114 * s), int(108 * s), int(12 * s)))
    pygame.draw.rect(surf, bone, pygame.Rect(int(44 * s), int(105 * s), int(8 * s), int(30 * s)))
    pygame.draw.rect(surf, bone, pygame.Rect(int(148 * s), int(105 * s), int(8 * s), int(30 * s)))
    hx = 14 * s
    pygame.draw.rect(surf, bone, pygame.Rect(int(hx - s), int(102 * s), int(2 * s), int(36 * s)))
    for hy in (106 * s, 120 * s, 134 * s):
        pygame.draw.circle(surf, bone, (int(hx), int(hy)), max(2, int(3.4 * s)))
    _cache[key] = surf
    _cache["theta-leaf-right"] = pygame.transform.flip(surf, True, False)
    _cache["theta-s"] = s
    return surf


def _hallway_plate():
    import pygame
    key = "hallway-cover"
    if key in _cache:
        return _cache[key]
    if not HALLWAY_PNG.exists():
        _cache[key] = None
        return None
    img = pygame.image.load(str(HALLWAY_PNG)).convert()
    iw, ih = img.get_size()
    scale = max(W / iw, H / ih)
    nw, nh = int(iw * scale), int(ih * scale)
    scaled = pygame.transform.smoothscale(img, (nw, nh))
    cover = pygame.Surface((W, H))
    cover.blit(scaled, ((W - nw) // 2, (H - nh) // 2))
    _cache[key] = cover
    return cover


def _blit_aperture(screen, hall, scale: float, radius: int, alpha: int) -> None:
    import pygame
    if hall is None or radius < 2 or alpha <= 0:
        return
    nw, nh = max(1, int(W * scale)), max(1, int(H * scale))
    scaled = pygame.transform.smoothscale(hall, (nw, nh))
    frame = pygame.Surface((W, H), pygame.SRCALPHA)
    frame.blit(scaled, ((W - nw) // 2, (H - nh) // 2))
    frame.fill((255, 255, 255, alpha), special_flags=pygame.BLEND_RGBA_MULT)
    hole = pygame.Surface((W, H), pygame.SRCALPHA)
    pygame.draw.circle(hole, (255, 255, 255, 255), (W // 2, H // 2), int(radius))
    frame.blit(hole, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    screen.blit(frame, (0, 0))


def _blit_leaf(screen, leaf, hinge_x: int, sx: float, alpha: int, right: bool) -> None:
    import pygame
    if alpha <= 0 or sx <= 0.02:
        return
    w, h = leaf.get_size()
    nw = max(1, int(w * sx))
    scaled = pygame.transform.smoothscale(leaf, (nw, h))
    if alpha < 255:
        scaled.set_alpha(alpha)
    y = H // 2 - h // 2
    if right:
        screen.blit(scaled, (int(hinge_x - nw), y))
    else:
        screen.blit(scaled, (int(hinge_x), y))


def _draw_act00(screen, t: float) -> None:
    """Black, then ΘΘ, then the hallway comes through the opening."""
    import pygame
    screen.fill(INK)
    appear = _smooth(0.40, 1.35, t)
    opened = _smooth(1.45, 3.25, t)
    sucked = _smooth(3.15, 5.45, t)
    if appear <= 0 and sucked <= 0:
        return

    hall_a = int(255 * min(1.0, opened * 0.45 + sucked))
    hall_s = 1.0 + sucked * 2.7
    radius = int(opened * 150 + sucked * 1200)
    _blit_aperture(screen, _hallway_plate(), hall_s, radius, hall_a)

    leaf = _theta_leaf()
    right = _cache["theta-leaf-right"]
    s = _cache["theta-s"]
    # Ring outer edge, in the unflipped leaf. The letters sit almost touching.
    ring_r = (100 + 72 + 5) * s
    gap = 8 + int(opened * 70 + sucked * 380)
    left_hinge = W // 2 - gap - ring_r
    right_hinge = W // 2 + gap + ring_r
    sx = 1.0 - opened * 0.62 - sucked * 0.30
    alpha = int(255 * appear * (1.0 - sucked * 0.92))
    _blit_leaf(screen, leaf, int(left_hinge), sx, alpha, False)
    _blit_leaf(screen, right, int(right_hinge), sx, alpha, True)


def _draw_chapter_card(screen, frame_id: str, font_big, font_small) -> None:
    """Black card, thin serif act title, centered."""
    import pygame
    screen.fill(INK)
    title = CHAPTER_TITLES.get(frame_id, frame_id.replace("_", " ").upper())
    lbl = font_big.render(title, True, BONE)
    screen.blit(lbl, (W // 2 - lbl.get_width() // 2, H // 2 - lbl.get_height() // 2))
    # Thin rule above and below
    pygame.draw.line(screen, CHALK, (W // 4, H // 2 - 40), (3 * W // 4, H // 2 - 40), 1)
    pygame.draw.line(screen, CHALK, (W // 4, H // 2 + 40), (3 * W // 4, H // 2 + 40), 1)


def _draw_initiative(screen, frame_id: str, bg, font, font_mono) -> None:
    """DD-style initiative block drawn over current background."""
    import pygame
    if bg:
        screen.blit(bg, (0, 0))
    else:
        screen.fill(NIGHT)

    block = INITIATIVE_BLOCKS.get(frame_id, [])
    panel_w, panel_h = 360, 30 + 38 * len(block)
    panel_x = W // 2 - panel_w // 2
    panel_y = H // 2 - panel_h // 2

    panel = pygame.Surface((panel_w, panel_h), pygame.SRCALPHA)
    panel.fill((0, 0, 0, 200))
    screen.blit(panel, (panel_x, panel_y))

    pygame.draw.rect(screen, RUST, (panel_x, panel_y, panel_w, panel_h), 1)
    hdr = font.render("INITIATIVE", True, AMBER)
    screen.blit(hdr, (panel_x + panel_w // 2 - hdr.get_width() // 2, panel_y + 6))

    for i, (name, init) in enumerate(block):
        y = panel_y + 32 + i * 36
        clr = PARCHMENT if name not in ("skeleton", "Gargoyle", "flesh golem",
                                         "peacock woman", "soldiers") else RUST
        screen.blit(font_mono.render(name, True, clr), (panel_x + 12, y))
        v = font_mono.render(init, True, clr)
        screen.blit(v, (panel_x + panel_w - v.get_width() - 12, y))
        pygame.draw.line(screen, (*CHALK, 60),
                         (panel_x + 8, y + 28), (panel_x + panel_w - 8, y + 28), 1)


# ── Manual page procedural renderer ──────────────────────────────────────────
def _draw_manual_page(screen, font, font_mono) -> None:
    """Render the 'organize a trip' SRD help text as a visible page overlay."""
    import pygame
    # Off-white page panel, centred
    pw, ph = 720, 380
    px, py = (W - pw) // 2, (H - ph) // 2
    panel = pygame.Surface((pw, ph), pygame.SRCALPHA)
    panel.fill((245, 240, 228, 230))   # aged paper
    screen.blit(panel, (px, py))
    pygame.draw.rect(screen, (160, 140, 100), (px, py, pw, ph), 2)

    y = py + 18
    for line in MANUAL_PAGE_TEXT:
        rendered = font_mono.render(line, True, (40, 35, 25))
        screen.blit(rendered, (px + 24, y))
        y += 28
        if y > py + ph - 24:
            break


# ── Image API render ──────────────────────────────────────────────────────────
# Drawn at 330×220 (lying figure), so rendered landscape.
WIDE_SPRITES = {"njala_fallen"}

def render_image(sid: str, prompt: str, style: str, dest: Path) -> Path:
    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.exists() and dest.stat().st_size > 1000:
        print(f"  [skip] {sid}")
        return dest
    key = os.environ.get("OPENAI_API_KEY", "").strip()
    if not key:
        sys.exit("Set OPENAI_API_KEY in .env or environment")
    transparent = sid in CHAR_PROMPTS or sid in PLAYER_STANDING_PROMPTS or sid in ENEMY_PROMPTS
    size = "1024x1536" if transparent and sid not in WIDE_SPRITES else "1536x1024"
    full_prompt = (STYLE_DD if style == "dd" else "") + prompt
    payload = {
        "model": "gpt-image-1.5",
        "prompt": full_prompt,
        "size": size,
        "quality": "high",
        "output_format": "png",
        "n": 1,
        "background": "transparent" if transparent else "opaque",
    }
    import requests
    r = requests.post(
        "https://api.openai.com/v1/images/generations",
        headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
        json=payload,
        timeout=180,
    )
    if r.status_code != 200:
        sys.exit(f"{sid} failed {r.status_code}: {r.text[:400]}")
    dest.write_bytes(base64.b64decode(r.json()["data"][0]["b64_json"]))
    print(f"  [ok] {sid}  {dest.stat().st_size // 1024}KB")
    return dest


def cmd_stills(render: bool = False) -> None:
    print("── Backgrounds ──────────────────────────────────────────────────")
    for sid, (prompt, style) in BG_PROMPTS.items():
        dest = bg_path(sid)
        if render:
            render_image(sid, prompt, style, dest)
        else:
            print(f"  [dry] {sid}")

    print("── Special frames ───────────────────────────────────────────────")
    for sid, (prompt, style) in SPECIAL_FRAME_PROMPTS.items():
        dest = bg_path(sid)
        if render:
            render_image(sid, prompt, style, dest)
        else:
            print(f"  [dry] {dest.relative_to(BACKGROUNDS)}")

    print("── Character sprites ─────────────────────────────────────────────")
    for sid, (prompt, style) in CHAR_PROMPTS.items():
        folder = PLAYERS if style == "player" else CHARACTERS
        dest = folder / f"{sid}.png"
        if render:
            render_image(sid, prompt, style, dest)
        else:
            print(f"  [dry] {sid}")

    print("── Player standing sprites ───────────────────────────────────────")
    for sid, (prompt, style) in PLAYER_STANDING_PROMPTS.items():
        dest = PLAYERS / f"{sid}.png"
        if render:
            render_image(sid, prompt, style, dest)
        else:
            print(f"  [dry] {sid}")

    print("── Enemy / NPC sprites ───────────────────────────────────────────")
    for sid, (prompt, style) in ENEMY_PROMPTS.items():
        dest = ENEMIES / f"{sid}.png"
        if render:
            render_image(sid, prompt, style, dest)
        else:
            print(f"  [dry] {sid}")

    print("── Character sheets ──────────────────────────────────────────────")
    for sid, (prompt, style) in SHEET_PROMPTS.items():
        dest = bg_path(sid)
        if render:
            render_image(sid, prompt, style, dest)
        else:
            print(f"  [dry] {sid}")


# ── Plate cache ───────────────────────────────────────────────────────────────
_cache: dict[str, object] = {}


def load_plate(path: Path, size: tuple[int, int], alpha: bool = False):
    import pygame
    key = f"{path}:{size}:{alpha}"
    if key not in _cache:
        if not path.exists():
            _cache[key] = None
        else:
            img = pygame.image.load(str(path))
            img = img.convert_alpha() if alpha else img.convert()
            _cache[key] = pygame.transform.smoothscale(img, size)
    return _cache[key]


def bg_plate(name: str):
    if name not in BG_HOME:
        return None
    p = bg_path(name)
    return load_plate(p, (W, H), False) if p.exists() else None


# What the current still drew, for shots.jsonl.
_SHOT: dict = {"bg": None, "sprites": [], "missing": []}


def char_plate(name: str, size: tuple[int, int] | None = None):
    sz = size or CHAR_SIZES.get(name, (260, 480))
    for d in (CHARACTERS, ENEMIES, PLAYERS):
        p = d / f"{name}.png"
        if p.exists():
            _SHOT["sprites"].append(name)
            return load_plate(p, sz, True)
    return None


# ── Amber glow overlay ────────────────────────────────────────────────────────
def _make_glow(size: tuple[int, int]) -> object:
    """Return a pygame Surface: amber radial glow at 30% opacity."""
    import pygame
    key = f"glow:{size}"
    if key not in _cache:
        surf = pygame.Surface(size, pygame.SRCALPHA)
        cx, cy = size[0] // 2, size[1] // 2
        max_r  = max(size) // 2
        for r in range(max_r, 0, -1):
            alpha = int(76 * (1.0 - r / max_r))   # 0–76 ≈ 0–30%
            pygame.draw.circle(surf, (*AMBER, alpha), (cx, cy), r)
        _cache[key] = surf
    return _cache[key]


# ── Cues ──────────────────────────────────────────────────────────────────────
# Sauron, the pole messenger. He announces the act and nothing else.
SAURON_VOICE_ID = os.environ.get("VOICE_SAURON", "M2HASKhyinBcyBrKOfms")  # Sauron (Default)
ACTS_DIR = AUDIO / "acts"

_cue_scale_cache: float | None = None


def act_label(n: int) -> str:
    return "ACT 00" if n == 0 else f"ACT {n}"


def act_spoken(n: int) -> str:
    return "ACT ZERO ZERO." if n == 0 else f"ACT {n}."


def load_cues() -> list[dict]:
    p = AUDIO / "cues.jsonl"
    if not p.exists():
        return []
    return [json.loads(l) for l in p.read_text().splitlines() if l.strip()]


def _probe_dur(path: Path) -> float:
    r = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1", str(path)],
        capture_output=True, text=True,
    )
    return float(r.stdout.strip())


def get_cue_scale(cues: list[dict]) -> float:
    global _cue_scale_cache
    if _cue_scale_cache is not None:
        return _cue_scale_cache
    if not cues:
        return 1.0
    cue_dur = cues[-1]["end"]
    try:
        mp3_dur = _probe_dur(AUDIO / "minus08.mp3")
    except Exception:
        mp3_dur = cue_dur
    _cue_scale_cache = cue_dur / mp3_dur if mp3_dur > 0 else 1.0
    return _cue_scale_cache


def audio_to_cue(t: float, cues: list[dict]) -> float:
    return max(0.0, t * get_cue_scale(cues) - AUDIO_OFFSET)


def cue_at(cues: list[dict], cue_t: float) -> dict | None:
    for c in cues:
        if c["start"] <= cue_t < c["end"]:
            return c
    if cues and cue_t >= cues[-1]["end"]:
        return cues[-1]
    return cues[0] if cues else None


def act_from_cue(cues: list[dict], cue_t: float) -> int:
    c = cue_at(cues, cue_t)
    return int(c["act"]) if c and "act" in c else 0


def frame_from_cue(cues: list[dict], cue_t: float) -> str:
    c = cue_at(cues, cue_t)
    return c.get("frame", "") if c else ""


def _act_spans(cues: list[dict]) -> list[tuple[int, float, float]]:
    """(act, cue_start, cue_end) covering the cue timeline without gaps."""
    spans: list[tuple[int, float, float]] = []
    for c in cues:
        act = int(c["act"])
        if not spans or spans[-1][0] != act:
            spans.append((act, c["start"], c["end"]))
        else:
            a, t0, _ = spans[-1]
            spans[-1] = (a, t0, c["end"])
    return spans


def cmd_announce() -> None:
    """Sauron names each act. One short file per act. Existing files are kept."""
    import requests
    key = os.environ.get("ELEVENLABS_API_KEY", "").strip()
    if not key:
        sys.exit("Set ELEVENLABS_API_KEY in .env")
    ACTS_DIR.mkdir(parents=True, exist_ok=True)
    cues = load_cues()
    acts = [a for a, _, _ in _act_spans(cues)] or list(range(12))
    for n in acts:
        dest = ACTS_DIR / f"act_{n:02d}.mp3"
        line = act_spoken(n)
        if dest.exists() and dest.stat().st_size > 1000:
            print(f"  [keep] {dest.name}  {line}")
            continue
        r = requests.post(
            f"https://api.elevenlabs.io/v1/text-to-speech/{SAURON_VOICE_ID}",
            headers={"xi-api-key": key, "Accept": "audio/mpeg",
                     "Content-Type": "application/json"},
            json={
                "text": line,
                "model_id": "eleven_multilingual_v2",
                "voice_settings": {
                    "stability": 0.70,
                    "similarity_boost": 0.80,
                    "style": 0.08,
                    "use_speaker_boost": True,
                },
            },
            timeout=90,
        )
        if r.status_code != 200 or not r.content:
            sys.exit(f"Sauron act {n} failed {r.status_code}: {r.text[:200]}")
        dest.write_bytes(r.content)
        print(f"  [ok] {dest.name}  {line}  {dest.stat().st_size // 1024}KB")


def _card_duration(path: Path) -> float:
    return max(2.2, round(_probe_dur(path) + 0.45, 3))


def _draw_act_card(screen, n: int, font) -> None:
    import pygame
    screen.fill(INK)
    lbl = font.render(act_label(n), True, BONE)
    screen.blit(lbl, (W // 2 - lbl.get_width() // 2, H // 2 - lbl.get_height() // 2))
    y0 = H // 2 - lbl.get_height() // 2 - 28
    y1 = H // 2 + lbl.get_height() // 2 + 28
    pygame.draw.line(screen, CHALK, (W // 3, y0), (2 * W // 3, y0), 1)
    pygame.draw.line(screen, CHALK, (W // 3, y1), (2 * W // 3, y1), 1)


# ── Visual breakpoints ────────────────────────────────────────────────────────
def _visual_breakpoints(cues: list[dict]) -> list[float]:
    """One still per cue: the caption, the glow and the script state all change on cues."""
    scale   = get_cue_scale(cues)
    mp3_dur = cues[-1]["end"] / scale if cues else 700.0
    tail    = (mp3_dur + 8.0) * scale
    return sorted({0.0, tail, *(c["start"] for c in cues)})


# ── Draw ──────────────────────────────────────────────────────────────────────
_PARTY_CHARS  = ["draavio", "njala", "merit", "pyrrhon", "raymora_doctor", "raymora_iguana"]
_RIGHT_CHARS  = ["feynman", "vincent", "witch_of_the_rivers"]

def _draw_strike(screen, seq: str, phase: str, speaker: str) -> None:
    """One strike, small: Draavio, the soldier(s) in the flank, the goat behind them."""
    import pygame
    s, d = STRIKES[seq], STRIKES[seq]["dir"]
    y = s["y"]
    k = strike_scale(y)
    gap, flank = int(150 * k), int(120 * k)

    def put(name: str, size: tuple[int, int], cx: int, face: int) -> tuple[int, int] | None:
        size = (int(size[0] * k), int(size[1] * k))
        img = char_plate(name, size)
        if img is None:
            return None
        # Draavio's sprites face right; the goat's faces left.
        native = -1 if name.startswith("goat") else +1
        if face != native:
            img = pygame.transform.flip(img, True, False)
        pos = (cx - size[0] // 2, y - size[1])
        screen.blit(img, pos)
        return pos

    for xs in s["xs"]:
        if phase == "down":
            put("were_soldier_crumpled", STRIKE_SIZES["crumpled"], xs, -d)
        else:
            put("were_soldier_scent", STRIKE_SIZES["soldier"], xs, -d)
        # The goat has the flank: the far side of the soldier from Draavio.
        put("goat_flank", STRIKE_SIZES["goat"], xs + d * flank, -d)

    first = s["xs"][0]
    if phase == "point":
        pose, cx = "draavio_point", s["x0"]
    elif phase == "swing":
        pose, cx = "draavio_lurch", (s["x0"] + first - d * gap) // 2
    else:
        # Two in one turn: he finishes facing the second.
        last = s["xs"][-1]
        face = d if len(s["xs"]) == 1 else (1 if last > s["x0"] else -1)
        pose, cx = "draavio_strike", last - face * gap
        d = face
    sz = STRIKE_SIZES["draavio"]
    pos = put(pose, sz, cx, d) or put("draavio", sz, cx, d)
    if pos and SPEAKER_CHAR.get(speaker) == "draavio":
        screen.blit(_make_glow((int(sz[0] * k), int(sz[1] * k))), pos)


def _draw_sprites(screen, cue, act: int, frame_id: str, speaker: str, speaking_char: str,
                  in_table_mode: bool, brk: bool, audio_t: float, font) -> None:
    import pygame
    joey_is_iguana = cue_state(cue, "raymora") == "iguana"
    # Characters off this frame: still on the climb, or Draavio gone through the oak.
    climb_gone_chars = set(CLIMB_GONE.get(frame_id, set()))
    if cue_state(cue, "draavio") == "gone":
        climb_gone_chars.add("draavio")
    njala_down = cue_state(cue, "njala") == "down"
    strike = strike_phase(frame_id)
    battle = frame_id in BATTLE_FRAMES or strike is not None

    # ── Who stands at the table (act 0 and the break) ────────────────────────
    # Nobody until Merlin reads the manual. Feynman arrives with the others.
    # Vincent's chair is empty until he walks in at the end of act 1.
    if in_table_mode and (frame_id in OCCUPIED_TABLE_FRAMES or brk):
        spk_key = PLAYER_STANDING_KEY.get(speaker, "")
        _PSZ  = (150, 375)
        _FPSZ = (170, 420)

        if frame_id in MERLIN_ALONE_FRAMES and not brk:
            variant = "_talk" if spk_key == "pstand_merlin" else "_main"
            img = char_plate("pstand_merlin" + variant, _PSZ) or char_plate("pstand_merlin_main", _PSZ)
            if img:
                mx = W // 2 - _PSZ[0] // 2
                my = H - _PSZ[1] - 10
                screen.blit(img, (mx, my))
                if spk_key == "pstand_merlin":
                    screen.blit(_make_glow(_PSZ), (mx, my))
        else:
            if spk_key == "pstand_feynman":
                f_variant = "pstand_feynman_gesture" if int(audio_t // 6) % 2 else "pstand_feynman_talk"
            else:
                f_variant = "pstand_feynman_main"
            f_img = char_plate(f_variant, _FPSZ) or char_plate("pstand_feynman_main", _FPSZ)
            if f_img:
                fx = W // 2 - _FPSZ[0] // 2
                fy = 20
                screen.blit(f_img, (fx, fy))
                if spk_key == "pstand_feynman":
                    screen.blit(_make_glow(_FPSZ), (fx, fy))
            line = ACT0_LINE + (["pstand_vincent"] if cue_state(cue, "vincent") == "seated" else [])
            slot = W // len(line)
            for i, pkey in enumerate(line):
                variant = "_talk" if pkey == spk_key else "_main"
                img = char_plate(pkey + variant, _PSZ) or char_plate(pkey + "_main", _PSZ)
                if img is None:
                    continue
                x = slot * i + (slot - _PSZ[0]) // 2
                y = H - _PSZ[1] - 10
                screen.blit(img, (x, y))
                if pkey == spk_key:
                    screen.blit(_make_glow(_PSZ), (x, y))
        return
    if in_table_mode:
        return

    # A strike at the back of the room is drawn behind the line.
    if strike and STRIKES[strike[0]]["y"] < 600:
        _draw_strike(screen, *strike, speaker)

    # ── The Portable Hole, by the oak, once the golem is led to it ───────────
    if frame_id in ("golem_in_hole", "battle_after"):
        hx, hy = HOLE_CENTER
        hw, hh = HOLE_SIZE
        pygame.draw.ellipse(screen, (4, 4, 6), (hx - hw // 2, hy - hh // 2, hw, hh))

    # ── Party sprites — DD line ──────────────────────────────────────────────
    if frame_id == "iguana_on_rope":
        # Only iguana visible — on the rope, midway up the cliff
        _active_party = ["raymora_iguana"]
    else:
        # Build active list: swap doctor ↔ iguana, remove climbed-away chars
        _active_party = []
        for char_key in _PARTY_CHARS:
            base = char_key.replace("_iguana", "").replace("_doctor", "")
            if base in climb_gone_chars:
                continue
            if base == "raymora":
                char_key = "raymora_iguana" if joey_is_iguana else "raymora_doctor"
                if char_key in _active_party:
                    continue
            _active_party.append(char_key)
        # Lying on the floor, she is nearest the camera.
        if njala_down and "njala" in _active_party:
            _active_party.remove("njala")
            _active_party.append("njala")

    for char_key in _active_party:
        base_key = char_key.replace("_iguana", "").replace("_doctor", "")
        if frame_id in RESTING_FRAMES:
            rest_key = base_key + "_rest"
            if (CHARACTERS / f"{rest_key}.png").exists():
                char_key = rest_key
        if base_key == "njala" and njala_down:
            char_key = "njala_fallen"
        if frame_id == "iguana_on_rope" and char_key == "raymora_iguana":
            sz  = (80, 120)
            pos = (W // 2 - 40, H // 2 - 20)   # center-ish, partway up
        elif char_key == "njala_fallen":
            sz  = (330, 220)
            pos = (140, _BASE - 190)
        else:
            pos = (CHAR_POSITIONS.get(char_key)
                   or CHAR_POSITIONS.get(base_key.capitalize())
                   or CHAR_POSITIONS.get(base_key, (0, 0)))
            sz  = (CHAR_SIZES.get(char_key)
                   or CHAR_SIZES.get(base_key.capitalize())
                   or (260, 480))
        img = char_plate(char_key, sz)
        if img and frame_id in FLIP_FRAMES:
            img = pygame.transform.flip(img, True, False)
        if img:
            screen.blit(img, pos)
        else:
            _SHOT["missing"].append(char_key)
            ph = pygame.Surface(sz, pygame.SRCALPHA)
            ph.fill((*NIGHT, 160))
            pl = font.render(char_key[:8], True, BONE)
            ph.blit(pl, (4, sz[1] // 2))
            screen.blit(ph, pos)
        speaking_base = (SPEAKER_CHAR.get(speaker, "") or "").lower()
        if speaking_base and (char_key.startswith(speaking_base) or base_key == speaking_base):
            screen.blit(_make_glow(sz), pos)

    # ── Enemy sprites — right side ───────────────────────────────────────────
    if frame_id == "golem_to_hole":
        # Led across the room toward the oak, standing.
        sz = (300, 480)
        img = char_plate("flesh_golem_dd", sz)
        if img:
            screen.blit(img, (HOLE_CENTER[0] + 40, HOLE_CENTER[1] + 60 - sz[1]))
    elif frame_id == "golem_in_hole":
        # Seated in the hole beside the oak, partially in the ground: cut at the rim.
        sz = (300, 480)
        img = char_plate("flesh_golem_dd", sz)
        if img:
            hx, hy = HOLE_CENTER
            screen.set_clip(pygame.Rect(0, 0, W, hy))
            screen.blit(img, (hx - sz[0] // 2, hy + 170 - sz[1]))
            screen.set_clip(None)
    else:
        enemies = FRAME_ENEMIES.get(frame_id, ["flesh_golem_dd"] if strike else [])
        for ekey in enemies:
            e_pos = ENEMY_POSITIONS.get(ekey, (W - 300, H - 500))
            e_sz  = ENEMY_SIZES.get(ekey, (260, 480))
            e_img = char_plate(ekey, e_sz)
            if e_img:
                screen.blit(e_img, e_pos)

    # ── Draavio and the goat, once, in the centre: he is back ────────────────
    if frame_id == "draavio_returned":
        g_sz, d_sz = (220, 330), (270, 480)
        g_img = char_plate("goat_flank", g_sz)
        d_img = char_plate("draavio", d_sz)
        if g_img:
            screen.blit(g_img, (560, _BASE - g_sz[1] + 10))
        if d_img:
            d_pos = (650, _BASE - d_sz[1])
            screen.blit(d_img, d_pos)
            if SPEAKER_CHAR.get(speaker) == "draavio":
                screen.blit(_make_glow(d_sz), d_pos)

    if strike and STRIKES[strike[0]]["y"] >= 600:
        _draw_strike(screen, *strike, speaker)

    # ── Vincent — trial frames only ──────────────────────────────────────────
    if not battle and frame_id in (
        "circle_room_trial", "archivist_ring", "archivist_card", "scratch_finale",
    ):
        pos = CHAR_POSITIONS.get("Vincent", (W - 220, H - 560))
        sz  = CHAR_SIZES.get("vincent", (260, 480))
        img = char_plate("vincent", sz)
        if img:
            screen.blit(img, pos)
        if speaking_char and speaking_char.lower() == "vincent":
            screen.blit(_make_glow(sz), pos)

    # ── Scratch scene overrides (scratch_iguana / language_invent) ───────────
    # Iguana centered, Draavio in notes pose, Njála in listen pose.
    if frame_id in {"scratch_iguana", "language_invent"}:
        d_sz  = CHAR_SIZES.get("draavio", (290, 520))
        d_pos = CHAR_POSITIONS.get("Draavio", (20, H - 520))
        d_img = char_plate("draavio_notes", d_sz)
        if d_img:
            screen.blit(d_img, d_pos)
        n_sz  = CHAR_SIZES.get("njala", (270, 500))
        n_pos = CHAR_POSITIONS.get("Njala", (240, H - 500))
        n_img = char_plate("njala_listen", n_sz)
        if n_img:
            screen.blit(n_img, n_pos)
        ig_sz  = (200, 280)
        ig_pos = (W // 2 - 100, H - ig_sz[1] - 20)
        ig_img = char_plate("raymora_iguana", ig_sz)
        if ig_img:
            screen.blit(ig_img, ig_pos)
            if speaking_char and "raymora" in (speaking_char or "").lower():
                screen.blit(_make_glow(ig_sz), ig_pos)


def draw_frame(screen, audio_t: float, cues: list[dict], font, font_mono) -> None:
    import pygame
    cue_t         = audio_to_cue(audio_t, cues)
    cue           = cue_at(cues, cue_t)
    act           = act_from_cue(cues, cue_t)
    frame_id      = frame_from_cue(cues, cue_t)
    speaker       = cue["speaker"] if cue else ""
    speaking_char = SPEAKER_CHAR.get(speaker, "")
    font_big      = pygame.font.SysFont("serif", 42)

    # ── Chapter card — full black frame, no sprites ───────────────────────────
    if frame_id in CHAPTER_TITLES:
        _draw_chapter_card(screen, frame_id, font_big, font_mono)
        return

    # ── Background ────────────────────────────────────────────────────────────
    # Act 0 and the break are at the table. Everything else is the dungeon.
    brk           = bool(cue and cue.get("brk"))
    in_table_mode = act == 0 or brk or frame_id == "axiomite_screen"
    # A cut scene has its figures painted in. No sprite is ever drawn over one.
    in_cutscene   = frame_id in CUTSCENE_FRAMES and not in_table_mode

    _SHOT.update(frame=frame_id, act=act, cut=in_cutscene, table=in_table_mode, brk=brk)

    def _resolve_bg(fid: str, act_n: int) -> object:
        """Return a loaded plate for the given frame, with fallback chain."""
        if brk:
            _SHOT["bg"] = "pre_game_table"
            return bg_plate("pre_game_table")
        # 1. The frame's own still; never a prop.
        kind = BG_HOME.get(fid, (None, ""))[1]
        if kind in ("table", "sheet", "loc") or (kind == "cut" and in_cutscene):
            plate = bg_plate(fid)
            if plate:
                _SHOT["bg"] = fid
                return plate
        # 2. Explicit fallback map
        fallback_id = FRAME_BG_FALLBACK.get(fid)
        if fallback_id:
            plate = bg_plate(fallback_id)
            if plate:
                _SHOT["bg"] = fallback_id
                return plate
        # 3. Act background
        act_bg_id = ACT_BACKGROUNDS.get(act_n, "circle_room")
        _SHOT["bg"] = act_bg_id
        return bg_plate(act_bg_id)

    if frame_id in ("initiative_1", "initiative_2", "initiative_3"):
        # Show background behind initiative panel — panel is a brief overlay only
        act_bg = ACT_BACKGROUNDS.get(act, "antechamber")
        _SHOT["bg"] = act_bg
        _draw_initiative(screen, frame_id, bg_plate(act_bg), font, font_mono)
    elif frame_id == "manual_page":
        # procedural: pre_game_table bg + "organize a trip" text overlay
        bg = _resolve_bg(frame_id, act)
        if bg:
            screen.blit(bg, (0, 0))
        else:
            screen.fill((30, 25, 20))
        _draw_manual_page(screen, font, font_mono)
    else:
        bg = _resolve_bg(frame_id, act)
        if bg:
            screen.blit(bg, (0, 0))
        else:
            screen.fill(NIGHT)

    if not in_cutscene:
        _draw_sprites(screen, cue, act, frame_id, speaker, speaking_char,
                      in_table_mode, brk, audio_t, font)

    # ── HUD ───────────────────────────────────────────────────────────────────
    if cue:
        spk_color = {
            "Feynman":  (255, 220, 140),   # warm gold — GM
            "Narrator": BONE,
            "Draavio":  (180, 220, 255),   # cool blue — Merlin
            "Magi":     (180, 220, 255),
            "Merlin":   (180, 220, 255),
            "Pyrrhon":  (255, 240, 200),
            "Raymora":  (255, 200, 160),
            "Lisbeth":  (200, 220, 200),   # flat green
            "LisbethEn":(200, 220, 200),
            "Witch":    (220, 180, 255),   # warm violet
            "Merit":    (200, 230, 255),   # cool plate
            "Sheldon":  (255, 240, 200),   # warm ivory
            "Joey":     (255, 200, 160),   # warm orange — actor energy
            "Vincent":  (160, 200, 180),   # muted teal — precise
            "Goat":     (190, 190, 190),   # flat grey — TTL
        }.get(speaker, CHALK)
        screen.blit(font.render(speaker, True, spk_color), (40, H - 52))
        screen.blit(font_mono.render((cue["text"] or "")[:90], True, CHALK), (40, H - 28))

# ── Pygame preview ────────────────────────────────────────────────────────────
def cmd_pygame(seek: float = 0.0) -> None:
    import pygame
    pygame.init()
    pygame.mixer.init()
    screen = pygame.display.set_mode((W, H))
    pygame.display.set_caption("-08 The Archive at the Mountain")
    clock     = pygame.time.Clock()
    font      = pygame.font.SysFont("serif", 20)
    font_mono = pygame.font.SysFont("monospace", 13)

    cues  = load_cues()
    audio = AUDIO / "minus08.mp3"
    if not audio.exists():
        sys.exit(f"missing audio: {audio}  (run `audio` first)")
    pygame.mixer.music.load(str(audio))

    running = True
    music_on = False
    t0 = pygame.time.get_ticks()
    while running:
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                running = False
            if ev.type == pygame.KEYDOWN and ev.key in (pygame.K_ESCAPE, pygame.K_q):
                running = False
        elapsed = (pygame.time.get_ticks() - t0) / 1000.0
        screen.fill(INK)
        if seek <= 0 and elapsed < ACT00_LEAD:
            _draw_act00(screen, elapsed)
        else:
            if not music_on:
                pygame.mixer.music.play(start=max(0.0, seek))
                music_on = True
            if not pygame.mixer.music.get_busy():
                break
            audio_t = seek + pygame.mixer.music.get_pos() / 1000.0
            draw_frame(screen, audio_t, cues, font, font_mono)
        pygame.display.flip()
        clock.tick(FPS)
    pygame.quit()


# ── Frame export ──────────────────────────────────────────────────────────────
def _append_still(lines: list[str], rel: str, dur: float) -> str:
    lines.append(f"file '{rel}'")
    lines.append(f"duration {dur:.4f}")
    return rel


def cmd_frames() -> None:
    import pygame
    FRAMES.mkdir(parents=True, exist_ok=True)
    os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
    os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
    pygame.init()
    pygame.display.set_mode((1, 1))
    screen    = pygame.Surface((W, H))
    font      = pygame.font.SysFont("serif", 20)
    font_mono = pygame.font.SysFont("monospace", 13)
    font_act  = pygame.font.SysFont("Noto Serif,serif", 84)

    cues = load_cues()
    scale = get_cue_scale(cues)
    spans = _act_spans(cues)
    bps   = _visual_breakpoints(cues)

    concat = OUT / "concat.txt"
    lines  = ["ffconcat version 1.0"]
    last_rel = ""
    manifest = []
    shots: list[dict] = []

    for act, t0, t1 in spans:
        card = ACTS_DIR / f"act_{act:02d}.mp3"
        if not card.exists():
            sys.exit(f"missing {card}  (run announce first)")
        hold = _card_duration(card)
        screen.fill(INK)
        _draw_act_card(screen, act, font_act)
        fname = f"actcard_{act:02d}.png"
        pygame.image.save(screen, str(FRAMES / fname))
        last_rel = _append_still(lines, f"frames/{fname}", hold)
        manifest.append({"kind": "card", "act": act, "dur": hold})
        print(f"  card ACT {act}  {hold:.2f}s  {act_spoken(act)}")

        if act == 0:
            n_lead = int(round(ACT00_LEAD * FPS))
            print(f"  theta lead — {n_lead} frames")
            for i in range(n_lead):
                screen.fill(INK)
                _draw_act00(screen, (i + 0.5) / FPS)
                fn = f"o{i:05d}.png"
                pygame.image.save(screen, str(FRAMES / fn))
                last_rel = _append_still(lines, f"frames/{fn}", 1 / FPS)
            manifest.append({"kind": "lead", "dur": n_lead / FPS})

        pts = [t for t in bps if t0 < t < t1]
        edges = [t0, *pts, t1]
        for i in range(len(edges) - 1):
            a, b = edges[i], edges[i + 1]
            dur = (b - a) / scale
            if dur < 0.04:
                continue
            mid = (a + b) / 2.0
            screen.fill(INK)
            _SHOT.clear()
            _SHOT.update(bg=None, sprites=[], missing=[], cut=False)
            draw_frame(screen, (mid + AUDIO_OFFSET) / scale, cues, font, font_mono)
            fn = f"a{act:02d}_{i:04d}.png"
            pygame.image.save(screen, str(FRAMES / fn))
            last_rel = _append_still(lines, f"frames/{fn}", dur)
            fid = frame_from_cue(cues, mid)
            c = cue_at(cues, audio_to_cue((mid + AUDIO_OFFSET) / scale, cues)) or {}
            spk = c.get("speaker", "?")
            shots.append({
                "still": fn, "act": act, "t": round(a / scale, 3), "dur": round(dur, 3),
                "frame": fid, "cut": _SHOT.get("cut", False), "brk": _SHOT.get("brk", False),
                "bg": _SHOT["bg"], "sprites": _SHOT["sprites"], "missing": _SHOT["missing"],
                "speaker": spk, "state": c.get("state", {}), "text": (c.get("text") or "")[:80],
            })
            print(f"  [{act:02d}.{i:04d}] {dur:6.2f}s  {fid:<24} {spk}", flush=True)
        manifest.append({"kind": "act", "act": act, "cue": [t0, t1]})

    lines.append(f"file '{last_rel}'")
    concat.write_text("\n".join(lines) + "\n")
    (OUT / "assemble.json").write_text(json.dumps({"scale": scale, "spans": spans, "manifest": manifest}))
    pygame.quit()
    (OUT / "shots.jsonl").write_text("".join(json.dumps(s, ensure_ascii=False) + "\n" for s in shots))
    bad_cut = [s["still"] for s in shots if s["cut"] and s["sprites"]]
    bad_missing = [(s["still"], s["missing"]) for s in shots if s["missing"]]
    # Between strikes the room is clear: no soldiers down, no Draavio mid-strike.
    strike_only = {"were_soldier_scent", "were_soldier_crumpled",
                   "draavio_point", "draavio_lurch", "draavio_strike"}
    hits = [i for i, s in enumerate(shots) if s["frame"].startswith("strike_")]
    between = shots[hits[0]:hits[-1] + 1] if hits else []
    bad_linger = [s["still"] for s in between
                  if not s["frame"].startswith("strike_") and strike_only & set(s["sprites"])]
    print(f"Done → {concat}  ({len(shots)} stills, shots.jsonl)")
    if bad_cut or bad_missing or bad_linger:
        sys.exit(f"sprite on a cut scene: {bad_cut[:10]}\nmissing sprites: {bad_missing[:10]}"
                 f"\nstrike sprites outside a strike: {bad_linger[:10]}")


# ── Assembly ──────────────────────────────────────────────────────────────────
def _wav(src_args: list[str], dest: Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        ["ffmpeg", "-y", "-loglevel", "error", *src_args,
         "-c:a", "pcm_s16le", "-ar", "44100", "-ac", "2", str(dest)],
        check=True,
    )


def cmd_assemble() -> None:
    mp4    = OUT / "-08_the_archive.mp4"
    narr   = AUDIO / "minus08.mp3"
    concat = OUT / "concat.txt"
    if not narr.exists():
        sys.exit(f"missing audio: {narr}")
    if not concat.exists():
        sys.exit("concat.txt missing — run frames first")

    cues  = load_cues()
    scale = get_cue_scale(cues)
    mp3_dur = _probe_dur(narr)
    spans = _act_spans(cues)
    work = OUT / "audio_build"
    work.mkdir(parents=True, exist_ok=True)

    pieces: list[Path] = []
    for act, t0, t1 in spans:
        card = ACTS_DIR / f"act_{act:02d}.mp3"
        hold = _card_duration(card)
        padded = work / f"card_{act:02d}.wav"
        _wav(["-i", str(card), "-af", f"apad=whole_dur={hold:.3f}", "-t", f"{hold:.3f}"], padded)
        pieces.append(padded)
        if act == 0:
            lead = work / "lead.wav"
            _wav(["-f", "lavfi", "-i", "anullsrc=r=44100:cl=stereo", "-t", f"{ACT00_LEAD:.3f}"], lead)
            pieces.append(lead)
        a0 = t0 / scale
        a1 = min(mp3_dur, t1 / scale)
        sl = work / f"slice_{act:02d}.wav"
        _wav(["-ss", f"{a0:.4f}", "-to", f"{a1:.4f}", "-i", str(narr)], sl)
        pieces.append(sl)

    alist = work / "concat.txt"
    alist.write_text("".join(f"file '{p.resolve()}'\n" for p in pieces))
    track = work / "track.m4a"
    subprocess.run(
        ["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0",
         "-i", str(alist), "-c:a", "aac", "-b:a", "192k", str(track)],
        check=True,
    )
    subprocess.run(
        ["ffmpeg", "-y", "-stats", "-loglevel", "warning",
         "-f", "concat", "-safe", "0", "-i", str(concat),
         "-i", str(track),
         "-c:v", "libx264", "-preset", "ultrafast", "-tune", "stillimage",
         "-pix_fmt", "yuv420p", "-crf", "20",
         "-c:a", "copy", "-shortest",
         str(mp4)],
        check=True, cwd=str(OUT),
    )
    print(f"Output: {mp4}  ({mp4.stat().st_size // (1024 * 1024)}MB)")


# ── Debug: print frame list ───────────────────────────────────────────────────
def cmd_print_frames() -> None:
    """Print a breakdown of visual breakpoints without rendering."""
    cues = load_cues()
    if not cues:
        print("No cues.jsonl — run audio first.")
        return
    bps = _visual_breakpoints(cues)
    scale = get_cue_scale(cues)
    print(f"{'#':<5}  {'act':<4}  {'cue_t':>7}  {'hold':>7}  {'frame':<28}  speaker")
    print("-" * 80)
    for i in range(len(bps) - 1):
        cue_start = bps[i]
        cue_end   = bps[i + 1]
        mid       = (cue_start + cue_end) / 2.0
        dur       = (cue_end - cue_start) / scale
        act       = act_from_cue(cues, mid)
        frame_id  = frame_from_cue(cues, mid)
        c         = cue_at(cues, mid)
        spk       = c["speaker"] if c else "?"
        print(f"  {i:<3}  {act:<4}  {mid:7.1f}s  {dur:6.2f}s  {frame_id:<28}  {spk}")
    print(f"\n{len(bps) - 1} frames total")


# ── CLI ───────────────────────────────────────────────────────────────────────
def main() -> None:
    ap = argparse.ArgumentParser(description="Build -08 The Archive at the Mountain")
    ap.add_argument("cmd", choices=[
        "audio", "announce", "stills", "pygame", "frames", "assemble", "all", "cmd_frames"
    ])
    ap.add_argument("--render", action="store_true",
                    help="Actually call image API (stills command)")
    ap.add_argument("--seek", type=float, default=0.0,
                    help="Seek position in seconds (pygame command)")
    args = ap.parse_args()

    if   args.cmd == "audio":      cmd_announce()
    elif args.cmd == "announce":   cmd_announce()
    elif args.cmd == "stills":     cmd_stills(render=args.render)
    elif args.cmd == "pygame":     cmd_pygame(seek=args.seek)
    elif args.cmd == "frames":     cmd_frames()
    elif args.cmd == "assemble":   cmd_assemble()
    elif args.cmd == "cmd_frames": cmd_print_frames()
    elif args.cmd == "all":
        cmd_announce()
        cmd_frames()
        cmd_assemble()


if __name__ == "__main__":
    main()
