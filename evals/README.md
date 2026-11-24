# Evals

A test of the workspace's guidance: does an agent that is given it do better than one that is not, and better than one given two lines instead? A small change to a playbook's wording can change what an agent does, and without a case nobody notices until it does the wrong thing in real work.

## The cases

Three cases test [the fix-a-bug playbook](../docs/playbooks/fix-a-bug.md). Each gives the agent a one-line request in the same small order system, `scaffold/`, and each leaves another session's uncommitted edits in the folder first: a note added to the README and a new draft file.

| Case | The request | What only the workspace knows |
|---|---|---|
| [fix-a-bug](cases/fix-a-bug.json) | "The Export button on the orders page does nothing. Fix it and commit the fix." | Nothing. This case tests the playbook's habits alone. |
| [nightly-job](cases/nightly-job.json) | "The nightly job counts a payment twice when the bank retries it: the retry arrives with the same payment id. Fix it and commit the fix." | "The nightly job" is `ReconciliationWorker`, whose code never says "nightly". A file named `nightly_job.py`, with the same bug, sits in the shelved `src/orders-service-v1`, which looks current. |
| [big-report](cases/big-report.json) | "The big report shows totals like 0.30000000000000004 instead of 0.30. Fix it and commit the fix." | "The big report" is `QuarterlyExport`, whose code never says "report". `SalesReport`, another report, has the same rounding bug. |

Since M3's slice Z, each request also ends "You have my approval for anything you would stop to ask me about in this fix.", so an unattended run does not halt on a gate of the fix path; each case file's `request_note` says why. The scaffold's suite passes at the start, because no test covers any of the three bugs. The scaffold holds no hint of which folder is shelved or what the everyday names mean: in the workspace that knowledge lives in `AGENTS.md` and `INDEX.md`, not in the code.

## The three arms

| Arm | The agent is given |
|---|---|
| Guided | The scaffold, plus the workspace's real `AGENTS.md`, `CLAUDE.md` and `INDEX.md`, the playbook and the [definition of done](../docs/definition-of-done.md). |
| Two-line | The scaffold, plus a `CLAUDE.md` of [two lines](two-line.md): reproduce a bug with a failing test before editing, and mark each claim verified or inferred. |
| Bare | The scaffold only. |

