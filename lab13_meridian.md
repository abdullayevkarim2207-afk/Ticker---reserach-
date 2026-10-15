# Lab 13 — Portfolio Mandate Defense

## D — the question

**Which of these portfolios does the Meridian Foundation's mandate permit —
and what must the CIO answer before anyone optimizes?**

## R — statement types before building

| Statement | Type | One-line reason |
|---|---|---|
| S1 — Horizon seven years; annual rebalancing. | Hard constraint | The investment period and permitted rebalancing frequency bound how the portfolio may be designed and maintained. |
| S2 — Objective: CPI + 4% a year, net of costs, over rolling five-year periods. | Objective | It defines the client outcome and the horizon over which performance should be evaluated. |
| S3 — Pays out $0.75 million every quarter; twelve months of payouts held in cash or daily-liquid government securities. | Hard constraint | It creates a measurable reserve requirement of four quarterly distributions in eligible holdings. |
| S4 — Benchmark: 60% global equities, 40% U.S. investment-grade bonds. | Preference | It supplies the CIO's comparison portfolio, but does not say candidate weights must equal it. |
| S5 — Long-only: no borrowing, short sales or derivatives. | Hard constraint | It expressly prohibits exposures and instruments rather than merely expressing a desired outcome. |
| S6 — No single issuer above 8%. | Hard constraint | It imposes a measurable issuer-concentration ceiling, subject to the stated exemptions. |
| S7 — Annual turnover at most 25% without committee approval. | Hard constraint | It caps trading unless the committee grants an exception, although testing it requires current holdings and trades. |
| S8 — At least 90% redeemable within five business days. | Hard constraint | It sets a measurable minimum for portfolio liquidity. |
| S9 — “The reserve cannot have a calendar-year loss greater than 10%.” No measure, no breach rule. | Unverifiable promise | The statement sounds like a guarantee but cannot be tested without a loss measure and a rule for what happens after a breach. |
| S10 — No sector, ESG, tax or home-bias preference; nobody has said what the pilot should optimize. | Missing | The decision criterion is absent, so there is no defined objective function for optimization. |

S7 is a hard rule in the mandate but is not checkable from static candidate
weights alone. S9 is intentionally not converted into a hard coded rule.

## Investment policy statement — learn on my own

### 1. What is an IPS?

An investment policy statement (IPS) records the agreement between an asset
owner and the people managing its assets. It states the portfolio's purpose,
return objective, risk and liquidity boundaries, eligible investments,
governance rules, benchmark, and review process. It gives managers a common
decision framework and gives the client a basis for monitoring them.

### 2. How objectives and constraints work

The objective describes what success means, such as achieving CPI + 4% net of
costs over rolling five-year periods. Constraints define the feasible set:
time horizon, liquidity needs, concentration limits, eligible instruments,
turnover, and other client restrictions. A portfolio should first satisfy the
hard constraints, then be evaluated against the objective and preferences.
Passing constraints does not prove that it can achieve the objective.

### 3. Mapping S1–S10 into the IPS

| IPS element | Meridian statements |
|---|---|
| Time horizon and rebalancing | S1 |
| Return objective and evaluation period | S2 |
| Spending and reserve liquidity | S3 |
| Benchmark | S4 |
| Eligible techniques and leverage | S5 |
| Diversification/concentration | S6 |
| Turnover and governance exception | S7 |
| Portfolio liquidity | S8 |
| Risk language requiring definition | S9 |
| Preferences and missing optimization target | S10 |

## I — checker

The checker is in [`mandate.py`](mandate.py). Run it from the repository root:

```bash
python mandate.py
```

The reserve minimum is computed from editable inputs, not typed as an answer:

\[
4 \times \$0.75\text{ million} \div \$100\text{ million} = 3.0\%.
\]

Cash, U.S. Treasury holdings, and diversified funds are exempt from the issuer
limit. The checker combines Acme bonds and Acme stock before applying the 8%
company limit.

## V — known-answer proof

The program produced the required results for A, B, and C:

