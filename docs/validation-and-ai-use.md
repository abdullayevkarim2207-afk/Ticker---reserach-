# Validation and AI Use

## Decision, version, and as-of boundary

- **User:** buy-side committee with no current Ford position.
- **Current provisional action:** watch/defer.
- **Reason action is provisional:** the Project 1 FCFF perimeter and complete
  enterprise-to-equity bridge are unresolved.
- **Repository baseline inspected:** Week 7 readiness packet commit
  `415a9ed80968ca5f7b72c3a814a0a5755d598122`, which preserves the prior
  `bda6296e7885f0fce1bbff55cd5533c4ab2e50e6` project baseline plus the
  disclosed readiness files dated October 7, 2026.
- **Historical boundary:** Ford FY2025 Form 10-K, supplemented by Q2 2026 Form
  10-Q where identified.
- **Saved price:** $12.86 at 9:55 a.m. EDT on September 24, 2026.

## Data and convention ledger

| Material input | Source | As-of/availability | Definition/units | Treatment | Risk |
|---|---|---|---|---|---|
| Starting FCFF proxy, $3.5B | Ford FY2025 Form 10-K; `lab06_ford.md` | FY2025 | Company adjusted free cash flow; USD millions | Used only in preliminary Company-excluding-Ford-Credit DCF | Non-GAAP proxy; not a full FCFF reconciliation |
| FY2025 revenue, $187.267B | Ford FY2025 Form 10-K; `lab10_ford.md` | 2025-12-31 | Consolidated revenue; USD millions | Opening historical fact | Point-in-time filing fact |
| Diluted shares, 3,979M | Ford FY2025 Form 10-K; `lab10_ford.md` | FY2025 | Diluted weighted-average shares; millions | Used in per-share outputs | Must match the final valuation date/share convention |
| Ford Credit finance assets, $139.119B | Ford FY2025 Form 10-K; `lab10_ford.md` | 2025-12-31 | Finance receivables plus operating-lease assets; USD millions | Forecast with Ford Credit debt | Final FCFF perimeter remains unresolved |
| Ford Credit debt, $141.417B | Ford FY2025 Form 10-K; `lab10_ford.md` | 2025-12-31 | Ford Credit debt; USD millions | Kept separate from Company debt | Subtracting debt without matched assets would mix perimeters |
| Saved market price, $12.86 | Timestamped source cited in `lab10_ford.md` | 2026-09-24 09:55 EDT | USD/share | Comparison only | Must be refreshed or frozen consistently for final valuation date |

## Validation register

| Claim/output | Failure mode | Test and expected result | Actual result | Disposition | Evidence location |
|---|---|---|---|---|---|
| Five-year statements articulate | Balance sheet does not balance | Maximum annual gap equals zero | Maximum displayed gap is 0.0 in every base year | Accepted for current engine | `python3 lab10_ford_proforma.py` |
| Loud accounting check refuses a broken model | A broken statement passes silently | Add $100M to FY2028 cash; expect failure | Expected FY2028 gap error is raised | Accepted | `python3 lab10_ford_proforma.py --break-check` |
| Higher growth/margin raises value | Direction is reversed or state leaks between cases | One input changes at a time; base restores exactly | Directions pass; base-before/base-after matches | Accepted with range qualification | `lab11_ford.md`; `lab11_ford_sensitivity.py` |
| Original $10.41 FCFE value | Negative FY2026 FCFE is improperly omitted | Include every explicit-period FCFE with its sign | Corrected base value is approximately $10.00 | **Corrected; old result retained** | `lab12_signed_fcfe_check.py`; `visible_output.md` |
| Preliminary $15.01 FCFF value is decision-ready | Non-GAAP starting proxy and Ford Credit perimeter distort value | Reconcile five-year FCFF and full bridge | Not yet completed | **Unresolved must-fix** | `dcf.py`; `lab06_ford.md` |
| Clean README-only cold run | Undocumented dependency or command blocks a cold analyst | Human tester follows only README and records first failure/time | Human cold run not yet performed | **Pending human evidence** | Complete below before checkpoint/final submission |

