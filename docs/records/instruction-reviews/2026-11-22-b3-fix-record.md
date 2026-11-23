---
kind: record
last-reviewed: 2026-11-22
covers: docs/templates/fix-record.md
reviewed-at: f757aed, with the uncommitted change of the B3 builder
---

# Instruction review: docs/templates/fix-record.md

This records the instruction review of the new fix record template, for its author and for agents writing a fix record.

**In short:** 6 findings, none blocking: 2 contradiction, 1 step, 1 trigger, 1 enforcement, 1 eval-case. The skeleton passes `claim_marks`, but the page describes the report's shape more loosely than the check reads it, cites escape analysis for a rule that page does not hold, and nothing on the fix path sends an agent here.

## Scope

In scope: the whole page, which is new. Read beside it: `AGENTS.md`, `INDEX.md`, `docs/playbooks/instruction-review.md`, `docs/procedure-endings.md`, `docs/layout.md`, `docs/reader-standard.md`, `docs/authoring.md`, B3's row and the 2026-11-22 entries naming B3 in the M3 plan, and its "Queued for slice Z" list. Read the pages it links: `docs/playbooks/fix-a-bug.md`, `docs/templates/hand-off-plan.md` ("How to use it"), `docs/playbooks/review-orchestrator.md` (and its diff), `docs/playbooks/escape-analysis.md`, `docs/definition-of-done.md` ("The report"), and beside them `docs/templates/spec.md`, `docs/records/README.md`, `docs/records/defects.md`, `docs/records/lessons.md` and `docs/question-log.md`. Read `parts/claim_marks.py`, its 9 cases, its `workspace.json` entry and its rows in `docs/parts.md` and the README. Ran `python3 ws.py check` (passes, with one warning on fix a bug's eval record) and `python3 ws.py rules`. Ran the check's `claim_lines` and `MARKED` on the skeleton and on variants of its report section. Listed each eval case's covered files with `evals/run.py`'s `covered()`.

## Findings

