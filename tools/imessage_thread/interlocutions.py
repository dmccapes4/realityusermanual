"""Detect pedagogical self-interlocution anchors in message text (no LLM)."""

from __future__ import annotations

import re
from typing import Any

# Answer voice openers after an interlocutor question (operator exposition).
_ANSWER_START = re.compile(
    r"^(?:It means|Much of|Price is|That['\u2019]s not|The safest|Supply and demand|Then\.|A rush of investment|Is that ok)",
    re.I,
)

_WH_QUESTION = re.compile(
    r"^(What|Why|Where|When|How|Are|Is|Do|Does|Did|Can|Could|Would|Should|Ok so|That['\u2019]s)\b",
    re.I,
)


def _content_tokens(s: str) -> set[str]:
    return {w.lower() for w in re.findall(r"[a-zA-Z']{4,}", s or "")}


def _responds_to_question(question: str, response: str) -> bool:
    """
    True when `response` is an operator answer to a pedagogical self-interlocution question.
    False when the question is likely addressed to the contact (dialog), not self-Q&A.
    """
    response = (response or "").strip()
    if not response:
        return False
    if response.startswith(">"):
        return True
    if _ANSWER_START.match(response):
        return True
    overlap = _content_tokens(question) & _content_tokens(response)
    if overlap:
        return True
    if len(response) > 80 and not response.endswith("?"):
        return True
    return False


def detect_interlocutions(text: str) -> list[dict[str, Any]]:
    """
    Return [{question, line}, ...] with 1-based line numbers into `text`.

    Pedagogical self-interlocution: interlocutor asks (probes); operator answers in the same send.
    Markers: `?\\n\\n` then a related answer, or `?\\n>` (answer line opens with `>`).
    A `?\\n\\n` followed by unrelated text is a normal dialog question, not an interlocution anchor.
    """
    text = text or ""
    lines = text.splitlines()
    out: list[dict[str, Any]] = []

    i = 0
    while i < len(lines):
        q = lines[i].strip()
        if not q or not q.endswith("?"):
            i += 1
            continue

        j = i + 1
        while j < len(lines) and not lines[j].strip():
            j += 1
        if j >= len(lines):
            i += 1
            continue

        nxt = lines[j].strip()
        blank_gap = j > i + 1

        if nxt.startswith(">"):
            out.append({"question": q, "line": i + 1})
            i += 1
            continue

        if blank_gap and _responds_to_question(q, nxt):
            out.append({"question": q, "line": i + 1})
            i += 1
            continue

        if not blank_gap:
            if nxt.startswith(">") or _responds_to_question(q, nxt):
                out.append({"question": q, "line": i + 1})

        i += 1

    return out


def blocks_by_interlocution(text: str, anchors: list[dict[str, Any]]) -> list[tuple[str, str]]:
    """
    (voice, block) pairs for report styling.
    voice interlocutor → operator (interlocutor) — the question / probe lines.
    voice author → operator — exposition and answers.
    """
    if not text.strip():
        return []
    if not anchors:
        return [("author", text.strip())]

    lines = text.splitlines()
    anchor_lines = sorted({int(a["line"]) for a in anchors if a.get("line")})
    blocks: list[tuple[str, str]] = []
    cursor = 0

    for pos, al in enumerate(anchor_lines):
        idx = al - 1
        if idx < 0 or idx >= len(lines):
            continue
        if idx > cursor:
            chunk = "\n".join(lines[cursor:idx]).strip()
            if chunk:
                blocks.append(("author", chunk))
        qline = lines[idx].strip()
        if qline:
            blocks.append(("interlocutor", qline))
        next_idx = len(lines)
        if pos + 1 < len(anchor_lines):
            next_idx = anchor_lines[pos + 1] - 1
        answer = "\n".join(lines[idx + 1 : next_idx]).strip()
        if answer:
            blocks.append(("author", answer))
        cursor = next_idx

    if cursor < len(lines):
        tail = "\n".join(lines[cursor:]).strip()
        if tail:
            blocks.append(("author", tail))

    merged: list[tuple[str, str]] = []
    for voice, block in blocks:
        if merged and merged[-1][0] == voice:
            merged[-1] = (voice, f"{merged[-1][1]}\n\n{block}".strip())
        else:
            merged.append((voice, block))
    return merged
