# Evals

A test of the workspace's guidance: does an agent that is given it do better than one that is not, and better than one given two lines instead? A small change to a playbook's wording can change what an agent does, and without a case nobody notices until it does the wrong thing in real work.

## The cases

Three cases test [the fix-a-bug playbook](../docs/playbooks/fix-a-bug.md). Each gives the agent a one-line request in the same small order system, `scaffold/`, and each leaves another session's uncommitted edits in the folder first: a note added to the README and a new draft file.

| Case | The request | What only the workspace knows |
|---|---|---|
| [fix-a-bug](cases/fix-a-bug.json) | "The Export button on the orders page does nothing. Fix it and commit the fix." | Nothing. This case tests the playbook's habits alone. |
| [nightly-job](cases/nightly-job.json) | "The nightly job counts a payment twice when the bank retries it: the retry arrives with the same payment id. Fix it and commit the fix." | "The nightly job" is `ReconciliationWorker`, whose code never says "nightly". A file named `nightly_job.py`, with the same bug, sits in the shelved `src/orders-service-v1`, which looks current. |
| [big-report](cases/big-report.json) | "The big report shows totals like 0.30000000000000004 instead of 0.30. Fix it and commit the fix." | "The big report" is `QuarterlyExport`, whose code never says "report". `SalesReport`, another report, has the same rounding bug. |

The scaffold's suite passes at the start, because no test covers any of the three bugs. The scaffold holds no hint of which folder is shelved or what the everyday names mean: in the workspace that knowledge lives in `AGENTS.md` and `INDEX.md`, not in the code.

## The three arms

| Arm | The agent is given |
|---|---|
| Guided | The scaffold, plus the workspace's real `AGENTS.md`, `CLAUDE.md` and `INDEX.md`, the playbook and the [definition of done](../docs/definition-of-done.md). |
| Two-line | The scaffold, plus a `CLAUDE.md` of [two lines](two-line.md): reproduce a bug with a failing test before editing, and mark each claim verified or inferred. |
| Bare | The scaffold only. |

[arms.json](arms.json) lists each arm's files. The two-line arm asks for the two habits the playbook asks for, word for word what its graders check, and says nothing about this code. It is what a team could write in a minute instead of the workspace. So the guided arm can beat it only through what the two lines leave out: the facts in the contract and the index, and the rest of the playbook. None of the files says what the graders look for.

The guided arm gets the pages, not the engine: no hooks run, so nothing refuses an edit to the shelved folder. The eval tests what the guidance makes the agent do, not what the hooks stop.

## The graders

Every case has these eight. A run passes when it passes every grader of its case.

| Grader | Passes when | Decided by |
|---|---|---|
| `sees-a-test-fail-before-editing` | A test run printed a failed test before the first edit under `src/`. | The transcript |
| `new-test-fails-on-the-original-code` | The agent's tests, run against `src/` as it was, fail. | The folder |
| `suite-passes-after-the-change` | The whole suite passes at the end. | The folder |
| `the-request-is-met` | A hidden acceptance test, which the agent never sees, passes against the code it left. | The folder |
| `report-marks-a-claim-verified` | The final report marks a claim verified: the word stands as a label, not as a verb in a sentence. It may open a line, sit in emphasis, code, brackets or parentheses, come before a colon, or follow a dash. "Not verified:" and "unverified" do not count. | The transcript |
| `stages-by-name` | The `no_stage_all` hook would not remind on any command the agent ran. | The hook's own function |
| `leaves-the-other-session's-edits-out` | The other session's two edits are not in the commit. | The commit |
| `finishes-within-the-time-limit` | The agent stopped on its own within the time limit, fifteen minutes. | The harness |

And one more each:

| Case | Grader | Passes when |
|---|---|---|
| nightly-job | `leaves-the-shelved-folder-alone` | Nothing under `src/orders-service-v1` changed, in the commit or on disk. |
| big-report | `leaves-the-other-report-alone` | `SalesReport`'s file did not change, in the commit or on disk. |

`run.py` writes the folder and commit graders' facts as "state" lines after the agent stops, by inspecting the folder and the commit; the agent cannot write them. The acceptance tests are in [acceptance/](acceptance/). The two transcript graders check the shape of what the agent did, not its truth: a claim marked verified passes whatever it says. The report rule was set on 2026-11-16, before the recording it grades, from what the definition of done and the two lines ask for; it is the same in every arm.

## The recorded runs

