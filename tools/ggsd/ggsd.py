#!/usr/bin/env python3
"""
GrammaticalGeometrySpaceDriver v0.0.2

Usage:
    python3 ggsd.py --verse "Matthew 25:18" --model claude-sonnet-5-5
    python3 ggsd.py --verse "Matthew 25:18" --model ollama/dengcao/Qwen3-30B-A3B-Instruct-2507:Q4_K_M
    python3 ggsd.py --verse "Matthew 25:18" --model ollama/... --morphgnt tools/sblgnt/Matthew-morphgnt.txt
    python3 ggsd.py --verse "Matthew 25:18" --model ollama/... --resume runs/Matthew_25_18_20261103T...

Required env vars (in REALITY_USER_MANUAL/.env or the shell):
    ANTHROPIC_API_KEY   (for claude-* models)
    OPENAI_API_KEY      (for gpt-* models)
    OLLAMA_HOST         (for ollama/* models; default http://localhost:11434)

Output per run (in tools/ggsd/runs/<verse_slug>_<timestamp>/):
    verse.jsonl                     — one primitive per word, in verse order
    verse_log.jsonl                 — timestamped log of every model call (decode + questions)
    verse_grammatical_decoding.json — clean structured decoding (input to the questions)
    questions.jsonl                 — Q1 and Q2 with full context
    report.md                       — human-readable report
    run_meta.json                   — run metadata
"""

from __future__ import annotations

import argparse
import datetime
import json
import os
import re
import sys
import time
from pathlib import Path

# Load .env from REALITY_USER_MANUAL root (two levels up from this file)
_env_path = Path(__file__).resolve().parent.parent.parent / ".env"
if _env_path.exists():
    from dotenv import load_dotenv
    load_dotenv(_env_path)

from schema import (
    empty_primitive,
    validate_primitive,
    compute_agreements,
    SchemaError,
)
from sources import fetch_greekbible, fetch_all_for_word, load_morphgnt, morphgnt_verse_tokens
from model import call_model, call_question
from report import write_report


# ─── helpers ───────────────────────────────────────────────────────────────────

def _now_iso() -> str:
    return datetime.datetime.now(datetime.UTC).isoformat() + "Z"


def tokenise_greek(greek_text: str) -> list[str]:
    """
    Split Greek text into word tokens.
    Strips punctuation, preserves polytonic Unicode.
    Returns a list of surface forms in order.
    """
    cleaned = re.sub(r"[·,;\.·—\[\]()]", " ", greek_text)
    tokens = [t.strip() for t in cleaned.split() if t.strip()]
    return tokens


def _load_completed(jsonl_path: Path) -> dict[int, dict]:
    """
    Load already-completed word primitives from an existing verse.jsonl.
    Returns {word_index: primitive} for all lines that have a valid primitive.
    """
    completed: dict[int, dict] = {}
    if not jsonl_path.exists():
        return completed
    with jsonl_path.open(encoding="utf-8") as f:
        for i, line in enumerate(f):
            line = line.strip()
            if not line:
                continue
            try:
                p = json.loads(line)
                completed[i] = p
            except json.JSONDecodeError:
                pass
    return completed


def _log(log_fh, entry: dict) -> None:
    """Append one JSON line to verse_log.jsonl."""
    entry.setdefault("ts", _now_iso())
    log_fh.write(json.dumps(entry, ensure_ascii=False) + "\n")
    log_fh.flush()


def _build_decoding_json(verse_ref: str, model_id: str, primitives: list[dict]) -> dict:
    """Build the clean verse_grammatical_decoding.json structure."""
    words = []
    for p in primitives:
        words.append({
            "surface":                p.get("word", {}).get("surface", "?"),
            "description":            p.get("description", ""),
            "grammatical_rules":      p.get("grammatical_rules", []),
            "lexical_rules":          p.get("lexical_rules", []),
            "semantic_rules":         p.get("semantic_rules", []),
            "possible_interpretations": p.get("possible_interpretations", []),
            "translations":           p.get("translations", []),
            "edges":                  p.get("edges", []),
        })
    return {
        "verse_ref":   verse_ref,
        "model_id":    model_id,
        "decoded_at":  _now_iso(),
        "word_count":  len(primitives),
        "words":       words,
    }


# ─── run ───────────────────────────────────────────────────────────────────────

