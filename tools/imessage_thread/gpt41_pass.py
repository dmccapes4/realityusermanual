"""Stages 5/6: one GPT-4.1 pass over the crops + message list → tool_calls applied once. No loop."""

from __future__ import annotations

import base64
import json
from pathlib import Path
from typing import Any

from openai_env import client
from thread_tools import TOOL_NAMES, apply_tool_calls, overlap_candidates

PASS_OUTPUT_SCHEMA = {
    "type": "object",
    "properties": {
        "pass": {"type": "integer", "enum": [1, 2]},
        "summary": {"type": "string"},
        "ok": {"type": "boolean"},
        "issues": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "type": {"type": "string"},
                    "msg_id": {"type": ["string", "null"]},
                    "image_index": {"type": ["integer", "null"]},
                    "evidence": {"type": "string"},
                },
                "required": ["type", "msg_id", "image_index", "evidence"],
                "additionalProperties": False,
            },
        },
        "tool_calls": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "tool": {"type": "string", "enum": TOOL_NAMES},
                    "msg_id": {"type": ["string", "null"]},
                    "msg_ids": {"type": ["array", "null"], "items": {"type": "string"}},
                    "after_msg_id": {"type": ["string", "null"]},
                    "author": {"type": ["string", "null"]},
                    "text": {"type": ["string", "null"]},
                    "reaction_emoji": {"type": ["string", "null"]},
                    "reaction_reactor": {"type": ["string", "null"]},
                    "reply_to_msg_id": {"type": ["string", "null"]},
                    "reply_to_visible_text": {"type": ["string", "null"]},
                    "timestamp_raw": {"type": ["string", "null"]},
                    "read_receipt": {"type": ["string", "null"]},
                    "link_title": {"type": ["string", "null"]},
                    "link_url": {"type": ["string", "null"]},
                    "source_image_index": {"type": ["integer", "null"]},
                    "reason": {"type": ["string", "null"]},
                },
                "required": [
                    "tool",
                    "msg_id",
                    "msg_ids",
                    "after_msg_id",
                    "author",
                    "text",
                    "reaction_emoji",
                    "reaction_reactor",
                    "reply_to_msg_id",
                    "reply_to_visible_text",
                    "timestamp_raw",
                    "read_receipt",
                    "link_title",
                    "link_url",
                    "source_image_index",
                    "reason",
                ],
                "additionalProperties": False,
            },
        },
    },
    "required": ["pass", "summary", "ok", "issues", "tool_calls"],
    "additionalProperties": False,
}

SYSTEM = """You are GPT-4.1 on pass {pass_number} of 2 for an iMessage thread reconstruction. There is no loop: you answer once, the Python system applies your tool_calls once{pass_tail}

You receive:
(a) every cropped screenshot in thread order, each labelled with its image_index;
(b) the current message list: msg_id, author, text, metadata, source_image_indices;
(c) frame_geometry: for each frame, the bubbles the system found by PIXEL COLOR (blue/gray fill, y-range, clipped_top/clipped_bottom) and which message each bubble feeds;
(d) overlap_candidates computed by code — hints only.

How the list was built: bubble outlines, author (blue = operator, gray = {contact}), tapback targets, date pills and read receipts were measured from pixels, not guessed. gpt-4.1-mini then read the text inside each bubble. Scroll overlap between consecutive frames was resolved by code: a bubble clipped at the bottom of frame k and the bubble clipped at the top of frame k+1 were joined into one message by word overlap, and whole bubbles repeated in the next frame were deduplicated. One blue bubble may span many frames (clipped top and bottom in every middle frame): that is ONE send.

Your job is verification against the pixels, in this priority:
1. TEXT FIDELITY. Compare every message to its bubble(s) in the frame(s) listed. Fix misread words, wrong punctuation, missing or duplicated words at a frame join, wraps emitted as newlines, or missing paragraph breaks with set_text (full corrected text). Text is verbatim: visual wraps joined with a space; "\\n\\n" only where the bubble shows a blank line; "\\n" only for a typed hard break (e.g. a '>' line). Keep *asterisks*, quotes, apostrophes and '?' exactly. Never paraphrase. Never correct the sender: typos, missing apostrophes, odd grammar and slang are the record ("Amazons" stays "Amazons" if that is what the bubble shows). The system rejects a set_text that removes a word both Tesseract and gpt-4.1-mini read from the pixels, or adds a word neither of them read, and logs the rejection. Whitespace and paragraph-break fixes are always accepted.
2. FRAME JOINS. Where a message spans frames, check the join: the end of the frame-k fragment and the start of the frame-k+1 fragment overlap in the images; the stitched text must read exactly as the bubble does, with no repeated or dropped line. Messages whose notes say "no word overlap" need special care.
3. METADATA. Tapback emoji (badge over the TOP corner of the reacted bubble → it belongs to the bubble BELOW the badge; gray badge = {contact} reacted), reply strips, date pills (belong only to the bubble directly under them), read receipts, link cards → set_meta if wrong.
4. STRUCTURE. Only if the pixel geometry is demonstrably wrong (cite the frame and y-range in issues): merge_messages for two items that are one bubble, set_text + insert_message to unfuse one item that is two bubbles, insert_message for a bubble with no message, delete_message for an item that is not a message, set_author for a bubble whose color was misjudged. Do not restructure on a hunch; the geometry was measured.

Emit every tool call you need in this one response; set ok=true only if, after your tool_calls run, the list matches the images. List remaining doubts in issues.
"""

