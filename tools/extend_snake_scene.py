#!/usr/bin/env python3
"""
tools/extend_snake_scene.py
Second-pass extend: inserts the fourth-wall break (snake scene) into the
ALREADY-EXTENDED cues.jsonl (1193 entries after extend_minus08_audio.py ran).

Inserts after cue index 1106 — Joey: "He's not a villain. He's like a librarian."

Run from REALITY_USER_MANUAL/:
    .venv/bin/python tools/extend_snake_scene.py [--dry-run]
"""
import argparse, hashlib, json, os, subprocess, sys, time
from pathlib import Path

BASE      = Path(__file__).parent.parent
AUDIO_DIR = BASE / "audio" / "minus08"
SEG_DIR   = AUDIO_DIR / "segments"
CUES_F    = AUDIO_DIR / "cues.jsonl"
CONCAT_F  = AUDIO_DIR / "concat_segs.txt"
MP3_OUT   = AUDIO_DIR / "minus08.mp3"

def _load_env():
    env_f = BASE / ".env"
    if env_f.exists():
        for line in env_f.read_text().splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, _, v = line.partition("=")
                os.environ.setdefault(k.strip(), v.strip())
_load_env()

ELEVEN_KEY = os.environ.get("ELEVENLABS_API_KEY", "")
MODEL_ID   = "eleven_multilingual_v2"

VOICE_MAP = {
    "Narrator":  os.environ.get("VOICE_NARRATOR",  "Nxtvajpo1h6Ok0K5zP4M"),
    "Archivist": os.environ.get("VOICE_NARRATOR",  "Nxtvajpo1h6Ok0K5zP4M"),
    "Snake":     os.environ.get("VOICE_SNAKE",     "iUex9jQAAsMqYMxYUkK0"),
    "Goat":      os.environ.get("VOICE_GOAT",      "LeKRRWCgp0eQIsROehFm"),
    "Joey":      os.environ.get("VOICE_JOEY",      os.environ.get("VOICE_JOEY_LIB", "QDidinP5kDJnJ9cCCGp6")),
}

SPEAKER_SHORT = {
    "Narrator": "Narr", "Archivist": "Arch",
    "Snake": "Snak", "Goat": "Goat", "Joey": "Joey",
}

# Insert all of these AFTER cue index 1106 in the current 1193-cue list.
# (Cue 1106 = Joey "He's not a villain. He's like a librarian.")
INSERT_AFTER = 1106

SNAKE_LINES = [
    ("Narrator",
     "A purple snake descends from the Oak, resting precisely upon the healer's perch "
     "for just a moment or none at all — and the snake eludes further description, "
     "which seems like something this snake would do."),
    ("Narrator",
     "The snake begins hissing in the hissy fashion of snakes which is to hiss. "
     "The Narrator notes, for the benefit of whoever is keeping the phonological record, "
     "that the speech which follows consists entirely of the letter P. "
     "The snake is aware of this. The snake does not consider it a problem. "
     "The snake is a snake. Its hiss is its medium and its medium is betraying it "
     "in the direction of the labial plosive which is not a sibilant and cannot be hissed "
     "and the snake does not care."),
    ("Snake",
     "Purple oh appears prettier preferring providing precisely per point, "
     "toe pre-empting preamble, pre ain pro prompting percolation, "
     "jinn proving prettier purples prior kai proof proving purpler prey, "
     "toe praying persons personifying purpler purplers, "
     "too printing prayers auto."),
    ("Goat",
     "Curios Hawke. The swyrd."),
    ("Narrator",
     "The Archivist produces a common longsword. "
     "It appears as common a longsword as common is common yet also commoner approaching a commonest, "
     "which fills this Narrator with the uncommon epistemic dread of buttons which skip time "
     "increasingly at the unnaturally logarithmic rate of hands which are based logs in ten. "
     "So fairly common by my estimation while hardly mundane by my appraisal. "
     "Draavio declared this phenomenon esteemed."),
    ("Archivist",
     "Joey. The druid is not averse to metals. Metals are in the soil and in the stone which they work. "
     "The druid is the material required to create standing circular apertures: hard wood and stone. "
     "The apertures are for celestial navigation and communication. "
     "In Nicaea they were called terrae and the trembled which caused the Romans to terrere "
     "which led to the deliberate demise of Nicomedia where necromancers and specters became warlocks and ghosts. "
     "A specter is found by observing patiently the space between within the aperture. "
     "The magic of this swyrd is in the subtle and natural flaws brought by decay which is rho. "
     "Inspect and you shall know it. It is possible to place the swyrd within a stone. "
     "The iguana explained as much with the patient under the knife and the knife under the patient."),
    ("Joey",
     "The Blank. Then in the small print of carefully folded steel: "
     "franca lingua translation page negative forty-two. "
     "The inscription scarred into the leather grip reads: only for those curios."),
]


def _probe_dur(path: Path) -> float:
    r = subprocess.run(
        ["ffprobe", "-v", "quiet", "-print_format", "json", "-show_format", str(path)],
        capture_output=True, text=True, check=True,
    )
    return float(json.loads(r.stdout)["format"]["duration"])


