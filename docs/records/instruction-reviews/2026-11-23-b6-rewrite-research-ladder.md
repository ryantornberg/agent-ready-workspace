---
kind: record
last-reviewed: 2026-11-23
covers: plugin/skills/research-ladder/SKILL.md
reviewed-at: 1a276e9, with the staged change of slice B6
---

# Instruction review: plugin/skills/research-ladder/SKILL.md

This records the review of the research-ladder wrapper's rewritten description, after the first selection run, for its author and its readers.

**In short:** 1 finding: 1 trigger, not blocking. The new triggers are the fires case's question split in two, and they drop the old "a topic", so several of the page's starting points no longer have words to match.

## Scope

In scope: the `description` line, the only line the staged change alters (`git diff --cached`); the body is unchanged. Read beside it: `AGENTS.md`, `INDEX.md`'s search aliases, `docs/playbooks/README.md`, `docs/research-ladder.md`, every other wrapper's description under `plugin/skills/`, every case's `prompt.md` under `plugin/evals/`, `evals/selection/2026-11-23/aggregate-result.json`, "The wrappers' selection cases" in `evals/README.md`, criterion 22 of `docs/plans/m3-reading-layer-machinery-and-kit.md`, the B6 record `2026-11-23-b6-wrapper-research-ladder.md`, and the `wrappers` and `loaded_size` entries in `workspace.json`. Neighbours read against the rewrite: `workspace:search-every-source`, whose first fires case is this wrapper's quiet case and whose first quiet case is this wrapper's fires case, and `workspace:reuse-checklist` and `workspace:impact-analysis`, which also search the code.

Run, on macOS: `python3 ws.py check` exits 0, with only `eval_record`'s usual no-base warning; `python3 ws.py selftest` reports `wrappers: 18 of 18 cases` and `loaded_size: 4 of 4 cases`; `claude plugin validate plugin`, on Claude Code 2.1.331, passes with warnings (verified). The 28 descriptions come to 8,613 bytes against the 9,000-byte ceiling, 924 more than at the base commit; this one is 357 bytes, up from 299 (verified). In the first selection run, on haiku, the fires case passed 0 of 3 runs and the quiet case 3 of 3 (verified, reading the result). No run has read the rewritten description, so every claim below about what it fires on is inferred.

## Findings

| # | Class | Where | Finding | Disposition |
|---|---|---|---|---|
| 1 | trigger | Front matter, `description`, "where something is defined or kept in this workspace, what a name or an everyday term refers to here" | Not blocking. The fires case reads "Where in this workspace is the nightly job defined?" (verified, reading). The rewrite's first two triggers are that question split in two: "where something is defined ... in this workspace", and an everyday term, "the nightly job" being an alias `INDEX.md` maps to `ReconciliationWorker` (verified, reading). The old trigger, "find code or a page in this workspace, with a name or a topic in hand", followed the page's "Pick one lookup" table (verified, reading the diff). The rewrite drops "a topic". The page's rows for a topic with no name and for text that is not a name, such as an error message, now have no words in the description to match, unless "kept" is read to take them in (inferred). Name the page's starting points rather than the case's question, such as "whenever a request needs code or a page found in this workspace, with a name, an everyday term, a topic or a piece of text in hand". Not blocking: the contract's "Finding things" loads in every session and gives the same lookups (verified, reading `AGENTS.md`). | fixed: the old trigger, "find code or a page in this workspace, with a name or a topic in hand, by the cheapest lookup", in the new frame. |

## Checked with no finding

- contradiction: the library clause, "how a library or tool behaves, from its live documentation", matches the page's row for it (verified, reading). The neighbour it names, `workspace:search-every-source`, exists and names this wrapper back for a question the workspace alone answers (verified).
- step: the body is unchanged and names `docs/research-ladder.md`, which exists; the `wrappers` check passes (verified).
- enforcement: the description states no must or never. The `wrappers` check holds its name, page, neighbours and cases, and its cases pass (verified).
- placement: the description says when to fire and when not, and restates no step of the page (verified, reading).
- eval-case: both selection cases exist (verified). The quiet case, a report from the tracker and the team wiki, stays with `workspace:search-every-source`, which the description names (inferred). The page is marked unproven with `prove-by: M4`.

