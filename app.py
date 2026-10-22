"""Streamlit interface for the reusable portfolio engine."""

from copy import deepcopy
from io import BytesIO

import streamlit as st

from portfolio import (
    CORRELATIONS,
    OBJECTIVE_RETURN,
    RESERVE_ELIGIBLE,
    SLEEVES,
    build_covariance_matrix,
    estimate_from_price_csv,
    expected_return,
    portfolio_volatility,
    reserve_eligible_weight,
    search_lowest_risk_mix,
)


st.set_page_config(page_title="Portfolio Stability Decision", layout="wide")
st.title("Portfolio Stability Decision")
st.caption("Built with AI help, a learning demonstration, not investment advice.")

st.sidebar.header("Mandate and data")
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
        loaded_sleeves = deepcopy(SLEEVES)
        loaded_correlations = deepcopy(CORRELATIONS)
        active_sleeves = deepcopy(SLEEVES)
        active_correlations = deepcopy(CORRELATIONS)
        source_label = "Meridian training inputs"
        horizon_label = "course-authored annual training estimates"
        default_reserve = RESERVE_ELIGIBLE
        widget_source = "meridian"
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

    st.subheader("Expected returns")
    st.write(
        f"Source: **{source_label}**. Returns shown below are a {horizon_label}, "
        "not a forecast. Edit any box to test estimation risk."
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

    def show_answer(
        heading: str,
        mix: dict[str, float] | None,
        sleeves: dict[str, dict[str, float]],
        correlations: dict[str, dict[str, float]],
    ) -> None:
        st.markdown(f"### {heading}")
        if mix is None:
            st.error("No mix meets the objective.")
            return
        covariance = build_covariance_matrix(sleeves, correlations)
        st.table(
            {
                "Asset": list(mix),
                "Weight": [f"{weight:.0%}" for weight in mix.values()],
            }
        )
        metric_columns = st.columns(3)
        metric_columns[0].metric("Expected return", f"{expected_return(mix, sleeves):.2%}")
        metric_columns[1].metric(
            "Volatility", f"{portfolio_volatility(mix, covariance):.2%}"
        )
        metric_columns[2].metric(
            "Reserve-eligible weight",
            f"{reserve_eligible_weight(mix, selected_reserve):.0%}",
        )

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
        st.info(
            f"Largest weight change: **{changes[largest_asset] * 100:.0f} points** "
            f"({largest_asset})."
        )
    else:
        st.info("Largest weight change is unavailable because one answer is infeasible.")
except ValueError as exc:
    st.error(str(exc))
