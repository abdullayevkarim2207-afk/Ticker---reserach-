# Lab 18 — Legend Investor as a Skill

## Decision question

**Can an investor's philosophy become a skill my AI runs the same way every time—every number computed by code from the 10-K, with judgment left to the model?**

Yes, for the parts that can be stated as reproducible rules. The skill makes the source, tag priority, period selection, calculations, missing-data treatment, checks, and number audit repeatable. It leaves the meaning of the evidence and the own/watch/pass verdict to the model.

## My build request

> Create a repo-scoped Codex skill called `buffett-10k` and a Streamlit app for FIN 43900 Lab 18. Use keyless SEC EDGAR company facts and only 10-K data. For the latest five fiscal-year-end dates, have code select one-year flow facts, let the latest filing win, follow the required XBRL tag priorities, print every value with its tag, compute ROE, owner earnings, and all three Buffett checks, and preserve `not found` and `not known`. Then write a short own/watch/pass memo using only printed numbers. The app must chart owner earnings and net income, display the tagged table and checks, show the memo, and flag every memo number that the script did not print. Do not use price data or estimates.

## Files and commands

- Skill: [`.codex/skills/buffett-10k/SKILL.md`](.codex/skills/buffett-10k/SKILL.md)
- SEC and calculation script: [`.codex/skills/buffett-10k/scripts/buffett_10k.py`](.codex/skills/buffett-10k/scripts/buffett_10k.py)
- Streamlit app: [`lab18_buffett_app.py`](lab18_buffett_app.py)
- COST memo: [`lab18_buffett_memo_COST.md`](lab18_buffett_memo_COST.md)
- JPM gap memo: [`lab18_buffett_memo_JPM.md`](lab18_buffett_memo_JPM.md)
- Tests: [`tests/test_lab18_buffett.py`](tests/test_lab18_buffett.py)

The SEC requires a descriptive automated-access identity. To keep personal information out of Git, I enter it only in my terminal session:

```bash
export SEC_USER_AGENT="My Name my_school_email@example.edu"
python .codex/skills/buffett-10k/scripts/buffett_10k.py COST
python .codex/skills/buffett-10k/scripts/buffett_10k.py JPM
python -m streamlit run lab18_buffett_app.py
```

## Rules implemented in code

The script uses only facts whose form is `10-K`. A flow fact must span 300 through 430 days, which admits ordinary 52- and 53-week fiscal years while rejecting quarters and multi-year totals. Rows are labeled by fiscal-year-end date. For a repeated period and tag, the fact from the latest filing date wins.

Revenue first uses `RevenueFromContractWithCustomerExcludingAssessedTax`, then `Revenues`. Net income uses `NetIncomeLoss`; operating cash flow uses `NetCashProvidedByUsedInOperatingActivities`; capital spending first uses `PaymentsToAcquirePropertyPlantAndEquipment`, then `PaymentsToAcquireProductiveAssets`; and equity uses `StockholdersEquity` at year-end.

Code calculates ROE as net income divided by year-end equity and owner earnings as operating cash flow minus capital spending. It then calculates the three checks. A missing reported value is `not found`; ROE is `not known` if equity is zero or below; and a check with any missing required input is `not known`. Nothing is estimated.

## Known-answer validation — COST, USD millions

| Fiscal year end | Revenue | Net income | Operating cash flow | Capital spending | Equity | ROE | Owner earnings |
|---|---:|---:|---:|---:|---:|---:|---:|
| 2022-08-28 | 226,954 | 5,844 | 7,392 | 3,891 | 20,642 | 28.3% | 3,501 |
| 2023-09-03 | 242,290 | 6,292 | 11,068 | 4,323 | 25,058 | 25.1% | 6,745 |
| 2024-09-01 | 254,453 | 7,367 | 11,339 | 4,710 | 23,622 | 31.2% | 6,629 |
| 2025-08-31 | 275,235 | 8,099 | 13,335 | 5,498 | 29,164 | 27.8% | 7,837 |
| 2026-08-30 | 303,154 | 9,226 | 15,817 | 6,435 | 35,803 | 25.8% | 9,382 |

The code reports `pass` for ROE of 15% or more every year, `pass` for positive owner earnings every year, and `pass` for owner earnings growth from the first displayed year to the last.

## Probes

