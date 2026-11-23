---
kind: record
last-reviewed: 2026-11-23
covers: docs/playbooks/qa-verification-list.md
reviewed-at: 1a18d68, with the uncommitted change of the B4 slice session
---

# Instruction review: docs/playbooks/qa-verification-list.md

This records the instruction review of slice B4's new QA verification list playbook, a QA lane draft, for the change's author.

**In short:** 5 findings: 2 step, 1 contradiction, 1 trigger, 1 enforcement; none blocking. Step 6 has no default for a document still failing the self-check, and never says which item the QA sub-task is. Tracker operations puts the commit or build into test notes QA reads, against rule 2. The catalog row offers a check-only path the steps lack. Rule 7 has no rules row.

## Scope

In scope: the whole page, which is new and untracked, and its rows in the playbook catalog, the README's proof table and the QA reading path. Read beside it: `AGENTS.md`, `CLAUDE.md`, `INDEX.md`, `docs/layout.md`, `docs/authoring.md`, `docs/procedure-endings.md`, `docs/reader-standard.md`, `docs/extend-the-workspace.md`, and the pages it links: `docs/templates/qa-test-plan.md`, `docs/playbooks/tracker-operations.md` and `docs/decisions/0006-what-proven-means.md`. Also read `git diff` of `docs/playbooks/README.md` and `README.md`, `docs/reading-paths.md`, and `docs/templates/pull-request.md`'s tracker row. Ran `grep` for "QA sub-task" and "test notes" across `docs/`, read `building` in `workspace.json` (`['M3']`), and ran `python3 ws.py check`, which reports no finding on this page. The page gives no command to run.

The page has no `## References` heading.

## Findings

| # | Class | Where | Finding | Disposition |
|---|---|---|---|---|
| 1 | step | Steps, steps 5 and 6 | Not blocking. Step 5 stops after two rounds and reports "any rule still failing, with the item". Step 6's input is "the checked document", and it says nothing of a document that still fails a rule. No default says whether to hand it on, hold it, or post it when the request names the posting. A document that breaks rule 1 or rule 2 could then reach the tracker. Verified: steps 5 and 6. | fixed: step 6's default now posts nothing while a rule still fails after step 5; the report says the document is waiting and why. |
| 2 | step | Steps, step 6 | Not blocking. Step 6 posts on "the tracker's QA sub-task", but no step names or reads that item. Step 1 reads the tickets the request names, and its output is the changes and the known issues, not the sub-task's key. No default covers a change with no QA sub-task, or several. Step 6 also links only tracker operations' "Which writes need a yes", not its steps 5 and 6, which make the write and read the item back; that page's rules table asks for the read-back. The person's yes still gates the post, so no write is made without it. Verified: steps 1 and 6, and tracker operations' steps and rules table. | fixed: step 1 notes the QA sub-task's key and outputs it; step 6 takes it as input, posts nothing when there is none or more than one, and links tracker operations' steps 3 to 6 for the write and its read-back. |
| 3 | contradiction | The rules, rule 2 | Not blocking. Rule 2 says a document QA reads holds nothing on builds or CI, except the build's visible version. Tracker operations' operations table, row "Ready for testing", has the agent write the item's test notes with "the commit or build it is in"; the pull request template sends the author there. Test notes on an item ready for testing are read by QA (inferred). Neither page routes to the other or labels the exception, so the same reader gets a commit in one document and is shielded from it in the next. Verified: rule 2, the tracker row, and `grep -rn "test notes"` across `docs/`. | fixed: rule 2 now labels the test notes that tracker operations' "Ready for testing" row writes as a tracker field outside this rule. |
| 4 | trigger | The playbook catalog row; Steps | Not blocking. The catalog row fires when "You write or check a document QA reads". The steps only write: step 1 gathers scope from tickets, and steps 2 to 4 build the items from it. A request to check an existing document, such as a test plan someone else wrote, has no entry point; the self-check of step 5 is the nearest, and it runs only after steps 1 to 4. The purpose line names writing alone. Verified: the row, the purpose line and the steps. | fixed: the purpose line names checking; step 1's first default sends a request to check an existing document straight to step 5. |
| 5 | enforcement | The rules, rule 7; Rules | Not blocking. Rule 7 is a never: "No code names, routes, status codes or field ids." Every other numbered rule has a row in the rules table, but rule 7 has none, so the rules list and `python3 ws.py rules` miss it. Extend the workspace asks for a row for every must and never. Verified: the numbered rules beside the rules table, row by row. | fixed: added a rules row for rule 7, plain language with no code names, routes, status codes or field ids. |

## Checked with no finding

- placement: step 7 links procedure endings for the ending and the report instead of restating them; step 1 links tracker operations' steps 1 and 2 and its draft mode instead of restating how to read a ticket; the "What this page does and does not do" section sends layout to the template.
- eval-case: the page is marked `proof: unproven` with `prove-by: M6`, which is not in `building`, so its new behavior needs no eval case yet; its README row says the same.

## Re-check

A fresh session's reading after the fix round, on `1a18d68` with the uncommitted fix of the B4 slice session. It read the page in full, tracker operations' "Which writes need a yes", "Steps" and "The operations", the QA test plan template and the playbook catalog's row, and ran `python3 ws.py check`, which reports nothing on this page.

| # | Verdict | Evidence |
|---|---|---|
| 1 | upheld | Verified: step 6's default posts nothing "when a rule still fails after step 5", and the report says the document is waiting and why. |
| 2 | upheld | Verified: step 1 notes the QA sub-task's key and outputs it. Step 6 takes it as input, posts nothing with none or more than one, and links tracker operations' steps 3 to 6, which list, ask, make and read back the write. |
| 3 | upheld | Verified: rule 2 now labels the test notes of tracker operations' "Ready for testing" row as a tracker field outside the rule. |
| 4 | upheld | Verified: the purpose line names writing or checking, and step 1's first default sends a request to check an existing document to step 5. |
| 5 | upheld | Verified: the rules row "Plain language: never a code name, route, status code or field id." |

What a fix broke:

- None on this page. Finding 4's fix and the playbook catalog's finding 3 fix went opposite ways; recorded on the catalog's record.

What the first reading missed:

- Not blocking. On the check path, step 1 sends the agent to step 5 without reading the tickets, so no QA sub-task key is noted. Step 6 then posts nothing, even when the request names the posting. No write goes wrong, but such a request cannot be met. Verified: steps 1 and 6. Inferred: that a check request will sometimes name the posting.

## Known defects

What stays open after the one fix round the plan allows, each not blocking.

- Not blocking, what the first reading missed: on the check path no QA sub-task key is noted, so step 6 cannot post even when the request names the posting. Known defect, for M6.
