---
kind: record
last-reviewed: 2026-11-23
covers: docs/changing-the-machinery.md
reviewed-at: 157570e, with the uncommitted change of slice C8
---

# Instruction review: docs/changing-the-machinery.md

This records the review of C8's new `kit/` and `kit.lock.json` row in the machinery table, for its author and its readers.

**In short:** 2 findings, 1 blocking: 2 step. The blocking one: the row puts `kit.lock.json`, which exists only in an instance, on a path whose step 3 runs tests that an instance never gets, so the command fails.

## Scope

In scope: the new row "`kit/`, `kit.lock.json`" in "What counts as machinery", read against the whole page. Read beside it: `AGENTS.md`, `INDEX.md`, `README.md` and `docs/adopt-the-workspace.md` with their uncommitted changes, `workspace.json` (the `direct_push` machinery list and the `review_trailer` guidance list), decision 0007, `kit/kit.json`, `kit/seed/`, `wslib/kit.py`, and the C5e review of this page (`2026-11-22-c5e-changing-the-machinery.md`).

Runs (all verified): in a clone with the C8 change committed, `python3 -m unittest tests.test_core -k machinery -b` runs 8 tests OK, among them `test_the_machinery_page_and_the_manifest_hold_one_list`. An instance was adopted from that clone. Its seeded `workspace.json` lists `kit.lock.json` among `direct_push`'s machinery paths. It has no `tests/` folder, and `python3 -m unittest discover -b tests` there exits 1 with "Start directory is not importable: 'tests'".

## Findings

| # | Class | Where | Finding | Disposition |
|---|---|---|---|---|
| 1 | step | "What counts as machinery", the `kit/`, `kit.lock.json` row; "The path for a machinery change", steps 2 and 3 | Blocking. `kit.lock.json` exists only in an instance, so the row sends an instance's lock changes down "The path for a machinery change". This page is synced, so the instance gets the same path. Step 3 there fails: `tests/` is never synced (`kit/kit.json`), and `python3 -m unittest discover -b tests` exits 1 in a new instance (verified). C8 dropped that command from the "Done when" table of `docs/adopt-the-workspace.md` for the same reason, so the gap is known (verified, the diff). Step 2's "failing case first" has no default for the lock either. It holds data that `ws.py upgrade` or `ws.py drift --keep` writes, not code. The `outward-repos.json` row above says so for its own data file ("step 2's failing case does not apply to it") after the C5e review found the same gap; this row does not (verified). | fixed: step 3 says an instance has no `tests/` and runs `python3 ws.py drift` as its third command; the row says step 2's failing case does not apply to the lock, which holds data the kit's commands write. |
| 2 | step | "What counts as machinery", the `kit/`, `kit.lock.json` row | Not blocking. `kit/seed/README.md` and `kit/seed/evals-README.md` are guidance pages: the `review_trailer` entry in `workspace.json` lists both under `guidance` (verified). They also sit under `kit/`, which the row makes machinery. The page's opening sorts every change into a doc path or a machinery path, and its step 2 asks for a failing case. The row does not say that a seed page's change needs both the instruction review and the machinery path, or what failing case a wording change to a seed page needs. `tests/test_kit.py` holds the seed README to its setup steps and the drift check, so a case is possible for some changes (verified, `test_the_setup_steps_include_the_hooks_and_the_drift_check`). | fixed: the row says a change to a seed page is also a guidance change and takes the instruction review too. |

## Checked with no finding

- contradiction: the row matches the `direct_push` machinery list, which gains `kit/` and `kit.lock.json` in the same commit, and the test that compares the two passes (verified). "An upgrade changes the engine and the lock together" matches decision 0007's "Upgrade" paragraph and `kit.upgrade`, which writes synced files, the manifest's version and the lock in one run (verified, reading).
- trigger: the row is in the table that decides whether a path is machinery, and its link to decision 0007 resolves once that page is committed (verified: `check` exits 0 in the committed clone's instance).
- enforcement: a change to `kit/` or `kit.lock.json` reaches main only through a pull request. `direct_push` holds this through the machinery list, which the instance's seeded manifest carries too (verified, reading the instance's `workspace.json`).
- placement: the row holds one line of what and why and links decision 0007 for the rest, as the other rows do.
- eval-case: the page is unproven, `prove-by: M4` (verified, front matter).

## Re-check

A fresh session re-read the page on 2026-11-23, after the fix round, at 8162e8e with the uncommitted change of slice C8, using `git diff 3c15e23`. It ran on a scratch clone with that change committed and an instance adopted from it.

| # | Verdict | Evidence |
|---|---|---|
| 1 | fixed | Step 3 says an instance has no `tests/` and runs `python3 ws.py drift` third; in the instance it exits 0, "drift: none" (verified). The row says step 2's failing case does not apply to the lock. In the scratch clone, `python3 -m unittest tests.test_core -k machinery -b` runs 8 tests OK (verified). |
| 2 | fixed | The row says a change to either seed page also takes the instruction review, and `workspace.json` lists both under `review_trailer`'s `guidance` (verified, reading). |

Broke: none. The seed README now cites this page's line on pushing a new main once with `--no-verify`. That line exists under "The path for a machinery change", and in the instance the first push with the hooks on is refused by `direct_push` for 139 machinery paths (verified).

Missed: none.
