---
kind: playbook
proof: unproven
prove-by: M6
last-reviewed: 2026-11-21
---

# Escape analysis

How an agent finds why a review missed a defect, and proposes a change to the review rather than the code. For the agent that fixed the defect.

**In short:** once a defect in reviewed code is fixed, find the reviews that covered it and every earlier time someone saw it. Put each miss in one of six classes, each with one owner, and propose a change to that owner that would also have caught another past defect. A change to a template, a gate, a script or a file the eval covers waits for the person's yes.

## When it runs

After the fix for a defect is committed, when a review covered the code that held it. A review covered the defect when the range of commits it read includes the commit that brought the defect in. It runs when:

- you finished a fix, by [fix a bug](fix-a-bug.md) or a larger route, and the faulty code had passed a review;
- a person asks why a review missed a defect.

Which page comes first:

| The situation | Go to |
|---|---|
| The defect is not fixed yet. | Fix it first: [debugging](debugging.md) when its cause is not known, otherwise the route the [size gate](../size-the-work.md#the-gate) gives. Come back once the fix is committed. |
| The fix is committed and the code had a review. | This page. |
| The defect is in a guidance page or a plan, not in code. | Not this page. Its scope is code under `src/` and the machinery paths. Report it to the person. |

This procedure only reads pull requests: it posts no comment and no reply on any of them. A change it proposes may open a pull request of its own, by the route step 7 gives it.

## Where a code review is on record today

The review mark, which will record each reviewed tip, is planned for M4, with the [review orchestrator](review-orchestrator.md)'s machinery. Until then a code review is on record in one of two places:

| Where | Read it with | The commits it covered |
|---|---|---|
| A pull request: its description, its reviews and its comments, including the review orchestrator's overview comment | `gh pr view NUMBER --json baseRefOid,headRefOid,body,reviews,comments`, and its line comments with `gh api "repos/{owner}/{repo}/pulls/NUMBER/comments" --paginate` | From its base to the tip the review names; with no tip named, to its head. |
| A review under a hand-off plan's "Results", such as a `### Review of <tip commit>` heading the review orchestrator writes, or the findings an architecture review or a reuse review writes there | The plan file under `docs/plans/` | The range in the review's `Range: <first>..<tip>` line; a delta round covers only that range. With no such line, the commits that slice's report names. |

## The six classes

Each miss gets exactly one class. Each class has one owner: the page or part a change goes to.

| Class | What happened | Owner |
|---|---|---|
| No remit | No review that ran was asked to look for this kind of defect. | The list of what reviews look for: the dimensions on the [review orchestrator](review-orchestrator.md) page, or, for a design rule, the invariants on [architecture review](architecture-review.md#the-invariants)'s page. |
| Did not look there | The review had the remit but did not read the code that held the defect, such as a caller outside the diff it was handed. | What that review is handed: the dispatch on the page that runs it. |
| Wrongly declined | A reviewer raised it, and the author declined it for a reason that was wrong. | The triage step of the page on which the finding was settled. |
| Deferred then lost | It was deferred, and nobody picked it up from where it went. | Where deferred findings go: the [defect register template](../templates/defect-register.md#when-to-add-a-row), or the page that named another place the finding was deferred to. |
| Closed on an unchecked claim | It was marked fixed on a claim nobody ran. | The step that accepted the claim, on the page whose review closed the finding. |
| Undetectable | No review could have seen it in the code and the diff it had, such as a fault that shows only with real data or real timing. | A test or a check that catches this kind of defect without a reviewer: a test, as [test first](test-first.md) writes one, or a part, as [parts](../parts.md) says. |

A change targets the kind of defect, never this one instance. So it never adds this defect's answer, or a hint on where to look, to a reviewer's template or to [architecture review](architecture-review.md)'s table of misframings: both pages forbid that, because a reviewer anchored on one answer stops looking. A missing invariant is added as a numbered entry, as that page says.

## Steps

1. **Find the commit that brought it in.** Input: the committed fix and its regression test. Find the commit that added the faulty code with `git log -S "TEXT" --reverse --oneline -- PATH`, where TEXT is a piece of the faulty code and PATH its file. Default when several commits carry the fault: the oldest. When it finds none, as for missing code such as an absent guard, run `git blame FIX^ -- PATH`, with FIX the fix commit, and take the newest commit that wrote the lines the fix changed or sits between. Output: the defect commit. If neither finds one, stop and report the fix commit and the two commands' results; nothing is written. If the fix is not committed, stop and report that the defect must be fixed first; nothing is written.
2. **Find the covering reviews.** Input: the defect commit. Find the pull request that merged it with `gh pr list --state merged --search DEFECT`, using the full commit hash. An empty list means the commit reached main with no pull request. Then read each review on record, as the table above says, In the plans, list each review's range with `git grep -n "^Range:" -- docs/plans`, and test each one by the rule below. A review covers the defect when `git merge-base --is-ancestor DEFECT HEAD` succeeds and `git merge-base --is-ancestor DEFECT BASE` fails, with HEAD and BASE the commits the review read to and from. Output: the covering reviews, each with where it is recorded. If none covers it, the code merged with no review on record: stop, and report the defect commit, its pull request and that finding. Nothing is written.
3. **Find every earlier sighting.** Input: the defect's symptom in a few words, the names in the fix, and the covering reviews. Search where findings are written down: `git grep -n -i "WORDS" -- docs/records docs/plans docs/milestones docs/question-log.md`, `git log -i --grep="WORDS" --oneline`, and the description and comments of each covering pull request, read as the table above says. Look first in the [defect register](../records/defects.md), in both its tables. Default when the symptom words find nothing: search again with the names in the fix. Output: each sighting, with its place, its date and what became of it: never raised, declined, deferred or marked fixed.
4. **Classify each miss.** Input: the covering reviews and the sightings. Each covering review that did not raise the defect is one miss. Each sighting that did not lead to a fix is one miss. Give each one class from [the table](#the-six-classes). Default when two classes fit: the higher row; use "Undetectable" only when no other row fits. Output: a table of each miss, its class and its evidence.
5. **Propose one change per class.** Input: the classified misses. For each class found, write a proposal in a few lines: the class, its owner, the change, and the evidence. Then apply the category test: name another past defect, from step 3's places or the git log, that the change would also have caught. If you cannot, rewrite the change once so it targets the kind of defect, not this one. Default if it still names none: keep the proposal and mark it "category test not met". Output: the proposals.
6. **Ask the person about templates, gates and scripts.** Input: the proposals. A proposal needs the person's yes when it changes a template: a page under `docs/templates/`, or a reviewer's dispatch template on a review page, such as the [review orchestrator](review-orchestrator.md)'s. It needs one too when it changes a machinery path that [changing the machinery](../changing-the-machinery.md#what-counts-as-machinery) lists, or a file the eval covers, such as AGENTS.md or INDEX.md. Send those to the person, one line each, with your recommendation. Default with no answer: apply none of them, and list each as waiting in the report. Output: each such proposal approved, declined or waiting.
7. **Apply the changes.** Input: the proposals that need no yes, and those the person approved. Apply each by the route the [size gate](../size-the-work.md#the-gate) gives it. A machinery change follows [changing the machinery](../changing-the-machinery.md), and a change to a guidance page gets its [instruction review](instruction-review.md) at the commit. The commit that applies a change also adds its row to the [lessons log](../records/lessons.md), as the [lessons log template](../templates/lessons-log.md#when-to-add-a-row) says. Output: each change committed with its lesson, or stopped where its route stopped it. A change whose route stops follows that route's own stop and report, and is listed in this report as not applied, with the reason.
8. **Record the replay case and the waiting lessons.** Input: the defect, its classes and the changes. An eval case that replays the miss waits for the eval system for procedures, planned for M4. Until then, describe the case in the report: the code at the defect commit, the review's request, and what the review must find. A change not applied adds no lessons-log row now. When it waits on the person's yes or is queued, its line in the report or the queue carries the lesson in one line. The commit that later makes it adds the row. Output: the case description and each waiting lesson.
9. **Write it down and report.** Input: the outputs of steps 1 to 8. When the fix has a [fix record](../templates/fix-record.md), write the analysis in its "Escape analysis" section, before its report. When the fix came from a hand-off plan, append the analysis under that plan's "Results". Commit either as [procedure endings](../procedure-endings.md#the-commit) says. With neither, the report is the only copy, and you say so in it. Report the defect commit, the covering reviews, the sightings, each miss with its class, and each proposal as applied, waiting or declined. Mark each claim verified or inferred.

Stop when the report is written. Stop early, and report, when the fix is not committed (step 1) or no review covered the defect (step 2).

## Rules

| Rule | Enforced by |
|---|---|
| Escape analysis starts only once the fix is committed. | `prose` |
| Each miss gets exactly one class, and "Undetectable" only when no other class fits. | `prose` |
| A proposal never adds a past defect's answer, or a hint, to a reviewer's template or to architecture review's misframing table. | `prose` |
| Every proposal names another past defect it would also have caught, or is marked "category test not met". | `prose` |
| A proposal that changes a template, including a reviewer's dispatch template, a machinery path or a file the eval covers is applied only on the person's yes. | `prose` |
| Never post a comment or a reply on a pull request during this procedure. | `prose` |
| Mark every claim in the report verified or inferred. | `eval:fix-a-bug` |
