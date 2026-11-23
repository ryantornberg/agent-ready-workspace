"""The facts a before-shell hook may declare in NEEDS, worked out by the engine.

Decision 0004 (docs/decisions/0004-the-hook-contract.md), "Shell events". A guard reads the command with the
shared parser, wslib/shell.py, and looks up each call's facts by the text the parser gives. The runner keys
its facts by the same text from the same parser call, so a call whose key has no fact counts as unresolved
and is refused.

    session          {"session", "pid", "cwd", "own_working_copy"}
    lease            {"state": "free" | "mine" | "other-live" | "other-dead" | "unknown", "holder", "file"}
    working_copies   {folder text: {"kind": "main" | "linked" | "other", "top"} or {"unresolved": why}}
    targets          {target_key(call): {"destinations": [...], "no_repository": bool, "unresolved": why or None,
                                         "remote": name or None, "refspecs": [...] or None, "mirror": bool,
                                         "branch": name or None, "main_branch": name or None}}
    aliases          {folder text: {"aliases": {name: expansion}} or {"unresolved": why}}, for the folder of each
                     git call whose subcommand is not one of git's own (M3 slice C5c)
    git_config       {"home", "files": [...], "unresolved": why or None}: the git config files a write must not
                     reach, the global ones and every file an include names (M3 slice C5c); before-edit too
    repositories     {"file", "repositories": [{"host", "owner", "name"}], "unresolved": why or None}: the
                     outward-write list, read from the file the hook's config names (M3 slice C5e)
    destinations     {target_key(call): {"destinations": [...], "unresolved": why or None}}: where each git push
                     goes, and nothing else, in one git call for a push that names a remote (M3 slice C5e)

A folder is the parser's folder for a git call, read from the session's folder. Its kind comes from git:
the folder's git folder and common git folder. A `git worktree remove` operand, joined to the call's folder,
is keyed too. Every git call goes through wslib/gitcall.py's environment, with a time limit.

A target is where a gh call or a `git push` really goes. A destination is {"host", "owner", "name", "url"} or,
for a local path or a file:// URL, {"local": True, "path", "url"}. For gh: `gh api`'s literal owner and
repository, with {owner} and {repo} filled from GH_REPO, then gh's set-default value, then the only remote;
for any other gh call, -R or --repo, then GH_REPO, then the set-default value, then the only remote. For a push:
every URL git would push to, from `git remote get-url --push --all` with the command's own config values, or,
for a URL on the command line, the URL with the longest `pushInsteadOf` applied, else the longest `insteadOf`.
With no refspec, the branch push.default and the upstream send, in "refspecs". Anything not modelled is unresolved. A push also gives "branch", the branch
checked out in its folder, and "main_branch", the one checked out in the main working copy of that repository
(M3 slice C5d). A git alias is expanded first, from the aliases read in the call's folder, so a stored alias that
pushes has its target worked out as the guards read it (wslib/gitrules.py, `expand`).
"""
import json
import os
import re
import pathlib
import posixpath
import subprocess

from . import gitcall
from . import gitrules
from . import lease as leases
from . import ledger as ledgers
from . import shell

TIMEOUT = 3.0          # seconds for one folder's git call; a call cut off leaves the folder unresolved
# {(flag, folder): outcome} of the git-folder lookup, kept only inside one hook call (see one_call): the session's own
# working copy, the folders a command acts on and a push's branches each ask git the same question of the same folder.
_FOLDERS = None


class one_call:
    """Within it, each folder's git folders are asked of git once. A hook call decides before its command runs, so
    nothing it looks at changes meanwhile; outside one, every lookup asks git again (slice TFIX of the M3 plan)."""

    def __enter__(self):
        global _FOLDERS
        _FOLDERS = {}
        return self

    def __exit__(self, *_):
        global _FOLDERS
        _FOLDERS = None


def session(event, tool, cwd, top=True):
    """The session's identity and folder. cwd: the folder the tool says the session runs in, or None.
    top=False leaves out own_working_copy, which needs git; the runner works it out only when a hook reads it."""
    pid = event.get("pid") if type(event.get("pid")) is int else leases.tool_pid(tool)
    found = {"session": event.get("session"), "pid": pid, "cwd": cwd}
    if top:
        found["own_working_copy"] = own_working_copy(cwd)
    return found


