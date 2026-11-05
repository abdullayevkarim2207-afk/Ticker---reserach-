"""Streamlit legend panel for FIN 43900 Lab 19."""

from __future__ import annotations

from html import escape
import os
from pathlib import Path
import sys

import altair as alt
import pandas as pd
import streamlit as st


REPO_ROOT = Path(__file__).resolve().parent
SKILL_SCRIPTS = REPO_ROOT / ".codex" / "skills" / "buffett-10k" / "scripts"
if str(SKILL_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SKILL_SCRIPTS))

from buffett_10k import (  # noqa: E402
    CHECK_LABELS,
    EdgarError,
    INVESTOR_CHECK_LABELS,
    METRIC_LABELS,
    analyze_ticker,
    audit_memo_numbers,
    format_cell,
    render_analysis,
    validate_user_agent,
)


DECISIONS = {
    "COST": (
        "Only with the condition that it remains a first-pass screen: COST's split is "
        "caused by Graham's liquidity threshold, and price and qualitative risks remain outside it."
    ),
    "NVDA": (
        "Only with the condition that every fail and not-known result is investigated in the "
        "10-K: NVDA's Burry cash-coverage failure is a prompt for research, not an automatic rejection."
    ),
}

METRIC_ORDER = (
    "revenue",
    "net_income",
    "operating_cash_flow",
    "capital_spending",
    "equity",
    "liabilities",
    "current_assets",
    "current_liabilities",
    "roe",
    "owner_earnings",
    "current_ratio",
    "liabilities_to_equity",
)

