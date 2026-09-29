"""Five-year Asbury Automotive Group (ABG) pro forma and FCFE valuation.

This project is for a FIN 439 lab assignment and is for educational purposes
only. I am not a professional financial analyst, and this is not financial
advice. All amounts are USD millions except per-share values.
"""


YEARS = range(2026, 2031)

# Forecast assumptions
ORGANIC_REVENUE_GROWTH = 0.018
GROSS_MARGIN = 0.1705
SGA_TO_GROSS_PROFIT = {
    2026: 0.665,
    2027: 0.655,
    2028: 0.645,
    2029: 0.645,
    2030: 0.645,
}
DEPRECIATION_TO_OPENING_PPE = 82.4 / 3_070.4
IMPAIRMENT = 120.0
CAPITAL_SPENDING = 250.0
TAX_RATE = 0.255
INVENTORY_DAYS = 2_135.8 / (17_999.0 - 3_071.7) * 365
FLOOR_PLAN_TO_INVENTORY = 2_027.0 / 2_135.8
OTHER_WORKING_CAPITAL_TO_REVENUE_CHANGE = 0.008
MINIMUM_CASH = 25.0
REVOLVER_LIMIT = 850.0
REVOLVER_RATE = 0.06
DEBT_REPAYMENT = 150.0
SHARE_BUYBACK = 150.0
FLOOR_PLAN_RATE = 0.0467
TERM_DEBT_RATE = 0.0544
COST_OF_EQUITY = 0.10
TERMINAL_GROWTH = 0.025
SHARES_OUTSTANDING = 17.951349

# FY2025 opening balance sheet
OPENING = {
    "revenue": 17_999.0,
    "inventory": 2_135.8,
    "ppe": 3_070.4,
    "other_assets": 6_371.6,
    "cash": 40.4,
    "floor_plan": 2_027.0,
    "debt": 3_572.0,
    "revolver": 0.0,
    "other_liabilities": 2_127.5,
    "equity": 3_891.7,
}


def build_projection():
    """Return forecast rows in calculation order."""
    forecasts = []
    opening = OPENING.copy()

    for year in YEARS:
        revenue = opening["revenue"] * (1 + ORGANIC_REVENUE_GROWTH)
        gross_profit = revenue * GROSS_MARGIN
        cost_of_sales = revenue - gross_profit
        sga = gross_profit * SGA_TO_GROSS_PROFIT[year]
        depreciation = opening["ppe"] * DEPRECIATION_TO_OPENING_PPE
        impairment = IMPAIRMENT
        operating_income = gross_profit - sga - depreciation - impairment
        interest = (
            opening["floor_plan"] * FLOOR_PLAN_RATE
            + opening["debt"] * TERM_DEBT_RATE
            + opening["revolver"] * REVOLVER_RATE
        )
        pretax_income = operating_income - interest
        tax = max(0.0, pretax_income) * TAX_RATE
        net_income = pretax_income - tax

        inventory = cost_of_sales * INVENTORY_DAYS / 365
        floor_plan = inventory * FLOOR_PLAN_TO_INVENTORY
        ppe = opening["ppe"] + CAPITAL_SPENDING - depreciation
        revenue_change = revenue - opening["revenue"]
        other_working_capital = (
            OTHER_WORKING_CAPITAL_TO_REVENUE_CHANGE * revenue_change
        )
        other_assets = opening["other_assets"] + other_working_capital - impairment
        debt = opening["debt"] - DEBT_REPAYMENT
        other_liabilities = opening["other_liabilities"]
        equity = opening["equity"] + net_income - SHARE_BUYBACK

        inventory_change = inventory - opening["inventory"]
        floor_plan_change = floor_plan - opening["floor_plan"]
        fcfe = (
            net_income
            + depreciation
            + impairment
            - CAPITAL_SPENDING
            - inventory_change
            - other_working_capital
            + floor_plan_change
            - DEBT_REPAYMENT
        )

        cash_before_revolver = opening["cash"] + fcfe - SHARE_BUYBACK
        revolver = opening["revolver"]
        if cash_before_revolver < MINIMUM_CASH:
            revolver_draw = MINIMUM_CASH - cash_before_revolver
            if revolver + revolver_draw > REVOLVER_LIMIT:
                raise ValueError(f"FY{year}E exceeds the revolver limit")
            revolver += revolver_draw
            cash = MINIMUM_CASH
        else:
            revolver_repayment = min(
                opening["revolver"], cash_before_revolver - MINIMUM_CASH
            )
            revolver -= revolver_repayment
            cash = cash_before_revolver - revolver_repayment

        assets = cash + inventory + ppe + other_assets
        liabilities_and_equity = (
            floor_plan + debt + revolver + other_liabilities + equity
        )
        balance_gap = assets - liabilities_and_equity

        row = {
            "year": year,
            "revenue": revenue,
            "gross_profit": gross_profit,
            "cost_of_sales": cost_of_sales,
            "sga": sga,
            "depreciation": depreciation,
            "impairment": impairment,
            "operating_income": operating_income,
            "interest": interest,
            "pretax_income": pretax_income,
            "tax": tax,
            "net_income": net_income,
            "cash": cash,
            "inventory": inventory,
            "ppe": ppe,
            "other_assets": other_assets,
            "total_assets": assets,
            "floor_plan": floor_plan,
            "debt": debt,
            "revolver": revolver,
            "other_liabilities": other_liabilities,
            "equity": equity,
            "total_liabilities_and_equity": liabilities_and_equity,
            "capital_spending": CAPITAL_SPENDING,
            "inventory_change": inventory_change,
            "other_working_capital": other_working_capital,
            "floor_plan_change": floor_plan_change,
            "debt_repayment": DEBT_REPAYMENT,
            "share_buyback": SHARE_BUYBACK,
            "fcfe": fcfe,
            "balance_gap": balance_gap,
        }
        forecasts.append(row)
        opening = row

    return forecasts


