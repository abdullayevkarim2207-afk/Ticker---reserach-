"""Streamlit interface for the reusable portfolio engine."""

import csv
from copy import deepcopy
from io import BytesIO
from pathlib import Path

import altair as alt
import pandas as pd
import streamlit as st

from portfolio import (
    OBJECTIVE_RETURN,
    build_covariance_matrix,
    equal_weights,
    estimate_from_price_csv,
    expected_return,
    inverse_volatility_weights,
    portfolio_volatility,
    reserve_eligible_weight,
    search_lowest_risk_mix,
)


st.set_page_config(
    page_title="Portfolio Stability Decision",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
    :root {
        --ink: #10243e;
        --muted: #5f6f82;
        --line: #dbe4ee;
        --blue: #175cd3;
        --blue-soft: #eaf2ff;
        --gold: #b7791f;
        --green: #16794b;
        --red: #b42318;
        --surface: rgba(255, 255, 255, 0.92);
    }

    .stApp {
        background:
            radial-gradient(circle at 86% 2%, rgba(54, 121, 246, 0.12), transparent 30rem),
            linear-gradient(180deg, #f7faff 0%, #eef4fb 100%);
        color: var(--ink);
    }

    [data-testid="stAppViewContainer"] > .main .block-container {
        max-width: 1240px;
        padding-top: 2.2rem;
        padding-bottom: 4rem;
    }

    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #10243e 0%, #15375f 100%);
        border-right: 1px solid rgba(255, 255, 255, 0.12);
    }

    [data-testid="stSidebar"] * {
        color: #f6f9ff !important;
    }

    [data-testid="stSidebar"] [data-baseweb="input"] > div,
    [data-testid="stSidebar"] [data-testid="stFileUploaderDropzone"] {
        background: rgba(255, 255, 255, 0.10);
        border-color: rgba(255, 255, 255, 0.24);
    }

    [data-testid="stSidebar"] button {
        border-color: rgba(255, 255, 255, 0.28) !important;
    }

    .hero {
        position: relative;
        overflow: hidden;
        padding: 2.2rem 2.4rem;
        margin-bottom: 1.5rem;
        border: 1px solid rgba(23, 92, 211, 0.16);
        border-radius: 24px;
        background: linear-gradient(125deg, #10243e 0%, #173f70 58%, #175cd3 130%);
        box-shadow: 0 18px 50px rgba(16, 36, 62, 0.16);
        color: white;
    }

    .hero::after {
        content: "";
        position: absolute;
        width: 300px;
        height: 300px;
        right: -95px;
        top: -145px;
        border-radius: 50%;
        border: 46px solid rgba(255, 255, 255, 0.07);
    }

    .hero-kicker {
        margin-bottom: 0.6rem;
        color: #9fc3ff;
        font-size: 0.78rem;
        font-weight: 800;
        letter-spacing: 0.14em;
        text-transform: uppercase;
    }

    .hero h1 {
        max-width: 760px;
        margin: 0;
        color: white;
        font-size: clamp(2rem, 4vw, 3.35rem);
        line-height: 1.04;
        letter-spacing: -0.035em;
    }

    .hero p {
        max-width: 750px;
        margin: 1rem 0 1.35rem;
        color: #dce9fb;
        font-size: 1.02rem;
        line-height: 1.65;
    }

    .hero-pills {
        display: flex;
        flex-wrap: wrap;
        gap: 0.55rem;
    }

    .hero-pill {
        padding: 0.42rem 0.72rem;
        border: 1px solid rgba(255, 255, 255, 0.18);
        border-radius: 999px;
        background: rgba(255, 255, 255, 0.09);
        color: #f6f9ff;
        font-size: 0.82rem;
        font-weight: 650;
    }

    .section-label {
        display: inline-flex;
        align-items: center;
        gap: 0.55rem;
        margin: 1rem 0 0.45rem;
        color: var(--blue);
        font-size: 0.77rem;
        font-weight: 800;
        letter-spacing: 0.1em;
        text-transform: uppercase;
    }

    .section-label span {
        display: grid;
        width: 1.65rem;
        height: 1.65rem;
        place-items: center;
        border-radius: 50%;
        background: var(--blue);
        color: white;
        letter-spacing: 0;
    }

    .source-note {
        margin: 0.25rem 0 1.2rem;
        padding: 0.9rem 1rem;
        border: 1px solid #cfe0fb;
        border-radius: 13px;
        background: var(--blue-soft);
        color: #29496f;
        line-height: 1.5;
    }

    .decision-strip {
        display: grid;
        grid-template-columns: repeat(4, minmax(0, 1fr));
        gap: 0.75rem;
        margin: 0 0 1.4rem;
    }

    .decision-item {
        padding: 0.9rem 1rem;
        border: 1px solid var(--line);
        border-radius: 15px;
        background: rgba(255, 255, 255, 0.86);
        box-shadow: 0 7px 20px rgba(16, 36, 62, 0.05);
    }

    .decision-item small {
        display: block;
        margin-bottom: 0.25rem;
        color: var(--muted);
        font-size: 0.68rem;
        font-weight: 800;
        letter-spacing: 0.08em;
        text-transform: uppercase;
    }

    .decision-item strong { color: var(--ink); font-size: 0.95rem; }

    .rule-grid {
        display: grid;
        grid-template-columns: repeat(3, minmax(0, 1fr));
        gap: 0.45rem;
        margin-top: 0.8rem;
    }

    .rule-chip {
        padding: 0.5rem 0.6rem;
        border: 1px solid var(--line);
        border-radius: 10px;
        background: #f8fbff;
        color: var(--muted);
        font-size: 0.72rem;
        line-height: 1.35;
    }

    .rule-chip b { display: block; color: var(--ink); font-size: 0.78rem; }
    .rule-chip.pass b { color: var(--green); }
    .rule-chip.fail b { color: var(--red); }

    .portfolio-note {
        min-height: 2.6rem;
        color: var(--muted);
        font-size: 0.82rem;
        line-height: 1.5;
    }

    [data-testid="stVerticalBlockBorderWrapper"] {
        border-color: var(--line) !important;
        border-radius: 18px !important;
        background: var(--surface);
        box-shadow: 0 8px 24px rgba(16, 36, 62, 0.06);
    }

    [data-testid="stMetric"] {
        min-height: 104px;
        padding: 0.9rem 1rem;
        border: 1px solid var(--line);
        border-radius: 14px;
        background: #f8fbff;
    }

    [data-testid="stMetricLabel"] {
        color: var(--muted);
        font-weight: 700;
    }

    [data-testid="stMetricValue"] {
        color: var(--ink);
        font-size: 1.6rem;
        font-weight: 800;
    }

    [data-testid="stTable"] {
        overflow: hidden;
        border: 1px solid var(--line);
        border-radius: 13px;
    }

    .allocation-bar {
        display: flex;
        width: 100%;
        height: 18px;
        margin: 0.5rem 0 0.75rem;
        overflow: hidden;
        border-radius: 999px;
        background: #e8eef5;
        box-shadow: inset 0 0 0 1px rgba(16, 36, 62, 0.05);
    }

    .allocation-segment { min-width: 0; height: 100%; }
    .legend-row { display: flex; flex-wrap: wrap; gap: 0.55rem 1rem; margin-bottom: 1rem; }
    .legend-item { color: var(--muted); font-size: 0.79rem; font-weight: 650; }
    .legend-dot { display: inline-block; width: 9px; height: 9px; margin-right: 0.3rem; border-radius: 50%; }

    [data-testid="stAlert"] {
        border-radius: 16px;
        border-width: 1px;
        box-shadow: 0 7px 20px rgba(16, 36, 62, 0.05);
    }

    h2, h3 { color: var(--ink); letter-spacing: -0.02em; }
    .stCheckbox label, .stNumberInput label { font-weight: 700; }

    @media (max-width: 720px) {
        [data-testid="stAppViewContainer"] > .main .block-container { padding: 1rem; }
        .hero { padding: 1.55rem; border-radius: 19px; }
        .hero h1 { font-size: 2rem; }
        .decision-strip { grid-template-columns: repeat(2, minmax(0, 1fr)); }
        .rule-grid { grid-template-columns: 1fr; }
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <section class="hero">
      <div class="hero-kicker">Meridian Foundation Reserve</div>
      <h1>Portfolio stability, made decision-ready.</h1>
      <p>Adjust one assumption, compare the allocation with the saved baseline,
      and read the mandate and stability verdict without digging through code.</p>
      <div class="hero-pills">
        <span class="hero-pill">4-asset universe</span>
        <span class="hero-pill">6.5% return objective</span>
        <span class="hero-pill">10-point stability limit</span>
        <span class="hero-pill">Paper pilot only</span>
      </div>
    </section>
    """,
    unsafe_allow_html=True,
)

PRICE_FILE = Path(__file__).with_name("prices.csv")
SIGNAL_FILE = Path(__file__).with_name("data") / "dgs10-point-in-time-signal.csv"
DEFAULT_RESERVE_MINIMUM = 0.03
DEFAULT_STABILITY_LIMIT = 0.10
ASSET_COLORS = {
    "SGOV": "#175cd3",
    "VGIT": "#61a0ff",
    "BND": "#b7791f",
    "VT": "#1f9d68",
}


def data_card(source: Path | bytes) -> tuple[str, str, int]:
    """Return first date, last date, and saved price-row count."""
    text = (
        source.decode("utf-8-sig")
        if isinstance(source, bytes)
        else source.read_text(encoding="utf-8-sig")
    )
    rows = list(csv.DictReader(text.splitlines()))
    if not rows:
        raise ValueError("The price file has no observations.")
    date_field = next(
        (field for field in rows[0] if field.strip().lower() == "date"), None
    )
    if date_field is None:
        raise ValueError("The first CSV column must be Date.")
    return rows[0][date_field], rows[-1][date_field], len(rows)


def load_point_in_time_signal(source: Path = SIGNAL_FILE) -> dict[str, str]:
    """Load the frozen, audited DGS10 monitoring signal."""
    with source.open(encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))
    if len(rows) != 1:
        raise ValueError("The point-in-time signal file must contain exactly one row.")
    required = {
        "series_id",
        "measurement_date",
        "value_percent",
        "vintage_date",
        "signal_threshold_percent",
        "signal",
        "decision_use",
        "source_url",
        "download_date",
        "release_rule",
    }
    missing = required - set(rows[0])
    if missing:
        raise ValueError(f"The point-in-time signal is missing fields: {sorted(missing)}")
    return rows[0]


def show_allocation_bar(mix: dict[str, float]) -> None:
    """Render one compact allocation bar and legend."""
    segments = "".join(
        f'<span class="allocation-segment" style="width:{weight * 100:.0f}%;'
        f'background:{ASSET_COLORS.get(asset, "#8091a5")}"></span>'
        for asset, weight in mix.items()
        if weight > 0
    )
    legend = "".join(
        f'<span class="legend-item"><span class="legend-dot" '
        f'style="background:{ASSET_COLORS.get(asset, "#8091a5")}"></span>'
        f'{asset} {weight:.0%}</span>'
        for asset, weight in mix.items()
    )
    st.markdown(
        f'<div class="allocation-bar">{segments}</div>'
        f'<div class="legend-row">{legend}</div>',
        unsafe_allow_html=True,
    )


def portfolio_metrics(
    mix: dict[str, float],
    sleeves: dict[str, dict[str, float]],
    correlations: dict[str, dict[str, float]],
    reserve_assets: set[str],
) -> dict[str, float]:
    covariance = build_covariance_matrix(sleeves, correlations)
    return {
        "return": expected_return(mix, sleeves),
        "volatility": portfolio_volatility(mix, covariance),
        "reserve": reserve_eligible_weight(mix, reserve_assets),
    }


def benchmark_mix(sleeves: dict[str, dict[str, float]]) -> dict[str, float] | None:
    """Return the documented 40% BND / 60% VT benchmark when available."""
    if not {"BND", "VT"}.issubset(sleeves):
        return None
    weights = {asset: 0.0 for asset in sleeves}
    weights["BND"] = 0.40
    weights["VT"] = 0.60
    return weights


def show_portfolio(
    heading: str,
    note: str,
    mix: dict[str, float] | None,
    sleeves: dict[str, dict[str, float]],
    correlations: dict[str, dict[str, float]],
    reserve_assets: set[str],
    objective: float,
    reserve_minimum: float,
) -> dict[str, float] | None:
    """Render a transparent allocation card with component mandate checks."""
    with st.container(border=True):
        st.markdown(f"### {heading}")
        st.markdown(f'<div class="portfolio-note">{note}</div>', unsafe_allow_html=True)
        if mix is None:
            st.markdown("**Unavailable:** this portfolio cannot be formed from the uploaded tickers.")
            return None
        result = portfolio_metrics(mix, sleeves, correlations, reserve_assets)
        show_allocation_bar(mix)
        metrics = st.columns(3)
        metrics[0].metric("Expected return", f"{result['return']:.2%}")
        metrics[1].metric("Volatility", f"{result['volatility']:.2%}")
        metrics[2].metric("Reserve weight", f"{result['reserve']:.0%}")
        return_passes = result["return"] + 1e-12 >= objective
        reserve_passes = result["reserve"] + 1e-12 >= reserve_minimum
        overall = return_passes and reserve_passes
        st.markdown(
            '<div class="rule-grid">'
            f'<div class="rule-chip {"pass" if return_passes else "fail"}">'
            f'<b>RETURN · {"PASS" if return_passes else "FAIL"}</b>'
            f'{result["return"]:.2%} / {objective:.2%}</div>'
            f'<div class="rule-chip {"pass" if reserve_passes else "fail"}">'
            f'<b>RESERVE · {"PASS" if reserve_passes else "FAIL"}</b>'
            f'{result["reserve"]:.0%} / {reserve_minimum:.0%}</div>'
            f'<div class="rule-chip {"pass" if overall else "fail"}">'
            f'<b>MANDATE · {"PASS" if overall else "FAIL"}</b>'
            'Long-only, fully invested</div></div>',
            unsafe_allow_html=True,
        )
        return result


st.sidebar.header("Mandate and data")
st.sidebar.caption("Move one control, then follow its effect through the dashboard.")
objective_percent = st.sidebar.number_input(
    "Objective expected return (%)",
    min_value=-100.0,
    max_value=100.0,
    value=OBJECTIVE_RETURN * 100.0,
    step=0.1,
)
reserve_percent = st.sidebar.number_input(
    "Minimum reserve-eligible weight (%)",
    min_value=0.0,
    max_value=100.0,
    value=DEFAULT_RESERVE_MINIMUM * 100.0,
    step=1.0,
)
stability_limit_percent = st.sidebar.number_input(
    "Maximum acceptable allocation move (points)",
    min_value=0.0,
    max_value=100.0,
    value=DEFAULT_STABILITY_LIMIT * 100.0,
    step=1.0,
)
annual_cost_bps = st.sidebar.number_input(
    "Annual implementation cost (basis points)",
    min_value=0.0,
    max_value=500.0,
    value=0.0,
    step=5.0,
)
uploaded_file = st.sidebar.file_uploader("Upload monthly prices.csv", type="csv")
last_36 = st.sidebar.toggle("Use only the last 36 monthly returns", value=False)

try:
    if uploaded_file is None:
        source_input: Path | bytes = PRICE_FILE
        loaded_sleeves, loaded_correlations = estimate_from_price_csv(
            PRICE_FILE, last_36_months=False
        )
        active_sleeves, active_correlations = estimate_from_price_csv(
            PRICE_FILE, last_36_months=last_36
        )
        source_label = "saved prices.csv"
        widget_source = f"saved-{'36' if last_36 else 'all'}"
    else:
        uploaded_bytes = uploaded_file.getvalue()
        source_input = uploaded_bytes
        loaded_sleeves, loaded_correlations = estimate_from_price_csv(
            BytesIO(uploaded_bytes), last_36_months=False
        )
        active_sleeves, active_correlations = estimate_from_price_csv(
            BytesIO(uploaded_bytes), last_36_months=last_36
        )
        source_label = uploaded_file.name
        widget_source = f"csv-{uploaded_file.name}-{'36' if last_36 else 'all'}"

    first_date, last_date, price_rows = data_card(source_input)
    point_signal = load_point_in_time_signal()
    default_reserve = {"BIL", "IEF", "SGOV", "VGIT"} & set(active_sleeves)
    baseline_reserve = {"BIL", "IEF", "SGOV", "VGIT"} & set(loaded_sleeves)
    baseline_sleeves = deepcopy(loaded_sleeves)
    baseline_correlations = deepcopy(loaded_correlations)
    saved_mix = search_lowest_risk_mix(
        baseline_sleeves,
        baseline_correlations,
        OBJECTIVE_RETURN,
        baseline_reserve,
        DEFAULT_RESERVE_MINIMUM,
    )

    st.markdown(
        """
        <div class="decision-strip">
          <div class="decision-item"><small>Decision</small><strong>Paper pilot only</strong></div>
          <div class="decision-item"><small>Capital</small><strong>No client allocation</strong></div>
          <div class="decision-item"><small>Key risk</small><strong>Window instability</strong></div>
          <div class="decision-item"><small>Reversal rule</small><strong>&gt;10-point move</strong></div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.caption(
        "OpenAI Codex assisted with code, testing, and documentation. The analysis "
        "and decision are the student's; education, not investment advice."
    )

    data_columns = st.columns(4)
    data_columns[0].metric("Input mode", "Uploaded CSV" if uploaded_file else "Saved CSV")
    data_columns[1].metric("Asset sleeves", len(active_sleeves))
    data_columns[2].metric("Price observations", price_rows)
    data_columns[3].metric("Estimation window", "Last 36 returns" if last_36 else "All returns")
    with st.expander("Data card and method"):
        st.markdown(
            f"**Source:** {source_label}  \n"
            f"**First observation:** {first_date}  \n"
            f"**Last observation:** {last_date}  \n"
            f"**Coverage:** {price_rows} monthly price rows / {price_rows - 1} returns  \n"
            "**Method:** arithmetic monthly returns; annual expected return is "
            "monthly mean × 12; annual volatility is sample monthly standard "
            "deviation × √12; correlations are estimated from the same window."
        )
        st.caption("Historical estimates are inputs to a classroom decision system, not forecasts.")

    with st.container(border=True):
        signal_columns = st.columns([1, 1, 2])
        signal_columns[0].metric(
            f"{point_signal['series_id']} point-in-time value",
            f"{float(point_signal['value_percent']):.2f}%",
        )
        signal_columns[1].metric("Monitoring signal", point_signal["signal"])
        signal_columns[2].markdown(
            f"**Rule:** value at or above {float(point_signal['signal_threshold_percent']):.2f}% "
            f"turns on a rate watch. {point_signal['decision_use']}."
        )
        with st.expander("Point-in-time signal data card"):
            st.markdown(
                f"**Series:** {point_signal['series_id']} - 10-year Treasury constant maturity rate  \n"
                f"**Measurement date:** {point_signal['measurement_date']}  \n"
                f"**Vintage/as-known date:** {point_signal['vintage_date']}  \n"
                f"**Value and units:** {float(point_signal['value_percent']):.2f}% per year  \n"
                f"**Source:** [Federal Reserve Bank of St. Louis / FRED]({point_signal['source_url']})  \n"
                f"**Download date:** {point_signal['download_date']}  \n"
                f"**Release rule:** {point_signal['release_rule']}  \n"
                "**Transformation:** compare the frozen value with the student-defined 5.00% "
                "monitoring threshold; no optimization weight is changed automatically."
            )

    st.markdown(
        '<div class="section-label"><span>1</span> Adjust assumptions</div>',
        unsafe_allow_html=True,
    )
    st.subheader("Gross expected-return inputs")
    horizon_label = "last 36 monthly returns" if last_36 else "all saved monthly returns"
    st.markdown(
        f'<div class="source-note"><strong>Source:</strong> {source_label}. '
        f"The displayed estimates use {horizon_label}. The selected cost drag is "
        f"deducted after these inputs. Change one field at a time so the scenario "
        "remains explainable.</div>",
        unsafe_allow_html=True,
    )
    return_columns = st.columns(len(active_sleeves))
    for column, (asset, inputs) in zip(return_columns, active_sleeves.items()):
        with column:
            edited_return = st.number_input(
                f"{asset} expected return (%)",
                min_value=-100.0,
                max_value=100.0,
                value=inputs["expected_return"] * 100.0,
                step=0.1,
                format="%.2f",
                key=f"return-{widget_source}-{asset}",
            )
            inputs["expected_return"] = edited_return / 100.0

    st.subheader("Reserve eligibility")
    st.caption("Checked sleeves count toward the minimum reserve requirement.")
    reserve_columns = st.columns(len(active_sleeves))
    selected_reserve: set[str] = set()
    for column, asset in zip(reserve_columns, active_sleeves):
        with column:
            if st.checkbox(
                asset,
                value=asset in default_reserve,
                key=f"reserve-{widget_source}-{asset}",
            ):
                selected_reserve.add(asset)

    objective = objective_percent / 100.0
    reserve_minimum = reserve_percent / 100.0
    stability_limit = stability_limit_percent / 100.0
    annual_cost = annual_cost_bps / 10_000.0
    scenario_sleeves = deepcopy(active_sleeves)
    for inputs in scenario_sleeves.values():
        inputs["expected_return"] -= annual_cost
    active_mix = search_lowest_risk_mix(
        scenario_sleeves,
        active_correlations,
        objective,
        selected_reserve,
        reserve_minimum,
    )
    comparison_portfolios = {
        "Equal weight": equal_weights(scenario_sleeves),
        "Inverse volatility": inverse_volatility_weights(scenario_sleeves),
        "60/40 benchmark": benchmark_mix(scenario_sleeves),
        "Constrained mix": active_mix,
    }

    st.markdown(
        '<div class="section-label"><span>2</span> Compare allocations</div>',
        unsafe_allow_html=True,
    )
    st.subheader("Four transparent portfolio choices")
    st.caption(
        "The first three are reference portfolios. The fourth is the engine's "
        "lowest-volatility feasible mix. Verdicts cover the encoded return, "
        "reserve, long-only, and fully-invested rules; issuer, five-day liquidity, "
        "turnover, and the undefined calendar-loss promise are not established."
    )
    portfolio_results: dict[str, dict[str, float] | None] = {}
    first_row = st.columns(2)
    with first_row[0]:
        portfolio_results["Equal weight"] = show_portfolio(
            "Baseline 1 · Equal weight",
            "A simple 25% allocation to each saved sleeve.",
            comparison_portfolios["Equal weight"], scenario_sleeves, active_correlations,
            selected_reserve, objective, reserve_minimum,
        )
    with first_row[1]:
        portfolio_results["Inverse volatility"] = show_portfolio(
            "Baseline 2 · Inverse volatility",
            "A transparent risk-scaling rule with no return optimization.",
            comparison_portfolios["Inverse volatility"], scenario_sleeves, active_correlations,
            selected_reserve, objective, reserve_minimum,
        )
    second_row = st.columns(2)
    with second_row[0]:
        portfolio_results["60/40 benchmark"] = show_portfolio(
            "Benchmark · 60% VT / 40% BND",
            "The documented equity/bond reference allocation.",
            comparison_portfolios["60/40 benchmark"], scenario_sleeves, active_correlations,
            selected_reserve, objective, reserve_minimum,
        )
    with second_row[1]:
        portfolio_results["Constrained mix"] = show_portfolio(
            "Proposed · Constrained lowest risk",
            "Searches the 5-point grid for the lowest-volatility feasible mix.",
            comparison_portfolios["Constrained mix"], scenario_sleeves, active_correlations,
            selected_reserve, objective, reserve_minimum,
        )

    chart_rows = []
    for name, result in portfolio_results.items():
        if result is None:
            continue
        mandate = (
            "Pass"
            if result["return"] + 1e-12 >= objective
            and result["reserve"] + 1e-12 >= reserve_minimum
            else "Fail"
        )
        chart_rows.append(
            {
                "Portfolio": name,
                "Volatility": result["volatility"],
                "Expected return": result["return"],
                "Mandate": mandate,
            }
        )

    st.markdown(
        '<div class="section-label"><span>3</span> Inspect trade-offs</div>',
        unsafe_allow_html=True,
    )
    st.subheader("Risk / return map")
    if chart_rows:
        chart_data = pd.DataFrame(chart_rows)
        points = alt.Chart(chart_data).mark_circle(size=190).encode(
            x=alt.X("Volatility:Q", axis=alt.Axis(format="%", title="Annual volatility")),
            y=alt.Y("Expected return:Q", axis=alt.Axis(format="%", title="Estimated annual return")),
            color=alt.Color(
                "Mandate:N",
                scale=alt.Scale(domain=["Pass", "Fail"], range=["#16794b", "#b42318"]),
            ),
            tooltip=[
                "Portfolio:N",
                alt.Tooltip("Expected return:Q", format=".2%"),
                alt.Tooltip("Volatility:Q", format=".2%"),
                "Mandate:N",
            ],
        )
        labels = alt.Chart(chart_data).mark_text(
            align="left", dx=9, dy=-8, color="#10243e"
        ).encode(x="Volatility:Q", y="Expected return:Q", text="Portfolio:N")
        return_rule = alt.Chart(pd.DataFrame({"target": [objective]})).mark_rule(
            color="#b7791f", strokeDash=[5, 5]
        ).encode(y="target:Q")
        st.altair_chart(
            (return_rule + points + labels).properties(height=330),
            width="stretch",
        )
        st.caption("Gold dashed line: current return objective. Green points pass the return and reserve rules.")

    st.subheader("Current scenario vs. frozen baseline")
    st.caption("The frozen baseline always uses all saved months, a 6.50% objective, a 3% reserve minimum, and the saved return estimates.")
    if active_mix is not None and saved_mix is not None:
        baseline_result = portfolio_metrics(
            saved_mix, baseline_sleeves, baseline_correlations, baseline_reserve
        )
        active_result = portfolio_metrics(
            active_mix, scenario_sleeves, active_correlations, selected_reserve
        )
        scenario_rows = [
            {
                "Measure": "Allocation",
                "Frozen baseline": " / ".join(f"{asset} {weight:.0%}" for asset, weight in saved_mix.items()),
                "Current scenario": " / ".join(f"{asset} {weight:.0%}" for asset, weight in active_mix.items()),
            },
            {
                "Measure": "Annual cost drag",
                "Frozen baseline": "0 basis points",
                "Current scenario": f"{annual_cost_bps:.0f} basis points",
            },
            {
                "Measure": "Expected return",
                "Frozen baseline": f"{baseline_result['return']:.2%}",
                "Current scenario": f"{active_result['return']:.2%}",
            },
            {
                "Measure": "Volatility",
                "Frozen baseline": f"{baseline_result['volatility']:.2%}",
                "Current scenario": f"{active_result['volatility']:.2%}",
            },
            {
                "Measure": "Reserve weight",
                "Frozen baseline": f"{baseline_result['reserve']:.0%}",
                "Current scenario": f"{active_result['reserve']:.0%}",
            },
        ]
        st.dataframe(pd.DataFrame(scenario_rows), hide_index=True, width="stretch")

        changes = {
            asset: abs(active_mix[asset] - saved_mix[asset])
            for asset in active_mix
        }
        largest_asset = max(changes, key=changes.get)
        largest_change = changes[largest_asset]
        st.markdown(
            '<div class="section-label"><span>4</span> Read the verdict</div>',
            unsafe_allow_html=True,
        )
        st.subheader("Decision checks")
        verdict_columns = st.columns(3)
        with verdict_columns[0]:
            st.success(
                "**Encoded mandate: PASS**\n\nThe proposed mix reaches the current return "
                "objective and reserve minimum; uncoded IPS rules remain open."
            )
        stability_passes = largest_change <= stability_limit + 1e-12
        selected_verdict = "PASS" if stability_passes else "FAIL"
        with verdict_columns[1]:
            message = (
                f"**Selected test: {selected_verdict}**\n\nLargest move: "
                f"**{largest_change * 100:.0f} points** ({largest_asset}), "
                f"{'within' if stability_passes else 'above'} the "
                f"{stability_limit * 100:.0f}-point limit."
            )
            if stability_passes:
                st.info(message)
            else:
                st.error(message)
        with verdict_columns[2]:
            st.warning(
                "**Committee: PAPER PILOT ONLY**\n\nNo client allocation. The saved "
                "all-month versus 36-month test moves SGOV and VT by 20 points."
            )
        st.caption(
            "The selected scenario can pass while adoption remains blocked by the saved window-instability evidence."
        )
    else:
        st.error(
            "**Mandate: FAIL** — no mix on the 5-point grid reaches both the "
            "current return objective and reserve minimum."
        )
        st.warning(
            "**Committee: DO NOT PILOT THIS SCENARIO** — review the mandate or "
            "input assumptions before proposing an allocation."
        )
except ValueError as exc:
    st.error(f"Input error: {exc}")
