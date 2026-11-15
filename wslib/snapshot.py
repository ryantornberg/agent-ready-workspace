"""A snapshot is the set of files a check looks at.

Every check reads through one of these, never the disk directly. That is what
lets the same check run against the working folder, against exactly what is
staged for a commit, or against an in-memory case in a test.

    Tree    the files on disk under a root
    Index   the files as staged in git: what the commit will contain
    Memory  a dict of path -> text, for cases and tests

Paths are POSIX-style and relative to the workspace root. `changed` is the set
of paths the commit or push edits; checks that care (freshness) use it.

Tree and Index start from the same git listing (listing() below), so the
working-folder check and the commit check see the same files: a tracked or
staged file is always listed, wherever it is, and the .git entry never is. A
Tree adds the untracked files git does not ignore. A symbolic link is listed
as git stores it, and reads as its target path. `repositories` names the code
repositories inside the workspace, such as submodules, and `pages()` leaves
their pages and every link out, so a page check covers only the pages the
workspace owns. read() gives UTF-8 text only; read_text() reads any encoding,
and not_utf8() says which one a file is in.

For the commit check, an Index also says what the commit will change and who
edited what: `staged` is every path the commit adds, changes or deletes;
`ledger` is the set of paths the agent's edit tools wrote in this working copy,
or None when no ledger is open (wslib/ledger.py); `replaying` names a merge,
cherry-pick, revert or rebase in progress, or is None. A Memory snapshot takes
the same three from a case. A Tree has no staged paths and no ledger.
"""
import codecs
import os
import pathlib
import re
import subprocess

from . import ledger as ledgers

# Folders skipped when a folder is walked, and untracked files under them. A tracked or staged file is always listed.
ALWAYS_SKIP = {".git", "node_modules", ".venv", "__pycache__"}
LINK, GITLINK = "120000", "160000"
MARKS = ((codecs.BOM_UTF32_LE, "utf-32-le", "UTF-32"), (codecs.BOM_UTF32_BE, "utf-32-be", "UTF-32"),
         (codecs.BOM_UTF8, "utf-8", "UTF-8"), (codecs.BOM_UTF16_LE, "utf-16-le", "UTF-16"),
         (codecs.BOM_UTF16_BE, "utf-16-be", "UTF-16"))


def decode(data):
    """(text, encoding) for a file's bytes, whatever the encoding. text is None for a file that is not text.

    The byte-order mark decides first. Then UTF-8; then UTF-16 without a mark, told by its NUL bytes;
    then Windows-1252, the usual encoding of older code on Windows, which reads any byte.
    """
    for mark, codec, name in MARKS:
        if data.startswith(mark):
            return data[len(mark):].decode(codec, "replace"), name
    if b"\0" not in data:
        try:
            return data.decode("utf-8"), "UTF-8"
        except UnicodeDecodeError:
            pass
        try:
            return data.decode("cp1252"), "Windows-1252"
        except UnicodeDecodeError:
            return data.decode("latin-1"), "Windows-1252"
    sample = data[:4096]
    pairs = len(sample) // 2
    even, odd = sample[0::2].count(0), sample[1::2].count(0)
    if len(data) % 2 == 0 and pairs:
        if odd > pairs * 0.3 and even < odd / 8:
            return data.decode("utf-16-le", "replace"), "UTF-16"
        if even > pairs * 0.3 and odd < even / 8:
            return data.decode("utf-16-be", "replace"), "UTF-16"
    return None, "binary"


