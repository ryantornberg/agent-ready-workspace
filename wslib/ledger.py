"""The edit ledger: the paths an agent's edit tools wrote in one git working copy.

Every before-edit hook call that is allowed records its path here. The commit
check (parts/edit_ledger.py) then compares the staged paths with the ledger:
while a ledger is open, a commit that stages a path no edit tool wrote fails,
whatever command staged it. So `git add -A` cannot sweep another session's
edits, or the person's, into an agent's commit.

One ledger per working copy, in its own git folder: `.git/ws-ledger` in the
main checkout, `.git/worktrees/<name>/ws-ledger` in a linked one. An edit is
recorded in the nearest working copy of this repository that holds it, so an
edit in a linked working copy outside the workspace folder is recorded there.
An edit that no working copy of this repository holds is not recorded. Inside
the workspace, an edit in a code repository under src/ is recorded in the
workspace's ledger, so the pin that the edit moves counts as edited.

A shell command that may stage files the session did not write, such as
`git add -A`, opens the ledger of the working copy the agent tool says the
session runs in, even with nothing in it, when that working copy has
uncommitted changes. A clean working copy has nothing of anyone's to sweep,
and the tool reports the folder the session started in, not the one a
command moves to, so a command run in a scratch repository opens nothing. So an agent that wrote its files only through the shell
still has its commit compared, and must record those files by name.

The ledger is open while the file exists. It closes on its own: after each
commit, the post-commit hook removes the paths the commit holds, and deletes
the file when nothing is left. A person's own commit, with no agent edits
waiting, finds no ledger and is not compared.

Format: one entry per line, relative to the working copy's top. An entry an edit tool wrote for a known
session is a JSON object, {"path": "docs/a.md", "session": "the session id"}, so the stop gate can tell a
session's own edits (decision 0005). An entry with no session, such as one `ws.py ledger --add` wrote, is the
JSON-quoted path alone, as every entry was before sessions were recorded; both forms are read. The same path
edited by two sessions has an entry for each. The commit check reads the paths only.
"""
import json
import os
import pathlib
import subprocess

NAME = "ws-ledger"
REPLAYING = ("MERGE_HEAD", "CHERRY_PICK_HEAD", "REVERT_HEAD", "rebase-merge", "rebase-apply")


class LedgerError(RuntimeError):
    pass


def git_dir(top):
    """The git folder of the working copy whose top is `top`, or None when `top` holds no .git."""
    marker = pathlib.Path(top) / ".git"
    if marker.is_dir():
        return marker.resolve()
    if marker.is_file():
        try:
            text = marker.read_text(encoding="utf-8").strip()
        except (OSError, UnicodeDecodeError):
            return None
        if text.startswith("gitdir:"):
            folder = pathlib.Path(text[len("gitdir:"):].strip())
            return (folder if folder.is_absolute() else pathlib.Path(top) / folder).resolve()
    return None


def common_dir(folder):
    """The repository a git folder belongs to: a linked working copy's folder names it in its `commondir` file."""
    pointer = folder / "commondir"
    if pointer.is_file():
        try:
            target = pathlib.Path(pointer.read_text(encoding="utf-8").strip())
        except (OSError, UnicodeDecodeError):
            return folder
        return (target if target.is_absolute() else folder / target).resolve()
    return folder


def _same(a, b):
    try:
        return a == b or os.path.samefile(a, b)
    except OSError:
        return False


def working_copy(path, repository):
    """(top, git folder) of the nearest working copy of `repository` (a common git folder) that holds path, or None."""
    for folder in pathlib.Path(path).parents:
        found = git_dir(folder)
        if found is not None and _same(common_dir(found), repository):
            return folder, found
    return None


def where(root, path):
    """(ledger file, path as recorded) for an edit to path, or None when no working copy of this repository holds it.

    path: as a before-edit event gives it, relative to root when it is inside, else absolute.
    """
    root = pathlib.Path(root).resolve()
    own = git_dir(root)
    if own is None:
        return None
    repository = common_dir(own)
    absolute = pathlib.Path(path) if pathlib.Path(path).is_absolute() else root / path
    found = working_copy(absolute, repository)
    if found is None:
        return None
    top, folder = found
    relative = absolute.relative_to(top).as_posix() if absolute != top else ""
    return (folder / NAME, relative) if relative else None


def entries(folder):
    """The (path, session or None) entries of a git folder's ledger, in order and each once, or None when the
    ledger is closed. Raises LedgerError."""
    if folder is None:
        return None
    file = pathlib.Path(folder) / NAME
    try:
        lines = file.read_text(encoding="utf-8").splitlines()
    except FileNotFoundError:
        return None
    except (OSError, UnicodeDecodeError) as error:
        raise LedgerError(f"the edit ledger {file} cannot be read: {error}")
    found = {}
    for number, line in enumerate(lines, 1):
        if not line.strip():
            continue
        try:
            value = json.loads(line)
        except ValueError:
            value = None
        if isinstance(value, dict) and set(value) == {"path", "session"} and isinstance(value["path"], str) \
                and isinstance(value["session"], str) and value["path"] and value["session"]:
            value = (value["path"], value["session"])
        elif isinstance(value, str):
            value = (value, None)
        else:
            raise LedgerError(f"line {number} of the edit ledger {file} is neither a quoted path nor "
                              '{"path": ..., "session": ...}')
        found[value] = None
    return list(found)


