"""
GrammaticalGeometrySpaceDriver — model call layer.

One model per run. The model id is configuration the operator supplies.
Temperature 0 when the interface allows it.
The model fills the schema. It may not eliminate. It may not choose a meaning.
It reports what the sources say, in the schema's fields.

Supported providers (detected from model_id prefix):
  claude-*      -> Anthropic (uses ANTHROPIC_API_KEY from .env)
  gpt-*         -> OpenAI    (uses OPENAI_API_KEY from .env)
  ollama/*      -> local Ollama at OLLAMA_HOST (default http://localhost:11434)
                   e.g. ollama/dengcao/Qwen3-30B-A3B-Instruct-2507:Q4_K_M
                        ollama/llama3.1:70b-instruct-q4_K_M
"""

from __future__ import annotations

import json
import os
from typing import Any

SYSTEM_PROMPT = """\
You are a philological assistant for the GrammaticalGeometrySpaceDriver.

Your job is to fill the variable fields for one Greek word.
You work from source retrievals already fetched and provided to you.
You do not add knowledge from memory unless clearly labelled as proposed.

RULES:
1. You may not eliminate any translation or interpretation.
   Eliminations require a consented rule set by the operator. You do not set consent.
2. You may not say what the verse means. You may list what it could mean (possible_interpretations).
3. Every rule you add must carry the source_id and a quotation from that source.
   If you cannot quote from the source, do not add the rule.
4. A rule you infer (not quoted) must have status "proposed". Only the operator sets "consented".
5. Do not add keys not in the schema.
5a. You have not read any translation of this verse in any language. If you find yourself \
supplying a referent not present in the source retrievals (for example, inferring what a \
numeral refers to from context outside this verse), you must label it \
[inferred from training, not sourced] and place it in possible_interpretations only. \
Never promote a training prior to a grammatical or lexical rule.
6. Do not spend the set. Keep all members unless contradicted by a consented rule with a source quotation.
7. Translations from greekbible.com go in the translations array. You do not choose which wins.

OUTPUT:
Return ONLY a JSON object with EXACTLY these keys — nothing else, no commentary:

{
  "description": "string — what this word is, from the sources only. Do not interpret.",
  "grammatical_rules": [{"category":"grammatical","value":"...","source_id":"...","quotation":"...","status":"proposed","notes":"...","added_at":"..."}],
  "lexical_rules": [{"category":"lexical","value":"...","source_id":"...","quotation":"...","status":"proposed","notes":"...","added_at":"..."}],
  "semantic_rules": [{"category":"semantic","value":"...","source_id":"...","quotation":"...","status":"proposed","notes":"...","added_at":"..."}],
  "translations": [{"value":"...","source_id":"...","notes":"..."}],
  "possible_interpretations": [],
  "edges": []
}

Do NOT output meta_data, verse, or word — those are already filled. Output only the 7 keys above.
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
        # 400 chars per source: words with 13+ dictionaries were hitting the 8192-token
        # output cap. The key lexical data is in the first paragraph of each entry.
        parts.append(entry.get("entry_text", "[no text]")[:400])

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


FILLABLE_KEYS = [
    "description",
    "grammatical_rules",
    "lexical_rules",
    "semantic_rules",
    "translations",
    "possible_interpretations",
    "edges",
]


def call_model(
    model_id: str,
    primitive: dict[str, Any],
    logeion_entries: dict[str, Any],
    greekbible_result: dict[str, Any],
    prior_words: list[dict[str, Any]],
) -> dict[str, Any]:
    """
    Call the model to fill the variable fields of the primitive.
    The model returns only the 7 fillable keys; we merge them into the primitive here.
    Returns the updated primitive dict.
    Raises on parse failure (caller decides whether to retry).
    """
    user_msg = _build_user_message(primitive, logeion_entries, greekbible_result, prior_words)

    if model_id.startswith("claude"):
        partial = _call_anthropic(model_id, user_msg)
    elif model_id.startswith("ollama/"):
        # Check ollama/ BEFORE "o"-prefix OpenAI catch below
        partial = _call_ollama(model_id, user_msg)
    elif model_id.startswith("gpt") or model_id.startswith("o"):
        partial = _call_openai(model_id, user_msg)
        partial = _call_ollama(model_id, user_msg)
    else:
        raise ValueError(
            f"Unknown model_id prefix: {model_id!r}. "
            f"Expected claude-*, gpt-*, or ollama/<tag>."
        )

    # Merge only the fillable keys back into the full primitive
    result = dict(primitive)
    for key in FILLABLE_KEYS:
        if key in partial:
            result[key] = partial[key]
    return result


def _call_anthropic(model_id: str, user_msg: str) -> dict[str, Any]:
    import anthropic

    key = os.environ.get("ANTHROPIC_API_KEY", "")
    if not key:
        raise RuntimeError("ANTHROPIC_API_KEY not set")

    client = anthropic.Anthropic(api_key=key)
    response = client.messages.create(
        model=model_id,
        max_tokens=8192,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_msg}],
    )
    # Models with extended thinking return ThinkingBlock(s) before the TextBlock.
    # Find the first block that has a .text attribute.
    text = None
    for block in response.content:
        if hasattr(block, "text"):
            text = block.text.strip()
            break
    if text is None:
        raise ValueError(f"No text block in model response. Content: {response.content}")
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


def _call_ollama(model_id: str, user_msg: str) -> dict[str, Any]:
    """
    Call a local Ollama model.
    model_id format: 'ollama/<tag>'
    e.g. 'ollama/dengcao/Qwen3-30B-A3B-Instruct-2507:Q4_K_M'

    OLLAMA_HOST env var overrides default http://localhost:11434.
    Use for remote hilarious_marcupial: set OLLAMA_HOST=http://192.168.0.245:11434
    """
    import urllib.request

    tag = model_id[len("ollama/"):]   # strip 'ollama/' prefix
    host = os.environ.get("OLLAMA_HOST", "http://localhost:11434").rstrip("/")

    # Qwen3 models default to thinking mode. Prepend /no_think to disable the
    # <think>...</think> reasoning block, which would precede the JSON output
    # and waste tokens. The JSON stripping below is a fallback if this is ignored.
    is_qwen3 = "qwen3" in tag.lower() or "qwen3" in tag.lower()
    if is_qwen3:
        user_msg = "/no_think\n" + user_msg

    payload = {
        "model": tag,
        "stream": False,
        "options": {
            "temperature": 0,
            "top_p": 1,
            "repeat_penalty": 1.0,
            "num_predict": 8192,  # generous cap; 4096 was truncating κυρίου/καὶ
        },
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user",   "content": user_msg},
        ],
        "format": "json",   # Ollama's JSON-mode constraint
    }

    data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(
        f"{host}/api/chat",
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    # Generous timeout: 70B on CPU split needs ~3 min for 500 tokens
    with urllib.request.urlopen(req, timeout=600) as resp:
        result = json.loads(resp.read())

    text = result["message"]["content"].strip()
    return _parse_json_response(text)


def _parse_json_response(text: str) -> dict[str, Any]:
    # Strip Qwen3 <think>...</think> reasoning blocks before the JSON
    import re as _re
    text = _re.sub(r"<think>.*?</think>", "", text, flags=_re.DOTALL).strip()

    # Strip markdown fences if present
    if text.startswith("```"):
        lines = text.split("\n")
        # Drop the opening fence line and any closing fence
        inner = lines[1:]
        if inner and inner[-1].strip().startswith("```"):
            inner = inner[:-1]
        text = "\n".join(inner)

    # Try direct parse first
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    # Model may have appended prose after the closing brace.
    # Extract the outermost {...} by brace-matching.
    start = text.find("{")
    if start == -1:
        raise ValueError(f"No JSON object found in model response:\n{text[:500]}")
    depth = 0
    in_string = False
    escape = False
    for i, ch in enumerate(text[start:], start=start):
        if escape:
            escape = False
            continue
        if ch == "\\" and in_string:
            escape = True
            continue
        if ch == '"':
            in_string = not in_string
            continue
        if in_string:
            continue
        if ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                candidate = text[start : i + 1]
                try:
                    return json.loads(candidate)
                except json.JSONDecodeError as e:
                    raise ValueError(
                        f"Model returned invalid JSON: {e}\n---\n{candidate[:500]}"
                    )
    raise ValueError(f"Unbalanced braces in model response:\n{text[:500]}")


# ─── Post-decode questions ────────────────────────────────────────────────────
# After a verse is fully decoded, the driver asks two sequential questions.
# These use a different system prompt: the model is allowed to answer, to choose,
# to reflect. The no-elimination / no-choosing rules do not apply here.
# The full verse_grammatical_decoding is passed as context for both questions.
# Question 2 also receives Question 1 and its answer.

QUESTION_SYSTEM_PROMPT = """\
You are reading a verse decoded word by word from original Greek Koine.
Each word entry contains what the sources say: grammatical rules, lexical rules,
semantic rules, and possible interpretations. No interpretation has been eliminated.
No meaning has been selected — until now.