def run(
    verse_ref: str,
    model_id: str,
    dry_run: bool = False,
    greek_override: str = "",
    morphgnt_path: str = "",
    resume_dir: str = "",
) -> Path:

    # ── Provider check ──────────────────────────────────────────────────────
    if model_id.startswith("claude"):
        key = os.environ.get("ANTHROPIC_API_KEY", "")
        if not key:
            sys.exit("ANTHROPIC_API_KEY not found. Set it in REALITY_USER_MANUAL/.env.")
        print(f"ANTHROPIC_API_KEY: present ({len(key)} chars)")
    elif model_id.startswith("ollama/"):
        host = os.environ.get("OLLAMA_HOST", "http://localhost:11434")
        print(f"OLLAMA_HOST: {host}")
        print(f"Ollama model tag: {model_id[len('ollama/'):]}")
    elif model_id.startswith("gpt") or model_id.startswith("o"):
        key = os.environ.get("OPENAI_API_KEY", "")
        if not key:
            sys.exit("OPENAI_API_KEY not found. Set it in REALITY_USER_MANUAL/.env.")
        print(f"OPENAI_API_KEY: present ({len(key)} chars)")
    else:
        sys.exit(
            f"Unknown model_id: {model_id!r}. "
            f"Expected claude-*, gpt-*, or ollama/<tag>."
        )

    # ── Run directory ───────────────────────────────────────────────────────
    slug = re.sub(r"[^a-zA-Z0-9]", "_", verse_ref)
    if resume_dir:
        run_dir = Path(resume_dir).resolve()
        if not run_dir.exists():
            sys.exit(f"--resume: directory not found: {run_dir}")
        print(f"resuming: {run_dir}")
    else:
        ts = datetime.datetime.now(datetime.UTC).strftime("%Y%m%dT%H%M%SZ")
        run_dir = Path(__file__).resolve().parent / "runs" / f"{slug}_{ts}"
        run_dir.mkdir(parents=True, exist_ok=True)

    jsonl_path     = run_dir / "verse.jsonl"
    log_path       = run_dir / "verse_log.jsonl"
    decoding_path  = run_dir / "verse_grammatical_decoding.json"
    questions_path = run_dir / "questions.jsonl"
    report_path    = run_dir / "report.md"

    # ── Checkpoint: load any already-completed words ────────────────────────
    completed = _load_completed(jsonl_path)
    if completed:
        print(f"checkpoint: {len(completed)} word(s) already completed — resuming")

    run_meta = {
        "started_at":   _now_iso(),
        "verse_ref":    verse_ref,
        "model_id":     model_id,
        "driver_version": "0.0.2",
        "resumed":      bool(resume_dir),
    }

    print(f"verse:   {verse_ref}")
    print(f"model:   {model_id}")
    print(f"run dir: {run_dir}")
    print()

    # ── MorphGNT source ─────────────────────────────────────────────────────
    morphgnt_data: dict | None = None
    morphgnt_tokens: list[dict] = []

    if morphgnt_path:
        print(f"loading MorphGNT: {morphgnt_path}")
        try:
            morphgnt_data = load_morphgnt(morphgnt_path)
            # Parse chapter:verse from the reference
            m = re.search(r"(\d+):(\d+)", verse_ref)
            if m:
                ch, vs = int(m.group(1)), int(m.group(2))
                morphgnt_tokens = morphgnt_verse_tokens(morphgnt_data, ch, vs)
                print(f"  MorphGNT tokens for {ch}:{vs}: {len(morphgnt_tokens)}")
            else:
                print("  WARNING: could not parse chapter:verse from verse_ref; MorphGNT unused")
        except Exception as e:
            print(f"  WARNING: MorphGNT load failed ({e}); falling back to greekbible.com")
            morphgnt_data = None

    # ── Verse text source ────────────────────────────────────────────────────
    if morphgnt_tokens and not greek_override:
        greek_text = " ".join(w["word"] for w in morphgnt_tokens)
        print(f"  greek text: [MorphGNT] {greek_text[:120]}")
        greekbible_result = {
            "source_id": "morphgnt",
            "url": f"MorphGNT SBL GNT — {morphgnt_path}",
            "retrieved_at": _now_iso(),
            "verse_ref": verse_ref,
            "greek_text": greek_text,
            "translations": [],
            "raw_html_snippet": "",
        }
    elif greek_override.strip():
        greek_text = greek_override.strip()
        print(f"  greek text: [manual] {greek_text[:120]}")
        print("fetching verse from greekbible.com for translations …")
        greekbible_result = fetch_greekbible(verse_ref)
        greekbible_result["greek_text"] = greek_text
    else:
        print("fetching verse from greekbible.com …")
        greekbible_result = fetch_greekbible(verse_ref)
        greek_text = greekbible_result.get("greek_text", "")
        print(f"  greek text: {greek_text[:120] or '[not retrieved]'}")

    print(f"  translations found: {len(greekbible_result.get('translations', []))}")
    print()

    if not greek_text:
        print(
            "WARNING: no Greek text available. "
            "Supply with --greek or --morphgnt. "
            "Continuing with empty token list."
        )

    # ── Tokenise ─────────────────────────────────────────────────────────────
    if morphgnt_tokens and not greek_override:
        # Use MorphGNT word list.
        # word (field 4) is clean — no ⸀ apparatus markers or trailing punctuation.
        # text (field 3) is the as-printed form and may include ⸀ markers.
        surface_tokens = [w["word"] for w in morphgnt_tokens]
        lemma_hints    = [w["lemma"] for w in morphgnt_tokens]
    else:
        surface_tokens = tokenise_greek(greek_text)
        lemma_hints    = [None] * len(surface_tokens)

    print(f"tokens ({len(surface_tokens)}): {surface_tokens}")
    print()

    if dry_run:
        print("[dry-run] would process these tokens. Exiting.")
        return run_dir

    # ── Walk ─────────────────────────────────────────────────────────────────
    primitives: list[dict] = list(completed.values()) if completed else []

    with (
        jsonl_path.open("a", encoding="utf-8") as jf,
        log_path.open("a",   encoding="utf-8") as lf,
    ):
        for i, (surface, hint_lemma) in enumerate(zip(surface_tokens, lemma_hints)):
            if i in completed:
                print(f"[{i+1}/{len(surface_tokens)}] {surface}  [skip — already done]")
                continue

            print(f"[{i+1}/{len(surface_tokens)}] {surface}")

            # Build empty primitive
            p = empty_primitive(verse_ref, surface, model_id)

            # Store greekbible / MorphGNT retrieval
            p["source_retrievals"][greekbible_result["source_id"]] = {
                "source_id": greekbible_result["source_id"],
                "url":         greekbible_result["url"],
                "retrieved_at": greekbible_result["retrieved_at"],
                "note": "fetched once for the verse; shared across all word primitives",
            }
            p["meta_data"]["sources"].append(greekbible_result["source_id"])

            # Fetch Logeion (hint_lemma skips /find when MorphGNT is active)
            print(f"  fetching logeion for '{surface}' …")
            logeion_entries = fetch_all_for_word(surface, verse_ref, hint_lemma=hint_lemma)
            for sid, entry in logeion_entries.items():
                p["source_retrievals"][sid] = {
                    "source_id":    entry["source_id"],
                    "url":          entry["url"],
                    "retrieved_at": entry["retrieved_at"],
                    "entry_preview": entry.get("entry_text", "")[:300],
                }
                if entry["source_id"] not in p["meta_data"]["sources"]:
                    p["meta_data"]["sources"].append(entry["source_id"])
            print(f"  logeion entries: {list(logeion_entries.keys())}")

            # Call model
            print(f"  calling model …")
            t0 = time.time()
            try:
                filled = call_model(
                    model_id=model_id,
                    primitive=p,
                    logeion_entries=logeion_entries,
                    greekbible_result=greekbible_result,
                    prior_words=primitives,
                )
            except Exception as e:
                print(f"  ERROR from model: {e}")
                filled = p
                filled["description"] = f"[model error: {e}]"
            duration = time.time() - t0

            # Restore driver-managed fields (model must not overwrite these)
            filled["source_retrievals"] = p["source_retrievals"]
            filled["meta_data"]         = p["meta_data"]
            filled["word"]["surface"]   = surface
            filled["word"]["letters"]   = list(surface)

            filled["source_agreements"] = compute_agreements(filled)

            try:
                validate_primitive(filled)
            except SchemaError as e:
                print(f"  schema error: {e}")
                filled["_schema_error"] = str(e)

            primitives.append(filled)

            # Write to verse.jsonl
            jf.write(json.dumps(filled, ensure_ascii=False) + "\n")
            jf.flush()

            # Log to verse_log.jsonl immediately after the model call
            _log(lf, {
                "type":        "decode",
                "word_index":  i,
                "surface":     surface,
                "model_id":    model_id,
                "duration_s":  round(duration, 2),
                "n_rules":     (
                    len(filled.get("grammatical_rules", [])) +
                    len(filled.get("lexical_rules", [])) +
                    len(filled.get("semantic_rules", []))
                ),
                "n_interpretations": len(filled.get("possible_interpretations", [])),
                "n_translations": len(filled.get("translations", [])),
            })

            print(f"  done. translations: {len(filled.get('translations', []))}  "
                  f"({duration:.1f}s)")
            print()

    # ── verse_grammatical_decoding.json ──────────────────────────────────────
    decoding = _build_decoding_json(verse_ref, model_id, primitives)
    decoding_path.write_text(
        json.dumps(decoding, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(f"decoding written: {decoding_path}")

    # ── Post-decode questions ─────────────────────────────────────────────────
    QUESTIONS = [
        "What was taken?",
        "Is it moral?",
    ]

    qa_results: list[dict] = []

    with (
        log_path.open("a",       encoding="utf-8") as lf,
        questions_path.open("w", encoding="utf-8") as qf,
    ):
        prior_qa = None
        for q_num, question in enumerate(QUESTIONS, 1):
            print(f"\n[Q{q_num}] {question}")
            t0 = time.time()
            try:
                answer = call_question(
                    model_id=model_id,
                    verse_ref=verse_ref,
                    verse_decoding=decoding["words"],
                    question=question,
                    prior_qa=prior_qa,
                )
            except Exception as e:
                answer = f"[question error: {e}]"
                print(f"  ERROR: {e}")
            duration = time.time() - t0

            print(f"\n  {answer[:300]}{'…' if len(answer) > 300 else ''}")
            print(f"  ({duration:.1f}s)")

            entry = {
                "question_number": q_num,
                "question":        question,
                "answer":          answer,
                "model_id":        model_id,
                "verse_ref":       verse_ref,
                "duration_s":      round(duration, 2),
                "context_words":   len(decoding["words"]),
                "prior_qa":        prior_qa,
            }
            qa_results.append(entry)

            # Write to questions.jsonl
            qf.write(json.dumps(entry, ensure_ascii=False) + "\n")
            qf.flush()

            # Log to verse_log.jsonl
            _log(lf, {
                "type":       f"question_{q_num}",
                "question":   question,
                "answer":     answer,
                "model_id":   model_id,
                "duration_s": round(duration, 2),
            })

            # Q2 receives Q1's result as context
            prior_qa = {"question": question, "answer": answer}

    # ── Report ────────────────────────────────────────────────────────────────
    write_report(verse_ref, run_meta, primitives, report_path)

    # ── Run meta ──────────────────────────────────────────────────────────────
    run_meta["finished_at"] = _now_iso()
    run_meta["word_count"]  = len(primitives)
    run_meta["questions"]   = [
        {"q": e["question"], "answer_preview": e["answer"][:120]}
        for e in qa_results
    ]
    (run_dir / "run_meta.json").write_text(
        json.dumps(run_meta, indent=2, ensure_ascii=False), encoding="utf-8"
    )

    print(f"\ndone.")
    print(f"  verse.jsonl:       {jsonl_path}")
    print(f"  verse_log.jsonl:   {log_path}")
    print(f"  decoding.json:     {decoding_path}")
    print(f"  questions.jsonl:   {questions_path}")
    print(f"  report.md:         {report_path}")
    return run_dir


# ─── CLI ───────────────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(
        description="GrammaticalGeometrySpaceDriver — walk a verse, keep the measure."
    )
    parser.add_argument(
        "--verse", required=True,
        help='Verse reference, e.g. "Matthew 25:18"',
    )
    parser.add_argument(
        "--model", required=True,
        help="Model id, e.g. claude-sonnet-5-5 or ollama/dengcao/Qwen3-30B-A3B-Instruct-2507:Q4_K_M",
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Fetch/tokenise the verse then exit without calling the model.",
    )
    parser.add_argument(
        "--greek", default="",
        help=(
            "Supply the Greek text of the verse manually. "
            'Example: --greek "ὁ δὲ τὸ ἓν λαβὼν ἀπελθὼν ὤρυξεν γῆν καὶ ἔκρυψεν τὸ ἀργύριον τοῦ κυρίου αὐτοῦ"'
        ),
    )
    parser.add_argument(
        "--morphgnt", default="",
        help=(
            "Path to a MorphGNT file for this book "
            "(e.g. tools/sblgnt/Matthew-morphgnt.txt). "
            "When provided, supplies Greek text AND lemma hints — skips /find calls."
        ),
    )
    parser.add_argument(
        "--resume", default="",
        metavar="RUN_DIR",
        help="Resume an interrupted run. Supply the run directory path.",
    )
    args = parser.parse_args()

    run(
        verse_ref=args.verse,
        model_id=args.model,
        dry_run=args.dry_run,
        greek_override=args.greek,
        morphgnt_path=args.morphgnt,
        resume_dir=args.resume,
    )


if __name__ == "__main__":
    main()
