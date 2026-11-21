---
kind: record
last-reviewed: 2026-11-21
covers: .github/copilot-instructions.md
reviewed-at: 8b33280
---

# Instruction review: .github/copilot-instructions.md

This records the instruction review of the GitHub Copilot pointer file, for its author and for anyone changing what an agent tool loads.

**In short:** 2 findings: 1 contradiction, 1 eval-case. The page names the contract and the rule pages and passes its checks, but it labels only one of the ways a Copilot session differs from the contract it sends that session to.

## Scope

In scope: the whole page, its title and one paragraph, as committed at 8b33280. Read beside it: `opencode.json`, the other pointer file the `pointers` entry lists, for comparison; `AGENTS.md`, `CLAUDE.md`, `INDEX.md`, `docs/definition-of-done.md`, `docs/orchestration.md`, `docs/layout.md`, `docs/glossary.md`, `docs/rules/orders-api.md`, `docs/changing-the-machinery.md`, `docs/agent-settings.md`, the README's limits, decision 0005, `workspace.json`, `.claude/settings.json`, `.codex/hooks.json`, `parts/pointers.py` and its cases, `parts/rule_pages.py`, `parts/edit_ledger.py`, `wslib/ledger.py`, `evals/README.md`, `evals/arms.json` and `evals/cases/`. Listed `.github/`. Commands run: `python3 ws.py check` and `python3 ws.py rules`.

## Findings

| # | Class | Where | Finding | Disposition |
|---|---|---|---|---|
| 1 | contradiction | The paragraph under the title | The page sends a Copilot session to `AGENTS.md` and labels one exception: Copilot does not load the rule pages. It does not say that no hook runs under Copilot. So three things `AGENTS.md` tells that session do not hold for it: "A hook refuses edits to" the shelved `src/orders-service-v1`; a hook refuses an edit in the main copy while another live session holds it; and the commit check compares staged files with an edit ledger, which only a hook opens. Verified: `.github/` holds this file and `workflows/` only, the hooks are wired in `.claude/settings.json` and `.codex/hooks.json` only, the README's limits say the hooks are wired for two agent tools, and `wslib/ledger.py` says before-edit and before-shell hooks open the ledger. Inferred: `opencode.json` has the same gap, outside this record's scope. | deferred to M5: whether a Copilot session runs this repository's agent hooks is unmeasured. A second review found Copilot's own documentation saying its command line and its editor agent read `.claude/settings.json` hooks, so a line saying no hook runs would be false, and the page cannot say either way until a Copilot session is measured. M5 sets up the first instance from the kit and can measure it. |
| 2 | eval-case | The paragraph under the title | The page asks a Copilot session to find and read, before each edit, the rule pages whose `applies-to` matches the file. No eval case covers that lookup, and the page carries no `prove-by` milestone. Verified: no arm or case in `evals/arms.json` or `evals/cases/` names this file, and the nightly-job and big-report cases hand the rule page to the guided arm, "as an agent tool that loads rule pages would show it", per `evals/README.md`. Inferred: whether an agent does the lookup unprompted by a hook is unmeasured. | declined: the layout gives a proof field to playbooks and how-tos only, and a pointer file is neither. An eval of a Copilot session needs a runner for that tool, which no slice of M3 builds. |

## Checked with no finding

- step: both links resolve, `docs/rules/` holds one page with an `applies-to` key, and `python3 ws.py check` reports no `links` or `pointers` finding. With today's single pattern, `src/orders-api/**`, matching needs no syntax beyond a plain glob.
- trigger: "Before you edit a file" fires on every edit, which is when the rule pages apply, and the claim that Copilot does not load `docs/rules/` on its own agrees with the glossary's rule-page entry, labelled as the exception.
- enforcement: the page states no must or never; that it keeps naming the contract and the rule pages is held by `pointers#a pointer file that stops naming the rule pages fails`, a true tag in the layout page's rules table.
- placement: the file is 314 bytes, holds only routing, and counts toward the 6,000-byte ceiling of the `loaded_size` entry, which `python3 ws.py check` reports as passing.
