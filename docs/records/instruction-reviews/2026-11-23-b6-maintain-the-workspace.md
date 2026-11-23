---
kind: record
last-reviewed: 2026-11-23
covers: docs/maintain-the-workspace.md
reviewed-at: a2d6a59, with the staged change of slice B6
---

# Instruction review: docs/maintain-the-workspace.md

This records the review of B6's edit to the periodic duty for pruning unused wrappers, for its author and the maintainer.

**In short:** 1 finding: 1 step, not blocking. The changed row says a wrapper leaves only with its page, but the event row for a moved, renamed or archived page names no wrapper work, and the check misses one part of it.

## Scope

In scope: in "Periodic duties", the row "Pruning unused wrappers", read against "Duties an event sets off" and "What the checks catch for you". The whole page was read, with `git diff --cached -- docs/maintain-the-workspace.md` for the change. Read beside it: `AGENTS.md`, `INDEX.md`, `docs/playbooks/README.md` ("Three ways to follow a playbook" and its rules), `docs/playbooks/instruction-review.md` (the `strike` reason), `docs/layout.md` ("Archiving a page"), `workspace.json` (the `wrappers` entry), `parts/wrappers.py` and its cases, and the wrappers under `plugin/skills/`.

Run, on macOS: `python3 ws.py check` exits 0, with only `eval_record`'s usual no-base warning, and `python3 ws.py selftest` reports `wrappers: 17 of 17 cases` (verified).

## Findings

| # | Class | Where | Finding | Disposition |
|---|---|---|---|---|
| 1 | step | "Duties an event sets off", the row "A page is moved, renamed or archived", read against the changed "Pruning unused wrappers" row | Not blocking. The changed row ties a wrapper to its page. The event row lists the links, the catalog or index row, the README's proof row and `INDEX.md`, but not the wrapper. For a core page that moves or is renamed, four things change with it: the wrapper's body path; its folder and `name`, since the catalog names a wrapper after its page's file; its selection cases' `input_match`; and each neighbour's description that names it as `workspace:<name>`. For an archived page, the wrapper and its cases go. The `wrappers` check refuses a body naming a missing page or a reference page, and a description naming a wrapper that does not exist (verified, the cases "a wrapper whose page is missing fails", "a wrapper for a reference page fails" and "a wrong name or no description fails"). It does not refuse a wrapper whose name no longer matches its page's file: `run` compares the name with its folder only (verified, reading). Nor does "What the checks catch for you" list the `wrappers` check, though the changed row relies on it. Add the wrapper to the event row, and a `wrappers` row to the table. | fixed: the event row names the wrapper's moves and its removal on archiving, and "What the checks catch" gains a `wrappers` row. The check now also refuses a wrapper not named after its page's file, with a case. |

## Checked with no finding

- contradiction: "a wrapper leaves only with its page, as a strike does" agrees with the instruction review's `strike` reason, whose commit removes the page with "its index rows, wrapper and table row" (verified, reading). "Nothing here records which wrappers fire in real sessions" holds: no part or hook reads a session's Skill calls (inferred, from `python3 ws.py list` and the parts table in `docs/parts.md`, which name none).
- trigger: the page's purpose and **In short** lines are unchanged and still cover the duty. The wrapper `plugin/skills/maintain-the-workspace/SKILL.md` fires on which duty an event sets off, and names `workspace:docs-audit` and `workspace:extend-the-workspace` as its neighbours (verified, reading).
- enforcement: the changed row's "the `wrappers` check fails one left behind" is true for a struck page (verified, the case "a wrapper whose page is missing fails").
- placement: the row states when the duty applies and links nothing it restates.
- eval-case: the page is marked unproven, with `prove-by: M5` (verified, reading its front matter).

## Re-check

A fresh session re-read the page on 2026-11-23, after the fix round, at a2d6a59 with the staged change of slice B6, using `git diff --cached`. On macOS, `python3 ws.py check` exits 0, with only `eval_record`'s usual no-base warning; `python3 ws.py selftest` exits 0, with `wrappers: 18 of 18 cases`; and `python3 -m unittest tests.test_kit tests.test_instruction_review -b` runs 48 tests, OK (verified).

| # | Verdict | Evidence |
|---|---|---|
| 1 | fixed | The event row names the wrapper's folder, `name` and body path, its cases' `input_match`, each description that names it, and its removal with an archived page. "What the checks catch for you" has a `wrappers` row, "At the commit and in CI", which `python3 ws.py list` confirms (verified). The check now refuses a wrapper not named after its page's file: the name test in `run`, and the case "a wrapper named for another page fails", passing (verified). Each change the row says the check names, it names: a body path to a missing page or a tombstone, a folder that no longer matches its page, a case whose `input_match` names no wrapper, and a description naming a wrapper that does not exist (verified, reading `run` and `_cases` in `parts/wrappers.py`). |

What a fix broke: nothing.

What the first reading missed: nothing.