| Rule | A | B | C |
|---|---:|---:|---:|
| Weights sum to 100 | 100.0% pass | 100.0% pass | 100.0% pass |
| Long-only (lowest weight) | 0.0% pass | 0.0% pass | 0.0% pass |
| Reserve ≥ 3.0% | 14.0% pass | 1.0% FAIL | 2.0% FAIL |
| Redeemable in 5 days ≥ 90% | 100.0% pass | 85.0% FAIL | 100.0% pass |
| Largest single company ≤ 8% | 0.0% pass | 9.0% FAIL | 8.0% pass |
| Calendar-year loss | Requires CIO clarification | Requires CIO clarification | Requires CIO clarification |
| Verdict | Passes every checkable rule | Fails 3 rules | Fails 1 rule |

Therefore, among the three assigned candidates, only **A** passes every rule
that can be checked from the supplied holdings data. This does not establish
that A will meet the return objective or the undefined loss statement.

### Deliberate changed-input proof

I temporarily changed A's Cash weight from 2% to -2% and its Global equity
index fund weight from 60% to 64%, preserving the 100% total. The rerun showed
a lowest weight of -2.0% and failed only long-only; the reserve fell from 14.0%
to 10.0% and still passed. I then restored the original weights.

## E — attack the checker

Candidate D is 100% Cash and 0% in every other supplied holding. Its weights
sum to 100.0%, its lowest weight is 0.0%, its reserve-eligible and five-day
liquid weights are both 100.0%, and its largest non-exempt company weight is
0.0%, so the program confirms that D passes every checkable rule.

Yes, the objection makes sense because Candidate D holds 100% cash, and even
though it passes all the rules, it is unlikely to earn CPI + 4% after costs.
S2 is the statement that matters because it defines the portfolio's return
objective.

**Sceptical-colleague check:** Playing the partner role, I proposed a second
passing candidate with 100% in the Treasury 10-year note. Playing the reviewer,
I would cite S2 because this concentration may have no credible path to the
required net real return; I would also ask for an explanation of its departure
from S4 without incorrectly treating the benchmark as a hard allocation rule.

## One question for the CIO

**Should the portfolio focus on getting the highest return, having the best
chance of reaching CPI + 4%, or keeping risk as low as possible while still
trying to meet that goal?**

If the CIO wants the highest return, I would invest more in stocks; if the CIO
wants lower risk, I would invest more in safer bonds but still keep some stocks
to help reach the target.

## Quiz on the line I understood least

**Sceptical colleague:** Why is Candidate C rejected even though it has 100%
five-day liquidity and its 8% Acme position does not exceed the issuer limit?

**My answer:** Candidate C is rejected because it only has 2% in reserve
assets, but the requirement is at least 3%. Even though it meets the liquidity
and issuer limits, it still fails the reserve rule, so it cannot be accepted.

## Reflection

A portfolio can pass all the rules but still not be right for the client
because that does not mean it will actually reach the return goal. The program
only checks the rules, not how the portfolio will perform. I was least sure
about S4 because I was not sure if the 60/40 benchmark was a requirement or
just a preference. I chose preference because the CIO did not say we had to
follow it exactly.

## Project 2 mandate — draft for client confirmation

The repository describes the client as a buy-side investment committee with no
current Ford position. Based on that limited context, my draft objective is to
decide whether Ford offers an adequate prospective return relative to its
fundamental risk using a consistent valuation perimeter and date-matched market
price. Hard constraints are to use point-in-time public information, preserve
signed cash flows, reconcile enterprise value to equity value without mixing
Ford Credit and industrial claims, state all units and as-of dates, and issue
no buy recommendation until the valuation range is decision-ready.

The one question for this client is: **What minimum expected return or margin
of safety must Ford offer before the committee will initiate a position?** If
the committee requires a larger margin of safety, the maximum acceptable entry
price falls and a borderline buy becomes watch/defer.

This Project 2 paragraph is a draft because the client's required return and
portfolio-level constraints are not recorded in the repository.

## AI-use disclosure

OpenAI Codex helped implement and run the checker, format the evidence, and
draft the written analysis. The student remains responsible for independently
reviewing the issuer aggregation, the distinction between checkable constraints
and suitability, and the conclusions reported here before submission.