## Re-check

A fresh session at the driver tier re-read the staged description on 2026-11-23, after the fix round, against its page, every other wrapper's description and the neighbours' selection cases in `plugin/evals/`. `python3 ws.py check` exits 0, with only `eval_record`'s usual no-base warning, and `python3 ws.py selftest` reports `wrappers: 18 of 18 cases` and `loaded_size: 4 of 4 cases` (verified). The 28 descriptions now come to 8,449 bytes against the 9,000-byte ceiling (verified). No selection run has read the final descriptions, so every claim about what they fire on is inferred.

| # | Verdict | Evidence |
|---|---|---|
| 1 | fixed | After "Use it first whenever you need to", the trigger is the base's word for word: "find code or a page in this workspace, with a name or a topic in hand, by the cheapest lookup" (verified, `git diff --cached`). "A name or a topic" is the how-to index row's wording; the fires case's "where ... defined" and "nightly job" are gone (verified, reading). Text that is not a name stays unnamed, as at the base (verified). This description is 347 bytes (verified). The restored breadth together with "Use it first" has a cost; see R1. |

| # | Kind | Finding | Disposition |
|---|---|---|---|
| R1 | broke | trigger. Not blocking. "Use it first whenever you need to find code ... with a name or a topic in hand" now claims, ahead of the rest, the reuse checklist's fires case, "check whether the code already has something that does the job", which asks to find code by topic (verified, reading; the match is inferred). The base said "Use when", and the first rewrite's trigger was narrower, "where something is defined or kept in this workspace" (verified, reading this record's quote). The description names no boundary with `workspace:reuse-checklist`, whose page owns the search before new logic and runs its rows "as in the research ladder" (verified, reading). An agent that loads only this wrapper finds code but writes no searched line and reads no prescribed pattern (inferred). Not blocking: the reuse checklist's description matches that request more closely, and loading both costs a read (inferred). Add "nor to find code to reuse before writing new logic (workspace:reuse-checklist)", or drop "first". | fixed (second round): the Not clause adds "nor to look for existing code before writing new logic (workspace:reuse-checklist)". |

What the first reading missed: nothing found. R1 is the fix round's, since the first rewrite's narrower trigger did not reach the reuse request.

## Second re-check

A fresh session at the driver tier re-read the unstaged second-round change on 2026-11-23, on commit 1a276e9, against its page, every other wrapper's description and the selection cases in `plugin/evals/`. `python3 ws.py check` exits 0, with only `eval_record`'s usual no-base warning, and `python3 ws.py selftest` exits 0, reporting `wrappers: 18 of 18 cases` and `loaded_size: 4 of 4 cases` (verified). The 28 descriptions now come to 8,542 bytes against the 9,000-byte ceiling (verified). No selection run has read these descriptions, so every claim about what they fire on is inferred.

| # | Verdict | Evidence |
|---|---|---|
| R1 | fixed | The Not clause adds "nor to look for existing code before writing new logic (workspace:reuse-checklist)" (verified, `git diff`). That is the reuse checklist page's moment, "before you write new logic in code under `src/`", and the same boundary impact analysis's description draws, "nor to find code to reuse (workspace:reuse-checklist)" (verified, reading). The reuse checklist fires case, "Before I write a new date-formatting helper ... check whether the code already has something that does the job", now meets this boundary by its own words (verified, reading; the routing is inferred). "Use it first" stays, which the R1 suggestion allowed. This description is 428 bytes (verified). |

Nothing this round broke was found. The research ladder fires case, "Where in this workspace is the nightly job defined?", writes no new logic, so the new clause does not reach it (verified, reading; the routing is inferred).
