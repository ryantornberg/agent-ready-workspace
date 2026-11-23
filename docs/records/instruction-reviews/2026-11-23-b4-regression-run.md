---
kind: record
last-reviewed: 2026-11-23
covers: docs/playbooks/regression-run.md
reviewed-at: 1a18d68, with the uncommitted change of the B4 slice session
---

# Instruction review: docs/playbooks/regression-run.md

This records the instruction review of slice B4's new regression run playbook, a QA lane draft, for the change's author.

**In short:** 10 findings: 6 step, 2 enforcement, 1 contradiction, 1 placement; none blocking. The three stages split cases by mode and tier in a way that leaves automated full-tier cases in no stage. A helper rerun that fails and every human-mode case get no verdict the report template allows. The server log, the excused-errors list and the previous run have no default when missing. The commit under test is the workspace's pin, not what the environment runs.

## Scope

In scope: the whole page, which is new and untracked. Read beside it: `AGENTS.md`, `INDEX.md`, `docs/layout.md`, `docs/authoring.md`, `docs/procedure-endings.md`, `docs/reader-standard.md`, `docs/extend-the-workspace.md`, the instruction review playbook, and every page the page links to: decision 0006, the regression case template, the regression run report template, saved workflows, browsers, orchestration, tracker operations, fix a bug and regression triage. Also read the regression candidates and bug report templates, `src/README.md`, decision 0001, the catalog's "Lane drafts" section and diff, and the README and reading-paths rows that name the page.

Ran: step 3's `python3 -c` command, which printed `2026-11-23-r1648` (UTC; local time was 09:48 MST); `git -C src/orders-api rev-parse HEAD`, which printed `1a18d68...`, the workspace's own HEAD, since this sample checks the code in rather than pinning it; `python3 ws.py rules`, which lists the page's rows and the `handoff_tier#no tier named` case; `grep -n -i regress INDEX.md`, which finds nothing; and `python3 ws.py check`, which reports nothing on this page.

## Findings

| # | Class | Where | Finding | Disposition |
|---|---|---|---|---|
| 1 | step | Steps, steps 6 to 9 | Not blocking. Stage 1 takes "the automated smoke cases", stage 2 "the agent-mode cases" and stage 3 "the human-mode cases". The case template makes tier and mode independent fields. So a selected automated case of tier `full` runs in no stage, and nothing says so. A smoke case in agent mode, such as the template's worked example `HOLD-001` (tier smoke, mode agent), runs in stage 2, after the smoke gate of step 7 has passed. Verified: the case template's "Filling it in" and worked example, beside steps 7 to 9. | fixed: step 6 says each mode runs in its own stage whatever its tier, smoke-tier first; step 7 runs every automated case, smoke then full, and gates on the automated smoke cases. |
| 2 | contradiction | Steps, step 6 | Not blocking. The case template says "A `smoke` case runs on every run". Step 6 selects "by tier, area, priority or case id, as the request says", so a request for one area drops the other areas' smoke cases. Neither page labels this as an exception. Verified by reading both. | fixed: the case template's Tier bullet now says a smoke case runs on every run that selects by tier, and a run narrowed to an area or case id runs only what it names, which matches step 6. |
| 3 | step | Steps, steps 8 and 9 | Not blocking. Two kinds of selected case get no verdict the report template allows. Step 8 reports an area whose helper fails twice "as not run". Step 9 runs none of the human-mode cases. The template's verdicts are pass, fail, blocked and skipped. Its results file holds one line per selected case, and the summary's counts must match it. The page does not say which verdict, if any, those cases take. Verified: the report template's "Filling the report" and "The results file". | fixed: step 8 marks each case of an area whose helper failed twice `blocked`; step 9 marks each human-mode case `skipped` with the reason "device checklist"; the report template's verdicts name both. |
| 4 | step | Steps, step 8, the third bullet | Not blocking. The helper "compares the errors it captured" with the excused-errors list, but the page never says what an unexcused error does to the verdict: fail the case, or go to the off-checkpoint notes. Nor does it give a default when the list's file does not exist; this repository has no `regression/` folder. Verified: `ls regression` fails, and step 8's bullets name no outcome. | fixed: step 8 says an error not on the excused list is an off-checkpoint note, not a failure, and with no list no error is excused; a Rules row added. |
| 5 | step | Steps, steps 4, 5 and 10 | Not blocking. Step 5 notes "the server log's size", and step 10 reads "the server log since the anchor" and "the previous run's folder". No step says how to reach the server log: it is neither a command nor an angle-bracket placeholder, so the page's stop for an unfilled placeholder does not fire. Step 4 notes a missing ability, but steps 5 and 10 give no default for a run without the log. Nor does step 10 say which folder is "the previous run": the newest, or the newest on the same environment and tier. Verified by reading the steps and the report template's "New server errors". | fixed: step 5 reads the log with the placeholder `<read the server log>` and notes only the time without one; step 10 defaults the previous run to the newest earlier folder on the same environment and writes "server log unavailable" with no log. |
| 6 | step | Steps, step 3 | Not blocking. Step 3 records the commit under test with `git -C src/<repo> rev-parse HEAD`. In an instance that prints the submodule's pinned commit, as `src/README.md` and decision 0001 describe. The environment may run another build: a shared environment's deployment, or a local build of a branch. Triage's split between flaky and fixed upstream rests on this commit. Also, step 3 records one commit per repository, while the report template has one "Commit under test" row. Verified: the command prints the workspace's own HEAD here, `1a18d68`, as this sample pins nothing. Inferred: that a deployed build can differ from the pin. | fixed: step 3 records the commit the target runs: `git -C src/<repo> rev-parse HEAD` for a local build, `<read the deployed commit>` for a shared environment; the report template's field now holds one `repository@commit` per repository. |
| 7 | step | Steps, step 8 | Not blocking. A helper takes screenshots and captures console and network traffic, but its brief names no folder for them. The evidence folder first appears in step 11, after the files exist. The browser server writes its snapshots to `.playwright-mcp/` inside the folder it starts in, as browsers' "Things to know" says, which is inside the workspace though ignored. Verified: step 8's brief lists four items, none a folder. Inferred: where a helper saves a screenshot with no folder named. | fixed: step 3's output names the evidence folder from the report template, and step 8's brief passes it to each helper. |
| 8 | enforcement | Rules, the row on a helper's tier | Not blocking. The row tags `handoff_tier#no tier named` for every delegated helper. The page's table allows stage 2 to run through a saved workflow. Saved workflows' Rules row says "Whether the agent tool's handoff hook sees a workflow's dispatches depends on the tool", and tags it `prose`. For that path the tag claims enforcement that may not hold. Verified by reading both rows. | fixed: the row now covers a helper handed off directly; a new `prose` row covers a saved workflow's helpers, linking saved workflows. |
| 9 | enforcement | Steps, step 9; Rules | Not blocking. Step 9 says "The agent runs none of them" of the human-mode cases, a never. It has no row in the Rules table. Verified by reading the table. | fixed: added the Rules row "The agent runs no human-mode case." |
| 10 | placement | Rules, the rows on evidence and personal data | Not blocking. "Commit summaries only; screenshots and logs stay outside the repository" and "Remove personal data from every file in the run folder" restate rules the report template owns in its own Rules table. Step 11 links that template; the Rules rows restate instead of linking. The style guide's "One rule, one page" counts this as a placement finding. Verified by reading both Rules tables. | fixed: step 11 and its Rules row now link the report template's where copies go and personal data sections instead of restating them. |

