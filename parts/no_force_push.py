"""Hook: refuse a force push, or a deletion, of the default branch.

A force push to main rewrites history every clone and every proof anchor builds on, and a deletion removes it.
GitHub's branch rule refuses both on this repository, but it does not bind every instance's host, and an owner can
turn it off; this guard refuses them before the command runs, in every form slice C5 names. It is always on: the
lease plays no part.

It judges each `git push` by what it would really send, from its words and from the target the runner worked out
with git (decision 0004, "Shell events": `targets`), so config a person set is applied as git applies it:
`pushurl`, `insteadOf`, `pushInsteadOf`, `remote.*.push`, `remote.*.mirror`, `push.default` and the upstream.
It refuses a push that would force or delete the branch named in "branch" (default "main"), on any destination:

- `--force` or `-f`, a `+` refspec, and a `--force-with-lease` with no ref or naming that branch, when the push
  sends that branch: by name, as `HEAD` while on it, or by push.default and the upstream with no refspec;
- `--all` or `--branches` with any force, `--mirror` written or configured, a glob refspec that may match the
  branch when forced, and `--prune` with a glob, `--all` or `--branches`;
- `--delete` or `-d` of the branch, and a refspec `:main`;
- a configured `remote.*.push` refspec that forces it.

`--force-with-lease` or `+` to another branch passes, and so does a push of the branch that only adds to it. A push
that names literal refspecs and asks for no force, deletion, prune or mirror passes without its target being worked
out, since no config can force it.

It also refuses a push it cannot judge, as the discard guard does: a remote or a refspec that is a variable or a
substitution, with a message pointing to `git push -u origin HEAD`; a target the runner could not work out; a
program or git subcommand that is a variable, an alias that runs a shell command, a git alias it could not read,
arguments `xargs` or `find -exec` supply to git; HOME, XDG_CONFIG_HOME, a GIT_CONFIG_* variable or a -c value that
changes a key the guards read, set on the push; and a forcing push after a call earlier in the line that changes
the branch, an upstream, a remote or gh's default (wslib/gitrules.py, `earlier_change`), since the runner worked
the target out before that call ran. A git alias is expanded from config, so a stored alias that force-pushes main
is refused, and one that pushes a branch passes. `--dry-run` publishes nothing and passes. A subcommand that is
neither built in nor an alias is a program named git-NAME, not a push, and passes.
See docs/decisions/0004-the-hook-contract.md.
"""
from wslib import gitrules

KIND = "hook"
EVENT = "before-shell"
NEEDS = ("targets", "aliases")
PAGE = "docs/decisions/0004-the-hook-contract.md"

HEAD_PUSH = "To push the current branch, write it as `git push -u origin HEAD`"


def _cannot_judge(why):
    return (f"this command may push, and no guard can tell whether it force-pushes the default branch: {why}. "
            f"Write it with literal words. See {PAGE}")


def _may_push(call, why_aliases):
    """Why a call that may be a push cannot be judged, or None. Only a git push, or a call that may be one."""
    if call.get("unresolved"):
        return call["unresolved"]
    git = call.get("git")
    if not git:
        return None
    subcommand = git.get("subcommand")
    program = subcommand is not None and not git.get("builtin") and not git.get("alias") and \
        not any(mark in subcommand for mark in "$`")
    if git.get("unresolved") and not program:
        return git["unresolved"]
    if subcommand is None:
        return f"{call['runtime_args']} supplies git's subcommand when it runs" if call.get("runtime_args") else None
    if not git.get("builtin"):
        changed = gitrules.config_write(call)
        if changed:
            return f"git {subcommand} is not one of git's own commands, and {changed}"
        if why_aliases:
            return f"git {subcommand} is not one of git's own commands, and {why_aliases}"
        return None                     # a git-NAME program: it is not git push
    alias = git.get("alias") or {}
    if alias.get("source") == "config" and (call.get("config_env") or gitrules.config_write(call)):
        return gitrules.unresolved(call) or f"git {alias['name']} is an alias read from config the command changes"
    if subcommand == "push" and call.get("runtime_args"):
        return f"{call['runtime_args']} supplies the push's arguments when it runs"
    return None


