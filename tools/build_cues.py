#!/usr/bin/env python3
"""
Build video/cues.jsonl from audio segments + the beat program.

Each cue carries the plates that should be on: background, layers, prop,
camera tag. Merlin is full-bleed. Recast ending is a frame shift
(stanley_exit → door_closed → butterfly_inside).

  .venv/bin/python tools/build_cues.py
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import generate_audio as g  # noqa: E402

BASE = Path(__file__).resolve().parent.parent
VIDEO = BASE / "video"
OUT = VIDEO / "cues.jsonl"
BEATS = VIDEO / "catalogs" / "beats.jsonl"
SHOTS = VIDEO / "catalogs" / "shots.jsonl"

SPEAKER_TO_CHAR = {
    "The Narrator": "narrator",
    "Feynman": "feynman",
    "McClane": "mcclane",
    "Stamper": "stamper",
    "Cecil": "cecil",
    "Cecil Palmer": "cecil",
    "Sauron": "sauron",
    "Chandler": "chandler",
    "Ross": "ross",
    "Joey": "joey",
    "Caller": "caller",
    "The Caller": "caller",
    "Euler": "euler",
    "Editor": "editor",
    "Vincent": "vincent",
    "Carter": "carter",
    "Goines": "goines",
    "Operator": "operator",
    "TTL": "operator",
    "Terminal": "operator",
    "Stanley": "stanley",
    "Merlin": "merlin",
}


def load_jsonl(path: Path) -> list[dict]:
    if not path.exists():
        return []
    return [json.loads(l) for l in path.read_text().splitlines() if l.strip()]


def duration(path: Path) -> float:
    cmd = [
        "ffprobe", "-v", "error", "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1", str(path),
    ]
    r = subprocess.run(cmd, capture_output=True, text=True)
    try:
        return float(r.stdout.strip())
    except ValueError:
        return 0.0


def when_matches(when: dict | None, speaker: str, text: str) -> bool:
    if not when:
        return True
    speakers = when.get("speaker")
    if speakers and speaker not in speakers:
        return False
    needles = when.get("text_contains") or []
    if needles and not any(n.lower() in text.lower() for n in needles):
        return False
    return True


def resolve_beat(
    beats: list[dict],
    section: str,
    speaker: str,
    text: str,
    sticky: dict | None,
) -> dict:
    chosen: dict = {}
    specific = False
    for beat in beats:
        if beat.get("section") != section:
            continue
        if not when_matches(beat.get("when"), speaker, text):
            continue
        chosen = beat
        if beat.get("when"):
            specific = True
    # Recast frame shift stays put. Do not snap back to the table
    # with Stanley still in the third row after he has left.
    if sticky and not specific and section == sticky.get("section"):
        return sticky
    return chosen


def compose(beat: dict, speaker: str, text: str, shots: dict[str, dict]) -> dict:
    background = beat.get("background")
    layers = list(beat.get("layers") or [])
    speaker_layer = beat.get("speaker_layer") or {}
    speaker_front = beat.get("speaker_front") or {}
    front = speaker_layer.get(speaker) or speaker_front.get(speaker)
    if front and front not in layers:
        layers.append(front)
    prop = beat.get("prop")
    for prop_id, needles in (beat.get("prop_when") or {}).items():
        if any(n.lower() in text.lower() for n in needles):
            prop = prop_id
            if prop_id not in layers:
                layers.append(prop_id)
    layers = [lid for lid in layers if lid in shots]
    if background and background not in shots:
        background = None
    return {
        "background": background,
        "layers": layers,
        "prop": prop if prop in shots else None,
        "camera": beat.get("camera"),
        "full_bleed": bool(beat.get("full_bleed")),
        "beat": beat.get("id"),
    }


def main():
    beats = load_jsonl(BEATS)
    shots = {row["id"]: row for row in load_jsonl(SHOTS)}
    if not beats:
        sys.exit(f"missing beats: {BEATS}")
    if not shots:
        sys.exit(f"missing shots: {SHOTS}")

    t = 0.0
    cues = []
    sticky: dict | None = None
    sticky_section: str | None = None
    for label, path, mode, extra in g.SECTIONS:
        if label != sticky_section:
            sticky = None
            sticky_section = label
        segs = g.parse_section(label, path, mode, extra)
        for speaker, text in segs:
            if speaker == "__operator__":
                rec = Path(text)
                d = duration(rec) if rec.exists() else 0.0
                speaker = "Operator"
                text = "[operator recording]"
            else:
                if not text.strip():
                    continue
                vid = g.VOICE_MAP.get(speaker, g.FALLBACK_VOICE)
                files = []
                for piece in g.chunk_text(text):
                    p = g.hash_path(speaker, piece, vid, g.settings_for(speaker))
                    if p.exists():
                        files.append(p)
                d = sum(duration(p) for p in files)
                if d <= 0:
                    continue
            beat = resolve_beat(beats, label, speaker, text, sticky)
            # Frame shift starts at Stanley's walk. Hold it through the
            # leftover lines (No answer / CLOSE) without matching them as words.
            if beat.get("id") in {
                "stanley_exit", "stanley_follow_out", "door_closed",
                "butterfly_inside", "butterfly_wings", "butterfly_debate",
            }:
                sticky = beat
            plate = compose(beat, speaker, text, shots)
            char = "merlin" if label == "Merlin seed" else SPEAKER_TO_CHAR.get(speaker, "narrator")
            cues.append({
                "start": round(t, 3),
                "end": round(t + d, 3),
                "section": label,
                "speaker": speaker,
                "character": char,
                "text": text.strip()[:180],
                **plate,
            })
            t += d

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text("".join(json.dumps(c, ensure_ascii=False) + "\n" for c in cues))
    cameras = {}
    for c in cues:
        cam = c.get("camera")
        if cam:
            cameras[cam] = cameras.get(cam, 0) + 1
    print(f"{len(cues)} cues  {t:.1f}s  → {OUT}")
    print(f"  cameras {cameras}")


if __name__ == "__main__":
    main()
