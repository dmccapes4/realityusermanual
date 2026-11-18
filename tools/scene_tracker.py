#!/usr/bin/env python3
"""Parse audio/minus08/cues.jsonl → images/minus08/scenes.jsonl + portraits.jsonl.

Maintains a state machine over the cue stream:
  - setting: which location we're in
  - aesthetic: lighting/palette/mood for the current setting
  - characters_present: who is in the scene
  - speaking: who is currently producing audio

Emits a new scene record when setting changes or >120s elapsed.
Emits portrait records for each character key encountered.

Usage:
  .venv/bin/python tools/scene_tracker.py
"""
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
CUES = BASE / "audio" / "minus08" / "cues.jsonl"
OUT_DIR = BASE / "images" / "minus08"
OUT_DIR.mkdir(parents=True, exist_ok=True)
(OUT_DIR / "bg").mkdir(exist_ok=True)
(OUT_DIR / "portraits").mkdir(exist_ok=True)

# ── Base aesthetic prefix ────────────────────────────────────────────────────
BASE_AESTHETIC = (
    "Oil painting aesthetic. Warm tungsten lamplight in interior scenes, "
    "cool blue-grey starlight in exterior night scenes. "
    "Ochre, burnt sienna, deep shadow, occasional electric blue for darkvision. "
    "1970s fantasy illustration rendered with precision. Painterly. "
    "Not photorealistic. No lens flare. No vignette. No text. No title. "
    "No UI elements. Full bleed composition."
)

# ── Settings ─────────────────────────────────────────────────────────────────
SETTINGS: dict[str, dict] = {
    "TABLE_ROOM": {
        "label": "The Table Room (Phase 2 hallway off-room)",
        "description": (
            "Round wooden table, seven mismatched chairs, one empty. "
            "Single rectangular window (four corners, night outside). "
            "Laptop on a sideboard, terminal glowing, fan visible. "
            "Cardboard GM screen folded in three panels, painted dragon on the facing side. "
            "Stack of index cards squared at the edge of the table. "
            "Old Adventure Path open to a coastal map. "
            "Warm lamplight from overhead. Pencils, dice, character sheets spread on felt. "
            "Evening. Interior. Intimate."
        ),
        "palette": "warm amber, deep shadow, lamplight pools, green felt",
    },
    "MOUNTAIN_APPROACH": {
        "label": "The Mountain Approach (night exterior)",
        "description": (
            "Night. Coastal fishing village far below, scattered lamplight. "
            "Dark mountain rising ahead, wet stone, switchback road visible on the lower face. "
            "Two guards at a fire on the switchback, small and distant. "
            "Stars. No moon shown. The party's silhouettes against the rock. "
            "The air is damp. The fire is the only warm colour in the frame."
        ),
        "palette": "blue-black night, amber fire, grey stone",
    },
    "CLIFF_FACE": {
        "label": "The Cliff Face (night, wet limestone)",
        "description": (
            "Night. Wet limestone cliff face, forty feet of rock. "
            "A rope hanging from an anchor near the top. "
            "Pink-painted carabiner links visible on the rope — each one distinct, painted individually. "
            "A figure mid-climb on the rope. "
            "Far below at the bottom, a small iguana grips the rope, feet on the ground, "
            "head tilted upward toward the climber. "
            "Starlight. No torch. The rope is the only line between."
        ),
        "palette": "blue-grey rock, silver starlight, pink accent on the links",
    },
    "ANTECHAMBER": {
        "label": "Antechamber of Bone (underground)",
        "description": (
            "Underground cut-stone chamber. Bones scattered across the floor — not arranged, scattered. "
            "Low ceiling. Darkvision rendering: sharp edges, colours drained to blues and grey-whites. "
            "No torch. The light source is the characters' darkvision — ambient, sourceless, cold. "
            "Doorway ahead, darkness beyond it."
        ),
        "palette": "darkvision blue-grey, white bone highlights, black shadow",
    },
    "GIFT_ROOM": {
        "label": "The Gift Room (underground altar chamber)",
        "description": (
            "Underground chamber. Stone altar at center. "
            "A single candle in a glass receptacle on the altar — the only warm light. "
            "Above and behind the altar, barely visible in the upper dark, a gargoyle "
            "on a ledge — stone grey, still, facing downward. "
            "The candle flame is perfectly still. "
            "Offerings on the altar, ancient. Dust. The smell of preserved things."
        ),
        "palette": "candlelight amber, stone grey, deep shadow above, single flame",
    },
    "CIRCLE_ROOM": {
        "label": "Circle Room with the Oak (underground sinkhole chamber)",
        "description": (
            "Large underground chamber. An oak tree grows through the floor, "
            "roots spread wide across stone. "
            "High above, a natural sinkhole opens to the sky — afternoon light "
            "descending in a column, forming a bright ring on the stone around the oak's trunk. "
            "The ring is orange at the edge, white in the center. "
            "The room is in shadow except for the ring. The oak is enormous and old."
        ),
        "palette": "afternoon gold, ring of orange-white light, deep chamber shadow, oak bark",
    },
    "SINKHOLE_COMBAT": {
        "label": "Sinkhole Combat (the elimination, afternoon light)",
        "description": (
            "The circle room during combat. Afternoon light ring on the stone around the oak. "
            "A flesh golem of stitched bodies stands to one side — large, slow, mismatched. "
            "A mountain goat with a red collar is in flanking position — precise, still, "
            "head already turned toward the next target. "
            "Cultists on the stone floor, some down, some moving. "
            "The room is in motion but the light does not move. "
            "The oak does not move either."
        ),
        "palette": "afternoon gold ring, flesh-grey golem, red collar, stone grey",
    },
    "AFTERMATH_EXIT": {
        "label": "Aftermath and Exit (sinkhole rim, late afternoon)",
        "description": (
            "Late afternoon. Broken basalt at the rim of the sinkhole. "
            "A goat with a red collar ascends a narrow path up the basalt, "
            "not looking back. "
            "Seven figures following in single file, one at a time, "
            "up into leaves and the last of the afternoon light. "
            "The sinkhole below them is now in shadow. "
            "The sky above is gold and losing it."
        ),
        "palette": "late afternoon gold, basalt grey, leaf-shadow green, fading sky",
    },
}

