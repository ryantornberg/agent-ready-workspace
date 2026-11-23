---
kind: record
last-reviewed: 2026-11-23
covers: kit/seed/README.md
reviewed-at: a2d6a59, with the staged change of slice B6
---

# Instruction review: kit/seed/README.md

This records the review of slice B6's change to the seed README, which becomes an instance's `README.md`, for its author and readers.

**In short:** 2 findings: 2 contradiction; none blocking. Every instance and the kit declare the same marketplace name, so on a machine holding two of them, the folder added last serves the wrappers to all of them. And "the nightly job" names nothing in an instance, while the contract it loads says the phrase means `ReconciliationWorker`.

## Scope

In scope: the block B6 adds under "Try it", which tells a person to load the wrappers in Claude Code with two commands. The whole page was read, as an instance's `README.md`, with links read from the instance's top folder.

Read beside it: the staged diff; in the worktree, `AGENTS.md`, `INDEX.md`, `kit/kit.json`, `docs/decisions/0007-the-kit.md`, `README.md` and `evals/README.md` with their staged diffs, `docs/playbooks/README.md` ("Three ways to follow a playbook" and "Rules"), the wrappers under `plugin/skills/`, several selection cases under `plugin/evals/`, `plugin/.claude-plugin/plugin.json`, `.claude-plugin/marketplace.json`, `.claude/settings.json`, `parts/wrappers.py`, `wslib/kit.py` and `tests/test_kit.py`.

Run: a clone outside the worktree, at a2d6a59 with B6's staged change applied and committed there, then `python3 ws.py adopt` into a scratch folder. In the instance, `python3 ws.py check` and `drift` exit 0, and `tools/setup_steps.py README.md` prints only the two marked blocks, so the new block is not a setup step (verified). The lock classes `.claude-plugin/marketplace.json`, `.claude/settings.json` and `plugin/skills/` as synced and `plugin/evals/` as seeded (verified). With `CLAUDE_CONFIG_DIR` set to scratch folders, Claude Code 2.1.331 ran both commands from the instance's top folder with exit 0. The first declared the marketplace in user settings, by absolute path. The second wrote `"workspace@agent-ready-workspace": true` to `.claude/settings.local.json`, which the instance's `.gitignore` ignores (verified, `git check-ignore`). With the marketplace alone, `claude plugin list` shows no plugin, so the install is needed (verified).

## Findings

| # | Class | Where | Finding | Disposition |
|---|---|---|---|---|
| 1 | contradiction | "Try it", the block on loading the wrappers | Not blocking. The page says the commands run once on each machine and install the plugin "for this folder only". That does not hold when the machine holds the kit's clone and an instance, or two instances. Every instance gets the kit's `.claude-plugin/marketplace.json`, named `agent-ready-workspace`, as a synced file, and its synced `.claude/settings.json` enables `workspace@agent-ready-workspace` (verified, the lock). A person makes an instance from a kit clone, and takes each upgrade from one, so both are on the machine; the kit's README tells them to run the same two commands there. In a scratch config, after both commands in the kit clone and then in the instance, the second `marketplace add ./` printed that the marketplace "now points at" the instance. `claude plugin list` from the kit clone then shows its install "Read from" the instance's `plugin/` (verified). A clone made in a second folder, and a worktree under `.claude/worktrees/`, also list the plugin as read from the folder added last (verified). So sessions in the other folder are listed as loading this folder's wrappers, without that folder's own wrappers (inferred: the list's "Read from" line is evidence; no session was started). Renaming the marketplace means keeping two synced files. Say that one marketplace name serves one folder per machine, or give each instance its own name. | open |
| 2 | contradiction | "Try it", "The nightly job does not run them, since it has no Claude Code" | Not blocking. An instance has no nightly job: its seeded `.github/workflows/ci.yml` runs weekly, and the kit's `cold-clone` job, which reads the marked setup blocks nightly, stays in the kit (verified, the instance's workflows folder). The instance's `AGENTS.md` says "The nightly job" means `ReconciliationWorker`, and its `INDEX.md` maps "the nightly job" to it (verified). An agent reading the sentence is pointed at the sample worker. What the sentence means here is that the block carries no `<!-- setup -->` mark, so no setup reader runs it. Say that instead. The kit's `README.md` carries the same sentence, where the alias also applies. | open |

## Checked with no finding

- step: both commands exist with the flags given (verified, `claude plugin marketplace add --help` and `claude plugin install --help`). Both ran with exit 0 from the instance's top folder, the local settings file is ignored, and the shared settings file stays as committed (verified, scratch config).
- trigger: the link to the playbook catalog's "Three ways to follow a playbook" resolves in the instance, since `check` passes its links, and that section names the two commands in this README's setup (verified).
- enforcement: the block says a person runs the commands, as a description, and claims no guard. The instance's `before-shell` hook passes both commands from an agent (verified, `python3 ws.py hook before-shell` with each command), and the page does not say otherwise.
- placement: the block belongs with the other per-machine setup under "Try it". It restates no rule that procedure endings states (verified, reading).
- eval-case: the page is a README with no proof mark, and the block asks a person, not an agent, to act. The wrappers' own selection is tested by their cases under `plugin/evals/` (verified, reading).
