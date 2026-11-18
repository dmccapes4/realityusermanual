# Reflection: GPT layering (your questions, 2026-11-04)

**Trigger:** `GAME_PLAN_v0.0.3.md` wrongly said vision is optional *outside* the tool. You had said the **opposite**: **gpt-4.1-mini in-tool per screenshot** for attribution and metadata only, then **gpt-4.1** at thread scope — twice for different work — then **gpt-4o** for report prose. This note answers your question list and records my read on the design.

---

## Correction

**Your intent (v0.0.2 game plan, still normative for v0.0.3):**

| Stage | Model | Scope |
|-------|--------|--------|
| B Attribute | **gpt-4.1-mini** | One (or N) **image + that frame’s OCR** → `attributed_text.jsonl` |
| C Dedupe | **gpt-4.1** (1st full-thread call) | All attributed + OCR + staging frames |
| D Review / merge assist | **gpt-4.1** (2nd call, when needed) | Canonical boundaries vs attributed + deduped texts |
| E Report | **gpt-4o** | Intro/analysis only; Transcript from JSON |

I incorrectly wrote “vision optional outside this tool” while resetting to v0.0.3. That line is removed; the pipeline section in `GAME_PLAN_v0.0.3.md` is corrected.

---

## GPT-4.1-mini vs GPT-4.1 (main differences)

**Modelled (OpenAI product family, not a lab measure):**

- **gpt-4.1-mini:** Cheaper, faster, strong **single-image** vision; good structured JSON per frame; weaker on long cross-frame reasoning and subtle “this gray line is still blue scroll continuation” logic.
- **gpt-4.1:** Higher capability on **long context**, multi-step consistency, comparing many JSONL rows to each other and to OCR; better for **thread-level** plans (dedupe scripts, merge audits, discrepancy notes) without replacing pixel truth.

**Why mini on individual screenshots (stage B):**

- Cost scales with **11+ images**; mini × N is affordable to re-run one bad frame.
- Task is **local**: bubble count, left/right color, verbatim text in box, tapback, link card, `starts_before` / `ends_after`.
- OCR is a **hint**, not the authority — mini must look at the image; OCR helps spelling and long bodies.

**Why full 4.1 on all screenshots + all attributed + all OCR (stage C/D):**

- **Overlap:** same bubble on frame *i* and *i+1*; dedupe must not drop tails or double-count.
- **Global consistency:** speaker must agree with side across frames; petroleum monologue must not become six messages or gray Justin.
- **Discrepancy triangulation:** frame B says `justin` but OCR tail only appears under blue continuation; only a thread view catches that.

---

## Why you layered two GPT-4.1 calls

**Separation of concerns** (and failure isolation):

1. **First 4.1 (dedupe / stage C):** “What are the **canonical bubble bodies** after scroll overlap?” Output: `transcript_texts.jsonl`, optional `dedupe.sh`, plan markdown. Thinks in **keys and overlap**, not final message merge or interlocution.

2. **Second 4.1 (review / stage D when row count or flags demand it):** “Do these canonical rows match **attribution** and **UI** intent?” Merge corrections, boundary fixes, notes — then hand off to **deterministic** merge + `interlocutions[]`.

If one prompt tries to dedupe + canonicalize + style interlocution, it **will** paraphrase, drop tails, and merge Q&A wrong (what v0.0.2 demonstrated). Two calls are not vanity; they are **different oracles** with different output schemas.

---

## What should the first GPT-4.1 call do if it notices a discrepancy?

**Default posture: record, don’t invent.**

- Append to row `notes` or `dedupe_plan.md`: type (`speaker_side_mismatch`, `ocr_tail_missing`, `duplicate_body`, `clip_unstitched`), `image_index`, `local_seq`, short evidence (OCR excerpt vs attributed text).
- Prefer **deterministic shell** (`dedupe.sh` from staging) when the fix is mechanical; use 4.1 to **author the script**, not to silently rewrite text in JSON.
- **Do not** set interlocution or split bubbles for literary Q&A in this stage.

**Second 4.1** (review) may propose **merge/join** operations with explicit source rows; human or agent re-runs merge; still no Transcript paraphrase.

---

## How would it know there is a discrepancy?

Needs **join keys** and **cross-signals**:

