#!/usr/bin/env python3
"""
tools/extend_minus08_audio.py
Generate TTS for new narration lines, splice into cues.jsonl and
concat_segs.txt, then rebuild audio/minus08/minus08.mp3.

Run from REALITY_USER_MANUAL/:
    python tools/extend_minus08_audio.py [--dry-run]

--dry-run  : print what would be generated; make no API calls or file changes.
"""
import argparse
import hashlib
import json
import os
import subprocess
import sys
import time
from pathlib import Path

# ── Paths ──────────────────────────────────────────────────────────────────────
BASE      = Path(__file__).parent.parent
AUDIO_DIR = BASE / "audio" / "minus08"
SEG_DIR   = AUDIO_DIR / "segments"
CUES_F    = AUDIO_DIR / "cues.jsonl"
CONCAT_F  = AUDIO_DIR / "concat_segs.txt"
MP3_OUT   = AUDIO_DIR / "minus08.mp3"

# Load .env
def _load_env() -> None:
    env_f = BASE / ".env"
    if env_f.exists():
        for line in env_f.read_text().splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, _, v = line.partition("=")
                os.environ.setdefault(k.strip(), v.strip())

_load_env()

ELEVEN_KEY  = os.environ.get("ELEVENLABS_API_KEY", "")
MODEL_ID    = "eleven_multilingual_v2"

VOICE_MAP = {
    "Narrator":  os.environ.get("VOICE_NARRATOR",  "Nxtvajpo1h6Ok0K5zP4M"),
    "Draavio":   os.environ.get("VOICE_MERLIN",     "Q9qXuNjHnmnYuh4qnepn"),
    "Feynman":   os.environ.get("VOICE_FEYNMAN",    "UosQzbgZZ3DYSVQ9ut6K"),
    "Sheldon":   os.environ.get("VOICE_SHELDON",    os.environ.get("VOICE_SHELDON_LIB", "OAXPclEPumYkMdEw2L4g")),
    "Lisbeth":   os.environ.get("VOICE_LISBETH",    "MhisHZND0w9JfMQVlH0A"),
    "LisbethEn": os.environ.get("VOICE_LISBETH",    "MhisHZND0w9JfMQVlH0A"),
    "Witch":     os.environ.get("VOICE_WITCH",      "hAPnKt1az4WnyeWHvYMF"),
    "Merit":     os.environ.get("VOICE_WITCH",      "hAPnKt1az4WnyeWHvYMF"),
    "Joey":      os.environ.get("VOICE_JOEY",       os.environ.get("VOICE_JOEY_LIB", "QDidinP5kDJnJ9cCCGp6")),
    "Vincent":   os.environ.get("VOICE_VINCENT",    "S0i6QfyFRAXPgXtLlrPQ"),
    "Goat":      os.environ.get("VOICE_GOAT",       "LeKRRWCgp0eQIsROehFm"),
    "Operator":  os.environ.get("VOICE_OPERATOR",   "ZU0FS6l2hYVQ80W3xDlT"),
    "Archivist": os.environ.get("VOICE_NARRATOR",   "Nxtvajpo1h6Ok0K5zP4M"),
    "Snake":     os.environ.get("VOICE_SNAKE",  "iUex9jQAAsMqYMxYUkK0"),   # RADA-trained ceremonial P-speech
    "Sauron":    os.environ.get("VOICE_SAURON", "M2HASKhyinBcyBrKOfms"),  # Sauron (Default)
}

SPEAKER_SHORT = {
    "Narrator":  "Narr",
    "Draavio":   "Drav",
    "Feynman":   "Feyn",
    "Sheldon":   "Shel",
    "Lisbeth":   "Lisb",
    "LisbethEn": "Lisb",
    "Witch":     "Witc",
    "Merit":     "Meri",
    "Joey":      "Joey",
    "Vincent":   "Vinc",
    "Goat":      "Goat",
    "Operator":  "Oper",
    "Archivist": "Arch",
    "Snake":     "Snak",
    "Sauron":    "Saur",
}

# ── New lines definition ────────────────────────────────────────────────────────
# Each entry:  (insert_after_cue_idx, act, frame_id, speaker, text)
# Lines are inserted IN ORDER after the specified cue index.
# Use consecutive insert_after values for multi-line blocks at the same point:
#   insert_after=34 means "insert after cue[34], in the order given here"
#
# BLOCK A: Draavio reads the player manual (insert after cue 34, Act 0, frame manual_page)
# BLOCK B: Axiomite stat block + conversation (insert after cue 382, Act 7, frame axiomite_screen)
# BLOCK C: Crisis pages / Gattaca dialogue (insert after cue 1107, Act 11, frame circle_room_trial)
# BLOCK D: Epilogue (append after cue 1121, Act 11, frame circle_room_trial)

