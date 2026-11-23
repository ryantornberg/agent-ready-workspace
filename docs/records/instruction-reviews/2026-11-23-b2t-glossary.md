---
kind: record
last-reviewed: 2026-11-23
covers: docs/glossary.md
reviewed-at: 18eccc5, with the uncommitted change of the B2t builder
---

# Instruction review: docs/glossary.md

This records the instruction review of slice B2t's edit to the glossary, for its author and for critics.

**In short:** 2 findings: 1 contradiction, 1 trigger, none blocking. The new "Red team" row keeps "adversarial review" as an alias outside `INDEX.md` and gives it to the session rather than the procedure. Two rows still name pages by titles the same change replaced.

## Scope

In scope: the link change in the "Critic" row, from commit 18eccc5, and the uncommitted edit, which moves the review date and adds the "Red team" row. Also in scope: anything on the page, or on a page it links to, that the change contradicts or leaves stale. That includes the rows that link pages the same change retitles.

Read beside it: `AGENTS.md`, `CLAUDE.md`, `INDEX.md`, `docs/procedure-endings.md`, `docs/definition-of-done.md`, `docs/orchestration.md`, `docs/size-the-work.md`, `docs/templates/hand-off-plan.md`, `docs/records/README.md`, and `docs/reader-standard.md`. Also the pages the changed rows link, `docs/playbooks/red-team-review.md` and orchestration's "Fresh context for critics", and the retitled `escape-analysis.md` and `search-every-source.md`. Read the M3 plan's change of 2026-11-22. Ran `git diff -M fad9f23` and `git diff` on the page. Ran `python3 ws.py check`: it passes, with one warning on `fix-a-bug.md` that has nothing to do with this page. Ran grep for the link texts used for the two retitled pages.

## Findings

| # | Class | Where | Finding | Disposition |
|---|---|---|---|---|
| 1 | contradiction | The table, the "Red team" row | Not blocking. The new row ends "Also called adversarial review." The reader standard's "Names" says a term coined here "stays only as a search word in the page's row of `INDEX.md`'s Topics table". The plan's change of 2026-11-22 puts "adversarial review" there, in the `INDEX.md` line queued for slice Z. The glossary is a second home for it. The row also gives the alias to the wrong thing. Its headword "Red team" names the session, "the critic that attacks". "Adversarial review" names the procedure, and red team review's own **In short** line gives the alias to the procedure. Verified: read the row, the reader standard's "Names" and Rules rows, the plan's change entry and red team review's **In short** line. Inferred: that "adversarial review" counts as a coined term under that rule. The plan's entry treats it as one. | fixed: the row no longer gives the alias; it goes in the queued `INDEX.md` row. |
| 2 | trigger | The table, the "Escape" and "Outside source" rows | Not blocking. The same uncommitted change retitles `escape-analysis.md` "Defect escape analysis" and `search-every-source.md` "Federated search", and the playbook catalog's rows now use those names. The glossary adds a row for the one rename it covers, red team, but its "Escape" row still links "Escape analysis", and its "Outside source" row still links "search every source". A reader who meets "federated search" in the catalog finds that name nowhere on this page. The reader standard keeps such old names only as search words in `INDEX.md`. Verified: read both pages' titles and the catalog rows, and grepped the link texts. Inferred: the same old link texts sit on other pages outside this record's scope, such as the research ladder, git-host operations, tracker operations and the spec template. | fixed: the Escape and Outside source rows use the new titles. |

## Checked with no finding

- step: the page has no steps. Every link resolves, and `python3 ws.py check` passes its links check. The "Critic" row's new link goes to the moved page.
- enforcement: the page has no Rules table and states no must or never.
- placement: the "Red team" row sits in alphabetical order, between "Proven" and "Rule page". It defines the word and points to the page, and restates no step. Its scope, a finished hand-off plan or requirements document, matches the playbook and the "Critic" row.
- eval-case: the page is a reference. No eval case or arm in `evals/arms.json` reads it.

## Re-check

A fresh session re-read the page on 2026-11-23, after B2t's fix round.

| # | Verdict | Evidence |
|---|---|---|
| 1 | fixed, holds | The "Red team" row reads "The critic that attacks a finished hand-off plan or requirements document before anyone builds from it", with no alias. The alias sits in the plan's queued `INDEX.md` line for slice Z. Verified: the page and the plan's queued list. |
| 2 | fixed, holds | The "Escape" row links "Defect escape analysis", and the "Outside source" row links "federated search". Both match the pages' headings, `# Defect escape analysis` and `# Federated search`. Other guidance pages no longer use the old link texts either: they now appear only in records and plans. Verified: `git diff -M fad9f23`, the headings, and grep for the old texts. |

Broke:

- Not blocking. With finding 1 fixed, and red team review's alias removed too, nothing in guidance maps "adversarial review" to its page until slice Z's `INDEX.md` line lands. The plan accepts this gap for coined terms. Verified: grep for "adversarial" over `INDEX.md`, the glossary and red team review.

Missed:

- none.