class Snapshot:
    """repositories: folders that are code repositories of their own, such as a submodule; links: symbolic links."""

    def __init__(self, paths, changed=(), staged=None, ledger=None, replaying=None, ledger_problem=None,
                 repositories=(), links=()):
        self._paths = frozenset(paths)
        self.changed = frozenset(changed)
        self.staged = frozenset(self.changed if staged is None else staged)
        self.ledger = None if ledger is None else frozenset(ledger)
        self.replaying = replaying
        self.ledger_problem = ledger_problem
        self.repositories = frozenset(folder.strip("/") for folder in repositories)
        self.links = frozenset(links)

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

    def pages(self, suffixes=(".md",), skip=()):
        """The pages the workspace owns: not a symbolic link, and not inside a code repository under it.

        A code repository keeps its own pages, linked to its own layout. A link's target is checked where it lives.
        """
        inside = tuple(folder + "/" for folder in self.repositories)
        for path in self.paths(suffixes, skip=skip):
            if path not in self.links and not path.startswith(inside):
                yield path

    def is_file(self, path):
        return path in self._paths

    def is_link(self, path):
        return path in self.links

    def exists(self, path):
        """True for a file, or a folder that holds one. Case-sensitive on every platform."""
        path = path.rstrip("/")
        return path == "" or path in self._paths or any(p.startswith(path + "/") for p in self._paths)

    def read(self, path):
        """The file's text, or None when it is not UTF-8 text. See not_utf8() for why."""
        data = self.read_bytes(path)
        if data is None or b"\0" in data:
            return None
        try:
            return data.decode("utf-8-sig")
        except UnicodeDecodeError:
            return None

    def read_text(self, path):
        """The file's text in whatever encoding it is in, or None for a file that is not text. For reading code."""
        data = self.read_bytes(path)
        return None if data is None else decode(data)[0]

    def not_utf8(self, path):
        """Why read() gives None, as the start of a finding: "is Windows-1252, not UTF-8"."""
        data = self.read_bytes(path)
        if data is None:
            return "cannot be read"
        encoding = decode(data)[1]
        return "is binary, not text" if encoding == "binary" else f"is {encoding}, not UTF-8"

    def read_bytes(self, path):
        """The file's bytes, or None when it cannot be read. For checks that must see every file, whatever its encoding."""
        try:
            return self._bytes(path)
        except (OSError, RuntimeError, KeyError):
            return None

    def _bytes(self, path):
        raise NotImplementedError


class Memory(Snapshot):
    def __init__(self, files, changed=(), staged=None, ledger=None, replaying=None, repositories=(), links=()):
        super().__init__(files, changed, staged, ledger, replaying, repositories=repositories, links=links)
        self._files = files

    def _bytes(self, path):
        text = self._files[path]
        return text if isinstance(text, bytes) else text.encode("utf-8")


def _git(root, *args, data=None):
    try:
        done = subprocess.run(["git", "-C", str(root), *args], capture_output=True, input=data)
    except OSError as error:
        raise RuntimeError(f"git cannot run: {error}")
    if done.returncode != 0:
        raise RuntimeError(done.stderr.decode("utf-8", "replace").strip() or "git failed")
    return done.stdout


def _names(output):
    return [name for name in output.decode("utf-8", "surrogateescape").split("\0") if name]


STAGED = re.compile(r"^(\d{6}) ([0-9a-f]+) (\d)\t(.*)$", re.S)


def listing(root, untracked=False):
    """The one file listing both snapshots start from: [(mode, object id, path)], in one git call.

    Staged entries come with their mode and blob; with untracked=True, untracked files that git does not
    ignore follow, with mode None, and an untracked code repository as its folder with a trailing "/".
    In a conflict, stage 0 or else "ours" (stage 2) stands for the path. The .git entry is never listed.
    """
    args = ["ls-files", "-s", "-z"] + (["-c", "-o", "--exclude-standard"] if untracked else [])
    entries, rank = {}, {}
    for entry in _names(_git(root, *args)):
        match = STAGED.match(entry)
        if match is None:
            entries.setdefault(entry, (None, None, entry))
            continue
        mode, oid, stage, path = match.groups()
        order = {"0": 0, "2": 1}.get(stage, 2)
        if path not in rank or order < rank[path]:
            entries[path], rank[path] = (mode, oid, path), order
    return list(entries.values())


def _skipped(path):
    return bool(ALWAYS_SKIP.intersection(path.split("/")))


def walk(top, prefix=""):
    """(files, code repositories, links) under a folder on disk, for a folder that is not a working copy's top.

    Skips the ALWAYS_SKIP folders and a .git file. A folder that holds .git is a code repository; its files
    are listed and the folder is named. A symbolic link counts when it points at a file.
    """
    top = pathlib.Path(top)
    files, repositories, links = [], [], []
    for folder, dirs, names in os.walk(top):
        here = pathlib.Path(folder)
        base = here.relative_to(top).as_posix()
        base = prefix + ("" if base == "." else base + "/")
        dirs[:] = [d for d in dirs if d not in ALWAYS_SKIP]
        if here != top and (here / ".git").exists():
            repositories.append(base.rstrip("/"))
        for name in names:
            if name == ".git" or not (here / name).is_file():
                continue
            files.append(base + name)
            if (here / name).is_symlink():
                links.append(base + name)
    return files, repositories, links


def _git_top(root):
    """True when root is the top of a git working copy: its .git is a folder, or a file naming one."""
    return (pathlib.Path(root) / ".git").exists()


