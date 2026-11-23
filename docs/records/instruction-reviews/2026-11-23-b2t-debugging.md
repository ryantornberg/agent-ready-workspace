---
kind: record
last-reviewed: 2026-11-23
covers: docs/playbooks/debugging.md
reviewed-at: 18eccc5, with the uncommitted change of the B2t builder
---

# Instruction review: docs/playbooks/debugging.md

This records the instruction review of slice B2t's change to the debugging playbook, for the change's author. The change adds failed CI runs, flaky failures, procedure endings and a References section.

**In short:** 6 findings: 4 step, 1 contradiction, 1 trigger; 1 blocking. Step 1's `gh run view RUN --log-failed` never says what RUN is, and the link a session is given for a failed run makes the command fail. The flaky-failure path has no default run count, a confirmation test that passes by chance about a third of the time, and no rule for its regression test. The Rules table still asks for a repro that fails every run, and the purpose line now claims any failure.

## Scope

In scope: the changed text (the purpose line, the **In short** line, steps 1, 4, 7 and 8, the first row of "Halt and report", the new Rules row and the References section), and anything on the page or a linked page that the change contradicts or leaves stale. Read beside it: `AGENTS.md`, `CLAUDE.md`, `INDEX.md`, `docs/procedure-endings.md`, `docs/definition-of-done.md`, `docs/playbooks/fix-a-bug.md`, `docs/question-log.md`, and the pages the changed text links to: `docs/size-the-work.md`, `docs/playbooks/escape-analysis.md`. Also read the catalog row in `docs/playbooks/README.md`, `docs/templates/spec.md`, `docs/playbooks/prompt-retrospective.md`, `parts/ci_notice.py` and `README.md`'s rows on the CI notice. Ran `git diff fad9f23` on the page, `gh run view --help`, `gh run list --status failure -L 1`, `gh run view <id> --log-failed` with a run ID and with that run's URL, `python3 ws.py check` (no error on this page) and `python3 ws.py rules` (the new row is listed, tagged `prose`).

