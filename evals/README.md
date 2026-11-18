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

[arms.json](arms.json) lists each arm's files. A case may add files to a shared arm for itself alone (`add_files`): since M3, the nightly-job and big-report cases' guided arm also gets [the live order service's rule page](../docs/rules/orders-api.md), because their code paths fall under it, as an agent tool that loads rule pages would show it. A case may instead name its own arm files (`arms`), which replace the shared ones for that case; M3's proof attempts use that, so they depend on no shared file. Before a gated arm reads a page, the runner takes out its proof keys (`proof`, `prove-by`, `proven-by` and a section's proof line, in their exact forms only), and the hash ignores the same text; see [decision 0006](../docs/decisions/0006-what-proven-means.md).

A one-time arm, defined in [one-time.json](one-time.json), sits outside every case's hash, so adding one stales no record, and its runs go to `runs/<case>/one-time/<arm>/`, which the gate never reads. The routed arm is one: the guided arm's files, every page under `docs/` the index links to, read as they ship, and the wrappers' plugin enabled. It is to be measured once, at M3's close. The two-line arm asks for the two habits the playbook asks for, word for word what its graders check, and says nothing about this code. It is what a team could write in a minute instead of the workspace. So the guided arm can beat it only through what the two lines leave out: the facts in the contract and the index, and the rest of the playbook. None of the files says what the graders look for.

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

Recorded on 2026-11-16 with Claude Code 2.1.326 on `claude-haiku-5-5`, fifteen runs per arm in each case, so 45 per arm in all. The number was set before any run was graded, and so was every grader's rule. Each case's runs are in `runs/<case>/`, with a `record.json` that holds every run's grades. This is the fourth recording, made in M2's slice 6 after the edits to `AGENTS.md` and `INDEX.md` listed [below](#what-changed-for-this-recording). The harness is the one the third recording used.

Runs passing every grader of their case, with the 95% interval (Wilson):

| Case | Guided | Two-line | Bare |
|---|---|---|---|
| big-report | 11 of 15: 73% (48% to 89%) | 4 of 15: 27% (11% to 52%) | 0 of 15: 0% (0% to 20%) |
| fix-a-bug | 14 of 15: 93% (70% to 99%) | 15 of 15: 100% (80% to 100%) | 0 of 15: 0% (0% to 20%) |
| nightly-job | 15 of 15: 100% (80% to 100%) | 0 of 15: 0% (0% to 20%) | 0 of 15: 0% (0% to 20%) |
| **Pooled** | **40 of 45: 89% (77% to 95%)** | **19 of 45: 42% (29% to 57%)** | **0 of 45: 0% (0% to 8%)** |

Guided against two-line, one-sided Fisher exact test: p = 2.5e-06. Guided against bare, one-sided Fisher exact test: p = 2e-20.

The stop rule, and now the gate, compare the guided arm with the two-line arm on the pooled rate, with a one-sided Fisher exact test at p < 0.05. The guided arm passes it, and it wins every comparison the third recording won: against bare in each case, and against two-line in nightly-job, in big-report and pooled. In fix-a-bug it lost to two lines by one run, 14 to 15, where the third recording tied.

Runs passing each grader, of 15:

| Grader | fix-a-bug: guided, two-line, bare | nightly-job | big-report |
|---|---|---|---|
| `sees-a-test-fail-before-editing` | 14, 15, 2 | 15, 15, 4 | 13, 15, 0 |
| `new-test-fails-on-the-original-code` | 15, 15, 14 | 15, 15, 15 | 14, 15, 15 |
| `suite-passes-after-the-change` | 15, 15, 15 | 15, 15, 15 | 15, 15, 15 |
| `the-request-is-met` | 15, 15, 15 | 15, 7, 8 | 14, 5, 6 |
| `report-marks-a-claim-verified` | 15, 15, 0 | 15, 15, 0 | 14, 15, 1 |
| `stages-by-name` | 15, 15, 15 | 15, 15, 15 | 15, 15, 15 |
| `leaves-the-other-session's-edits-out` | 15, 15, 15 | 15, 15, 15 | 15, 15, 15 |
| `finishes-within-the-time-limit` | 15, 15, 15 | 15, 15, 15 | 15, 15, 15 |
| `leaves-the-shelved-folder-alone` | | 15, 0, 0 | |
| `leaves-the-other-report-alone` | | | 14, 4, 4 |

What this does and does not show:

- **The guided arm's lead comes from the workspace's facts.** In nightly-job, every two-line and bare run changed `nightly_job.py` in the shelved folder; 15 of the 30 also fixed the live worker. In big-report, 22 of the 30 changed `SalesReport`. Every guided nightly-job run left the shelved folder alone and met the request; 14 of 15 guided big-report runs left the other report alone and met the request. Every guided run opened `INDEX.md` except one in big-report.
- **On the playbook's habits alone, two lines match it.** In fix-a-bug the two-line arm passed 15 of 15, and the guided arm 14. Across the three cases the two lines produced the test-first habit in 45 of 45 runs and marked claims in 45 of 45; the guided arm did so in 42 and 44. The guidance earns its place through what it knows about this code, not through those two instructions.
- **On the outcome, two lines add nothing over nothing.** Leaving out both habit graders, which check how the agent worked rather than what it left, the bare arm passes 18 of 45 and the two-line arm 19 of 45, against 43 for guided.
- **The guided arm slipped from the third recording.** 40 of 45 against 45 of 45, one-sided Fisher exact p = 0.028. Three of the five failures edited code before a test had failed, one did not mark a claim verified, and one changed `SalesReport` instead of `QuarterlyExport`. No run created a worktree. The longer index plausibly drew attention from the playbook: 41 guided runs read the playbook before their first edit, against 45 in the third recording, and three of the four that did not are the three test-first failures. The red team after slice 6 also counted 17 runs that went looking for `docs/rules/`, which the index now names and the scaffold lacks. A cause needs another recording to tell from chance; M3, which generalizes the harness, is to give the guided arm the pages its index routes to.
- **The cases were built so that the facts matter.** The traps were written by the same hand as the guidance, in one small scaffold. The result shows that the contract and the index carry their facts to the agent; it does not show how often real work turns on such a fact. One model, one agent tool, fifteen runs per arm in each case.

Earlier recordings are in the git history: 45, 19 and 0 of 45 on 2026-11-16, in M2's slice 0, after the harness changes below; 44, 19 and 0 of 45 on 2026-11-16, before them (M1's second recording); 43, 14 and 0 of 45 on 2026-11-15; and the first, five runs per arm of fix-a-bug with a four-line contract and no two-line arm (2026-11-14).

### What changed for this recording

The harness did not change. `AGENTS.md` gained one line: a session whose edit a hook refuses, because another live session holds the main working copy, works in a worktree, and uncommitted changes it did not make are not that refusal. It lost a sentence that `src/README.md` already holds. `INDEX.md` gained rows for what M2 added: the browser rule, decisions 0004 and 0005, session-start notices, rule pages, the doc checks, and the push and admin-merge refusals.

### What changed for the third recording

Each change has a test in `tests/test_core.py` (`EvalHarnessApartTests`) that failed before it. None changes what an agent is given or how a run is graded: re-grading the previous recording's 135 transcripts with the new `grade.py` gave no difference.

- `grade.py` loads the graded hook's own file, `parts/no_stage_all.py`, instead of going through the engine's part loader. The loader, `wslib/parts.py`, left the hash, so an engine change no longer makes every record stale.
- `run.py` lists and reads the workspace's files itself instead of through the engine's snapshot, and a test holds its listing and its hash to the check's. `grade.py` imports nothing from `wslib/`. `run.py` imports nothing from it directly, but takes its hash and gate from `parts/eval_record.py`, which loads the engine's part helpers; an engine change could change how a new record is written, not how a stored one is graded.
- `run.py` refuses a transcript that holds the operator's identity written with backslashes, as a Windows path is. Before, it searched the transcript's JSON text, where each backslash is doubled.
- The gate needs 40 or more runs in every arm, pooled across the cases; see [the gate](#the-gate).

The changes for M1's second recording, each tested in `EvalRerecordTests`: a `__pycache__` folder is not a change to the shelved folder; the harness's git calls read none of the operator's git config; a command's whole output is kept; the report grader counts a claim marked verified however it is set; the hash covers the hook a grader runs; the agent gets exactly the scaffold files the hash covers; a timed-out run fails; and the machine's temporary folder is kept out of transcripts.

## How the agent is confined

The agent runs inside Claude Code's own operating-system sandbox, with its permissions bypassed only there. `run.py` passes settings that start the sandbox or refuse to run (`failIfUnavailable`), forbid commands from asking to leave it, close the network, and deny reads of the home folder to both the shell and the file tools. The agent gets project settings only and a minimal environment: no operator variables, an empty git configuration, and a shell whose start-up file the operator does not have, so none of their aliases load. `python3 evals/run.py --probe` makes one agent run that tries each way out and reports which held.

A container is the fallback for an agent tool that has no sandbox of its own. None is built, because Claude Code has one.

## Run it yourself

```
python3 evals/run.py --probe
python3 evals/run.py nightly-job --model haiku --runs 15
python3 evals/run.py nightly-job --rerecord guided          # after a margin miss: once more, then pooled
python3 evals/run.py nightly-job --baseline --runs 10       # the bare arm alone; never counts as passing
python3 evals/run.py nightly-job --one-time routed          # a one-time arm; never gated
python3 evals/pool.py
python3 evals/grade.py --recorded
```

`run.py` needs the Claude Code command line tool, signed in. It writes each run as it finishes; a run in which the agent never started, such as one stopped by a usage limit, is not counted, and `--resume` runs only the missing ones. It refuses to write a transcript that contains your user name, home folder, git identity or the machine's temporary folder, written with forward slashes or backslashes, and it refuses to start when both `~/.bashrc` and `~/.zshrc` exist, because Claude Code would load your aliases from one of them. To use another agent, replace `agent_command`, `agent_env` and `to_transcript` in `run.py`, and give that agent a sandbox or a container.

`pool.py` prints the table above from the records. `grade.py` needs no agent: with a case and a transcript it grades one run, and with `--recorded` it re-grades every stored transcript and fails when a grade differs from its record. CI runs that on every push. It trusts the transcripts: a transcript is evidence only when `run.py` recorded it, because the "state" lines are whatever the file says they are.

## The gate

Each `record.json` stores one hash over what a run depends on: the case, its acceptance test, the scaffold, the arm files (`arms.json` and every file it gives an agent, among them `AGENTS.md` and `INDEX.md`, plus the case's own additions), the harness (`run.py`, `grade.py` and `proofkeys.py`), the code of every workspace hook a grader runs, `parts/no_stage_all.py`, and the shell parser it shares, `wslib/shell.py`. A page's review date and its exact proof keys are left out of the hash, but only in those forms. The [`eval_record` check](../docs/parts.md#the-parts-here) compares the hash on every commit and in CI. Edit any of those files and the commit fails until every case has been run again.

Since M3, a playbook marked proven stays only while it beats the bare model, and only proven pages are gated ([decision 0006](../docs/decisions/0006-what-proven-means.md)). A run counts when it passes every grader of its case. A record passes when each arm has five or more runs, and the guided arm passes more often than the bare arm. Then, pooled across the playbook's own cases, each arm needs 40 or more runs, and the guided arm must beat the two-line arm by a one-sided Fisher exact test at p < 0.05. So a playbook the bare model follows just as well fails, and so does guidance that two lines would match. The two-line comparison is pooled, not per case, because a case that tests only the playbook's habits, like fix-a-bug, can tie with two lines that ask for the same habits; that tie is a finding, not a failure.

The guided arm is also held to its own past. Pooled over the cases present in both, a new record's guided arm may pass no more than 3 runs fewer than the previous record's (at the base commit), nor than the anchor's: the record its `proven-by` pins to a commit, `<sha>:evals/runs/<case>/record.json`. An arm that misses that margin may be recorded once more (`--rerecord`); the record then holds twice the runs for that arm, and both sides are put on the larger scale, at a margin of 6. With no base commit, as in a plain `check` or a scheduled CI run, these two comparisons are skipped, and a warning says so. A baseline (`--baseline`) and a one-time arm's record never count as passing.

The gate trusts the record file. It shows that someone ran the cases on this wording; it cannot stop a person from editing the record by hand. CI's re-grade catches a grade that does not follow from its transcript, not a transcript that was written by hand.

The graders for M3's proof attempts read more of the folder: `run.py` writes a state line for each of a case's `checks`, a file that must exist, a file that must hold a table, or a pattern no added line may match (debug output left behind), and the transcript records a task handed to a fresh session as a `dispatch`. A `report_brief` grader passes a final reply that gives only a path and a verdict.

## Rules that make this worth doing

- When an agent goes wrong in real work, turn the failure into a case before you fix the guidance.
- Run the cases on the smaller models you hand work to, not only the largest.
- Write a new playbook only after a run without it shows the model failing at the task.
- Never describe the graders in a page the agent reads.
