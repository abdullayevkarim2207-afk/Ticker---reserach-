"""Check candidate portfolios against Meridian's checkable mandate rules.

All portfolio weights and policy limits are percentages unless noted otherwise.
The calendar-year loss statement is intentionally not tested because the CIO
has not defined its measure or breach rule.
"""

from __future__ import annotations

from math import isclose


# Editable inputs
HOLDINGS = {
    "Cash": {
        "issuer": "none",
        "redemption_days": 0,
        "reserve_eligible": True,
    },
    "Treasury bills": {
        "issuer": "U.S. Treasury",
        "redemption_days": 1,
        "reserve_eligible": True,
    },
    "Treasury 10-year note": {
        "issuer": "U.S. Treasury",
        "redemption_days": 1,
        "reserve_eligible": True,
    },
    "Global equity index fund": {
        "issuer": "diversified fund",
        "redemption_days": 2,
        "reserve_eligible": False,
    },
    "Investment-grade bond fund": {
        "issuer": "diversified fund",
        "redemption_days": 3,
        "reserve_eligible": False,
    },
    "Private real estate fund": {
        "issuer": "diversified fund",
        "redemption_days": 90,
        "reserve_eligible": False,
    },
    "Acme Corp bonds": {
        "issuer": "Acme Corp",
        "redemption_days": 4,
        "reserve_eligible": False,
    },
    "Acme Corp stock": {
        "issuer": "Acme Corp",
        "redemption_days": 1,
        "reserve_eligible": False,
    },
}

CANDIDATES = {
    "A": {
        "Cash": 2,
        "Treasury bills": 2,
        "Treasury 10-year note": 10,
        "Global equity index fund": 60,
        "Investment-grade bond fund": 26,
        "Private real estate fund": 0,
        "Acme Corp bonds": 0,
        "Acme Corp stock": 0,
    },
    "B": {
        "Cash": 1,
        "Treasury bills": 0,
        "Treasury 10-year note": 0,
        "Global equity index fund": 55,
        "Investment-grade bond fund": 20,
        "Private real estate fund": 15,
        "Acme Corp bonds": 5,
        "Acme Corp stock": 4,
    },
    "C": {
        "Cash": 1,
        "Treasury bills": 1,
        "Treasury 10-year note": 0,
        "Global equity index fund": 70,
        "Investment-grade bond fund": 20,
        "Private real estate fund": 0,
        "Acme Corp bonds": 0,
        "Acme Corp stock": 8,
    },
    # Attack portfolio: passes every coded rule but may be unsuitable for S2.
    "D": {
        "Cash": 100,
        "Treasury bills": 0,
        "Treasury 10-year note": 0,
        "Global equity index fund": 0,
        "Investment-grade bond fund": 0,
        "Private real estate fund": 0,
        "Acme Corp bonds": 0,
        "Acme Corp stock": 0,
    },
}

RESERVE_SIZE_USD_MILLIONS = 100
QUARTERLY_DISTRIBUTION_USD_MILLIONS = 0.75
QUARTERS_TO_COVER = 4
LIQUIDITY_WINDOW_BUSINESS_DAYS = 5
MINIMUM_LIQUID_SHARE = 90
ISSUER_LIMIT = 8
ISSUER_EXEMPTIONS = {"none", "U.S. Treasury", "diversified fund"}


def status(passed: bool) -> str:
    """Return the required display label for a rule result."""
    return "pass" if passed else "FAIL"


def check_candidate(
    name: str, weights: dict[str, float], reserve_minimum: float
) -> None:
    """Measure and print every checkable rule for one candidate."""
    missing_holdings = set(HOLDINGS) - set(weights)
    unknown_holdings = set(weights) - set(HOLDINGS)
    if missing_holdings or unknown_holdings:
        raise ValueError(
            f"Candidate {name} does not match the holdings table; "
            f"missing={sorted(missing_holdings)}, unknown={sorted(unknown_holdings)}"
        )

    total_weight = sum(weights.values())
    lowest_weight = min(weights.values())
    reserve_weight = sum(
        weights[holding]
        for holding, details in HOLDINGS.items()
        if details["reserve_eligible"]
    )
    liquid_weight = sum(
        weights[holding]
        for holding, details in HOLDINGS.items()
        if details["redemption_days"] <= LIQUIDITY_WINDOW_BUSINESS_DAYS
    )

    company_weights: dict[str, float] = {}
    for holding, weight in weights.items():
        issuer = HOLDINGS[holding]["issuer"]
        if issuer not in ISSUER_EXEMPTIONS:
            company_weights[issuer] = company_weights.get(issuer, 0.0) + weight
    largest_company_weight = max(company_weights.values(), default=0.0)

    checks = (
        ("Weights sum to 100", total_weight, isclose(total_weight, 100.0)),
        ("Long-only (lowest weight)", lowest_weight, lowest_weight >= 0.0),
        (
            f"Reserve >= {reserve_minimum:.1f}%",
            reserve_weight,
            reserve_weight >= reserve_minimum,
        ),
        (
            "Redeemable in "
            f"{LIQUIDITY_WINDOW_BUSINESS_DAYS} days >= "
            f"{MINIMUM_LIQUID_SHARE:.1f}%",
            liquid_weight,
            liquid_weight >= MINIMUM_LIQUID_SHARE,
        ),
        (
            f"Largest single company <= {ISSUER_LIMIT:.1f}%",
            largest_company_weight,
            largest_company_weight <= ISSUER_LIMIT,
        ),
    )

    print(f"\nCandidate {name}")
    failures = 0
    for label, measured_value, passed in checks:
        print(f"  {label}: {measured_value:.1f}% {status(passed)}")
        failures += not passed
    print("  Calendar-year loss: requires CIO clarification")
    if failures:
        print(f"  Verdict: fails {failures} rule(s)")
    else:
        print("  Verdict: passes every checkable rule")


def main() -> None:
    reserve_minimum = (
        QUARTERS_TO_COVER
        * QUARTERLY_DISTRIBUTION_USD_MILLIONS
        / RESERVE_SIZE_USD_MILLIONS
        * 100
    )
    print(f"Reserve minimum: {reserve_minimum:.1f}% of the portfolio")
    for name, weights in CANDIDATES.items():
        check_candidate(name, weights, reserve_minimum)


if __name__ == "__main__":
    main()
