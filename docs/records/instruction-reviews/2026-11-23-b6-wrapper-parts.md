---
kind: record
last-reviewed: 2026-11-23
covers: plugin/skills/parts/SKILL.md
reviewed-at: a2d6a59, with the staged change of slice B6
---

# Instruction review: plugin/skills/parts/SKILL.md

This records the review of slice B6's new `parts` wrapper, for its author and whoever settles its findings.

**In short:** 2 findings: 2 trigger, none blocking. Adding a check needs both this wrapper and `workspace:changing-the-machinery`, but each description puts the other in its "Not for" clause, and the page this one loads has no branch step. And "a hook" also matches the git hooks, which are not parts, as the quiet case shows.

## Scope

In scope: the whole wrapper, new in this change: its `name`, its `description` and its body, read against the page its body names. The change was read with `git diff --cached`. Read beside it: `AGENTS.md`, `INDEX.md`, the playbook catalog `docs/playbooks/README.md`, `docs/how-tos.md`, `docs/parts.md` in full, `docs/changing-the-machinery.md` and the `changing-the-machinery` and `extend-the-workspace` wrappers' descriptions, the description of every other wrapper under `plugin/skills/`, its selection cases `plugin/evals/parts-fires` and `-quiet`, `parts/wrappers.py` and `parts/wrappers.cases.json`, and the `wrappers` and `loaded_size` entries in `workspace.json`.

Run, on macOS, in the worktree, before any record was written: `python3 ws.py check` exits 0, with only `eval_record`'s usual no-base warning, and `python3 ws.py selftest` exits 0 and lists `wrappers: 17 of 17 cases` (verified). With the records written, `check` fails only on `review_index`, for the index rows the author adds at step 5 (verified). The 28 wrappers' descriptions come to 6,542 bytes against the 9,000 the `loaded_size` entry allows (verified, summing each `description` value). The selection cases have not run: `evals/README.md` says the first run waits for the maintainer's yes to its budget. So every claim below about which wrapper a model would load is inferred.

## Findings

| # | Class | Where | Finding | Disposition |
|---|---|---|---|---|
| 1 | trigger | The description, "Not for the branch, pull request and merge every machinery change takes: use workspace:changing-the-machinery" | Not blocking. The fires case, "Add a check that fails when a page under docs/ is empty", needs both wrappers: a part is machinery, as the table in `docs/changing-the-machinery.md` and the contract's "How work flows" say. This description puts the machinery path in its "Not for" clause, and `workspace:changing-the-machinery` puts "writing the check or hook itself" in its own, so each reads as the other's alternative (verified, reading both). The page this wrapper loads does not close the gap: "Adding a part" ends at `selftest`, `check` and the hook replay, with no branch, commit or pull request, and `docs/parts.md` links changing the machinery only from the `direct_push` and `no_admin_merge` rows of "The parts here" (verified, `grep -n changing-the-machinery docs/parts.md`). An agent that loads only this wrapper reaches the branch path through the contract's one line. Say that the change also takes `workspace:changing-the-machinery`, instead of "Not for". Not blocking: the contract loads in every session, and `direct_push` refuses a push to main that changes a part. | fixed: the description says the change is machinery, so its branch and merge follow workspace:changing-the-machinery. |
| 2 | trigger | The description, "adding or changing a check or a hook" | Not blocking. Here "a hook" means a part whose `KIND` is `hook`, which runs on an agent tool's event, as "A hook" in `docs/parts.md` defines it. The workspace also calls the git hooks in `.githooks/` hooks: `docs/changing-the-machinery.md` lists them as "The commit hook", and the pages speak of the pre-push hook. The quiet case asks to "change the pre-push hook and the CI workflow", which the description's words match, though the request is `workspace:changing-the-machinery`'s (verified, reading the case). Say "a check, or a hook on an agent tool's event", or name `.githooks/` as outside it. Inferred: the case has not run. | fixed: "a hook on an agent tool's event"; a git hook in `.githooks/` is changing the machinery's alone. |

## Checked with no finding

- step: the body names one path, `docs/parts.md`, which exists and is a how-to with no `lane` key and no place on the waiting list, as the `wrappers` check confirms on this tree (verified). Its one action, to read the page and follow it, needs no input it does not name. "Adding a part" names its files, its manifest entry and the three commands, and each exists (verified, by running `selftest` and `check`).
- contradiction: the description agrees with the page's purpose line, its how-to index row, "Add a check or a hook", and the INDEX.md topic "Adding a check or a hook" (verified, reading).
- enforcement: the wrapper states no must or never of its own. The catalog's rules that bind it are tagged to `wrappers` cases that show them: a description that names no wrapper next to it fails `a wrong name or no description fails`, and a page that is missing fails `a wrapper whose page is missing fails` (verified, reading `parts/wrappers.cases.json`; selftest passes them). That a wrapper stays thin is tagged `prose`, and this one is: its body restates no step of the page.
- placement: the description, which loads into every session, holds only when to fire and the wrapper next to it that owns the nearby request; it restates no rule of the page. The body is one pointer.
- eval-case: the one behavior the wrapper asks is loading its page on a matching request, and its selection cases cover it: `parts-fires` (`min: 1`) and `parts-quiet` (`min: 0`, `max: 0`, `arm: both`), each `input_match` in the one form the check takes (verified, reading). What the page then asks is the page's own; `docs/parts.md` is marked unproven with `prove-by: M4` (verified, reading its front matter).

## Re-check

A fresh session re-read the wrapper on 2026-11-23, after the fix round, at a2d6a59 with the staged change of slice B6 (`git diff --cached`). It read the wrapper as staged, its canonical page, every other wrapper's description and the selection cases under `plugin/evals/`. `python3 ws.py check` exits 0, with only `eval_record`'s usual no-base warning; `python3 ws.py selftest` reports `wrappers: 18 of 18 cases` and `loaded_size: 4 of 4 cases`; the 28 descriptions now come to 7,535 bytes against the 9,000-byte ceiling (verified). No selection case has run, so what a description fires on stays inferred.

| # | Verdict | Evidence |
|---|---|---|
| 1 | upheld: fixed | The description says "The change is machinery, so its branch and merge follow workspace:changing-the-machinery", and that wrapper now says to use it with this one (verified, reading both). |
| 2 | upheld: fixed | The description says "a hook on an agent tool's event" and that a git hook in `.githooks/` is changing the machinery's alone. The quiet case, the pre-push hook and the CI workflow, stays outside this description (verified, reading). Changing the machinery's own pointer, "With workspace:parts for a check or hook", still sends that request here; that is recorded in its record. |

What a fix broke: Nothing.

What the first reading missed: Nothing.
