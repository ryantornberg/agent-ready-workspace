"""Hook: refuse an agent's write to a repository outside the instance's list, and an approval anywhere.

Agents here may open, publish and merge their own pull requests once CI passes. They write on no repository
other people own. The instance's list of repositories is a file of its own, `outward-repos.json`, which the
manifest names in "list" and which only a person edits (`outward_list` refuses an edit tool's write to it, and
this hook a shell write the parser reports). An adopted instance starts with an empty list. M3 slice C5e.

On a repository not in the list, `gh` may run only the read subcommands in READS, and `gh api` only a read: a
call whose method is GET, or that has no method, no field flag and no `--input`. Everything else is refused: any
other gh subcommand, a `gh api` write, a gh write that names no repository (`gh gist create`, `gh api user -X
PATCH`), and a `git push` that reaches it. Where a call really goes is worked out by the runner (decision 0004,
"Shell events"): for gh, `-R` or `--repo`, then `GH_REPO`, then gh's set-default value, then the only remote, and
for `gh api` the owner and repository in its path; for a push, every URL git would push to. A local path or a
`file://` URL counts as inside the instance; an scp-style `host:path` is not a local path.

On every repository, this one included:

- an approval is refused: `gh pr review --approve`, a `gh api` reviews call whose `event` is APPROVE or is not a
  literal, or that reads its body from `--input` or a field from a file, and the approval of a workflow run or a
  deployment;
- every `gh api graphql` call is refused, a plain query included, since a node id names no repository and nothing
  here needs GraphQL.

`git remote add` and `set-url` to a URL outside the list are refused. A push is also refused when it sets one of
the keys the guards read with `-c`, `--config-env` or a GIT_CONFIG_* variable, or sets HOME and the rest
(wslib/gitrules.py, `config_write`), and when a call earlier in the line changes where it goes: a `git remote`
write, or a gh call that can add a remote such as `gh pr checkout`, before any push, and for a push that names no
remote, a change of branch or upstream as well.

It also refuses `git send-pack` and `git http-push` to a URL outside the list, a push that recurses into
submodules on demand, and `git mv`, `rm`, `checkout` or `restore` naming the list. A URL matches an entry of the
list by its host and its whole path, so a GitLab group nested under another is a different repository.

It refuses a command it cannot judge, as the other shell guards do: a program word that is a variable, text piped
into a shell, an alias that runs a shell command or that it could not read, a gh subcommand that is a variable
or is not one of gh's own (a gh alias or extension may run anything), arguments that `xargs` or `find -exec` give
gh or git push, a remote URL that is a variable, and a target the runner could not work out. A read subcommand
from READS with arguments `xargs` supplies passes, since none of gh's arguments turns a read into a write.
See docs/decisions/0004-the-hook-contract.md.
"""
import posixpath
import re

from wslib import gitrules

KIND = "hook"
EVENT = "before-shell"
NEEDS = ("targets", "destinations", "aliases", "repositories")
PAGE = "docs/decisions/0004-the-hook-contract.md"