def _cannot_force(push):
    """True for a push that names literal refspecs and asks for no force, deletion, prune or mirror: config can
    force only a push with no refspec (`remote.*.push`), and a configured mirror refuses refspecs, so its target
    cannot change the answer and the runner need not work it out. A push is timed on a row of its own."""
    specs = push.get("refspecs") or []
    if not specs or push.get("remote_dynamic") or any(spec.get("dynamic") for spec in specs):
        return False
    if any(spec.get("force") or spec.get("delete") for spec in specs):
        return False
    return not (push.get("force") or push.get("force_with_lease") or push.get("delete") or push.get("prune")
                or push.get("mirror") or push.get("all") or push.get("branches"))


def _refusal(updates, branch):
    """Why these updates force or delete the branch, or None."""
    if updates["mirror"]:
        return f"--mirror, written or set in the remote's config, force-updates and deletes every branch, {branch} too"
    for update in updates["updates"]:
        if not gitrules.touches_branch(update, branch):
            continue
        what = "every branch" if update.get("every") else f"{update.get('dst')}"
        reaches = "" if what == branch else f", which reaches {branch}"
        if update.get("delete"):
            return f"it deletes {what}{reaches}"
        if update.get("force"):
            return f"it force-pushes {what}{reaches}"
        if updates["prune"] and (update.get("glob") or update.get("every")):
            return f"--prune with {what} deletes any branch the other side has and this one lacks, {branch} included"
    return None


def decide(event, config):
    branch = config.get("branch", "main")
    expanded = gitrules.unreadable(event.get("command"))   # {git,} push: the git it becomes goes unjudged (Q54, Q74)
    if expanded:
        return _cannot_judge(expanded)
    calls, why_aliases = gitrules.read(event)
    targets = None
    for index, call in enumerate(calls):
        why = _may_push(call, why_aliases)
        if why:
            return _cannot_judge(why)
        git = call.get("git")
        if not git or git.get("subcommand") != "push":
            continue
        push = git.get("push") or {}
        if push.get("dry_run"):
            continue
        changed = gitrules.config_write(call, every_guarded=True)
        if changed:
            return (f"{changed}. This guard cannot tell where the push goes or what it sends. Run it without that "
                    f"setting. See {PAGE}")
        if _cannot_force(push):
            continue
        if targets is None:
            targets = event.get("targets") or {}
        fact = targets.get(gitrules.target_key(call))
        updates = gitrules.push_updates(call, fact)
        if updates["unresolved"]:
            if push.get("remote_dynamic") or any(spec.get("dynamic") for spec in push.get("refspecs") or ()):
                return (f"this push names its remote or branch with a variable or a substitution, so no guard can "
                        f"tell whether it reaches {branch}. {HEAD_PUSH}. See {PAGE}")
            return (f"this guard cannot tell what this push sends: {updates['unresolved']}. Name the remote and the "
                    f"branch, as in `git push -u origin HEAD`, from a folder written literally. See {PAGE}")
        forcing = any(update.get("force") or update.get("delete") for update in updates["updates"]) or \
            updates["prune"] or updates["mirror"]
        earlier = gitrules.earlier_change(calls, index)
        if earlier and forcing:
            return (f"{earlier}, and the guard worked this push's target out before that call runs, so it cannot "
                    f"tell whether the forced push reaches {branch}. Run the two commands one at a time. See {PAGE}")
        refused = _refusal(updates, branch)
        if refused:
            return (f"a force push or deletion of {branch} rewrites the history every clone and proof anchor builds "
                    f"on, and this push would do it: {refused}. Push your own branch, such as with `git push -u origin "
                    f"HEAD`, and merge it through a pull request; --force-with-lease to your own branch is allowed. "
                    f"See {PAGE}")
    return None
