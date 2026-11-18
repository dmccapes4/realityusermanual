# stock_ledger — JSON Ledger of stock-state primitives

Version 0.0.1 (2026-11-05). Built from the sketch at the bottom of
`misc/justin_texts_amzn_202611/GEMINI_CHAT_DATA_CENTERS_WORLD_IS_FLAT_20261104.md`, with two changes:
the nested schema is flattened into dotted keys so every line holds one JSON primitive, and every line
carries a label and a source.

## Shape

```
{"ts":"2026-11-05T07:30:00Z","ticker":"AMZN","key":"fcf_ttm","period":"2026Q3","value":-42357,
 "unit":"USD_millions","label":"measured","source":"amzn_q3_2026_pr","note":"..."}
```

- `value` is a JSON primitive (string, number, bool, null). No objects, no arrays. A vector is N lines.
- The file is append-only. A correction is a new line with a later `ts`; the resolver takes the latest
  `ts` per `(ticker, key, period)`.
- `label` is one of `measured` (read from a primary document; `source` names it), `modelled` (an
  assumption or a computed number; the reason is in `note`), `stated` (a claim someone made — guidance,
  an analyst target, a person's thesis; `source` says who).
- `sources.jsonl` holds `{id, title, url, accessed, read_extent}` for every `source` id.

## Files

| file | role |
|---|---|
| `ledger.py` | primitives: `make_line`, `append`, `read`, `resolve`, `View` |
| `seed_amzn.py` | the AMZN facts, assumptions and sources as read on 2026-11-05; idempotent |
| `model.py` | derived series, snapshot at a price, 2027–2031 scenarios driven by `scn.*` lines, chart, markdown |
| `stock_ledger.py` | CLI: `put`, `get`, `keys`, `model` |

## Run

```bash
cd REALITY_USER_MANUAL
.venv/bin/python tools/stock_ledger/seed_amzn.py
.venv/bin/python tools/stock_ledger/stock_ledger.py model \
    misc/justin_texts_amzn_202611/amzn_model/ledger misc/justin_texts_amzn_202611/amzn_model/out AMZN
```

Add a fact later (new price, a filing line):

```bash
.venv/bin/python tools/stock_ledger/stock_ledger.py put misc/justin_texts_amzn_202611/amzn_model/ledger \
    AMZN close_price 270.10 --period 2026-11-05 --unit USD --source yahoo_amzn_hist
```

Change a scenario view without touching code (latest `ts` wins):

```bash
.venv/bin/python tools/stock_ledger/stock_ledger.py put misc/justin_texts_amzn_202611/amzn_model/ledger \
    AMZN scn.B.terminal_p_ocf 11 --unit x --label modelled --file assumptions --note "lower multiple after FERC large-load rule"
```

## Model

- Base: TTM at `model.base_period`. Scenario year *y*: revenue × (1+g), OCF = revenue × margin, capex as
  an absolute or a `"NN%"` of revenue, plus `asset_sale_proceeds`. FCF discounted at `model.discount_rate_pct`.
- Terminal value = final-year OCF × `scn.<id>.terminal_p_ocf`. P/OCF is used because it is the multiple
  the market actually applies to AMZN; a terminal on FCF would silently assume a capex intensity.
- Outputs: `out/derived.jsonl` (every computed number as a `modelled` line), `out/MODEL_<T>_<date>.md`,
  `out/<T>_model_<date>.png`.
- The model has no loop and no LLM in it. It is arithmetic over the ledger.

## Not in 0.0.1

- No daemon; run on demand.
- Gemini's `RISK_WEIGHT_MATRIX` / `AXIS_LABELS` composite (liquidation > 1.5, compression > 1.2) is not
  implemented: its weights were invented in the chat and the thresholds have no measurement behind them.
  If wanted, each axis should be a ledger key with a source first.