# The gh subcommands allowed on any repository: each reads, and none writes anything another person can see.
READS = {
    ("pr", "list"), ("pr", "ls"), ("pr", "view"), ("pr", "diff"), ("pr", "checks"), ("pr", "status"),
    ("pr", "checkout"), ("pr", "co"),
    ("issue", "list"), ("issue", "ls"), ("issue", "view"), ("issue", "status"),
    ("repo", "view"), ("repo", "list"), ("repo", "ls"), ("repo", "clone"),
    ("release", "list"), ("release", "ls"), ("release", "view"), ("release", "download"),
    ("run", "list"), ("run", "ls"), ("run", "view"), ("run", "watch"), ("run", "download"),
    ("workflow", "list"), ("workflow", "ls"), ("workflow", "view"),
    ("label", "list"), ("label", "ls"),
    ("search", "repos"), ("search", "issues"), ("search", "prs"), ("search", "code"), ("search", "commits"),
    ("gist", "list"), ("gist", "ls"), ("gist", "view"),
    ("cache", "list"), ("cache", "ls"), ("ruleset", "list"), ("ruleset", "ls"), ("ruleset", "view"),
    ("ruleset", "check"), ("rs", "list"), ("rs", "ls"), ("rs", "view"), ("rs", "check"),
    ("secret", "list"), ("secret", "ls"), ("variable", "list"), ("variable", "ls"), ("variable", "get"),
    ("auth", "status"), ("config", "get"), ("config", "list"), ("config", "ls"), ("alias", "list"),
    ("alias", "ls"), ("extension", "list"), ("extension", "ls"), ("ext", "list"), ("ext", "ls"),
    ("project", "list"), ("project", "ls"), ("project", "view"), ("project", "field-list"),
    ("project", "item-list"),
    ("status",), ("help",), ("version",), ("completion",), ("browse",),
}
# gh writes that create a repository or act on an owner's account rather than on one repository, so no listed
# repository can hold them: gh's runner-worked target would name the folder's repository instead.
NEW_REPOSITORY = {("repo", "create"), ("repo", "fork")}
OWNER_WRITES = {"project"}
OWNER_FLAGS = {"--org", "-o", "--user", "-u"}
# git subcommands that push without `git push`: each names its destination as its first operand.
PLUMBING_PUSHES = {"send-pack", "http-push"}
# Their options that take the next word as a value, when not written with "=".
PLUMBING_VALUES = {"--receive-pack", "--exec", "--push-option", "-o", "--signed", "--force-with-lease"}
# gh calls that can add a remote or set a branch's upstream, so a later push may go somewhere the guard did not see.
GH_REMOTE_CHANGES = {("pr", "checkout"), ("pr", "co"), ("repo", "fork"), ("repo", "set-default"), ("repo", "clone")}
# gh's own top-level commands. Any other first word is a gh alias or an extension, which may run anything.
GH_COMMANDS = {"pr", "issue", "repo", "release", "gist", "run", "workflow", "secret", "variable", "label",
               "project", "codespace", "cs", "cache", "ruleset", "rs", "attestation", "at", "auth", "config",
               "extension", "ext", "extensions", "gpg-key", "ssh-key", "org", "search", "alias", "completion",
               "preview", "agent-task", "api", "browse", "status", "help", "version", "copilot"}
# gh pr review's options that take a value, so the value is not read as a flag.
REVIEW_LONG_VALUES = {"--body", "--body-file", "--repo"}
REVIEW_SHORT_VALUES = set("bFR")
REVIEWS = re.compile(r"^repos/[^/]+/[^/]+/pulls/[^/]+/reviews(/|$)")
APPROVALS = re.compile(r"^repos/[^/]+/[^/]+/actions/runs/[^/]+/(approve|pending_deployments)$")
OVERRIDE = re.compile(r"^\s*x-http-method-override\s*:", re.I)


def _dynamic(text):
    return "$" in text or "`" in text


def _cannot_judge(why):
    return (f"this command cannot be judged: {why}, so it may write to a repository outside this instance's list. "
            f"Write it with literal words. See {PAGE}")


# -- writes onto the list ------------------------------------------------------------------------------------------

def _list_write(call, name):
    """Why a shell write in this call lands on the list of repositories, or None. The list is matched by its file
    name in any folder, so a write to it from a worktree, or through a folder the parser cannot place, is seen."""
    wanted = gitrules.fold(posixpath.basename(name.replace("\\", "/")))
    for write in call.get("writes") or ():
        path = write.get("path") or ""
        if gitrules.fold(path).split("/")[-1] == wanted or (write.get("dynamic") and wanted in gitrules.fold(path)):
            return (f"{path} is the list of repositories agents may write to. Only a person adds a repository to "
                    f"it, from their own terminal. See {PAGE}")
    return None


# -- calls it cannot judge -----------------------------------------------------------------------------------------

def _git_unresolved(call, why_aliases):
    """Why a git call that may push or change a remote cannot be judged, or None."""
    git = call["git"]
    subcommand = git.get("subcommand")
    program = subcommand is not None and not git.get("builtin") and not git.get("alias") and not _dynamic(subcommand)
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
        return None                         # a program named git-NAME: neither a push nor git remote
    alias = git.get("alias") or {}
    if alias.get("source") == "config" and (call.get("config_env") or gitrules.config_write(call)):
        return gitrules.unresolved(call) or f"git {alias['name']} is an alias read from config the command changes"
    if subcommand in ("push", "remote") and call.get("runtime_args"):
        return f"{call['runtime_args']} supplies git {subcommand}'s arguments when it runs"
    return None


def _gh_unresolved(call):
    """Why a gh call cannot be judged, or None."""
    gh = call["gh"]
    if gh.get("unresolved"):
        return gh["unresolved"]
    path = gh.get("path") or []
    if any(_dynamic(word) for word in path):
        return "the gh subcommand is a variable or a substitution"
    if path and path[0] not in GH_COMMANDS:
        return f"gh {path[0]} is not one of gh's own commands; a gh alias or extension may run anything"
    if call.get("runtime_args") and (path[:1] in ([], ["api"]) or not _is_read_path(path)):
        return f"{call['runtime_args']} gives gh {' '.join(path) or 'its subcommand'} its arguments when it runs"
    return None


