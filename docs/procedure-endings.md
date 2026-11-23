---
kind: reference
last-reviewed: 2026-11-23
---

# Procedure endings

The rules a procedure ends with, stated once, for the agent finishing a playbook or how-to and for anyone writing one.

**In short:** a procedure ends the same way, whatever it did. Get a yes before any write outside the workspace that the request does not name. Log a question the workspace should have answered. Commit what you wrote, staged by name, with a review trailer when a guidance page changed. Push as this page says; off main, push nothing for pages. Then report, each claim marked verified or inferred. A page links here instead of restating these rules.

## The order

Run these in order, after the procedure's own last step. Skip a step only where it says so.

1. [Outward writes](#outward-writes): settled before any is made.
2. [The question-log entry](#the-question-log-entry): only if you had to ask a person something.
3. [The commit](#the-commit): every file the procedure wrote, the log row included unless step 2 leaves it uncommitted.
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

Commit every file the procedure wrote, once the work is verified, and the question-log row of step 2 unless that step leaves it uncommitted. A procedure that wrote nothing commits nothing.

- **Stage each file by name.** Never `git add -A`, `git add .` or `git commit -a`: another session may have edits in the same folder. The commit check refuses a staged file your edit tools did not write. Record one you wrote another way, such as by shell, with `python3 ws.py ledger --add PATH`.
- **Leave other changes alone.** An uncommitted change you did not make is not yours: do not stage it, revert it or stash it.
- **Name the review.** A commit that adds, changes or deletes a guidance page carries `Instructions-review: <record>` for each record, or a listed skip reason. [The instruction review](playbooks/instruction-review.md) says which pages are guidance and how to get the record.
- **Write the subject** as [commits](commits.md) says: a conventional commit by default.
- **Where the commit goes.** A change of pages only: on main in the main working copy, or on the worktree's branch in a worktree. [Off main](#off-main), on the branch checked out. A change to scripts, parts, hooks or CI: on a branch of its own, as [changing the machinery](changing-the-machinery.md#the-path-for-a-machinery-change) says. A change to code under `src/` or in a pinned repository: on a branch of its own in the repository that holds the code, never on its main. This page holds that rule; [fix a bug](playbooks/fix-a-bug.md)'s step 5 states it too, until it links here.

If the commit is refused, read the refusal, fix what it names, and commit again. If it is still refused, leave the files uncommitted and name each in the report with the refusal.

## The question-log entry

If you had to ask a person something this workspace should have answered, add a dated row to the [question log](question-log.md). With no such question, skip this step.

- Add the row with your edit tools, so the edit ledger holds the file.
- It is committed in the next step, with the rest or on its own, and needs no `Instructions-review:` trailer: the log is a record, not a guidance page.
- A procedure that otherwise commits nothing still commits this entry, unless the next bullet applies.
- If the log already holds uncommitted rows you did not add, do not stage it, since they are not yours to commit. Leave your row in the file, and give its text in the report.
- Rows left uncommitted are the person's to settle. The report says the log holds them. A session commits them only when the person names which rows to commit. Until then, the start-of-session fast-forward of [decision 0005](decisions/0005-concurrent-sessions-and-the-edit-ledger.md) holds back, and [the push](#the-push) takes its path for a main copy with uncommitted changes.
- If the edit is refused, give the row's text and the refusal in the report.

## The push

Push the commits of step 3. First run `git fetch origin`. Then check whether you are [off main](#off-main): if you are, the table's first row applies and no other. Main has moved when `git merge-base --is-ancestor origin/main HEAD` exits with 1.

| What you committed | What you push | Who pushes |
|---|---|---|
| Pages, [off main](#off-main) | Nothing. The commits stay on the branch, for its pull request. | Nobody: the report names each commit left on the branch. |
| Pages only, in the main working copy | `git push origin main`, or, if main has moved, as [the next section](#when-main-has-moved) says | In this repository, the agent. In a team's workspace, a person: leave the commits unpushed and say so in the report. |
| Pages only, in a worktree | `git push origin HEAD:main`, after `git pull --rebase origin main` if main has moved | As above. |
| Machinery, on its own branch | The branch, then a draft pull request | As [changing the machinery](changing-the-machinery.md#the-path-for-a-machinery-change) says: in this repository the agent publishes and merges once CI passes on Linux, macOS and Windows; in a team's workspace, a person does. |
| Code under `src/` or in a pinned repository | The branch, to the remote of the repository that holds the code, then a draft pull request. With no remote, nothing. | As the contract's rule on draft pull requests says for that repository. |

A push is done when, after `git fetch origin`, `git rev-parse HEAD` in the copy you pushed from prints the same commit as the branch you pushed to, such as `git rev-parse origin/main`.

If the push is refused, read why. The pre-push hook names a commit and its reason: fix it and push again, once. The remote's rejection as not a fast-forward means the branch moved after your fetch: fetch again, follow the table's row for a moved main, and push again, once. If it is still refused, leave the commits unpushed and name them in the report.

### Off main

Off main, push nothing for pages. You are off main when the branch checked out is not `main`, unless it is a worktree's branch made for pages alone, as the contract sends you to when another session holds the main working copy. A fix's, a feature's, a machinery change's or a pull request's branch is off main, in the main working copy or in a worktree. A push of pages from there would carry the branch's other work to main ahead of its pull request and its review.

In a worktree made for pages, check before any push: run `git log --format='%h %s' origin/main..HEAD`. It lists each commit the push would carry. If one is not a page commit made for this worktree's work, such as a code or machinery commit, your own included, or one you cannot account for, you are off main.

Off main:

- Push nothing. Leave the page commits, the question-log row among them, on the branch checked out.
- Name each one in the report. Say that it reaches main only if the branch is pushed again before its pull request merges; until then it is on this copy alone.

This holds for every page commit the procedure makes, including one made by a procedure it calls. It narrows [changing the machinery](changing-the-machinery.md)'s rule that a page change goes straight to main: it does, from main or from a worktree made for pages.

### When main has moved

In the main working copy, first run `git status --porcelain --untracked-files=no`.

- **It prints nothing:** run `git pull --rebase origin main`, then `git push origin main`.
- **It prints a file:** a tracked file holds an uncommitted change, another session's or a row you left in the question log. `git pull --rebase` refuses while it does. Do not stash it or pull with `--autostash`: either one sweeps up changes that are not yours. Push from a throwaway worktree of `origin/main` instead:
  1. Run `git log --format='%h %s' origin/main..main`. It lists the commits to push. If it lists one this procedure did not make, stop: push nothing, and name the commits in the report.
  2. `git worktree add --detach .claude/worktrees/push-main origin/main`. If that folder exists, add a word to its name, here and below.
  3. `git -C .claude/worktrees/push-main cherry-pick origin/main..main`. If it stops on a conflict, run `git -C .claude/worktrees/push-main cherry-pick --abort` and go to step 6, leaving the commits unpushed.
  4. `git -C .claude/worktrees/push-main push origin HEAD:main`.
  5. Check the push as above, with `git -C .claude/worktrees/push-main rev-parse HEAD`.
  6. `git worktree remove .claude/worktrees/push-main`.
  7. If the push is done, run `git reset --keep origin/main` in the main working copy. Main there then matches what you pushed, and the uncommitted changes stay. If it is refused, a file with an uncommitted change also changed on `origin/main`. Leave the main copy as it is. Say in the report that its main still holds the commits as first made, that they are on `origin/main`, and that a person runs `git reset --keep origin/main` once that file's change is settled.

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
| Off main, push nothing for pages; the commits stay on the branch for its pull request, and the report names each. | `prose` |
| Log a question the workspace should have answered, and commit the entry before the report, unless the log holds uncommitted rows you did not add; then give its text in the report. | `prose` |
| A refused step does not skip the report; the report names the refusal. | `prose` |
| An uncommitted change you did not make is left alone: not staged, not reverted, not stashed. | `prose` |
| A page links this one instead of restating its rules. The instruction review counts a restated rule as a finding. | `prose` |