PASS1_TAIL = ", then pass 2 sees the result with the images again and answers once."
PASS2_TAIL = ". You are the final pass: prior_pass contains pass 1's output and the tool execution log; the message list you see is the state after pass 1. Verify every message against its frame(s) and fix what remains. Do not repeat merges that already succeeded."


def _data_url(path: Path) -> str:
    ext = path.suffix.lower()
    mime = "image/png" if ext == ".png" else "image/jpeg"
    return f"data:{mime};base64,{base64.b64encode(path.read_bytes()).decode('ascii')}"


def run_gpt41_pass(
    model: str,
    pass_number: int,
    *,
    messages: list[dict[str, Any]],
    frames: list[dict[str, Any]],
    contact_slug: str,
    prior_pass: dict[str, Any] | None = None,
    frame_geometry: list[dict[str, Any]] | None = None,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    if pass_number not in (1, 2):
        raise ValueError("pass_number must be 1 or 2")

    payload: dict[str, Any] = {
        "pass": pass_number,
        "contact_slug": contact_slug,
        "messages": [{k: v for k, v in m.items() if k not in ("geometry", "ocr_hint")} for m in messages],
        "frame_geometry": frame_geometry or [],
        "overlap_candidates": overlap_candidates(messages),
        "tools": TOOL_NAMES,
    }
    if pass_number == 2 and prior_pass:
        payload["prior_pass"] = {
            "summary": prior_pass.get("summary"),
            "ok": prior_pass.get("ok"),
            "issues": prior_pass.get("issues"),
            "tool_calls": prior_pass.get("tool_calls"),
            "tool_execution_log": prior_pass.get("tool_execution_log"),
        }

    content: list[dict[str, Any]] = [{"type": "text", "text": json.dumps(payload, ensure_ascii=False)}]
    for fr in frames:
        content.append({"type": "text", "text": f"image_index={fr['image_index']} ({fr['filename']})"})
        content.append({"type": "image_url", "image_url": {"url": _data_url(Path(fr["crop_path"])), "detail": "high"}})

    system = SYSTEM.format(
        pass_number=pass_number,
        contact=contact_slug,
        pass_tail=PASS1_TAIL if pass_number == 1 else PASS2_TAIL,
    )
    resp = client().chat.completions.create(
        model=model,
        messages=[{"role": "system", "content": system}, {"role": "user", "content": content}],
        response_format={
            "type": "json_schema",
            "json_schema": {"name": "gpt41_pass", "strict": True, "schema": PASS_OUTPUT_SCHEMA},
        },
        max_tokens=16000,
        temperature=0,
        seed=7,
    )
    data = json.loads(resp.choices[0].message.content or "{}")
    data["pass"] = pass_number
    data["model"] = model
    usage = getattr(resp, "usage", None)
    if usage:
        data["usage"] = {"prompt_tokens": usage.prompt_tokens, "completion_tokens": usage.completion_tokens}

    new_messages, log = apply_tool_calls(messages, list(data.get("tool_calls") or []))
    data["tool_execution_log"] = log
    data["message_count_before"] = len(messages)
    data["message_count_after"] = len(new_messages)
    return new_messages, data
