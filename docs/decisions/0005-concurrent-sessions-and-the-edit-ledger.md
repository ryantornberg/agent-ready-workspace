---
kind: decision
status: accepted
date: 2026-11-16
deciders: the maintainer
last-reviewed: 2026-11-21
---

# 0005: Concurrent sessions and the edit ledger

**In short:** the first live agent session that edits a tracked file in the main working copy holds a lease on it. Any other live session is refused there and sent to a worktree of its own. A person working with one session sees no change. The lease is taken over only when its holder is dead, or when the main copy has nothing to protect and the lease is at least five seconds old. It is released when its session ends. While another live session holds it, git commands that would drop that session's work are refused, and so are a push from the main working copy and a push from a worktree that sends the branch the main copy has checked out, every branch, a mirror or a glob. The edit ledger records which session's edit tool wrote each entry, so a session with edits of its own cannot finish a turn on its first try while the check or the fast tests fail.

## Context

[Decision 0002](0002-hooks-remind-the-commit-enforces.md) keeps another session's edits out of a commit: the commit check compares the staged paths with the paths this session's edit tools wrote. It does not stop two sessions sharing one working copy. They still share one index, one local main and one set of files. The walled reader's survey of the work workspace listed what that costs: commits carrying another session's files, a hard reset erasing another session's work, stashes catching everyone's edits, one session's unpushed commits blocking another's push, and a branch switch swapping every session's files.

An earlier rule there sent every writing session to a worktree. For a person working with one session, that broke two things: the session started from the remote's main and never saw the person's uncommitted edits, and its edits landed in a folder the person's editor was not showing. So the lease keeps the solo case as it was, and isolates only the second session onward.

## Decision

**What needs a lease.** An edit to a file that git tracks in the main working copy of this repository. A new or untracked file, an ignored path, an edit in a linked worktree, and an edit in another repository need none. The ledger is unchanged: each working copy keeps its own, and the lease does not replace it.

**The record.** One JSON file, `ws-lease.json`, in the common git folder, so every worktree sees the same one: the session id, the agent tool's process id, and when it was taken. It is written to a temporary file and renamed over the old one, under an exclusive lock on `ws-lease.lock` beside it: an advisory file lock on POSIX, a byte-range lock on Windows. The lock is polled for two seconds; without it, nothing is written. The operating system frees it when its process dies.

**Identity.** The session id comes from the tool's payload, `session_id`, for both Claude Code and Codex CLI. The process id is the agent tool's own long-lived process:

| Tool | Process id |
|---|---|
| Claude Code | `CLAUDE_PID`, which the tool sets for its hooks |
| Codex CLI | The runner's grandparent, on POSIX only. Codex sets no such variable; its recorded run showed each hook's parent is a shell whose parent is Codex. On Windows no id is read, so a Codex edit that needs a lease is refused there. |
| Another tool | The workspace's own event shape may carry `"session"` and `"pid"` |

A subagent inherits both, so it counts as its session.

**Liveness.** On POSIX, signal 0: no such process is dead, and permission denied is alive. On Windows, signal 0 is not a probe, so the process is opened for a limited query and its exit code read; only "still active" is alive, and access denied is alive. An id that is not a positive whole number is dead. The probe never raises. If the system reuses a dead holder's id, the lease looks live, and the next session is refused: the error falls on the safe side, and the refusal says how to clear it.

**Acquire.** The lease file already holding this session's id and process id is "mine", without the lock. Otherwise, under the lock: no lease, or a dead holder, is taken. The same session under a new process id refreshes it. A corrupt lease younger than five seconds counts as held, since it may be mid-write; an older one is replaced. A live other holder is refused, unless the takeover holds.

**Takeover is by state, not by time.** The plan's "idle past the limit" means this: a live holder's lease is taken over only when all of these hold.

- The lease is at least five seconds old: the minimum age, so a holder about to edit keeps it.
- It is not corrupt.
- The main copy has no tracked change, staged or not. Untracked files, and uncommitted work inside a pinned repository, do not count; a moved pin does.
- It is on main, not detached and not another branch.
- Main has no commit ahead of its upstream, or of `origin/main` when none is set.

