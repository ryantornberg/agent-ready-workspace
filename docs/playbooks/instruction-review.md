---
kind: playbook
proof: unproven
prove-by: M4
last-reviewed: 2026-11-21
---

# The instruction review

How a change to a guidance page is reviewed as a program, recorded, and named in its commit. For the author of the change and the reviewer.

**In short:** guidance has no compiler, so a fresh session at the driver tier reads each changed guidance page against six checks and writes a record of its findings, each marked blocking or not. The author settles each finding, commits the record with the pages, and names it in an `Instructions-review:` trailer. The commit hook, the pre-push hook and CI refuse a guidance change that names no record and gives no listed reason to skip.

## When it runs

On every commit that adds, changes or deletes a guidance page. A guidance page is any path the `review_trailer` entry in [workspace.json](../../workspace.json) lists under `guidance` and not under `except`. Today that is `AGENTS.md`, `CLAUDE.md`, the Copilot and opencode pointer files, `INDEX.md`, the README, `evals/README.md`, and every page under `docs/` except plans, milestone records, records and the question log. The list also names `plugin/`, for the wrappers slice B6 of M3 adds there. In the kit's own repository it names the two seed pages under `kit/seed/` as well, which become an instance's README and eval page.

Skip the review only for one of these reasons, named in the trailer:

| Reason | When |
|---|---|
| `link or typo only` | The change fixes a link target or a spelling, and no sentence means something new. |
| `front matter only` | The change touches front matter and nothing below it, such as a review date. |
| `strike` | The maintainer struck the page: the commit removes it and its index rows, wrapper and table row. |
| `as the kit wrote it` | In an instance made from the kit, the first commit, or the commit of an upgrade, brings pages the kit's own reviews read. The check compares each guidance page the commit leaves in place with the hash in the commit's `kit.lock.json`, and refuses the deletion of a page that lock still holds. A page a record the commit names covers is judged by the record instead. The check trusts the lock in the same commit; the lock is machinery, so a change to it reaches main through a pull request, where its diff shows. See [decision 0007](../decisions/0007-the-kit.md). |

Anything else needs a review. When in doubt, review. For the first three reasons the check reads the reason, not the change, so a reason that does not apply passes it; using one is the author's word that it applies.

## Steps

