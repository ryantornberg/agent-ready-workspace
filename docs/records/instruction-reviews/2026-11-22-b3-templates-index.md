---
kind: record
last-reviewed: 2026-11-22
covers: docs/templates/README.md
reviewed-at: f757aed, with the uncommitted change of the B3 builder
---

# Instruction review: docs/templates/README.md

This records the instruction review of the new templates index, for its author and for anyone choosing a template or record shape.

**In short:** 3 findings, none blocking: 1 contradiction, 2 trigger. The page claims every shape but omits the question log, its new kickoff prompt and decision records; two rows fire more narrowly than their templates; and nothing in `INDEX.md` routes here.

## Scope

In scope: the whole page, which is new. Read beside it: `AGENTS.md`, `INDEX.md`, `docs/playbooks/instruction-review.md`, `docs/procedure-endings.md`, `docs/layout.md`, `docs/reader-standard.md`, `docs/authoring.md`, B3's row and the 2026-11-22 entries naming B3 in the M3 plan, and its "Queued for slice Z" list. Read the opening and the "when" and "where" sections of every template it lists, and the sections it links on `docs/size-the-work.md`, `docs/adopt-the-workspace.md`, `docs/playbooks/decision-interview.md`, `docs/playbooks/adversarial-review.md`, `docs/playbooks/handoff.md` (with its diff), `docs/playbooks/review-orchestrator.md` (with its diff) and `docs/playbooks/instruction-review.md`. Also read `docs/playbooks/git-host-operations.md` ("Which writes need a yes"), `docs/extend-the-workspace.md`, `docs/records/README.md`, `docs/records/defects.md`, `docs/records/lessons.md` and `docs/question-log.md`. Ran `python3 ws.py check` (passes, with one warning on fix a bug's eval record).

## Findings

| # | Class | Where | Finding | Disposition |
|---|---|---|---|---|
| 1 | contradiction | Purpose line; "Record shapes a playbook defines" | Not blocking. The purpose says "Every shape this workspace asks you to copy", and the records README, changed in this batch, says "Every template and record shape is indexed in templates". Three shapes have no row. The question log is a record with its own row shape and, new in this batch, its kinds of gap. The kickoff prompt, also new in this batch on the question log, is a prompt a newcomer pastes into a new session. Decision records take "the shape of the newest record there", as extend the workspace and the decision interview say. A reader who trusts "every" stops looking here. Verified: read the question log's diff, the records README, and both pages on decision records. | fixed: rows added for the question-log row with its kinds of gap, the kickoff prompt and decision records; the section is renamed "Record shapes another page defines" |
| 2 | trigger | "Templates in this folder", the fresh-session prompt and defect register rows | Not blocking. Two rows fire more narrowly than their templates. The fresh-session prompt row says "A person asks for a prompt"; the template also applies "when a task needs a context of its own, such as one slice of a plan", and its own table routes a new session for a plan slice there. The defect register row says "a defect in passing that you are not fixing now"; the template also takes a review finding the author defers on their own change, which is not found in passing. Verified: read both templates' "When" sections. | fixed: both rows now name the wider trigger their templates give |
| 3 | trigger | The whole page | Not blocking. Nothing in `INDEX.md` routes to this page, or to the fix record, defect register and lessons log it lists. The contract says to look in `INDEX.md` before searching. Its Topics table routes only "Writing a plan for larger work" and the milestone record to templates. The M3 plan's "Queued for slice Z" list holds one B3 line, procedure endings' row. The stop rule does not count a missing `INDEX.md` row; it is recorded so the author can queue it. Verified: read `INDEX.md` and the queue. | queued for slice Z: an `INDEX.md` Topics row for this page; `INDEX.md` is hashed by the eval |

## Checked with no finding

- step: every link and anchor resolves (`ws.py check` passes). Each "Your copy goes" cell matches its template: the spec's `docs/records/specs/` name, the epic folder's `docs/plans/<epic-slug>/`, the milestone record's `docs/milestones/`, the hub and unit doc's open question, the fix record's folder, and the handoff note's keep mode in the changed handoff page. The table lists all twelve templates in the folder. Verified.
- enforcement: the page states no must or never, so it needs no rules table. Verified.
- placement: outward writes link [procedure endings](../../procedure-endings.md#outward-writes) rather than restating it. Each record shape a playbook defines links its playbook's section, so the shape is stated once. Verified.
- eval-case: an index asks no behavior beyond choosing a row. Verified.

## Re-check

A fresh session re-read the page on 2026-11-22, after the fix round.

| # | Verdict | Evidence |
|---|---|---|
| 1 | fixed | Rows for the question-log row, the kickoff prompt and decision records are added, and the section is "Record shapes another page defines". Their anchors resolve: `python3 ws.py check` passes. Verified. |
| 2 | fixed | Both rows now name the wider triggers their templates give. Verified, by reading. |
| 3 | queue upheld | `INDEX.md` is hashed by the eval, and a missing `INDEX.md` row does not count under the stop rule. The line is not yet in the plan's "Queued for slice Z" list, whose only B3 line is procedure endings' row. Verified. |

Broke:

- Not blocking. The hub and unit doc fixes made `docs/projects/<project>/` the default for unit pages, and the unit doc record's disposition says this index names it. The Unit doc row's "Your copy goes" still says "Not settled: the same open question". An agent routing from here gets no path, against the template it opens. Verified, by reading.

Missed:

- Not blocking. This is a reference page a reader goes to for a task, and the how-to index has no row for it. That index's first rule asks for one in the same commit as the page. Verified: `docs/how-tos.md` links two templates and never `templates/README.md`.

## Second fix round

The builder's second fix round, on 2026-11-23, under the maintainer's answer to Q35 in the workspace queue, recorded in the M3 plan. It first cut back: the rule that a review record or a kept handoff note is committed on main from a throwaway worktree is removed, a review round's record goes in the plan's "Results" or the pull request's description, and a kept handoff note waits for M4. Then it fixed the blocking items the re-check found. This page held no blocking break; the cut-back's shared rule swept it.

| Item | Disposition |
|---|---|
| The cut-back, swept: the handoff note and review record rows named `docs/records/handoffs/` and `docs/records/reviews/` | fixed: the handoff note row says keep mode waits for M4, and the review record row names the plan's "Results" or the pull request's description. |

## Second re-check

A fresh session re-read the page on 2026-11-23, after the second fix round.

It read the page whole, `git show 65a6f5c`, the records README, handoff's "Two modes", the review orchestrator's step 10, and the templates each row links.

| Item | Verdict | Evidence |
|---|---|---|
| The cut-back, swept: the handoff note and review record rows named `docs/records/handoffs/` and `docs/records/reviews/` | fixed | The Handoff note row says "Outside every repository", and that keep mode waits for M4, linking "two modes". The anchor resolves. The Review record row names the plan's "Results" or the pull request's description, as step 10 does. The records README lists four records that live elsewhere, the code review's record among them, and counts them right. Neither page names a removed folder. Verified: the three texts, `git grep`, and `python3 ws.py check`, which checks links. |

Broke: none.

Missed:

- Not blocking. The first re-check's two items are still open: the Unit doc row's "Not settled" against the template's `docs/projects/<project>/` default, and the how-to index's missing row. Neither has a row in "Second fix round", and this record has no "Known defects" section. Verified: the page and `docs/how-tos.md`.
