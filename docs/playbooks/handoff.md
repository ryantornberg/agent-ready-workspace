---
kind: playbook
proof: unproven
prove-by: M6
last-reviewed: 2026-11-21
---

# Handoff

How a session writes down its state so that a later session can pick up the work, and how that session reads it. For any agent about to stop mid-task.

**In short:** commit what the plan and the question log are owed, write one note with six fixed sections from the session's real state, then stop without going on with the task. The next session reads the note, checks it against the working copy, and starts from its next step. Until slice C5b of M3 adds the marker and the loader, the person passes the note's path by hand.

## When to use it

Use it when a session must stop before its task is done: its context is running low, the person asks to hand off or to pause, or the work will resume in another session.

| The situation | Go to |
|---|---|
| The whole session stops, and a later session will carry on its task. | This page. |
| You hand one piece of the work to a helper that reports back to you now. | [Handing work off](../orchestration.md#handing-work-off), which is delegation, not this. |
| The work needs a plan before it is built. | The [hand-off plan template](../templates/hand-off-plan.md). A plan says what to build; a handoff note says where a session got to. |

When the task has a hand-off plan, a handoff note does not replace its "Results": step 2 writes there first.

## Writing the note

1. **Gather the real state.** Input: the session's own history and the working copy. Run `git status --short`, `git log --oneline -5` and `git branch --show-current`, and reread what the session decided and ran. Output: the facts the note needs. Fill the note from these only. Never invent a state, a result or a decision; what you did not check is marked inferred.
2. **Write down what is owed.** Input: the facts from step 1. Two records are written before the note, because the next session may never come: findings the task's hand-off plan should hold go under its "Results", as [delegating](../orchestration.md#delegating) says, and a question you had to ask a person goes in the [question log](../question-log.md), as the contract says. Stage each file you wrote here by name and commit it. Default: with no plan and no such question, skip this step. If the commit is refused, leave those edits uncommitted, name them in the note's "Current state", and go on. Output: the commit, or what was left and why.
3. **Pick the file.** Input: the repository's folder name, today's date and a short topic of two to four words. Default: write to `~/handoffs/`, outside every repository, unless the person names another folder. Name the file `<YYYY-MM-DD>-<repository>-<topic>.md`. When this session already wrote a note on this topic, update that file in place instead of starting a new one. Output: the path.
4. **Write the six sections.** Input: the facts from step 1. Open with the title line `# Handoff: <repository>, <date>, <topic>`, then the sections in the order under [The note](#the-note). Err toward more detail. Keep the reasoning and the history, so a reader who has only the note knows all a reader needs. Output: the note, written. If the folder cannot be written, put the whole note in your reply instead, and say so.
5. **Stop.** Input: the written note. Do not go on with the task, and edit nothing beyond what step 2 wrote. Leave the task's uncommitted changes as they are; the note's "Current state" names each one, and the working copy that holds them, main copy or worktree, by path. The next session finishes and commits them. Output: a reply that gives the note's path, the mode, the line that resumes the work, `Read <path> and resume from its next step.`, and one more: end this session before you start the next one in the same working copy. Until it ends, its lease on the main working copy stays held, as [decision 0005](../decisions/0005-concurrent-sessions-and-the-edit-ledger.md) says.

Stop when that reply is given.

## The note

The six sections, in this order, each a `##` heading:

| Section | Holds |
|---|---|
| Goal | What the session is trying to do, and for whom. |
| Current state | What is built, verified, in flight and blocked, stated specifically: paths, branches, commits and uncommitted files. Each claim is marked verified or inferred. |
| Decisions made | Each decision, its reasoning, and the options rejected. |
| Open threads and next step | The single next concrete action first, then the rest of the open threads. |
| Key references | Paths, commands, pull request numbers and links, enough to act without searching again; and the session's working-notes file, when it has one. |
| Do not redo | Dead ends already ruled out, each with what ruled it out. |

## Two modes

| Mode | Where the note goes | Status |
|---|---|---|
| Archive | A file outside every repository, as step 3 says. Nothing is committed. | The default; works today. |
| Keep | A tracked copy committed with the repository, for work whose history the team wants to keep. A path that exists only on the author's machine is flagged as such, and a committed page is linked in its place. | Waits for the handoff note record type that slice B3 of M3 adds. Until then, write an archive note and say that keep mode waits. |

## Resuming

1. **Read the note in full.** Input: the note's path, from the person. Output: the goal, the next step and the dead ends.
2. **Check it against the working copy.** Input: the note's "Current state", which names the working copy by path. Run `git -C PATH status --short`, `git -C PATH log --oneline -5` and `git -C PATH branch --show-current` on that path, and compare. Output: the note's state confirmed, or each difference listed. When they differ, the working copy wins: tell the person what changed, and ask before you act on the old state. Default: with no answer, report the differences and stop, changing nothing.
3. **Start from the next step.** Input: the confirmed note. Work in the working copy the note names. If the lease refuses your edit there, the stopping session is still live. A worktree of your own, which the refusal offers, would lack the uncommitted changes the note names. So tell the person, and ask: wait until that session ends, or carry on in a worktree without them. Default: with no answer, report and stop, changing nothing. Do the action "Open threads and next step" names first. Do not retry what "Do not redo" lists unless something new makes it worth it, and say what. Output: the task under way again, under the procedure it was following.

## The marker and the loader

Slice C5b of M3 plans a marker and a loader. `python3 ws.py handoff` will write a marker naming the note, keyed by the branch, in the working copy's git folder; it updates its own marker in place and touches no other. At session start, the loader will show the note when one marker is pending, and list the markers when two or more are. A marker clears when its branch merges, or on `python3 ws.py handoff --done`. None of this exists yet, and `python3 ws.py --help` shows no `handoff`. Until it does, the person passes the path as step 5 of writing gives it. Never write a marker by hand.

## Rules

| Rule | Enforced by |
|---|---|
| Fill the note from the session's real state; never invent a state, a result or a decision. | `prose` |
| Writing the note is the whole job: do not go on with the task, and edit nothing beyond the plan's "Results" and the question log that step 2 writes. | `prose` |
| The note holds the six sections, in their order. | `prose` |
| When the note and the working copy differ, the working copy wins; ask before acting on the old state. | `prose` |
| Never write a handoff marker by hand. | `prose` |
| On resuming, do not retry what "Do not redo" lists unless something new makes it worth it, and say what. | `prose` |
| Mark each claim in "Current state" verified or inferred. | `prose` |
