---
kind: how-to
proof: unproven
prove-by: M5
last-reviewed: 2026-11-23
---

# Extend the workspace

How to add a page to this workspace, or change one, with its routing: a playbook, how-to, reference page, decision record or rule page. For any agent or person doing so.

**In short:** pick the page's kind and place from the table below, write it to its kind's shape, and give it a catalog row, a route in and, for a core playbook or how-to, a wrapper. Then commit it with its instruction review. A small change to an existing page, such as a fix, follows the same steps. A check, a hook or any other part is not a page: it is on [parts](parts.md).

## What this page covers

This page covers pages: a playbook, a how-to, a reference page, a decision record or a rule page, and their routing rows. A check, a hook or any other part is on [parts](parts.md). Any change to scripts, parts, hooks or CI follows [changing the machinery](changing-the-machinery.md). This page restates neither. Moving, renaming or archiving a page is on [layout](layout.md#archiving-a-page) and [maintain the workspace](maintain-the-workspace.md).

A finding the workspace should have told you, such as a missing alias, first goes through the research ladder's [offer to write a finding down](research-ladder.md#offer-to-write-a-finding-down): the offer decides whether it is written, and nothing is written without the person's yes. Once the person says yes, the write follows the steps below, like any other page change.

A change to pages only that passes the size gate, such as a fix to a page a review or an audit found wrong, also follows the steps below. The contract routes it here, not to fix a bug, since a page has no failing test to start from. For it, step 2's owner is the page being changed, step 3 is skipped, and step 4 edits that page in place. When that page is one the eval covers, step 5 says what to do instead.

## Pick the kind and the place

[Layout](layout.md) defines each kind and its front matter. This table says which one a new piece of text is.

| You are adding | Kind | Where | Its routing row |
|---|---|---|---|
| Steps an agent follows from a request to a report | playbook | `docs/playbooks/<name>.md` | A row in the [playbook catalog](playbooks/README.md), in its stage |
| Steps for one task, for a person or an agent | how-to | `docs/<name>.md` | A row in the [how-to index](how-tos.md), in the table of its stage |
| Facts to look up, not steps | reference | `docs/<name>.md` | A row in the how-to index, when a reader goes to it for a task |
| Facts that hold for every edit to files in one folder | reference, with an `applies-to` key | `docs/rules/<name>.md` | None: the `rule_pages` hook shows it when a matching file is edited |
| A choice that is hard to reverse, its options and what it gave up | decision | `docs/decisions/<NNNN>-<name>.md` | None: link it from the page whose rule it explains |
| A trap every session must know, in three lines or fewer | Not a page: a line in [AGENTS.md](../AGENTS.md#facts-a-model-cannot-derive) | The contract, which the eval covers: see step 5 | None |

Name a file for its task or topic, in lower-case words joined by hyphens, such as `safe-refactor.md`. A decision record takes the next free four-digit number in `docs/decisions/`.

**One owner per topic.** A procedure that overlaps a page already here goes into that page as a section, not into a page beside it. The section gets its own `## Heading`, and a procedure section carries the line `Proof: unproven, prove-by M<n>.` directly under that heading, as [decision 0006](decisions/0006-what-proven-means.md) says.

## Steps

1. **Size it.** Input: the request for a page. Put the change through [the size gate](size-the-work.md#the-gate). Default: when you cannot tell whether it passes, it fails. If it fails, climb [the ladder](size-the-work.md#the-ladder): goal and non-goals, then a hand-off plan a person approves, whose slices run steps 2 to 8. If it passes, run steps 2 to 8 yourself. The contract's "How work flows" routes it here, not to [fix a bug](playbooks/fix-a-bug.md): a page has no failing test to start from, so the instruction review at step 7 is its check instead. Output: the route the work takes.
2. **Find the owner.** Input: the page's topic. Look for a page that already owns it, in the [how-to index](how-tos.md), the [playbook catalog](playbooks/README.md) and [INDEX.md's topics](../INDEX.md#topics). Default: when one owns it, add a section there, as "One owner per topic" says. When two could own it, choose the one whose purpose sentence names the task. Output: the path of the new page or section, and its kind from the table above.
3. **For a playbook, show the need.** Input: the task the playbook would guide. The [evals rule](../evals/README.md#rules-that-make-this-worth-doing) is to write a new playbook only after a run without it shows the model failing at the task. Hand the task to a fresh session at the worker tier, as [orchestration](orchestration.md#handing-work-off) says, with the contract and no new page. Note what it got wrong. Output: that failure, the page's reason to exist. If the run does not fail, write nothing and go to step 8: report that the run passed, so the playbook is not needed. When an approved plan names the playbook, such as one a milestone ports, skip this run: the page ships unproven, and the milestone its `prove-by` names runs it on real work, as [decision 0006](decisions/0006-what-proven-means.md) says. Skip this step for every other kind.
4. **Write the page.** Input: the path and kind from step 2.
   - Front matter, as [layout](layout.md#page-kinds) requires. A playbook or how-to carries `kind`, `proof: unproven`, `prove-by: M<n>` and `last-reviewed` with today's date. A reference page carries `kind: reference` and `last-reviewed`; a rule page adds `applies-to` with a quoted path pattern, as in [the live order service's rule page](rules/orders-api.md). A decision record carries `kind: decision`, `status: proposed`, `date`, `deciders` and `last-reviewed`, as the [decision record template](templates/decision-record.md#front-matter) says; one an approved plan asks for may start at `status: accepted`.
   - `prove-by` default: the milestone the plan names. With no plan, take the first milestone after those in the `building` list of [workspace.json](../workspace.json). The `proof` check refuses a new page whose `prove-by` is a milestone being built.
   - The opening: title, a purpose sentence of 25 words or fewer, then the **In short** line, as [layout](layout.md#the-opening) says. A decision record may open with its **In short** line instead of a purpose sentence.
   - The words: as [the style guide](authoring.md) says.
   - The body. A playbook is numbered steps from request to report. A how-to is steps for one task. Each step names its input, its action and its output, a default for every decision, and when to stop. Machinery that does not exist yet is named as planned, with its milestone, and is never a step to run.
   - Never point a reader at an agent's private memory, a session's scratch folder, or any file only one machine holds: another reader cannot open it. Write the fact on the page instead.
   - A decision record is written only when the three conditions in [when a decision gets a record](playbooks/decision-interview.md#when-a-decision-gets-a-record) hold, and the person says yes. An approved plan that asks for a record is that yes. It follows the [decision record template](templates/decision-record.md), which the `decisions` check holds.
   - A rule page holds only facts that hold for every edit its pattern matches. opencode loads every rule page into every session, as [opencode.json](../opencode.json) says, so each line costs every session there.
   - End a playbook, how-to or reference page with `## Rules`: a table `| Rule | Enforced by |` with a row for every must and never on the page. A tag names a part and a case only when that case shows the rule, or an eval case as `eval:<case>`; otherwise it is `prose`. `python3 ws.py rules` lists the tags in use.

   Output: the page, or the section.
5. **Route it.** Input: the page. Add, in the same commit as the page:
   - Its row from the table above, in the playbook catalog or the how-to index.
   - For a playbook or how-to with no `lane` key, its wrapper and two selection cases, as the [playbook catalog](playbooks/README.md#three-ways-to-follow-a-playbook) describes them. Copy an existing wrapper to `plugin/skills/<the page's file name without .md>/SKILL.md`: a description that says when to fire and when not, naming the wrapper next to it, and a body that names your page. Copy an existing pair of cases in `plugin/evals/`: one request that should fire it, and one nearby request that should leave it quiet. Each description loads into every session, so keep it to a few lines. A page whose wrapper waits for M4's review machinery or M8's providers goes on the waiting list in the `wrappers` entry of [workspace.json](../workspace.json) instead, which is a machinery change; a wait for any other milestone needs the `wrappers` part changed as well. A lane page gets no wrapper until it is marked proven. The wrapper is a guidance page, so step 7's review gives it a record of its own.
   - For a playbook or how-to, its row in the README's [proven and unproven pages](../README.md#proven-and-unproven-pages) table. A procedure section with its own proof line gets a row too, named as the page's path, `#`, and the heading's anchor, such as `docs/orchestration.md#delegating`. The `proof` check fails a marked page or section with no row there.
   - A route in: one sentence on the page a reader is on when they need yours, naming the condition and linking your page. Where your page and another could both fire on one request, say on your page which one wins, and when.

   Some files are covered by the eval, so a change to them needs a new eval run, as the contract's rules say. They are the files [evals/arms.json](../evals/arms.json) gives the guided arm (`AGENTS.md`, `CLAUDE.md`, `INDEX.md`, [fix a bug](playbooks/fix-a-bug.md) and [the definition of done](definition-of-done.md)), and any page a case in `evals/cases/` adds, such as [the live order service's rule page](rules/orders-api.md). Default: make no change to them now, whether a new row or a fix in place; name it in the report as queued, for the next batch of eval-covered edits. When a check refuses the commit without the change, or an approved plan makes it, such as an adoption's, follow [maintain the workspace](maintain-the-workspace.md#when-a-duty-falls-due)'s step 4: the change goes on a branch, which is not merged until the eval run is on record. Output: the rows and the sentence.
6. **Run the checks.** Input: the changed files. Run `python3 ws.py check`. Fix each finding that names a file you wrote, and run it again. Output: no finding on your files. On a branch that step 5 sent through maintain's step 4, an `eval_record` finding naming a playbook, such as [fix a bug](playbooks/fix-a-bug.md), is expected until the eval run is on record. Unless your change is to that playbook, it is not a finding on your files: leave it and carry on as that step says. If a finding on your files will not clear, leave the files uncommitted and go to step 8: report the finding and what you tried.
7. **Review and commit.** Input: the checked files. Follow [the instruction review](playbooks/instruction-review.md): a fresh session reviews the page, you settle each finding, and the commit names the record in its trailer. Commit them as [procedure endings](procedure-endings.md#the-commit) says. By exception to that page's place for a page commit, a change step 5 sent to a branch is committed on that branch. Output: the commit. If a finding needs a person's decision and they have not answered, leave the files uncommitted and go to step 8 with the open findings. If the commit check refuses, fix the cause and commit again; if it refuses a file you did not write, leave that file out. On step 5's branch, an `eval_record` refusal is the expected one of step 6: commit as maintain's step 4 and [the trap it links](changing-the-machinery.md#traps) say, rather than fixing it or leaving a file out.
8. **Finish.** Input: the outputs above. End as [procedure endings](procedure-endings.md) says: the question-log entry and its commit, the push, and the report. By exception to its push table's rows for pages, a branch from step 5 is pushed as a branch, as [the trap](changing-the-machinery.md#traps) says, never to main; who pushes it follows that table's row for machinery. The report names the page, its rows, its route in, its wrapper, every row queued for the next eval run, and a branch waiting for its eval run.

Stop when the report is given. Every stop in steps 3, 6 and 7 ends in that report, with what was left uncommitted and why.

## After the page lands

Once the page is committed, its upkeep, such as its review date and the rows that point at it, is on [maintain the workspace](maintain-the-workspace.md).

## Rules

| Rule | Enforced by |
|---|---|
| A procedure that overlaps a page already here goes into that page as a section, with its own proof line. | `prose` |
| A new playbook is written only after a run without it shows the model failing at the task, unless an approved plan names it; then it ships unproven with its `prove-by`. | `prose` |
| A playbook or how-to carries `proof`, and an unproven one names `prove-by`. | `page_kinds#a playbook without proof fails`, `proof#an unproven page with no prove-by fails` |
| A new page's `prove-by` is never a milestone being built. | `proof#a new page whose prove-by is a milestone being built fails` |
| A page opens with its title, a purpose sentence of 25 words or fewer, then its **In short** line. | `page_kinds#an In short line before the purpose is out of order`, `page_kinds#a purpose sentence over 25 words fails` |
| A decision record is written only when the three conditions hold and the person says yes; an approved plan that asks for one is that yes. | `prose` |
| Machinery not built yet is named as planned, with its milestone, and never written as a step to run. | `prose` |
| Every must and never on a page has a row in its rules table, with a true tag. | `prose` |
| A rules-table tag names a part the manifest uses. | `rules#a part not in the manifest fails` |
| A page's catalog or index row, and its route in, land in the same commit as the page. | `prose` |
| A core playbook or how-to lands with its wrapper and two selection cases, one that should fire it and one that should leave it quiet, unless the `wrappers` entry's waiting list names it; a lane draft gets none. | `wrappers#a core procedure with no wrapper fails`, `wrappers#a wrapper missing a selection case fails`, `wrappers#a lane draft with a wrapper fails` |
| The README's table names each playbook, how-to and procedure section with the state its proof mark gives. | `proof#a README row that disagrees with the page fails` |
| A change to a file the eval covers, such as a row in INDEX.md or a line in AGENTS.md, waits for a new eval run on record. | `eval_record#so does an edit to the contract the guided arm is given` |
| A change to a file the eval covers is queued by default; when a check or an approved plan needs it now, it goes on a branch that is not merged until the eval run is on record. | `prose` |
| A page never points a reader at an agent's private memory, a session's scratch folder, or any file only one machine holds; the fact is written on the page instead. | `prose` |
| A rule page holds only facts that hold for every edit its pattern matches. | `prose` |
| A finding the workspace should have told you is written only on the person's yes to the research ladder's offer. | `prose` |
| The commit that adds the page names its instruction review. | `review_trailer#a guidance page changed with no trailer fails` |
| The procedure ends as [procedure endings](procedure-endings.md) says, which holds the staging and report rules. | `edit_ledger#a path the ledger does not hold fails, whatever staged it`, `eval:fix-a-bug` |
| A branch from step 5 is pushed as a branch, never to main, until its eval run is on record. | `prose` |
