---
kind: record
last-reviewed: 2026-11-23
covers: docs/playbooks/bug-triage-meeting.md
reviewed-at: 1a18d68, with the uncommitted change of the B4 slice session
---

# Instruction review: docs/playbooks/bug-triage-meeting.md

This records the instruction review of slice B4's new bug triage meeting playbook, a product lane draft, for the change's author.

**In short:** 12 findings: 5 contradiction, 5 step, 1 trigger, 1 placement; 1 blocking. Step 7 makes the request the yes for a row added to the area's hardening story, an item the request does not name, which tracker operations makes ask-first. The default scope gathers every "no release yet" bug again at each meeting. A groomed bug gets an `effort` label proposed back. The sheet is not updated after the label writes, and the hardening story has no way to be found.

## Scope

In scope: the whole page, which is new and untracked. Read beside it: `AGENTS.md`, `INDEX.md`, `docs/layout.md`, `docs/authoring.md`, `docs/procedure-endings.md`, `docs/reader-standard.md`, `docs/extend-the-workspace.md`, the instruction review playbook, and every page the page links to: decision 0006, the triage labels, tracker operations and pages for a product reader. Also read bug grooming, the bug report template's opening, and the QA test plan template, which the triage labels and the product reader page name beside this one.

Ran: `python3 ws.py check`, which reports nothing on this page but the expected `proof` error for its missing README row, so every link and anchor on it resolves and its opening passes `page_kinds`; `grep -n -i triage INDEX.md`, which finds nothing; and `grep -n '"building"' -A3 workspace.json`, which shows `M3` only.

## Findings

| # | Class | Where | Finding | Disposition |
|---|---|---|---|---|
| 1 | contradiction | Steps, step 7 | Blocking. Step 7 says "A request to apply named outcomes is the yes for those writes", and carves out only rejecting and creating. A Harden outcome also needs a row added to the area's open hardening story, a separate item the request does not name. Tracker operations' "Which writes need a yes" always asks first for "an item nobody asked about", and says none of those follows from a request that names something wider. So an agent following step 7 writes on the hardening story without the yes tracker operations requires. Also, the step says creating is ask-first "as tracker operations says", but that section's list does not name creating. Verified by reading both sections. Inferred: that "Harden ORD-415" does not name the story write in its own words, since step 7 itself treats the rejection that Harden implies as needing its own words. | fixed: step 7 says three writes need their own yes unless the request names them: rejecting a bug (tracker operations), a row on a hardening story, and creating a hardening story; a Harden outcome alone names none; the rules row matches and no longer claims tracker operations lists creating |
| 2 | step | Steps, step 1 | Not blocking. The default scope is "every bug at the tracker's first status with no release set". Step 1 then sends the agent to tracker operations' steps 1 and 2. That step 2 reads "the item keys the request names", and when the request names none and the words match more than one item, it asks which. In draft mode, it asks the person to paste each item. Neither gives a way to list the default set, and step 1 gives no default for draft mode, where the agent cannot query. Verified by reading tracker operations' steps 1 and 2. | fixed: step 1 lists the default set with the session's tracker tool, and in draft mode asks the person for the keys, going to step 8 with no answer |
| 3 | step | Steps, step 1; The outcomes | Not blocking. The outcome "No release yet" leaves a bug open with no release, and step 6 lists no status change for it. So it stays at the first status with no release set, and step 1's default gathers it again at every later meeting, with no way to tell it from a new bug. Verified by reading "The outcomes" and step 6's list of writes. Inferred: that a team's first status does not change on its own after triage. | fixed: step 1's default scope is bugs filed since the last meeting, so a "No release yet" bug is not gathered again |
| 4 | step | Steps, step 1; In short | Not blocking. "Run this two days before the meeting" is not an action an agent can take: it runs when asked. Nothing says what to do when the request comes one day before, or on the day, when the developer's check of step 5 can no longer happen the day before. Verified: no step or default names a late run. | fixed: step 1 gives a default for a late request: run anyway and say the developer's check may not fit |
| 5 | contradiction | Steps, steps 2 and 3 | Not blocking. Step 2 holds each bug to "one from each category and one area", and proposes a missing label. The triage labels page says "A groomed bug carries every label here but `effort`", and bug grooming removes it "so a bug never shows two sizes". A groomed bug in scope gets an `effort` label proposed back, and step 3's "the effort in words" has no source for it. Neither page labels this as an exception. Verified by reading the triage labels' "Boundary rules" and bug grooming's step 7. Inferred: that a groomed bug can be in scope, as when the request names it, since the default scope is the first status. | fixed: step 2 says a bug with grooming's size needs no `effort` label, and step 3's effort in words reads the label or grooming's size; the triage labels' boundary rule says the same |
| 6 | step | Steps, steps 3 and 4 | Not blocking. Step 3 writes the sheet, grouping by proposed labels and marking those rows. Step 4 then sets some labels and leaves others proposed. No step updates the sheet after step 4: a row whose label was set stays marked proposed, and a row whose proposal the person declined may sit in the wrong group. Verified: step 5 hands over "the sheet" from step 3 with no revision. | fixed: step 4 updates the sheet after the label writes: unmarks labels set and regroups rows whose proposal was declined |
| 7 | step | The hardening story; Steps, steps 6 and 7 | Not blocking. Step 6 needs "its area's open hardening story", but nothing says how to find it: no label, title or link marks a story as an area's hardening story. The row needs "where in the code by file and name", and a bug at triage may have no code pointer; there is no default. Verified by reading the section and both steps. | fixed: the hardening story's default title is `Hardening: <area>`, and a row with no code pointer says `where: not known yet` |
| 8 | contradiction | Steps, step 8 | Not blocking. "This page writes no file in this repository" conflicts with procedure endings' question-log entry, which writes and commits a row when the agent had to ask something the workspace should have answered. Tracker operations labels the same exception: "Apart from a question-log entry". This page does not. Verified by reading procedure endings' "The question-log entry" and tracker operations' stop line. | fixed: step 8 now reads "Apart from a question-log entry, this page writes no file in this repository" |
| 9 | contradiction | Example | Not blocking. Step 2 holds every bug to one label from each of five categories and one area. The example's three bugs carry three, three and two labels, with no area, and none of the rows is marked as proposed, as step 3 requires. A reader copying the example learns that a partial set is normal. Verified by reading the example against the triage labels' "In short" and step 3. | fixed: the example gives each bug its full label set, and marks the third bug's labels as proposed |
| 10 | contradiction | Steps, step 3 | Not blocking. Pages for a product reader, which step 3 says the sheet is, has rule 2: a decision "sits under text that names each choice and what follows from it". Step 3 asks only to "name the outcomes the meeting can choose", not what follows from each, such as a Harden bug being closed as rejected. Verified by reading both. | fixed: step 3 names what follows from each outcome, such as a Harden bug being closed as rejected with a link to its story |
| 11 | trigger | The page as a whole | Not blocking. The page has no "which page wins" section. A request to set a bug's release, reject a bug or check a bug's labels fires this page, tracker operations and bug grooming alike. Extend the workspace's step 5 asks a page to say which wins where two could fire on one request. Verified: the page has no such section, and `grep -i triage` finds no link to this page on either of the other two. | fixed: a "Which page wins" section routes between this page, bug grooming and tracker operations |
| 12 | placement | Rules | Not blocking. Three rows restate rules other pages own instead of linking them. "Every tracker write follows tracker operations; rejecting or creating an item is ask-first" restates tracker operations. "Posting the sheet outside the workspace needs the person's yes" restates procedure endings' outward writes, and drops its "unless the request names the write". "Mark every claim in the report verified or inferred" restates procedure endings' report. The style guide's "One rule, one page" counts these as placement findings. Verified by reading the three source pages. | fixed: the rows restating tracker operations, outward writes and the report's mark are removed; one row states this page's own yes rule |

