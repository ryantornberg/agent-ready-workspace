---
kind: record
last-reviewed: 2026-11-23
covers: docs/playbooks/docs-audit.md
reviewed-at: 18eccc5, with the uncommitted change of the B2t builder
---

# Instruction review: docs/playbooks/docs-audit.md

This records the instruction review of slice B2t's change to the docs audit playbook, which points its question-log rule at procedure endings. It is for the change's author.

**In short:** 2 findings: 1 step, 1 contradiction; none blocking. The page now links only procedure endings' question-log section, so nothing on it tells the agent to push the entry it commits. The first Rules row allows "one new question-log row", where an audit that asked two questions writes two.

## Scope

In scope: the changed text (the paragraph under the "When it runs" table, step 5's first sentences, and the first and last Rules rows), and anything on the page or a linked page that the change contradicts or leaves stale. Read beside it: `AGENTS.md`, `CLAUDE.md`, `INDEX.md`, `docs/procedure-endings.md`, `docs/definition-of-done.md`, `docs/playbooks/fix-a-bug.md`, `docs/question-log.md`, and the page the changed text links to, procedure endings' "The question-log entry" section. Also read the page's earlier record, `2026-11-22-b4-docs-audit.md`, whose second re-check found the first Rules row missed. The changed steps name no new command; ran `git diff fad9f23` on the page and `python3 ws.py check`, which reports no error on it.

## Findings

| # | Class | Where | Finding | Disposition |
|---|---|---|---|---|
| 1 | step | When it runs, the paragraph under the table; Steps, step 5; Rules, the last row | Not blocking. The change replaced "committed as that page says" with a link to procedure endings' "The question-log entry" section only. That section says the row "is committed in the next step", but this page never sends the agent to procedure endings' commit or push steps, and step 5 ends "Stop here" after the report. The question log's own page says "commit and push it as procedure endings says". An agent following this page commits the row at most, and has no instruction to push it. Verified by reading the diff, the linked section and the question log's "Adding an entry" line. | fixed: step 5 says to log, commit and push the entry as procedure endings says. |
| 2 | contradiction | Rules, the first row | Not blocking. The row now says the audit changes nothing "except one new question-log row". "When it runs" and step 5 speak of "a question-log entry", procedure endings adds "a dated row" for each question a person had to answer, and each row of the log holds one question. An audit that had to ask two questions breaks the row by following the page. Verified: each row in the question log's table holds one question. Inferred: that "one" reads as a limit rather than an example. | fixed: the row allows new question-log rows. |

## Checked with no finding

- trigger: the purpose line, **In short** line and "When it runs" table are unchanged, and the change does not alter when the audit runs.
- enforcement: both changed Rules rows keep `prose`, as before; the report row keeps `eval:fix-a-bug`.
- placement: both changed sentences now link procedure endings instead of restating its question-log rule; step 5's verified-or-inferred sentence links the definition of done's report, which procedure endings' report also points to.
- eval-case: the page is marked `proof: unproven` with `prove-by: M10`.

## Re-check

A fresh session re-read the page on 2026-11-23 after B2t's fix round. It read the page whole, `git diff fad9f23` of it, the contract, procedure endings, changing the machinery's "Traps", maintain the workspace, fix a bug and the question log's "Adding an entry" line, and ran `python3 ws.py check`, which exits 0 with only the known warning on fix a bug's eval record.

| # | Verdict | Evidence |
|---|---|---|
| 1 | upheld | Step 5 now says to "log it, commit it and push it as procedure endings says", before the report, which matches procedure endings' order and the question log's "commit and push it". The paragraph under "When it runs" and the last Rules row link procedure endings too. Verified: the text. |
| 2 | upheld | The first Rules row allows "new question-log rows", so an audit that asked two questions keeps the rule. Verified: the text. |

Broke: none.

Missed: none.