def tts_segment(speaker: str, text: str, dest: Path, dry_run: bool) -> float:
    import urllib.request
    voice_id = VOICE_MAP.get(speaker, "")
    if not voice_id:
        print(f"  [skip] no voice for {speaker}"); dest.write_bytes(b""); return 0.0
    if dest.exists() and dest.stat().st_size > 1000:
        dur = _probe_dur(dest)
        print(f"  [keep] {dest.name}  ({dur:.2f}s)"); return dur
    if dry_run:
        print(f"  [dry]  {speaker}: {text[:70]}"); return 2.5
    print(f"  [gen]  {speaker}: {text[:70]}")
    body = json.dumps({
        "text": text, "model_id": MODEL_ID,
        "voice_settings": {"stability": 0.5, "similarity_boost": 0.75},
    }).encode()
    req = urllib.request.Request(
        f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}",
        data=body,
        headers={"xi-api-key": ELEVEN_KEY, "Content-Type": "application/json", "Accept": "audio/mpeg"},
    )
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, timeout=60) as resp:
                dest.write_bytes(resp.read())
            break
        except Exception as e:
            if attempt == 2: raise
            print(f"    retry {attempt+1}: {e}"); time.sleep(3)
    dur = _probe_dur(dest)
    print(f"    → {dur:.2f}s")
    return dur


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    SEG_DIR.mkdir(parents=True, exist_ok=True)

    cues = [json.loads(l) for l in CUES_F.read_text().splitlines() if l.strip()]
    concat_lines = [l for l in CONCAT_F.read_text().splitlines() if l.strip()]
    print(f"Loaded {len(cues)} cues, {len(concat_lines)} concat lines")

    if len(cues) != len(concat_lines):
        sys.exit(f"Mismatch: {len(cues)} cues vs {len(concat_lines)} concat lines")

    # Verify insertion point
    anchor = cues[INSERT_AFTER]
    print(f"\nAnchor cue [{INSERT_AFTER}]: {anchor['speaker']!r}: {anchor['text'][:60]!r}")
    if "librarian" not in anchor.get("text", "").lower() and "villain" not in anchor.get("text","").lower():
        print(f"WARNING: anchor cue does not look like the expected librarian line.")
        print(f"  Full text: {anchor['text']}")

    # Start index for new segments
    existing = list(SEG_DIR.glob("*.mp3"))
    start_idx = max(int(p.name.split("_")[0]) for p in existing) + 1 if existing else 1200
    print(f"New segments start at index {start_idx}")
    print(f"Inserting {len(SNAKE_LINES)} new lines after cue {INSERT_AFTER}\n")

    # Generate TTS
    segs = []
    for i, (speaker, text) in enumerate(SNAKE_LINES):
        short = SPEAKER_SHORT.get(speaker, speaker[:4])
        h = hashlib.md5(text.encode()).hexdigest()[:16]
        seg_name = f"{start_idx + i:04d}_{short}_{h}.mp3"
        seg_path = SEG_DIR / seg_name
        dur = tts_segment(speaker, text, seg_path, args.dry_run)
        segs.append((speaker, text, seg_path, dur))

    if args.dry_run:
        total = sum(d for _, _, _, d in segs)
        print(f"\nDry run: {len(segs)} lines, ~{total:.1f}s total (+{total/60:.1f} min)")
        return

    # Rebuild cues + concat with insertion
    import shutil
    shutil.copy2(CUES_F,   CUES_F.with_suffix(".jsonl.bak2"))
    shutil.copy2(CONCAT_F, CONCAT_F.with_suffix(".txt.bak2"))

    new_cues:   list[dict] = []
    new_concat: list[str]  = []
    time_offset = 0.0

    for idx, (cue, concat_line) in enumerate(zip(cues, concat_lines)):
        adjusted = dict(cue)
        adjusted["start"] = cue["start"] + time_offset
        adjusted["end"]   = cue["end"]   + time_offset
        new_cues.append(adjusted)
        new_concat.append(concat_line)

        if idx == INSERT_AFTER:
            t_insert = adjusted["end"]
            for speaker, text, seg_path, dur in segs:
                new_cues.append({
                    "act": 11,
                    "frame": "fourth_wall_break",
                    "speaker": speaker,
                    "text": text,
                    "start": t_insert,
                    "end":   t_insert + dur,
                })
                new_concat.append(f"file '{seg_path.resolve()}'")
                t_insert    += dur
                time_offset += dur

    print(f"\nNew timeline: {len(new_cues)} cues  (was {len(cues)})")
    print(f"Total duration shift: +{time_offset:.1f}s  (+{time_offset/60:.2f} min)")

    CUES_F.write_text("\n".join(json.dumps(c) for c in new_cues) + "\n")
    CONCAT_F.write_text("\n".join(new_concat) + "\n")
    print("Written cues.jsonl and concat_segs.txt")

    print(f"\nRebuilding {MP3_OUT.name} …")
    subprocess.run(
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
