---
kind: record
last-reviewed: 2026-11-23
covers: plugin/skills/impact-analysis/SKILL.md
reviewed-at: a2d6a59, with the staged change of slice B6
---

# Instruction review: plugin/skills/impact-analysis/SKILL.md

This records the review of the impact-analysis wrapper that slice B6 adds, for its author and its readers.

**In short:** 1 finding: 1 trigger, not blocking. The description's "Not inside ... a refactor" drops the page's "while working through", so it reads as excluding any request about a rename, which is what its own fires case is.

## Scope

In scope: the whole wrapper, its front matter (`name`, `description`) and its body, which the staged change adds (`git diff --cached`). Read beside it: `AGENTS.md`, `INDEX.md`, `docs/playbooks/README.md`, `docs/how-tos.md`, `docs/playbooks/impact-analysis.md`, `docs/safe-refactor.md`, every other wrapper under `plugin/skills/`, the cases `plugin/evals/impact-analysis-fires` and `plugin/evals/impact-analysis-quiet`, `parts/wrappers.py`, and the `wrappers` and `loaded_size` entries in `workspace.json`.

Run, on macOS: `python3 ws.py check` exits 0, with only `eval_record`'s usual no-base warning; `python3 ws.py selftest` reports `wrappers: 17 of 17 cases` and `loaded_size: 4 of 4 cases`; `claude plugin validate plugin`, on Claude Code 2.1.330, passes with one warning, for a missing icon (verified). The 28 descriptions come to 6,542 bytes against the 9,000-byte ceiling; this one is 283 (verified). No selection case has run yet, as `evals/README.md` says (verified, reading), so every claim below about what a description fires on is inferred.

## Findings

| # | Class | Where | Finding | Disposition |
|---|---|---|---|---|
| 1 | trigger | Front matter, `description`, "Not inside a bug fix or a refactor, which map their own" | Not blocking. The page limits that exclusion to a session already working through fix a bug or safe refactor: its table reads "You are working through ... Use its step 4" (verified, reading). The description drops "working through", so "not ... a refactor" can read as any request about a rename. Its own fires case is one: "I am about to rename the order_total field. List everything that change would reach." A rename is the shape change safe refactor's description claims, so the case sits on the line the description draws, and a pass or a fail says little about the description (inferred). Write "Not while working through workspace:fix-a-bug or workspace:safe-refactor, which map their own". | fixed: "Not while working through workspace:fix-a-bug or workspace:safe-refactor". The fires case now asks what a change to how `order_total` is computed reaches, not a rename. |

## Checked with no finding

- contradiction: the description's occasions, closing the feature ladder, planning slices and on request, match the page's "When it runs" and the catalog row (verified, reading). All three neighbors it names exist, and `workspace:reuse-checklist` names this wrapper back for everything a change reaches (verified).
- step: the body names one page, `docs/playbooks/impact-analysis.md`, which exists, is a playbook with no `lane` key and has eight numbered steps (verified).
- enforcement: the wrapper states no must or never. The rule that a wrapper stays thin is tagged `prose` in the catalog; the name, page, neighbor and case rules are enforced by the `wrappers` check, whose cases pass (verified).
- placement: the description says only when to fire and when not, and restates no step of the page (verified, reading).
- eval-case: both selection cases exist; the quiet case asks for an existing helper before writing a new one, which `workspace:reuse-checklist` owns and the description names (verified, reading). The page is marked unproven with `prove-by: M6`.

## Re-check

A fresh session re-read the wrapper on 2026-11-23, after the fix round, at a2d6a59 with the staged change of slice B6 (`git diff --cached`). It read the wrapper as staged, its canonical page, every other wrapper's description and the selection cases under `plugin/evals/`. `python3 ws.py check` exits 0, with only `eval_record`'s usual no-base warning; `python3 ws.py selftest` reports `wrappers: 18 of 18 cases` and `loaded_size: 4 of 4 cases`; the 28 descriptions now come to 7,535 bytes against the 9,000-byte ceiling (verified). No selection case has run, so what a description fires on stays inferred.

| # | Verdict | Evidence |
|---|---|---|
| 1 | upheld: fixed | The description says "Not while working through workspace:fix-a-bug or workspace:safe-refactor, which map their own", matching the page's "You are working through" table (verified, reading). The fires case now asks what a change to how `order_total` is computed reaches, which no other description takes; `reuse-checklist-quiet` uses the same request, and reuse's description names this wrapper for it (verified, reading). |

What a fix broke: Nothing.

What the first reading missed: Nothing.
