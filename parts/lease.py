"""Hook: the first live agent session that edits the main working copy keeps it; any other is sent to a worktree.

Two sessions in one working copy share one index, one local main and one set of files, so one can commit,
reset or switch away the other's work. Before an edit to a tracked file in the main working copy, the runner
takes or keeps the lease for this session (wslib/lease.py) and gives the result here. A new or untracked file,
an edit in a linked worktree, and an edit in another repository need no lease. When the lease cannot be
checked, the edit is refused: a lease bug must never let an edit through.
See docs/decisions/0005-concurrent-sessions-and-the-edit-ledger.md.
"""
import datetime

KIND = "hook"
EVENT = "before-edit"
NEEDS = ("lease",)
PAGE = "docs/decisions/0005-concurrent-sessions-and-the-edit-ledger.md"


def decide(event, config):
    lease = event.get("lease") or {}
    state = lease.get("state")
    if state in ("mine", "taken", "not-needed"):
        return None
    where = event.get("path") or "the file"
    if state == "refused":
        holder = lease.get("holder") or {}
        since = ""
        if isinstance(holder.get("taken"), (int, float)):
            since = " since " + datetime.datetime.fromtimestamp(holder["taken"]).strftime("%Y-%m-%d %H:%M")
        who = f"session {str(holder.get('session', '?'))[:8]}{since}" if holder else "a session whose lease is being written"
        return (f"another live agent session ({who}) holds the main working copy. Work in a worktree of your own, "
                f"started from the remote's main so it holds none of that session's commits: git worktree add "
                f"--no-track -b BRANCH .claude/worktrees/NAME origin/main, then edit {where} there. If you are sure no "
                f"other session runs, ask the person; they may delete {lease.get('file', 'the lease file')}. See {PAGE}")
    return (f"the writing-session lease could not be checked ({lease.get('error', 'no lease facts')}), so the edit is "
            f"refused. Work in a worktree of your own, or ask the person. See {PAGE}")
