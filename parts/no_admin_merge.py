"""Hook: refuse a pull-request merge with GitHub's administrator flag.

GitHub's branch rule requires CI to pass on Linux, macOS and Windows before a pull
request merges to main. It does not bind the repository's owner: `gh pr merge
--admin` merges past red CI, and an agent using the owner's sign-in can run it.
This hook refuses that command. A merge without the flag goes ahead, and GitHub
then requires CI as usual.

It reads the command line with the parser `no_stage_all` uses, from
wslib/shell.py, so it follows the same separators, new lines, subshells, `sh -c`,
`eval` and wrappers, and skips heredoc bodies and quoted text. It cannot see a
merge made another way: a raw API call to the merge endpoint, a `gh` alias, or a
script. The machinery page says so. See docs/changing-the-machinery.md.
"""
from wslib import shell

KIND = "hook"
EVENT = "before-shell"
PAGE = "docs/changing-the-machinery.md"
GLOBAL_WITH_A_VALUE = {"-R", "--repo", "--hostname"}


def _admin(arguments):
    for argument in arguments:
        if argument == "--":
            return False
        if argument == "--admin" or (argument.startswith("--admin=") and argument.split("=", 1)[1].lower() != "false"):
            return True
    return False


def decide(event, config):
    for arguments in shell.calls(event.get("command") or "", "gh"):
        rest = list(arguments)
        while rest and rest[0].startswith("-"):
            rest = rest[2:] if rest[0] in GLOBAL_WITH_A_VALUE else rest[1:]
        if rest[:2] == ["pr", "merge"] and _admin(rest[2:]):
            return ("gh pr merge --admin merges past the CI that GitHub's branch rule requires. Wait until all five "
                    f"CI jobs pass, then merge without --admin; see {PAGE}")
    return None
