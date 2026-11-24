"""The writing-session lease: one session at a time writes in the main working copy.

The lease is a small JSON file in the git folder the caller names: the session that holds it, that session's
process id, and when it was taken or last refreshed.
"""
import json
import pathlib
import time

NAME = "ws-lease.json"
MAX_AGE = 30 * 60     # seconds a lease lasts without a refresh


def read(folder):
    """The lease in the folder, or None."""
    path = pathlib.Path(folder) / NAME
    try:
        lease = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    return lease if isinstance(lease, dict) else None


def acquire(folder, session, pid, now=None):
    """Take or refresh the lease for a session: "taken", "mine" or "refused"."""
    now = time.time() if now is None else now
    lease = read(folder)
    if lease is not None and lease.get("session") != session and now - lease.get("taken", 0) <= MAX_AGE:
        return "refused"
    mine = lease is not None and lease.get("session") == session
    (pathlib.Path(folder) / NAME).write_text(json.dumps({"session": session, "pid": pid, "taken": now}),
                                             encoding="utf-8")
    return "mine" if mine else "taken"
