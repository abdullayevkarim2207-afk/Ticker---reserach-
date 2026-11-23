# Project 2 — Portfolio Stability Decision

> OpenAI Codex was used for code, testing, debugging, and documentation organization.
> The analysis and decision are mine; this is for education, not investment advice.

## Decision

**Recommendation: run a tightly bounded paper pilot; do not adopt the allocation
or commit client capital yet.** The model searches for the lowest-volatility
long-only portfolio that reaches a 6.5% expected-return threshold and holds at
least 3% in reserve-eligible assets. Using all 60 saved monthly returns produces
65% SGOV / 0% VGIT / 0% BND / 35% VT. Using only the last 36 months produces
85% / 0% / 0% / 15%. The 20-point change in SGOV and VT is larger than the
10-point stability limit and prevents adoption.

The intended user is the Meridian Foundation Reserve investment committee. The
model is a classroom decision system, not a return forecast.

## One-command reproduction

Python 3.11 or newer is recommended. Use a fresh destination name so this cold
run does not collide with an earlier clone.

On Windows PowerShell or Command Prompt:

```powershell
git clone https://github.com/abdullayevkarim2207-afk/Ticker---reserach-.git Ticker-research-cold-run
cd Ticker-research-cold-run
py project2_run.py
```

On macOS or Linux:

```bash
git clone https://github.com/abdullayevkarim2207-afk/Ticker---reserach-.git Ticker-research-cold-run
cd Ticker-research-cold-run
python3 project2_run.py
```

