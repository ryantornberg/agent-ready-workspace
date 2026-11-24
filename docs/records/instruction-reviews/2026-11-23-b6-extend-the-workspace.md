---
kind: record
last-reviewed: 2026-11-23
covers: docs/extend-the-workspace.md
reviewed-at: a2d6a59, with the staged change of slice B6
---

# Instruction review: docs/extend-the-workspace.md

This records the review of B6's edit to extend the workspace's step 5, on wrappers, for its author and its readers.

**In short:** 3 findings: 2 step, 1 enforcement, none blocking. The wrapper's path names "the page's file name", `.md` included, which the check refuses as a wrapper name. The waiting list accepts only M4 and M8, so a page waiting for another milestone needs a change to the part, which the step does not say. The new duties have no row in the page's rules table, and the **In short** line does not name them.

## Scope

In scope: step 5's new bullet on the wrapper, read against the rest of steps 5 to 8, the **In short** line and the rules table. The whole page was read, with `git diff --cached -- docs/extend-the-workspace.md` for the change. Read beside it: `AGENTS.md`, `INDEX.md`, `docs/playbooks/README.md` ("Three ways to follow a playbook" and its rules), `docs/playbooks/instruction-review.md`, `docs/changing-the-machinery.md`, `workspace.json` (the `wrappers`, `review_trailer` and `loaded_size` entries), `parts/wrappers.py` and its cases, the wrappers under `plugin/skills/`, the selection cases under `plugin/evals/`, `evals/README.md` ("The wrappers' selection cases"), `evals/arms.json` and `evals/one-time.json`.

Run, on macOS: `python3 ws.py check` exits 0, with only `eval_record`'s usual no-base warning, and `python3 ws.py selftest` reports `wrappers: 17 of 17 cases` (verified). The wrappers' descriptions total 6,542 bytes of the 9,000 the `loaded_size` entry allows (verified, by summing each `description` field).

## Findings

| # | Class | Where | Finding | Disposition |
|---|---|---|---|---|
| 1 | step | Step 5, the wrapper bullet, "`plugin/skills/<the page's file name>/SKILL.md`" | Not blocking. A page's file name ends in `.md`, so the path reads as `plugin/skills/debugging.md/SKILL.md`. The check takes a wrapper's folder as its name and refuses one that is not lower-case words joined by hyphens (verified, reading `NAME` and the name test in `parts/wrappers.py`). Every wrapper's folder is its page's file name without `.md` (verified, by comparing each body's path with its folder). The catalog's example, `workspace:debugging`, shows the right form, and the check's message names the fix. Say "the page's file name without `.md`". | fixed: "the page's file name without .md". |
| 2 | step | Step 5, the wrapper bullet, "goes on the waiting list in the `wrappers` entry of workspace.json instead" | Not blocking. The check accepts a waiting entry only `for` M4 or M8: `WAITS_FOR` in `parts/wrappers.py` holds those two (verified, reading, and the case "a waiting entry for another milestone or a lane page fails"). A page that waits for another milestone cannot be listed by editing `workspace.json`; it needs a change to the part as well. The step names only the manifest. Name the two milestones, as the catalog's rules row does, and say that any other needs the part changed. | fixed: the bullet names M4's review machinery and M8's providers, and says another milestone needs the part changed. |
| 3 | enforcement | "Rules", read against step 5's wrapper bullet and the **In short** line | Not blocking. The bullet adds two duties: a core page gets its wrapper and two selection cases in the same commit, and a lane page gets none. The rules table gains no row for either, though the `wrappers` check enforces both (`wrappers#a core procedure with no wrapper fails`, `wrappers#a wrapper missing a selection case fails`, `wrappers#a lane draft with a wrapper fails`; verified, by name in `parts/wrappers.cases.json`). The **In short** line still lists only "a catalog row and a route in", and step 8's report names the page, its rows and its route in, not the wrapper. Add the rule with those tags, and name the wrapper in the **In short** line and the report. | fixed: a rules row with the three tags, and the wrapper in the In short line and step 8's report. |

## Checked with no finding

- contradiction: the bullet agrees with the catalog, the check and the instruction review. A core page is a playbook or how-to with no `lane` key, as the bullet says. The wrapper is guidance, as the `review_trailer` entry lists `plugin/skills/`, and its selection cases are not (verified, `tests.test_instruction_review` passes, with `test_the_wrappers_are_guidance_and_their_selection_cases_are_not`). A waiting-list edit is a change to `workspace.json`, which is machinery, as the bullet says. Adding a wrapper changes no file the eval's gate covers: the plugin enters only the one-time `routed` arm, which "sits outside every case's hash" (verified, reading `evals/one-time.json` and `one_time_arm` in `evals/run.py`). So step 5's paragraph on eval-covered files needs no wrapper line.
- trigger: the page's purpose line still covers the task. The wrapper `plugin/skills/extend-the-workspace/SKILL.md` fires on adding a playbook or how-to with its routing rows, and names `workspace:parts` and `workspace:maintain-the-workspace` as its neighbours (verified, reading).
- placement: the bullet describes the wrapper's shape in one sentence and links the catalog for the rest. "Each description loads into every session" is the reason for the size advice, not a restated rule.
- eval-case: the page is marked unproven, with `prove-by: M5` (verified, reading its front matter).

## Re-check

A fresh session re-read the page on 2026-11-23, after the fix round, at a2d6a59 with the staged change of slice B6, using `git diff --cached`. On macOS, `python3 ws.py check` exits 0, with only `eval_record`'s usual no-base warning; `python3 ws.py selftest` exits 0, with `wrappers: 18 of 18 cases`; and `python3 -m unittest tests.test_kit tests.test_instruction_review -b` runs 48 tests, OK (verified).

| # | Verdict | Evidence |
|---|---|---|
| 1 | fixed | Step 5 reads `plugin/skills/<the page's file name without .md>/SKILL.md`. The check now requires that name too: case "a wrapper named for another page fails", passing (verified). |
| 2 | fixed | The bullet names M4's review machinery and M8's providers, and says a wait for any other milestone needs the `wrappers` part changed. `WAITS_FOR` in `parts/wrappers.py` holds only M4 and M8 (verified, reading). |
| 3 | fixed | The new rules row carries the three tags, and the `rules` check passes, so each names a real case (verified). The **In short** line names a wrapper for a core playbook or how-to, and step 8's report names "its wrapper" (verified, reading). |

| # | Kind | Finding | Disposition |
|---|---|---|---|
| R1 | broke | Not blocking. contradiction. The new rules row says "A core playbook or how-to lands with its wrapper and two selection cases ...; a lane draft gets none." A core page on the `wrappers` waiting list lands with no wrapper, and the check refuses one ("a waiting page with a wrapper fails") (verified, reading `run` and the case). Step 5's bullet and the catalog's rules row state that exception; this row does not label it. Add "unless the `wrappers` entry's waiting list names it". | fixed (second round): "unless the `wrappers` entry's waiting list names it". |

What the first reading missed: nothing.