def own_working_copy(cwd):
    """The top folder of the working copy that holds the session's folder, or None."""
    return _kind(pathlib.Path(cwd), None).get("top") if cwd else None


def lease(root, session_id):
    """The lease as it stands, never taken or changed."""
    found = leases.main_copy(root)
    if found is None:
        return {"state": "free", "holder": None, "file": None}
    file = str(found[1] / leases.NAME)
    holder, corrupt = leases.read(found[1])
    if corrupt:
        return {"state": "unknown", "holder": None, "file": file}
    if holder is None:
        return {"state": "free", "holder": None, "file": file}
    if isinstance(session_id, str) and session_id and holder["session"] == session_id:
        return {"state": "mine", "holder": holder, "file": file}
    return {"state": "other-live" if leases.alive(holder["pid"]) else "other-dead", "holder": holder, "file": file}


def keys(command):
    """[(key, folder text, is a git folder, operand or None)] for every folder a guard may look up in the command."""
    found = []
    for call in shell.analyze(command):
        git = call.get("git")
        if not git or git.get("folder") is None:
            continue
        folder = git["folder"]
        found.append((folder, folder, bool(git.get("git_dir")), None))
        if git.get("subcommand") == "worktree" and git.get("action") == "remove":
            for operand in worktree_operands(git.get("args") or []):
                found.append((posixpath.join(folder, operand), folder, bool(git.get("git_dir")), operand))
    return found


def worktree_operands(args):
    """The paths `git worktree remove [--force|-f]... <path>` names."""
    operands, rest = [], list(args[1:]) if args[:1] == ["remove"] else list(args)
    ended = False
    for word in rest:
        if not ended and word == "--":
            ended = True
        elif ended or not word.startswith("-"):
            operands.append(word)
    return operands


def working_copies(root, command, cwd):
    """{key: fact} for every folder the command's git calls act on. A relative folder needs the session's cwd."""
    facts = {}
    for key, folder, is_git_dir, operand in keys(command):
        if key in facts:
            continue
        folder = os.path.expanduser(folder) if folder.startswith("~") else folder
        if not posixpath.isabs(folder) and not os.path.isabs(folder) and not cwd:
            facts[key] = {"unresolved": "the tool did not say which folder the session runs in"}
            continue
        base = pathlib.Path(cwd or "/") / folder
        if operand is not None:
            facts[key] = _kind(base / operand, None, workspace=_common(root))
        else:
            facts[key] = _kind(base, is_git_dir, workspace=_common(root))
    return facts


def _common(root):
    own = ledgers.git_dir(pathlib.Path(root).resolve())
    return ledgers.common_dir(own) if own is not None else None


def _kind(folder, is_git_dir, workspace=None):
    """{"kind", "top"} for a folder, or {"unresolved": why}. workspace: this workspace's common git folder."""
    if not folder.exists():
        return {"kind": "other", "top": None}
    where = ["--git-dir", str(folder)] if is_git_dir else ["-C", str(folder)]
    try:
        code, text = _git_folders(where)
    except subprocess.TimeoutExpired:
        return {"unresolved": "git did not answer in time"}
    except OSError as error:
        return {"unresolved": f"git could not run: {error}"}
    if code != 0:
        return {"kind": "other", "top": None}       # no repository there
    lines = text.splitlines()
    if len(lines) < 2:
        return {"unresolved": "git gave no git folder"}
    own = pathlib.Path(os.path.realpath(lines[0]))
    common = pathlib.Path(os.path.realpath(lines[1]))
    main = ledgers._same(own, common)
    top = _top(own, common, main)
    if workspace is None:
        workspace = common
    if not ledgers._same(common, workspace):
        return {"kind": "other", "top": top}
    return {"kind": "main" if main else "linked", "top": top}