def assert_balanced(forecasts):
    """Refuse a forecast whose balance sheet or minimum-cash check fails."""
    for row in forecasts:
        # Recompute the gap here so a changed cash line cannot leave a stale check.
        assets = row["cash"] + row["inventory"] + row["ppe"] + row["other_assets"]
        liabilities_and_equity = (
            row["floor_plan"]
            + row["debt"]
            + row["revolver"]
            + row["other_liabilities"]
            + row["equity"]
        )
        gap = assets - liabilities_and_equity
        if abs(gap) >= 0.05:
            raise ValueError(f"FY{row['year']}E balance-sheet gap: {gap:.1f}")
        if row["cash"] + 0.05 < MINIMUM_CASH:
            raise ValueError(
                f"FY{row['year']}E cash {row['cash']:.1f} is below "
                f"the {MINIMUM_CASH:.1f} minimum"
            )


def print_table(title, lines, forecasts):
    """Print one statement with forecast years in columns."""
    width = max(len(label) for label, _ in lines)
    print(f"\n{title}")
    print(f"{'USD millions':<{width}}" + "".join(f"FY{y}E".rjust(12) for y in YEARS))
    print("-" * (width + 12 * len(forecasts)))
    for label, key in lines:
        values = "".join(f"{row[key]:12,.1f}" for row in forecasts)
        print(f"{label:<{width}}{values}")


def print_statements(forecasts):
    print_table(
        "INCOME STATEMENT",
        [
            ("Revenue", "revenue"),
            ("Gross profit", "gross_profit"),
            ("SG&A", "sga"),
            ("Depreciation", "depreciation"),
            ("Impairment", "impairment"),
            ("Operating income", "operating_income"),
            ("Interest expense", "interest"),
            ("Pretax income", "pretax_income"),
            ("Tax", "tax"),
            ("Net income", "net_income"),
        ],
        forecasts,
    )
    print_table(
        "BALANCE SHEET",
        [
            ("Cash", "cash"),
            ("Inventory", "inventory"),
            ("PP&E", "ppe"),
            ("Other assets", "other_assets"),
            ("Total assets", "total_assets"),
            ("Floor plan", "floor_plan"),
            ("Term debt", "debt"),
            ("Revolver", "revolver"),
            ("Other liabilities", "other_liabilities"),
            ("Equity", "equity"),
            ("Total liabilities & equity", "total_liabilities_and_equity"),
        ],
        forecasts,
    )
    print_table(
        "CASH FLOW STATEMENT",
        [
            ("Net income", "net_income"),
            ("Depreciation", "depreciation"),
            ("Impairment", "impairment"),
            ("Capital spending", "capital_spending"),
            ("Change in inventory", "inventory_change"),
            ("Change in other working capital", "other_working_capital"),
            ("Change in floor plan", "floor_plan_change"),
            ("Debt repayment", "debt_repayment"),
            ("Free cash flow to equity", "fcfe"),
            ("Share buyback", "share_buyback"),
        ],
        forecasts,
    )


def print_checks(forecasts):
    print("\nCHECKS")
    print(f"{'':28}" + "".join(f"FY{y}E".rjust(12) for y in YEARS))
    gaps = "".join(f"{row['balance_gap']:12.1f}" for row in forecasts)
    cash_checks = "".join(
        f"{('PASS' if row['cash'] >= MINIMUM_CASH else 'FAIL'):>12}"
        for row in forecasts
    )
    print(f"{'Assets - liabilities - equity':28}{gaps}")
    print(f"{'Cash at/above minimum':28}{cash_checks}")


def print_valuation(forecasts):
    present_value_fcfe = sum(
        row["fcfe"] / (1 + COST_OF_EQUITY) ** index
        for index, row in enumerate(forecasts, start=1)
    )
    normalized_2030_fcfe = forecasts[-1]["fcfe"] + DEBT_REPAYMENT
    terminal_value_2030 = (
        normalized_2030_fcfe
        * (1 + TERMINAL_GROWTH)
        / (COST_OF_EQUITY - TERMINAL_GROWTH)
    )
    present_value_terminal = terminal_value_2030 / (1 + COST_OF_EQUITY) ** 5
    equity_value = present_value_fcfe + present_value_terminal
    share_after_2030 = present_value_terminal / equity_value
    value_per_share = equity_value / SHARES_OUTSTANDING

    print("\nVALUATION")
    print(f"Equity value: ${equity_value:,.2f} million")
    print(f"Share of value after 2030: {share_after_2030:.1%}")
    print(f"Value per share: ${value_per_share:,.2f}")


def main():
    forecasts = build_projection()
    print_statements(forecasts)
    print_checks(forecasts)
    assert_balanced(forecasts)
    print_valuation(forecasts)


if __name__ == "__main__":
    main()
