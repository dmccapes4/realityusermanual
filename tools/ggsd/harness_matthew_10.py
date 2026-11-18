#!/usr/bin/env python3
"""harness_matthew_10.py — 10-verse quality harness for GGSD.

Runs the first N verses of Matthew (default Matthew 1:1–1:10) through
ggsd.run() and evaluates each run against ten named criteria.

Usage:
    .venv/bin/python harness_matthew_10.py --model claude-sonnet-5-5
    .venv/bin/python harness_matthew_10.py --model claude-sonnet-5-5 --n-verses 5
    .venv/bin/python harness_matthew_10.py --model claude-sonnet-5-5 --dry-run
    .venv/bin/python harness_matthew_10.py --eval-only runs/harness_matthew_10_<timestamp>/

Output:
    runs/harness_matthew_10_<timestamp>/
        summary.json        — machine-readable pass/fail per criterion per verse
        summary.md          — human-readable table
        <verse_slug>_*/     — standard ggsd per-verse run directories (symlinked)

Criteria (evaluated per verse after the run):
    C1  run_complete          run_meta.json present + finished_at set (no crash)
    C2  word_count_positive   word_count >= 1 in run_meta
    C3  no_empty_words        no word with 0 gram + 0 lex + 0 trans in decoding JSON
    C4  all_words_translated  every word has >= 1 translation
    C5  all_words_lexical     every word has >= 1 lexical_rule
    C6  coverage_80pct        >= 80% of words have all three field groups non-empty
    C7  source_agreements     >= 1 multi-source agreement exists in verse.jsonl
    C8  questions_answered    both Q1 and Q2 answered without "[question error:"
    C9  no_schema_errors      validate_primitive() passes every word in verse.jsonl
    C10 driver_version        run_meta["driver_version"] == "0.0.2"
"""
from __future__ import annotations

import argparse
import datetime
import json
import os
import sys
import time
from pathlib import Path
from typing import Callable

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
from schema import validate_primitive, SchemaError

# ── Verse list ────────────────────────────────────────────────────────────────

# Full chapter 1 verse count from MorphGNT / NA28.
_CH1_VERSES = 25

def build_verse_list(n: int) -> list[str]:
    """Return the first n verses of Matthew (starting from 1:1)."""
    refs: list[str] = []
    for ch in range(1, 29):
        # verse counts (from run_matthew.py MATTHEW_VERSE_COUNTS)
        counts = {
            1: 25,  2: 23,  3: 17,  4: 25,  5: 48,
            6: 34,  7: 29,  8: 34,  9: 38, 10: 42,
            11: 30, 12: 50, 13: 58, 14: 36, 15: 39,
            16: 28, 17: 27, 18: 35, 19: 30, 20: 34,
            21: 46, 22: 46, 23: 39, 24: 51, 25: 46,
            26: 75, 27: 66, 28: 20,
        }
        for vs in range(1, counts.get(ch, 0) + 1):
            refs.append(f"Matthew {ch}:{vs}")
            if len(refs) >= n:
                return refs
    return refs

# ── Criteria ──────────────────────────────────────────────────────────────────
# Each criterion is a function:
#   fn(run_dir: Path) -> tuple[bool, str]
#   Returns (passed, detail_message)

CriterionFn = Callable[[Path], tuple[bool, str]]

CRITERIA: list[tuple[str, str, CriterionFn]] = []  # (id, label, fn)


def criterion(cid: str, label: str):
    """Decorator: register a criterion function."""
    def _dec(fn: CriterionFn) -> CriterionFn:
        CRITERIA.append((cid, label, fn))
        return fn
    return _dec


@criterion("C1", "run_complete")
def c_run_complete(run_dir: Path) -> tuple[bool, str]:
    meta_path = run_dir / "run_meta.json"
    if not meta_path.exists():
        return False, "run_meta.json missing"
    meta = json.loads(meta_path.read_text())
    if not meta.get("finished_at"):
        return False, "finished_at absent — run did not complete"
    return True, f"finished_at={meta['finished_at'][:19]}"


