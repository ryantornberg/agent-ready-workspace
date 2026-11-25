# Changelog

What changed in each version, for someone deciding whether to take it. The [milestone records](docs/milestones/m1.md) say how each change was made and checked.

## Unreleased: M3

**Changed:**

- The engine's version is 0.4.0. Set the manifest's `version` to match, in the same step as the engine upgrade.
- `python3 ws.py check --commits BASE..HEAD` also runs `deny_list` on the lines each commit adds, the scan the machinery page asks for before a branch committed with `--no-verify` is pushed.
- `INDEX.md` gains a row for every page, chain and part M3 added, grouped under four headings. `AGENTS.md` links the request map and the reading paths, and routes a small refactor and a small change to pages. The definition of done names where each record keeps its report.
- `fix-a-bug.md` gains the fix path's gates, in a section marked unproven for M6: the fix brief, a stop before a risky change, and the test matrix. The three fix-a-bug cases' requests grant any approval those gates ask for.

- `freshness` is retired. `page_kinds` holds its review-date rule, with the same cases, beside the new kind and opening rules. `stale_pages` reads `page_kinds`.
- `eval_record` gates only the playbooks marked proven (decision record 0006). For each, pooled across its own cases, the guided arm must beat two lines, and pass no more than 3 runs fewer than the previous record's guided arm and the anchor its `proven-by` names.
- The eval hash leaves out a page's exact proof keys, and the runner takes them out of every page a gated arm reads, through one file, `evals/proofkeys.py`. It now also covers `wslib/shell.py`, the shell parser the graded hook uses.
- The shell parser moved from `parts/no_stage_all.py` into `wslib/shell.py`, and learned the commands M3's guards will judge. `no_admin_merge` imports it instead of loading another part's file.
- The manifest gains `building`, the milestones being built now.
- `check --staged` starts a fixed number of git processes: three for the files, and at most two more for the history the proof checks read.
- `AGENTS.md` keeps its rules in a table tagged with how each is enforced. `INDEX.md` gains rows for the layout, the glossary and decision 0006, and a table of cross-cutting chains.

**Added:**

- Per-case arm files (`arms`), additions to a shared arm (`add_files`), one-time arms outside every hash (`evals/one-time.json`, with the routed arm), the wrappers' plugin inside the sandbox, `run.py --baseline`, `--attempt`, `--rerecord`, and graders for a review protocol and a diagnosis.
- Checks: `page_kinds`, `chains`, `pointers`, `rules` (and `ws.py rules`), `loaded_size`, `proof`. `direct_push` also refuses a commit that changes a proof anchor pushed straight to main.
- Pages: the layout, the glossary, decision record 0006, the records folder, an archive hidden from search, and pointer files for GitHub Copilot and opencode.
- The safety machinery M2 did not build. Shell guards that judge a git or gh call by what it would really do, read from git's and gh's own config: `no_force_push` refuses a force push or deletion of main in every form the plan names; `no_discard` refuses a discard of uncommitted work, and `push_lease` a push, while another live session holds the main working copy; `outward_write` lets an agent write only to the repositories in `outward-repos.json`, and refuses every approval and `gh api graphql` call; `git_folder` and `git_folder_shell` refuse writes into a git folder or git config file and config changes to the keys the guards read; `secrets_shell` refuses environment dumps and reads of the secrets file. Each refuses a command it cannot judge. Decision 0004 is amended for each.
- `python3 ws.py merge NUMBER`, which merges a pull request with a merge commit only once every required check passed on its head commit, and `python3 ws.py with-secrets NAME -- PROGRAM`, which hands one program a value from the secrets file and never the shell.
- An after-edit reminder of the index chain a path is in, and a stop gate that refuses a session's first stop of a turn while the check or the fast tests fail. Session-start notices for a pending handoff note and for red CI on main; `python3 ws.py handoff`.
- One launcher, `wslib/launch.sh`, for every hook, git hook and CI step, with one Python process per hook call and a time budget per hook that the case runner holds on three systems. Baselines (`python3 ws.py baseline`): a check tolerates its old findings and fails a new one. `python3 ws.py pins` checks out the pinned repositories that answer.
- The kit: `python3 ws.py adopt PATH` makes an instance whose checks pass, `upgrade` takes a new kit in and refuses on drift, and `drift` and the `kit_drift` check name a hand edit to a file the kit owns. Decision 0007.
- About 60 pages of procedures, templates and records, each playbook and how-to marked proven or unproven with the milestone that is to prove it: the playbook catalog, the review orchestrator, the instruction review, red team review, debugging, the lane drafts for QA, product, DevOps, development and automation, two tutorials, and decisions 0006 to 0020. 28 skill wrappers in `plugin/skills/` point at the procedures that can run today, with a selection case each that should fire it and one that should not.
- Checks: `review_trailer` (a guidance change names its review record), `review_index`, `claim_marks`, `plan_budgets`, `decisions`, `wrappers`, `commit_subject`, `secret_scan`, `agent_settings`, `kit_drift`, `chain_reminder`, `ci_notice`, `handoff_loader` and `stop_gate`, besides those listed above.
- The eval's closing recording, R2, on 2026-11-24: 42, 18 and 0 of 45 runs passed every grader. The routed arm, the guided arm's files plus every page the index links to and the wrappers, passed 40 of 45 after one fix to the fix record template and procedure endings, against 39 needed.

