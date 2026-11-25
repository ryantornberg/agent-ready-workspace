---
kind: record
last-reviewed: 2026-11-18
covers: docs/plans/decision-queue.md
reviewed-at: 319cb1d312f4819a94f9ddf21d5cb23e6165b0ec
---

# Red team review: docs/plans/decision-queue.md

Round 4 of the red team on the decision queue plan's fourth draft, with the author's triage of each finding.

**In short:** 14 findings on the fourth draft, each triaged by the plan's author. The red team's own verdict was not kept.

This record was moved out of the plan's "Red team" section on 2026-11-25, by the maintainer's decision. The red team's own record was not kept at the time, so the table below is the author's triage, word for word as the plan held it.

## Verdict

Not recorded. The plan's author kept only the triage below.

## Findings

In the Verdict column, the author's disposition and whether the author verified the finding or inferred it. In the Action column, what the next draft changed.

| # | Finding | Verdict | Action |
|---|---|---|---|
| R4-1 | R3-5's action brought back engine liveness with no source; Codex on Windows has no process id. | Accepted, verified | No liveness: `pass start` ends any open pass and logs it abandoned. Only the person starts a pass. |
| R4-2 | Slice 4's selection runs could call the private skill, which messages sessions, and publish its text. | Accepted, verified | Runs use `--disallow-tools SendMessage` and `--no-publish`; fact (e) checks the private skill is absent; the same-purpose case uses a stand-in. |
| R4-3 | Turning the private skill off in the main copy may not reach worktree sessions. | Accepted, inferred | Fact (e) checks worktree sessions; on failure, a user-level deny or a stop. |
| R4-4 | Criterion 8 fails without the playbook's row in the README's proof table. | Accepted, verified, finishing | Slice 3 adds the row and count; the cut path removes them. |
| R4-5 | Criterion 12's `grep` forbade the pickup line and scanned eval results. | Accepted, verified, finishing | It greps the playbook and the wrapper only, and forbids only a resume line that carries a prompt. |
| R4-6 | The same-purpose case was called should-not-fire but must win. | Accepted, verified, finishing | It is a should-fire case with a stand-in. |
| R4-7 | The run budget did not count the baseline arm. | Accepted, verified | `--ablation none`; the budget is in child runs. |
| R4-8 | Some stops left merged machinery with no way out. | Accepted, verified | Facts (a), (b), (d) and (e) stop before slice 1; a slice 4 miss runs the cut path. |
| R4-9 | If fact (b) fails, the ownership guards are honor-system. | Accepted, verified | A failed fact (b) is a stop. |
| R4-10 | Fact (c)'s output would put private sessions in a public page. | Accepted, verified | `--cwd` this repository, and field names only. |
| R4-11 | Codex pickup is shown by wiring and cases, not a run. | Accepted, verified | Stated as an unverified limit. |
| R4-12 | A session answering its own item in its own pass counted as pickup. | Accepted, verified | Excluded from the count. |
| R4-13 | A closed item never reached the session that asked. | Accepted, verified | Pickup shows closed items with their reason; `done` acknowledges them. |
| R4-14 | `docs/layout.md`'s page table got no row. | Accepted, verified | Slice 3 adds it; the cut path removes it. |

## What survives

Not recorded by the red team. The plan noted of the round: Round 4, 2026-11-18. A fresh session read the fourth draft and the sources. All 20 round-3 actions are in the body; four made new problems and three needed a follow-up.
