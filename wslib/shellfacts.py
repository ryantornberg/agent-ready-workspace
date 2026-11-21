"""The facts a before-shell hook may declare in NEEDS, worked out by the engine.

Decision 0004 (docs/decisions/0004-the-hook-contract.md), "Shell events". A guard reads the command with the
shared parser, wslib/shell.py, and looks up each call's facts by the text the parser gives. The runner keys
its facts by the same text from the same parser call, so a call whose key has no fact counts as unresolved
and is refused.

    session          {"session", "pid", "cwd", "own_working_copy"}
    lease            {"state": "free" | "mine" | "other-live" | "other-dead" | "unknown", "holder", "file"}
    working_copies   {folder text: {"kind": "main" | "linked" | "other", "top"} or {"unresolved": why}}

A folder is the parser's folder for a git call, read from the session's folder. Its kind comes from git:
the folder's git folder and common git folder. A `git worktree remove` operand, joined to the call's folder,
is keyed too. Every git call goes through wslib/gitcall.py's environment, with a time limit.
"""
import os
import pathlib
import posixpath
import subprocess

from . import gitcall
from . import lease as leases
from . import ledger as ledgers
from . import shell

TIMEOUT = 3.0          # seconds for one folder's git call; a call cut off leaves the folder unresolved


def session(event, tool, cwd):
    """The session's identity and folder. cwd: the folder the tool says the session runs in, or None."""
    pid = event.get("pid") if type(event.get("pid")) is int else leases.tool_pid(tool)
    top = None
    if cwd:
        found = _kind(pathlib.Path(cwd), None)
        top = found.get("top")
    return {"session": event.get("session"), "pid": pid, "cwd": cwd, "own_working_copy": top}


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
