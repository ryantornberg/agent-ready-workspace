---
kind: record
last-reviewed: 2026-11-22
covers: docs/playbooks/tracker-operations.md
reviewed-at: f757aed, with the uncommitted change of the B3 builder
---

# Instruction review: docs/playbooks/tracker-operations.md

This records the review of the fix-round link to the bug report template, for its author and any agent filing a bug.

**In short:** 2 findings, none blocking: 1 step, 1 trigger. The link covers creating a bug but not rewriting one, and step 2 gives a request to create an item no way past its target rule.

## Scope

In scope: the sentence the fix round added to the "Create an item" row of "The operations", shown by `git diff -- docs/playbooks/tracker-operations.md`, read in the context of the whole page. Read beside it: `AGENTS.md`, `INDEX.md`, `docs/playbooks/instruction-review.md`, `docs/procedure-endings.md`, `docs/reader-standard.md`, `docs/authoring.md`, `docs/templates/bug-ticket.md` and its review record, `docs/templates/README.md`, `docs/playbooks/git-host-operations.md`, and B3's row and the 2026-11-22 entries naming B3 in the M3 plan. Ran `python3 ws.py check` in the worktree: its only errors are review records of the B3 fix round not yet in the index, none about this page.

## Findings

| # | Class | Where | Finding | Disposition |
|---|---|---|---|---|
| 1 | trigger | The operations, the "Rewrite a stale item" row | Not blocking. The new link sits on "Create an item" only. The bug report template's "When to use it" also covers rewriting a stale bug ticket, and the templates index row fires on "file or rewrite a bug". An agent rewriting a stale bug through this page follows "Rewrite a stale item" and never meets the template's fixed headings. It also misses the template's rule that a disproved claim moves to "Out of scope" and is never deleted. Verified: the three texts. | open |
| 2 | step | Steps, step 2 | Not blocking. Step 2 says that when the request names no item, and the person's words match more than one item or none, the agent asks which, and with no answer makes no write. A request to create an item names none, and a new bug matches no item, so read as written step 2 stops every create. The newly linked template expects the agent to search for a duplicate, find none and file. The step needs a case for a create: the duplicate search is the read, and no match means the new item is the target. Verified: step 2's text and the template's "Before you write". Inferred: that an agent applies step 2's rule to a create. | open |

## Checked with no finding

- contradiction: the "Create an item" row's field groups and the template's "Filing it", which leaves the fields triage sets empty, can both hold: the row fills a later group only when one is filled. The template's duplicate search ends in an offer to add to the existing ticket, which matches this page's ask-first rule for an item nobody asked about. The template's `--repo` sentence names a repository this page does not limit; that gap is recorded in the bug report template's re-check. Verified.
- enforcement: the new sentence is an instruction, not a must or a never, so it needs no Rules row. Verified.
- placement: the row links the template instead of restating its shape. No rule of procedure endings is restated by the change. Verified.
- eval-case: the page is `proof: unproven` with `prove-by: M8`. Verified from the front matter.
