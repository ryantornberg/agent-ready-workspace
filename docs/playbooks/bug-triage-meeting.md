---
kind: playbook
lane: product
proof: unproven
prove-by: M9
last-reviewed: 2026-11-23
---

# Bug triage meeting

How an agent prepares a bug triage meeting's sheet and applies its outcomes, for the agent asked to do either.

**In short:** two days before, the agent checks each new bug's labels, writes a one-line plain summary, and puts each bug in one agenda group. The day before, a developer checks the labels on the rows discussed one at a time. After the meeting, the agent applies the outcomes on the person's yes.

This is a lane draft: product lane. It has not been run on real work yet; M9 runs it, as [decision 0006](../decisions/0006-what-proven-means.md) says.

Why: a triage meeting's cost is reading time. Grouping by [the triage labels](../triage-labels.md) lets the meeting decide most bugs a group at a time, and spend its reading on the few that need it.

## The agenda groups

Each bug goes in one group: the first row that matches wins. Inside a group, `effort:small` bugs come first. Anyone in the meeting may pull a bug out of its group to discuss it alone.

| # | Group | A bug matches when it carries | Decided |
|---|---|---|---|
| 1 | Security and data | `kind:security` or `kind:data` | One at a time. |
| 2 | Possible launch blocker | `affects:end-user` or `affects:staff`, and `seen:observed`, and `kind:functional` | One at a time. |
| 3 | Accessibility | `kind:accessibility` | One decision for the group. |
| 4 | Harden | `trigger:other-system-fails`, and `affects:team-only` or `affects:nobody-yet`, and `kind:functional` | One decision for the group. |
| 5 | Developers' call | `kind:tooling` | By the developers, without product. |
| 6 | Everything else | Anything left | One decision for the group. |

A fault nobody has watched happen, `seen:code-reading`, never lands in group 2.

## The outcomes

The meeting gives each bug one outcome:

- **A release:** a release not yet shipped, by its name on the tracker.
- **No release yet:** it stays open with no release.
- **Harden:** it is folded into its area's hardening story, as [the next section](#the-hardening-story) says.
- **Reject:** closed as rejected, with a one-line reason.

## Which page wins

| The request | Go to |
|---|---|
| Prepare a triage meeting's sheet, or apply its outcomes | This page. |
| Check one bug's text, labels and size so a developer can take it | [Bug grooming](bug-grooming.md). |
| Change one bug's field, status or label outside a meeting | [Tracker operations](tracker-operations.md). |

## The hardening story

One hardening story is open per area at a time. Default: its title is `Hardening: <area>`, so a search finds it. It holds one row per finding: what fails, when, and where in the code by file and name. Default: when the bug has no code pointer, write `where: not known yet`. It is sized and closed like any story. A bug folded into it is rejected, with a link to the story.

## Steps

