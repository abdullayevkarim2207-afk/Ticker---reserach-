# Project 2 — Recording Screenboard

> Open each recording with both statements: “I used OpenAI Codex for code,
> testing, debugging, and documentation organization.” “The analysis and
> decision are mine; this is for education, not investment advice.”

These are rehearsal prompts, not final transcripts. Correct transcripts must
match the videos actually recorded.

## Video 1 — How the research changed (maximum 3:00)

**Question answered:** What changed since the first mandate, and which AI output
did I check?

1. Show the unchanged Edition A and state its initial recommendation in your
   own words.
2. Show `Research-Evolution.md` and identify the most consequential change:
   reproducible mandate compliance did not establish allocation stability.
3. Show the all-month 65/0/0/35 result and last-36-month 85/0/0/15 result.
4. Explain that AI helped implement the engine, but the deterministic rerun on
   `prices.csv` checked its numbers.
5. Disposition: accept the calculated numbers, reject the implied claim that a
   historical return threshold proves prospective performance, and change the
   action to a paper-only pilot.

Do not turn this video into a code walkthrough.

## Video 2 — Technical walkthrough (maximum 5:00)

**Question answered:** How does the code turn data into the result, and which
test passed or failed?

Open `app.py` running live, then run:

```bash
python3 project2_run.py
python3 -m unittest tests.test_portfolio tests.test_project2_run -v
```

Trace `prices.csv` → `estimate_from_price_csv` → covariance matrix → exhaustive
5-point `search_lowest_risk_mix` → mandate filters → lowest-volatility feasible
mix. Show that `app.py` imports the same engine.

Highest-risk test: compare all 60 returns with the last 36. The test fails the
decision threshold because SGOV and VT each move 20 points, above the 10-point
limit. Also mention one loud technical refusal: correlations outside −1 to +1
or an asymmetric table raise an error. Show the 25-basis-point cost control and
the 70% reserve stress that returns no feasible mix and stops the process.

Do not spend this video defending the committee recommendation.

## Video 3 — Committee decision (maximum 5:00)

**Question answered:** What should the committee do, under what conditions, and
what reverses the decision?

Opening answer: “Authorize a three-cycle, paper-only pilot of a notional
$100,000 portfolio. Do not allocate client capital.”

Defend with four points:

- The all-month mix is 65% SGOV / 35% VT, with 6.58% estimated return and
  5.29% estimated volatility.
- The last-36-month mix is 85% SGOV / 15% VT, with 6.81% estimated return and
  1.79% estimated volatility.
- Both pass the encoded mandate, but the 20-point weight change rejects current
  adoption.
- A one-point VT return stress moves weights by five points; that narrow pass
  does not cure the failed window test.
- A 25-basis-point annual cost drag also moves weights by five points, while a
  70% reserve minimum makes the search infeasible and stops the process.
- The point-in-time DGS10 watch is 5.26%, above the student-defined 5.00%
  review threshold; it triggers a stress rerun, not an automatic trade.

Monitoring owner: portfolio analyst, reporting monthly to the CIO. Kill the
pilot if a lineage or mandate check fails or any predeclared stress/window
update moves a weight by more than 10 points. Reconsider a live pilot only
after three prospective cycles pass every rule.

### Sceptical question rehearsal

**Question:** “If both portfolios clear 6.5%, why not allocate now?”

**Answer:** “Because 6.5% is an in-sample historical estimate, not a promised
after-cost return. A reasonable window change moves 20% of the portfolio, so
the system has not established a stable action. My system cannot establish
prospective performance from this sample.”

End with the committee ask; do not explain the code architecture again.
