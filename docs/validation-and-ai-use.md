# Project 2 — Validation and AI-Use Record

> OpenAI Codex was used for code, testing, debugging, and documentation organization.
> The analysis and decision are mine; this is for education, not investment advice.

## Highest-risk claim

**Claim:** the historical minimum-volatility mix that meets the encoded mandate
is stable enough to support a committee allocation.

An independent challenger should reject that claim if reasonable estimation
windows or small input changes cause decision-relevant allocation changes,
even when the displayed output looks attractive.

## Claim-to-source-to-test-to-decision trace

| Claim | Source | Test | Result | Decision use |
|---|---|---|---|---|
| The saved all-month mix is 65% SGOV / 35% VT | `prices.csv`, saved through 2026-09-01 | Deterministic run and known-answer test | 6.58% return; 5.29% volatility; 65% reserve | Establishes reproducibility, not prospective validity |
| The process is stable across a reasonable window | Same saved file, last 36 returns | Rerun without changing the search rule | 85% SGOV / 15% VT; 20-point largest change | **Rejected for adoption** because limit is 10 points |
| A one-point VT estimate change is tolerable | Same saved file; VT return −1 point | Locked one-input stress already recorded in Lab 15 | 60% SGOV / 40% VT; five-point move | Narrow test passes; does not cure window failure |
| A modest cost drag is tolerable | Same saved file; uniform 25-basis-point annual drag | Rerun the full search on net estimates | 60% SGOV / 40% VT; 6.74% net return; five-point move | Narrow test passes; does not cure window failure |
| A stricter reserve rule remains feasible | Same saved file; reserve minimum raised from 3% to 70% | Exhaustive 5-point-grid search | No feasible portfolio | **STOP** rather than relax the mandate |
| The monitoring signal is point-in-time | DGS10 2026-09-29 measurement in 2026-09-30 vintage | Lab 17 vintage/revision audit and frozen data card | 5.26%, above student-defined 5.00% watch threshold | Rerun stress package; no automatic trade |
| Inputs obey basic technical constraints | Course training inputs and saved CSV | Known answers, symmetric/bounded correlation checks, malformed-input refusals | Checks pass | Supports use in a paper pilot |

<!-- pagebreak -->

## Data integrity and lineage

- `data/input-ledger.csv` is the single source-of-truth map for every
  load-bearing value, unit, as-of boundary, definition, source, transformation,
  exclusion, and decision use.
- `prices.csv` is a frozen 2026-10-22 Yahoo Finance snapshot with 61 shared
  monthly adjusted closes through 2026-09-01. The incomplete October month was
  excluded; arithmetic returns, annualization, covariance, and both windows are
  calculated in `portfolio.py`.
- Provider corrections can revise adjusted closes. A refreshed file is a new
  data version and must rerun the full package; it may not silently replace the
  frozen submission input. The repository contains no credentials or personal
  data, and production redistribution requires a separate licensing review.
- The DGS10 monitoring value is stored with measurement date, as-known vintage,
  units, source, download date, release rule, transformation, and decision use
  in `data/dgs10-point-in-time-signal.csv`.

## Model-risk challenge

- **Conceptual soundness:** minimizing volatility under a historical mean-return
  constraint fits the coded classroom purpose, but historical means are weak
  forecasts and the 6.5% threshold is not a guaranteed client outcome. The app
  checks return, reserve, long-only, and full investment; it does not establish
  issuer, five-day-liquidity, turnover, or the undefined calendar-loss promise.
- **Outcome analysis:** no prospective out-of-sample result exists. The window
  comparison rejects stability, despite both outputs satisfying the mandate.
- **Ongoing monitoring:** rerun after each monthly data update and any method
  change; monitor data lineage, constraint compliance, turnover, and weight
  sensitivity. The portfolio analyst owns monitoring.
- **Independent rejection evidence:** unsupported forward-looking inputs,
  missing point-in-time data, a failed mandate rule, or a weight move above 10
  points is sufficient to reject or restrict use.

## Locked changed-input record

**Immutable prediction commit:** `9ec9d32`, committed 2026-11-17 at 14:19:29
America/Indiana/Indianapolis, before the changed-input run. The human-authored,
AI-off prediction is preserved verbatim in `LAB20_READINESS.md`:

> I think the VT allocation will increase from 35% to around 40% because the
> portfolio needs more stocks to reach the higher return target.

| Field | Locked record |
|---|---|
| Load-bearing input | Objective expected return |
| Old value | 6.50% annually |
| New value | 6.80% annually |
| Predicted direction | VT increases from 35% to about 40% |
| Predicted decision effect | Recommendation remains a paper pilot because the original stability issue remains |
| Result commit | `dbf17bb`, committed 2026-11-17 at 14:21:38 America/Indiana/Indianapolis |
| Actual allocation | 60% SGOV / 0% VGIT / 0% BND / 40% VT |
| Actual direction | VT rose five points; SGOV fell five points |
| Actual decision effect | No change: paper pilot only; the saved 20-point window failure still blocks adoption |
| Match/diagnosis | Direction and approximate weight matched. The higher hurdle required one additional 5-point VT grid unit. |

The first interface view incorrectly compared the edited objective with itself
and showed a zero-point move. The dashboard was repaired to compare every
scenario with the frozen 6.50% baseline; the locked prediction and observed
weights were not rewritten. A separate earlier Lab 15 partner stress reduced
VT's estimated return from 11.90% to 10.90% and also produced a five-point move;
it is supporting evidence, not a substitute for the locked Lab 20 record.

## Named AI-use register

| Tool/version/date | Material output | Independent check | Disposition | Decision effect |
|---|---|---|---|---|
| OpenAI Codex, GPT-5 family; exact service build not exposed; interactions through 2026-11-23 | Portfolio engine, tests, and Streamlit app assistance | Known answers, invalid-input tests, saved CSV reruns | Accepted for calculation with limitations | Produced reproducible evidence; did not authorize adoption |
| OpenAI Codex, GPT-5 family; exact service build not exposed; 2026-10-29 and 2026-11-23 | Point-in-time audit, data card, and written organization | PAYEMS revision probe, DGS10 overlap comparison, student source checks | Qualified | DGS10 admitted only under explicit as-of rule and used only as a monitoring flag |
| OpenAI Codex, GPT-5 family; exact service build not exposed; 2026-11-17 to 2026-11-23 | README, memo, validation trace, tests, and video plan | Deterministic command, app tests, repository comparison, student final review | Accepted as drafting/implementation support | Aligns the package around a paper-pilot recommendation; student owns the decision |

## Pilot, monitoring, and kill rule

Pilot a notional $100,000 portfolio for three monthly decision cycles with no
client capital. The portfolio analyst monitors the two window results, estimate
and cost stresses, the point-in-time DGS10 watch, data lineage, constraint
compliance, and turnover each cycle.
Kill the pilot and recommend rejection if a lineage/mandate check fails or any
predeclared stress/window update moves a weight by more than 10 points. A live
pilot can be reconsidered only after three prospective cycles pass every rule.
