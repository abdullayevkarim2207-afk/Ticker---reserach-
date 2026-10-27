# Lab 16 — Provenance Gate

## Decision question

**On the day I would have traded, what did this data actually say — and how
much of what I see now came later?**

The standard-library implementation is in [`asof.py`](asof.py). From the
repository root, run:

```bash
python asof.py
```

The editable table and decision date are at the top of the file. Every output
is calculated from those inputs; the expected answers are not stored in the
program.

## Known-answer proof

With the decision date set to `2026-03-31`, the four rules produce this audit
trail in the required order:

| Funnel step | Count removed | Source rows removed |
|---|---:|---|
| Quarantined: no ticker | 1 | 11 |
| Exact duplicate | 1 | 7 |
| Published after the decision date | 3 | 3, 8, 10 |
| Older vintage replaced by a revision | 1 | 2 |
| **As-of panel** | **6 remain** | **1, 4, 5, 6, 9, 12** |

The calculated signals also match the known answer:

| Ticker | As-of signal | Naive signal |
|---|---:|---:|
| AAA | +1.98% (February) | +5.83% (March) |
| BBB | −1.02% (February) | −5.15% (March) |
| CCC | +0.91% (February) | +1.82% (February, revised) |

The automated later-date check changes the decision date to `2026-04-15` and
proves that every as-of signal then equals its naive counterpart. By that date,
all rows in the training table had been published.

## How rule 4 works

`keep_latest_vintage` creates one dictionary entry for each `(ticker, month)`
pair. It reads the surviving rows in order and replaces the entry only when it
finds a later publication date. After the loop, the dictionary contains the
row that was most recently published for every ticker-month. The function
then returns those rows as the panel and records every other vintage as
removed. A row-number tie-break makes the result deterministic if two
different values have the same publication date.

This rule is why row 4, not row 2, supplies AAA's February value. Row 4 was
published on 25 March and revised the earlier 10 March value from 104.0 to
103.0. The knowable change is therefore `103 / 101 − 1 = +1.98%`.

## Point-in-time learning and reflection

The month measured is the period the value describes; the publication date is
the first day the value could be used. A revision is another publication for
the same measured month. Before the revision date, only the old vintage is
knowable. After that date, the revised vintage becomes knowable.

Look-ahead bias occurs when a historical decision is calculated using data
that was published or revised only later. For AAA, the naive signal uses the
March value of 109.0 even though it was not published until 10 April. On 31
March, the latest knowable value was February's revised 103.0. The naive
`+5.83%` therefore looks stronger than the `+1.98%` signal a trader could
actually have calculated.

Rule 3 removes the rows that matter most to the signal comparison because it
excludes the not-yet-published March observations (and CCC's later February
revision). Rule 4 is also essential: it replaces AAA row 2 with row 4 and
prevents the incorrect `+2.97%` result. A backtest built on the naive column
would claim that the strategy saw stronger AAA growth and a sharper BBB
decline on 31 March than were publicly available. That would overstate the
strategy's historical information and could make a weak rule appear useful.

## Verification

Run the focused checks with:

```bash
python -m unittest tests.test_asof -v
```

The tests cover the funnel, remaining panel, both sets of signals, CCC's later
revision, and the required 15 April comparison.

## AI-use disclosure

OpenAI Codex assisted with implementing and testing the filter and organizing
this written record. I am the student remains responsible for reading and
explaining the code, completing the in-class partner exercise, and submitting
the GitHub links through Brightspace.