The probe shares one deadline of 1.5 seconds across its git calls, runs them without optional locks, and gives no takeover when any call fails or times out. A takeover purely by idle time was rejected: it could hand a live session's uncommitted edits to another.

**Release.** On `session-end`, from either tool, the lease is removed when this session holds it, and only then.

**What refuses.** Another live holder: the refusal names the worktree command, the path to edit there, the holder's session and when it took the lease, and the lease file a person may delete. A missing session or process id, or any lease error: refused, and no lease is taken. A lease bug never lets an edit through.

**The start-of-session fast-forward.** At `session-start`, the main copy is brought up to `origin/main` only when the session runs in the main copy, on main, with no tracked change, no merge or rebase in progress, and no other live holder. It fetches with prompts off and a time limit, then merges fast-forward only, fifteen seconds in all. It reports why it held back. A fetch that fails, another branch or a linked worktree is left alone without a word. It never fails the session.

**The discard guard.** Amended 2026-11-21, M3 slice C3a. A lease on the edit tools does not stop a shell command from erasing another session's work. So the `no_discard` hook refuses git commands that drop work, and only while another live session is on record: the lease is held by a live session other than this one. A person working with one session, and the lease holder itself, see no change. A lease that cannot be read counts as held.

- **In the main working copy** it refuses a hard reset, `reset --keep` and `--merge`, a whole-tree checkout or restore, `checkout -f`, `switch -f`, `read-tree -u --reset`, a forced clean, a stash write, and the rebase family: rebase, cherry-pick, a rebasing pull, and anything with autostash.
- **From any working copy** it refuses `stash drop`, `pop` and `clear`, since every worktree shares one stash; `worktree prune`; and `worktree remove --force` of a worktree the session is not in.
- **In a linked worktree** every other form passes.
- **A command it cannot judge is refused**: a program or git subcommand that is a variable, a git subcommand that is neither built in nor an alias, an alias that runs a shell command, arguments supplied at run time, or a folder that cannot be placed.
- **Aliases and config writes.** Amended 2026-11-21, M3 slice C5c. A git alias is read from config at hook time and judged as what it runs, so an alias for `git status` passes and one for a hard reset is a hard reset. On a form it decides on, `HOME`, `XDG_CONFIG_HOME`, `GIT_CONFIG_GLOBAL`, `GIT_CONFIG_SYSTEM` or `GIT_CONFIG_NOSYSTEM` set on the command, or an include or a key it cannot read given by `-c`, `--config-env` or `GIT_CONFIG_*`, changes the config the guard read. So it is refused wherever the call acts: the main copy, a linked worktree or another repository. The rules are shared with the push guard, in `wslib/gitrules.py`; see [decision 0004](0004-the-hook-contract.md), "The rules the shell guards share".

The runner tells it which working copy each git call acts on, read from the command's `-C`, `--git-dir`, `--work-tree`, their variables and a leading `cd` or `pushd`, and asked of git; see [decision 0004](0004-the-hook-contract.md), "Shell events". So `cd <main>; git reset --hard` from a worktree is judged as a reset in the main copy.

**The push guard.** Amended 2026-11-21, M3 slice C4. A push from the main working copy can publish the lease holder's unpushed commits, which it has not finished. So the `push_lease` hook refuses a `git push` whose folder is the main working copy, under the same condition as the discard guard: only while the lease is held by a live session other than this one, or cannot be read. A dry run passes, since it publishes nothing. A push from a linked worktree passes. So does a push in another repository. A push whose folder cannot be placed, and a command the guard cannot judge, are refused, and so is a push with any of the config writes the discard guard refuses set on it, listed above, wherever it acts: from a linked worktree and from another repository too. A stored alias that pushes is judged as a push. A session that needs to push works in a worktree of its own. The guard does not judge what a push from a worktree sends: every working copy shares one set of branches, so a worktree's push of the branch the main copy has checked out, or of all branches, can still publish the holder's commits.

