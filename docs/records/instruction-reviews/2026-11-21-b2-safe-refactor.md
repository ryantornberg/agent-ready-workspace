---
kind: record
last-reviewed: 2026-11-21
covers: docs/safe-refactor.md
reviewed-at: 8b33280, with the uncommitted change of the B2 builder
---

# Instruction review: docs/safe-refactor.md

This records the instruction review of the new safe refactor page, for its author and for agents who restructure code.

**In short:** 4 findings: 2 contradiction, 1 step, 1 trigger. The routing past the contract is unlabelled, the two behavior-change exits disagree, step 3 has no default when there is no test harness, and nothing in the index leads here.

## Scope

In scope: the whole page, which is new. Read beside it: `AGENTS.md`, `CLAUDE.md`, `INDEX.md`, `docs/definition-of-done.md`, `docs/orchestration.md`, `docs/layout.md`, `docs/glossary.md`, and the pages it links: `docs/playbooks/fix-a-bug.md`, `docs/playbooks/test-first.md`, `docs/size-the-work.md` and `docs/parts.md`. Also read `docs/rules/orders-api.md`, which is shown on any edit under `src/orders-api`, and `src/README.md`. Ran `python3 tools/symbols.py ReconciliationWorker src`, `git grep -n ReconciliationWorker -- src`, `python3 ws.py rules` and `python3 ws.py check`.

## Findings

| # | Class | Where | Finding | Disposition |
|---|---|---|---|---|
| 1 | contradiction | Steps, step 2 | The contract's "How work flows" sends every small, one-repository change straight to fix a bug, and the orders-api rule page says a change there "is a bug fix or a feature, and follows its page". Step 2 sends a refactor that passes the size gate on to this page's step 3 instead. The page does not label this as an exception to the contract, so an agent that reads the contract first routes a small refactor into fix-a-bug, whose step 1 needs a test that fails. Verified: read `AGENTS.md` "How work flows", `docs/rules/orders-api.md` and fix-a-bug's step 1. | fixed: step 2 labels the exception, and queued for slice Z: the contract's routing line names this page for a small refactor. |
| 2 | contradiction | Steps, step 3, and the stop line under the steps | Step 3 says that if an assertion has to change, stop and go back to step 1, which reclassifies the work as a fix or feature and carries on. The stop line says to stop early and report if step 3 or step 5 shows a change in behavior. The two give different actions for one event. Step 3 also runs before any edit, so it cannot itself show a change; the assertion change it guards against happens in steps 5 and 6. Verified: read both. | fixed: step 3 no longer sends the reader back; the stop line covers a failing or changed assertion at any later step. |
| 3 | step | Steps, step 3 | Step 3 says to write and run a characterization test, and steps 5 and 6 run "the suite", but the page never says how to find the repository's test command, or what to do when the code has no harness to test through. Test-first gives both: its step 2 reads the repository's own build files and stops and reports with no harness, and its "Writing a good test" table moves down a level. This sample has no test files under `src/`. Verified: read step 3 and test-first; `find src -iname '*test*'` returned nothing. | fixed: step 3 points at test first's step 2 for the test command and a missing harness. |
| 4 | trigger | `INDEX.md`, Topics table | No index row routes a refactor to this page, and `docs/layout.md`'s table of existing pages does not list it. The index's "Add a page" chain names both files; this change touches neither. Only test-first's tidy-up step links here, so an agent with a refactor request that looks in the index first, as the contract says, does not find it. Verified: grep over the workspace's Markdown found the page linked only from test-first and the README's proof table. | queued for slice Z: a Topics row in INDEX.md, which the eval hashes. Until then the playbook catalog and how-to index, later in this slice, list the page. |

## Checked with no finding

- enforcement: `python3 ws.py rules` lists all four rules rows. The `shelved` tag names the case "an edit inside the shelved folder", which exists in `parts/shelved.cases.json` with `allow: false`. The other three rows are `prose`. The raw-literal gate says no check holds it yet, so it does not read as running today.
- placement: refactor steps belong on their own page, and the tokenize-then-swap pattern belongs with them. The page links test-first and fix-a-bug for behavior changes instead of repeating them. Step 4 runs several lookups, but each answers a different question, so it does not stack lookups.
- eval-case: the page is marked `proof: unproven` with `prove-by: M4`.