@criterion("C2", "word_count_positive")
def c_word_count(run_dir: Path) -> tuple[bool, str]:
    meta_path = run_dir / "run_meta.json"
    if not meta_path.exists():
        return False, "run_meta.json missing"
    meta = json.loads(meta_path.read_text())
    wc = meta.get("word_count", 0)
    if wc < 1:
        return False, f"word_count={wc}"
    return True, f"word_count={wc}"


@criterion("C3", "no_empty_words")
def c_no_empty_words(run_dir: Path) -> tuple[bool, str]:
    decoding_path = run_dir / "verse_grammatical_decoding.json"
    if not decoding_path.exists():
        return False, "verse_grammatical_decoding.json missing"
    decoding = json.loads(decoding_path.read_text())
    empty = []
    for w in decoding.get("words", []):
        if (not w.get("grammatical_rules")
                and not w.get("lexical_rules")
                and not w.get("translations")):
            empty.append(w.get("surface", "?"))
    if empty:
        return False, f"{len(empty)} empty word(s): {', '.join(empty)}"
    return True, "all words have at least one populated field"


@criterion("C4", "all_words_translated")
def c_all_translated(run_dir: Path) -> tuple[bool, str]:
    decoding_path = run_dir / "verse_grammatical_decoding.json"
    if not decoding_path.exists():
        return False, "verse_grammatical_decoding.json missing"
    decoding = json.loads(decoding_path.read_text())
    missing = [w.get("surface", "?") for w in decoding.get("words", [])
               if not w.get("translations")]
    if missing:
        return False, f"{len(missing)} word(s) without translation: {', '.join(missing)}"
    return True, "every word has >= 1 translation"


@criterion("C5", "all_words_lexical")
def c_all_lexical(run_dir: Path) -> tuple[bool, str]:
    decoding_path = run_dir / "verse_grammatical_decoding.json"
    if not decoding_path.exists():
        return False, "verse_grammatical_decoding.json missing"
    decoding = json.loads(decoding_path.read_text())
    missing = [w.get("surface", "?") for w in decoding.get("words", [])
               if not w.get("lexical_rules")]
    if missing:
        return False, f"{len(missing)} word(s) without lexical rule: {', '.join(missing)}"
    return True, "every word has >= 1 lexical rule"


@criterion("C6", "coverage_80pct")
def c_coverage_80(run_dir: Path) -> tuple[bool, str]:
    decoding_path = run_dir / "verse_grammatical_decoding.json"
    if not decoding_path.exists():
        return False, "verse_grammatical_decoding.json missing"
    decoding = json.loads(decoding_path.read_text())
    words = decoding.get("words", [])
    if not words:
        return False, "no words"
    full = sum(
        1 for w in words
        if w.get("grammatical_rules") and w.get("lexical_rules") and w.get("translations")
    )
    pct = full / len(words)
    ok = pct >= 0.80
    return ok, f"{full}/{len(words)} words fully populated ({pct:.0%})"


@criterion("C7", "source_agreements")
def c_source_agreements(run_dir: Path) -> tuple[bool, str]:
    """At least one word in verse.jsonl has a multi-source agreement."""
    jsonl_path = run_dir / "verse.jsonl"
    if not jsonl_path.exists():
        return False, "verse.jsonl missing"
    agreements_found = 0
    for line in jsonl_path.read_text().splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            p = json.loads(line)
        except json.JSONDecodeError:
            continue
        for ag in p.get("source_agreements", []):
            if ag.get("agreement", False):
                agreements_found += 1
    if agreements_found == 0:
        return False, "no multi-source agreements found in verse.jsonl"
    return True, f"{agreements_found} multi-source agreement(s) across verse"


@criterion("C8", "questions_answered")
def c_questions_answered(run_dir: Path) -> tuple[bool, str]:
    qpath = run_dir / "questions.jsonl"
    if not qpath.exists():
        return False, "questions.jsonl missing"
    lines = [l.strip() for l in qpath.read_text().splitlines() if l.strip()]
    if len(lines) < 2:
        return False, f"only {len(lines)}/2 question(s) in questions.jsonl"
    errors = []
    for line in lines[:2]:
        try:
            q = json.loads(line)
        except json.JSONDecodeError:
            errors.append("invalid JSON line")
            continue
        answer = q.get("answer", "")
        if "[question error:" in answer.lower():
            errors.append(f"Q{q.get('question_number','?')}: {answer[:80]}")
    if errors:
        return False, "; ".join(errors)
    return True, "both questions answered without error"


