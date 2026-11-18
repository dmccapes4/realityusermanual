"""Compute the current truth and the scenario model from the ledgers.

Reads  : <ledger_dir>/<TICKER>.facts.jsonl, <ledger_dir>/<TICKER>.assumptions.jsonl
Writes : <out_dir>/derived.jsonl  (modelled lines, one per computed number)
         <out_dir>/MODEL_<TICKER>_<YYYYMMDD>.md
         <out_dir>/<TICKER>_model_<YYYYMMDD>.png
"""

from __future__ import annotations

import datetime
from pathlib import Path
from typing import Any

from ledger import View, append, make_line, now_ts, read

YEARS = ["2027", "2028", "2029", "2030", "2031"]


def _fmt(v: float, nd: int = 1) -> str:
    return f"{v:,.{nd}f}"


def _b(v_millions: float, nd: int = 1) -> str:
    """millions → $B string."""
    return f"${v_millions / 1000:,.{nd}f}B"


# --------------------------------------------------------------------------------------------- derived

def derived_series(v: View) -> dict[str, dict[str, float]]:
    ocf = v.series("ocf_ttm")
    capex = v.series("capex_net_ttm")
    fcf = v.series("fcf_ttm")
    rev = v.series("revenue_ttm")
    opi = v.series("op_income_ttm")
    aws_oi = v.series("aws_op_income_ttm")
    aws_rev = v.series("aws_revenue_ttm")
    periods = sorted(set(ocf) & set(capex) & set(rev))
    out: dict[str, dict[str, float]] = {
        "capex_to_ocf_pct": {}, "capex_to_revenue_pct": {}, "ocf_margin_pct": {}, "fcf_margin_pct": {},
        "op_margin_ttm_pct": {}, "aws_share_of_op_income_pct": {}, "aws_share_of_revenue_pct": {},
        "nonaws_op_income_ttm": {},
    }
    for p in periods:
        out["capex_to_ocf_pct"][p] = round(capex[p] / ocf[p] * 100, 1)
        out["capex_to_revenue_pct"][p] = round(capex[p] / rev[p] * 100, 1)
        out["ocf_margin_pct"][p] = round(ocf[p] / rev[p] * 100, 1)
        out["fcf_margin_pct"][p] = round(fcf[p] / rev[p] * 100, 1)
        if p in opi:
            out["op_margin_ttm_pct"][p] = round(opi[p] / rev[p] * 100, 1)
        if p in opi and p in aws_oi:
            out["aws_share_of_op_income_pct"][p] = round(aws_oi[p] / opi[p] * 100, 1)
            out["nonaws_op_income_ttm"][p] = opi[p] - aws_oi[p]
        if p in aws_rev:
            out["aws_share_of_revenue_pct"][p] = round(aws_rev[p] / rev[p] * 100, 1)
    return out


def snapshot(v: View, base: str, price_date: str) -> dict[str, Any]:
    price = v.get("close_price", price_date)
    shares = v.get("shares_outstanding", base)
    mcap = price * shares  # USD millions
    cash = v.get("bs_cash", base) + v.get("bs_marketable_securities", base)
    debt = v.get("bs_lt_debt", base)
    net_debt = debt - cash
    ev = mcap + net_debt
    ocf = v.get("ocf_ttm", base)
    fcf = v.get("fcf_ttm", base)
    rev = v.get("revenue_ttm", base)
    opi = v.get("op_income_ttm", base)
    ni = v.get("net_income_ttm", base)
    nonop = v.get("nonoperating_income_ttm", base)
    dep = v.get("depreciation_ttm", base)
    capex_gross = v.get("capex_gross_ttm", base)
    pe = v.get("bs_pe_net", base)
    eq = v.get("bs_equity", base)
    snap = {
        "price": price, "price_date": price_date, "shares_m": shares, "market_cap": mcap, "net_debt": net_debt, "ev": ev,
        "p_ocf": mcap / ocf, "p_e_ttm": mcap / ni, "ev_to_op_income": ev / opi, "ev_to_revenue": ev / rev,
        "fcf_yield_pct": fcf / mcap * 100, "ocf_yield_pct": ocf / mcap * 100,
        "nonop_share_of_net_income_pct": nonop / ni * 100,
        "capex_gross_to_da": capex_gross / dep, "capex_gross_to_ocf_pct": capex_gross / ocf * 100,
        "ocf_9m_to_capex_gross_9m_pct": v.get("ocf_9m", base) / v.get("capex_gross_9m", base) * 100,
        "lt_debt_change_9m": debt - v.get("bs_lt_debt", "2025Q4"),
        "other_lt_liab_change_9m": v.get("bs_other_lt_liabilities", base) - v.get("bs_other_lt_liabilities", "2025Q4"),
        "cash_change_9m": v.get("bs_cash", base) - v.get("bs_cash", "2025Q4"),
        "pe_net_change_9m": pe - v.get("bs_pe_net", "2025Q4"),
        "aoci_change_9m": v.get("bs_aoci", base) - v.get("bs_aoci", "2025Q4"),
        "per_share": {
            "revenue": rev / shares, "ocf": ocf / shares, "fcf": fcf / shares, "op_income": opi / shares,
            "net_debt": net_debt / shares, "pe_net": pe / shares, "book": eq / shares,
            "aws_op_income": v.get("aws_op_income_ttm", base) / shares,
        },
    }
    return snap


