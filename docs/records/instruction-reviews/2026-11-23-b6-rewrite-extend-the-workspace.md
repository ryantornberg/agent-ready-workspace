---
kind: record
last-reviewed: 2026-11-23
covers: plugin/skills/extend-the-workspace/SKILL.md
reviewed-at: 1a276e9, with the staged change of slice B6
---

# Instruction review: plugin/skills/extend-the-workspace/SKILL.md

This records the review of the extend-the-workspace wrapper's rewritten description, after the first selection run, for its author and its readers.

**In short:** 1 finding: 1 trigger, not blocking. The new first sentence claims every change to pages, wider than the sentence after it and the page, and now matches the instruction review's request too.

## Scope

In scope: the `description` line, the only line the staged change alters (`git diff --cached`); the body is unchanged. Read beside it: `AGENTS.md`, `docs/playbooks/README.md`, `docs/extend-the-workspace.md`, every other wrapper's description under `plugin/skills/`, every case's `prompt.md` under `plugin/evals/`, `evals/selection/2026-11-23/aggregate-result.json`, "The wrappers' selection cases" in `evals/README.md`, criterion 22 of `docs/plans/m3-reading-layer-machinery-and-kit.md`, the B6 record `2026-11-23-b6-wrapper-extend-the-workspace.md`, and the `wrappers` and `loaded_size` entries in `workspace.json`. Neighbours read against the rewrite: `workspace:parts`, whose fires case is this wrapper's quiet case; `workspace:instruction-review`, `workspace:maintain-the-workspace` and `workspace:size-the-work`; and `workspace:search-every-source`, whose second quiet case, a glossary row edit, this wrapper owns.

Run, on macOS: `python3 ws.py check` exits 0, with only `eval_record`'s usual no-base warning; `python3 ws.py selftest` reports `wrappers: 18 of 18 cases` and `loaded_size: 4 of 4 cases`; `claude plugin validate plugin`, on Claude Code 2.1.331, passes with warnings (verified). The 28 descriptions come to 8,613 bytes against the 9,000-byte ceiling, 924 more than at the base commit; this one is 357 bytes, up from 255 (verified). In the first selection run, on haiku, the fires case passed 1 of 3 runs and the quiet case 3 of 3 (verified, reading the result). No run has read the rewritten description, so every claim below about what it fires on is inferred.

## Findings

| # | Class | Where | Finding | Disposition |
|---|---|---|---|---|
| 1 | trigger | Front matter, `description`, its first sentence, "This workspace's procedure for adding or changing its pages" | Not blocking. The first sentence claims every change to pages, with no limit. The sentence after it keeps the old one, "a small change to pages only", and the page's "What this page covers" sends moving, renaming or archiving a page to layout and maintain the workspace (verified, reading). `workspace:maintain-the-workspace` claims the upkeep "after a change that moves a page", and `workspace:size-the-work` sends here only a pages-only change that passes the gate (verified, reading their descriptions). The instruction review's fires case, "I edited docs/size-the-work.md and the glossary. They need their review before I commit them", is a change to pages as well, and this sentence now matches it beside `workspace:instruction-review` (inferred). Make the first sentence as narrow as the second, such as "for adding a page, or making a small change to pages only", or drop it. Not blocking: the page's In short line ends "Then commit it with its instruction review", so an agent that loads this wrapper for a review still reaches the review (verified, reading). | fixed: "procedure for writing its pages", "a new playbook ...", and the Not clause names workspace:instruction-review for a guidance change's review. |

## Checked with no finding

- contradiction: the five page kinds, "the index rows that route to it" and "a small change to pages only" match the page's "What this page covers" and its kind table (verified, reading). Both neighbours it names, `workspace:parts` and `workspace:maintain-the-workspace`, exist; maintain the workspace names this wrapper back for adding a page (verified).
- step: the body is unchanged and names `docs/extend-the-workspace.md`, which exists; the `wrappers` check passes (verified).
- enforcement: the description states no must or never. The `wrappers` check holds its name, page, neighbours and cases, and its cases pass (verified).
- placement: the description says when to fire and when not, and restates no step of the page (verified, reading).
- eval-case: both selection cases exist (verified). The quiet case, adding a check, stays with `workspace:parts`, which this description names. "the index rows that route to it" for the fires case's "its row in the how-to index" uses the workspace's own word for its routing tables, not the case's alone (inferred). The page is marked unproven with `prove-by: M5`.

