# Changelog

What changed in each version, for someone deciding whether to take it. The [milestone records](docs/milestones/m1.md) say how each change was made and checked.

## Unreleased: M2, port what the work workspace learned

**Changed:**

- The eval harness no longer depends on the engine. `evals/grade.py` loads the graded hook's own file, and neither `grade.py` nor `run.py` imports anything from `wslib/`, so an engine change leaves the eval records current.
- `eval_record` needs 40 or more runs in every arm, pooled across the cases, before it compares the guided arm with the two-line arm.
- Git ignores `.claude/worktrees/`.
- The eval was recorded again on 2026-11-16, 135 runs on `claude-haiku-5-5`: 45, 19 and 0 of 45 passed every grader (95% intervals 92% to 100%, 29% to 57%, 0% to 8%); guided against two-line, one-sided Fisher exact p = 8.4e-11.

**Fixed:**

- `run.py` refuses a transcript holding the operator's identity written with backslashes, as a Windows path is.

## 0.2.0, 2026-11-16: M1, make the core hold weight

A red team ran attacks against the first version, and several claims in the README did not survive them. Each failure became a test that failed before its fix and passes after it. [The M1 plan](docs/plans/m1-make-the-core-hold-weight.md) lists them; [EVIDENCE.md](EVIDENCE.md) says how to check each one.

**Breaking for anyone who adopted the first version:**

- Hook events now have a versioned shape, `{"version": 1, ...}`, or come through a named adapter (`--tool claude-code`, `--tool codex`). Anything else is refused. Re-copy the wiring in `.claude/settings.json`.
- The manifest must name the engine's version, give a `why` for every part, and bind every tier to a model and an effort. A part leaves it only by being listed under `retired`, with a reason.
- The shell hook no longer refuses `git add -A`; it reminds, and the commit check refuses a staged file the agent's edit tools did not write. See [decision 0002](docs/decisions/0002-hooks-remind-the-commit-enforces.md).
- The engine moved into `wslib/`. `ws.py` and `tools/symbols.py` only start it. See [decision 0003](docs/decisions/0003-the-engine-in-one-folder.md).
- An edit to `AGENTS.md`, `INDEX.md` or the eval harness now fails the commit until the eval is run again.

**Added:**

- Orchestration rules: three tiers bound to a model and an effort in the manifest, and a hook that refuses a delegated task naming no tier.
- A size gate, a hand-off plan template, a milestone record template, and a page on changing the machinery.
- A deny-list check that keeps private terms out of files, file names, commit messages and identities, read from a list outside the repository.
- An edit ledger and a commit-msg hook.
- Hooks for Codex CLI, with one recorded run.
- An eval that can lose: three cases, three arms (the guidance, a two-line instruction, nothing), 45 recorded runs per arm, and a CI step that re-grades every stored transcript. The agent runs inside Claude Code's own sandbox. In the recording of 2026-11-16, 44, 19 and 0 of 45 runs passed every grader; guided against two-line, one-sided Fisher exact p = 1.6e-9.
- A gate on that eval: counting runs that pass every grader, the guidance must beat the bare model in each case, and beat the two-line instruction across the cases by a one-sided Fisher exact test at p < 0.05.
- Check phases (`--phase commit|ci|nightly`), `--version`, a CI permissions block and a weekly CI run.

**Fixed:**

- A broken check no longer locks out the session that repairs it, and a manifest edit can no longer switch the checks off.
- Page checks skip pages inside code repositories under `src/`, report files they cannot decode, and agree between the working folder and the commit. The commit check starts three git processes however many files the workspace has.
- `AGENTS.md` and `INDEX.md` carry review dates, and a code name in the contract must still exist.
- The link reader reports a line over 10,000 characters; `symbols.py` no longer reads `new Order(1),` as a constructor.
- The eval harness: a `__pycache__` folder no longer counts as an edit, the harness's own git calls ignore the operator's git config, a command's whole output is kept, the report grader counts a claim marked verified however it is set, the hash covers the hook a grader runs, the agent gets only the scaffold files the hash covers, a timed-out run fails, and the machine's temporary folder is kept out of transcripts.

## The first version, 2026-11-14, untagged

The contract, the index, the manifest, six parts, one playbook and one eval case with ten recorded runs.
