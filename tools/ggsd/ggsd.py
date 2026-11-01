#!/usr/bin/env python3
"""
GrammaticalGeometrySpaceDriver v0.0.1

Usage:
    python3 ggsd.py --verse "Matthew 25:18" --model claude-3-5-sonnet-20241022

Required env vars (in REALITY_USER_MANUAL/.env):
    ANTHROPIC_API_KEY   (for claude-* models)
    OPENAI_API_KEY      (for gpt-* models)

Output:
    tools/ggsd/runs/<verse_slug>_<timestamp>/
        verse.jsonl      — one primitive per word, in verse order
        report.md        — the report

The driver will not start if model_id is not set.
The driver will not start if no API key is found for the model provider.
"""

from __future__ import annotations

import argparse
import datetime
import json
import os
import re
import sys
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
from sources import fetch_greekbible, fetch_all_for_word
from model import call_model
from report import write_report


# ─── verse tokeniser ───────────────────────────────────────────────────────────

def tokenise_greek(greek_text: str) -> list[str]:
    """
    Split Greek text into word tokens.
    Strips punctuation, preserves polytonic Unicode.
    Returns a list of surface forms in order.
    """
    # Remove punctuation except Greek-range characters and spaces
    cleaned = re.sub(r"[·,;\.·—\[\]()]", " ", greek_text)
    tokens = [t.strip() for t in cleaned.split() if t.strip()]
    return tokens


# ─── run ───────────────────────────────────────────────────────────────────────

def run(verse_ref: str, model_id: str, dry_run: bool = False, greek_override: str = "") -> Path:
    # Verify key presence (length only)
    if model_id.startswith("claude"):
        key = os.environ.get("ANTHROPIC_API_KEY", "")
        if not key:
            sys.exit("ANTHROPIC_API_KEY not found. Set it in REALITY_USER_MANUAL/.env.")
        print(f"ANTHROPIC_API_KEY: present ({len(key)} chars)")
    elif model_id.startswith("gpt") or model_id.startswith("o"):
        key = os.environ.get("OPENAI_API_KEY", "")
        if not key:
            sys.exit("OPENAI_API_KEY not found. Set it in REALITY_USER_MANUAL/.env.")
        print(f"OPENAI_API_KEY: present ({len(key)} chars)")
    else:
        sys.exit(f"Unknown model_id: {model_id!r}. Expected claude-* or gpt-*.")

    # Output directory
    slug = re.sub(r"[^a-zA-Z0-9]", "_", verse_ref)
    ts = datetime.datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    run_dir = Path(__file__).resolve().parent / "runs" / f"{slug}_{ts}"
    run_dir.mkdir(parents=True, exist_ok=True)

    jsonl_path = run_dir / "verse.jsonl"
    report_path = run_dir / "report.md"

    run_meta = {
        "started_at": datetime.datetime.utcnow().isoformat() + "Z",
        "verse_ref": verse_ref,
        "model_id": model_id,
        "driver_version": "0.0.1",
    }

    print(f"verse:   {verse_ref}")
    print(f"model:   {model_id}")
    print(f"run dir: {run_dir}")
    print()

    # Fetch the verse from greekbible.com (once per verse)
    print("fetching verse from greekbible.com …")
    greekbible_result = fetch_greekbible(verse_ref)
    greek_text = greek_override.strip() or greekbible_result.get("greek_text", "")
    if greek_override.strip():
        print(f"  greek text: [supplied manually] {greek_text[:120]}")
    else:
        print(f"  greek text: {greek_text[:120] or '[not retrieved]'}")
    print(f"  translations found: {len(greekbible_result.get('translations', []))}")
    print()

    if not greek_text:
        print(
            "WARNING: greekbible.com returned no Greek text. "
            "The verse text may need to be supplied manually. "
            "Continuing with empty token list — add words with --word if needed."
        )

    tokens = tokenise_greek(greek_text)
    print(f"tokens ({len(tokens)}): {tokens}")
    print()

    if dry_run:
        print("[dry-run] would process these tokens. Exiting.")
        return run_dir

    # Walk
    primitives: list[dict] = []
    with jsonl_path.open("w", encoding="utf-8") as jf:
        for i, surface in enumerate(tokens):
            print(f"[{i+1}/{len(tokens)}] {surface}")

            # Build empty primitive
            p = empty_primitive(verse_ref, surface, model_id)

            # Store greekbible retrieval in primitive
            p["source_retrievals"][greekbible_result["source_id"]] = {
                "source_id": greekbible_result["source_id"],
                "url": greekbible_result["url"],
                "retrieved_at": greekbible_result["retrieved_at"],
                "note": "fetched once for the verse; shared across all word primitives",
            }
            p["meta_data"]["sources"].append(greekbible_result["source_id"])

            # Fetch Logeion for this word
            print(f"  fetching logeion for '{surface}' …")
            logeion_entries = fetch_all_for_word(surface, verse_ref)
            for sid, entry in logeion_entries.items():
                p["source_retrievals"][sid] = {
                    "source_id": entry["source_id"],
                    "url": entry["url"],
                    "retrieved_at": entry["retrieved_at"],
                    "entry_preview": entry.get("entry_text", "")[:300],
                }
                if entry["source_id"] not in p["meta_data"]["sources"]:
                    p["meta_data"]["sources"].append(entry["source_id"])
            print(f"  logeion entries: {list(logeion_entries.keys())}")

            # Call model
            print(f"  calling model …")
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

            # Merge model output back: keep source_retrievals the driver set
            filled["source_retrievals"] = p["source_retrievals"]
            filled["meta_data"] = p["meta_data"]
            filled["word"]["surface"] = surface
            filled["word"]["letters"] = list(surface)

            # Compute source agreements
            filled["source_agreements"] = compute_agreements(filled)

            # Validate
            try:
                validate_primitive(filled)
            except SchemaError as e:
                print(f"  schema error: {e} — storing raw with error note")
                filled["_schema_error"] = str(e)

            primitives.append(filled)
            jf.write(json.dumps(filled, ensure_ascii=False) + "\n")
            print(f"  done. translations: {len(filled.get('translations', []))}")
            print()

    # Report
    write_report(verse_ref, run_meta, primitives, report_path)

    # Run meta
    run_meta["finished_at"] = datetime.datetime.utcnow().isoformat() + "Z"
    run_meta["word_count"] = len(primitives)
    (run_dir / "run_meta.json").write_text(
        json.dumps(run_meta, indent=2, ensure_ascii=False), encoding="utf-8"
    )

    print(f"\ndone.")
    print(f"  JSONL:  {jsonl_path}")
    print(f"  report: {report_path}")
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
        help="Model id, e.g. claude-3-5-sonnet-20241022 or gpt-4.1",
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Fetch the verse and tokenise, then exit without calling the model.",
    )
    parser.add_argument(
        "--greek", default="",
        help=(
            "Supply the Greek text of the verse manually when the web scraper "
            "cannot retrieve it (e.g. greekbible.com requires JS). "
            "Example: --greek \"ὁ δὲ τὸ ἓν λαβὼν ἀπελθὼν ὤρυξεν γῆν καὶ ἔκρυψεν τὸ ἀργύριον τοῦ κυρίου αὐτοῦ\""
        ),
    )
    args = parser.parse_args()

    if not args.model:
        sys.exit("--model is required. The driver will not start without a model id.")

    run(verse_ref=args.verse, model_id=args.model, dry_run=args.dry_run, greek_override=args.greek)


if __name__ == "__main__":
    main()
