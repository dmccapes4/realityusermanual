# imessage_thread

Screenshots → contact → fixed crop → OCR → pixel-measured bubbles read by gpt-4.1-mini → deterministic prestitch → two GPT-4.1 verification passes (tool calls applied once each, two-reader veto) → `transcript.jsonl` → `report.md` (Transcript derived by code; Brief / Analysis / Metacommentary by gpt-4o).

**Version:** see `VERSION` (0.0.5).

## Quick start

```bash
cd REALITY_USER_MANUAL
.venv/bin/python tools/imessage_thread/imessage_thread.py run \
  --images misc/your_thread/images \
  --out misc/your_thread/runs \
  --process-date 2026-11-04 --tz America/Los_Angeles \
  --stage all
```

Re-run one stage on an existing run:

```bash
.venv/bin/python tools/imessage_thread/imessage_thread.py run \
  --images misc/your_thread/images \
  --out misc/your_thread/runs \
  --run-dir misc/your_thread/runs/<run_id> \
  --stage attribute      # init|contact|crop|ocr|attribute|stitch|review|scaffold|report
```

Requires `OPENAI_API_KEY` in `REALITY_USER_MANUAL/.env` (loaded by `openai_env.py`) and `tesseract` on PATH.

## Spec

- `GAME_PLAN_v0.0.5.md` — stages 0–8, crop box, geometry rules, tools, veto, fidelity checks
- `interlocution_example.md` — canonical `transcript.jsonl` message + `interlocutions` (question anchors)
- `.cursor/rules/self-interlocution.mdc` (workspace) — interlocutor / pedagogical self-interlocution
- `REFLECTION_PEDAGOGICAL_INTERLOCUTION_20261105.md`, `REFLECTION_GPT_LAYERING_20261105.md`, `REFLECTION_v0.0.2_to_v0.0.3_20261105.md` — history

Quarantined code and runs: `quarantine/` (v0.0.2, v0.0.3, v0.0.4 and their failed runs).
