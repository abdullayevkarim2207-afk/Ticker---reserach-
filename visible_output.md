# Project 2 — Visible Executed Output

> OpenAI Codex was used for code, testing, debugging, and documentation organization.
> The analysis and decision are mine; this is for education, not investment advice.

**Decision:** tightly bounded paper pilot; no client allocation yet

**Primary allocation evidence:** all-month 65% SGOV / 35% VT; last-36-month
85% SGOV / 15% VT; largest change 20-point allocation move.

**User:** Meridian Foundation Reserve investment committee

**Data:** 61 monthly adjusted-close observations, 2021-09-01 to 2026-09-01

**Objective:** estimated return at least 6.5%; SGOV + VGIT at least 3%

## Baselines and encoded mandate verdicts

| Portfolio | Estimated return | Volatility | Reserve | Verdict and failed rule |
|---|---:|---:|---:|---|
| Equal weight | 3.72% | 6.13% | 50% | **FAIL - return** |
| Inverse volatility | 3.37% | 1.31% | 91% | **FAIL - return** |
| 60% VT / 40% BND benchmark | 6.97% | 10.96% | 0% | **FAIL - reserve** |
| Constrained lowest risk | 6.58% | 5.29% | 65% | **PASS** |

These verdicts cover the encoded return, reserve, long-only, and fully-invested
rules. Issuer concentration, five-day liquidity, turnover, and the undefined
calendar-loss promise remain unestablished and block live use.

## Saved run and stresses

| Run | SGOV / VGIT / BND / VT | Estimated return | Estimated volatility | Reserve |
|---|---:|---:|---:|---:|
| All 60 monthly returns | 65 / 0 / 0 / 35 | 6.58% | 5.29% | 65% |
| Last 36 monthly returns | 85 / 0 / 0 / 15 | 6.81% | 1.79% | 85% |
| VT return estimate −1.00 point | 60 / 0 / 0 / 40 | 6.59% | 6.03% | 60% |
| Annual implementation cost 25 bps | 60 / 0 / 0 / 40 | 6.74% net | 6.03% | 60% |

**Constraint stress:** raising the reserve minimum from 3% to 70% produces no
feasible portfolio on the 5-point grid. The process stops; it does not relax
the constraint.

The all-month and last-36-month runs differ by 20 percentage points in SGOV
and VT. That exceeds the 10-point stability limit and rejects immediate
adoption. The one-point VT stress moves the mix by five points, so it passes
that narrow test but does not overturn the failed window test.

**Point-in-time monitoring signal:** DGS10 was 5.26% for the 2026-09-29
measurement in the 2026-09-30 vintage. That exceeds the student-defined 5.00%
high-rate-watch threshold and requires a stress rerun, not an automatic trade.

Reproduce this output with:

```bash
python3 project2_run.py
```
