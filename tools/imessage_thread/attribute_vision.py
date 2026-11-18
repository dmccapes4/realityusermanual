"""Stage 4: pixel geometry fixes the bubble structure; gpt-4.1-mini reads the text of each detected element.

Per frame:
  1. bubbles.detect_bubbles → bubbles (blue/gray, clip flags), tapback badges (→ bubble below), labels (pill / receipt).
  2. Each element is cropped; bubble crops are OCR'd for a spelling hint.
  3. One gpt-4.1-mini call receives the full frame + every element crop and returns text per element id.
  4. Rows are assembled by code: author from color, reaction from badge→target, pill/receipt from label→target.
"""

from __future__ import annotations

import base64
import io
import json
from pathlib import Path
from typing import Any

from PIL import Image

from bubbles import bubble_crop, detect_bubbles
from ocr import ocr_image
from openai_env import client

SCHEMA = {
    "type": "object",
    "properties": {
        "bubbles": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "idx": {"type": "integer"},
                    "text": {"type": "string"},
                    "is_link_card": {"type": "boolean"},
                    "link_title": {"type": ["string", "null"]},
                    "link_url": {"type": ["string", "null"]},
                    "reply_to_visible_text": {"type": ["string", "null"]},
                    "notes": {"type": ["string", "null"]},
                },
                "required": ["idx", "text", "is_link_card", "link_title", "link_url", "reply_to_visible_text", "notes"],
                "additionalProperties": False,
            },
        },
        "badges": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {"idx": {"type": "integer"}, "emoji": {"type": "string"}},
                "required": ["idx", "emoji"],
                "additionalProperties": False,
            },
        },
        "labels": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {"idx": {"type": "integer"}, "text": {"type": "string"}},
                "required": ["idx", "text"],
                "additionalProperties": False,
            },
        },
    },
    "required": ["bubbles", "badges", "labels"],
    "additionalProperties": False,
}

SYSTEM = """You transcribe text from ONE cropped iMessage screenshot. The system has already located every element by pixel color and gives you a crop of each one; you only read what is printed inside.

Elements:
- bubble b<idx>: a message bubble (blue = operator, gray = {contact}; the system already knows the color). Return its full text verbatim.
- badge g<idx>: a tapback emoji badge. Return the emoji character(s).
- label l<idx>: thin gray system text (a date pill such as "Yesterday 8:11 AM" / "Today 9:06 AM", or "Read 3:18 PM" / "Delivered"). Return it exactly.

TEXT FIDELITY for bubbles
- Transcribe verbatim from the pixels. ocr_hint is Tesseract output for the same crop (line wraps already collapsed); use it to confirm spelling only. When it disagrees with the image, the image wins.
- Join visual line wraps with a single space. Write "\\n\\n" only where the bubble shows a blank line between paragraphs; write "\\n" only for a typed hard line break (for example a line that starts with '>').
- Keep punctuation exactly as printed: curly quotes, apostrophes, '>' at line starts, *asterisks*, '?' marks, ellipses, emoji.
- If the bubble is cut by the crop edge (clipped_top / clipped_bottom = true) and the first or last text line is only partly visible (half-height glyphs), OMIT that partial line. Do not guess hidden words.
- A link preview card (large thumbnail, bold title, domain line) → is_link_card=true, link_title = the title, link_url = the domain/URL exactly as printed, text = "title\\nurl".
- If a small quoted strip sits above the bubble (reply UI), put its visible text in reply_to_visible_text, else null.
- notes: only real uncertainty (blur, unreadable glyph). Otherwise null.

Return exactly one entry per element id you were given — no more, no fewer."""


def _png_data_url(img: Image.Image) -> str:
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode("ascii")


def _collapse(ocr_text: str) -> str:
    import re

    paras = re.split(r"\n\s*\n", (ocr_text or "").strip())
    return "\n\n".join(" ".join(p.split()) for p in paras if p.strip())


def _upscale(img: Image.Image, factor: int) -> Image.Image:
    return img.resize((img.width * factor, img.height * factor), Image.LANCZOS)