You are answering a question about this verse. Answer from the decoded set.
You may draw on any of the possible interpretations. If the decoding does not
settle the question, say so directly.

If you add an inference not supported by the decoding, label it [inference]
and keep it separate from what the sources support.

Be direct. One or two paragraphs. Do not summarise the decoding back at the reader.
Answer the question.
"""


def _build_question_message(
    verse_ref: str,
    verse_decoding: list[dict[str, Any]],
    question: str,
    prior_qa: dict[str, str] | None,
) -> str:
    """Build the user message for a question call."""
    lines = [f"VERSE: {verse_ref}", ""]
    for w in verse_decoding:
        surface = w.get("word", {}).get("surface", "?")
        desc    = (w.get("description") or "")[:200]
        interps = w.get("possible_interpretations") or []
        lex     = w.get("lexical_rules") or []
        lines.append(f"  {surface}: {desc}")
        for r in lex[:4]:
            lines.append(f"    lex: {r.get('value','')[:80]}")
        for p in interps[:3]:
            lines.append(f"    interpretation: {str(p)[:120]}")
    if prior_qa:
        lines += [
            "",
            f"PRIOR QUESTION: {prior_qa['question']}",
            f"PRIOR ANSWER:",
            prior_qa["answer"],
        ]
    lines += ["", f"QUESTION: {question}"]
    return "\n".join(lines)


def call_question(
    model_id: str,
    verse_ref: str,
    verse_decoding: list[dict[str, Any]],
    question: str,
    prior_qa: dict[str, str] | None = None,
) -> str:
    """
    Ask a question about a fully decoded verse. Returns a plain-text answer.

    verse_decoding: list of word primitives from the full run.
    prior_qa: {"question": str, "answer": str} — for Q2, pass Q1's result here.
    """
    user_msg = _build_question_message(verse_ref, verse_decoding, question, prior_qa)

    if model_id.startswith("claude"):
        return _call_question_anthropic(model_id, user_msg)
    elif model_id.startswith("ollama/"):
        return _call_question_ollama(model_id, user_msg)
    elif model_id.startswith("gpt") or model_id.startswith("o"):
        return _call_question_openai(model_id, user_msg)
    else:
        raise ValueError(f"Unknown model_id: {model_id!r}")


def _call_question_anthropic(model_id: str, user_msg: str) -> str:
    import anthropic
    key = os.environ.get("ANTHROPIC_API_KEY", "")
    if not key:
        raise RuntimeError("ANTHROPIC_API_KEY not set")
    client = anthropic.Anthropic(api_key=key)
    response = client.messages.create(
        model=model_id,
        max_tokens=1024,
        system=QUESTION_SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_msg}],
    )
    for block in response.content:
        if hasattr(block, "text"):
            return block.text.strip()
    raise ValueError("No text block in question response")


def _call_question_openai(model_id: str, user_msg: str) -> str:
    from openai import OpenAI
    key = os.environ.get("OPENAI_API_KEY", "")
    if not key:
        raise RuntimeError("OPENAI_API_KEY not set")
    client = OpenAI(api_key=key)
    response = client.chat.completions.create(
        model=model_id,
        temperature=0,
        messages=[
            {"role": "system", "content": QUESTION_SYSTEM_PROMPT},
            {"role": "user",   "content": user_msg},
        ],
    )
    return response.choices[0].message.content.strip()


def _call_question_ollama(model_id: str, user_msg: str) -> str:
    import urllib.request as _urllib
    tag  = model_id[len("ollama/"):]
    host = os.environ.get("OLLAMA_HOST", "http://localhost:11434").rstrip("/")

    is_qwen3 = "qwen3" in tag.lower()
    if is_qwen3:
        user_msg = "/no_think\n" + user_msg

    payload = {
        "model": tag,
        "stream": False,
        "options": {"temperature": 0, "num_predict": 1024},
        "messages": [
            {"role": "system", "content": QUESTION_SYSTEM_PROMPT},
            {"role": "user",   "content": user_msg},
        ],
        # No "format": "json" — questions return free prose
    }
    data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    req  = _urllib.Request(
        f"{host}/api/chat",
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with _urllib.urlopen(req, timeout=120) as resp:
        result = json.loads(resp.read())
    text = result["message"]["content"].strip()
    import re as _re
    text = _re.sub(r"<think>.*?</think>", "", text, flags=_re.DOTALL).strip()
    return text
