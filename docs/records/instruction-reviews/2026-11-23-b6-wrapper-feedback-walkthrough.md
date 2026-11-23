---
kind: record
last-reviewed: 2026-11-23
covers: plugin/skills/feedback-walkthrough/SKILL.md
reviewed-at: a2d6a59, with the staged change of slice B6
---

# Instruction review: plugin/skills/feedback-walkthrough/SKILL.md

This records the review of the feedback-walkthrough wrapper that slice B6 adds, for its author and its readers.

**In short:** 1 finding: 1 trigger, not blocking. The page also owns a request to fix one named review comment, and says it wins over fix a bug there; the description covers only the walk-through.

## Scope

In scope: the whole wrapper, its front matter (`name`, `description`) and its body, which the staged change adds (`git diff --cached`). Read beside it: `AGENTS.md`, `INDEX.md`, `docs/playbooks/README.md`, `docs/how-tos.md`, `docs/playbooks/feedback-walkthrough.md`, `docs/review-in-a-worktree.md`, `docs/playbooks/review-orchestrator.md` ("When it runs, and which page wins"), every other wrapper under `plugin/skills/`, the cases `plugin/evals/feedback-walkthrough-fires` and `plugin/evals/feedback-walkthrough-quiet`, `parts/wrappers.py`, and the `wrappers` and `loaded_size` entries in `workspace.json`.

Run, on macOS: `python3 ws.py check` exits 0, with only `eval_record`'s usual no-base warning; `python3 ws.py selftest` reports `wrappers: 17 of 17 cases` and `loaded_size: 4 of 4 cases`; `claude plugin validate plugin`, on Claude Code 2.1.330, passes with one warning, for a missing icon (verified). The 28 descriptions come to 6,542 bytes against the 9,000-byte ceiling; this one is 215 (verified). No selection case has run yet, as `evals/README.md` says (verified, reading), so every claim below about what a description fires on is inferred.

## Findings

| # | Class | Where | Finding | Disposition |
|---|---|---|---|---|
| 1 | trigger | Front matter, `description`, "go through its review comments one at a time and understand each before anything changes" | Not blocking. The page's "When to use it" table sends a second request here: "The author names one comment and asks only for its fix". It says why this page wins there: its step 5 sizes the change and its step 6 asks before committing, "which fix a bug would not" (verified, reading). The description covers only the walk-through, so a request like "fix the comment Dana left on pull request 42" matches fix-a-bug's "small change in one repository" instead (inferred). That route commits without asking the author first. Add "or asks for the fix of one named review comment". | fixed: the description adds a request for the fix of one named review comment. |

## Checked with no finding

- contradiction: the description matches the catalog row and the page's purpose line (verified, reading). Its exclusion sends reviewing a pull request yourself to `workspace:review-in-a-worktree`. The page's table names the review orchestrator or reviewing in a worktree for that case, and review in a worktree's step 5 follows the orchestrator, so the two routes meet (verified, reading).
- step: the body names one page, `docs/playbooks/feedback-walkthrough.md`, which exists, is a playbook with no `lane` key and has numbered steps (verified).
- enforcement: the wrapper states no must or never. The rule that a wrapper stays thin is tagged `prose` in the catalog; the name, page, neighbor and case rules are enforced by the `wrappers` check, whose cases pass (verified).
- placement: the description says only when to fire and when not, and restates no step of the page (verified, reading).
- eval-case: the fires case asks to go through a pull request's comments one at a time; the quiet case asks to review a pull request without touching the main copy, which `workspace:review-in-a-worktree` owns and the description names (verified, reading). The page is marked unproven with `prove-by: M6`.

## Re-check

A fresh session re-read the wrapper on 2026-11-23, after the fix round, at a2d6a59 with the staged change of slice B6 (`git diff --cached`). It read the wrapper as staged, its canonical page, every other wrapper's description and the selection cases under `plugin/evals/`. `python3 ws.py check` exits 0, with only `eval_record`'s usual no-base warning; `python3 ws.py selftest` reports `wrappers: 18 of 18 cases` and `loaded_size: 4 of 4 cases`; the 28 descriptions now come to 7,535 bytes against the 9,000-byte ceiling (verified). No selection case has run, so what a description fires on stays inferred.

| # | Verdict | Evidence |
|---|---|---|
| 1 | upheld: fixed | The description adds "or asks for the fix of one named review comment", matching the page's "When to use it" row, "The author names one comment and asks only for its fix" (verified, reading). The quiet case, a review of pull request #42 in a worktree, stays outside it. Fix a bug's description does not cede that request back; that is recorded in its record. |

What a fix broke: Nothing.

What the first reading missed: Nothing.
