---
kind: how-to
proof: unproven
prove-by: M4
last-reviewed: 2026-11-21
---

# Orchestration: tiers, models and delegation

Which model and effort a piece of work gets, and how work is handed to a helper session. It is for any agent that plans work, delegates it or writes a hand-off plan, and for the person who approves the plan.

**In short:** every task belongs to one of three tiers. One entry in the manifest binds each tier to a model and an effort level. Stakes raise the tier. Every handoff names its tier, and a helper returns conclusions, not files.

## The three tiers

| Tier | Does | For example |
|---|---|---|
| Driver | Judgment: design, review, deciding what to do next | Writing a hand-off plan; red-teaming a plan that changes a gate |
| Worker | Bounded work against a written plan | Building one slice of pages; a fix round on a page; rewriting a page after its review |
| Mechanical | Reading, listing and sweeping | Finding every caller of a function; collecting check output |

Pick the cheapest tier that fits. Lower the effort before you lower the model.

## The binding

The `tiers` entry in [workspace.json](../workspace.json) maps each tier to a model and an effort level. It is the only place a model name appears, so a model change is one edit. Read the current values there.

Driver and worker may share a model and differ by effort. The tier name in the handoff is what tells them apart.

The person chooses the model of the session they talk to. The binding governs everything that session hands off.

## Stakes raise the tier

A task runs at the driver tier, whatever its size, when it:

- changes a gate: a check, a hook, a grader, CI or the commit hook;
- changes any other machinery path, as [changing the machinery](changing-the-machinery.md#what-counts-as-machinery) lists, tests included;
- changes the contract, [AGENTS.md](../AGENTS.md);
- produces text that someone outside the team will read, such as an upstream pull request.

Work *about* such a change is not stakes. Listing the callers of a hook is still mechanical.

## Delegating

Proof: unproven, prove-by M4.

Delegating saves context, not tokens. A helper reads widely so the main session does not have to. The bill drops only when the helper runs on a cheaper tier or at lower effort.

Delegate when the reading is wide and the answer is short. Keep the work when it is small or bound up with what you are editing.

| The work | Delegate? |
|---|---|
| Reading several files you will not edit, to answer one question | Yes, at the mechanical tier. |
| A sweep: every caller of a function, every use of a name, collecting check output | Yes, at the mechanical tier. |
| Several questions that do not depend on each other | Yes, one helper each, run in parallel. |
| A review or red team the plan or a playbook calls for | Yes, to a fresh session, as [fresh context for critics](#fresh-context-for-critics) says. |
| A slice of an approved plan | Yes, at the tier the plan names. |
| An exact name or a known file | No. Look it up yourself, as the [research ladder](research-ladder.md) says. |
| A handful of tool calls | No. It is cheaper done than delegated. |
| Work tightly bound to the change you are making | No. |
| Checking your own work before you report it | No. See below. |

- **One helper per job.** Do not chain helpers on tightly coupled work, and do not redo work a helper returned.
- **Name the shape of the return.** Say what comes back and how long it may be: a table of file, line and finding, a yes or no with its evidence, or a list of at most ten items. Ask for each claim marked verified or inferred, so you know which ones to check.
- **Write down what must outlive the session.** A helper's report reaches only you, and it ends with the session. Before you finish, put each finding that matters in the record your task names, such as the plan's results or a fix record. A finding that belongs on a guidance page goes through the [research ladder's offer](research-ladder.md#offer-to-write-a-finding-down), and is written there only on a yes.
- **Checking your own work stays in the main session.** When you decide to verify something, such as running the tests or reading a changed caller, do it yourself. A helper's check comes back as a claim, not as a result you saw. A review the plan or a playbook calls for is different: it goes to a fresh session.

## Handing work off

- **Every handoff names its tier.** A hand-off plan names one per slice. A delegated task starts its prompt with `Tier: driver`, `Tier: worker` or `Tier: mechanical`, and sets the model and effort from the binding.
- **A delegated task carries** one tight question, the [shape of the answer](#delegating), and what is already ruled out.
- **A helper returns conclusions**: file, line and finding. It never returns whole files.

## Fresh context for critics

A reviewer or a red team never shares the author's session. It gets the artifact and the sources, never the author's conclusions. A critic who is handed the author's reasoning tends to confirm it.

## Limits

- **An attended review loop** runs while it converges. It ends on a round that only finishes earlier work. It has no fixed round count.
- **An unattended run** stops after the fix rounds its plan allows, and after three when the plan sets no limit. It then freezes and reports; nothing is published or merged.

## What enforces this

| Rule | Enforced by |
|---|---|
| A delegated task's prompt starts with its tier. | `handoff_tier#no tier named` |
| A delegated task runs at its tier's model and effort, as the binding sets them. | `handoff_tier#a model off the binding`, `handoff_tier#an effort off the binding` |
| A slice that changes a gate, any other machinery path, the contract or text an outsider reads runs at the driver tier. | `prose` |
| One helper per job: never chain helpers on tightly coupled work, and never redo work a helper returned. | `prose` |
| Checking your own work stays in the main session; it is never delegated. | `prose` |
| A reviewer or red team works in a fresh session, without the author's conclusions. | `prose` |
| An unattended run stops after the fix rounds its plan allows, or three when it sets none, then freezes and reports. | `prose` |


The `handoff_tier` hook refuses a delegated task whose prompt does not start with its tier. Where the agent tool lets a task set its model and effort, the hook also refuses a task that sets values other than the binding's for its tier, or leaves one unset, since an unset value inherits the calling session's. A tool that exposes neither setting needs only the tier line. See [parts](parts.md#the-parts-here).

The rest is prose. The person reading a hand-off plan checks that each slice names a tier. Nothing checks that the tier fits the work.
