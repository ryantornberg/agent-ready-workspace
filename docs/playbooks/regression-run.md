---
kind: playbook
lane: qa
proof: unproven
prove-by: M10
last-reviewed: 2026-11-23
---

# Regression run

How an agent runs a regression suite against one environment and writes the run's report set, for the agent asked to run the suite.

**In short:** run on the person's local environment unless they name a shared one. Check the cases, run them in three stages, and write the report set. File no ticket: a fresh session triages the run.

This is a lane draft: QA lane. It has not been run on real work yet; M10 runs it, as [decision 0006](../decisions/0006-what-proven-means.md) says.

## What exists today and what is planned

| Piece | State |
|---|---|
| A regression suite and its case files | None in this repository. An instance keeps its own, one case per file, shaped by the [regression case template](../templates/regression-case.md). |
| The case checker | Planned for M10. Until then, the agent checks each case by reading it. |
| A saved workflow for stage 2 | An instance may write one, as [saved workflows](../saved-workflows.md) says. This repository has none. |
| A way to claim a shared environment | The instance's own, if it has one. |

Commands marked with angle brackets, such as `<run the smoke cases>`, are placeholders. The instance fills each with its own tool. A placeholder with no filling in the instance is a stop: report it.

## Which page wins

| The request | Go to |
|---|---|
| Run the suite, or part of it | This page. |
| Sort a finished run's failures, or file tickets from them | [Regression triage](regression-triage.md), in a fresh session. |
| Fix one known bug | [Fix a bug](fix-a-bug.md). |

## Steps

1. **Pick the target.** Input: the request. Default: the person's local environment. Run against a shared environment only when the person names it; naming it is their yes. Output: the target. If the target does not answer, stop.
2. **Check the cases.** Input: the instance's case files. Read each against the [regression case template](../templates/regression-case.md). A case that does not fit it is excluded, with the gap logged. Output: the valid cases. If there are none, stop.
3. **Open the run.** Input: today's date. Make the run folder name with `python3 -c "import datetime; print(datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%d-r%H%M'))"`. The part after the date is the run id. Record the commit the target runs, for each repository the run covers. For a local build from `src/<repo>`, use `git -C src/<repo> rev-parse HEAD`. For a shared environment, use `<read the deployed commit>`. Output: the run id, the folder `docs/records/regression-runs/<YYYY-MM-DD>-<run-id>/`, the evidence folder the [report template](../templates/regression-report.md#where-copies-go) names, and the commits.
4. **Probe the tools.** Input: the target. Check what the environment and the session can do: sign in, reach the server log, open a browser as [browsers](../browsers.md) says. Note each missing ability. Default: a case that needs a missing ability is blocked, not failed. Output: the abilities, and the cases they block.
5. **Claim and anchor.** Input: the target. If the instance has a way to claim the environment, claim it. Default: with no such way, claim nothing and say so in the report. Note the server log's size with `<read the server log>`, and the time now; they mark where this run's log lines start. Default: with no server log, note only the time. Output: the claim, the log size and the start time.
6. **Select the cases.** Input: the request and the valid cases. Select by tier, area, priority or case id, as the request says. Default: every valid case. Log each exclusion with its reason. Output: the selected cases, grouped by automation mode. Each mode runs in its own stage, whatever its tier; inside a stage, smoke-tier cases run first.
7. **Stage 1: automated cases.** Input: the automated-mode cases. Run the smoke-tier ones with `<run the smoke cases>`, then the rest with `<run the full cases>`. Output: a verdict per case. Default: if most automated smoke cases fail, stop the run and report; the environment is likely down.
8. **Stage 2: agent cases.** Input: the agent-mode cases, grouped by area. Hand each area to one helper, strictly one after another, never in parallel. Each helper gets a written brief: the area's case files, the target, the excused-errors list, the evidence folder and the shape of its return. Its prompt starts with `Tier: worker`, as [orchestration](../orchestration.md#handing-work-off) says. For each case, the helper:
   - records the browser console and network traffic;
   - takes a screenshot at each checkpoint;
   - compares the errors it captured with the instance's one list of excused errors (default `regression/excused-errors.md`, the instance's choice). An error not on the list is an off-checkpoint note, not a failure. Default: with no list, no error is excused;
   - runs the case's sink checks, such as a database row or a log line;
   - gives a verdict: pass, fail, blocked or skipped, with its evidence;
   - notes anything odd it saw off a checkpoint.

   A helper never loosens an expectation to make a case pass. A case that seems wrong is still failed, with a note. Output: a verdict and evidence per case. A helper that fails is rerun once; then each case in its area is `blocked`, with the reason "helper failed twice".
9. **Stage 3: the person's checklist.** Input: the human-mode cases, such as those that need a real device. Write them as a checklist for the person, in the report. Each is `skipped` in the results, with the reason "device checklist". Output: the checklist. The agent runs none of them.
10. **Assemble the report set.** Input: the verdicts, the server log since the anchor, and the previous run's folder. Default: the previous run is the newest earlier folder on the same environment; with none, there is no previous run. With no server log, write "server log unavailable" under New server errors. Write the three files the [regression run report template](../templates/regression-report.md) names into the run folder. Compare this run's server-error signatures with the previous run's, and list the new ones. Read the tickets named by failing cases, as [tracker operations](tracker-operations.md#steps) says for reads, and list each closed ticket whose case still fails. Output: the report set.
11. **Keep evidence out.** Input: the report set. Keep evidence and personal data out of the run folder, as the report template's [where copies go](../templates/regression-report.md#where-copies-go) and [personal data](../templates/regression-report.md#personal-data) sections say. Output: a scrubbed report set.
12. **Release the environment.** Input: the claim from step 5. Release it. Output: the environment free.
13. **Finish.** Input: everything above. The report names the run folder, the counts per verdict, the new server errors, and the closed tickets whose case still fails. It recommends [regression triage](regression-triage.md) in a fresh session. The run folder is committed as [procedure endings](../procedure-endings.md#the-commit) says. End as [procedure endings](../procedure-endings.md) says.

Stop when the report is given. Every stop in steps 1 to 12 releases the environment first, then ends in that report with the reason.

## Rules

| Rule | Enforced by |
|---|---|
| Run against a shared environment only when the person names it. | `prose` |
| A case checker is planned for M10; until then, check each case by reading it against the template. | `prose` |
| Stage 2 runs one helper per area, strictly one after another. | `prose` |
| A helper handed off directly has a prompt that starts with its tier. | `handoff_tier#no tier named` |
| A saved workflow's helpers start with their tier too, as [saved workflows](../saved-workflows.md) says. | `prose` |
| Never loosen an expectation to make a case pass. | `prose` |
| Evidence and personal data stay out of the run folder, as the report template says. | `prose` |
| The agent runs no human-mode case. | `prose` |
| An error not on the excused list is a note, not a failure; with no list, none is excused. | `prose` |
| Release the environment before the report, on every stop. | `prose` |
| The run files no ticket; triage happens in a fresh session. | `prose` |
| Mark every claim in the report verified or inferred. | `eval:fix-a-bug` |