# ------------------------------------------------------------------------------------------- scenarios

def run_scenario(v: View, sid: str, base: str, discount_pct: float, shares: float, net_debt: float) -> dict[str, Any]:
    rev = v.get("revenue_ttm", base)
    rows = []
    pv_fcf = 0.0
    r = 1 + discount_pct / 100
    for i, y in enumerate(YEARS, start=1):
        g = v.get(f"scn.{sid}.revenue_growth_pct", y)
        m = v.get(f"scn.{sid}.ocf_margin_pct", y)
        cx = v.get(f"scn.{sid}.capex", y)
        sale = v.get(f"scn.{sid}.asset_sale_proceeds", y) or 0
        rev = rev * (1 + g / 100)
        ocf = rev * m / 100
        capex = rev * float(cx.rstrip("%")) / 100 if isinstance(cx, str) else float(cx)
        fcf = ocf - capex + sale
        df = r ** i
        pv_fcf += fcf / df
        rows.append({"year": y, "revenue": rev, "revenue_growth_pct": g, "ocf": ocf, "ocf_margin_pct": m, "capex": capex,
                     "capex_to_revenue_pct": capex / rev * 100, "asset_sale": sale, "fcf": fcf, "discount_factor": df, "pv_fcf": fcf / df})
    mult = v.get(f"scn.{sid}.terminal_p_ocf")
    terminal = rows[-1]["ocf"] * mult
    pv_terminal = terminal / rows[-1]["discount_factor"]
    ev = pv_fcf + pv_terminal
    equity = ev - net_debt
    return {
        "id": sid, "name": v.get(f"scn.{sid}.name"), "story": v.get(f"scn.{sid}.story"), "rows": rows,
        "terminal_p_ocf": mult, "terminal_value": terminal, "pv_terminal": pv_terminal, "pv_fcf_sum": pv_fcf,
        "ev": ev, "equity": equity, "per_share": equity / shares,
        "cum_fcf_2027_2031": sum(x["fcf"] for x in rows),
        "terminal_share_of_ev_pct": pv_terminal / ev * 100,
    }


def sensitivity(v: View, sid: str, base: str, discount_pct: float, shares: float, net_debt: float, mults=(10, 13, 17, 20)) -> dict[int, float]:
    out = {}
    for mlt in mults:
        rev = v.get("revenue_ttm", base)
        pv = 0.0
        r = 1 + discount_pct / 100
        for i, y in enumerate(YEARS, start=1):
            rev *= 1 + v.get(f"scn.{sid}.revenue_growth_pct", y) / 100
            ocf = rev * v.get(f"scn.{sid}.ocf_margin_pct", y) / 100
            cx = v.get(f"scn.{sid}.capex", y)
            capex = rev * float(cx.rstrip("%")) / 100 if isinstance(cx, str) else float(cx)
            pv += (ocf - capex + (v.get(f"scn.{sid}.asset_sale_proceeds", y) or 0)) / r ** i
        pv += ocf * mlt / r ** len(YEARS)
        out[mlt] = (pv - net_debt) / shares
    return out


def implied_terminal_multiple(v: View, sid: str, base: str, discount_pct: float, shares: float, net_debt: float, price: float) -> float:
    """Terminal P/OCF that makes the scenario worth today's price."""
    rev = v.get("revenue_ttm", base)
    pv = 0.0
    r = 1 + discount_pct / 100
    for i, y in enumerate(YEARS, start=1):
        rev *= 1 + v.get(f"scn.{sid}.revenue_growth_pct", y) / 100
        ocf = rev * v.get(f"scn.{sid}.ocf_margin_pct", y) / 100
        cx = v.get(f"scn.{sid}.capex", y)
        capex = rev * float(cx.rstrip("%")) / 100 if isinstance(cx, str) else float(cx)
        pv += (ocf - capex + (v.get(f"scn.{sid}.asset_sale_proceeds", y) or 0)) / r ** i
    target_ev = price * shares + net_debt
    return (target_ev - pv) * r ** len(YEARS) / ocf


