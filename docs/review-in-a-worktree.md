---
kind: how-to
proof: unproven
prove-by: M6
last-reviewed: 2026-11-21
---

# Review a pull request in a worktree

How to put a pull request's files in a separate worktree, review them there, and remove it after. For an agent or a person reviewing a pull request.

**In short:** fetch the pull request's head, add a detached worktree for it under `.claude/worktrees/`, check out its pinned repositories, review, then remove the worktree once it shows no change. Start every session in the main working copy, never inside the worktree or a pinned repository.

## Why a worktree, as an exception

The contract sends a session to a worktree of its own only when another live session holds the main working copy. This page is an exception to that, for one reason: a review needs the files of one exact commit, such as a pull request's head, or the tip and base of a branch the [review orchestrator](playbooks/review-orchestrator.md) builds and compares. Checking that commit out in the main working copy would change the files every other session and the person's editor see. A review worktree is detached from every branch, nothing is edited in it, and it is removed when the review ends.

## Start in the main working copy

An agent tool reads the contract from the folder its session starts in. Started inside a review worktree, it may read the pull request's own copy of `AGENTS.md`, which the review has not accepted. Started inside a pinned repository, it may read no contract at all. So start the session in the main working copy, and give the worktree's path to whoever reads the code, such as each reviewer the [review orchestrator](playbooks/review-orchestrator.md) dispatches.

## Steps

Steps 1 and 2 are for a pull request on GitHub. A pull request on another host waits for M8's planned git-host provider: stop at step 1 and report that. For a commit already in the repository, such as your own branch's tip or base, skip steps 1 and 2: COMMIT is that commit, and the name below uses its first seven characters in place of `pr-NUMBER`.

1. **Read the pull request.** Input: its number, and the repository it is in; by default, this workspace's own. Run `gh pr view NUMBER --json headRefOid,baseRefName,state`, adding `-R OWNER/REPO` for a repository pinned under `src/`. Output: the head commit, the branch it targets, and its state. Default: review an open pull request. If its state is not `OPEN`, stop and report the state; nothing is made.
2. **Fetch its head.** Input: the number. For this workspace's repository, run `git fetch origin pull/NUMBER/head`. For a pinned repository in `src/REPO`, run `git -C src/REPO fetch origin pull/NUMBER/head`. In this sample, the folders under `src/` hold files, not repositories, so the pinned form applies to a workspace with real pins, not to this sample. Check that `git rev-parse FETCH_HEAD`, with the same `-C`, prints the head commit from step 1. If it does not, someone pushed in between: run steps 1 and 2 once more, and if they still differ, stop and report. If the fetch fails, stop and report its error; nothing is made. Output: COMMIT, the fetched head.
3. **Add the worktree.** Input: COMMIT. For this workspace's repository, run `git worktree add --detach .claude/worktrees/review-pr-NUMBER COMMIT`. For a pinned repository, run `git -C src/REPO worktree add --detach "$PWD/.claude/worktrees/review-REPO-pr-NUMBER" COMMIT` from the main working copy. If the path is taken by a review worktree you made for the same commit or pull request, remove it as step 6 says, then add it again. If it is taken by anything else, add `-2` to the name. Output: PATH, the worktree's path, at COMMIT.
4. **Check out its pinned repositories.** Input: PATH, when it is a worktree of this workspace's repository. From the main working copy, run `python3 ws.py --root PATH pins`. It runs the main copy's own engine, not the pull request's, on the worktree. It skips each pinned repository whose remote does not answer, with a note. Default: go on with the review, and say in it which repositories were skipped. Skip this step for a pinned repository's worktree, which has no pins of its own. Output: the worktree with its pins checked out, or the list skipped.
5. **Review.** Input: PATH. Follow the [review orchestrator](playbooks/review-orchestrator.md) with that path as the folder at the tip, or read the code yourself. Edit nothing in the worktree. Output: the review.
6. **Remove the worktree.** Input: PATH. First check that nothing changed in it: `git -C PATH status --short` and `git -C PATH submodule foreach --quiet --recursive 'git status --short'` both print nothing. Then run `git worktree remove PATH`, with `-C src/REPO` for a pinned repository's worktree.
   - If git refuses with "working trees containing submodules cannot be moved or removed", and the check printed nothing, run `git worktree remove --force PATH`. Git always refuses a plain removal once step 4 checked pins out.
   - If the check printed anything, something edited the worktree. Do not remove it: report the files to the person.
   - If the discard guard refuses the `--force`, because another live session holds the main working copy, leave the worktree and report its path for the person to remove.

   Never run `git worktree prune`. Output: `git worktree list` no longer names PATH, or the reason it is still there.
7. **Report.** Input: the outputs above. Report the pull request or commit, the commit reviewed, any pinned repository skipped, and whether the worktree was removed. Nothing in this page commits anything: the review writes no file in this repository, and the review orchestrator says where its findings go.

Stop when the report is given. Every stop in steps 1 to 6 ends in that report too, with the reason said.

## Rules

| Rule | Enforced by |
|---|---|
| A review worktree is used only to read one commit for a review; edit nothing in it. | `prose` |
| Start every session in the main working copy, never inside a review worktree or a pinned repository. | `prose` |
| Use `--force` only on a review worktree whose check printed nothing and that git refuses for its submodules. Never run `git worktree prune`. While another live session holds the main working copy, the discard guard refuses `git worktree prune`, and `--force` on a worktree the session is not in. | `no_discard#worktree remove --force of another session's worktree is refused`, `no_discard#from the main copy, worktree prune is refused` |
| Remove the review worktree when the review ends, unless something edited it or the guard refuses. | `prose` |
