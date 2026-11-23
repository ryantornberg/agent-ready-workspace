---
kind: record
last-reviewed: 2026-11-23
covers: docs/playbooks/standup-report.md
reviewed-at: 1a18d68, with the uncommitted change of the B4 slice session
---

# Instruction review: docs/playbooks/standup-report.md

This records the instruction review of slice B4's new standup report playbook, a product lane draft, for the change's author.

**In short:** 9 findings, 2 blocking: 2 contradiction, 5 step, 1 enforcement, 1 placement. The page says it writes only the standup log, which rules out the question-log entry the contract requires. Its reply carries claims with no verified or inferred mark. Its `git log --since=<date>` drops the start day's commits before the current time of day, and the evidence it gathers cannot fill Done or "no movement".

## Scope

In scope: the whole page, which is new and untracked. Read beside it: `AGENTS.md`, `INDEX.md`, `docs/layout.md`, `docs/authoring.md`, `docs/procedure-endings.md`, `docs/reader-standard.md`, `docs/extend-the-workspace.md`, and the pages it links to: `docs/playbooks/tracker-operations.md`, `docs/playbooks/git-host-operations.md`, `docs/templates/standup-log.md` and `docs/decisions/0006-what-proven-means.md`. Also read `src/README.md`, `workspace.json`'s `building` list, and the M3 plan's B4 row.

Ran, read-only: `gh auth status` (exit 0); step 2's two `gh pr list` commands with `<start>` as `2026-11-20` (both exit 0; the first listed 22 pull requests, the second none); `gh pr list ... --json number,state,mergedAt,createdAt,updatedAt`; step 2's `git log` with `--since=2026-11-21` and with `--since="2026-11-21 00:00"`, and with and without `--all`; the same `git log` with `-C src/orders-api`; `git submodule status`; `grep` for inbound links to the page; and `python3 ws.py check`, which reports nothing on this page beyond the expected missing README row for a batch 2 page.

The page has no `## References` heading.

## Findings

| # | Class | Where | Finding | Disposition |
|---|---|---|---|---|
| 1 | contradiction | Steps, step 8; Rules, the seventh row | Blocking. The Rules row says "Write only the standup log, outside every repository", and step 8 says "This page writes no file in this repository." Step 8 also says to end as procedure endings says, and that page's question-log entry writes and commits a row in `docs/question-log.md`. The contract's rules table requires that row whenever the agent had to ask a person something the workspace should have answered. An agent that follows the Rules row skips the entry the contract requires. Tracker operations, which this page links, states the exception: "Apart from a question-log entry, nothing on this page commits a file". Verified: the three texts. | fixed: the In short line, step 8 and the seventh Rules row now say "Apart from a question-log entry"; the same exception was swept into bug triage meeting's step 8 |
| 2 | contradiction | Steps, step 7; the template's skeleton | Blocking. Step 7 gives the rollup and closing lines as the reply, in the template's shape, which has no place for a verified or inferred mark. The contract's rules table says to mark every claim in a report, and procedure endings' "The report" says the same. Many of the claims are inferences: step 3 turns commits into outcomes, and step 4 judges what is blocked "on someone else". Step 8 names only the window, the unavailable sources and the save as the report's content. So an agent following the page reports the person's work with no marks. Verified: the texts. Inferred: that an agent treats the rollup as the report the contract means; when in doubt, blocking. | fixed: step 4 writes each line with its verified or inferred mark, as the template now defines; step 7's reply and step 8's report carry the marks; the template's skeleton and example gained a mark on every line but the title; a new Rules row |
| 3 | step | Steps, step 2, Git | Not blocking. `git log --since=<start>` with a bare date starts at that date at the current time of day, not at midnight. Run at 09:55, `--since=2026-11-21` listed 119 commits and `--since="2026-11-21 00:00"` listed 146: the 27 commits made before 09:55 on the start day were dropped. With no log, step 1's default starts on the previous working day, so most of that day's morning is lost. The command also reads only the branch checked out: with `--all` it listed 85 commits since 2026-11-22, not 81, so work on other branches is missed. Verified: the commands and counts. | fixed: the command is now `git log --all --since="<start> 00:00" ...`; run once at 2026-11-21, exit 0, 152 commits |
| 4 | step | Steps, step 2, The git host; step 4 | Not blocking. Step 4's Done holds what was "merged, closed, shipped or filed in the window". Step 2's first `gh pr list` asks for `number,title,state,url,updatedAt` only, and filters by `updated:>=<start>`. So a pull request merged before the window and commented on inside it comes back `MERGED`, and nothing gathered says when it merged. `mergedAt` and `createdAt` are fields `gh pr list --json` returns. Verified: the command with those fields printed them. Inferred: how often such a pull request shows up. | fixed: the first `gh pr list` now asks for `createdAt,mergedAt` too; run once, exit 0, both fields printed |
| 5 | step | Steps, step 4, the closing lines | Not blocking. Two closing-line inputs are not defined. "No movement" lists the person's open items that did not move, but every source in step 2 lists only items changed since the start date, so those items are never gathered. "Left out" names each personal item, but no step says what makes an item personal or when step 3 leaves one out. Verified: step 2's three queries each filter by date, and neither page defines a personal item. | fixed: the tracker read now also lists the person's open items of any date, and step 4's no-movement line takes those that did not change; step 3 defines a personal item and leaves it out |
| 6 | step | Steps, steps 1 and 6 | Not blocking. Step 6 replaces that day's entry on a second run the same day. Step 1 starts the window at the newest entry's date, which on that rerun is today's own entry. So the replacing entry covers only today, and the earlier window's items leave the log. No step says to take the window from the entry before today's. Verified: the two steps. Inferred: the effect on a rerun. | fixed: step 1 reads the entry below today's when the newest entry is today's, since this run replaces it; Rules row updated |
| 7 | step | Steps, step 2, Git and The git host | Not blocking. Step 2 runs git "in each one pinned under `src/` with `-C src/REPO`" but gives no way to tell which folders are pinned. In this sample none is: `git submodule status` prints nothing, and `git -C src/orders-api log` returned the same 81 commits as the workspace, so each folder would repeat the workspace's history. The `-R OWNER/REPO` for a pinned repository's pull requests is not defined either. Verified: the commands. | fixed: step 2 says `git submodule status` lists the pinned repositories, and none means this repository's log only (run once: exit 0, prints nothing); `-R OWNER/REPO` comes from `git -C src/REPO remote get-url origin` |
| 8 | enforcement | Steps, steps 2 and 7; Rules | Not blocking. Two rules have no Rules row: step 2's "In draft mode, do not ask the person to paste items", and step 7's "Print the detail only when the person asks for it". Extend the workspace's step 4 asks for a row for every must and never on the page. Verified: the Rules table's eight rows. | fixed: two Rules rows added, for draft mode's no-paste rule and for printing the detail only on request |
| 9 | placement | Steps, steps 3 and 4; Rules, rows three to five | Not blocking. Steps 3 and 4 and three Rules rows restate the entry's item rules: an item is an outcome, never a commit; a parent item is one line with nested sub-tasks; each item is one short spoken-style line with a link. The [standup log template](../../templates/standup-log.md#filling-it-in)'s "Filling it in" and Rules table state the same rules. Step 5 links the template for the rollup's rules instead, so the page is inconsistent about which page owns the entry's shape. Verified: both pages' texts. | fixed: steps 3 and 4 now link the template's "Filling it in" for the item rules instead of restating them; Rules rows three to five became one row pointing at the template, plus the mark row |

