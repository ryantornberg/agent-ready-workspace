---
kind: record
last-reviewed: 2026-11-23
covers: docs/playbooks/regression-triage.md
reviewed-at: 1a18d68, with the uncommitted change of the B4 slice session
---

# Instruction review: docs/playbooks/regression-triage.md

This records the instruction review of slice B4's new regression triage playbook, a QA lane draft, for the change's author.

**In short:** 8 findings: 5 step, 3 contradiction; none blocking. "Take the first row that fits" makes the environment, test defect and intended behavior classes unreachable for a failure that still fails. Re-checking at the tip of main makes flaky unreachable once main has moved. Off-checkpoint notes are classified without a re-check. The tracker search links a page with no search. Cleanup deletes evidence the committed report still names.

## Scope

In scope: the whole page, which is new and untracked. Read beside it: `AGENTS.md`, `INDEX.md`, `docs/layout.md`, `docs/authoring.md`, `docs/procedure-endings.md`, `docs/reader-standard.md`, `docs/extend-the-workspace.md`, the instruction review playbook, and every page the page links to: decision 0006, regression run, the regression run report template, tracker operations, the bug report template and the regression candidates ledger template. Also read the regression case template, saved workflows, `src/README.md`, decision 0001, the catalog's "Lane drafts" section and diff, and the README and reading-paths rows that name the page.

Ran: `git -C src/orders-api rev-parse origin/main`, which printed `1a18d68...`, the workspace's own commit, since this sample pins nothing; `grep -rn M10 docs README.md` for what M10 plans; `grep -n -i regress INDEX.md`, which finds nothing; and `python3 ws.py check`, which reports nothing on this page. Did not run step 4's `git fetch`, which writes refs.

## Findings

| # | Class | Where | Finding | Disposition |
|---|---|---|---|---|
| 1 | contradiction | The seven classes | Not blocking. The table says "Take the first row that fits". Its first row fits any failure that fails on re-check with no open ticket; its second fits one with an open ticket. So every failure that still fails lands in one of those two rows. The environment, test defect and intended behavior rows can then never take one. A stale selector is drafted as a bug, and step 8's case-file fixes never fire for it. The default for "when two classes fit and the table's order does not settle it" never fires either, since the order always settles it. Verified by reading the table's "When" column against its order rule. | fixed: the table now reads top to bottom with the pass classes first, then environment, test defect and intended behavior, then known and open, and new regression last as the fallback; the default is new regression when unsure. |
| 2 | step | Steps, step 4; The seven classes, the flaky and fixed upstream rows | Not blocking. Step 4 re-checks at the tip of main by default. Flaky means "passes on re-check at the run's commit"; fixed upstream means "at a newer commit". Once main has moved since the run, every pass is fixed upstream, and flaky is unreachable. A flaky case then counts as fixed and, per the candidates template, may earn a ledger row. The step also never says how the environment comes to run the tip of main, when `src/<repo>` is a submodule at a pinned commit. Its fallback, "record its commit", gives no command for the environment's commit. And the report template records no account, though step 4 reuses "the same account the run used". Verified: the class table, step 4 and the report template's fields. Inferred: how an agent brings the environment to the tip of main. | fixed: step 4 re-checks the environment as it stands, on the fixture's account, records its commit as regression run's step 3 says, and never redeploys without a yes; flaky now means a pass with nothing naming a fix, fixed upstream a pass at a newer commit with a named fix. |
| 3 | step | Steps, step 5 | Not blocking. Step 5 classifies "each off-checkpoint note the same way". Step 4 re-checks only failures, so a note has no re-check result. Four of the seven rows turn on that result: new regression, known and open, flaky and fixed upstream. The page gives no default for classifying a note. Verified by reading steps 4 and 5 against the table. | fixed: step 5 says a note has no re-check and gets environment, test defect, intended behavior, new regression, or `none` when no row fits with evidence. |
| 4 | step | Steps, step 5 | Not blocking. Step 5 says "Search the tracker for tickets on each failure, as tracker operations says for reads". Tracker operations has no search. Its step 2 reads the items a request names, and when none is named it asks the person which, with no answer meaning no write and a stop. An agent following that link asks the person once per failure. The search for a duplicate lives in the bug report template's "Before you write". Verified: tracker operations' steps and operations table. | fixed: step 5 now searches as the bug report template's "Before you write" says, and reads a found ticket through tracker operations. |
| 5 | step | Steps, step 6 | Not blocking. Step 6 shows every draft "as a multi-select" in one message. Claude Code's question tool takes a few options per question, so a run with many drafts does not fit one multi-select; the page gives no fallback, such as a numbered list to answer in text. Inferred: from the tool's limits as known to the reviewer, not run here. | fixed: step 6 adds a default: with more drafts than the question tool takes, ask once as a numbered list answered in text. |
| 6 | step | Steps, step 3 | Not blocking. Step 3 says a shared environment "needs the person's yes, as in the run". In the run, naming it in the request is the yes; here the request names a run folder, not an environment. The page gives no default when the run's environment is shared and no yes comes. The step's own default, the person's local environment, may lack the run's account and build, which step 4 needs. Verified by reading step 3 beside regression run's step 1. | fixed: step 3 re-checks on the environment the report names; a shared one needs the person's yes first, and with no yes the session stops and reports. |
| 7 | contradiction | Steps, step 9 | Not blocking. Step 9 deletes "the run's bulky local evidence", keeping only a waiting draft's. The report template says the committed report names evidence files by name only, "so a reader asks the runner for them". After triage those names point at deleted files, for every class but a waiting draft. Neither page labels the exception. Verified by reading step 9 and the template's "Where copies go". | fixed: step 9 marks each deleted file's name in the report as "deleted after triage"; the report template labels the by-name rule as an exception that holds until triage deletes the evidence. |
| 8 | contradiction | The paragraph under the lane-draft line | Not blocking. The page says "This repository has no regression suite; one is planned for M10." Regression run's table says the suite is "None in this repository. An instance keeps its own", and the case template says "This repository holds no suite and no cases". No plan names a suite for this repository in M10. Verified: `grep -rn M10 docs README.md` finds only lane-draft lines and the docs audit's schedule. | fixed: the line now reads "This repository has no regression suite; an instance keeps its own.", matching regression run and the case template. |

