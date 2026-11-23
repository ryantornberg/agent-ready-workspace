"""Hook: while another live session holds the main working copy, refuse git commands that drop its work.

Two sessions share the main working copy's files, index and branch, and every worktree shares one stash.
A hard reset, a forced checkout or a stash drop by one session erases the other's uncommitted work. This guard
is active only while the writing-session lease is held by a live session other than this one (decision 0005),
so a person working with one session sees no change. A lease that cannot be read counts as held.

While it is active:

- In the main working copy: hard reset, `reset --keep` and `--merge`, a whole-tree checkout or restore,
  `checkout -f`, `switch -f`, `read-tree -u --reset`, a forced clean, a stash write, and the rebase family
  (rebase, cherry-pick, a rebasing pull, anything with autostash) are refused. The lease holder is never
  refused, since for that session the guard is not active.
- From any working copy: `stash drop`, `pop` and `clear`, which reach the stash every worktree shares,
  `worktree prune`, and `worktree remove --force` of a worktree the session is not in.
- In a linked worktree, every other form passes.
- A command the guard cannot resolve is refused: a program or subcommand that is a variable, a git subcommand
  that is neither built in nor an alias at hook time, an alias that runs a shell command, arguments supplied at
  run time by xargs or find -exec, or a folder the parser or the runner could not place.
- On a form it decides on, HOME, XDG_CONFIG_HOME or a GIT_CONFIG_* variable set on the command, and an include
  given by -c or GIT_CONFIG_*, count as config writes and are refused, from any working copy.

A git alias is expanded from config at hook time, as git would run it, so an alias that resets hard is judged as a
hard reset and one that runs git status passes. The runner gives the lease, the session's own working copy, each
git folder's kind and the aliases read in each folder (decision 0004, "Shell events"). This part reads the command
through wslib/gitrules.py, which the shell guards share, and looks each call's folder up by the parser's own text.
Parser gaps it handles here, until slice Z moves them into the parser: a whole-tree checkout or restore, a stash
write, and the rebase and cherry-pick commands, none of which the parser lists among the forms that drop work.
See docs/decisions/0005-concurrent-sessions-and-the-edit-ledger.md.
"""
import datetime
import posixpath

from wslib import gitrules

KIND = "hook"
EVENT = "before-shell"
NEEDS = ("session", "lease", "working_copies", "aliases")
PAGE = "docs/decisions/0005-concurrent-sessions-and-the-edit-ledger.md"

QUIET = ("free", "mine", "other-dead")
SHARED = {"stash drop", "stash pop", "stash clear", "worktree prune"}
MAIN_ONLY = {"reset --hard", "reset --keep", "reset --merge", "switch --force", "checkout --force",
             "read-tree --reset -u", "clean --force", "autostash", "whole-tree checkout", "whole-tree restore",
             "stash write", "rebase", "cherry-pick", "pull --rebase"}
STASH_WRITES = {"push", "save", "store"}
WHOLE = {".", "./", ":/", ":/.", ":/*", ":(top)", ":(top).", "*", "**"}
CHECKOUT_VALUES = {"-b", "-B", "--orphan", "--conflict", "--pathspec-from-file"}
RESTORE_VALUES = {"-s", "--source", "--conflict", "--pathspec-from-file"}


def _whole(word):
    if word in WHOLE:
        return True
    parts = [part for part in word.split("/") if part]
    return bool(parts) and all(part in (".", "..") for part in parts)


def _operands(args, with_values):
    """(operands, flags) of a checkout or restore, with every operand after "--" counted."""
    operands, flags, skip, ended = [], set(), False, False
    for word in args:
        if skip:
            skip = False
        elif ended:
            operands.append(word)
        elif word == "--":
            ended = True
        elif word.startswith("-") and word != "-":
            name = word.split("=", 1)[0]
            flags.add(name)
            skip = name in with_values and "=" not in word
        else:
            operands.append(word)
    return operands, flags


