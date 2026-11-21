"""Hook: while another live session holds the main working copy, refuse a git push from it.

The main working copy has one local main and one set of branches, shared by every session that works there. A
push from it by a session that does not hold the lease can publish the holder's unpushed commits, which the
holder has not finished. This guard is active only while the writing-session lease is held by a live session
other than this one (decision 0005), so a person working with one session, and the lease holder itself, see no
change. A lease that cannot be read counts as held.

While it is active, it refuses:

- a `git push` whose folder is the main working copy, in any form, except `--dry-run`, which publishes nothing;
- a `git push` whose folder the parser or the runner could not place;
- a command it cannot judge: a program or git subcommand that is a variable, a git alias it does not read, or
  arguments supplied when it runs, any of which may be a push.

A push from a linked worktree, or from another repository, passes: it publishes only that working copy's
commits. The runner gives the lease and each git folder's kind (decision 0004, "Shell events"); this part reads
the command with the shared parser, wslib/shell.py, and looks each call's folder up by the parser's own text.
See docs/decisions/0005-concurrent-sessions-and-the-edit-ledger.md.
"""
import datetime

from wslib import shell

KIND = "hook"
EVENT = "before-shell"
NEEDS = ("session", "lease", "working_copies")
PAGE = "docs/decisions/0005-concurrent-sessions-and-the-edit-ledger.md"

QUIET = ("free", "mine", "other-dead")


def _holder(lease):
    holder = lease.get("holder") or {}
    if not holder:
        return "a session whose lease cannot be read"
    since = ""
    if isinstance(holder.get("taken"), (int, float)):
        since = " since " + datetime.datetime.fromtimestamp(holder["taken"]).strftime("%Y-%m-%d %H:%M")
    return f"session {str(holder.get('session', '?'))[:8]}{since}"


def _unresolved(call):
    """Why the guard cannot tell whether this call pushes, or None."""
    if call.get("unresolved"):
        return call["unresolved"]
    git = call.get("git")
    if not git:
        return None
    if git.get("unresolved"):
        return git["unresolved"]
    if git.get("subcommand") is not None and not git.get("builtin"):
        return f"git {git['subcommand']} is not one of git's own commands, and its alias is not read here"
    if call.get("runtime_args"):
        return f"{call['runtime_args']} supplies git's arguments when it runs"
    return None


def decide(event, config):
    lease = event.get("lease") or {}
    if lease.get("state") in QUIET:
        return None
    copies = event.get("working_copies") or {}
    who = _holder(lease)
    for call in shell.analyze(event.get("command") or ""):
        why = _unresolved(call)
        if why:
            return (f"another live agent session ({who}) holds the main working copy, and this command cannot be "
                    f"judged: {why}. A push from there would publish that session's commits. Write it with "
                    f"literal words, or run it in a worktree of your own. See {PAGE}")
        git = call.get("git")
        if not git or git.get("subcommand") != "push" or (git.get("push") or {}).get("dry_run"):
            continue
        folder = git.get("folder")
        fact = copies.get(folder) if folder is not None else None
        if folder is None or not fact or fact.get("unresolved"):
            reason = git.get("folder_unresolved") or (fact or {}).get("unresolved") or "no fact for its folder"
            return (f"another live agent session ({who}) holds the main working copy, and the folder this git "
                    f"push acts on cannot be placed ({reason}). Push from a worktree of your own, with a literal "
                    f"folder. See {PAGE}")
        if fact.get("kind") == "main":
            return (f"a git push from the main working copy can publish the unpushed commits of another live agent "
                    f"session ({who}), which holds it. Commit in a worktree of your own and push from there: git "
                    f"worktree add .claude/worktrees/NAME -b BRANCH. See {PAGE}")
    return None
