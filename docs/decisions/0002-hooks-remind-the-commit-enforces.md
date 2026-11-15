---
status: accepted
last-reviewed: 2026-11-15
---

# 0002: Hooks remind; the commit enforces

**In short:** the rule "stage files by name" is enforced at the commit, not before the shell command. The commit check compares the staged paths with the paths the agent's edit tools wrote. The shell hook stays, as a reminder that never refuses.

## Context

Another session, or the person, may have edits in the same folder. A commit that stages everything sweeps them in under the wrong message.

The first guard read each shell command and refused `git add -A`, `git add .` and `git commit -a`. It read a command line without running a shell, so each new spelling grew the parser: wrappers, `sh -c`, `eval`, heredocs, abbreviated options. The M1 red team found it wrong in both directions:

- **Too wide.** It refused `git commit -m"add export handler"`, because it read the message as the flag `-a`. It refused `git add -u docs/parts.md`, which names its path. It refused `git add .` in a scratch repository that has nothing to do with the workspace, because a command line does not say which repository it acts on.
- **Too narrow.** A script, an alias or a variable that runs the same command got past it. So did `git add src`, which names a whole folder.

A command line does not hold the answer. The commit does: it holds exactly the paths that will be recorded, whatever staged them.

## Decision

- **The runner records each path an edit tool is allowed to write**, in a ledger for the working copy that holds the file, inside its git folder.
- **The commit check compares.** While a ledger is open, a staged path that no edit tool wrote fails the `edit_ledger` check. This covers every way of staging, including `git commit -a` and a script.
- **A commit closes what it holds.** The post-commit hook removes the committed paths from the ledger, and deletes the ledger when it is empty. With no ledger, as for a person's own commit, nothing is compared.
- **The shell hook reminds.** `no_stage_all` still reads the command line. When it sees a command that stages everything, the agent is told so next to the command's result, and the call goes ahead. The runner also opens the ledger at that moment, even empty, so a session that wrote its files only through the shell still has its commit compared.
- **A file written another way is named.** A file a shell command or a generator wrote is recorded with `python3 ws.py ledger --add PATH`. Naming it is the same act as staging it by name.

## What it gave up

- **A refusal before the damage.** The index can hold another session's edits for a moment, until the commit is refused and the agent unstages them. Nothing reaches the history.
- **One more step for shell-written files.** An agent that writes a file with a heredoc and then commits it must record it first. The refusal says how.
- **A person can be refused.** While an agent's edits wait uncommitted, a person's own commit in the same working copy is compared too. The refusal says how to close the ledger.
- **It stops accidents, not intent.** `git commit --no-verify`, or closing the ledger by hand, gets past it. CI cannot run it, because CI has no ledger.

## Options rejected

- **Keep refusing, and teach the parser where a command runs.** It would track `cd`, `git -C` and the session's folder, and still could not follow a variable or a script. That is the parser growth this record ends.
- **Record shell writes too.** A shell command's writes cannot be read from its text, and a tracer for every command is out of proportion to the risk.
- **Close the ledger at the end of the session.** Claude Code can run a hook then, but no other tool here can yet, and a crashed session would leave it open. Closing on commit needs nothing but git.
