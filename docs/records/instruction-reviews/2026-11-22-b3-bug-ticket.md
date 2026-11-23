---
kind: record
last-reviewed: 2026-11-22
covers: docs/templates/bug-ticket.md
reviewed-at: f757aed, with the uncommitted change of the B3 builder
---

# Instruction review: docs/templates/bug-ticket.md

This records the instruction review of the new bug report template, for its author and for anyone filing a bug from it.

**In short:** 5 findings, 1 of them blocking: 1 contradiction, 1 step, 1 trigger, 1 enforcement, 1 eval-case. The blocking one: the `gh issue create` command names no repository, so from the workspace it files the bug on this workspace's own repository, which has issues turned on.

## Scope

In scope: the whole page, as a new template. Read in full: the page; `AGENTS.md`, `INDEX.md`, `docs/playbooks/instruction-review.md`, `docs/procedure-endings.md`, `docs/layout.md`, `docs/reader-standard.md`, `docs/authoring.md`; B3's row and the 2026-11-22 entries naming B3 in the M3 plan, including the bug ticket standard's entry of 2026-11-21; `docs/templates/README.md`, `docs/playbooks/tracker-operations.md`, `docs/playbooks/git-host-operations.md`, `docs/playbooks/handoff.md`, `docs/playbooks/fix-a-bug.md`, decision 0006. Ran `python3 ws.py check` in the worktree: it passed, with one warning about fix a bug's eval record, unrelated to this page. Ran `gh repo view --json hasIssuesEnabled` and `gh issue create --help`, both read-only. Read `src/orders-web/quarterlyExport.ts` against the worked example. Counted the page's top layer at 81 words.

## Findings

| # | Class | Where | Finding | Disposition |
|---|---|---|---|---|
| 1 | step | Where tickets live | Blocking. "Where the tracker is GitHub's issues, the skeleton below works as it stands, and `gh issue create --title "TITLE" --body-file FILE` files it." The command names no repository, so `gh` files on the repository of the current folder. An agent working in this workspace files the bug on the workspace's own repository, not the team's tracker. The same section says "This repository has no tracker", yet its issues are turned on, so the write succeeds there. The person's yes, given for a ticket on the team's tracker, does not cover a post on this repository. The command needs `-R OWNER/REPO` naming the tracker's repository. Verified: `gh repo view --json hasIssuesEnabled` prints `true` here; `gh issue create --help` gives `-R` as the way to select another repository. Inferred: that an agent runs the command from the workspace's top folder. | fixed: "Where tickets live" now files with `gh issue create --repo OWNER/REPO`, says why the repository is always named, and never files on this workspace's repository unless it is the team's tracker. The yes links tracker operations' "Which writes need a yes". A rules row holds it. |
| 2 | contradiction | Skeleton; A worked example | Not blocking. The skeleton's body starts with the summary quote, and the title goes in the tracker's title field, as `--title` shows. The worked example's body starts with the title as a `#` heading. An agent copying the example as the body file repeats the title inside the body, and two writers following the skeleton and the example produce different tickets, against the reader standard's reason for fixed headings. Verified. | fixed: the worked example's title now sits on a `Title:` line above the fenced block, which is the body alone, as the skeleton has it. |
| 3 | trigger | When to use it | Not blocking. The page fires when "a request asks you to file a bug, or to write one up". The templates index row also fires it when you "rewrite a bug in the tracker", and tracker operations' "Rewrite a stale item" row does that rewrite without naming this template. Tracker operations' "Create an item" row, which an agent reaches first for "file a bug", does not route here either; only the templates index and the reader standard link the page. Verified with `grep -rln bug-ticket.md`. A missing `INDEX.md` row is left to slice Z, as the plan queues index rows. | fixed: "When to use it" now covers rewriting a stale bug ticket, and tracker operations' "Create an item" row links this template. The `INDEX.md` row is queued for slice Z. |
| 4 | enforcement | Filling it, Evidence and Code pointer | Not blocking. Two nevers have no row in the rules table: "Never a link that expires or that only you can open" and "Do not give a line number: lines move". The style guide asks each must and never to have a row. Verified. | fixed: both nevers now have rows in the rules table. |
| 5 | eval-case | Before you write; Filling it, Filing it | Not blocking. Beyond the shape, the page asks an agent for new behavior of its own: search open and closed tickets for a duplicate before filing, reproduce the fault and record the commit, offer an addition to an existing ticket instead of filing, and file at the first status with triage's fields empty. No eval case covers it, and decision 0006 gives a template no proof mark, so the behavior has neither a case nor a `prove-by` milestone. Verified: `covered()` lists no template for `big-report`, `fix-a-bug` or `nightly-job`. | declined: a template or reference page carries no proof key; the procedures that use it carry the proof state, as the plan sets the page kind. |

## Checked with no finding

- placement: the outward-write rule is linked to procedure endings, not restated, and the write itself is sent to tracker operations, including the case with no tracker tool. The page states no rule of the commit, push or report. Verified.
- The reader standard's shape rules hold: the copy's readers are named ("a product manager, a tester or a triage meeting"), the top layer has a budget of 200 words and a summary of two sentences at most, the headings are fixed with a drop rule, and there is one worked example marked invented. The page's own top layer is 81 words, under 120. The example's code pointer is real: `QuarterlyExport.toCsv` in `src/orders-web/quarterlyExport.ts` joins one line per order and writes no header line. Verified.

## Re-check

A fresh session re-read the page on 2026-11-22, after the fix round.

| # | Verdict | Evidence |
|---|---|---|
| 1 | fixed | "Where tickets live" files with `gh issue create --repo OWNER/REPO`, says why the repository is always named, and a rules row holds it. Verified: the page's text. The fix opens a new gap, under "Broke". |
| 2 | fixed | The worked example's title sits on a `Title:` line above the fenced block, which holds the body alone, as the skeleton does. Verified. |
| 3 | fixed | "When to use it" covers rewriting a stale bug ticket, and tracker operations' "Create an item" row links the page. Verified: both texts. Tracker operations' "Rewrite a stale item" row still does not link it; that is recorded in the sweep record of tracker operations. |
| 4 | fixed | Both nevers have rows in the Rules table. Verified. |
| 5 | decline upheld | Decision 0006 says a template carries no proof key, so the page cannot hold a `prove-by`. The behavior runs inside tracker operations, which is `proof: unproven` with `prove-by: M8`. Verified: decision 0006's "The mark" and tracker operations' front matter. |

Broke:

- Blocking. "Where tickets live" now files on "the tracker's repository" with `--repo OWNER/REPO`, whatever that repository is. Procedure endings' Rules table says to "write nothing on a repository outside this one and those pinned under `src/`". Git-host operations says such a write "is never made. Give the person the text to post instead." When a team's issues sit on a repository that is neither, an agent following this page files there, against both rule pages. Verified: the three texts. Inferred: that a team's issue tracker can sit on a repository not pinned under `src/`. The page needs the same limit: file only on this repository or one pinned under `src/`, and otherwise give the person the ticket's text.

Missed: none.
