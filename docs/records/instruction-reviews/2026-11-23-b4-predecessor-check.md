---
kind: record
last-reviewed: 2026-11-23
covers: docs/predecessor-check.md
reviewed-at: 1a18d68, with the uncommitted change of the B4 slice session
---

# Instruction review: docs/predecessor-check.md

This records the instruction review of slice B4's new how-to for checking a shelved predecessor, a product lane draft, for the change's author.

**In short:** 5 findings: 2 contradiction, 2 step, 1 trigger; 1 blocking. Step 8's "writes no file" drops the question-log entry. Only "carried over" can ever be marked verified. An unlabelled bug is stopped as not major. No page handling a security bug sends it here. A `no` fix decision lacks the initials and date the rule asks for.

## Scope

In scope: the whole page, which is new and untracked. Read beside it: `AGENTS.md`, `CLAUDE.md`, `INDEX.md`, `docs/layout.md`, `docs/authoring.md`, `docs/procedure-endings.md`, `docs/reader-standard.md`, `docs/extend-the-workspace.md`, and the pages it links: `docs/decisions/0006-what-proven-means.md`, `docs/triage-labels.md`, `docs/playbooks/tracker-operations.md` and `docs/templates/bug-ticket.md`. Also read `docs/playbooks/bug-grooming.md`, `docs/playbooks/bug-triage-meeting.md`, the files under `src/`, the `shelved` entry in `workspace.json`, `parts/shelved.cases.json`, and the B4 record on the feature layer walk. Ran `python3 tools/symbols.py` for `AccountFreeze`, `Lift` and `OrderService` (found in `src/orders-api/AccountFreeze.cs` and `src/orders-service-v1/OrderService.cs`), and step 3 and 4's read-only commands: `git rev-parse origin/main` (`1a18d68`), `git grep -n "OrderService" origin/main -- src/orders-service-v1` (one match), `git grep -n "Lift" origin/main -- src/orders-service-v1` (none, exit 1), and `git show origin/main:src/orders-service-v1/OrderService.cs`. Each worked as the page says. `git fetch origin` was not run: it writes outside a temporary folder. Also ran `python3 ws.py rules` (the `shelved#an edit inside the shelved folder` tag is in use), `grep` for links to this page, and `python3 ws.py check`, which reports nothing on this page but the expected missing README row.

The page has no `## References` heading. Missing catalog, how-to index and README rows are out of scope for batch 2.

## Findings

| # | Class | Where | Finding | Disposition |
|---|---|---|---|---|
| 1 | contradiction | Steps, step 8 | Blocking. Step 8 says "End as procedure endings says", then "This page writes no file in this repository". The contract says a session that had to ask a person something the workspace should have answered adds it to the question log; procedure endings says such a procedure "still commits this entry". Step 2's default asks the person for a code pointer, so the case arises. The page does not label an exception. Tracker operations words it as "Apart from a question-log entry, nothing on this page commits a file". Verified: the contract's rules table, procedure endings' "The question-log entry", and the B4 feature layer walk record's finding 1 on the same sentence. Blocking because following the page skips a step the contract requires; when in doubt, blocking. | fixed: step 8 now reads "Apart from a question-log entry, this page writes no file in this repository" |
| 2 | step | Steps, step 5 | Not blocking. "Mark it verified only when you reproduced the fault against the predecessor and saw it." That can hold only for "carried over". "Introduced here" means the predecessor lacks the fault, so it can never be seen there, and the page gives no other test for it, such as running the attack against the predecessor and seeing it refused. Nor does any step say how to run the predecessor at the commit checked: step 4 reads it with `git show`, without checking it out. The **In short** line still offers every origin "marked verified or inferred". Verified: step 4, step 5 and the **In short** line. Inferred: that an agent marks every "introduced here" inferred, or invents a test. | fixed: step 5 marks verified when the fault's input was run against the predecessor and the result seen, reproduced for carried over or refused for introduced here, in a temporary copy made as bug grooming's step 3 makes one |
| 3 | step | Steps, step 1; When it applies | Not blocking. The default for a major security bug reads the labels `kind:security` and `affects:end-user` or `affects:staff`. Step 1 stops when the bug is not a major security bug. A bug with no labels yet, which the bug report template's filing steps leave it, is stopped as not major, whatever its text says. No default covers a bug with no labels, such as judging from the text or asking the person. Verified: "When it applies", step 1, and the template's "Filing it". | fixed: "When it applies" adds a default for a bug with no labels: judge from its text and say so in the report |
| 4 | trigger | When it applies | Not blocking. The page is for "the agent or developer handling a major security bug", but only the triage labels' optional label section links it. Bug grooming handles every bug and never mentions the predecessor. The triage meeting puts `kind:security` bugs in group 1 and never sends one here. An agent grooming or triaging a major security bug does not reach this page. Verified: `grep -rln predecessor-check` over `docs/`, the README and the contract, outside records and plans, found only `docs/triage-labels.md`. Catalog and index rows are out of scope for batch 2; this finding is about the lane pages that handle the bug. | fixed: bug grooming's step 4 checklist and the triage meeting's step 5 now send a major security bug here |
| 5 | contradiction | Steps, step 7; Rules, the fifth row | Not blocking. Step 7 gives the record as `Predecessor fix: yes, <initials>, <YYYY-MM-DD>.` "or `no`". The rules row says "the ticket records it with initials and date". Taken as written, a `no` decision carries neither. Verified: step 7 and the rules row. | fixed: step 7 gives the `no` record with initials and date too |

