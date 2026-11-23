---
kind: record
last-reviewed: 2026-11-23
covers: kit/seed/README.md
reviewed-at: 2bedbd8, with the uncommitted change of slice C8
---

# Instruction review: kit/seed/README.md

This records the review of the seed README's new section on checks, for its author and its readers.

**In short:** 3 findings: 3 contradiction; none blocking. The synced tutorial calls the section a checks table that lists every guard, and it holds neither. `ws.py list` leaves out the commit-message runs of three checks. Some guards live in the runner, not in parts.

## Scope

In scope: only the new section "What is checked, and by what", read as an instance's `README.md`, with links read from the instance's top folder. Read beside it: `docs/tutorials/get-oriented.md`, `docs/parts.md` ("The parts here"), `workspace.json`, this repository's `README.md` (its section of the same name), `wslib/runner.py` (`command_list`, `command_rules`, `command_commits`), `wslib/parts.py` (its account of `PHASES`), `parts/review_trailer.py`, `parts/commit_subject.py` and `parts/deny_list.py` (their `PHASES` and `COMMIT_MESSAGE` lines), `tests/test_kit.py`, and `docs/decisions/0007-the-kit.md` with its uncommitted change.

Runs (all verified):

- In the worktree: `python3 ws.py list` exits 0 and prints 45 parts. `python3 ws.py rules` exits 0 and prints 408 rules.
- The worktree's tracked files, with the uncommitted change, copied into a scratch git repository and committed there. In it, `python3 -m unittest tests.test_kit -b` runs 28 tests OK. `python3 ws.py adopt` made an instance: 197 synced, 25 seeded, 381 never synced.
- In the instance, before any commit: the section is at the README's heading "What is checked, and by what". `python3 ws.py list` exits 0 and prints 45 parts, the same names, no more and no fewer, as the table under "The parts here" in the instance's `docs/parts.md`. `python3 ws.py rules` exits 0 and prints 407 rules from 52 pages; every page in the instance with a `| Rule | Enforced by` table is among them. `python3 ws.py check` exits 0.
- In the instance: changing the section's link to `#the-parts-hereX` makes `check` fail with a `links` error on the README: "no heading for #the-parts-herex in docs/parts.md". Renaming the heading to "What is checked" makes `check` fail with a `links` error on the tutorial: `no heading for #what-is-checked-and-by-what in README.md [links]`. Both were restored.
- In the instance: `echo 'not json' | python3 ws.py hook before-shell` prints `ws: hook input is not JSON: JSONDecodeError` and exits 2.

## Findings

| # | Class | Where | Finding | Disposition |
|---|---|---|---|---|
| 1 | contradiction | "What is checked, and by what"; against `docs/tutorials/get-oriented.md`, "4. Watch a guard remind, then refuse" | Not blocking. The synced tutorial, which an instance also gets, says: "The README's checks table (linked as `../../README.md#what-is-checked-and-by-what`) lists every guard." In an instance that link now resolves (verified, `links` passes, and fails when the heading is renamed). But the section it reaches is one paragraph: it has no table, and names no guard. It sends the reader on to `docs/parts.md` and to two commands instead (verified, reading the instance's `README.md`). A newcomer following the tutorial is told to expect a list of guards on this page and finds a pointer. The section exists for this link, so the page and the tutorial need to agree on what the reader finds there: a table here, or tutorial wording that also fits a pointer (inferred). | fixed: the section now names the table in the parts here, which lists each check and guard one row each; the tutorial's own wording is a synced page of lane B's and is left as it stands. |
| 2 | contradiction | "What is checked, and by what", "`python3 ws.py list` prints them with the phases each check runs in" | Not blocking. `ws.py list` prints each check's `PHASES` only (verified, reading `command_list`). Three checks also run on the commit message, outside any phase: the commit-msg hook (`ws.py check --message`) and CI's `ws.py check --commits` run every check with `COMMIT_MESSAGE = True`, whatever its phases (verified, reading `command_message` and `command_commits`, and the instance's `.github/workflows/ci.yml`, whose comment on `check --commits` names "the instruction-review trailer"). So in the instance `list` prints `review_trailer` as `check in push`, and `commit_subject` and `deny_list` as `check in commit, ci` (verified). `docs/parts.md` ("The parts here") says `review_trailer` runs "on the commit message and at the push", and `commit_subject` "on the commit message" (verified). A reader who takes `list` as the record of when each check runs misses the commit-msg hook and the CI step that most often refuse a commit. | fixed: the section says the parts table tells which parts also read the commit message, and that `list` prints the phases. |
| 3 | contradiction | "What is checked, and by what", "Each check and guard is a part" | Not blocking. Some guards are the runner's own, not parts. In the instance the runner refuses a hook event it cannot read, with exit 2, and no part is involved (verified, the run under Scope). This repository's `README.md`, in its section of the same name, lists such rows: a hook refusing an event it cannot read, "The runner and `wslib/launch.sh`"; a part's own cases passing, "The runner"; the manifest's version, reasons and tiers, "The runner" (verified, reading). The engine is synced, so an instance has the same guards (inferred from decision 0007's Synced row). They appear in neither `ws.py list` nor "The parts here" (verified: the 45 names match exactly). A reader who trusts the sentence takes those two as the whole set of guards. | fixed: the section says the checks and guards are parts, and that the runner itself also refuses an unreadable event and a manifest for another engine version, with links to decisions 0004 and 0003. |

## Checked with no finding

- trigger: the heading text gives exactly the anchor the synced tutorial links to; in an instance `links` passes, and fails naming the tutorial's line when the heading is renamed (verified). The section sits after the setup steps, where a reader who has just run `ws.py list` would look next.
- step: both commands the section names run and exit 0 in a fresh instance before its first commit, and its link to `docs/parts.md#the-parts-here` resolves there (verified). `rules` covers every page with a rules table in the instance (verified).
- enforcement: the section states no must or never. Its heading is held by `links` in an instance (verified by renaming it). In the kit, `links` skips `kit/seed`, so the heading is held by `tests/test_kit.py`, whose `test_selftest_and_check_pass_in_the_instance` runs `check` in an adopted instance (verified, reading), and the kit's CI runs the tests (verified, `.github/workflows/ci.yml` runs `unittest discover`).
- placement: the section links the synced `docs/parts.md` instead of copying this repository's table into a seeded page. Decision 0007 says a seeded file never hears from the kit again, so a copied table would go stale at the first upgrade that adds a part; the link does not (inferred from decision 0007, "What it gave up"). No rule that procedure endings states is restated (verified, reading).
- eval-case: the section asks no new behavior of an agent; it describes where the checks are listed. The page carries no proof mark and is not a playbook or how-to (verified, reading).
