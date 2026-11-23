---
kind: record
last-reviewed: 2026-11-23
covers: plugin/skills/extend-the-workspace/SKILL.md
reviewed-at: a2d6a59, with the staged change of slice B6
---

# Instruction review: plugin/skills/extend-the-workspace/SKILL.md

This records the review of the extend-the-workspace wrapper that slice B6 adds, for its author and its readers.

**In short:** no findings. The description matches the page's scope and its how-to index row. Its overlap with fix a bug on a small page change is recorded once, against the fix-a-bug wrapper.

## Scope

In scope: the whole wrapper, its front matter (`name`, `description`) and its body, which the staged change adds (`git diff --cached`). Read beside it: `AGENTS.md`, `INDEX.md`, `docs/playbooks/README.md`, `docs/how-tos.md`, `docs/extend-the-workspace.md` and its diff, `docs/parts.md`, `docs/maintain-the-workspace.md`, every other wrapper under `plugin/skills/`, the cases `plugin/evals/extend-the-workspace-fires` and `plugin/evals/extend-the-workspace-quiet`, `parts/wrappers.py`, and the `wrappers` and `loaded_size` entries in `workspace.json`.

Run, on macOS: `python3 ws.py check` exits 0, with only `eval_record`'s usual no-base warning; `python3 ws.py selftest` reports `wrappers: 17 of 17 cases` and `loaded_size: 4 of 4 cases`; `claude plugin validate plugin`, on Claude Code 2.1.330, passes with one warning, for a missing icon (verified). The 28 descriptions come to 6,542 bytes against the 9,000-byte ceiling; this one is 255 (verified). No selection case has run yet, as `evals/README.md` says (verified, reading), so every claim below about what a description fires on is inferred.

## Findings

| # | Class | Where | Finding | Disposition |
|---|---|---|---|---|

No findings.

## Checked with no finding

- contradiction: the description's five page kinds, their routing rows and a small change to pages only match the page's "What this page covers" section and its how-to index row (verified, reading). Its exclusions match the page: a check or hook is on parts, and upkeep is on maintain the workspace. Both neighbors it names exist (verified).
- step: the body names one page, `docs/extend-the-workspace.md`, which exists, is a how-to with no `lane` key and has numbered steps. The staged step 5 tells a new procedure's author to copy a wrapper to `plugin/skills/<file name>/SKILL.md` and a pair of cases in `plugin/evals/`; both folders exist and the `wrappers` check holds the result (verified).
- trigger: the fires case asks for a how-to page with its index row; the quiet case asks for a check, which `workspace:parts` owns and the description names (verified, reading). A small page fix also matches fix-a-bug's "small change in one repository"; that is recorded against fix-a-bug, in `2026-11-23-b6-wrapper-fix-a-bug.md`, since its description is the one that lacks the exception.
- enforcement: the wrapper states no must or never. The rule that a wrapper stays thin is tagged `prose` in the catalog; the name, page, neighbor and case rules are enforced by the `wrappers` check, whose cases pass (verified).
- placement: the description says only when to fire and when not, and restates no step of the page (verified, reading).
- eval-case: both selection cases exist (verified). The page is marked unproven with `prove-by: M5`.

## Re-check

A fresh session re-read the wrapper on 2026-11-23, after the fix round, at a2d6a59 with the staged change of slice B6 (`git diff --cached`). It read the wrapper as staged, its canonical page, every other wrapper's description and the selection cases under `plugin/evals/`. `python3 ws.py check` exits 0, with only `eval_record`'s usual no-base warning; `python3 ws.py selftest` reports `wrappers: 18 of 18 cases` and `loaded_size: 4 of 4 cases`; the 28 descriptions now come to 7,535 bytes against the 9,000-byte ceiling (verified). No selection case has run, so what a description fires on stays inferred.

The first reading recorded no findings, so there is no disposition to rule on. The fix round made fix a bug, size the work and search every source name this wrapper for pages only or a page edit, which settles the overlap the first reading left to fix a bug's record. The quiet case, adding a check, stays outside this description and inside parts' (verified, reading). Changing the machinery's "eval cases", which can draw a request to add selection cases away from this page, is recorded in that wrapper's record.

What a fix broke: Nothing.

What the first reading missed: Nothing.
