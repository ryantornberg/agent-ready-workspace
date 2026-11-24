---
kind: record
last-reviewed: 2026-11-23
covers: plugin/skills/machine-self-check/SKILL.md
reviewed-at: a2d6a59, with the staged change of slice B6
---

# Instruction review: plugin/skills/machine-self-check/SKILL.md

This records the review of slice B6's new `machine-self-check` wrapper, for its author and whoever settles its findings.

**In short:** 1 finding: 1 contradiction, none blocking. The description sends a person here to check that their machine runs the workspace's tools after setup, but this change adds a per-machine step, adding the plugin's marketplace, that no step of the self-check checks and no setup step carries.

## Scope

In scope: the whole wrapper, new in this change: its `name`, its `description` and its body, read against the page its body names. The change was read with `git diff --cached`. Read beside it: `AGENTS.md`, `INDEX.md`, the playbook catalog `docs/playbooks/README.md`, `docs/how-tos.md`, `docs/machine-self-check.md` in full, the `browsers` and `adopt-the-workspace` wrappers' descriptions, a `git grep -n marketplace -- '*.md'` over the pages for the plugin's setup command, the description of every other wrapper under `plugin/skills/`, its selection cases `plugin/evals/machine-self-check-fires` and `-quiet`, `parts/wrappers.py` and `parts/wrappers.cases.json`, and the `wrappers` and `loaded_size` entries in `workspace.json`.

Run, on macOS, in the worktree, before any record was written: `python3 ws.py check` exits 0, with only `eval_record`'s usual no-base warning, and `python3 ws.py selftest` exits 0 and lists `wrappers: 17 of 17 cases` (verified). With the records written, `check` fails only on `review_index`, for the index rows the author adds at step 5 (verified). The 28 wrappers' descriptions come to 6,542 bytes against the 9,000 the `loaded_size` entry allows (verified, summing each `description` value). The selection cases have not run: `evals/README.md` says the first run waits for the maintainer's yes to its budget. So every claim below about which wrapper a model would load is inferred.

## Findings

| # | Class | Where | Finding | Disposition |
|---|---|---|---|---|
| 1 | contradiction | The description, "after setup", against `docs/machine-self-check.md` "Steps" and the catalog's "Three ways to follow a playbook" | Not blocking. The description sends a person here to check that their machine runs "this workspace's hooks, checks and tools", "after setup". This change adds a step each machine needs: the catalog says Claude Code loads the wrappers as the plugin `workspace`, and that "on a new machine, a person runs `claude plugin marketplace add ./` once" (verified, reading). None of the self-check's eleven steps checks that the plugin is known or loaded; step 4 looks only for hook and permission overrides (verified, reading). The README's marked setup steps, which the page's "When to run it" names as setup, do not carry the command either: `git grep -n marketplace -- '*.md'` finds it only in the catalog, `docs/layout.md` and `docs/parts.md` (verified). So a machine on which no wrapper ever fires passes the check this wrapper routes to. Add a check that the plugin loads, under step 4 or as its own step, and put the command in the README's marked setup steps. | deferred to M5: the self-check's own step for the plugin waits for M5, its prove-by milestone, which runs it on a real machine. The other half is fixed: the README and the seed README give the plugin's two setup commands. |

## Checked with no finding

- step: the body names one path, `docs/machine-self-check.md`, which exists and is a how-to with no `lane` key and no place on the waiting list, as the `wrappers` check confirms on this tree (verified). Its one action, to read the page and follow it, needs no input it does not name.
- trigger: the description repeats the three cases of the page's "When to run it": after setup, after a machine change, and when a guard seems not to run. Its "Not for" names `workspace:adopt-the-workspace`, whose description owns a team's setup, and the quiet case, "Set us up an instance of it", is that request (verified, reading). The `browsers` wrapper sends "the whole machine's setup" here, so the two agree.
- enforcement: the wrapper states no must or never of its own. The catalog's rules that bind it are tagged to `wrappers` cases that show them: a description that names no wrapper next to it fails `a wrong name or no description fails`, and a page that is missing fails `a wrapper whose page is missing fails` (verified, reading `parts/wrappers.cases.json`; selftest passes them). That a wrapper stays thin is tagged `prose`, and this one is: its body restates no step of the page.
- placement: the description, which loads into every session, holds only when to fire and the wrapper next to it that owns the nearby request; it restates no rule of the page. The body is one pointer.
- eval-case: the one behavior the wrapper asks is loading its page on a matching request, and its selection cases cover it: `machine-self-check-fires` (`min: 1`) and `machine-self-check-quiet` (`min: 0`, `max: 0`, `arm: both`), each `input_match` in the one form the check takes (verified, reading). What the page then asks is the page's own; `docs/machine-self-check.md` is marked unproven with `prove-by: M5` (verified, reading its front matter).

## Re-check

A fresh session re-read the wrapper on 2026-11-23, after the fix round, at a2d6a59 with the staged change of slice B6 (`git diff --cached`). It read the wrapper as staged, its canonical page, every other wrapper's description and the selection cases under `plugin/evals/`. `python3 ws.py check` exits 0, with only `eval_record`'s usual no-base warning; `python3 ws.py selftest` reports `wrappers: 18 of 18 cases` and `loaded_size: 4 of 4 cases`; the 28 descriptions now come to 7,535 bytes against the 9,000-byte ceiling (verified). No selection case has run, so what a description fires on stays inferred.

| # | Verdict | Evidence |
|---|---|---|
| 1 | upheld: the README half fixed, the self-check half deferred to M5 | The README and the seed README give the plugin's two commands (verified, reading). The self-check's steps still check nothing about the plugin, and its "When to run it" counts only the marked setup steps, which leave the plugin's block unmarked (verified, reading). M5 is the page's `prove-by` (verified), and the finding is not blocking, so the deferral stands. |

What a fix broke: Nothing.

What the first reading missed: Nothing.
