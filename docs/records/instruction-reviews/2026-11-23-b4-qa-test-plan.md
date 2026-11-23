---
kind: record
last-reviewed: 2026-11-23
covers: docs/templates/qa-test-plan.md
reviewed-at: 1a18d68, with the uncommitted change of the B4 slice session
---

# Instruction review: docs/templates/qa-test-plan.md

This records the instruction review of slice B4's new QA test plan template, a QA lane draft, for the change's author.

**In short:** 3 findings: 2 contradiction, 1 placement; none blocking. The Sign-off section files each finding as "its own ticket", where tracker operations raises a change-request sub-task. The skeleton's "Build tested" line is a second build mention, where the QA verification list allows exactly one. The "none when empty" rule is stated on this page and on the verification list.

## Scope

In scope: the whole page, which is new and untracked, and its rows in the templates index and the QA reading path. Read beside it: `AGENTS.md`, `CLAUDE.md`, `INDEX.md`, `docs/layout.md`, `docs/authoring.md`, `docs/procedure-endings.md`, `docs/reader-standard.md`, `docs/extend-the-workspace.md`, and the pages it links: `docs/playbooks/qa-verification-list.md` and `docs/playbooks/tracker-operations.md`. Also read `git diff -- docs/templates/README.md`, `docs/reading-paths.md`, `docs/templates/pull-request.md`'s tracker row and `src/orders-api/AccountFreeze.cs`. Ran `python3 tools/symbols.py AccountFreeze src` (it prints `src/orders-api/AccountFreeze.cs`, so the worked example's path holds), `grep` for "QA sub-task" and "test notes" across `docs/`, and `python3 ws.py check`, which reports no finding on this page.

The page has no `## References` heading.

## Findings

| # | Class | Where | Finding | Disposition |
|---|---|---|---|---|
| 1 | contradiction | Filling it in, the Sign-off bullet; Skeleton, Sign-off | Not blocking. The page says "A finding goes on the tracker as its own ticket", and the skeleton's Findings line asks for "one ticket per finding", linking tracker operations' operations table for how. That table's row "A finding from testing" says: "Raise one change-request sub-task per finding." A separate ticket and a sub-task of the item under test are different writes, and the page names one while linking the other. The QA reading path adds a third reading: the bug report template is "the shape of every ticket QA files". Verified: the three texts. | fixed: the Sign-off bullet and the skeleton's Findings line now say one change-request sub-task per finding, as tracker operations' "A finding from testing" row says. The QA reading path's "every ticket QA files" line is not this page's; reported to the slice session. |
| 2 | contradiction | Skeleton, Sign-off; Rules, second row | Not blocking. The page says what goes under each heading follows the QA verification list. That page's rule 2 says the document holds nothing on builds, with "The one exception": "Before you start" names the build by its version. The skeleton's Sign-off adds a second build line, "Build tested: <version>", and the page does not label it as a further exception. A writer who runs the verification list's self-check on a copy of this skeleton finds rule 2 broken by the template itself. Verified: the skeleton and rule 2. | fixed: removed "Build tested" from the skeleton and the worked example; the Sign-off bullet says the build is the one "Before you start" names, so rule 2's one exception holds. |
| 3 | placement | Skeleton, the paragraph above the block; Rules, first row | Not blocking. "'Do not file' and 'Not in this release' say 'none' when empty" is stated here, in prose and as a rules row, and again as rule 10 of the QA verification list, with its own rules row and step 4. The style guide's "One rule, one page" asks for one statement and a link. Two copies can drift apart, and then a writer cannot tell which holds. Verified: both pages' text and rules tables. | fixed: the skeleton's paragraph links rule 10 of the QA verification list instead of restating it; the first rules row keeps only the headings' order, and the second says an empty heading follows the verification list. |

## Checked with no finding

- step: the page has no steps; the skeleton's five headings match the **In short** line's list and order, every link resolves (`python3 ws.py check` reports none on this page), and the worked example's `AccountFreeze` path and its description, orders accepted and not shipped while held, match the code.
- trigger: the purpose line, the **In short** line, the templates index row ("You hand QA a release or a change to test") and the QA reading path's row agree on the template's use and its reader, the tester.
- enforcement: each must on the page, the headings and their order, the "none" rule, and the copy to the tracker, has a rules row tagged `prose`; no tag names a part.
- eval-case: a lane template carries no proof keys, and this one carries none; its first use is named as M6 on the page and in the templates index.

## Re-check

A fresh session's reading after the fix round, on `1a18d68` with the uncommitted fix of the B4 slice session. It read the page in full, the QA verification list, tracker operations' "The operations" and the QA reading path, and ran `python3 ws.py check`, which reports nothing on this page.

| # | Verdict | Evidence |
|---|---|---|
| 1 | upheld | Verified: the Sign-off bullet and the skeleton's Findings line say one change-request sub-task per finding, as tracker operations' "A finding from testing" row says ("Raise one change-request sub-task per finding"); the link resolves. The QA reading path's first line now sends a bug QA files outside a QA sub-task to the bug report template, so the third reading is settled too. |
| 2 | upheld | Verified: the skeleton and the worked example hold one build line, under "Before you start", and the Sign-off bullet ties the build to it. The verification list's rule 2 has one exception, and it holds. |
| 3 | upheld | Verified: the skeleton's paragraph links rule 10 of the verification list instead of restating it, and the rules table no longer restates the "none" rule. |

What a fix broke:

- None.

What the first reading missed:

- None.
