---
kind: record
last-reviewed: 2026-11-23
covers: plugin/skills/escape-analysis/SKILL.md
reviewed-at: a2d6a59, with the staged change of slice B6
---

# Instruction review: plugin/skills/escape-analysis/SKILL.md

This records the review of the escape-analysis wrapper that slice B6 adds, for its author and its readers.

**In short:** no findings. The description follows the page's "When it runs" and the catalog row, and both neighbors it names exist.

## Scope

In scope: the whole wrapper, its front matter (`name`, `description`) and its body, which the staged change adds (`git diff --cached`). Read beside it: `AGENTS.md`, `INDEX.md`, `docs/playbooks/README.md`, `docs/how-tos.md`, `docs/playbooks/escape-analysis.md`, every other wrapper under `plugin/skills/`, the cases `plugin/evals/escape-analysis-fires` and `plugin/evals/escape-analysis-quiet`, `parts/wrappers.py`, and the `wrappers` and `loaded_size` entries in `workspace.json`.

Run, on macOS: `python3 ws.py check` exits 0, with only `eval_record`'s usual no-base warning; `python3 ws.py selftest` reports `wrappers: 17 of 17 cases` and `loaded_size: 4 of 4 cases`; `claude plugin validate plugin`, on Claude Code 2.1.330, passes with one warning, for a missing icon (verified). The 28 descriptions come to 6,542 bytes against the 9,000-byte ceiling; this one is 236 (verified). No selection case has run yet, as `evals/README.md` says (verified, reading), so every claim below about what a description fires on is inferred.

## Findings

| # | Class | Where | Finding | Disposition |
|---|---|---|---|---|

No findings.

## Checked with no finding

- contradiction: the description matches the page's "When it runs", a fix committed for a defect in code a review covered, and the catalog row (verified, reading). Both neighbors it names exist; `workspace:prompt-retrospective` names this wrapper back for why a review missed a defect (verified).
- step: the body names one page, `docs/playbooks/escape-analysis.md`, which exists, is a playbook with no `lane` key and has nine numbered steps (verified).
- trigger: the fires case is a fixed rounding defect in reviewed code; the quiet case asks to fix the same defect, which `workspace:fix-a-bug` owns and the description names (verified, reading). "A defect" also matches a defect in a guidance page, which the page scopes out; its own routing table sends that case away before step 1, so a misfire costs one page read (inferred).
- enforcement: the wrapper states no must or never. The rule that a wrapper stays thin is tagged `prose` in the catalog; the name, page, neighbor and case rules are enforced by the `wrappers` check, whose cases pass (verified).
- placement: the description says only when to fire and when not, and restates no step of the page (verified, reading).
- eval-case: both selection cases exist (verified). The page is marked unproven with `prove-by: M6`.

## Re-check

A fresh session re-read the wrapper on 2026-11-23, after the fix round, at a2d6a59 with the staged change of slice B6 (`git diff --cached`). It read the wrapper as staged, its canonical page, every other wrapper's description and the selection cases under `plugin/evals/`. `python3 ws.py check` exits 0, with only `eval_record`'s usual no-base warning; `python3 ws.py selftest` reports `wrappers: 18 of 18 cases` and `loaded_size: 4 of 4 cases`; the 28 descriptions now come to 7,535 bytes against the 9,000-byte ceiling (verified). No selection case has run, so what a description fires on stays inferred.

The first reading recorded no findings, so there is no disposition to rule on. Prompt retrospective's description still names this wrapper back, and the quiet case, fixing the rounding defect, sits inside fix a bug's description, not this one (verified, reading).

What a fix broke: Nothing.

What the first reading missed: Nothing.
