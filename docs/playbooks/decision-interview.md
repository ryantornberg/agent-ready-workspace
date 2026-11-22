---
kind: playbook
proof: unproven
prove-by: M9
last-reviewed: 2026-11-21
---

# Decision interview

How an agent settles the open design questions of a piece of work with a person, before a plan or code. For the agent running the interview.

**In short:** split a large topic first, then ask one question at a time, each with a recommended answer and its reason. Answer from the code where it can, sharpen terms in the glossary as they come up, and end with a dated summary in the draft hand-off plan.

## When to use it

It is the Grill rung of [size the work](../size-the-work.md#the-ladder): use it when a change has failed the size gate, its goal and non-goals are written, and design questions are still open. Use it too when a person asks to be interviewed on a topic.

Skip it when the code, the docs or the request already settle every question, as a bug report with a clear cause does. If the gate passes, the change goes to [fix a bug](fix-a-bug.md) instead, with no interview.

Run it in the session the person talks to: it is a conversation, so it is never handed to a helper. Wide reading during it may be delegated, as [orchestration](../orchestration.md#delegating) says.

## Steps

1. **Check the scope.** Input: the topic, and the goal and non-goals from the draft hand-off plan in `docs/plans/`, if there is one. If the topic holds parts that could each ship on their own, list them as sub-topics. Recommend the one the others depend on to go first, and ask the person to confirm the order; without an answer, use yours. Output: one sub-topic to interview now, and the others listed for later interviews. By default, a topic with one deliverable is one sub-topic.
2. **Load what is already decided.** Input: the sub-topic. Read the [glossary](../glossary.md), [INDEX.md's search aliases](../../INDEX.md#search-aliases), and every record in [docs/decisions/](../decisions/) whose title touches the sub-topic. Output: the words already defined and the decisions already made. Never reopen a recorded decision unless the person asks to; a question that would undo one is put to the person as exactly that.
3. **List the open questions.** Input: the sub-topic and step 2's output. Write every design question the work must settle, then order them so a question comes after the ones its answer depends on. Output: the ordered list. It is a working list, not a script: an answer may add, remove or reorder questions.
4. **Answer from the code first.** Input: the next question on the list. If the code or the docs can answer it, look it up with the one lookup that fits, as the [research ladder](../research-ladder.md) says, such as `python3 tools/symbols.py NAME src`. State the answer and the file it came from, without asking, and repeat this step for the next question. Output: the first question still open. When none is left, go to step 9. Ask the person only what the code cannot say: intent, priority, and what users need.
5. **If the answer must be seen, prototype it.** Input: an open question that reading cannot settle, such as how a screen should look. Run the [throwaway prototype](throwaway-prototype.md), then put the question to the person with what the prototype showed. Output: the question, ready to ask with evidence. By default, a question about behavior that reading can trace is not one of these: skip this step and go to step 6.
6. **Ask one question.** Input: one open question. Ask only that question. Give your recommended answer and the reason for it, so the person can accept it with a word. Output: the person's answer. If the person cannot answer it, note it as open, with who can answer it. Note the questions that depend on it as open too, and go back to step 4 for the next question.
7. **Sharpen the terms.** Input: the answer, and any word in it that is vague or used two ways. Propose one meaning and ask the person to confirm it. On a yes, write it at once, as "Where a term goes" below says. Output: the word defined, or the question of its meaning listed as open.
8. **Offer a decision record.** Input: a decision just made. Offer a record only when all three conditions under "When a decision gets a record" hold. Write it only on a yes. Output: a record with `status: proposed`, or nothing. Then go back to step 4 for the next question on the list; when none is left, go to step 9.
9. **End the interview** when every question on the list is answered or listed as open, or when the person stops it. Write the summary below. Output: the summary, written where "The summary" says.
10. **Finish.** Input: the summary, and the glossary rows and decision records you wrote. If you wrote any, run the [instruction review](instruction-review.md) on them, as its steps say, and commit them with the plan, staged by name, naming the review's record in the trailer. With none, commit the plan alone. Log any question you had to ask a person that the workspace should have answered, as "The question log" below says, and commit it as [the log's page](../question-log.md) says. Report the summary's next step and any row that waits for an eval run, with each claim marked verified or inferred, as the contract says. Output: the commit and the report. Stop.

## Where a term goes

| The term | Where it goes |
|---|---|
| An everyday word for a thing the code already names, such as "a hold" for `AccountFreeze` | A row in [INDEX.md's search aliases](../../INDEX.md#search-aliases). INDEX.md is covered by the eval, and an edit to it needs a new eval run, which costs real agent time. So do not write the row now. List it under the summary's doc changes as `waits for an eval run`, and name it in your report, so the person decides when to run the eval with it. |
| Any other word the work uses in its own sense | A row in the [glossary](../glossary.md), written as soon as the person confirms it. |

The glossary is a guidance page. So the commit that carries a new row needs an [instruction review](instruction-review.md) and names its record in an `Instructions-review:` trailer. List each row under the summary's doc changes; step 10 runs one review on all of them together, after the interview.

## When a decision gets a record

Offer a [decision record](../decisions/) only when all three hold:

1. **It is hard to reverse.** Undoing it later costs a migration, a release or rework across repositories.
2. **It would surprise a newcomer.** Someone reading the code without the context would ask why it was done this way.
3. **It was a real trade-off.** At least one other option was workable, and the choice gave something up.

Fewer than three, and the decision lives in the summary only. A record takes the next free number in `docs/decisions/`, follows the shape of the newest record there, and starts at `status: proposed` until the person accepts it. It is a guidance page, so its commit needs an instruction review, like a glossary row.

## The summary

The interview produces one dated summary with four parts:

| Part | Holds |
|---|---|
| Decisions | Each decision, in the person's words, and the decision record, if one was written. |
| Open questions | Each question nobody answered, with who can answer it and what it blocks. |
| Doc changes | Each glossary row, alias row and decision record written or queued, and whether its instruction review has run. |
| Next step | One recommendation. By default, writing the spec from these decisions, as [the spec process](../size-the-work.md#the-spec-process) says. Otherwise a throwaway prototype, more interviews for the sub-topics left, or [fix a bug](fix-a-bug.md) if the answers show the change now passes the gate. |

Write it in the draft hand-off plan for the work, in two places, since "Settled decisions" holds only what is settled. The decisions go under "Settled decisions", as a subsection headed `### Interview, YYYY-MM-DD`. The open questions, doc changes and next step go in a section of their own after it, headed `## Interview, YYYY-MM-DD: open`. The spec is written from the decisions afterwards, in the plan's own sections, as [the spec process](../size-the-work.md#where-it-lives) says. If no plan exists yet, copy the [hand-off plan template](../templates/hand-off-plan.md) into `docs/plans/<name>.md` first, with `status: draft`. If the plan is already approved, its sections are frozen: write the summary as a dated entry under "Changes after approval" instead, and ask the person for its approval line.

## The question log

Design questions are what the interview is for; they are not workspace failures. But a question of fact that you had to ask the person, and that the workspace should have answered, goes in the [question log](../question-log.md) before you finish, as the contract says. An example is which service is the live one. An open question that nobody answered is not logged there: it stays in the summary.

## Rules

| Rule | Enforced by |
|---|---|
| The interview runs in the session the person talks to; it is never handed to a helper. | `prose` |
| Ask one question at a time, each with a recommended answer and its reason. | `prose` |
| Never ask the person what the code or the docs can answer. | `prose` |
| Never reopen a recorded decision unless the person asks to. | `prose` |
| Offer a decision record only when all three conditions hold, and write it only on a yes. | `prose` |
| A glossary row or decision record is committed with an instruction review. | `review_trailer#a guidance page changed with no trailer fails` |
| The interview ends with a dated summary in the work's hand-off plan, its decisions under "Settled decisions" and its open questions outside it. | `prose` |
| The glossary rows and decision records it wrote are reviewed and committed before it stops. | `prose` |
| A question of fact the workspace should have answered goes in the question log before you finish. | `prose` |