## Locked Changed-Input Record — existing September 29 record

### Precommit before the run and before AI assistance on the prediction

| Precommit timestamp | Repository commit | Material input | Old → new value/units | Expected output direction | Expected decision effect |
|---|---|---|---|---|---|
| 2026-09-29 1:50 p.m. | Commit not recorded in the original lab record | Revenue growth and gross margin | Revenue base path → 3.5% annually; gross-margin base path → 15.5% annually | Operating income, FCFE, and value/share rise; margin expected to have larger effect | Test strength of provisional valuation; no predetermined recommendation reversal |

### Preserved execution result

| Before/after output | Actual decision effect | Prediction reconciliation | Failure diagnosis or why action did not change | Evidence path |
|---|---|---|---|---|
| Original convention: revenue high $12.00 vs $10.41 base; margin high $12.34 vs $10.41 base | Watch/defer unchanged | Direction passed; operating-income estimate was close but FCFE/value effects exceeded predicted 5%–10% | Even higher cases remained below the cited $12.86 market price; ranges show impact rather than probability | `lab11_ford.md` |
| Signed correction: revenue high $11.66 vs $10.00 base; margin high $12.11 vs $10.00 base | Watch/defer unchanged | Direction and margin-driver ranking remain | The original valuation excluded negative FY2026 FCFE; signed audit repaired the arithmetic | `lab12_signed_fcfe_check.py` |

The missing pre-run repository commit is preserved as a limitation; it must not
be backfilled as though it had been recorded contemporaneously.

## README-only cold-run record

| Field | Result |
|---|---|
| Tester | Peer (name intentionally omitted) |
| Operating system | Windows 11; terminal shell not recorded |
| Python version | 3.13.1 |
| Repository commit tested | `12bbf96` |
| Start time | 9:10 p.m. on October 7, 2026 ET |
| First failure | No failure |
| Resolution or limitation | Not applicable; terminal shell was not recorded |
| Time to visible output | 13 minutes |
| Visible output reached | Yes |
| Result observed | DCF $15.01/share; corrected signed-FCFE $10.00/share; balance-sheet checks passed; manifest audit ran successfully; watch/defer remained the recommendation |

The peer followed only `README.md` without coaching. The student's separate
guided learning run is not represented as the required human cold run.

## Project readiness audit — October 7, 2026

### Mechanical manifest result

The supplied checker ran after installing the dependency listed in
`requirements.txt`. It confirmed 12 manifest rows and returned these gaps:

- `Research-Evolution.pdf`
- Decision memo or deck
- Video 1 and Transcript Video 1
- Video 2 and Transcript Video 2
- Video 3 and Transcript Video 3

The first AI-assisted local setup failure was
`ModuleNotFoundError: No module named 'pandas'`; running the README's dependency
installation resolved it. This is a local smoke-test record, **not** the
required human README-only cold run, so the human record above remains pending.
The repository URL returned HTTP 200 in a logged-out access check on October 7,
2026 ET; access must be confirmed again after the final submission is frozen.

### Highest-risk claim

The normalized operating forecast and treatment of Ford Credit can produce a
defensible valuation range for a committee with no current position.

### Three ways the claim could be wrong

- **Finance convention:** Ford Credit assets, earnings, cash, and debt are
  treated inconsistently between FCFF and the enterprise-to-equity bridge.
- **Data:** unusual FY2025 items are normalized too aggressively, overstating
  sustainable gross margin and cash flow.
- **Technical/reproducibility:** a negative cash flow or model dependency is
  omitted, as demonstrated by the corrected FY2026 FCFE treatment.

### Open-ended challenge — AI countercase pending independent student check

AI proposed the following boundary case; it is not accepted project evidence
until the student independently reruns or recalculates it with AI closed.