def _git_folders(where):
    """(exit code, output) of `git rev-parse` for the folder's own and common git folders. Raises
    subprocess.TimeoutExpired or OSError as subprocess.run does. Inside one_call, a folder asked once is not asked
    again."""
    key = (where[0], os.path.normpath(where[1])) if len(where) == 2 else tuple(where)
    if _FOLDERS is not None and key in _FOLDERS:
        found = _FOLDERS[key]
    else:
        try:
            done = subprocess.run(["git", *where, "rev-parse", "--path-format=absolute", "--git-dir",
                                   "--git-common-dir"], capture_output=True, env=gitcall.environment(),
                                  timeout=TIMEOUT, stdin=subprocess.DEVNULL)
            found = (done.returncode, done.stdout.decode("utf-8", "surrogateescape").replace("\r\n", "\n"))
        except (subprocess.TimeoutExpired, OSError) as error:
            found = error
        if _FOLDERS is not None:
            _FOLDERS[key] = found
    if isinstance(found, BaseException):
        raise found
    return found


def _top(own, common, main):
    """The working copy's top folder, from git's own records: the main copy's is the common folder's parent; a
    linked one's is named in its git folder's `gitdir` file."""
    if main:
        return common.parent.as_posix() if common.name == ".git" else None
    try:
        pointer = (own / "gitdir").read_text(encoding="utf-8").strip()
    except (OSError, UnicodeDecodeError):
        return None
    return pathlib.Path(os.path.realpath(pointer)).parent.as_posix()


# -- aliases and git config files (M3 slice C5c) ---------------------------------------------------------------

def aliases(root, command, cwd):
    """{folder: {"aliases": {name: expansion}} or {"unresolved": why}} for the folder of every git call in the
    command whose subcommand is not one of git's own, read from git config there at hook time. A call whose own
    words make it unresolved, or whose folder the parser could not place, gets nothing: the guard refuses it."""
    facts = {}
    for call in shell.analyze(command):
        git = call.get("git")
        if not git or git.get("subcommand") is None or git.get("builtin") or git.get("unresolved"):
            continue
        folder = git.get("folder")
        if folder is None or folder in facts:
            continue
        place = _place(cwd, folder)
        if place is None:
            facts[folder] = {"unresolved": "the tool did not say which folder the session runs in"}
            continue
        where = ["--git-dir", str(place)] if git.get("git_dir") else ["-C", str(place)]
        done = _run(where, ["config", "-z", "--get-regexp", r"^alias\."])
        if done is None:
            facts[folder] = {"unresolved": "git did not answer in time"}
        elif done[0] not in (0, 1):
            facts[folder] = {"unresolved": "git could not read the config there"}
        else:
            found = {}
            for entry in done[1].split("\0"):
                key, _, value = entry.partition("\n")
                if key.lower().startswith("alias."):
                    found[key[len("alias."):].lower()] = value
            facts[folder] = {"aliases": found}
    return facts


def git_config(cwd, environ=None):
    """{"home", "files", "unresolved"}: the git config files no write may reach. The global ones and the system one,
    whether they exist or not, and every file an include.path or includeIf.*.path names, read from git config in cwd, existing or not,
    each also by its real path when it is a symbolic link. A file a person has not created yet still counts, since
    writing it would bring new config in."""
    environ = os.environ if environ is None else environ
    home = environ.get("HOME") or os.path.expanduser("~")
    xdg = environ.get("XDG_CONFIG_HOME") or os.path.join(home, ".config")
    files = [os.path.join(home, ".gitconfig"), os.path.join(xdg, "git", "config"),
             os.path.join(home, ".config", "git", "config")]
    if environ.get("GIT_CONFIG_GLOBAL"):
        files.append(environ["GIT_CONFIG_GLOBAL"])
    system = environ.get("GIT_CONFIG_SYSTEM")
    where = ["-C", str(cwd)] if cwd else []
    # The two git calls run at once: this runs on every edit, and a second git start in turn cost it about a tenth.
    asking = None if system else _start([], ["var", "GIT_CONFIG_SYSTEM"])   # git 2.42 and later; older gits give nothing
    including = _start(where, ["config", "-z", "--show-origin", "--get-regexp", r"^include(if\..*)?\.path$"])
    if not system:
        found = _finish(asking)
        system = found[1].strip() if found and found[0] == 0 else None
    if system:
        files.append(system)
    unresolved = None
    done = _finish(including)
    if done is None:
        unresolved = "git did not answer in time"
    elif done[0] not in (0, 1):
        unresolved = "git could not read the config, so the files its includes name are not known"
    elif done[0] == 0:
        fields = done[1].split("\0")
        for origin, entry in zip(fields[0::2], fields[1::2]):
            _, _, value = entry.partition("\n")
            if not origin.startswith("file:") or not value:
                continue
            source = origin[len("file:"):]
            if value.startswith("~/"):
                value = os.path.join(home, value[2:])
            elif not os.path.isabs(value):
                base = source if os.path.isabs(source) else os.path.join(str(cwd or "."), source)
                value = os.path.join(os.path.dirname(base), value)
            files.append(value)
    known = []
    for name in files:
        for each in (os.path.normpath(name), os.path.realpath(name)):
            each = each.replace("\\", "/")
            if each not in known:
                known.append(each)
    return {"home": home.replace("\\", "/"), "files": known, "unresolved": unresolved}


