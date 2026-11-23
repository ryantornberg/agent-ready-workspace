---
kind: record
last-reviewed: 2026-11-22
covers: docs/playbooks/decision-interview.md
reviewed-at: 1fa880a, with the uncommitted change of the B2 builder
---

# Instruction review: docs/playbooks/decision-interview.md

This records the instruction review of batch 5's sweep change to the decision interview, for its author and for agents who run the interview.

**In short:** 2 findings: 1 enforcement, 1 step.

## Scope

The fix round's change only: step 10 now commits the question-log entry "as [the log's page] says", linking `docs/question-log.md` instead of saying how. In scope too is anything on the page that change contradicts or leaves stale. Read beside it: `AGENTS.md`, `docs/question-log.md` ("Adding an entry"), `docs/commits.md`, `docs/changing-the-machinery.md` ("The path for a machinery change" and "Traps"), `docs/maintain-the-workspace.md` step 4, `docs/playbooks/instruction-review.md`, `docs/playbooks/handoff.md`, `docs/how-tos.md`, `docs/definition-of-done.md`, the `review_trailer`, `page_kinds` and `edit_ledger` entries in `workspace.json`, and `parts/edit_ledger.py`. Ran: `git diff -- docs/playbooks/decision-interview.md docs/question-log.md`, `grep -rn "commit it as that page says"` across `docs/` (the other swept pages and their rules rows), and `python3 ws.py check` (exit 0, one unrelated `eval_record` warning).

## Findings

| # | Class | Where | Finding | Disposition |
|---|---|---|---|---|
| 1 | enforcement | "Rules" table, the question-log row | Step 10 now makes committing the question-log entry a must, but the rules row still reads only "goes in the question log before you finish", with no commit. The same sweep added "and commit it as that page says" to the question-log row of machine self-check, git host operations, tracker operations and search every source, so this page's table no longer states the rule its step holds. Verified by reading the page and by the grep. Cause: sweep-incomplete — the sweep changed the step's sentence but not the rules row that restates it on this page. | deferred to B2's next fix round, which waits for the maintainer's answer to Q29 |
| 2 | step | "Steps", step 10 | The linked rule says "Push it with the session's other work. With none, an agent may push it in this repository, and in a team's workspace a person does." The interview commits a plan, and maybe glossary rows and decision records, but never says whether that work is pushed. So an agent cannot tell whether the entry rides an unpushed plan commit, or counts as "with none" and is pushed alone, which would push the plan commit under it on the same branch. Verified by reading both pages; that agents will split on it is inferred. Cause: linked-rule-unreconciled — linking a shared rule brought in a push step that the linking page has no matching word for. | deferred to B2's next fix round, which waits for the maintainer's answer to Q29 |

## Checked with no finding

- contradiction: the link resolves to `docs/question-log.md`'s "Adding an entry", and `python3 ws.py check` passes with it. That rule's "no `Instructions-review:` trailer" agrees with `workspace.json`, which lists `docs/question-log.md` under `review_trailer`'s `except`, so the entry may share the plan's commit without the record covering it. "The question log" section's "before you finish" matches the log's "before the session finishes". Step 10 commits the plan before it logs the question, so there may be two commits where its Output says "the commit"; the log's page allows the entry "on its own", so this is wording, not a conflict. The eval rule is not touched: "Where a term goes" still queues an alias row as `waits for an eval run`, the default that maintain the workspace's step 4 states.
- trigger: the change touches no purpose line, In short line or catalog row.
- placement: the commit rule is linked, not restated, as the sweep intends; step 10 still points to "The question log" below for what to log.
- eval-case: the page is `proof: unproven`, `prove-by: M9`, so the new behavior needs no case yet.
