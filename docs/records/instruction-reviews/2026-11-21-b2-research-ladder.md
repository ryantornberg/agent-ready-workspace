---
kind: record
last-reviewed: 2026-11-21
covers: docs/research-ladder.md
reviewed-at: 8b33280, with the uncommitted change of the B2 builder
---

# Instruction review: docs/research-ladder.md

This records the instruction review of the new research ladder page, for its author and for agents about to search the workspace.

**In short:** 3 findings: 1 contradiction, 1 step, 1 trigger. An empty lookup has no next row and no stop, the eval-run note leaves out the rule page, and nothing in the index or the contract leads here.

## Scope

In scope: the whole page, which is new. Read beside it: `AGENTS.md`, `CLAUDE.md`, `INDEX.md`, `docs/definition-of-done.md`, `docs/orchestration.md`, `docs/layout.md`, `docs/glossary.md`, and the pages it links: `docs/agent-settings.md`, `docs/rules/orders-api.md`, `docs/playbooks/instruction-review.md`, `docs/question-log.md` and `evals/README.md`. Also read `evals/arms.json`, `evals/cases/` and `covered_files` in `parts/eval_record.py`. Ran `python3 tools/symbols.py` for a name that exists, for a missing one, and with `--contains`, plus `python3 ws.py rules` and `python3 ws.py check`, whose link check resolves every anchor the page uses.

A conflict between this page's "write only on a yes" and the orchestration page's "Write down what must outlive the session" bullet is recorded once, in the orchestration record, `2026-11-21-b2-orchestration.md`.

## Findings

| # | Class | Where | Finding | Disposition |
|---|---|---|---|---|
| 1 | step | Pick one lookup, the paragraph after the table | When a lookup comes back empty, the page says to move to another row but does not say which. What you already have has not changed, so the table points back at the same row. It also gives no point at which to stop searching and report that the thing was not found. Verified: read the section; `python3 tools/symbols.py NightlyJob src` printed "No definition" and exited 1, the empty case an agent meets. | fixed: an empty lookup moves to the next row down that fits; when the last fitting row is empty, the search stops and the report says so. |
| 2 | contradiction | Offer to write a finding down, the paragraph after the table | The page says a change to `INDEX.md` or `AGENTS.md` also needs a new eval run, which implies the other writes do not. The contract's rule covers "anything else the eval covers". `docs/rules/orders-api.md` is in the guided arm of the `nightly-job` and `big-report` eval cases, and the index's "Add a rule page" chain names `INDEX.md`, so the rule-page row's write can need a run too. Verified: grep of `evals/cases/` and the chain row. That `eval_record` then refuses the commit is inferred from reading `covered_files`. | fixed: the sentence now names any file the eval covers, a rule page an eval case names among them. |
| 3 | trigger | `INDEX.md`, Topics table; `AGENTS.md`, "Finding things" | No index row and no line in the contract's "Finding things" leads here, though that section is the short form of this page. `docs/layout.md`'s table of existing pages does not list it either. Only the orchestration page links here. Verified: grep over the workspace's Markdown. | queued for slice Z: a Topics row in INDEX.md, which the eval hashes. Until then the playbook catalog and how-to index, later in this slice, list the page; the contract's "Finding things" link to it is queued with the row. |

## Checked with no finding

- enforcement: `python3 ws.py rules` lists both rules rows, tagged `prose`. "Never run a second lookup" and "write only if the person says yes" each have a row.
- placement: the page expands the contract's "Finding things" without repeating it there, and the question log is labelled as not an offer, so the contract's question-log rule stands.
- eval-case: the page is marked `proof: unproven` with `prove-by: M4`.