# -- targets --------------------------------------------------------------------------------------------------

# gh commands that act on no repository: a write by one of them reaches no listed repository.
NO_REPOSITORY = {"gist", "auth", "config", "extension", "alias", "search", "status", "codespace", "org", "ssh-key",
                 "gpg-key", "completion", "help", "version", "copilot", "agent-task", "attestation", "preview"}


target_key = gitrules.target_key


def targets(root, command, cwd, environ=None):
    """{target_key: fact} for every gh call and every git push in the command, a push through a git alias
    included."""
    environ = os.environ if environ is None else environ
    facts = {}
    calls, _ = gitrules.expand(command, lambda: aliases(root, command, cwd))
    for call in calls:
        if call.get("gh"):
            facts[target_key(call)] = _gh_target(call, cwd, environ)
        elif call.get("git") and call["git"].get("push") is not None and call["git"].get("subcommand") == "push":
            facts[target_key(call)] = _push_target(call, cwd)
    return facts


def _fact(destinations=(), unresolved=None, no_repository=False, remote=None, refspecs=None, mirror=False,
          branch=None, main_branch=None):
    return {"destinations": list(destinations), "unresolved": unresolved, "no_repository": no_repository,
            "remote": remote, "refspecs": refspecs, "mirror": mirror, "branch": branch, "main_branch": main_branch}


def _place(cwd, folder):
    """An absolute folder, or None when a relative one has no session folder to start from."""
    if folder is None:
        return None
    folder = os.path.expanduser(folder) if folder.startswith("~") else folder
    if posixpath.isabs(folder) or os.path.isabs(folder):
        return pathlib.Path(folder)
    return pathlib.Path(cwd) / folder if cwd else None


def _run(where, args, env_extra=None):
    """(exit code, output) of git, or None when it cannot run or runs past TIMEOUT."""
    return _finish(_start(where, args, env_extra))


def _start(where, args, env_extra=None):
    """A git process started with its output captured, or None when it cannot start. _finish waits for it."""
    env = gitcall.environment()
    env.update(env_extra or {})
    try:
        return subprocess.Popen(["git", *where, *args], stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env,
                                stdin=subprocess.DEVNULL)
    except OSError:
        return None


def _finish(process):
    """(exit code, output) of a process _start gave, or None when it did not start or runs past TIMEOUT."""
    if process is None:
        return None
    try:
        out, _ = process.communicate(timeout=TIMEOUT)
    except subprocess.TimeoutExpired:
        process.kill()
        process.communicate()
        return None
    return process.returncode, out.decode("utf-8", "surrogateescape").replace("\r\n", "\n")


parse_url = gitrules.parse_url


def _remotes(where, config_args=(), env_extra=None):
    """{name: {"url", "gh-resolved"}} from the folder's git config, or None when git cannot say."""
    found = _run(where, [*config_args, "config", "--get-regexp", r"^remote\."], env_extra)
    if found is None:
        return None
    code, text = found
    if code not in (0, 1):
        return None
    remotes = {}
    for line in text.splitlines():
        key, _, value = line.partition(" ")
        match = re.match(r"^remote\.(.+)\.([^.]+)$", key)
        if match:
            remotes.setdefault(match.group(1), {})[match.group(2).lower()] = value
    return remotes


