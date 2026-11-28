---
kind: record
last-reviewed: 2026-11-22
---

# Defect register

Defects found in passing, kept until each is fixed or accepted, in the shape the [defect register template](../templates/defect-register.md) gives.

## Open

| Found | Where | What | Evidence | State |
|---|---|---|---|---|
| 2026-11-23 | `docs/orchestration.md`, "The binding" | It says the `tiers` entry is "the only place a model name appears", but the eval harness sets its own model with `--model`, and `evals/README.md` names models in its commands. | Read `evals/run.py`'s argument handling and `evals/README.md` at `dace91e`; found by slice B5's review of decision 0014, which now says the binding is the only place a tier's model is set. | open |
| 2026-11-23 | `.gitignore`, beside `secrets_shell`'s `"file": ".env"` in `workspace.json` | The secrets file `ws.py with-secrets` reads, `.env` at the top of the main working copy, is not ignored by git, so a person's `git add -A` there would stage their tokens; the secret scan at the commit is the only stop. | `git check-ignore -q .env` exits 1 in the m3-b5 worktree at `dace91e`; `.gitignore` lists no `.env` pattern. Found by slice B5's review of decision 0001. | open |
| 2026-11-25 | `docs/parts.md`, the `building` row; `tests/test_m3_a.py`; `docs/adopt-the-workspace.md` | The parts page says a milestone removes itself from `building` at sign-off, but a test pins `building` to `["M3"]` and the adoption page says it names M3. So M3's sign-off left M3 in `building`: removing it is a machinery change that fails that test and makes the adoption page false. | Read at `9902534`: the `building` row of `docs/parts.md`, the test's assertion on the manifest, and the adoption page's milestone-state row. Found at M3's sign-off. M4's first slice, which sets `building` to M4, is the place to fix all three. | open |
| 2026-11-28 | `evals/grade.py` and `run.py`, run as scripts from `evals/` | Python puts the script's own folder, `evals/`, first on the import path, so a file such as `evals/shlex.py` would stand in for the standard library module the shell parser imports, and change grades. No such file exists, and neither eval hash covers one if it is added. | Found by the re-check of M4 slice H0a's pull request 64; the same at H0a's base, `f04fddf`, so open on main. Inferred from Python's import path rules; the re-check showed it. | open |
| 2026-11-28 | `parts/eval_record.py`, one-time records under `evals/runs/<case>/one-time/` | Nothing checks a one-time record's hashes: `eval_record` gates only the record of a proven page's case, so the twelve one-time records may go stale, or hold a grader hash that no longer matches, with no finding. `grade.py --recorded` re-grades their transcripts, but reads neither hash. | Found by the re-check of M4 slice H0a's pull request 64; the same at H0a's base, `f04fddf`, so open on main. | open |
| 2026-11-28 | `parts/eval_record.py`, `imported_files`, which finds the modules a graded hook imports for the grader hash | It cuts comments with a pattern that does not know strings, so in `x = '#'; import wslib.shell` the import is cut away; and an `importlib.import_module` call given a name the line does not spell, such as `'ws' + 'lib.shell'`, names no package it can see. Either form leaves a module out of the grader hash, with no fail-closed path. No graded hook uses either form today. | Found by the delta re-check of M4 slice H0a's pull request 64: both forms return no file. Reading the module with `ast`, which decision 0004's list of modules a part may import leaves out, would close the first. | open |

## Closed

| Found | Where | What | Evidence | Closed | How |
|---|---|---|---|---|---|
