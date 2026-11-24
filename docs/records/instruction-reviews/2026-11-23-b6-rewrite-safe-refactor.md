---
kind: record
last-reviewed: 2026-11-23
covers: plugin/skills/safe-refactor/SKILL.md
reviewed-at: 1a276e9, with the staged change of slice B6
---

# Instruction review: plugin/skills/safe-refactor/SKILL.md

This records the review of the safe-refactor wrapper's rewritten description, after the first selection run, for its author and its readers.

**In short:** no findings. The rewrite names the kinds of refactor and keeps the page's test of one, "without changing what it does", and its neighbours are unchanged.

## Scope

In scope: the `description` line, the only line the staged change alters (`git diff --cached`); the body is unchanged. Read beside it: `AGENTS.md`, `docs/playbooks/README.md`, `docs/safe-refactor.md`, every other wrapper's description under `plugin/skills/`, every case's `prompt.md` under `plugin/evals/`, `evals/selection/2026-11-23/aggregate-result.json`, "The wrappers' selection cases" in `evals/README.md`, criterion 22 of `docs/plans/m3-reading-layer-machinery-and-kit.md`, the B6 record `2026-11-23-b6-wrapper-safe-refactor.md`, and the `wrappers` and `loaded_size` entries in `workspace.json`. Neighbours read against the rewrite: `workspace:test-first`, whose quiet case is this wrapper's fires case and whose fires case is this wrapper's quiet case; `workspace:fix-a-bug`, `workspace:debugging`, `workspace:size-the-work`, `workspace:impact-analysis` and `workspace:maintain-the-workspace`.

Run, on macOS: `python3 ws.py check` exits 0, with only `eval_record`'s usual no-base warning; `python3 ws.py selftest` reports `wrappers: 18 of 18 cases` and `loaded_size: 4 of 4 cases`; `claude plugin validate plugin`, on Claude Code 2.1.331, passes with warnings (verified). The 28 descriptions come to 8,613 bytes against the 9,000-byte ceiling, 924 more than at the base commit; this one is 362 bytes, up from 244 (verified). In the first selection run, on haiku, the fires case passed 0 of 3 runs and the quiet case 3 of 3 (verified, reading the result). No run has read the rewritten description, so every claim below about what it fires on is inferred.

## Findings

| # | Class | Where | Finding | Disposition |
|---|---|---|---|---|

No findings.

## Checked with no finding

- contradiction: "rename, move, split, merge or restructure code under src/ without changing what it does" matches the page's purpose line and step 1's test of a refactor, "same inputs, same outputs, same side effects" (verified, reading). The three neighbours it names, `workspace:fix-a-bug`, `workspace:test-first` and `workspace:debugging`, exist, and fix a bug and test first name this wrapper back (verified).
- step: the body is unchanged and names `docs/safe-refactor.md`, which exists; the `wrappers` check passes (verified).
- trigger: the fires case asks only to rename, and "without changing what it does" was already in the old description, so the five verbs are the kinds of refactor, not the case's words alone (verified, reading the diff and the case). The quiet case, a plan's slice that adds a status, changes behavior and stays outside (inferred). A refactor across two repositories also matches size the work's "when its size is unclear", but the page's step 2 runs the size gate itself, so loading this wrapper first is what the page asks (verified, reading). Maintain the workspace fires after a change that renames a code name, which follows a rename rather than competing for it (inferred).
- enforcement: the description states no must or never. The `wrappers` check holds its name, page, neighbours and cases, and its cases pass (verified).
- placement: "before changing code" says when to load the wrapper, not how to work, and the description restates no step of the page (verified, reading).
- eval-case: both selection cases exist (verified). The page is marked unproven with `prove-by: M4`.

## Re-check

A fresh session at the driver tier re-read the staged description on 2026-11-23, after the fix round, against its page, every other wrapper's description and the neighbours' selection cases in `plugin/evals/`. `python3 ws.py check` exits 0, with only `eval_record`'s usual no-base warning, and `python3 ws.py selftest` reports `wrappers: 18 of 18 cases` and `loaded_size: 4 of 4 cases` (verified). The 28 descriptions now come to 8,449 bytes against the 9,000-byte ceiling (verified). No selection run has read the final descriptions, so every claim about what they fire on is inferred.

| # | Verdict | Evidence |
|---|---|---|

No findings to rule on: the first reading recorded none. The final description still holds the text that reading quoted, "rename, move, split, merge or restructure code under src/ without changing what it does", and is 362 bytes (verified, reading).

What the first reading missed: nothing found. "Rename" is the first of five verbs, the page's step 4 names moving and renaming, and "without changing what it does" predates the rewrite, so the description is not fitted to the fires case's words (verified, reading). Test first's fires case, this wrapper's quiet case, adds behavior and stays outside (inferred).