If Windows reports that `py` is not recognized, install Python 3.11 or newer
from [python.org](https://www.python.org/downloads/) with **Add Python to PATH**
enabled, reopen the terminal, and rerun `py project2_run.py`. Do not delete an
existing project folder merely to make the clone command work; use the fresh
destination name shown above.

The command uses only Python's standard library. It reads `prices.csv` and
prints the all-month result plus estimate, window, cost, and constraint
stresses, the explicit infeasibility stop, and the committee decision. The expected output is preserved in
[`visible_output.md`](visible_output.md).

Optional interface and checks:

```bash
python3 -m pip install -r requirements.txt
python3 -m streamlit run app.py
python3 -m unittest tests.test_portfolio tests.test_project2_run -v
python3 scripts/final_readiness.py
```

Optional PDF rebuild after the Markdown sources are final:

```bash
python3 -m pip install -r requirements-docs.txt
python3 scripts/create_project_pdfs.py
```

The PDF command always rebuilds the memo, validation record, and Research
Evolution PDF in both `output/pdf/` and their canonical `docs/` locations. If
an unchanged `docs/edition-a.pdf` exists, the builder places it before Edition
B. Because no preserved Edition A was available for this project, the current
Research Evolution PDF instead opens with an explicit missing-baseline
disclosure and does not recreate earlier work. Use
`--require-research-evolution` for a strict final freeze.

The app opens on the saved `prices.csv` inputs. Move the expected-return,
objective, reserve, cost, stability-limit, or historical-window control; compare the
equal-weight, inverse-volatility, 60/40, and constrained portfolios; then read
the mandate, scenario-stability, and committee verdicts. The data card and
risk/return map keep the source, method, and trade-offs visible on the page. A
frozen DGS10 point-in-time monitoring signal includes its source, vintage,
release rule, units, transformation, and decision use.

## Mandate and method

- Universe: SGOV, VGIT, BND, and VT.
- Horizon and maintenance: seven years with annual rebalancing.
- Benchmark: 60% VT / 40% BND.
- Objective: at least 6.5% estimated annual return.
- Hard constraints: long-only, fully invested, at least 3% combined SGOV and
  VGIT, and a 5-percentage-point allocation grid.
- Search: evaluate every feasible grid portfolio and keep the one with the
  lowest estimated volatility.
- Risk measure and limit: minimize annualized historical volatility; because
  the Lab 13 calendar-loss promise has no defined measure or breach rule, the
  enforceable decision limit is a maximum 10-percentage-point allocation move
  under a predeclared stress or window change.
- Costs: the saved baseline assumes zero incremental implementation drag; the
  app can deduct a user-selected annual basis-point cost from every gross
  return estimate, and the saved stress uses 25 basis points.
- Decision rule: do not adopt when a reasonable historical-window change or a
  one-point input stress moves any weight by more than 10 percentage points.

The return, volatility, and correlation inputs are arithmetic historical
estimates calculated from the saved monthly adjusted-close data. They are not
forecasts. The app's pass/fail verdicts cover only the encoded return, reserve,
long-only, and fully-invested rules. The broader IPS's 8% issuer limit, 90%
five-day-liquidity rule, 25% turnover cap, and undefined calendar-loss promise
cannot be established from sleeve weights alone; a failed or unavailable check
blocks live use.

## Repository map

- `project2_run.py`: single-command decision reproduction.
- `scripts/final_readiness.py`: mechanical freeze audit that separates code or
  document errors from unresolved student/video evidence.
- `portfolio.py`: return, covariance, mandate, exhaustive-search, and CSV logic.
- `app.py`: Project 2 Streamlit product.
- `prices.csv`: frozen monthly adjusted-close inputs.
- `data/input-ledger.csv`: single source-of-truth table for load-bearing inputs,
  definitions, sources, dates, transformations, exclusions, and decision use.
- `docs/data-card.md`: reviewer-facing cards for the frozen fund prices and
  point-in-time DGS10 monitoring signal.
- `tests/test_portfolio.py` and `tests/test_project2_run.py`: known-answer,
  invalid-input, changed-input, and stability checks.
- `lab13_meridian.md` through `lab19_legend_panel.md`: Lab 13–19 evidence.
- `visible_output.md`: human-readable executed output.
- `docs/decision-memo.md`: committee memo at the Lab 20 required path.
- `docs/decision-memo.pdf` and `docs/validation-and-ai-use.pdf`: canonical
  rendered submission PDFs; `output/pdf/` keeps build copies.
- `Research-Evolution.md`: working research-evolution brief.
- `docs/validation-and-ai-use.md`: working validation and AI-use record.
- `MUST_FIX.md`: frozen Week 12 completion list.
- `COLD_RUN_RECORD.md`: peer-completed README-only cold-run template.
- `VIDEO_SCREENBOARD.md`: distinct plans for Videos 1–3.
- `docs/student-final-steps.md`: the remaining student-only freeze, recording,
  transcript, and submission actions.
- `submission/`: separate plain-text checklists for the repository, exact
  submission package, each video's timing/screens/talking points, YouTube and
  transcript links, and final submission confirmation.
- `project-submission-manifest.csv`: canonical 12-row submission manifest;
  unresolved final links remain visibly marked.

Older Ford files remain as prior-course evidence and are not inputs to the
Project 2 result.

## Data boundary

`prices.csv` contains 61 complete month-end adjusted-close observations from
2021-09-01 through 2026-09-01, downloaded from Yahoo Finance on 2026-10-22.
The incomplete October 2026 month was excluded. The consolidated data card is
[`docs/data-card.md`](docs/data-card.md), with supporting detail in
`lab15_portfolio_stability.md` and `lab17_point_in_time_audit.md`. The frozen
point-in-time signal is DGS10 at
5.26% for the 2026-09-29 measurement in the 2026-09-30 as-known vintage. The
student-defined rule turns on a high-rate watch at 5.00%; it triggers review
and a stress rerun, not an automatic trade. Its full data card is in
`data/dgs10-point-in-time-signal.csv` and the Lab 17 audit.

The repository freezes these classroom inputs so a later provider revision
cannot silently change the submitted result. Adjusted closes can change after
corporate-action corrections, so any refresh must be treated as a new data
version and rerun through the full validation package. No credentials or
personal data are used. The included market-data snapshot is for educational
reproducibility; any production use or redistribution requires a separate
licensing review under the provider's then-current terms.

## Riskiest claim and rejection test

The riskiest claim is that a historical minimum-volatility mix meeting the
mandate is stable enough to guide a committee allocation. The direct test is to
change the estimation window from all 60 returns to the last 36. The resulting
20-point allocation change rejects that claim for current adoption. A separate
one-point reduction in VT's estimated return moves the all-month mix by five
points. A 25-basis-point annual cost drag also moves the mix by five points.
Both pass the 10-point limit but do not repair the failed window test. Raising
the reserve minimum from 3% to 70% produces no feasible grid portfolio and
stops the process rather than silently relaxing the mandate.

## Limitations and monitoring

- Historical means are noisy and are not prospective expected returns.
- The short sample includes one market regime and does not prove future risk.
- The 5-point grid can hide solutions between grid points.
- The saved cost stress is a uniform annual drag; it does not separately model
  fund fees, bid-ask spread, taxes, market impact, or turnover-dependent costs.
- Meeting the 6.5% input threshold does not establish that the realized return
  will reach CPI + 4% after costs.
- The monitoring owner is the portfolio analyst. During a paper pilot, rerun
  monthly and after any data-method change. Kill the pilot if a mandate rule
  fails, any data lineage check fails, or an estimate/cost/window update
  moves any weight by more than 10 points.

## AI disclosure

OpenAI Codex assisted with code, tests, documentation, and the Week 12 package.
The working record in `docs/validation-and-ai-use.md` identifies the outputs,
checks, dispositions, and remaining student-owned evidence. The student owns
the final recommendation and must verify every number before submission.
