# Project 2 — Research Evolution

> OpenAI Codex was used for code, testing, debugging, and documentation organization.
> The analysis and decision are mine; this is for education, not investment advice.

## Edition A status — unavailable and not recreated

No Project 2 Edition A PDF or Brightspace receipt was available for the final
package. On 2026-11-23, the public repository, every reachable Git commit, and
the local project files were searched; no Edition A checkpoint was found. The
student then confirmed that the file was unavailable. Consistent with the
course boundary, this document does not reconstruct, backdate, or label later
work as Edition A. The missing baseline limits the ability to establish an
auditable before/after change. Edition B and the current decision evidence are
preserved below.

## Edition B — current decision and intended user

The intended user is the Meridian Foundation Reserve investment committee. The
decision is whether to adopt, allocate to, rebalance, pilot, or reject the
portfolio process under its seven-year mandate. The current recommendation is
a tightly bounded three-cycle paper pilot of a $100,000 notional portfolio,
with **$0 client capital**.

## Edition B change table

| Changed item | Edition A | Edition B | Driver | Evidence or test |
|---|---|---|---|---|
| Recommendation | Unavailable; no preserved baseline and not recreated | Tightly bounded paper pilot; no client allocation | Own analysis, course tests, AI-assisted implementation | All-month versus last-36-month window changes SGOV and VT by 20 points |
| Data/source choice | Unavailable; no preserved baseline and not recreated | Frozen monthly adjusted closes; explicit 2021-09 to 2026-09 boundary | Course instruction and own source work | `prices.csv`; Lab 15 source table; Lab 17 point-in-time audit |
| Model design | Unavailable; no preserved baseline and not recreated | Exhaustive long-only 5-point grid subject to return and reserve constraints | Mixed | Known answers, invalid-input refusals, and shared app/engine checks |
| Risk or uncertainty | Unavailable; no preserved baseline and not recreated | Expected-return, cost, and window instability prevent adoption; an infeasible constraint stops the process | Peer challenge, own analysis, and AI-assisted implementation | VT and 25-bp cost stresses each move five points; window test moves 20 points; 70% reserve stress has no feasible mix |

## AI-output check

AI assisted with the allocation engine, tests, documentation, and package
alignment. The material allocation numbers are accepted only because the saved
price file and deterministic code reproduce them. The inference that meeting a
historical return threshold proves a prospective return is rejected. The
committee action is therefore bounded to a paper pilot.

## What changed from Edition A to Edition B, and why?

The unavailable Edition A means this package cannot establish a reliable
A-to-B change, and it does not claim one. The current evidence nevertheless
supports a bounded decision: reproducibility and encoded mandate compliance
are necessary but not sufficient because the 20-point historical-window
instability exceeds the 10-point limit. That result prevents live adoption and
makes a prospective, monitored paper test the next decision-relevant step.
