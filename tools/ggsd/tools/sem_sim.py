#!/usr/bin/env python3
"""
GGSD tool — semantic similarity via bge-m3.

Usage:
    python3 tools/sem_sim.py --terms "hand" "work" "throw" "worship"
    python3 tools/sem_sim.py --terms "hand" "work" "throw" "worship" \
                              --anchors "gardening" "agriculture" "stewardship"
    python3 tools/sem_sim.py --file terms.txt --anchors "growth" "harvest"

The tool measures semantic similarity between terms and (optionally) a set of
anchor concepts. It does not say what the terms mean. It says how close they
sit in the embedding space, using bge-m3 as the measure.

bge-m3 is multilingual and handles Greek, Hebrew transliterations, Arabic,
and English in one vector space. Model is downloaded to ~/.cache/huggingface
on first run and cached there.

This is a pointing tool. The pointing was done by the operator. The tool
measures whether the pointing holds in the embedding space. It does not invent
or rederive the pointing.

Output:
    - pairwise similarity matrix (terms × terms)
    - if anchors supplied: each term's similarity to each anchor
    - JSON lines written to stdout (--json) or readable table (default)
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


# ─── model loading ─────────────────────────────────────────────────────────────

_MODEL = None
MODEL_ID = "BAAI/bge-m3"


def _load_model():
    global _MODEL
    if _MODEL is None:
        try:
            from sentence_transformers import SentenceTransformer
        except ImportError:
            sys.exit(
                "sentence-transformers not installed.\n"
                "Run: .venv/bin/pip install sentence-transformers"
            )
        print(f"loading {MODEL_ID} …", file=sys.stderr)
        _MODEL = SentenceTransformer(MODEL_ID)
        print("model ready.", file=sys.stderr)
    return _MODEL


# ─── similarity ────────────────────────────────────────────────────────────────

def embed(texts: list[str]) -> "np.ndarray":
    import numpy as np
    model = _load_model()
    vecs = model.encode(texts, normalize_embeddings=True, show_progress_bar=False)
    return np.array(vecs)


def cosine_matrix(vecs: "np.ndarray") -> "np.ndarray":
    """Cosine similarity matrix. Vectors must already be L2-normalised."""
    import numpy as np
    return (vecs @ vecs.T).clip(-1.0, 1.0)


def cosine_pairs(vecs_a: "np.ndarray", vecs_b: "np.ndarray") -> "np.ndarray":
    """vecs_a [n, d] × vecs_b [m, d] → [n, m] similarity matrix."""
    return (vecs_a @ vecs_b.T).clip(-1.0, 1.0)


# ─── output ────────────────────────────────────────────────────────────────────

def _fmt(v: float) -> str:
    return f"{v:+.4f}"


def print_matrix(labels: list[str], mat: "np.ndarray") -> None:
    w = max(len(l) for l in labels) + 2
    header = " " * w + "  ".join(f"{l:>{w}}" for l in labels)
    print(header)
    for i, row_label in enumerate(labels):
        row = "  ".join(_fmt(mat[i, j]) for j in range(len(labels)))
        print(f"{row_label:<{w}}{row}")
    print()


def print_anchor_table(
    terms: list[str], anchors: list[str], mat: "np.ndarray"
) -> None:
    """mat is [len(terms), len(anchors)]"""
    w = max(len(l) for l in terms) + 2
    aw = max(len(a) for a in anchors) + 2
    header = " " * w + "  ".join(f"{a:>{aw}}" for a in anchors)
    print(header)
    for i, term in enumerate(terms):
        row = "  ".join(_fmt(mat[i, j]) for j in range(len(anchors)))
        print(f"{term:<{w}}{row}")
    print()


def emit_json(
    terms: list[str],
    term_mat: "np.ndarray",
    anchors: list[str],
    anchor_mat: "np.ndarray | None",
    meta: dict[str, Any],
) -> None:
    import numpy as np
    out: dict[str, Any] = {
        "meta": meta,
        "model": MODEL_ID,
        "terms": terms,
        "pairwise": [
            {"a": terms[i], "b": terms[j], "similarity": float(term_mat[i, j])}
            for i in range(len(terms))
            for j in range(i + 1, len(terms))
        ],
    }
    if anchors and anchor_mat is not None:
        out["anchors"] = anchors
        out["term_anchor"] = [
            {
                "term": terms[i],
                "anchor": anchors[j],
                "similarity": float(anchor_mat[i, j]),
            }
            for i in range(len(terms))
            for j in range(len(anchors))
        ]
    print(json.dumps(out, ensure_ascii=False, indent=2))


# ─── main ───────────────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Semantic similarity via bge-m3. "
            "Measures how close terms sit in the embedding space. "
            "Does not say what the terms mean."
        )
    )
    parser.add_argument(
        "--terms", nargs="+", metavar="TERM",
        help="Terms to compare with each other.",
    )
    parser.add_argument(
        "--anchors", nargs="*", metavar="ANCHOR", default=[],
        help="Anchor concepts. Each term's similarity to each anchor is reported.",
    )
    parser.add_argument(
        "--file", metavar="PATH",
        help="Text file with one term per line (used instead of --terms).",
    )
    parser.add_argument(
        "--json", action="store_true",
        help="Emit JSON instead of a readable table.",
    )
    parser.add_argument(
        "--note", default="",
        help="Optional note stored in JSON meta (e.g. the pointing being measured).",
    )
    args = parser.parse_args()

    # Collect terms
    terms: list[str] = []
    if args.file:
        terms = [l.strip() for l in Path(args.file).read_text().splitlines() if l.strip()]
    if args.terms:
        terms += args.terms
    terms = list(dict.fromkeys(terms))  # dedupe, preserve order

    if not terms:
        sys.exit("no terms supplied. Use --terms or --file.")

    anchors: list[str] = list(dict.fromkeys(args.anchors or []))

    # Embed
    all_texts = terms + anchors
    vecs = embed(all_texts)
    term_vecs = vecs[:len(terms)]
    anchor_vecs = vecs[len(terms):] if anchors else None

    term_mat = cosine_matrix(term_vecs)
    anchor_mat = cosine_pairs(term_vecs, anchor_vecs) if anchor_vecs is not None else None

    import datetime
    meta = {
        "timestamp": datetime.datetime.now(datetime.UTC).isoformat(),
        "model": MODEL_ID,
        "note": args.note,
    }

    if args.json:
        emit_json(terms, term_mat, anchors, anchor_mat, meta)
        return

    # Readable output
    print(f"\n=== semantic similarity ({MODEL_ID}) ===\n")
    if args.note:
        print(f"note: {args.note}\n")

    print("pairwise similarity (terms × terms):")
    print_matrix(terms, term_mat)

    if anchors and anchor_mat is not None:
        print("term → anchor similarity:")
        print_anchor_table(terms, anchors, anchor_mat)

    # Highest-similarity pair
    import numpy as np
    n = len(terms)
    if n >= 2:
        pairs = [
            (float(term_mat[i, j]), terms[i], terms[j])
            for i in range(n) for j in range(i + 1, n)
        ]
        pairs.sort(reverse=True)
        print("closest pair:", pairs[0][1], "↔", pairs[0][2], f"({_fmt(pairs[0][0])})")
        if anchors and anchor_mat is not None:
            flat = [
                (float(anchor_mat[i, j]), terms[i], anchors[j])
                for i in range(n) for j in range(len(anchors))
            ]
            flat.sort(reverse=True)
            print("closest term→anchor:", flat[0][1], "→", flat[0][2], f"({_fmt(flat[0][0])})")
        print()


if __name__ == "__main__":
    main()