class Tree(Snapshot):
    """The files in a folder. At the top of a git working copy, git's own listing decides which: every tracked
    or staged file, and every untracked file git does not ignore. Any other folder is walked."""

    def __init__(self, root, changed=()):
        self.root = pathlib.Path(root).resolve()
        if not self.root.is_dir():
            raise NotADirectoryError(f"not a folder: {root}")
        entries = None
        if _git_top(self.root):
            try:
                entries = listing(self.root, untracked=True)
            except RuntimeError:
                entries = None          # git is missing, or this is no repository it can read: walk instead
        if entries is None:
            files, repositories, links = walk(self.root)
            super().__init__(files, changed, repositories=repositories, links=links)
            return
        files, repositories, links = [], [], []
        for mode, _, path in entries:
            disk = self.root / path
            if mode == GITLINK or (mode is None and path.endswith("/") and (disk / ".git").exists()):
                repositories.append(path.rstrip("/"))
                if disk.is_dir():
                    inside = walk(disk, path.rstrip("/") + "/")
                    files += inside[0]
                    repositories += inside[1]
                    links += inside[2]
            elif mode is None:
                if path.endswith("/"):
                    inside = walk(disk, path)
                    files += inside[0]
                    repositories += inside[1]
                    links += inside[2]
                elif not _skipped(path) and disk.is_file():
                    files.append(path)
                    if disk.is_symlink():
                        links.append(path)
            elif disk.is_symlink() or mode == LINK:
                files.append(path)      # a link is listed as git stores it: as a path, whether or not its target exists
                links.append(path)
            elif disk.is_file():
                files.append(path)      # a tracked file deleted from disk is left out
        super().__init__(files, changed, repositories=repositories, links=links)

    def _bytes(self, path):
        disk = self.root / path
        if path in self.links and disk.is_symlink():
            return os.fsencode(os.readlink(disk))   # what git stores for a link: its target
        return disk.read_bytes()


class Index(Snapshot):
    """What is staged. An unstaged edit or an untracked file cannot pass or fail the commit.

    A submodule is staged as one pinned commit, not as files. Its files are read
    from its checkout on disk, so links into pinned code and names defined there
    still resolve.

    Three git processes, whatever the size: one listing, one diff against the last commit, and one batch read
    that fetches every staged file, plus any extra objects named, such as HEAD:./workspace.json.
    """

    def __init__(self, root, extra=()):
        self.root = pathlib.Path(root).resolve()
        paths, repositories, links, self._on_disk, self._oids = [], [], [], set(), {}
        for mode, oid, path in listing(self.root):
            if mode == GITLINK:
                repositories.append(path)
                folder = self.root / path
                if folder.is_dir():
                    inside = walk(folder, path + "/")
                    self._on_disk.update(inside[0])
                    paths += inside[0]
                    repositories += inside[1]
                    links += inside[2]
                continue
            paths.append(path)
            self._oids[path] = oid
            if mode == LINK:
                links.append(path)
        # One call gives both: every staged path, deletions included, and the ones the commit adds or changes.
        status = _names(_git(self.root, "diff", "--cached", "--name-status", "--no-renames", "-z"))
        staged = dict(zip(status[1::2], status[0::2]))
        changed = [path for path, letter in staged.items() if letter[:1] in "ACMR"]
        self._extra, self._objects, self._failed = tuple(extra), None, None
        folder = ledgers.git_dir(self.root)
        try:
            ledger, problem = ledgers.read(folder), None
        except ledgers.LedgerError as error:
            ledger, problem = None, str(error)
        super().__init__(paths, changed, staged, ledger, ledgers.replaying(folder), problem,
                         repositories=repositories, links=links)

    def _batch(self):
        """Every staged blob and every extra object, read in one git process the first time any is needed."""
        if self._failed:
            raise RuntimeError(self._failed)    # once only: a failed batch is not retried for every file
        if self._objects is None:
            names = list(dict.fromkeys(list(self._oids.values()) + list(self._extra)))
            try:
                output = _git(self.root, "cat-file", "--batch", data="".join(n + "\n" for n in names).encode("utf-8")) \
                    if names else b""
            except RuntimeError as error:
                self._failed = f"cannot read the staged files: {error}"
                raise RuntimeError(self._failed)
            self._objects, at = {}, 0
            for name in names:
                end = output.index(b"\n", at)
                header = output[at:end].decode("utf-8", "replace")
                at = end + 1
                if header in (f"{name} missing", f"{name} ambiguous"):
                    self._objects[name] = None
                    continue
                size = int(header.rsplit(" ", 1)[1])
                self._objects[name] = output[at:at + size]
                at += size + 1
        return self._objects

    def _bytes(self, path):
        if path in self._on_disk:
            return (self.root / path).read_bytes()
        return self._batch()[self._oids[path]]

    def object(self, name):
        """The bytes of an extra object named when the snapshot was made, or None when git has no such object."""
        if name not in self._extra:
            raise KeyError(f"{name} was not named when the snapshot was made")
        return self._batch()[name]


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