@criterion("C9", "no_schema_errors")
def c_schema_valid(run_dir: Path) -> tuple[bool, str]:
    jsonl_path = run_dir / "verse.jsonl"
    if not jsonl_path.exists():
        return False, "verse.jsonl missing"
    bad: list[str] = []
    for i, line in enumerate(jsonl_path.read_text().splitlines()):
        line = line.strip()
        if not line:
            continue
        try:
            p = json.loads(line)
            validate_primitive(p)
        except json.JSONDecodeError as e:
            bad.append(f"word[{i}]: JSON error: {e}")
        except SchemaError as e:
            surface = ""
            try:
                surface = json.loads(line).get("word", {}).get("surface", "?")
            except Exception:
                surface = f"line {i}"
            bad.append(f"{surface}: {e}")
    if bad:
        return False, f"{len(bad)} schema error(s): {bad[0]}"
    return True, "all primitives pass schema validation"


@criterion("C10", "driver_version")
def c_driver_version(run_dir: Path) -> tuple[bool, str]:
    meta_path = run_dir / "run_meta.json"
    if not meta_path.exists():
        return False, "run_meta.json missing"
    meta = json.loads(meta_path.read_text())
    v = meta.get("driver_version", "")
    if v != "0.0.2":
        return False, f"driver_version={v!r} (expected 0.0.2)"
    return True, f"driver_version={v}"


# ── Evaluation ────────────────────────────────────────────────────────────────

def evaluate_run(run_dir: Path) -> dict:
    """Evaluate all criteria against a completed run directory.

    Returns:
        {
            "run_dir": str,
            "results": [{"id", "label", "passed", "detail"}, ...],
            "n_passed": int,
            "n_total": int,
        }
    """
    results = []
    for cid, label, fn in CRITERIA:
        try:
            passed, detail = fn(run_dir)
        except Exception as e:
            passed, detail = False, f"criterion raised exception: {e}"
        results.append({
            "id":     cid,
            "label":  label,
            "passed": passed,
            "detail": detail,
        })
    n_passed = sum(1 for r in results if r["passed"])
    return {
        "run_dir":  str(run_dir),
        "results":  results,
        "n_passed": n_passed,
        "n_total":  len(results),
    }


# ── Formatting ────────────────────────────────────────────────────────────────

_PASS = "✓"
_FAIL = "✗"
_BAR  = "─" * 80


def format_verse_section(verse_ref: str, eval_result: dict, elapsed: float) -> str:
    lines = [
        f"\n{_BAR}",
        f"  {verse_ref}   ({elapsed:.1f}s)   "
        f"{eval_result['n_passed']}/{eval_result['n_total']} criteria passed",
        _BAR,
    ]
    for r in eval_result["results"]:
        mark = _PASS if r["passed"] else _FAIL
        lines.append(f"  {mark} {r['id']:3s} {r['label']:25s}  {r['detail']}")
    return "\n".join(lines)


def format_summary_table(verse_refs: list[str], evals: list[dict]) -> str:
    """ASCII table: rows = verses, columns = criteria."""
    criterion_ids = [c[0] for c in CRITERIA]
    col_w = 6
    header = "Verse           " + "".join(f"{cid:>{col_w}}" for cid in criterion_ids) + "  score"
    sep    = "─" * len(header)
    lines  = ["\n" + sep, header, sep]
    for ref, ev in zip(verse_refs, evals):
        row_label = ref.replace("Matthew ", "Mt ").ljust(16)
        cells = ""
        for r in ev["results"]:
            cells += (_PASS if r["passed"] else _FAIL).rjust(col_w)
        score = f"  {ev['n_passed']}/{ev['n_total']}"
        lines.append(row_label + cells + score)
    lines.append(sep)
    # Column totals
    totals_label = "PASS COUNT      "
    totals = ""
    for cid in criterion_ids:
        count = sum(1 for ev in evals
                    for r in ev["results"] if r["id"] == cid and r["passed"])
        totals += str(count).rjust(col_w)
    total_score = f"  {sum(ev['n_passed'] for ev in evals)}/{sum(ev['n_total'] for ev in evals)}"
    lines.append(totals_label + totals + total_score)
    lines.append(sep)
    return "\n".join(lines)


