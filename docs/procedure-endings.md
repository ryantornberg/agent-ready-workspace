---
kind: reference
last-reviewed: 2026-11-22
---

# Procedure endings

The rules a procedure ends with, stated once, for the agent finishing a playbook or how-to and for anyone writing one.

**In short:** a procedure ends the same way, whatever it did. Get a yes before any write outside the workspace that the request does not name. Log a question the workspace should have answered. Commit what you wrote, staged by name, with a review trailer when a guidance page changed. Push as this page says. Then report, each claim marked verified or inferred. A page links here instead of restating these rules.

## The order

Run these in order, after the procedure's own last step. Skip a step only where it says so.

1. [Outward writes](#outward-writes): settled before any is made.
2. [The question-log entry](#the-question-log-entry): only if you had to ask a person something.
3. [The commit](#the-commit): every file the procedure wrote, the log included.
4. [The push](#the-push): the commits of step 3.
5. [The report](#the-report): always, and last.

A step that is refused does not end the procedure. Leave its work where it stopped, carry on with the next step, and name the refusal in the report. The report is never skipped.

## Outward writes

An outward write is one that people can see outside this workspace's own files: a ticket, a comment, a pull request, a post, a message.

- Before a write on a tracker, follow "Which writes need a yes" in [tracker operations](playbooks/tracker-operations.md#which-writes-need-a-yes). Before a write on a git host, follow the same section of [git-host operations](playbooks/git-host-operations.md#which-writes-need-a-yes). Those sections own the rules: which writes a request's own words cover, and which always need a yes first.
- On any other system, ask first unless the request names the write in its own words.
- With no answer, make no write. Say in the report what is waiting on the person's yes.

Pushing and merging in this workspace's own repository follow [the commit](#the-commit) and [the push](#the-push), not this section.

## The commit

Commit every file the procedure wrote, once the work is verified, and the question-log row of step 2. A procedure that wrote nothing commits nothing.

- **Stage each file by name.** Never `git add -A`, `git add .` or `git commit -a`: another session may have edits in the same folder. The commit check refuses a staged file your edit tools did not write. Record one you wrote another way, such as by shell, with `python3 ws.py ledger --add PATH`.
- **Leave other changes alone.** An uncommitted change you did not make is not yours: do not stage it or revert it.
- **Name the review.** A commit that adds, changes or deletes a guidance page carries `Instructions-review: <record>` for each record, or a listed skip reason. [The instruction review](playbooks/instruction-review.md) says which pages are guidance and how to get the record.
- **Write the subject** as [commits](commits.md) says: a conventional commit by default.
- **Where the commit goes.** A change of pages only: on main in the main working copy, or on the worktree's branch in a worktree. A change to scripts, parts, hooks or CI: on a branch of its own, as [changing the machinery](changing-the-machinery.md#the-path-for-a-machinery-change) says. A change to code under `src/` or in a pinned repository: as the procedure that made it says, such as [fix a bug](playbooks/fix-a-bug.md), which opens a draft pull request where the repository has a remote.

If the commit is refused, read the refusal, fix what it names, and commit again. If it is still refused, leave the files uncommitted and name each in the report with the refusal.

## The question-log entry

If you had to ask a person something this workspace should have answered, add a dated row to the [question log](question-log.md). With no such question, skip this step.

- Add the row with your edit tools, so the edit ledger holds the file.
- It is committed in the next step, with the rest or on its own, and needs no `Instructions-review:` trailer: the log is a record, not a guidance page.
- A procedure that otherwise commits nothing still commits this entry.
- If the log already holds uncommitted rows you did not add, do not stage it, since they are not yours to commit. Leave your row in the file, and give its text in the report.
- If the edit is refused, give the row's text and the refusal in the report.

## The push

Push the commits of step 3. First run `git fetch origin`; if main moved, run `git pull --rebase origin main` before a push to main.

| What you committed | What you push | Who pushes |
|---|---|---|
| Pages only, in the main working copy | `git push origin main` | In this repository, the agent. In a team's workspace, a person: leave the commits unpushed and say so in the report. |
| Pages only, in a worktree | `git push origin HEAD:main` | As above. |
| Machinery, on its own branch | The branch, then a draft pull request | As [changing the machinery](changing-the-machinery.md#the-path-for-a-machinery-change) says: in this repository the agent publishes and merges once CI passes on Linux, macOS and Windows; in a team's workspace, a person does. |
| Code under `src/` or in a pinned repository | As the procedure that made it says | As that procedure says. |

Read the push's output. A push is done when, after `git fetch origin`, `git rev-parse HEAD` prints the same commit as the branch you pushed to, such as `git rev-parse origin/main`.

If the push is refused, read why. The pre-push hook names a commit and its reason: fix it and push again, once. The remote's rejection as not a fast-forward means the branch moved: pull with rebase and push again, once. If it is still refused, leave the commits unpushed and name them in the report.

## The report

Report to the person in the session's reply, in the shape [the definition of done](definition-of-done.md#the-report) gives. Mark each claim:

- **verified**: you ran something and saw the result;
- **inferred**: you reasoned your way there.

Then name what is not done: anything left uncommitted or unpushed, any refusal from the steps above with its text, any write waiting on the person's yes, and the question-log entry's text if it could not be committed. A procedure that writes its report to a record, such as a fix record, puts the same lines there.

## Rules

| Rule | Enforced by |
|---|---|
| Stage files by name; never stage everything. | `no_stage_all#add -A`, `edit_ledger#a path the ledger does not hold fails, whatever staged it` |
| A commit that changes a guidance page names its review record or a listed skip reason. | `review_trailer#a guidance page changed with no trailer fails` |
| A commit that changes a machinery path reaches main only through a pull request. | `direct_push#a commit that changes a part fails, naming the commit and the path` |
| Mark every claim in a report as verified or inferred. | `eval:fix-a-bug` |
| Ask before an outward write the request does not name, and write nothing on a repository outside this one and those pinned under `src/`. | `prose` |
| Log a question the workspace should have answered, and commit the entry, before the report. | `prose` |
| A refused step does not skip the report; the report names the refusal. | `prose` |
| An uncommitted change you did not make is left alone: not staged, not reverted. | `prose` |
| A page links this one instead of restating its rules. The instruction review counts a restated rule as a finding. | `prose` |