def _gh_default(remotes, host):
    """gh's own choice when no repository is named: the set-default remote, else the only remote."""
    chosen = [name for name, values in remotes.items() if values.get("gh-resolved")]
    if len(chosen) > 1:
        return None, "more than one remote is marked as gh's default"
    if chosen:
        values = remotes[chosen[0]]
        resolved = values["gh-resolved"]
        base = parse_url(values.get("url", ""))
        if resolved != "base" and "/" in resolved:
            owner, name = resolved.split("/", 1)
            return {"host": base.get("host") or host, "owner": owner, "name": name, "url": None}, None
        return base, None
    with_url = [name for name, values in remotes.items() if values.get("url")]
    if len(with_url) == 1:
        return parse_url(remotes[with_url[0]]["url"]), None
    if not with_url:
        return None, "the folder has no remote, so gh has no repository to act on"
    return None, "two or more remotes and no gh default set, so gh picks a remote by rules of its own"


def _gh_target(call, cwd, environ):
    gh = call["gh"]
    if call.get("unresolved") or gh.get("unresolved"):
        return _fact(unresolved=call.get("unresolved") or gh["unresolved"])
    host = gh.get("host") or environ.get("GH_HOST") or "github.com"
    repo = gh.get("repo")
    if repo is None and environ.get("GH_REPO") and (call.get("env") or {}).get("GH_REPO", "") is not None:
        repo = _gh_repository(environ["GH_REPO"])
    if repo and repo.get("dynamic"):
        return _fact(unresolved="the repository is a variable")
    path = gh.get("path") or []
    api = gh.get("api")
    if path[:1] == ["api"]:
        if api is None or api.get("dynamic"):
            return _fact(unresolved="the api path is a variable")
        if api.get("graphql"):
            return _fact(no_repository=True)
        if not api.get("owner") or not api.get("repo"):
            return _fact(no_repository=True)
        if not api.get("placeholders"):
            return _fact([{"host": host, "owner": api["owner"], "name": api["repo"], "url": None}])
        if repo:
            filled = {"owner": repo["owner"], "repo": repo["name"]}
        else:
            default, why = _gh_folder_default(call, cwd, host)
            if default is None:
                return _fact(unresolved=why)
            filled = {"owner": default.get("owner"), "repo": default.get("name")}
            host = default.get("host") or host
        owner = filled["owner"] if api["owner"] == "{owner}" else api["owner"]
        name = filled["repo"] if api["repo"] == "{repo}" else api["repo"]
        return _fact([{"host": host, "owner": owner, "name": name, "url": None}])
    named = [r for r in (gh.get("repo_argument"),) if r] + list(gh.get("target_urls") or [])
    if any(r.get("dynamic") for r in named):
        return _fact(unresolved="a repository operand is a variable")
    destinations = [{"host": r.get("host") or host, "owner": r.get("owner"), "name": r.get("name"), "url": None}
                    for r in named]
    if repo:
        destinations.insert(0, {"host": repo.get("host") or host, "owner": repo["owner"], "name": repo["name"],
                                "url": None})
    if destinations:
        return _fact(destinations)
    if path[:1] and path[0] in NO_REPOSITORY:
        return _fact(no_repository=True)
    default, why = _gh_folder_default(call, cwd, host)
    if default is None:
        return _fact(unresolved=why)
    return _fact([default])


def _gh_repository(text):
    parts = text.strip().split("/")
    if len(parts) == 3:
        return {"host": parts[0], "owner": parts[1], "name": parts[2], "dynamic": False}
    if len(parts) == 2:
        return {"host": None, "owner": parts[0], "name": parts[1], "dynamic": False}
    return {"host": None, "owner": None, "name": None, "dynamic": True}


