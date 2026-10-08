"""Project 1 Ford industrial FCFF and Ford Credit bridge.

Educational FIN 43900 model. Amounts are USD millions except per-share data.
The model values Company-excluding-Ford-Credit operations with FCFF and adds
Ford Credit as a separately valued equity asset. This avoids subtracting Ford
Credit debt from an industrial enterprise value while ignoring the finance
assets and earnings funded by that debt.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass


YEARS = (2026, 2027, 2028, 2029, 2030)
TAX_RATE = 0.21
COMPANY_INTEREST = 1_249.4
COMPANY_CASH = 28_684.0
OPERATING_CASH_FLOOR = 20_000.0
EXCESS_COMPANY_CASH = COMPANY_CASH - OPERATING_CASH_FLOOR
COMPANY_DEBT = 21_919.0
PENSION_AND_OPEB_DEFICIT = 4_600.0
NONCONTROLLING_INTEREST = 28.0
FORD_CREDIT_EQUITY = 14_800.0
FORD_CREDIT_DEBT = 141_417.0
SHARES = 3_979.0
SAVED_MARKET_PRICE = 12.86


@dataclass(frozen=True)
class Scenario:
    name: str
    adjusted_fcf: float
    ford_credit_distribution: float
    growth: tuple[float, float, float, float, float]
    wacc: float
    terminal_growth: float
    ford_credit_equity_multiple: float


SCENARIOS = (
    Scenario(
        "Low",
        adjusted_fcf=6_000.0,
        ford_credit_distribution=2_000.0,
        growth=(0.00, 0.01, 0.02, 0.02, 0.02),
        wacc=0.11,
        terminal_growth=0.02,
        ford_credit_equity_multiple=0.80,
    ),
    Scenario(
        "Base",
        adjusted_fcf=6_500.0,
        ford_credit_distribution=1_700.0,
        growth=(0.00, 0.03, 0.03, 0.03, 0.02),
        wacc=0.10,
        terminal_growth=0.025,
        ford_credit_equity_multiple=1.00,
    ),
    Scenario(
        "High",
        adjusted_fcf=7_000.0,
        ford_credit_distribution=1_500.0,
        growth=(0.00, 0.05, 0.04, 0.03, 0.03),
        wacc=0.09,
        terminal_growth=0.03,
        ford_credit_equity_multiple=1.20,
    ),
)


def starting_industrial_fcff(case: Scenario) -> float:
    """Convert Company adjusted FCF to industrial FCFF without double count.

    Company adjusted FCF contains Ford Credit distributions and is after
    Company interest. Ford Credit is valued separately, so its distribution is
    removed. After-tax Company interest is added back to obtain unlevered FCFF.
    """
    after_tax_interest = COMPANY_INTEREST * (1.0 - TAX_RATE)
    return case.adjusted_fcf - case.ford_credit_distribution + after_tax_interest


def forecast_fcff(case: Scenario) -> list[float]:
    cash_flows: list[float] = []
    fcff = starting_industrial_fcff(case)
    for growth in case.growth:
        fcff *= 1.0 + growth
        cash_flows.append(fcff)
    return cash_flows


def enterprise_value(
    cash_flows: list[float], *, wacc: float, terminal_growth: float
) -> tuple[float, float, float]:
    if terminal_growth >= wacc:
        raise ValueError("Terminal growth must be below WACC")
    if len(cash_flows) != len(YEARS) or any(value <= 0.0 for value in cash_flows):
        raise ValueError("Five positive annual FCFF values are required")
    explicit_pv = sum(
        value / (1.0 + wacc) ** year
        for year, value in enumerate(cash_flows, start=1)
    )
    terminal_value = (
        cash_flows[-1]
        * (1.0 + terminal_growth)
        / (wacc - terminal_growth)
    )
    terminal_pv = terminal_value / (1.0 + wacc) ** len(cash_flows)
    return explicit_pv + terminal_pv, explicit_pv, terminal_pv


def equity_bridge(
    industrial_ev: float,
    *,
    ford_credit_multiple: float,
    subtract_ford_credit_debt: bool = False,
) -> dict[str, float]:
    if subtract_ford_credit_debt:
        raise ValueError(
            "Bridge perimeter failure: Ford Credit debt cannot be subtracted "
            "from industrial EV when Ford Credit is added as an equity asset"
        )
    ford_credit_value = FORD_CREDIT_EQUITY * ford_credit_multiple
    common_equity = (
        industrial_ev
        + EXCESS_COMPANY_CASH
        - COMPANY_DEBT
        + ford_credit_value
        - PENSION_AND_OPEB_DEFICIT
        - NONCONTROLLING_INTEREST
    )
    return {
        "industrial_ev": industrial_ev,
        "excess_company_cash": EXCESS_COMPANY_CASH,
        "company_debt": COMPANY_DEBT,
        "ford_credit_equity": ford_credit_value,
        "pension_and_opeb_deficit": PENSION_AND_OPEB_DEFICIT,
        "noncontrolling_interest": NONCONTROLLING_INTEREST,
        "common_equity": common_equity,
        "value_per_share": common_equity / SHARES,
    }


def evaluate(case: Scenario) -> dict[str, object]:
    cash_flows = forecast_fcff(case)
    industrial_ev, explicit_pv, terminal_pv = enterprise_value(
        cash_flows, wacc=case.wacc, terminal_growth=case.terminal_growth
    )
    bridge = equity_bridge(
        industrial_ev, ford_credit_multiple=case.ford_credit_equity_multiple
    )
    return {
        "case": case,
        "fcff": cash_flows,
        "explicit_pv": explicit_pv,
        "terminal_pv": terminal_pv,
        "terminal_share": terminal_pv / industrial_ev,
        "bridge": bridge,
    }


def value_for_rates(wacc: float, terminal_growth: float) -> float:
    base = next(case for case in SCENARIOS if case.name == "Base")
    industrial_ev, _, _ = enterprise_value(
        forecast_fcff(base), wacc=wacc, terminal_growth=terminal_growth
    )
    return equity_bridge(
        industrial_ev, ford_credit_multiple=base.ford_credit_equity_multiple
    )["value_per_share"]


def implied_starting_fcff(target_price: float) -> float:
    """Solve the starting FCFF consistent with price under base assumptions."""
    base = next(case for case in SCENARIOS if case.name == "Base")
    low, high = 1.0, 20_000.0
    for _ in range(100):
        midpoint = (low + high) / 2.0
        cash_flows = []
        value = midpoint
        for growth in base.growth:
            value *= 1.0 + growth
            cash_flows.append(value)
        industrial_ev, _, _ = enterprise_value(
            cash_flows, wacc=base.wacc, terminal_growth=base.terminal_growth
        )
        price = equity_bridge(
            industrial_ev,
            ford_credit_multiple=base.ford_credit_equity_multiple,
        )["value_per_share"]
        if price < target_price:
            low = midpoint
        else:
            high = midpoint
    return high


def validate(results: list[dict[str, object]]) -> None:
    values = [result["bridge"]["value_per_share"] for result in results]
    if values != sorted(values):
        raise ValueError("Scenario ordering failure: low <= base <= high did not hold")
    if value_for_rates(0.09, 0.025) <= value_for_rates(0.11, 0.025):
        raise ValueError("DCF monotonicity failure: lower WACC did not raise value")
    if value_for_rates(0.10, 0.03) <= value_for_rates(0.10, 0.02):
        raise ValueError("DCF monotonicity failure: higher terminal growth did not raise value")
    for result in results:
        bridge = result["bridge"]
        recomputed = (
            bridge["industrial_ev"]
            + bridge["excess_company_cash"]
            - bridge["company_debt"]
            + bridge["ford_credit_equity"]
            - bridge["pension_and_opeb_deficit"]
            - bridge["noncontrolling_interest"]
        )
        if abs(recomputed - bridge["common_equity"]) > 1e-6:
            raise ValueError("Enterprise-to-equity bridge does not reconcile")


def print_results(results: list[dict[str, object]]) -> None:
    print("PROJECT 1 - FORD INDUSTRIAL FCFF + FORD CREDIT EQUITY BRIDGE")
    print("USD millions except per-share values")
    print(
        f"{'Case':<8}{'2026 FCFF':>12}{'2030 FCFF':>12}{'WACC':>9}"
        f"{'Term g':>9}{'Industrial EV':>16}{'FC equity':>13}"
        f"{'Value/share':>14}{'TV/EV':>9}"
    )
    print("-" * 102)
    for result in results:
        case = result["case"]
        bridge = result["bridge"]
        print(
            f"{case.name:<8}{result['fcff'][0]:>12,.1f}{result['fcff'][-1]:>12,.1f}"
            f"{case.wacc:>8.1%}{case.terminal_growth:>9.1%}"
            f"{bridge['industrial_ev']:>16,.1f}{bridge['ford_credit_equity']:>13,.1f}"
            f"{bridge['value_per_share']:>14.2f}{result['terminal_share']:>9.1%}"
        )

    base = next(result for result in results if result["case"].name == "Base")
    bridge = base["bridge"]
    print("\nBASE ENTERPRISE-TO-EQUITY BRIDGE")
    print(f"Industrial enterprise value       ${bridge['industrial_ev']:>12,.1f}")
    print(f"Add: excess Company cash          ${bridge['excess_company_cash']:>12,.1f}")
    print(f"Less: Company debt                ${bridge['company_debt']:>12,.1f}")
    print(f"Add: Ford Credit equity value     ${bridge['ford_credit_equity']:>12,.1f}")
    print(f"Less: pension and OPEB deficit    ${bridge['pension_and_opeb_deficit']:>12,.1f}")
    print(f"Less: noncontrolling interest     ${bridge['noncontrolling_interest']:>12,.1f}")
    print(f"Common equity value               ${bridge['common_equity']:>12,.1f}")
    print(f"Diluted shares                    {SHARES:>13,.1f}")
    print(f"Value per share                   ${bridge['value_per_share']:>12.2f}")

    print("\nBASE WACC / TERMINAL-GROWTH SENSITIVITY ($/share)")
    growth_rates = (0.02, 0.025, 0.03)
    print("WACC \\ g" + "".join(f"{growth:>12.1%}" for growth in growth_rates))
    for wacc in (0.09, 0.10, 0.11):
        print(
            f"{wacc:>8.1%}"
            + "".join(
                f"{value_for_rates(wacc, growth):>12.2f}"
                for growth in growth_rates
            )
        )

    implied = implied_starting_fcff(SAVED_MARKET_PRICE)
    print("\nREVERSE DCF")
    print(f"Saved market price: ${SAVED_MARKET_PRICE:.2f}")
    print(f"Base converted 2026 industrial FCFF: ${base['fcff'][0]:,.1f} million")
    print(f"Market-implied 2026 industrial FCFF: ${implied:,.1f} million")
    print("Held fixed: base growth path, WACC, terminal growth, and bridge inputs.")

    print("\nVALIDATION")
    print("PASS - low/base/high ordering")
    print("PASS - WACC and terminal-growth monotonicity")
    print("PASS - enterprise-to-equity bridge reconciliation")
    print("PASS - Ford Credit debt excluded from the industrial bridge")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run Ford industrial FCFF cases and the Ford Credit bridge."
    )
    parser.add_argument(
        "--break-bridge",
        action="store_true",
        help="deliberately attempt to subtract Ford Credit debt",
    )
    args = parser.parse_args()
    if args.break_bridge:
        equity_bridge(
            75_000.0,
            ford_credit_multiple=1.0,
            subtract_ford_credit_debt=True,
        )
    results = [evaluate(case) for case in SCENARIOS]
    validate(results)
    print_results(results)


if __name__ == "__main__":
    main()