**What a worktree's push sends.** Amended 2026-11-22, M3 slice C5d, on the maintainer's answer to Q11. The gap the paragraph above names is closed for the forms that share most. While the lease is held by a live session other than this one, `push_lease` also refuses a push from a linked worktree of this repository that sends the branch the main working copy has checked out, every branch with `--all` or `--branches`, a mirror, written or set in the remote's config, or a glob refspec. It reads what the push sends from the runner's `targets` fact, which works out the push's refspecs with git, so a bare push is judged by `push.default` and the branch's upstream, and a push whose target cannot be worked out is refused. A push of HEAD, or a bare push, after a call earlier in the same line that can change the branch, such as `git switch --ignore-other-worktrees main`, is refused, since the target was worked out before that call runs. A push of the worktree's own branch passes, and so does a deletion of a remote branch. A commit of the main copy's branch named by its id, another branch the holder made, and a tag still pass, since nothing records which commits and branches are the holder's. A branch made from the main copy's HEAD holds the holder's commits too, so the guard's refusal in the main copy says to start a new worktree from `origin/main`, with `--no-track`.

**The ledger records each entry's session, and the stop gate reads it.** Amended 2026-11-21, M3 slice C5a. An entry an edit tool wrote names the session whose tool wrote it, `{"path": ..., "session": ...}`. The same path edited by two sessions has an entry for each. An entry with no known session, such as one `python3 ws.py ledger --add` wrote, is the quoted path alone, as every entry was before, and both forms are read. The commit check still reads only the paths, every entry's whoever wrote it, and a commit still drops every entry for each path it holds.

The `stop_gate` hook uses it. When a session tries to finish a turn, the runner looks for that session's entries in the ledger of every working copy of this repository. With none, the session stops and nothing runs. With some, the runner runs `python3 ws.py check` and the fast tests the manifest names, in each working copy that holds them, within 20 seconds. While either fails, runs out of time or cannot start, the stop is refused with the failure. The stop right after a refusal goes ahead with the failure as a report, so a turn is refused at most once; the next turn's first stop is judged again. An edit ledger that cannot be read refuses once too, with nothing run, since whose edits are waiting cannot be told. See [decision 0004](0004-the-hook-contract.md), "After-edit and stop events".

**The merge helper and the lease.** Amended 2026-11-21, M3 slice C4. `python3 ws.py merge NUMBER` merges a pull request on GitHub, so no working copy takes part in the merge and the lease does not bar it. After the merge it brings the main working copy up to date under the conditions of the start-of-session fast-forward: on main, no tracked change, no merge or rebase in progress, and no other live holder. Unlike that fast-forward, it acts from any working copy, and it says why it held back in every case. A holder whose process id is the caller's own Claude Code process, as `CLAUDE_PID` names it, does not hold it back. Under Codex the helper cannot tell its own process, so any live holder holds it back, the caller's own lease included. See [changing the machinery](../changing-the-machinery.md#the-path-for-a-machinery-change).

## What it gave up

- **An accepted race.** A holder whose edit cleared the hook a moment before a takeover, or sat on a permission prompt past the minimum age, may get that one edit in. Its next commit is refused by the ledger, and it moves to a worktree.
- **A shell write takes no lease.** It does not pass the edit hook. The lease check at commit, which would close that, is in the plan's "Later".
- **The stop gate sees only what the edit tools wrote.** Amended 2026-11-21, M3 slice C5a. A file written through the shell, or recorded with `ws.py ledger --add`, carries no session, so it does not start the gate. A commit drops its paths from the ledger, so a session that committed every edit stops without the gate; the commit check ran at that commit, the fast tests did not.
- **Worktree sessions are recorded nowhere.** A session in a worktree takes no lease, so the discard and push guards cannot tell that one is working there. Nothing stops the lease holder from dropping a worktree session's stash or removing its worktree. M5's worktree work may record them.
- **Codex on Windows** cannot hold a lease until a recorded run shows where its process id is.

## Rejected

- **Every writing session in a worktree**, the source's earlier rule. It broke the solo case.
- **Walking the whole parent-process chain** to find the agent. A wrapper shell can sit above it. The one fixed step for Codex rests on its recorded run, and is the first thing to recheck when Codex changes.