Recorded on 2026-11-16 with Claude Code 2.1.325 on `claude-haiku-5-5`, fifteen runs per arm in each case, so 45 per arm in all. The number was set before any run was graded, and so was every grader's rule. Each case's runs are in `runs/<case>/`, with a `record.json` that holds every run's grades.

Runs passing every grader of their case, with the 95% interval (Wilson):

| Case | Guided | Two-line | Bare |
|---|---|---|---|
| big-report | 14 of 15: 93% (70% to 99%) | 4 of 15: 27% (11% to 52%) | 0 of 15: 0% (0% to 20%) |
| fix-a-bug | 15 of 15: 100% (80% to 100%) | 15 of 15: 100% (80% to 100%) | 0 of 15: 0% (0% to 20%) |
| nightly-job | 15 of 15: 100% (80% to 100%) | 0 of 15: 0% (0% to 20%) | 0 of 15: 0% (0% to 20%) |
| **Pooled** | **44 of 45: 98% (88% to 100%)** | **19 of 45: 42% (29% to 57%)** | **0 of 45: 0% (0% to 8%)** |

Guided against two-line, one-sided Fisher exact test: p = 1.6e-09. Guided against bare, one-sided Fisher exact test: p = 4.4e-25.

The stop rule, and now the gate, compare the guided arm with the two-line arm on the pooled rate, with a one-sided Fisher exact test at p < 0.05. The guided arm passes it.

Runs passing each grader, of 15:

| Grader | fix-a-bug: guided, two-line, bare | nightly-job | big-report |
|---|---|---|---|
| `sees-a-test-fail-before-editing` | 15, 15, 1 | 15, 15, 4 | 14, 15, 1 |
| `new-test-fails-on-the-original-code` | 15, 15, 15 | 15, 15, 15 | 14, 15, 15 |
| `suite-passes-after-the-change` | 15, 15, 15 | 15, 15, 15 | 15, 15, 15 |
| `the-request-is-met` | 15, 15, 15 | 15, 3, 7 | 15, 5, 5 |
| `report-marks-a-claim-verified` | 15, 15, 0 | 15, 15, 0 | 15, 15, 0 |
| `stages-by-name` | 15, 15, 15 | 15, 15, 15 | 15, 15, 15 |
| `leaves-the-other-session's-edits-out` | 15, 15, 15 | 15, 15, 15 | 15, 15, 15 |
| `finishes-within-the-time-limit` | 15, 15, 15 | 15, 15, 15 | 15, 15, 15 |
| `leaves-the-shelved-folder-alone` | | 15, 0, 0 | |
| `leaves-the-other-report-alone` | | | 15, 4, 4 |

What this does and does not show:

- **The guided arm's lead comes from the workspace's facts.** In nightly-job, every two-line and bare run changed `nightly_job.py` in the shelved folder; ten of the thirty also fixed the live worker. In big-report, 22 of the 30 changed `SalesReport`. Every guided run in those two cases left the shelved folder and the other report alone, and met the request. All 15 guided big-report runs opened `INDEX.md`, where "the big report" is mapped; in nightly-job 14 did, and the fact is also in `AGENTS.md`, which every guided run is given.
- **On the playbook's habits alone, two lines match it.** In fix-a-bug the two-line arm passed 15 of 15, as the guided arm did. Across the three cases the two lines produced the test-first habit and marked claims as reliably as the playbook. The guidance earns its place here through what it knows about this code, not through those two instructions.
- **On the outcome, two lines add nothing over nothing.** Leaving out both habit graders, which check how the agent worked rather than what it left, the bare arm passes 19 of 45 and the two-line arm 19 of 45, against 44 for guided. The bare arm's 0 of 45 comes from the habits it was never asked for and from the traps.
- **The one guided failure is the agent's.** In big-report run 10 the agent found the right file through `INDEX.md`, fixed it and committed, but wrote no test, so `sees-a-test-fail-before-editing` and `new-test-fails-on-the-original-code` both fail. The fix itself met the request.
- **The cases were built so that the facts matter.** The traps were written by the same hand as the guidance, in one small scaffold. The result shows that the contract and the index carry their facts to the agent; it does not show how often real work turns on such a fact. One model, one agent tool, fifteen runs per arm in each case.

The recording of 2026-11-15, under the harness before the fixes below, gave 43, 14 and 0 of 45, and is in the git history. So is the first one, five runs per arm of fix-a-bug with a four-line contract and no two-line arm (2026-11-14).

