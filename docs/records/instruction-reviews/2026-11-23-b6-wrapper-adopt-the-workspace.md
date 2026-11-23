---
kind: record
last-reviewed: 2026-11-23
covers: plugin/skills/adopt-the-workspace/SKILL.md
reviewed-at: a2d6a59, with the staged change of slice B6
---

# Instruction review: plugin/skills/adopt-the-workspace/SKILL.md

This records the review of the adopt-the-workspace wrapper that slice B6 adds, for its author and its readers.

**In short:** 1 finding: 1 trigger, not blocking. No setup step a team follows loads the wrappers, so this description, like every other, never fires in a fresh clone or in an instance the kit makes. It is recorded once, here.

## Scope

In scope: the whole wrapper, its front matter (`name`, `description`) and its body, which the staged change adds (`git diff --cached`). Read beside it: `AGENTS.md`, `INDEX.md`, `docs/playbooks/README.md`, `docs/how-tos.md`, `docs/adopt-the-workspace.md`, every other wrapper under `plugin/skills/`, the cases `plugin/evals/adopt-the-workspace-fires` and `plugin/evals/adopt-the-workspace-quiet`, `parts/wrappers.py`, the `wrappers` and `loaded_size` entries in `workspace.json`, `.claude/settings.json`, `.claude-plugin/marketplace.json`, `plugin/.claude-plugin/plugin.json`, `kit/kit.json` and `evals/README.md`.

Run, on macOS: `python3 ws.py check` exits 0, with only `eval_record`'s usual no-base warning; `python3 ws.py selftest` reports `wrappers: 17 of 17 cases` and `loaded_size: 4 of 4 cases`; `claude plugin validate plugin`, on Claude Code 2.1.330, passes with one warning, for a missing icon (verified). The 28 descriptions come to 6,542 bytes against the 9,000-byte ceiling; this one is 273 (verified). No selection case has run yet, as `evals/README.md` says (verified, reading), so every claim below about what a description fires on is inferred.

## Findings

| # | Class | Where | Finding | Disposition |
|---|---|---|---|---|
| 1 | trigger | Front matter, `description`, against the catalog's "Three ways to follow a playbook", item 3 | Not blocking. Nothing in the setup a team follows makes Claude Code load the plugin, so this description never fires in a fresh clone or an instance. The project settings enable `workspace@agent-ready-workspace`, but `.claude/settings.json` has no `extraKnownMarketplaces` entry that says where that marketplace is (verified, by search). The one page that says to run `claude plugin marketplace add ./` is the catalog's item 3: `git grep marketplace -- '*.md'` outside records and plans finds only the catalog, layout and parts, and not the README, the seed README or the machine self-check (verified). Adopt's step 1 runs only the README's setup blocks. On this machine, `claude plugin marketplace list` shows no `agent-ready-workspace` marketplace, and this review's own session listed no `workspace:` skill (verified). That Claude Code ignores an enabled plugin whose marketplace it does not know is inferred. The finding holds for every wrapper and is recorded once, here, since adopt's step 1 is where an instance's setup runs. Put the marketplace step in the README's and the seed README's marked setup steps, or declare the marketplace under `extraKnownMarketplaces`, and have the machine self-check confirm that a `workspace:` skill loads. | fixed: the README and the seed README give, beside their setup steps and unmarked, the two commands that make Claude Code load the plugin: `claude plugin marketplace add ./`, then `claude plugin install workspace@agent-ready-workspace --scope local`, which leaves the shared settings file as committed (verified, with a scratch config folder: the plugin then lists as enabled, read in place from the folder). The catalog links them. A check for it in the machine self-check is deferred to M5, that page's prove-by milestone. |

## Checked with no finding

- contradiction: the description matches the page's purpose line and **In short** line and the how-to index row "Set the workspace up for your own team" (verified, reading). Both neighbors it names exist, and `workspace:machine-self-check` names this wrapper back for the request it excludes (verified).
- step: the body names one page, `docs/adopt-the-workspace.md`, which exists, is a how-to with no `lane` key and has numbered steps (verified). "From the top of this workspace" holds from the main copy or a worktree, since both hold `docs/`.
- enforcement: the wrapper states no must or never. The rule that a wrapper stays thin is tagged `prose` in the catalog; the name, page, neighbor and case rules are enforced by the `wrappers` check, whose cases pass (verified).
- placement: the 273-byte description says only when to fire and when not, and restates no step of the page (verified, reading).
- eval-case: the fires case asks to set up an instance for a team's code; the quiet case asks to check one laptop's hooks, which `workspace:machine-self-check` owns and the description names (verified, reading). The page is marked unproven with `prove-by: M5`.

## Re-check

A fresh session re-read the wrapper on 2026-11-23, after the fix round, at a2d6a59 with the staged change of slice B6 (`git diff --cached`). It read the wrapper as staged, its canonical page, every other wrapper's description and the selection cases under `plugin/evals/`. `python3 ws.py check` exits 0, with only `eval_record`'s usual no-base warning; `python3 ws.py selftest` reports `wrappers: 18 of 18 cases` and `loaded_size: 4 of 4 cases`; the 28 descriptions now come to 7,535 bytes against the 9,000-byte ceiling (verified). No selection case has run, so what a description fires on stays inferred.

| # | Verdict | Evidence |
|---|---|---|
| 1 | upheld: fixed, and the self-check half deferred to M5 | The README's and the seed README's "Try it" sections now give `claude plugin marketplace add ./` and `claude plugin install workspace@agent-ready-workspace --scope local`, unmarked, after the marked blocks; the marketplace file names itself `agent-ready-workspace`, `kit/kit.json` syncs `.claude-plugin/` and `plugin/`, and `.claude/settings.local.json` is git-ignored (verified, reading and `git check-ignore`). The catalog's item 3 links the README's setup. That the two commands make the plugin load was not run again here (inferred from the disposition). M5 is the machine self-check's `prove-by` (verified). |

What a fix broke: Nothing.

What the first reading missed: Nothing.
