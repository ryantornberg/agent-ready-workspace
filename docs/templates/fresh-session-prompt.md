---
kind: template
last-reviewed: 2026-11-22
---

# Fresh-session prompt template

The prompt that hands one task to a new session with no history. For the agent asked to write one, and the person who pastes it.

**In short:** a fresh session knows only its prompt and the workspace. The prompt opens with its tier line, then six parts. They are purpose and done, what is settled, the starting commit, claims to check, what the run skips, and the report.

## When to use it

Use it when a person asks for a prompt to paste into a new session, for a task or for one slice of a plan.

| The situation | Use |
|---|---|
| A person starts a new session on a task, or on one slice of a plan. | This template. |
| A session stops mid-task and a later one carries on. | A note, as [handoff](../playbooks/handoff.md) says. Its resume line is the whole prompt. |
| This session hands a helper one question, or a slice of an approved plan. | [Handing work off](../orchestration.md#handing-work-off), as orchestration's delegating table says. |
| A critic reviews a plan or a page. | The template on the critic's own playbook, such as the [adversarial review](../playbooks/adversarial-review.md#the-template). It is kept thin on purpose; do not add these parts to it. |

## Where copies go

A prompt is not saved as a page. Give it to the person in your reply, inside one fenced block, so it can be pasted whole. When the task has a hand-off plan, the prompt links the plan and names the slice; it does not copy the plan.

## Skeleton

```markdown
Tier: <driver, worker or mechanical>

## Purpose and done
<What this session is for, in one or two sentences. Then what is true when it is done, stated so the session can check it, such as a command and what it prints. Link the plan and name the slice, if there is one.>

## Settled
<Decisions already made that the session must not reopen, each in a line, with who made it and when. Write "none" if there are none.>

## Start from a known commit
Working copy: <path>. Branch: <branch>. Starting commit: <the writer's `git rev-parse --short HEAD`>. Status: <the writer's `git status -sb` first line>.
In that working copy, run `git fetch origin`, then `git status -sb` and `git rev-parse --short HEAD`. If the working copy or its branch is not the one named, stop and report. Do not pull. If the commit differs from the one named, or the branch is behind `origin/main`, say so in the report; do not rebase or merge. The report names the commit the work started at.
<Only if the run must rebase or merge: say so here, and onto what.>

## Claims to check
<Each thing the writer believes but did not verify, one per line. The session checks each before relying on it, and reports what it found. Write "none" if there are none.>

## Not in this run
<What the session must not do or touch: files, systems, outward writes, follow-up work. Write "none" only when the purpose already bounds it.>

## Report
<The shape of the reply: what it lists, and how long it may be. Ask for each claim marked verified or inferred.>
```

## Filling it in

1. **Start with the tier line.** It is the first line of the prompt, as [handing work off](../orchestration.md#handing-work-off) says. Pick the tier from [the three tiers](../orchestration.md#the-three-tiers).
2. **Write for a reader with nothing else.** The session has the prompt and the workspace, and none of your history. Link pages by path instead of restating them.
3. **Settled means settled.** List only what the person or an approved plan decided. Something you merely concluded goes under "Claims to check" instead.
4. **Name the starting point; do not move it.** Run `git rev-parse --short HEAD` and `git status -sb` in the working copy as you write, and copy both into the prompt. The new session fetches and checks; it never pulls. In the main working copy, the start-of-session fast-forward of [decision 0005](../decisions/0005-concurrent-sessions-and-the-edit-ledger.md) updates main under its own conditions. On a branch, a pull would move the tip the work was sent to.
5. **Keep the claims to check honest.** A belief you did not run or read goes there, not under "Purpose and done". A fresh session that is handed a conclusion tends to confirm it.
6. **Make "Not in this run" concrete.** Name the paths and systems, not "stay in scope".
7. **Give the report a shape.** When the session ends a procedure, the report follows [procedure endings](../procedure-endings.md#the-report); point at it rather than restate it. Add only what this task needs, such as a line limit or a list of files written.
8. **Check it once** by reading it as the new session would: every path exists, and every command runs.

## Rules

| Rule | Enforced by |
|---|---|
| The prompt holds all six parts, in their order; a part with nothing in it says "none". | `prose` |
| Something the writer concluded but did not verify goes under "Claims to check", never under "Settled". | `prose` |
| The prompt links the plan and the workspace's pages instead of copying them. | `prose` |
| A critic is dispatched with its own playbook's template, never with this one. | `prose` |
| The prompt names the working copy, its branch and the starting commit. The new session fetches and never pulls, and stops only when the working copy or branch is not the one named. A branch behind main is reported, not rebased, unless the prompt says to. | `prose` |