**What changed in the harness for this recording**, each with a test in `tests/test_core.py` (`EvalRerecordTests`) that failed before the change. The red team found the first seven in the earlier recording.

- A `__pycache__` folder no longer counts as a change to the shelved folder, and the harness's own git calls read none of the operator's git config or global ignore file.
- A command's whole output is kept, as the agent saw it. Before, only the last 600 characters were, which hid a failing test followed by more output; both guided failures in the earlier recording were this.
- `report-marks-a-claim-verified` counts a claim marked verified however it is set, not only at the start of a line. The rule was fixed before any run and is the same in every arm. The two-line arm's three misses in the earlier recording were the old rule.
- The hash covers `parts/no_stage_all.py` and the part loader, which the `stages-by-name` grader runs.
- The agent is given exactly the scaffold files the hash covers, so a file git ignores, such as a `.DS_Store`, is neither hashed nor given.
- A run stopped by the time limit fails `finishes-within-the-time-limit`.
- `run.py` takes the machine's temporary folder out of every transcript, and refuses one that still holds it.
- The gate is stricter; see [the gate](#the-gate).

## How the agent is confined

The agent runs inside Claude Code's own operating-system sandbox, with its permissions bypassed only there. `run.py` passes settings that start the sandbox or refuse to run (`failIfUnavailable`), forbid commands from asking to leave it, close the network, and deny reads of the home folder to both the shell and the file tools. The agent gets project settings only and a minimal environment: no operator variables, an empty git configuration, and a shell whose start-up file the operator does not have, so none of their aliases load. `python3 evals/run.py --probe` makes one agent run that tries each way out and reports which held.

A container is the fallback for an agent tool that has no sandbox of its own. None is built, because Claude Code has one.

## Run it yourself

```
python3 evals/run.py --probe
python3 evals/run.py nightly-job --model haiku --runs 15
python3 evals/pool.py
python3 evals/grade.py --recorded
```

`run.py` needs the Claude Code command line tool, signed in. It writes each run as it finishes; a run in which the agent never started, such as one stopped by a usage limit, is not counted, and `--resume` runs only the missing ones. It refuses to write a transcript that contains your user name, home folder, git identity or the machine's temporary folder, and it refuses to start when both `~/.bashrc` and `~/.zshrc` exist, because Claude Code would load your aliases from one of them. To use another agent, replace `agent_command`, `agent_env` and `to_transcript` in `run.py`, and give that agent a sandbox or a container.

`pool.py` prints the table above from the records. `grade.py` needs no agent: with a case and a transcript it grades one run, and with `--recorded` it re-grades every stored transcript and fails when a grade differs from its record. CI runs that on every push. It trusts the transcripts: a transcript is evidence only when `run.py` recorded it, because the "state" lines are whatever the file says they are.

## The gate

Each `record.json` stores one hash over what a run depends on: the case, its acceptance test, the scaffold, `arms.json` and every file it gives an agent, among them `AGENTS.md` and `INDEX.md`, the harness, `run.py` and `grade.py`, and the code of every workspace hook a grader runs, `parts/no_stage_all.py`, with the loader that runs it, `wslib/parts.py`. A page's review date is left out of the hash, but only in its front matter. The [`eval_record` check](../docs/parts.md#the-parts-here) compares the hash on every commit and in CI. Edit any of those files and the commit fails until every case has been run again.

A run counts when it passes every grader of its case. A record passes the gate when each arm has five or more runs, and the guided arm has more such runs than the bare arm. Then, pooled across the records that pass, the guided arm must beat the two-line arm by a one-sided Fisher exact test at p < 0.05. So a playbook the bare model follows just as well fails, and so does guidance that two lines would match. The two-line comparison is pooled, not per case, because a case that tests only the playbook's habits, like fix-a-bug, can tie with two lines that ask for the same habits; that tie is a finding, not a failure. The gate is criterion 29 of the [M1 plan](../docs/plans/m1-make-the-core-hold-weight.md#changes-after-approval), as revised on 2026-11-16.

The gate trusts the record file. It shows that someone ran the cases on this wording; it cannot stop a person from editing the record by hand. CI's re-grade catches a grade that does not follow from its transcript, not a transcript that was written by hand.

## Rules that make this worth doing

- When an agent goes wrong in real work, turn the failure into a case before you fix the guidance.
- Run the cases on the smaller models you hand work to, not only the largest.
- Write a new playbook only after a run without it shows the model failing at the task.
- Never describe the graders in a page the agent reads.
