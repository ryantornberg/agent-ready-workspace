---
kind: how-to
proof: unproven
prove-by: M9
last-reviewed: 2026-11-21
---

# Size the work first

How much process a change gets, and how to run that process for a feature. It is for the agent deciding how to start, and for the person who will read its plan.

**In short:** a change that is small, easy to reverse, in one repository and under a day of work goes straight to [fix a bug](playbooks/fix-a-bug.md). Everything else climbs a ladder, and stops climbing as soon as the work allows. A feature climbs it in the order the feature ladder gives, with a spec a person agrees to before any plan.

## The gate

A change skips the ladder only when all four hold:

1. **Small.** One screen of diff, give or take.
2. **Easy to reverse.** Reverting the commit undoes it. No data migration, no published release, no message sent.
3. **In one repository.**
4. **Under a day of work.**

If any one fails, or you cannot tell, climb the ladder. A change that turns out bigger than it looked stops and climbs from where it is.

## The ladder

| Rung | What it produces | Here |
|---|---|---|
| Bound | The goal and the non-goals, written before anything is touched. Non-goals stop an agent doing more than was asked. | A section of the hand-off plan |
| Grill | The agent asks the person about the design until the open questions are settled. | [Decision interview](playbooks/decision-interview.md) |
| Spec | What will be true when the work is done. | [The spec process](#the-spec-process) |
| Plan | Slices an agent can run, each with its own checks and tier. | [Hand-off plan template](templates/hand-off-plan.md) |
| Red team | A fresh session attacks the plan. Every finding is triaged. | [Red team review](playbooks/red-team-review.md); the hand-off plan's red team table holds the triage |
| Execute | Run the slices, verify each one, record what happened. | [Definition of done](definition-of-done.md) |

Skip a rung only when its answer is already in hand, from an earlier rung, the code, the docs or the request. A bug report with a clear cause needs no grill. A plan nobody has red-teamed does not get built.

A call that is hard to reverse may also need a decision record: the choice, the options and what it gave up. Offer one only when all three conditions in [when a decision gets a record](playbooks/decision-interview.md#when-a-decision-gets-a-record) hold, and write it only on a yes.

Work that runs for weeks is one milestone. It gets a hand-off plan and, at the end, a [milestone record](templates/milestone-record.md).

## The feature ladder

Proof: unproven, prove-by M9.

How to run the ladder for work that adds or changes behavior of the order system, once the gate has sent it up. A bug whose cause is not known yet goes to [debugging](playbooks/debugging.md) first, and its fix is sized at the gate once the cause is found. A refactor that fails the gate climbs the ladder too, but its slices follow [safe refactor](safe-refactor.md) from its third step, not these steps.

1. **Bound, then interview.** Input: the request. Copy the [hand-off plan template](templates/hand-off-plan.md) into `docs/plans/<name>.md` with `status: draft`, and write its goal and non-goals. While the design has open questions, settle them with the person through the [decision interview](playbooks/decision-interview.md). Default: interview; skip it only when the code, the docs or the request already settle every question the spec needs. When a question can only be settled by seeing it, such as how a screen should feel, run a [throwaway prototype](playbooks/throwaway-prototype.md) first. Output: a spec the person has agreed to, written and recorded as [the spec process](#the-spec-process) says. If the person does not agree, stop and report.
2. **Plan.** Input: the agreed spec. Fill every other section of the hand-off plan, with each slice naming its tier and its "Done when". Have it attacked by a [red team review](playbooks/red-team-review.md), and triage every finding in the plan's red team table, as that page says. Then ask the person to approve it. Output: the plan with `status: approved`. If the person does not approve, stop and report.
3. **Check the outside world before UI work.** Input: the approved plan. For each slice that changes a screen in `src/orders-web`, before writing its code, read what the world outside this repository already settles for that screen. That is the current documentation of the libraries it uses, read live as the [research ladder](research-ladder.md) says, and the platform's conventions for that kind of control, such as accessibility guidance. Default: skip this step when no slice changes a screen. Output: a short note under the plan's "Results" of what you read and what it changes. If it changes what the spec says, go to step 7 before you build.
4. **Build each slice test first.** Input: one slice of the approved plan, run at the tier it names. Follow [test first](playbooks/test-first.md). Output: the slice's change with its suite passing, and its report appended under the plan's "Results". If a step fails, do what the plan's recovery section says; by default, halt and report.
5. **Drive the real app, then review.** Input: the built slices. Start the app on a local environment no other session shares, with a browser set up as [browsers](browsers.md) says, and walk through each success criterion a user would see. Write what you did and saw as verified lines. Where the change has no running app, say so instead. Then commit each built slice that is not committed yet, staged by name, since the review reads commits, not uncommitted edits. Then have the change reviewed by following the [review orchestrator](playbooks/review-orchestrator.md), which sends each review dimension to its own fresh session at the driver tier, never with your reasoning, as [fresh context for critics](orchestration.md#fresh-context-for-critics) says. Its machinery is planned for M4, so until then you follow its steps by hand. Output: each finding fixed, deferred to a named place, or declined, each with its reason under the plan's "Results". A finding that needs a code change sends you back to step 4 for that slice. If the review stops at its pre-pass on a new error or warning, fix it as step 4 does and have the change reviewed again. If a dimension is still not complete after its retry, halt: the review's record is in the plan's "Results", committed, and you report which dimension did not complete; do not go on to step 6.
6. **Close the loop.** Input: the reviewed change. For the impact check the [definition of done](definition-of-done.md) asks for, run [impact analysis](playbooks/impact-analysis.md) on the changed paths and names. Output: its ranked list, naming each caller you looked at and each one you did not. Then finish with the report the definition of done gives.
7. **When reality diverges, update the spec first.** Input: a finding at any step that contradicts the spec, such as a requirement that cannot hold or a non-goal the work must cross. Stop that step. Change the spec as [the spec process](#when-reality-diverges) says, with the person's agreement, and only then change the code. Output: the updated spec, and a return to the step that found the divergence. Default: if the person has not answered, wait; do not build against the old spec.

Stop when the definition of done's report is written. Stop early and report when the person declines the spec or the plan, or when a step fails and the plan's recovery says to halt.

## The spec process

Proof: unproven, prove-by M9.

A spec says what will be true when the work is done, not how to get there. This section says when to write one, where it lives, and how to keep it true.

### When to write a spec

| The work | Spec? |
|---|---|
| Passes [the gate](#the-gate) | No. Go to [fix a bug](playbooks/fix-a-bug.md). |
| A bug whose cause is not known | Not yet. Find the cause with [debugging](playbooks/debugging.md), then put the fix through the gate. |
| Has an open question of feel, such as how a screen should look or behave | Not yet. Answer it with a [throwaway prototype](playbooks/throwaway-prototype.md), then write the spec with its answer. |
| Anything else that climbs the ladder | Yes. |

### Where it lives

The spec is three sections of the hand-off plan: "Goal", "Non-goals" and "Success criteria". The Bound rung writes the first two; the spec adds the criteria. They are written before every other section except "Settled decisions", which holds the interview's decisions and the spec's agreement.

### The four phases

| Phase | Produces | In this workspace | Gate after it |
|---|---|---|---|
| Specify | What will be true at the end | The plan's goal and non-goals, then the decision interview, then the success criteria | The person agrees to the spec. Record it under the plan's "Settled decisions" as `Spec agreed by <name>, <date>.` |
| Plan | How the work will be checked and recovered | The plan's verification, recovery, stop rule and limits | None of its own: the next phase ends at the plan's gate. |
| Slice | Pieces an agent can run | The plan's slices table, each slice with its tier and its "Done when"; then the adversarial review of the finished plan, triaged in its red team table | The person approves the plan: `status: approved` and its approval line. |
| Build | The change | [Test first](playbooks/test-first.md) per slice; each slice's report under "Results" | The [definition of done](definition-of-done.md). |

A person holds two gates: between the spec and the plan, and between the plan and the build. Without an answer, wait. No plan is written on a spec the person has not agreed to, and no slice runs on a plan the person has not approved.

### Writing a requirement

Each success criterion is one requirement, in one of these forms, followed by the command that checks it:

- `When <condition>, <part> <does what>.`
- `While <state>, <part> <does what>.`
- `<Part> never <does what>.`

For example: "While an account is under an `AccountFreeze`, the order service accepts its new orders and ships none of them. Checked by: `<the test command>`."

A criterion that says "works", "fast", "clean", "better" or "should" has no command that can check it. Rewrite it in one of the forms.

### When reality diverges

The spec is updated first, then the code. The plan's `status` carries the spec through its life: `draft` while it is written, `approved` once the person approves the plan, then `done` or `abandoned`.

- **Before the plan is approved:** edit the spec's sections, and ask the person to agree again. Record the new agreement under "Settled decisions".
- **After the plan is approved:** its sections are frozen. Write the change as a dated entry under "Changes after approval", with its `Approved by:` line, as the [hand-off plan template](templates/hand-off-plan.md#how-to-use-it) says. Then change the code.

Whether a spec is kept up to date after the work ships, or frozen as written, is not settled yet; a decision record will settle it.

### Failure modes

| Failure | What it looks like | Instead |
|---|---|---|
| Ceremony | A spec for work that passes the gate. | Go to fix a bug. |
| Guessing | A spec for a bug whose cause is not known. | Debug first. |
| Design in the spec | The spec says how: which class, which table. | Say what will be true; leave the how to the plan. |
| Untestable | A criterion no command can check. | Rewrite it in a requirement form, with its command. |
| Spec after code | The spec describes what was built, not what was asked. | Write it before the plan; it is the record of what was asked. |
| Silent drift | The code moved and the spec did not. | Update the spec first, as above. |
| Skipped gate | A plan written, or a slice run, without the person's yes. | Stop and ask. |

## Rules

| Rule | Enforced by |
|---|---|
| A change skips the ladder only when all four conditions of the gate hold. | `prose` |
| A plan nobody has red-teamed does not get built. | `prose` |
| A decision record is offered only when the decision interview's three conditions hold, and written only on a yes. | `prose` |
| No plan is written on a spec the person has not agreed to, and no slice runs on a plan the person has not approved. | `prose` |
| When reality diverges from the spec, the spec is updated first, then the code. | `prose` |
| Every success criterion names the command that checks it. | `prose` |
| A review of a feature runs in a fresh session, without the author's reasoning. | `prose` |
