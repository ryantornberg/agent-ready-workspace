---
kind: record
last-reviewed: 2026-11-28
covers: docs/adopt-the-workspace.md
reviewed-at: c37afc9, with the uncommitted change of the G0 session
---

# Instruction review: docs/adopt-the-workspace.md

This records the instruction review of M4 slice G0's change to the adoption page, for its author and its readers.

**In short:** 1 finding, not blocking: 1 step. The milestone-state row tells an instance to remove its milestone from `building` in the sign-off commit, and does not say that commit is then a machinery change that goes through a pull request.

## Scope

In scope: the milestone-state row of "What does not transfer", which the diff against c37afc9 changes in two ways. It no longer names M3, and it adds the sentence telling an instance to remove its milestone from `building` in the commit that signs its record off. Also read, as touched by it: the page's opening, "The kit", the rest of "What does not transfer", and the front matter (`proof: unproven`, `prove-by: M5`, `last-reviewed: 2026-11-23`). Read beside it: `AGENTS.md`, `CLAUDE.md`, `INDEX.md`, decision 0006, decision 0007's paragraph on seeded files, `kit/kit.json`'s entries for `workspace.json`, `.gitignore`, `parts/` and `tests/`, `docs/templates/milestone-record.md`, `docs/changing-the-machinery.md`'s machinery table, `docs/procedure-endings.md`'s "Where the commit goes", and the machinery diff `origin/main..c37afc9`. Ran `python3 ws.py check` in the worktree with the change uncommitted: exit 0, no finding on this page.

## Findings

| # | Class | Where | Finding | Disposition |
|---|---|---|---|---|
| 1 | step | "What does not transfer", the milestone-state row | Not blocking. The row says "Remove it from `building` in the commit that signs its record off". In an instance that commit changes `workspace.json`, which the instance's `direct_push` part lists as machinery, so it reaches main only through a pull request. A milestone record is a page, and procedure endings sends a change of pages only straight to main. The row does not say the sign-off is now machinery. Verified: `kit/kit.json` seeds `workspace.json` from this one, setting only `building` and the review index's `required` list; this workspace's `direct_push` entry lists `workspace.json`. Inferred: that the instance keeps that list, and that its pre-push hook refuses a sign-off pushed straight to main. Not blocking: the page names no push, and procedure endings routes a commit that changes the manifest to a branch. | fixed: the row now says the manifest is machinery, so the sign-off commit merges through a pull request, and links changing the machinery. |

## Checked with no finding

- contradiction: "names the milestone being built here and nothing in an instance the kit makes" holds: `workspace.json` names M4 at c37afc9, and `kit/kit.json` sets `building` to `[]` (verified, read). "Once step 3's plan is approved … set `building`" agrees with the new test in `tests/test_m3_a.py`, which requires an approved plan for each milestone listed (verified, read).
- trigger: the row's change touches no purpose line, **In short** line or index row; `INDEX.md` routes adoption to this page as before (verified, read).
- enforcement: the new sentence's stated enforcement, that the `proof` check fails an entry whose record is signed off, is true: `proof#a building entry whose milestone record is signed off fails` (verified, case in the diff; `parts/` is synced to an instance per `kit/kit.json`).
- placement: the sentence sits in the row that already tells an instance how to set `building`, beside the rule on choosing a milestone number (verified, read).
- eval-case: the page is marked `proof: unproven` with `prove-by: M5` (verified, front matter).