NEW_LINES = [
    # ── BLOCK A: manual reading ──────────────────────────────────────────────
    (34, 0, "manual_page", "Draavio",
     "You can also"),
    (34, 0, "manual_page", "Draavio",
     "Organize a trip (fares, tickets, places to see, good addresses....)"),
    (34, 0, "manual_page", "Draavio",
     "Gather classified ads from different sites"),
    (34, 0, "manual_page", "Draavio",
     "Centralize your favorite recipes"),
    (34, 0, "manual_page", "Draavio",
     "Compile articles about your passions"),
    (34, 0, "manual_page", "Draavio",
     "Compare offers and prices"),
    (34, 0, "manual_page", "Draavio",
     "Gather everything that documents your thesis"),
    (34, 0, "manual_page", "Draavio",
     "etc."),
    (34, 0, "manual_page", "Draavio",
     "How does it work?"),

    # ── BLOCK B: axiomite stat block + conversation ──────────────────────────
    (382, 7, "axiomite_screen", "Sheldon",
     "CR 8. LN. Medium outsider. Extraplanar. Lawful."),
    (382, 7, "axiomite_screen", "Lisbeth",
     "Hvad er det?"),
    (382, 7, "axiomite_screen", "LisbethEn",
     "What is it?"),
    (382, 7, "axiomite_screen", "Sheldon",
     "It is a creature whose true form is mathematical dust. Golden. Crystalline. "
     "It condenses into symbols and equations and reforms into flesh. "
     "The physical appearance is a container. The content is law."),
    (382, 7, "axiomite_screen", "Lisbeth",
     "Det er smukke."),
    (382, 7, "axiomite_screen", "LisbethEn",
     "It is beautiful."),
    (382, 7, "axiomite_screen", "Sheldon",
     "According to their own history, the first axiomites sprang from the raw mathematical "
     "underpinnings of the cosmos long before the first gods began to stir. "
     "They are personifications of a primordial reality made flesh in an attempt to understand itself. "
     "The flesh is the attempt. The dust is the reality."),
    (382, 7, "axiomite_screen", "Lisbeth",
     "De husker det?"),
    (382, 7, "axiomite_screen", "LisbethEn",
     "They remember this?"),
    (382, 7, "axiomite_screen", "Sheldon",
     "They do not need to remember it. They are it. New axiomites are formed from souls "
     "drawn across the planes to one of the axiomites' humming crystal monoliths, "
     "emerging later as purified creatures of law and theory."),
    (382, 7, "axiomite_screen", "Narrator",
     "Lisbeth has set the coin down."),
    (382, 7, "axiomite_screen", "Sheldon",
     "In dust form it looks like a shifting mass of glowing mathematical symbols and equations. "
     "In that form it can fly and gains the incorporeal quality. "
     "Both shapes are the axiomite's true form. A true seeing spell reveals both forms simultaneously."),
    (382, 7, "axiomite_screen", "Lisbeth",
     "Hvad siger det?"),
    (382, 7, "axiomite_screen", "LisbethEn",
     "What does that say?"),
    (382, 7, "axiomite_screen", "Sheldon",
     "It says what you are at full resolution is not incompatible with what you appear to be. "
     "The true seeing does not replace one with the other. It holds both."),
    (382, 7, "axiomite_screen", "Witch",
     "That is a prism."),
    (382, 7, "axiomite_screen", "Sheldon",
     "Yes."),
    (382, 7, "axiomite_screen", "Witch",
     "A prism does not destroy the light. It reveals what the light already was. "
     "The axiomite does not become dust when the spell is cast. "
     "The dust was always there. The flesh was always there. "
     "The spell is the prism. The essence prism."),
    (382, 7, "axiomite_screen", "Narrator",
     "The Witch of the Rivers has not moved her mini. "
     "She is looking at the stat block from across the table."),
    (382, 7, "axiomite_screen", "Witch",
     "Who wrote this."),
    (382, 7, "axiomite_screen", "Sheldon",
     "Philosophers of law. They called it a game."),
    (382, 7, "axiomite_screen", "Lisbeth",
     "En spilfilosof."),
    (382, 7, "axiomite_screen", "LisbethEn",
     "A game philosopher."),
    (382, 7, "axiomite_screen", "Narrator",
     "Sheldon considers this. He does not correct it."),
    (382, 7, "axiomite_screen", "Vincent",
     "Of course, they say every atom in our bodies was once part of a star."),
    (382, 7, "axiomite_screen", "Narrator",
     "Nobody asked."),
    (382, 7, "axiomite_screen", "Vincent",
     "Maybe I'm not leaving. Maybe I'm going home."),
    (382, 7, "axiomite_screen", "Feynman",
     "That is from Gattaca."),
    (382, 7, "axiomite_screen", "Vincent",
     "It is also from the stat block."),
    (382, 7, "axiomite_screen", "Narrator",
     "Lisbeth picks the coin back up."),
    (382, 7, "axiomite_screen", "Sheldon",
     "The third division — one maintaining the inevitables, one expanding the city, "
     "one continuing the exploration and calculation of the laws and constants that underlie all of reality. "
     "Their leader is a gestalt mind. It forms when needed. "
     "It disperses into its component axiomites to put the god-mind's plans into action."),
    (382, 7, "axiomite_screen", "Lisbeth",
     "Hvem satte det i spillet?"),
    (382, 7, "axiomite_screen", "LisbethEn",
     "Who put that in the game?"),
    (382, 7, "axiomite_screen", "Narrator",
     "Sheldon sets the stat block down. He looks at the page."),
    (382, 7, "axiomite_screen", "Sheldon",
     "Wolfgang Baur. Jason Bulmahn. Adam Daigle. Graeme Davis. Crystal Frasier. "
     "Joshua J. Frost. Tim Hitchcock. Brandon Hodge. James Jacobs. Steve Kenson. "
     "Hal MacLean. Martin Mason. Rob McCreary. Erik Mona. Jason Nelson. Patrick Renie. "
     "Sean K Reynolds. F. Wesley Schneider. Owen K.C. Stephens. James L. Sutter. "
     "Russ Taylor. Greg A. Vaughan. "
     "Based on material by Jonathan Tweet. Monte Cook. Skip Williams."),
    (382, 7, "axiomite_screen", "Lisbeth",
     "De er tilgængelige?"),
    (382, 7, "axiomite_screen", "LisbethEn",
     "They are available?"),
    (382, 7, "axiomite_screen", "Sheldon",
     "On message boards. At conventions. At Pathfinder Society games. "
     "James Jacobs answered a question in 2015. "
     "The question was whether the sources of magic had ever been described. "
     "He said: they have not been described, by intent. "
     "Leaving it ambiguous is good for the game, "
     "because once we start setting down rules, we start limiting story options."),
    (382, 7, "axiomite_screen", "Witch",
     "He left the source undescribed so the table could make it."),
    (382, 7, "axiomite_screen", "Witch",
     "That is also jurisprudence."),
    (382, 7, "axiomite_screen", "Lisbeth",
     "Jurisprudence."),
    (382, 7, "axiomite_screen", "Sheldon",
     "Kept vague to allow it."),

    # ── BLOCK C: crisis pages / Gattaca dialogue ─────────────────────────────
    (1107, 11, "circle_room_trial", "Vincent",
     "The seven days once every 70 years is real. That is not the point of the film."),
    (1107, 11, "circle_room_trial", "Feynman",
     "What is the point."),
    (1107, 11, "circle_room_trial", "Vincent",
     "Whether the printed number decides the order. Or reports on something that was already there."),
    (1107, 11, "circle_room_trial", "Narrator",
     "Feynman holds the screen. He does not open it."),
    (1107, 11, "circle_room_trial", "Feynman",
     "In the crisis pages — the accounting crisis, the unnumbered page — the question was the same one. "
     "The operator declared the page unnumbered. But the page was already bound in sequence. "
     "It was still the nth page. Every calculation that followed was off by one on the label, not on the page. "
     "The crisis was about a missing label. Not a missing number. "
     "The order was already there before the label existed."),
    (1107, 11, "circle_room_trial", "Draavio",
     "Was that my bad?"),
    (1107, 11, "circle_room_trial", "Feynman",
     "Every bit of it."),
    (1107, 11, "circle_room_trial", "Draavio",
     "I apologize."),
    (1107, 11, "circle_room_trial", "Narrator",
     "He does not sound apologetic."),
    (1107, 11, "circle_room_trial", "Vincent",
     "The film says: heart disorder, 99% probability. Life expectancy 30.2 years. "
     "That is a label attached to an order. The label was real. The 30.2 years was not, "
     "because the label was reporting on a probability and the probability was not the order itself. "
     "He flew. His heart was 10,000 beats overdue by the count on the certificate. "
     "He had the number memorized. He recited it. He did not believe it was doing the counting."),
    (1107, 11, "circle_room_trial", "Sheldon",
     "The label is only the floor if you stand on it."),
    (1107, 11, "circle_room_trial", "Lisbeth",
     "Han overtog sin egen journefart."),
    (1107, 11, "circle_room_trial", "LisbethEn",
     "He took charge of his own departure."),
    (1107, 11, "circle_room_trial", "Vincent",
     "The window is open seven days once every 70 years. "
     "If you miss it you will not live to see the next one. That is also true. "
     "The geometry does not move. You decide which truth you build on."),
    (1107, 11, "circle_room_trial", "Narrator",
     "The Narrator notes that the goat with the red collar found its own window. "
     "Nobody gave it a number."),

    # ── BLOCK D: epilogue ────────────────────────────────────────────────────
    (1121, 11, "circle_room_trial", "Sauron",
     "EPILOGUE"),
    (1121, 11, "circle_room_trial", "Vincent",
     "I was kind of hoping to deliver this one."),
    (1121, 11, "circle_room_trial", "Operator",
     "My name is Vincent Anton, and I live in reality. "
     "My day job used to be focused mainly on harmonic frequency tuning "
     "which usually required an acclimation ladder. "
     "Also some aerodynamics, but that part of my work was limited to ignition. "
     "I have a lot of experience playing Pathfinder. "
     "Most recently I played a home-brewed character called the Archivist which was interesting. "
     "The operator who wrote the campaign had the name sound mysterious and villainous "
     "then the Archivist turned out to be Azazel who was accompanied by goats. "
     "I showed up to a session late and the GM had me play the Archivist "
     "who is more of a judge who keeps track of things without condemning anyone. "
     "His goat SCAPE is part of the larger campaign, "
     "and the goats claim to be, 'The ones who find paths for mortals. We are the Pathfinders.' "
     "Which I think is pretty funny."),
    (1121, 11, "circle_room_trial", "Operator",
     "The campaign rips off both Rise of the Runelords and Sunless Citadel shamelessly. "
     "Normally I play casters. I actually find that melee characters can be more difficult. "
     "You could build in a linear path to something like a Vital Strike build "
     "or a reach Cleave build with Outflank "
     "yet still the moment arrives and you have to add up all of your bonuses "
     "and it is easy to get something wrong. "
     "Most casters find a few spells they think are cool then cast Scorching Ray every combat. "
     "Even the cool ones you must prepare beforehand or know each level-up "
     "bound to a very discrete list."),
    (1121, 11, "circle_room_trial", "Operator",
     "The alchemist is my favorite because of the dynamic nature of mutagens, "
     "the range of extracts, and the directionality still found in bombs. "
     "I go Healing Bomb often so that I don't have to develop a feat tree around bombs, "
     "and so I can offer healing without sacrificing a dynamic yet specialized build. "
     "I am the In Between Quests GM which means that I fill in when the GM can't make a session. "
     "Last time we played Mork Borg which was an interesting detour. "
     "Anyway, I would like to become a User."),
]


