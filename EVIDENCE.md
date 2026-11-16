# Evidence

What this workspace claims, what shows it, and how to check it yourself. A claim is listed only when a command, a test or a record backs it. The [milestone record](docs/milestones/m1.md) has how each was built and what went wrong on the way.

Last run: 2026-11-15, at the merge of M1's slice 3 (pull request #9). CI ran the first three commands below on Linux, macOS and Windows: [the run on `main`](https://github.com/ryantornberg/agent-ready-workspace/actions/runs/43792179708).

## The checks and hooks

| Claim | Evidence | Re-run |
|---|---|---|
| Every part passes its own cases, and the runner refuses one that does not. | 9 parts, 164 cases | `python3 ws.py selftest` |
| A hook refuses an event it cannot read, and the wiring refuses when Python is missing. | `FailClosedTests`: an empty event, a renamed field, a command given as a list, an upper-cased path, a symbolic link into the shelved folder, no Python on the path | `python3 -m unittest tests.test_core.FailClosedTests` |
| A broken check cannot lock out the session that repairs it, and a manifest edit cannot switch the checks off. | `NoSelfLockTests` | `python3 -m unittest tests.test_core.NoSelfLockTests` |
| A commit holds only the files the agent session wrote, whatever command staged them. | `StagingAtTheCommitTests`; [decision 0002](docs/decisions/0002-hooks-remind-the-commit-enforces.md) | `python3 -m unittest tests.test_core.StagingAtTheCommitTests` |
| The page checks cover the workspace's own pages, report a file they cannot decode, and agree between the folder and the commit. | `AdoptionPathTests` | `python3 -m unittest tests.test_core.AdoptionPathTests` |
| The manifest names the engine's version, a reason for every part and a full tier binding. | `ShapeForGrowthTests` | `python3 -m unittest tests.test_core.ShapeForGrowthTests` |
| The same hooks run under Codex CLI. | One recorded run of codex-cli 0.169.0, [tests/records/codex-cli-run.json](tests/records/codex-cli-run.json), replayed by `SecondToolTests` | `python3 -m unittest tests.test_core.SecondToolTests` |

## The eval

| Claim | Evidence | Re-run |
|---|---|---|
| With the workspace's guidance, a small model passes more often than with a two-line instruction or with nothing. | 135 recorded runs on `claude-haiku-5-5`, 45 per arm across three cases: 43, 14 and 0 passed every grader. One-sided Fisher exact test, guided against two-line: p = 4e-11. Two graders were stricter than the habits they check; read fairly, 44 or 45, 17 and 0, and p is below 2e-9. [evals/README.md](evals/README.md#the-recorded-runs) | `python3 evals/pool.py` reads the records. A new recording is `python3 evals/run.py CASE --runs 15` per case: 135 agent runs. |
| The lead comes from the contract's and the index's facts, not the playbook's two habits. | Two-line arm: test first in 45 of 45 runs; shelved folder left alone in 0 of 15; right report fixed in 3 of 15 | The per-grader counts in each `evals/runs/*/record.json` |
| Every stored grade follows from its transcript. | CI re-grades all 135 transcripts on every push | `python3 evals/grade.py --recorded` |
| A change to a playbook, the contract, the index or the harness fails the commit until the eval runs again, and a record in which the guidance does not beat the bare model fails too. | `eval_record`'s cases; `EvalThatCanLoseTests` | `python3 -m unittest tests.test_core.EvalThatCanLoseTests` |
| The agent runs inside Claude Code's own sandbox, and none of the operator's environment reaches it. | A probe run held on nine points: no write outside the run's folder, no home folder, no network, no global git identity, none of the operator's aliases, no Read of a home-folder file; Python and a commit still worked. The transcripts are scanned by a test. | `python3 evals/run.py --probe` (one agent run) |

## Outside checks

| Check | Result |
|---|---|
| The red team's private attack scripts, re-run on 2026-11-15 against a scratch copy of the merged `main` | Every attack was handled or is listed in the M1 plan's "Attacks left for later". The [milestone record](docs/milestones/m1.md#outside-checks) has each outcome. |
| A fresh session's red team of the result | Triaged in the [milestone record](docs/milestones/m1.md#outside-checks). |

## Not yet shown

- **That the workspace helps on real work.** The eval's traps were written by the same hand as the guidance, in a small invented scaffold, and nothing here has yet been used on a real project.
- **Any model but one, any agent tool but Claude Code for the eval.**
