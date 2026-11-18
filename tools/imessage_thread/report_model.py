"""Stage 8: gpt-4o writes Brief, Analysis, Metacommentary. Transcript is never touched."""

from __future__ import annotations

import json
from typing import Any

from openai_env import client

REPORT_SCHEMA = {
    "type": "object",
    "properties": {
        "brief": {"type": "string"},
        "analysis": {"type": "string"},
        "metacommentary": {"type": "string"},
    },
    "required": ["brief", "analysis", "metacommentary"],
    "additionalProperties": False,
}

SYSTEM = """You write three markdown sections for a report on a reconstructed iMessage thread. The Transcript section already exists verbatim in the report; do not quote it at length, summarize it, or rewrite any message.

Participants: `operator` (the phone owner, blue bubbles) and the contact slug given in contact.json (gray bubbles). Always say "operator", never "self" or "user".

brief — an abstract of the conversation: who, when (use thread_anchor and timestamps), what was asked, what was argued, how it ended. 4–8 sentences, neutral.

analysis — TECHNICAL ONLY. The claims as stated in-thread (e.g. valuation, cash flow, cap-ex, policy, petroleum, infrastructure cycles), the structure of the argument, where the operator uses pedagogical self-interlocution (question lines answered in the same send), and what the contact's replies do or do not engage. No hot takes, no advice.

metacommentary — AGENT OPINION, clearly separate from analysis: how much to trust this reconstruction (screenshots → crops → OCR hint → vision attribution → two GPT-4.1 passes), where ambiguity remains, and your reading of the exchange's tone and dynamics."""


def run_report(contact: dict[str, Any], run_meta: dict[str, Any], transcript: list[dict[str, Any]], model: str) -> dict[str, str]:
    bundle = {
        "contact": contact,
        "run_meta": {k: v for k, v in run_meta.items() if not k.endswith("_committed_at")},
        "transcript": [
            {
                "message_id": r.get("message_id"),
                "author": r.get("author"),
                "timestamp_raw": r.get("timestamp_raw"),
                "timestamp_iso": r.get("timestamp_iso"),
                "text": r.get("text"),
                "interlocutions": r.get("interlocutions"),
                "reaction_emoji": r.get("reaction_emoji"),
                "reaction_reactor": r.get("reaction_reactor"),
                "reply_to_visible_text": r.get("reply_to_visible_text"),
                "read_receipt": r.get("read_receipt"),
            }
            for r in transcript
        ],
    }
    resp = client().chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": SYSTEM},
            {"role": "user", "content": json.dumps(bundle, ensure_ascii=False)[:150000]},
        ],
        response_format={
            "type": "json_schema",
            "json_schema": {"name": "imessage_report", "strict": True, "schema": REPORT_SCHEMA},
        },
        max_tokens=6000,
        temperature=0.3,
        seed=7,
    )
    raw = resp.choices[0].message.content
    if not raw:
        raise RuntimeError("empty report model response")
    return json.loads(raw)
