"""JSON Ledger primitives.

One line = one fact. Values are JSON primitives only (string, number, bool, null). Nothing is ever
rewritten; a correction is a new line with a later `ts` for the same (ticker, key, period). The current
truth is resolved by reading top to bottom and letting the latest `ts` win.

Line shape:
  {"ts": "2026-11-05T07:00:00Z", "ticker": "AMZN", "key": "ocf_ttm", "period": "2026Q3",
   "value": 168300, "unit": "USD_millions", "label": "measured", "source": "amzn_q3_2026_pr", "note": null}

label ∈ {"measured", "modelled", "stated"}:
  measured  — read from a primary document (filing, press release, EIA table); `source` names it
  modelled  — an assumption or a derived number; the formula or the reason is in `note`
  stated    — a claim someone made (management guidance, an analyst target, a person's thesis); `source`
              says who. A stated value is not a measurement of the thing it is about.
"""

from __future__ import annotations

import datetime
import json
from pathlib import Path
from typing import Any, Iterable

PRIMITIVES = (str, int, float, bool, type(None))
LABELS = ("measured", "modelled", "stated")


def now_ts() -> str:
    return datetime.datetime.now(datetime.UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def make_line(
    ticker: str,
    key: str,
    value: Any,
    *,
    period: str | None = None,
    unit: str | None = None,
    label: str = "measured",
    source: str | None = None,
    note: str | None = None,
    ts: str | None = None,
) -> dict[str, Any]:
    if not isinstance(value, PRIMITIVES):
        raise TypeError(f"value must be a JSON primitive, got {type(value).__name__} for {key}")
    if label not in LABELS:
        raise ValueError(f"label must be one of {LABELS}")
    if label == "measured" and not source:
        raise ValueError(f"measured line {key} needs a source")
    return {
        "ts": ts or now_ts(),
        "ticker": ticker,
        "key": key,
        "period": period,
        "value": value,
        "unit": unit,
        "label": label,
        "source": source,
        "note": note,
    }


def append(path: Path, lines: Iterable[dict[str, Any]]) -> int:
    path.parent.mkdir(parents=True, exist_ok=True)
    n = 0
    with path.open("a", encoding="utf-8") as f:
        for ln in lines:
            f.write(json.dumps(ln, ensure_ascii=False) + "\n")
            n += 1
    return n


def read(path: Path) -> list[dict[str, Any]]:
    if not path.is_file():
        return []
    out = []
    for raw in path.read_text(encoding="utf-8").splitlines():
        raw = raw.strip()
        if raw:
            out.append(json.loads(raw))
    return out


def resolve(lines: list[dict[str, Any]]) -> dict[tuple[str, str, str | None], dict[str, Any]]:
    """Latest ts wins per (ticker, key, period)."""
    cur: dict[tuple[str, str, str | None], dict[str, Any]] = {}
    for ln in sorted(lines, key=lambda x: x["ts"]):
        cur[(ln["ticker"], ln["key"], ln.get("period"))] = ln
    return cur


class View:
    """Read-side helper over a resolved ledger."""

    def __init__(self, lines: list[dict[str, Any]], ticker: str):
        self.ticker = ticker
        self.cur = resolve([ln for ln in lines if ln["ticker"] == ticker])

    def get(self, key: str, period: str | None = None, default: Any = None) -> Any:
        ln = self.cur.get((self.ticker, key, period))
        return default if ln is None else ln["value"]

    def line(self, key: str, period: str | None = None) -> dict[str, Any] | None:
        return self.cur.get((self.ticker, key, period))

    def series(self, key: str) -> dict[str, Any]:
        """period → value for every period that has this key, sorted by period string."""
        out = {p: ln["value"] for (t, k, p), ln in self.cur.items() if k == key and p is not None}
        return dict(sorted(out.items()))

    def keys(self) -> list[str]:
        return sorted({k for (_, k, _) in self.cur})
