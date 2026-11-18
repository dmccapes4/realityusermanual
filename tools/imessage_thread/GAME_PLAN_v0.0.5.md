# imessage_thread v0.0.5

**Goal:** Reconstruct an iMessage thread from sequential iPhone screenshots with **fidelity**: one message per send, verbatim text, correct author, UI metadata (tapbacks, reply context, timestamps, read receipts), and a report whose Transcript is derived from `transcript.jsonl` by code.

**Supersedes:** v0.0.4 (quarantined in `quarantine/v0.0.4_code/`). v0.0.4 failed on the Justin AMZN run: OCR visual line-wraps leaked into message bodies, scroll-overlap duplicates survived both GPT-4.1 passes, blue operator text was filed as `justin`, and interlocution labels were inverted.

**Why v0.0.4 failed (read before changing anything):**

1. **GPT-4.1 never saw the images.** It compared `attributed` vs `ocr_text` strings. OCR of wrapped bubbles is line-per-visual-line with glyph errors (`'` → `\u0002`, `debt. Then. The market` → `daht Than Tha marlat`). A text-only judge cannot tell a wrap from a newline or a scroll duplicate from a new message.
2. **Deterministic dedupe (`dedupe_local` + `consolidate`) ran on bad rows** and invented merges; `stitch_ocr_tail` appended OCR garbage to good text.
3. **Interlocutor label on the answer blocks.** Fixed in `interlocutions.py` + `.cursor/rules/self-interlocution.mdc`; carried forward.

---

## Authors

| Slug | UI |
|------|-----|
| `operator` | Blue, right-aligned (phone owner) |
| `{contact}` | Gray, left (slug from header, e.g. `justin`) |

Report labels: `operator` (exposition/answers), `operator (interlocutor)` (anchored **question** lines of pedagogical self-interlocution), `{contact}`. See `.cursor/rules/self-interlocution.mdc` and `interlocution_example.md`.

---

## Stages (operator spec 0–8)

```
0 init       mkdir run_dir + empty jsonl/json/md/log files
1 contact    header crop of image[0] → contact.json  (name, locality, status-bar time, first date pill)
2 crop       fixed thread box per screenshot → crops/{stem}.png  (740×946)
3 ocr        tesseract on crops → ocr.jsonl
4 attribute  gpt-4.1-mini × N  (crop + ocr_text) → attributed.jsonl   (bubble = item; OCR corrected from pixels)
5 stitch     gpt-4.1 pass 1  (attributed + crops, NO ocr) → tool_calls → system applies once → transcript.jsonl
6 review     gpt-4.1 pass 2  (transcript + crops + pass-1 log)   → tool_calls → system applies once → transcript.jsonl
7 scaffold   system writes report.md: header + Brief/Analysis/Metacommentary placeholders + styled Transcript (from transcript.jsonl)
8 report     gpt-4o fills Brief (abstract of the conversation) + Analysis + Metacommentary; Transcript untouched
```

CLI: `--stage init|contact|crop|ocr|attribute|stitch|review|scaffold|report|all`. Each stage reads the previous stage's file from disk and rewrites its own; re-running a stage is safe.

### 0 — `init`

Creates:

```
{run_dir}/
  run.log
  run_meta.json          {run_id, version, images_dir, image_count, models, created_at}
  contact.json           {}
  ocr.jsonl              (empty)
  attributed.jsonl       (empty)
  transcript.jsonl       (empty)
  gpt41_pass1.json       {}
  gpt41_pass2.json       {}
  report.md              (empty)
  crops/
```

`run_meta.json` gains `*_committed_at` timestamps as stages finish. `run.log` is append-only, one line per stage event.

### 1 — `contact`

- Header crop of `images[0]` (`header_crop_px` in the profile) → tesseract → `parse_contact_header` → `contact_name`, `contact_locality`.
- If tesseract yields no plausible name, gpt-4.1-mini reads the header crop (name + locality only).
- Status-bar time (`status_bar_crop_px`) and the first date pill from the thread crop → `thread_anchor` via `dates.resolve_pill` against `--process-date` (assumption 0b: screenshots taken the day they are processed).
- Output `contact.json`: `{contact_name, contact_slug, contact_locality, status_bar_time, thread_anchor:{raw, timestamp_iso, timestamp_confidence}, header_ocr_text}`.

