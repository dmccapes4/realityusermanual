"""Seed the AMZN ledger from the documents read on 2026-11-05.

Every `measured` line below was read from the named source on that date (the press release and 10-Q
tables were extracted in full; news pages were read for the quoted figure only). Re-running appends
nothing if the ledger already has the same (key, period, value); it appends a correction line otherwise.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ledger import append, make_line, read, resolve  # noqa: E402

TS = "2026-11-05T07:30:00Z"
T = "AMZN"
M = "USD_millions"

SOURCES = [
    ("amzn_q3_2026_pr", "Amazon.com Announces Third Quarter Results (Oct 29, 2026)", "https://ir.aboutamazon.com/news-release/news-release-details/2026/Amazon-com-Announces-Third-Quarter-Results/", "full text incl. supplemental tables"),
    ("amzn_q3_2026_10q", "Form 10-Q, period ended September 30, 2026", "https://www.sec.gov/Archives/edgar/data/1018724/000101872426000040/amzn-20260930.htm", "income statement, segment table"),
    ("amzn_q4_2025_pr", "Amazon.com Announces Fourth Quarter Results (Feb 5, 2026)", "https://ir.aboutamazon.com/news-release/news-release-details/2026/Amazon-com-Announces-Fourth-Quarter-Results/default.aspx", "supplemental tables, balance sheet"),
    ("yahoo_amzn_hist", "Yahoo Finance AMZN historical prices", "https://finance.yahoo.com/quote/AMZN/history/", "Sep 1 – Nov 4 2026 rows"),
    ("cnbc_q3_2026", "CNBC: Amazon (AMZN) Q3 earnings report 2026 (Oct 29, 2026)", "https://www.cnbc.com/2026/10/29/amazon-amzn-q3-earnings-report-2026.html", "capex figures, FactSet estimate"),
    ("techcrunch_q3_2026", "TechCrunch: AWS will be a $1T business, Jassy says (Oct 29, 2026)", "https://techcrunch.com/2026/10/29/aws-will-be-a-1t-business-jassy-says-but-first-it-will-spend-big/", "Jassy quotes"),
    ("bmo_note_2026_10", "BMO Capital Markets note via StreetInsider (Oct/Nov 2026)", "https://www.streetinsider.com/General+News/BMO+Capital+Markets+reiterates+this+AI+hyperscaler+as+its+top+pick/27286088.html", "targets, backlog, capex estimates"),
    ("fpi_amzn_2026_11_02", "Fair Price Index AMZN report (Nov 2, 2026)", "https://www.fairpriceindex.com/stock/AMZN/reports/2026-11-02", "consensus tally, target range"),
    ("ap_midterms_2026", "AP: Democrats win the US House and Senate (Nov 3, 2026)", "https://apnews.com/article/midterm-election-house-senate-democrats-republicans-trump-f126e12e05b579a327b98481c0ae2226", "lede"),
    ("reuters_midterms_2026", "Reuters: Democrats flex congressional majorities (Nov 4, 2026)", "https://www.reuters.com/3fec1b0a85a0/legal/government/democrats-seize-congress-sweeping-midterm-repudiation-trump-2026-11-04/", "seat counts"),
    ("guardian_midterms_2026", "Guardian live results (Nov 4, 2026 05:26 EST)", "https://www.theguardian.com/us-news/ng-interactive/2026/nov/03/midterm-elections-full-results-senate-house-governor-races", "Senate 54–44 with 33/35 called; House 228–139 with 367/435 called"),
    ("congress_s4214", "S.4214 Artificial Intelligence Data Center Moratorium Act (introduced Mar 25, 2026)", "https://www.congress.gov/bill/119th-congress/senate-bill/4214/text", "bill text §3"),
    ("heinrich_grid_savings", "Sen. Heinrich floor statement on GRID Savings Act (Senate ENR Dems)", "https://www.energy.senate.gov/press/dem/heinrich-offers-his-grid-savings-act-to-force-ai-data-centers-to-pay-for-grid-upgrades-highlights-how-husted-backed-bill-falls-short/", "statement; Dallas Fed figure quoted second-hand"),
    ("nbc_ratepayer_2026", "NBC: Senate Democrats block Husted-led bill on data centers", "https://www.nbcnews.com/politics/congress/senate-democrats-block-sen-husted-led-bill-data-centers-calling-toothl-rcna600269", "vote counts"),
    ("eia_gas_wk_2026_11_02", "EIA weekly retail gasoline, week of Nov 2, 2026 (via political.org / newspaperjoint summaries)", "https://political.org/explained/gas-prices-iran-oil/", "price lines; EIA table itself not opened"),
    ("eia_exports_2026_10_30", "EIA weekly crude exports, week ended Oct 30, 2026 (via fxnews.ai)", "https://fxnews.ai/news/us-crude-exports-drop-cushing-stocks-rise-october-30-2026/", "export rows; EIA table itself not opened"),
    ("pricegroup_2026_11_03", "Price Futures Group Energy Report 11/03/2026", "https://blog.pricegroup.com/2026/11/03/diplomacy-and-barrels-the-energy-report-11-03-2026/", "Brent/WTI settles"),
    ("latimes_telecom_2002", "LA Times: Too Much, Too Soon for Telecom (Jun 30, 2002)", "https://www.latimes.com/archives/la-xpm-2002-jun-30-fi-billions30-story.html", "capex total"),
    ("wsj_fiber_glut_2002", "WSJ: Wildly Optimistic Data Drove Telecoms to Build Fiber Glut (Sep 2002)", "https://www.wsj.com/articles/SB1032982764442483713", "2.7% lit; bandwidth price decline"),
    ("house_fin_svcs_gx_2002", "House Financial Services memo on Global Crossing bankruptcy (Mar 21, 2002)", "https://financialservices.house.gov/media/pdf/032102wm.pdf", "assets/debts, network cost"),
    ("gpueconomy_h100_2026_11_05", "GPU Economy Cloud GPU Price Index, H100 on-demand (Nov 5, 2026)", "https://gpueconomy.com/price-index", "index page"),
    ("compute_terminal_h100_2026_11_04", "Compute Terminal H100 rental price history (Nov 4, 2026)", "https://compute-terminal.com/gpu-prices/h100", "summary figures"),
    ("bargo_cti_2026_11_01", "Bargo Compute Tightness Index (Nov 1, 2026)", "https://www.bargo.ai/compute-tightness", "headline and per-GPU table"),
    ("eu_ai_act_service_desk", "EU AI Act Service Desk FAQ and implementation timeline", "https://ai-act-service-desk.ec.europa.eu/en/faq", "enforcement and Digital Omnibus sections"),
    ("steptoe_ai_tracker_2026_11", "Steptoe Federal AI Legislative Tracker, November 2026", "https://www.steptoe.com/a/web/u3UBoABYv2v3ehpGebnt9q/steptoe-federal-ai-legislative-tracker_november-2026.pdf", "chatbot bill rows"),
    ("thehill_dems_ai_2026_11", "The Hill: Democrats eye Big Tech after midterm wins (Nov 2026)", "https://thehill.com/policy/technology/6197847-democrats-big-tech-ai-regulations-2026-midterm-wins/", "lede and quotes"),
    ("gemini_chat_2026_11_04", "GEMINI_CHAT_DATA_CENTERS_WORLD_IS_FLAT_20261104.md (operator's Gemini session)", "misc/justin_texts_amzn_202611/GEMINI_CHAT_DATA_CENTERS_WORLD_IS_FLAT_20261104.md", "full text; Gemini's numbers are NOT measurements"),
    ("imessage_run_20261105", "imessage_thread run justin_texts_amzn_202611_20261105T054428Z transcript", "misc/justin_texts_amzn_202611/runs/justin_texts_amzn_202611_20261105T054428Z/transcript.jsonl", "16 messages"),
]


def L(key, value, *, period=None, unit=None, label="measured", source=None, note=None):
    return make_line(T, key, value, period=period, unit=unit, label=label, source=source, note=note, ts=TS)


def facts() -> list[dict]:
    out: list[dict] = []
    S = "amzn_q3_2026_pr"
    S4 = "amzn_q4_2025_pr"

    # ---- TTM cash-flow series (Supplemental Financial Information tables)
    ocf = {"2024Q3": 112706, "2024Q4": 115877, "2025Q1": 113903, "2025Q2": 121137, "2025Q3": 130691, "2025Q4": 139514, "2026Q1": 148531, "2026Q2": 161403, "2026Q3": 168300}
    capex_net = {"2024Q3": 64959, "2024Q4": 77658, "2025Q1": 87978, "2025Q2": 102953, "2025Q3": 115903, "2025Q4": 128320, "2026Q1": 147299, "2026Q2": 169007, "2026Q3": 210657}
    fcf = {"2024Q3": 47747, "2024Q4": 38219, "2025Q1": 25925, "2025Q2": 18184, "2025Q3": 14788, "2025Q4": 11194, "2026Q1": 1232, "2026Q2": -7604, "2026Q3": -42357}
    for p, v in ocf.items():
        out.append(L("ocf_ttm", v, period=p, unit=M, source=S4 if p <= "2025Q4" else S, note="Operating cash flow -- trailing twelve months"))
    for p, v in capex_net.items():
        out.append(L("capex_net_ttm", v, period=p, unit=M, source=S4 if p <= "2025Q4" else S, note="Purchases of property and equipment, net of proceeds from sales and incentives -- TTM"))
    for p, v in fcf.items():
        out.append(L("fcf_ttm", v, period=p, unit=M, source=S4 if p <= "2025Q4" else S, note="Free cash flow -- TTM = OCF TTM − capex_net TTM (Amazon's own definition)"))

    # ---- revenue / operating income
    rev_q = {"2024Q3": 158877, "2024Q4": 187792, "2025Q1": 155667, "2025Q2": 167702, "2025Q3": 180169, "2025Q4": 213386, "2026Q1": 181519, "2026Q2": 200606, "2026Q3": 201944}
    rev_ttm = {"2024Q3": 620128, "2024Q4": 637959, "2025Q1": 650313, "2025Q2": 670038, "2025Q3": 691330, "2025Q4": 716924, "2026Q1": 742776, "2026Q2": 775680, "2026Q3": 797455}
    opinc_q = {"2024Q3": 17411, "2024Q4": 21203, "2025Q1": 18405, "2025Q2": 19171, "2025Q3": 17422, "2025Q4": 24977, "2026Q3": 28076}
    opinc_ttm = {"2024Q3": 60599, "2024Q4": 68593, "2025Q1": 71691, "2025Q2": 76190, "2025Q3": 76201, "2025Q4": 79975, "2026Q1": 85422, "2026Q2": 93712, "2026Q3": 104366}
    for p, v in rev_q.items():
        out.append(L("revenue_q", v, period=p, unit=M, source=S4 if p <= "2025Q4" else S))
    for p, v in rev_ttm.items():
        out.append(L("revenue_ttm", v, period=p, unit=M, source=S4 if p <= "2025Q4" else S))
    for p, v in opinc_q.items():
        out.append(L("op_income_q", v, period=p, unit=M, source=S4 if p <= "2025Q4" else S))
    for p, v in opinc_ttm.items():
        out.append(L("op_income_ttm", v, period=p, unit=M, source=S4 if p <= "2025Q4" else S))
    out.append(L("op_margin_q_pct", 13.9, period="2026Q3", unit="pct", source=S, note="highest operating margin in Amazon's history (press release)"))

    # ---- AWS
    aws_q = {"2025Q2": 30873, "2025Q3": 33006, "2025Q4": 35579, "2026Q1": 37587, "2026Q2": 42232, "2026Q3": 45984}
    aws_ttm = {"2024Q3": 102974, "2024Q4": 107556, "2025Q1": 111786, "2025Q2": 116378, "2025Q3": 121932, "2025Q4": 128725, "2026Q1": 137045, "2026Q2": 148404, "2026Q3": 161382}
    aws_oi_q = {"2024Q3": 10447, "2024Q4": 10632, "2025Q1": 11547, "2025Q2": 10160, "2025Q3": 11434, "2025Q4": 12465, "2026Q1": 14161, "2026Q2": 16621, "2026Q3": 17773}
    aws_oi_ttm = {"2024Q3": 36369, "2024Q4": 39834, "2025Q1": 41960, "2025Q2": 42786, "2025Q3": 43773, "2025Q4": 45606, "2026Q1": 48220, "2026Q2": 54681, "2026Q3": 61020}
    aws_growth = {"2025Q2": 17, "2025Q3": 20, "2025Q4": 24, "2026Q1": 28, "2026Q2": 37, "2026Q3": 39}
    for p, v in aws_q.items():
        out.append(L("aws_revenue_q", v, period=p, unit=M, source=S4 if p <= "2025Q4" else S))
    for p, v in aws_ttm.items():
        out.append(L("aws_revenue_ttm", v, period=p, unit=M, source=S4 if p <= "2025Q4" else S))
    for p, v in aws_oi_q.items():
        out.append(L("aws_op_income_q", v, period=p, unit=M, source=S4 if p <= "2025Q4" else S))
    for p, v in aws_oi_ttm.items():
        out.append(L("aws_op_income_ttm", v, period=p, unit=M, source=S4 if p <= "2025Q4" else S))
    for p, v in aws_growth.items():
        out.append(L("aws_revenue_growth_yoy_pct", v, period=p, unit="pct", source=S4 if p <= "2025Q4" else S, note="excluding F/X per supplemental table"))
    out.append(L("aws_op_margin_q_pct", 38.7, period="2026Q3", unit="pct", source=S))
    out.append(L("aws_op_margin_q_pct", 39.4, period="2026Q2", unit="pct", source=S))
    out.append(L("aws_run_rate_annualized", 184000, period="2026Q3", unit=M, source=S, note="press release: $184 billion annualized revenue run rate"))

    # ---- quarterly cash flow detail (10-Q / press release cash flow statement)
    out.append(L("capex_gross_q", 77259, period="2026Q3", unit=M, source=S, note="Purchases of property and equipment, three months"))
    out.append(L("capex_gross_q", 35095, period="2025Q3", unit=M, source=S))
    out.append(L("capex_gross_9m", 175670, period="2026Q3", unit=M, source=S, note="nine months ended Sep 30 2026"))
    out.append(L("capex_gross_9m", 92297, period="2025Q3", unit=M, source=S))
    out.append(L("capex_gross_ttm", 215192, period="2026Q3", unit=M, source=S))
    out.append(L("capex_gross_ttm", 120131, period="2025Q3", unit=M, source=S))
    out.append(L("ocf_9m", 113841, period="2026Q3", unit=M, source=S))
    out.append(L("ocf_9m", 85055, period="2025Q3", unit=M, source=S))
    out.append(L("ocf_q", 42422, period="2026Q3", unit=M, source=S))
    out.append(L("ocf_q", 35525, period="2025Q3", unit=M, source=S))
    out.append(L("depreciation_q", 20949, period="2026Q3", unit=M, source=S, note="D&A of property and equipment and capitalized content costs, operating lease assets, and other"))
    out.append(L("depreciation_q", 16796, period="2025Q3", unit=M, source=S))
    out.append(L("depreciation_ttm", 79353, period="2026Q3", unit=M, source=S))
    out.append(L("depreciation_ttm", 65756, period="2025Q4", unit=M, source=S4))
    out.append(L("depreciation_ttm", 52795, period="2024Q4", unit=M, source=S4))
    out.append(L("pe_acquired_not_yet_paid_increase_ttm", 26779, period="2026Q3", unit=M, source=S, note="Increase in property and equipment acquired but not yet paid (TTM) — capex incurred, cash not yet out"))
    out.append(L("pe_finance_leases_ttm", 4543, period="2026Q3", unit=M, source=S, note="Property and equipment acquired under finance leases (TTM)"))
    out.append(L("nonoperating_income_ttm", 69012, period="2026Q3", unit=M, source=S, note="Non-operating (income) expense, net, TTM — sign flipped to income; driven by Anthropic investment gains; inflates net income, not operating cash"))
    out.append(L("net_income_ttm", 134779, period="2026Q3", unit=M, source=S))
    out.append(L("net_income_q", 20685, period="2026Q3", unit=M, source=S))
    out.append(L("diluted_eps_q", 1.89, period="2026Q3", unit="USD", source=S))

    # ---- balance sheet
    bs = {
        "2024Q4": {"cash": 78779, "marketable_securities": 22423, "pe_net": 252665, "lt_debt": 52623},
        "2025Q4": {"cash": 86810, "marketable_securities": 36219, "pe_net": 357025, "lt_debt": 65648, "other_lt_liabilities": 35985, "total_assets": 818042, "equity": 411065},
        "2026Q3": {"cash": 55783, "marketable_securities": 58443, "pe_net": 508862, "lt_debt": 173125, "other_lt_liabilities": 99858, "total_assets": 1243390, "equity": 613601, "other_assets": 358775, "aoci": 102278},
    }
    for p, d in bs.items():
        for k, v in d.items():
            src = S if p == "2026Q3" else S4
            out.append(L(f"bs_{k}", v, period=p, unit=M, source=src))
    out.append(L("bs_other_assets", 122607, period="2025Q4", unit=M, source=S))
    out.append(L("bs_aoci", 28230, period="2025Q4", unit=M, source=S))

    # ---- shares, price
    shares = {"2024Q4": 10593, "2025Q4": 10731, "2026Q2": 10783, "2026Q3": 10811}
    for p, v in shares.items():
        out.append(L("shares_outstanding", v, period=p, unit="millions", source=S4 if p <= "2025Q4" else S))
    out.append(L("diluted_shares_q", 10929, period="2026Q3", unit="millions", source="amzn_q3_2026_10q"))
    px = {"2026-09-30": 249.15, "2026-10-28": 254.60, "2026-10-29": 243.79, "2026-10-30": 240.35, "2026-11-02": 245.63, "2026-11-03": 250.69, "2026-11-04": 266.03}
    for d, v in px.items():
        out.append(L("close_price", v, period=d, unit="USD", source="yahoo_amzn_hist"))
    out.append(L("price_52w_high", 284.92, period="2026-11-04", unit="USD", source="yahoo_amzn_hist", note="sharecast figure shown alongside; not re-checked"))
    out.append(L("price_52w_low", 198.79, period="2026-11-04", unit="USD", source="yahoo_amzn_hist", note="sharecast figure shown alongside; not re-checked"))

    # ---- guidance and management statements (stated)
    out.append(L("guide_capex_2026", 220000, period="2026", unit=M, label="stated", source=S, note="'We continue to expect 2026 cash capital expenditures to be approximately $220 billion.' Oct 29 2026. Was ~$200B on Feb 5 2026 (Q4'25 PR)."))
    out.append(L("guide_capex_2026_prior", 200000, period="2026", unit=M, label="stated", source=S4, note="Feb 5 2026 guidance, superseded Jul 30 2026"))
    out.append(L("guide_q4_2026_net_sales_low", 240000, period="2026Q4", unit=M, label="stated", source=S))
    out.append(L("guide_q4_2026_net_sales_high", 247000, period="2026Q4", unit=M, label="stated", source=S))
    out.append(L("guide_q4_2026_op_income_low", 28500, period="2026Q4", unit=M, label="stated", source=S))
    out.append(L("guide_q4_2026_op_income_high", 33500, period="2026Q4", unit=M, label="stated", source=S))
    out.append(L("mgmt_aws_growth_2027_2028", "over 40% in each of 2027 and 2028", period="2027", label="stated", source=S, note="Jassy, Q3 2026 press release"))
    out.append(L("mgmt_capex_2027", "meaningfully more than 2026", period="2027", label="stated", source="techcrunch_q3_2026", note="Jassy, Q3 2026 call"))
    out.append(L("mgmt_capacity", "still lacks enough capacity to meet 2026 demand", period="2026", label="stated", source="cnbc_q3_2026", note="Jassy, Jul 30 and Oct 29 2026 calls; a claim about demand, not a measurement of it"))
    out.append(L("aws_backlog", 578000, period="2026Q3", unit=M, label="stated", source="bmo_note_2026_10", note="'$578 billion backlog' quoted by BMO; the figure appears in Amazon's 10-Q as remaining performance obligations but that table was not opened here"))

    # ---- analyst frame (stated)
    out.append(L("analyst_consensus_rating", "buy: 84 buy / 10 hold / 1 sell", period="2026-11-02", label="stated", source="fpi_amzn_2026_11_02"))
    out.append(L("analyst_target_median", 329.50, period="2026-11-02", unit="USD", label="stated", source="fpi_amzn_2026_11_02"))
    out.append(L("analyst_target_low", 250.0, period="2026-11-02", unit="USD", label="stated", source="fpi_amzn_2026_11_02", note="D.A. Davidson, Raymond James"))
    out.append(L("analyst_target_high", 390.0, period="2026-11-02", unit="USD", label="stated", source="bmo_note_2026_10", note="BMO, Top Pick"))
    out.append(L("analyst_capex_2027_bmo", 320000, period="2027", unit=M, label="stated", source="bmo_note_2026_10"))
    out.append(L("analyst_capex_2028_bmo", 335000, period="2028", unit=M, label="stated", source="bmo_note_2026_10"))
    out.append(L("analyst_net_sales_2026_bmo", 831000, period="2026", unit=M, label="stated", source="bmo_note_2026_10"))
    out.append(L("analyst_net_sales_2027_bmo", 974000, period="2027", unit=M, label="stated", source="bmo_note_2026_10"))
    out.append(L("analyst_frame", "AWS >40% growth and $578B backlog justify capex; capex normalises later; FCF drag is temporary", period="2026-11", label="stated", source="fpi_amzn_2026_11_02", note="Justin's 'analysts say AMZN is undervalued because low FCF is capex' is this frame (imessage 2026-11-03)"))
    out.append(L("dcf_fair_value_fpi", 166.54, period="2026-11-02", unit="USD", label="stated", source="fpi_amzn_2026_11_02", note="one vendor's blended DCF; shown as the bear anchor, not endorsed"))

    # ---- politics / regulation
    out.append(L("congress_control_2027", "Democrats, both chambers", period="2026-11-04", label="measured", source="ap_midterms_2026", note="AP call Nov 3 2026; seated Jan 2027"))
    out.append(L("senate_seats_dem", 54, period="2026-11-04", unit="seats", source="guardian_midterms_2026", note="33/35 races called at time of read; Reuters: 'at least 54-44'"))
    out.append(L("house_seats_dem_called", 228, period="2026-11-04", unit="seats", source="guardian_midterms_2026", note="367/435 called at time of read; NBC projects ≥259"))
    out.append(L("midterm_issue_iran_war", True, period="2026-11-04", label="measured", source="ap_midterms_2026", note="AP: 'high prices, the Iran war'; Reuters: Iran war's role in cost of living"))
    out.append(L("bill_s4214_status", "introduced Mar 25 2026; referred to Commerce; no further action", period="2026-11-05", label="measured", source="congress_s4214", note="AI Data Center Moratorium Act (Sanders/Ocasio-Cortez): halts AI data centers >20 MW or >20 kW/rack until conditions met"))
    out.append(L("bill_grid_savings_act", "Heinrich (D-NM); requires large-load customers to pay for grid connection; blocked by unanimous-consent objection", period="2026", label="measured", source="heinrich_grid_savings"))
    out.append(L("bill_ratepayer_protection_act", "passed House 417-3; failed Senate cloture 57-43; Democrats called it toothless", period="2026", label="measured", source="nbc_ratepayer_2026"))
    out.append(L("electricity_price_effect_dc_pct", "2 to 6 (now), 20 to 30 (by 2028)", period="2026", unit="pct", label="stated", source="heinrich_grid_savings", note="Dallas Fed estimate quoted by Heinrich; Dallas Fed paper not opened"))

    # ---- petroleum (the operator's supply/demand argument)
    out.append(L("us_regular_gasoline_avg", 4.153, period="2026-W44", unit="USD_per_gallon", source="eia_gas_wk_2026_11_02", note="EIA weekly, week of Nov 2 2026; −0.116 w/w; +1.134 y/y"))
    out.append(L("us_regular_gasoline_avg", 4.35, period="2026-W40", unit="USD_per_gallon", source="eia_gas_wk_2026_11_02", note="four weeks earlier"))
    out.append(L("brent_settle", 104.77, period="2026-11-02", unit="USD_per_bbl", source="pricegroup_2026_11_03"))
    out.append(L("wti_settle", 96.46, period="2026-11-02", unit="USD_per_bbl", source="pricegroup_2026_11_03"))
    out.append(L("brent_settle", 116.72, period="2026-10-23", unit="USD_per_bbl", source="eia_gas_wk_2026_11_02", note="highest since Apr 29 2026 (political.org)"))
    out.append(L("us_crude_exports_mbd", 3.675, period="2026-W44", unit="million_bbl_per_day", source="eia_exports_2026_10_30", note="week ended Oct 30; 4-wk avg 4.135, 4.9% below a year earlier"))
    out.append(L("us_crude_exports_mbd", 4.854, period="2026-W43", unit="million_bbl_per_day", source="eia_exports_2026_10_30"))
    out.append(L("hormuz_transits_vs_prewar_pct", -70, period="2026-10-28", unit="pct", label="stated", source="eia_gas_wk_2026_11_02", note="UKMTO weekly assessment Oct 31 via political.org; Kpler counts Gulf flows incl. alternate routes ABOVE prewar — the two measures disagree on what is counted"))

    # ---- compute price: the gauge for the matmul-floor claim
    out.append(L("compute.h100_on_demand_median_usd_hr", 3.27, period="2026-W45", unit="USD_per_GPU_hour", source="gpueconomy_h100_2026_11_05", note="week of Nov 2 2026, provisional; October monthly avg 4.20; +19% y/y per TechFlow summary"))
    out.append(L("compute.h100_advertised_median_usd_hr", 3.81, period="2026-W45", unit="USD_per_GPU_hour", source="compute_terminal_h100_2026_11_04", note="46 providers; $2.99 in week of Nov 3 2025 (+27.5% y/y)"))
    out.append(L("compute.h100_marketplace_usd_hr", 2.41, period="2026-11-04", unit="USD_per_GPU_hour", source="compute_terminal_h100_2026_11_04"))
    out.append(L("compute.h100_hyperscaler_list_usd_hr", 10.04, period="2026-11-04", unit="USD_per_GPU_hour", source="compute_terminal_h100_2026_11_04", note="4 of 4 hyperscalers; the AWS-class price vs the neocloud price"))
    out.append(L("compute.tightness_index", 57.8, period="2026-11-01", unit="index_0_100", source="bargo_cti_2026_11_01", note="'balanced', −3.4 on the month; H100 spot 43% under on-demand"))
    out.append(L("compute.matmul_floor_reached", False, period="2026-11-05", label="modelled", note="thesis precondition: H100 index sustained under ~$2/hr with Blackwell/Rubin volume arriving (one tracker's threshold). Not met: price is +19–27% y/y."))

    # ---- LLM regulation: the other gauge
    out.append(L("reg.eu_ai_act_gpai_enforcement", "AI Office enforcement powers over GPAI providers in application since 2 Aug 2026; fines to 3% global turnover; transparency obligations live, grace to 2 Dec 2026; high-risk rules delayed to Dec 2027 / Aug 2028 by Digital Omnibus", period="2026-11-05", label="measured", source="eu_ai_act_service_desk"))
    out.append(L("reg.us_chatbot_bills", "People-First Chatbot Act (H.R.9619); Senior Chatbot Protection Act (S.5117, bipartisan); SAFE KIDS (S.4855); CHATBOT Act (S.4407, Cruz); CLAIM Act discussion draft (Trahan, developer liability); FRONTIER Act (Trahan/Obernolte)", period="2026-11", label="measured", source="steptoe_ai_tracker_2026_11"))
    out.append(L("reg.us_dem_priority_ai", "Democrats name AI oversight, CEO testimony under oath, investigations as priorities for the new Congress; comprehensive statute unlikely under Trump veto", period="2026-11-04", label="stated", source="thehill_dems_ai_2026_11"))

    # ---- dot-com template (historical)
    out.append(L("telecom_capex_1996_2001", 444000, period="1996-2001", unit=M, source="latimes_telecom_2002", note="'more than $444 billion'"))
    out.append(L("fiber_lit_pct_2002", 2.7, period="2002", unit="pct", source="wsj_fiber_glut_2002", note="TeleGeography via WSJ"))
    out.append(L("bandwidth_price_decline_pct_per_year", 65, period="2001-2002", unit="pct", source="wsj_fiber_glut_2002"))
    out.append(L("global_crossing_assets", 22440, period="2002-01-28", unit=M, source="house_fin_svcs_gx_2002"))
    out.append(L("global_crossing_debts", 12390, period="2002-01-28", unit=M, source="house_fin_svcs_gx_2002"))
    out.append(L("global_crossing_network_cost", 13700, period="2002-01-28", unit=M, source="house_fin_svcs_gx_2002"))

    # ---- profile primitives (flattened from the Gemini sketch; labelled)
    out.append(L("profile.primary_type", "hyperscaler cloud (AWS) + retail/marketplace + advertising", label="measured", source="amzn_q3_2026_10q", note="segments: North America, International, AWS"))
    out.append(L("profile.revenue_mix_aws_pct", round(45984 / 201944 * 100, 1), period="2026Q3", unit="pct", label="modelled", note="AWS / consolidated net sales, Q3 2026"))
    out.append(L("profile.op_income_mix_aws_pct", round(17773 / 28076 * 100, 1), period="2026Q3", unit="pct", label="modelled", note="AWS / consolidated operating income, Q3 2026"))
    out.append(L("profile.commodity_exposure", "grid electricity; memory chips (Jassy cited memory prices for the Jul 2026 capex raise); diesel/jet for logistics", label="stated", source="cnbc_q3_2026"))
    out.append(L("profile.buyer_primitive", "enterprise compute dependency: customers rent capacity Amazon owns; Amazon is both builder and largest customer of its own data centers", label="modelled", note="why the dot-com template fits pure-play builders better than AMZN itself"))

    # ---- the two frames in the thread (stated, attributed)
    out.append(L("thesis.justin", "Analysts: AMZN undervalued; low FCF is AI capex; once realised, FCF will be the largest in the world with 5–10 year returns", period="2026-11-03", label="stated", source="imessage_run_20261105"))
    out.append(L("thesis.operator", "Wait for the midterm. A Democratic Congress retards the data-center growth horizon → infrastructure valuations drop → Amazon sells data centers to mitigate loss while data-center companies default and liquidate → compute becomes cheap (matrix multiplication at cost). Template: dot-com transatlantic fiber.", period="2026-11-03", label="stated", source="imessage_run_20261105", note="operator's own words, condensed; see transcript message 14 (the Q&A text)"))
    out.append(L("thesis.operator.data_center_pivot", "Data centers refocus on abstract-vector matrix multiplication and transduction while LLM products become more constrained and regulated", period="2026-11-04", label="stated", source="gemini_chat_2026_11_04", note="operator: 'my theory that data centers will become focused on…'"))
    out.append(L("thesis.operator.holding_is_buying", "Every day you do not sell an investment you are actively buying it at that day's price. 'I own stocks' answered yes in that frame; 'I'm not buying' answered no in the cash-inflow frame.", period="2026-11-05", label="stated", source="imessage_run_20261105", note="operator, chat 2026-11-05, on transcript message 2"))
    return out


YEARS = ["2027", "2028", "2029", "2030", "2031"]

# Scenario primitives. Every number here is `modelled`; the model reads them back from the ledger, so a
# different view is one appended line, not a code change.
SCENARIOS = {
    "A": {
        "name": "Analyst frame: capex normalises, OCF stays",
        "story": "Justin's frame. AWS keeps >40% growth through 2028 as guided, capex peaks 2027-28 near BMO's $320B then falls back toward Amazon's pre-AI intensity, OCF margin expands with AWS mix. Terminal P/OCF 17x (AMZN traded 15-20x OCF 2019-2025).",
        "revenue_growth_pct": [13, 12, 11, 10, 10],
        "ocf_margin_pct": [22, 23, 24, 24, 24],
        "capex_abs_or_pct": [300000, 300000, "25%", "20%", "18%"],
        "asset_sale_proceeds": [0, 0, 0, 0, 0],
        "terminal_p_ocf": 17,
    },
    "B": {
        "name": "Retarded horizon: a Democratic Congress prices the grid into the data center",
        "story": "Operator's first-order case. Large-load cost-shifting (GRID Savings Act logic) and state moratoria stretch build timelines; 2027 capex is already contracted (~$280B) but 2028 is cut hard; AWS growth decays 40 → 25 → 15%; compute pricing softens so OCF margin does not expand. Terminal P/OCF 13x.",
        "revenue_growth_pct": [12, 9, 7, 7, 7],
        "ocf_margin_pct": [21, 20, 20, 20, 20],
        "capex_abs_or_pct": [280000, 180000, "15%", "13%", "12%"],
        "asset_sale_proceeds": [0, 0, 0, 0, 0],
        "terminal_p_ocf": 13,
    },
    "C": {
        "name": "Liquidation: dot-com fiber template",
        "story": "Operator's second-order case. Pure-play data-center developers default, compute becomes a commodity at cost, Amazon sells a slice of its own AI plant to mitigate loss (operator: Amazon sells, the pure-plays liquidate). Modelled as: 2027 capex at contract floor, 2028 capex collapses, $100B book of AI P&E sold in 2028 at 60c (a $40B impairment, non-cash), OCF margin compresses to 17%. Terminal P/OCF 10x.",
        "revenue_growth_pct": [10, 4, 5, 5, 5],
        "ocf_margin_pct": [21, 18, 17, 17, 17],
        "capex_abs_or_pct": [240000, 100000, "10%", "10%", "10%"],
        "asset_sale_proceeds": [0, 60000, 0, 0, 0],
        "terminal_p_ocf": 10,
    },
}


def assumptions() -> list[dict]:
    out: list[dict] = []
    A = lambda key, value, **kw: L(key, value, label="modelled", **kw)  # noqa: E731
    out.append(A("model.discount_rate_pct", 9.0, note="cost of equity proxy; 9% is the middle of what sell-side uses for mega-cap tech"))
    out.append(A("model.base_period", "2026Q3", note="TTM base for all projections"))
    out.append(A("model.horizon_years", 5))
    out.append(A("model.shares_basis", "shares_outstanding", note="10,811M shares outstanding at Sep 30 2026; diluted count is 10,929M (10-Q) — using outstanding understates dilution by ~1%"))
    out.append(A("model.net_debt_definition", "bs_lt_debt − bs_cash − bs_marketable_securities", note="excludes current portion of LT debt, finance and operating leases, and the Anthropic stake; both omissions are material and offsetting in sign"))
    for sid, s in SCENARIOS.items():
        out.append(A(f"scn.{sid}.name", s["name"]))
        out.append(A(f"scn.{sid}.story", s["story"]))
        out.append(A(f"scn.{sid}.terminal_p_ocf", s["terminal_p_ocf"], unit="x"))
        for i, y in enumerate(YEARS):
            out.append(A(f"scn.{sid}.revenue_growth_pct", s["revenue_growth_pct"][i], period=y, unit="pct"))
            out.append(A(f"scn.{sid}.ocf_margin_pct", s["ocf_margin_pct"][i], period=y, unit="pct"))
            cx = s["capex_abs_or_pct"][i]
            out.append(A(f"scn.{sid}.capex", cx, period=y, unit=("pct_of_revenue" if isinstance(cx, str) else M)))
            out.append(A(f"scn.{sid}.asset_sale_proceeds", s["asset_sale_proceeds"][i], period=y, unit=M))
    return out


def _append_new(path: Path, lines: list[dict]) -> int:
    existing = resolve(read(path))
    new = [ln for ln in lines if (ln["ticker"], ln["key"], ln["period"]) not in existing or existing[(ln["ticker"], ln["key"], ln["period"])]["value"] != ln["value"]]
    return append(path, new)


def main() -> None:
    base = Path(__file__).resolve().parents[2] / "misc" / "justin_texts_amzn_202611" / "amzn_model" / "ledger"
    base.mkdir(parents=True, exist_ok=True)
    facts_path = base / "AMZN.facts.jsonl"
    assumptions_path = base / "AMZN.assumptions.jsonl"
    sources_path = base / "sources.jsonl"

    n = _append_new(facts_path, facts())
    print(f"facts: appended {n} lines → {facts_path}")
    a = _append_new(assumptions_path, assumptions())
    print(f"assumptions: appended {a} lines → {assumptions_path}")

    have = {s["id"] for s in read(sources_path)}
    src_lines = [
        {"ts": TS, "id": sid, "title": title, "url": url, "accessed": "2026-11-05", "read_extent": extent}
        for sid, title, url, extent in SOURCES
        if sid not in have
    ]
    m = append(sources_path, src_lines)
    print(f"sources: appended {m} lines → {sources_path}")


if __name__ == "__main__":
    main()
