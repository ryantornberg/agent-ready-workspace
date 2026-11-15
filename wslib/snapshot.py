"""A snapshot is the set of files a check looks at.

Every check reads through one of these, never the disk directly. That is what
lets the same check run against the working folder, against exactly what is
staged for a commit, or against an in-memory case in a test.

    Tree    the files on disk under a root
    Index   the files as staged in git: what the commit will contain
    Memory  a dict of path -> text, for cases and tests

Paths are POSIX-style and relative to the workspace root. `changed` is the set
of paths the commit or push edits; checks that care (freshness) use it.

For the commit check, an Index also says what the commit will change and who
edited what: `staged` is every path the commit adds, changes or deletes;
`ledger` is the set of paths the agent's edit tools wrote in this working copy,
or None when no ledger is open (wslib/ledger.py); `replaying` names a merge,
cherry-pick, revert or rebase in progress, or is None. A Memory snapshot takes
the same three from a case. A Tree has no staged paths and no ledger.
"""
import os
import pathlib
import subprocess

from . import ledger as ledgers

ALWAYS_SKIP = {".git", "node_modules", ".venv", "__pycache__"}


class Snapshot:
    def __init__(self, paths, changed=(), staged=None, ledger=None, replaying=None, ledger_problem=None):
        self._paths = frozenset(paths)
        self.changed = frozenset(changed)
        self.staged = frozenset(self.changed if staged is None else staged)
        self.ledger = None if ledger is None else frozenset(ledger)
        self.replaying = replaying
        self.ledger_problem = ledger_problem

    def paths(self, suffixes=None, under="", skip=()):
        """Sorted file paths, optionally by suffix, under a folder, minus skipped folders."""
        prefix = under.strip("/") + "/" if under.strip("/") else ""
        skips = tuple(s.strip("/") + "/" for s in skip)
        for path in sorted(self._paths):
            if not path.startswith(prefix) or path.startswith(skips):
                continue
            if suffixes and not path.lower().endswith(tuple(suffixes)):
                continue
            yield path

    def is_file(self, path):
        return path in self._paths

    def exists(self, path):
        """True for a file, or a folder that holds one. Case-sensitive on every platform."""
        path = path.rstrip("/")
        return path == "" or path in self._paths or any(p.startswith(path + "/") for p in self._paths)

    def read(self, path):
        """The file's text, or None when it is not valid UTF-8."""
        try:
            return self._bytes(path).decode("utf-8-sig")
        except (UnicodeDecodeError, OSError, RuntimeError):
            return None

    def read_bytes(self, path):
        """The file's bytes, or None when it cannot be read. For checks that must see every file, whatever its encoding."""
        try:
            return self._bytes(path)
        except (OSError, RuntimeError, KeyError):
            return None

    def _bytes(self, path):
        raise NotImplementedError


class Memory(Snapshot):
    def __init__(self, files, changed=(), staged=None, ledger=None, replaying=None):
        super().__init__(files, changed, staged, ledger, replaying)
        self._files = files

    def _bytes(self, path):
        text = self._files[path]
        return text if isinstance(text, bytes) else text.encode("utf-8")


class Tree(Snapshot):
    def __init__(self, root, changed=()):
        self.root = pathlib.Path(root).resolve()
        if not self.root.is_dir():
            raise NotADirectoryError(f"not a folder: {root}")
        found = []
        for folder, dirs, files in os.walk(self.root):
            dirs[:] = [d for d in dirs if d not in ALWAYS_SKIP]
            base = pathlib.Path(folder).relative_to(self.root)
            found.extend((base / name).as_posix() for name in files if (pathlib.Path(folder) / name).is_file())
        super().__init__(found, changed)

    def _bytes(self, path):
        return (self.root / path).read_bytes()


def _git(root, *args):
    done = subprocess.run(["git", "-C", str(root), *args], capture_output=True)
    if done.returncode != 0:
        raise RuntimeError(done.stderr.decode("utf-8", "replace").strip() or "git failed")
    return done.stdout


def _names(output):
    return [name for name in output.decode("utf-8", "surrogateescape").split("\0") if name]


class Index(Snapshot):
    """What is staged. An unstaged edit or an untracked file cannot pass or fail the commit.

    A submodule is staged as one pinned commit, not as files. Its files are read
    from its checkout on disk, so links into pinned code and names defined there
    still resolve.
    """

    def __init__(self, root):
        self.root = pathlib.Path(root).resolve()
        paths, self._on_disk = [], set()
        for entry in _names(_git(self.root, "ls-files", "-s", "-z")):
            meta, _, path = entry.partition("\t")
            if ALWAYS_SKIP.intersection(path.split("/")):
                continue
            if meta.startswith("160000"):
                folder = self.root / path
                if folder.is_dir():
                    inside = [f"{path}/{name}" for name in Tree(folder).paths()]
                    self._on_disk.update(inside)
                    paths.extend(inside)
            else:
                paths.append(path)
        # One call gives both: every staged path, deletions included, and the ones the commit adds or changes.
        status = _names(_git(self.root, "diff", "--cached", "--name-status", "--no-renames", "-z"))
        staged = dict(zip(status[1::2], status[0::2]))
        changed = [path for path, letter in staged.items() if letter[:1] in "ACMR"]
        folder = ledgers.git_dir(self.root)
        try:
            ledger, problem = ledgers.read(folder), None
        except ledgers.LedgerError as error:
            ledger, problem = None, str(error)
        super().__init__(paths, changed, staged, ledger, ledgers.replaying(folder), problem)

    def _bytes(self, path):
        if path in self._on_disk:
            return (self.root / path).read_bytes()
        return _git(self.root, "show", f":{path}")


def changed_since(root, ref):
    """Paths edited between ref and HEAD. Empty, with a reason, when ref cannot be used."""
    if not ref or set(ref) == {"0"}:
        return [], "no base commit to compare with"
    try:
        return _names(_git(root, "diff", "--name-only", "-z", "--diff-filter=ACMR", f"{ref}...HEAD")), None
    except RuntimeError as error:
        return [], f"cannot compare with {ref}: {error}"


class Message(Snapshot):
    """A commit about to be made, as three files: its message, its author and its committer.

    The identities are git's own view, `git var GIT_AUTHOR_IDENT` and `GIT_COMMITTER_IDENT`, which
    take `--author`, the environment and the config into account. Each is the name and the email,
    without the date. Not a Memory snapshot: a part never takes it for one of its cases.
    """

    FILES = ("commit message", "author", "committer")

    def __init__(self, root, message):
        self._files = {"commit message": message}
        for name, variable in (("author", "GIT_AUTHOR_IDENT"), ("committer", "GIT_COMMITTER_IDENT")):
            ident = _git(root, "var", variable).decode("utf-8", "surrogateescape").strip()
            self._files[name] = (ident[:ident.rfind(">") + 1] if ">" in ident else ident).encode("utf-8", "surrogateescape")
        super().__init__(self._files)

    def _bytes(self, path):
        return self._files[path]
