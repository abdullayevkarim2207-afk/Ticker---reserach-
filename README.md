# Project 2 — Portfolio Stability Decision

> This repository and its outputs were prepared with disclosed AI assistance.
> It is an educational demonstration, not investment advice.

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

Python 3.11 or newer is recommended. Clone the repository, enter its folder,
and run:

```bash
python3 project2_run.py
```

The command uses only Python's standard library. It reads `prices.csv` and
prints the all-month result, the last-36-month result, the one-point VT stress,
and the committee decision. The expected output is preserved in
[`visible_output.md`](visible_output.md).

Optional interface and checks:

```bash
python3 -m pip install -r requirements.txt
python3 -m streamlit run app.py
python3 -m unittest tests.test_portfolio tests.test_project2_run -v
```

The app opens on the saved `prices.csv` inputs. Move the expected-return,
objective, reserve, or historical-window control and read the mandate,
stability, and committee verdicts below the two result panels.

## Mandate and method

- Universe: SGOV, VGIT, BND, and VT.
- Objective: at least 6.5% estimated annual return.
- Hard constraints: long-only, fully invested, at least 3% combined SGOV and
  VGIT, and a 5-percentage-point allocation grid.
- Search: evaluate every feasible grid portfolio and keep the one with the
  lowest estimated volatility.
- Decision rule: do not adopt when a reasonable historical-window change or a
  one-point input stress moves any weight by more than 10 percentage points.

The return, volatility, and correlation inputs are arithmetic historical
estimates calculated from the saved monthly adjusted-close data. They are not
forecasts.

## Repository map

- `project2_run.py`: single-command decision reproduction.
- `portfolio.py`: return, covariance, mandate, exhaustive-search, and CSV logic.
- `app.py`: Project 2 Streamlit product.
- `prices.csv`: frozen monthly adjusted-close inputs.
- `tests/test_portfolio.py` and `tests/test_project2_run.py`: known-answer,
  invalid-input, changed-input, and stability checks.
- `lab13_meridian.md` through `lab19_legend_panel.md`: Lab 13–19 evidence.
- `visible_output.md`: human-readable executed output.
- `docs/decision-memo.md`: committee memo at the Lab 20 required path.
- `output/pdf/`: rendered decision-memo and validation PDFs.
- `Research-Evolution.md`: working research-evolution brief.
- `docs/validation-and-ai-use.md`: working validation and AI-use record.
- `MUST_FIX.md`: frozen Week 12 completion list.
- `COLD_RUN_RECORD.md`: peer-completed README-only cold-run template.
- `VIDEO_SCREENBOARD.md`: distinct plans for Videos 1–3.
- `project-submission-manifest-template.csv`: 12-row submission manifest;
  unresolved final links remain visibly marked.

Older Ford files remain as prior-course evidence and are not inputs to the
Project 2 result.

## Data boundary

`prices.csv` contains 61 complete month-end adjusted-close observations from
2021-09-01 through 2026-09-01, downloaded from Yahoo Finance on 2026-10-22.
The incomplete October 2026 month was excluded. The source links and data-card
details are recorded in `lab15_portfolio_stability.md` and
`lab17_point_in_time_audit.md`. DGS10 is admitted only under the as-of rule in
Lab 17 and is not used by the allocation command above.

## Riskiest claim and rejection test

The riskiest claim is that a historical minimum-volatility mix meeting the
mandate is stable enough to guide a committee allocation. The direct test is to
change the estimation window from all 60 returns to the last 36. The resulting
20-point allocation change rejects that claim for current adoption. A separate
one-point reduction in VT's estimated return moves the all-month mix by five
points, which passes the 10-point limit but does not repair the failed window
test.

## Limitations and monitoring

- Historical means are noisy and are not prospective expected returns.
- The short sample includes one market regime and does not prove future risk.
- The 5-point grid can hide solutions between grid points.
- No taxes, transaction costs, slippage, tracking error, or client cash flows
  are modeled.
- Meeting the 6.5% input threshold does not establish that the realized return
  will reach CPI + 4% after costs.
- The monitoring owner is the portfolio analyst. During a paper pilot, rerun
  monthly and after any data-method change. Kill the pilot if a mandate rule
  fails, any data lineage check fails, or a one-point stress/window update
  moves any weight by more than 10 points.

## AI disclosure

OpenAI Codex assisted with code, tests, documentation, and the Week 12 package.
The working record in `docs/validation-and-ai-use.md` identifies the outputs,
checks, dispositions, and remaining student-owned evidence. The student owns
the final recommendation and must verify every number before submission.