# ── Character dossiers ────────────────────────────────────────────────────────
CHARACTERS: dict[str, dict] = {
    "gm_feynman": {
        "label": "Feynman (GM)",
        "description": (
            "Lean man in his forties. Cardboard GM screen folded in three panels propped before him, "
            "painted dragon visible on the outside facing. "
            "Pencil behind one ear, second pencil in hand. "
            "Index cards stacked and squared at the edge. "
            "Reading glasses pushed up on his forehead. "
            "Dark circles. Completely alert. "
            "He is behind the screen, not in front of it. The screen is the wall he chose."
        ),
    },
    "draavio": {
        "label": "Draavio (half-orc Ranger / Alchemist)",
        "description": (
            "Half-orc. Green-grey skin, broad jaw, calm eyes — not aggressive, watchful. "
            "Mithral chain shirt, light and close-fitting. "
            "Large falchion on his back, handle visible over one shoulder. "
            "Bandolier across the chest with small vials in clips. "
            "Pink-painted carabiner links hanging from the bandolier — each individually painted. "
            "Scroll case at his hip. "
            "He does not look like a player's idea of a ranger. He looks like the ranger."
        ),
    },
    "pyrrhon": {
        "label": "Pyrrhon the Thrice-Kindled (human Wizard)",
        "description": (
            "Human man, trim, precise in his movements. "
            "Three highlighters in his breast pocket — orange, yellow, blue — arranged by colour. "
            "Gold ring on his right hand, the bonded object. "
            "Spellbook under one arm, colour-coded tabs visible at the edges by school. "
            "Light crossbow slung across his back. "
            "Expression: calculating. Not warm. Not cold. Calibrating."
        ),
    },
    "njala": {
        "label": "Njála (human Witch / Rogue)",
        "description": (
            "Human woman. Studded leather armour, close-fitting. "
            "Two short swords at her hips, not masterwork — the blades are honest. "
            "A coin moving between the fingers of one hand — index, middle, ring, middle, index — "
            "without looking at it. "
            "Sheet of paper folded in her jacket, written in pencil. "
            "She is not looking at you. She is listening."
        ),
    },
    "merit": {
        "label": "Merit of the Ford (gnome Paladin)",
        "description": (
            "Gnome paladin, small — roughly three and a half feet. "
            "Full plate armour, well-maintained, no heraldry. "
            "Longsword at the hip, in scabbard. "
            "Ring of climbing on the left hand. "
            "No archetype insignia. Just the code and the sword. "
            "Expression: present. Not righteous. Present. "
            "The sword is down."
        ),
    },
    "raymora_human": {
        "label": "Raymora the Dragon / Joey (human Druid, human form)",
        "description": (
            "Human man, broad-shouldered, unhurried. "
            "Hide armour, worn and comfortable. "
            "Scimitar at the hip. "
            "Something on his face that is both kind and professional — a doctor's bearing. "
            "His character sheet visible on the table if in a table scene: DOCTOR written "
            "in the margin in block capitals, a stethoscope drawn beneath it."
        ),
    },
    "raymora_iguana": {
        "label": "Raymora (iguana wild-shape form)",
        "description": (
            "Green iguana, Tiny-size category — roughly the length of a large forearm. "
            "Sharp claws, clearly and specifically depicted — they are doing something useful: "
            "gripping rope, gripping stone, holding a vial. "
            "One eye holds steady on a point. The other is tracking. "
            "The claws are the whole story."
        ),
    },
    "azazel": {
        "label": "Azazel the Archivist (Vincent's character)",
        "description": (
            "A figure with wings of fire — the wings burn but do not burn what they touch. "
            "The face is a clerk's face: it has seen everything in the record and formed "
            "no opinion about any of it that it intends to share. "
            "Lawful neutral bearing. Not a villain's face. "
            "He is carrying nothing that is not the record. "
            "The goat with the red collar is just behind him."
        ),
    },
}