# -- gh ------------------------------------------------------------------------------------------------------------

def _is_read_path(path):
    return tuple(path[:2]) in READS or tuple(path[:1]) in READS


def _approves(arguments):
    """True when gh pr review's arguments approve: --approve, -a, or -a inside a group of short flags."""
    skip = False
    for argument in arguments:
        if skip:
            skip = False
            continue
        if argument == "--":
            break
        if argument.startswith("--"):
            name = argument.split("=", 1)[0]
            if name in REVIEW_LONG_VALUES:
                skip = "=" not in argument
            elif name == "--approve" and ("=" not in argument or argument.split("=", 1)[1].lower() != "false"):
                return True
            continue
        if argument.startswith("-") and len(argument) > 1:
            for k, letter in enumerate(argument[1:]):
                if letter in REVIEW_SHORT_VALUES:
                    skip = k == len(argument) - 2
                    break
                if letter == "a":
                    return True
    return False


def _approval(call):
    """Why a gh call approves, or may, on any repository, or None."""
    gh = call["gh"]
    path = gh.get("path") or []
    if path[:2] == ["pr", "review"]:
        if _approves(gh.get("args") or []):
            return "gh pr review --approve approves a pull request"
        args, rest = call.get("args") or [], gh.get("args") or []
        start = len(args) - len(rest)
        if any(index >= start for index in call.get("dynamic_args") or ()):
            return "an argument of gh pr review is a variable or a substitution, and could be --approve"
        return None
    api = gh.get("api") if path[:1] == ["api"] else None
    if not api:
        return None
    api_path = api.get("path") or ""
    if APPROVALS.match(api_path) and api.get("effective_method") != "GET":
        return "it approves a workflow run or a deployment"
    if not REVIEWS.match(api_path):
        return None
    if api.get("input"):
        return "a reviews call reads its body from --input, so its event cannot be read"
    for field in api.get("fields") or ():
        if field.get("file"):
            return "a reviews call reads a field from a file, so its event cannot be read"
        if field.get("dynamic") and (field.get("key") in (None, "event") or _dynamic(field.get("key") or "")):
            return "a reviews call's event is a variable or a substitution"
        if (field.get("key") or "").lower() == "event" and (field.get("value") or "").strip().upper() == "APPROVE":
            return "a reviews call with event APPROVE approves a pull request"
    return None


def _gh_read(call):
    """True for a gh call that only reads: a subcommand in READS, or a gh api call whose method is GET."""
    gh = call["gh"]
    path = gh.get("path") or []
    if not path:
        return True                          # gh alone, or with flags only, prints help
    if path[:1] == ["api"]:
        api = gh.get("api") or {}
        if api.get("dynamic"):
            return False
        overridden = any(OVERRIDE.match(header or "") for header in api.get("headers") or ())
        return api.get("effective_method") == "GET" and not overridden
    return _is_read_path(path)


def _name(destination):
    if destination.get("local"):
        return f"the local path {destination.get('path')}"
    if destination.get("owner") and destination.get("name"):
        path = destination.get("path") or f"{destination['owner']}/{destination['name']}"
        return f"{destination.get('host')}/{path}"
    return destination.get("url") or f"{destination.get('host')} with no repository named"


class _List:
    """The list of repositories, read from the event the first time a write needs it."""

    def __init__(self, event):
        self.event, self._fact = event, None

    def fact(self):
        if self._fact is None:
            found = self.event.get("repositories")
            self._fact = found if isinstance(found, dict) else {"repositories": [], "unresolved": "it was not read"}
        return self._fact

    def unlisted(self, destination):
        return not gitrules.listed(destination, self.fact().get("repositories") or [])

    def refusal(self, what, destination):
        fact = self.fact()
        broken = f" The list cannot be used ({fact['unresolved']}), so no repository is on it." \
            if fact.get("unresolved") else ""
        return (f"{what} writes to {_name(destination)}, which is not in this instance's list of repositories "
                f"({fact.get('file') or 'outward-repos.json'}).{broken} Agents write only to the repositories a "
                f"person listed there; give the person the text to post or the change to push instead. See {PAGE}")


def _earlier_target_change(calls, index):
    """Why a call earlier in the line changes the repository a gh call acts on, or None: gh repo set-default, or a
    git remote write, which changes gh's default or the only remote. The runner worked the target out before."""
    for call in calls[:index]:
        if ((call.get("gh") or {}).get("path") or [])[:2] == ["repo", "set-default"]:
            return "gh repo set-default earlier in the line changes the repository gh's commands act on"
        git = call.get("git") or {}
        if git.get("subcommand") == "remote" and git.get("action") not in gitrules.READ_ONLY_REMOTE:
            return "git remote earlier in the line changes a remote, which can change the repository gh acts on"
    return None


