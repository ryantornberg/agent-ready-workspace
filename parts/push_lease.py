"""Hook: while another live session holds the main working copy, refuse a git push from it.

The main working copy has one local main and one set of branches, shared by every session that works there. A
push from it by a session that does not hold the lease can publish the holder's unpushed commits, which the
holder has not finished. This guard is active only while the writing-session lease is held by a live session
other than this one (decision 0005), so a person working with one session, and the lease holder itself, see no
change. A lease that cannot be read counts as held.

While it is active, it refuses:

- a `git push` whose folder is the main working copy, in any form, except `--dry-run`, which publishes nothing;
- a `git push` whose folder the parser or the runner could not place;
- a command it cannot judge: a program or git subcommand that is a variable, a git subcommand that is neither
  built in nor an alias at hook time, or arguments supplied when it runs, any of which may be a push;
- a push with HOME, XDG_CONFIG_HOME or a GIT_CONFIG_* variable set on it, or an include given by -c or
  GIT_CONFIG_*, from any working copy: each counts as a config write.

A git alias is expanded from config at hook time, so a stored alias that pushes is judged as a push, and
`git -c alias.push=status push` is a push, since git ignores an alias of its own command's name. A push from a
linked worktree, or from another repository, passes: it publishes only that working copy's commits. The runner
gives the lease, each git folder's kind and the aliases read in each folder (decision 0004, "Shell events"); this
part reads the command through wslib/gitrules.py and looks each call's folder up by the parser's own text.
See docs/decisions/0005-concurrent-sessions-and-the-edit-ledger.md.
"""
import datetime

from wslib import gitrules

KIND = "hook"
EVENT = "before-shell"
NEEDS = ("session", "lease", "working_copies", "aliases")
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


def decide(event, config):
    lease = event.get("lease") or {}
    if lease.get("state") in QUIET:
        return None
    copies = event.get("working_copies") or {}
    who = _holder(lease)
    calls, why_aliases = gitrules.read(event)
    for call in calls:
        why = gitrules.unresolved(call, why_aliases)
        if why:
            return (f"another live agent session ({who}) holds the main working copy, and this command cannot be "
                    f"judged: {why}. A push from there would publish that session's commits. Write it with "
                    f"literal words, or run it in a worktree of your own. See {PAGE}")
        git = call.get("git")
        if not git or git.get("subcommand") != "push" or (git.get("push") or {}).get("dry_run"):
            continue
        changed = gitrules.config_write(call)
        if changed:
            return (f"another live agent session ({who}) holds the main working copy, and {changed}, so this guard "
                    f"cannot judge it. Run it without that setting. See {PAGE}")
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
