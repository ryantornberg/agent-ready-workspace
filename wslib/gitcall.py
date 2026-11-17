"""Git calls the engine makes on behalf of a part: in another repository, with a time limit and no prompts.

Decision 0004 (docs/decisions/0004-the-hook-contract.md): a part never runs git itself. The engine runs it
here, and gives the part the facts. Each call strips the variables git sets for a hook, so it acts on the
folder named and not on the repository whose hook is running; turns off every credential prompt, so a
fetch that would ask hangs nobody; and stops at its time limit, in Python, since macOS has no timeout
command. A call that fails, or runs out of time, returns None: the caller decides what that means.
"""
import os
import subprocess

# Set by git for a hook. A call on another repository must not inherit them.
HOOK_VARIABLES = ("GIT_DIR", "GIT_WORK_TREE", "GIT_INDEX_FILE", "GIT_OBJECT_DIRECTORY", "GIT_PREFIX",
                  "GIT_ALTERNATE_OBJECT_DIRECTORIES", "GIT_QUARANTINE_PATH", "GIT_COMMON_DIR")


def environment():
    env = {key: value for key, value in os.environ.items() if key not in HOOK_VARIABLES}
    env.update({"GIT_TERMINAL_PROMPT": "0", "GCM_INTERACTIVE": "never",
                "GIT_SSH_COMMAND": env.get("GIT_SSH_COMMAND", "ssh") + " -o BatchMode=yes"})
    return env


def run(folder, *args, timeout=10):
    """git's output as text, carriage returns dropped, or None when it fails or runs past timeout seconds."""
    try:
        done = subprocess.run(["git", "-C", str(folder), "-c", "core.quotePath=false",
                               "-c", "protocol.file.allow=always", *args],
                              capture_output=True, env=environment(), timeout=timeout, stdin=subprocess.DEVNULL)
    except (OSError, subprocess.TimeoutExpired):
        return None
    if done.returncode != 0:
        return None
    return done.stdout.decode("utf-8", "surrogateescape").replace("\r\n", "\n")


def ok(folder, *args, timeout=10):
    """True when the git call exits 0, False when it exits otherwise, None when it cannot run or times out."""
    try:
        done = subprocess.run(["git", "-C", str(folder), *args], capture_output=True, env=environment(),
                              timeout=timeout, stdin=subprocess.DEVNULL)
    except (OSError, subprocess.TimeoutExpired):
        return None
    return done.returncode == 0


def default_branch(folder):
    """The upstream's default branch name, from the clone's remote-tracking refs: origin's HEAD, else main, else master.
    Never fetches. None when none is known."""
    head = run(folder, "symbolic-ref", "-q", "refs/remotes/origin/HEAD")
    if head and head.strip().startswith("refs/remotes/origin/"):
        return head.strip()[len("refs/remotes/origin/"):]
    for name in ("main", "master"):
        if run(folder, "rev-parse", "--verify", "-q", f"refs/remotes/origin/{name}") is not None:
            return name
    return None


def fetch(folder, branch, timeout=10):
    """Fetch one branch of origin into its remote-tracking ref. True when it worked within the time limit."""
    return run(folder, "fetch", "-q", "--no-tags", "origin",
               f"+refs/heads/{branch}:refs/remotes/origin/{branch}", timeout=timeout) is not None


def pin_state(folder, pin):
    """For a pinned repository checked out at folder and a staged pin: (state, branch, head).

    state: "on" (the pin is on the upstream's default branch), "off", "unreachable" (the fetch failed),
    "absent" (no checkout), or "no-branch" (no default branch is known).
    """
    if not os.path.exists(os.path.join(str(folder), ".git")):
        return "absent", None, None
    branch = default_branch(folder)
    if branch is None:
        return "no-branch", None, None
    head = (run(folder, "rev-parse", "HEAD") or "").strip() or None
    if not fetch(folder, branch):
        return "unreachable", branch, head
    on = ok(folder, "merge-base", "--is-ancestor", pin, f"refs/remotes/origin/{branch}")
    return ("on" if on else "off"), branch, head


def behind(folder):
    """How many commits the upstream's default branch has that the checkout lacks: (branch, count) or None."""
    if not os.path.exists(os.path.join(str(folder), ".git")):
        return None
    branch = default_branch(folder)
    if branch is None or not fetch(folder, branch):
        return None
    count = run(folder, "rev-list", "--count", f"HEAD..refs/remotes/origin/{branch}")
    try:
        return branch, int((count or "").strip())
    except ValueError:
        return None
