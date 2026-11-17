# Evidence

What this workspace claims, what shows it, and how to check it yourself. A claim is listed only when a command, a test or a record backs it. The [milestone record](docs/milestones/m1.md) has how each was built and what went wrong on the way.

Last run: 2026-11-16, at the eval's third recording, on the branch `m2/slice-0`. CI runs the first three commands below on Linux, macOS and Windows on every pull request and every push to `main`. After the merge, [the run on `main`](https://github.com/ryantornberg/agent-ready-workspace/actions/runs/43996833124) passed on all three.

## The checks and hooks

| Claim | Evidence | Re-run |
|---|---|---|
| Every part passes its own cases, and the runner refuses one that does not. | 17 parts, 237 cases | `python3 ws.py selftest` |
| Each part added since M2 has a case that a do-nothing stub fails. | `test_cases_bite` | `python3 -m unittest tests.test_cases_bite` |
| A hook refuses an event it cannot read, and the wiring refuses when Python is missing. | `FailClosedTests`: an empty event, a renamed field, a command given as a list, an upper-cased path, a symbolic link into the shelved folder, no Python on the path | `python3 -m unittest tests.test_core.FailClosedTests` |
| A broken check cannot lock out the session that repairs it, and a manifest edit cannot switch the checks off. | `NoSelfLockTests` | `python3 -m unittest tests.test_core.NoSelfLockTests` |
| A commit holds only the files the agent session wrote, whatever command staged them. | `StagingAtTheCommitTests`; [decision 0002](docs/decisions/0002-hooks-remind-the-commit-enforces.md) | `python3 -m unittest tests.test_core.StagingAtTheCommitTests` |
| The page checks cover the workspace's own pages, report a file they cannot decode, and agree between the folder and the commit. | `AdoptionPathTests` | `python3 -m unittest tests.test_core.AdoptionPathTests` |
| The manifest names the engine's version, a reason for every part and a full tier binding. | `ShapeForGrowthTests` | `python3 -m unittest tests.test_core.ShapeForGrowthTests` |
| A direct push to main that adds a machinery commit is refused, and so is `gh pr merge --admin`; the machinery page and the manifest hold one list. | `DirectPushTests`, against a temporary bare remote and through `git push` itself; `AdminMergeTests`; the cases of `direct_push` and `no_admin_merge` | `python3 -m unittest tests.test_core.DirectPushTests tests.test_core.AdminMergeTests` |
| Each session gets its own browser. | Two isolated browser servers both opened a page, and two sharing a profile folder collided, the second reporting the lock (opt-in test, run 2026-11-16 on macOS with `@playwright/mcp@0.0.84`). A recorded Claude Code 2.1.326 session listed the project's server as connected, with 25 browser tools and none of the plugin's: [tests/records/claude-code-browser-session.json](tests/records/claude-code-browser-session.json). `browser_isolation`'s cases. | `WS_BROWSER_TEST=1 python3 -m unittest tests.test_browser` (needs Node and Chrome); `python3 -m unittest tests.test_core.BrowserIsolationTests` |
| A path is placed by the working copy that holds it, so `shelved` answers the same in a linked worktree, and the edit is recorded in that worktree's ledger. | `WorktreePlacementTests` | `python3 -m unittest tests.test_core.WorktreePlacementTests` |
| A part reaches files, git, the environment and processes only as [decision 0004](docs/decisions/0004-the-hook-contract.md) allows. | `AccessContractTests` reads the decision's table and every part's code | `python3 -m unittest tests.test_core.AccessContractTests` |
| A session start lists the stale pages and the pins behind their upstream, and never fails. Both tools deliver session start and end. | `SessionEventTests`, `PinTests`; one recorded run of each tool, [tests/records/session-events.json](tests/records/session-events.json), replayed by `SessionReplayTests`. In the Claude Code run the notice reached the agent, which named the stale page. | `python3 -m unittest tests.test_core.SessionEventTests tests.test_core.PinTests tests.test_core.SessionReplayTests` |
| A staged pin must be on its reachable upstream's default branch. | `PinTests`, against local fixture repositories; `pin_on_default`'s cases | `python3 -m unittest tests.test_core.PinTests` |
| Two live agent sessions cannot both write in the main working copy: the second is refused and sent to a worktree; a takeover needs a dead holder, or an idle main copy and a lease at least five seconds old; session end releases it. A race of 40 threads has one winner. | `LeaseTests`: every takeover condition refuses on its own; liveness on Linux, macOS and Windows in CI; a Claude Code payload and a Codex payload each take, keep and release a lease | `python3 -m unittest tests.test_core.LeaseTests` |
| The same hooks run under Codex CLI. | One recorded run of codex-cli 0.169.0, [tests/records/codex-cli-run.json](tests/records/codex-cli-run.json), replayed by `SecondToolTests` | `python3 -m unittest tests.test_core.SecondToolTests` |

