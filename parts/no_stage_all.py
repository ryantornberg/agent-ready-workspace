"""Hook: remind the agent when a shell command stages everything.

Another session, or the person, may have edits in the same folder. "Stage
everything" sweeps those into this commit under the wrong message. Staging by
name cannot.

It reminds; it does not refuse. The commit check enforces the rule
(parts/edit_ledger.py): it compares what is staged with what the session's
edit tools wrote, whatever command staged it. The runner opens that ledger
when this hook fires and the session's working copy has uncommitted changes,
so the comparison runs even for a session that wrote its files only through
the shell. A command line cannot say which repository
it stages in, or what a pathspec covers, so a refusal here was both too wide,
as for `git add .` in a scratch repository, and too narrow, as for a script.
See docs/decisions/0002-hooks-remind-the-commit-enforces.md.

It reads the command line; it does not run a shell. It follows separators,
new lines, subshells, `sh -c "..."`, `eval` and common wrappers, and it skips
heredoc bodies and quoted text, so a commit message may mention the commands
it refuses. It cannot see through a shell alias, a script, a variable that
holds the command, or a command piped into a shell, and it cannot tell that
`git add src` names a whole folder. The README's Limits say so.

The parser lives in wslib/shell.py, shared with no_admin_merge. The eval grader
uses the same function, so the rule an agent is tested against is the rule the
hook enforces, and the eval hash covers that module with this file.
"""
import re

from wslib import shell

KIND = "hook"
EVENT = "before-shell"
MODE = "remind"

EVERYTHING = re.compile(r"^(?::/\*?|[./*]+)$")   # .  ./  *  ./*  ../..  :/
_long = shell.long_option


def stages_everything(command):
    """The reason a command stages more than it names, or None."""
    for subcommand, arguments in shell.git_calls(command or ""):
        short, longs, specs = shell.options(subcommand, arguments)
        if subcommand in ("add", "stage"):
            every = short & {"A", "u"} or any(_long(a, "--all") or _long(a, "--update") for a in longs)
            if any(EVERYTHING.match(a) for a in specs) or (every and not specs):
                return "git add of everything"
        elif subcommand == "commit":
            if "a" in short or any(_long(a, "--all") for a in longs):
                return "git commit -a stages every tracked change"
            if any(EVERYTHING.match(a) for a in specs):
                return "git commit of the whole folder"
    return None


def decide(event, config):
    reason = stages_everything(event.get("command"))
    if reason:
        return (f"This command stages more than it names ({reason}). Another session, or the person, may have "
                "edits in this folder. Stage the files this session changed, by name, and check what is staged "
                "with: git diff --cached --name-only")
    return None
