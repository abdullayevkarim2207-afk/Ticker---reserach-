# Lab 20 - Project 2 Readiness

> Prepared with disclosed AI assistance. Education, not investment advice.

## Readiness question

Could a committee member who has never met me reach my decision from this
repository, and does the decision survive one changed input?

**Current answer:** the repository path is reproducible locally, but the final
Lab 20 floor remains incomplete until a partner records a README-only cold run
of a pushed commit and the student completes the AI-closed changed-input step.

## Repository-only local audit

This is an AI-assisted local audit, not the required partner cold run.

| Field | Local audit result |
|---|---|
| Command copied from README | `python3 project2_run.py` |
| First failure | None in the one-command Project 2 path |
| Elapsed time | 0.51 seconds on the local machine |
| Result location | Terminal; preserved in `visible_output.md` |
| Baseline result | 65% SGOV / 0% VGIT / 0% BND / 35% VT; 6.58% return; 5.29% volatility |
| Changed window result | 85% / 0% / 0% / 15%; 6.81% return; 1.79% volatility |
| Largest window change | 20 percentage points, above the 10-point limit |
| Narrow stress result | VT return estimate -1.00 point produces 60% / 0% / 0% / 40%; five-point move |
| Focused tests | 11 passed with `python3 -m unittest tests.test_portfolio tests.test_project2_run -v` |
| Full suite | 24 passed in an isolated environment after `python3 -m pip install -r requirements.txt`, including two app-verdict tests |
| Bare local Python note | Without optional dependencies, discovery stops at `tests/test_asof_app.py`; the one-command Project 2 path still succeeds because it uses only the standard library |
| Copied-snapshot rerun | Clean copied-folder run succeeded in 0.11 seconds with the same decision output; this is still not a peer clone of a pushed commit |

The first documentation failure found by this audit was that the memo was at
`decision_memo.md` instead of the required `docs/decision-memo.md`. The
canonical memo has been added at the required path and the README and manifest
now point to it. A second audit finding was that the app defaulted to older
training inputs and did not state a verdict; it now opens on `prices.csv` and
prints mandate, stability, and committee verdicts after a control is moved.
These fixes do not substitute for the partner's first-failure record.

## Partner cold-run record - required human evidence

The partner must clone the pushed commit, use only the README, and complete the
following without coaching. Do not commit the partner's name or other personal
information.

| Field | Partner record |
|---|---|
| Repository URL | `https://github.com/abdullayevkarim2207-afk/Ticker---reserach-` |
| Commit tested | `8c9e7cb` from the main branch |
| Command copied from corrected README | `git clone ... Ticker-research-cold-run`; `cd Ticker-research-cold-run`; `py project2_run.py` |
| First failure, exactly as observed | `fatal: destination path 'Ticker---reserach-' already exists and is not an empty directory.` |
| Second failure | Windows reported that Python was not found when `python3` was used |
| Elapsed time to result | Not explicitly timed; clone and decision completed in one terminal run |
| Result location | Windows PowerShell terminal output |
| Observed decision | Tightly bounded pilot; do not adopt or allocate client capital yet |
| Fix pushed | README now uses a fresh clone destination and Windows `py` command |
| Rerun after fix | Successful; all three cases, the decision, and reversal trigger printed |

## Changed input - required AI-closed student record

The prediction below was written before changing the input. The existing Lab
15 VT stress is preserved as prior evidence but is not used as today's changed
input.

**Prediction commit:** `9ec9d32`

**Load-bearing input:** Objective expected return

**Old value:** 6.50% annually

**New value:** 6.80% annually

**Prediction:** I think the VT allocation will increase from 35% to around 40%
because the portfolio needs more stocks to reach the higher return target.

**Expected decision effect:** I expect the recommendation to stay as a paper
pilot because the original stability issue still exists.

**Prediction written before running the changed input:** Yes

### Before

- **Input value:** 6.50%
- **Allocation:** SGOV 65%, VGIT 0%, BND 0%, VT 35%
- **Expected return:** 6.58%
- **Volatility:** 5.29%
- **Mandate verdict:** PASS
- **Selected test:** Pending student observation before changing the control
- **Committee decision:** PAPER PILOT ONLY

### After

- **Input value:** 6.80%
- **Allocation:** SGOV 60%, VGIT 0%, BND 0%, VT 40%
- **Expected return:** 6.99%
- **Volatility:** 6.03%
- **Mandate verdict:** PASS
- **Selected test:** PASS; corrected frozen-baseline comparison shows a
  5-point move in SGOV and VT, within the 10-point limit
- **Committee decision:** PAPER PILOT ONLY

**Interface correction after the run:** The first interface view displayed a
0-point move because both comparison panels reused the edited 6.80% objective.
The dashboard now freezes the baseline at the saved 6.50% objective and shows
the actual 5-point allocation move. The prediction and observed allocations
were not changed.

### Outcome

Pending student's AI-closed explanation of whether the decision changed, why
the observed result did or did not match the prediction, and whether the
original decision survived the higher return target. The original prediction
above remains unchanged.

## Code explanation record - required partner exchange

The decision block is `main()` in `project2_run.py`. It calculates the
all-month case, the last-36-month case, and the one-point VT stress; calculates
the largest absolute weight difference between the two windows; then prints the
pilot decision and its reversal rule.

**Partner question and answer from the code:** pending partner exchange.

## Decision line

**Pilot a notional $100,000 portfolio for three monthly decision cycles with no
client capital; reject it if a mandate or data-lineage check fails or any
predeclared stress or window update moves a weight by more than 10 percentage
points.**

## Reflection

1. **What the partner cold run found that I could not see:** the original
   README assumed the macOS/Linux `python3` command and did not protect a
   Windows user from an existing clone-folder collision. The corrected README
   uses the Windows `py` launcher and a fresh destination name; the partner's
   rerun then reached the full decision output.
2. **What I will not touch before the deadline:** after the final prediction,
   partner rerun, and evidence freeze, I will not change `prices.csv`, the
   mandate thresholds, the 5-point grid, or the decision rule.

## Checkout links

- [Lab 20 record](https://github.com/abdullayevkarim2207-afk/Ticker---reserach-/blob/main/LAB20_READINESS.md)
- [README](https://github.com/abdullayevkarim2207-afk/Ticker---reserach-/blob/main/README.md)
- [Decision command](https://github.com/abdullayevkarim2207-afk/Ticker---reserach-/blob/main/project2_run.py)
- [Visible output](https://github.com/abdullayevkarim2207-afk/Ticker---reserach-/blob/main/visible_output.md)
- [Decision memo](https://github.com/abdullayevkarim2207-afk/Ticker---reserach-/blob/main/docs/decision-memo.md)
- [Validation and AI-use record](https://github.com/abdullayevkarim2207-afk/Ticker---reserach-/blob/main/docs/validation-and-ai-use.md)
- [Decision memo PDF](https://github.com/abdullayevkarim2207-afk/Ticker---reserach-/blob/main/output/pdf/project-2-decision-memo.pdf)
- [Validation and AI-use PDF](https://github.com/abdullayevkarim2207-afk/Ticker---reserach-/blob/main/output/pdf/project-2-validation-and-ai-use.pdf)
- [Partner cold-run template](https://github.com/abdullayevkarim2207-afk/Ticker---reserach-/blob/main/COLD_RUN_RECORD.md)
