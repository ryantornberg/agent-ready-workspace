---
kind: playbook
proof: unproven
prove-by: M6
last-reviewed: 2026-11-21
---

# Architecture review

How a fresh reviewer checks a code change against what this system has already decided. For the agent that asks for the review and the reviewer.

**In short:** a fresh driver-tier reviewer gets the diff, the request and the plan. It answers each numbered invariant below, reads the decision records the diff touches, then steps back and asks whether the change solves the right problem. It reports findings that trace to an invariant or a decision record, and ends with two fixed lines.

## When it runs

It fits a diff of code: a branch or a pull request that changes files under `src/` or the [machinery](../changing-the-machinery.md#what-counts-as-machinery). It runs whether or not the diff looks architectural, because a one-file patch is the usual shape of a fix for a symptom.

- It runs as one dimension of a full review, which the [review orchestrator](review-orchestrator.md) runs, by hand until its machinery lands in M4. There the dispatched reviewer does step 4 only, and replies in the table that page's template gives, with the "Traces to" value at the start of each Finding cell, then the two closing lines below, then the `Dimension complete: <dimension>` line that template ends with. The orchestrator and the author do the rest, as that page says.
- The steps below, in full, are for a request for an architecture review alone, of a branch or pull request.
- When the change is a hand-off plan or a requirements document, not a diff, use [red team review](red-team-review.md) instead.
- When the diff changes guidance pages, those pages go to the [instruction review](instruction-review.md); this review takes the code in the same diff.
- When a finding is about how the code is written, not about what the system has decided, it is not this review's. Leave it to the code dimension of the review, which [code review](../code-review.md) explains.
- When a finding is about code that already exists for the job, it belongs to the [reuse checklist](reuse-checklist.md).

## Steps

1. **Check that it fits.** Input: the request and the change. Confirm the change is a diff of code, as "When it runs" says. Default: a diff that mixes code and guidance pages is reviewed here for its code only. Find the tip and the base as step 1 of the [review orchestrator](review-orchestrator.md#steps) does, which fetches a pull request's head. Output: the tip and base commits; the request, word for word, from the sources step 5 of the review orchestrator names, with its default: the plan's spec, the issue, the pull request's description, and, with none of them, the commit messages, saying so; and the plan's path under `docs/plans/`, or none. If the change does not fit, stop and report which playbook fits instead. Nothing is committed.
2. **Decide who reviews.** Input: what this session has done. If this session wrote or edited the change, or holds the author's reasoning, a fresh agent reviews: go to step 3. If it has done neither, and it runs at the driver tier's model and effort in the `tiers` entry of [workspace.json](../../workspace.json), this session is the reviewer: do step 4 yourself, then go to step 6. Default, when unsure: dispatch.
3. **Dispatch the reviewer.** Input: [the template](#the-template), with its placeholders filled from step 1's output. Change nothing else, and add nothing: never your reasoning or what you expect it to find, as [fresh context for critics](../orchestration.md#fresh-context-for-critics) says. Send it to one fresh agent at the driver tier's model and effort. Output: the dispatch.
4. **Review.** This step is the reviewer's. Input: the diff, the request, the plan and this page. Read the diff with `git diff BASE..TIP`, and a file at the tip with `git show TIP:PATH`, so no working copy changes. When the review orchestrator dispatched you, read the folder its template names instead. Edit nothing and post nothing.
   - For each entry in [the invariants](#the-invariants), say whether the diff touches it and, if it does, whether it still holds.
   - List the accepted records in [docs/decisions/](../decisions/) with `grep -l "status: accepted" docs/decisions/*.md`. Read each one whose decision the diff touches, and check that the diff keeps it.
   - Run [the big-picture pass](#the-big-picture-pass).
   - Write a finding only when it traces to an invariant, an accepted decision record, or the big-picture pass's symptom rule. Anything else goes to the code dimension, as "When it runs" says.
   - Output: the reply in the shape under [the reply](#the-reply). "No architectural surface" is a valid answer: the findings table says `No findings.` and the two closing lines still follow.
5. **Read the reply.** Input: the reviewer's reply. Check that it ends with both closing lines. If either is missing, dispatch one more fresh reviewer with the same template. If the second reply also lacks one, stop: report to the person that the review did not complete, with both replies. Nothing is committed. Output: the findings and the two lines.
6. **Hand on, if the change is not yours.** Input: the reply, when this session did not write the change, such as a review of someone else's pull request. Report the findings to the person who asked, and stop. Posting them on a pull request is an outward write: do it only on that person's yes, and only where the [review orchestrator's](review-orchestrator.md#steps) step 11 allows a post, on a pull request in this repository or one pinned under `src/`. On any other, give the person the findings to post. Default: do not post. Nothing is committed.
7. **Settle each finding.** Input: the findings, when the change is yours. Verify each one yourself, by reading or running what its evidence cites. Then give it one disposition: `fixed`, with the fix made by the procedure the change follows, such as [test first](test-first.md) for a slice of a plan; `deferred to <where>`, with the reason; or `declined`, with a reason a stranger could judge. A finding against an invariant marked non-declinable is never declined. The alternative line is a proposal for whoever owns the request, never a defect: put it to the person, and without an answer leave it open for that person. Output: a disposition for every finding.
8. **Decide on another round.** Input: the dispositions. If a fix changed the design of the diff, such as a new path, a moved responsibility or a changed answer to an invariant, go back to step 3 with the new diff. A fix that adds a test or rewords code is not that. Default: no new round. The loop stops as [the limits](../orchestration.md#limits) say. Output: a diff whose last review needs no change in design.
9. **Record and report.** Input: the last reply and the dispositions. When the work has a plan, write the findings, their dispositions and the two closing lines under the plan's "Results", stage the plan by name and commit it. When it has none, they go in your report, and the review itself commits nothing; the fixes were committed by the procedure that made them. The fix record that will hold them for a bug fix is planned in slice B3 of M3. Report the two closing lines and the count of findings per disposition, each claim marked verified or inferred. Stop.

Stop when the report is written. Stop early and report when the change does not fit, when two reviewers in a row miss a closing line, or when the change is not yours.

## The template

Send this, with only the angle-bracket placeholders replaced. For `<plan>`, write `none` when there is no plan.

```text
Tier: driver

Run an architecture review: follow step 4 of docs/playbooks/architecture-review.md, then stop.
The change: git diff <base commit>..<tip commit>
The request, word for word: <request>
The plan: <plan>
Edit nothing and post nothing.
Reply in the shape under "The reply" on that page.
```

## The invariants

What this system has already decided, numbered. A finding cites an entry by its number. Numbers are never reused: a retired entry stays, struck through, with the date and the reason.

| # | Invariant | Source | Non-declinable |
|---|---|---|---|
| 1 | `src/orders-service-v1` never changes. It is the shelved service, kept read-only for audits; a change in behavior lands in `src/orders-api`. | [AGENTS.md](../../AGENTS.md#facts-a-model-cannot-derive) | Yes |

This sample's list starts with one entry. A team adopting this workspace writes its own, one line per decision the system already rests on, each with its source.

The list grows when a defect escapes that an entry would have caught. [Escape analysis](escape-analysis.md) is where such a miss is traced. Adding an entry is a change to this page, so it gets an [instruction review](instruction-review.md).

A non-declinable entry is one no author or agent may decline. Only a person can retire it, by changing its source first.

## The big-picture pass

Proof: unproven, prove-by M6.

A reviewer handed a diff reviews the diff. A diff can keep every invariant and still answer the wrong question. So after the invariants, the reviewer steps back and asks whether the problem is framed right, and whether a much simpler design meets it.

1. **Trace the change past the diff.** Follow what the changed code does in the running system: its callers, found with `python3 tools/symbols.py NAME src` and `git grep -n NAME`, and the paths [INDEX.md's cross-cutting chains](../../INDEX.md#cross-cutting-chains) name for this kind of change.
2. **Restate the problem in one sentence,** in your own words, apart from how the request frames it. Then test the sentence. Is this the defect, or a symptom of it? Is it one instance of a class? Would it look different from another seat, such as a caller, the person using the screen, or the team that runs the service? Does it match a misframing in the table below?
3. **Read the rejected options.** They are the plan's "Settled decisions" and the "Rejected" sections of the decision records the plan cites. Do not propose one again without a new reason.
4. **Try removals first.** Could the thing the change guards against be removed, or narrowed, instead of guarded?
5. **Look past the repository.** Could a layer the diff does not touch do the job for every caller at once, even one another team owns? For example, a check added in `src/orders-web` that `src/orders-api` could make for every client. When several callers share one cause, weigh fixing it where they meet before adding shared code.
6. **Name at most one alternative,** and only a concrete one: what changes, what it removes, what it costs, and what the user sees. `none` is a valid answer, and the usual one for a small diff, with a one-line reason.

A fix for a symptom, shown by reading the code, with the cause still reachable on a path the request covers, is a finding. It traces to the restated problem, the one finding that needs no invariant. A suspicion that the code cannot show goes in the alternative line instead.

| Misframing | The question that exposes it |
|---|---|
| Wrong layer | Would the fix hold for every caller, or only for the one that reported it? |
| Wrong store | Does the data live where its owner and its lifetime say it should, or in a second place that drifts? |
| Known pattern rebuilt | Does the framework, the language or this code already have this mechanism, such as a retry, a queue or a cache? |
| Lifecycle patched | Is the fix a guard against a state that should never exist? Would changing when the thing is created, started or ended remove the need? |
| Data treated as code | Is a list of values, such as statuses or rates, written into branches, so changing the data needs a release? |
| Configuration treated as code | Does a value that differs per environment, or changes without a release, live in the code? |
| Not this team's call | Does the right fix belong to another team's system, or to a person's decision, so this change works around it? |

The table teaches misframings in general. Never add the answer to a past case to it: a reviewer anchored on one answer stops looking.

## The reply

The reviewer replies with a findings table, then the two closing lines, and nothing else, except when the review orchestrator dispatched it: then its template's `Dimension complete:` line follows them.

```text
| # | Traces to | Finding | Evidence |
|---|---|---|---|
| 1 | Invariant 1 | <what fails, and where> | <what you read or ran, marked verified or inferred> |

Invariants checked: <each number, with "not touched", "holds" or "fails, finding <n>">; decision records read: <their numbers, or none>
Big picture: <the problem in one sentence>. Alternative: <one concrete alternative, or none, with a one-line reason>
```

"Traces to" holds an invariant's number, a decision record's number, or `restated problem`. When the review orchestrator dispatched the review, its template's table replaces this one, as "When it runs" says. With no findings, the table keeps its header and the line `No findings.` follows it. The review is complete only with both closing lines; either alone does not complete it.

## Rules

| Rule | Enforced by |
|---|---|
| The reviewer is a driver-tier session that did not write or edit the change. A dispatched reviewer gets the template with nothing added, never the author's reasoning. | `prose` |
| The dispatch's first line names its tier. | `handoff_tier#no tier named` |
| A finding traces to an invariant, an accepted decision record, or the restated problem; anything else goes to the code dimension. | `prose` |
| The reviewer edits nothing and posts nothing. | `prose` |
| Never post findings on someone else's pull request without the person's yes, and never on one outside this repository and the repositories it pins. | `prose` |
| The big-picture pass runs on every review, even when the diff has no architectural surface. | `prose` |
| Name at most one alternative, and only a concrete one; it is a proposal, never a defect. | `prose` |
| The review is complete only when the reply holds both closing lines. | `prose` |
| A finding against a non-declinable invariant is never declined, and only a person retires such an invariant. | `prose` |
| An invariant's number is never reused. | `prose` |
| Never propose a rejected option again without a new reason. | `prose` |
| Never change `src/orders-service-v1`. | `shelved#an edit inside the shelved folder` |
| A declined finding carries a reason a stranger could judge. | `prose` |
| Never add the answer to a past case to the misframing table. | `prose` |
