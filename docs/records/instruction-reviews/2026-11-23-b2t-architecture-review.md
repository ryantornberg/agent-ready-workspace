---
kind: record
last-reviewed: 2026-11-23
covers: docs/playbooks/architecture-review.md
reviewed-at: 18eccc5, with the uncommitted change of the B2t builder
---

# Instruction review: docs/playbooks/architecture-review.md

This records the instruction review of B2t's change to architecture review, for its author and for any agent recording a review.

**In short:** 3 findings, 1 of them blocking: 2 contradiction, 1 placement. The blocking one: step 9 now sends the agent to procedure endings and keeps a question-log row uncommitted so that no push carries the reviewed branch to main, but commits the plan on that same branch, which procedure endings' push for pages then carries to main from a worktree.

## Scope

In scope: the changed text, which is the red team review link in "When it runs", step 1's new path output and default, step 7's and step 9's new sentences, the template's `The path:` line, the big-picture pass's two paragraphs on the path and the symptom rule, and the two rules rows; and anything on the page, or a page it links to, that the change contradicts or leaves stale.

Read: the page whole; `git diff fad9f23` of it; `AGENTS.md`, `CLAUDE.md`, `INDEX.md`; `docs/procedure-endings.md`; `docs/definition-of-done.md`; `docs/orchestration.md`'s "Fresh context for critics" and "Limits"; `docs/playbooks/fix-a-bug.md`; the `outward_write` row of `docs/parts.md`; the review orchestrator, escape analysis, red team review, the instruction review, the question log's "Adding an entry", the defect register template's "When to add a row", `docs/review-in-a-worktree.md`, `docs/reader-standard.md`'s names rules, `workspace.json`'s `direct_push` entry, and the M3 plan's "Changes after approval" of 2026-11-22 and 2026-11-23 with B3's and B2's results. Ran `python3 ws.py check` in the worktree: it passes, with only the known warning on fix a bug's eval record, so every link and anchor the change adds resolves and the rules table's tags are valid. In a scratch repository with a local bare remote, ran `git push origin HEAD:main` from a worktree on a task branch holding a code commit and a plan commit.

## Findings

| # | Class | Where | Finding | Disposition |
|---|---|---|---|---|
| 1 | contradiction | Steps, step 9 | Blocking. Step 9 commits the plan's "Results" with no branch named, so on your own branch it lands on the reviewed branch. The change now links procedure endings twice in the same step, for the report and for the question-log entry. Procedure endings' order then commits "every file the procedure wrote" and pushes "the commits of step 3"; for pages only, in a worktree, its table gives `git push origin HEAD:main`. HEAD there is the reviewed branch, so the push carries its unmerged code to main, against procedure endings' "never on its main" for code and the contract's draft pull request rule. The change's own exception names exactly this hazard, "so no push of it carries the branch's code to main", but applies it to the question-log row only, not to the plan commit two sentences earlier. In this sample `src/` is checked in, and `direct_push` refuses only machinery paths, so nothing stops it for code under `src/`. Verified: the texts; `workspace.json`'s `direct_push` list; in the scratch repository, the push exited 0 and moved the remote's main to include the code commit. Inferred: that an agent sent to procedure endings from step 9 runs its order through the push. Q41 left where a review commits on a branch for M4, so the fix may be to say the review pushes nothing, or to extend the exception to the plan commit; that choice is the plan owner's. | fixed: step 9 pushes only from `main`; on any other branch it pushes nothing, and the plan commit and the log row reach main with the branch's pull request. A rules row holds it. |
| 2 | contradiction | The big-picture pass, the symptom paragraph; Rules, the new symptom row | Not blocking. The paragraph makes a symptom fix a finding when the cause stays reachable "on a path the request covers", then justifies it on the `fix` path by "the reported path"; the new rules row keeps only "the reported path". On the `fix` path, a cause still reachable on another path the request covers is a finding by the paragraph and not by the row. The row also uses "path" in two senses in one sentence, "reachable on the reported path is a finding on every path", one a code path and one the route the change came by. Verified: the texts. | fixed: the body and the rules row both say "a path the request covers", and the row no longer uses "path" twice. |
| 3 | placement | Steps, step 9 | Not blocking. The question-log exception to procedure endings is written here and again in the review orchestrator's paragraph after step 11, in two wordings: "while the reviewed branch is checked out" here, "when the copy you work in has the reviewed branch checked out" there. It is a rule about procedure endings' question-log entry, which other procedures that end on an unmerged branch also meet, such as escape analysis after a fix on its branch, so it belongs once on procedure endings and linked. Step 9 also still restates procedure endings' commit rule, "stage the plan by name and commit it", though the step is edited now and links the page. Verified: the texts of both pages and procedure endings' "The question-log entry" and "The commit". | declined: the one place for it is procedure endings, which this slice's row does not edit and which has had its two fix rounds; where a review commits on a branch is M4's, as the plan's entry for Q41 says. |

