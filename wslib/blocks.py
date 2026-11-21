"""Marked command blocks in a page, and running a tutorial's runnable blocks in a fresh clone.

A marked block is a fenced code block whose opening fence comes right after a line `<!-- NAME -->` (blank lines
between are allowed). The README marks its setup steps `<!-- setup -->`, which the cold-clone job runs
(tools/setup_steps.py); a tutorial marks the blocks a reader runs `<!-- runnable -->`. A fence no marker opens is
an example: its text is never read as a marker. A marker with no block after it is an error.

run_tutorial() clones the workspace fresh at one commit, into a temporary folder, and runs the page's runnable
blocks there, in order, in one bash script that stops at the first failing command. Python is started through the
clone's launcher, as the hooks start it, so `python3` in a block works on Windows, where the installer gives no
`python3`. The local pre-push check runs it on every tutorial a push to main changes; tests/test_tutorials.py
runs it on every tutorial, in CI on three systems.
"""
import os
import pathlib
import re
import shutil
import subprocess
import sys
import tempfile

FENCE = re.compile(r"^ {0,3}(`{3,}|~{3,})")
RUNNABLE = "runnable"
TUTORIALS = "docs/tutorials"
TIMEOUT = 600    # seconds for one tutorial's blocks; a block that waits on input is a failure, not a hang


def _marker(name):
    return re.compile(rf"^ {{0,3}}<!--\s*{re.escape(name)}\s*-->\s*$")


def close(lines, index):
    """The index of the line that closes the fence opened at lines[index], or len(lines) when none does."""
    fence = FENCE.match(lines[index]).group(1)
    for end in range(index + 1, len(lines)):
        closing = FENCE.match(lines[end])
        if closing and closing.group(1)[0] == fence[0] and len(closing.group(1)) >= len(fence) \
                and not lines[end].strip().strip(fence[0]):
            return end
    return len(lines)


def marked(text, name):
    """[(line number of the marker, [command lines])]. Raises ValueError for a marker with no block after it."""
    marker = _marker(name)
    lines, found, index = text.splitlines(), [], 0
    while index < len(lines):
        if FENCE.match(lines[index]):   # a block no marker opens: an example, whose text is never a marker
            index = close(lines, index) + 1
            continue
        if not marker.match(lines[index]):
            index += 1
            continue
        at = index + 1
        index += 1
        while index < len(lines) and not lines[index].strip():
            index += 1
        if index >= len(lines) or not FENCE.match(lines[index]):
            raise ValueError(f"line {at}: a {name} marker must be followed by a fenced code block")
        end = close(lines, index)
        if end == len(lines):
            raise ValueError(f"line {at}: the {name} block's fence is never closed")
        found.append((at, lines[index + 1:end]))
        index = end + 1
    return found


def script(page, text, name, prelude=()):
    """One bash script of the page's marked blocks, stopping at the first failing command."""
    blocks = marked(text, name)
    if not blocks:
        raise ValueError(f"no block is marked <!-- {name} -->")
    out = ["set -eu", *prelude]
    for at, body in blocks:
        out.append(f"# {page}, the block marked at line {at}")
        out.extend(body)
    return "\n".join(out) + "\n"


# Blocks call python3 by name; this sends it through the clone's launcher, which finds a good Python everywhere.
LAUNCHER = 'python3() { bash "$WS_CLONE/wslib/launch.sh" "$@"; }'


def is_tutorial(path):
    return path.startswith(TUTORIALS + "/") and path.endswith(".md") and path.rsplit("/", 1)[-1].lower() != "readme.md"


GIT_TIMEOUT = 120   # seconds for the local clone and the checkout


def _git(*args, cwd=None):
    env = {key: value for key, value in os.environ.items() if not key.startswith("GIT_")}
    try:
        return subprocess.run(["git", *args], cwd=cwd, capture_output=True, env=env, timeout=GIT_TIMEOUT)
    except subprocess.TimeoutExpired:
        return subprocess.CompletedProcess(args, 1, b"", f"git {args[0]} ran past {GIT_TIMEOUT} seconds".encode())


def run_tutorial(root, commit, page, timeout=TIMEOUT):
    """Clone root fresh at commit and run page's runnable blocks there. Returns (passed, output).

    A tutorial with no runnable block fails, as a marker with no block does: a run must not pass by running nothing."""
    folder = pathlib.Path(tempfile.mkdtemp(prefix="ws-tutorial-"))
    clone = folder / "clone"
    try:
        made = _git("clone", "--quiet", "--no-checkout", str(root), str(clone))
        if made.returncode != 0:
            return False, f"cannot clone {root}: {made.stderr.decode('utf-8', 'replace').strip()}"
        moved = _git("-c", "advice.detachedHead=false", "checkout", "--quiet", "--detach", commit, cwd=clone)
        if moved.returncode != 0:
            return False, f"cannot check out {commit[:12]}: {moved.stderr.decode('utf-8', 'replace').strip()}"
        source = clone / page
        if not source.is_file():
            return False, f"{page} is not in the commit {commit[:12]}"
        text = source.read_text(encoding="utf-8")
        try:
            body = script(page, text, RUNNABLE, prelude=(LAUNCHER,))
        except ValueError as error:
            return False, f"{page}: {error}"
        with open(folder / "blocks.sh", "w", encoding="utf-8", newline="\n") as handle:
            handle.write(body)
        env = dict((key, value) for key, value in os.environ.items() if not key.startswith("GIT_"))
        env["WS_CLONE"] = clone.as_posix()
        try:
            done = subprocess.run(["bash", (folder / "blocks.sh").as_posix()], cwd=clone, capture_output=True,
                                  env=env, timeout=timeout, stdin=subprocess.DEVNULL)
        except subprocess.TimeoutExpired:
            return False, f"{page}: its runnable blocks ran past {timeout} seconds"
        output = (done.stdout + done.stderr).decode("utf-8", "replace")
        return done.returncode == 0, output
    finally:
        _remove(folder)


def _remove(folder):
    """Windows refuses to delete git's read-only object files; clear the flag and try again."""
    def again(function, path, _):
        try:
            os.chmod(path, 0o700)
            function(path)
        except OSError:
            pass
    if sys.version_info >= (3, 12):
        shutil.rmtree(folder, onexc=again)
    else:
        shutil.rmtree(folder, onerror=again)