## Re-check

A fresh session at the driver tier re-read the staged description on 2026-11-23, after the fix round, against its page, every other wrapper's description and the neighbours' selection cases in `plugin/evals/`. `python3 ws.py check` exits 0, with only `eval_record`'s usual no-base warning, and `python3 ws.py selftest` reports `wrappers: 18 of 18 cases` and `loaded_size: 4 of 4 cases` (verified). The 28 descriptions now come to 8,449 bytes against the 9,000-byte ceiling (verified). No selection run has read the final descriptions, so every claim about what they fire on is inferred.

| # | Verdict | Evidence |
|---|---|---|
| 1 | fixed | The first sentence is now "procedure for writing its pages", and the trigger names a new page of the five kinds or "a small change to pages only", as the page's "What this page covers" and its how-to index row do (verified, reading). It no longer claims a move or a rename, which `workspace:maintain-the-workspace` keeps (verified, reading). The Not clause sends a guidance change's review to `workspace:instruction-review` (verified). This description is 436 bytes (verified). The fix carried a phrase from the instruction review's fires case into this description; see R1. |

| # | Kind | Finding | Disposition |
|---|---|---|---|
| R1 | broke | trigger. Not blocking. The new Not clause, "the review a guidance change needs before its commit", is the instruction review's fires case, "They need their review before I commit them", in this description's words: need, review, before, commit (verified, reading both). That record's finding 1 flagged the same phrase in that wrapper's own description; the fix moved it here rather than dropping it (verified, comparing that record's quote with both final descriptions). The clause routes the request the right way, so no agent goes wrong, but the instruction review's fires case now partly tests whether a neighbour's Not clause repeats its words (inferred). Name the procedure instead, such as "the review of a guidance change (workspace:instruction-review)". | fixed (second round): "the review of a guidance change (workspace:instruction-review)". |
| R2 | missed | contradiction. Not blocking. "Not for a check or a hook (workspace:parts)" sends every hook to parts. Parts' description takes only "a hook on an agent tool's event" and says `workspace:changing-the-machinery` "alone owns a git hook in .githooks/"; changing the machinery's description says the same (verified, reading the three). The clause predates the rewrite, and the first reading's contradiction check named parts without testing this boundary (verified, reading this record). A git hook is not a page, so a request for one seldom meets this clause, and parts' description passes it on (inferred). Say "a check or an agent tool's hook (workspace:parts)", or "a part (workspace:parts)". | fixed (second round): "a check or a hook on an agent tool's event (workspace:parts), a git hook (workspace:changing-the-machinery)". |

What the first reading missed: the hook boundary in R2, which the B6 narrowing of parts' description left one-sided here.

## Second re-check

A fresh session at the driver tier re-read the unstaged second-round change on 2026-11-23, on commit 1a276e9, against its page, every other wrapper's description and the selection cases in `plugin/evals/`. `python3 ws.py check` exits 0, with only `eval_record`'s usual no-base warning, and `python3 ws.py selftest` exits 0, reporting `wrappers: 18 of 18 cases` and `loaded_size: 4 of 4 cases` (verified). The 28 descriptions now come to 8,542 bytes against the 9,000-byte ceiling (verified). No selection run has read these descriptions, so every claim about what they fire on is inferred.

| # | Verdict | Evidence |
|---|---|---|
| R1 | fixed | The Not clause now reads "the review of a guidance change (workspace:instruction-review)": it names the procedure, and of the instruction review fires case's words, "They need their review before I commit them", only "review" is left (verified, reading both). |
| R2 | fixed | The clause now splits the hooks: "a check or a hook on an agent tool's event (workspace:parts), a git hook (workspace:changing-the-machinery)". That is parts' own wording, and parts' description says changing the machinery "alone owns a git hook in .githooks/", which the machinery table on `docs/changing-the-machinery.md` lists (verified, reading the three). The parts quiet case, "I need to change the pre-push hook and the CI workflow", now meets a description here that also points it to changing the machinery (verified, reading; the routing is inferred). This description is 487 bytes (verified). |

Nothing this round broke was found. The page's "What this page covers" still says "a check, a hook or any other part is on parts", which is looser than the description; that sentence predates this round and the description does not contradict it, since the same paragraph sends any change to hooks to changing the machinery (verified, reading).