## Checked with no finding

- step: step 1's new output and default name an input step 1 already holds, the request; the template's `<path>` placeholder is defined in its lead-in sentence and filled from step 1; step 7's `fix`-path sentence gives the disposition a default. Verified.
- trigger: the purpose line, **In short** line and the catalog row in `docs/playbooks/README.md` still describe what the page does; "When it runs" now sends a plan or requirements document to red team review, which exists at `docs/playbooks/red-team-review.md`. Verified.
- enforcement: both new rules rows say `prose`, and no must or never in the changed text claims a part or case. `python3 ws.py check` passes the `rules` check. Verified.
- eval-case: the page is `proof: unproven` with `prove-by: M6`, so the new behavior on the `fix` path needs no eval case yet. Verified: the front matter.

## Re-check

A fresh session re-read the page on 2026-11-23 after B2t's fix round, with `git diff fad9f23`, procedure endings, changing the machinery, the contract, the M3 plan's Q41 entry, and the other five pages of this batch that share the off-`main` rule: the review orchestrator, defect escape analysis, git-host operations, tracker operations and federated search. `python3 ws.py check` passes, with only the known warning on fix a bug's eval record.

| # | Verdict | Evidence |
|---|---|---|
| 1 | holds | Step 9 now pushes as procedure endings says only when `main` is checked out, and on any other branch pushes nothing, labelled "By exception to that page". The exception now covers the plan commit as well as the log row, which was the gap. The new rules row, "Off `main`, the review pushes nothing", says the same. With nothing pushed, procedure endings' `git push origin HEAD:main` for pages in a worktree is never reached from the reviewed branch. Verified: the text. The rule matches the review orchestrator's paragraph after step 11 word for word, and escape analysis's step 9 in substance. Verified: the three pages. |
| 2 | holds | The big-picture paragraph and the new rules row both say "a path the request covers", and the row says "whichever way the change came" for the route, so it no longer uses "path" twice. Verified: the text. The body sentence still uses "path" in both senses; see "Missed". |
| 3 | accepted | The decline holds for the exception's placement: the one place for a rule on any procedure that ends on an unmerged branch is procedure endings, which B2t's row does not edit, and Q41 leaves where a review commits on a branch for M4. Verified: the M3 plan's entry "B3 reverts the commit steps, then merges (Q41)". The second half, step 9's restated "stage the plan by name and commit it", is main's text, unchanged by this slice. Verified: the diff. The two wordings the finding named are now one wording on both pages, so the drift it warned of is gone for now. Verified. |

Broke:

- Not blocking. Step 9 says the plan commit and the log row "reach main with its pull request". That holds only when the checked-out branch has an open pull request. Two cases break it: a session working in its own pages-only worktree branch, which procedure endings pushes with `git push origin HEAD:main` and which has no pull request; and a branch whose pull request has already merged. There the commits stay on the branch and never reach main. Step 9's report names each commit left unpushed, so nothing is lost silently. Verified: the texts of step 9 and procedure endings' "The push". Inferred: that a review runs in such a branch.

Missed:

- Not blocking. The big-picture pass's symptom sentence still uses "path" in two senses in one sentence: "with the cause still reachable on a path the request covers, is a finding, on the `fix` path too". Finding 2 named this in the rules row only, and the fix changed the row. Verified: the text.