### 2 — `crop`

Fixed box for iPhone SE (2022) 750×1334, iMessage dark, measured on this corpus:

| Edge | px | Reason |
|------|----|--------|
| top | 248 | first row below the `Justin ›` / `Roseville, CA` header pill (pill ends y≈246) |
| bottom | 1194 | last row above the composer bar line (y≈1197) |
| left / right | 5 / 745 | 740 px wide |

Result **740×946**, the same dimensions as `IMG_1484.jpg`, which was supplied already cropped. Rule per frame:

- size == `screenshot_size_px` (750×1334) → crop with the box
- size == `thread_crop_size_px` (740×946) → use as-is (already cropped)
- otherwise → use as-is, write a `notes` warning to `ocr.jsonl` and `run.log`

Crops are saved to `crops/{stem}.png` and are the **only** images sent to GPT in stages 4–6.

### 3 — `ocr`

Tesseract `--psm 6` on each crop → `ocr.jsonl` row: `{image_index, filename, image_path, crop_path, crop_box_px, dimensions_px, ocr_text, ocr_confidence, thread_markers_raw, notes}`. OCR is auxiliary from here on: it is a hint to stage 4 and never reaches stages 5–8.

### 4 — `attribute` (pixel geometry + gpt-4.1-mini, one call per crop)

**Revision 2026-11-05 (after the first v0.0.5 run):** four mini-only attribution runs each fused or split bubbles differently, filed a cut line as `justin`, and put a tapback on the bubble above the badge. Structure is now **measured, not asked for**. `bubbles.py` reads the dark-mode crop by color:

| Element | Pixel test | Fields |
|---|---|---|
| blue bubble | `B>150, B>R+60` row bands ≥ 8 px | `top/bottom/left/right`, `clipped_top/bottom`, `head_gap/tail_gap` |
| gray bubble | `|R−G|<14, |G−B|<16, 24≤R≤70` | same |
| tapback badge | gray/blue band ≤ 130×90 px | `target_idx` = bubble **below** (iOS draws it over the reacted bubble's top corner) |
| label | thin gray band ≤ 30 px, not at an edge | centred → `pill` (→ bubble below); right-aligned → `receipt` (→ blue bubble above) |

- **Clipped** = the band runs at **full width** into the crop edge. A rounded corner touching the edge is a bubble that starts/ends there (frame 3: "Send me the theory" begins at y=2 with its corners visible → separate send, not a continuation).
- `head_gap` / `tail_gap` = empty fill between the crop edge and the first/last glyph row. Clean continuation ≤ ~12 px; a blank paragraph line adds ~40 px. Used by stage 5 to pick `"\n\n"` vs `" "` at a zero-overlap join.

mini receives the full frame **and** a crop of every element (bubbles, badges ×3, labels ×3), plus per-bubble Tesseract text as `ocr_hint`, and returns **only text**: `bubbles[{idx,text,is_link_card,link_title,link_url,reply_to_visible_text,notes}]`, `badges[{idx,emoji}]`, `labels[{idx,text}]` — exactly one entry per element id. Code assembles the row: `author` from color, `bubble_side`, `starts_before/ends_after` from the clip test, `timestamp_raw` from the pill above, `read_receipt` from the receipt below, `reaction_*` from the badge target. Each row also carries `geometry` and `ocr_hint`.

Prompt rules that remain the model's job: verbatim text, visual wraps joined, `\n\n` only at a blank line, `\n` only for a typed hard break (`>` lines), keep `*asterisks*` / quotes / `?`, **omit** a half-cut line at a clipped edge, no guessing hidden words.

Writes `attributed.jsonl` (one line per bubble, with `image_index`, `filename`, `crop_path`, `geometry`, `ocr_hint`). `run.log` shows one line per frame, e.g. `items=4 [b0:g^ b1:b+pill b2:b+👍 b3:bv]`.

### 5 — `stitch` (code prestitch, then gpt-4.1 pass 1)

**Prestitch (`thread_tools.prestitch`, deterministic, logged to `run.log` and `gpt41_pass1.json.prestitch_log`).** For each consecutive frame pair k, k+1:

1. a bubble of k+1 whose text is identical to / contained in a same-author bubble of k → folded into it (scroll repeat);
2. a textless sliver clipped at the top of k+1 → the bottom edge of k's last bubble;
3. k's last bubble `clipped_bottom` + k+1's first bubble `clipped_top`, same author → **one send**, text joined by word overlap (`stitch_texts`); with zero overlap the separator comes from `head_gap + tail_gap ≥ 36 px → "\n\n"`, else `" "`, and a `notes` entry says so.

A send spanning frames 4–10 becomes one message with `member_ids = [m04_03 … m10_00]`. Justin run: 25 bubbles → 16 messages before any model sees the list.

**GPT-4.1 pass 1.** Input: all crops as images (labelled `image_index`), the prestitched message list, `frame_geometry` (per frame: every measured bubble, its color/y-range/clip flags and which `msg_id` it feeds), `overlap_candidates`. **No OCR text in the payload.** Job, in priority: text fidelity against pixels → frame joins → metadata → structure only with cited pixel evidence.

Output JSON (strict schema): `{pass, summary, ok, issues[], tool_calls[]}`. The system applies `tool_calls` **once** with `thread_tools.apply_tool_calls` and writes `transcript.jsonl`.

**Two-reader veto (`thread_tools.two_reader_veto`).** Tesseract and mini are two independent readers of the same bubble. A `set_text` (or `merge_messages` with `text`) is **rejected and logged** if it removes a token both readers produced or adds a token neither produced. Whitespace / paragraph-break edits always pass. Observed on the Justin run: 4.1 tried `Amazons → Amazon's`, `fin ham → fin ham on`, `than price → that price`, `principles → principles.`; all four were inventions (checked against the frames), all four vetoed. Cost of the rule: a word both readers misread identically (e.g. `Al` for `AI`) cannot be fixed by 4.1 either; it would need a human.

### 6 — `review` (gpt-4.1 pass 2)

Same prompt body, same schema, same executor, same tools, same veto. Role text says pass 2; payload adds `prior_pass` (pass-1 JSON + `tool_execution_log`, including rejections) and the current `transcript.jsonl` messages. Applied **once**. No third pass. No loop.

### Tools (`thread_tools.apply_tool_calls`)

| Tool | Args | Effect |
|------|------|--------|
| `merge_messages` | `msg_ids[]`, `text?` | Combine scroll-split / duplicated bubbles into the first id. `text` null → deterministic word-overlap stitch (containment → keep longer). `text` given → used only if it passes the two-reader veto. |
| `set_text` | `msg_id`, `text` | Replace body with verbatim text read from the image. Subject to the two-reader veto. |
| `set_author` | `msg_id`, `author` | Fix blue/gray mis-attribution. |
| `set_meta` | `msg_id`, any of `reaction_emoji`, `reaction_reactor`, `reply_to_msg_id`, `reply_to_visible_text`, `timestamp_raw`, `read_receipt`, `link_title`, `link_url` | Attach UI metadata to the text. |
| `delete_message` | `msg_id`, `reason` | Remove a pure duplicate or non-message. |
| `insert_message` | `after_msg_id`, `author`, `text`, `source_image_index` | Add a bubble vision missed. |

Tools do not know which pass invoked them. Every call is logged to `tool_execution_log` in that pass's JSON.

### 7 — `scaffold` (code only)

Writes `report.md`:

```
# {Contact} — thread
**Processed:** … · **Run:** … · **Tool:** imessage_thread v0.0.5
**Source:** `{images_dir}` ({n} screenshots) · **Contact:** {name} ({locality}) · **Anchor:** {thread_anchor.raw} → {iso}

## Brief
<!-- gpt4o:brief -->

## Transcript
{format_transcript_md(transcript.jsonl)}

## Analysis
<!-- gpt4o:analysis -->

## Metacommentary
<!-- gpt4o:metacommentary -->
```

Transcript styling (`format_report.format_transcript_md`):

- `**operator** (Yesterday 8:11 AM):` then the body; markdown is **not** escaped (`*observe*` renders italic as typed).
- `interlocutions[]` from `interlocutions.detect_interlocutions(text)` → anchored question lines rendered under `**operator (interlocutor)**`; everything else under `**operator**`.
- `↳ 👍 from justin` for tapbacks, `↩ replying to: "…"` for reply strips, `(Read 3:18 PM)` for read receipts.

### 8 — `report` (gpt-4o)

Receives `contact.json`, `run_meta.json`, `transcript.jsonl`. Returns `{brief, analysis, metacommentary}` and the system replaces the three placeholders. **Brief** = abstract of the conversation (who, when, what was argued, how it ended). **Analysis** = technical content as stated in-thread. **Metacommentary** = agent opinion on the reconstruction and the exchange. The Transcript section is never touched by the model.

---

## Models

| Stage | Model | Must not |
|-------|-------|----------|
| 1 (fallback) | gpt-4.1-mini | anything but name + locality |
| 4 | gpt-4.1-mini | split bubbles; emit visual wraps as `\n`; invent reactions |
| 5, 6 | gpt-4.1 | execute tools; paraphrase; see OCR |
| 8 | gpt-4o | rewrite the Transcript |

---

## Join keys

| Key | Ties |
|-----|------|
| `run_id` | every artifact in `{run_dir}` |
| `image_index` | `ocr.jsonl` ↔ `attributed.jsonl` ↔ `crops/` ↔ image order |
| `local_seq` | bubble order top→bottom inside one frame |
| `msg_id` | `attributed` item → message in passes 5/6 (`m{image_index:02d}_{local_seq:02d}`) |
| `message_id` | final 0-based index in `transcript.jsonl` |
| `source_image_indices[]` | provenance after merges |
| `interlocutions[].line` | 1-based line into that message's `text` |

---

## Fidelity checks (run against the frames, not the OCR)

- No message body contains a visual wrap (`\n` inside a sentence).
- No consecutive messages share a 6-word sequence (scroll duplicate).
- Right-aligned blue text never appears as `{contact}`.
- Long operator Q&A sends are one message each; closing "It is fine…" is operator.
- Count of messages ≈ count of distinct bubbles across frames (Justin run: 16).
- No model-invented words: every `set_text` rejection in `tool_execution_log` was checked against its frame.

## Result on the Justin run (2026-11-05, run `justin_texts_amzn_202611_20261105T045857Z`)

25 measured bubbles → 16 messages; the operator's Q&A send is one message across frames 4–10 with 6 interlocution anchors; 👍 on "People are dumb…" and "It's Q&A format…" (both from Justin); `Read 3:18 PM` on the last blue bubble; `*observe*` kept as typed; `oils` kept as typed. Pass 1 proposed four word edits, all vetoed (all four were wrong against the frames); pass 2 confirmed with no tool calls. Frames 0–10 were read by eye against the transcript.

## Code map (v0.0.5)

| File | Role |
|------|------|
| `imessage_thread.py` | CLI |
| `pipeline.py` | stages 0–8 |
| `crop.py`, `ocr.py`, `dates.py`, `io_jsonl.py`, `openai_env.py` | capture + I/O |
| `contact.py` | stage 1 |
| `bubbles.py` | stage 4 geometry: bubbles / badges / labels by pixel color, clip test, glyph gaps |
| `attribute_vision.py` | stage 4 text reading (mini) + row assembly |
| `gpt41_pass.py` | stages 5/6 (one function, `pass_number`) |
| `thread_tools.py` | message state, `prestitch`, `frame_geometry`, `two_reader_veto`, `apply_tool_calls`, overlap stitch |
| `interlocutions.py`, `format_report.py` | stage 7 |
| `report_model.py` | stage 8 |
| `crop_profiles/iphone_se_2022_imessage_dark.json` | boxes above |

## CLI

```bash
cd REALITY_USER_MANUAL
.venv/bin/python tools/imessage_thread/imessage_thread.py run \
  --images misc/justin_texts_amzn_202611/images \
  --out misc/justin_texts_amzn_202611/runs \
  --process-date 2026-11-04 --tz America/Los_Angeles \
  --stage all            # or one stage with --run-dir <existing run>
```
