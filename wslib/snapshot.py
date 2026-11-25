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

For the pin check, `pin_facts()` lists each pinned repository whose pin the commit adds or moves, as
{"path", "pin", "state", "branch", "head"}: state is "on" (the pin is on its upstream's default branch),
"off", "unreachable", "absent" (not checked out) or "no-branch". The engine works them out with git
(wslib/gitcall.py), fetching the default branch; a case gives them as "pins".

`added_lines(path)` gives the lines a commit adds to a file, as [(line number, text)], or None when the
snapshot cannot say: an Index compares the staged file with the last commit's, inside the one batch read;
a Tree compares the file with the base it was given (`check --changed-from`); a case gives them as "added".
A file the last commit did not have is all added lines.

For the pre-push check, `pushed` lists the commits a push adds to a branch, each as
{"commit": full hash, "subject": first line, "paths": [paths it changes], "anchors": whether it changes a
proof anchor line}. Merge commits are left out; the commits they bring in are listed.

History, for the checks that judge a change against what came before (eval_record's comparisons and the
proof checks, decision record 0006). The base is the last commit for an Index, the merge base with the
commit given to `check --changed-from` for a Tree, and none for a plain `check`; a case gives it as
"history": {"base": {path: text}}. `has_base()` says whether there is one. `base_text(path)` is the file at
the base, or None when it was not there. `base_path(path)` is the path the file had at the base when the
change renamed it. `commit_text(sha, path)` reads a file at any commit, `is_ancestor(sha)` says whether a
commit is in the history of the one being checked, and `building_when_added(path)` is the manifest's
`building` list at the commit that added the file (the snapshot's own manifest for a file not yet
committed). A case gives these as "commits": {"sha:path": text}, "ancestors": [sha], "renamed": {new: old}
and "added_with": {path: [milestones]} inside "history". All of them read git through the engine; a
part never runs git itself (decision record 0004).
"""
import codecs
import difflib
import os
import pathlib
import re
import subprocess

from . import gitcall
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
                 repositories=(), links=(), pushed=(), pins=None, added=None):
        self._paths = frozenset(paths)
        self._added = None if added is None else {path: [tuple(line) for line in lines] for path, lines in added.items()}
        self.pushed = tuple(pushed)
        self._pins = None if pins is None else [dict(p) for p in pins]
        self._gitlinks = {}       # path -> staged commit, for a snapshot read from git
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

    def added_lines(self, path):
        """[(line number, text)] that this change adds to path, or None when the snapshot cannot say."""
        if self._added is not None:
            return self._added.get(path, [])
        old = self._old_text(path)
        if old is None:
            return None
        new = self.read(path)
        if new is None:
            return None
        return added_between(old, new)

    def _old_text(self, path):
        return None

    # History. A snapshot read from git answers these with git; a Memory snapshot from its case. Reads are
    # cached, and prefetch_history() reads many files in one git process, so the commit check stays at a fixed
    # number of git processes however many pages it holds.

    _history = None

    def _base_commit_id(self):
        """A name git resolves to the base commit ("HEAD", or a hash), or None when the snapshot has none."""
        return None

    def has_base(self):
        if self._history is not None:
            return "base" in self._history
        return self._base_commit_id() is not None

    def _cache(self):
        if getattr(self, "_read_cache", None) is None:
            self._read_cache, self._ancestors = {}, {}
        return self._read_cache

    def prefetch_history(self, base_paths=(), commits=()):
        """Read files at the base, and (sha, path) at other commits, in one git process; later reads come from it."""
        if self._history is not None or getattr(self, "root", None) is None:
            return
        base = self._base_commit_id()
        names = [f"{base}:./{path}" for path in base_paths] if base else []
        names += [f"{sha}:./{path}" for sha, path in commits if re.fullmatch(r"[0-9a-f]{40}", sha or "")]
        cache = self._cache()
        names = [name for name in dict.fromkeys(names) if name not in cache]
        if not names:
            return
        try:
            output = _git(self.root, "cat-file", "--batch", data="".join(n + "\n" for n in names).encode("utf-8"))
        except RuntimeError:
            return
        at = 0
        for name in names:
            end = output.index(b"\n", at)
            header = output[at:end].decode("utf-8", "replace")
            at = end + 1
            if header.endswith((" missing", " ambiguous")) or len(header.split()) != 3:
                cache[name] = None
                continue
            size = int(header.rsplit(" ", 1)[1])
            cache[name] = output[at:at + size].decode("utf-8-sig", "replace")
            at += size + 1

    def base_text(self, path):
        """The file's text at the base, or None when it was not there or there is no base."""
        if self._history is not None:
            return (self._history.get("base") or {}).get(path)
        base = self._base_commit_id()
        return None if base is None else self._git_text(f"{base}:./{path}")

    def base_path(self, path):
        """The path this file had at the base, when the change renamed it there; else the path itself."""
        if self._history is not None:
            return (self._history.get("renamed") or {}).get(path, path)
        if self._base_commit_id() is None or getattr(self, "root", None) is None:
            return path
        return self._renames().get(path) or path

    def _renames(self):
        if getattr(self, "_rename_map", None) is None:
            self._rename_map = {}
            if isinstance(self, Index) and not self._deleted:
                return self._rename_map          # a rename needs a deletion, and the commit makes none
            args = ["diff", "--name-status", "-M", "-z", self._base_commit_id()]
            if isinstance(self, Index):
                args.insert(1, "--cached")
            try:
                fields = _names(_git(self.root, *args))
            except RuntimeError:
                fields = []
            index = 0
            while index < len(fields):
                status = fields[index]
                if status.startswith(("R", "C")) and index + 2 < len(fields):
                    if status.startswith("R"):
                        self._rename_map[fields[index + 2]] = fields[index + 1]
                    index += 3
                else:
                    index += 2
        return self._rename_map

    def commit_text(self, sha, path):
        """The file's text at a commit, or None when git has no such commit or file."""
        if self._history is not None:
            return (self._history.get("commits") or {}).get(f"{sha}:{path}")
        if not re.fullmatch(r"[0-9a-f]{40}", sha or "") or getattr(self, "root", None) is None:
            return None
        return self._git_text(f"{sha}:./{path}")

    def is_ancestor(self, sha):
        """True when the commit is in the history of the commit being checked (HEAD, for a folder or a commit)."""
        if self._history is not None:
            return sha in (self._history.get("ancestors") or ())
        if not re.fullmatch(r"[0-9a-f]{40}", sha or "") or getattr(self, "root", None) is None:
            return False
        self._cache()
        if sha not in self._ancestors:
            try:
                _git(self.root, "merge-base", "--is-ancestor", sha, "HEAD")
                self._ancestors[sha] = True
            except RuntimeError:
                self._ancestors[sha] = False
        return self._ancestors[sha]

    def building_when_added(self, path):
        """The manifest's "building" list at the commit that added the file. A file no commit has added yet is
        judged by this snapshot's own manifest. [] when the manifest had no such list."""
        if self._history is not None:
            return list((self._history.get("added_with") or {}).get(path, []))
        root = getattr(self, "root", None)
        sha = None
        if root is not None:
            try:
                sha = _git(root, "log", "--diff-filter=A", "--format=%H", "-1", "HEAD", "--", path).decode().strip()
            except RuntimeError:
                sha = None
        text = self._git_text(f"{sha}:./workspace.json") if sha else self.read("workspace.json")
        return _building(text)

    def _git_text(self, name):
        cache = self._cache()
        if name not in cache:
            root = getattr(self, "root", None)
            try:
                cache[name] = None if root is None else _git(root, "show", name).decode("utf-8-sig", "replace")
            except RuntimeError:
                cache[name] = None
        return cache[name]

    def pin_facts(self):
        """The pins this commit adds or moves, each with its state. Worked out with git the first time it is asked."""
        if self._pins is None:
            root = getattr(self, "root", None)
            self._pins = []
            for path, pin in sorted(self._gitlinks.items()):
                if path in self.changed and root is not None:
                    state, branch, head = gitcall.pin_state(root / path, pin)
                    self._pins.append({"path": path, "pin": pin, "state": state, "branch": branch, "head": head})
        return list(self._pins)

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
    def __init__(self, files, changed=(), staged=None, ledger=None, replaying=None, repositories=(), links=(),
                 pushed=(), pins=(), added=None, history=None):
        super().__init__(files, changed, staged, ledger, replaying, repositories=repositories, links=links,
                         pushed=pushed, pins=pins, added=added if added is not None else {})
        self._files = files
        self._history = dict(history or {})

    def _bytes(self, path):
        text = self._files[path]
        return text if isinstance(text, bytes) else text.encode("utf-8")


def _building(text):
    """The "building" list of a manifest's text, or [] when it has none or cannot be read."""
    import json
    try:
        found = json.loads(text or "").get("building", [])
    except (ValueError, AttributeError):
        return []
    return [item for item in found if isinstance(item, str)] if isinstance(found, list) else []


def added_between(old, new):
    """The lines new adds to old, numbered as in new."""
    old_lines, new_lines = old.replace("\r\n", "\n").split("\n"), new.replace("\r\n", "\n").split("\n")
    found = []
    for tag, _, _, start, end in difflib.SequenceMatcher(None, old_lines, new_lines, autojunk=False).get_opcodes():
        if tag in ("insert", "replace"):
            found += [(number + 1, new_lines[number]) for number in range(start, end)]
    return found


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

    def __init__(self, root, changed=(), base=None):
        self.root = pathlib.Path(root).resolve()
        self._base, self._base_commit = base, None
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
        files, repositories, links, gitlinks = [], [], [], {}
        for mode, oid, path in entries:
            disk = self.root / path
            if mode == GITLINK:
                gitlinks[path] = oid
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
        self._gitlinks = gitlinks

    def _old_text(self, path):
        """The file at the merge base of HEAD and the base it was given, "" when it was not there, None with no base."""
        if not self._base or set(self._base) == {"0"}:
            return None
        if self._base_commit is None:
            try:
                self._base_commit = _git(self.root, "merge-base", self._base, "HEAD").decode().strip()
            except RuntimeError:
                self._base_commit = ""
        if not self._base_commit:
            return None
        try:
            data = _git(self.root, "show", f"{self._base_commit}:./{path}")
        except RuntimeError:
            return ""
        return data.decode("utf-8-sig", "replace")

    def _base_commit_id(self):
        """The merge base of HEAD and the base given to `check --changed-from`, or None."""
        if not self._base or set(self._base) == {"0"}:
            return None
        if self._base_commit is None:
            try:
                self._base_commit = _git(self.root, "merge-base", self._base, "HEAD").decode().strip()
            except RuntimeError:
                self._base_commit = ""
        return self._base_commit or None

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
        paths, repositories, links, self._on_disk, self._oids, gitlinks = [], [], [], set(), {}, {}
        for mode, oid, path in listing(self.root):
            if mode == GITLINK:
                gitlinks[path] = oid
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
        self._deleted = [path for path, letter in staged.items() if letter[:1] == "D"]
        # The last commit's copy of each changed file comes in the same batch read, for added_lines(): the doc
        # checks read a page's added lines, and the secret scan every file's.
        # A submodule's pin is not a file: its old copy is a commit, which the batch read cannot give as text.
        self._previous = {path: f"HEAD:./{path}" for path in changed if path in self._oids}
        self._extra, self._objects, self._failed = ("HEAD",) + tuple(extra) + tuple(self._previous.values()), None, None
        folder = ledgers.git_dir(self.root)
        try:
            ledger, problem = ledgers.read(folder), None
        except ledgers.LedgerError as error:
            ledger, problem = None, str(error)
        super().__init__(paths, changed, staged, ledger, ledgers.replaying(folder), problem,
                         repositories=repositories, links=links)
        self._gitlinks = gitlinks

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

    def _base_commit_id(self):
        """"HEAD", the last commit, which the staged commit is judged against; None in a repository with no commit
        yet. Asked in the one batch read the snapshot makes anyway, so it starts no git process of its own."""
        try:
            return "HEAD" if self._batch().get("HEAD") is not None else None
        except RuntimeError:
            return None

    def _old_text(self, path):
        name = self._previous.get(path)
        if name is None:
            return None
        try:
            data = self._batch().get(name)
        except RuntimeError:
            return None
        return "" if data is None else data.decode("utf-8-sig", "replace")

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
    """A commit about to be made, or one already made, as three files: its message, its author and its committer.

    The identities are git's own view, `git var GIT_AUTHOR_IDENT` and `GIT_COMMITTER_IDENT`, which
    take `--author`, the environment and the config into account; for a commit already made, its own.
    Each is the name and the email, without the date. `commit`, when given, is the one entry of `pushed`:
    the commit with its paths and its tree, for a part that judges what a commit changes.
    Not a Memory snapshot: a part never takes it for one of its cases.
    """

    FILES = ("commit message", "author", "committer")

    def __init__(self, root, message, commit=None, identities=None):
        self._files = {"commit message": message}
        for name, variable in (("author", "GIT_AUTHOR_IDENT"), ("committer", "GIT_COMMITTER_IDENT")):
            if identities is not None:
                self._files[name] = identities[name].encode("utf-8", "surrogateescape")
                continue
            ident = _git(root, "var", variable).decode("utf-8", "surrogateescape").strip()
            self._files[name] = (ident[:ident.rfind(">") + 1] if ">" in ident else ident).encode("utf-8", "surrogateescape")
        super().__init__(self._files, pushed=[commit] if commit is not None else ())

    def _bytes(self, path):
        return self._files[path]


class Added(Snapshot):
    """The lines one commit added, as files: each path the commit changed, holding only its added lines, each on
    the line number it has in the commit, with blank lines between. A file the commit created with no lines is
    there, empty, so its name is still read. Used by `ws.py check --commits` for the parts that set COMMIT_DIFF.
    Not a Memory snapshot: a part never takes it for one of its cases."""

    def __init__(self, added):
        self._files = {}
        for path, lines in added.items():
            text = []
            for number, line in lines:
                text += [""] * max(0, number - 1 - len(text))
                text.append(line)
            self._files[path] = "\n".join(text).encode("utf-8", "surrogateescape")
        super().__init__(self._files, list(self._files), added=added)

    def _bytes(self, path):
        return self._files.get(path)


def added_by_commit(root, revisions):
    """{commit id: {path: [(line number, text)]}}: the lines each commit in revisions (such as BASE..HEAD) added,
    read as text whatever the file's encoding, so a UTF-16 file's lines are read too. One git process. A path a
    commit created with no lines maps to []. A merge adds no lines of its own here."""
    output = _git(root, "-c", "core.quotePath=false", "log", revisions, "-p", "-U0", "--text", "--no-color",
                  "--no-ext-diff", "--no-renames", "--format=%x00commit %H")
    found, commit, path, header, number = {}, None, None, None, 0
    for raw in output.decode("utf-8", "surrogateescape").split("\n"):
        if raw.startswith("\0commit "):
            commit, path = raw[len("\0commit "):].strip(), None
            found.setdefault(commit, {})
        elif raw.startswith("diff --git ") and commit:
            rest, path = raw[len("diff --git "):], None
            size = (len(rest) - 5) // 2
            header = rest[2 + size + 3:] if rest.startswith("a/") and rest[2 + size:2 + size + 3] == " b/" else None
        elif raw.startswith("new file mode") and commit and header:
            found[commit].setdefault(header, [])
        elif raw.startswith("+++ ") and commit:
            target = raw[4:]
            path = None if target == "/dev/null" else (target[2:] if target.startswith("b/") else target)
            if path is not None:
                found[commit].setdefault(path, [])
        elif raw.startswith("--- ") and commit:
            continue
        elif raw.startswith("@@ "):
            try:
                number = int(raw.split("+", 1)[1].split(" ", 1)[0].split(",", 1)[0])
            except (IndexError, ValueError):
                number = 0
        elif raw.startswith("+") and commit and path is not None:
            found[commit][path].append((number, raw[1:]))
            number += 1
    return found


def history(root, ref="HEAD"):
    """Every line every commit in ref's history added, as a Memory snapshot: each changed path is
    "<commit>:<path>", and its added lines are the lines that commit added to that file. One git process.
    A binary file adds no lines. Used by `ws.py check --history` for the parts that set HISTORY."""
    output = _git(root, "-c", "core.quotePath=false", "log", ref, "-p", "-U0", "--no-color", "--no-ext-diff",
                  "--no-renames", "--format=%x00commit %H")
    added, commit, path, number = {}, None, None, 0
    for raw in output.decode("utf-8", "surrogateescape").split("\n"):
        if raw.startswith("\0commit "):
            commit, path = raw[len("\0commit "):].strip()[:12], None
        elif raw.startswith("+++ "):
            target = raw[4:]
            path = None if target == "/dev/null" else (target[2:] if target.startswith("b/") else target)
        elif raw.startswith("@@ "):
            try:
                number = int(raw.split("+", 1)[1].split(" ", 1)[0].split(",", 1)[0])
            except (IndexError, ValueError):
                number = 0
        elif raw.startswith("+") and commit and path is not None:
            added.setdefault(f"{commit}:{path}", []).append((number, raw[1:]))
            number += 1
    return Memory({key: "" for key in added}, list(added), added=added)