def _gh_folder_default(call, cwd, host):
    folder = _place(cwd, call.get("cwd"))
    if folder is None:
        return None, call.get("cwd_unresolved") or "the folder gh runs in cannot be placed"
    remotes = _remotes(["-C", str(folder)])
    if remotes is None:
        return None, "git did not answer in time"
    return _gh_default(remotes, host)


def _config_args(git):
    """The command's own config values as -c options, or None when one cannot be known."""
    args = []
    for item in git.get("config") or ():
        if item.get("dynamic") or item.get("key") is None:
            return None
        args += ["-c", f"{item['key']}={item.get('value') if item.get('value') is not None else 'true'}"]
    return args


def _push_target(call, cwd):
    git, push = call["git"], call["git"]["push"]
    if call.get("unresolved") or git.get("unresolved"):
        return _fact(unresolved=call.get("unresolved") or git["unresolved"])
    if call.get("config_env"):
        return _fact(unresolved=f"{sorted(call['config_env'])[0]} is set, which changes the config git reads")
    if push.get("remote_dynamic") or any(r.get("dynamic") for r in push.get("refspecs") or ()):
        return _fact(unresolved="the remote or a refspec is a variable")
    if push.get("unknown_options"):
        return _fact(unresolved=f"the option {push['unknown_options'][0]} is not modelled")
    folder = _place(cwd, git.get("folder"))
    if folder is None:
        return _fact(unresolved=git.get("folder_unresolved") or "the folder cannot be placed")
    where = ["--git-dir", str(folder)] if git.get("git_dir") else ["-C", str(folder)]
    config_args = _config_args(git)
    if config_args is None:
        return _fact(unresolved="a config value on the command cannot be known")
    try:
        return _push_resolved(where, config_args, push)
    except TimeoutError:
        return _fact(unresolved="git did not answer in time")


def destinations(root, command, cwd):
    """{target_key: {"destinations", "unresolved"}} for every git push in the command, a push through a git alias
    included: the URLs it reaches, as `targets` gives them, without the branch and refspecs the push guards also
    need. A push that names a remote takes one git call; one that names a URL, or none, takes what `targets` does."""
    facts = {}
    calls, _ = gitrules.expand(command, lambda: aliases(root, command, cwd))
    for call in calls:
        git = call.get("git")
        if git and git.get("push") is not None and git.get("subcommand") == "push":
            found = _push_destinations(call, cwd)
            facts[target_key(call)] = {"destinations": found["destinations"], "unresolved": found["unresolved"]}
    return facts


def _push_destinations(call, cwd):
    git, push = call["git"], call["git"]["push"]
    if call.get("unresolved") or git.get("unresolved"):
        return _fact(unresolved=call.get("unresolved") or git["unresolved"])
    if call.get("config_env"):
        return _fact(unresolved=f"{sorted(call['config_env'])[0]} is set, which changes the config git reads")
    if push.get("remote_dynamic"):
        return _fact(unresolved="the remote is a variable")
    if push.get("unknown_options"):
        return _fact(unresolved=f"the option {push['unknown_options'][0]} is not modelled")
    folder = _place(cwd, git.get("folder"))
    if folder is None:
        return _fact(unresolved=git.get("folder_unresolved") or "the folder cannot be placed")
    where = ["--git-dir", str(folder)] if git.get("git_dir") else ["-C", str(folder)]
    config_args = _config_args(git)
    if config_args is None:
        return _fact(unresolved="a config value on the command cannot be known")
    remote = push.get("remote")
    try:
        if remote is not None:
            found = _run(where, [*config_args, "remote", "get-url", "--push", "--all", remote])
            if found is None:
                raise TimeoutError
            if found[0] == 0:
                return _fact([parse_url(url) for url in found[1].splitlines() if url.strip()], remote=remote)
            if found[0] != 2:                 # 2: no such remote, so the word is a URL
                return _fact(unresolved=f"git cannot say where the remote {remote} pushes")
            return _fact([parse_url(_insteadof(_Config(where, config_args), remote))])
        return _push_resolved(where, config_args, push)
    except TimeoutError:
        return _fact(unresolved="git did not answer in time")


