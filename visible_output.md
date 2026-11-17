# Project 2 — Visible Executed Output

> Prepared with disclosed AI assistance. Education, not investment advice.

**Decision:** tightly bounded paper pilot; no client allocation yet

**User:** Meridian Foundation Reserve investment committee

**Data:** 61 monthly adjusted-close observations, 2021-09-01 to 2026-09-01

**Objective:** estimated return at least 6.5%; SGOV + VGIT at least 3%

| Run | SGOV / VGIT / BND / VT | Estimated return | Estimated volatility | Reserve |
|---|---:|---:|---:|---:|
| All 60 monthly returns | 65 / 0 / 0 / 35 | 6.58% | 5.29% | 65% |
| Last 36 monthly returns | 85 / 0 / 0 / 15 | 6.81% | 1.79% | 85% |
| VT return estimate −1.00 point | 60 / 0 / 0 / 40 | 6.59% | 6.03% | 60% |

The all-month and last-36-month runs differ by 20 percentage points in SGOV
and VT. That exceeds the 10-point stability limit and rejects immediate
adoption. The one-point VT stress moves the mix by five points, so it passes
that narrow test but does not overturn the failed window test.

Reproduce this output with:

```bash
python3 project2_run.py
```