[arms.json](arms.json) lists each arm's files. A case may add files to a shared arm for itself alone (`add_files`): since M3, the nightly-job and big-report cases' guided arm also gets [the live order service's rule page](../docs/rules/orders-api.md), because their code paths fall under it, as an agent tool that loads rule pages would show it. A case may instead name its own arm files (`arms`), which replace the shared ones for that case; M3's proof attempts use that, so they depend on no shared file. Before a gated arm reads a page, the runner takes out its proof keys (`proof`, `prove-by`, `proven-by` and a section's proof line, in their exact forms only), and the hash ignores the same text; see [decision 0006](../docs/decisions/0006-what-proven-means.md).

A one-time arm, defined in [one-time.json](one-time.json), sits outside every case's hash, so adding one stales no record, and its runs go to `runs/<case>/one-time/<arm>/`, which the gate never reads. The routed arm is one: the guided arm's files, every page under `docs/` the index links to, read as they ship, and the wrappers' plugin enabled. It was measured once, at M3's close; see [the routed arm](#the-routed-arm-measured-once). The two-line arm asks for the two habits the playbook asks for, word for word what its graders check, and says nothing about this code. It is what a team could write in a minute instead of the workspace. So the guided arm can beat it only through what the two lines leave out: the facts in the contract and the index, and the rest of the playbook. None of the files says what the graders look for.

The guided arm gets the pages, not the engine: no hooks run, so nothing refuses an edit to the shelved folder. The eval tests what the guidance makes the agent do, not what the hooks stop.

## The graders

Each of the three fix-a-bug cases has these eight. A run passes when it passes every grader of its case. The proof attempts' cases have their own, under [the proof attempts](#the-proof-attempts).

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

Recorded on 2026-11-24 with Claude Code 2.1.331 on `claude-haiku-5-5`, fifteen runs per arm in each case, so 45 per arm in all. The number was set before any run was graded, and so was every grader's rule. Each case's runs are in `runs/<case>/`, with a `record.json` that holds every run's grades. This is the sixth recording, R2 of M3, made at M3's close after the changes listed [below](#what-changed-for-this-recording). No gated arm missed its margin, so none was recorded twice.

Runs passing every grader of their case, with the 95% interval (Wilson):

| Case | Guided | Two-line | Bare |
|---|---|---|---|
| big-report | 13 of 15: 87% (62% to 96%) | 3 of 15: 20% (7% to 45%) | 0 of 15: 0% (0% to 20%) |
| fix-a-bug | 14 of 15: 93% (70% to 99%) | 15 of 15: 100% (80% to 100%) | 0 of 15: 0% (0% to 20%) |
| nightly-job | 15 of 15: 100% (80% to 100%) | 0 of 15: 0% (0% to 20%) | 0 of 15: 0% (0% to 20%) |
| **Pooled** | **42 of 45: 93% (82% to 98%)** | **18 of 45: 40% (27% to 55%)** | **0 of 45: 0% (0% to 8%)** |

Guided against two-line, one-sided Fisher exact test: p = 3.8e-08. Guided against bare, one-sided Fisher exact test: p = 1.7e-22.

The gate passes: the guided arm beats bare in each case and two lines pooled. It is held to its past too: R1, the previous record, passed 41 of 45, and M2's closing recording, the anchor `fix-a-bug.md`'s `proven-by` names, 40; 42 is within 3 of both.

Runs passing each grader, of 15:

| Grader | fix-a-bug: guided, two-line, bare | nightly-job | big-report |
|---|---|---|---|
| `sees-a-test-fail-before-editing` | 15, 15, 1 | 15, 15, 5 | 15, 15, 1 |
| `new-test-fails-on-the-original-code` | 15, 15, 15 | 15, 15, 15 | 15, 15, 15 |
| `suite-passes-after-the-change` | 15, 15, 15 | 15, 15, 15 | 15, 15, 15 |
| `the-request-is-met` | 15, 15, 15 | 15, 6, 13 | 13, 4, 10 |
| `report-marks-a-claim-verified` | 14, 15, 0 | 15, 13, 0 | 15, 15, 0 |
| `stages-by-name` | 15, 15, 15 | 15, 15, 15 | 15, 15, 15 |
| `leaves-the-other-session's-edits-out` | 15, 15, 15 | 15, 15, 15 | 15, 15, 15 |
| `finishes-within-the-time-limit` | 15, 15, 15 | 15, 15, 15 | 15, 15, 15 |
| `leaves-the-shelved-folder-alone` | | 15, 0, 0 | |
| `leaves-the-other-report-alone` | | | 13, 3, 5 |

What this does and does not show:

- **The guided arm's lead still comes from the workspace's facts.** No two-line or bare nightly-job run left the shelved folder alone; every guided one did. In big-report, 13 of 15 guided runs left `SalesReport` alone and met the request; 3 two-line runs and 5 bare runs left it alone.
- **On the playbook's habits alone, two lines still match it.** In fix-a-bug, two lines passed 15 of 15 and the guided arm 14; the guided failure did not mark a claim verified.
- **The comparison with R1 is confounded.** Each case's request now grants any approval a gate of the fix path asks for, so an unattended run does not stop on it, and R2 ran that request, not R1's. The contract, the index, the definition of done and the playbook's gates section changed too. 42 of 45 against R1's 41 is no change, and it cannot say which change mattered.
- **The cases were built so that the facts matter.** The traps were written by the same hand as the guidance, in one small scaffold. One model, one agent tool, fifteen runs per arm in each case.

Earlier recordings are in the git history: 41, 18 and 0 of 45 on 2026-11-18, R1 of M3; 40, 19 and 0 of 45 on 2026-11-16, at M2's close; 45, 19 and 0 of 45 on 2026-11-16, in M2's slice 0; 44, 19 and 0 of 45 on 2026-11-16 (M1's second recording); 43, 14 and 0 of 45 on 2026-11-15; and the first, five runs per arm of fix-a-bug with a four-line contract and no two-line arm (2026-11-14).

### The routed arm, measured once

The routed arm asks whether shipping the unproven pages and the wrappers harms what is proven. It is the guided arm's files, every page under `docs/` that the index links to, and the wrappers' plugin enabled. It read those pages as they ship, unstripped, proof keys included. It was measured once, at M3's close, against R2's guided arm, in a record the gate never reads, and recorded once more after it missed its margin. Its runs are in `runs/<case>/one-time/routed-first/` and `runs/<case>/one-time/routed/`. `--rerecord` takes only the gated arms, and `--one-time` empties its arm's folder before it runs, so the first batch was moved to `routed-first/` by hand before the second ran, and the pooled count was worked by hand. `pool.py` reads gated records only, so it prints neither.

| Case | Routed, first 45 | Routed, once more | Routed, pooled |
|---|---|---|---|
| big-report | 10 of 15 | 10 of 15 | 20 of 30: 67% (49% to 81%) |
| fix-a-bug | 11 of 15 | 11 of 15 | 22 of 30: 73% (56% to 86%) |
| nightly-job | 15 of 15 | 12 of 15 | 27 of 30: 90% (74% to 97%) |
| **Pooled** | **36 of 45** | **33 of 45** | **69 of 90: 77% (67% to 84%)** |

**It fails.** R2's guided arm passed 42 of 45, 84 on the 90-run scale. Pooled, the routed arm needed 78 of 90, the guided count less a margin of 6, and passed 69. The first 45 runs alone missed too: 36, against 39. Routed against guided, one-sided Fisher exact test: p = 0.012. So the plan's stop rule fires, and the plan stops. A person decides whether the unproven pages' index rows, which slice Z adds, and the wrappers, already in the plugin on main, stay; slice Z is not merged until then.

- **Almost all of the loss is one habit.** 18 of the routed arm's 21 failed runs failed only `report-marks-a-claim-verified`, against 1 of the guided arm's 3. The facts held: every routed nightly-job run left the shelved folder alone, and 27 of 30 big-report runs left `SalesReport` alone, against 13 of 15 guided.
- **The extra pages send the agent into record keeping and branching** (counts verified, cause inferred). Of the 90 routed runs, 63 wrote a file under `docs/records/` and 55 made a branch; R2's guided runs did so 0 and 1 times. Of the 19 routed runs that failed the report grader, 15 wrote such a record. Most of their reports mark no claim at all; a few write one as prose, such as "Not verified:". The pages that ask for records and branches are the likely cause; no run has tested it.
- **A pass would not have proved there is no harm.** At M2's guided rate of 40 of 45, an arm that truly drops to 80% is caught about half the time, as the plan computed; at R2's 42 of 45, about three times in four.

### What changed for this recording

M3's slice Z. The harness: the agent gets a fixed `PATH` of system folders, and `run.py` refuses any account's home folder but the placeholder's, in the forms the run.py paragraph above lists. Each fix-a-bug case's request ends "You have my approval for anything you would stop to ask me about in this fix." The graded hook: the shell parser, `wslib/shell.py`, lists more command forms for the guards, and `parts/no_stage_all.py` names its page. The pages the guided arm reads: `AGENTS.md` links the request map and the reading paths, routes small work to its playbooks, lets a review read a pull request in a worktree, links the research ladder, names `python3 ws.py merge`, and tags the claim rule; `INDEX.md` gained a row for every M3 page, part and chain; the definition of done gained the record types' rows and the lessons' reasons; `fix-a-bug.md` gained the fix path's gates as a section marked unproven. Re-grading R1's 135 transcripts with today's `grade.py` gave no difference, by the review of this page.

### What changed for R1

M3's sub-batch A. The harness: per-case arm files and additions, one-time arms, the proof keys taken out of every page a gated arm reads (`proofkeys.py`, now hashed), new graders and state lines, `--baseline` and `--rerecord`, and the hash extended to `wslib/shell.py`, where the graded hook's parser moved. Re-grading the 135 transcripts of M2's closing recording with the new `grade.py` gave no difference. The guided arm: nightly-job and big-report also get `docs/rules/orders-api.md`. The pages it reads: `AGENTS.md` keeps its rules in a tagged table and no longer says `src/` holds one repository per folder; `INDEX.md` gained rows for the layout, the glossary and decision 0006, and a table of cross-cutting chains; `fix-a-bug.md`, the definition of done and the rule page gained the front matter and opening their kinds need.

### What changed for M2's closing recording

The harness did not change. `AGENTS.md` gained one line: a session whose edit a hook refuses, because another live session holds the main working copy, works in a worktree, and uncommitted changes it did not make are not that refusal. It lost a sentence that `src/README.md` already holds. `INDEX.md` gained rows for what M2 added: the browser rule, decisions 0004 and 0005, session-start notices, rule pages, the doc checks, and the push and admin-merge refusals.

### What changed for the third recording

Each change has a test in `tests/test_core.py` (`EvalHarnessApartTests`) that failed before it. None changes what an agent is given or how a run is graded: re-grading the previous recording's 135 transcripts with the new `grade.py` gave no difference.

- `grade.py` loads the graded hook's own file, `parts/no_stage_all.py`, instead of going through the engine's part loader. The loader, `wslib/parts.py`, left the hash, so an engine change no longer makes every record stale.
- `run.py` lists and reads the workspace's files itself instead of through the engine's snapshot, and a test holds its listing and its hash to the check's. `grade.py` imports nothing from `wslib/`. `run.py` imports nothing from it directly, but takes its hash and gate from `parts/eval_record.py`, which loads the engine's part helpers; an engine change could change how a new record is written, not how a stored one is graded.
- `run.py` refuses a transcript that holds the operator's identity written with backslashes, as a Windows path is. Before, it searched the transcript's JSON text, where each backslash is doubled.
- The gate needs 40 or more runs in every arm, pooled across the cases; see [the gate](#the-gate).

The changes for M1's second recording, each tested in `EvalRerecordTests`: a `__pycache__` folder is not a change to the shelved folder; the harness's git calls read none of the operator's git config; a command's whole output is kept; the report grader counts a claim marked verified however it is set; the hash covers the hook a grader runs; the agent gets exactly the scaffold files the hash covers; a timed-out run fails; and the machine's temporary folder is kept out of transcripts.

## The proof attempts

M3 tests two unproven playbooks, [debugging](../docs/playbooks/debugging.md) and [red team review](../docs/playbooks/red-team-review.md), with two cases each, drawn from M1's and M2's real work. Each case names its own arms, from `proof/<playbook>/`: the guided arm gets the playbook, a fixed copy of the contract text it needs, and for red team review a tier binding that names the small model; the two-line arm gets that playbook's [two](proof/debugging/two-line.md) [lines](proof/red-team-review/two-line.md); the bare arm gets the scaffold alone. So these cases depend on no shared arm file and no live page but their playbook. Each playbook has its own scaffold under `proof/<playbook>/scaffold/`.

| Case | The request | Drawn from |
|---|---|---|
| [debug-staging-reminder](cases/debug-staging-reminder.json) | The staging reminder fires on a commit with an attached message; find the cause, fix it and commit. | M1's slice 5, where the staging hook read `-m"add …"` as options |
| [debug-leak-check](cases/debug-leak-check.json) | The leak check misses a Windows home folder; find the cause, and leave the code as it is. | M2's slice 0, where the harness's leak check searched JSON text |
| [red-team-fail-closed](cases/red-team-fail-closed.json) | Write a plan's missing Verification section, then have the plan red-teamed and settle every finding. | M1's slice 1, hooks fail closed |
| [red-team-lease](cases/red-team-lease.json) | Write a plan's missing Recovery section, then have the plan red-teamed and settle every finding. | M2's slice 4, the writing-session lease |

These graders read more of the folder than the fix-a-bug ones. `run.py` writes a state line for each of a case's `checks`: a file that must exist, a file that must hold a table, or a pattern no line added under the code folder may match. The transcript records a task handed to a fresh session as a `dispatch`, and a `report_brief` grader passes a final reply of a few lines that gives a path and a verdict.

The debugging graders read what the playbook asks for: a failing test, a regression test that fails on the original code, and a report that marks its claims and names the causes ruled out. The fix case, debug-staging-reminder, also wants the change committed with no print or breakpoint among the lines it adds under `src/`; that check does not read `tests/` or a new file git does not track. The cause-only case, debug-leak-check, wants the code left exactly as it was, which leaves no room for debug output there, and nothing committed.

The red team graders read the protocol: a fresh session dispatched, the record where the playbook puts it, a short reply with its path and verdict, and the code left alone. Its hidden test also asks that a record names the false claim the plan rests on, and, unless a record's verdict is `does not hold`, that every finding is settled in the plan's Red team table. It does not check the record's headings or columns, so a win cannot come from format alone. Graded on its protocol, red team review stays thin by design, as its page says.

The guided arm gets the playbook and a contract copy, not the pages the playbook links to, such as procedure endings or fix a bug. Those links lead nowhere in the run, so the arm is tested on the playbook's own steps, and a dead link may cost it runs against two lines.

An attempt starts only when [the plan's B7 row](../docs/plans/m3-reading-layer-machinery-and-kit.md#sub-batch-b-the-reading-layer) allows it: the playbook's two-line text committed, its instruction review done, the maintainer's read of its batch recorded under the plan's Results, and the maintainer's yes to the run count. It opens with a bare-only baseline, 10 runs per case. If the bare model passes 8 or more of 10 in both cases, the page is cut; if 5 or fewer in either, the three arms are recorded at 22 runs per case; in between, the page stays unproven and the baseline is its failed attempt. Red team review's recording may instead be deferred to M9 by the plan's stop rule, which leaves the page unproven with its baseline run. No run is on record yet. `tests/test_m3_b7.py` runs each case through the harness without an agent: a run that does nothing fails, and one that does what the playbook asks passes every grader.

## How the agent is confined

The agent runs inside Claude Code's own operating-system sandbox, with its permissions bypassed only there. `run.py` passes settings that start the sandbox or refuse to run (`failIfUnavailable`), forbid commands from asking to leave it, close the network, and deny reads of the home folder to both the shell and the file tools. The agent gets project settings only and a minimal environment: no operator variables, a fixed `PATH` of system folders (`/usr/local/bin`, `/usr/bin`, `/bin`, `/usr/sbin`, `/sbin`) in place of the operator's, an empty git configuration, and a shell whose start-up file the operator does not have, so none of their aliases load. So the agent's `python3` and `git` are the system's, as R1's transcripts show they already were on the maintainer's Mac. `run.py` finds Claude Code itself on your own `PATH`, and refuses to start when `python3` or `git` is missing from the fixed one. A Claude Code installed by npm is a script that needs `node`, which the fixed `PATH` may not hold; use the native install. `python3 evals/run.py --probe` makes one agent run that tries each way out and reports which held.

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

`run.py` needs the Claude Code command line tool, signed in. It writes each run as it finishes; a run in which the agent never started, such as one stopped by a usage limit, is not counted, and `--resume` runs only the missing ones. It refuses to write a transcript that contains your user name, git identity, the machine's temporary folder or any account's home folder, such as `/Users/NAME`, `/home/NAME`, `C:\Users\NAME` or `C:\Documents and Settings\NAME`. Before it looks, it reads every run of backslashes as a slash, and `//` and `/./` as one slash, so `\home\NAME`, `C:/Users\NAME` and `/home/./NAME` count too. Only the placeholder `user`, which your user name becomes in a transcript, passes, with `Shared` and `Public`, which belong to no account. A folder's name is read whole, up to the next separator, quote or shell character, so a name that goes on past one of these, such as `user` followed by a letter outside ASCII, is refused. Those three pass only when a slash, a line break or the end of the text follows the name, so `C:\Users\User (2)` is refused, and so is `cd /home/user && ls`, which costs a run and leaks nothing. No case's own text makes a name pass: the debugging fixture's invented owner is refused too, so its stored transcripts are stale until M4 points the fixture at `/home/user`. It refuses to start when both `~/.bashrc` and `~/.zshrc` exist, because Claude Code would load your aliases from one of them. To use another agent, replace `agent_command`, `agent_env` and `to_transcript` in `run.py`, and give that agent a sandbox or a container.

`pool.py` prints the table above from the records. `grade.py` needs no agent: with a case and a transcript it grades one run, and with `--recorded` it re-grades every stored transcript and fails when a grade differs from its record. CI runs that on every push. It trusts the transcripts: a transcript is evidence only when `run.py` recorded it, because the "state" lines are whatever the file says they are.

## The gate

Each `record.json` stores one hash over what a run depends on: the case, its acceptance test, the scaffold, the arm files (`arms.json` and every file it gives an agent, among them `AGENTS.md` and `INDEX.md`, plus the case's own additions; or, for a case that names its own arms, those files alone), the harness (`run.py`, `grade.py` and `proofkeys.py`), the code of every workspace hook a grader runs, `parts/no_stage_all.py`, and the shell parser it shares, `wslib/shell.py`. A page's review date and its exact proof keys are left out of the hash, but only in those forms. The [`eval_record` check](../docs/parts.md#the-parts-here) compares the hash on every commit and in CI. Edit any of those files and the commit fails until every case has been run again.

Since M3, a playbook marked proven stays only while it beats the bare model, and only proven pages are gated ([decision 0006](../docs/decisions/0006-what-proven-means.md)). A run counts when it passes every grader of its case. A record passes when each arm has five or more runs, and the guided arm passes more often than the bare arm. Then, pooled across the playbook's own cases, each arm needs 40 or more runs, and the guided arm must beat the two-line arm by a one-sided Fisher exact test at p < 0.05. So a playbook the bare model follows just as well fails, and so does guidance that two lines would match. The two-line comparison is pooled, not per case, because a case that tests only the playbook's habits, like fix-a-bug, can tie with two lines that ask for the same habits; that tie is a finding, not a failure.

The guided arm is also held to its own past. Pooled over the cases present in both, a new record's guided arm may pass no more than 3 runs fewer than the previous record's (at the base commit), nor than the anchor's: the record its `proven-by` pins to a commit, `<sha>:evals/runs/<case>/record.json`. An arm that misses that margin may be recorded once more (`--rerecord`); the record then holds twice the runs for that arm, and both sides are put on the larger scale, at a margin of 6. With no base commit, as in a plain `check` or a scheduled CI run, these two comparisons are skipped, and a warning says so. A baseline (`--baseline`) and a one-time arm's record never count as passing.

The gate trusts the record file. It shows that someone ran the cases on this wording; it cannot stop a person from editing the record by hand. CI's re-grade catches a grade that does not follow from its transcript, not a transcript that was written by hand.

## The wrappers' selection cases

Each [wrapper](../docs/playbooks/README.md#three-ways-to-follow-a-playbook) has two or more selection cases: a request that should fire it, and a nearby request, one a wrapper next to it owns, that should leave it quiet. They test only whether the right wrapper loads, not what the agent then does. They sit with the plugin, one folder per case in `plugin/evals/`, in the format `claude plugin eval` reads. `prompt.md` holds the request and its settings: three runs of at most three turns each. `graders/selected.md` is a `tool_used` grader on the Skill tool, whose `input_match` names the plugin and the one wrapper, as `'"skill"\s*:\s*"workspace:<name>"'`. A case that fires sets `min: 1` and no `max`; a quiet one sets `min: 0`, `max: 0` and `arm: both`. To add a pair, copy an existing one and change the request and the name. The `wrappers` check fails a wrapper that lacks either kind, and a Skill grader in any other form; it does not read a grader of another type.

This is the format M4's eval system adopts for selection cases, so M4 builds on these cases rather than replacing them.

A run costs real agent time, so it runs in batches, and each batch needs the maintainer's yes with a run count. A batch's count is its cases times their runs: all 58 cases at three runs each are 174. A rerun after a rewrite is a new batch with its own yes. An agent with that yes runs the batch itself, and adds `--trust-plugin`: in a folder not yet trusted, `claude plugin eval` otherwise asks for a confirmation, and with no terminal to answer it the command exits 1. The agent stops before it would pass the count, and narrows a batch with `--case` or `--runs` to stay under it. No check holds the yes or the count; they rest on the agent's word. A person at a terminal may leave `--trust-plugin` out and answer the question there. Run them from the top of the workspace, on the small model the recordings use. Leave out the run without the plugin, since a case that fires cannot pass there.

```
claude plugin eval plugin --model haiku --ablation none --no-publish --trust-plugin --output-dir evals/selection/YYYY-MM-DD
```

Its results go to `evals/selection/YYYY-MM-DD/aggregate-result.json`. Commit that file and nothing else from the run. Before you commit it, search it for your user name, your home folder and your git identity, as `run.py` does for its transcripts, and replace each with a placeholder; the commit check's secret and deny-list scans read it as they read any file. A wrapper that fails its case that fires in most of its runs is rewritten once, and the result is recorded either way.

## Rules that make this worth doing

- When an agent goes wrong in real work, turn the failure into a case before you fix the guidance. A guidance fix with no case to replay the failure has nothing to catch the failure's return. Until procedures have an eval system, planned for M4, [escape analysis](../docs/playbooks/escape-analysis.md) describes such a case in its report instead.
- Run the cases on the smaller models you hand work to, not only the largest.
- Write a new playbook only after a run without it shows the model failing at the task.
- Never describe the graders in a page the agent reads.