| Item | Current case | AI-proposed changed case |
|---|---:|---:|
| Gross-margin path | 14.5%, 14.6%, 14.7%, 14.8%, 14.8% | Approximately 15.956%, 16.056%, 16.156%, 16.256%, 16.256% |
| Change | — | Parallel increase of approximately 1.456 percentage points |
| Corrected signed-FCFE value/share | $10.00 | $14.146 |
| Saved comparison price | $12.86 | $12.86 |
| Implied upside | –22.2% | 10.0% |
| Provisional decision effect | Watch/defer | Potential initiate boundary only if the student adopts a 10% margin-of-safety rule and independently supports durable margins |

This is decision-relevant rather than merely possible only if primary evidence
supports the higher margin path and the FCFF/Ford Credit perimeter is also
resolved. The student must independently verify the input path and arithmetic,
then write the monitoring owner, smallest committee action, and reversal
threshold without AI assistance.

### Must-fix before final submission

1. Confirm the unchanged Edition A and Brightspace receipt.
2. Resolve the Ford Credit/FCFF valuation perimeter with the instructor or TA.
3. Build the required five-year FCFF forecast and complete bridge.
4. Produce a date-consistent low/base/high valuation range and final action rule.
5. Preserve this human README-only cold run and repeat it if the final frozen
   commit materially changes the setup or execution path.
6. Create Research Evolution, decision memo/deck, frozen validation PDF,
   videos, corrected transcripts, and final access confirmations.
7. Commit/freeze the final evidence and rerun the manifest audit.

### Criterion-specific risk probe requested from the instructional team

Does the proposed treatment of Ford Credit produce an acceptable FCFF
valuation perimeter and enterprise-to-equity bridge for Project 1, or must the
model separate Ford Credit differently before the valuation range can support
the committee action?

## Named AI-use register

| Tool/model surface and exposed version | Interaction date | Material task | Output/claim used or considered | Independent check | Disposition | Effect on decision |
|---|---|---|---|---|---|---|
| OpenAI Codex (version exposed by interface, if any, should be added by student) | 2026-09-29 | Sensitivity implementation and evidence formatting | One-at-a-time growth and margin tests | Student signed arithmetic check and base restoration | Accepted with qualification | Identified gross margin as larger driver over tested ranges; action unchanged |
| OpenAI Codex (version exposed by interface, if any, should be added by student) | 2026-10-05 | Interpreted Week 7 and Project 1 requirements | Readiness checklist and FCFF/FCFE gap | Checked against local course architecture and templates | Accepted | Prioritized FCFF/Ford Credit perimeter as must-fix |
| OpenAI Codex (version exposed by interface, if any, should be added by student) | 2026-10-07 | Prepared readiness files and ran local smoke checks | README, visible output, working manifest, and validation record | Outputs rerun locally; human cold run and access checks explicitly left pending | Accepted as working draft | No change to provisional watch/defer action |
| OpenAI Codex (version exposed by interface, if any, should be added by student) | 2026-10-07 | Proposed strongest changed-assumption countercase | Parallel gross-margin shift that would produce 10% modeled upside to the saved price | **Pending student rerun or independent arithmetic with AI closed** | Pending; do not cite as accepted evidence yet | Potential initiate boundary; current action remains watch/defer |

## Limitations, monitoring, and kill/escalation rules

- Do not initiate based on the preliminary $15.01 FCFF proxy alone.
- Do not average the preliminary FCFF proxy with the linked FCFE diagnostic.
- Escalate the Ford Credit perimeter question before finalizing the range.
- Monitor gross margin, Ford Pro profitability, Model e losses, warranty costs,
  signed cash flow, and Ford Credit asset/debt funding each reporting period.
- If the reconciled FCFF range remains wholly below the same-date market price,
  the committee should consider **do not initiate**, not indefinite watch/defer.
- An initiate action requires a reconciled range and an explicit margin-of-safety
  rule supported by evidence; that threshold has not yet been set by the student.
