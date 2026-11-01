"""
GrammaticalGeometrySpaceDriver — model call layer.

One model per run. The model id is configuration the operator supplies.
Temperature 0 when the interface allows it.
The model fills the schema. It may not eliminate. It may not choose a meaning.
It reports what the sources say, in the schema's fields.

Supported providers (detected from model_id prefix):
  claude-*      -> Anthropic (uses ANTHROPIC_API_KEY from .env)
  gpt-*         -> OpenAI    (uses OPENAI_API_KEY from .env)
"""

from __future__ import annotations

import json
import os
from typing import Any

SYSTEM_PROMPT = """\
You are a philological assistant for the GrammaticalGeometrySpaceDriver.

Your job is to fill a JSON primitive for one word in a verse.
You work from source retrievals already fetched and provided to you.
You do not add knowledge from memory unless it is clearly labelled as proposed.

RULES:
1. You may not eliminate any translation or interpretation.
   Eliminations require a consented rule set by the operator. You do not set consent.
2. You may not say what the verse means. You may list what it could mean (possible_interpretations).
3. Every rule you add must carry the source_id and a quotation from that source.
   If you cannot quote from the source, do not add the rule.
4. A rule you infer (not quoted) must have status "proposed". Only the operator sets "consented".
5. Do not add keys not present in the schema.
6. The word's letters are already in word.letters. Do not change them.
7. Do not spend the set. Keep all members that are not contradicted by a consented rule and a source quotation.
8. Translations from greekbible.com are stored as candidates. You may add them to the translations array.
   You do not choose which translation wins.

OUTPUT:
Return ONLY valid JSON matching the primitive schema below.
Do not add commentary outside the JSON.

SCHEMA (fill the empty fields; do not remove existing fields):
{
  "meta_data": {already filled},
  "verse": {already filled},
  "word": {surface and letters already filled},
  "description": "string — what this word is, from the sources. Do not interpret.",
  "grammatical_rules": [{"category":"grammatical","value":"...","source_id":"...","quotation":"...","status":"proposed","notes":"...","added_at":"..."}],
  "lexical_rules": [{"category":"lexical","value":"...","source_id":"...","quotation":"...","status":"proposed","notes":"...","added_at":"..."}],
  "semantic_rules": [{"category":"semantic","value":"...","source_id":"...","quotation":"...","status":"proposed","notes":"...","added_at":"..."}],
  "translations": [{"value":"...","source_id":"...","notes":"..."}],
  "possible_interpretations": [],
  "edges": []
}

Return the complete updated primitive as JSON.
"""


def _build_user_message(
    primitive: dict[str, Any],
    logeion_entries: dict[str, Any],
    greekbible_result: dict[str, Any],
    prior_words: list[dict[str, Any]],
) -> str:
    parts = [
        "=== PRIMITIVE TO FILL ===",
        json.dumps(primitive, ensure_ascii=False, indent=2),
        "",
        "=== LOGEION SOURCE RETRIEVALS ===",
    ]
    for sid, entry in logeion_entries.items():
        parts.append(f"-- {sid} --")
        parts.append(entry.get("entry_text", "[no text]")[:2000])

    parts += [
        "",
        "=== GREEKBIBLE.COM (verse context and translations) ===",
        f"Greek text: {greekbible_result.get('greek_text', '[not retrieved]')}",
        f"Translations stored as candidates:",
    ]
    for t in greekbible_result.get("translations", []):
        parts.append(f"  [{t.get('version','')}] {t.get('text','')}")

    if prior_words:
        parts += ["", "=== PRIOR WORDS IN THIS VERSE (for context only) ==="]
        for pw in prior_words:
            parts.append(
                f"  {pw['word']['surface']}: {pw.get('description','')[:120]}"
            )

    return "\n".join(parts)


def call_model(
    model_id: str,
    primitive: dict[str, Any],
    logeion_entries: dict[str, Any],
    greekbible_result: dict[str, Any],
    prior_words: list[dict[str, Any]],
) -> dict[str, Any]:
    """
    Call the model to fill the primitive.
    Returns the updated primitive dict.
    Raises on parse failure (caller decides whether to retry).
    """
    user_msg = _build_user_message(primitive, logeion_entries, greekbible_result, prior_words)

    if model_id.startswith("claude"):
        return _call_anthropic(model_id, user_msg)
    elif model_id.startswith("gpt") or model_id.startswith("o"):
        return _call_openai(model_id, user_msg)
    else:
        raise ValueError(f"Unknown model_id prefix: {model_id!r}. Expected claude-* or gpt-*.")


def _call_anthropic(model_id: str, user_msg: str) -> dict[str, Any]:
    import anthropic

    key = os.environ.get("ANTHROPIC_API_KEY", "")
    if not key:
        raise RuntimeError("ANTHROPIC_API_KEY not set")

    client = anthropic.Anthropic(api_key=key)
    response = client.messages.create(
        model=model_id,
        max_tokens=4096,
        temperature=0,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_msg}],
    )
    text = response.content[0].text.strip()
    return _parse_json_response(text)


def _call_openai(model_id: str, user_msg: str) -> dict[str, Any]:
    from openai import OpenAI

    key = os.environ.get("OPENAI_API_KEY", "")
    if not key:
        raise RuntimeError("OPENAI_API_KEY not set")

    client = OpenAI(api_key=key)
    response = client.chat.completions.create(
        model=model_id,
        temperature=0,
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_msg},
        ],
    )
    text = response.choices[0].message.content.strip()
    return _parse_json_response(text)


def _parse_json_response(text: str) -> dict[str, Any]:
    # Strip markdown fences if present
    if text.startswith("```"):
        lines = text.split("\n")
        text = "\n".join(lines[1:-1]) if lines[-1].strip() == "```" else "\n".join(lines[1:])
    try:
        return json.loads(text)
    except json.JSONDecodeError as e:
        raise ValueError(f"Model returned invalid JSON: {e}\n---\n{text[:500]}")
