---
kind: record
last-reviewed: 2026-11-23
covers: docs/templates/standup-log.md
reviewed-at: 1a18d68, with the uncommitted change of the B4 slice session
---

# Instruction review: docs/templates/standup-log.md

This records the instruction review of slice B4's new standup log template, a product lane draft, for the change's author.

**In short:** 4 findings, none blocking: 2 contradiction, 1 enforcement, 1 placement. The worked example puts one pull request in both Doing and Waiting on, though the playbook puts each item in one section. A same-day rerun's window starts at the entry it replaces. The page restates the playbook's window rules.

## Scope

In scope: the whole page, which is new and untracked. Read beside it: `AGENTS.md`, `INDEX.md`, `docs/layout.md`, `docs/authoring.md`, `docs/procedure-endings.md`, `docs/reader-standard.md`, `docs/extend-the-workspace.md`, and the page it links to, `docs/playbooks/standup-report.md`, with the pages that one links: tracker operations, git-host operations and decision 0006. The page gives no command to run. Ran `grep` for inbound links to the page, and `python3 ws.py check`, which reports nothing on this page.

The page has no `## References` heading.

## Findings

| # | Class | Where | Finding | Disposition |
|---|---|---|---|---|
| 1 | contradiction | Worked example | Not blocking. The example lists pull request 88, the retry fix, under Doing ("Opened the retry fix for the nightly job") and under Waiting on ("The retry fix, on a payments team review"), with the same link. The standup report's step 4 says "Put each item in one section", and this page gives no rule for an item that is both open and blocked. An agent copying the example lists such an item twice. Verified: the example and step 4. | fixed: the example's pull request 88 now sits under Waiting on only, Doing holds another invented pull request, and "Filling it in" says a blocked open item goes under Waiting on only; the playbook's step 4 says the same |
| 2 | contradiction | Where it lives; In short | Not blocking. The page says a second run on the same day replaces that day's entry, and that the next report's window starts at the newest entry's date. On a same-day rerun the newest entry is the one being replaced, so the window starts today. The replacing entry then covers only today, and the first run's earlier window leaves the log. The two rules cannot both hold as a redo of that day's report. Verified: the two bullets. Inferred: the effect on a rerun. | fixed: the window and rerun bullets left this page; it now links the standup report's steps 1 and 6, and step 1 there takes the entry below today's on a rerun |
| 3 | enforcement | Where it lives; Filling it in; Rules | Not blocking. Two rules have no Rules row: "The standup report writes it; nothing else does", and each item has "at least one link". Extend the workspace's step 4 asks for a row for every must and never on the page. Verified: the Rules table's five rows. | fixed: Rules rows added for "only the standup report writes the log" and for one link and one section per item |
| 4 | placement | Where it lives; Rules, the second row | Not blocking. The bullets on the window's start and the same-day rerun, and the second Rules row, restate procedure rules that the [standup report](../../playbooks/standup-report.md#steps)'s steps 1 and 6 own. Finding 2's gap sits in both copies. A template owns the entry's shape; the procedure that writes it owns when and over what window. Verified: both pages' texts. | fixed: the window and rerun rules now live only in the playbook's steps 1 and 6; this page links them, and its second Rules row keeps only the entry order |

## Checked with no finding

- step: the page has no steps. The skeleton's placeholders are each defined under "Filling it in", including which empty sections are dropped and which keep "none". The undefined "personal item" is recorded on the playbook's record, where the step that needs it lives.
- trigger: the purpose line names the log and its two readers; the **In short** line gives its place, order and parts. No inbound link exists but the playbook's, and the batch 2 note puts index rows out of scope.
- eval-case: the page is a template, which carries no proof keys under decision 0006. Its lane-draft line names M9 as its first use on real work.

## Re-check

A fresh session read the page as it stands on `4190d8d`, uncommitted, beside the standup report playbook.

| # | Verdict | Evidence |
|---|---|---|
| 1 | upheld | Pull request 88 sits under Waiting on only; Doing holds pull request 90. "Filling it in" says a blocked open item goes under Waiting on only, and the playbook's step 4 says the same. Verified: both texts. |
| 2 | upheld | "Where it lives" no longer states the window or the rerun rule; it links the playbook's steps 1 and 6, and step 1 there takes the entry below today's on a rerun. Verified: both texts. |
| 3 | upheld | The Rules table gained "Only the standup report writes the log" and "Each item has at least one link, and sits in one section only". Verified: the table. |
| 4 | upheld | The window and rerun rules live only in the playbook's steps 1 and 6. The second Rules row keeps only the entry order. Verified: both pages. |

What a fix broke:

- Not blocking. The rule that a blocked open item goes under Waiting on, never also Doing, is now stated on both pages: this page's "An item in two sections" and Rules row, and the playbook's step 4, Waiting on. Finding 4's own reasoning gives sorting to the procedure and the entry's shape to the template; one page should state it and the other link. Verified: both texts.

What the first reading missed:

- Not blocking. The skeleton's no-movement line is `<...> (<mark>)`, with no link, but the worked example's no-movement line carries a link. A writer cannot tell from the skeleton whether the line takes one. Verified: the skeleton and the example.
