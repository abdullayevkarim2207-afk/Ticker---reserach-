"""Streamlit interface for the reusable portfolio engine."""

from copy import deepcopy
from io import BytesIO
from pathlib import Path

import streamlit as st

from portfolio import (
    OBJECTIVE_RETURN,
    build_covariance_matrix,
    estimate_from_price_csv,
    expected_return,
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
STABILITY_LIMIT = 0.10

st.sidebar.header("Mandate and data")
st.sidebar.caption("Change one control at a time, then read the verdict at the bottom.")
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
    value=3.0,
    step=1.0,
)
uploaded_file = st.sidebar.file_uploader("Upload monthly prices.csv", type="csv")
last_36 = st.sidebar.toggle("Use only the last 36 monthly returns", value=False)

try:
    if uploaded_file is None:
        loaded_sleeves, loaded_correlations = estimate_from_price_csv(
            PRICE_FILE, last_36_months=False
        )
        active_sleeves, active_correlations = estimate_from_price_csv(
            PRICE_FILE, last_36_months=last_36
        )
        source_label = "saved prices.csv"
        horizon_label = (
            "historical estimate from the last 36 monthly returns"
            if last_36
            else "historical estimate from all monthly returns"
        )
        default_reserve = {"SGOV", "VGIT"}
        widget_source = f"saved-{'36' if last_36 else 'all'}"
    else:
        uploaded_bytes = uploaded_file.getvalue()
        loaded_sleeves, loaded_correlations = estimate_from_price_csv(
            BytesIO(uploaded_bytes), last_36_months=False
        )
        active_sleeves, active_correlations = estimate_from_price_csv(
            BytesIO(uploaded_bytes), last_36_months=last_36
        )
        source_label = f"{uploaded_file.name}"
        horizon_label = (
            "historical estimate from the last 36 monthly returns"
            if last_36
            else "historical estimate from all monthly returns"
        )
        default_reserve = {"BIL", "IEF", "SGOV", "VGIT"} & set(active_sleeves)
        widget_source = f"csv-{uploaded_file.name}-{'36' if last_36 else 'all'}"

    st.markdown(
        '<div class="section-label"><span>1</span> Adjust assumptions</div>',
        unsafe_allow_html=True,
    )
    st.subheader("Expected-return inputs")
    st.markdown(
        f'<div class="source-note"><strong>Source:</strong> {source_label}. '
        f"These values are a {horizon_label}, not a forecast. Change one box "
        "to test how sensitive the allocation is.</div>",
        unsafe_allow_html=True,
    )
    return_columns = st.columns(len(active_sleeves))
    for column, (asset, inputs) in zip(return_columns, active_sleeves.items()):
        with column:
            edited_return = st.number_input(
                asset,
                min_value=-100.0,
                max_value=100.0,
                value=inputs["expected_return"] * 100.0,
                step=0.1,
                format="%.2f",
                key=f"return-{widget_source}-{asset}",
            )
            inputs["expected_return"] = edited_return / 100.0

    st.subheader("Reserve eligibility")
    st.caption("Checked assets count toward the minimum reserve requirement.")
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
    loaded_mix = search_lowest_risk_mix(
        loaded_sleeves,
        loaded_correlations,
        objective,
        selected_reserve,
        reserve_minimum,
    )
    active_mix = search_lowest_risk_mix(
        active_sleeves,
        active_correlations,
        objective,
        selected_reserve,
        reserve_minimum,
    )

    asset_colors = {
        "SGOV": "#175cd3",
        "VGIT": "#61a0ff",
        "BND": "#b7791f",
        "VT": "#1f9d68",
    }

    def show_allocation_bar(mix: dict[str, float]) -> None:
        segments = "".join(
            f'<span class="allocation-segment" style="width:{weight * 100:.0f}%;'
            f'background:{asset_colors.get(asset, "#8091a5")}"></span>'
            for asset, weight in mix.items()
            if weight > 0
        )
        legend = "".join(
            f'<span class="legend-item"><span class="legend-dot" '
            f'style="background:{asset_colors.get(asset, "#8091a5")}"></span>'
            f'{asset} {weight:.0%}</span>'
            for asset, weight in mix.items()
        )
        st.markdown(
            f'<div class="allocation-bar">{segments}</div><div class="legend-row">{legend}</div>',
            unsafe_allow_html=True,
        )

    def show_answer(
        heading: str,
        mix: dict[str, float] | None,
        sleeves: dict[str, dict[str, float]],
        correlations: dict[str, dict[str, float]],
    ) -> None:
        with st.container(border=True):
            st.markdown(f"### {heading}")
            if mix is None:
                st.error("No mix meets the objective.")
                return
            covariance = build_covariance_matrix(sleeves, correlations)
            show_allocation_bar(mix)
            st.table(
                {
                    "Asset": list(mix),
                    "Weight": [f"{weight:.0%}" for weight in mix.values()],
                }
            )
            metric_columns = st.columns(3)
            metric_columns[0].metric(
                "Expected return", f"{expected_return(mix, sleeves):.2%}"
            )
            metric_columns[1].metric(
                "Volatility", f"{portfolio_volatility(mix, covariance):.2%}"
            )
            metric_columns[2].metric(
                "Reserve weight",
                f"{reserve_eligible_weight(mix, selected_reserve):.0%}",
            )

    st.markdown(
        '<div class="section-label"><span>2</span> Compare allocations</div>',
        unsafe_allow_html=True,
    )
    st.subheader("Current controls vs. saved baseline")
    st.caption("The left panel reacts to your controls. The right panel stays anchored to all saved months.")
    result_columns = st.columns(2)
    with result_columns[0]:
        show_answer("Current controls", active_mix, active_sleeves, active_correlations)
    with result_columns[1]:
        show_answer(
            "Inputs as loaded (all months for CSV)",
            loaded_mix,
            loaded_sleeves,
            loaded_correlations,
        )

    if active_mix is not None and loaded_mix is not None:
        changes = {
            asset: abs(active_mix[asset] - loaded_mix[asset])
            for asset in active_mix
        }
        largest_asset = max(changes, key=changes.get)
        st.markdown(
            '<div class="section-label"><span>3</span> Read the verdict</div>',
            unsafe_allow_html=True,
        )
        st.subheader("Decision checks")
        verdict_columns = st.columns(3)
        with verdict_columns[0]:
            st.success(
                "**Mandate: PASS**\n\nThe displayed mix reaches the return objective "
                "and reserve minimum."
            )
        stability_passes = changes[largest_asset] <= STABILITY_LIMIT
        verdict = "PASS" if stability_passes else "FAIL"
        with verdict_columns[1]:
            if stability_passes:
                st.info(
                    f"**Selected test: {verdict}**\n\nLargest move: "
                    f"**{changes[largest_asset] * 100:.0f} points** ({largest_asset}), "
                    "within the 10-point limit."
                )
            else:
                st.error(
                    f"**Selected test: {verdict}**\n\nLargest move: "
                    f"**{changes[largest_asset] * 100:.0f} points** ({largest_asset}), "
                    "above the 10-point limit."
                )
        with verdict_columns[2]:
            st.warning(
                "**Committee: PAPER PILOT ONLY**\n\nNo client allocation. The saved "
                "window test moves SGOV and VT by 20 points."
            )
        st.caption(
            "Overall adoption remains blocked even when a different single-control test passes."
        )
    else:
        st.error(
            "Mandate verdict: **FAIL** - no mix on the 5-point grid meets the "
            "current return objective and reserve minimum."
        )
except ValueError as exc:
    st.error(str(exc))
