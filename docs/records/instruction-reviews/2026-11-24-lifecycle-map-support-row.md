---
kind: record
last-reviewed: 2026-11-24
covers: docs/lifecycle-map.md
reviewed-at: 4cc14be, with the uncommitted change of the lifecycle map session
---

# Instruction review: docs/lifecycle-map.md

This records the instruction review of the lifecycle map's new "Support questions" row, for its author and for critics.

**In short:** 2 findings: 2 contradiction, none blocking. The row plans a new read-only playbook that answers a question from the workspace, which federated search and the research ladder already own, and it names "defect records", a record the workspace does not keep.

## Scope

In scope: the one added row, "Support questions", in the table under "Across every stage". The rest of the page was reviewed in [the earlier record](2026-11-24-lifecycle-map.md) at the previous commit. Read beside it: `AGENTS.md`, `INDEX.md`, `docs/reading-paths.md`, `docs/how-tos.md`, the rest of `docs/lifecycle-map.md` with its state definitions and Rules table, `docs/procedure-endings.md`, `docs/extend-the-workspace.md`'s "One owner per topic", `docs/research-ladder.md`, `docs/playbooks/search-every-source.md`, decision 0008, `docs/records/README.md`, `docs/records/defects.md`, `docs/glossary.md`, the unit doc template and the list of `docs/decisions/`. Ran `git diff HEAD`, `git grep` for "support", "defect record", "unit doc" and "user", a grep of `evals/arms.json` and `evals/cases/` for the page, and `python3 ws.py check`, which reported only its known warning on fix a bug's eval record.

The page has no `## References` heading.

## Findings

| # | Class | Where | Finding | Disposition |
|---|---|---|---|---|
| 1 | contradiction | Across every stage, the Support questions row and the Finding code and pages row | Not blocking. The Planned cell plans a new "read-only playbook that answers a user's question from the decision records, defect records and unit docs, with each claim marked verified or inferred". Federated search already does that: it "answers a question from the workspace and the outside sources a person names, writing nothing on what it reads", its step 1 goes straight to the report "if the workspace answers the question in full", and the report marks each claim verified or inferred as procedure endings says. The research ladder owns a question the workspace alone answers. Extend the workspace's "One owner per topic" says a procedure that overlaps a page already here goes into that page as a section, not a page beside it. Two rows above, the Finding code and pages row links both pages and plans "Nothing more". The row's Pages cell says "None", so a reader with a support question today is not sent to the two pages that answer questions now. Verified: the four texts read. Inferred: what would set the planned playbook apart, such as the asker being a product's end user, or the answer being written for a non-developer, is not stated; the row does not say who "a user" is, and the glossary has no entry for it. | fixed: the row links the two pages that answer a question today, says who the new procedure is for, and makes it a section of federated search by default. |
| 2 | contradiction | Across every stage, the Support questions row | Not blocking. The Planned cell names "defect records" as a source. The workspace keeps no record by that name: the records index lists a defect register, one file, and fix records, and no other page uses "defect record". The defect register holds "defects found in passing" in the workspace's own pages and machinery; both its open rows are about `docs/orchestration.md` and `.gitignore`, not a product's behavior. A reader cannot tell whether the planned playbook reads the register, fix records or the tracker's bug tickets. Verified: `git grep` for "defect record" finds only this row; the records index and the register read. Inferred: a user's question about a product would draw on fix records and bug tickets rather than the register. | fixed: the row names decision records, fix records, bug tickets and unit docs, which the records index and the templates define. |

## Checked with no finding

- step: the page is a reference page with no steps, and the row holds no link or command. `python3 ws.py check` reported nothing on the page (verified).
- trigger: the purpose line, the **In short** line and the how-to index row for the map still describe the page with the row added; the **In short** line lists no topic it now misses. The row's effect on routing a support question today is part of finding 1 (verified, by reading).
- enforcement: the row states no must or never. It meets the second rule: a topic with no page, marked Planned with a milestone. The first rule does not fire, since the commit adds no playbook or how-to. The planned item has no source in this repository: `git grep` finds "support" nowhere else, as for most Planned cells; the program plan outside the repository was not read (inferred). Its "each claim marked verified or inferred" agrees with the contract's first rule (verified).
- placement: the row sits under "Across every stage", whose topics "cut across every stage". A support answer drawn from decision records, defect or fix records and unit docs reads what several stages produce, so the table is defensible (inferred). "Read-only" fits procedure endings, where "a procedure that wrote nothing commits nothing" (verified). The row restates no rule procedure endings owns.
- eval-case: the row asks no new behavior of an agent. The page is a reference page with no proof keys, and neither `evals/arms.json` nor any case under `evals/cases/` reads it (verified, grep).
