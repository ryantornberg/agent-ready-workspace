"""The facts a before-shell hook may declare in NEEDS, worked out by the engine.

Decision 0004 (docs/decisions/0004-the-hook-contract.md), "Shell events". A guard reads the command with the
shared parser, wslib/shell.py, and looks up each call's facts by the text the parser gives. The runner keys
its facts by the same text from the same parser call, so a call whose key has no fact counts as unresolved
and is refused.

    session          {"session", "pid", "cwd", "own_working_copy"}
    lease            {"state": "free" | "mine" | "other-live" | "other-dead" | "unknown", "holder", "file"}
    working_copies   {folder text: {"kind": "main" | "linked" | "other", "top"} or {"unresolved": why}}
    targets          {target_key(call): {"destinations": [...], "no_repository": bool, "unresolved": why or None,
                                         "remote": name or None, "refspecs": [...] or None, "mirror": bool}}

A folder is the parser's folder for a git call, read from the session's folder. Its kind comes from git:
the folder's git folder and common git folder. A `git worktree remove` operand, joined to the call's folder,
is keyed too. Every git call goes through wslib/gitcall.py's environment, with a time limit.

A target is where a gh call or a `git push` really goes. A destination is {"host", "owner", "name", "url"} or,
for a local path or a file:// URL, {"local": True, "path", "url"}. For gh: `gh api`'s literal owner and
repository, with {owner} and {repo} filled from GH_REPO, then gh's set-default value, then the only remote;
for any other gh call, -R or --repo, then GH_REPO, then the set-default value, then the only remote. For a push:
every URL git would push to, from `git remote get-url --push --all` with the command's own config values, or,
for a URL on the command line, the URL with the longest `insteadOf` applied. With no refspec, the branch push.default
and the upstream send, in "refspecs". Anything not modelled is unresolved.
"""
import json
import os
import re
import pathlib
import posixpath
import subprocess

from . import gitcall
from . import lease as leases
from . import ledger as ledgers
from . import shell

TIMEOUT = 3.0          # seconds for one folder's git call; a call cut off leaves the folder unresolved


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
        done = subprocess.run(["git", *where, "rev-parse", "--path-format=absolute", "--git-dir", "--git-common-dir"],
                              capture_output=True, env=gitcall.environment(), timeout=TIMEOUT,
                              stdin=subprocess.DEVNULL)
    except subprocess.TimeoutExpired:
        return {"unresolved": "git did not answer in time"}
    except OSError as error:
        return {"unresolved": f"git could not run: {error}"}
    if done.returncode != 0:
        return {"kind": "other", "top": None}       # no repository there
    lines = done.stdout.decode("utf-8", "surrogateescape").replace("\r\n", "\n").splitlines()
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


# -- targets --------------------------------------------------------------------------------------------------

# gh commands that act on no repository: a write by one of them reaches no listed repository.
NO_REPOSITORY = {"gist", "auth", "config", "extension", "alias", "search", "status", "codespace", "org", "ssh-key",
                 "gpg-key", "completion", "help", "version", "copilot", "agent-task", "attestation", "preview"}


def target_key(call):
    """The key a gh call's or a git push's target is filed under: its folder and its words, as the parser gives
    them. A guard computes the same key from the same parser output."""
    git = call.get("git")
    folder = git.get("folder") if git else call.get("cwd")
    return json.dumps([folder, call.get("program"), call.get("args")])


def targets(root, command, cwd, environ=None):
    """{target_key: fact} for every gh call and every git push in the command."""
    environ = os.environ if environ is None else environ
    facts = {}
    for call in shell.analyze(command):
        if call.get("gh"):
            facts[target_key(call)] = _gh_target(call, cwd, environ)
        elif call.get("git") and call["git"].get("push") is not None and call["git"].get("subcommand") == "push":
            facts[target_key(call)] = _push_target(call, cwd)
    return facts


def _fact(destinations=(), unresolved=None, no_repository=False, remote=None, refspecs=None, mirror=False):
    return {"destinations": list(destinations), "unresolved": unresolved, "no_repository": no_repository,
            "remote": remote, "refspecs": refspecs, "mirror": mirror}


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
    env = gitcall.environment()
    env.update(env_extra or {})
    try:
        done = subprocess.run(["git", *where, *args], capture_output=True, env=env, timeout=TIMEOUT,
                              stdin=subprocess.DEVNULL)
    except (OSError, subprocess.TimeoutExpired):
        return None
    return done.returncode, done.stdout.decode("utf-8", "surrogateescape").replace("\r\n", "\n")


