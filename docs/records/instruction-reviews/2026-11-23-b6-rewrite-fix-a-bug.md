---
kind: record
last-reviewed: 2026-11-23
covers: plugin/skills/fix-a-bug/SKILL.md
reviewed-at: 1a276e9, with the staged change of slice B6
---

# Instruction review: plugin/skills/fix-a-bug/SKILL.md

This records the review of the fix-a-bug wrapper's rewritten description, after the first selection run, for its author and its readers.

**In short:** 2 findings: 2 trigger, not blocking. The exclusion for an unknown cause now holds only when the request asks why, which fits the quiet case's wording and moves the boundary with debugging; and "fix something" carries no size, so a fix of unclear size is claimed here first as well as by size the work.

## Scope

In scope: the `description` line, the only line the staged change alters (`git diff --cached`); the body is unchanged. Read beside it: `AGENTS.md`, `docs/playbooks/README.md`, `docs/playbooks/fix-a-bug.md`, every other wrapper's description under `plugin/skills/`, every case's `prompt.md` under `plugin/evals/`, `evals/selection/2026-11-23/aggregate-result.json`, "The wrappers' selection cases" in `evals/README.md`, criterion 22 of `docs/plans/m3-reading-layer-machinery-and-kit.md`, the B6 record `2026-11-23-b6-wrapper-fix-a-bug.md`, and the `wrappers`, `loaded_size` and `eval_record` entries in `workspace.json`. Neighbours read against the rewrite: `workspace:debugging`, whose fires case is this wrapper's quiet case; `workspace:size-the-work`, whose quiet case is this wrapper's fires case; `workspace:safe-refactor`, `workspace:extend-the-workspace`, `workspace:feedback-walkthrough` and `workspace:test-first`.

Run, on macOS: `python3 ws.py check` exits 0, with only `eval_record`'s usual no-base warning; `python3 ws.py selftest` reports `wrappers: 18 of 18 cases` and `loaded_size: 4 of 4 cases`; `claude plugin validate plugin`, on Claude Code 2.1.331, passes with warnings (verified). The 28 descriptions come to 8,613 bytes against the 9,000-byte ceiling, 924 more than at the base commit; this one is 575 bytes, up from 420, and the longest (verified). In the first selection run, on haiku, the fires case passed 0 of 3 runs and the quiet case 3 of 3 (verified, reading the result). No run has read the rewritten description, so every claim below about what it fires on is inferred.

## Findings

| # | Class | Where | Finding | Disposition |
|---|---|---|---|---|
| 1 | trigger | Front matter, `description`, its "Not when" clause, "when the request asks why a failure happens and its cause is unknown" | Not blocking. The old clause was "Not when the cause is still unknown"; the rewrite excludes an unknown cause only when the request asks why (verified, reading the diff). The catalog's "Before you pick one" sends a bug to debugging whenever its reason cannot yet be said, whatever the request asks: "When you cannot yet say what that reason is, start at debugging" (verified, reading). A request such as "the checkout test fails now and then and nobody knows why; fix it" asks for a fix, so it now matches this description's "whenever a request asks to fix something" as well as debugging's "reports a failure nobody can explain yet" (inferred). The new wording fits the quiet case, which ends "Can you work out what is going on?", so that case still passes while the boundary it was written to test has moved (inferred). Restore the kind: "Not when the cause is still unknown, even when the request asks for a fix (workspace:debugging)". Not blocking: the page's step 1 says that if you cannot make the test fail, "report that, and do not guess at a fix", so an agent that loads this wrapper for an unknown cause reports rather than guesses (verified, reading). | fixed: "Not when the cause is still unknown (workspace:debugging)", as before the rewrite. |
| 2 | trigger | Front matter, `description`, "whenever a request asks to fix something or make a small change in one repository that is easy to reverse and under a day of work" | Not blocking. The size terms bind to "make a small change"; "fix something" stands without them, and "Use it first, before reading or changing code" puts this wrapper ahead of the rest (verified, reading). `workspace:size-the-work` claims a change "when its size is unclear" (verified, reading). A fix whose size is not yet known, such as "fix the refund rounding in the API and the web front end", now matches both, and this one says to go first (inferred). The "Not ... when the change is bigger" clause helps only once the size is known. Put the size terms on both halves, such as "to fix something or make another change that is small: in one repository, easy to reverse and under a day of work". Not blocking: the contract's "How work flows" loads in every session and sends anything else up the size gate's ladder, and the page says "If the bug turns out to be bigger than that, stop and say so" (verified, reading). | fixed: "fix a bug or make another change that is small: in one repository, easy to reverse and under a day of work", and size-the-work takes a change "bigger or its size unclear". |