## Checked with no finding

- trigger: the purpose line, the **In short** line and the catalog row all name sorting a finished run's failures and filing the picked ones, in a fresh session. Regression run's "Which page wins" routes here. `INDEX.md` has no row for the page; extend the workspace's step 5 queues an eval-covered row by default, so its absence is that queue, not this page's text.
- enforcement: each must and never on the page has a Rules row: the fresh session, one re-check, one class, a closed ticket as a new regression, asking once and filing only the picks, not loosening an expectation, releasing the environment, and marking claims. Each is tagged `prose` except the report row, which keeps `eval:fix-a-bug` as the page's peers do.
- placement: step 10 and step 8's commit link procedure endings instead of restating it; the bar for a ledger row is linked, not copied.
- eval-case: the page is marked `proof: unproven` with `prove-by: M10`, and `workspace.json`'s `building` list holds only `M3`.

## Re-check

A fresh session's reading after the fix round, on `1a18d68` with the uncommitted change of the B4 slice session. Read the whole page, the contract, procedure endings, and each page the changed text links to: regression run's steps, the bug report template's "Before you write", tracker operations' steps, the regression candidates template's "The bar", and the report template. Ran no command: step 4 names none of its own, and regression run's step 3 commands were run for that page's re-check.

| # | Verdict | Evidence |
|---|---|---|
| 1 | upheld | Verified: the table now reads top to bottom with fixed upstream and flaky first, then environment, test defect and intended behavior, then known and open, and new regression last, as "no row above fits". A failure that still fails reaches the environment, test defect and intended behavior rows before the ticket rows. An unsure one defaults to new regression. |
| 2 | upheld | Verified: step 4 re-checks the environment as it stands, on the fixture's account, records the commit as regression run's step 3 says, and never redeploys without a yes. The Rules row matches. Flaky now turns on no fix being named, so it stays reachable once main has moved. |
| 3 | upheld | Verified: step 5 gives a note one of the four classes that need no re-check, or `none`. |
| 4 | upheld | Verified: step 5 links the bug template's "Before you write", which holds the search over open and closed tickets. A found ticket is read through tracker operations' steps. Both anchors exist. |
| 5 | upheld | Verified: step 6 gives the numbered-list fallback. Inferred: the question tool's limit, as in the first reading. |
| 6 | upheld | Verified: step 3 re-checks on the environment the report names, and stops with no yes for a shared one. The stop line releases any claim first. |
| 7 | upheld | Verified: step 9 marks each deleted file's name in the report. The report template's "Where copies go" says the names hold until triage deletes and marks them. Inferred: the marks are committed, since procedure endings' commit runs after the last step. |
| 8 | upheld | Verified: the line under the lane-draft line matches regression run's table and the case template. |

What a fix broke:

- Not blocking. Steps, step 2. The report template's fix for its finding 2 says the person writes each device checklist result on its line, "where triage reads it". This page's step 2 loads only the failures, blocked cases and off-checkpoint notes, and no step reads the checklist. A human case the person marks failed is never classified or drafted. Verified by reading step 2 beside the template's "Device checklist" bullet.

What the first reading missed:

- Not blocking. Steps, step 2: its output includes the blocked cases, but no later step takes them as input, and step 10's report gives no count for them. Verified by reading steps 3 to 10.

## Known defects

What stays open after the one fix round the plan allows, each not blocking.

- Not blocking, what a fix broke: no step reads the person's device checklist results, so a human case marked failed is never classified. Known defect, for M10.
- Not blocking, what the first reading missed: the blocked cases step 2 loads feed no later step, and the report gives no count for them. Known defect, for M10.
