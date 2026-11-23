---
kind: playbook
lane: qa
proof: unproven
prove-by: M10
last-reviewed: 2026-11-23
---

# Regression triage

How an agent sorts a regression run's failures into classes and files the bugs the person picks, for the agent asked to triage a run.

**In short:** use a fresh session, never the one that ran the suite. Re-check each failure once, sort it into one of seven classes, draft the bugs, and file only those the person picks.

This is a lane draft: QA lane. It has not been run on real work yet; M10 runs it, as [decision 0006](../decisions/0006-what-proven-means.md) says.

A fresh session sees the report, not the run's reasoning, so it does not inherit the runner's guesses. The run itself is [regression run](regression-run.md). This repository has no regression suite; an instance keeps its own.

## The seven classes

Each failure gets exactly one class. Read the rows top to bottom and take the first that fits with evidence.

| Class | When | What follows |
|---|---|---|
| Fixed upstream | It passes on re-check at a newer commit than the run's, and a ticket or commit since the run names the fix. | A note naming both commits. |
| Flaky | It passes on re-check, and nothing since the run names a fix. | A note in the report. |
| Environment | The environment caused it: a service down, missing data, an expired account. | A note for the person. No ticket. |
| Test defect | The case itself is wrong: a stale selector, a wrong step. | A fix to the case file. |
| Intended behavior | The product changed on purpose, and a ticket or spec says so. | A fix to the case file, naming that source. |
| Known and open | It fails on re-check, and an open ticket covers it. | The ticket key goes in the report. No new ticket. |
| New regression | It fails on re-check, and no row above fits. A closed ticket on a failing case lands here, never in "known". | A bug draft. |

Default: when unsure whether a row above fits, pick new regression. The person can drop its draft in step 6.

## Steps

1. **Check the session.** Input: the session's history. If this session ran the suite, stop and ask the person to start a fresh one. Output: a fresh session.
2. **Load the report set.** Input: the run folder the person names. Default: the newest folder in `docs/records/regression-runs/`. Read its three files, as the [regression run report template](../templates/regression-report.md) lays them out. Output: the failures, blocked cases and off-checkpoint notes.
3. **Claim the environment.** Input: the environment the report names. Re-check there. If it is shared, ask the person's yes first; with no yes, stop and report. Claim it if the instance has a way to. Output: the claim.
4. **Re-check each failure once.** Input: the failures. Run each case's steps once, on the account its fixture names, against the environment as it stands now. Record the commit it runs, as [regression run](regression-run.md#steps)'s step 3 says. Default: never rebuild or redeploy the environment to reach a newer commit without the person's yes. Output: pass or fail per failure, with the commit. Never re-check a case twice.
5. **Search and classify.** Input: the re-checks. Search for tickets on each failure, as the bug report template's [before you write](../templates/bug-ticket.md#before-you-write) says. Read a ticket you find as [tracker operations](tracker-operations.md#steps) says for reads. Classify each failure with [the seven classes](#the-seven-classes). An off-checkpoint note has no re-check: give it environment, test defect, intended behavior or new regression, or `none` when no row fits with evidence. Output: a class per failure and note.
6. **Draft and ask once.** Input: the new regressions. Draft each as a bug, to the [bug report template](../templates/bug-ticket.md). Show every draft in one message, as a multi-select, and ask which to file. Default: with more drafts than the question tool takes, ask once as a numbered list answered in text. Default: with no answer, file none; the drafts go in the report. Output: the drafts to file.
7. **File the picked ones.** Input: the picked drafts and their local evidence. File each with its evidence attached, as [tracker operations](tracker-operations.md#steps) says. With no tracker tool, it gives the person the text instead. Output: each ticket key, or the text.
8. **Write back.** Input: the keys and the classes. Add each ticket key and each class to the run's report. Fix each case file a test defect or an intended behavior names, inside the instance's case folder. Never loosen an expectation without a ticket or spec that states the new intent. A failing case never earns a [regression candidates ledger](../templates/regression-candidates.md#the-bar) row: its case exists. A note's bug may, once it meets the bar; then add a row to `docs/records/regression-candidates.md`, creating it from that template if it is missing. Default: when unsure it meets the bar, add none. Output: the changed files. They are committed as [procedure endings](../procedure-endings.md#the-commit) says.
9. **Clean up.** Input: the claim and the local evidence folder. Release the environment. Delete the run's bulky local evidence, such as screenshots and logs. First mark each deleted file's name in the report as "deleted after triage". Default: keep the evidence for a draft not yet filed, and say so in the report. Output: the environment free, and the evidence removed.
10. **Finish.** Input: everything above. The report gives the count per class, each ticket filed, each draft waiting, and each case file changed. End as [procedure endings](../procedure-endings.md) says.

Stop when the report is given. Every stop in steps 1 to 9 releases any claim first, then ends in that report with the reason.

## Rules

| Rule | Enforced by |
|---|---|
| Triage runs in a fresh session, never the one that ran the suite. | `prose` |
| Re-check each failure once, on its fixture's account, where the environment stands; never redeploy without the person's yes. | `prose` |
| Each failure gets exactly one of the seven classes. | `prose` |
| A closed ticket on a failing case is a new regression, never "known". | `prose` |
| Ask once which drafts to file; file only those, through tracker operations. | `prose` |
| Never loosen a case's expectation without a ticket or spec that states the new intent. | `prose` |
| Release the environment before the report, on every stop. | `prose` |
| Mark every claim in the report verified or inferred. | `eval:fix-a-bug` |
