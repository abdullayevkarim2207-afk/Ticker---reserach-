# Lab 14 — Portfolio Baselines

## Decision question

**What does each simple portfolio earn and risk — and does any of them meet the
Meridian mandate?**

The reusable standard-library risk engine is in [`portfolio.py`](portfolio.py).
Run it from the repository root:

```bash
python portfolio.py
```

## Known-answer proof

All results are computed from the editable sleeve and correlation inputs. No
portfolio result is typed into the engine.

| Portfolio | Weights: bills / 10-year / IG / equity | Return | Volatility | Reserve-eligible | Meets 6.5%? |
|---|---|---:|---:|---:|---|
| Benchmark | 0.0 / 0.0 / 40.0 / 60.0 | 6.80% | 10.46% | 0.0% | yes |
| Equal weight | 25.0 / 25.0 / 25.0 / 25.0 | 5.20% | 5.21% | 50.0% | no |
| Inverse volatility | 84.3 / 6.0 / 7.0 / 2.6 | 3.77% | 1.05% | 90.3% | no |

The benchmark is the only baseline that meets the 6.5% expected-return
objective. It has no reserve-eligible allocation, however, so meeting the
return objective is not the same as satisfying the full mandate.

## Changed-input and refusal proofs

Changing both IG–equity correlation cells from `0.25` to `0.50` raises the
computed benchmark volatility from 10.46% to **11.00%**. The automated test
does this on a copy of the inputs, so the original table remains at `0.25`.

Changing the IG-to-equity correlation to `1.30` causes the validator to raise:

```text
ValueError: Correlation for Investment-grade bond fund and Global equity index fund must be between -1 and 1; received 1.3.
```

The tests also prove that a table with two unequal mirror cells is refused.
Run all checks with:

```bash
python -m unittest discover -s tests -v
```

## Partner swap proof

The partner's `portfolio.py` reproduced the same required values for all three
portfolios. On a temporary copy, changing the IG-to-equity correlation from
`0.25` to `1.30` produced this refusal before any portfolio was calculated:

```text
Input error: Correlation for Investment-grade bond fund / Global equity index fund is 1.3; it must be between -1 and 1.
```

The partner's original code was not changed.

## How portfolio volatility is computed

`build_covariance_matrix` converts every correlation into a covariance:

```text
covariance(i, j) = correlation(i, j) × volatility(i) × volatility(j)
```

`portfolio_variance` then evaluates every row-and-column pair:

```text
variance = sum(weight(i) × weight(j) × covariance(i, j))
```

Finally, `portfolio_volatility` takes the square root. Including the
off-diagonal terms is essential: they capture how the sleeves move together.
Leaving them out incorrectly produces a 9.90% benchmark volatility.

## Benchmark calculation by hand

With a 40% IG weight, 60% equity weight, 6% IG volatility, 16% equity
volatility, and 0.25 correlation:

```text
variance
= (0.40² × 0.06²)
  + (0.60² × 0.16²)
  + (2 × 0.40 × 0.60 × 0.25 × 0.06 × 0.16)
= 0.000576 + 0.009216 + 0.001152
= 0.010944

volatility = sqrt(0.010944) = 0.1046 = 10.46%
```

Two risky assets can be less risky together because a correlation below +1
means their movements do not line up perfectly. When one sleeve moves down,
the other may fall less, remain stable, or rise. The covariance terms therefore
add less risk than they would under perfect positive correlation.

## Mandate result

The benchmark was added to [`mandate.py`](mandate.py) as candidate E. It sums
to 100%, is long-only, is fully redeemable within five days, and has no
single-company concentration. It nevertheless fails the reserve rule:

```text
Candidate E
  Reserve >= 3.0%: 0.0% FAIL
  Verdict: fails 1 rule(s)
```

The client's own benchmark therefore breaks the client's stated mandate.

## Reflection

Inverse volatility piles into Treasury bills because their 0.5% volatility has
an inverse of 200, far larger than the inverse volatilities of the other
sleeves. The method treats low measured volatility as a reason for a larger
weight without considering whether the resulting expected return can meet the
objective. Its 84.3% bill allocation produces only a 3.77% expected return.

I would show the CIO the benchmark first. It is the only baseline that reaches
the return objective and it is the client's stated comparison portfolio, so it
provides the clearest starting point. I would immediately pair that result with
its 0.0% reserve allocation to expose the conflict between the benchmark and
the hard reserve rule; showing it first is a diagnostic choice, not a
recommendation to approve it.

## Before-Thursday fund universe

| Ticker | Fund | Mandate role | Price-history source |
|---|---|---|---|
| BIL | State Street SPDR Bloomberg 1–3 Month T-Bill ETF | Cash and reserve | [Yahoo Finance](https://finance.yahoo.com/quote/BIL/history/), monthly Adj Close |
| IEF | iShares 7–10 Year Treasury Bond ETF | Government bonds | [Yahoo Finance](https://finance.yahoo.com/quote/IEF/history/), monthly Adj Close |
| LQD | iShares iBoxx $ Investment Grade Corporate Bond ETF | Fixed income | [Yahoo Finance](https://finance.yahoo.com/quote/LQD/history/), monthly Adj Close |
| VT | Vanguard Total World Stock Index Fund ETF Shares | Equity | [Yahoo Finance](https://finance.yahoo.com/quote/VT/history/), monthly Adj Close |

These funds are a practice universe, not investment recommendations. The
monthly adjusted-close observations are saved oldest-first in
[`prices.csv`](prices.csv), with one shared date column and one column per
ticker. The file contains 61 monthly observations from **2021-10-01 through
2026-10-01**, downloaded from Yahoo Finance on **2026-10-20**. The extra
intramonth observation dated 2026-10-20 returned by the API was excluded so
the file contains one observation per month.

## AI-use note

AI assisted with implementing and testing the risk engine and drafting this
record. The submitted numerical conclusions are tied to executable code and
automated known-answer, changed-input, and invalid-input checks.