def _gh(call, calls, index, event, repos):
    gh = call["gh"]
    path = gh.get("path") or []
    shown = "gh " + " ".join(path) if path else "gh"
    if path[:1] == ["api"] and (gh.get("api") or {}).get("graphql"):
        return (f"gh api graphql is refused on every repository, this one included, a plain query too: it names its "
                f"target by node ids, which name no repository, so no list can hold it, and nothing here needs it. "
                f"Use gh's own subcommands or a REST path under repos/OWNER/REPO. See {PAGE}")
    approval = _approval(call)
    if approval:
        return (f"{shown} is refused on every repository, this one included: {approval}. An agent never approves; "
                f"a person reviews and approves. See {PAGE}")
    if _gh_read(call):
        return None
    earlier = _earlier_target_change(calls, index)
    if earlier:
        return (f"{earlier}, and the guard worked out where {shown} writes before that call runs. Run the two "
                f"commands one at a time. See {PAGE}")
    owner = _owner_write(gh)
    if owner:
        return (f"{shown} {owner}, which no listed repository holds. Only the read subcommands run outside a listed "
                f"repository. See {PAGE}")
    fact = (event.get("targets") or {}).get(gitrules.target_key(call))
    if not isinstance(fact, dict):
        return _cannot_judge(f"where {shown} writes was not worked out")
    if fact.get("unresolved"):
        return _cannot_judge(f"where {shown} writes is unknown ({fact['unresolved']})")
    if fact.get("no_repository") or not fact.get("destinations"):
        return (f"{shown} writes, and names no repository, so it cannot be held to this instance's list. Only the "
                f"read subcommands run outside a listed repository. See {PAGE}")
    for destination in fact["destinations"] + _transfer(gh):
        if destination.get("local") or repos.unlisted(destination):
            return repos.refusal(shown, destination)
    return None


def _owner_write(gh):
    """Why a gh write acts on no single repository, or None."""
    path = tuple(gh.get("path") or [])
    if path[:2] in NEW_REPOSITORY:
        return "creates a repository"
    if path[:1] and path[0] in OWNER_WRITES:
        return "writes to an account's projects"
    if path[:1] and path[0] in ("secret", "variable"):
        flags = {word.split("=", 1)[0] for word in gh.get("args") or [] if word.startswith("-")}
        if flags & OWNER_FLAGS:
            return "writes to an organization's or a user's settings"
    return None


def _transfer(gh):
    """The repository `gh issue transfer ISSUE OWNER/REPO` moves an issue to, as a destination, or nothing."""
    if (gh.get("path") or [])[:2] != ["issue", "transfer"]:
        return []
    operands, skip = [], False
    for word in gh.get("args") or []:
        if skip:
            skip = False
        elif word in ("-R", "--repo"):
            skip = True
        elif not word.startswith("-"):
            operands.append(word)
    if len(operands) < 2:
        return [{"host": gh.get("host") or "github.com", "owner": None, "name": None, "url": None}]
    parts = operands[-1].split("/")
    if len(parts) == 2:
        return [{"host": gh.get("host") or "github.com", "owner": parts[0], "name": parts[1], "url": None}]
    if len(parts) == 3:
        return [{"host": parts[0], "owner": parts[1], "name": parts[2], "url": None}]
    return [{"host": None, "owner": None, "name": None, "url": operands[-1]}]


# -- git remote and git push ---------------------------------------------------------------------------------------

def _remote(call, repos):
    git = call["git"]
    remote = git.get("remote") or {}
    if remote.get("action") not in ("add", "set-url") or "--delete" in (git.get("args") or []):
        return None
    url = remote.get("url")
    if url is None:
        return None                          # git refuses it: no URL given
    if _dynamic(url):
        return _cannot_judge(f"the URL git remote {remote['action']} sets is a variable or a substitution")
    destination = gitrules.parse_url(url)
    if destination.get("local") or not repos.unlisted(destination):
        return None
    return repos.refusal(f"git remote {remote['action']} {url} sets a remote that", destination)


def _plumbing(call, repos):
    """git send-pack and git http-push push without git push. They are judged by the URL they name, read as it is
    written: git applies no insteadOf to it."""
    git = call["git"]
    operands, skip = [], False
    for word in git.get("args") or []:
        if skip:
            skip = False
        elif word in PLUMBING_VALUES:
            skip = True                      # its value is the next word, not the destination
        elif not word.startswith("-"):
            operands.append(word)
    shown = f"git {git['subcommand']}"
    if not operands or _dynamic(operands[0]) or call.get("runtime_args"):
        return _cannot_judge(f"where {shown} pushes is not written on the line")
    destination = gitrules.parse_url(operands[0])
    if destination.get("local") or not repos.unlisted(destination):
        return None
    return repos.refusal(shown, destination)