| Signal | Example |
|--------|---------|
| Same `text` prefix on adjacent `image_index` | Scroll duplicate |
| `ends_after` / `starts_before` pair without merge | Stitch failure |
| `bubble_side` vs `speaker` invariant broken | Blue labeled `justin` |
| OCR contains substring attributed text lacks | Clipped “humanity… World wars” |
| Attributed `local_seq` gaps vs vision item count | Missing bubble |
| `ends_after` + next frame OCR continues mid-word | `humanitv` → full sentence |

Without **`image_index`, `local_seq`, `image_path`, `ocr_text` per frame**, and attributed rows keyed the same way, 4.1 is guessing.

---

## Data required to tie artifacts together

Minimum graph:

```
image_path (absolute)
  → image_index
      → ocr_output.jsonl (ocr_text)
      → attributed_text.jsonl (many rows: local_seq, speaker, text, clip flags)
      → staging/frame_{index}.jsonl (copy for dedupe.sh)
  → transcript_texts.jsonl (text_key, source_image_index, …)
  → transcript.jsonl (message_id, author, text, interlocutions[], source_image_indices[])
  → report.md (Transcript section derived from transcript.jsonl only)
```

`images.jsonl` (v0.0.2) bundles per-frame OCR + serialized mini output for audit. **`run_id`** scopes one run folder.

---

## Is GPT-4.1 a great tool for this?

**For thread-level dedupe and audit plans: yes, with constraints.** Structured output, long context, good at “compare these 40 JSON lines and write awk.”

**For pixel attribution: use mini (or human), not 4.1 alone** — cost and overkill per frame; 4.1 without images cannot fix blue/gray errors.

**Not great when:** prompts ask it to **author** transcript text, **segment** interlocution, and **dedupe** in one shot — that violates your reflection and produces clipped Friedman tails.

---

## What is GPT-4o better at?

**Modelled:** fluent **prose**, intro/analysis/metacommentary, summarizing **for reading** when fidelity is not the deliverable. Weaker choice for strict JSON schema discipline and multi-file forensic consistency than 4.1 in this pipeline’s experience.

**Good fit:** stage E — “what is this thread about?” given an **already authoritative** `transcript.jsonl`.

**Bad fit:** replacing stage B vision or rewriting Transcript bodies.

---

## Can GPT-4o effectively build `report.md` from `transcript.jsonl`?

**Partially.**

- **Yes:** Intro, Analysis, Metacommentary from structured messages.
- **No (alone):** Transcript section must be **verbatim** — use `format_report.format_transcript_md` (deterministic). v0.0.2 acceptance rule 5: gpt-4o for everything **except** Transcript body.

4o **can** assemble the markdown **file** if the pipeline **injects** the Transcript block from code. Letting 4o type bubbles from memory is how summarization and wrong speakers creep in.

---

## Must `transcript.jsonl` be authoritative before GPT-4o runs?

**Yes.** That is the contract:

- **Authoritative:** `text` + `author` + provenance + `interlocutions[]` are frozen; E adds commentary around them.
- If E runs on a draft transcript, the report **lies** even when prose sounds fine.

Stages B–D exist to **earn** that authority; E **describes** it.

---

## How would the two GPT-4.1 calls handle this? (v0.0.4)

**Two-pass system, no loop.** “Flags” means **which tools to run** — not prose fixes in the model.

| | Pass 1 (C) | Pass 2 (D) |
|---|------------|------------|
| **Model output** | Same schema → `gpt41_pass1.json` | Same schema → `gpt41_pass2.json` |
| **System runs** | `apply_tool_calls` once | `apply_tool_calls` once (not chained with pass 1) |
| **Difference** | Role in prompt: first pass | Role in prompt: verify prior log + state |

One executor, one tool list, one JSON shape. **merge** → **4o** after pass 2 only.

---

## Opinion

Your layering was right; my v0.0.3 over-correction (“no LLM”) threw away **mini-in-tool**, which you never asked to remove. The lesson from the reset is not “no models” — it is **narrow prompts, frozen transcript, join keys, read images, two 4.1 jobs not one god prompt**.

v0.0.3 code should **re-wire B/C/E** from quarantine without bringing back D2-style segment duplication. Interlocution stays **derived** from full message text (`interlocution_example.md`), not a second GPT rewrite of the bubble.

Your questions in this message are the **spec** for that re-wire; this file is the reflection on them.