## The eval

| Claim | Evidence | Re-run |
|---|---|---|
| With the workspace's guidance, a small model passes more often than with a two-line instruction or with nothing. | 135 runs on `claude-haiku-5-5`, recorded 2026-11-16 with Claude Code 2.1.326, 45 per arm across three cases: 45, 19 and 0 passed every grader, with 95% intervals of 92% to 100%, 29% to 57% and 0% to 8%. One-sided Fisher exact test, guided against two-line: p = 8.4e-11. [evals/README.md](evals/README.md#the-recorded-runs) | `python3 evals/pool.py` reads the records. A new recording is `python3 evals/run.py CASE --runs 15` per case: 135 agent runs. |
| The lead comes from the contract's and the index's facts, not the playbook's two habits. | Two-line arm: test first in 45 of 45 runs and 15 of 15 passing on the Export bug, as the guided arm; shelved folder left alone in 0 of 15; other report left alone in 4 of 15. Leaving out the two habit graders, bare passes 20 of 45 and two-line 19 | The per-grader counts in each `evals/runs/*/record.json` |
| Every stored grade follows from its transcript. | CI re-grades all 135 transcripts on every push | `python3 evals/grade.py --recorded` |
| A change to a playbook, the contract, the index, the harness or a hook a grader runs fails the commit until the eval runs again. A record fails too when, counting runs that pass every grader, the guidance does not beat the bare model in each case, or does not beat a two-line instruction across the cases by a one-sided Fisher exact test at p < 0.05, with 40 or more runs in every arm. | `eval_record`'s cases; `EvalThatCanLoseTests`; `EvalRerecordTests`; `EvalHarnessApartTests` | `python3 -m unittest tests.test_core.EvalThatCanLoseTests tests.test_core.EvalRerecordTests tests.test_core.EvalHarnessApartTests` |
| An engine change leaves the eval records current: the harness loads the graded hook's own file and imports nothing from `wslib/`. | `EvalHarnessApartTests`: an added hook event and an edited snapshot module leave every record as it was | `python3 -m unittest tests.test_core.EvalHarnessApartTests` |
| The agent runs inside Claude Code's own sandbox, and none of the operator's environment reaches it. | A probe run held on nine points: no write outside the run's folder, no home folder, no network, no global git identity, none of the operator's aliases, no Read of a home-folder file; Python and a commit still worked. The transcripts are scanned by a test, for forward-slash and backslash paths alike. | `python3 evals/run.py --probe` (one agent run) |

## Outside checks

| Check | Result |
|---|---|
| The red team's private attack scripts, re-run on 2026-11-15 against a scratch copy of the merged `main` | Every attack was handled or is listed in the M1 plan's "Attacks left for later". The [milestone record](docs/milestones/m1.md#outside-checks) has each outcome. |
| A fresh session's red team of the result | Triaged in the [milestone record](docs/milestones/m1.md#outside-checks). |

## Not yet shown

- **That the workspace helps on real work.** The eval's traps were written by the same hand as the guidance, in a small invented scaffold, and nothing here has yet been used on a real project.
- **Any model but one, any agent tool but Claude Code for the eval.**