def parse_url(url):
    """A destination for a remote URL, by git's rules: a scheme, else host:path is ssh unless a slash comes
    before the colon, else a local path."""
    text = url.strip()
    scheme = re.match(r"^([A-Za-z][A-Za-z0-9+.-]*)://(.*)$", text)
    if scheme:
        kind, rest = scheme.group(1).lower(), scheme.group(2)
        if kind == "file":
            return {"local": True, "path": rest, "url": text}
        host_part, _, path = rest.partition("/")
        host = host_part.rsplit("@", 1)[-1].split(":", 1)[0].lower()
        return _repository(host, path, text)
    colon, slash = text.find(":"), text.find("/")
    drive = os.name == "nt" and re.match(r"^[A-Za-z]:[\\/]", text)
    if colon < 0 or (0 <= slash < colon) or drive:
        return {"local": True, "path": text, "url": text}
    host = text[:colon].rsplit("@", 1)[-1].lower()
    return _repository(host, text[colon + 1:], text)


def _repository(host, path, url):
    parts = [part for part in path.split("/") if part]
    if len(parts) < 2:
        return {"host": host, "owner": None, "name": None, "url": url}
    name = parts[-1][:-4] if parts[-1].endswith(".git") else parts[-1]
    return {"host": host, "owner": parts[-2], "name": name, "url": url}


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


def _get(where, config_args, key):
    found = _run(where, [*config_args, "config", "--get", key])
    if found is None:
        raise TimeoutError
    return found[1].strip() if found[0] == 0 else None


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


def _push_resolved(where, config_args, push):
    branch_text = _run(where, ["symbolic-ref", "-q", "--short", "HEAD"])
    if branch_text is None:
        raise TimeoutError
    branch = branch_text[1].strip() if branch_text[0] == 0 else None
    remote = push.get("remote")
    if remote is None:
        remote = (branch and _get(where, config_args, f"branch.{branch}.pushRemote")) \
            or _get(where, config_args, "remote.pushDefault") \
            or (branch and _get(where, config_args, f"branch.{branch}.remote")) or "origin"
    remotes = _remotes(where, config_args)
    if remotes is None:
        raise TimeoutError
    if remote in remotes:
        found = _run(where, [*config_args, "remote", "get-url", "--push", "--all", remote])
        if found is None:
            raise TimeoutError
        if found[0] != 0:
            return _fact(unresolved=f"git cannot say where the remote {remote} pushes")
        urls = [line for line in found[1].splitlines() if line.strip()]
        mirror = (_get(where, config_args, f"remote.{remote}.mirror") or "").lower() in ("true", "yes", "on", "1")
        configured = _run(where, [*config_args, "config", "--get-all", f"remote.{remote}.push"])
        if configured is None:
            raise TimeoutError
        configured = [line for line in configured[1].splitlines() if line.strip()] if configured[0] == 0 else []
    else:
        urls, mirror, configured = [_insteadof(where, config_args, remote)], False, []
    refspecs = None
    if not push.get("refspecs") and not (push.get("all") or push.get("branches") or push.get("mirror")
                                          or push.get("tags") or mirror):
        if configured:
            refspecs = [_refspec(text) for text in configured]
        else:
            refspecs = _push_default(where, config_args, branch, remote)
            if isinstance(refspecs, str):
                return _fact([parse_url(url) for url in urls], unresolved=refspecs, remote=remote)
    return _fact([parse_url(url) for url in urls], remote=remote if remote in remotes else None, refspecs=refspecs,
                 mirror=mirror)


def _insteadof(where, config_args, url):
    """A URL typed on the command line, with the longest matching insteadOf prefix applied. git applies no
    pushInsteadOf to it."""
    found = _run(where, [*config_args, "config", "--get-regexp", r"^url\..*\.insteadof$"])
    if found is None:
        raise TimeoutError
    best = ("", url)
    for line in found[1].splitlines() if found[0] == 0 else ():
        key, _, prefix = line.partition(" ")
        base = key[len("url."):-len(".insteadof")]
        if prefix and url.startswith(prefix) and len(prefix) > len(best[0]):
            best = (prefix, base + url[len(prefix):])
    return best[1]


def _refspec(text):
    force = text.startswith("+")
    body = text[1:] if force else text
    src, _, dst = body.partition(":")
    return {"src": src, "dst": dst or src, "force": force}


def _push_default(where, config_args, branch, remote):
    """[refspec] for a push with no refspec, by push.default and the upstream; or why it is unresolved."""
    mode = (_get(where, config_args, "push.default") or "simple").lower()
    if mode == "nothing":
        return []
    if mode == "matching":
        return "push.default is matching, which pushes every branch both sides have"
    if branch is None:
        return "HEAD is detached and the push names no refspec"
    source = f"refs/heads/{branch}"
    if mode == "current":
        return [{"src": source, "dst": source, "force": False}]
    upstream_remote = _get(where, config_args, f"branch.{branch}.remote")
    merge = _get(where, config_args, f"branch.{branch}.merge")
    if mode in ("upstream", "tracking"):
        if not merge:
            return "push.default is upstream and the branch has no upstream"
        return [{"src": source, "dst": merge, "force": False}]
    if mode == "simple":
        if upstream_remote == remote and merge:
            return [{"src": source, "dst": merge, "force": False}]
        return [{"src": source, "dst": source, "force": False}]
    return f"push.default {mode} is not modelled"
