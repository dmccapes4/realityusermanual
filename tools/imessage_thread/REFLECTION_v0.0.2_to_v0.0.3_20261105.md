# Reflection: v0.0.2 → v0.0.3 (what was complicated, what is easier)

## What v0.0.2 got wrong

1. **Too many LLM gates** — vision attribution, dedupe model, canonicalize model, interlocution model, report model. Each could rewrite text or invent rows.
2. **Confused layers** — `interlocutor` on attributed rows, `dialog_segments_json` parallel to `text`, report labels flipping between `operator` and `author`.
3. **Merge logic as archaeology** — `canonicalize_local`, `consolidate`, `scroll_stitch`, petroleum mega-merge, dedupe ratios. Hard to answer: “what is one message?”
4. **Fidelity failures masked as style** — clipped “It is fine…”, operator prose filed under `justin`, duplicate Friedman paragraphs. GPT “audits” claimed success.

Prompts grew because each failure added a **prose rule** instead of a **deterministic stage** or a **human-editable JSONL file**.

## What v0.0.3 does instead

| Step | Mechanism |
|------|-----------|
| Capture | Tesseract OCR → JSONL |
| Attribute | `attributed_text.jsonl` (explicit rows; vision optional, outside core) |
| Record | `merge_messages` → one line per send, full `text` |
| Style | `interlocutions[]` line anchors + `format_report` |
| Verify | Images + OCR + `rg`/`jq`; re-run merge |

No deleted text in the Transcript section. No model paraphrase in the pipeline path.

## Is it easier?

**For agents:** yes. The state is four files and line-oriented JSON. Tool calls look like: read image → fix attributed row → run `--stage merge` → diff `text` tail.

**For you:** more honest work at **attribute** time (or one good vision pass into attributed JSONL), less chasing GPT contradictions in review.

## Was your instruction helpful?

Yes. Specifically:

- **`interlocution_example.md`** — concrete target shape; better than paragraphs of rules.
- **“operator not author in system names”** — corrected my label drift.
- **Pedagogical reflection** — stopped me from treating interlocution as dedupe/speaker split.
- **Delete prompts / quarantine** — forced a real reset instead of another patch on `interlocution_model.py`.

What hurt was my **non-compliance**: I kept adding prompt surface area when merge or attributed rows were wrong.

## What I think overall

The tool should behave like **git for sent text**: boring storage, explicit merges, derivable views (report). v0.0.2 tried to make the model the merge driver; that fails screenshot threads where **color, scroll, and one long blue monologue** are the hard facts.

v0.0.3 is not finished — attributed input for Justin’s run still carries v0.0.2 vision errors until someone re-attributes with images. The architecture is finally aligned with your example.

**Next honest step:** Re-build `attributed_text.jsonl` for the AMZN thread (bubble-by-bubble from images), run `merge` + `report`, compare tail of the petroleum message to `interlocution_example.md` line 32.
