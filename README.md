# Ford Motor Company Project 1 Readiness Repository

## Finance decision and intended user

This project supports a buy-side investment committee with no current Ford
Motor Company (`F`) position. The current provisional action is **watch/defer**
at the saved market price of **$12.86 per share on September 24, 2026**. This is
not yet a final Project 1 recommendation: the required FCFF perimeter and
enterprise-to-equity bridge must be resolved before the valuation range is
decision-ready.

## Visible result

See [`visible_output.md`](visible_output.md). It preserves the material inputs,
as-of dates, current results, model disagreement, and unresolved decision risk
without requiring execution.

## Setup and run

Python 3.11 or newer is recommended.

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -r requirements.txt
python3 dcf.py
python3 lab10_ford_proforma.py
python3 lab12_signed_fcfe_check.py
python3 project_audit.py project-submission-manifest-template.csv
```

Expected readiness results:

- `dcf.py` prints the five-year FCFF-proxy DCF, WACC/growth grid, and reverse DCF.
- `lab10_ford_proforma.py` prints linked statements and the originally submitted
  FCFE convention.
- `lab12_signed_fcfe_check.py` preserves the negative FY2026 FCFE and corrects
  the base FCFE value from $10.41 to approximately $10.00 per share.
- `project_audit.py` reports incomplete final-submission surfaces until the
  missing PDFs, videos, transcripts, and access confirmations exist.

To test the pro-forma's loud accounting failure:

```bash
python3 lab10_ford_proforma.py --break-check
```

The command should stop with an FY2028 balance-sheet-gap error.

## Repository map

- `Ford-research/`: source ledger and Ford research support.
- `dcf.py` and `lab06_ford.md`: preliminary Company-excluding-Ford-Credit
  FCFF-proxy DCF.
- `lab08_ford_pe.py`, `lab08_inputs.csv`, and `lab08_ford.md`: peer policy and
  multiple analysis.
- `lab10_ford_proforma.py` and `lab10_ford.md`: linked five-year consolidated
  pro-forma and original FCFE valuation.
- `lab11_ford_sensitivity.py` and `lab11_ford.md`: locked changed-input test and
  one-at-a-time sensitivity evidence.
- `lab12_signed_fcfe_check.py`: signed-FCFE correction and rerun.
- `visible_output.md`: frozen, human-readable readiness output.
- `docs/validation-and-ai-use.md`: working validation and AI-use record.
- `project-submission-manifest-template.csv`: working 12-row manifest.

## Data sources and point-in-time boundary

The historical model uses Ford's 2023, 2024, and 2025 Forms 10-K. The latest
operating reference presently cited is Ford's Q2 2026 Form 10-Q. The saved
comparison price is $12.86 at 9:55 a.m. EDT on September 24, 2026. Financial
statement amounts are USD millions unless identified otherwise.

## Financial conventions and assumptions

The preliminary DCF starts from Ford's $3.5 billion Company adjusted free cash
flow proxy, uses a 10% WACC and 3% terminal growth, adds $28.684 billion of
non-operating cash, subtracts $21.919 billion of Company debt, and divides by
3,979 million diluted shares. This is not a full GAAP FCFF reconciliation.

The linked pro-forma forecasts Ford Credit finance assets and Ford Credit debt
together and separates Company debt. It currently values FCFE at a 10% cost of
equity and 2% terminal growth. This FCFE result is supporting diagnostic
evidence; it does not replace Project 1's required FCFF/enterprise-value
architecture.

## Validation and changed-input tests

The linked statements balance in every forecast year. The deliberate
`--break-check` run is expected to refuse a $100 million FY2028 imbalance. The
September 29 locked changed-input test varies revenue growth and gross margin
one at a time. The later signed-FCFE audit corrects the original exclusion of
negative FY2026 FCFE.

## Known limitations, monitoring, and reversal triggers

- The FCFF starting cash flow is a non-GAAP proxy rather than a reconciled
  five-year FCFF forecast.
- Ford Credit's treatment in the required FCFF perimeter and bridge remains
  the most important unresolved finance convention.
- The 10% discount rates and normalized gross-margin path are judgmental.
- The preliminary FCFF and linked FCFE results use different perimeters and
  must not be averaged.
- Watch/defer should not become the final action until a consistent FCFF range
  is compared with the date-matched market price.
- Monitor consolidated gross margin, Ford Pro profitability, Model e losses,
  warranty costs, signed cash flow, and the Ford Credit asset/debt relationship.

This repository is course work and not investment advice.
