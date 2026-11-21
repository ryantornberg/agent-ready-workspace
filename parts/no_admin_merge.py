"""Hook: refuse a pull-request merge past CI, and any merge that is not a merge commit.

GitHub's branch rule requires CI to pass on Linux, macOS and Windows before a pull request merges to main. It does
not bind the repository's owner: `gh pr merge --admin` merges past red CI, and an agent using the owner's sign-in
can run it. This hook refuses that command.

It also refuses a merge that rewrites the branch's commits: `gh pr merge --squash` or `--rebase`, in their short
forms too, and a `gh api` call to a pull request's merge endpoint whose `merge_method` is not the literal `merge`.
A squash or rebase merge leaves the branch's own commits unreachable from main once the branch is deleted, and a
proof anchor pinned to one of them then names a commit main does not hold (decision record 0006). A call whose
body the hook cannot read, from `--input` or a field read from a file, is refused too, and so is any API write whose
path is a variable or a substitution. So is a GraphQL call that
merges a pull request, or turns on auto-merge, with a method other than `MERGE`, or whose query the hook cannot
read. A merge without a method flag goes ahead: gh then asks, and refuses to guess when no one can answer.

It reads the command line with the shared parser, wslib/shell.py, so it follows separators, new lines, subshells,
`sh -c`, `eval` and wrappers, and skips heredoc bodies and quoted text. It cannot see a merge made another way: another
program such as `curl`, a `gh` alias, a script, an interpreter, or the web page. The repository's settings, which
allow merge commits only, close those. See docs/changing-the-machinery.md.
"""
import re

from wslib import shell

KIND = "hook"
EVENT = "before-shell"
PAGE = "docs/changing-the-machinery.md"
# gh pr merge's options that take a value, so the value is not read as a flag: -b "--squash" is a body.
LONG_VALUES = {"--author-email", "--body", "--body-file", "--subject", "--match-head-commit", "--repo"}
SHORT_VALUES = set("AbFtR")
REWRITES = {"--squash": "--squash", "--rebase": "--rebase", "s": "--squash", "r": "--rebase"}
MERGE_ENDPOINT = re.compile(r"^repos/[^/]+/[^/]+/pulls/[^/]+/merge$")
GRAPHQL_MERGES = ("mergePullRequest", "enablePullRequestAutoMerge")


def _on(argument):
    """True for --flag, and for --flag=value unless the value is false."""
    return "=" not in argument or argument.split("=", 1)[1].lower() != "false"


def merge_flags(arguments):
    """The flags of a gh pr merge that this hook refuses: --admin, --squash and --rebase, however written."""
    found, skip = [], False
    for argument in arguments:
        if skip:
            skip = False
            continue
        if argument == "--":
            break
        if argument.startswith("--"):
            name = argument.split("=", 1)[0]
            if name in LONG_VALUES:
                skip = "=" not in argument
            elif name in ("--admin", "--squash", "--rebase") and _on(argument):
                found.append(name)
            continue
        if argument.startswith("-") and len(argument) > 1:
            for k, letter in enumerate(argument[1:]):
                if letter in SHORT_VALUES:
                    skip = k == len(argument) - 2          # the value is the next word only when none follows
                    break
                if letter in REWRITES:
                    found.append(REWRITES[letter])
    return found


def _api_merge(api):
    """Why a gh api call is a merge this hook refuses, or None."""
    if api.get("dynamic") or api.get("endpoint") is None:
        if api.get("effective_method") in ("GET", "HEAD"):
            return None
        return "a write to an API path it cannot read, which may be a pull request's merge endpoint"
    if api.get("graphql"):
        texts = [field.get("value") or "" for field in api.get("fields") or ()]
        if api.get("input") or any(field.get("file") or field.get("dynamic") for field in api.get("fields") or ()):
            return "a GraphQL call whose query is read from a file or a variable, which may merge a pull request"
        for text in texts:
            if any(name in text for name in GRAPHQL_MERGES):
                methods = re.findall(r"mergeMethod\s*:\s*(\$?\w+)", text)
                if any(method != "MERGE" for method in methods):
                    return f"a GraphQL merge with mergeMethod {next(m for m in methods if m != 'MERGE')}"
                if not methods and "enablePullRequestAutoMerge" in text:
                    return "a GraphQL auto-merge that names no mergeMethod"
        return None
    if not MERGE_ENDPOINT.match(api.get("path") or "") or api.get("effective_method") in ("GET", "HEAD"):
        return None
    if api.get("input"):
        return "a merge whose body is read from --input, so its merge_method cannot be read"
    for field in api.get("fields") or ():
        if field.get("key") != "merge_method":
            continue
        if field.get("dynamic") or field.get("file"):
            return "a merge whose merge_method is a variable or is read from a file"
        if field.get("value") != "merge":
            return f"a merge with merge_method {field.get('value')!r}"
    return None


def decide(event, config):
    for call in shell.analyze(event.get("command") or ""):
        gh = call.get("gh")
        if not gh:
            continue
        if gh.get("path", [])[:2] == ["pr", "merge"]:
            found = merge_flags(gh.get("args") or [])
            if "--admin" in found:
                return ("gh pr merge --admin merges past the CI that GitHub's branch rule requires. Wait until every "
                        f"required CI job passes, then merge with python3 ws.py merge NUMBER; see {PAGE}")
            if found:
                return (f"gh pr merge {found[0]} rewrites the branch's commits, and a proof anchor pinned to one of "
                        f"them would name a commit main does not hold. Merge with a merge commit: python3 ws.py "
                        f"merge NUMBER, or gh pr merge NUMBER --merge; see {PAGE}")
        elif gh.get("path", [])[:1] == ["api"] and gh.get("api"):
            why = _api_merge(gh["api"])
            if why:
                return (f"gh api makes {why}. Only a merge commit keeps a branch's commits on main. Merge with "
                        f"python3 ws.py merge NUMBER; see {PAGE}")
    return None
