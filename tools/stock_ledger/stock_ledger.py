"""CLI for the JSON Ledger.

  python tools/stock_ledger/stock_ledger.py put  <ledger_dir> AMZN close_price 266.03 --period 2026-11-04 --unit USD --label measured --source yahoo_amzn_hist
  python tools/stock_ledger/stock_ledger.py get  <ledger_dir> AMZN fcf_ttm            # series
  python tools/stock_ledger/stock_ledger.py keys <ledger_dir> AMZN
  python tools/stock_ledger/stock_ledger.py model <ledger_dir> <out_dir> AMZN [--price-date 2026-11-04]
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ledger import View, append, make_line, read  # noqa: E402


def _parse_value(s: str):
    try:
        return json.loads(s)
    except json.JSONDecodeError:
        return s


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="JSON Ledger of stock-state primitives")
    sub = ap.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("put", help="append one line")
    p.add_argument("ledger_dir"); p.add_argument("ticker"); p.add_argument("key"); p.add_argument("value")
    p.add_argument("--period"); p.add_argument("--unit"); p.add_argument("--label", default="measured", choices=["measured", "modelled", "stated"])
    p.add_argument("--source"); p.add_argument("--note"); p.add_argument("--file", default="facts", choices=["facts", "assumptions"])

    g = sub.add_parser("get", help="resolved value(s) for a key")
    g.add_argument("ledger_dir"); g.add_argument("ticker"); g.add_argument("key"); g.add_argument("--period")

    k = sub.add_parser("keys", help="list keys")
    k.add_argument("ledger_dir"); k.add_argument("ticker")

    m = sub.add_parser("model", help="run the model and write outputs")
    m.add_argument("ledger_dir"); m.add_argument("out_dir"); m.add_argument("ticker"); m.add_argument("--price-date")

    a = ap.parse_args(argv)
    ld = Path(a.ledger_dir)

    if a.cmd == "put":
        ln = make_line(a.ticker, a.key, _parse_value(a.value), period=a.period, unit=a.unit, label=a.label, source=a.source, note=a.note)
        append(ld / f"{a.ticker}.{a.file}.jsonl", [ln])
        print(json.dumps(ln))
        return 0

    lines = read(ld / f"{a.ticker}.facts.jsonl") + read(ld / f"{a.ticker}.assumptions.jsonl")
    v = View(lines, a.ticker)
    if a.cmd == "get":
        if a.period:
            print(json.dumps(v.line(a.key, a.period), indent=2))
        else:
            ser = v.series(a.key)
            print(json.dumps(ser if ser else v.line(a.key), indent=2))
        return 0
    if a.cmd == "keys":
        print("\n".join(v.keys()))
        return 0
    if a.cmd == "model":
        from model import run
        md = run(a.ticker, ld, Path(a.out_dir), a.price_date)
        print(md)
        return 0
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
