#!/usr/bin/env python3
"""run_matthew.py — Full Matthew decode on hilarious_marcupial (245 / RTX 4090).

Iterates all 1071 verses of Matthew, calling ggsd.run() per verse.
Verse-level checkpoint: completed verses are skipped on resume.

Usage (on hilarious_marcupial):
    # First time — download MorphGNT if not present:
    bash tools/download_morphgnt.sh

    # Dry run (tokenise only, no model calls):
    .venv/bin/python run_matthew.py --model ollama/dengcao/Qwen3-30B-A3B-Instruct-2507:Q4_K_M --dry-run

    # Full run:
    .venv/bin/python run_matthew.py --model ollama/dengcao/Qwen3-30B-A3B-Instruct-2507:Q4_K_M

    # Resume after interruption:
    .venv/bin/python run_matthew.py --model ollama/dengcao/Qwen3-30B-A3B-Instruct-2507:Q4_K_M

    # Watch from 82 (heuristic-friction):
    bash tools/watch_matthew.sh

Output:
    runs/matthew_full/progress.json       — live progress (poll from 82)
    runs/matthew_full/completed.json      — list of completed verse refs
    runs/matthew_full/errors.jsonl        — verse-level errors (append-only)
    runs/<verse_slug>_<timestamp>/        — standard ggsd per-verse output
"""
from __future__ import annotations

import datetime
import json
import os
import sys
import time
import traceback
from pathlib import Path

# ── Path setup ────────────────────────────────────────────────────────────────
GGSD_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(GGSD_DIR))

_env_path = GGSD_DIR.parent.parent / ".env"
if _env_path.exists():
    try:
        from dotenv import load_dotenv
        load_dotenv(_env_path)
    except ImportError:
        for line in _env_path.read_text().splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, _, v = line.partition("=")
                os.environ.setdefault(k.strip(), v.strip())

from ggsd import run as ggsd_run
from sources import load_morphgnt

# ── Matthew verse table ───────────────────────────────────────────────────────
# Verse counts from MorphGNT / NA28. 1071 verses total.
MATTHEW_VERSE_COUNTS: dict[int, int] = {
     1: 25,  2: 23,  3: 17,  4: 25,  5: 48,
     6: 34,  7: 29,  8: 34,  9: 38, 10: 42,
    11: 30, 12: 50, 13: 58, 14: 36, 15: 39,
    16: 28, 17: 27, 18: 35, 19: 30, 20: 34,
    21: 46, 22: 46, 23: 39, 24: 51, 25: 46,
    26: 75, 27: 66, 28: 20,
}

TOTAL_VERSES = sum(MATTHEW_VERSE_COUNTS.values())   # 1071

def all_verse_refs() -> list[str]:
    """Return every Matthew verse reference in order."""
    refs = []
    for ch in range(1, 29):
        for vs in range(1, MATTHEW_VERSE_COUNTS[ch] + 1):
            refs.append(f"Matthew {ch}:{vs}")
    return refs

# ── Progress / checkpoint ─────────────────────────────────────────────────────
BOOK_DIR = GGSD_DIR / "runs" / "matthew_full"

def load_progress() -> dict:
    p = BOOK_DIR / "progress.json"
    if p.exists():
        return json.loads(p.read_text())
    return {
        "n_done": 0,
        "n_total": TOTAL_VERSES,
        "n_words_done": 0,
        "current_verse": None,
        "rate_verses_per_hour": None,
        "eta_hours": None,
        "started_utc": None,
        "updated_utc": None,
        "model": None,
        "status": "pending",
    }


def load_completed() -> set[str]:
    p = BOOK_DIR / "completed.json"
    if p.exists():
        return set(json.loads(p.read_text()))
    return set()


def save_progress(prog: dict) -> None:
    BOOK_DIR.mkdir(parents=True, exist_ok=True)
    prog["updated_utc"] = datetime.datetime.utcnow().isoformat() + "Z"
    (BOOK_DIR / "progress.json").write_text(json.dumps(prog, indent=2, ensure_ascii=False))


def save_completed(completed: set[str]) -> None:
    BOOK_DIR.mkdir(parents=True, exist_ok=True)
    (BOOK_DIR / "completed.json").write_text(
        json.dumps(sorted(completed), indent=2, ensure_ascii=False)
    )


def log_error(verse_ref: str, exc: Exception) -> None:
    BOOK_DIR.mkdir(parents=True, exist_ok=True)
    entry = {
        "verse": verse_ref,
        "error": str(exc),
        "traceback": traceback.format_exc(),
        "utc": datetime.datetime.utcnow().isoformat() + "Z",
    }
    with open(BOOK_DIR / "errors.jsonl", "a") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")