def forms(git):
    """The forms of this git call that can drop work, the parser's and this guard's own."""
    found = set(git.get("discard") or ())
    subcommand, args = git.get("subcommand"), git.get("args") or []
    if subcommand == "checkout":
        operands, flags = _operands(args, CHECKOUT_VALUES)
        if any(_whole(word) for word in operands) or any(f.startswith("--pathspec-from") for f in flags):
            found.add("whole-tree checkout")
    if subcommand == "restore":
        operands, flags = _operands(args, RESTORE_VALUES)
        staged_only = flags & {"-S", "--staged"} and not flags & {"-W", "--worktree"}
        whole = any(_whole(word) for word in operands) or any(f.startswith("--pathspec-from") for f in flags)
        if whole and not staged_only:
            found.add("whole-tree restore")
    if subcommand == "stash" and git.get("action") in STASH_WRITES:
        found.add("stash write")
    if subcommand in ("rebase", "cherry-pick"):
        found.add(subcommand)
    if git.get("pull_rebase"):
        found.add("pull --rebase")
    return found


def _holder(lease):
    holder = lease.get("holder") or {}
    if not holder:
        return "a session whose lease cannot be read"
    since = ""
    if isinstance(holder.get("taken"), (int, float)):
        since = " since " + datetime.datetime.fromtimestamp(holder["taken"]).strftime("%Y-%m-%d %H:%M")
    return f"session {str(holder.get('session', '?'))[:8]}{since}"


def decide(event, config):
    lease = event.get("lease") or {}
    if lease.get("state") in QUIET:
        return None
    copies = event.get("working_copies") or {}
    own = event.get("own_working_copy")
    who = _holder(lease)
    calls, why_aliases = gitrules.read(event)
    for call in calls:
        why = gitrules.unresolved(call, why_aliases)
        if why:
            return (f"another live agent session ({who}) holds the main working copy, and this command cannot be "
                    f"judged: {why}. Write it with literal words, or run it in a worktree of your own. See {PAGE}")
        git = call.get("git")
        if not git:
            continue
        found = forms(git)
        if not found:
            continue
        changed = gitrules.config_write(call)
        if changed:
            return (f"another live agent session ({who}) holds the main working copy, and {changed}, so this guard "
                    f"cannot judge it. Run it without that setting. See {PAGE}")
        folder = git.get("folder")
        fact = copies.get(folder) if folder is not None else None
        if folder is None or not fact or fact.get("unresolved"):
            reason = git.get("folder_unresolved") or (fact or {}).get("unresolved") or "no fact for its folder"
            return (f"another live agent session ({who}) holds the main working copy, and the folder this "
                    f"git {git.get('subcommand')} acts on cannot be placed ({reason}). Run it from a worktree of "
                    f"your own, with a literal folder. See {PAGE}")
        kind = fact.get("kind")
        if kind == "other":
            continue
        shared = sorted(found & SHARED)
        if shared:
            return (f"git {shared[0]} reaches the stash or the worktree list every working copy shares, and "
                    f"another live agent session ({who}) is working here, and no one can tell whose entry it is. "
                    f"Leave them. To set work aside, commit it on your own branch instead of stashing; to get a "
                    f"stash of your own back, use git stash apply with its id. See {PAGE}")
        if "worktree remove --force" in found:
            for operand in _remove_operands(git):
                target = copies.get(posixpath.join(folder, operand))
                if not target or target.get("unresolved"):
                    return (f"another live agent session ({who}) is working here, and the worktree {operand} "
                            f"cannot be placed. Remove only your own worktree, without --force. See {PAGE}")
                if target.get("kind") == "main" or (target.get("kind") == "linked" and target.get("top") != own):
                    return (f"git worktree remove --force {operand} removes a worktree another session may be "
                            f"working in, while another live agent session ({who}) is on record. Remove only "
                            f"your own worktree. See {PAGE}")
        if kind == "main":
            drops = sorted(found & MAIN_ONLY)
            if drops:
                return (f"git {drops[0]} in the main working copy can drop the work of another live agent session "
                        f"({who}), which holds it. Work in a worktree of your own, started from the remote's main so "
                        f"it holds none of that session's commits: git worktree add --no-track -b BRANCH "
                        f".claude/worktrees/NAME origin/main, and run it there. See {PAGE}")
    return None


def _remove_operands(git):
    args = git.get("args") or []
    rest = args[1:] if args[:1] == ["remove"] else args
    operands, ended = [], False
    for word in rest:
        if not ended and word == "--":
            ended = True
        elif ended or not word.startswith("-"):
            operands.append(word)
    return operands
