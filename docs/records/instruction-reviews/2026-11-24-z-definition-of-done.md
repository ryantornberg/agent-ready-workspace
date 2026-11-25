---
kind: record
last-reviewed: 2026-11-24
covers: docs/definition-of-done.md
reviewed-at: d2aa593, with the uncommitted change of the slice Z builder
---

# Instruction review: docs/definition-of-done.md

This records the instruction review of slice Z's change to the definition of done, for its author and its readers.

**In short:** 7 findings, none blocking: 1 contradiction, 2 step, 2 enforcement, 1 placement, 1 eval-case.

## Scope

In scope: the whole page, with most attention to the diff from d2aa593: the qualified first two rows, the new rows on the claim check, where the report is kept, the defect register and the review record, the paragraph on "where", the report's new sentence, and three new items under "What does not count". Read beside it: `AGENTS.md` and `CLAUDE.md` with their uncommitted change, `INDEX.md`, `docs/templates/fix-record.md`, `docs/records/defects.md`, `docs/templates/defect-register.md`, `docs/playbooks/instruction-review.md`, `docs/procedure-endings.md`, `docs/size-the-work.md`, `docs/safe-refactor.md`, `docs/extend-the-workspace.md`, `docs/request-map.md` (new, untracked), `parts/claim_marks.py` and its cases, `evals/arms.json`, the three eval cases and `evals/run.py`'s `prepare`. Every link on the page resolves. Ran `python3 ws.py rules` and `python3 ws.py check`; the check's only errors are the three `eval_record` errors on fix a bug, not on this page.

## Findings

| # | Class | Where | Finding | Disposition |
|---|---|---|---|---|
| 1 | step | The list, "The report is kept where its record says"; In short | Not blocking. The row names a place only for a fix (its fix record's `## Report`) and for a slice of a plan (the plan's "Results"). The page is the done bar for all work: safe refactor's step 7 sends a refactor here ("Report as that page says"), and test first (step 7) ends here too; extend the workspace ends with procedure endings' report, which takes this page's shape. A refactor or a page change has no record type, and the row gives no default, so an agent finishing one cannot tell where "the same text" of the report's new sentence goes, or whether the row applies. The "where" paragraph does not cover it, since this row does not say "where" for a thing the work may lack. Verified: the row's text; safe refactor step 7; test first step 7; procedure endings, "The report". | fixed: the row now gives other work, such as a refactor or a page change, the final reply as the report's place |
| 2 | enforcement | The list, "The report is kept where its record says" | Not blocking. The tag `claim_marks#a fix record with no report section fails` shows only that a fix record which exists has a `## Report` section. Nothing fails a fix that opened no fix record, and nothing checks a plan slice's report under "Results". The row's rule is wider than its case. Verified: `parts/claim_marks.py` says "A folder with no fix records passes", and it reads only `docs/records/fixes/`. | fixed: the row now says the check reads only fix records, and is also tagged `prose` |
| 3 | step | What does not count, the staging item | Not blocking. "The commit check reads the staged files, so stage first, then check" names no command. The command other pages give, plain `python3 ws.py check`, reads the working folder whatever is staged; only `python3 ws.py check --staged` reads the staged files. So an agent that stages first, then runs the command it knows, gets the same run as before, and the item's warning does not reach it. Extend the workspace's step 6 also runs the plain check before anything is staged. "A required check" in the last item is not defined either: the manifest's checks, CI's jobs, or the repository's suite. Verified: `ws.py`'s usage text ("run the checks on the working folder" against "run them on exactly what is staged"). | fixed: the item now names `python3 ws.py check` and `python3 ws.py check --staged`, and defines a required check |
| 4 | enforcement | What does not count | Not blocking. "Stage first, then check" is a must with no row in the page's rules table ("The list"), tagged or `prose`. The defect-register duty in the last item is covered by the row on findings outside the change. Verified. | fixed: the item no longer states a duty; it says which run counts as proof of what was committed |
| 5 | placement | The list, "A changed guidance page names its review record" | Not blocking. The row restates the commit rule that procedure endings owns ("Name the review", in "The commit") and links the instruction review, not procedure endings. Procedure endings' own rule is that a page links it instead of restating its rules, and the instruction review counts a restated rule as a placement finding. Verified: `docs/procedure-endings.md`, "The commit" and its rules table. | fixed: the row now links procedure endings' commit section |
| 6 | contradiction | The list, the running-app row | Not blocking. The row requires a check in the running app "on a local environment that no other session shares", with no milestone caveat. The new request map, which the contract now links, cites this row for its default "A local environment, never shared data" and adds "Verifying on a local environment waits for M5." A reader of both cannot tell whether the row binds now. Verified: `docs/request-map.md`, the defaults table. | fixed: the request map no longer says local verification waits for M5, so both pages say the row binds where there is a running app |
| 7 | eval-case | The list, the three new rows; What does not count | Not blocking. The page is in the eval's guided arm and carries no proof mark, as a reference page. It now asks for new behavior: keep the report in a fix record's `## Report`, write a finding outside the change, or an errored check, as a defect-register row, and stage before checking. No grader of `fix-a-bug`, `nightly-job` or `big-report` reads a fix record, the defect register or the order of staging and checking. The guided arm's run folder also holds neither `docs/templates/fix-record.md` nor `docs/records/defects.md`, so in the eval those links lead nowhere. Verified: the graders' ids in the three cases; `evals/arms.json`; `prepare` in `evals/run.py` copies the scaffold and the arm's five files only. | declined: a reference page carries no proof field, and R2 records the guided arm with this text; the eval's arm holds the five files it always has |

