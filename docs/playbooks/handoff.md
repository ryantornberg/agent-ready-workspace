---
kind: playbook
proof: unproven
prove-by: M6
last-reviewed: 2026-11-22
---

# Handoff

How a session writes down its state so that a later session can pick up the work, and how that session reads it. For any agent about to stop mid-task.

**In short:** commit what the plan and the question log are owed, write one note with six fixed sections from the session's real state, mark it with `python3 ws.py handoff`, then stop without going on with the task. The next session in that working copy is shown the note when it starts. When the person asks it to resume, it checks the note against the working copy and starts from its next step.

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
4. **Write the six sections.** Input: the facts from step 1. Open with the title line `# Handoff: <repository>, <date>, <topic>`, then the sections in the order under [The note](#the-note). Err toward more detail. Keep the reasoning and the history, so a reader who has only the note knows all a reader needs. Output: the note, written. If the folder cannot be written, put the whole note in your reply instead, say so, and skip step 5.
5. **Mark the note.** Input: the note's path. From the top of the working copy whose task the note covers, the one its "Current state" names, run `python3 ws.py handoff <path>`. It writes a marker for the branch checked out there, or replaces the one it wrote before; see [The marker and the loader](#the-marker-and-the-loader). Output: the line it prints. If it refuses, such as on a detached HEAD, skip the marker: the reply in step 6 gives the person the path by hand.
6. **Stop.** Input: the written note. Do not go on with the task, and edit nothing beyond what step 2 wrote. Leave the task's uncommitted changes as they are; the note's "Current state" names each one, and the working copy that holds them, main copy or worktree, by path. The next session finishes and commits them. Output: a reply that gives the note's path, the mode, whether step 5 marked it, the line that resumes the work, `Read <path> and resume from its next step.`, and one more: end this session before you start the next one in the same working copy. Until it ends, its lease on the main working copy stays held, as [decision 0005](../decisions/0005-concurrent-sessions-and-the-edit-ledger.md) says.

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

1. **Read the note in full.** Start here only when the person's request is to resume the work. A session-start notice of a pending note is not that request: for any other request, do what was asked, and tell the person once that the note is pending. Input: the note, which the notice shows when one marker is pending in this working copy, or its path, from the person. When the notice lists two or more notes instead, ask the person which one to resume. Default: with no answer, report the list and stop, changing nothing. A note the notice cuts short says so; read the rest from its file. Output: the goal, the next step and the dead ends.
2. **Check it against the working copy.** Input: the note's "Current state", which names the working copy by path. Run `git -C PATH status --short`, `git -C PATH log --oneline -5` and `git -C PATH branch --show-current` on that path, and compare. Output: the note's state confirmed, or each difference listed. When they differ, the working copy wins: tell the person what changed, and ask before you act on the old state. Default: with no answer, report the differences and stop, changing nothing.
3. **Start from the next step.** Input: the confirmed note. Work in the working copy the note names. If the lease refuses your edit there, the stopping session is still live. A worktree of your own, which the refusal offers, would lack the uncommitted changes the note names. So tell the person, and ask: wait until that session ends, or carry on in a worktree without them. Default: with no answer, report and stop, changing nothing. Do the action "Open threads and next step" names first. Do not retry what "Do not redo" lists unless something new makes it worth it, and say what. Output: the task under way again, under the procedure it was following.
4. **Clear the marker when the note is spent.** Input: the note's branch, which the notice names, and the working copy the notice came from: the one this session started in. When the person gave you the path by hand, run `python3 ws.py handoff` at the top of the working copy the note names; it lists that copy's markers, and the one naming this note gives the branch. Default: when none names it, there is nothing to clear. A marker stops showing on its own once its branch merges. Otherwise, from the top of that working copy, run `python3 ws.py handoff --done <branch>` once the work the note covers is committed, or when the person drops it. `ws.py` acts on the working copy that holds the `ws.py` file you run, so run the one at that working copy's top, never another copy's by path, and check that it prints "cleared". If you stop again before then, write a new note and mark it, which replaces the marker. Output: the marker cleared or replaced, so the next session is not shown a spent note.

## The marker and the loader

`python3 ws.py handoff <path>` writes a marker that names the note. It is keyed by the branch the working copy has checked out, and kept in that working copy's git folder, where an agent may not write. The `git_folder` guards refuse an edit tool's write there and every shell write the parser reports. An interpreter, such as `python3 -c`, can still write there, as the README's limits say, so the rule below is the agent's part. Run on the same branch again, it replaces that branch's marker in place. It never opens another branch's marker.

A marker is pending until its branch merges, or until `python3 ws.py handoff --done <branch>` removes it; with no branch, `--done` removes the one checked out. A merged branch's marker stays in the git folder, not shown, until `--done` removes it or a new note on that branch replaces it. A branch has merged when its tip, when the note was written or now, has since reached `origin/main`, or `main` when there is no remote-tracking ref. Three cases stay pending until `--done`:

- a note on `main` itself;
- a branch with no commits of its own;
- a branch merged by a squash or a rebase, which this repository's merge settings refuse.

At session start, the loader reads the markers of the working copy the session starts in, a linked worktree's own included:

| Pending markers | The session is shown |
|---|---|
| One | Its note, with the branch, the path and when it was written. A note over 8,000 characters is cut, and the notice says so. A note that cannot be read is named, not shown. The notice says to resume only when the person's request is to resume this work. |
| Two or more | No note. The markers are listed, branch and path. When the person's request is to resume work, the session asks which one. |
| None | Nothing. |

`python3 ws.py handoff` with no argument lists the working copy's markers, each pending or merged. A session that starts in another working copy is not shown the note: give the person the path, as step 6 of writing does.

## Rules

| Rule | Enforced by |
|---|---|
| Fill the note from the session's real state; never invent a state, a result or a decision. | `prose` |
| Writing the note is the whole job: do not go on with the task, and edit nothing beyond the plan's "Results" and the question log that step 2 writes. | `prose` |
| The note holds the six sections, in their order. | `prose` |
| When the note and the working copy differ, the working copy wins; ask before acting on the old state. | `prose` |
| Never write a handoff marker by hand: run `python3 ws.py handoff`. | `git_folder#an edit to a handoff marker in the git folder is refused`, `git_folder_shell#a shell write to a handoff marker in the git folder is refused` |
| Mark a written note with `python3 ws.py handoff`, and clear a spent one with `--done`. | `prose` |
| On resuming, do not retry what "Do not redo" lists unless something new makes it worth it, and say what. | `prose` |
| Mark each claim in "Current state" verified or inferred. | `prose` |