# ── Main ──────────────────────────────────────────────────────────────────────

def main() -> None:
    ap = argparse.ArgumentParser(
        description="10-verse quality harness for GGSD — Matthew 1:1 onwards"
    )
    ap.add_argument(
        "--model", default="claude-sonnet-5-5",
        help="Model ID (default: claude-sonnet-5-5)",
    )
    ap.add_argument(
        "--n-verses", type=int, default=10,
        metavar="N",
        help="Number of verses to run, starting from Matthew 1:1 (default: 10)",
    )
    ap.add_argument(
        "--morphgnt", default="",
        help="Path to MorphGNT Matthew file (default: tools/sblgnt/Matthew-morphgnt.txt)",
    )
    ap.add_argument(
        "--dry-run", action="store_true",
        help="Tokenise only — no model calls (structural criteria only)",
    )
    ap.add_argument(
        "--eval-only", default="",
        metavar="HARNESS_DIR",
        help="Skip running; evaluate an existing harness output directory",
    )
    args = ap.parse_args()

    morphgnt = args.morphgnt or str(GGSD_DIR / "tools" / "sblgnt" / "Matthew-morphgnt.txt")
    morphgnt_path = Path(morphgnt)
    if not morphgnt_path.exists():
        print(f"\nMorphGNT file not found: {morphgnt_path}")
        print("Run:  bash tools/download_morphgnt.sh")
        sys.exit(1)

    verses = build_verse_list(args.n_verses)

    # ── Harness output directory ───────────────────────────────────────────
    if args.eval_only:
        harness_dir = Path(args.eval_only).resolve()
        if not harness_dir.exists():
            sys.exit(f"--eval-only: directory not found: {harness_dir}")
        print(f"Eval-only mode: {harness_dir}")
    else:
        ts = datetime.datetime.now(datetime.UTC).strftime("%Y%m%dT%H%M%SZ")
        harness_dir = GGSD_DIR / "runs" / f"harness_matthew_10_{ts}"
        harness_dir.mkdir(parents=True, exist_ok=True)

    print(f"\nGGSD 10-verse harness")
    print(f"Model:    {args.model}")
    print(f"Verses:   {verses[0]} → {verses[-1]} ({len(verses)} total)")
    print(f"Dry-run:  {args.dry_run}")
    print(f"Output:   {harness_dir}")
    print(f"Criteria: {len(CRITERIA)}")
    print()

    # ── Run or locate each verse ───────────────────────────────────────────
    verse_run_dirs: list[Path] = []

    if args.eval_only:
        # Expect one sub-dir per verse named <slug>_<ts>
        import re as _re
        for verse_ref in verses:
            slug = _re.sub(r"[^a-zA-Z0-9]", "_", verse_ref)
            matches = sorted(harness_dir.glob(f"{slug}_*"))
            if not matches:
                print(f"  WARN: no run dir for {verse_ref} in {harness_dir}")
                verse_run_dirs.append(None)
            else:
                verse_run_dirs.append(matches[-1])  # latest
    else:
        for i, verse_ref in enumerate(verses, 1):
            print(f"[{i:2d}/{len(verses)}] Running {verse_ref} ...", flush=True)
            t0 = time.time()
            try:
                run_dir = ggsd_run(
                    verse_ref=verse_ref,
                    model_id=args.model,
                    dry_run=args.dry_run,
                    greek_override="",
                    morphgnt_path=morphgnt,
                    resume_dir="",
                )
                elapsed = time.time() - t0
                print(f"       done in {elapsed:.1f}s → {run_dir}", flush=True)
                verse_run_dirs.append(Path(run_dir))
            except Exception as exc:
                elapsed = time.time() - t0
                print(f"       ERROR after {elapsed:.1f}s: {exc}", flush=True)
                verse_run_dirs.append(None)

    # ── Evaluate each verse ────────────────────────────────────────────────
    print(f"\n{'═' * 80}")
    print("  EVALUATION")
    print(f"{'═' * 80}")

    evals: list[dict] = []
    verse_elapseds: list[float] = []  # not available in eval-only mode

    for verse_ref, run_dir in zip(verses, verse_run_dirs):
        if run_dir is None:
            # Build a fully-failed eval record
            ev = {
                "run_dir":  None,
                "results":  [
                    {"id": cid, "label": label, "passed": False, "detail": "run_dir missing"}
                    for cid, label, _ in CRITERIA
                ],
                "n_passed": 0,
                "n_total":  len(CRITERIA),
            }
        else:
            ev = evaluate_run(run_dir)
        evals.append(ev)
        # Per-verse output
        elapsed_str = ""  # elapsed not available in eval-only or after error
        section = format_verse_section(verse_ref, ev, 0.0)
        print(section)

    # ── Summary table ─────────────────────────────────────────────────────
    table = format_summary_table(verses, evals)
    print(table)

    total_passed = sum(ev["n_passed"] for ev in evals)
    total_possible = sum(ev["n_total"] for ev in evals)
    pct = total_passed / total_possible if total_possible else 0
    print(f"\nOverall: {total_passed}/{total_possible} criterion-passes ({pct:.0%})")

    # Identify failing criteria across all verses
    criterion_fail_counts: dict[str, int] = {c[0]: 0 for c in CRITERIA}
    for ev in evals:
        for r in ev["results"]:
            if not r["passed"]:
                criterion_fail_counts[r["id"]] += 1

    worst = sorted(criterion_fail_counts.items(), key=lambda x: -x[1])
    print("\nCriterion failure counts (worst first):")
    for cid, count in worst:
        label = next(c[1] for c in CRITERIA if c[0] == cid)
        bar = "█" * count + "░" * (len(verses) - count)
        print(f"  {cid:3s} {label:25s} {bar} {count}/{len(verses)}")

    # ── Write machine-readable summary ────────────────────────────────────
    summary = {
        "harness": "harness_matthew_10",
        "run_at":  datetime.datetime.now(datetime.UTC).isoformat() + "Z",
        "model":   args.model if not args.eval_only else "(eval-only)",
        "dry_run": args.dry_run,
        "verses":  verses,
        "n_verses": len(verses),
        "criteria": [{"id": c[0], "label": c[1]} for c in CRITERIA],
        "results":  [
            {
                "verse":    ref,
                "run_dir":  ev["run_dir"],
                "n_passed": ev["n_passed"],
                "n_total":  ev["n_total"],
                "criteria": ev["results"],
            }
            for ref, ev in zip(verses, evals)
        ],
        "totals": {
            "n_passed":   total_passed,
            "n_possible": total_possible,
            "pct":        round(pct, 4),
        },
        "criterion_fail_counts": criterion_fail_counts,
    }
    summary_json = harness_dir / "summary.json"
    summary_json.write_text(json.dumps(summary, indent=2, ensure_ascii=False))

    # Write markdown summary
    md_lines = [
        f"# GGSD Harness — Matthew 1:1–{verses[-1]}",
        f"",
        f"Run at: {summary['run_at']}  ",
        f"Model: `{summary['model']}`  ",
        f"Dry-run: {args.dry_run}  ",
        f"",
        "## Criterion Definitions",
        "",
    ]
    for cid, label, _ in CRITERIA:
        md_lines.append(f"- **{cid}** `{label}`")
    md_lines += ["", "## Results", "", "```", table, "```", ""]
    md_lines += ["## Criterion Failure Counts", ""]
    for cid, count in worst:
        label = next(c[1] for c in CRITERIA if c[0] == cid)
        md_lines.append(f"- **{cid}** `{label}`: {count}/{len(verses)} verses failed")
    md_lines += [
        "",
        f"## Overall",
        f"",
        f"**{total_passed}/{total_possible}** criterion-passes ({pct:.0%})",
    ]
    (harness_dir / "summary.md").write_text("\n".join(md_lines), encoding="utf-8")

    print(f"\nSummary written:")
    print(f"  {summary_json}")
    print(f"  {harness_dir / 'summary.md'}")
    print()

    # Exit code: 0 if all verses pass all criteria, 1 otherwise
    sys.exit(0 if total_passed == total_possible else 1)


if __name__ == "__main__":
    main()