def read(folder):
    """The set of recorded paths in a git folder's ledger, or None when the ledger is closed. Raises LedgerError."""
    found = entries(folder)
    return None if found is None else {path for path, _ in found}


def _line(path, session):
    return json.dumps({"path": path, "session": session} if session else path) + "\n"


def add(file, paths, session=None):
    """Append the paths not yet recorded for this session. Creates the ledger, and so opens it.

    session: the agent session whose edit tool wrote them, or None when it is not known."""
    folder = pathlib.Path(file).parent
    session = session if isinstance(session, str) and session else None
    known = set(entries(folder) or ())
    new = [p for p in dict.fromkeys(paths) if (p, session) not in known]
    try:
        with open(file, "a", encoding="utf-8", newline="\n") as stream:
            stream.write("".join(_line(p, session) for p in new))
    except OSError as error:
        raise LedgerError(f"the edit ledger {file} cannot be written: {error}")


def dirty(top):
    """True when the working copy at top has a staged, unstaged or untracked change. True when git cannot say."""
    done = subprocess.run(["git", "-C", str(top), "status", "--porcelain", "-z", "--untracked-files=normal"],
                          capture_output=True)
    return done.returncode != 0 or bool(done.stdout)


def open_at(root, folder):
    """Open the ledger of the working copy of this repository that holds folder, when that working copy has
    uncommitted changes. Returns the file, or None when nothing was opened."""
    own = git_dir(pathlib.Path(root).resolve())
    if own is None:
        return None
    # The child name only makes the walk start at folder itself.
    found = working_copy(pathlib.Path(folder).resolve() / "probe", common_dir(own))
    if found is None or not dirty(found[0]):
        return None
    file = found[1] / NAME
    add(file, [])
    return file


def record(root, path, session=None):
    """Record one edit, for the session that made it when known. Returns the ledger file written, or None when no
    working copy of this repository holds it."""
    found = where(root, path)
    if found is None:
        return None
    file, relative = found
    add(file, [relative], session)
    return file


def remove(folder, paths):
    """Drop paths from a git folder's ledger, every session's entry for each, and delete the ledger when it is
    empty. Returns the paths left."""
    gone = set(paths)
    kept = [(p, s) for p, s in entries(folder) or () if p not in gone]
    file = pathlib.Path(folder) / NAME
    try:
        if kept:
            temporary = file.with_name(NAME + ".tmp")
            with open(temporary, "w", encoding="utf-8", newline="\n") as stream:   # Python 3.9 has no write_text(newline=)
                stream.write("".join(_line(p, s) for p, s in sorted(kept, key=lambda e: (e[0], e[1] or ""))))
            os.replace(temporary, file)
        elif file.exists():
            file.unlink()
    except OSError as error:
        raise LedgerError(f"the edit ledger {file} cannot be written: {error}")
    return {p for p, _ in kept}


def ledger_folders(root):
    """The git folder of every working copy of the repository that holds root: the main one, then each linked one
    in name order. Empty when root is in no repository."""
    own = git_dir(pathlib.Path(root).resolve())
    if own is None:
        return []
    common = common_dir(own)
    linked = common / "worktrees"
    return [common] + (sorted(f for f in linked.iterdir() if f.is_dir()) if linked.is_dir() else [])


def top_of(folder):
    """The top folder of the working copy whose git folder this is, or None. A linked one's `gitdir` file names
    its `.git` file; the main one's top holds the folder itself."""
    folder = pathlib.Path(folder)
    pointer = folder / "gitdir"
    if pointer.is_file():
        try:
            marker = pathlib.Path(pointer.read_text(encoding="utf-8").strip())
        except (OSError, UnicodeDecodeError):
            return None
        return marker.parent if marker.name == ".git" else None
    return folder.parent if folder.name == ".git" else None


def session_entries(root, session):
    """[(top folder, [paths])] for each working copy of this repository whose ledger holds an entry this session's
    edit tools wrote. An unreadable ledger raises LedgerError."""
    if not isinstance(session, str) or not session:
        return []
    found = []
    for folder in ledger_folders(root):
        mine = sorted({p for p, s in entries(folder) or () if s == session})
        top = top_of(folder) if mine else None
        if mine and top is not None and top.is_dir():
            found.append((top, mine))
    return found


def committed(top):
    """The paths the last commit holds, deletions included."""
    done = subprocess.run(["git", "-C", str(top), "diff-tree", "--root", "--no-commit-id", "--name-only", "-r",
                           "--no-renames", "-z", "HEAD"], capture_output=True)
    if done.returncode != 0:
        raise LedgerError(done.stderr.decode("utf-8", "replace").strip() or "git diff-tree failed")
    return [p for p in done.stdout.decode("utf-8", "surrogateescape").split("\0") if p]


def replaying(folder):
    """The reason a commit is replaying other commits (a merge, cherry-pick, revert or rebase), or None."""
    if folder is None:
        return None
    for name in REPLAYING:
        if (pathlib.Path(folder) / name).exists():
            return name
    return None
