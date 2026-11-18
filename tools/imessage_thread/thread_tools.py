"""Message state + deterministic tools for the two GPT-4.1 passes. Tools do not know which pass called them."""

from __future__ import annotations

import re
from typing import Any

TOOL_NAMES = [
    "merge_messages",
    "set_text",
    "set_author",
    "set_meta",
    "delete_message",
    "insert_message",
]

META_FIELDS = (
    "reaction_emoji",
    "reaction_reactor",
    "reply_to_msg_id",
    "reply_to_visible_text",
    "timestamp_raw",
    "read_receipt",
    "link_title",
    "link_url",
)


# --------------------------------------------------------------------------- state


def msg_id_for(image_index: int, local_seq: int) -> str:
    return f"m{int(image_index):02d}_{int(local_seq):02d}"


def messages_from_attributed(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Initial message list: one per text/link item; system pills fold into the next item's timestamp_raw."""
    rows = sorted(rows, key=lambda r: (int(r.get("image_index") or 0), int(r.get("local_seq") or 0)))
    out: list[dict[str, Any]] = []
    pending_pill: str | None = None
    last_pill: str | None = None
    for r in rows:
        kind = r.get("kind") or "text"
        if kind == "system" or (r.get("author") == "system"):
            pending_pill = (r.get("text") or "").strip() or pending_pill
            last_pill = pending_pill
            continue
        ts = (r.get("timestamp_raw") or "").strip() or None
        rr = r.get("read_receipt")
        if ts and re.match(r"^(Read|Delivered)\b", ts, re.I):
            rr = rr or ts
            ts = None
        if ts and ts == last_pill and pending_pill is None:
            # the model copied the pill onto a later bubble in the same frame
            ts = None
        msg = {
            "msg_id": msg_id_for(r["image_index"], r["local_seq"]),
            "author": r.get("author"),
            "kind": kind,
            "text": r.get("text") or "",
            "link_title": r.get("link_title"),
            "link_url": r.get("link_url"),
            "bubble_side": r.get("bubble_side"),
            "timestamp_raw": ts or pending_pill,
            "read_receipt": rr,
            "reaction_emoji": r.get("reaction_emoji"),
            "reaction_reactor": r.get("reaction_reactor"),
            "reply_to_msg_id": None,
            "reply_to_visible_text": r.get("reply_to_visible_text"),
            "starts_before": bool(r.get("starts_before")),
            "ends_after": bool(r.get("ends_after")),
            "source_image_indices": [int(r["image_index"])],
            "notes": r.get("notes"),
            "geometry": r.get("geometry"),
            "ocr_hint": r.get("ocr_hint"),
        }
        pending_pill = None
        out.append(msg)
    return out


# --------------------------------------------------------------------------- stitching


def _norm_words(text: str) -> list[str]:
    words = re.findall(r"[^\s]+", text or "")
    return [re.sub(r"[^a-z0-9]+", "", w.lower()) for w in words]


def _orig_words(text: str) -> list[str]:
    return re.findall(r"[^\s]+", text or "")


def _overlap_len(a_norm: list[str], b_norm: list[str], min_n: int = 3) -> int:
    best = 0
    for n in range(min(len(a_norm), len(b_norm)), min_n - 1, -1):
        if a_norm[-n:] == b_norm[:n]:
            best = n
            break
    return best


def _contains(outer: list[str], inner: list[str]) -> bool:
    if not inner or len(inner) > len(outer):
        return False
    s_outer = " ".join(outer)
    s_inner = " ".join(inner)
    return s_inner in s_outer


def stitch_texts(a: str, b: str, sep_if_no_overlap: str | None = None) -> str:
    """Join two fragments of one bubble split by a scroll boundary."""
    a = (a or "").rstrip()
    b = (b or "").lstrip()
    if not a:
        return b
    if not b:
        return a
    an, bn = _norm_words(a), _norm_words(b)
    if _contains(an, bn):
        return a
    if _contains(bn, an):
        return b
    n = _overlap_len(an, bn)
    rest_words = _orig_words(b)[n:] if n else _orig_words(b)
    if not rest_words:
        return a
    # Rebuild the remainder of b preserving its paragraph breaks.
    if n:
        # locate where the (n)th word ends in b's original text
        idx = 0
        for _ in range(n):
            m = re.compile(r"\S+").search(b, idx)
            if not m:
                break
            idx = m.end()
        rest = b[idx:].lstrip(" ")
        rest = rest.lstrip("\n") if not rest.startswith("\n\n") else rest
    else:
        rest = b
    if rest.startswith("\n"):
        return a + rest
    sep = " "
    if n == 0 and sep_if_no_overlap is not None:
        sep = sep_if_no_overlap
    elif a.endswith("?") and rest[:1].isupper():
        sep = "\n\n"
    return a + sep + rest


# Glyph geometry of the SF font at 3x on iPhone SE: line pitch ≈ 40 px, inter-line gap ≈ 12 px.
# At a clean continuation the clipped tail/head show ≤ ~12 px of empty fill beyond the last/first glyph row;
# a blank (paragraph) line adds another ~40 px somewhere across the two fragments.
JOIN_PARAGRAPH_GAP_PX = 36


def join_separator(tail: dict[str, Any], head: dict[str, Any]) -> tuple[str, str]:
    """Separator for a zero-overlap join, from the measured empty fill at the two crop edges."""
    tg = (tail.get("geometry") or {}).get("tail_gap")
    hg = (head.get("geometry") or {}).get("head_gap")
    if tg is None or hg is None:
        return " ", "gaps unmeasured"
    if tg + hg >= JOIN_PARAGRAPH_GAP_PX:
        return "\n\n", f"paragraph break (tail_gap={tg}, head_gap={hg})"
    return " ", f"continuation (tail_gap={tg}, head_gap={hg})"


def _merge_into(base: dict[str, Any], other: dict[str, Any], text: str | None = None, sep_if_no_overlap: str | None = None) -> None:
    """Fold `other` (later fragment / duplicate) into `base` in place."""
    base["text"] = str(text).strip() if text else stitch_texts(base.get("text") or "", other.get("text") or "", sep_if_no_overlap)
    if other.get("geometry"):
        # the merged message's bottom edge is now the later fragment's
        g = dict(base.get("geometry") or {})
        g["tail_gap"] = (other.get("geometry") or {}).get("tail_gap")
        base["geometry"] = g
    if other.get("ocr_hint"):
        base["ocr_hint"] = stitch_texts(base.get("ocr_hint") or "", other["ocr_hint"], sep_if_no_overlap)
    for f in ("read_receipt", "reaction_emoji", "reaction_reactor", "reply_to_visible_text", "link_title", "link_url", "timestamp_raw"):
        base[f] = _first_non_null(base.get(f), other.get(f))
    if other.get("kind") == "link":
        base["kind"] = "link"
    base["source_image_indices"] = sorted(set(base.get("source_image_indices") or []) | set(other.get("source_image_indices") or []))
    if other.get("notes"):
        base["notes"] = _first_non_null(base.get("notes"), other.get("notes"))
    base["starts_before"] = bool(base.get("starts_before"))
    base["ends_after"] = bool(other.get("ends_after"))
    members = list(base.get("member_ids") or [base["msg_id"]])
    for mid in other.get("member_ids") or [other["msg_id"]]:
        if mid not in members:
            members.append(mid)
    base["member_ids"] = members


def frame_geometry(attributed: list[dict[str, Any]], messages: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Per-frame pixel-measured bubbles and the message each one feeds (for the GPT-4.1 passes)."""
    owner: dict[str, str] = {}
    for m in messages:
        for mid in m.get("member_ids") or [m["msg_id"]]:
            owner[mid] = m["msg_id"]
    frames: dict[int, list[dict[str, Any]]] = {}
    for r in sorted(attributed, key=lambda r: (int(r.get("image_index") or 0), int(r.get("local_seq") or 0))):
        g = r.get("geometry") or {}
        mid = msg_id_for(r["image_index"], r["local_seq"])
        frames.setdefault(int(r["image_index"]), []).append(
            {
                "bubble": f"b{r['local_seq']}",
                "color": g.get("color"),
                "y": [g.get("top"), g.get("bottom")],
                "clipped_top": bool(r.get("starts_before")),
                "clipped_bottom": bool(r.get("ends_after")),
                "feeds_msg_id": owner.get(mid, mid if any(m["msg_id"] == mid for m in messages) else None),
            }
        )
    return [{"image_index": k, "bubble_count": len(v), "bubbles": v} for k, v in sorted(frames.items())]


def prestitch(messages: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], list[str]]:
    """
    Deterministic scroll-overlap resolution between consecutive frames, using the pixel clip flags:
      - a bubble repeated whole in the next frame (identical / contained text, same author) → one message;
      - a bubble clipped at the bottom of frame k continued by the bubble clipped at the top of frame k+1
        (same author) → one message, text joined by word overlap.
    """
    msgs = [dict(m, source_image_indices=list(m.get("source_image_indices") or [])) for m in messages]
    log: list[str] = []
    if not msgs:
        return msgs, log
    last_frame = max(max(m["source_image_indices"] or [0]) for m in msgs)

    def frame_of(m: dict[str, Any], which: str) -> int:
        s = m.get("source_image_indices") or [0]
        return max(s) if which == "max" else min(s)

    for k in range(0, last_frame):
        prev = [m for m in msgs if frame_of(m, "max") == k]
        nxt = [m for m in msgs if frame_of(m, "min") == k + 1]
        if not prev or not nxt:
            continue
        # 1) whole-bubble repeats: a message of frame k+1 contained in / identical to one of frame k
        for b in list(nxt):
            bn = _norm_words(b.get("text"))
            if len(bn) < 3:
                continue
            for a in prev:
                if a is b or a.get("author") != b.get("author"):
                    continue
                an = _norm_words(a.get("text"))
                if " ".join(an) == " ".join(bn) or _contains(an, bn):
                    _merge_into(a, b)
                    msgs.remove(b)
                    nxt.remove(b)
                    log.append(f"prestitch repeat {b['msg_id']} → {a['msg_id']}")
                    break
                if len(an) >= 3 and _contains(bn, an) and a.get("ends_after") and b.get("starts_before"):
                    # a is a clipped fragment of b: keep b's fuller text
                    _merge_into(a, b, text=b.get("text"))
                    msgs.remove(b)
                    nxt.remove(b)
                    log.append(f"prestitch fragment {b['msg_id']} → {a['msg_id']} (kept later text)")
                    break
        if not nxt:
            continue
        tail, head = prev[-1], nxt[0]
        # 2) a textless sliver clipped at the top of frame k+1 is the bottom edge of frame k's last bubble
        if (
            tail is not head
            and head.get("starts_before")
            and not _norm_words(head.get("text"))
            and tail.get("author") == head.get("author")
        ):
            tail["source_image_indices"] = sorted(set(tail["source_image_indices"]) | set(head["source_image_indices"]))
            members = list(tail.get("member_ids") or [tail["msg_id"]])
            members.append(head["msg_id"])
            tail["member_ids"] = members
            for f in ("read_receipt", "reaction_emoji", "reaction_reactor"):
                tail[f] = _first_non_null(tail.get(f), head.get(f))
            msgs.remove(head)
            log.append(f"prestitch sliver {head['msg_id']} → {tail['msg_id']} (textless clipped head)")
            continue
        # 3) clipped tail of frame k + clipped head of frame k+1, same author → one send
        if tail is not head and tail.get("ends_after") and head.get("starts_before") and tail.get("author") == head.get("author") and tail in msgs and head in msgs:
            n = _overlap_len(_norm_words(tail.get("text")), _norm_words(head.get("text")))
            sep, why = join_separator(tail, head)
            _merge_into(tail, head, sep_if_no_overlap=sep)
            if n == 0 and tail.get("text") and head.get("text"):
                tail["notes"] = _first_non_null(tail.get("notes"), f"frame {k}/{k+1} join had no word overlap; joined as {why}; verify no line was lost")
            msgs.remove(head)
            log.append(f"prestitch clipped {head['msg_id']} → {tail['msg_id']} (overlap_words={n}{'' if n else ', ' + why})")
    return msgs, log


def overlap_candidates(messages: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Code hints for the model: adjacent-frame pairs that look like the same bubble."""
    out: list[dict[str, Any]] = []
    by_frame: dict[int, list[dict[str, Any]]] = {}
    for m in messages:
        for idx in m.get("source_image_indices") or []:
            by_frame.setdefault(int(idx), []).append(m)
    frames = sorted(by_frame)
    for k in frames:
        if k + 1 not in by_frame:
            continue
        # A bubble clipped at the bottom of frame k whose author matches the first bubble of frame k+1
        # is usually the same send continuing (the head of frame k+1 is often clipped at the top).
        tail, head = by_frame[k][-1], by_frame[k + 1][0]
        if tail is not head and tail.get("ends_after") and tail.get("author") == head.get("author"):
            out.append(
                {
                    "a": tail["msg_id"],
                    "b": head["msg_id"],
                    "reason": "clipped_tail_then_same_author_head",
                    "overlap_words": 0,
                    "same_author": True,
                }
            )
        for a in by_frame[k]:
            for b in by_frame[k + 1]:
                if a is b:
                    continue
                an, bn = _norm_words(a.get("text")), _norm_words(b.get("text"))
                reason = None
                n = 0
                if an and bn and (" ".join(an) == " ".join(bn)):
                    reason = "identical_text"
                elif len(bn) >= 5 and _contains(an, bn):
                    reason = "b_inside_a"
                elif len(an) >= 5 and _contains(bn, an):
                    reason = "a_inside_b"
                else:
                    n = _overlap_len(an, bn, min_n=4)
                    if n:
                        reason = "suffix_prefix_overlap"
                    elif a.get("ends_after") and b.get("starts_before") and a.get("author") == b.get("author"):
                        reason = "clip_flags_pair"
                if reason:
                    out.append(
                        {
                            "a": a["msg_id"],
                            "b": b["msg_id"],
                            "reason": reason,
                            "overlap_words": n,
                            "same_author": a.get("author") == b.get("author"),
                        }
                    )
    return out


# --------------------------------------------------------------------------- tools


def _index(messages: list[dict[str, Any]]) -> dict[str, int]:
    return {m["msg_id"]: i for i, m in enumerate(messages)}


def _first_non_null(*vals):
    for v in vals:
        if v not in (None, ""):
            return v
    return None


_QUOTES = str.maketrans({"’": "'", "‘": "'", "“": '"', "”": '"'})


def _raw_tokens(text: str) -> list[str]:
    # punctuation kept: "principles" and "principles." are different readings
    return (text or "").translate(_QUOTES).split()


def two_reader_veto(old_text: str, new_text: str, ocr_hint: str | None) -> list[str]:
    """
    Two independent readers (Tesseract, gpt-4.1-mini) read the same pixels. A pass may not
      - remove/alter a token both readers produced ("Amazons" → "Amazon's"), nor
      - add a token neither reader produced ("fin ham" → "fin ham on", "principles" → "principles.").
    Whitespace / paragraph-break changes are never vetoed. Returns the vetoed tokens (empty = allowed).
    """
    if not ocr_hint:
        return []
    from collections import Counter

    old_c, new_c, ocr_c = Counter(_raw_tokens(old_text)), Counter(_raw_tokens(new_text)), Counter(_raw_tokens(ocr_hint))
    vetoed = []
    for tok, n_old in old_c.items():
        n_new = new_c.get(tok, 0)
        if n_new < n_old and ocr_c.get(tok, 0) >= n_old:
            vetoed.append(f"-{tok}")
    for tok, n_new in new_c.items():
        n_old = old_c.get(tok, 0)
        if n_new > n_old and ocr_c.get(tok, 0) < n_new:
            vetoed.append(f"+{tok}")
    return vetoed


def apply_tool_calls(
    messages: list[dict[str, Any]],
    tool_calls: list[dict[str, Any]],
) -> tuple[list[dict[str, Any]], list[str]]:
    """Run one batch of tool calls from a single GPT-4.1 pass. Returns (messages, log)."""
    msgs = [dict(m, source_image_indices=list(m.get("source_image_indices") or [])) for m in messages]
    log: list[str] = []

    for call in tool_calls:
        tool = (call.get("tool") or "").strip()
        idx = _index(msgs)

        if tool == "merge_messages":
            ids = [i for i in (call.get("msg_ids") or []) if i in idx]
            if len(ids) < 2:
                log.append(f"skip merge_messages: need ≥2 known ids, got {call.get('msg_ids')}")
                continue
            ids.sort(key=lambda i: idx[i])
            base = msgs[idx[ids[0]]]
            others = [msgs[idx[i]] for i in ids[1:]]
            for o in others:
                _merge_into(base, o)
            if call.get("text"):
                veto = two_reader_veto(base["text"], str(call["text"]), base.get("ocr_hint"))
                if veto:
                    log.append(f"merge_messages {ids}: stitched by code; supplied text REJECTED (would alter words both readers confirmed: {veto})")
                else:
                    base["text"] = str(call["text"]).strip()
            if call.get("author"):
                base["author"] = call["author"]
            drop = set(ids[1:])
            msgs = [m for m in msgs if m["msg_id"] not in drop]
            log.append(f"merge_messages {ids} → {ids[0]} ({'text given' if call.get('text') else 'stitched'})")

        elif tool == "set_text":
            mid = call.get("msg_id")
            if mid not in idx or not call.get("text"):
                log.append(f"skip set_text: {mid}")
                continue
            veto = two_reader_veto(msgs[idx[mid]]["text"], str(call["text"]), msgs[idx[mid]].get("ocr_hint"))
            if veto:
                log.append(f"set_text {mid} REJECTED: would alter words both Tesseract and gpt-4.1-mini read identically from the pixels: {veto}. Sender's spelling stays.")
                continue
            msgs[idx[mid]]["text"] = str(call["text"]).strip()
            log.append(f"set_text {mid}")

        elif tool == "set_author":
            mid = call.get("msg_id")
            if mid not in idx or not call.get("author"):
                log.append(f"skip set_author: {mid}")
                continue
            msgs[idx[mid]]["author"] = call["author"]
            msgs[idx[mid]]["bubble_side"] = "right" if call["author"] == "operator" else "left"
            log.append(f"set_author {mid} → {call['author']}")

        elif tool == "set_meta":
            mid = call.get("msg_id")
            if mid not in idx:
                log.append(f"skip set_meta: {mid}")
                continue
            changed = []
            for f in META_FIELDS:
                if call.get(f) is not None:
                    msgs[idx[mid]][f] = call[f]
                    changed.append(f)
            log.append(f"set_meta {mid} {changed}")

        elif tool == "delete_message":
            mid = call.get("msg_id")
            if mid not in idx:
                log.append(f"skip delete_message: {mid}")
                continue
            msgs = [m for m in msgs if m["msg_id"] != mid]
            log.append(f"delete_message {mid} ({call.get('reason') or 'no reason'})")

        elif tool == "insert_message":
            if not call.get("text") or not call.get("author"):
                log.append("skip insert_message: text and author required")
                continue
            after = call.get("after_msg_id")
            src = call.get("source_image_index")
            new_id = f"ins_{len(msgs):02d}_{abs(hash(call['text'])) % 10000:04d}"
            new = {
                "msg_id": new_id,
                "author": call["author"],
                "kind": "text",
                "text": str(call["text"]).strip(),
                "link_title": call.get("link_title"),
                "link_url": call.get("link_url"),
                "bubble_side": "right" if call["author"] == "operator" else "left",
                "timestamp_raw": call.get("timestamp_raw"),
                "read_receipt": call.get("read_receipt"),
                "reaction_emoji": call.get("reaction_emoji"),
                "reaction_reactor": call.get("reaction_reactor"),
                "reply_to_msg_id": call.get("reply_to_msg_id"),
                "reply_to_visible_text": call.get("reply_to_visible_text"),
                "starts_before": False,
                "ends_after": False,
                "source_image_indices": [int(src)] if src is not None else [],
                "notes": call.get("reason") or "inserted by GPT-4.1 pass",
            }
            pos = idx[after] + 1 if after in idx else len(msgs)
            msgs.insert(pos, new)
            log.append(f"insert_message {new_id} after {after}")

        elif tool:
            log.append(f"unknown tool: {tool}")

    return msgs, log


# --------------------------------------------------------------------------- transcript rows


def to_transcript_rows(
    messages: list[dict[str, Any]],
    *,
    run_id: str,
    frames: dict[int, dict[str, Any]],
    process_date: str,
    tz: str,
) -> list[dict[str, Any]]:
    from dates import resolve_pill
    from interlocutions import detect_interlocutions
    import datetime
    from zoneinfo import ZoneInfo

    y, mo, d = (int(x) for x in process_date.split("-"))
    cap = datetime.date(y, mo, d)
    zone = ZoneInfo(tz)
    id_map = {m["msg_id"]: i for i, m in enumerate(messages)}

    rows: list[dict[str, Any]] = []
    for i, m in enumerate(messages):
        srcs = sorted(set(int(x) for x in (m.get("source_image_indices") or [])))
        first = frames.get(srcs[0]) if srcs else None
        ts_iso = None
        if m.get("timestamp_raw"):
            ts_iso, _ = resolve_pill(str(m["timestamp_raw"]), cap, zone)
        rows.append(
            {
                "record_type": "message",
                "run_id": run_id,
                "message_id": i,
                "msg_id": m["msg_id"],
                "author": m.get("author"),
                "kind": m.get("kind") or "text",
                "text": m.get("text") or "",
                "interlocutions": detect_interlocutions(m.get("text") or ""),
                "link_title": m.get("link_title"),
                "link_url": m.get("link_url"),
                "bubble_side": m.get("bubble_side"),
                "timestamp_raw": m.get("timestamp_raw"),
                "timestamp_iso": ts_iso,
                "read_receipt": m.get("read_receipt"),
                "reaction_emoji": m.get("reaction_emoji"),
                "reaction_reactor": m.get("reaction_reactor"),
                "reply_to_message_id": id_map.get(m.get("reply_to_msg_id")) if m.get("reply_to_msg_id") else None,
                "reply_to_visible_text": m.get("reply_to_visible_text"),
                "source_image_indices": srcs,
                "member_ids": list(m.get("member_ids") or [m["msg_id"]]),
                "ocr_hint": m.get("ocr_hint"),
                "source_image_index": srcs[0] if srcs else None,
                "source_filename": (first or {}).get("filename"),
                "source_image_path": (first or {}).get("image_path"),
                "source_crop_path": (first or {}).get("crop_path"),
                "notes": m.get("notes"),
            }
        )
    return rows


def messages_from_transcript_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Inverse of to_transcript_rows for pass 2 / re-runs."""
    id_by_index = {r.get("message_id"): r.get("msg_id") for r in rows}
    out = []
    for r in rows:
        out.append(
            {
                "msg_id": r.get("msg_id") or f"m{int(r.get('message_id') or 0):04d}",
                "author": r.get("author"),
                "kind": r.get("kind") or "text",
                "text": r.get("text") or "",
                "link_title": r.get("link_title"),
                "link_url": r.get("link_url"),
                "bubble_side": r.get("bubble_side"),
                "timestamp_raw": r.get("timestamp_raw"),
                "read_receipt": r.get("read_receipt"),
                "reaction_emoji": r.get("reaction_emoji"),
                "reaction_reactor": r.get("reaction_reactor"),
                "reply_to_msg_id": id_by_index.get(r.get("reply_to_message_id")),
                "reply_to_visible_text": r.get("reply_to_visible_text"),
                "starts_before": False,
                "ends_after": False,
                "source_image_indices": list(r.get("source_image_indices") or []),
                "member_ids": list(r.get("member_ids") or [r.get("msg_id")]),
                "ocr_hint": r.get("ocr_hint"),
                "notes": r.get("notes"),
            }
        )
    return out
