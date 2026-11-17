# Project 2 — Investment-Committee Memo

> Prepared with disclosed AI assistance. Education, not investment advice.

**To:** Meridian Foundation Reserve Investment Committee

**From:** Portfolio analyst

**Decision:** authorize a paper-only pilot; do not adopt or allocate client capital

**Evidence date:** saved prices through 2026-09-01, downloaded 2026-10-22

## Recommendation

Run the strategy as a tightly bounded paper pilot because it can enforce the
stated mandate but cannot yet support a live allocation. The all-month search
selects 65% SGOV and 35% VT, with 6.58% estimated return and 5.29% estimated
volatility. The last-36-month search selects 85% SGOV and 15% VT, with 6.81%
estimated return and 1.79% estimated volatility. Both satisfy the encoded
6.5% return threshold and 3% reserve rule, but the 20-point allocation change
exceeds the 10-point stability limit.

## Evidence and strongest supported claim

The evidence supports only this claim: the code reproducibly finds a feasible
lowest-volatility portfolio on its 5-point grid under the supplied historical
inputs. Known-answer tests reproduce the baseline portfolios, invalid
correlations fail loudly, and the app and command use the same engine.

It does not establish that 6.5% will be earned after costs, that the selected
mix is stable, or that historical volatility measures prospective loss risk.
A one-point reduction in VT's estimated return changes the all-month mix to
60% SGOV and 40% VT, a five-point move. That passes the narrow stress limit but
does not cure the larger historical-window failure.

The three claims the evidence cannot support are: (1) the strategy will earn
6.5% after costs, (2) the selected weights are stable, and (3) historical
volatility captures the client's prospective loss risk.

## AI-generated cases for student disposition

| Case | Tagged case |
|---|---|
| Reject | **Output:** reject live use because the window test fails. **Source:** the 65/35 and 85/15 saved runs. **Assumption:** a move above 10 points is decision-material. **Speculation:** instability will persist in future samples. |
| Redesign | **Output:** predeclare inputs and evaluate prospective decisions. **Source:** the current test is in-sample and window-sensitive. **Assumption:** three monthly cycles can reveal operational failure. **Speculation:** a redesigned estimator may reduce turnover. |
| Pilot | **Output:** use a paper-only pilot with the kill rule below. **Source:** the code passes reproducibility and constraint checks. **Assumption:** a notional pilot has educational value without client-capital risk. **Speculation:** it may produce evidence strong enough for a later live-pilot decision. |

These are AI-generated cases, not the student's final judgment. The student
must independently accept, qualify, or reject them before submission.

## Pilot terms

- **Size:** $0 client capital; shadow a notional $100,000 portfolio.
- **Duration:** three monthly decision cycles.
- **Monitoring owner:** portfolio analyst, reporting each cycle to the CIO.
- **Monitor:** mandate compliance, missing or changed data, estimated inputs,
  turnover, weight changes, and the result under both saved windows.
- **Kill rule:** stop and recommend rejection if any mandate rule or lineage
  check fails, or if a one-point input stress or window update moves any weight
  by more than 10 points. The current 20-point window result already prevents
  adoption; the pilot is for evaluating a redesign, not for validating the
  current allocation after the fact.

## Committee ask and reversal condition

Approve the three-cycle paper pilot and require a redesigned prospective test
that fixes inputs before each decision. Reconsider a live pilot only if all
three cycles preserve every mandate rule, complete point-in-time data, and a
maximum weight change of 10 points or less under the predeclared stresses.
Reject the strategy if it continues to breach that limit.

AI use and material checks are recorded in
`docs/validation-and-ai-use.md`. The student must independently verify the
final memo, video statements, and manifest before submission.
