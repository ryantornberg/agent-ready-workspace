"""Hook, at session start: bring the main working copy up to origin/main, when that is safe.

Hooks and pages run from the main working copy's files, even in a worktree session, so a fix another session
merged does nothing until the main copy is updated. The runner fetches origin/main and fast-forwards main,
but only in the main working copy, on main, with no tracked change, no merge or rebase in progress, and no
other live session holding its lease (wslib/lease.py). It reports here why it held back, if it did; a
fetch that fails, another branch or a linked worktree is left alone without a word.
See docs/decisions/0005-concurrent-sessions-and-the-edit-ledger.md.
"""
KIND = "hook"
PAGE = "docs/decisions/0005-concurrent-sessions-and-the-edit-ledger.md"   # the rule's page, which every finding names (criterion 34)
EVENT = "session-start"
MODE = "remind"
NEEDS = ("fast_forward",)


def decide(event, config):
    said = event.get("fast_forward")
    return said if isinstance(said, str) and said else None
