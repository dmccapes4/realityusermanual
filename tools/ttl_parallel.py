#!/usr/bin/env python3
"""
Vincent's parallel TTL track — the boot clock.

The experiment (inferred; we were not present at construction) is
narrative retrograde: the heard recording is to start at access granted
(the card / key), not at boot. TTL is the boot-accounted control: same
text, start of scene to end, no engine switch.

The heard mix still phases (TTL → Matilda at the card → Narrator at the
retrograde notice). This script does not judge the clocks. The assay
that measures them is tools/vincent_assay.py.

  .venv/bin/python tools/ttl_parallel.py

Writes:
  audio/vincentvision_ttl.mp3
  audio/vincentvision_heard.mp3   (ElevenLabs/TTL-phase mix of -05 only)
  audio/vincentvision_parallel.jsonl
  audio/vincentvision_parallel_summary.json
"""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import generate_audio as g  # noqa: E402
from ttl_espeak import to_mp3  # noqa: E402

BASE = g.BASE
AUDIO = g.AUDIO_DIR
TTL_DIR = AUDIO / "ttl_parallel"
TTL_DIR.mkdir(parents=True, exist_ok=True)
SRC = g.SRC / "-05_VincentVision.md"


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


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    h.update(path.read_bytes())
    return h.hexdigest()


def flatten(segs: list[tuple[str, str]]) -> list[tuple[str, str]]:
    out = []
    for speaker, text in segs:
        if not text.strip():
            continue
        for piece in g.chunk_text(text):
            out.append((speaker, piece))
    return out


def heard_path(speaker: str, text: str) -> Path:
    vid = g.VOICE_MAP.get(speaker, g.FALLBACK_VOICE)
    return g.hash_path(speaker, text, vid, g.settings_for(speaker))


def ttl_path(text: str) -> Path:
    return g.hash_path("TTL", text, "ttl-espeak-ng", g.settings_for("TTL"))


def main():
    segs = flatten(g.parse_vincent(SRC))
    rows = []
    ttl_files: list[Path] = []
    heard_files: list[Path] = []
    t_ttl = 0.0
    t_heard = 0.0
    missing_heard = 0

    for i, (speaker, text) in enumerate(segs):
        hp = heard_path(speaker, text)
        tp = ttl_path(text)
        if not tp.exists() or tp.stat().st_size < 500:
            to_mp3(text, tp)
            print(f"  [ttl] {i:03d}  {tp.name}  {text[:56]}...")
        else:
            print(f"  [cached] {i:03d}  {tp.name}")

        if not hp.exists() or hp.stat().st_size < 500:
            missing_heard += 1
            hd = hb = 0
            hsha = ""
        else:
            hd = duration(hp)
            hb = hp.stat().st_size
            hsha = sha256(hp)
            heard_files.append(hp)

        td = duration(tp)
        tb = tp.stat().st_size
        words = [w for w in text.split() if w]
        chars = len(text)
        row = {
            "i": i,
            "heard_speaker": speaker,
            "text": text,
            "chars": chars,
            "words": len(words),
            "heard_file": str(hp.relative_to(BASE)) if hp.exists() else None,
            "heard_sha256": hsha or None,
            "heard_bytes": hb,
            "heard_dur": round(hd, 6),
            "heard_start": round(t_heard, 6),
            "heard_end": round(t_heard + hd, 6),
            "ttl_file": str(tp.relative_to(BASE)),
            "ttl_sha256": sha256(tp),
            "ttl_bytes": tb,
            "ttl_dur": round(td, 6),
            "ttl_start": round(t_ttl, 6),
            "ttl_end": round(t_ttl + td, 6),
            "dur_delta": round(td - hd, 6),
            "dur_ratio": round(td / hd, 6) if hd else None,
            "heard_chars_per_sec": round(chars / hd, 6) if hd else None,
            "ttl_chars_per_sec": round(chars / td, 6) if td else None,
        }
        rows.append(row)
        ttl_files.append(tp)
        t_ttl += td
        t_heard += hd

    ledger = AUDIO / "vincentvision_parallel.jsonl"
    ledger.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows))
    ledger_sha = sha256(ledger)

    g.concatenate(ttl_files, AUDIO / "vincentvision_ttl.mp3")
    if heard_files:
        g.concatenate(heard_files, AUDIO / "vincentvision_heard.mp3")

    deltas = [r["dur_delta"] for r in rows]
    ratios = [r["dur_ratio"] for r in rows if r["dur_ratio"] is not None]
    summary = {
        "scene": "-05_VincentVision.md",
        "plan": "Narrative retrograde: TTL is the boot clock (scene start→end). Heard starts ElevenLabs at access granted. Assay: tools/vincent_assay.py.",
        "segments": len(rows),
        "missing_heard": missing_heard,
        "ttl_total_s": round(t_ttl, 6),
        "heard_total_s": round(t_heard, 6),
        "total_dur_delta": round(t_ttl - t_heard, 6),
        "mean_dur_delta": round(sum(deltas) / len(deltas), 6) if deltas else None,
        "mean_dur_ratio": round(sum(ratios) / len(ratios), 6) if ratios else None,
        "min_dur_ratio": round(min(ratios), 6) if ratios else None,
        "max_dur_ratio": round(max(ratios), 6) if ratios else None,
        "ttl_bytes": sum(r["ttl_bytes"] for r in rows),
        "heard_bytes": sum(r["heard_bytes"] for r in rows),
        "text_chars": sum(r["chars"] for r in rows),
        "text_words": sum(r["words"] for r in rows),
        "ledger": str(ledger.relative_to(BASE)),
        "ledger_sha256": ledger_sha,
        "ttl_mix": "audio/vincentvision_ttl.mp3",
        "heard_mix": "audio/vincentvision_heard.mp3",
        "note": "Anomaly hunt is later. These numbers are the control, not a verdict. Arithmetic prestidigitation is a named later pass, not this file.",
    }
    (AUDIO / "vincentvision_parallel_summary.json").write_text(
        json.dumps(summary, indent=2) + "\n"
    )
    print(f"\n{len(rows)} segments")
    print(f"  TTL   {t_ttl:.2f}s  → audio/vincentvision_ttl.mp3")
    print(f"  heard {t_heard:.2f}s  → audio/vincentvision_heard.mp3")
    print(f"  delta {t_ttl - t_heard:+.2f}s")
    print(f"  ledger {ledger}  sha256 {ledger_sha[:16]}…")
    print("TTL runs the whole scene. Analysis comes later.")


if __name__ == "__main__":
    main()
