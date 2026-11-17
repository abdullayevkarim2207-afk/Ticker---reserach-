"""Reproduce the decision evidence for FIN 43900 Project 2.

Run from the repository root with: python3 project2_run.py
"""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path

from portfolio import (
    build_covariance_matrix,
    estimate_from_price_csv,
    expected_return,
    portfolio_volatility,
    reserve_eligible_weight,
    search_lowest_risk_mix,
)


OBJECTIVE = 0.065
RESERVE_MINIMUM = 0.03
RESERVE_ELIGIBLE = {"SGOV", "VGIT"}
PRICE_FILE = Path(__file__).with_name("prices.csv")


def calculate_case(last_36_months: bool = False) -> dict[str, object]:
    """Calculate one historical-window case from the saved price file."""
    sleeves, correlations = estimate_from_price_csv(
        PRICE_FILE, last_36_months=last_36_months
    )
    weights = search_lowest_risk_mix(
        sleeves, correlations, OBJECTIVE, RESERVE_ELIGIBLE, RESERVE_MINIMUM
    )
    if weights is None:
        raise RuntimeError("No feasible portfolio was found on the 5-point grid.")
    covariance = build_covariance_matrix(sleeves, correlations)
    return {
        "sleeves": sleeves,
        "correlations": correlations,
        "weights": weights,
        "return": expected_return(weights, sleeves),
        "volatility": portfolio_volatility(weights, covariance),
        "reserve": reserve_eligible_weight(weights, RESERVE_ELIGIBLE),
    }


def calculate_vt_stress() -> dict[str, object]:
    """Reduce VT's estimated return by one point and rerun the same search."""
    sleeves, correlations = estimate_from_price_csv(PRICE_FILE)
    stressed_sleeves = deepcopy(sleeves)
    stressed_sleeves["VT"]["expected_return"] -= 0.01
    weights = search_lowest_risk_mix(
        stressed_sleeves,
        correlations,
        OBJECTIVE,
        RESERVE_ELIGIBLE,
        RESERVE_MINIMUM,
    )
    if weights is None:
        raise RuntimeError("The VT stress produced no feasible portfolio.")
    covariance = build_covariance_matrix(stressed_sleeves, correlations)
    return {
        "sleeves": stressed_sleeves,
        "correlations": correlations,
        "weights": weights,
        "return": expected_return(weights, stressed_sleeves),
        "volatility": portfolio_volatility(weights, covariance),
        "reserve": reserve_eligible_weight(weights, RESERVE_ELIGIBLE),
    }


def format_weights(weights: dict[str, float]) -> str:
    """Return weights in the saved CSV column order."""
    return " / ".join(f"{ticker} {weight:.0%}" for ticker, weight in weights.items())


def main() -> None:
    all_months = calculate_case()
    recent = calculate_case(last_36_months=True)
    stress = calculate_vt_stress()
    largest_window_change = max(
        abs(recent["weights"][ticker] - all_months["weights"][ticker])
        for ticker in all_months["weights"]
    )

    print("FIN 43900 Project 2 decision output")
    print("AI-assisted learning demonstration; education, not investment advice.")
    print("Data: 61 monthly adjusted-close observations, 2021-09-01 to 2026-09-01")
    print("Objective: return >= 6.50%; SGOV + VGIT reserve >= 3.00%")
    print()
    for label, case in (
        ("All 60 monthly returns", all_months),
        ("Last 36 monthly returns", recent),
        ("VT expected-return stress (-1.00 point)", stress),
    ):
        print(label)
        print(f"  Weights: {format_weights(case['weights'])}")
        print(f"  Estimated return: {case['return']:.2%}")
        print(f"  Estimated volatility: {case['volatility']:.2%}")
        print(f"  Reserve-eligible weight: {case['reserve']:.0%}")
    print()
    print(f"Largest all-month versus 36-month weight change: {largest_window_change:.0%}")
    print("Decision: tightly bounded pilot; do not adopt or allocate client capital yet.")
    print("Reversal trigger: reject if a one-point input stress or window change moves")
    print("any weight by more than 10 points, or if a mandate rule fails.")


if __name__ == "__main__":
    main()