## Checked with no finding

- contradiction: "fixing a bug or making another small code change" matches the catalog row and its "whether or not it is a bug", and the contract's routing of a small change (verified, reading). The five neighbours it names, `workspace:debugging`, `workspace:safe-refactor`, `workspace:extend-the-workspace`, `workspace:size-the-work` and `workspace:feedback-walkthrough`, exist; the `wrappers` check passes (verified).
- step: the body is unchanged and names `docs/playbooks/fix-a-bug.md`, which exists (verified).
- enforcement: the description states no must or never. The page is proven, but `eval_record` reads the playbooks under `docs/playbooks`, not the wrappers, and `python3 ws.py check` passes with the staged change (verified, reading `workspace.json` and running the check).
- placement: "before reading or changing code" says when to load the wrapper, not how to work, and the description restates no step of the page (verified, reading).
- eval-case: both selection cases exist (verified). The fires case, a CSV column bug with a plain fix request, matches "asks to fix something", the kind of request rather than its words (inferred). No case tests the boundary of finding 1 from this side with a fix request.

## Re-check

A fresh session at the driver tier re-read the staged description on 2026-11-23, after the fix round, against its page, every other wrapper's description and the neighbours' selection cases in `plugin/evals/`. `python3 ws.py check` exits 0, with only `eval_record`'s usual no-base warning, and `python3 ws.py selftest` reports `wrappers: 18 of 18 cases` and `loaded_size: 4 of 4 cases` (verified). The 28 descriptions now come to 8,449 bytes against the 9,000-byte ceiling (verified). No selection run has read the final descriptions, so every claim about what they fire on is inferred.

| # | Verdict | Evidence |
|---|---|---|
| 1 | fixed | The clause is "Not when the cause is still unknown (workspace:debugging)", word for word the base's (verified, `git diff --cached`). It holds whatever the request asks, as the catalog's "Before you pick one" does (verified, reading). |
| 2 | fixed | "fix a bug or make another change that is small: in one repository, easy to reverse and under a day of work" puts the size terms on both halves through "another change that is small" (verified, reading). The Not clause now gives a change "bigger or its size unclear" to `workspace:size-the-work`, which matches size the work's "when its size is unclear" (verified, reading both). That added "or its size unclear" has a cost; see R1. This description is 529 bytes, still the longest (verified). |

| # | Kind | Finding | Disposition |
|---|---|---|---|
| R1 | broke | trigger. Not blocking. The fix added "or its size unclear" to the Not clause. A plain bug report seldom states its size: neither the page's own example, "the Export button does nothing, fix it", nor the fires case, "The CSV export on the orders page puts each order's date in the wrong column. Please fix it", does (verified, reading). That fires case is also size the work's quiet case (verified). Whether the size is "unclear" is now the model's call, and on an unsized request this description itself points to size the work, so the fires case may lean there (inferred). Not blocking: size the work's description sends a change that passes the gate back here, and the catalog's "Before you pick one" puts every change request through the gate (verified, reading). Drop "or its size unclear" and leave unclear size to size the work's own description, as the base did. | fixed (second round): "or its size unclear" is gone; size-the-work takes a change that is bigger. |

What the first reading missed: nothing found. R1 is the fix round's. The overlap of this description's "Use it first" with the reuse checklist's new trigger is recorded in `2026-11-23-b6-rewrite-reuse-checklist.md`, R1.

## Second re-check

A fresh session at the driver tier re-read the unstaged second-round change on 2026-11-23, on commit 1a276e9, against its page, every other wrapper's description and the selection cases in `plugin/evals/`. `python3 ws.py check` exits 0, with only `eval_record`'s usual no-base warning, and `python3 ws.py selftest` exits 0, reporting `wrappers: 18 of 18 cases` and `loaded_size: 4 of 4 cases` (verified). The 28 descriptions now come to 8,542 bytes against the 9,000-byte ceiling (verified). No selection run has read these descriptions, so every claim about what they fire on is inferred.

| # | Verdict | Evidence |
|---|---|---|
| R1 | fixed | "or its size unclear" is gone. The Not clause is now word for word the base's, from "Not when the cause is still unknown" to "(workspace:feedback-walkthrough)" (verified, comparing with `git show HEAD`). Unclear size stays with size the work's description, "or when its size is unclear", and with its page's gate, "If any one fails, or you cannot tell, climb the ladder" (verified, reading). This description is 509 bytes, still the longest (verified). |

Nothing this round broke was found. The reuse checklist's description no longer says "Use it first", so the overlap noted in its record's R1 is gone; four descriptions now say "Use it first": debugging, fix a bug, research ladder and safe refactor (verified, searching them).
