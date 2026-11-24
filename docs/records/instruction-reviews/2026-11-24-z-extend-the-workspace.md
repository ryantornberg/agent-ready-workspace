---
kind: record
last-reviewed: 2026-11-24
covers: docs/extend-the-workspace.md
reviewed-at: d2aa593, with the uncommitted change of the slice Z builder
---

# Instruction review: docs/extend-the-workspace.md

This records the instruction review of slice Z's change to extend the workspace, for its author and its readers.

**In short:** 2 findings, none blocking: 2 contradiction.

## Scope

In scope: the whole page, with most attention to the diff from d2aa593, which adds one sentence to "What this page covers": the contract routes a small change to pages only here, not to fix a bug. Read beside it: `AGENTS.md` and `CLAUDE.md` with their uncommitted change, `INDEX.md`, `docs/size-the-work.md`, `docs/procedure-endings.md`, `docs/definition-of-done.md` with its change, `docs/templates/fix-record.md`, `docs/records/defects.md`, and the pages this one links: layout, parts, changing the machinery, maintain the workspace, the research ladder, the playbook catalog, the how-to index, decision 0006, the evals README, orchestration, the decision record template, the decision interview, the instruction review and `evals/arms.json`. Every link and anchor on the page resolves. The five files step 5 names as the guided arm's match `evals/arms.json`.

## Findings

| # | Class | Where | Finding | Disposition |
|---|---|---|---|---|
| 1 | contradiction | Steps, step 1 | Not blocking. The new sentence says the contract routes a small change to pages here, and the contract, with its uncommitted change, now does: "A small change to pages only follows extend the workspace". Step 1 still calls running steps 2 to 8 "a labelled exception to the contract's 'How work flows', which sends a change that passes the gate to fix a bug". The page now says both that the contract routes the work here and that the contract sends it to fix a bug. The action is the same either way. Verified: `AGENTS.md`, "How work flows"; this page, "What this page covers" and step 1. | fixed: step 1 now says the contract routes the change here, not to fix a bug |
| 2 | contradiction | Steps, step 6 | Not blocking. Step 6 runs `python3 ws.py check` on the changed files, and step 7 stages and commits them afterwards. The definition of done's new item under "What does not count" says a green run of the checks on files never staged does not count: "stage first, then check". An agent following both cannot tell whether step 6's clean run counts as evidence. The plain check reads the working folder, so step 6's run is sound; the conflict is in what the definition of done says, but this page's order is what it names. Verified: `ws.py`'s usage text for `check` and `check --staged`; `docs/definition-of-done.md`, "What does not count". | fixed: the definition of done now discounts a clean `python3 ws.py check` only as proof of what was committed, so step 6's run stands |

## Checked with no finding

- step: each step names its input, action, output and a default for its decisions; the stops in steps 3, 6 and 7 all end in step 8's report. The new sentence gives no step of its own, and the three adjustments that follow it (step 2's owner, step 3 skipped, step 4 in place) are unchanged.
- trigger: the purpose sentence and In short line cover a small change to an existing page, and the contract's new routing line, the how-to index's row, INDEX.md's row and the request map's "Add a page", "fix this page" row all fire it.
- enforcement: each must and never on the page has a row in its rules table (verified, read). `python3 ws.py check` raises no `rules` finding on the page (verified); that each tagged case shows its rule is inferred from earlier reviews, not re-read here.
- placement: the new sentence states the routing once, where the page says which changes it covers; the commit, push and report rules are linked to procedure endings, not restated.
- eval-case: the page is `proof: unproven` with `prove-by: M5`, so its behavior needs no case yet.

## Re-check

A fresh session at the driver tier read extend the workspace on 2026-11-24 as it stands on fca7d9b with the slice Z builder's uncommitted change, with `git diff d2aa593 -- docs/extend-the-workspace.md`, and the contract, the definition of done, the size gate's page, the playbook catalog and ship a new deployable.

| # | Verdict | Evidence |
|---|---|---|
| 1 | The fix holds. | Verified: step 1 now says the contract's "How work flows" routes the change here, not to fix a bug, matching the sentence under "What this page covers" and the contract's bullet. Ship a new deployable keeps its own "labelled exception" wording, which stays true, since the contract does not route a new deployable. |
| 2 | The fix holds. | Verified: the definition of done now discounts a green `python3 ws.py check` only "as proof of what was committed", and says the commit check reads the staged files, as `python3 ws.py check --staged` does. Step 6's run before staging checks the working folder, and step 7's commit check reads what is staged; neither page now says step 6's run does not count. |

What the fixes broke: nothing found. Verified: every link and anchor on the page resolves (a link script), and `python3 ws.py check` reports nothing on it.

What the first reading missed: nothing found, blocking or not.
