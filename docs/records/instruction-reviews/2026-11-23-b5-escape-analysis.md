---
kind: record
last-reviewed: 2026-11-23
covers: docs/playbooks/escape-analysis.md
reviewed-at: dace91e, with the uncommitted change of the B5 slice session
---

# Instruction review: docs/playbooks/escape-analysis.md

This records the review of B5's added sentence in step 8 of defect escape analysis, for its author and its readers.

**In short:** 3 findings, none blocking: 1 step, 1 enforcement, 1 placement. "Each miss gets a case" widens step 8 to misses the case's shape does not fit, and its reason cites a guidance defect, a kind this page sends away.

## Scope

In scope: the sentence added to step 8 under "Steps", "A guidance defect once fixed with nothing to catch it coming back did come back, so each miss gets a case that replays it." The whole page was read, with `git diff HEAD`. Read beside it: `AGENTS.md`, `INDEX.md`, `docs/layout.md`, `docs/authoring.md`, `docs/procedure-endings.md` ("The report", "Off main"), `docs/playbooks/instruction-review.md`, `docs/records/lessons.md`, `docs/templates/lessons-log.md`, and the pages step 8 links.

Runs (verified): `python3 ws.py check` exits 0 in the worktree, with only the `eval_record` warning about a missing base commit. `git grep -n -i "replay" -- docs` finds no other page that asks for a replay case.

## Findings

| # | Class | Where | Finding | Disposition |
|---|---|---|---|---|
| 1 | step | "Steps", steps 4, 8 and 9 | Not blocking. Step 4 makes two kinds of miss: "Each covering review that did not raise the defect" and "Each sighting that did not lead to a fix" (verified). Step 8 now gives each miss a case, but describes a case as "the code at the defect commit, the review's request, and what the review must find". A sighting miss, such as a question-log row or a commit message, has no review request, so that input is undefined for it (inferred). Step 8's output still names "the case description", in the singular (verified). Step 9's list of what the report holds omits the case descriptions, though step 8 says to put them "in the report" (verified). | fixed in part: the added sentence is removed, so no step gives each miss a case. The gaps in steps 8 and 9 the finding also names predate this change: a known defect, for M6 |
| 2 | enforcement | "Steps", step 8, and "Rules" | Not blocking. "Each miss gets a case" is a must, and the rules table has no row for it, while most other step rules have one, tagged `prose` (verified, reading "Rules"). | fixed: the sentence that made the rule is removed |
| 3 | placement | "Steps", step 8, the added reason, against "When it runs" | Not blocking. The reason cites a guidance defect. The page's own table sends a defect "in a guidance page or a plan, not in code" away: "Not this page. Its scope is code under `src/` and the machinery paths" (verified). A reader may take the reason as bringing guidance defects into scope, or find a code rule resting on evidence from outside its scope (inferred). The reason belongs on a page that handles guidance defects, or should cite a code defect (inferred). | fixed: the reason moved to the eval rule it belongs with, "turn the failure into a case" in `evals/README.md`'s "Rules that make this worth doing" |

## Checked with no finding

- contradiction: "each miss gets a case" and "An eval case ... waits for the eval system for procedures, planned for M4. Until then, describe the case in the report" can both hold: the case is described now and built in M4 (verified, reading step 8).
- trigger: the purpose and **In short** lines are unchanged and do not mention replay cases, which were in step 8 before this change (verified, `git diff HEAD`).
- eval-case: the page is `proof: unproven` with `prove-by: M6` (verified, reading its front matter). The incident the reason cites has no record in this workspace to check it against (inferred; `git grep -n -i "came back\|replay" -- docs/records/lessons.md docs/records/defects.md` finds nothing).

## Known defects

- Steps 8 and 9: a sighting miss has no review request for its case description, step 8's output names one case description, and step 9's report leaves the case descriptions out. These predate slice B5. For M6, the page's `prove-by` milestone.

## Re-check

A fresh driver-tier session read steps 4, 7, 8 and 9 and "Rules" as they stand, confirmed the page matches `HEAD` (`git status --short` and `git diff HEAD` print nothing for it), read `evals/README.md` with its diff, and ran `python3 ws.py check` (exit 0, only the `eval_record` warning).

| # | Verdict | Evidence |
|---|---|---|
| 1 | upheld | The sentence "each miss gets a case" is gone; step 8 again describes "the case" for the review that missed (verified, the page matches `HEAD`). The older gaps in steps 8 and 9 are in "Known defects", for M6, and the finding was not blocking (verified). |
| 2 | upheld | With the sentence removed, the page holds no must without a rules row that this change added (verified). |
| 3 | upheld | The reason now sits in `evals/README.md`'s "Rules that make this worth doing", under "turn the failure into a case", as a present-tense claim that cites no incident (verified, `git diff HEAD -- evals/README.md`). |

What a fix broke:

- None on this page. The moved reason's fit on its new page is judged in its own record, `2026-11-23-b5-evals-readme.md`.

What the first reading missed:

- None.
