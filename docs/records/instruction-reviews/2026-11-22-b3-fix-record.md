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

## Second re-check

A fresh session re-read the page on 2026-11-23, after the second fix round.

It read the page whole, `git show 65a6f5c`, procedure endings, the contract, the review orchestrator, escape analysis, the pull request template, git-host operations and the M3 plan's B3 results and "Queued for slice Z" list. It ran git in a scratch repository with a local bare remote, under its own temp folder.

| Item | Verdict | Evidence |
|---|---|---|
| Broke, blocking: "Committing it" contradicts the orchestrator's commit of a review block on main | withdrawn-upheld | The skeleton has no "Reviews" section, and the filling bullet and the rules row about it are gone. "Committing it" sends a review round's record to the pull request's description. No page still names a fix record's review section. Verified: the page, and `git grep` for `"Reviews"`, "review section" and `records/reviews` across `docs/` outside plans and these records. |
| The commit after the push moves the tip past the reviewed one | fixed | "Committing it" points to the review orchestrator's step 2, which now counts as reviewed a tip whose only change since the reviewed commit is this record. Verified in the scratch repository: after a reviewed commit and a commit that changed only the record, `git merge-base --is-ancestor` exited 0, and `git diff --name-only REVIEWED TIP` listed only that file. That commit comes after the pull request opens, so git-host operations' tip check at creation is not hit here. Inferred, from the order "Committing it" gives. |
| Re-check item 5, not blocking: the slice Z lines are not in the plan's queue | not fixed | The lines are still not in "Queued for slice Z": its only B3 line is procedure endings' index row. B3's "Not done" carries them ("the queued slice Z lines, which join the queue when the pages merge"), so the queue is promised in the plan, not lost. Verified: the plan. |

Broke: none.

Missed: none.

## Revert (Q41)

The builder's revert, on 2026-11-23, under the maintainer's answer to Q41 in the workspace queue, recorded in the M3 plan. No third fix round was made. The page is new in B3, so main holds no copy: the revert removed the skeleton's "Escape analysis" section, its filling bullet, and the sentence in "Committing it" that pointed at the review orchestrator's step 2 clause. Where a review commits on a branch stays unsettled, for M4.

| Item | Disposition |
|---|---|
| Second fix round, the commit after the push moves the tip past the reviewed one: "Committing it" pointed at the review orchestrator's new step 2 clause | withdrawn by the revert: the clause is removed from the review orchestrator, so its sentence in "Committing it" is removed too. |
| The skeleton's "Escape analysis" section and its filling bullet | removed under Q41: escape analysis's step 9 is main's text again and writes no section here. |
| Second re-check, re-check item 5, not blocking: the slice Z lines are not in the plan's queue | queued for slice Z: the lines join "Queued for slice Z" in the commit that records B3's results, once these pages merge. |

## Re-check after the revert

A fresh session re-read the page on 2026-11-23, after the revert under Q41. It read the contract, the instruction review, procedure endings, the Q41 entry under "Changes after approval" in the M3 plan on `origin/main` (the branch does not hold that entry yet), `git diff HEAD` of the page, the review orchestrator, escape analysis, architecture review, git-host operations, the spec template, the templates index, the records README, the pull request template and the lessons log template. It searched `docs/`, `parts/` and `tests/` for the removed section, and ran `python3 ws.py check`, which exits 0 with only the known warning on fix a bug's eval record. Verified.

The page is new in B3, so `origin/main` holds no copy to compare. The revert's diff removes three things: the skeleton's "Escape analysis" section, its filling bullet, and the sentence in "Committing it" that pointed at the review orchestrator's step 2 clause. Nothing else changed. "Committing it" keeps B3's own rule that the record is committed on the fix's branch, which is not one of the three pages Q41 returns to main's wording. Verified: `git diff HEAD` and `git cat-file` on `origin/main`.

| Item | Verdict | Evidence |
|---|---|---|
| Second fix round, the commit after the push moves the tip past the reviewed one: "Committing it" pointed at the step 2 clause | upheld | The sentence is gone, and the review orchestrator's step 2 is main's text. Verified: both diffs. The tip still moves, under "Broke". |
| The skeleton's "Escape analysis" section and its filling bullet | upheld | The skeleton goes from "Where it stands" to "Report", no bullet names the section, and no page, part or test names it. Escape analysis's step 9 writes nothing here, and the spec template says only that each playbook says what it writes down. Verified: the page and the search. |
| Second re-check, re-check item 5, not blocking: the slice Z lines are not in the plan's queue | upheld | B3's results on `origin/main` carry "the queued slice Z lines, which join the queue when the pages merge" under "Not done", so the queue is promised on record. Verified: the plan. |

Broke:

- Not blocking. "Committing it" still makes a second commit on the fix's branch after the push, and nothing now says whether that tip needs a review. A later run of the review orchestrator finds the reviewed commit an ancestor and runs a delta round over the record alone. Git-host operations checks the tip only when the pull request is created, and that comes before this commit, so nothing is refused; it costs a round. Verified: the texts. Inferred: the order, from "Committing it".

Missed:

- Not blocking. Architecture review's step 9 still says "The fix record that will hold them for a bug fix is planned in slice B3 of M3". Once B3 merges, the fix record exists and holds no review, as "Committing it" says. Main's text was true on main; B3 makes it stale. Verified: a search of `docs/`.
- Not blocking. This record's "Revert (Q41)" paragraph says the page's commit wording "went back to main's text". The template is new in B3 and main holds no copy; the revert removed the section and the sentence above. The fault is in this record, not the page. Verified: `git cat-file` on `origin/main`.

## Known defects

The plan allows the page no further fix round, so the non-blocking items the re-check after the revert found stay here. The template has no `prove-by`, so each is for the docs audit unless another place is named.

- "Committing it" makes a second commit on the fix's branch after the push, and nothing says whether that tip needs a review. For M4, which settles where and when a review commits, as Q41 leaves it.
- Architecture review's step 9 still says the fix record that will hold its findings "is planned in slice B3 of M3". Once B3 merges, the fix record exists and holds no review. For M6, architecture review's `prove-by`, or the docs audit, whichever comes first.
- This record's "Revert (Q41)" paragraph first said the page went back to main's text; the page is new in B3. Corrected in the paragraph above.
