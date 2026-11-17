"""The writing-session lease: the first live agent session that edits the main working copy keeps it.

Decision 0005 (docs/decisions/0005-concurrent-sessions-and-the-edit-ledger.md). Two sessions in one working
copy share one index, one local main and one set of files: one commits the other's edits, resets them away,
or switches the branch under it. So the first live session to edit a tracked file in the main working copy
takes a lease, and any other live session that tries is refused and sent to a worktree of its own. A person
working with one session sees no change.

The lease is one small JSON file in the common git folder, so every worktree sees the same one:
{"session": id, "pid": the agent tool's process, "taken": seconds since the epoch}. It is written to a
temporary file and renamed over the old one, under an exclusive lock on a sibling lock file, so a reader
always finds a whole lease. The operating system frees the lock when its process dies.

Identity: the session id from the tool's payload, and the process id of the agent tool's own long-lived
process. Liveness: on POSIX, signal 0; on Windows, which has no signal 0, the process is opened for a limited
query and its exit code read. A process id that is not a positive whole number is dead. The probe never raises.

Takeover of a live holder is by state, not by time: only when the lease is at least MIN_AGE seconds old and
not corrupt, and the main working copy has nothing to protect: no tracked change, on main, and no commit
ahead of its upstream. Any git call that fails or runs out of time means no takeover.
"""
import json
import os
import time

from . import gitcall
from . import ledger as ledgers

NAME, LOCK = "ws-lease.json", "ws-lease.lock"
MIN_AGE = 5.0           # seconds: a lease younger than this is never taken over, so a holder about to edit keeps it
LOCK_WAIT = 2.0         # seconds to wait for the lock before refusing; nothing is ever written without it
PROBE_BUDGET = 1.5      # seconds for all the git calls of one takeover probe
BRANCH = "main"


class LeaseError(RuntimeError):
    pass


def alive(pid):
    """True when the process exists. Never raises: anything unreadable is dead."""
    if isinstance(pid, str) and pid.strip().isdigit():
        pid = int(pid)
    if type(pid) is not int:
        return False
    if pid <= 0 or pid > 2 ** 31 - 1:
        return False
    if os.name == "nt":
        return _alive_windows(pid)
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        return True             # it exists, under another user
    except (OSError, OverflowError, ValueError):
        return False
    return True


def _alive_windows(pid):
    try:
        import ctypes
        from ctypes import wintypes
        kernel = ctypes.WinDLL("kernel32", use_last_error=True)
        kernel.OpenProcess.restype = wintypes.HANDLE
        handle = kernel.OpenProcess(0x1000, False, pid)        # PROCESS_QUERY_LIMITED_INFORMATION
        if not handle:
            return ctypes.get_last_error() == 5                # access denied: it exists
        try:
            code = wintypes.DWORD()
            if not kernel.GetExitCodeProcess(handle, ctypes.byref(code)):
                return False
            return code.value == 259                           # STILL_ACTIVE
        finally:
            kernel.CloseHandle(handle)
    except Exception:
        return False


def main_copy(root):
    """(top folder, common git folder) of the repository's main working copy, or None (a bare repository, no git)."""
    own = ledgers.git_dir(root)
    if own is None:
        return None
    common = ledgers.common_dir(own)
    if common.name != ".git" or ledgers.git_dir(common.parent) is None:
        return None
    if not ledgers._same(ledgers.git_dir(common.parent), common):
        return None
    return common.parent, common


def read(common):
    """(lease or None, corrupt). A lease needs a text session and a whole-number pid."""
    try:
        with open(os.path.join(str(common), NAME), encoding="utf-8") as stream:
            data = json.load(stream)
    except FileNotFoundError:
        return None, False
    except (OSError, ValueError):
        return None, True
    if not isinstance(data, dict) or not isinstance(data.get("session"), str) or not data["session"] \
            or type(data.get("pid")) is not int:
        return None, True
    return data, False


def _write(common, lease):
    path = os.path.join(str(common), NAME)
    temporary = path + f".{os.getpid()}.tmp"
    with open(temporary, "w", encoding="utf-8") as stream:
        json.dump(lease, stream)
    for attempt in range(10):          # on Windows, a reader holding the file open makes the rename fail for a moment
        try:
            os.replace(temporary, path)
            return
        except PermissionError:
            time.sleep(0.05)
    try:
        os.remove(temporary)
    finally:
        raise LeaseError(f"the lease {path} could not be written")