# ----------------------------------------------------------------------------------------------- chart

def chart(v: View, der: dict, scns: list[dict], path: Path, ticker: str) -> None:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, axes = plt.subplots(1, 3, figsize=(17, 5.2))
    ocf = v.series("ocf_ttm"); capex = v.series("capex_net_ttm"); fcf = v.series("fcf_ttm")
    ps = sorted(ocf)
    ax = axes[0]
    ax.plot(ps, [ocf[p] / 1000 for p in ps], marker="o", label="Operating cash flow (TTM)")
    ax.plot(ps, [capex[p] / 1000 for p in ps], marker="o", label="Capex, net (TTM)")
    ax.bar(ps, [fcf[p] / 1000 for p in ps], alpha=0.35, color="grey", label="Free cash flow (TTM)")
    ax.axhline(0, color="black", lw=0.7)
    ax.set_title(f"{ticker} measured: cash in, cash into plant, what is left ($B)")
    ax.tick_params(axis="x", rotation=45); ax.legend(fontsize=8); ax.grid(alpha=0.3)

    ax = axes[1]
    opi = v.series("op_income_ttm"); aws = v.series("aws_op_income_ttm")
    pp = [p for p in ps if p in opi and p in aws]
    ax.stackplot(pp, [aws[p] / 1000 for p in pp], [(opi[p] - aws[p]) / 1000 for p in pp], labels=["AWS operating income", "Everything else"], alpha=0.7)
    ax.set_title("Operating income TTM: AWS vs the rest ($B)")
    ax.tick_params(axis="x", rotation=45); ax.legend(fontsize=8, loc="upper left"); ax.grid(alpha=0.3)

    ax = axes[2]
    for s in scns:
        ax.plot(["2026Q3 TTM"] + YEARS, [fcf[ps[-1]] / 1000] + [r["fcf"] / 1000 for r in s["rows"]], marker="o", label=f"{s['id']}: {s['name'].split(':')[0]}  → ${s['per_share']:.0f}/sh")
    ax.axhline(0, color="black", lw=0.7)
    ax.set_title("Modelled FCF paths 2027–2031 ($B) and value/share")
    ax.tick_params(axis="x", rotation=45); ax.legend(fontsize=8); ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(path, dpi=130)
    plt.close(fig)


# ---------------------------------------------------------------------------------------------- report