PAGE_CSS = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Space+Mono:wght@400;700&display=swap');

    :root {
        --bg: #050816;
        --panel: rgba(12, 20, 42, .82);
        --panel-2: rgba(17, 29, 58, .76);
        --line: rgba(104, 225, 255, .20);
        --cyan: #68e1ff;
        --lime: #b7f36b;
        --violet: #a98bff;
        --text: #f4f8ff;
        --muted: #8fa2c4;
        --danger: #ff7b96;
        --warning: #ffd166;
    }

    html, body, [class*="css"] { font-family: "DM Sans", sans-serif; }
    html, body, [data-testid="stAppViewContainer"], [data-testid="stMain"],
    [data-testid="stMainBlockContainer"], [data-testid="stBottom"],
    [data-testid="stBottomBlockContainer"], footer {
        background: #050816 !important;
    }
    [data-testid="stHeader"], [data-testid="stToolbar"], [data-testid="stStatusWidget"] {
        color: var(--text) !important;
        background: rgba(5, 8, 22, .96) !important;
        border-bottom-color: var(--line) !important;
    }
    [data-testid="stDecoration"] {
        background: linear-gradient(90deg, var(--cyan), var(--violet), var(--lime)) !important;
    }
    .stApp {
        color: var(--text);
        background:
            radial-gradient(circle at 82% 5%, rgba(72, 91, 255, .22), transparent 28rem),
            radial-gradient(circle at 25% 80%, rgba(0, 219, 180, .10), transparent 34rem),
            linear-gradient(rgba(104,225,255,.025) 1px, transparent 1px),
            linear-gradient(90deg, rgba(104,225,255,.025) 1px, transparent 1px),
            var(--bg);
        background-size: auto, auto, 32px 32px, 32px 32px, auto;
    }
    .main .block-container { max-width: 1440px; padding: 2rem 2.5rem 4rem; }
    h1, h2, h3, h4, p, label, .stMarkdown { color: var(--text); }
    code, pre, .mono { font-family: "Space Mono", monospace !important; }

    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, rgba(8,15,33,.98), rgba(10,21,43,.98));
        border-right: 1px solid var(--line);
    }
    [data-testid="stSidebar"] > div { padding-top: 1.2rem; }
    [data-testid="stSidebar"] h2, [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] label { color: var(--text) !important; }
    [data-testid="stSidebar"] input {
        color: var(--text) !important;
        background: rgba(4,10,24,.9) !important;
        border-color: rgba(104,225,255,.25) !important;
        font-family: "Space Mono", monospace;
        letter-spacing: .08em;
    }
    [data-testid="stSidebar"] input:focus { border-color: var(--cyan) !important; }

    .brand-lockup { margin: .3rem 0 1.7rem; }
    .brand-kicker {
        color: var(--cyan); font: 700 .68rem/1 "Space Mono", monospace;
        letter-spacing: .18em; text-transform: uppercase;
    }
    .brand-title { margin-top: .45rem; font-size: 1.35rem; font-weight: 750; letter-spacing: -.03em; }
    .brand-title span { color: var(--lime); }
    .connection {
        display: flex; align-items: center; gap: .55rem; margin: .2rem 0 1.2rem;
        color: #a9bad7; font-size: .78rem;
    }
    .pulse {
        width: .52rem; height: .52rem; border-radius: 50%; background: var(--lime);
        box-shadow: 0 0 14px rgba(183,243,107,.8);
    }
    .workflow {
        margin-top: 1.5rem; padding: 1rem; border: 1px solid var(--line);
        border-radius: 14px; background: rgba(10,19,40,.7);
    }
    .workflow-title { color: var(--muted); font: 700 .66rem/1 "Space Mono", monospace; letter-spacing: .14em; }
    .workflow-step { display: flex; gap: .65rem; margin-top: .85rem; color: #c3d1e8; font-size: .78rem; }
    .step-no { color: var(--cyan); font-family: "Space Mono", monospace; }

    div.stButton > button {
        min-height: 3rem; border: 1px solid rgba(104,225,255,.5); border-radius: 10px;
        color: #04101d; font-weight: 800; letter-spacing: .02em;
        background: linear-gradient(110deg, var(--cyan), #a5f3fc 55%, var(--lime));
        box-shadow: 0 8px 26px rgba(104,225,255,.15);
    }
    div.stButton > button:hover { border-color: var(--lime); transform: translateY(-1px); }

    .hero {
        position: relative; overflow: hidden; padding: 1.8rem 2rem 1.65rem; margin-bottom: 1.2rem;
        border: 1px solid var(--line); border-radius: 22px;
        background: linear-gradient(120deg, rgba(15,28,58,.95), rgba(8,17,38,.82));
        box-shadow: 0 22px 70px rgba(0,0,0,.28);
    }
    .hero:after {
        content: ""; position: absolute; width: 260px; height: 260px; right: -70px; top: -110px;
        border: 1px solid rgba(104,225,255,.2); border-radius: 50%;
        box-shadow: 0 0 80px rgba(104,225,255,.12), inset 0 0 70px rgba(169,139,255,.07);
    }
    .hero-kicker { color: var(--cyan); font: 700 .7rem/1 "Space Mono", monospace; letter-spacing: .18em; }
    .hero h1 { margin: .55rem 0 .4rem; font-size: clamp(2rem, 5vw, 3.5rem); letter-spacing: -.055em; line-height: 1.02; }
    .hero h1 span { color: var(--lime); }
    .hero p { max-width: 830px; margin: 0; color: #a9bad7; font-size: .98rem; }
    .hero-chips { display: flex; flex-wrap: wrap; gap: .5rem; margin-top: 1.25rem; }
    .chip {
        padding: .36rem .62rem; border: 1px solid rgba(104,225,255,.2); border-radius: 999px;
        background: rgba(4,10,24,.48); color: #c5d2e8; font: 700 .66rem/1 "Space Mono", monospace;
    }
    .chip strong { color: var(--cyan); }

    .metric-grid { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: .8rem; margin: .3rem 0 1.2rem; }
    .metric-card {
        min-height: 112px; padding: 1rem 1.05rem; border: 1px solid var(--line); border-radius: 16px;
        background: linear-gradient(145deg, rgba(15,28,56,.82), rgba(8,16,34,.78));
    }
    .metric-label { color: var(--muted); font: 700 .65rem/1.2 "Space Mono", monospace; letter-spacing: .12em; text-transform: uppercase; }
    .metric-value { margin-top: .55rem; color: var(--text); font-size: 1.55rem; font-weight: 750; letter-spacing: -.03em; }
    .metric-note { margin-top: .2rem; color: #7286aa; font-size: .72rem; }

    .section-label { margin: .45rem 0 .85rem; color: var(--muted); font: 700 .68rem/1 "Space Mono", monospace; letter-spacing: .15em; text-transform: uppercase; }
    .panel {
        padding: 1.15rem 1.2rem; border: 1px solid var(--line); border-radius: 16px;
        background: var(--panel); box-shadow: 0 15px 40px rgba(0,0,0,.18);
    }
    .check-card { min-height: 130px; padding: 1.05rem; border: 1px solid var(--line); border-radius: 16px; background: var(--panel-2); }
    .check-card.pass { border-top: 2px solid var(--lime); }
    .check-card.fail { border-top: 2px solid var(--danger); }
    .check-card.unknown { border-top: 2px solid var(--warning); }
    .check-status { font: 700 .68rem/1 "Space Mono", monospace; letter-spacing: .12em; }
    .check-card.pass .check-status { color: var(--lime); }
    .check-card.fail .check-status { color: var(--danger); }
    .check-card.unknown .check-status { color: var(--warning); }
    .check-name { margin-top: .8rem; color: #e7eefb; font-size: .93rem; font-weight: 600; line-height: 1.35; }

    .audit-pass, .audit-fail, .decision-card, .empty-state {
        padding: 1rem 1.1rem; border-radius: 14px; margin: .8rem 0;
    }
    .audit-pass { border: 1px solid rgba(183,243,107,.35); background: rgba(104,190,92,.10); color: #d9ffad; }
    .audit-fail { border: 1px solid rgba(255,123,150,.42); background: rgba(255,83,119,.10); color: #ffc0cd; }
    .decision-card { border: 1px solid rgba(169,139,255,.32); background: rgba(169,139,255,.09); color: #ddd4ff; }
    .empty-state { padding: 2rem; border: 1px dashed rgba(104,225,255,.3); background: rgba(8,17,36,.62); }
    .empty-state h3 { margin: 0 0 .5rem; }
    .empty-state p { color: var(--muted); margin: 0; }

    .stTabs [data-baseweb="tab-list"] { gap: .35rem; border-bottom: 1px solid var(--line); }
    .stTabs [data-baseweb="tab"] { height: 3.2rem; padding: 0 1rem; border-radius: 10px 10px 0 0; }
    .stTabs [aria-selected="true"] { background: rgba(104,225,255,.09); }
    .stTabs [data-baseweb="tab"] p { color: #8296b9 !important; font: 700 .72rem/1 "Space Mono", monospace; }
    .stTabs [aria-selected="true"] p { color: var(--cyan) !important; }
    div[data-testid="stDataFrame"] {
        border: 1px solid var(--line); border-radius: 14px; overflow: hidden;
        background: #071024 !important;
    }
    .vega-embed, .vega-embed canvas, .vega-embed svg { background: transparent !important; }
    [data-testid="stExpander"] { border-color: var(--line) !important; background: rgba(8,17,36,.55); }
    [data-testid="stTextArea"] textarea {
        min-height: 410px; color: #dfeaff; background: #071024; border-color: rgba(104,225,255,.25);
        font-family: "Space Mono", monospace; font-size: .78rem; line-height: 1.65;
    }
    [data-testid="stCaptionContainer"] { color: var(--muted); }
    hr { border-color: var(--line); }

    @media (max-width: 900px) {
        .main .block-container { padding: 1.25rem 1rem 3rem; }
        .metric-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); }
        .hero { padding: 1.4rem; }
    }
</style>
"""


@st.cache_data(show_spinner=False, ttl=3600)
def download_analysis(ticker: str, user_agent: str) -> dict:
    """Cache public SEC facts for one hour to avoid repeated requests."""
    return analyze_ticker(ticker, user_agent)


def display_table(analysis: dict) -> pd.DataFrame:
    """Build the visible tagged table without recomputing any values."""
    records = []
    for row in analysis["rows"]:
        record = {"Fiscal year end": row["fiscal_year_end"]}
        for metric in METRIC_ORDER:
            record[METRIC_LABELS[metric]] = format_cell(row[metric], metric)
        records.append(record)
    return pd.DataFrame.from_records(records)


def chart_frame(analysis: dict) -> pd.DataFrame:
    """Return only printed owner earnings and net income for charting."""
    records = []
    for row in analysis["rows"]:
        owner = row["owner_earnings"]
        net_income = row["net_income"]
        records.append(
            {
                "Fiscal year end": row["fiscal_year_end"],
                "Owner earnings": owner["value"] if owner["status"] == "ok" else None,
                "Net income": net_income["value"] if net_income["status"] == "ok" else None,
            }
        )
    return pd.DataFrame.from_records(records)


def verdict_for(checks: dict[str, str]) -> str:
    """Map coded checks to a consistent panel verdict without hiding gaps."""
    statuses = list(checks.values())
    if statuses and all(status == "pass" for status in statuses):
        return "OWN"
    if any(status == "not known" for status in statuses):
        return "WATCH — EVIDENCE GAP"
    return "WATCH"


def generated_memo(analysis: dict, investor: str) -> str:
    """Create a concise memo using only values present in rendered evidence."""
    ticker = analysis["ticker"]
    rows = analysis["rows"]
    checks = analysis["panel_checks"][investor]
    passed = sum(status == "pass" for status in checks.values())
    total = len(checks)
    verdict = verdict_for(checks)

    if investor == "Buffett":
        first_owner = format_cell(rows[0]["owner_earnings"], "owner_earnings").split(" [")[0]
        last_owner = format_cell(rows[-1]["owner_earnings"], "owner_earnings").split(" [")[0]
        latest_roe = format_cell(rows[-1]["roe"], "roe").split(" [")[0]
        body = (
            f"The coded screen passes {passed} of {total} checks. Latest ROE is "
            f"{latest_roe}; owner earnings move from {first_owner} to {last_owner}. "
            "The evidence supports business quality, but this is not a price judgment."
        )
    elif investor == "Graham":
        ratio = format_cell(rows[-1]["current_ratio"], "current_ratio").split(" [")[0]
        first_income = format_cell(rows[0]["net_income"], "net_income").split(" [")[0]
        last_income = format_cell(rows[-1]["net_income"], "net_income").split(" [")[0]
        body = (
            f"The coded screen passes {passed} of {total} checks. The latest current "
            f"ratio is {ratio}; net income moves from {first_income} to {last_income}. "
            "I keep the 2.0 current-ratio threshold because this defensive screen is meant "
            "to demand a substantial liquidity cushion. The 1.0 probe result is "
            f"{analysis['graham_probe_checks']['current_ratio_latest']}."
        )
    else:
        leverage = format_cell(
            rows[-1]["liabilities_to_equity"], "liabilities_to_equity"
        ).split(" [")[0]
        latest_cash = format_cell(
            rows[-1]["operating_cash_flow"], "operating_cash_flow"
        ).split(" [")[0]
        latest_income = format_cell(rows[-1]["net_income"], "net_income").split(" [")[0]
        body = (
            f"The coded screen passes {passed} of {total} checks. Latest liabilities "
            f"to equity are {leverage}; latest operating cash flow is {latest_cash}, "
            f"and latest net income is {latest_income}. The every-year cash-coverage "
            f"check is {checks['cash_flow_covers_net_income_every_year']}."
        )
    return f"### {investor} — {verdict}\n\n{body}"


def load_memo(ticker: str, investor: str, analysis: dict) -> str:
    path = REPO_ROOT / f"lab19_{investor.lower()}_memo_{ticker}.md"
    if path.exists():
        return path.read_text(encoding="utf-8")
    if investor == "Buffett":
        legacy = REPO_ROOT / f"lab18_buffett_memo_{ticker}.md"
        if legacy.exists():
            return legacy.read_text(encoding="utf-8")
    return generated_memo(analysis, investor)


def evidence_gap_count(analysis: dict) -> int:
    """Count explicit missing or unknown cells without changing their meaning."""
    return sum(
        row[metric]["status"] != "ok"
        for row in analysis["rows"]
        for metric in METRIC_ORDER
    )


def latest_owner_earnings(analysis: dict) -> str:
    cell = analysis["rows"][-1]["owner_earnings"]
    if cell["status"] != "ok":
        return cell["status"]
    return f"${cell['value']:,.0f}M"


def render_sidebar() -> tuple[str, str, bool]:
    with st.sidebar:
        st.markdown(
            """
            <div class="brand-lockup">
                <div class="brand-kicker">FIN 43900 · LAB 19</div>
                <div class="brand-title">LEGEND<span>//</span>PANEL</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        ticker = st.text_input(
            "Ticker symbol",
            value="COST",
            max_chars=10,
            help="Try COST for the known answer or NVDA for the largest VT holding.",
        ).strip().upper()

        environment_agent = os.environ.get("SEC_USER_AGENT", "")
        if environment_agent:
            user_agent = environment_agent
            st.markdown(
                '<div class="connection"><span class="pulse"></span>SEC identity connected</div>',
                unsafe_allow_html=True,
            )
        else:
            user_agent = st.text_input(
                "SEC identity · name and email",
                type="password",
                help="Sent to the SEC for this session and never written to the repository.",
            )

        run = st.button("Run 10-K analysis →", type="primary", use_container_width=True)
        st.markdown(
            """
            <div class="workflow">
                <div class="workflow-title">MISSION SEQUENCE</div>
                <div class="workflow-step"><span class="step-no">01</span><span>Fetch keyless SEC company facts</span></div>
                <div class="workflow-step"><span class="step-no">02</span><span>Run Buffett, Graham, and Burry checks</span></div>
                <div class="workflow-step"><span class="step-no">03</span><span>Audit all three memos together</span></div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.caption("10-K only · USD millions · no price data · no estimates")
    return ticker, user_agent, run


def render_hero(analysis: dict | None = None) -> None:
    target = "SEC EVIDENCE TERMINAL"
    company_line = "Deterministic investor analysis"
    if analysis:
        target = escape(analysis["ticker"])
        company_line = escape(analysis["company"])
    st.markdown(
        f"""
        <section class="hero">
            <div class="hero-kicker">{target} // 10-K COMPUTE LAYER</div>
            <h1>Three legends, <span>one fact set</span></h1>
            <p>{company_line}. Data from SEC EDGAR; built with AI help, a learning demonstration, not investment advice.</p>
            <div class="hero-chips">
                <span class="chip"><strong>01</strong> CODED NUMBERS</span>
                <span class="chip"><strong>02</strong> TAGGED EVIDENCE</span>
                <span class="chip"><strong>03</strong> MODEL JUDGMENT</span>
            </div>
        </section>
        """,
        unsafe_allow_html=True,
    )


def render_summary(analysis: dict) -> None:
    all_checks = [
        status
        for checks in analysis["panel_checks"].values()
        for status in checks.values()
    ]
    checks_passed = sum(status == "pass" for status in all_checks)
    gaps = evidence_gap_count(analysis)
    years = len(analysis["rows"])
    owner_value = escape(latest_owner_earnings(analysis))
    st.markdown(
        f"""
        <div class="metric-grid">
            <div class="metric-card"><div class="metric-label">Audit window</div><div class="metric-value">{years} years</div><div class="metric-note">latest fiscal-year ends</div></div>
            <div class="metric-card"><div class="metric-label">Panel checks passed</div><div class="metric-value">{checks_passed} / {len(all_checks)}</div><div class="metric-note">computed, not judged</div></div>
            <div class="metric-card"><div class="metric-label">Latest owner earnings</div><div class="metric-value">{owner_value}</div><div class="metric-note">operating cash flow − capex</div></div>
            <div class="metric-card"><div class="metric-label">Evidence gaps</div><div class="metric-value">{gaps}</div><div class="metric-note">explicitly preserved</div></div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_chart(analysis: dict) -> None:
    frame = chart_frame(analysis)
    long_frame = frame.melt(
        id_vars="Fiscal year end",
        value_vars=["Owner earnings", "Net income"],
        var_name="Metric",
        value_name="USD millions",
    ).dropna()
    if long_frame.empty:
        st.warning("Owner earnings and net income are not found for the displayed years.")
        return

    chart = (
        alt.Chart(long_frame)
        .mark_line(point=alt.OverlayMarkDef(size=80, filled=True), strokeWidth=3)
        .encode(
            x=alt.X(
                "Fiscal year end:N",
                sort=frame["Fiscal year end"].tolist(),
                axis=alt.Axis(title=None, labelAngle=0, labelColor="#8fa2c4", tickColor="#26385d"),
            ),
            y=alt.Y(
                "USD millions:Q",
                axis=alt.Axis(title="USD millions", labelColor="#8fa2c4", titleColor="#8fa2c4", gridColor="#18294c"),
            ),
            color=alt.Color(
                "Metric:N",
                scale=alt.Scale(domain=["Owner earnings", "Net income"], range=["#b7f36b", "#68e1ff"]),
                legend=alt.Legend(orient="top", title=None, labelColor="#c7d3e8"),
            ),
            tooltip=["Fiscal year end:N", "Metric:N", alt.Tooltip("USD millions:Q", format=",.0f")],
        )
        .properties(height=340)
        .configure_view(strokeWidth=0)
        .configure(background="transparent")
    )
    st.altair_chart(chart, use_container_width=True)


def render_checks(analysis: dict) -> None:
    columns = st.columns(3)
    for column, (key, label) in zip(columns, CHECK_LABELS.items()):
        status = analysis["checks"][key]
        css_class = "unknown" if status == "not known" else status
        with column:
            st.markdown(
                f"""
                <div class="check-card {css_class}">
                    <div class="check-status">● {escape(status.upper())}</div>
                    <div class="check-name">{escape(label)}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )


def panel_frame(analysis: dict) -> pd.DataFrame:
    """Build investor-by-check rows and retain the two required ratio values."""
    records = []
    latest = analysis["rows"][-1]
    for investor, labels in INVESTOR_CHECK_LABELS.items():
        for key, label in labels.items():
            status = analysis["panel_checks"][investor][key]
            result = status
            if investor == "Graham" and key == "current_ratio_latest":
                cell = latest["current_ratio"]
                if cell["status"] == "ok":
                    result = f"{status} ({cell['value']:.2f})"
            if investor == "Burry" and key == "liabilities_no_more_than_twice_equity_latest":
                cell = latest["liabilities_to_equity"]
                if cell["status"] == "ok":
                    result = f"{status} ({cell['value']:.2f})"
            records.append({"Investor": investor, "Check": label, analysis["ticker"]: result})
    return pd.DataFrame.from_records(records)


def styled_panel(analysis: dict) -> pd.io.formats.style.Styler:
    """Apply a low-glare dark theme while keeping pass/fail text explicit."""
    frame = panel_frame(analysis)

    def result_color(value: object) -> str:
        text = str(value).lower()
        if text.startswith("pass"):
            return "color: #b7f36b !important; font-weight: 800;"
        if text.startswith("fail"):
            return "color: #ff5f7d !important; font-weight: 800;"
        if text.startswith("not known"):
            return "color: #ffd166 !important; font-weight: 800;"
        return "color: #f4f8ff;"

    return (
        frame.style
        .set_properties(
            **{
                "background-color": "#0b1530",
                "color": "#dfeaff",
                "border-color": "#26385d",
            }
        )
        .set_table_styles(
            [
                {
                    "selector": "th",
                    "props": [
                        ("background-color", "#111d3a"),
                        ("color", "#68e1ff"),
                        ("border-color", "#26385d"),
                    ],
                }
            ]
        )
        .map(result_color, subset=[analysis["ticker"]])
    )


def render_panel(analysis: dict) -> None:
    st.markdown('<div class="section-label">Investor × check panel</div>', unsafe_allow_html=True)
    st.dataframe(styled_panel(analysis), hide_index=True, use_container_width=True)
    verdict_columns = st.columns(3)
    for column, investor in zip(verdict_columns, INVESTOR_CHECK_LABELS):
        checks = analysis["panel_checks"][investor]
        passed = sum(status == "pass" for status in checks.values())
        with column:
            st.markdown(
                f'<div class="decision-card"><strong>{escape(investor.upper())}</strong><br>'
                f'{passed} of {len(checks)} · {escape(verdict_for(checks))}</div>',
                unsafe_allow_html=True,
            )


def render_empty_state() -> None:
    st.markdown(
        """
        <div class="empty-state">
            <h3>Ready for evidence</h3>
            <p>Use COST to reproduce the known answer or NVDA for the largest-company run from VT. The app downloads public SEC facts only after you press Run.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    columns = st.columns(3)
    for column, title, body in zip(
        columns,
        ("Compute", "Verify", "Judge"),
        (
            "Python selects periods, tags, and calculates every number.",
            "Each value stays connected to its XBRL source tag.",
            "The memo chooses own, watch, or pass without adding numbers.",
        ),
    ):
        with column:
            st.markdown(
                f'<div class="panel"><strong>{title}</strong><br><span style="color:#8fa2c4;font-size:.84rem">{body}</span></div>',
                unsafe_allow_html=True,
            )


def render_overview(analysis: dict) -> None:
    render_panel(analysis)
    st.markdown('<div class="section-label">Performance signal</div>', unsafe_allow_html=True)
    render_chart(analysis)
    st.markdown('<div class="section-label">Buffett checks · computed in code</div>', unsafe_allow_html=True)
    render_checks(analysis)


def render_evidence(analysis: dict) -> None:
    st.markdown('<div class="section-label">Five fiscal years · values and XBRL tags</div>', unsafe_allow_html=True)
    st.caption("Every displayed value is either filed, calculated from filed values, or explicitly marked not found / not known.")
    st.dataframe(
        display_table(analysis),
        hide_index=True,
        use_container_width=True,
        height=270,
    )
    with st.expander("Exact script output · audit source"):
        st.code(render_analysis(analysis), language="text")


def render_memo_audit(analysis: dict) -> None:
    ticker = analysis["ticker"]
    st.markdown('<div class="section-label">Three evidence-bounded memos</div>', unsafe_allow_html=True)
    columns = st.columns(3)
    memos = []
    for column, investor in zip(columns, INVESTOR_CHECK_LABELS):
        with column:
            memo = st.text_area(
                f"{investor} memo",
                value=load_memo(ticker, investor, analysis),
                height=430,
                key=f"memo_{investor}_{ticker}",
            )
            memos.append(memo)

    st.markdown('<div class="section-label">Number-origin gate · all memos</div>', unsafe_allow_html=True)
    flagged = audit_memo_numbers("\n".join(memos), render_analysis(analysis))
    if flagged:
        items = ", ".join(f"<code>{escape(item)}</code>" for item in flagged)
        st.markdown(
            f'<div class="audit-fail"><strong>REJECTED</strong><br>Numbers not printed by the script: {items}</div>',
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            '<div class="audit-pass"><strong>VERIFIED</strong><br>Every numeric claim across all three memos appears in the script output.</div>',
            unsafe_allow_html=True,
        )
    decision = escape(DECISIONS.get(ticker, "Only with the condition that every evidence gap remains not known and the panel is a screen, not an investment decision."))
    st.markdown(
        f'<div class="decision-card"><strong>TRUST DECISION</strong><br>{decision}</div>',
        unsafe_allow_html=True,
    )


def render_method() -> None:
    st.markdown('<div class="section-label">Deterministic method</div>', unsafe_allow_html=True)
    left, right = st.columns(2)
    with left:
        st.markdown(
            """
            <div class="panel">
                <div class="metric-label">Formulas</div>
                <p><code>ROE = net income ÷ year-end equity</code></p>
                <p><code>Owner earnings = operating cash flow − capital spending</code></p>
                <p><code>Current ratio = current assets ÷ current liabilities</code></p>
                <p><code>Leverage = liabilities ÷ equity</code></p>
                <p style="color:#8fa2c4;font-size:.84rem">All eight panel checks are computed from the same five-year fact set.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with right:
        st.markdown(
            """
            <div class="panel">
                <div class="metric-label">Evidence rules</div>
                <p style="color:#c7d3e8;font-size:.88rem">10-K only · one-year flows · latest filing wins · five fiscal-year ends · tag priority preserved.</p>
                <p style="color:#8fa2c4;font-size:.84rem">A missing value is <code>not found</code>. A check without all required inputs is <code>not known</code>. Nothing is estimated.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
    st.markdown('<div class="section-label" style="margin-top:1.3rem">Source tags</div>', unsafe_allow_html=True)
    st.markdown(
        """
        | Measure | XBRL selection rule |
        |---|---|
        | Revenue | `RevenueFromContractWithCustomerExcludingAssessedTax`, then `Revenues` |
        | Net income | `NetIncomeLoss` |
        | Operating cash flow | `NetCashProvidedByUsedInOperatingActivities` |
        | Capital spending | `PaymentsToAcquirePropertyPlantAndEquipment`, then `PaymentsToAcquireProductiveAssets` |
        | Equity | `StockholdersEquity` |
        | Liabilities | `Liabilities` |
        | Current assets | `AssetsCurrent` |
        | Current liabilities | `LiabilitiesCurrent` |
        """
    )


def main() -> None:
    st.set_page_config(
        page_title="LEGEND//PANEL · 10-K",
        page_icon="◈",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    st.markdown(PAGE_CSS, unsafe_allow_html=True)
    ticker, user_agent, run = render_sidebar()

    if run:
        try:
            declared_agent = validate_user_agent(user_agent)
            with st.spinner("Synchronizing with SEC EDGAR…"):
                st.session_state.analysis = download_analysis(ticker, declared_agent)
        except EdgarError as exc:
            st.error(str(exc))

    analysis = st.session_state.get("analysis")
    render_hero(analysis)

    if analysis is None:
        render_empty_state()
        return

    render_summary(analysis)
    overview_tab, evidence_tab, memo_tab, method_tab = st.tabs(
        ["01 · OVERVIEW", "02 · EVIDENCE", "03 · MEMO AUDIT", "04 · METHOD"]
    )
    with overview_tab:
        render_overview(analysis)
    with evidence_tab:
        render_evidence(analysis)
    with memo_tab:
        render_memo_audit(analysis)
    with method_tab:
        render_method()


if __name__ == "__main__":
    main()
