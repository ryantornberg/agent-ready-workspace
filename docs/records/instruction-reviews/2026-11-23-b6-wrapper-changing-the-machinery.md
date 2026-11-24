---
kind: record
last-reviewed: 2026-11-23
covers: plugin/skills/changing-the-machinery/SKILL.md
reviewed-at: a2d6a59, with the staged change of slice B6
---

# Instruction review: plugin/skills/changing-the-machinery/SKILL.md

This records the review of the changing-the-machinery wrapper that slice B6 adds, for its author and its readers.

**In short:** 2 findings: 2 trigger, none blocking. The description's list of what it covers leaves out several machinery paths, such as the eval cases, `kit/` and `outward-repos.json`. And its exclusion of "writing the check or hook itself" can keep it from firing on a request to add a check, which always needs this page's path too.

## Scope

In scope: the whole wrapper, its front matter (`name`, `description`) and its body, which the staged change adds (`git diff --cached`). Read beside it: `AGENTS.md`, `INDEX.md`, `docs/playbooks/README.md`, `docs/how-tos.md`, `docs/changing-the-machinery.md`, `docs/parts.md` ("The pieces" and its parts table), every other wrapper under `plugin/skills/`, the cases `plugin/evals/changing-the-machinery-fires` and `plugin/evals/changing-the-machinery-quiet`, `parts/wrappers.py`, and the `wrappers`, `loaded_size` and `direct_push` entries in `workspace.json`.

Run, on macOS: `python3 ws.py check` exits 0, with only `eval_record`'s usual no-base warning; `python3 ws.py selftest` reports `wrappers: 17 of 17 cases` and `loaded_size: 4 of 4 cases`; `claude plugin validate plugin`, on Claude Code 2.1.330, passes with one warning, for a missing icon (verified). The 28 descriptions come to 6,542 bytes against the 9,000-byte ceiling; this one is 274 (verified). No selection case has run yet, as `evals/README.md` says (verified, reading), so every claim below about what a description fires on is inferred.

## Findings

| # | Class | Where | Finding | Disposition |
|---|---|---|---|---|
| 1 | trigger | Front matter, `description`, the list "scripts, parts, hooks, CI, the manifest or the agent tools' wiring" | Not blocking. The list leaves out machinery paths that the page's "What counts as machinery" table and the `direct_push` entry's `machinery` list name: the eval cases, acceptance tests and arms, `tests/`, `baselines/`, `kit/` and `kit.lock.json`, `outward-repos.json`, and the browser server's `.mcp.json` (verified, comparing the three). A request such as "add an eval case" or "make a file synced in `kit/kit.json`" may not fire it (inferred). The `direct_push` check still refuses such a commit in a push to main, so a miss costs a refused push, not a bad write. The list can also fire where it should not: "the agent tools' wiring" reads as taking in the plugin's own wiring, `.claude-plugin/marketplace.json` and `plugin/.claude-plugin/plugin.json`, which are not machinery paths (verified). Say "any path the page's machinery table lists", or name the missing groups in a few words. | fixed: the description says any path the page's machinery table lists, with tests and eval cases among the examples. |
| 2 | trigger | Front matter, `description`, "Not for writing the check or hook itself (workspace:parts)" | Not blocking. A new or changed check or hook is a change under `parts/`, which is machinery, so it always needs both pages: parts for the part file and its cases, this page for the branch, the failing case, the pull request and the merge. The description says to use it "before changing ... parts", then excludes writing the check. Parts' description hands back only "the branch, pull request and merge" (verified, reading both). For a request like "add a check that fails when a page under docs/ is empty", the extend-the-workspace quiet case, an agent may load parts alone (inferred). Parts does not send it here before its steps: its one link to this page is in the `direct_push` row of its parts table (verified, reading). The contract's line "A change to scripts, parts, hooks or CI is machinery" is the backstop. Say "Use with workspace:parts when adding or changing a check or hook: parts owns the part, this page the path." | fixed: it says to use it with workspace:parts for a check or hook, and parts' description says its branch and merge follow this one. |

## Checked with no finding

- contradiction: the description's summary of the path, the branch, the failing case, the draft pull request and the merge, matches the page's steps 1, 2, 5 and 6 and the contract's line on machinery (verified, reading). The neighbors it names, `workspace:parts` and `workspace:extend-the-workspace`, exist.
- step: the body names one page, `docs/changing-the-machinery.md`, which exists, is a how-to with no `lane` key and has numbered steps under "The path for a machinery change" (verified).
- enforcement: the wrapper states no must or never. The rule that a wrapper stays thin is tagged `prose` in the catalog; the name, page, neighbor and case rules are enforced by the `wrappers` check, whose cases pass (verified).
- placement: the description says when to fire and when not, with a four-word summary of the path, and restates no step (verified, reading).
- eval-case: the fires case asks what path a change to the pre-push hook and the CI workflow takes; the quiet case asks for a how-to page with its index row, which `workspace:extend-the-workspace` owns and the description names (verified, reading). The page is marked unproven with `prove-by: M4`.

## Re-check

A fresh session re-read the wrapper on 2026-11-23, after the fix round, at a2d6a59 with the staged change of slice B6 (`git diff --cached`). It read the wrapper as staged, its canonical page, every other wrapper's description and the selection cases under `plugin/evals/`. `python3 ws.py check` exits 0, with only `eval_record`'s usual no-base warning; `python3 ws.py selftest` reports `wrappers: 18 of 18 cases` and `loaded_size: 4 of 4 cases`; the 28 descriptions now come to 7,535 bytes against the 9,000-byte ceiling (verified). No selection case has run, so what a description fires on stays inferred.

| # | Verdict | Evidence |
|---|---|---|
| 1 | upheld: fixed | The description says "any path the page's machinery table lists, such as scripts, parts, hooks, CI, tests, eval cases, the manifest or the agent tools' settings". The table matches the `direct_push` entry's `machinery` list, which holds `tests/`, `evals/cases/` and `.claude/settings.json` and not `.claude-plugin/` or `plugin/` (verified, reading both). |
| 2 | upheld: fixed | The description says "With workspace:parts for a check or hook", and parts' description says its branch and merge follow this wrapper (verified, reading both). |

What a fix broke: the rows marked broke below.

What the first reading missed: Nothing.

| # | Kind | Finding | Disposition |
|---|---|---|---|
| R1 | broke | Not blocking. A trigger finding. Finding 2's fix, "With workspace:parts for a check or hook", sends any hook to parts, a git hook included. Parts' fixed description says the opposite: a git hook in `.githooks/` is "changing-the-machinery's alone" (verified, reading both). This wrapper's fires case, which is also `parts-quiet`, asks to change the pre-push hook; this description now points an agent that loads it at parts for that request, so the parts quiet case sits inside this description's pointer (inferred: no case has run). Say "With workspace:parts for a check, or a hook on an agent tool's event". | fixed (second round): "With workspace:parts for a check, or a hook on an agent tool's event." |
| R2 | broke | Not blocking. A trigger finding. Finding 1's fix names "eval cases" among the machinery. The workspace now has two kinds: the eval harness's cases in `evals/cases/`, which are machinery, and the wrappers' selection cases in `plugin/evals/`, which are not on the table or the `direct_push` list (verified, reading `workspace.json`). A request to add a wrapper's selection cases, which extend the workspace's step 5 asks for with a new page, can fire this description and take a branch it does not need (inferred). Say "the eval harness's cases", or leave the qualifier "any path the page's machinery table lists" to carry it. | fixed (second round): "the eval harness's cases". |
