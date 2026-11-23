---
kind: template
lane: qa
last-reviewed: 2026-11-23
---

# Regression run report template

The shape of the three files a regression run writes: the report, the results and the error signatures. For the run's writer and its triage session.

**In short:** each run gets one folder holding three files. The report is a record page a person reads. The results file holds each case's verdict, and the error-signature file lets the next run spot new server errors. Screenshots and logs stay outside the repository.

This is a lane draft: QA lane. It has not been run on real work yet; M10 first uses it on real work.

## When to use it

A [regression run](../playbooks/regression-run.md) writes these files as its report set. [Regression triage](../playbooks/regression-triage.md) reads them, then writes ticket keys back into the report.

## Where copies go

One folder per run: `docs/records/regression-runs/<YYYY-MM-DD>-<run-id>/`, holding `report.md`, `results.tsv` and `error-signatures.tsv`. The run commits them as [procedure endings](../procedure-endings.md#the-commit) says.

Evidence, such as screenshots, console and network captures and server log excerpts, stays on the runner's machine, outside every repository. The default folder is `~/regression-evidence/<YYYY-MM-DD>-<run-id>/`; an instance may name another. The report names evidence files by name only, so a reader asks the runner for them. This is a deliberate exception to the rule against pointing at a file on one machine. It keeps personal data out of the repository. The names hold until triage deletes the evidence and marks them. A filed ticket gets the evidence attached, never its name alone.

## Personal data

The committed files hold no personal data: no real names, email addresses, phone numbers, tokens or account ids of real people. Replace each with its role, such as `<customer>`. Test accounts named in a case's fixture may appear.

## The report: report.md

It is a record page, so it carries the front matter and opening [layout](../layout.md#page-kinds) gives a record. Keep every heading of this skeleton; write "none" under one with nothing in it. A failure block's bug headings are the one exception: drop those with nothing under them.

```markdown
---
kind: record
last-reviewed: <YYYY-MM-DD>
---

# Regression run <run-id>

The report of regression run <run-id> on <environment>, for the triage session and the person who asked for the run.

| Field | Value |
|---|---|
| Run id | <run-id> |
| Date | <YYYY-MM-DD> |
| Commit under test | <one `repository@40-character-commit` per repository, comma-separated> |
| Environment | <local, or the shared environment the person named> |
| Run by | <the person, or the session and its tier> |
| Previous run compared | <the previous run's folder, or none> |

## Summary

| Verdict | Cases |
|---|---|
| pass | <n> |
| fail | <n> |
| blocked | <n> |
| skipped | <n> |

## Failures

### <CASE-ID>: <the journey>

<One block per failed case. Use the bug report template's headings, in its order, at level ####, dropping any with nothing under it.>

Triage: <left empty by the run; triage writes the class and the ticket key>

## New server errors

## Blocked

## Skipped

## Off-checkpoint notes

## Closed but failing

## Device checklist

## Residue left
```

### Filling the report

- **Verdicts:** `pass`, `fail`, `blocked` or `skipped`. `blocked` means the case could not run, such as a fixture missing, the environment down or its helper failed twice. `skipped` means excluded at the case check or at selection, or a `human` case left for the device checklist, with the reason. The summary's counts match the results file.
- **Failures:** each block uses the [bug report template](bug-ticket.md#skeleton)'s headings, so triage can lift it into a draft ticket. Put the bug template's headings at level `####`, under the case heading. Leave out its summary line and its `<details>` wrapper. "How to reproduce" gives the case's steps up to the failed checkpoint. "Acceptance criteria" is that checkpoint. When a sink check failed and every checkpoint passed, "How to reproduce" gives every step and "Acceptance criteria" is that sink check. "Environment and version" names the commit under test. "Evidence" names the local files.
- **New server errors:** each signature in this run's error-signature file that the previous run's file lacks, with its count. The previous run is the newest earlier folder whose Environment matches this run's. With no previous run, write "no previous run; every signature is new" and list them.
- **Blocked and Skipped:** one line per case: its id and why.
- **Off-checkpoint notes:** what a run saw outside any checkpoint, such as a slow page or a console warning, with the case and step it happened in. Triage adds its class to each note.
- **Closed but failing:** each case whose source ticket is closed and that failed this run. Name the case and the ticket.
- **Device checklist:** the `human` cases, as checkboxes a person works through on a real device, with what to record. The person writes each result on its line; triage reads it there.
- **Residue left:** what the run left in the environment that its cleanup did not remove.

## The results file: results.tsv

Tab-separated, one header line, one line per case the run considered: each selected case, and each skipped one. A checkpoint list gives each checkpoint's step number and verdict. A case stops at its first failed checkpoint, so the list ends there; a skipped case's list is empty.

```text
case_id	verdict	checkpoints	note
HOLD-001	fail	1:pass 2:pass 3:fail	status stayed On hold after the lift
```

## The error-signature file: error-signatures.tsv

Tab-separated, one header line, one line per distinct server error. Normalize each message before counting. First replace timestamps with `<time>`. Then replace ids, such as GUIDs and long hex strings, with `<id>`. Then replace any remaining run of digits with `<n>`. Two errors that differ only in those values share a signature.

```text
signature	count	source
OrderShipping: no carrier for order <n>	3	server log
```

The example lines above are invented.

## Rules

| Rule | Enforced by |
|---|---|
| Screenshots and logs stay outside every repository; the report names them only by file name. | `prose` |
| The committed files hold no personal data of a real person. | `prose` |
| The report keeps every skeleton heading, with "none" under an empty one; a failure block drops its empty bug headings. | `prose` |
| A failure block uses the bug report template's headings in its order. | `prose` |
| The summary's counts match the results file. | `prose` |
