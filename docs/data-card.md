# Project 2 Data Card

## Frozen fund-price panel

| Field | Evidence |
|---|---|
| Decision use | Estimate monthly returns, annualized arithmetic returns, annualized covariance and volatility, portfolio weights, baseline verdicts, and stresses |
| Assets | SGOV, VGIT, BND, and VT |
| Measure | Monthly adjusted close in U.S. dollars |
| Period | 61 common month-end observations from 2021-09-01 through 2026-09-01, producing 60 monthly returns |
| Sources | Yahoo Finance history pages for [SGOV](https://finance.yahoo.com/quote/SGOV/history/), [VGIT](https://finance.yahoo.com/quote/VGIT/history/), [BND](https://finance.yahoo.com/quote/BND/history/), and [VT](https://finance.yahoo.com/quote/VT/history/) |
| Download date | 2026-10-22 |
| Stored evidence | `prices.csv`; frozen locally so the submitted result does not change after provider revisions |
| Transformation | Sort common dates oldest first; compute simple monthly return as current adjusted close divided by prior adjusted close minus one; annualize arithmetic mean by multiplying by 12; annualize sample covariance by multiplying by 12 |
| Exclusions | Incomplete October 2026 excluded; dates not shared by all four sleeves excluded; no silent imputation |
| Revision boundary | Adjusted closes may later change after corporate-action corrections. Any refresh is a new data version and requires the complete validation package to be rerun. |
| Licensing/privacy | Classroom reproducibility snapshot only; production use or redistribution needs a separate current licensing review. No credentials or personal data are stored. |
| Known limitations | Historical adjusted-close returns are not forecasts; the sample covers a limited set of regimes; fund-level weights do not establish every underlying issuer or liquidity rule. |

## Point-in-time DGS10 monitoring signal

| Field | Evidence |
|---|---|
| Decision use | Turn on a high-rate watch and require a stress rerun; never create an automatic trade |
| Series | DGS10, 10-year Treasury constant-maturity market yield, quoted on an investment basis |
| Source | Board of Governors of the Federal Reserve System via [FRED/ALFRED](https://fred.stlouisfed.org/series/DGS10) and the [H.15 release](https://www.federalreserve.gov/releases/h15/) |
| Units/frequency | Percent per year, not seasonally adjusted; daily business-day series |
| Measurement and vintage | 5.26% measured 2026-09-29 in the 2026-09-30 as-known vintage |
| Download date | 2026-10-29 |
| Stored evidence | `data/dgs10-point-in-time-signal.csv` |
| Release rule | Use an observation only after the applicable H.15 release; an earlier decision must use the prior available observation. |
| Transformation | Compare DGS10 with the student-defined 5.00% watch threshold. At or above the threshold, display `HIGH-RATE WATCH`. |
| Revision test | The 2026-09-30 ALFRED vintage and 2026-10-29 FRED file had zero changed values on their common dates; this tested result is not a promise of no future correction. |
| Exclusions/boundary | Observations published after the vintage date are later data, not revisions and not available to the earlier decision. The signal does not directly change weights. |
| Quarantine rule | Stop using the signal if its release timing cannot be matched to the decision timestamp, the release convention changes, or a new audit finds unexplained material revisions. |

The load-bearing driver-level lineage is in `data/input-ledger.csv`; the
supporting method records are `lab15_portfolio_stability.md` and
`lab17_point_in_time_audit.md`.
