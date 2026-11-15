"""Check: while the edit ledger is open, a commit stages only paths the agent's edit tools wrote.

Another session, or the person, may have edits in the same folder. A commit
that sweeps them in carries them under the wrong message. The before-shell
hook used to refuse `git add -A` by reading the command line, and every new
spelling grew the parser. This check looks at the result instead: whatever
command staged a path, the commit holds it, and the check compares it with
the paths this working copy's ledger recorded (wslib/ledger.py).

With no ledger open, as for a person's own commit, it passes. During a merge,
cherry-pick, revert or rebase, the commit replays other work, so it warns and
does not compare. A submodule pin counts as edited when the ledger holds a
path inside it. `git commit --no-verify` skips it, and so does anyone who
closes the ledger by hand: it stops accidents, not a session set on getting
past it.

It runs on what is staged; the working-folder check and CI see no ledger and
find nothing.
"""
from wslib.parts import finding

KIND = "check"
HOW = ("Unstage it with: git restore --staged -- {path}. If this session wrote it with a shell command or a "
       "generator, record it by name with: python3 ws.py ledger --add {path}. If this is a person's own commit, "
       "close the ledger with: python3 ws.py ledger --close")


def _covered(path, ledger):
    return path in ledger or any(entry.startswith(path + "/") for entry in ledger)


def run(snapshot, config):
    if snapshot.ledger_problem:
        return [finding("workspace.json", 1, f"{snapshot.ledger_problem}, so the staged paths cannot be compared")]
    if snapshot.ledger is None or not snapshot.staged:
        return []
    if snapshot.replaying:
        return [finding("workspace.json", 1, f"a commit that replays other work ({snapshot.replaying}) "
                                             "is not compared with the edit ledger", level="warning")]
    return [finding(path, 1, "staged, but no edit tool of the agent session wrote it while the edit ledger "
                             "was open. " + HOW.format(path=path))
            for path in sorted(snapshot.staged) if not _covered(path, snapshot.ledger)]
