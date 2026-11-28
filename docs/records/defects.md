---
kind: record
last-reviewed: 2026-11-22
---

# Defect register

Defects found in passing, kept until each is fixed or accepted, in the shape the [defect register template](../templates/defect-register.md) gives.

## Open

| Found | Where | What | Evidence | State |
|---|---|---|---|---|
| 2026-11-28 | `wslib/parts.py`, `Library.builtins` | The pre-push check loads a push check's library from the remote's tip by redirecting the `import` statement and `__import__` alone. A module at the tip that loads another with `importlib.import_module("wslib.x")` gets the one on disk, so its cases would call a library from another commit. Nothing in `wslib/` or `parts/` calls `importlib.import_module` today, so no push check is affected yet. | Found by M4 slice G1's delta re-check of #63, reading `Library.builtins`, which wraps `__import__` only (verified). That no module calls `importlib.import_module` is from a search of `wslib/` and `parts/` (verified). | open |
| 2026-11-23 | `docs/orchestration.md`, "The binding" | It says the `tiers` entry is "the only place a model name appears", but the eval harness sets its own model with `--model`, and `evals/README.md` names models in its commands. | Read `evals/run.py`'s argument handling and `evals/README.md` at `dace91e`; found by slice B5's review of decision 0014, which now says the binding is the only place a tier's model is set. | open |

## Closed

| Found | Where | What | Evidence | Closed | How |
|---|---|---|---|---|---|
| 2026-11-23 | `.gitignore`, beside `secrets_shell`'s `"file": ".env"` in `workspace.json` | The secrets file `ws.py with-secrets` reads, `.env` at the top of the main working copy, is not ignored by git, so a person's `git add -A` there would stage their tokens; the secret scan at the commit is the only stop. | `git check-ignore -q .env` exits 1 in the m3-b5 worktree at `dace91e`; `.gitignore` lists no `.env` pattern. Found by slice B5's review of decision 0001. | 2026-11-28 | M4 slice G0: `.gitignore` lists `.env`, so `git check-ignore -q .env` exits 0. An instance the kit makes gets the line, since the kit seeds `.gitignore`. `tests/test_kit.py` checks both. |
| 2026-11-25 | `docs/parts.md`, the `building` row; `tests/test_m3_a.py`; `docs/adopt-the-workspace.md` | The parts page says a milestone removes itself from `building` at sign-off, but a test pins `building` to `["M3"]` and the adoption page says it names M3. So M3's sign-off left M3 in `building`: removing it is a machinery change that fails that test and makes the adoption page false. | Read at `9902534`: the `building` row of `docs/parts.md`, the test's assertion on the manifest, and the adoption page's milestone-state row. Found at M3's sign-off. M4's first slice, which sets `building` to M4, is the place to fix all three. | 2026-11-28 | M4 slice G0: `building` is `["M4"]`. The test no longer pins a number: each milestone listed must have an approved plan and a record not signed off. The adoption page no longer names M3. The `proof` check now fails a `building` entry whose record is signed off, so a sign-off that leaves its milestone listed fails. |