# ── Speaker → character key mapping ──────────────────────────────────────────
SPEAKER_CHAR: dict[str, str] = {
    "Feynman": "gm_feynman",
    "Draavio": "draavio",
    "Magi": "draavio",
    "Sheldon": "pyrrhon",
    "Lisbeth": "njala",
    "LisbethEn": "njala",
    "Witch": "merit",
    "Merit": "merit",
    "Joey": "raymora_human",
    "Raymora": "raymora_iguana",   # when Joey is speaking as the iguana form
    "Doctor Drake": "raymora_human",
    "Vincent": "azazel",
}

# Table-room forms: show the player at the table rather than the character in-game.
# gm_feynman IS already the table form (Feynman behind the GM screen).
SPEAKER_CHAR_TABLE: dict[str, str] = {
    "Feynman": "gm_feynman",
    "Draavio": "draavio_table",
    "Magi": "draavio_table",
    "Sheldon": "pyrrhon_table",
    "Lisbeth": "njala_table",
    "LisbethEn": "njala_table",
    "Witch": "merit_table",
    "Merit": "merit_table",
    "Joey": "raymora_table",
    "Raymora": "raymora_table",    # still human at the table
    "Doctor Drake": "raymora_table",
    "Vincent": "azazel_table",
}

TABLE_SETTINGS: frozenset[str] = frozenset({"TABLE_ROOM"})

# ── Setting keyword triggers ──────────────────────────────────────────────────
# Each entry: (speakers_allowed, regex, setting_key)
# speakers_allowed: set of speaker names that can trigger, or None = any speaker.
# Patterns match actual *arrival* language, not descriptions of upcoming rooms.
SETTING_TRIGGERS: list[tuple[set[str] | None, re.Pattern, str]] = [
    # The room description at session open
    ({"The Narrator"}, re.compile(r"room is off the PHASE 2 hallway", re.I), "TABLE_ROOM"),
    # GM's line when party leaves for the mountain
    ({"Feynman"}, re.compile(r"fishing town is behind you|mountain is in front of you", re.I), "MOUNTAIN_APPROACH"),
    # GM describing the cliff access
    ({"Feynman"}, re.compile(r"forty feet up a wet face|access is forty feet up", re.I), "CLIFF_FACE"),
    # Arrival underground: GM says "You're in. Cut passage"
    ({"Feynman", "The Narrator"}, re.compile(r"You're in\.|Cut passage|going down and in", re.I), "ANTECHAMBER"),
    # Gift room: GM or Narrator describing the room the party is NOW in.
    # "stone altar" or gargoyle "above the altar" (not the Merit sheet comment about
    # "miss a gargoyle on a ledge") or "candle in a glass receptacle".
    ({"Feynman", "The Narrator"}, re.compile(r"stone altar|candle in.{0,30}glass|gargoyle.{0,30}above.{0,30}altar|vampire gargoyle|gargoyle comes off", re.I), "GIFT_ROOM"),
    # Circle room with oak: party actually arrives (Narrator describes it standing there)
    ({"The Narrator"}, re.compile(r"oak tree.{0,30}(grows|roots)|light.{0,30}(descends|forming a ring)|the ring of light|ring on the stone", re.I), "CIRCLE_ROOM"),
    # Draavio returns through the sinkhole — combat begins
    (None, re.compile(r"goat found a path|goat descends first|At the lip of the sinkhole", re.I), "SINKHOLE_COMBAT"),
    # Aftermath: the party leaves
    ({"The Narrator"}, re.compile(r"goat with the red collar turns on the basalt|seven go after it", re.I), "AFTERMATH_EXIT"),
]

# Iguana trigger: when Joey transitions to iguana
IGUANA_TRIGGER = re.compile(r"Raymora turns into an iguana|wild shape.*iguana|iguana.*wild shape", re.I)
IGUANA_BACK = re.compile(r"ceases being|iguana crawls the body|no longer iguana", re.I)