## Checked with no finding

- trigger: the purpose sentence and the In short line still say when the page applies, and the contract's "How work flows", INDEX.md's topic row and the how-to index all route "done" here. The In short line's new clause matches the new row, whose gap is finding 1.

## Re-check

A fresh session at the driver tier read the definition of done on 2026-11-24 as it stands on fca7d9b with the slice Z builder's uncommitted change, with `git diff d2aa593 -- docs/definition-of-done.md`, and the pages it touches: the fix record template, procedure endings, fix a bug, extend the workspace, safe refactor and the request map.

| # | Verdict | Evidence |
|---|---|---|
| 1 | The fix holds. | Verified: the row now gives a fix its fix record's `## Report`, a slice of a plan the plan's "Results", and other work, such as a refactor or a page change, the final reply alone. Safe refactor's step 7 ("Report as that page says") and extend the workspace's step 8 now each have a place. |
| 2 | The fix holds. | Verified: the row says "The check reads only fix records." and carries `prose` beside the `claim_marks` tag. `parts/claim_marks.py` reads only `docs/records/fixes/`. |
| 3 | The fix holds. | Verified: the item names `python3 ws.py check` and `python3 ws.py check --staged`, and `python3 ws.py check --help` lists `--staged`. "A required check" is now defined as one the commit, CI or the repository's suite runs. |
| 4 | The fix holds. | Verified: the item now says which run does not count as proof of what was committed, and states no duty. The last item's duty, to write an errored check in the defect register, is held by the row on findings outside the change, tagged `prose`. |
| 5 | The fix holds. | Verified: the row links procedure endings' commit section, whose anchor resolves, and keeps one clause with the `review_trailer` tag, which is the linked form. |
| 6 | The fix holds. | Verified: the request map's local-environment default no longer mentions M5 and cites this page's running-app row. |
| 7 | The decline is upheld. | Verified: decision 0006 gives a reference page no proof mark, and `evals/arms.json` still gives the guided arm the same five files. Not blocking, what is left: in the guided arm, this page and fix a bug now link the fix record template and the defect register, which the arm's run folder does not hold. Whether that costs runs is for R2 to show (inferred). |

What the fixes broke: nothing found. Verified: every link and anchor on the page resolves (a link script), and `python3 ws.py check` reports nothing on it.

What the first reading missed: nothing found on this page. The question of where a brief goes for a fix run as a plan's slice touches this page's report row; it is recorded in fix a bug's re-check, 2026-11-24-z-fix-a-bug.md.
