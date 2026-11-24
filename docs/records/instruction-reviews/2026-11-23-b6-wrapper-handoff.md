---
kind: record
last-reviewed: 2026-11-23
covers: plugin/skills/handoff/SKILL.md
reviewed-at: a2d6a59, with the staged change of slice B6
---

# Instruction review: plugin/skills/handoff/SKILL.md

This records the review of the handoff wrapper that slice B6 adds, for its author and its readers.

**In short:** 1 finding: 1 eval-case, not blocking. The selection cases accept a skill named `handoff` from any plugin, and a session can load another plugin's skill of that name, so neither case shows whether this description works.

## Scope

In scope: the whole wrapper, its front matter (`name`, `description`) and its body, which the staged change adds (`git diff --cached`). Read beside it: `AGENTS.md`, `INDEX.md`, `docs/playbooks/README.md`, `docs/how-tos.md`, `docs/playbooks/handoff.md`, `docs/orchestration.md` ("Handing work off"), every other wrapper under `plugin/skills/`, the cases `plugin/evals/handoff-fires` and `plugin/evals/handoff-quiet`, `parts/wrappers.py` (`match_for`), `evals/README.md` ("The wrappers' selection cases"), and the `wrappers` and `loaded_size` entries in `workspace.json`.

Run, on macOS: `python3 ws.py check` exits 0, with only `eval_record`'s usual no-base warning; `python3 ws.py selftest` reports `wrappers: 17 of 17 cases` and `loaded_size: 4 of 4 cases`; `claude plugin validate plugin`, on Claude Code 2.1.330, passes with one warning, for a missing icon (verified). The 28 descriptions come to 6,542 bytes against the 9,000-byte ceiling; this one is 241 (verified). No selection case has run yet, as `evals/README.md` says (verified, reading), so every claim below about what a description fires on is inferred.

## Findings

| # | Class | Where | Finding | Disposition |
|---|---|---|---|---|
| 1 | eval-case | Front matter, `name: handoff`, as the selection cases' `input_match` names it | Not blocking. Both cases name the wrapper by `"skill"\s*:\s*"(?:[\w-]+:)?handoff"`, the one form `match_for` in `parts/wrappers.py` allows. It accepts any plugin's prefix: run on three inputs, it matches `workspace:handoff`, a bare `handoff` and another plugin's `<plugin>:handoff` alike (verified). The maintainer's sessions load a user-level skill named `handoff` from another plugin; this review's own session lists one (verified). Where such a skill loads, the fires case passes when it fires instead, and the quiet case fails when it fires, so neither case tells whether this description works (inferred: whether `claude plugin eval` loads user-level skills was not checked). The two skills also compete for the same request in such a session. Match `workspace:` exactly in `match_for`, or give the wrapper a name no common skill shares. The form is the `wrappers` check's, so the first fix is a machinery change. | fixed: `input_match` now names the plugin, `workspace:handoff`. The `wrappers` check accepts only that form, and a case refuses the old one; all 58 cases were regenerated. |

## Checked with no finding

- contradiction: the description matches the page's "When to use it", a session that must stop with a later session carrying on, and its "Resuming" section, which starts only when the person asks to resume (verified, reading). The neighbor it names, `workspace:orchestration`, exists and names this wrapper back for a session that stops mid-task (verified).
- step: the body names one page, `docs/playbooks/handoff.md`, which exists, is a playbook with no `lane` key and has numbered steps under "Writing the note" and "Resuming" (verified).
- trigger: the fires case is a session whose context is nearly full; the quiet case asks which model a helper gets and how to hand it a sweep, which orchestration owns (verified, reading). The page's own table draws the same line, between a whole session stopping and one piece handed to a helper.
- enforcement: the wrapper states no must or never. The rule that a wrapper stays thin is tagged `prose` in the catalog; the name, page, neighbor and case rules are enforced by the `wrappers` check, whose cases pass (verified).
- placement: the description says only when to fire and when not, and restates no step of the page (verified, reading).

## Re-check

A fresh session re-read the wrapper on 2026-11-23, after the fix round, at a2d6a59 with the staged change of slice B6 (`git diff --cached`). It read the wrapper as staged, its canonical page, every other wrapper's description and the selection cases under `plugin/evals/`. `python3 ws.py check` exits 0, with only `eval_record`'s usual no-base warning; `python3 ws.py selftest` reports `wrappers: 18 of 18 cases` and `loaded_size: 4 of 4 cases`; the 28 descriptions now come to 7,535 bytes against the 9,000-byte ceiling (verified). No selection case has run, so what a description fires on stays inferred.

| # | Verdict | Evidence |
|---|---|---|
| 1 | upheld: fixed | `match_for` in `parts/wrappers.py` now builds `"skill"\s*:\s*"workspace:<name>"`, and the check accepts only that form. All 58 selection cases use it, and no file under `plugin/evals/` holds the old `(?:...)` form (verified, `git grep`). The case "a stray or malformed selection case fails" gives the old form and expects it refused, and passes in `python3 ws.py selftest` (verified). |

What a fix broke: Nothing.

What the first reading missed: Nothing.
