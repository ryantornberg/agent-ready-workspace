---
kind: playbook
proof: unproven
prove-by: M6
last-reviewed: 2026-11-21
---

# Reuse checklist

How to find code that already does the job before writing new logic, and how a reviewer checks that it was looked for. For authors and reviewers.

**In short:** before new logic, the author searches for an existing helper, repeated logic and the pattern a rule page, decision record or plan prescribes, and writes one line saying where it searched and what it found. The reviewer runs the same searches on the diff and checks four debt patterns. Debt findings are always the person's decision.

## When it runs

- **The author's half** runs before you write new logic in code under `src/`: a new function, class, branch or literal. [Test first](test-first.md) sends you here from its first step. A one-line change that adds no logic skips it.
- **The reviewer's half** runs as one dimension of a full review, and it is advisory: its findings never hold a change back on their own. The [review orchestrator](review-orchestrator.md) runs that review, by hand until its machinery lands in M4. There the dispatched reviewer does steps 2 to 4 of the reviewer's steps, replies in the table that page's template gives, with the pattern at the start of each Finding cell, then the closing line. It never labels a finding `blocker`, and labels every debt finding `decision`. The orchestrator and the author do the rest, as that page says. The reviewer's steps in full are for a request for a reuse review alone.
- A finding that the change breaks a decision the system rests on is not this checklist's. It belongs to [architecture review](architecture-review.md).
- Extracting duplicates that already exist is a refactor, and a change of its own. Write it down and leave it alone in this change; when someone takes it up, it follows [safe refactor](../safe-refactor.md).

Test code is exempt from extraction: repeated setup in tests is not a finding.

## Where to search

The rows run from cheapest to dearest, as in the [research ladder](../research-ladder.md). Start at the first row, since you always know the kind of change you are about to make. Move down only while a row comes back empty, and stop at the first row that finds code that fits. A claim that nothing fits needs every row run.