## Checked with no finding

- enforcement: every must and never on the page has a row in its Rules table, each tagged `prose` but the report's mark, whose tag `eval:fix-a-bug` is the contract's own for that rule. No tag claims a part or case that does not show its rule.
- eval-case: the page is marked `proof: unproven` with `prove-by: M9`, and `workspace.json`'s `building` list holds only `M3`.

## Re-check

A fresh session read the page at `4190d8d`, with the uncommitted change of the B4 slice session, beside the contract, procedure endings, tracker operations, the triage labels, bug grooming, the predecessor check and pages for a product reader. It ran `python3 ws.py check`, which reports nothing on this page.

| # | Verdict | Evidence |
|---|---|---|
| 1 | upheld | Verified: step 7 says rejecting a bug, a row on a hardening story and creating a hardening story each need their own yes unless the request names them, and that a Harden outcome alone names none. Tracker operations' "Which writes need a yes" lists rejecting and "an item nobody asked about", which covers the story row. The rules row matches and no longer says tracker operations lists creating. |
| 2 | upheld | Verified: step 1 lists the default set with the session's tracker tool, and in draft mode asks the person for the keys, going to step 8 with no answer. |
| 3 | upheld | Verified: step 1's default scope is bugs filed since the last meeting, so a "No release yet" bug is not gathered again. The fix opens a gap, below. |
| 4 | upheld | Verified: step 1 runs a late request anyway and says the developer's check may not fit. |
| 5 | upheld | Verified: step 2 needs no `effort` label on a bug with grooming's size, step 3 reads the label or grooming's size, and the triage labels' boundary rule says the same. |
| 6 | upheld | Verified: step 4 unmarks each label set and regroups each row whose proposal was declined. |
| 7 | upheld | Verified: "The hardening story" gives the `Hardening: <area>` title and `where: not known yet` defaults. |
| 8 | upheld | Verified: step 8 ends "Apart from a question-log entry, this page writes no file in this repository". |
| 9 | upheld | Verified: the example gives each bug one label per category and an area, and marks `ORD-426`'s labels as proposed; each group matches the agenda table's first matching row. |
| 10 | upheld | Verified: step 3 names what follows from each outcome, as rule 2 of pages for a product reader asks. |
| 11 | upheld | Verified: "Which page wins" routes between this page, bug grooming and tracker operations. |
| 12 | upheld | Verified: the rows restating tracker operations, outward writes and the report's mark are gone; one row states this page's own yes rule. |

What a fix broke:

- Not blocking. Step 1's new scope, "filed since the last meeting", drops a bug the meeting left undecided. Step 6's default leaves a bug with no outcome as it is, at the first status with no release, the same state as a "No release yet" bug. It was filed before the last meeting, so no later run gathers it, and nothing on the tracker tells it apart. The page also gives no source or default for the last meeting's date. Verified by reading steps 1 and 6. Asking the person for that date, and recording each outcome as a comment so an undecided bug can be told from a "No release yet" one, would settle both.

What the first reading missed: none.
