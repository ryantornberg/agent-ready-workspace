---
kind: record
last-reviewed: 2026-11-18
covers: docs/plans/decision-queue.md
reviewed-at: 818692b1d9624ec9669ed454cee5f56e5c7bda9e
---

# Red team review: docs/plans/decision-queue.md

Round 2 of the red team on the decision queue plan's second draft, with the author's triage of each finding.

**In short:** 16 findings on the second draft, each triaged by the plan's author. The red team's own verdict was not kept.

This record was moved out of the plan's "Red team" section on 2026-11-25, by the maintainer's decision. The red team's own record was not kept at the time, so the table below is the author's triage, word for word as the plan held it.

## Verdict

Not recorded. The plan's author kept only the triage below.

## Findings

In the Verdict column, the author's disposition and whether the author verified the finding or inferred it. In the Action column, what the next draft changed.

| # | Finding | Verdict | Action |
|---|---|---|---|
| R2-1 | C3 cannot be computed: nothing writes a pass or a session start, so "must be 0" held by construction. A `direct` answer would count as pickup. | Accepted, verified | `pass start` and `pass end` write events and issue ids. C3 counts only answers not `direct`. "No message sent" is checked against the playbook and wrapper text, and stated as prose. |
| R2-2 | Answers to a session that is gone are stranded; several paths give a new session id; `close` had no rule. | Accepted, verified | `take` re-keys an answer on the person's word, and the report prints its line. Fact (a) covers every path. `close` runs only in a pass, on `open` or `answered`. |
| R2-3 | A broad park rule files every clarifying question, the pass's own included, and re-asks settled ones. | Accepted, inferred | The rule is narrowed: park only on the person's word or with no person present. An in-session answer is recorded `direct` and `done`. Should-not-fire cases named. |
| R2-4 | Trigger 2 is not measurable by what criterion 9 named, and nothing checks the wrapper loads. | Accepted, verified | Fact (d); a bar of 8 of 10 and 1 of 10; scenario prompts; at most 80 runs. |
| R2-5 | Criterion 7 named the wrong command for the session-start budget, which is shared. | Accepted, verified | `python3 tests/hook_cases.py` with a store fixture. |
| R2-6 | Evidence answers read like the person's decision. | Accepted, inferred | They join the thread's confirmation list and are labelled at pickup. |
| R2-7 | A pass id can be forged. | Accepted, verified | The tool refuses an id it did not issue or that has ended. |
| R2-8 | The cut path leaves the queue half alive. | Accepted, verified | The cut path lists every artifact and withdraws the queued edits. |
| R2-9 | Slice 6 is not ordered against M4's closing recording. | Accepted, inferred | The queued edits are marked "only on slice 6's keep", and the M4 plan must order the verdict first. |
| R2-10 | `milestone: M10` contradicts the decision to build after M3; `prove-by: M10` is not tied to M10. | Accepted, verified | `milestone: M4`. Slice 5 writes a line for the program's M10 done-when. |
| R2-11 | Codex already has pickup through its `SessionStart` wiring. | Accepted, verified | Non-goals corrected; Codex cases in criterion 6; Codex resume in fact (a). |
| R2-12 | If fact (b) fails, nothing tells the agent its session id. | Accepted, verified | On that branch the hook prints the id at every start. |
| R2-13 | The wrapper may have no room, and `loaded_size` prints nothing under the ceiling. | Accepted, verified | A precondition of 600 bytes of headroom, a test that prints the total, a stop rule. |
| R2-14 | `ws.py check` does not verify `prove-by` or the M4 queued list. | Accepted, verified | Each has a `grep`. |
| R2-15 | The contract's eval-rule wording is not this plan's business. | Accepted, verified | Removed from slice 5. |
| R2-16 | Slice 5 writes public text at the worker tier. | Accepted, verified | Slice 5 runs at the driver tier. |

## What survives

Not recorded by the red team. The plan noted of the round: Round 2, 2026-11-18. A fresh session read the second draft and the sources. It found every round-1 action in the body; 7 of its 16 findings finish round-1 actions.