References: I could open the source. [Introduction to Debugging](https://www.debuggingbook.org/html/Intro_Debugging.html) loaded with WebFetch and with `curl`. Its section "The Scientific Method" lists the steps: invent a hypothesis, formulate a prediction that can support or refute it, test the prediction in an experiment, and "Repeat Steps 2–4 until there are no discrepancies", after which the hypothesis "may be named a theory". That is what the page credits it for, for steps 2 to 4. Verified.

## Findings

| # | Class | Where | Finding | Disposition |
|---|---|---|---|---|
| 1 | step | Steps, step 1 | Blocking. Step 1 names `gh run view RUN --log-failed` but never defines RUN or says where to get it. The command takes a numeric run ID. The link a session is given for a failed run, from the `ci_notice` session-start notice ("Newest run: <url>"), is a URL, and the command fails on it. Verified: `gh run view 45186436116 --log-failed` printed the failed step's log; `gh run view https://github.com/ryantornberg/agent-ready-workspace/actions/runs/45186436116 --log-failed` failed with `HTTP 404: Not Found`; `parts/ci_notice.py` prints the run's `url`. Also inferred, not run: for a CI run in a pinned code repository, `gh` called from the top of the workspace reads the workspace's own repository unless `-R OWNER/REPO` is given (the inherited `-R` flag in `gh run view --help`); this sample pins none. An agent that passes the link it was given runs a command that fails. | fixed: step 1 says RUN is the run's number, the last part of its URL, which `gh run list` also lists. |
| 2 | step | Steps, step 1; Halt and report, the first row | Not blocking. Step 1 runs a flaky failure "at least 20 times"; the halt row stops when it "does not fail once in 100 runs of the loop". No default says how many runs the loop takes between 20 and 100, or what to do when 20 runs show no failure. Nor does step 1 say how to tell a flaky failure from one it cannot reproduce when all three first runs pass. Verified by reading step 1 and the halt table. | fixed: step 1 runs the loop 20 times, then 100 when none fails, which the halt row's 100 matches. |
| 3 | step | Steps, step 4 | Not blocking. For a flaky failure, step 4 counts a pass as "no failure in as many runs as step 1 counted", and a fail as "its rate returns", which has no threshold: one failure, or the same count. At step 1's minimum of 20 runs and a measured rate of 1 in 20, a change with no effect still gives 20 clean runs about 36% of the time; at 1 in 10, about 12%. So step 4 can confirm a wrong cause, and the page's "never ship a fix for a cause you have not confirmed" rests on it. Verified: `0.95**20` is 0.358 and `0.9**20` is 0.122. Inferred: that runs fail independently at the measured rate. | fixed: a pass now needs no failure in 100 runs. |
| 4 | step | Steps, step 5 | Not blocking. Step 5 says the regression test "must fail on the code before the fix", and the definition of done asks for a test that "failed before the fix". The change adds flaky failures but leaves this step as it was. It does not say whether the kept test loops the command as step 1 did, or how many runs must fail before the fix. A one-run test for a 1-in-20 failure passes on the unfixed code 95% of the time. Verified by reading step 5 and the definition of done's list; the rate is arithmetic. | fixed: step 5 says a flaky failure's test fails at least once in step 1's loop on the code before the fix. |
| 5 | contradiction | Rules, the first row | Not blocking. The row still says "Build a repro that fails every run before you form any theory." The changed step 1 and **In short** line now accept a repro that fails at a measured rate for a flaky failure. The rule and the steps cannot both hold for a flaky failure, and the row does not label the exception. Verified by reading the row beside step 1 and the **In short** line. | fixed: the row says the repro shows the failure on demand, every run or at a measured rate. |
| 6 | trigger | The purpose line | Not blocking. The purpose line now says the page finds "the cause of any failure"; it dropped the earlier "whose cause is not yet known". Every page that routes here sends only a failure whose cause is unknown: size the work, in its ladder introduction and the gate table's "A bug whose cause is not known" row; escape analysis's table; the spec template; and the catalog row, whose paragraph sends a bug with a known reason to fix a bug. Read alone, the purpose line pulls in a failure whose cause is already known. Verified: those pages' lines found by grep for `debugging`. | fixed: the purpose line says the cause is unknown again. |

## Checked with no finding

- enforcement: the new Rules row is tagged `prose`, as the page's other procedural rows are, and `python3 ws.py rules` lists it; the report row keeps `eval:fix-a-bug`; the shelved-folder row's tag is unchanged.
- placement: step 8 links procedure endings for the report and the question-log entry instead of restating them, and labels its one exception, the uncommitted regression test of a cause-only run, as an exception to that page's commit step; fix a bug's step 5 commits the test on the fix path.
- eval-case: the page is marked `proof: unproven` with `prove-by: M4`, so the new flaky-failure and CI-run behavior needs no eval case yet.

## Re-check

A fresh session re-read the page on 2026-11-23 after B2t's fix round. It read the page whole, `git diff fad9f23` of it, the contract, procedure endings, changing the machinery's "Traps", maintain the workspace, fix a bug, the definition of done, the catalog row and size the work's routes in. It ran `gh run list --limit 5`, `gh run list --status failure -L 1`, `gh run view 45192296457 --log-failed`, `gh pr checks 44`, `gh run view` on a job number from that output, and `python3 ws.py check`, which exits 0 with only the known warning on fix a bug's eval record.

| # | Verdict | Evidence |
|---|---|---|
| 1 | upheld | Step 1 says RUN is the run's number, which `gh run list --limit 5` lists in its ID column, and the `ci_notice` link ends in that number. Verified: `gh run view 45192296457 --log-failed` printed the failed step's log and exited 0. For a link of another form the rule gives the wrong number, under "Broke". The inferred `-R` gap for a pinned repository stays as the first reading left it; this sample pins none. |
| 2 | fixed in part | The loop runs 20 times, then 100 when none fails, and the halt row's 100 matches. Verified: the text. The finding's last part stands: when all three first runs pass, step 1 does not say whether to treat the failure as flaky and loop, or to halt as not reproduced. Not blocking. |
| 3 | fixed in part | A pass now needs no failure in 100 runs. At a rate step 1's 20-run loop can measure, 1 in 20, a change with no effect gives 100 clean runs about 0.6% of the time. But a failure that shows only in the 100-run loop, at about 1 in 100, still gives 100 clean runs about 37% of the time, so step 4 can still confirm a wrong cause for it. Verified: `0.95**100` is 0.006 and `0.99**100` is 0.366. Inferred: that runs fail independently. Not blocking. |
| 4 | upheld | Step 5 says a flaky failure's test fails at least once in step 1's loop on the code before the fix, which meets the definition of done's "failed before the fix". Verified: both texts. |
| 5 | upheld | The Rules row says the repro shows the failure on demand, every run or at a measured rate, matching the **In short** line and step 1. Verified: the text. |
| 6 | upheld | The purpose line says "the unknown cause of a failure", matching size the work's gate row and ladder introduction, escape analysis's table and the catalog row. Verified: `grep -n -i debugging` on those pages. |

Broke:

- Blocking. Step 1's fix says RUN is "the last part of its URL". That holds for the `ci_notice` link, which ends `/runs/<number>`. The link `gh pr checks` prints, and a job's page on GitHub, end `/runs/<run>/job/<job>`, so the last part is the job's number, and the command fails. Verified: `gh pr checks 44` printed `.../actions/runs/45183926414/job/137724493197`, and `gh run view 137724493197 --log-failed` exited 1 with `HTTP 404: Not Found`. The catalog row sends reading a pull request's CI state to git-host operations, so a session that moves on to debugging is likely to hold such a link (inferred). Saying "the number after `/runs/` in its URL" settles it.

Missed:

- Not blocking. Step 7 has three paths: cause only, a fix that passes the gate, and a fix that does not ("Otherwise go to step 8, and let the work be sized"). Step 8's exception keeps the regression test uncommitted only for the first, and fix a bug commits it only on the second. On the third, procedure endings' commit and push apply, so the agent commits a test that fails on the code to a branch in the code's repository and, where it has a remote, pushes it with a draft pull request, before anyone has sized the fix. Inferred: from step 7, step 8 and procedure endings' "Where the commit goes" and push table. Naming the third path in step 8's exception settles it.

## Second fix round

The builder's second fix round, on 2026-11-23, under the maintainer's answer to Q42 in the workspace queue, recorded in the M3 plan. Procedure endings gained one rule, under "Off main": a procedure pushes nothing for pages when the branch checked out holds work other than its own pages, and the commits reach main with the branch's pull request. Its own review is in `2026-11-23-b2t-procedure-endings.md`. The non-blocking items of the re-check are not fixed in this round; each goes to "Known defects".

| Item | Disposition |
|---|---|
| Re-check, broke, blocking: step 1 takes RUN from the last part of a link, the job's number in a job link | fixed: step 1 takes the number right after `/runs/`, and says a job's link goes on past it. |
| Re-check, item 2, not blocking: when all three first runs pass, step 1 does not say whether to loop or halt | known defect, for M4. |
| Re-check, item 3, not blocking: a 1-in-100 failure gives 100 clean runs about 37% of the time | known defect, for M4. |
| Re-check, missed, not blocking: step 8's exception does not cover a fix that fails the gate | known defect, for M4. |

## Second re-check

A fresh driver-tier session re-checked the second fix round on 2026-11-23, narrowly. It read the contract, the instruction review's "The record", the M3 plan's Q42 entry and lane B's stop rule, and `git diff HEAD` of the page and its record. It ran `gh pr checks 45`, `gh run list --limit 5`, `gh run list --status failure -L 2`, `gh run view 45192296457 --json jobs,number,databaseId`, `gh run view 45192296457 --log-failed`, `gh run view 137753507639 --log-failed`, `gh run view 237 --log-failed` and `python3 ws.py check`, which exits 0 with only the known warning on fix a bug's eval record. It searched `docs/` outside records and plans for other wording of the run number; only git-host operations' "Read CI" row has one, and it already says the number after `/runs/`.

| Item | Verdict | Evidence |
|---|---|---|
| Re-check, broke, blocking: step 1 takes RUN from the last part of a link, the job's number in a job link | upheld | `gh pr checks 45` prints job links such as `.../actions/runs/45198559481/job/137775504831`. The failed run 45192296457's failed job link is `.../runs/45192296457/job/137753507639`. The number right after `/runs/` works: `gh run view 45192296457 --log-failed` printed the failed step's log and exited 0. The job's number does not: `gh run view 137753507639 --log-failed` failed with HTTP 404. `gh run list --limit 5` lists the same kind of number, such as 45202012668. Verified: the commands. |
| Re-check, item 2, not blocking: when all three first runs pass, step 1 does not say whether to loop or halt | upheld | Listed in "Known defects" for M4, the page's `prove-by`. Verified. |
| Re-check, item 3, not blocking: a 1-in-100 failure gives 100 clean runs about 37% of the time | upheld | Listed in "Known defects" for M4. Verified. |
| Re-check, missed, not blocking: step 8's exception does not cover a fix that fails the gate | upheld | Listed in "Known defects" for M4. Verified. |

Broke:

- none.

Missed:

- Not blocking. "The run's number" is another number in GitHub's own words. `gh run view 45192296457 --json number` prints `237`, the run's count in its workflow, which the Actions page shows as "#237", and `gh run view 237 --log-failed` fails with HTTP 404. The colon after it defines RUN as the number after `/runs/`, so a careful reader gets the right one. Verified: the commands. Inferred: that an agent takes "#237" from the page's title. "The run's ID", the column `gh run list` prints, would not collide.

## Known defects

The plan allows the page no further fix round, so the re-check's non-blocking items stay here.

- Re-check, item 2: when all three first runs pass, step 1 does not say whether to treat the failure as flaky and loop, or halt as not reproduced. For M4.
- Re-check, item 3: a failure that shows only in the 100-run loop, about 1 in 100, still gives 100 clean runs about 37% of the time, so step 4 can confirm a wrong cause for it. For M4.
- Re-check, missed: step 8's exception keeps the regression test uncommitted only on a cause-only run; on a fix that fails the gate, procedure endings commits and may push a failing test before the fix is sized. For M4.
- Second re-check, missed: "the run's number" collides with GitHub's own run number, such as `#237`, which `gh run view` refuses; the colon after it defines RUN correctly. "The run's ID" would not collide. For M4.