1. **Gather the new bugs.** Input: the meeting's date and the bugs in scope. Default: every bug filed since the last meeting, at the tracker's first status with no release set. List them with the session's tracker tool. In draft mode, ask the person for the keys; with no answer, go to step 8 and say what you needed. Read each as [tracker operations](tracker-operations.md#steps) says in its steps 1 and 2; its draft mode applies when the session has no tracker tool. Run this two days before the meeting. Default: when asked later, run it anyway, and say in the report that the developer's check of step 5 may not fit before the meeting. Output: each bug's text and labels.
2. **Check the labels.** Input: each bug's labels. Hold them against [the triage labels](../triage-labels.md): one from each category and one area. A bug that has grooming's size needs no `effort` label. Where a label is missing or does not fit the text, propose one. Output: each bug's labels, with each proposal marked. Default: group a bug by its proposed labels until they are settled.
3. **Write the sheet.** Input: the labels and the text. Write one plain line per bug: what goes wrong, and for whom, with no code terms. Put each bug in its group by the table above, small effort first. The sheet is a [page for a product reader](../product-reader-pages.md). Under each group, name the outcomes the meeting can choose and what follows from each, such as a Harden bug being closed as rejected, with a link to its story. Give each row the bug's key and link, the plain line, the effort in words (the `effort` label, or grooming's size), and an empty outcome column the meeting fills in. Mark each row whose labels were proposed. Output: the sheet.
4. **Ask once for the label writes.** Input: the proposed labels. Show them in one message, by bug, and ask which to set. Labels on another person's bug always need a yes first, as [tracker operations](tracker-operations.md#which-writes-need-a-yes) says. Default: with no answer, set none; the sheet keeps them marked as proposed. Make the writes as tracker operations says in its steps 5 and 6. Then update the sheet: unmark each label set, and regroup each row whose proposal was declined by the labels it still carries. Output: each label set, or still proposed, and the updated sheet.
5. **Hand over the sheet.** Input: the sheet. Give it in your reply for the person. Posting it anywhere outside the workspace, such as a chat or a wiki, is an outward write: make it only as [procedure endings](../procedure-endings.md#outward-writes) says. Name the rows in groups 1 and 2 for a developer to check the day before. For each major security bug, as [checking a shelved predecessor](../predecessor-check.md#when-it-applies) defines it, name that check as due. Output: the sheet, and the rows to check. The run before the meeting ends here: go to step 8. A later request to apply the outcomes starts at step 6.
6. **Take the outcomes.** Input: the outcome per bug, from the person, after the meeting. Default: a bug with no outcome stays as it is. List each write the outcomes need: the release field, a hardening row, a rejection with its reason as a comment. A bug for hardening needs its area's open hardening story; when there is none, creating one is a write to list. Output: the list of writes.
7. **Apply the outcomes.** Input: the list. A request to apply named outcomes is the yes for the writes on those bugs, except rejecting one. Three writes need their own yes, unless the request names them in its own words. Rejecting a bug is one, as [tracker operations](tracker-operations.md#which-writes-need-a-yes) says. A row on a hardening story is one, as the story is an item the request did not name. Creating a hardening story is the third. A Harden outcome alone names none of them. Ask once for those; with no answer, make none, and the bug stays as it is. Make the rest as tracker operations says in its steps 5 and 6. Add a hardening row before you reject the bug it came from. Output: each write made and confirmed, or proposed.
8. **Finish.** End as [procedure endings](../procedure-endings.md) says. Before the meeting, the report gives the sheet, the label writes made or proposed, and the rows for a developer to check. After it, the report lists each outcome applied, and each one waiting. Apart from a question-log entry, this page writes no file in this repository.

Stop when the report is given.

## Example

Invented: three new bugs on the order system.

| Bug | Labels | Group |
|---|---|---|
| `ORD-421`: holds lifted by the nightly job | `affects:end-user`, `trigger:normal-path`, `seen:observed`, `kind:functional`, `effort:medium`, `area:holds` | 2, possible launch blocker |
| `ORD-415`: the nightly job floods its log with retries when the payment service is down | `affects:team-only`, `trigger:other-system-fails`, `seen:observed`, `kind:functional`, `effort:small`, `area:reconciliation` | 4, harden |
| `ORD-426`: anyone can lift another account's hold | `affects:end-user`, `trigger:specific-input`, `seen:code-reading`, `kind:security`, `effort:small`, `area:holds` (all proposed: filed without labels) | 1, security and data |

`ORD-426` would never reach group 2, as nobody has watched it happen. It lands in group 1 by its kind.

## Rules

| Rule | Enforced by |
|---|---|
| Each bug goes in exactly one group: the first matching row wins. | `prose` |
| A bug with `seen:code-reading` never lands in the launch-blocker group. | `prose` |
| A developer checks the labels on the rows decided one at a time before the meeting. | `prose` |
| The sheet follows the pages for a product reader: plain lines, no codes the reader must learn. | `prose` |
| Rejecting a bug, a row on a hardening story and creating a hardening story each need their own yes, unless the request names them. | `prose` |
| One hardening story is open per area; a bug folded into it is rejected with a link. | `prose` |