| Search | How | Finds |
|---|---|---|
| The paths this kind of change touches | [INDEX.md's cross-cutting chains](../../INDEX.md#cross-cutting-chains) | Where logic of this kind already lives. |
| A name it might already have | `python3 tools/symbols.py --contains PART src`, once per key noun or verb | Definitions whose name holds the word. |
| Its key verbs and literals | `git grep -n "TEXT" -- src`, for the verbs and for any string or number it will use | Code that does the same work under another name, or uses the same value. |
| Sibling files | `git ls-files src/<repository>/<folder>` for the folder you are changing | Helpers that sit next to the code you will change. |
| Code shared across repositories | The interfaces one repository calls in another, such as the order service's API that `src/orders-web` calls, and a shared library where the workspace has one; this sample has none | Logic another repository already owns. |

Code in `src/orders-service-v1` is never a reuse candidate. It is shelved and does not run. When the only match is there, say so in your line.

## The author's steps

1. **Name what you will write.** Input: the behavior you are about to add, from the request or the plan's slice. Write one line on what the new logic does, then list its key nouns, verbs and literals. Output: the line and the list.
2. **Search for it.** Input: the list. Work down [where to search](#where-to-search). Output: the existing code that fits, or every row run and nothing that fits.
3. **Check for repeated logic.** Input: what step 2 found. If the logic you are about to write already exists, call it, or extend it where it stands. Never copy it and change the copy. Default: when extending it would change what its current callers get, write a new function that calls the existing one for what they share, never a copy of its body, and say why in your line. If using the code that fits would need a change in another repository, stop and ask the person, as [fix a bug's "Stop and ask when"](fix-a-bug.md#stop-and-ask-when) says for a fix that needs a change in a second repository. Report what you found; nothing is committed. Output: what you will call, extend or write.
4. **Read the prescribed pattern.** Input: the folder you will change. Read the [rule page](../rules/) whose `applies-to` matches it, each accepted record in [docs/decisions/](../decisions/) that names the area, and the plan's "Settled decisions" when there is a plan. Use the pattern they prescribe. Default: when one of them and an existing helper disagree, the rule page, record or plan wins; say so in your line. Output: the pattern you will follow, or none.
5. **Write the searched line.** Input: steps 2 to 4. Write one line, in this form: `Reuse: searched <the rows you ran>; found <the names, or nothing that fits>; using <what you will call, extend or write>.` When the work has a plan, put it in the slice's report under the plan's "Results"; otherwise put it in your report. Output: the line. Then go back to the procedure that sent you, such as [test first](test-first.md), at its next step.

Stop when the line is written. It is committed with the slice's report, or carried in your report, by the procedure that sent you; this checklist commits nothing of its own.

## The reviewer's steps

1. **Dispatch the reviewer.** Input: the change's tip and base commits, found as step 1 of the [review orchestrator](review-orchestrator.md#steps) finds them, and the author's searched line. When this session wrote the change, send one fresh agent a prompt that starts `Tier: driver`, as [orchestration](../orchestration.md#handing-work-off) requires. It names the diff command, the searched line, and this page's reviewer's steps 2 to 4, and asks for the reply below and no edits. Never add your reasoning. When this session did not write the change, and runs at the driver tier's model and effort in the `tiers` entry of [workspace.json](../../workspace.json), it is the reviewer: go on to step 2 yourself. Default, when unsure: dispatch. Output: the dispatch, or a reviewer at step 2.
2. **Search again.** This step is the reviewer's. Input: the diff, read with `git diff BASE..TIP`, files at the tip read with `git show TIP:PATH`, and the author's line. For each function, class, branch or literal the diff adds outside test code, run the searches in [where to search](#where-to-search). Default: when the author's line is missing, that is a finding of its own, and you search from the first row. Output: each piece of existing code the change could have used, with its path and name.
3. **Check the four debt patterns.** Input: the diff. Check each pattern in [the debt patterns](#the-debt-patterns), and write a finding only with the evidence its row requires. Output: the debt findings.
4. **Reply.** Input: steps 2 and 3. Reply with a table `| # | Pattern | Finding | Evidence |`, where Pattern is `no searched line`, `missed helper`, `repeated logic` or a debt pattern's name, and each piece of evidence is marked verified or inferred. With no findings, the table keeps its header and the line `No findings.` follows it. End with one line: `Reuse: searched <the rows you ran>; <n> findings, <m> of them debt.` When the review orchestrator dispatched you, its template's `Dimension complete:` line follows it. Edit nothing and post nothing. Output: the reply.
5. **Read the reply.** Input: the reply, from the dispatched reviewer or from your own step 4. If it lacks the closing line, dispatch one more fresh reviewer. If the second also lacks it, stop and report to the person that the reuse review did not complete, with both replies; nothing is committed. If this session did not write the change, report the findings to the person who asked, and stop: posting them on a pull request is an outward write, only on that person's yes, and only where the [review orchestrator's](review-orchestrator.md#steps) step 11 allows a post, on a pull request in this repository or one pinned under `src/`. On any other, give the person the findings to post. Output: the findings, when the change is yours.
6. **Settle each finding.** Input: the findings. Verify each one yourself. A missing searched line is `fixed` by the author writing it, as the author's step 5 says. A missed helper or repeated logic is `fixed`, using the existing code; `deferred to <where>`, with the reason; or `declined`, with a reason a stranger could judge. A debt finding is always a decision for the person, never fixed on your own: put it to them with your recommendation. If they decline it, name where the debt now lives, such as an open issue or a line under the plan's "Results". Without an answer, leave it open for that person. Output: a disposition for every finding.
7. **Record and report.** Input: the dispositions. When the work has a plan, write the findings, their dispositions and the closing line under the plan's "Results", stage the plan by name and commit it. When it has none, they go in your report, and nothing is committed for the review. Report the closing line and the count per disposition, each claim marked verified or inferred. Stop.

## The debt patterns

The reviewer checks these. The author need not.

| Pattern | What it looks like | Evidence the finding needs |
|---|---|---|
| Copy and tweak | A new function that repeats an existing one with a small change, instead of extending it. | Both definitions, by path and name, and what differs. |
| Pattern bypassed | New code that goes around the pattern a rule page, decision record or plan prescribes. | The prescription, by page and heading, and the code that skips it. |
| Scattered value | A status string, number or other literal written by hand in several places, with no one named home. | The `git grep -n` that finds it, and its count. [Safe refactor's tokenize-then-swap](../safe-refactor.md#a-worked-pattern-tokenize-then-swap) is the fix, as a change of its own. |
| One-user abstraction | A new interface, base class or option with one caller and no second one planned. | The search that finds its one caller, and the plan or request that names no second. |

## Rules

| Rule | Enforced by |
|---|---|
| Before new logic, the author searches, then writes the searched line. | `prose` |
| Never copy existing logic and change the copy; call it or extend it. | `prose` |
| Code in `src/orders-service-v1` is never a reuse candidate. | `prose` |
| A debt finding needs the evidence its pattern's row requires. | `prose` |
| A debt finding is always the person's decision; a declined one names where the debt now lives. | `prose` |
| The reviewer is a driver-tier session that did not write the change. A dispatched reviewer never gets the author's reasoning. It edits and posts nothing. | `prose` |
| The dispatch's first line names its tier. | `handoff_tier#no tier named` |
| Never post findings on someone else's pull request without the person's yes, and never on one outside this repository and the repositories it pins. | `prose` |
| Test code is exempt from extraction. | `prose` |
| A claim that nothing fits needs every search row run. | `prose` |
| The reviewer's findings are advisory: they never hold a change back on their own. | `prose` |
| Extracting duplicates that already exist is never done in the same change; it is a refactor of its own. | `prose` |