def write_markdown(v: View, der: dict, snap: dict, scns: list[dict], sens: dict, implied: dict, chart_name: str, ticker: str, base: str, discount: float, path: Path) -> None:
    L = []
    w = L.append
    w(f"# {ticker} model — computed {datetime.date.today().isoformat()}")
    w("")
    w(f"Base period {base} TTM. Price {snap['price_date']} close ${snap['price']:.2f}. Everything in this file is `modelled` from `measured` and `stated` lines in the ledger; the arithmetic is in `tools/stock_ledger/model.py`. Dollar figures are USD billions unless marked.")
    w("")
    w(f"![chart]({chart_name})")
    w("")
    w("## 1. Measured series (TTM)")
    w("")
    ps = sorted(v.series("ocf_ttm"))
    w("| Period | Revenue | OCF | Capex net | FCF | Capex/OCF | Capex/Rev | OCF margin | AWS op inc | AWS share of op inc |")
    w("|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|")
    for p in ps:
        w(f"| {p} | {_b(v.get('revenue_ttm', p))} | {_b(v.get('ocf_ttm', p))} | {_b(v.get('capex_net_ttm', p))} | {_b(v.get('fcf_ttm', p))} | {der['capex_to_ocf_pct'][p]}% | {der['capex_to_revenue_pct'][p]}% | {der['ocf_margin_pct'][p]}% | {_b(v.get('aws_op_income_ttm', p))} | {der['aws_share_of_op_income_pct'].get(p, float('nan'))}% |")
    w("")
    w("Reading: OCF grew 49% in two years; net capex grew 224%. FCF went from +$47.7B to −$42.4B across the same eight quarters. AWS is 58% of operating income on 20% of revenue.")
    w("")
    w("## 2. Snapshot at the price")
    w("")
    w(f"- Market cap {_b(snap['market_cap'], 0)} on {snap['shares_m']:,}M shares; net debt {_b(snap['net_debt'])} (LT debt − cash − marketable securities; leases and current debt excluded); EV {_b(snap['ev'], 0)}.")
    w(f"- P/OCF {snap['p_ocf']:.1f}x; EV/operating income {snap['ev_to_op_income']:.1f}x; EV/revenue {snap['ev_to_revenue']:.2f}x; P/E (TTM) {snap['p_e_ttm']:.1f}x.")
    w(f"- OCF yield {snap['ocf_yield_pct']:.1f}%; FCF yield {snap['fcf_yield_pct']:.1f}%.")
    w(f"- {snap['nonop_share_of_net_income_pct']:.0f}% of TTM net income is non-operating income (mostly Anthropic mark-ups). The P/E above is flattered by it; EV/operating income is not.")
    w(f"- Gross capex TTM is {snap['capex_gross_to_da']:.1f}x depreciation: the plant is growing far faster than it is being expensed. Gross capex is {snap['capex_gross_to_ocf_pct']:.0f}% of OCF on a TTM basis, {snap['ocf_9m_to_capex_gross_9m_pct']:.0f}% covered by OCF in the first nine months of 2026.")
    w(f"- Nine months of 2026: LT debt +{_b(snap['lt_debt_change_9m'])}, other long-term liabilities +{_b(snap['other_lt_liab_change_9m'])}, cash {_b(snap['cash_change_9m'])}, net P&E +{_b(snap['pe_net_change_9m'])}, accumulated OCI +{_b(snap['aoci_change_9m'])} (unrealised Anthropic gains sitting in equity).")
    w("")
    w("### What one share is, today (holding is buying at this price)")
    w("")
    w(f"| per share | $ |\n|---|---:|")
    for k, lab in [("revenue", "Revenue (TTM)"), ("op_income", "Operating income (TTM)"), ("aws_op_income", "of which AWS"), ("ocf", "Operating cash flow (TTM)"), ("fcf", "Free cash flow (TTM)"), ("pe_net", "Property & equipment, net"), ("net_debt", "Net debt"), ("book", "Book equity")]:
        w(f"| {lab} | {snap['per_share'][k]:.2f} |")
    w(f"| **Price** | **{snap['price']:.2f}** |")
    w("")
    w("## 3. Scenarios 2027–2031")
    w("")
    w(f"Discount rate {discount:.0f}%. Terminal value = 2031 OCF × a P/OCF multiple (the market's own habit for this stock), discounted five years. Scenario inputs are `modelled` lines under `scn.*` in `AMZN.assumptions.jsonl`; change a line, rerun.")
    w("")
    for s in scns:
        w(f"### {s['id']}. {s['name']}")
        w("")
        w(s["story"])
        w("")
        w("| Year | Revenue | growth | OCF | margin | Capex | capex/rev | Asset sales | FCF | PV(FCF) |")
        w("|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|")
        for r in s["rows"]:
            w(f"| {r['year']} | {_b(r['revenue'], 0)} | {r['revenue_growth_pct']}% | {_b(r['ocf'], 0)} | {r['ocf_margin_pct']}% | {_b(r['capex'], 0)} | {r['capex_to_revenue_pct']:.0f}% | {_b(r['asset_sale'], 0)} | {_b(r['fcf'], 0)} | {_b(r['pv_fcf'], 0)} |")
        w("")
        w(f"Cumulative FCF 2027–31 {_b(s['cum_fcf_2027_2031'], 0)}; terminal {s['terminal_p_ocf']}x × 2031 OCF = {_b(s['terminal_value'], 0)} (PV {_b(s['pv_terminal'], 0)}, {s['terminal_share_of_ev_pct']:.0f}% of EV). EV {_b(s['ev'], 0)}, equity {_b(s['equity'], 0)}, **${s['per_share']:.0f} per share**. Implied terminal multiple to justify today's ${snap['price']:.0f}: **{implied[s['id']]:.1f}x**.")
        w("")
    w("### Sensitivity: value per share vs terminal P/OCF")
    w("")
    mults = list(next(iter(sens.values())).keys())
    w("| Scenario | " + " | ".join(f"{m}x" for m in mults) + " |")
    w("|---|" + "---:|" * len(mults))
    for sid, row in sens.items():
        w(f"| {sid} | " + " | ".join(f"${x:.0f}" for x in row.values()) + " |")
    w("")
    w("## 4. What the arithmetic says")
    w("")
    a, b, c = scns
    w(f"- At ${snap['price']:.0f} the market is paying for scenario A with a terminal multiple of about {implied['A']:.0f}x OCF, i.e. it is paying for the capex to end and the operating cash flow to stay. That is Justin's frame, and it is internally consistent; it is not a measurement of whether the capex ends.")
    w(f"- Scenario A produces **no positive free cash flow until {next((r['year'] for r in a['rows'] if r['fcf'] > 0), 'after 2031')}** even on consensus inputs. The 'largest FCF in the world' is a 2030s statement.")
    w(f"- Scenario B ({b['per_share']:.0f}) is the policy case. Its damage is mostly in the terminal multiple, not in 2027: 2027 capex is contracted either way. If the horizon is retarded, the stock reprices before the cash flows change.")
    w(f"- Scenario C ({c['per_share']:.0f}) is the liquidation template. Note what it needs: AWS growth to 4–5%, a 17% OCF margin, and a 10x multiple. A Global Crossing outcome for Amazon itself is not what the operator claimed; he said Amazon *sells* and the pure-plays *default*. The ledger agrees with that distinction: Amazon funds ~78% of gross capex from operating cash; the 1998–2001 fiber builders funded it from debt and equity raises.")
    w(f"- Dot-com marker worth tracking: gross capex / depreciation is {snap['capex_gross_to_da']:.1f}x. For Global Crossing the network cost $13.7B against $22.4B of assets at bankruptcy and sold for cents. Amazon's number is the rate at which the plant could become stranded; it is not evidence that it will.")
    w("")
    w("## 5. Provenance")
    w("")
    w("Measured lines: Amazon Q3 2026 press release and 10-Q (full tables), Q4 2025 release (tables), Yahoo historical prices. Stated lines: Amazon guidance, BMO and FPI analyst tallies, AP/Reuters/Guardian election results, congress.gov bill text, Heinrich floor statement, EIA weekly figures via secondary summaries (EIA tables themselves not opened). Modelled: every number in §3 and the ratios in §1–2. Nothing from the Gemini session is used as a measurement.")
    path.write_text("\n".join(L) + "\n", encoding="utf-8")