## Checked with no finding

- enforcement: "Never edit the predecessor from this procedure" is tagged `shelved#an edit inside the shelved folder`, and `parts/shelved.cases.json` holds that case, refusing an edit to `src/orders-service-v1/OrderService.cs`; `workspace.json` points the `shelved` part at `src/orders-service-v1`. The other rows are `prose`, which is true for tracker writes and judgment.
- placement: step 8 links procedure endings; steps 1, 6 and 7 link tracker operations instead of restating its yes rules; the label values are linked from the triage labels, not copied. "A fix in the predecessor" restates the contract's read-only fact in one sentence where the step needs it.
- eval-case: the page is marked `proof: unproven` with `prove-by: M9`, which is not in `building` (`["M3"]` in `workspace.json`), so its new behavior needs no eval case yet.

## Re-check

A fresh session read the page at `4190d8d`, with the uncommitted change of the B4 slice session, beside the contract, procedure endings, tracker operations, the triage labels, bug grooming's step 3 and the triage meeting's step 5. It ran step 4's read-only commands once: `git rev-parse origin/main` (`4190d8d`), `git grep -n "OrderService" origin/main -- src/orders-service-v1` (one match), `git grep -n "Lift" origin/main -- src/orders-service-v1` (none, exit 1), and `python3 tools/symbols.py AccountFreeze src` (found in `src/orders-api/AccountFreeze.cs`). It did not run `git fetch origin`, which writes in the repository.

| # | Verdict | Evidence |
|---|---|---|
| 1 | upheld | Verified: step 8 ends "Apart from a question-log entry, this page writes no file in this repository". |
| 2 | upheld | Verified: step 5 marks an origin verified when the fault's input was run against the predecessor and the result seen, reproduced for carried over or refused for introduced here, in a temporary copy made as bug grooming's step 3 makes one. Verified: that copy's commands work, as bug grooming's re-check records. The **In short** line's "marked verified or inferred" now holds for both origins. |
| 3 | upheld | Verified: "When it applies" says to judge a bug with no labels from its text, and to say so in the report. |
| 4 | upheld | Verified: bug grooming's step 4 checklist and the triage meeting's step 5 both send a major security bug to `predecessor-check.md#when-it-applies`, and `python3 ws.py check` reports no broken link. |
| 5 | upheld | Verified: step 7 gives the `no` line with initials and date, as the rules row asks. |

What a fix broke:

- Not blocking. Step 5's temporary copy inherits the cleanup gap bug grooming's re-check records for step 3: the remove refuses when the run leaves a file git does not ignore. Inferred from the shared commands.

What the first reading missed: none.
