#!/usr/bin/env python3
"""
Segment JERRY_MCGUIRE_TRANSCRIPT.md into scene blocks.

Scene break: INT./EXT. headings, or >600 chars of accumulated text.
Output: tools/jm_segments.jsonl
"""
import json, hashlib, re, sys
from pathlib import Path

ROOT    = Path(__file__).resolve().parent.parent        # REALITY_USER_MANUAL/
SCRIPT  = ROOT / "tools" / "JERRY_MCGUIRE_TRANSCRIPT.md"
OUT     = ROOT / "tools" / "jm_segments.jsonl"

SCENE_RE = re.compile(r'^\s+(INT\.|EXT\.|FADE|CUT TO:|DISSOLVE)')
MAX_CHARS = 800


def sha1(text):
    return hashlib.sha1(text.encode()).hexdigest()


def flush(buf, idx):
    text = " ".join(buf).strip()
    text = re.sub(r' {2,}', ' ', text)
    if len(text) < 20:           # skip near-empty chunks
        return None
    return {"segment_id": f"JM{idx:04d}", "text": text, "text_sha1": sha1(text)}


def main():
    lines = SCRIPT.read_text(errors="replace").splitlines()
    segments, buf, idx = [], [], 0
    scene_heading = ""

    for line in lines:
        stripped = line.strip()
        is_scene = bool(SCENE_RE.match(line))

        if is_scene:
            rec = flush(buf, idx)
            if rec:
                rec["scene_heading"] = scene_heading
                segments.append(rec)
                idx += 1
            scene_heading = stripped
            buf = []
            continue

        if stripped:
            buf.append(stripped)

        # hard split on size
        if sum(len(x) for x in buf) >= MAX_CHARS:
            rec = flush(buf, idx)
            if rec:
                rec["scene_heading"] = scene_heading
                segments.append(rec)
                idx += 1
            buf = []

    # tail
    rec = flush(buf, idx)
    if rec:
        rec["scene_heading"] = scene_heading
        segments.append(rec)

    with OUT.open("w") as f:
        for seg in segments:
            f.write(json.dumps(seg) + "\n")

    print(f"Segmented {len(segments)} blocks → {OUT}")


if __name__ == "__main__":
    main()
