# Ford Project 1 - Recording Screenboard

Use this file as the clean visual anchor while recording. The detailed evidence
remains in the linked project files.

## Video 1 - Research Evolution

### Decision question

- Target: Ford Motor Company (`F`)
- User: buy-side committee with no current position
- Horizon: three-year decision; five-year forecast
- Action: **WATCH/DEFER**

### How the work changed

| Stage | Initial evidence | Challenge | Final treatment |
|---|---|---|---|
| Preliminary DCF | $15.01 base | $3.5B cash flow was a non-GAAP proxy | Rejected as final valuation evidence |
| Ford Credit | Consolidated debt looked very high | Finance debt funds matched receivables and leases | Professor-approved SOTP perimeter |
| FCFE diagnostic | $10.41/share | Negative FY2026 FCFE was omitted | Corrected to about $10.00/share |
| Reported P/E | Positive peer multiples | Ford FY2025 EPS was negative | Refused as unusable |
| EV multiple | No enterprise-value cross-check | Captive-finance definitions had to match | GM implies about $13.78/share |

### Final evidence

| Low | Base | High | Market price | Action |
|---:|---:|---:|---:|---|
| $12.80 | $20.47 | $33.35 | $12.86 | **WATCH/DEFER** |

Decision rule: at least 15% base upside and no low-case downside.

## Video 2 - Code and Validation

### Commands

```bash
python3 project1_app.py
python3 lab10_ford_proforma.py
python3 lab10_ford_proforma.py --break-check
python3 lab12_signed_fcfe_check.py
python3 -m unittest discover -s tests -v
```

### Evidence to show

| Test | Required screen result |
|---|---|
| Base-year reconciliation | FY2025 assets and liabilities plus equity each equal $289.160B |
| Statement articulation | Five annual balance-sheet gaps equal zero |
| Cash tie | Cash recomputes from the cash-flow roll-forward |
| Loud failure | `ValueError: FY2028E balance-sheet gap: 100.0` |
| Signed cash flow | $10.41 original FCFE diagnostic becomes about $10.00 |
| Automated validation | Seven tests pass; final status `OK` |

The deliberate error is expected. Explain it immediately when it appears.

## Video 3 - Committee Defense

### Valuation and method disagreement

| Evidence | Result | Interpretation |
|---|---:|---|
| Low SOTP | $12.80 | Below market; downside fails protection rule |
| Base SOTP | $20.47 | 59.2% upside, but assumption-sensitive |
| High SOTP | $33.35 | Requires stronger sustained margin recovery |
| GM industrial multiple | $13.78 | More conservative current-earnings cross-check |
| Reverse DCF margin path | 1.46%-2.96% | Market-implied industrial EBIT margins |
| Base terminal value / EV | 79.0% | Long-duration assumption risk |

### Committee decision

**WATCH/DEFER** because the base clears the 15% hurdle but the low case is
below the $12.86 market price.

### Reversal and monitoring triggers

- Initiate if supported evidence lifts the low value above market while the
  base continues to clear the 15% rule.
- Do not initiate if the base falls below market or margin recovery fails.
- Monitor Ford Pro profitability, Model e losses, warranty costs, signed cash
  flow, and Ford Credit funding and credit quality.