def _earlier_remote(calls, index):
    """Why a call earlier in the line than the call at index adds or changes a remote, or None: a git remote write,
    or a gh call that adds a remote or sets an upstream to another repository, such as gh pr checkout of a pull
    request from a fork. A remote it adds does not exist yet when the guard asks git, so its name would read as a
    local path."""
    for call in calls[:index]:
        git = call.get("git") or {}
        if git.get("subcommand") == "remote" and git.get("action") not in gitrules.READ_ONLY_REMOTE:
            return "git remote earlier in the line changes a remote, which decides where a push goes"
        path = tuple(((call.get("gh") or {}).get("path") or [])[:2])
        if path in GH_REMOTE_CHANGES:
            return f"gh {' '.join(path)} earlier in the line can add a remote or set an upstream"
    return None


def _recurses(git):
    """True when a push also pushes submodules, each to its own remote, which the guard does not work out: the
    option in any prefix git accepts (`--recu` on), or `submodule.recurse` or `push.recurseSubmodules` given on the
    command line by -c, --config-env or GIT_CONFIG_*."""
    args = list(git.get("args") or [])
    for index, word in enumerate(args):
        if word == "--":
            break
        name, equals, value = word.partition("=")
        if not (len(name) >= len("--recu") and "--recurse-submodules".startswith(name)):
            continue
        if not equals:
            value = args[index + 1] if index + 1 < len(args) else ""
        if value.lower() in ("on-demand", "only"):
            return True
    for entry in git.get("config") or ():
        key = (entry.get("key") or "").lower()
        value = (entry.get("value") or "true").lower() if not entry.get("dynamic") else "on-demand"
        if key == "submodule.recurse" and value not in ("false", "no", "off", "0"):
            return True
        if key == "push.recursesubmodules" and value in ("on-demand", "only"):
            return True
    return False


def _push(call, calls, index, event, repos):
    push = call["git"].get("push") or {}
    if push.get("dry_run"):
        return None
    changed = gitrules.config_write(call, every_guarded=True)
    if changed:
        return f"{changed}. This guard cannot tell where the push goes. Run it without that setting. See {PAGE}"
    if _recurses(call["git"]):
        return (f"--recurse-submodules pushes each submodule to its own remote, which this guard does not work out. "
                f"Push each repository on its own, such as with git -C src/NAME push. See {PAGE}")
    earlier = _earlier_remote(calls, index) or (gitrules.earlier_change(calls, index)
                                                if push.get("remote") is None else None)
    if earlier:
        return (f"{earlier}, and the guard worked out where this push goes before that call runs. Run the two "
                f"commands one at a time. See {PAGE}")
    fact = (event.get("destinations") or {}).get(gitrules.target_key(call))
    if not isinstance(fact, dict):
        return _cannot_judge("where the push goes was not worked out")
    if not fact.get("destinations"):
        return _cannot_judge(f"where the push goes is unknown ({fact.get('unresolved') or 'git named no URL'})")
    for destination in fact["destinations"]:
        if not destination.get("local") and repos.unlisted(destination):
            return repos.refusal("this push", destination)
    return None


def decide(event, config):
    name = config.get("list", "outward-repos.json")
    calls, why_aliases = gitrules.read(event)
    repos = _List(event)
    for index, call in enumerate(calls):
        why = _list_write(call, name)
        if why:
            return why
        if call.get("unresolved"):
            return _cannot_judge(call["unresolved"])
        expanded = gitrules.expanded_program(call)   # {gh,} pr create: no guard sees the gh it becomes (Q54)
        if expanded:
            return _cannot_judge(expanded)
        if call.get("gh"):
            why = _gh_unresolved(call)
            if why:
                return _cannot_judge(why)
            refused = _gh(call, calls, index, event, repos)
            if refused:
                return refused
            continue
        git = call.get("git")
        if not git:
            continue
        why = _git_unresolved(call, why_aliases)
        if why:
            return _cannot_judge(why)
        if git.get("subcommand") == "remote" and git.get("builtin", True):
            refused = _remote(call, repos)
        elif git.get("subcommand") == "push":
            refused = _push(call, calls, index, event, repos)
        elif git.get("subcommand") in PLUMBING_PUSHES:
            refused = _plumbing(call, repos)
        else:
            refused = None
        if refused:
            return refused
    return None
