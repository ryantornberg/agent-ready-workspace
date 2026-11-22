"""The stop gate's runs: the check and the fast tests, in each working copy that holds a session's own edits.

The runner calls this only when a stop hook reads the "gate" fact, and the stop gate reads it only when the
session has entries of its own in an edit ledger (parts/stop_gate.py, decision 0005). Each run starts the same
Python this runner runs under, in the working copy's own top folder, so a worktree is judged by its own branch's
checks. Every run shares one deadline, so the stop gate answers within its 20 seconds; a run the deadline cuts
off, or one that never got time to start, is "timed-out". The variables git sets for a hook are stripped, as
wslib/gitcall.py strips them, and nothing reads standard input.
"""
import subprocess
import sys
import time

from . import gitcall

SECONDS = 18.0          # for every run together; the hook's start and its reply fit in the rest of the 20 seconds
OUTPUT = 4000           # characters kept from the end of a run's output


def commands(tests):
    """[(the command as shown, the arguments)] the gate runs in each working copy."""
    found = [("python3 ws.py check", ["ws.py", "check"])]
    if tests:
        found.append((f"python3 -m unittest -b {' '.join(tests)}", ["-m", "unittest", "-b", *tests]))
    return found


def run(working_copies, tests, seconds=SECONDS, clock=time.monotonic):
    """[{"working_copy", "command", "status", "output"}] for each command in each working copy, in order.

    status: "passed" (exit 0), "failed" (any other exit), "timed-out", or "error" (it could not start)."""
    deadline = clock() + seconds
    results = []
    for top in working_copies:
        for shown, arguments in commands(tests):
            left = deadline - clock()
            entry = {"working_copy": str(top), "command": shown}
            if left <= 0:
                results.append(dict(entry, status="timed-out", output="not started: no time was left"))
                continue
            try:
                done = subprocess.run([sys.executable, "-X", "utf8", *arguments], cwd=str(top), capture_output=True,
                                      env=gitcall.environment(), stdin=subprocess.DEVNULL, timeout=left)
            except subprocess.TimeoutExpired as error:
                text = (error.stdout or b"") + (error.stderr or b"")
                results.append(dict(entry, status="timed-out", output=_tail(text)))
                continue
            except OSError as error:
                results.append(dict(entry, status="error", output=str(error)))
                continue
            results.append(dict(entry, status="passed" if done.returncode == 0 else "failed",
                                output=_tail(done.stdout + done.stderr)))
    return results


def _tail(data):
    text = data.decode("utf-8", "replace").replace("\r\n", "\n").strip()
    return text if len(text) <= OUTPUT else text[-OUTPUT:]