MAX_SCENE_SECONDS = 120  # force new scene after this many seconds


def prompt_hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]


def build_bg_prompt(setting_key: str, chars: list[str]) -> str:
    s = SETTINGS[setting_key]
    char_fragments = []
    for c in chars:
        if c in CHARACTERS:
            short = CHARACTERS[c]["description"].split(".")[0]
            char_fragments.append(short)
    chars_str = (" In the scene: " + "; ".join(char_fragments) + ".") if char_fragments else ""
    return f"{BASE_AESTHETIC} SCENE: {s['description']}{chars_str}"


def build_portrait_prompt(char_key: str) -> str:
    c = CHARACTERS[char_key]
    return (
        f"{BASE_AESTHETIC} "
        f"CHARACTER PORTRAIT: {c['description']} "
        f"Square composition. Character fills most of the frame. "
        f"Plain dark background. Shoulders and face visible. "
        f"No text."
    )


def main() -> None:
    cues = []
    for line in CUES.read_text().splitlines():
        if line.strip():
            cues.append(json.loads(line))

    scenes: list[dict] = []
    portraits_seen: set[str] = set()
    portraits: list[dict] = []

    setting = "TABLE_ROOM"
    chars_present: list[str] = []
    scene_start_ms = 0.0
    last_scene_break_ms = 0.0
    joey_is_iguana = False

    scene_id = 0

    def emit_scene(end_ms: float) -> None:
        nonlocal scene_id
        prompt = build_bg_prompt(setting, chars_present)
        h = prompt_hash(prompt)
        scenes.append({
            "id": scene_id,
            "setting": setting,
            "start_ms": scene_start_ms,
            "end_ms": end_ms,
            "chars_present": list(chars_present),
            "prompt": prompt,
            "hash": h,
            "bg_path": f"images/minus08/bg/{h}.png",
        })
        scene_id += 1

    for cue in cues:
        pos_ms = cue["start"] * 1000
        speaker = cue["speaker"]
        text = cue["text"]
        end_ms = cue["end"] * 1000

        # Detect setting change
        for allowed_speakers, pattern, key in SETTING_TRIGGERS:
            if allowed_speakers is not None and speaker not in allowed_speakers:
                continue
            if pattern.search(text):
                if key != setting:
                    emit_scene(pos_ms)
                    scene_start_ms = pos_ms
                    last_scene_break_ms = pos_ms
                    setting = key
                break

        # Iguana tracking (any speaker)
        if IGUANA_TRIGGER.search(text):
            joey_is_iguana = True
        if IGUANA_BACK.search(text):
            joey_is_iguana = False

        # Force scene break at max duration
        if (pos_ms - last_scene_break_ms) > MAX_SCENE_SECONDS * 1000:
            emit_scene(pos_ms)
            scene_start_ms = pos_ms
            last_scene_break_ms = pos_ms

        # Track characters present
        char_key = SPEAKER_CHAR.get(speaker)
        if char_key == "raymora_human" and joey_is_iguana:
            char_key = "raymora_iguana"
        if char_key == "raymora_iguana" and not joey_is_iguana:
            char_key = "raymora_human"

        if char_key and char_key not in chars_present:
            chars_present.append(char_key)

        # Portrait records
        if char_key and char_key not in portraits_seen:
            portraits_seen.add(char_key)
            prompt = build_portrait_prompt(char_key)
            h = prompt_hash(prompt)
            portraits.append({
                "key": char_key,
                "label": CHARACTERS[char_key]["label"],
                "prompt": prompt,
                "hash": h,
                "path": f"images/minus08/portraits/{h}.png",
            })

    # Final scene
    if cues:
        emit_scene(cues[-1]["end"] * 1000)

    # Write outputs
    scenes_path = OUT_DIR / "scenes.jsonl"
    scenes_path.write_text(
        "".join(json.dumps(s, ensure_ascii=False) + "\n" for s in scenes)
    )
    portraits_path = OUT_DIR / "portraits.jsonl"
    portraits_path.write_text(
        "".join(json.dumps(p, ensure_ascii=False) + "\n" for p in portraits)
    )

    print(f"scenes: {len(scenes)} → {scenes_path}")
    print(f"portraits: {len(portraits)} → {portraits_path}")
    for s in scenes:
        dur = (s["end_ms"] - s["start_ms"]) / 1000
        print(f"  [{s['id']:03d}] {s['setting']:<20} {s['start_ms']/1000:7.0f}s–{s['end_ms']/1000:.0f}s  ({dur:.0f}s)  chars={s['chars_present']}")


if __name__ == "__main__":
    main()
