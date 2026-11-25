---
kind: record
last-reviewed: 2026-11-18
covers: docs/plans/decision-queue.md
reviewed-at: 1f11f886156f2434f78ef4366f4e48fefd139bb8, with the uncommitted change of the author
---

# Red team review: docs/plans/decision-queue.md

Round 1 of the red team on the decision queue plan's first draft, with the author's triage of each finding.

**In short:** 26 findings on the first draft, each triaged by the plan's author. The red team's own verdict was not kept.

This record was moved out of the plan's "Red team" section on 2026-11-25, by the maintainer's decision. The red team's own record was not kept at the time, so the table below is the author's triage, word for word as the plan held it.

## Verdict

Not recorded. The plan's author kept only the triage below.

## Findings

In the Verdict column, the author's disposition and whether the author verified the finding or inferred it. In the Action column, what the next draft changed.

| # | Finding | Verdict | Action |
|---|---|---|---|
| 1 | Items closed from evidence never reach the session that asked. | Accepted, verified | An evidence answer is `answered` with source `evidence` and goes through pickup. Only the session holding it closes it with `done`. |
| 2 | "Wake only by the person's pick" is not enforced: any agent can run the grant command. | Accepted, inferred | Waking is out of version one. "Later" names a guard an agent cannot grant itself as its precondition. |
| 3 | "Live", "idle a day" and "gone" have no data source a hook may use. | Accepted, verified | With no wake, the engine needs no liveness. The pass's report uses `claude agents --json`, fact (c). |
| 4 | Matching a gone session's answers by branch sends them to every main-copy session. | Accepted, verified | Matching is by session id only. Fact (a) checks which paths keep the id; `take` covers the rest. |
| 5 | The 0004 amendment names no facts, so pickup cannot be a pure part. | Accepted, verified | Slice 2 names the `answers` fact the runner fills. The printed-once mark is dropped: the hook prints at every start until `done`. |
| 6 | Criterion 4's `git ls-files` command is empty in the main copy and fails in a worktree. | Accepted, verified | Replaced by a `test_queue` case on the store path and `git status --porcelain`. |
| 7 | Criteria 5 and 6 named commands that cannot check them; 10 and 13 named none. | Accepted, verified | Every criterion names a command, and criterion 13 says it is a person's reading. |
| 8 | The `before-message` hook fails closed and blocks other messages. | Accepted, verified | The hook is dropped with waking. |
| 9 | Slice 0 missed facts the design depends on. | Accepted, verified | Slice 0 checks the facts the pull-only design needs, and says when it needs the person. |
| 10 | C2's item count was already met, and the private version tests push, not pull. | Accepted, verified | C2 drops the item count. C3 gives slice 6 a keep-or-cut bar. |
| 11 | The trial gate and a cut were not sequenced or defined. | Accepted, verified | "Preconditions" gates slice 1 on the trial. The stop rule holds a cut path. |
| 12 | The queued contract and index edits had no owner or list. | Accepted, verified | They go to the M4 plan's queued list. |
| 13 | Decision number 0007 will be taken by M3's B5. | Accepted, verified | "The next free number". |
| 14 | Question-log rows change the log's meaning and need a ledger step. | Accepted, verified | Deferred to "Later", after B3's gap kinds. |
| 15 | A wrapper added after M3 is never measured in the routed arm. | Accepted, verified | Slice 4 adds selection cases with a bar, and a byte count. The routed-arm harm stays unmeasured until M4's recording, a known limit. |
| 16 | A prompt-time hook resembles the retired prompt-nudge hook and has no budget. | Accepted, inferred | Dropped from version one; "Later" needs the maintainer's word first. |
| 17 | The pickup notice was called tool-neutral but wired for Claude Code only. | Accepted, verified | Corrected in round 2: pickup works for both; the wrapper is the Claude Code-only part. |
| 18 | Nothing records who answered. | Accepted, inferred | `answer` records its source, a pass id must be one the tool issued, and pickup labels every answer not from a pass. |
| 19 | An untracked store keeps no history for slice 6's counts. | Accepted, verified | An append-only `events.jsonl`; criterion 12 counts from it. |
| 20 | C1 claimed it needs only machinery that exists now. | Partly accepted | B6 has not merged and is a precondition. C1 and C2 have merged (verified, `git log`), against the finding. |
| 21 | Slice details written by the walled reader may carry the original's design. | Accepted, inferred | Details taken from the original are marked (*o*), and builders may change them. |
| 22 | The `?` rule made `do` and `notice` items impossible. | Accepted, verified | It applies to `decide` items only. |
| 23 | `close` had no status; a grant allowed many messages. | Accepted, verified | `closed` is a status. Grants are gone. |
| 24 | Criterion 3 may be flaky on Windows on a shared, briefly polled lock. | Accepted, inferred | The queue has its own lock file and `add` retries. |
| 25 | `AGENTS.md` says any playbook change needs an eval run; decision 0006 exempts unproven pages. | Accepted, verified | Slice 3 cites 0006. The contract's wording is not this plan's to fix (round 2, finding 15). |
| 26 | Slice 6 changes what M4's questions-asked count measures. | Accepted, inferred | Slice 6 notes it in M4's record. |

## What survives

Not recorded by the red team. The plan noted of the round: Round 1, 2026-11-18. A fresh session read the first draft and the sources, and not the private version.
