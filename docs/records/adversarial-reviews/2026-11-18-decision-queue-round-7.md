---
kind: record
last-reviewed: 2026-11-18
covers: docs/plans/decision-queue.md
reviewed-at: 32e9b9620780195d3690e1f1b485a0cb58734032
---

# Red team review: docs/plans/decision-queue.md

Round 7 of the red team on the decision queue plan's seventh draft, with the author's triage of each finding.

**In short:** 17 findings on the seventh draft, each triaged by the plan's author. The red team's own verdict was not kept.

This record was moved out of the plan's "Red team" section on 2026-11-25, by the maintainer's decision. The red team's own record was not kept at the time, so the table below is the author's triage, word for word as the plan held it.

## Verdict

Not recorded. The plan's author kept only the triage below.

## Findings

In the Verdict column, the author's disposition and whether the author verified the finding or inferred it. In the Action column, what the next draft changed.

| # | Finding | Verdict | Action |
|---|---|---|---|
| R7-1 | `done` is the session's own claim, so C3 could count acknowledgements, not action. | Accepted, inferred | `done` requires a `--did` note; the maintainer reads the counted notes before keep. |
| R7-2 | `answer` had no state rule and could send a finished item back to pickup. | Accepted, verified | `answer` takes `open`, or amends `answered`; it refuses `done` and `closed`. |
| R7-3 | Nothing checks that a sandboxed session can write the store in the common git folder. | Accepted, inferred | Fact (b) checks it from a worktree session and from Codex. |
| R7-4 | A live session learns its answers only if the person tells it to look, and the report gave no line for that. | Accepted, verified, finishing | The report prints the line to type in each live session. |
| R7-5 | The cut's first commit would be refused, left broken links, and misread the archive's rules. | Accepted, verified, finishing | Commit 1 moves the page and fixes the README row, links and layout row together; no tombstone; no reference-page wording. |
| R7-6 | The cut left `queuetext`, its allowed-list entry and the seeded hook rows behind. | Accepted, verified, finishing | All three are in the cut path. |
| R7-7 | The allowed-modules test reads one bullet only, so a separate amendment paragraph would not count. | Accepted, verified | Slice 2 edits the bullet inline with a dated note; a test checks it; a refusal by B5's check is a stop. |
| R7-8 | M4's routed arm runs unattended requests with the wrappers on, and trigger 2 could stop those runs. | Accepted, inferred | Three selection cases from the fix-a-bug requests must never stop; M4's queued list notes it. |
| R7-9 | No test covers `done` on a closed item. | Accepted, verified, finishing | Added to criterion 5. |
| R7-10 | Fact (d) tested no stated size. | Accepted, verified | 600 bytes; slice 4 shows the real description is no larger. |
| R7-11 | A key point and the preconditions disagreed on when the private skill is turned off. | Accepted, verified, finishing | Both say before slice 0. |
| R7-12 | Dropped invalid runs left the 8-of-10 bar undefined. | Accepted, verified, finishing | Re-run to 10 valid; more than 2 invalid in a case is a stop. |
| R7-13 | Something else might file this repository's questions into the private queue. | Accepted, inferred | The maintainer confirms nothing does. |
| R7-14 | Slice 0 writes public text under a privacy rule at the worker tier. | Accepted, verified | Driver tier. |
| R7-15 | "Filtered in memory" named no filter. | Accepted, verified, finishing | The playbook gives the filter, printing only id and state. |
| R7-16 | An exported `WS_QUEUE_DIR` would silently point pickup at the wrong store. | Accepted, inferred | Set per command; `list` and the notice name the store when it is set. |
| R7-17 | Criterion 11's grep counts the phrase anywhere in the M4 plan. | Accepted, verified | The list sits under the M4 plan's "Results", and the count reads that section only. |

## What survives

Not recorded by the red team. The plan noted of the round: Round 7, 2026-11-18. A fresh session read the seventh draft and the sources. All 16 round-6 actions are in the body; six left gaps or made new problems. It found no blocker.
