---
kind: record
last-reviewed: 2026-11-23
covers: plugin/skills/debugging/SKILL.md
reviewed-at: a2d6a59, with the staged change of slice B6
---

# Instruction review: plugin/skills/debugging/SKILL.md

This records the review of the debugging wrapper that slice B6 adds, for its author and its readers.

**In short:** 1 finding: 1 trigger, not blocking. The description fires on any failing CI run, while the catalog gives reading why a pull request's CI failed, with no cause to find, to git-host operations, which has no wrapper.

## Scope

In scope: the whole wrapper, its front matter (`name`, `description`) and its body, which the staged change adds (`git diff --cached`). Read beside it: `AGENTS.md`, `INDEX.md`, `docs/playbooks/README.md`, `docs/how-tos.md`, `docs/playbooks/debugging.md`, every other wrapper under `plugin/skills/`, the cases `plugin/evals/debugging-fires`, `plugin/evals/debugging-quiet` and `plugin/evals/fix-a-bug-quiet`, `parts/wrappers.py`, and the `wrappers` and `loaded_size` entries in `workspace.json`.

Run, on macOS: `python3 ws.py check` exits 0, with only `eval_record`'s usual no-base warning; `python3 ws.py selftest` reports `wrappers: 17 of 17 cases` and `loaded_size: 4 of 4 cases`; `claude plugin validate plugin`, on Claude Code 2.1.330, passes with one warning, for a missing icon (verified). The 28 descriptions come to 6,542 bytes against the 9,000-byte ceiling; this one is 206 (verified). No selection case has run yet, as `evals/README.md` says (verified, reading), so every claim below about what a description fires on is inferred.

## Findings

| # | Class | Where | Finding | Disposition |
|---|---|---|---|---|
| 1 | trigger | Front matter, `description`, "a failing test or CI run" | Not blocking. The catalog's debugging row says "Reading a pull request's CI state or log, with no cause to find, is git-host operations", and the git-host operations row claims "read why its CI failed" (verified, reading). The description fires on any failing CI run and names no exclusion for it. Git-host operations has no wrapper, since it waits for M8, so a request like "why did CI fail on pull request 7?" fires only this one (inferred). Debugging's step 1 then builds a repro loop where reading the failed step's log was the whole answer. Add "Not for reading why a pull request's CI failed when its log already says", or have the catalog settle which row owns that request, since its two rows overlap. | fixed: the description leaves out reading why a pull request's CI failed when its log already says. |

## Checked with no finding

- contradiction: the description matches the page's purpose line, "a bug report, a failing test or CI run, or a flaky test", and the catalog row, including the hand-on to fix a bug once the cause is found (verified, reading). The neighbor it names, `workspace:fix-a-bug`, exists and names this wrapper back for an unknown cause (verified).
- step: the body names one page, `docs/playbooks/debugging.md`, which exists, is a playbook with no `lane` key and has numbered steps (verified).
- enforcement: the wrapper states no must or never. The rule that a wrapper stays thin is tagged `prose` in the catalog; the name, page, neighbor and case rules are enforced by the `wrappers` check, whose cases pass (verified).
- placement: the description says when to fire and when not, and restates no step of the page (verified, reading).
- eval-case: the fires case is a nightly job failing one run in five; the quiet case is a plan's slice built test first, which `workspace:test-first` owns. The boundary the description names, with fix a bug, is tested from the other side: fix-a-bug's quiet case is this same flaky request (verified, reading). The page is marked unproven with `prove-by: M4`.

## Re-check

A fresh session re-read the wrapper on 2026-11-23, after the fix round, at a2d6a59 with the staged change of slice B6 (`git diff --cached`). It read the wrapper as staged, its canonical page, every other wrapper's description and the selection cases under `plugin/evals/`. `python3 ws.py check` exits 0, with only `eval_record`'s usual no-base warning; `python3 ws.py selftest` reports `wrappers: 18 of 18 cases` and `loaded_size: 4 of 4 cases`; the 28 descriptions now come to 7,535 bytes against the 9,000-byte ceiling (verified). No selection case has run, so what a description fires on stays inferred.

| # | Verdict | Evidence |
|---|---|---|
| 1 | upheld: fixed | The description ends "nor to read why a pull request's CI failed when its log already says", matching the catalog's debugging row; it names no wrapper for that request, since git-host operations waits for M8 (verified, reading the description and the `wrappers` entry). The fires case, a nightly job failing one run in five, still sits inside the description. |

What a fix broke: Nothing.

What the first reading missed: Nothing.
