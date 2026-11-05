# Lab 19 — Legend Panel

## Decision question

**When three investors' skills read the same 10-K facts, where do they agree, where do they split — and would you trust the panel?**

They agree when the same filed evidence clears each investor's coded rule, but they split because each investor asks a different question of that evidence. I would trust the panel only as a reproducible first-pass screen, with every failure and evidence gap investigated before an investment decision.

## Build request

> Keep the Lab 18 SEC evidence rules and app, add `Liabilities`, `AssetsCurrent`, and `LiabilitiesCurrent`, and calculate current ratio as current assets divided by current liabilities. Add repo-scoped Graham and Burry skills with the course checks in code. Show investor-by-check results, three verdicts, three side-by-side memos, and one unprinted-number audit across all memos. Preserve every `not found` and `not known` value.

## Files and run commands

- App entry point: [`lab19_legend_panel.py`](lab19_legend_panel.py)
- Extended app: [`lab18_buffett_app.py`](lab18_buffett_app.py)
- Shared SEC calculation code: [`.codex/skills/buffett-10k/scripts/buffett_10k.py`](.codex/skills/buffett-10k/scripts/buffett_10k.py)
- Graham skill: [`.codex/skills/graham-10k/SKILL.md`](.codex/skills/graham-10k/SKILL.md)
- Burry skill: [`.codex/skills/burry-10k/SKILL.md`](.codex/skills/burry-10k/SKILL.md)
- Tests: [`tests/test_lab18_buffett.py`](tests/test_lab18_buffett.py)

The SEC identity belongs only in the terminal environment and is not saved in Git:

```bash
export SEC_USER_AGENT="Your Name your_school_email@example.edu"
python .codex/skills/buffett-10k/scripts/buffett_10k.py COST
python .codex/skills/graham-10k/scripts/graham_10k.py COST
python .codex/skills/burry-10k/scripts/burry_10k.py COST
python -m streamlit run lab19_legend_panel.py
```

## Known-answer validation — COST

All figures below were produced by the SEC script from 10-K company facts; none was typed into the app as an answer.

| Fiscal year end | 2022-08-28 | 2023-09-03 | 2024-09-01 | 2025-08-31 | 2026-08-30 |
|---|---:|---:|---:|---:|---:|
| Current ratio | 1.02 | 1.07 | 0.97 | 1.03 | 1.06 |
| Liabilities / equity | 2.11 | 1.75 | 1.96 | 1.64 | 1.49 |

| Investor | Check | COST |
|---|---|---|
| Buffett | ROE of 15% or more every year | pass |
| Buffett | Owner earnings positive every year | pass |
| Buffett | Owner earnings grew, first year to last | pass |
| Graham | Current ratio of 2 or more, latest year | **fail (1.06)** |
| Graham | Net income positive every year | pass |
| Graham | Net income grew, first year to last | pass |
| Burry | Operating cash flow at least net income every year | pass |
| Burry | Liabilities no more than twice equity, latest year | pass (1.49) |

The result matches the known answer: **Buffett 3 of 3, Graham 2 of 3, and Burry 2 of 2.**

### Threshold probe

At a temporary Graham threshold of 1.0, COST's latest current-ratio check changes from fail to pass. **I keep 2.0 because this defensive screen is intended to demand a substantial liquidity cushion; the probe demonstrates that a threshold is a design choice, not a fact about the company.**

## Project 2 company — NVIDIA

My Project 2 universe is SGOV, VGIT, BND, and VT. SGOV, VGIT, and BND are fixed-income funds, while VT holds operating companies; Vanguard listed **NVIDIA (NVDA) as VT's largest holding at 4.52%**, so NVDA is the company used here. NVIDIA files a Form 10-K, so no substitute company was needed.

| Investor | Check | NVDA |
|---|---|---|
| Buffett | ROE of 15% or more every year | pass |
| Buffett | Owner earnings positive every year | pass |
| Buffett | Owner earnings grew, first year to last | pass |
| Graham | Current ratio of 2 or more, latest year | pass (3.91) |
| Graham | Net income positive every year | pass |
| Graham | Net income grew, first year to last | pass |
| Burry | Operating cash flow at least net income every year | **fail** |
| Burry | Liabilities no more than twice equity, latest year | pass (0.31) |

The NVDA result is **Buffett 3 of 3, Graham 3 of 3, and Burry 1 of 2**. There are no missing required facts in this run. Burry splits from the other investors because operating cash flow is below net income in at least one displayed year; the code preserves that failure instead of explaining it away.

## Bull and bear

**Bull case:** Buffett passes all 3 checks, including positive and growing owner earnings, while Graham passes all 3 checks with a latest current ratio of 3.91. Burry also finds latest liabilities to equity of 0.31 within his limit, so profitability, liquidity, and balance-sheet leverage align positively.

**Bear case:** Burry's operating-cash-flow coverage check fails because cash flow does not reach net income in every displayed year. The panel does not explain the cash-versus-income divergence or test price, so the strong majority verdict could still conceal earnings-quality or valuation risk.

## Explain the code

`compute_graham_checks` starts the latest-ratio result as `not known`. It changes that result only when the latest current-ratio cell has status `ok`, then compares the value with the supplied threshold. The positive-income helper returns `not known` if any year is missing, and the growth check stays `not known` unless both the first and last net-income values exist. This is why a missing input is never silently changed to zero, a guess, or a pass.

## Decision

**Only with a condition: I would use the panel as a first-pass Project 2 screen only when every fail and `not known` result is investigated in the filing and no verdict is treated as a substitute for valuation.**

## A panel of AI agents — learn and reflect

A panel of AI agents is a set of specialized roles that examine a shared evidence set under different instructions or rules. Here, the data do not change between investors: the code selects one set of 10-K facts, and Buffett, Graham, and Burry apply different definitions of business quality, defensive strength, and accounting quality. Their disagreement comes from different checks and thresholds, not from giving each persona different facts.

On NVDA, all three agree that at least one part of the evidence is strong, and Buffett and Graham pass every check. The split is Burry's cash-coverage failure. The COST threshold probe shows that a screen's verdict combines company evidence with a human-designed cutoff; changing the cutoff can change the label even when the company facts are identical.

## Number-origin and honest-gap checks

Each memo is loaded separately in the app, but the app concatenates all three before calling the number auditor. Any numeric literal absent from the shared script output rejects the combined memo set. Missing reported values remain `not found`; any check that cannot be evaluated remains `not known`.

## Sources

- [Benjamin Graham expert page, FAskills](https://github.com/CinderZhang/FAskills/blob/main/financial-researcher/experts/ben_graham.md)
- [Michael Burry expert page, FAskills](https://github.com/CinderZhang/FAskills/blob/main/financial-researcher/experts/michael_burry.md)
- [SEC EDGAR APIs](https://www.sec.gov/search-filings/edgar-application-programming-interfaces)
- [Streamlit `st.columns`](https://docs.streamlit.io/develop/api-reference/layout/st.columns)
- [Vanguard VT portfolio and holdings](https://advisors.vanguard.com/investments/products/vt/vanguard-total-world-stock-etf)

This is a course screening exercise, not investment advice.