def repositories(root, name):
    """The outward-write list: {"file", "repositories": [{"host", "owner", "name", "path"}], "unresolved"}. name: the
    file the hook's config names, relative to the workspace. Each entry is HOST/PATH, the path as the repository's
    URL gives it: OWNER/NAME on GitHub, GROUP/SUBGROUP/NAME on GitLab, ORG/PROJECT/_git/NAME on Azure Repos. A
    missing or unreadable file, or one not in the form {"repositories": ["HOST/OWNER/NAME", ...]}, gives an empty
    list and says why, so every write to a repository is refused until a person repairs it."""
    file = pathlib.Path(root) / name
    found = {"file": name, "repositories": [], "unresolved": None}
    try:
        data = json.loads(file.read_text(encoding="utf-8-sig"))
    except FileNotFoundError:
        found["unresolved"] = f"the list {name} does not exist"
        return found
    except (OSError, UnicodeDecodeError, ValueError) as error:
        found["unresolved"] = f"the list {name} cannot be read: {error}"
        return found
    entries = data.get("repositories") if isinstance(data, dict) else None
    if not isinstance(entries, list):
        found["unresolved"] = f'the list {name} has no "repositories" list'
        return found
    for entry in entries:
        parts = entry.strip().strip("/").split("/") if isinstance(entry, str) else []
        if len(parts) < 3 or not all(part.strip() for part in parts):
            found["repositories"] = []
            found["unresolved"] = f"the list {name} holds {entry!r}, which is not HOST/OWNER/NAME or a longer HOST/PATH"
            return found
        name_part = parts[-1][:-4] if parts[-1].endswith(".git") else parts[-1]
        found["repositories"].append({"host": parts[0].lower(), "owner": parts[-2], "name": name_part,
                                      "path": "/".join(parts[1:-1] + [name_part])})
    return found


def _push_resolved(where, config_args, push):
    """The push's target from three git calls at most, since a push is timed on a row of its own: the folder's
    git folders, its whole config with the command's own values, and, for a named remote, the URLs git pushes to."""
    branch, main_branch = _branches(where)
    config = _Config(where, config_args)
    remote = push.get("remote")
    if remote is None:
        remote = (branch and config.get(f"branch.{branch}.pushRemote")) or config.get("remote.pushDefault") \
            or (branch and config.get(f"branch.{branch}.remote")) or "origin"
    remotes = config.remotes()
    if remote in remotes:
        found = _run(where, [*config_args, "remote", "get-url", "--push", "--all", remote])
        if found is None:
            raise TimeoutError
        if found[0] != 0:
            return _fact(unresolved=f"git cannot say where the remote {remote} pushes")
        urls = [line for line in found[1].splitlines() if line.strip()]
        mirror = (config.get(f"remote.{remote}.mirror") or "").lower() in ("true", "yes", "on", "1")
        configured = [line for line in config.get_all(f"remote.{remote}.push") if line.strip()]
    else:
        urls, mirror, configured = [_insteadof(config, remote)], False, []
    refspecs = None
    if not push.get("refspecs") and not (push.get("all") or push.get("branches") or push.get("mirror")
                                          or push.get("tags") or mirror):
        if configured:
            refspecs = [_refspec(text) for text in configured]
        else:
            refspecs = _push_default(config, branch, remote)
            if isinstance(refspecs, str):
                return _fact([parse_url(url) for url in urls], unresolved=refspecs, remote=remote, branch=branch,
                             main_branch=main_branch)
    return _fact([parse_url(url) for url in urls], remote=remote if remote in remotes else None, refspecs=refspecs,
                 mirror=mirror, branch=branch, main_branch=main_branch)


def _config_key(key):
    """A config key as `git config --list` prints it: the section and the variable in lower case, a subsection
    as written."""
    first, dot, rest = key.partition(".")
    if not dot:
        return key.lower()
    middle, dot, last = rest.rpartition(".")
    return f"{first.lower()}.{middle}.{last.lower()}" if dot else f"{first.lower()}.{rest.lower()}"


