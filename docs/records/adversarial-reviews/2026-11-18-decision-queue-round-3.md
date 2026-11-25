---
kind: record
last-reviewed: 2026-11-18
covers: docs/plans/decision-queue.md
reviewed-at: f494e96ad3d2adf66b1bb4012a4c1f3072ab2411
---

# Red team review: docs/plans/decision-queue.md

Round 3 of the red team on the decision queue plan's third draft, with the author's triage of each finding.

**In short:** 20 findings on the third draft, each triaged by the plan's author. The red team's own verdict was not kept.

This record was moved out of the plan's "Red team" section on 2026-11-25, by the maintainer's decision. The red team's own record was not kept at the time, so the table below is the author's triage, word for word as the plan held it.

## Verdict

Not recorded. The plan's author kept only the triage below.

## Findings

In the Verdict column, the author's disposition and whether the author verified the finding or inferred it. In the Action column, what the next draft changed.

| # | Finding | Verdict | Action |
|---|---|---|---|
| R3-1 | The maintainer's private decision skill is loaded in every session here, overlaps the wrapper's trigger and pushes answers by message, which would spoil slice 6 and bring back the flagged risk. | Accepted, verified | A precondition: the maintainer turns it off for this repository and makes the private pass skip its sessions until slice 6's verdict. A should-not-fire case runs with a same-purpose user skill loaded. |
| R3-2 | Builders can call that skill and load the original. | Accepted, verified | The same precondition. Its one-line description is the stated exposure. |
| R3-3 | A corrupt store would silence every session-start notice, because the runner wraps all session hooks together. | Accepted, verified | The runner sets `answers` to empty on a store error; criterion 7 checks another hook still prints. |
| R3-4 | An evidence answer needed no pass, and `done` was not tied to the item's session, so C3 could be met with no person and no pickup. | Accepted, verified | Evidence answers name the caller's open pass; `done` refuses another session; criterion 5 tests both. |
| R3-5 | A pass cut off before `pass end` stays open, and its id stays usable from any session. | Accepted, inferred | A pass belongs to its session. `pass start` ends one left by a gone session and refuses while a live one holds a pass. |
| R3-6 | R2-3's wording could be read as filing every in-session question. | Accepted, verified | Questions asked and answered in the session are never filed; `direct` is for a filed item answered outside a pass. |
| R3-7 | "No person present" has no signal an agent can read. | Accepted, inferred | The launch or the prompt says the run is unattended; the cases state it. |
| R3-8 | 80 runs could not cover the cases plus the rewrite the stop rule allows. | Accepted, verified | 80 runs per round, two rounds, 160 in all. |
| R3-9 | The plan wrote to the program's M10 line, which is outside this repository. | Accepted, verified, finishing | The M10 line is the maintainer's, listed under "Preconditions". |
| R3-10 | The cut path left tests, the part's files and the fixture behind, and misread decision 0006. | Accepted, verified, finishing | Every file is listed; the cut page becomes a reference page with no proof keys. |
| R3-11 | Criterion 12's `grep` did not search the folder and missed shell routes. | Accepted, verified, finishing | `grep -rnE` over both, with the shell routes, must print nothing. |
| R3-12 | `-b` hides the printed byte total. | Accepted, verified, finishing | The slice report records it from a `-v` run of the one test. |
| R3-13 | If fact (b) fails, `take`, `done` and `close` also need the caller's id. | Accepted, verified | Every such command takes `--session` on that branch. |
| R3-14 | With no gathering and a narrow park rule, a quiet week could cut an untested design. | Accepted, inferred | C3 has a floor of 8 filed items, below which the verdict is "not tested". The intake gap is a key point. |
| R3-15 | B6's check may refuse the playbook committed without its wrapper. | Accepted, inferred | Slices 3 and 4 commit them together. |
| R3-16 | Criterion 12 counted "closed from evidence", which this design does not have. | Accepted, verified | "Answered from evidence". |
| R3-17 | "C2" named both a plan choice and M3's slice. | Accepted, verified | The preconditions say "M3's slices C1 and C2". |
| R3-18 | The key point on the trial read as if a second, time-boxed trial changed the settled one. | Accepted, verified | The key point separates the trial (C2) from slice 6's window (C3). |
| R3-19 | Fact (c) had no branch for failure. | Accepted, verified | The report lists sessions by id without live or gone. |
| R3-20 | Decision 0004 omits facts the runner already fills. | Accepted, verified | Slice 2's amendment lists them. |

## What survives

Not recorded by the red team. The plan noted of the round: Round 3, 2026-11-18. A fresh session read the third draft and the sources. It found 9 of round 2's actions applied as written, 4 applied in part and 3 that made new problems; 4 of its 20 findings finish earlier work.
