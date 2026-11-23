---
kind: record
last-reviewed: 2026-11-23
covers: kit/seed/evals-README.md
reviewed-at: a2d6a59, with the staged change of slice B6
---

# Instruction review: kit/seed/evals-README.md

This records the review of slice B6's change to the seed eval page, which becomes an instance's `evals/README.md`, for its author and readers.

**In short:** 6 findings: 3 step, 2 enforcement, 1 contradiction; 1 blocking. An agent told to run the cases on a person's yes meets a trust prompt the page no longer mentions. A team's first playbook fails the `wrappers` check, and a rewritten wrapper fails `kit_drift`; the page says neither. The check does not fail a case in another form, as the page says it does. The page's opening still says the workspace has no cases and the kit's cases stay in the kit.

## Scope

In scope: the section B6 adds, "The wrappers' selection cases". The whole page was read, as an instance's `evals/README.md`, with links read from the instance's `evals/` folder.

Read beside it: the staged diff; in the worktree, `AGENTS.md`, `INDEX.md`, `kit/kit.json`, `docs/decisions/0007-the-kit.md`, `README.md` and `evals/README.md` with their staged diffs, `docs/playbooks/README.md` ("Three ways to follow a playbook" and "Rules"), the wrappers under `plugin/skills/`, the cases `debugging-fires` and `debugging-quiet` and others under `plugin/evals/`, `plugin/.claude-plugin/plugin.json`, `.claude-plugin/marketplace.json`, `.claude/settings.json`, `parts/wrappers.py`, `wslib/kit.py` and `tests/test_kit.py`.

Run: a clone outside the worktree, at a2d6a59 with B6's staged change applied and committed there, then `python3 ws.py adopt` into a scratch folder. The instance holds 28 wrappers, as synced files, and 58 selection cases, as seeded ones; `python3 ws.py check` and `drift` exit 0 (verified). `claude plugin eval --help` shows every flag the page's command uses (verified, Claude Code 2.1.331). No eval run was started.

## Findings

| # | Class | Where | Finding | Disposition |
|---|---|---|---|---|
| 1 | step | "The wrappers' selection cases", the command block | Blocking. The page lets an agent start a run on a person's yes, and gives a command without `--trust-plugin`. `claude plugin eval --help` says "The first run in an untrusted plugin directory asks you to confirm (--trust-plugin answers for CI)" (verified). An agent's shell has no terminal to answer that prompt, so its first run fails or waits (inferred; no run was started). The kit's own `evals/README.md` warns of the prompt and says to answer it at the terminal; the seed drops that sentence (verified, the staged diff). Say that the first run asks for trust, and that a person answers it, or names `--trust-plugin` in their yes. | open |
| 2 | step | "The wrappers' selection cases", "The `wrappers` check fails a wrapper that lacks either kind" | Not blocking. The page names only what the check fails about a wrapper. It does not say every core playbook and how-to needs one. The README's step 4 and this page's **In short** send a team to write its first playbook. In the scratch instance, a new playbook with `kind: playbook` and no `lane` key fails `wrappers`: "is a core procedure with no wrapper; add one under plugin/skills/ with its selection cases, or list the page under waiting" (verified). The waiting list accepts only `M4` or `M8`, the kit's milestones, so an instance cannot defer its own page there (verified, `WAITS_FOR` in `parts/wrappers.py`). The check names the fix, but the page could say it: a new procedure needs a wrapper, named after its file, and one case of each kind. | open |
| 3 | step | "The wrappers' selection cases", "A wrapper that fails its case that fires in most of its runs is rewritten once" | Not blocking. In an instance, the wrappers are the kit's synced files (verified, `kit/kit.json` and the lock). In the scratch instance, an edit to the description of `plugin/skills/debugging/SKILL.md` makes `drift` exit 1 and `check` fail on `kit_drift` (verified). The page does not say that a rewrite means `python3 ws.py drift --keep PATH`, after which upgrades leave that wrapper alone. Nor does it say where "the result is recorded". | open |
| 4 | enforcement | "The wrappers' selection cases", "and a case in any other form" | Not blocking. The stated enforcement is false. The check reads only graders of `type: tool_used` on the Skill tool, and skips every other case (verified, `_cases` in `parts/wrappers.py`). In the scratch instance, a case folder with a `prompt.md` and an `llm` grader, and a folder holding a `case.yaml`, both leave `check` at exit 0 (verified). Say that the check fails a Skill grader in any other form. The kit's own `evals/README.md` carries the same sentence. | open |
| 5 | enforcement | "The wrappers' selection cases", "a person starts it, or an agent on that person's yes for that run" | Not blocking. The section states a rule, that no run starts without a person's yes, with no enforcement named. It sits outside the "Rules that make this worth doing" section, whose line "These are advice; no check holds them" covers only that list. The instance's `before-shell` hook passes the page's `claude plugin eval` command from an agent (verified, `python3 ws.py hook before-shell` with the command). Say that this is the agent's word, which nothing checks. | open |
| 6 | contradiction | **In short**; "The cases"; "The wrappers' selection cases" | Not blocking. The **In short** line says "this workspace has no eval cases yet", and "The cases" says "The kit's own cases test its invented order system and stay in the kit, so the first case here is your team's". The new section says "The kit gave you its own cases", and the instance holds 58 of them, whose requests name the invented order system, such as the nightly reconciliation job (verified, the scratch instance's `plugin/evals/debugging-fires/prompt.md`). Say that the kit's selection cases came with the wrappers, and that the instance has no outcome case yet. | open |

## Checked with no finding

- trigger: the section's heading and its link to the catalog's "Three ways to follow a playbook" resolve in the instance, since `check` passes its links (verified). The heading matches the anchor the catalog's Rules table links to.
- placement: the section is on the eval page, beside the outcome cases it is set against. It links the catalog for what a wrapper is, rather than restating it, and restates no rule that procedure endings states (verified, reading).
- eval-case: the page is an eval page with no proof mark, not a playbook or how-to. The selection cases it describes are the test inputs, and the `wrappers` check holds their presence (verified, reading).
