---
kind: record
last-reviewed: 2026-11-23
covers: docs/playbooks/red-team-review.md
reviewed-at: 18eccc5, with the uncommitted change of the B2t builder
---

# Instruction review: docs/playbooks/red-team-review.md

This records the instruction review of slice B2t's move and edit of the red team review playbook, for its author and for critics.

**In short:** 4 findings: 4 contradiction, none blocking. The page keeps "adversarial review" as an alias outside `INDEX.md`, gives a false reason for the records folder's name, ends with a rule that step 2's red team session does not label as an exception, and leaves the old name on two pages it links to.

## Scope

In scope: the move from `docs/playbooks/adversarial-review.md` in commit 18eccc5, which changes the template's path line, and the uncommitted edit on top of it. That edit renames the critic the red team throughout, changes the title, purpose and **In short** lines and adds an alias, rewords "Thin by design", adds step 3's sentence on the records folder, ends steps 4 and 7 through procedure endings, renames the record's title line, adds a Rules row and adds the "References" heading. Also in scope: anything on the page, or on a page it links to, that the change contradicts or leaves stale.

Read beside it: `AGENTS.md`, `CLAUDE.md`, `INDEX.md`, `docs/procedure-endings.md`, `docs/definition-of-done.md`, `docs/orchestration.md`, `docs/size-the-work.md`, `docs/templates/hand-off-plan.md`, `docs/records/README.md`, `docs/reader-standard.md`, `docs/playbooks/instruction-review.md`, and the M3 plan's change of 2026-11-22. The routes into this page from architecture review, the review orchestrator, the fresh-session prompt template and the templates index were checked with grep. Ran `git diff -M fad9f23` on the page and `git show -M 18eccc5`. Ran `python3 ws.py check`: it passes, with one warning on `fix-a-bug.md` that has nothing to do with this page. Ran grep for "adversarial" across the repository.

References: opened the source live, not the local copy. Fetched `https://www.gov.uk/government/publications/a-guide-to-red-teaming` (HTTP 200). The page is titled "Red Teaming Handbook", from the Ministry of Defence, and its updates list the third edition added on 30 June 2021. Downloaded the PDF it links on `assets.publishing.service.gov.uk` and read it with `pdftotext`. Its cover reads "Red Teaming Handbook, 3rd Edition, dated June 2021". Under "Terminology", paragraph 1.10 defines a red team as "a team that is formed with the objective of subjecting an organisation's plans, programmes, ideas and assumptions to rigorous analysis and challenge". Paragraph 1.9 calls red teaming "the independent application" of thinking techniques and says the exercises "are best conducted by a separate red team". The credit holds, verified. One note, not a finding: in 1.9, "separate" contrasts a team with individuals. The plainest statement that a red team stands apart from the plan's own decision-makers is paragraph 1.3, outside "Terminology": "an external viewpoint separate to that of 'home team' decision-makers". The entry makes no comparison and is credit only, as the reader standard asks.

## Findings

