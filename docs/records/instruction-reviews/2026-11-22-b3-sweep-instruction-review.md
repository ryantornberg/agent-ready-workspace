---
kind: record
last-reviewed: 2026-11-22
covers: docs/playbooks/instruction-review.md
reviewed-at: f757aed, with the uncommitted change of the B3 builder
---

# Instruction review: docs/playbooks/instruction-review.md

This records the review of B3's fix-round sentence on checking sources, for its author and for the reviewer who follows step 3.

**In short:** 1 finding, not blocking: 1 step. Step 3 gives no default for a source the reviewer cannot open, and no class for a credit the source does not support.

## Scope

In scope: the sentence the fix round added to step 3, shown by `git diff -- docs/playbooks/instruction-review.md`, read in the context of the whole page. It has the reviewer open each source under a page's `## References` heading and check its credit.

Read beside it: `AGENTS.md`, `INDEX.md`, `docs/procedure-endings.md`, `docs/reader-standard.md` ("References"), `docs/authoring.md`, `docs/agent-settings.md` ("The documentation domains"), the page's own record `2026-11-22-b3-instruction-review.md`, and B3's row and the 2026-11-22 entries naming B3 in the M3 plan. Ran `python3 ws.py check` in the worktree: exit 0, with one unrelated `eval_record` warning on fix a bug.

## Findings

| # | Class | Where | Finding | Disposition |
|---|---|---|---|---|
| 1 | step | Steps, step 3; The six checks | Not blocking. Step 3 says to open each source and check its credit, with no default for two cases. First, a source the reviewer cannot open: one gone, behind a login, or outside the eight domains Claude Code may fetch without asking. Second, a source that does not say what the page credits it for: "Each finding gets exactly one class", and no class names a wrong credit. Verified: the eight domains in agent settings, and the six classes. Inferred: an unattended reviewer's fetch outside those domains is refused. | open |

## Checked with no finding

- contradiction: the sentence matches the reader standard's "References", which links "Steps" and names step 3, and its rule that a source is credit only. Verified.
- trigger: the purpose sentence, the **In short** line and "When it runs" are unchanged and still fit; the sentence fires only where a page has the heading. Verified.
- enforcement: the sentence is a step duty, like step 3's others, such as verifying each finding, none of which has its own rules row. The builder's side is the reader standard's `prose` row. Verified.
- placement: the duty is stated here once, and the reader standard links it instead of restating it. Nothing from procedure endings is restated. Verified.
- eval-case: the page is unproven with `prove-by: M4`. Verified.