**Fixed:**

- Found by M3's outside checks, each with cases that failed first, in [#57](https://github.com/ryantornberg/agent-ready-workspace/pull/57):
  - A push word the shell expands passed `no_force_push`, which read the word before the shell expanded it: `git push origin {+,}main` becomes `+main main`. A word of a push, or of a git call that may be one, holding unquoted braces or a glob, or directly followed by `(`, which zsh reads as a glob or a glob qualifier, is now refused as a push no guard can judge.
  - `git send-pack`, `git http-push` and the remote helpers called by name, such as `git remote-https`, pushed past `no_force_push`, which judged only `git push`. They are now refused outright.

**Known limits, for M4:**

- The same cause still opens other routes: braces or a glob in a write path or a `git config` key reach into `.git` past `git_folder_shell`, braces or a glob in a write path edit `outward-repos.json` past `outward_write`, and a word followed by `(` outside a push's own words runs code through a zsh glob qualifier. They close with the parser work in M4.
- Git can still reach main through a command it runs from its config, the environment or a URL, such as `GIT_EDITOR`, `core.fsmonitor`, `credential.helper`, `GIT_SSH_COMMAND` or an `ext::` URL. The README names this as the interpreter limit; M4 takes it up.
- The README's Limits list the other lines the shell parser still misreads.

## 0.3.0, 2026-11-17: M2, port what the work workspace learned

**Changed:**

- The engine's version is 0.3.0. Set the manifest's `version` to match, in the same step as the engine upgrade.
- The eval harness no longer depends on the engine. `evals/grade.py` loads the graded hook's own file, and `grade.py` imports nothing from `wslib/`, so an engine change leaves the eval records current. `run.py` still reaches the engine through `parts/eval_record.py`.
- `eval_record` needs 40 or more runs in every arm, pooled across the cases, before it compares the guided arm with the two-line arm.
- Git ignores `.claude/worktrees/`.
- The eval was recorded again on 2026-11-16, 135 runs on `claude-haiku-5-5`: 45, 19 and 0 of 45 passed every grader (95% intervals 92% to 100%, 29% to 57%, 0% to 8%); guided against two-line, one-sided Fisher exact p = 8.4e-11.
- `INDEX.md` routes what M2 added: the browser rule, decisions 0004 and 0005, the lease and worktrees, session-start notices, rule pages, the doc checks, and the push and admin-merge refusals. `AGENTS.md` gains one trap: a session refused because another holds the main working copy works in a worktree.
- The eval was recorded again after those edits, on 2026-11-16, 135 runs on `claude-haiku-5-5`: 40, 19 and 0 of 45 passed every grader (95% intervals 77% to 95%, 29% to 57%, 0% to 8%); guided against two-line, one-sided Fisher exact p = 2.5e-06.

**Added:**

- `direct_push`, a check the new pre-push hook runs: a push to main that adds a commit changing machinery is refused, and names each such commit with its path. It reads the machinery list from the remote's current tip. The machinery page's table and the manifest's list are one list, held together by a test.
- `no_admin_merge`, a shell hook that refuses `gh pr merge --admin`.
- A `push` phase for checks, and `ws.py check --push REMOTE`.
- One browser per session: `.mcp.json` and `.codex/config.toml` run the browser server pinned to `@playwright/mcp@0.0.84` with `--isolated`, the project settings turn the agent tool's browser plugin off, and the `browser_isolation` check holds all three. See `docs/browsers.md`.

- Decision record 0004, the hook contract: a part reads its event, its config and a snapshot, and the engine hands in the rest; a test holds every part to it.
- `session-start` and `session-end` events, in the workspace's shape and both tools' adapters and wiring. They never fail. Hooks on them: `stale_pages` and `stale_pins`.
- `pin_on_default`, a check that a staged pin is on its reachable upstream's default branch.

- The writing-session lease (decision record 0005): the first live agent session that edits a tracked file in the main working copy keeps it, any other is refused and sent to a worktree, and session end releases it. The `lease` hook and `wslib/lease.py`.
- `fast_forward`: at session start, the main working copy is brought up to `origin/main` when nothing would be moved under someone.

- `line_cites`, `in_short` and `rule_pages`, with the first rule page, `docs/rules/orders-api.md`. The snapshot gives the lines a change adds, from the same batch read at the commit.

**Changed:**

- A before-edit event's `path` is relative to the working copy that holds the file, a linked worktree included, and the event carries `working_copy`, `main` and `absolute`. `shelved` now refuses an edit to a shelved folder inside a worktree.

**Fixed:**

- `run.py` refuses a transcript holding the operator's identity written with backslashes, as a Windows path is.
- Found by the M2 red team, each with a test that failed first:
  - `direct_push` refused nothing when a machinery file was renamed away, or when a merge commit made a machinery change of its own. Both are now refused.
  - The lease let a second session edit a tracked file by naming it in another case on a case-insensitive file system.
  - Decision 0004's test blocked a list of modules and missed others that reach files or git. It now holds parts to a list of what is allowed.
  - `browser_isolation` read `--isolated` from a TOML comment. `line_cites` missed `file#L12` links. `rule_pages` never matched a pattern on a dot folder such as `.github/**`.
  - `eval_record` passed a record with runs dropped from an arm after the recording.

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
