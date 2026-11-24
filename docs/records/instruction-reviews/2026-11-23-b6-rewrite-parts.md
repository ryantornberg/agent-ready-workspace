---
kind: record
last-reviewed: 2026-11-23
covers: plugin/skills/parts/SKILL.md
reviewed-at: 1a276e9, with the staged change of slice B6
---

# Instruction review: plugin/skills/parts/SKILL.md

This records the review of the parts wrapper's rewritten description, after the first selection run, for its author and its readers.

**In short:** 1 finding: 1 trigger, not blocking. The new first sentence says "hooks" with no limit, undoing in one sentence the narrowing the B6 review asked for, and the gloss on a check adds "CI"; both words are in the quiet case.

## Scope

In scope: the `description` line, the only line the staged change alters (`git diff --cached`); the body is unchanged. Read beside it: `AGENTS.md`, `docs/playbooks/README.md`, `docs/parts.md`, `docs/changing-the-machinery.md`, every other wrapper's description under `plugin/skills/`, every case's `prompt.md` under `plugin/evals/`, `evals/selection/2026-11-23/aggregate-result.json`, "The wrappers' selection cases" in `evals/README.md`, criterion 22 of `docs/plans/m3-reading-layer-machinery-and-kit.md`, the B6 record `2026-11-23-b6-wrapper-parts.md`, and the `wrappers` and `loaded_size` entries in `workspace.json`. Neighbours read against the rewrite: `workspace:changing-the-machinery`, whose fires case is this wrapper's quiet case, and `workspace:extend-the-workspace`, whose quiet case is this wrapper's fires case.

Run, on macOS: `python3 ws.py check` exits 0, with only `eval_record`'s usual no-base warning; `python3 ws.py selftest` reports `wrappers: 18 of 18 cases` and `loaded_size: 4 of 4 cases`; `claude plugin validate plugin`, on Claude Code 2.1.331, passes with warnings (verified). The 28 descriptions come to 8,613 bytes against the 9,000-byte ceiling, 924 more than at the base commit; this one is 365 bytes, up from 254 (verified). In the first selection run, on haiku, the fires case passed 0 of 3 runs and the quiet case 3 of 3 (verified, reading the result). No run has read the rewritten description, so every claim below about what it fires on is inferred.

## Findings

| # | Class | Where | Finding | Disposition |
|---|---|---|---|---|
| 1 | trigger | Front matter, `description`, its first sentence, "This workspace's procedure for checks and hooks", and "a check, which fails a commit or a CI run" | Not blocking. The B6 review's finding 2 narrowed "a hook" to "a hook on an agent tool's event", since the pages also call the git hooks in `.githooks/` hooks (verified, reading `2026-11-23-b6-wrapper-parts.md`). The new first sentence says "checks and hooks" with no such limit, and the gloss on a check adds "a commit or a CI run" (verified, reading the diff). The quiet case, "I need to change the pre-push hook and the CI workflow", shares "hook" and "CI" with the description (verified, reading). Both words now pull that request toward this wrapper, and only the last sentence, which gives a git hook in `.githooks/` to `workspace:changing-the-machinery`, pushes it back (inferred). Say "checks, and hooks on an agent tool's event" in the first sentence. Not blocking: `workspace:changing-the-machinery` still matches the request too, so loading this wrapper as well costs a read, not a wrong write (inferred). | fixed: "procedure for a check, or a hook on an agent tool's event"; the gloss naming a CI run is gone. |

## Checked with no finding

- contradiction: "add, change or remove" matches the page's "Adding a part" and "Removing a part" sections, and "its part file, its cases and its manifest entry" matches its table "The pieces" (verified, `grep -n` on `docs/parts.md`). The neighbour it names, `workspace:changing-the-machinery`, exists and names this wrapper back for a check or a hook on an agent tool's event (verified).
- step: the body is unchanged and names `docs/parts.md`, which exists; the `wrappers` check passes (verified).
- enforcement: the description states no must or never. The `wrappers` check holds its name, page, neighbours and cases, and its cases pass (verified).
- placement: "which fails a commit or a CI run" glosses what a check is, so a model that has not read the page knows the word; it restates no step of the page (verified, reading).
- eval-case: both selection cases exist (verified). The fires case's "a check that fails" meets the gloss "a check, which fails a commit or a CI run", but the gloss is the page's meaning of a check, not the case's request, so the case still tests the kind of request (inferred). The page is marked unproven with `prove-by: M4`.

## Re-check

A fresh session at the driver tier re-read the staged description on 2026-11-23, after the fix round, against its page, every other wrapper's description and the neighbours' selection cases in `plugin/evals/`. `python3 ws.py check` exits 0, with only `eval_record`'s usual no-base warning, and `python3 ws.py selftest` reports `wrappers: 18 of 18 cases` and `loaded_size: 4 of 4 cases` (verified). The 28 descriptions now come to 8,449 bytes against the 9,000-byte ceiling (verified). No selection run has read the final descriptions, so every claim about what they fire on is inferred.

| # | Verdict | Evidence |
|---|---|---|
| 1 | fixed | The first sentence now reads "a check, or a hook on an agent tool's event", the B6 narrowing (verified, reading). The gloss naming a commit or a CI run is gone, and "CI" no longer appears in the description (verified, searching it). The quiet case's "pre-push hook" is a git hook, which the last sentence gives to `workspace:changing-the-machinery` (verified, reading). This description is 318 bytes (verified). |

What the first reading missed: nothing found in this description. Extend the workspace's Not clause still sends every hook here; that is recorded in `2026-11-23-b6-rewrite-extend-the-workspace.md`, R2.
