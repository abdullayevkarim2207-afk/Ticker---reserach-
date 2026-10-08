"""Lab 12 audit: value every explicit FCFE with its reported sign.

This file preserves the submitted Lab 10 and Lab 11 files. It imports their
forecast engine, includes negative explicit-period FCFE in present value, and
reruns the two Lab 11 one-at-a-time sensitivities.
"""

from __future__ import annotations

import lab10_ford_proforma as model


YEARS = tuple(model.YEARS)
REVENUE_CASES = {
    "Lower": {year: 0.010 for year in YEARS},
    "Base": model.REVENUE_GROWTH.copy(),
    "Higher": {year: 0.035 for year in YEARS},
}
MARGIN_CASES = {
    "Lower": {year: 0.135 for year in YEARS},
    "Base": model.GROSS_MARGIN.copy(),
    "Higher": {year: 0.155 for year in YEARS},
}


def signed_value_per_share(forecasts: list[dict[str, float]]) -> float:
    """Discount all explicit FCFE, then add a positive terminal value."""
    explicit_value = sum(
        row["fcfe"] / (1.0 + model.COST_OF_EQUITY) ** index
        for index, row in enumerate(forecasts, start=1)
    )
    terminal_value = 0.0
    if forecasts[-1]["fcfe"] > 0.0:
        terminal_value = (
            forecasts[-1]["fcfe"]
            * (1.0 + model.TERMINAL_GROWTH)
            / (model.COST_OF_EQUITY - model.TERMINAL_GROWTH)
        )
    equity_value = explicit_value + terminal_value / (
        1.0 + model.COST_OF_EQUITY
    ) ** len(forecasts)
    return equity_value / model.SHARES_OUTSTANDING


def run_case(
    driver: str, input_path: dict[int, float]
) -> tuple[float, float, float, float]:
    revenue_growth = model.REVENUE_GROWTH.copy()
    gross_margin = model.GROSS_MARGIN.copy()
    if driver == "Revenue growth":
        revenue_growth = input_path.copy()
    elif driver == "Gross margin":
        gross_margin = input_path.copy()
    else:
        raise ValueError(f"Unknown driver: {driver}")

    forecasts = model.build_projection(
        revenue_growth=revenue_growth,
        gross_margin=gross_margin,
    )
    model.assert_balanced(forecasts)
    return (
        forecasts[-1]["operating_income"],
        forecasts[-1]["fcfe"],
        signed_value_per_share(forecasts),
        max(abs(row["balance_gap"]) for row in forecasts),
    )


def main() -> None:
    print("LAB 12 — SIGNED-FCFE AUDIT")
    print("Amounts are USD millions except value per share.")
    print(
        f"{'Driver / case':<29}{'FY2030 operating income':>25}"
        f"{'FY2030 FCFE':>16}{'Value/share':>16}{'Max gap':>14}"
    )
    print("-" * 100)

    results: dict[str, list[float]] = {}
    for driver, cases in (
        ("Revenue growth", REVENUE_CASES),
        ("Gross margin", MARGIN_CASES),
    ):
        results[driver] = []
        for case, input_path in cases.items():
            operating_income, fcfe, value, max_gap = run_case(driver, input_path)
            results[driver].append(value)
            print(
                f"{f'{driver} — {case}':<29}{operating_income:>25,.1f}"
                f"{fcfe:>16,.1f}{value:>16.2f}{max_gap:>14.6f}"
            )

    print("\nVALUE-PER-SHARE SPANS")
    for driver, values in results.items():
        print(f"{driver}: ${max(values) - min(values):.2f}")


if __name__ == "__main__":
    main()
