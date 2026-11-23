---
kind: record
last-reviewed: 2026-11-23
covers: docs/adopt-the-workspace.md
reviewed-at: 18eccc5, with the uncommitted change of the B2t builder
---

# Instruction review: docs/adopt-the-workspace.md

This records the review of B2t's edit to adopt the workspace, for its author and its readers.

**In short:** 2 findings: 1 placement, 1 contradiction, neither blocking. The new milestone command runs and lists the milestones in number order. The switch to procedure endings stops at the report: step 6 still sends staging to commits, which no longer holds it, and step 8 skips the question-log entry and the push that procedure endings runs before the report.

## Scope

In scope: the changed text, as `git diff fad9f23 -- docs/adopt-the-workspace.md` shows it: the milestone-state row of "What does not transfer", step 8 of "Steps", and the review date. Also in scope: anything on the page, or on a page the change links, that the change contradicts or leaves stale. The whole page was read. Also read: `AGENTS.md`, `CLAUDE.md`, `INDEX.md`, `README.md` ("Try it", "Use it for your own team"), `docs/procedure-endings.md`, `docs/definition-of-done.md`, `docs/maintain-the-workspace.md`, `docs/changing-the-machinery.md`, `docs/layout.md`, `docs/commits.md`, `docs/extend-the-workspace.md`, `parts/proof.py`, `evals/arms.json` and `workspace.json`.

Commands run in the worktree: the row's `git grep -h -o -E 'prove-by:? M[0-9]+|^milestone: M[0-9]+' -- docs | grep -o -E 'M[0-9]+' | sort -u -k1.2n` printed M3, M4, M5, M6, M8, M9, M10, one per line, the highest last (verified). The `^milestone:` branch matched `milestone: M3` and `milestone: M4` in two plans, and the `prove-by M<n>` branch matched section proof lines for M4, M6 and M9 (verified). `printf 'M10\nM3\nM4\nM3\n' | sort -u -k1.2n` printed M3, M4, M10 with macOS's sort (verified); GNU sort, which Git for Windows ships, takes the same key form (inferred: no GNU sort on this machine). `python3 ws.py check` exited 0 with one warning, on `eval_record`'s missing base commit (verified).

## Findings

| # | Class | Where | Finding | Disposition |
|---|---|---|---|---|
| 1 | placement | "Steps", step 6 "Commit" | Not blocking. The change moves step 8 to [procedure endings](../../procedure-endings.md), but step 6 still restates the staging rule and credits it to commits: "files staged by name, as commits says", linking `commits.md`. `docs/commits.md` does not hold that rule: its only staging text is `python3 ws.py check --staged` in "Credentials" (verified, `grep -i stag docs/commits.md`). The how-to index's "Commit" row says staging is in procedure endings' "The commit" (verified, reading). The instruction review counts a procedure-endings rule restated instead of linked as a placement finding, to be switched when the page is next edited, and this edit is that occasion (verified, reading the playbook's "The six checks"). Step 6 should commit "as procedure endings says", linking `procedure-endings.md#the-commit`, as extend the workspace's step 7 now does. | fixed: step 6 links procedure endings' "The commit" for staging. |
| 2 | contradiction | "Steps", step 8 "Report", against procedure endings "The order" | Not blocking. The new link sends step 8 to procedure endings' "The report" section only. Procedure endings says to run its five steps in order after the procedure's last step, and to "skip a step only where it says so" (verified, reading). The question-log entry and the push both come before the report. Adopt has no step for either, and step 8 does not say it skips them, so this is an exception that is not labelled as one (verified, reading the page). An agent in an instance would not log a question it had to ask, unless the always-loaded contract's rule caught it. It would also not say that its commits from step 6 are unpushed, which procedure endings' push table requires in a team's workspace, where a person pushes (inferred). Nothing is written where it may not be, so this is not blocking (inferred). Extend the workspace's new step 8 shows the fix: "End as procedure endings says". | fixed: step 8 ends as procedure endings says, the question-log entry and the push included. |

## Checked with no finding

- step: the row's new command exists and runs as written, and its output matches the row's claim, "in number order, the highest last" (verified, the run above). The row's added "a section's proof line" is right: `parts/proof.py` checks each marked section's `prove-by` against `docs/milestones/m<n>.md` as it does a page's (verified, reading `proof`'s loop over `marks`). Step 8's link target, `procedure-endings.md#the-report`, exists, and the `links` check passes (verified, the run above).
- trigger: the purpose and **In short** lines are unchanged. The how-to index's row for this page is unchanged and still fires for setting the workspace up for a team (verified, reading).
- enforcement: the change adds no must or never. The rules table's row "Mark every claim in the report verified or inferred" still matches step 8, and its tag `eval:fix-a-bug` is the one the contract uses for the same rule (verified, reading).
- eval-case: the page is `proof: unproven` with `prove-by: M5`, so new behavior needs no eval case yet (verified, reading the front matter). The page is not in an eval arm: `evals/arms.json` gives the guided arm `AGENTS.md`, `CLAUDE.md`, `INDEX.md`, fix a bug and the definition of done (verified, reading).

## Re-check

A fresh session re-read the page on 2026-11-23 after B2t's fix round. It read the page whole, `git diff fad9f23` of it, the contract, procedure endings, changing the machinery's path and "Traps", maintain the workspace, fix a bug and extend the workspace's steps 6 to 8 and Rules. It ran the milestone row's command, which printed M3, M4, M5, M6, M8, M9, M10 in that order, and `python3 ws.py check`, which exits 0 with only the known warning on fix a bug's eval record.

| # | Verdict | Evidence |
|---|---|---|
| 1 | upheld | Step 6 now credits staging by name to procedure endings' "The commit", which holds it. Verified: the link and that section. |
| 2 | fixed in part | Step 8 now ends "as procedure endings says: the question-log entry, the push, and the report", and labels its push exception for an eval-trap branch. But its list skips the commit of the log row, which procedure endings runs between the entry and the push. Step 6 has committed by then, so an agent working from the list pushes without the row. Extend the workspace's step 8 had the same gap as its finding 4 and now reads "the question-log entry and its commit". Verified: both pages. Not blocking. |

Broke:

- Not blocking. Step 8's new exception says an eval-trap branch is pushed "never to main". The Rules table has no row for it. Extend the workspace's fix for the same sentence, its finding 6, added a row tagged `prose`. Verified: both Rules tables.

Missed: none.
