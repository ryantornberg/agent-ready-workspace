"""A snapshot is the set of files a check looks at.

Every check reads through one of these, never the disk directly. That is what
lets the same check run against the working folder, against exactly what is
staged for a commit, or against an in-memory case in a test.

    Tree    the files on disk under a root
    Index   the files as staged in git: what the commit will contain
    Memory  a dict of path -> text, for cases and tests

Paths are POSIX-style and relative to the workspace root. `changed` is the set
of paths the commit or push edits; checks that care (freshness) use it.
"""
import os
import pathlib
import subprocess

ALWAYS_SKIP = {".git", "node_modules", ".venv", "__pycache__"}


class Snapshot:
    def __init__(self, paths, changed=()):
        self._paths = frozenset(paths)
        self.changed = frozenset(changed)

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

    def _bytes(self, path):
        raise NotImplementedError


class Memory(Snapshot):
    def __init__(self, files, changed=()):
        super().__init__(files, changed)
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
        changed = _names(_git(self.root, "diff", "--cached", "--name-only", "-z", "--diff-filter=ACMR"))
        super().__init__(paths, changed)

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