| # | Class | Where | Finding | Disposition |
|---|---|---|---|---|
| 1 | contradiction | "Filling it in", the escape analysis bullet | Not blocking. The page says an escape analysis "adds its own section before the report, as escape analysis says". Escape analysis does not say so. Its step 9 says the fix record is "planned in slice B3 of M3", and that until it exists a fix outside a plan has "the report is the only copy". The new spec template's "Which spec" lists escape analysis among playbooks that "write no record of their own; their report is the output". An agent running escape analysis follows its own page and writes no section here. Verified: read escape analysis step 9 and the spec template; `git status` shows escape analysis unchanged in this batch. | fixed: the template now has an "Escape analysis" section before the report, and escape analysis's step 9 writes the analysis there; the spec template's "Which spec" line is passed to its owner |
| 2 | contradiction | "Filling it in", the report bullet | Not blocking. The page says a claim line starts with `verified` or `inferred` "after an optional list marker and optional bold". The check is narrower: only a `- ` or `* ` marker, a lowercase mark, then a space, a colon or `**`. Run through the check's own functions, each of these fails: `1. verified: a`, `- Verified: b`, a claim wrapped onto a second line, a `### ` subheading inside the report, and a `Not done:` line followed by a bulleted list of items. A capitalized "Verified" is the form the definition of done's prose and the M3 plan's "Results" use, so a copied habit fails the commit. The page also says "Use the shape in the skeleton", while fix a bug's step 6 sends the agent to the definition of done's shape, a fenced block of `verified  <...>` lines; the check passes both (its case "the definition of done's block shape passes"), but the page does not say either is accepted. Verified: scratch runs of `claim_lines` and `MARKED`. | fixed: a new section, "What the check reads", states what `claim_marks` reads, names both accepted shapes and lists each form that fails |
| 3 | step | "When to write one"; "Filling it in", the report and "Committing it" bullets | Not blocking. The page does not say when, or on which branch, the record is committed. It is "opened when the fix starts and filled as it goes", and must name the fix's commits, its pull request, and, under "Not done", what procedure endings' report names: anything unpushed and any refusal. Those exist only after the commit and the push that procedure endings orders before the report, and procedure endings says a record "puts the same lines there". Nothing says whether the record is committed once or at each step, or whether a second commit follows the push. When the fix is code under `src/`, procedure endings puts the code on a branch of its own and a page change on main, and the page does not say which one the record rides. Verified: read both pages. Inferred: agents will pick different orders, and a record committed with the fix cannot name that commit or the later pull request. | fixed: "Committing it" says the record is committed with the fix on the fix's branch, then again after the push with the report filled, as procedure endings' order runs |
| 4 | enforcement | Rules table, first row | Not blocking. The row says "A fix record ends with a `## Report` section" and tags only `claim_marks#a claim line not marked verified or inferred fails`. That case shows the marking half. The missing-report half is shown by another case, "a fix record with no report section fails", which the row does not cite. "Ends with" is not checked at all: a scratch record with a `## Escape analysis` section after its report passes. Verified: read the cases and ran `claim_lines` on that record. | fixed: the row now cites both cases and says "has", and the report coming last is its own `prose` row |
| 5 | trigger | "When to write one" | Not blocking. Nothing on the fix path routes an agent here, so "One fix record per fix" never fires. The contract sends a small change to fix a bug, which does not mention a fix record. `INDEX.md` has no row for it. The M3 plan's "Queued for slice Z" list holds no edit to fix a bug or `INDEX.md` that would link it; its only B3 line is procedure endings' index row. The pages that do link it (the templates index, the records README, `docs/parts.md`, the README and the review orchestrator's step 10) are read only once an agent already looks for a record. Verified: a search for "fix record", "fix-record" and "records/fixes" across the Markdown files, and a read of the queue. | queued for slice Z: fix a bug's step 6 to link the fix record, and an `INDEX.md` Topics row; both files are hashed by the eval |
| 6 | eval-case | "When to write one"; Rules table, second row | Not blocking. The page asks new behavior of an agent on the proven fix a bug path: open, fill and commit one record per fix. No eval case covers it. `covered()` for `fix-a-bug`, `nightly-job` and `big-report` lists no template or record file, and no grader looks for a record. A template carries no `proof` key, by layout's page kinds table, so the page cannot be marked unproven with a `prove-by` milestone. Verified: ran `covered()` for the three cases. | declined: a template or reference page carries no proof key; the procedures that use it carry the proof state, as the plan sets the page kind |

## Checked with no finding

- placement: committing links [procedure endings](../../procedure-endings.md#the-commit) and "Not done" links its report section; no rule procedure endings states is restated. The review block's shape is left to the review orchestrator's step 10, as the page says. Verified.

Also checked, with no finding: every link resolves (`ws.py check` passes); the skeleton's report passes the check unchanged; the folder and file names match the records README, the check's default folder and its `docs/parts.md` row. Verified. The page is held as written mainly for agents, so the reader standard's worked example is not required. Inferred.

## Re-check

A fresh session re-read the page on 2026-11-22, after the fix round.

| # | Verdict | Evidence |
|---|---|---|
| 1 | fixed | The skeleton has an "Escape analysis" section before "Report", escape analysis's step 9 writes the analysis there, and the spec template's "Which spec" no longer says escape analysis writes no record. Verified: read the three pages and the diff of escape analysis. |
| 2 | fixed | "What the check reads" matches `parts/claim_marks.py`. Run through its `claim_lines` and `MARKED`, each listed failure fails and both shapes pass, as its cases show. Verified. |
| 3 | fixed as asked, but the fix broke a step: see Broke. | "Committing it" now names the fix's branch and a second commit after the push. Verified: read the page. |
| 4 | fixed | `python3 ws.py rules` shows the first row tagged with both `claim_marks` cases, and "the report is the record's last section" is its own `prose` row. Verified. |
| 5 | not fixed: the queue holds no line | The disposition says queued for slice Z, but the M3 plan's "Queued for slice Z" list holds no line for fix a bug's step 6 or an `INDEX.md` row on the fix record; its only B3 lines are the `AGENTS.md` tag and procedure endings' index row, and `git status` shows the plan unchanged. Verified. Not blocking. |
| 6 | decline upheld | Layout's page kinds table gives a template only `kind` and `last-reviewed`, so the page cannot carry `proof` or `prove-by`. The behavior reaches the proven fix a bug path only through slice Z's queued link, whose eval run covers it then. Verified for the table; inferred for slice Z. |

Broke:

- Blocking. "Committing it" contradicts the review orchestrator's new "Committing a record about a branch", written in the same round. This page commits the record with the fix on the fix's branch, and again on that branch after the push. The orchestrator's step 10 appends each review block to the fix record's "Reviews" and commits it on main, from a throwaway worktree of `origin/main`, "never on the branch it is about, so the branch's tip stays the one reviewed". A fix is reviewed before it merges, so `origin/main` holds no fix record yet. The block then lands in a new file with no `## Report`, which `claim_marks` refuses at the commit. On merge, both branches add the same file. This page's second commit after the push also moves the tip past the reviewed one, which sends the next review into a delta round. Verified: both pages' text; `claim_lines` returns None for a record holding only a "Reviews" section, which the check reports as a finding. Inferred: the merge conflict and the delta round.

Missed: none.

## Second fix round

The builder's second fix round, on 2026-11-23, under the maintainer's answer to Q35 in the workspace queue, recorded in the M3 plan. It first cut back: the rule that a review record or a kept handoff note is committed on main from a throwaway worktree is removed, a review round's record goes in the plan's "Results" or the pull request's description, and a kept handoff note waits for M4. Then it fixed the blocking items the re-check found.

| Item | Disposition |
|---|---|
| Broke, blocking: "Committing it" contradicts the orchestrator's commit of a review block on main | withdrawn by the cut-back: the skeleton's "Reviews" section, its filling bullet and its rules row are removed, and "Committing it" says a review round's record goes in the pull request's description. |
| The same item's inferred part: the commit after the push moves the tip past the reviewed one | fixed: the review orchestrator's step 2 now counts a tip whose only change since the reviewed commit is the fix record, or the plan, as reviewed, and "Committing it" says so. |
| Re-check item 5, not blocking: the slice Z lines were not in the plan's queue | queued for slice Z: the lines join the M3 plan's "Queued for slice Z" list in the commit that records B3's results, once these pages merge. |
