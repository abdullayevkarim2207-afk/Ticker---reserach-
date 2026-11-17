# Project 2 — Validation and AI-Use Record

> Prepared with disclosed AI assistance. Education, not investment advice.

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
| Inputs obey basic technical constraints | Course training inputs and saved CSV | Known answers, symmetric/bounded correlation checks, malformed-input refusals | Checks pass | Supports use in a paper pilot |

## Model-risk challenge

- **Conceptual soundness:** minimizing volatility under a historical mean-return
  constraint fits the coded classroom purpose, but historical means are weak
  forecasts and the 6.5% threshold is not a guaranteed client outcome.
- **Outcome analysis:** no prospective out-of-sample result exists. The window
  comparison rejects stability, despite both outputs satisfying the mandate.
- **Ongoing monitoring:** rerun after each monthly data update and any method
  change; monitor data lineage, constraint compliance, turnover, and weight
  sensitivity. The portfolio analyst owns monitoring.
- **Independent rejection evidence:** unsupported forward-looking inputs,
  missing point-in-time data, a failed mandate rule, or a weight move above 10
  points is sufficient to reject or restrict use.

## Locked changed-input record

The existing Lab 15 record must remain unchanged as the contemporaneous record.
It reduces VT's all-month estimated return from 11.90% to 10.90%, predicts and
then observes a change from 65/0/0/35 to 60/0/0/40, and records a five-point
largest weight move. See `lab15_portfolio_stability.md`. Do not backfill any
missing timestamp or commit.

## Named AI-use register

| Tool | Material output | Independent check | Disposition | Decision effect |
|---|---|---|---|---|
| OpenAI Codex | Portfolio engine, tests, and Streamlit app assistance | Known answers, invalid-input tests, saved CSV reruns | Accepted for calculation with limitations | Produced reproducible evidence; did not authorize adoption |
| OpenAI Codex | Point-in-time audit app and written organization | PAYEMS revision probe, DGS10 overlap comparison, student source checks | Qualified | DGS10 admitted only under explicit as-of rule; not used in allocation output |
| OpenAI Codex | Week 12 README, memo, validation trace, and video plan | Student must compare every number to `python3 project2_run.py` and course requirements | Working draft pending student check | Aligns the package around a paper-pilot recommendation |

## Pilot, monitoring, and kill rule

Pilot a notional $100,000 portfolio for three monthly decision cycles with no
client capital. The portfolio analyst monitors the two window results, the
one-point stress, data lineage, constraint compliance, and turnover each cycle.
Kill the pilot and recommend rejection if a lineage/mandate check fails or any
predeclared stress/window update moves a weight by more than 10 points. A live
pilot can be reconsidered only after three prospective cycles pass every rule.

## Remaining human evidence

- A peer must complete a cold run of the final commit without coaching.
- The student must insert the unchanged Edition A and finish the A-to-B account.
- The student must verify the decision and speak the three videos.
- Final video URLs, transcripts, timestamps, and access checks cannot be
  invented and remain unresolved until completed. The memo and validation PDFs
  have been generated and visually checked in `output/pdf/`.
