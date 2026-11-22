"""Handoff markers: which handoff note a later session in a working copy should read first.

A session that must stop mid-task writes a handoff note (docs/playbooks/handoff.md), then runs
`python3 ws.py handoff NOTE`. That writes a marker naming the note, keyed by the branch the working copy has
checked out, in the working copy's own git folder: `.git/ws-handoff/` in the main checkout,
`.git/worktrees/<name>/ws-handoff/` in a linked one. An agent may not write in a git folder itself (the
`git_folder` guards refuse it), so the engine writes the marker here. Writing again on the same branch replaces
that branch's marker in place; no other marker is opened.

A marker is pending until its branch merges or `python3 ws.py handoff --done` clears it. A branch has merged when
its tip at the time the note was written, or its tip now, has reached the default branch since then: an ancestor
of `origin/main` (or of `main`, with no remote-tracking ref) now, and not of the default branch as it stood when the
note was written. So a branch with no commits of its own yet stays pending, and a note on the default branch
itself stays pending until it is cleared. A branch merged by a squash or a rebase leaves no tip on the default
branch, so its marker stays pending until it is cleared too.

At session start the loader (parts/handoff_loader.py) is given the pending markers of the working copy the session
runs in, each with its note's text, and shows the note when there is exactly one.

Marker format, one JSON file per branch, named by a hash of the branch so that any branch name is a safe file
name on every system: {"branch", "note" (absolute path), "written" (UTC, ISO 8601), "head" (the branch's tip
then, or null), "base" (the default branch's tip then, or null)}.
"""
import datetime
import hashlib
import json
import os
import pathlib
import time

from . import gitcall
from . import ledger as ledgers

FOLDER = "ws-handoff"
DEFAULT_BRANCH = "main"
SHOWN = 8000               # characters of a note given to the loader; a longer note is cut, and the loader says so


class HandoffError(RuntimeError):
    """The marker cannot be written or cleared: the runner prints the reason and exits 2."""


def folder_of(git_dir):
    return pathlib.Path(git_dir) / FOLDER


def file_of(git_dir, branch):
    return folder_of(git_dir) / (hashlib.sha256(branch.encode("utf-8")).hexdigest()[:16] + ".json")


def current_branch(top):
    """The branch checked out at top, or None when HEAD is detached or git cannot say."""
    found = gitcall.run(top, "symbolic-ref", "-q", "--short", "HEAD")
    return found.strip() or None if found is not None else None


def _tip(top, ref):
    found = gitcall.run(top, "rev-parse", "-q", "--verify", f"{ref}^{{commit}}")
    return found.strip() or None if found is not None else None


def default_tip(top, branch=DEFAULT_BRANCH):
    """The default branch's tip: origin's remote-tracking ref when there is one, else the local branch."""
    return _tip(top, f"refs/remotes/origin/{branch}") or _tip(top, f"refs/heads/{branch}")


def _write_json(path, body):
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + f".{os.getpid()}.tmp")
    temporary.write_text(json.dumps(body, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    for _ in range(10):          # on Windows, a reader holding the file open makes the rename fail for a moment
        try:
            os.replace(temporary, path)
            return
        except PermissionError:
            time.sleep(0.05)
    try:
        temporary.unlink()
    finally:
        raise HandoffError(f"the marker {path} could not be written")


def place(top):
    """(top, git folder) of the working copy at top. Raises HandoffError when top is not one."""
    found = ledgers.git_dir(top)
    if found is None:
        raise HandoffError(f"{top} is not the top of a git working copy, so it has no git folder for a marker")
    return pathlib.Path(top), found


def write(top, note, default=DEFAULT_BRANCH, now=None):
    """Write or replace the marker for the branch checked out at top, naming the note. Returns (branch, marker file,
    "written" or "updated"). Raises HandoffError."""
    top, git_dir = place(top)
    path = pathlib.Path(note).expanduser()
    if not path.is_file():
        raise HandoffError(f"{note} is not a file. Write the note first, then run python3 ws.py handoff NOTE")
    branch = current_branch(top)
    if branch is None:
        raise HandoffError("HEAD is detached, so there is no branch to key the marker by. Check out a branch, or "
                           "give the person the note's path by hand")
    when = (now or datetime.datetime.now(datetime.timezone.utc)).strftime("%Y-%m-%dT%H:%M:%SZ")
    body = {"branch": branch, "note": str(path.resolve()), "written": when,
            "head": _tip(top, f"refs/heads/{branch}"), "base": default_tip(top, default)}
    marker = file_of(git_dir, branch)
    outcome = "updated" if marker.exists() else "written"
    _write_json(marker, body)
    return branch, marker, outcome


def clear(top, branch=None):
    """Remove the marker for branch, or for the branch checked out at top. Returns (branch, whether one was there).
    Raises HandoffError."""
    top, git_dir = place(top)
    branch = branch or current_branch(top)
    if branch is None:
        raise HandoffError("HEAD is detached, so name the branch: python3 ws.py handoff --done BRANCH")
    marker = file_of(git_dir, branch)
    try:
        marker.unlink()
        return branch, True
    except FileNotFoundError:
        return branch, False
    except OSError as error:
        raise HandoffError(f"the marker {marker} could not be removed: {error}")


def markers(git_dir):
    """Every readable marker in a git folder, sorted by branch. A file that is not a marker is skipped."""
    found = []
    folder = folder_of(git_dir)
    for path in sorted(folder.glob("*.json")) if folder.is_dir() else ():
        try:
            body = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, ValueError, UnicodeDecodeError):
            continue
        if isinstance(body, dict) and isinstance(body.get("branch"), str) and isinstance(body.get("note"), str):
            found.append(dict(body, file=str(path)))
    return sorted(found, key=lambda body: body["branch"])


def _reached(top, sha, base, now):
    """Whether commit sha is on the default branch now (its tip `now`) and was not when the note was written."""
    if not sha or not now:
        return False
    if gitcall.ok(top, "merge-base", "--is-ancestor", sha, now) is not True:
        return False
    return not base or gitcall.ok(top, "merge-base", "--is-ancestor", sha, base) is False


def merged(top, marker, default=DEFAULT_BRANCH):
    """Whether the marker's branch has merged since the note was written. The default branch itself never merges."""
    branch = marker.get("branch")
    if branch == default:
        return False
    now = default_tip(top, default)
    tips = [marker.get("head"), _tip(top, f"refs/heads/{branch}")]
    return any(_reached(top, sha, marker.get("base"), now) for sha in dict.fromkeys(t for t in tips if t))


def read_note(path, limit=SHOWN):
    """(text, whether it was cut), or (None, False) when the note cannot be read."""
    try:
        text = pathlib.Path(path).read_text(encoding="utf-8-sig")
    except (OSError, UnicodeDecodeError, ValueError):
        return None, False
    return (text[:limit], True) if len(text) > limit else (text, False)


def pending(top, git_dir, default=DEFAULT_BRANCH):
    """The pending markers of one working copy, each {"branch", "note", "written", "text", "cut"}. "text" is None
    when the note cannot be read; it is read only when exactly one marker is pending, since only then is it shown."""
    found = [marker for marker in markers(git_dir) if not merged(top, marker, default)]
    result = [{"branch": m["branch"], "note": m["note"], "written": m.get("written"), "text": None, "cut": False}
              for m in found]
    if len(result) == 1:
        result[0]["text"], result[0]["cut"] = read_note(result[0]["note"])
    return result
