# Project 1 - Ford Industrial FCFF and Ford Credit Bridge

## Valuation perimeter

The final Project 1 architecture values Ford's Company-excluding-Ford-Credit
operations with FCFF and treats Ford Credit as a separately valued equity
asset. Ford Credit debt is not subtracted from industrial enterprise value.
Ford's 2025 Form 10-K states that Ford Credit is self-funding and reports
$141.4 billion of Ford Credit debt, $14.8 billion of Ford Credit equity, and
9.6x debt-to-equity leverage at December 31, 2025.

## Starting FCFF conversion

Ford's Q2 2026 Form 10-Q guidance reports Company adjusted free cash flow of
$6-$7 billion. That measure excludes Ford Credit operating cash flow but
includes Ford Credit distributions and is after Company interest. The model
therefore uses:

`Industrial FCFF = Company adjusted FCF - Ford Credit distribution + after-tax Company interest`

This is an explicit perimeter conversion, not a claim that the non-GAAP measure
is identical to GAAP FCFF. Low/base/high cases use $6.0/$6.5/$7.0 billion of
adjusted free cash flow, $2.0/$1.7/$1.5 billion of Ford Credit distributions,
and the same $1.249 billion Company interest reference at a 21% tax rate.

## Enterprise-to-equity bridge policy

- Add only Company cash above Ford's stated $20 billion operating-cash target.
- Subtract Company debt excluding Ford Credit.
- Add Ford Credit at 0.8x/1.0x/1.2x its reported $14.8 billion equity.
- Subtract the $0.2 billion pension deficit and $4.4 billion OPEB deficit.
- Subtract $28 million of noncontrolling interest.
- Divide by 3,979 million diluted shares.
- Do not subtract Ford Credit debt because Ford Credit enters as an equity
  value after its financing liabilities.

## Scenario design

| Case | 2026 adjusted FCF | Ford Credit distribution | FCFF growth after 2026 | WACC | Terminal growth | Ford Credit P/B proxy |
|---|---:|---:|---|---:|---:|---:|
| Low | $6.0B | $2.0B | 1%, 2%, 2%, 2% | 11% | 2.0% | 0.8x |
| Base | $6.5B | $1.7B | 3%, 3%, 3%, 2% | 10% | 2.5% | 1.0x |
| High | $7.0B | $1.5B | 5%, 4%, 3%, 3% | 9% | 3.0% | 1.2x |

The cases are causal bundles rather than probabilities. The low case combines
weaker cash conversion, slower growth, a higher discount rate, and a lower
Ford Credit equity multiple. The high case combines stronger cash conversion,
growth, financing value, and a lower discount rate. This breadth is deliberate
because the starting measure is non-GAAP and the terminal value is material.

## Run and validation

```bash
python3 project1_fcff.py
python3 project1_fcff.py --break-bridge
```

The normal run checks scenario ordering, WACC and terminal-growth direction,
and bridge reconciliation. The deliberate break must stop with a perimeter
error rather than subtracting Ford Credit debt twice.

## Decision rule

The saved comparison price is $12.86 on September 24, 2026. The student's
initiation threshold requires at least 15% upside, or $14.79 per share, after
the FCFF perimeter and Ford Credit bridge are supported. A low case at or below
the market price supports watch/defer rather than initiation even when the base
case exceeds the threshold.

## Primary sources and limitations

- Ford 2025 Form 10-K: Company cash and target, Company debt, Ford Credit debt
  and equity, pension/OPEB status, noncontrolling interest, and shares.
- Ford Q2 2026 Form 10-Q: adjusted EBIT and adjusted free-cash-flow guidance.
- `lab10_ford.md`: linked five-year pro-forma assumptions and source map.

The largest limitation is that the starting FCFF conversion uses management's
non-GAAP adjusted free-cash-flow guidance. Ford Credit's book-value multiple is
also a valuation convention, not an observed standalone market price. These
inputs require instructor review and sensitivity disclosure before the final
recommendation is frozen.