# ── TTS helper ─────────────────────────────────────────────────────────────────

def _probe_dur(path: Path) -> float:
    r = subprocess.run(
        ["ffprobe", "-v", "quiet", "-print_format", "json",
         "-show_format", str(path)],
        capture_output=True, text=True, check=True,
    )
    return float(json.loads(r.stdout)["format"]["duration"])


def tts_segment(speaker: str, text: str, dest: Path, dry_run: bool) -> float:
    """Generate TTS, save to dest, return duration in seconds."""
    import urllib.request
    voice_id = VOICE_MAP.get(speaker, "")
    if not voice_id:
        print(f"  [skip] no voice for {speaker}")
        dest.write_bytes(b"")          # empty placeholder
        return 0.0
    if dest.exists() and dest.stat().st_size > 1000:
        dur = _probe_dur(dest)
        print(f"  [keep] {dest.name}  ({dur:.2f}s)")
        return dur
    if dry_run:
        print(f"  [dry]  {speaker}: {text[:60]}")
        return 2.0                      # estimate
    print(f"  [gen]  {speaker}: {text[:60]}")
    body = json.dumps({
        "text": text,
        "model_id": MODEL_ID,
        "voice_settings": {"stability": 0.5, "similarity_boost": 0.75},
    }).encode()
    req = urllib.request.Request(
        f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}",
        data=body,
        headers={
            "xi-api-key": ELEVEN_KEY,
            "Content-Type": "application/json",
            "Accept": "audio/mpeg",
        },
    )
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, timeout=60) as resp:
                dest.write_bytes(resp.read())
            break
        except Exception as e:
            if attempt == 2:
                raise
            print(f"    retry {attempt+1}: {e}")
            time.sleep(3)
    dur = _probe_dur(dest)
    print(f"    → {dur:.2f}s")
    return dur


