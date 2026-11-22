---
kind: record
last-reviewed: 2026-11-21
covers: docs/playbooks/debugging.md
reviewed-at: 9f3de36, with the uncommitted change of the B2 builder
---

# Instruction review: docs/playbooks/debugging.md

This records the instruction review of batch 3's edit to the debugging playbook, for its author and for agents finding the cause of a failure.

**In short:** 2 findings: 1 step, 1 trigger. Step 8's new route to escape analysis gives no way to tell whether the code passed a review, and sits where an agent that commits the fix does not return.

## Scope

In scope: the batch 3 edit to "Steps", step 8, which adds a route to escape analysis when the faulty code had passed a review, and anything on the page it contradicts or leaves stale, including step 7, "Halt and report" and "Rules". Read beside it: `AGENTS.md`, `CLAUDE.md`, `INDEX.md`, `docs/definition-of-done.md`, `docs/orchestration.md`, `docs/layout.md`, `docs/glossary.md` (with its new "Escape" row), the linked pages escape analysis, fix a bug and size the work, and the other batch 3 pages (review orchestrator, the playbook catalog diff). Ran `git diff docs/playbooks/debugging.md`, `git grep -n "escape-analysis" -- '*.md' ':!docs/records' ':!docs/plans'` (tracked pages linking it: the README table, the glossary, the playbook catalog and this page; not fix a bug), and `python3 ws.py check` (no finding on this page).

## Findings

| # | Class | Where | Finding | Disposition |
|---|---|---|---|---|
| 1 | step | "Steps", step 8 | "If the faulty code had passed a review, say so" is a decision with no method and no default. Nothing on the page says how to tell. Escape analysis defines coverage precisely, in its step 2: the pull request that merged the defect commit, a review on record whose range holds that commit. An agent at step 8 has not found the defect commit, so it either guesses or skips the line. Verified: read step 8 and escape analysis's "When it runs", "Where a code review is on record today" and step 2. Cause: `brief-silent-on-route-in-edit-review` — the brief limits a route-in edit to one sentence but does not ask that the edited step pass the step pass, which is framed for the builder's own page. | fixed: the sentence no longer asks the agent to judge coverage; escape analysis's step 2 decides whether a review covered the faulty code. |
| 2 | trigger | "Steps", steps 7 and 8 | The route fires only at step 8, but on the path where a fix is made, step 7 sends the agent to fix a bug "from its second step", and fix a bug ends with its own report (its step 6). That page has no link to escape analysis. Step 8 is reached only when no fix is made here, so "once the fix is committed" names a later event this agent does not see. An agent that commits the fix is not routed to escape analysis. Verified: read steps 7 and 8 and fix a bug; the `git grep` above finds no link from fix a bug. Inferred: an agent following step 7 to fix a bug does not come back for step 8, since nothing tells it to. Cause: `brief-silent-on-route-reachability` — the route-in rule asks for a link on the page the reader is on, but not for a check that the reader reaches that sentence on the path that should trigger the linked page. | fixed: the route moved from step 8 into step 7's fix path, where the agent hands on to fix a bug, so it is read on the path that commits the fix. |

## Checked with no finding

- contradiction: "once the fix is committed" agrees with escape analysis's "When it runs" and its first Rules row (it starts only once the fix is committed), and with its "Which page comes first" table, which sends an unfixed defect back here. The glossary's "Escape" row matches the edit's wording.
- enforcement: the edit adds no must or never; the page's Rules table still covers every rule on it.
- placement: the edit links to escape analysis rather than restating it, and sits in the report step where a reader finishing a diagnosis would look.
- eval-case: the page is `proof: unproven`, `prove-by: M4`, so the new behavior needs no case yet.
