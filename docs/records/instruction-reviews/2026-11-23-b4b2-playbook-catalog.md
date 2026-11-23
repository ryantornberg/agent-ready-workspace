---
kind: record
last-reviewed: 2026-11-23
covers: docs/playbooks/README.md
reviewed-at: 4190d8d, with the uncommitted change of the B4 slice session
---

# Instruction review: docs/playbooks/README.md

This records the instruction review of slice B4's second-batch edit to the playbook catalog, for its author and for critics.

**In short:** 1 finding: 1 trigger, not blocking. The tracker operations row still fires for applying triage outcomes and for grooming a bug, with nothing on the catalog saying the new lane rows win.

## Scope

In scope: the uncommitted edit to "Lane drafts". It widens the QA verification list row to "write or check", and adds four product rows (bug grooming, bug triage meeting, effort estimate, standup report) and one DevOps row (import a repository). Also in scope: how those rows fit the rest of the catalog, its "Before you pick one" routing and the rows already there.

Read beside it: `AGENTS.md`, `INDEX.md`, `docs/layout.md`, `docs/authoring.md`, `docs/procedure-endings.md`, `docs/reader-standard.md`, `docs/extend-the-workspace.md`, and each page the new rows link, in full. Also the QA verification list's opening and step 1, and tracker operations' "When to use it, and which page wins". Ran `git diff -- docs/playbooks/README.md` and `python3 ws.py check`, which reports nothing on this page. Checked that every file in `docs/playbooks/` has a row here with a shell loop: none is missing.

The page has no `## References` heading.

## Findings

| # | Class | Where | Finding | Disposition |
|---|---|---|---|---|
| 1 | trigger | The catalog, the tracker operations row; Lane drafts, the bug triage meeting and bug grooming rows | Not blocking. The tracker operations row fires on "A request acts on a work item: read it, create one, change its fields, sub-tasks or status". A request to apply a triage meeting's outcomes, or to groom a filed bug, matches it as well as its new lane row, and the catalog says nothing on which wins. Tracker operations' own "which page wins" table does not route either away. Only the triage meeting page's own table says it wins, and an agent sent to tracker operations never reads it. There, it would apply outcomes with no hardening row before a rejection, and groom with no fresh-session re-check. Every write still needs a yes on that page, so nothing is written without one. Verified: the two rows, and tracker operations' table. Inferred: that an agent picks the "Any stage" row for such a request. | fixed: the tracker operations row's task cell now says that applying a bug triage meeting's outcomes or grooming a bug takes its lane row instead. |

## Checked with no finding

- contradiction: each new row's Proof cell matches its page's front matter: M9 for the four product rows, M11 for the import. Each title matches its page's heading, and each Lane cell its `lane` key. The QA verification list row's "write or check" matches that page's purpose line, "for the agent or person writing or checking it", and its step 1 default for checking a document. The effort estimate row's "A bug's size is grooming's" matches that page's "When to use it". The rows run in the lane order the section's intro names: QA, product, DevOps, development. Verified: pages read.
- step: the change adds no step. Every new link resolves; the `links` check reported nothing on this page.
- enforcement: the first Rules row holds: every playbook in the folder has a row here. Verified: a shell loop over `docs/playbooks/*.md` found none missing. The wrapper rule holds: each new row's page names a `prove-by`.
- placement: the rows route only; none restates a procedure's steps or a rule of procedure endings.
- eval-case: the page is a reference. No eval case or arm in `evals/arms.json` reads it, and each new row routes to a page marked unproven with a `prove-by`.

## Re-check

A fresh session read the fix round's `git diff -- docs/playbooks/README.md` and the whole catalog as it now stands. It read beside it tracker operations' "When to use it, and which page wins", the bug triage meeting's "Which page wins", and bug grooming's opening and steps. It ran `python3 ws.py check`, which exited 0 with only the known `eval_record` warning on `fix-a-bug.md`. Verified: the catalog table keeps four columns on every row.

| # | Verdict | Evidence |
|---|---|---|
| 1 | upheld | Verified: the catalog's tracker operations row now ends "To apply a bug triage meeting's outcomes or to groom a bug, take its lane row below instead." Both lane rows sit below it, under "Lane drafts". The routing matches the bug triage meeting's "Which page wins": applying outcomes goes to that page, checking one bug goes to bug grooming, and one field change outside a meeting stays with tracker operations. Left as it was, outside this record: tracker operations' own "which page wins" table still routes neither request away, so an agent that reaches that page by another route still meets the first reading's gap. Inferred: few agents reach it without the catalog or the triage meeting page. |

What a fix broke:

- None.