# ── Main ────────────────────────────────────────────────────────────────────────

def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    SEG_DIR.mkdir(parents=True, exist_ok=True)

    # Load existing cues and concat lines
    cues = [json.loads(l) for l in CUES_F.read_text().splitlines() if l.strip()]
    concat_lines = [l for l in CONCAT_F.read_text().splitlines() if l.strip()]
    print(f"Loaded {len(cues)} cues, {len(concat_lines)} concat lines")

    # Validate alignment
    if len(cues) != len(concat_lines):
        sys.exit(f"Mismatch: {len(cues)} cues vs {len(concat_lines)} concat lines")

    # Step 1: generate TTS for all new lines, collect (insert_after, segment_path, duration)
    # Group by insert_after to maintain order within each block
    from collections import defaultdict
    blocks: dict[int, list[tuple[int, dict, Path, float]]] = defaultdict(list)

    start_idx = max(int(p.name.split("_")[0]) for p in SEG_DIR.glob("*.mp3")) + 1
    print(f"New segments start at index {start_idx}")

    for i, (insert_after, act, frame, speaker, text) in enumerate(NEW_LINES):
        short = SPEAKER_SHORT.get(speaker, speaker[:4])
        h = hashlib.md5(text.encode()).hexdigest()[:16]
        seg_name = f"{start_idx + i:04d}_{short}_{h}.mp3"
        seg_path = SEG_DIR / seg_name
        dur = tts_segment(speaker, text, seg_path, args.dry_run)
        cue_entry = {
            "act": act,
            "frame": frame,
            "speaker": speaker,
            "text": text,
            "start": -1.0,      # will be computed in step 2
            "end":   -1.0,
        }
        blocks[insert_after].append((i, cue_entry, seg_path, dur))

    if args.dry_run:
        total = sum(dur for block in blocks.values() for _, _, _, dur in block)
        print(f"\nDry run: {sum(len(b) for b in blocks.values())} new lines, ~{total:.1f}s total")
        return

    # Step 2: rebuild cues.jsonl and concat_lines with insertions
    new_cues:   list[dict] = []
    new_concat: list[str]  = []
    time_offset = 0.0   # cumulative duration added by insertions

    for idx, (cue, concat_line) in enumerate(zip(cues, concat_lines)):
        # Adjust timing of this existing cue
        adjusted = dict(cue)
        adjusted["start"] = cue["start"] + time_offset
        adjusted["end"]   = cue["end"]   + time_offset
        new_cues.append(adjusted)
        new_concat.append(concat_line)

        # Insert new lines AFTER this cue?
        if idx in blocks:
            t_insert = adjusted["end"]
            for _, cue_entry, seg_path, dur in blocks[idx]:
                entry = dict(cue_entry)
                entry["start"] = t_insert
                entry["end"]   = t_insert + dur
                new_cues.append(entry)
                new_concat.append(f"file '{seg_path.resolve()}'")
                t_insert     += dur
                time_offset  += dur

    print(f"\nNew timeline: {len(new_cues)} cues  (was {len(cues)})")
    print(f"Total duration shift: +{time_offset:.1f}s")

    # Step 3: write updated files (back up originals first)
    import shutil
    if not args.dry_run:
        shutil.copy2(CUES_F, CUES_F.with_suffix(".jsonl.bak"))
        shutil.copy2(CONCAT_F, CONCAT_F.with_suffix(".txt.bak"))

    CUES_F.write_text("\n".join(json.dumps(c) for c in new_cues) + "\n")
    CONCAT_F.write_text("\n".join(new_concat) + "\n")
    print("Written cues.jsonl and concat_segs.txt")

    # Step 4: rebuild minus08.mp3
    print(f"\nRebuilding {MP3_OUT.name} …")
    r = subprocess.run(
        ["ffmpeg", "-y", "-loglevel", "error",
         "-f", "concat", "-safe", "0",
         "-i", str(CONCAT_F),
         "-c:a", "libmp3lame", "-q:a", "2",
         str(MP3_OUT)],
        check=True,
    )
    dur = _probe_dur(MP3_OUT)
    print(f"Done: {MP3_OUT}  ({dur/60:.2f} min)")


if __name__ == "__main__":
    main()
