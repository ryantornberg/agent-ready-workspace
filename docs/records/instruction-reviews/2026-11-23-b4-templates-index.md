---
kind: record
last-reviewed: 2026-11-23
covers: docs/templates/README.md
reviewed-at: 1a18d68, with the uncommitted change of the B4 slice session
---

# Instruction review: docs/templates/README.md

This records the instruction review of slice B4's edit to the templates index, for its author and for critics.

**In short:** 1 finding: 1 contradiction, not blocking. Two new rows send copies into `docs/records/`, but the records index does not list either place, so the page's closing line is no longer true.

## Scope

In scope: the uncommitted edit, which adds the section "Lane templates" with its intro and four rows: regression case, regression run report, regression candidates ledger and QA test plan. Also in scope: anything on the page, or on a page it links to, that the change contradicts or leaves stale.

Read beside it: `AGENTS.md`, `INDEX.md`, `docs/layout.md`, `docs/authoring.md`, `docs/procedure-endings.md`, `docs/reader-standard.md`, `docs/extend-the-workspace.md`, `docs/records/README.md`, `docs/reading-paths.md`, the four new templates' openings and their "When" and "Where" sections, and the regression run, regression triage and QA verification list playbooks in full. Ran `git diff -- docs/templates/README.md`. Ran the run-folder command from regression run's step 3: it printed `2026-11-23-r1648`, which fits the row's `<YYYY-MM-DD>-<run-id>` folder. Ran `python3 ws.py check` at the start: it passed, with the known `eval_record` warning on `fix-a-bug.md`.

## Findings

| # | Class | Where | Finding | Disposition |
|---|---|---|---|---|
| 1 | contradiction | "Lane templates", the Regression run report and Regression candidates ledger rows, against the page's last line | Not blocking. The two rows send copies to `docs/records/regression-runs/<YYYY-MM-DD>-<run-id>/` and `docs/records/regression-candidates.md`. The page's last line says "Every records folder is listed in records". The records index's table lists neither place, and the change does not touch it. A reader who opens the records index to find a past run or the ledger does not find them. Verified: grep for "regression" in `docs/records/README.md` found nothing, and `git status` shows it unchanged. | fixed: the records index gains a row for `regression-runs/` and one for `regression-candidates.md`. |

## Checked with no finding

- step: the change adds no step. Every new link resolves; the `links` check reported nothing on this page. The run-folder command the report row's page relies on runs and prints a name of the row's shape.
- trigger: each row's "Use it when" matches its template's "When" section, and each "Your copy goes" cell matches its "Where" section: `regression/cases/<area>/<case-id>.md` as the instance's default, a run folder of three files, one ledger file, and the tracker's QA sub-task as an outward write. The QA test plan row and the playbook catalog's QA verification list row both fire on writing a test plan; the two pages say how they divide the work, layout against content, so they compose.
- enforcement: the new section states no must or never.
- placement: the section routes and links reading paths; it restates no template's rules.
- eval-case: the page is a reference, and lane templates carry no proof keys, as layout's controlled values say. No eval case or arm in `evals/arms.json` reads the page. Each row's "First used in" cell matches the milestone its template names: M10, M10, M10 and M6.

## Re-check

A fresh session's reading after the fix round, on `1a18d68` with the uncommitted fix of the B4 slice session. It read `git diff` of this page and `docs/records/README.md`, the regression run report and candidates templates' "Where" text, `ls docs/records`, and ran `python3 ws.py check`, which reports nothing on this page.

| # | Verdict | Evidence |
|---|---|---|
| 1 | upheld | Verified: the records index gains a row for `regression-runs/`, one folder per run named `<YYYY-MM-DD>-<run-id>/`, and one for `regression-candidates.md`, one file, each linking its template. The places match the two templates and this page's rows. Neither exists yet, which the records index's "A folder is created by the first record written into it" covers. |

What a fix broke:

- None.

What the first reading missed:

- None.