## Checked with no finding

- trigger: the purpose line, the **In short** line and the catalog row all name running a suite against one environment and writing the report set. "Which page wins" routes sorting and filing to regression triage, and one known bug to fix a bug. `INDEX.md` has no row for the page; extend the workspace's step 5 queues an eval-covered row by default, so its absence is that queue, not this page's text.
- eval-case: the page is marked `proof: unproven` with `prove-by: M10`, and `workspace.json`'s `building` list holds only `M3`.

## Re-check

A fresh session's reading after the fix round, on `1a18d68` with the uncommitted change of the B4 slice session. Read the whole page, the contract, procedure endings, and each page the changed text links to: the report template's "Where copies go" and "Personal data", the case template, orchestration's "Handing work off", saved workflows and regression triage. Ran step 3's two commands: the `python3 -c` command printed `2026-11-23-r1657`, and `git -C src/orders-api rev-parse HEAD` printed a 40-character commit, `1a18d683...`.

| # | Verdict | Evidence |
|---|---|---|
| 1 | upheld | Verified: step 6 says each mode runs in its own stage, whatever its tier, smoke-tier first. Step 7 takes every automated case, smoke then full, and its stop default reads the automated smoke cases. An automated full-tier case now runs in stage 1, and `HOLD-001` runs first inside stage 2. |
| 2 | upheld | Verified: the case template's Tier bullet limits "every run" to a run that selects by tier, and says a narrowed run runs only what it names. That matches step 6. |
| 3 | upheld | Verified: step 8 marks each case of the area `blocked`, "helper failed twice". Step 9 marks each human-mode case `skipped`, "device checklist". The report template's Verdicts bullet names both. |
| 4 | upheld | Verified: step 8's third bullet makes an unexcused error an off-checkpoint note, and with no list excuses none. The Rules table has the row. |
| 5 | fixed in part | Verified: step 5 reads the log through `<read the server log>`. Step 10 defaults the previous run to the newest earlier folder on the same environment, as the report template does, and writes "server log unavailable" with no log. But the placeholder paragraph makes an unfilled placeholder a stop. So in an instance with no server log, the run stops at step 5 before its default "note only the time" applies. See "What a fix broke". |
| 6 | upheld | Verified: step 3 reads the commit the target runs, local or deployed. The report template's field holds one `repository@commit` per repository. The local command prints the 40-character commit the field asks for. |
| 7 | upheld | Verified: step 3's output names the evidence folder from the report template's "Where copies go", which gives `~/regression-evidence/<YYYY-MM-DD>-<run-id>/`. Step 8's brief passes it to each helper. |
| 8 | upheld | Verified: the tier row now covers a helper handed off directly. A `prose` row covers a saved workflow's helpers and links saved workflows, whose own row is `prose`. |
| 9 | upheld | Verified: the Rules row "The agent runs no human-mode case." is present. |
| 10 | upheld | Verified: step 11 links the template's two sections, and both anchors exist. Its Rules row defers to the template instead of restating it. |

What a fix broke:

- Not blocking. The placeholder paragraph under "What exists today and what is planned", against step 5. The paragraph says "A placeholder with no filling in the instance is a stop". Step 5's fix adds `<read the server log>` with "Default: with no server log, note only the time". In an instance with no server log, that placeholder has no filling, so the page says both stop and carry on. Verified by reading both.

What the first reading missed: none.

## Known defects

What stays open after the one fix round the plan allows, each not blocking.

- Not blocking, finding 5's open part and what its fix broke: the placeholder paragraph makes an unfilled placeholder a stop, while step 5 defaults to noting only the time when there is no server log. Known defect, for M10.