# ── Main runner ───────────────────────────────────────────────────────────────
def main() -> None:
    import argparse
    ap = argparse.ArgumentParser(description="Full Matthew decode — hilarious_marcupial")
    ap.add_argument(
        "--model", required=True,
        help="Model ID, e.g. ollama/dengcao/Qwen3-30B-A3B-Instruct-2507:Q4_K_M",
    )
    ap.add_argument(
        "--morphgnt", default="",
        help="Path to MorphGNT Matthew file (default: tools/sblgnt/Matthew-morphgnt.txt)",
    )
    ap.add_argument(
        "--dry-run", action="store_true",
        help="Tokenise only — no model calls. Verifies MorphGNT coverage and Logeion reachability.",
    )
    ap.add_argument(
        "--start-at", default="",
        metavar="Matthew CH:VS",
        help="Skip all verses before this reference (useful for manual range splits).",
    )
    ap.add_argument(
        "--end-at", default="",
        metavar="Matthew CH:VS",
        help="Stop after this reference.",
    )
    ap.add_argument(
        "--chapter", type=int, default=0,
        help="Run only this chapter (1–28).",
    )
    args = ap.parse_args()

    model_id  = args.model
    morphgnt  = args.morphgnt or str(GGSD_DIR / "tools" / "sblgnt" / "Matthew-morphgnt.txt")
    dry_run   = args.dry_run

    # Verify MorphGNT file
    morphgnt_path = Path(morphgnt)
    if not morphgnt_path.exists():
        print(f"\nMorphGNT file not found: {morphgnt_path}")
        print("Run:  bash tools/download_morphgnt.sh")
        sys.exit(1)

    # Load MorphGNT once — reused across all verses
    print(f"Loading MorphGNT: {morphgnt_path}")
    morphgnt_data = load_morphgnt(morphgnt_path)
    total_morphgnt_words = sum(len(v) for v in morphgnt_data.values())
    print(f"  {len(morphgnt_data)} verses · {total_morphgnt_words} words loaded")

    # Verse list
    refs = all_verse_refs()

    # Apply --chapter filter
    if args.chapter:
        refs = [r for r in refs if r.startswith(f"Matthew {args.chapter}:")]
        print(f"Chapter filter: {len(refs)} verses in chapter {args.chapter}")

    # Apply --start-at / --end-at
    if args.start_at:
        try:
            idx = refs.index(args.start_at)
            refs = refs[idx:]
            print(f"Starting at {args.start_at} ({len(refs)} verses remaining)")
        except ValueError:
            sys.exit(f"--start-at: '{args.start_at}' not found in Matthew verse list")

    if args.end_at:
        try:
            idx = refs.index(args.end_at)
            refs = refs[:idx + 1]
            print(f"Ending at {args.end_at} ({len(refs)} verses)")
        except ValueError:
            sys.exit(f"--end-at: '{args.end_at}' not found in Matthew verse list")

    # Load checkpoint
    completed = load_completed()
    remaining = [r for r in refs if r not in completed]
    print(f"\nCheckpoint: {len(completed)} done, {len(remaining)} remaining of {len(refs)} in scope")

    if not remaining:
        print("All verses complete.")
        return

    # Progress
    prog = load_progress()
    if prog["started_utc"] is None:
        prog["started_utc"] = datetime.datetime.utcnow().isoformat() + "Z"
    prog["model"]    = model_id
    prog["n_total"]  = len(refs)
    prog["n_done"]   = len(completed)
    prog["status"]   = "running"
    save_progress(prog)

    print(f"\nModel:    {model_id}")
    print(f"Dry-run:  {dry_run}")
    print(f"Output:   {BOOK_DIR}")
    print(f"\nStarting decode — {len(remaining)} verses\n")
    print("─" * 72)

    t_start     = time.time()
    words_done  = prog.get("n_words_done", 0)
    verse_times: list[float] = []

    for i, verse_ref in enumerate(remaining):
        prog["current_verse"] = verse_ref
        prog["n_done"]        = len(completed)
        prog["n_words_done"]  = words_done
        save_progress(prog)

        t0 = time.time()
        print(f"\n[{len(completed) + 1:4d}/{len(refs)}]  {verse_ref}", flush=True)

        try:
            run_dir = ggsd_run(
                verse_ref=verse_ref,
                model_id=model_id,
                dry_run=dry_run,
                greek_override="",
                morphgnt_path=str(morphgnt_path),
                resume_dir="",
            )
            elapsed = time.time() - t0
            verse_times.append(elapsed)

            # Count words from this verse
            meta_path = Path(run_dir) / "run_meta.json" if run_dir else None
            if meta_path and meta_path.exists():
                meta = json.loads(meta_path.read_text())
                words_done += meta.get("n_words", 0)

            completed.add(verse_ref)
            save_completed(completed)

            # Rate estimate (rolling 20-verse window)
            window = verse_times[-20:]
            rate_s = sum(window) / len(window)   # seconds per verse
            remaining_count = len(refs) - len(completed)
            eta_h = (remaining_count * rate_s) / 3600.0

            prog["n_done"]              = len(completed)
            prog["n_words_done"]        = words_done
            prog["rate_verses_per_hour"] = round(3600.0 / rate_s, 1)
            prog["eta_hours"]           = round(eta_h, 2)
            save_progress(prog)

            print(f"  ✓  {elapsed:.1f}s  |  {len(completed)}/{len(refs)}  |  "
                  f"rate {3600/rate_s:.0f} v/h  |  ETA {eta_h:.1f}h", flush=True)

        except KeyboardInterrupt:
            print(f"\n\nInterrupted at {verse_ref}. Progress saved — resume with same command.")
            prog["status"] = "interrupted"
            prog["current_verse"] = verse_ref
            save_progress(prog)
            sys.exit(0)

        except Exception as exc:
            print(f"  ✗  ERROR: {exc}")
            log_error(verse_ref, exc)
            # Continue to next verse — do not add to completed
            time.sleep(2)   # brief pause after error before next verse

    # Done
    total_elapsed = time.time() - t_start
    prog["status"]        = "complete"
    prog["n_done"]        = len(completed)
    prog["n_words_done"]  = words_done
    prog["current_verse"] = None
    prog["eta_hours"]     = 0.0
    save_progress(prog)

    print(f"\n{'─' * 72}")
    print(f"Complete — {len(completed)} verses in {total_elapsed / 3600:.2f}h")
    print(f"Output: {BOOK_DIR}")
    print(f"Per-verse runs: {GGSD_DIR / 'runs'}/Matthew_*/")


if __name__ == "__main__":
    main()
