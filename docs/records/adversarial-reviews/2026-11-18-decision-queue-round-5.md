---
kind: record
last-reviewed: 2026-11-18
covers: docs/plans/decision-queue.md
reviewed-at: 8bd2b07f9ebee6762e8f9156d74f8a3ab1ac3619
---

# Red team review: docs/plans/decision-queue.md

Round 5 of the red team on the decision queue plan's fifth draft, with the author's triage of each finding.

**In short:** 17 findings on the fifth draft, each triaged by the plan's author. The red team's own verdict was not kept.

This record was moved out of the plan's "Red team" section on 2026-11-25, by the maintainer's decision. The red team's own record was not kept at the time, so the table below is the author's triage, word for word as the plan held it.

## Verdict

Not recorded. The plan's author kept only the triage below.

## Findings

In the Verdict column, the author's disposition and whether the author verified the finding or inferred it. In the Action column, what the next draft changed.

| # | Finding | Verdict | Action |
|---|---|---|---|
| R5-1 | Criterion 5 still required the liveness R4-1 removed. | Accepted, verified, finishing | Criterion 5 matches slice 1. |
| R5-2 | Any session running `pass start` would end the person's pass mid-way; the park steps and the pass steps shared a page. | Accepted, inferred | `pass start` refuses while the open pass had a write in the last 30 minutes, unless `--replace`, and prints what it ends. The playbook re-asks from the last confirmed thread, and parking is a separate section with no pass commands. |
| R5-3 | Criterion 12's greps matched text the plan requires. | Accepted, verified, finishing | One pattern for a command that carries a prompt; the page states the prohibition without naming a tool. |
| R5-4 | Closed items were only half wired: criterion 5 and `take` disagreed with slice 1. | Accepted, verified, finishing | `done` refuses `open` and `done`; criteria 6 and 7 cover closed items; `take` accepts them. |
| R5-5 | A stand-in "user skill" cannot load without loading the private one, and writes outside the repository. | Accepted, inferred | The stand-in is a second local plugin in the case's scaffold. Fact (e) checks whether user skills load in eval runs. |
| R5-6 | Nothing gives a still-open session its answers. | Accepted, verified | `queue list --mine`, named in the playbook, with a test. |
| R5-7 | Fact (b)'s stop rule had no branch for Claude Code passing and Codex failing. | Accepted, verified | A Codex-only failure makes the ownership commands refuse under Codex, stated in the README. Codex resume goes through `take`. |
| R5-8 | Fact (d) cannot test a wrapper that does not exist yet. | Accepted, verified | It tests a throwaway wrapper of the planned size, or one B6 shipped. |
| R5-9 | The report would call every Codex session gone and offer to take its answers. | Accepted, inferred | Items record the agent tool; Codex sessions are "liveness unknown" with no `take` line unless asked. |
| R5-10 | The fact (e) fallback silently turns off the maintainer's daily tool everywhere. | Accepted, inferred | A narrower guard first: the private skill refuses inside this repository. The user-level deny is the last resort, with its cost stated. |
| R5-11 | Tests and trials could write into the live store for good. | Accepted, inferred | `WS_QUEUE_DIR` overrides the folder; tests use a throwaway one; criterion 4 checks the live store is untouched. |
| R5-12 | The Verification block left out criteria 9, 11 and 12. | Accepted, verified | Added. |
| R5-13 | C3 lacked the own-pass exclusion criterion 12 counts. | Accepted, verified, finishing | C3 carries it. |
| R5-14 | Slice 5 named one Codex limit where there are two. | Accepted, verified, finishing | Both named. |
| R5-15 | The counting window had no end. | Accepted, verified | `--until`. |
| R5-16 | A cut after a slice 4 miss listed files on an unmerged branch. | Accepted, verified | Close that pull request and cut only what merged. |
| R5-17 | `do` and `notice` items had no path to `done`. | Accepted, inferred | One sentence each in slice 1. |

## What survives

Not recorded by the red team. The plan noted of the round: Round 5, 2026-11-18. A fresh session read the fifth draft and the sources. All 14 round-4 actions are in the body; two were applied in part, two did not reach the criteria, and one made a new problem.