def attribute_frame(
    model: str,
    crop_path: Path,
    ocr_text: str,  # kept for signature compatibility; per-bubble OCR is computed here
    image_index: int,
    contact_slug: str,
) -> list[dict[str, Any]]:
    img = Image.open(crop_path).convert("RGB")
    elements = detect_bubbles(img)
    bubbles = [e for e in elements if e["kind"] == "bubble"]
    badges = [e for e in elements if e["kind"] == "badge"]
    labels = [e for e in elements if e["kind"] == "label"]

    manifest: dict[str, Any] = {
        "image_index": image_index,
        "contact_slug_gray_left": contact_slug,
        "bubbles": [],
        "badges": [{"id": f"g{b['idx']}", "y": [b["top"], b["bottom"]]} for b in badges],
        "labels": [{"id": f"l{b['idx']}", "y": [b["top"], b["bottom"]], "role": b.get("label_role")} for b in labels],
    }
    content: list[dict[str, Any]] = []
    for b in bubbles:
        c = bubble_crop(img, b, pad=4)
        hint = _collapse(ocr_image(c, psm=6))
        b["_ocr_hint"] = hint
        manifest["bubbles"].append(
            {
                "id": f"b{b['idx']}",
                "color": b["color"],
                "y": [b["top"], b["bottom"]],
                "clipped_top": b["clipped_top"],
                "clipped_bottom": b["clipped_bottom"],
                "ocr_hint": hint,
            }
        )
    content.append({"type": "text", "text": json.dumps(manifest, ensure_ascii=False)})
    content.append({"type": "text", "text": "FULL FRAME"})
    content.append({"type": "image_url", "image_url": {"url": _png_data_url(img), "detail": "high"}})
    for b in bubbles:
        content.append({"type": "text", "text": f"b{b['idx']} ({b['color']}, y {b['top']}-{b['bottom']})"})
        content.append({"type": "image_url", "image_url": {"url": _png_data_url(bubble_crop(img, b, pad=4)), "detail": "high"}})
    for b in badges:
        content.append({"type": "text", "text": f"g{b['idx']} (tapback badge)"})
        content.append({"type": "image_url", "image_url": {"url": _png_data_url(_upscale(bubble_crop(img, b, pad=6), 3)), "detail": "high"}})
    for b in labels:
        content.append({"type": "text", "text": f"l{b['idx']} (system label, role={b.get('label_role')})"})
        content.append({"type": "image_url", "image_url": {"url": _png_data_url(_upscale(bubble_crop(img, b, pad=6), 3)), "detail": "high"}})

    resp = client().chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": SYSTEM.format(contact=contact_slug)},
            {"role": "user", "content": content},
        ],
        response_format={"type": "json_schema", "json_schema": {"name": "frame_elements", "strict": True, "schema": SCHEMA}},
        max_tokens=8000,
        temperature=0,
        seed=7,
    )
    data = json.loads(resp.choices[0].message.content or "{}")
    text_by_idx = {int(x["idx"]): x for x in data.get("bubbles") or []}
    emoji_by_idx = {int(x["idx"]): (x.get("emoji") or "").strip() for x in data.get("badges") or []}
    label_by_idx = {int(x["idx"]): (x.get("text") or "").strip() for x in data.get("labels") or []}

    # ---- assemble rows deterministically
    reactions: dict[int, dict[str, str]] = {}
    for g in badges:
        if g.get("target_idx") is not None:
            reactions[g["target_idx"]] = {
                "reaction_emoji": emoji_by_idx.get(g["idx"]) or "?",
                "reaction_reactor": contact_slug if g["color"] == "gray" else "operator",
            }
    pills: dict[int, str] = {}
    receipts: dict[int, str] = {}
    for lb in labels:
        txt = label_by_idx.get(lb["idx"]) or ""
        if lb.get("target_idx") is None or not txt:
            continue
        if lb.get("label_role") == "pill":
            pills[lb["target_idx"]] = txt
        elif lb.get("label_role") == "receipt":
            receipts[lb["target_idx"]] = txt

    rows: list[dict[str, Any]] = []
    for b in bubbles:
        t = text_by_idx.get(b["idx"], {})
        is_link = bool(t.get("is_link_card")) or bool(t.get("link_url"))
        rows.append(
            {
                "local_seq": b["idx"],
                "kind": "link" if is_link else "text",
                "author": "operator" if b["color"] == "blue" else contact_slug,
                "bubble_side": b["side"],
                "text": (t.get("text") or "").strip(),
                "starts_before": b["clipped_top"],
                "ends_after": b["clipped_bottom"],
                "timestamp_raw": pills.get(b["idx"]),
                "read_receipt": receipts.get(b["idx"]),
                "reaction_emoji": reactions.get(b["idx"], {}).get("reaction_emoji"),
                "reaction_reactor": reactions.get(b["idx"], {}).get("reaction_reactor"),
                "reply_to_visible_text": t.get("reply_to_visible_text"),
                "link_title": t.get("link_title"),
                "link_url": t.get("link_url"),
                "notes": t.get("notes"),
                "geometry": {k: b[k] for k in ("top", "bottom", "left", "right", "width", "height", "color", "head_gap", "tail_gap")},
                "ocr_hint": b.get("_ocr_hint"),
            }
        )
    return rows
