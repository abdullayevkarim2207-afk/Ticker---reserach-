---
name: buffett-10k
description: Analyze a public company as a Buffett-style business owner using five fiscal years of keyless SEC EDGAR 10-K facts. Use when a user asks for the Lab 18 Buffett screen, owner earnings, five-year ROE, or an own/watch/pass memo based only on filed numbers; do not use for price or valuation advice.
---

# Buffett 10-K

Keep the boundary strict: the bundled script retrieves and computes every number; the model only interprets the printed evidence.

## Run the evidence script

Ask for a ticker if none is supplied. SEC automated access requires a descriptive user agent containing the student's name and email. Read it from `SEC_USER_AGENT`; never save it in the repository.

From the repository root, run:

```bash
SEC_USER_AGENT="Student Name student@example.edu" \
python .codex/skills/buffett-10k/scripts/buffett_10k.py TICKER
```

The script must remain the sole source of numeric claims. It applies the course rules: 10-K only, one-year flow periods, latest filing wins, exact tag priority, five latest fiscal-year-end dates, honest gaps, and code-computed Buffett checks.

## Write the memo

After a successful run, write a short Markdown memo named `lab18_buffett_memo_TICKER.md` in the repository root.

- Choose exactly one verdict: **own the business**, **watch it**, or **pass**.
- Judge business quality, not price. Do not introduce stock prices, valuation, forecasts, per-share data, debt ratios, moat scores, or outside facts.
- Use only numbers printed by the script. Do not calculate, estimate, interpolate, or silently repair a missing value.
- Discuss the three code-computed checks and explain any `not found` or `not known` limitation.
- Distinguish evidence from judgment. The verdict is a Buffett-inspired learning exercise, not Buffett's actual view or investment advice.

Before finishing, import `audit_memo_numbers` from `scripts/buffett_10k.py` and verify the memo against the exact script output. Revise until the unprinted-number list is empty. If a requested judgment needs evidence the script did not print, state that it cannot be judged from this evidence.
