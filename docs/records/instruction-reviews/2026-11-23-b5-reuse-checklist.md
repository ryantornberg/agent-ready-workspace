---
kind: record
last-reviewed: 2026-11-23
covers: docs/playbooks/reuse-checklist.md
reviewed-at: dace91e, with the uncommitted change of the B5 slice session
---

# Instruction review: docs/playbooks/reuse-checklist.md

This records the review of B5's added sentence in the reuse checklist's "Where to search", for its author and its readers.

**In short:** 1 finding, none blocking: 1 enforcement. The new rule, that a claim of fit names the code and what you will call, has no rules-table row, and no reviewer step checks that the named code really does the job.

## Scope

In scope: the sentence added to "Where to search", "A claim that something fits names it, and the line names what you will call: scope was once cut because the code 'already covered it', and it did not." The whole page was read, with `git diff HEAD`. Read beside it: `AGENTS.md`, `INDEX.md`, `docs/layout.md`, `docs/authoring.md`, `docs/procedure-endings.md`, `docs/research-ladder.md`'s link target, and the pages the changed section links.

Runs (verified): `python3 ws.py check` exits 0 in the worktree, with only the `eval_record` warning about a missing base commit.

## Findings

| # | Class | Where | Finding | Disposition |
|---|---|---|---|---|
| 1 | enforcement | "Where to search", the added sentence, and "Rules" | Not blocking. The sentence is a rule, and the rules table has no row for it, though its neighbour "A claim that nothing fits needs every search row run" has one, tagged `prose` (verified, reading "Rules"). The incident it cites is a fit claimed that did not hold. Naming the code does not catch that on its own. The reviewer's reply patterns are `no searched line`, `missed helper`, `repeated logic` and the four debt patterns, and none checks that the code the author named does what the new logic needs (verified, reading reviewer's step 4). So a named but wrong fit passes both halves (inferred). | fixed in part: the sentence is now the reason the searched line names the code found, not a new rule. The reviewer's lack of a check that the named code does the job predates this change: a known defect, for M6 |

## Checked with no finding

- contradiction: "the line" is the searched line. The **In short** line and "say so in your line" below the table introduce it, and the author's step 5 gives its form, `found <the names, or nothing that fits>; using <what you will call, extend or write>`, which already asks for both names (verified). Step 3's "call, extend or write" and the new "what you will call" agree, since an extended helper is still called (inferred).
- step: the sentence names no command or path. The table's commands are unchanged (not re-run).
- trigger: the purpose and **In short** lines are unchanged and still cover the new sentence, which concerns the searched line they name (verified).
- placement: the rule sits beside "A claim that nothing fits needs every row run", its pair, on the page that owns the searched line. The style guide's "state what is true now" is read as barring a page's own history, not a one-line reason for a rule (inferred).
- eval-case: the page is `proof: unproven` with `prove-by: M6` (verified, reading its front matter).

## Known defects

- The reviewer's step 4 has no check that the code the author's line names does what the new logic needs. This predates slice B5. For M6, the page's `prove-by` milestone.

## Re-check

A fresh driver-tier session read the changed passage as it stands, with `git diff HEAD -- docs/playbooks/reuse-checklist.md`, beside the author's step 5, the reviewer's steps 1 to 6 and "Rules", and ran `python3 ws.py check` (exit 0, only the `eval_record` warning).

| # | Verdict | Evidence |
|---|---|---|
| 1 | upheld | The sentence now reads "The searched line names the code found, so a reviewer can check a claim that existing code already covers the case; such a claim made from memory is often wrong": a reason for step 5's existing form, `found <the names ...>; using <what you will call, extend or write>`, not a new must (verified, reading). The reviewer's missing check is in "Known defects", for M6, and the finding was not blocking (verified). |

What a fix broke:

- None.

What the first reading missed:

- None.
