---
kind: record
last-reviewed: 2026-11-22
covers: docs/templates/defect-register.md
reviewed-at: f757aed, with the uncommitted change of the B3 builder
---

# Instruction review: docs/templates/defect-register.md

This records the instruction review of the new defect register template, for its author and for agents adding or settling a row.

**In short:** 5 findings, none blocking: 2 contradiction, 1 trigger, 1 enforcement, 1 eval-case. The register exists now, but the review orchestrator and escape analysis still call it planned, the pages that should send defects here do not, and the line-number rule's tag is skipped by the commit hash the page asks for.

## Scope

In scope: the whole page, which is new, with the register file it describes, `docs/records/defects.md`, read beside it. Read beside it: `AGENTS.md`, `INDEX.md`, `docs/playbooks/instruction-review.md`, `docs/procedure-endings.md`, `docs/layout.md`, `docs/reader-standard.md`, `docs/authoring.md`, B3's row and the 2026-11-22 entries naming B3 in the M3 plan, and its "Queued for slice Z" list. Read the pages it links: `docs/playbooks/fix-a-bug.md` and `docs/playbooks/review-orchestrator.md` (with its diff), and beside them `docs/playbooks/escape-analysis.md`, `docs/size-the-work.md` (the feature ladder), `docs/templates/spec.md`, `docs/records/README.md`, `docs/records/lessons.md` and `docs/question-log.md`. Read `parts/line_cites.py` and its cases. Ran `python3 ws.py check` (passes, with one warning on fix a bug's eval record) and `python3 ws.py rules`. Ran the check's `PINNED` and `CITE` patterns on two sample register rows. Listed each eval case's covered files with `evals/run.py`'s `covered()`.

## Findings

| # | Class | Where | Finding | Disposition |
|---|---|---|---|---|
| 1 | contradiction | "Filling it in", the reconciling bullet | Not blocking. The page says "step 5 of the review orchestrator is where a review checks the change against the open rows", done by hand until a script exists. The review orchestrator's step 5 still says "The reconcile against deferred defects waits for slice B3's defect register: write 'not run' in the record", and its "What exists today" table says the register is "Planned for slice B3 of M3". An agent running a review follows the orchestrator and writes "not run". Escape analysis also still calls the register planned, in its "Deferred then lost" owner and in step 3. This batch's diff of the review orchestrator changes only step 10, and escape analysis is unchanged. Verified: read both pages and `git diff` of the orchestrator. Inferred: the page's "A script that reconciles the register is planned for M4" has no source here; a search of `docs/` for "reconcil" finds only the orchestrator's step 5. | fixed: escape analysis's "Deferred then lost" owner and step 3 now link the register; the review orchestrator's step 5 and its "What exists today" row are fixed by another worker, as finding 4 of the orchestrator's record; the M4 script claim, which had no source, is removed |
| 2 | trigger | "When to add a row" | Not blocking. The two sources the page names do not send their reader here. Fix a bug's step 2 says to "write it down and leave it alone", with no place. The review orchestrator's closing paragraph has the author defer a finding "to a named place", and the feature ladder's step 5 says the same, neither naming the register. Nothing in the M3 plan's "Queued for slice Z" list links the register from fix a bug or `INDEX.md`. So the page fires only for an agent that already opened it. Verified: a search for "defect register", "defects.md" and "defect-register", and a read of the queue. | queued for slice Z: fix a bug's step 2 links the register, since the eval hashes that page; the review orchestrator's closing paragraph now names it as a place to defer a finding |
| 3 | contradiction | "When to add a row", second bullet; "The four states" | Not blocking. A deferred review finding "goes here unless a tracker item already holds it". But the `filed` state keeps a row the tracker holds in the open table, "so a review can still find it here". The two rules disagree on whether the register holds defects a tracker holds. A finding filed before it was deferred never gets a row, so the reconcile against open rows misses it. Verified: the page's text. Inferred: the miss, since no reconcile runs yet. | fixed: a deferred finding a tracker item already holds now gets a row in the `filed` state, with its key |
| 4 | enforcement | Rules table, last row | Not blocking. The rule that a row's Where never names a line number is tagged `line_cites#an added line that cites a file by line number fails`. That check skips any added line holding a commit hash. The page asks the Evidence cell for "the code you read at which commit", and a closed row's How for a commit. So a row with a file and line number in Where and a hash in Evidence passes the check. Verified: ran `PINNED` and `CITE` on a sample row with a hash in Evidence (skipped) and one without (cited). | fixed: the row is now tagged `prose`, and says that `line_cites` skips a line holding a commit hash |
| 5 | eval-case | "When to add a row", first bullet | Not blocking. The page asks new behavior of an agent on the proven fix a bug path: reproduce or read the second bug first, add a register row, and commit it. No eval case covers it. `covered()` for `fix-a-bug`, `nightly-job` and `big-report` lists no template or record file. A template carries no `proof` key, by layout's page kinds table, so the page cannot be marked unproven with a `prove-by` milestone. Verified: ran `covered()` for the three cases. | declined: a template or reference page carries no proof key; the procedures that use it carry the proof state, as the plan sets the page kind |

## Checked with no finding

- step: every link resolves (`ws.py check` passes). The skeleton's two tables match `docs/records/defects.md` column for column. Each state names its table, and moving a row is defined. Verified.
- placement: committing links [procedure endings](../../procedure-endings.md#the-commit) rather than restating it, and the record file holds only its purpose line and the empty tables. Verified.

Also checked: the page is held as written mainly for agents, so the reader standard's worked example is not required. Inferred.

## Re-check

A fresh session re-read the page on 2026-11-22, after the fix round.

| # | Verdict | Evidence |
|---|---|---|
| 1 | fixed, with one break: see Broke | Escape analysis's "Deferred then lost" owner and step 3 link the register. The review orchestrator's step 5 reconciles by hand against the open rows, and its "What exists today" row links the register. The page now says no script does this yet. Verified: read the pages and their diffs. |
| 2 | half fixed: the queue holds no line | The review orchestrator's closing paragraph now names the register as a place to defer a finding. Verified. The M3 plan's "Queued for slice Z" list holds no line for fix a bug's step 2; its only B3 lines are the `AGENTS.md` tag and procedure endings' index row, and `git status` shows the plan unchanged. Verified. Not blocking. |
| 3 | fixed | "When to add a row" starts a deferred finding a tracker already holds in the `filed` state, with its key, which agrees with "The four states". Verified. |
| 4 | fixed | `python3 ws.py rules` shows the row tagged `prose`, and its text names the commit-hash gap in `line_cites`. Verified, with `parts/line_cites.py`'s `PINNED` skip read. |
| 5 | decline upheld | Layout's page kinds table gives a template only `kind` and `last-reviewed`, so the page cannot carry `proof` or `prove-by`. The behavior reaches the proven fix a bug path only through slice Z's queued link. Verified for the table; inferred for slice Z. |

Broke:

- Not blocking. The fix to finding 1 removed this page's claim that M4 plans a reconcile script, since it had no source. The review orchestrator's new "What exists today" row now says "M4 plans a script for it", still with no source. Verified: a search of `docs/plans/` and `docs/` for "reconcil" finds no M4 plan for it.

Missed:

- Not blocking. "When to add a row" says a deferred review finding "goes here". The review orchestrator's closing paragraph names the register only as one choice, "a named place, such as the defect register". An author following the orchestrator may defer elsewhere, and step 5's reconcile then misses the finding. Verified: both pages' text. Inferred: the miss.
