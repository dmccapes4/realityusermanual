#!/usr/bin/env python3
"""Compile Pathfinder-plate prompts for page −08.

Three layers, in this order, every time:
  1. aesthetic  — the house look, identical for every plate
  2. scene      — what this chapter is a picture of
  3. character  — only the people present, from a fixed lexicon

The seed is the first eight hex digits of sha256("paizo-plate-v2|" + shot id).
Same shot, same layers, same seed, same prompt. A scene is many shots.
Closeups are allowed. The image model is called with that prompt and nothing added.

Usage:
  python3 src/form/render_plates.py            # write chapters + manifest
  python3 src/form/render_plates.py --chapter 03
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
VERSION = "paizo-plate-v3"

AESTHETIC = (
    "A painted interior plate from a Pathfinder roleplaying-game book. "
    "Oil and gouache. Saturated color under control. Figures read in silhouette "
    "before they read in detail. Armor and weapons are clear at a distance. "
    "Warm key light, cool shadow. The background is simpler than the figures. "
    "Three-quarter staging when the shot is wide. Closeups are allowed and are "
    "the same paint. No caption, no letters, no numerals, no watermark, "
    "no logo, no photograph, no anime, no chibi. 16:9 plate."
)

CHARACTERS = {
    "feynman": (
        "The gamemaster sits behind a cardboard screen folded in three, a painted "
        "dragon on the face the table sees. A pencil behind one ear, another in "
        "his hand. He is a man at work, not a portrait of a known person."
    ),
    "draavio": (
        "Draavio, a half-orc ranger: modest tusks, measured face, no boast in the "
        "posture. Mithral chain shirt, heavy wooden shield, a keen falchion. "
        "Pink-painted metal links on a climbing sling. The same face and kit on every plate."
    ),
    "pyrrhon": (
        "Pyrrhon, a human evoker: lean, precise, no plate. A cloak, bracers, one "
        "ring. His attention is on the thing he is about to name. The same face on every plate."
    ),
    "njala": (
        "Njála, a human witch-rogue: cropped dark hair, studded leather, two short "
        "swords, a coin. Watchful, still. Not a likeness of any actress. The same face on every plate."
    ),
    "merit": (
        "Merit of the Ford, a gnome paladin. Small. The same face on every plate: "
        "a gnome woman, calm, no extra ornament. A ring of climbing on one hand. "
        "Full plate, heavy steel shield, and longsword, unless the scene says the "
        "armor is in the bag and she is in her underwear, which is how she prefers to climb."
    ),
    "iguana": (
        "Raymora in iguana form: a green iguana, sharp claws, slow, deliberate, "
        "doctor's stillness. One eye can look elsewhere than the other. The same animal on every plate."
    ),
    "goat": (
        "A small goat with a red collar. It does not pose. It is already where it meant to stand."
    ),
    "golem": (
        "A flesh golem stitched from several human bodies. The hair and the marks "
        "read as scholars, not as monsters. Large, slow, linen and thread visible. The same body on every plate."
    ),
    "peacock": (
        "A small winged woman with a fanned tail like a peacock, outlined in gold "
        "dust, blinded, hands that can rise. The same figure on every plate."
    ),
    "archivist": (
        "The Archivist steps from a ring of low sun. Wings of fire that do not burn "
        "the oak. A keeper of a record, not a snarling fiend. The same figure on every plate."
    ),
    "soldiers": (
        "Seven soldiers outlined in gold dust, blinded, moving by scent, ordinary "
        "kit, no heroic pose."
    ),
}


def S(sid, slug, cast, scene):
    return {"id": sid, "slug": slug, "cast": cast, "scene": scene}


# A scene is named by presence. Presence is the frequency of shots.
# The first shot of each scene is the wide. The rest are mids and closeups.
SCENES = [
    {
        "id": "01",
        "slug": "the_table",
        "title": "The Table",
        "shots": [
            S("01a", "wide", ["feynman", "draavio", "pyrrhon", "njala", "merit"],
              "Wide. A round table, seven chairs, one rectangular window, night outside. Five people. A laptop compiling on a sideboard, its screen unreadable."),
            S("01b", "coin", ["njala"],
              "Closeup. A coin moves across a woman's fingers, index to middle to ring, and she does not look at it."),
            S("01c", "screen", ["feynman"],
              "Closeup. The outside of a cardboard screen: a painted dragon, the fold of the board, a pencil behind an ear."),
            S("01d", "cards", ["feynman"],
              "Closeup. Index cards being squared against the heel of a hand. The edges are the subject."),
            S("01e", "links", ["draavio"],
              "Closeup. Pink-painted metal climbing links on a wooden table beside a half-orc's hand. No text on the paper near them."),
            S("01f", "laptop", ["feynman"],
              "Closeup. A laptop on a sideboard, fan implied by the heat-haze of the paint, the screen a blank glow with no readable marks."),
        ],
    },
    {
        "id": "02",
        "slug": "the_climb",
        "title": "The Climb",
        "shots": [
            S("02a", "wide", ["draavio", "iguana", "pyrrhon", "njala", "merit"],
              "Wide. Night. A wet rock face under a lip of stone, a door cut into it. A rope runs from the man on the wall to the bottom. A small gnome woman climbs the face in her underwear, a ring on one hand. Her plate, shield, and sword are in a bag at the bottom. That is how she prefers to climb."),
            S("02b", "iguana_rope", ["iguana"],
              "Closeup. Iguana at the very bottom. Feet on the ground. Claws on the rope. Head thrown up the line."),
            S("02c", "missed_link", ["draavio"],
              "Closeup. A pink metal link has missed its gate and swings on the rope against wet stone."),
            S("02d", "thumb", ["draavio"],
              "Closeup. A half-orc thumb reaching for a gate on the wet wall. The hand is the subject."),
            S("02e", "coin_teeth", ["njala"],
              "Medium. A woman in studded leather climbs with no rope and a coin between her teeth."),
            S("02f", "the_face", ["merit"],
              "Medium. A small gnome woman in her underwear climbs the wet face toward a door under a lip of stone. A ring is on one hand. The plate, the shield, and the sword are in a bag at the bottom. She prefers it this way."),
            S("02g", "wizard_walks", ["pyrrhon"],
              "Medium. A wizard walks up the vertical stone as if it were a floor, cloak hanging toward the cliff."),
        ],
    },
    {
        "id": "03",
        "slug": "the_tongue",
        "title": "The Tongue",
        "shots": [
            S("03a", "wide", ["iguana", "draavio", "pyrrhon", "njala", "merit"],
              "Wide. The top of a cliff at night. A shut door into the mountain. The iguana has come over the lip last. Four people wait."),
            S("03b", "eyes", ["iguana"],
              "Closeup. An iguana's head. One eye on the people. The other eye elsewhere. Both eyes sharp."),
            S("03c", "claws_card", ["iguana"],
              "Closeup. Iguana claws tapping a blank card. No writing is visible. The claws are the subject."),
            S("03d", "coin_still", ["njala"],
              "Closeup. The coin has stopped. It sits on a knuckle. The woman watches the lizard, not the coin."),
            S("03e", "waiting", ["draavio", "pyrrhon", "merit"],
              "Medium. Three people at the shut door, not hurrying, night behind them."),
        ],
    },
    {
        "id": "04",
        "slug": "the_oak",
        "title": "The Oak",
        "shots": [
            S("04a", "wide", ["goat", "draavio", "merit"],
              "Wide. A broken stone floor open to the sky. A living oak rises through the hole. Late orange light in the leaves. A pen of goats at the far wall."),
            S("04b", "collar", ["goat"],
              "Closeup. A red collar on a small goat. The wool and the collar. Nothing else."),
            S("04c", "pen", ["goat"],
              "Medium. Seven calm goats in a pen. One wears the red collar. Straw. They are not afraid."),
            S("04d", "roots", ["draavio"],
              "Closeup. Oak roots under broken floor stones. A half-orc's boot at the edge, not the subject. The roots are."),
            S("04e", "leaves", [],
              "Closeup. Late light in oak leaves, orange at the edge of each leaf, the sky beyond."),
        ],
    },
    {
        "id": "05",
        "slug": "the_descent",
        "title": "The Descent",
        "shots": [
            S("05a", "wide", ["peacock", "golem", "soldiers"],
              "Wide. A stair from the woods down into orange oak-light. Seven blinded soldiers. A small winged woman in front. A stitched golem behind, carrying, not looking."),
            S("05b", "tail", ["peacock"],
              "Medium. The winged woman, tail fanned, gold dust in the air around her, blinded."),
            S("05c", "golem_walks", ["golem"],
              "Medium. The golem walks and does not look at anything. Stitches. Scholar's hair. Burden in its arms."),
            S("05d", "gold_dust", ["soldiers"],
              "Closeup. Gold dust on a face that cannot see. The eyes are open and useless. Ordinary soldier's kit at the edge of the frame."),
            S("05e", "stitch_hair", ["golem"],
              "Closeup. Linen thread through skin. Hair dressed like a scholar's. A mark like a crucifix scar. Not gory for its own sake. The stitch is the subject."),
        ],
    },
    {
        "id": "06",
        "slug": "the_flank",
        "title": "The Flank",
        "shots": [
            S("06a", "goat_placed", ["goat"],
              "Medium. The goat is already standing where a flank is. It does not look at the people coming."),
            S("06b", "scent", ["soldiers", "goat"],
              "Closeup. A blinded soldier's face turning toward a smell. The red collar is in the background, soft."),
            S("06c", "one_swing", ["draavio", "soldiers"],
              "Medium. One swing of a falchion. One soldier going down. The swing is the whole of it. No second blow in the frame."),
            S("06d", "edge", ["draavio"],
              "Closeup. The edge of a keen falchion, mithral sleeve at the wrist, pink link in the other hand."),
            S("06e", "after", ["goat", "draavio"],
              "Wide. Bodies down. The goat has not moved. The half-orc is already walking to the next. No one is speaking in this picture."),
            S("06f", "walk", ["draavio", "goat"],
              "Medium. He does not run. He walks. The goat's head has already turned."),
        ],
    },
    {
        "id": "07",
        "slug": "the_unsewing",
        "title": "The Unsewing",
        "shots": [
            S("07a", "sitting", ["golem"],
              "Medium. The golem is sitting on the stone because it likes sitting. It is not in a chair. Large, slow, quiet."),
            S("07b", "claw_stitch", ["iguana", "golem"],
              "Closeup. An iguana claw in one stitch, cutting. The speed looks careful. Thread, not a wound displayed."),
            S("07c", "dust", ["merit"],
              "Closeup. White dust and tan dirt in a paladin's gauntlet. A mostly empty book of blank pages beside the hand. No writing."),
            S("07d", "coffins", ["merit", "draavio"],
              "Medium. Six plain coffins. Bodies in wet wraps being laid down carefully. No jewels. The paladin's sword is down."),
            S("07e", "sword_down", ["merit"],
              "Closeup. A longsword point on the stone, the hand not gripping for a fight. Full plate at the edge of the frame."),
            S("07f", "last_stitch", ["iguana", "golem"],
              "Closeup. The last stitch parting. The iguana's claw. The thread going slack."),
        ],
    },
    {
        "id": "08",
        "slug": "the_record",
        "title": "The Record",
        "shots": [
            S("08a", "wide", ["archivist", "goat"],
              "Wide. A ring of low sun on stone around an oak, orange at the edge, white in the middle. A figure steps out. Wings of fire. The leaves are not burning."),
            S("08b", "binding", ["draavio"],
              "Closeup. A dark leather book binding held up. No letters, no title, no ornament that can be read. The hands are a half-orc's."),
            S("08c", "lip", ["goat"],
              "Medium. The goat with the red collar at the lip of the sinkhole, owning the view, not looking back."),
            S("08d", "leaf", ["archivist"],
              "Closeup. A tongue of fire beside a green oak leaf. The leaf is intact. The fire is a wing."),
            S("08e", "facing", ["archivist", "draavio", "goat"],
              "Medium. Draavio holds the book so the binding faces the Archivist. The goat is behind them at the lip. The oak is not on fire."),
        ],
    },
]


# Per-scene primitives. The house bans stay. The light is the scene's.
AESTHETICS = {
    "01": {
        "paint": "oil and gouache, interior plate",
        "key": "warm lamp on a round table",
        "shadow": "cool night from one rectangular window",
        "saturation": "held, paper and wood",
        "frame": "16:9",
    },
    "02": {
        "paint": "oil and gouache, interior plate",
        "key": "cold moonlight on wet stone",
        "shadow": "blue-black under the lip",
        "saturation": "low, the pink links the only hot note",
        "frame": "16:9",
    },
    "03": {
        "paint": "oil and gouache, interior plate",
        "key": "the same moonlight, tighter",
        "shadow": "the shut door a darker vertical",
        "saturation": "low, skin and scale against stone",
        "frame": "16:9",
    },
    "04": {
        "paint": "oil and gouache, interior plate",
        "key": "late orange light in oak leaves",
        "shadow": "cool stone of the broken floor",
        "saturation": "green and orange, controlled",
        "frame": "16:9",
    },
    "05": {
        "paint": "oil and gouache, interior plate",
        "key": "orange oak light from below, gold dust in it",
        "shadow": "the woods above the stair, dark",
        "saturation": "gold against orange, held",
        "frame": "16:9",
    },
    "06": {
        "paint": "oil and gouache, interior plate",
        "key": "hard light on one swing",
        "shadow": "the oak room falling off behind the blade",
        "saturation": "controlled, the red collar readable",
        "frame": "16:9",
    },
    "07": {
        "paint": "oil and gouache, interior plate",
        "key": "low and even",
        "shadow": "linen, white dust, tan dirt",
        "saturation": "quiet, almost no chroma",
        "frame": "16:9",
    },
    "08": {
        "paint": "oil and gouache, interior plate",
        "key": "a ring of low sun, orange at the edge, white in the middle",
        "shadow": "stone outside the ring",
        "saturation": "fire against a green leaf that is not burning",
        "frame": "16:9",
    },
}

BANS = (
    "Silhouette before detail. No caption, no letters, no numerals, no watermark, "
    "no logo, no photograph, no anime, no chibi."
)


def aesthetic_line(scene_id: str) -> str:
    a = AESTHETICS[scene_id]
    return (
        f"Paint: {a['paint']}. Key: {a['key']}. Shadow: {a['shadow']}. "
        f"Saturation: {a['saturation']}. {BANS} Frame {a['frame']}."
    )


def plate_seed(shot_id: str) -> int:
    digest = hashlib.sha256(f"{VERSION}|{shot_id}".encode()).hexdigest()
    return int(digest[:8], 16)


def iter_shots(scenes: list[dict]):
    for scene in scenes:
        for shot in scene["shots"]:
            yield scene, shot


def compile_prompt(scene: dict, shot: dict) -> str:
    cast = " ".join(CHARACTERS[name] for name in shot["cast"])
    if not cast:
        cast = "No figure. The place is the subject."
    return (
        f"AESTHETIC: {aesthetic_line(scene['id'])}\n"
        f"SCENE: {shot['scene']}\n"
        f"CHARACTERS: {cast}\n"
        f"SEED: {plate_seed(shot['id'])}"
    )


def chapters_markdown() -> str:
    lines = [
        "# Plates for −08",
        "",
        "A scene is a run of shots. The wide names the place. The closeups are the frequency "
        "that makes the place present. Every prompt is three layers in a fixed order: "
        "aesthetic, scene, character. Character sentences come from one lexicon.",
        "",
        f"Version: `{VERSION}`",
        "",
    ]
    for scene in SCENES:
        lines.append(f"## {scene['id']} — {scene['title']}")
        lines.append("")
        for shot in scene["shots"]:
            cast = ", ".join(shot["cast"]) or "none"
            lines.append(f"### {shot['id']} {shot['slug']}")
            lines.append("")
            lines.append(f"Seed `{plate_seed(shot['id'])}`. Cast: {cast}.")
            lines.append("")
            lines.append(shot["scene"])
            lines.append("")
    return "\n".join(lines)


def manifest(scenes: list[dict]) -> dict:
    plates = []
    for scene, shot in iter_shots(scenes):
        plates.append({
            "scene_id": scene["id"],
            "scene": scene["title"],
            "id": shot["id"],
            "slug": shot["slug"],
            "seed": plate_seed(shot["id"]),
            "cast": shot["cast"],
            "filename": f"plate_{shot['id']}_{scene['slug']}_{shot['slug']}.png",
            "aspect_ratio": "16:9",
            "aesthetic": AESTHETICS[scene["id"]],
            "prompt": compile_prompt(scene, shot),
        })
    return {
        "version": VERSION,
        "characters": CHARACTERS,
        "aesthetics": AESTHETICS,
        "shot_count": len(plates),
        "plates": plates,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--chapter", help="scene id, e.g. 03; default all")
    args = parser.parse_args()
    scenes = SCENES
    if args.chapter:
        scenes = [s for s in SCENES if s["id"] == args.chapter]
        if not scenes:
            raise SystemExit(f"no scene {args.chapter}")
    (ROOT / "CHAPTERS.md").write_text(chapters_markdown(), encoding="utf-8")
    # One JSON object per scene. The aesthetic is a primitive, not a shared sentence.
    scene_lines = []
    for scene in SCENES:
        scene_lines.append(json.dumps({
            "id": scene["id"],
            "slug": scene["slug"],
            "title": scene["title"],
            "aesthetic": AESTHETICS[scene["id"]],
            "shots": scene["shots"],
        }, ensure_ascii=False))
    (ROOT / "scenes.jsonl").write_text("\n".join(scene_lines) + "\n", encoding="utf-8")
    payload = manifest(SCENES if not args.chapter else scenes)
    (ROOT / "manifest.json").write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(f"{payload['shot_count']} shots")
    for plate in payload["plates"]:
        print(f"{plate['id']}\t{plate['seed']}\t{plate['filename']}")


if __name__ == "__main__":
    main()


