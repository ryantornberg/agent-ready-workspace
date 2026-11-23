---
kind: record
last-reviewed: 2026-11-22
covers: docs/templates/epic-folder.md
reviewed-at: f757aed, with the uncommitted change of the B3 builder
---

# Instruction review: docs/templates/epic-folder.md

This records the instruction review of the new epic folder template, for its author and for agents planning work large enough for an epic.

**In short:** 5 findings, 2 of them blocking: 1 step, 2 contradiction, 1 trigger, 1 placement. The blocking two are in the move into a folder: recording only the moved path leaves the deleted one out of the edit ledger, so the commit is refused; and fixing the links of an approved plan edits sections the template freezes.

## Scope

In scope: the whole page, as a new template.

Read beside it: `AGENTS.md`, `INDEX.md`, `docs/playbooks/instruction-review.md`, `docs/procedure-endings.md`, `docs/layout.md`, `docs/reader-standard.md`, `docs/authoring.md`, `docs/templates/hand-off-plan.md` and its diff, `docs/templates/hub.md`, `docs/templates/spec.md`, `docs/templates/README.md`, `docs/records/README.md`, `docs/size-the-work.md`, `docs/question-log.md`, decision 0005, `parts/page_kinds.py` and its cases, `parts/in_short.py`, `parts/plan_budgets.py` and its cases, `parts/edit_ledger.py` and its cases, the `review_trailer` entry of `workspace.json`, the M2 plan's links, and the M3 plan's B3 row, its results and its 2026-11-22 entries. Ran `python3 ws.py check` in the worktree (exit 0, one unrelated `eval_record` warning; links resolve), `python3 ws.py rules`, and a search for pages that link this one.

## Findings

| # | Class | Where | Finding | Disposition |
|---|---|---|---|---|
| 1 | step | "Where it lives and how it is named", the paragraph on crossing the threshold | Blocking. "Move the plan into it with `git mv`. Record the moved path in the edit ledger." `git mv` stages two paths: the new one and the deletion of the old one. The commit check counts a staged deletion: `edit_ledger`'s case "a staged deletion counts" fails a commit whose ledger lacks the deleted path. An agent that records "the moved path", the new one, runs a commit that is refused. The step should name both paths. Verified: the case and `edit_ledger.py`. | fixed: the move step now records both paths with `python3 ws.py ledger --add OLD NEW`, and a rules row cites `edit_ledger#a staged deletion counts`. |
| 2 | contradiction | "Where it lives and how it is named", the paragraph on crossing the threshold | Blocking. The step moves "the plan" one folder down and says to "fix each link the links check reports", with no limit on the plan's status. Plans link with relative paths, such as `../templates/hand-off-plan.md` in the M2 plan, so every link in the moved plan breaks. When the plan is approved, fixing them edits sections the hand-off plan template freezes: its rule 6 and its rules row "An approved plan changes only by a dated entry under 'Changes after approval' and by reports under 'Results'". Links to it from other approved plans and signed-off records are frozen too. Leaving them fails the links check at the commit. The M3 plan already keeps a records folder in place "since approved plans link there and are frozen". Verified: the rule texts and the M2 plan's links. | fixed: only a draft plan moves, and only when no frozen page links it; an approved, done or abandoned plan stays put and the hub lists it under "Docs elsewhere". |
| 3 | trigger | "When to use it" | Not blocking. The rule "its plans go in one folder" fires only for a reader who opens this page, and only the templates index links it. The pages a plan writer follows send every plan to the top level: the hand-off plan template's step 1 ("Copy the skeleton below into `docs/plans/<name>.md`") and size-the-work's feature ladder, step 1. The hand-off plan's change in this batch links the spec template but not this one. Verified: a search finds links to this page only from `docs/templates/README.md`, `docs/templates/hub.md` and the M3 plan. | fixed: the hand-off plan template's step 1 now links this page's "When to use it" for plans that belong in an epic folder. |
| 4 | contradiction | "Skeleton"; "Filling it in" | Not blocking. The epic hub is a page a person reads to learn where the work stands, like the project hub the reader standard names. The standard asks the template for "one worked example" and for its copies' top layer and budget. The page gives no filled-in hub, and the **In short** placeholder has no word budget. It does say empty sections keep "none", which meets that rule. Verified: the page holds no example. Inferred: that the standard binds the epic hub, since it names only the project hub. | fixed: the reader standard now names the templates it binds, and this one is not among them. |
| 5 | placement | "When to use it", the third paragraph | Not blocking. "Two other shapes were tried and rejected: a subfolder for each page kind inside the epic, and one shared questions page for every epic." This narrates how the page came about, which the style guide sends to a record. The live reason is already in the next section: the page-kind check allows only plans in the folder. Verified: the style guide's "Writing" list. | fixed: the sentence on the two rejected shapes is removed; the live reason stays in the next section. |

## Checked with no finding

- enforcement: the rules row "Every page in an epic folder other than its `README.md` is a plan" is tagged `page_kinds#a page in a kind's folder must be of that kind`, and `page_kinds.py` holds every non-README page under `docs/plans/`, subfolders included, to `kind: plan`. `plan_budgets` reads subfolders ("a draft in a subfolder is read") and skips the hub ("a page that is not a plan is skipped"); `in_short` skips a README. The other three rows are `prose`, which is true. Verified.
- eval-case: no eval case covers the template (`covered()` lists none). Planning runs under size-the-work's feature ladder, unproven with `prove-by: M9`. Verified.

## Re-check

A fresh session re-read the page on 2026-11-22, after the fix round.

| # | Verdict | Evidence |
|---|---|---|
| 1 | fixed | In a scratch clone at f757aed, `git mv docs/plans/decision-queue.md docs/plans/epic-x/decision-queue.md` with only the new path recorded made `python3 ws.py check --staged` refuse the old path under `edit_ledger`. After `python3 ws.py ledger --add OLD NEW`, the `edit_ledger` error was gone. Only `links` errors on the moved plan's relative links remained, which the step says to fix. Verified. |
| 2 | fixed | Only a draft moves; an approved, done or abandoned plan stays and is listed under "Docs elsewhere". Verified, by reading. Its guard for a linked draft is narrower than its own next bullet; see Broke. |
| 3 | fixed | The hand-off plan template's step 1 links this page's "When to use it". Verified. |
| 4 | fixed | The reader standard's "Who it binds" now names three templates, and this one is not among them. Verified. |
| 5 | fixed | The sentence on the two rejected shapes is gone; the live reason stays. Verified. |

Broke:

- Not blocking. The draft bullet leaves a draft in place only when "an approved plan or a signed-off record links" it. The next bullet treats done and abandoned plans as frozen too, and layout's "The opening" also freezes accepted and superseded decision records. A draft linked only from a done plan or an accepted decision record is moved, and the `links` check then sends the agent to edit a frozen page. Verified, by reading. No check holds frozen pages, as layout says, so none of the four blocking conditions applies.

Missed: none.
