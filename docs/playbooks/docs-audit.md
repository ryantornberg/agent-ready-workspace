---
kind: playbook
proof: unproven
prove-by: M10
last-reviewed: 2026-11-22
---

# Docs audit

How an agent audits the whole `docs/` tree for drift between pages, and reports a ranked cleanup list. For the maintainer, or an agent the maintainer asks.

**In short:** run every check, then do the judgment pass no check covers, for drift between pages. Rank what you found by category and report it. The audit fixes nothing and edits no page; the most it adds is a question-log entry. The maintainer decides what gets fixed.

## When it runs

Until M10 schedules the docs audit, a person runs it by hand once per milestone, before the milestone's record is signed off, and whenever the [maintain page's event list](../maintain-the-workspace.md#duties-an-event-sets-off) says so. The owner is the workspace's maintainer: the person named as approver in the current plan. A person may also ask for one at any time.

| The situation | Go to |
|---|---|
| A commit changes some guidance pages, and they need reading before it lands | The [instruction review](instruction-review.md). It reads the pages one commit changes, at that commit. |
| The whole `docs/` tree needs reading for drift between pages, on the cadence above or on request | This page. |
| A page is known to be wrong and the fix is clear | No audit. Size the fix at the [size gate](../size-the-work.md#the-gate). |

The audit, helpers included, edits no page or code, fixes no finding and writes no record of its own. The report is its output. The one thing it may add is a question-log entry: if you had to ask a person something this workspace should have answered, add it to the [question log](../question-log.md) before you finish, committed as that page says.

## Steps

1. **Fix the scope.** Input: the request, or the cadence that called the audit. Default: the whole guidance set, which is every page under `docs/` plus `AGENTS.md`, `INDEX.md` and the README, leaving out plans, milestone records and records. Run `git rev-parse --short HEAD` and note the commit you audit. The checks, `git grep` and the shell loops read pages as they are on disk, and `git grep` skips untracked files. Default: audit a working copy with no changes. If `git status --short -- docs AGENTS.md INDEX.md README.md` lists any, audit anyway and name each in the report. A changed page was read as changed, and an untracked one may be missed. Output: the scope, the commit and any changed pages.
2. **Run the checks.** Input: the scope. Run `python3 ws.py check` and `python3 ws.py check --phase ci`. Each prints its findings, and the first also lists every page past its review date as a warning. Then run `python3 ws.py rules`, which lists every rule with its page and tag, and ends with a count per kind of tag. You may hand these three commands to a helper at the mechanical tier, as [orchestration](../orchestration.md#handing-work-off) says, asking for the output unchanged. A failing check is a finding, not a stop. If a command cannot run at all, such as a manifest the runner refuses, go to step 5 and report that, with its message. Output: the check findings, the stale pages and the rules list.
3. **Do the judgment pass.** Input: the scope and the rules list. The checks prove that nothing is dangling, not that pages agree. Do this pass yourself; never hand it off. Work through the five items of [the judgment pass](#the-judgment-pass) below, and write down each finding with its pages and evidence. Output: the judgment findings. Default: when an item finds nothing, record what you checked.
4. **Rank the findings.** Input: the findings of steps 2 and 3. Put each in one category from [the categories](#the-categories), and order the categories as that table does. Within a category, put first the pages more sessions load: the contract and the index, then the catalog and the how-to index, then the rest. Output: the ranked cleanup list.
5. **Report.** Input: the ranked list, or the reason the audit stopped. Before you report: if you had to ask a person something this workspace should have answered, add it to the [question log](../question-log.md), and commit it as that page says. Report to the person in the session's reply, with each claim marked verified or inferred, as [the definition of done](../definition-of-done.md#the-report) says. Give the commit you audited, then the list: category, page, finding, evidence and a proposed fix. Then offer the fixes, and wait for the person to choose. A fix the person says yes to is new work, and starts at the [size gate](../size-the-work.md#the-gate). A small fix that changes pages only follows [extend the workspace](../extend-the-workspace.md). A change to scripts, parts, hooks or CI follows [changing the machinery](../changing-the-machinery.md). A finding worth keeping on a page goes through the research ladder's [offer to write a finding down](../research-ladder.md#offer-to-write-a-finding-down). Apart from a question-log entry, the audit wrote nothing, so nothing else is left uncommitted. Stop here.

## The judgment pass

Five items. For each, the command lists candidates; reading the pages decides which are findings.

1. **Headings two pages share.** List each heading that appears more than once, then find its pages with `git grep -n -F 'HEADING' -- docs`. Skip headings every page of a kind carries, such as `## Rules`, `## Steps`, `## When it runs`, and a decision record's sections. A finding is two pages that hold the same content under one heading, where one should link the other.

   ```
   git grep -h -E '^#{2,} ' -- docs ':!docs/plans' ':!docs/milestones' ':!docs/records' | sort | uniq -c | sort -rn | awk '$1>1'
   ```

2. **Rules stated on two pages.** Read the rules list from step 2 for a rule that appears on two pages. A finding is one rule worded in two meanings. The same rule in the same words on two pages is a restatement, a smaller finding.
3. **Pages nothing routes to.** No check catches a missing row. The first command lists playbooks with no row in the [playbook catalog](README.md); the second lists how-tos and reference pages with no row in the [how-to index](../how-tos.md). Each page listed is a finding.

   ```
   for f in docs/playbooks/*.md; do b=$(basename "$f"); [ "$b" = README.md ] || grep -q "($b" docs/playbooks/README.md || echo "$f"; done
   for f in $(git grep -l -E '^kind: (how-to|reference)' -- 'docs/*.md' ':!docs/playbooks' ':!docs/rules' ':!docs/records' ':!docs/how-tos.md'); do grep -q "](${f#docs/}" docs/how-tos.md || echo "$f"; done
   ```

4. **Deferred findings whose time has come.** The command lists every finding an instruction review or a plan put off. For each, check whether the slice or milestone it names is done. A slice is done when its report is under its plan's "Results". A milestone is done when its record under `docs/milestones/` says `status: signed off`. A finding is one put off to work that is done, with nothing showing it was settled. Default for a row that names no slice or milestone, such as "queued for the maintainer": list it as a finding for the maintainer. Leave it out only when a later record, plan entry or commit shows it settled.

   ```
   git grep -n -E '[|] *(deferred to|queued for)' -- docs/records docs/plans
   ```

5. **Gaps the question log holds.** Read the [question log](../question-log.md). A finding is a row whose "Where the answer lives now" cell is empty, or names a page that does not hold the answer.

## The categories

| Category | Means |
|---|---|
| Broken | A check fails. |
| Contradiction | Two pages say things that cannot both hold, such as one rule in two meanings. |
| Overdue | A deferred finding whose time has come, or a page past its review date. |
| Unrouted | A page nothing routes to: no catalog or index row. |
| Restated | Content held on two pages that should be on one, with a link from the other. |
| Gap | A question-log row with no fix. |

## Rules

| Rule | Enforced by |
|---|---|
| The audit changes no line of the pages, code or records it reads, helpers included; the report is its output. | `prose` |
| The session running the audit does the judgment pass itself; only the check output may be handed to a helper. | `prose` |
| The audit runs once per milestone, before its record is signed off, and on the maintain page's events; the maintainer owns it. | `prose` |
| A defect the audit finds is reported, and fixed only on the person's yes, as new work that starts at the size gate. | `prose` |
| Mark every claim in the report verified or inferred. | `eval:fix-a-bug` |
| If you had to ask a person something this workspace should have answered, add it to the question log before you finish, and commit it staged by name. | `prose` |
