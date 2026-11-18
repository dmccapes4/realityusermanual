"""Stage 7: report scaffold + styled Transcript from transcript.jsonl (no LLM)."""

from __future__ import annotations

from typing import Any

from interlocutions import blocks_by_interlocution

PLACEHOLDERS = {
    "brief": "<!-- gpt4o:brief -->",
    "analysis": "<!-- gpt4o:analysis -->",
    "metacommentary": "<!-- gpt4o:metacommentary -->",
}


def label_for(author: str, voice: str) -> str:
    return f"{author} (interlocutor)" if voice == "interlocutor" else author


def format_message_md(row: dict[str, Any]) -> str:
    author = row.get("author") or "operator"
    text = (row.get("text") or "").strip()
    lines: list[str] = []
    ts = row.get("timestamp_raw") or ""
    if row.get("reply_to_visible_text"):
        lines.append(f"↩ replying to: “{row['reply_to_visible_text']}”\n")
    anchors = row.get("interlocutions") or []
    blocks = blocks_by_interlocution(text, anchors) if text else []
    if row.get("kind") == "link" and not blocks:
        title = row.get("link_title") or ""
        url = row.get("link_url") or ""
        blocks = [("author", f"[link] {title}\n{url}".strip())]
    for i, (voice, block) in enumerate(blocks):
        if not block.strip():
            continue
        head = f"**{label_for(author, voice)}**"
        if ts and i == 0:
            head += f" ({ts})"
        lines.append(f"{head}:\n\n{block.strip()}\n")
    if row.get("reaction_emoji"):
        lines.append(f"↳ {row['reaction_emoji']} from {row.get('reaction_reactor') or '?'}\n")
    if row.get("read_receipt"):
        lines.append(f"({row['read_receipt']})\n")
    return "\n".join(lines)


def format_transcript_md(messages: list[dict[str, Any]]) -> str:
    parts = [format_message_md(r) for r in messages if r.get("record_type") == "message"]
    return "\n".join(p for p in parts if p.strip()).strip() + "\n"


def scaffold_report(contact: dict[str, Any], run_meta: dict[str, Any], transcript_md: str, version: str) -> str:
    name = contact.get("contact_name") or "Contact"
    loc = contact.get("contact_locality")
    anchor = contact.get("thread_anchor") or {}
    anchor_txt = ""
    if anchor.get("raw"):
        anchor_txt = f" · **Anchor:** {anchor['raw']}"
        if anchor.get("timestamp_iso"):
            anchor_txt += f" → {anchor['timestamp_iso']}"
    who = f"{name} ({loc})" if loc else name
    return f"""# {name} — thread
**Processed:** {run_meta.get("capture_assumption_date", "")} · **Run:** {run_meta.get("run_id", "")} · **Tool:** imessage_thread v{version}  
**Source:** `{run_meta.get("images_dir", "")}` ({run_meta.get("image_count", "")} screenshots) · **Contact:** {who}{anchor_txt}  
**Artifacts:** [transcript.jsonl](./transcript.jsonl) · [attributed.jsonl](./attributed.jsonl) · [gpt41_pass1.json](./gpt41_pass1.json) · [gpt41_pass2.json](./gpt41_pass2.json)

## Brief

{PLACEHOLDERS["brief"]}

## Transcript

{transcript_md.strip()}

## Analysis

{PLACEHOLDERS["analysis"]}

## Metacommentary

{PLACEHOLDERS["metacommentary"]}
"""


def fill_report(report_md: str, sections: dict[str, str]) -> str:
    out = report_md
    for key, marker in PLACEHOLDERS.items():
        val = (sections.get(key) or "").strip()
        if val and marker in out:
            out = out.replace(marker, val)
    return out