# ------------------------------------------------------------------------------------------------ main

def run(ticker: str, ledger_dir: Path, out_dir: Path, price_date: str | None = None) -> Path:
    lines = read(ledger_dir / f"{ticker}.facts.jsonl") + read(ledger_dir / f"{ticker}.assumptions.jsonl")
    v = View(lines, ticker)
    base = v.get("model.base_period")
    discount = v.get("model.discount_rate_pct")
    price_date = price_date or max(v.series("close_price"))
    der = derived_series(v)
    snap = snapshot(v, base, price_date)
    sids = sorted({k.split(".")[1] for k in v.keys() if k.startswith("scn.")})
    scns = [run_scenario(v, s, base, discount, snap["shares_m"], snap["net_debt"]) for s in sids]
    sens = {s: sensitivity(v, s, base, discount, snap["shares_m"], snap["net_debt"]) for s in sids}
    implied = {s: implied_terminal_multiple(v, s, base, discount, snap["shares_m"], snap["net_debt"], snap["price"]) for s in sids}

    out_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.date.today().strftime("%Y%m%d")
    chart_name = f"{ticker}_model_{stamp}.png"
    chart(v, der, scns, out_dir / chart_name, ticker)
    md = out_dir / f"MODEL_{ticker}_{stamp}.md"
    write_markdown(v, der, snap, scns, sens, implied, chart_name, ticker, base, discount, md)

    ts = now_ts()
    dl: list[dict] = []
    for k, ser in der.items():
        for p, val in ser.items():
            dl.append(make_line(ticker, f"derived.{k}", round(val, 1), period=p, label="modelled", note="model.derived_series", ts=ts))
    for k, val in snap.items():
        if k == "per_share":
            for kk, vv in val.items():
                dl.append(make_line(ticker, f"derived.per_share.{kk}", round(vv, 2), period=price_date, unit="USD", label="modelled", ts=ts))
        elif isinstance(val, (int, float)):
            dl.append(make_line(ticker, f"derived.{k}", round(val, 2), period=price_date, label="modelled", ts=ts))
    for s in scns:
        for r in s["rows"]:
            for kk in ("revenue", "ocf", "capex", "fcf"):
                dl.append(make_line(ticker, f"scn.{s['id']}.out.{kk}", round(r[kk]), period=r["year"], unit="USD_millions", label="modelled", ts=ts))
        dl.append(make_line(ticker, f"scn.{s['id']}.out.per_share", round(s["per_share"], 2), period=price_date, unit="USD", label="modelled", ts=ts))
        dl.append(make_line(ticker, f"scn.{s['id']}.out.implied_terminal_p_ocf", round(implied[s["id"]], 2), period=price_date, unit="x", label="modelled", ts=ts))
    append(out_dir / "derived.jsonl", dl)
    return md
