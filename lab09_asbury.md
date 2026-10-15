# Lab 09 — Asbury Pro-Forma Build

This submission answers the course question: **What are five years of a
company's statements worth, built from assumptions I can defend, and how do I
know the statements are right?** It applies the common Lab 09 assumption set to
Asbury Automotive Group (`ABG`). All financial-statement amounts are USD
millions except per-share values.

## Model and assumption set

The required standard-library model is [`proforma.py`](proforma.py). It begins
with the supplied FY2025 opening balance sheet and projects FY2026E through
FY2030E in the required order: income statement, non-cash balance-sheet lines,
FCFE, and cash last.

| Assumption | Value | Label |
|---|---:|---|
| Organic revenue growth | 1.8% annually | Judgment |
| Gross margin | 17.05% | Judgment |
| SG&A / gross profit, 2026–2030 | 66.5%, 65.5%, 64.5%, 64.5%, 64.5% | Judgment |
| Depreciation / opening PP&E | 82.4 / 3,070.4 | History |
| Non-cash impairment | $120 annually | Judgment |
| Capital spending | $250 annually | Guidance |
| Tax rate | 25.5% | Judgment |
| Inventory days | 2,135.8 / (17,999.0 − 3,071.7) × 365 | History |
| Floor plan / inventory | 2,027.0 / 2,135.8 | History |
| Other working capital | 0.8% of change in revenue | Judgment |
| Minimum cash / revolver limit / revolver rate | $25 / $850 / 6% | History / judgment / judgment |
| Debt repayment / share buyback | $150 / $150 annually | Judgment |
| Floor-plan / term-debt interest rate | 4.67% / 5.44% | History |
| Cost of equity / terminal growth | 10% / 2.5% | Judgment |
| Shares outstanding | 17.951349 million | Fact |

The course supplied the assumptions and opening balances in the
[official Lab 09 instructions](https://github.com/CinderZhang/FIN43900-Fall2026/blob/main/lessons/week-05/lab-09-proforma-build.md).

## Known-answer proof

Run:

```bash
python3 proforma.py
```

The completed model reproduces the course checkpoints:

| Line | FY2026E | FY2030E |
|---|---:|---:|
| Revenue | 18,323.0 | 19,678.3 |
| Operating income | 844.2 | 971.4 |
| Net income | 413.6 | 527.5 |
| Free cash flow to equity | 211.4 | 342.3 |
| Cash, year end | 101.8 | 719.8 |
| Assets − liabilities − equity | 0.0 | 0.0 |

The resulting equity value is **$5,237.34 million**, the share of value after
2030 is **79.8%**, and the value per share is **$291.75**.

## Validation and deliberate failure

All five projected balance sheets balance to one decimal, and every year ends
at or above the $25 minimum cash balance. The valuation runs only after
`assert_balanced` accepts the statements.

I also replaced FY2026 computed cash of $101.8 with opening cash of $40.4 in a
temporary test copy. The model refused to proceed with:

```text
FY2026E balance-sheet gap: -61.4
```

This is the required loud failure. The $61.4 difference is FY2026 FCFE of
$211.4 less the $150.0 share buyback. It shows that holding cash at its opening
balance breaks the link between the cash-flow statement and balance sheet.

## Reflection

Cash is computed last because it is the result of the operating forecast,
investment, financing changes, and shareholder distributions. Typing cash as
an independent assumption would hide an inconsistency instead of exposing it.
The −$61.4 gap identifies both the size and direction of the omitted cash
movement before any individual model line needs to be inspected.

The floor-plan line represents inventory financing. It rises with inventory,
creates interest expense based on its opening balance, and enters FCFE through
the change in floor-plan borrowing. Removing it would keep the inventory cash
outflow while discarding its matched financing source, materially understating
cash.

## AI-use note

AI was used to compare the existing model with the published Lab 09
requirements, run the known-answer and deliberate-failure checks, and organize
this report. The numerical assumptions come from the course prompt, and the
model outputs were verified by executing the Python file.
