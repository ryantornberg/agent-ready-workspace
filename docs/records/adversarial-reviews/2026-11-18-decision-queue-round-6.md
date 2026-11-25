---
kind: record
last-reviewed: 2026-11-18
covers: docs/plans/decision-queue.md
reviewed-at: 09fd39cc3be61659eb359444d7f4ff82e18e79fd
---

# Red team review: docs/plans/decision-queue.md

Round 6 of the red team on the decision queue plan's sixth draft, with the author's triage of each finding.

**In short:** 16 findings on the sixth draft, each triaged by the plan's author. The red team's own verdict was not kept.

This record was moved out of the plan's "Red team" section on 2026-11-25, by the maintainer's decision. The red team's own record was not kept at the time, so the table below is the author's triage, word for word as the plan held it.

## Verdict

Not recorded. The plan's author kept only the triage below.

## Findings

In the Verdict column, the author's disposition and whether the author verified the finding or inferred it. In the Action column, what the next draft changed.

| # | Finding | Verdict | Action |
|---|---|---|---|
| R6-1 | The cut path left a reference page in `docs/playbooks/`, and moved it and changed its proof keys in one commit; both are refused. | Accepted, verified | Move to `archive/` in one commit, strip the keys in a second. |
| R6-2 | `claude agents --cwd` may list background sessions only, so the report would call interactive ones gone. | Accepted, verified | Fact (c) checks it; on a miss the report filters `--json` in memory. |
| R6-3 | Without `--scaffold` the stand-in never loads, and the should-fire case passes by default. | Accepted, verified, finishing | `--scaffold` and `--runs 10`; a grader checks the stand-in loaded; a run without it is invalid. |
| R6-4 | The narrow guard never triggers in eval runs, which use temporary folders. | Accepted, verified | Fact (e) is split. Eval runs get a user-level deny held only during slice 4's runs, its cost stated. |
| R6-5 | Checking fact (e) by calling the skill would load the original, and slice 0 ran before the turn-off. | Accepted, verified | Fact (e) reads the skill listing only; slice 0 waits for the turn-off. |
| R6-6 | The Codex branch left "ownership commands" undefined and contradicted the non-goals. | Accepted, verified | The commands are listed; on that branch Codex neither files nor picks up, and the README says so. |
| R6-7 | Acknowledged closed items could inflate C3. | Accepted, verified | Counted apart, never toward C3; the status after `done` is stated. |
| R6-8 | A size check on the live store fails when another session files during the tests. | Accepted, inferred | A unique marker, checked absent; a missing live store passes. |
| R6-9 | Criterion 5 missed the idle-pass branch and `pass end` from another session. | Accepted, verified, finishing | Both added. |
| R6-10 | The hook and `list --mine` cannot share wording under 0004's import list. | Accepted, verified | `wslib.queuetext`, added to the allowed modules by the amendment. |
| R6-11 | Slice 5's `docs/parts.md` edit missed the facts table. | Accepted, verified, finishing | Named, in slice 5 and the cut path. |
| R6-12 | The 9,000-byte ceiling is hard-coded, and M3 resets it. | Accepted, verified | Read from `workspace.json`. |
| R6-13 | Verification omitted the `-v` run. | Accepted, verified, finishing | Added. |
| R6-14 | The grep missed common resume-with-prompt forms. | Accepted, inferred | Widened, and the page's prose covers the rest. |
| R6-15 | Building in a worktree contradicts the contract's "only then". | Rejected | The maintainer's standing rule since M2's slice 4 builds slices in worktrees; the M3 plan carries it. The Limits line now cites it. |
| R6-16 | `CLAUDE_CODE_SESSION_ATTENDED` may signal "no person present", and helpers share their parent's session id. | Accepted, verified | Fact (b) records both; helpers run no queue command; the park rule may use the variable. |

## What survives

Not recorded by the red team. The plan noted of the round: Round 6, 2026-11-18. A fresh session read the sixth draft and the sources. All 17 round-5 actions are in the body; four made new problems. It found no blocker.