**JPM:** Neither permitted capital-spending tag appears in the company facts. The table prints `not found` for capital spending and owner earnings. Both owner-earnings checks print `not known`, and the saved JPM memo explicitly says it cannot judge owner earnings.

**Hand-typed number:** The number-audit function has a test that adds `40.0%` to the COST memo. It flags `40.0%` because that ROE was never printed by the script. The same probe can be repeated in the app's memo editor.

**Fresh chat without the skill:** A browser model can state five ROEs without exposing an exact filing, tag, period rule, or reproducible computation. Those numbers are assertions. This app's table is auditable because every input is tied to an XBRL tag and every derived number is produced by visible code.

## My explanation for my partner

### What can code compute, and what requires judgment?

Code can handle the numbers, such as revenue, ROE, owner earnings, and the three required checks. Judgment is still needed to decide whether the business should be owned, watched, or passed because these numbers do not explain everything about management, competition, or the company's future. The lab also does not include stock price, so it is not a complete investment decision.

### What does `analyze_companyfacts` do?

It processes the company's SEC facts for the last five fiscal years. It selects revenue, net income, operating cash flow, capital spending, and equity. It then calculates ROE and owner earnings and runs Buffett's three checks.

### What information is this based on?

It is based on financial information officially reported in SEC EDGAR 10-K filings. We use filed company facts instead of predictions, analyst estimates, or numbers generated by the AI.

### How does the program choose the right financial fact?

It searches for specific XBRL tags in the SEC data. For measures with two permitted tags, it tries the preferred tag first. If that tag is unavailable for the period, it tries the approved backup tag.

### What if the same period appears in several filings?

When the same period and financial fact appear in multiple 10-K filings, the program selects the version from the latest filing date. This follows the assignment's rule that the latest filing wins.

### Where does `not found` come from?

`Not found` appears when the program cannot find the required information under any of the approved XBRL tags. Instead of estimating the value or treating it as zero, the program reports that it was not found.

### Why is `not found` important?

It is important because we should not base a decision on invented or unsupported numbers. Knowing that evidence is missing is more honest than using an estimate that could change owner earnings, the checks, and the final verdict.

## Trust decision

I trust the COST verdict as a consistent, reproducible business-quality screen because all three checks trace to tagged 10-K facts and survive the known-answer test. I would not trust it as a complete investment decision because this lab intentionally excludes price and because five accounting series cannot prove moat durability, management quality, or future performance.

## Learn and reflect

A skill is a folder anchored by `SKILL.md`, optionally bundled with scripts and other resources. Codex initially sees only each skill's name and description so selection stays cheap; it reads the full instructions only when the request matches, and it runs the bundled script when deterministic work is needed.

The numbers belong in code because period selection, tag priority, arithmetic, and missing-data rules can be inspected and rerun. The model is useful for explaining what that fixed evidence may mean, but it must not become an undocumented calculator or data source.

The skill makes the same data rules and checks run every time. It leaves the final interpretation to the model, while the memo audit prevents that interpretation from smuggling in unprinted numbers. `Not found` is better than an estimate because it reveals the evidence boundary; an estimate could look precise, change the checks, and produce a confident verdict the filing does not support.

## Work I must do myself in class

1. Enter my own name and school email as `SEC_USER_AGENT`; it must not be committed.
2. Explain `analyze_companyfacts` and `_flow_metric` to my partner without AI, then listen to my partner's explanation.
3. Type `40.0%` into the running app and show the flag in the checkout attempt.

## Sources and AI-use disclosure

The build follows the [official Codex skill explanation](https://developers.openai.com/blog/eval-skills), the [FAskills README and Buffett page](https://github.com/CinderZhang/FAskills), the [SEC EDGAR company-facts API documentation](https://www.sec.gov/search-filings/edgar-application-programming-interfaces), the [SEC ticker-map documentation](https://www.sec.gov/search-filings/edgar-search-assistance/accessing-edgar-data), and the [Streamlit line-chart documentation](https://docs.streamlit.io/develop/api-reference/charts/st.line_chart). FAskills was read for the philosophy only; it was not installed and none of its paid data sources were used.

OpenAI Codex assisted with the skill, script, app, tests, memo structure, and validation record. All financial values are selected and computed by the bundled Python script from SEC EDGAR facts; the memos contain model judgment constrained to those printed values.
