"""Five-year FCFF discounted-cash-flow model (USD millions)."""

import sys

# Editable inputs
# Ford Motor Company (F), USD millions, FY2025 base year.
# Starting FCFF is Ford's disclosed Company adjusted free-cash-flow proxy,
# which excludes Ford Credit. See lab06_ford.md.
STARTING_FCFF = 3500.0
GROWTH_RATES = (0.05, 0.04, 0.03, 0.03, 0.03)
WACC = 0.10
TERMINAL_GROWTH = 0.03
NON_OPERATING_CASH = 28684.0
DEBT = 21919.0
DILUTED_SHARES = 3979.0

# Sensitivity and reverse-DCF controls
SENSITIVITY_WACCS = (0.09, 0.10, 0.11)
SENSITIVITY_TERMINAL_GROWTHS = (0.02, 0.03, 0.04)
TARGET_SHARE_PRICE = 13.90
REVERSE_SHIFT_LOWER = -0.05
REVERSE_SHIFT_UPPER = 0.10


def value_per_diluted_share(wacc=WACC, terminal_growth=TERMINAL_GROWTH,
                            growth_rates=GROWTH_RATES):
    """Return DCF value per diluted share for one set of assumptions."""
    if terminal_growth >= wacc:
        raise ValueError("Terminal growth must be less than WACC.")

    fcff = STARTING_FCFF
    yearly_fcff = []
    for growth_rate in growth_rates:
        fcff *= 1 + growth_rate
        yearly_fcff.append(fcff)

    present_value_explicit_fcff = sum(
        cash_flow / (1 + wacc) ** year
        for year, cash_flow in enumerate(yearly_fcff, start=1)
    )
    terminal_value_year_5 = (
        yearly_fcff[-1] * (1 + terminal_growth) / (wacc - terminal_growth)
    )
    present_value_terminal_value = terminal_value_year_5 / (1 + wacc) ** 5
    enterprise_value = present_value_explicit_fcff + present_value_terminal_value
    equity_value = enterprise_value + NON_OPERATING_CASH - DEBT
    return equity_value / DILUTED_SHARES


def print_sensitivity_grid():
    """Print value per diluted share for each WACC/terminal-growth pair."""
    print("\nSensitivity grid: value per diluted share ($)")
    print("WACC \\ terminal growth", end="")
    for terminal_growth in SENSITIVITY_TERMINAL_GROWTHS:
        print(f" {terminal_growth:>9.1%}", end="")
    print()

    for wacc in SENSITIVITY_WACCS:
        print(f"{wacc:>21.1%}", end="")
        for terminal_growth in SENSITIVITY_TERMINAL_GROWTHS:
            if terminal_growth >= wacc:
                cell = "invalid"
            else:
                cell = f"{value_per_diluted_share(wacc, terminal_growth):.2f}"
            print(f" {cell:>9}", end="")
        print()


def print_reverse_dcf():
    """Solve by bisection for a uniform shift to all explicit growth rates."""
    if any(rate + REVERSE_SHIFT_LOWER <= -1 or rate + REVERSE_SHIFT_UPPER <= -1
           for rate in GROWTH_RATES):
        print("\nReverse DCF: no solution; the stated bracket makes an annual growth "
              "rate -100% or below.")
        return

    def difference(shift):
        shifted_rates = tuple(rate + shift for rate in GROWTH_RATES)
        return value_per_diluted_share(growth_rates=shifted_rates) - TARGET_SHARE_PRICE

    lower = REVERSE_SHIFT_LOWER
    upper = REVERSE_SHIFT_UPPER
    lower_difference = difference(lower)
    upper_difference = difference(upper)

    print("\nReverse DCF")
    print(f"Target share price: ${TARGET_SHARE_PRICE:.2f}")
    print("Solved input: uniform shift to all five explicit growth rates")
    print("Held fixed: starting FCFF, WACC, terminal growth, cash, debt, "
          "diluted shares, and the relative pattern of the five growth rates.")

    if lower_difference == 0:
        solution = lower
    elif upper_difference == 0:
        solution = upper
    elif lower_difference * upper_difference > 0:
        print("Result: no solution in the stated bracket.")
        return
    else:
        for _ in range(100):
            midpoint = (lower + upper) / 2
            midpoint_difference = difference(midpoint)
            if abs(midpoint_difference) < 0.000001:
                break
            if lower_difference * midpoint_difference < 0:
                upper = midpoint
            else:
                lower = midpoint
                lower_difference = midpoint_difference
        solution = midpoint

    print(f"Solved uniform growth shift: {solution:+.4%}")


def main():
    if len(GROWTH_RATES) != 5:
        raise ValueError("Provide exactly five yearly growth rates.")
    if TERMINAL_GROWTH >= WACC:
        sys.exit(
            "Terminal growth must be less than WACC; the Gordon-growth formula "
            "is not valid when terminal growth is greater than or equal to WACC."
        )
    if DILUTED_SHARES <= 0:
        raise ValueError("Diluted shares must be greater than zero.")

    fcff = STARTING_FCFF
    yearly_fcff = []
    for growth_rate in GROWTH_RATES:
        fcff *= 1 + growth_rate
        yearly_fcff.append(fcff)

    present_value_explicit_fcff = sum(
        cash_flow / (1 + WACC) ** year
        for year, cash_flow in enumerate(yearly_fcff, start=1)
    )
    terminal_value_year_5 = (
        yearly_fcff[-1] * (1 + TERMINAL_GROWTH) / (WACC - TERMINAL_GROWTH)
    )
    present_value_terminal_value = terminal_value_year_5 / (1 + WACC) ** 5
    enterprise_value = present_value_explicit_fcff + present_value_terminal_value
    equity_value = enterprise_value + NON_OPERATING_CASH - DEBT
    value_per_diluted_share = equity_value / DILUTED_SHARES
    terminal_value_share_of_enterprise_value = (
        present_value_terminal_value / enterprise_value
    )

    for year, cash_flow in enumerate(yearly_fcff, start=1):
        print(f"FCFF Year {year}: {cash_flow:.4f}")
    print(f"PV of explicit FCFF: {present_value_explicit_fcff:.4f}")
    print(f"Terminal value at Year 5: {terminal_value_year_5:.4f}")
    print(f"PV of terminal value: {present_value_terminal_value:.4f}")
    print(f"Enterprise value: {enterprise_value:.4f}")
    print(f"Equity value: {equity_value:.4f}")
    print(f"Value per diluted share: {value_per_diluted_share:.4f}")
    print(
        "PV of terminal value as share of enterprise value: "
        f"{terminal_value_share_of_enterprise_value:.4f}"
    )
    print_sensitivity_grid()
    print_reverse_dcf()


if __name__ == "__main__":
    main()