| # | Class | Where | Finding | Disposition |
|---|---|---|---|---|
| 1 | contradiction | The **In short** line | Not blocking. The **In short** line now ends "Also called adversarial review." The reader standard's "Names" says a term coined here "stays only as a search word in the page's row of `INDEX.md`'s Topics table". The plan's change of 2026-11-22 puts "adversarial review" in exactly that place: a search alias in the `INDEX.md` line queued for slice Z. The page states the alias outside the index, and says nothing to mark it as a stopgap until slice Z lands. Verified: read the **In short** line, the reader standard's "Names" and Rules rows, and the plan's change entry. Inferred: that "adversarial review" counts as a coined term under that rule. The plan's entry treats it as one. | fixed: the In short line no longer gives the alias. |
| 2 | contradiction | "Steps", step 3 | Not blocking. The new sentence "The folder keeps its older name, since approved plans link records there" gives a reason that is false today. `docs/records/adversarial-reviews/` does not exist on this branch or on `origin/main`. `git log --all` shows no commit that ever touched it. No Markdown link into it appears under `docs/plans/` or `docs/milestones/`. The approved M3 plan names the folder only in prose, in its change of 2026-11-22 and in B2's results. There is no record yet for a plan to link. The folder name itself is settled and works. Only the stated reason misleads a reader who goes looking for those links. Verified: `ls`, `git log --all -- docs/records/adversarial-reviews`, `git ls-tree -r origin/main`, and grep over the plans and milestone records. | fixed: the sentence gives no reason. |
| 3 | contradiction | "Rules", the new last row, against "Steps", step 2 and the template | Not blocking. The new row says "The procedure ends as procedure endings says". Procedure endings commits every file the procedure wrote, then pushes. Step 2 has a session that is itself the red team "carry out its lines yourself, and stop there. The author takes it from step 4." The template tells a dispatched red team "Edit nothing else". Steps 4 and 7 then have the author commit the record. A red team session reads this page for the record's shape, and nothing excludes it from the new row. It can read the row as covering its own record and commit and push it before triage. The author would then commit the same record again. The page labels no exception for the red team's own session, as debugging's step 8 does with "By exception to that page's commit step". Inferred: from reading step 2, the template, the Rules table and procedure endings' "The commit" and "The push". No run. | fixed: the row says the author's procedure ends there, and the red team commits nothing; step 2 says so too. |
| 4 | contradiction | Pages it links to: size the work's "The four phases" and the hand-off plan template's skeleton | Not blocking. The move updated every link but left the old name in running text on two pages this page links to. The Slice row of size the work's "The four phases" says "then the adversarial review of the finished plan, triaged in its red team table". Its ladder table, on the same page, names the rung's page "Red team review". The hand-off plan template's skeleton, under "## Red team", says "Record: <link to the adversarial review record>." Both put the old name outside `INDEX.md`, against the reader standard's "Names", like finding 1. The glossary maps the old name, so a reader is not lost. A third use, in `evals/grade.py`'s docstring, is machinery and not guidance. Verified: grep for "adversarial" across the repository, and read both rows. | fixed: both lines now say red team review. |

## Checked with no finding

- step: every link on the page resolves, and `python3 ws.py check` passes its links check. The template's path, `docs/playbooks/red-team-review.md`, exists. The template still has exactly four placeholders. The records folder does not exist yet, and the records README says the first record written into a folder creates it. Steps 4 and 7 each end with a stop or an output.
- trigger: the purpose and **In short** lines cover the same documents as before. The catalog row, size the work's ladder and feature ladder, architecture review, the review orchestrator's routing table and the fresh-session prompt template all send a plan or requirements document here under the new name.
- enforcement: the new Rules row is tagged `prose` and states no enforcement it lacks. `handoff_tier#no tier named` exists in `parts/handoff_tier.cases.json`. The edit adds no must or never without a Rules row.
- placement: steps 4 and 7 now link procedure endings instead of restating staging by name and claim marks. "References" sits after the Rules table, as the reader standard asks. It credits the source and gives no guidance on how to attack, so "Thin by design" still holds.
- eval-case: the page is `proof: unproven`, `prove-by: M9`. No eval case or arm in `evals/arms.json` reads it.

## Re-check

A fresh session re-read the page on 2026-11-23, after B2t's fix round.

| # | Verdict | Evidence |
|---|---|---|
| 1 | fixed, holds | The **In short** line ends at "until every finding is triaged". No alias is left on the page. The alias sits in the plan's queued `INDEX.md` line for slice Z: "Red team; adversarial review; a critic attacks a plan". Verified: the page and the plan's queued list. |
| 2 | fixed, holds | Steps 3 and "The record" say only "The folder keeps the page's older name". The false reason is gone. Verified: the page. |
| 3 | fixed, holds | Step 2 now says a session that is itself the red team will "commit nothing, and stop there". The last Rules row labels the exception: "The author's procedure ends as procedure endings says. The red team, dispatched or not, writes its record and commits nothing; the author commits it." Steps 4 and 7 keep the commit with the author. Verified: the page against procedure endings' "The commit". |
| 4 | fixed, holds | Size the work's "The four phases" Slice row now reads "the red team review of the finished plan", and the hand-off plan template reads "Record: <link to the red team review record>." No guidance page outside the plans and records still uses "adversarial review" as a name. The folder path `adversarial-reviews/` remains, and so does `evals/grade.py`'s docstring, which is machinery. Verified: grep for "adversarial" across the worktree. |

Broke:

- Not blocking. This fix and the glossary record's finding 1 removed the only two places in guidance that mapped "adversarial review" to this page. Until slice Z adds the queued `INDEX.md` line, a reader or agent who searches the old name finds only the records folder's path. The plan accepts this gap for coined terms. Verified: grep for "adversarial" over `INDEX.md`, the glossary and this page.

Missed:

- none.