## Checked with no finding

- trigger: the purpose line and **In short** line name the request (what a person moved since their last standup) and the page's one write, and fire on nothing else. No inbound link exists yet, which the batch 2 note puts out of scope.
- eval-case: the page is marked `proof: unproven` with `prove-by: M9`, which is not in `workspace.json`'s `building` list, and the lane-draft line names M9, so the new behavior needs no eval case yet.

## Re-check

A fresh session read the page as it stands on `4190d8d`, uncommitted, beside its template, the contract, procedure endings, tracker operations and git-host operations.

| # | Verdict | Evidence |
|---|---|---|
| 1 | upheld | The **In short** line, step 8 and the eighth Rules row each now open with "Apart from a question-log entry", matching tracker operations' closing line. Bug triage meeting's step 8 carries the same words. Verified: the texts and `grep`. |
| 2 | upheld | Step 4 writes each line with its mark, as the template's "Filling it in" defines verified and inferred; step 7's reply and step 8's report carry the marks; the fourth Rules row states it. The template's skeleton and worked example mark every line but the title. Verified: both pages' texts. |
| 3 | upheld | Step 2's command is `git log --all --since="<start> 00:00" ...`. Run once with `2026-11-21`: exit 0, 152 commits. Verified. |
| 4 | upheld | The first `gh pr list` asks for `createdAt,mergedAt`. Run once with `2026-11-20`: exit 0, both fields printed, such as `"mergedAt":"2026-11-23T16:14:54Z"`. The second, the reviews query, also exit 0. Verified. |
| 5 | upheld | The tracker read lists the person's open items of any date, step 4's no-movement line takes those that did not change, and step 3 defines a personal item as one about the person rather than the work. Verified: the texts. |
| 6 | upheld | Step 1 reads the entry below today's when the newest entry is today's, and the second Rules row says the same. Verified: the texts. |
| 7 | upheld | `git submodule status` ran: exit 0, prints nothing, which the page now reads as "none is pinned". `gh pr list -R` with the output of `git remote get-url origin`, an SSH URL, ran: exit 0, so the remote's URL works as the `-R` value. Verified. |
| 8 | upheld | The fifth and sixth Rules rows hold draft mode's no-paste rule and printing the detail only on request. Verified: the Rules table. |
| 9 | upheld | Steps 3 and 4 link the template's "Filling it in" for the item rules, and the third Rules row points at the template instead of restating them. Verified: the texts. |

What a fix broke:

- none.

What the first reading missed:

- Not blocking. Step 2's git-host bullet says to check access "as step 1 of git-host operations says". That step sends a failed check to its own step 7, the report, while this page's step 7 is "Show it" and step 2 still has the tracker to read. Step 2's output, each unreachable source with its reason, is the intended path, but the borrowed step does not say so. Verified: git-host operations' step 1. Inferred: that an agent might jump.