class _Lock:
    """An exclusive lock on the lease's sibling lock file, polled for up to LOCK_WAIT seconds."""

    def __init__(self, common):
        self.path = os.path.join(str(common), LOCK)
        self.stream = None

    def __enter__(self):
        self.stream = open(self.path, "a+b")
        deadline = time.monotonic() + LOCK_WAIT
        while True:
            try:
                if os.name == "nt":
                    import msvcrt
                    self.stream.seek(0)
                    msvcrt.locking(self.stream.fileno(), msvcrt.LK_NBLCK, 1)
                else:
                    import fcntl
                    fcntl.flock(self.stream.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
                return self
            except OSError:
                if time.monotonic() > deadline:
                    self.stream.close()
                    raise LeaseError("another session holds the lease's lock; try again")
                time.sleep(0.02)

    def __exit__(self, *_):
        try:
            if os.name == "nt":
                import msvcrt
                self.stream.seek(0)
                msvcrt.locking(self.stream.fileno(), msvcrt.LK_UNLCK, 1)
            else:
                import fcntl
                fcntl.flock(self.stream.fileno(), fcntl.LOCK_UN)
        finally:
            self.stream.close()


def _age(common):
    try:
        return time.time() - os.path.getmtime(os.path.join(str(common), NAME))
    except OSError:
        return 0.0


def idle(top, budget=PROBE_BUDGET):
    """True only when the main working copy has nothing to protect: no tracked change, on main, nothing unpushed.
    Any git call that fails, runs out of time or answers unclearly gives False."""
    deadline = time.monotonic() + budget

    def git(*args):
        left = deadline - time.monotonic()
        if left < 0.2:
            return None
        return gitcall.run(top, "--no-optional-locks", *args, timeout=left)

    status = git("status", "--porcelain", "--untracked-files=no", "--ignore-submodules=dirty")
    if status is None or status.strip():
        return False
    head = git("symbolic-ref", "-q", "HEAD")
    if head is None or head.strip() != f"refs/heads/{BRANCH}":
        return False
    upstream = git("rev-parse", "--verify", "-q", "@{upstream}") or git("rev-parse", "--verify", "-q", f"refs/remotes/origin/{BRANCH}")
    if not upstream:
        return False
    ahead = git("rev-list", "--count", f"{upstream.strip()}..HEAD")
    return ahead is not None and ahead.strip() == "0"


def acquire(root, session, pid):
    """Take or keep the lease for this session. Returns ("mine" | "taken" | "refused", the holder or None).
    Raises LeaseError when it cannot decide; the caller refuses then."""
    found = main_copy(root)
    if found is None:
        raise LeaseError("the main working copy cannot be found")
    top, common = found
    if not isinstance(session, str) or not session or type(pid) is not int or pid <= 0:
        raise LeaseError("the session has no id or no process id, so it cannot hold a lease")
    lease, corrupt = read(common)
    if lease and lease["session"] == session and lease["pid"] == pid:
        return "mine", lease               # the holder never waits on the lock
    with _Lock(common):
        lease, corrupt = read(common)
        mine = {"session": session, "pid": pid, "taken": time.time()}
        if lease is None and not corrupt:
            _write(common, mine)
            return "taken", None
        if corrupt:
            if _age(common) < MIN_AGE:
                return "refused", None     # it may be in the middle of a write
            _write(common, mine)
            return "taken", None
        if lease["session"] == session:
            _write(common, dict(mine, taken=lease.get("taken", mine["taken"])))
            return "mine", lease
        if not alive(lease["pid"]):
            _write(common, mine)
            return "taken", lease
        if _age(common) >= MIN_AGE and idle(top):
            _write(common, mine)
            return "taken", lease
        return "refused", lease


def query(root):
    """(the lease or None, whether its holder is alive). Never takes or writes anything."""
    found = main_copy(root)
    if found is None:
        return None, False
    lease, corrupt = read(found[1])
    if corrupt:
        return {"session": "?", "pid": 0, "taken": None}, True    # unreadable: treated as held
    return lease, bool(lease) and alive(lease["pid"])


def release(root, session):
    """Remove the lease when this session holds it. Never raises."""
    try:
        found = main_copy(root)
        if found is None or not session:
            return False
        common = found[1]
        with _Lock(common):
            lease, _ = read(common)
            if lease and lease["session"] == session:
                os.remove(os.path.join(str(common), NAME))
                return True
    except Exception:
        pass
    return False


def tracked(top, path):
    """True when path is tracked in the working copy at top. None when git cannot say.

    Matched without regard to case, so SRC/A.CS needs the lease that src/a.cs does where the file system folds case.
    On a file system that does not, a new file that differs from a tracked one only in case needs it too: the safe side."""
    out = gitcall.run(top, "ls-files", "-z", "--", f":(icase){path}", timeout=5)
    return None if out is None else bool(out.strip("\0"))


def tool_pid(tool, environ=None):
    """The agent tool's own long-lived process id, or None.

    Claude Code names it in CLAUDE_PID. Codex sets no such variable; its recorded runs show the hook's parent is a
    shell whose parent is Codex, so the runner's grandparent is taken, on POSIX only. See decision 0005."""
    environ = os.environ if environ is None else environ
    if tool == "claude-code":
        try:
            return int(environ.get("CLAUDE_PID", ""))
        except ValueError:
            return None
    if tool == "codex" and os.name != "nt":
        parent = gitcall_parent(os.getppid())
        return parent
    return None


def gitcall_parent(pid):
    """The parent of a process, read with ps. None when it cannot be read."""
    import subprocess
    try:
        out = subprocess.run(["ps", "-o", "ppid=", "-p", str(pid)], capture_output=True, text=True, timeout=2).stdout
        return int(out.strip())
    except (OSError, ValueError, subprocess.TimeoutExpired):
        return None


FETCH_BUDGET = 15.0     # seconds for the whole start-of-session fast-forward


def fast_forward(root, cwd, session, budget=FETCH_BUDGET):
    """Bring the main working copy up to origin/main at session start, when that is safe. Returns what to tell
    the session, or None. Never raises. A linked worktree, another branch, a merge or rebase in progress, or a
    fetch that fails is left alone without a word."""
    try:
        found = main_copy(root)
        if found is None:
            return None
        top, common = found
        here = ledgers.working_copy(os.path.join(os.path.realpath(cwd), "probe"), common)
        if here is None or not ledgers._same(here[0], top):
            return None
        deadline = time.monotonic() + budget

        def git(*args):
            left = deadline - time.monotonic()
            return None if left < 0.5 else gitcall.run(top, *args, timeout=left)

        head = git("symbolic-ref", "-q", "HEAD")
        if head is None or head.strip() != f"refs/heads/{BRANCH}" or ledgers.replaying(common):
            return None
        status = git("status", "--porcelain", "--untracked-files=no", "--ignore-submodules=dirty")
        if status is None:
            return None
        if status.strip():
            return ("The main working copy has uncommitted changes to tracked files, so it was not brought up to "
                    "date with origin/main. Commit or set them aside, then pull.")
        lease, live = query(root)
        if lease and live and lease.get("session") != session:
            return (f"Another live agent session ({str(lease.get('session'))[:8]}) holds the main working copy, so it "
                    "was not brought up to date with origin/main. Work in a worktree of your own.")
        if git("fetch", "-q", "--no-tags", "origin", f"+refs/heads/{BRANCH}:refs/remotes/origin/{BRANCH}") is None:
            return None
        if git("merge", "--ff-only", "-q", f"refs/remotes/origin/{BRANCH}") is not None:
            return None
        ahead = git("log", "--format=%h %s", "-3", f"refs/remotes/origin/{BRANCH}..HEAD") or ""
        if ahead.strip():
            named = "; ".join(line for line in ahead.splitlines() if line.strip())
            return (f"main has commits that are not on origin/main ({named}), so it could not fast-forward. They "
                    "are a person's unpushed work: report them, and do not move them.")
        return ("main could not fast-forward to origin/main: another git process may hold its lock, or uncommitted "
                "files clash with incoming ones.")
    except Exception:
        return None