1. **Finish the change first.** The review reads the pages as they will be committed.
2. **Hand the review to a fresh session at the driver tier.** Its prompt starts `Tier: driver`, as [orchestration](../orchestration.md#handing-work-off) requires. Give it the changed pages, the diff, and the paths of the files loaded beside them: the contract, the index, and the pages they link to. Never give it your reasoning or what you expect it to find.
3. **The reviewer runs the six checks** below on each page, verifies each finding before recording it, marks its [severity](#severity), and writes one record per page, with `open` in every Disposition cell. Where a page has a `## References` heading, the reviewer opens each source and checks that it says what the page credits it for. It edits nothing else.
4. **Settle every finding.** Verify it yourself. Fix the ones that are plainly right. For one that needs a decision, write your recommendation and ask the person who owns it. Write the outcome in the finding's Disposition cell, in one of the forms under "The record". Never lower a finding's severity mark. When the plan you work under allows no more fix rounds, a non-blocking finding still open goes to the record's "Known defects" section. A blocking finding still open then is never a known defect: name it in your report to the plan's owner, who decides.
5. **Index the record.** Add its row to [the index](../records/instruction-reviews/README.md): the record, the pages it covers, and the classes it found.
6. **Commit the record with the pages,** as [procedure endings](../procedure-endings.md#the-commit) says, and name it in the message: `Instructions-review: docs/records/instruction-reviews/<record>.md`. Give one trailer line per record.
7. **Stop** when every finding has a disposition and the commit check passes, then push and report as [procedure endings](../procedure-endings.md) says. When a plan asks for a re-check after its fix round, a fresh session writes it in the same record's "Re-check" section. Any other later change to the page in substance gets a review and a record of its own.

## The six checks

Each finding gets exactly one class.

| Class | The reviewer looks for |
|---|---|
| `contradiction` | Two statements that cannot both hold, on the page or against a file loaded beside it, or an exception that is not labelled as one. |
| `step` | A step an agent cannot execute as written: a path or command that does not exist, an input that is not defined, a decision with no default, or no stop condition. |
| `trigger` | Text that decides when guidance applies, such as a purpose line, an **In short** line, a wrapper's description or an index row, firing when it should not, or not firing when it should. |
| `enforcement` | A must or never with no enforcement stated, or a stated enforcement that is false, such as a rules-table tag whose case does not show the rule. |
| `placement` | Text on the wrong page, or text in the always-loaded layer that costs every session but belongs on a page loaded only when needed. A rule that [procedure endings](../procedure-endings.md) states, restated on a page instead of linked, is a placement finding; an older page switches to the link when it is next edited. |
| `eval-case` | New behavior the page asks of an agent that no eval case covers, where the page is not marked unproven with a `prove-by` milestone. |

## Severity

The reviewer marks each finding **blocking** or **not blocking**. A finding is blocking when an agent following the page as written would:

- write where it may not, such as a path a rule or the contract forbids, or a system outside the workspace without a yes;
- skip a person's yes that the contract, a rule page or a procedure requires;
- run a command that fails, or one that does not exist;
- follow a step that contradicts the contract or a rule page.

Anything else is not blocking, such as a weak trigger, a misplaced paragraph or a rule restated instead of linked. When in doubt, the reviewer marks it blocking.

The mark is the reviewer's. The author may fix, queue, defer or decline a finding, but never lowers its mark. A plan may stop on blocking findings alone, as M3's plan does for lane B.

## The record

One file per page, in [docs/records/instruction-reviews/](../records/instruction-reviews/README.md). Name it for the date and the page, such as `2026-11-21-layout.md`, adding a word when that name is taken, such as `2026-11-21-b1-layout.md`. The `covers:` line, not the name, ties a record to its page. Its front matter is `kind: record`, `last-reviewed`, `covers:` with the path of the one page it reviewed, and `reviewed-at:`. That names the commit the reviewer read; for a change not yet committed, the commit it sits on, followed by `, with the uncommitted change of <whose>`.

It opens with its title, `# Instruction review: <page>`, a purpose sentence, and an **In short** line with the count of findings per class. Then three sections:

- `## Scope`: what the reviewer read, and which part of the page was in scope.
- `## Findings`: a table with the header `| # | Class | Where | Finding | Disposition |`. "Where" names a heading or a table, never a line number. The Finding cell opens with its severity, `Blocking.` or `Not blocking.`, then the finding. Each finding marks its evidence verified or inferred. With no findings, the table keeps its header and the line `No findings.` follows it.
- `## Checked with no finding`: one line per class with no finding, saying what was checked.

Two more sections are added when they apply:

- `## Re-check`: a fresh session's reading after a fix round, with a table `| # | Verdict | Evidence |`, then what a fix broke and what the first reading missed, each marked blocking or not.
- `## Known defects`: each non-blocking finding still open when the plan allows no more fix rounds, with the milestone that is to fix it, which is the page's `prove-by` milestone, or the docs audit for a page with no `prove-by`.

The reviewer writes `open` in each Disposition cell. The author replaces it with one of: `fixed`, `queued for <where>`, `deferred to <slice or milestone>`, `known defect, for <milestone or the docs audit>`, or `declined`, each with its reason. A declined finding is not counted in the index.

## Where it is checked

The `review_trailer` check judges each commit by its own message, paths and files. A trailer must name a record that the same commit adds or changes and whose `covers:` line lists every guidance page the commit leaves in place, or give a listed reason. A deleted page needs a trailer, but no record covers it.

| Where | What it judges |
|---|---|
| The commit-msg hook | The commit being made, against the staged files. A merge in progress is left to the next two. |
| The pre-push hook | Every commit a push to main adds, with the check read from the remote's tip. A doc push lands on main before CI runs, so this is what stops one. |
| CI, `python3 ws.py check --commits BASE..HEAD` | Every commit of a pull request, and of a push to main. On main it can only report a failing run after the push. |

A commit is judged only once its own tree uses the check, so a branch started before the rule reached it is not judged for its older commits. A merge is judged by what it changes itself, not by what it brings in.

The `review_index` check holds [the index](../records/instruction-reviews/README.md) to the records: every record has a row and covers one page, each row's page and classes match its record, and each page in its `required` list has a record.

## Counting for a stop rule

A plan may stop when the same class turns up in too many pages. Count from the index: for each class, the rows that list it, over the pages reviewed in the batch being counted. Each record covers one page, and the index counts a class once per record, however many findings of it the record holds.

A plan may instead stop on blocking findings: one that survives the fix round, a declined one a re-check rejects, or one a fix creates. Count those from the records' Finding cells and "Re-check" sections; the index does not hold severity.

## Rules

| Rule | Enforced by |
|---|---|
| A commit that adds, changes or deletes a guidance page names a review record, or a listed reason to skip. | `review_trailer#a guidance page changed with no trailer fails`, `review_trailer#a skip reason outside the listed set fails` |
| The record a commit names exists in that commit, is added or changed by it, and covers every guidance page it leaves in place. | `review_trailer#a named record that does not exist fails`, `review_trailer#an old record the commit does not add or change fails`, `review_trailer#a record that does not cover a changed page fails` |
| A push to main holding such a commit is refused before it lands. | `review_trailer#of several commits, only the one without a trailer is named` |
| The index lists every record as it is, and each required page has one. | `review_index#a record with no row fails`, `review_index#a row whose classes differ from the record's findings fails`, `review_index#a required page with no record fails` |
| A record covers exactly one page. | `review_index#a record that covers two pages fails` |
| A skip reason is used only when it applies; for the first three, the check reads the reason, not the change. | `prose` |
| The reason `as the kit wrote it` passes only when every guidance page the commit leaves in place, other than those a named record covers, is as the commit's lock holds it. | `review_trailer#as the kit wrote it fails a page that differs from the lock` |
| A fresh session at the driver tier runs the review, without the author's reasoning. | `prose` |
| The author settles every finding before the commit. | `prose` |
| The reviewer marks each finding blocking or not, and the author never lowers the mark. | `prose` |
