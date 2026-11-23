"""Reproduce the decision evidence for FIN 43900 Project 2.

Run from the repository root with: python3 project2_run.py
"""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path

from portfolio import (
    build_covariance_matrix,
    equal_weights,
    estimate_from_price_csv,
    expected_return,
    inverse_volatility_weights,
    portfolio_volatility,
    reserve_eligible_weight,
    search_lowest_risk_mix,
)


OBJECTIVE = 0.065
RESERVE_MINIMUM = 0.03
RESERVE_ELIGIBLE = {"SGOV", "VGIT"}
ANNUAL_COST_STRESS = 0.0025
RESERVE_CONSTRAINT_STRESS = 0.70
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


def calculate_baselines() -> dict[str, dict[str, object]]:
    """Calculate the two transparent baselines and the documented benchmark."""
    sleeves, correlations = estimate_from_price_csv(PRICE_FILE)
    covariance = build_covariance_matrix(sleeves, correlations)
    benchmark = {asset: 0.0 for asset in sleeves}
    benchmark["BND"] = 0.40
    benchmark["VT"] = 0.60
    mixes = {
        "Equal weight": equal_weights(sleeves),
        "Inverse volatility": inverse_volatility_weights(sleeves),
        "60/40 benchmark": benchmark,
    }
    results = {}
    for name, weights in mixes.items():
        portfolio_return = expected_return(weights, sleeves)
        reserve = reserve_eligible_weight(weights, RESERVE_ELIGIBLE)
        failed_rules = []
        if portfolio_return + 1e-12 < OBJECTIVE:
            failed_rules.append("return")
        if reserve + 1e-12 < RESERVE_MINIMUM:
            failed_rules.append("reserve")
        results[name] = {
            "weights": weights,
            "return": portfolio_return,
            "volatility": portfolio_volatility(weights, covariance),
            "reserve": reserve,
            "verdict": "PASS" if not failed_rules else "FAIL: " + ", ".join(failed_rules),
        }
    return results


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


def calculate_cost_stress() -> dict[str, object]:
    """Deduct a 25-basis-point annual cost drag and rerun the search."""
    sleeves, correlations = estimate_from_price_csv(PRICE_FILE)
    net_sleeves = deepcopy(sleeves)
    for inputs in net_sleeves.values():
        inputs["expected_return"] -= ANNUAL_COST_STRESS
    weights = search_lowest_risk_mix(
        net_sleeves,
        correlations,
        OBJECTIVE,
        RESERVE_ELIGIBLE,
        RESERVE_MINIMUM,
    )
    if weights is None:
        raise RuntimeError("The cost stress produced no feasible portfolio.")
    covariance = build_covariance_matrix(net_sleeves, correlations)
    return {
        "sleeves": net_sleeves,
        "correlations": correlations,
        "weights": weights,
        "return": expected_return(weights, net_sleeves),
        "volatility": portfolio_volatility(weights, covariance),
        "reserve": reserve_eligible_weight(weights, RESERVE_ELIGIBLE),
    }


def calculate_constraint_stress() -> dict[str, object] | None:
    """Raise the reserve minimum to 70%; ``None`` is the explicit stop result."""
    sleeves, correlations = estimate_from_price_csv(PRICE_FILE)
    weights = search_lowest_risk_mix(
        sleeves,
        correlations,
        OBJECTIVE,
        RESERVE_ELIGIBLE,
        RESERVE_CONSTRAINT_STRESS,
    )
    if weights is None:
        return None
    covariance = build_covariance_matrix(sleeves, correlations)
    return {
        "sleeves": sleeves,
        "correlations": correlations,
        "weights": weights,
        "return": expected_return(weights, sleeves),
        "volatility": portfolio_volatility(weights, covariance),
        "reserve": reserve_eligible_weight(weights, RESERVE_ELIGIBLE),
    }


def format_weights(weights: dict[str, float]) -> str:
    """Return weights in the saved CSV column order."""
    return " / ".join(f"{ticker} {weight:.0%}" for ticker, weight in weights.items())


def main() -> None:
    baselines = calculate_baselines()
    all_months = calculate_case()
    recent = calculate_case(last_36_months=True)
    stress = calculate_vt_stress()
    cost_stress = calculate_cost_stress()
    constraint_stress = calculate_constraint_stress()
    largest_window_change = max(
        abs(recent["weights"][ticker] - all_months["weights"][ticker])
        for ticker in all_months["weights"]
    )

    print("FIN 43900 Project 2 decision output")
    print("OpenAI Codex supported code, testing, debugging, and documentation.")
    print("The analysis and decision are mine; education, not investment advice.")
    print("Data: 61 monthly adjusted-close observations, 2021-09-01 to 2026-09-01")
    print("Objective: return >= 6.50%; SGOV + VGIT reserve >= 3.00%")
    print()
    print("Transparent baselines and benchmark (encoded mandate)")
    for label, case in baselines.items():
        print(f"  {label}: {format_weights(case['weights'])}")
        print(
            f"    Return {case['return']:.2%}; volatility {case['volatility']:.2%}; "
            f"reserve {case['reserve']:.0%}; {case['verdict']}"
        )
    print()
    for label, case in (
        ("All 60 monthly returns", all_months),
        ("Last 36 monthly returns", recent),
        ("VT expected-return stress (-1.00 point)", stress),
        ("Annual implementation-cost stress (25 basis points)", cost_stress),
    ):
        print(label)
        print(f"  Weights: {format_weights(case['weights'])}")
        print(f"  Estimated return: {case['return']:.2%}")
        print(f"  Estimated volatility: {case['volatility']:.2%}")
        print(f"  Reserve-eligible weight: {case['reserve']:.0%}")
    print("Reserve-constraint stress (minimum raised from 3% to 70%)")
    if constraint_stress is None:
        print("  STOP: no feasible portfolio exists on the 5-point grid.")
    else:
        print(f"  Weights: {format_weights(constraint_stress['weights'])}")
    print()
    print(f"Largest all-month versus 36-month weight change: {largest_window_change:.0%}")
    print("Decision: tightly bounded pilot; do not adopt or allocate client capital yet.")
    print("Reversal trigger: reject if an estimate, cost, or window stress moves any")
    print("weight by more than 10 points; stop if no feasible mix or a lineage check fails.")


if __name__ == "__main__":
    main()
