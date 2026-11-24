---
kind: record
last-reviewed: 2026-11-23
covers: plugin/skills/instruction-review/SKILL.md
reviewed-at: 1a276e9, with the staged change of slice B6
---

# Instruction review: plugin/skills/instruction-review/SKILL.md

This records the review of the instruction-review wrapper's rewritten description, after the first selection run, for its author and its readers.

**In short:** 1 finding: 1 trigger, not blocking. The new trigger, "need their review before a commit", is the fires case's own sentence, where the old one named the event that needs a review.

## Scope

In scope: the `description` line, the only line the staged change alters (`git diff --cached`); the body is unchanged. Read beside it: `AGENTS.md`, `docs/playbooks/README.md`, `docs/playbooks/instruction-review.md`, every other wrapper's description under `plugin/skills/`, every case's `prompt.md` under `plugin/evals/`, `evals/selection/2026-11-23/aggregate-result.json`, "The wrappers' selection cases" in `evals/README.md`, criterion 22 of `docs/plans/m3-reading-layer-machinery-and-kit.md`, the B6 record `2026-11-23-b6-wrapper-instruction-review.md`, and the `wrappers`, `loaded_size` and `review_trailer` entries in `workspace.json`. Neighbours read against the rewrite: `workspace:docs-audit`, whose fires case is this wrapper's quiet case and whose quiet case is this wrapper's fires case, and `workspace:extend-the-workspace`.

Run, on macOS: `python3 ws.py check` exits 0, with only `eval_record`'s usual no-base warning; `python3 ws.py selftest` reports `wrappers: 18 of 18 cases` and `loaded_size: 4 of 4 cases`; `claude plugin validate plugin`, on Claude Code 2.1.331, passes with warnings (verified). The 28 descriptions come to 8,613 bytes against the 9,000-byte ceiling, 924 more than at the base commit; this one is 443 bytes, up from 368 (verified). In the first selection run, on haiku, the fires case passed 1 of 3 runs and the quiet case 3 of 3 (verified, reading the result). No run has read the rewritten description, so every claim below about what it fires on is inferred.

## Findings

| # | Class | Where | Finding | Disposition |
|---|---|---|---|---|
| 1 | trigger | Front matter, `description`, "and need their review before a commit" | Not blocking. The fires case reads "I edited docs/size-the-work.md and the glossary. They need their review before I commit them." (verified, reading). The rewrite's "need their review before a commit" is that sentence in the description's words; the old trigger was the event, "a commit adds, changes or deletes a guidance page" (verified, reading the diff). The case now tests whether the request repeats that phrase more than whether the model routes a guidance change here (inferred). Requests of the same kind in other words, such as "write the review record for my change to the debugging playbook" or "my commit was refused for a missing Instructions-review trailer", keep only "pages that guide agents were added, changed or deleted" to match (inferred). Lead with the event and the refusal it causes, such as "whenever a commit or a staged change adds, changes or deletes a guidance page, or a commit is refused for a missing Instructions-review trailer". Not blocking: a missed fire costs a refused commit, since the commit hook, the pre-push hook and CI refuse a guidance change with no trailer (verified, reading the page's "Where it is checked"). | fixed: "before committing any change that adds, changes or deletes a guidance page", the old trigger in the new frame. |

## Checked with no finding

- contradiction: the list of guidance pages and "as the review_trailer entry in workspace.json lists" match the page's "When it runs" and the catalog row (verified, reading). The neighbour it names, `workspace:docs-audit`, exists and names this wrapper back for "the pages one commit changes" (verified). Extend the workspace's new first sentence also matches the fires case; that is recorded in `2026-11-23-b6-rewrite-extend-the-workspace.md`.
- step: the body is unchanged and names `docs/playbooks/instruction-review.md`, which exists; the `wrappers` check passes (verified).
- enforcement: the description states no must or never. The `wrappers` check holds its name, page, neighbours and cases, and its cases pass (verified).
- placement: the description says when to fire and when not, and restates no step of the page (verified, reading).
- eval-case: both selection cases exist (verified). The quiet case, a whole-tree drift read before sign-off, stays with `workspace:docs-audit`, which the description names (inferred). The page is marked unproven with `prove-by: M4`.

## Re-check

A fresh session at the driver tier re-read the staged description on 2026-11-23, after the fix round, against its page, every other wrapper's description and the neighbours' selection cases in `plugin/evals/`. `python3 ws.py check` exits 0, with only `eval_record`'s usual no-base warning, and `python3 ws.py selftest` reports `wrappers: 18 of 18 cases` and `loaded_size: 4 of 4 cases` (verified). The 28 descriptions now come to 8,449 bytes against the 9,000-byte ceiling (verified). No selection run has read the final descriptions, so every claim about what they fire on is inferred.

| # | Verdict | Evidence |
|---|---|---|
| 1 | fixed | The trigger is the event again, "before committing any change that adds, changes or deletes a guidance page" (verified, reading). "Need their review" is gone from this description (verified, searching it). The finding's second suggestion, a commit refused for a missing trailer, was not taken; the finding asked for the kind of request, and the event covers a refused commit's change (inferred). The list of guidance pages still matches the page's "When it runs" and ends "as the review_trailer entry in workspace.json lists", which also covers the kit's seed pages the list leaves out (verified, reading `workspace.json`). This description is 416 bytes (verified). The phrase the finding named moved into extend the workspace's Not clause, recorded there as R1. |

What the first reading missed: nothing found. Docs audit's "after a batch of page changes" could meet the fires case's two edited pages, but its "Not for the pages one commit changes" names this wrapper for them (verified, reading).