class _Config:
    """The folder's git config, with the command's own -c values, read once with `git config --list`."""

    def __init__(self, where, config_args):
        found = _run(where, [*config_args, "config", "-z", "--list"])
        if found is None:
            raise TimeoutError
        self.values = {}
        for entry in found[1].split("\0") if found[0] == 0 else ():
            if not entry:
                continue
            key, newline, value = entry.partition("\n")
            self.values.setdefault(key, []).append(value if newline else "true")

    def get(self, key):
        found = self.values.get(_config_key(key))
        return found[-1] if found else None

    def get_all(self, key):
        return list(self.values.get(_config_key(key)) or ())

    def remotes(self):
        names = set()
        for key in self.values:
            match = re.match(r"^remote\.(.+)\.([^.]+)$", key)
            if match:
                names.add(match.group(1))
        return names


def _branches(where):
    """(the branch checked out in the folder, the branch checked out in its repository's main working copy), each
    None when HEAD is detached. One git call finds the git folders; each HEAD file is read from there."""
    try:
        found = _git_folders(where)
    except (subprocess.TimeoutExpired, OSError):
        raise TimeoutError
    lines = found[1].splitlines() if found[0] == 0 else []
    if len(lines) < 2:
        return None, None
    return _head(where, pathlib.Path(lines[0])), _head(where, pathlib.Path(lines[1]))


def _head(where, git_dir):
    """The branch a git folder's HEAD names, read from its HEAD file, or None when it is detached."""
    try:
        text = (git_dir / "HEAD").read_text(encoding="utf-8", errors="surrogateescape").strip()
    except OSError:
        text = ""
    if text.startswith("ref: refs/heads/") and text != "ref: refs/heads/.invalid":
        return text[len("ref: refs/heads/"):]
    if text and not text.startswith("ref:"):
        return None                           # a commit id: detached
    # Not a plain file to read, such as the reftable format's placeholder: ask git.
    found = _run(["--git-dir", str(git_dir)], ["symbolic-ref", "-q", "--short", "HEAD"])
    if found is None:
        raise TimeoutError
    return found[1].strip() if found[0] == 0 and found[1].strip() else None


def _insteadof(config, url):
    """A URL typed on the command line, rewritten as git rewrites it for a push: the longest matching pushInsteadOf
    prefix when one matches, else the longest matching insteadOf prefix (git's remote.c, `add_url_alias`: a URL
    given as the remote is an anonymous remote, and its push URL is the pushInsteadOf rewrite of what was typed).
    M3 slice C5e: until then only insteadOf was applied, which its instruction review found git does not do."""
    for suffix in (".pushinsteadof", ".insteadof"):
        best = ("", None)
        for key, values in config.values.items():
            if not (key.startswith("url.") and key.endswith(suffix)):
                continue
            base = key[len("url."):-len(suffix)]
            for prefix in values:
                if prefix and url.startswith(prefix) and len(prefix) > len(best[0]):
                    best = (prefix, base + url[len(prefix):])
        if best[1] is not None:
            return best[1]
    return url


def _refspec(text):
    force = text.startswith("+")
    body = text[1:] if force else text
    src, _, dst = body.partition(":")
    return {"src": src, "dst": dst or src, "force": force}


def _push_default(config, branch, remote):
    """[refspec] for a push with no refspec, by push.default and the upstream; or why it is unresolved."""
    mode = (config.get("push.default") or "simple").lower()
    if mode == "nothing":
        return []
    if mode == "matching":
        return "push.default is matching, which pushes every branch both sides have"
    if branch is None:
        return "HEAD is detached and the push names no refspec"
    source = f"refs/heads/{branch}"
    if mode == "current":
        return [{"src": source, "dst": source, "force": False}]
    upstream_remote = config.get(f"branch.{branch}.remote")
    merge = config.get(f"branch.{branch}.merge")
    if mode in ("upstream", "tracking"):
        if not merge:
            return "push.default is upstream and the branch has no upstream"
        return [{"src": source, "dst": merge, "force": False}]
    if mode == "simple":
        if upstream_remote == remote and merge:
            return [{"src": source, "dst": merge, "force": False}]
        return [{"src": source, "dst": source, "force": False}]
    return f"push.default {mode} is not modelled"
