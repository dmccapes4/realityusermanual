"""
GrammaticalGeometrySpaceDriver — report writer.

The report lists:
  - the kernel (verse reference, run metadata)
  - the retrievals (sources read, URLs, timestamps)
  - the source agreements (where dictionaries converge)
  - the set that remains (translations and interpretations not eliminated)
  - what remains open (members not yet resolved)

The report does not say what the verse means while more than one member remains.
The report does not call the operator an immoral liar.
The report does not apply [his] unless explicitly requested.
The report does not apply [measured] without naming the measure.
"""

from __future__ import annotations

import datetime
import json
from pathlib import Path
from typing import Any


def write_report(
    verse_ref: str,
    run_meta: dict[str, Any],
    primitives: list[dict[str, Any]],
    output_path: Path,
) -> None:
    """Write the report markdown beside the JSONL."""
    lines = [
        f"# GGSD Report — {verse_ref}",
        "",
        f"**Run date:** {run_meta.get('started_at', '?')}",
        f"**Model:** {run_meta.get('model_id', '?')}",
        f"**Verse:** {verse_ref}",
        "",
        "---",
        "",
        "## Kernel",
        "",
        f"- Verse reference: `{verse_ref}`",
        f"- Word count: {len(primitives)}",
        f"- JSONL: `{output_path.stem}.jsonl`",
        "",
    ]

    # Sources retrieved
    lines += ["## Sources retrieved", ""]
    all_sources: dict[str, list[str]] = {}  # source_id -> urls
    for p in primitives:
        for sid, entry in p.get("source_retrievals", {}).items():
            all_sources.setdefault(sid, [])
            url = entry.get("url", "")
            if url not in all_sources[sid]:
                all_sources[sid].append(url)

    if all_sources:
        for sid, urls in sorted(all_sources.items()):
            lines.append(f"- **{sid}**")
            for u in urls:
                lines.append(f"  - {u}")
    else:
        lines.append("- No sources retrieved (check retrieval logs).")
    lines.append("")

    # Source agreements
    lines += ["## Source agreements", ""]
    any_agreement = False
    for p in primitives:
        word = p["word"]["surface"]
        agreements = [a for a in p.get("source_agreements", []) if a.get("agreement")]
        if agreements:
            any_agreement = True
            lines.append(f"**{word}**")
            for a in agreements:
                sids = ", ".join(a["source_ids"])
                lines.append(f"  - `{a['field']}` → `{a['value']}` [{sids}]")
            lines.append("")

    if not any_agreement:
        lines.append("No multi-source agreements recorded in this run.")
        lines.append("")

    # Per-word: the set that remains
    lines += ["## The set (per word)", ""]
    for p in primitives:
        word = p["word"]["surface"]
        lines.append(f"### {word}")
        lines.append("")
        desc = p.get("description", "").strip()
        if desc:
            lines.append(desc)
            lines.append("")

        # Translations that remain (not eliminated)
        eliminated = {e["translation"] for e in p.get("eliminations", [])}
        translations = p.get("translations", [])
        standing = [
            t for t in translations
            if (t if isinstance(t, str) else t.get("value", "")) not in eliminated
        ]
        if standing:
            lines.append("**Translations standing:**")
            for t in standing:
                val = t if isinstance(t, str) else t.get("value", "")
                sid = "" if isinstance(t, str) else t.get("source_id", "")
                lines.append(f"  - {val}" + (f" ({sid})" if sid else ""))
        else:
            lines.append("*No translations recorded yet.*")

        if eliminated:
            lines.append("")
            lines.append("**Eliminated (rule-consented):**")
            for e in p.get("eliminations", []):
                lines.append(f"  - {e['translation']} — rule `{e['rule_id']}`")

        # Possible interpretations
        interps = p.get("possible_interpretations", [])
        if interps:
            lines.append("")
            lines.append("**Possible interpretations (set — not a choice):**")
            for i in interps:
                val = i if isinstance(i, str) else i.get("value", str(i))
                lines.append(f"  - {val}")

        lines.append("")

    # What remains open
    lines += ["## What remains open", ""]
    open_words = []
    for p in primitives:
        eliminated = {e["translation"] for e in p.get("eliminations", [])}
        translations = p.get("translations", [])
        standing = [
            t for t in translations
            if (t if isinstance(t, str) else t.get("value", "")) not in eliminated
        ]
        if len(standing) > 1:
            open_words.append(p["word"]["surface"])

    if open_words:
        lines.append(
            "The following words have more than one translation standing. "
            "The verse does not yet mean one thing. The set is open."
        )
        lines.append("")
        for w in open_words:
            lines.append(f"- {w}")
    elif primitives:
        lines.append(
            "Every word has one translation standing. "
            "If every elimination was made by a consented rule with a source quotation, "
            "the verse resolves to that reading. Check the eliminations."
        )
    else:
        lines.append("No words processed.")

    lines += [
        "",
        "---",
        "",
        f"*Generated by GrammaticalGeometrySpaceDriver v0.0.1 — "
        f"{datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}*",
    ]

    output_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"report written: {output_path}")
