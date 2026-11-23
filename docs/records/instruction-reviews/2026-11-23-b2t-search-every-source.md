---
kind: record
last-reviewed: 2026-11-23
covers: docs/playbooks/search-every-source.md
reviewed-at: 18eccc5, with the uncommitted change of the B2t builder
---

# Instruction review: docs/playbooks/search-every-source.md

This records the instruction review of slice B2t's change to the federated search playbook, for its author and for agents searching outside sources.

**In short:** 3 findings: 1 trigger, 1 step, 1 placement. None is blocking.

## Scope

The change is `git diff fad9f23 -- docs/playbooks/search-every-source.md`: the title, the purpose line and the In short line, the paragraph on tracker operations in "When to use it", the question-log sentence after "Steps", the report's last line, and the question-log row of "Rules". In scope: that changed text, and anything on the page, or on a page it links to, that the change contradicts or leaves stale.

Read beside it: `AGENTS.md`, `CLAUDE.md`, `INDEX.md`, `docs/procedure-endings.md`, `docs/definition-of-done.md`, `docs/orchestration.md`, `docs/changing-the-machinery.md`, `docs/parts.md`, `docs/research-ladder.md`, `docs/question-log.md`, tracker operations, git-host operations, the playbook list, the glossary, and the plan's B2t rule on standard titles. Searched the repository for every link to `search-every-source.md`. Ran `python3 ws.py check` (no error; one unrelated eval_record warning).

## Findings

| # | Class | Where | Finding | Disposition |
|---|---|---|---|---|
| 1 | trigger | Title, with the routing rows of git-host operations and tracker operations | Not blocking. The page is now titled "Federated search", and the playbook list says so. The text that routes agents here still uses the old title as the link's name: git-host operations' and tracker operations' "which page wins" tables, the research ladder's sentence on outside sources, the glossary's "Outside source" row and the spec template. The plan's B2t rule keeps a coined term only as a search alias. The links resolve and the page says "Also called searching every source", so routing still works. Verified by searching the repository for `search-every-source.md`. | fixed: the link text on the five pages now reads federated search. |
| 2 | step | "When to use it", the paragraph on tracker operations | Not blocking. The new exception fires "when that read fails, or the person does not paste the item as its step 2 asks". In tracker operations, a failed read in step 1 is what sends step 2 to ask for the paste. Read with "or", a failed read alone lets the agent skip that ask and search without the item. Read as one path, it asks first. The page gives no default between the two. Verified by reading this paragraph and tracker operations' steps 1 and 2; how an agent reads it is inferred. | fixed: the exception asks once for the item, as tracker operations' step 2 does, before it carries on. |
| 3 | placement | "Steps", step 5 | Not blocking. The page now links procedure endings for the question-log entry, but step 5 still restates the report rule ("each claim marked verified or inferred as the definition of done says") rather than linking [procedure endings' report](../../procedure-endings.md#the-report). That section also names refusals and anything left uncommitted or unpushed, such as the log row. Verified by reading both pages. | fixed: step 5 links procedure endings' "The report". |

## Checked with no finding

- contradiction: the new exception to tracker operations is labelled as one; the purpose line, the In short line, step 5, the sentence after the steps, the report's "Written:" line and the first rules row all allow exactly one written file, a question-log entry, and agree with procedure endings' "The question-log entry".
- enforcement: no new must or never; the changed rules row stays `prose`.
- eval-case: the page is `proof: unproven`, `prove-by: M8`, so the new exception needs no eval case yet.

## Re-check

A fresh session re-read the page on 2026-11-23 after B2t's fix round, with `git diff fad9f23`, procedure endings, changing the machinery, the contract, tracker operations' steps 1 and 2, and the other five pages of this batch that share the off-`main` rule: architecture review, the review orchestrator, defect escape analysis, git-host operations and tracker operations. `python3 ws.py check` passes, with only the known warning on fix a bug's eval record. In a scratch repository with a local bare remote, `git push origin HEAD:main` from a worktree on a branch holding a code commit and then a question-log commit exited 0 and moved the remote's main to include the code commit.

| # | Verdict | Evidence |
|---|---|---|
| 1 | holds | The five pages the finding named now link the page as "federated search": git-host operations' and tracker operations' tables, the research ladder, the glossary's "Outside source" row and the spec template. The playbook list already did. Verified: `git grep` for `search-every-source.md` outside records, plans and milestones. The page no longer carries an "Also called" line, which the finding counted on for routing. That follows the reader standard's rule, as the red team review and glossary records ask, and leaves the old name to the queued `INDEX.md` row. Verified: the page. |
| 2 | holds | The exception now says, when the tracker read fails, to ask the person once to paste the item, as tracker operations' step 2 does, and with no answer to carry on without it and list the tracker as not reachable. So one path holds, and it has a default. Verified: the text. |
| 3 | holds | Step 5 links procedure endings' "The report". Verified: the text. |

Broke:

- none.

Missed:

- Blocking. The paragraph after the steps logs a question "as procedure endings says", with no exception for a branch other than `main`. Procedure endings commits the row "on the worktree's branch in a worktree", then pushes it with `git push origin HEAD:main`. A search asked for mid-task, from a fix's or a feature's worktree, has an unmerged code branch checked out, so the push carries that code to main with no pull request and no CI. That goes against procedure endings' "never on its main" for code and the contract's draft pull request rule. `direct_push` refuses only machinery paths. Git-host operations' finding 1 was this same chain, marked blocking, and was fixed there; this page got no exception. Verified: the texts of this page and procedure endings' "The commit" and "The push"; the scratch push above. Inferred: that the search runs with a code branch checked out, and that an agent follows procedure endings through to the push. The fix is the exception git-host operations has, or one rule on procedure endings for every procedure.