## Second fix round

The builder's second fix round, on 2026-11-23, under the maintainer's answer to Q42 in the workspace queue, recorded in the M3 plan. Procedure endings gained one rule, under "Off main": a procedure pushes nothing for pages when the branch checked out holds work other than its own pages, and the commits reach main with the branch's pull request. Its own review is in `2026-11-23-b2t-procedure-endings.md`. The non-blocking items of the re-check are not fixed in this round; each goes to "Known defects".

| Item | Disposition |
|---|---|
| Second fix round: step 9 and the rules row labelled the off-main rule an exception to procedure endings | changed: that page now holds the rule, so step 9 and the row link it instead of labelling an exception. Step 9 names the case: on a branch of the work it reviews. |
| Re-check, broke, not blocking: on a pages-only worktree branch or a merged branch, the commits never reach main | fixed in part: a pages-only worktree is not off main under procedure endings' rule, so it pushes as that page's table says. A merged branch is a known defect, for M6. |
| Re-check, missed, not blocking: the big-picture sentence uses "path" in two senses | known defect, for M6. |

## Second re-check

A fresh driver-tier session re-checked the second fix round on 2026-11-23, narrowly. It read the contract, the instruction review's "The record", the M3 plan's Q42 entry and lane B's stop rule, `git diff HEAD` of the six pages, procedure endings and the six records, and procedure endings' "The order", "The commit", "The question-log entry", "The push" and its new "Off main". `python3 ws.py check` exits 0, with only the known warning on fix a bug's eval record. In a scratch repository with a local bare remote, `git log --format='%h %s' origin/main..HEAD` listed the code commit on a fix branch holding a code commit and then a page commit, so the test finds it off main. On a pages-only worktree it listed only the page commit, and `git push origin HEAD:main` from there put no code on the remote's main. On a fix branch with no code commit yet, it listed only the page commit. The record the round names for procedure endings, `2026-11-23-b2t-procedure-endings.md`, is not yet in the worktree (verified, `ls`); that rule is a separate reviewer's.

| Item | Verdict | Evidence |
|---|---|---|
| Second fix round: step 9 and the rules row labelled the off-main rule an exception to procedure endings | upheld | Step 9 now pushes "as procedure endings says" and, on a branch of the work it reviews, calls the review off main and pushes nothing, linking `#off-main`; the rules row says "as procedure endings says". No "By exception" is left. A branch of reviewed work holds work other than the review's own pages, so the page's case falls inside the rule's. The plan commit and the log row are named, and neither is pushed from that branch. Verified: the texts; the anchor resolves and `ws.py check` passes. |
| Re-check, broke, not blocking: on a pages-only worktree branch or a merged branch, the commits never reach main | upheld | Procedure endings' last "Off main" paragraph says a worktree made for pages alone is not off main and pushes as the table says. In the scratch test such a worktree's test listed only its page commit, and its push put no code on main. The merged branch is in "Known defects" for M6, the page's `prove-by`. Verified. |
| Re-check, missed, not blocking: the big-picture sentence uses "path" in two senses | upheld | Listed in "Known defects" for M6. Verified. |

Broke:

- none.

Missed:

- Not blocking. "Push nothing" and "reach main with its pull request" hold together only when the branch is pushed again after this commit, by the procedure that owns it. A review that is the last step before merge leaves its plan commit on the local branch, outside the pull request. The report names each commit left unpushed, so nothing is lost silently. Inferred: from step 9 and procedure endings' "Off main", which says the same; the rule's own wording is the separate reviewer's.

## Known defects

The plan allows the page no further fix round, so the re-check's non-blocking items stay here.

- Re-check, broke: on a branch whose pull request has merged, step 9's commits stay on the branch; the report names each. For M6.
- Re-check, missed: the big-picture pass's symptom sentence uses "path" in two senses in one sentence. For M6.
- Second re-check, missed: a plan commit left on the branch reaches the pull request only if the branch is pushed again. Procedure endings' fix round now has the report say so. For M6.
