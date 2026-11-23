"""Check: in an instance made from the kit, every synced file is as the kit shipped it.

An instance's lock, kit.lock.json, holds the hash of each file the kit owns there (decision record 0007). This check
fails a synced file whose text no longer matches its hash, or that is gone, and names the two ways out: put the
kit's copy back, or keep the instance's own with `python3 ws.py drift --keep PATH`, which marks it kept in the lock
so the kit stops owning it and upgrades leave it alone. `python3 ws.py drift` reports the same on the working
folder. A seeded file, a kept one, and a file the kit never shipped are the instance's, and pass.

A workspace with no lock is not an instance, and the check finds nothing in it: the kit's own repository has none.
"""
from wslib import kitlock
from wslib.parts import finding

KIND = "check"
PAGE = "docs/decisions/0007-the-kit.md"


def run(snapshot, config):
    try:
        lock = kitlock.read(snapshot)
    except kitlock.LockError as error:
        return [finding(kitlock.LOCK, 1, f"{error}; see {PAGE}")]
    if lock is None:
        return []
    version, found = kitlock.version(lock), []
    for path in sorted(kitlock.synced(lock)):
        way_out = (f"put the kit's copy back with git checkout, or keep the instance's own with "
                   f"python3 ws.py drift --keep {path}; see {PAGE}")
        if not snapshot.is_file(path):
            found.append(finding(path, 1, f"deleted, but kit {version} ships it as synced ({kitlock.LOCK}); {way_out}"))
            continue
        text = snapshot.read(path)
        if text is None:
            found.append(finding(path, 1, f"{snapshot.not_utf8(path)}, so it cannot be compared with kit {version}'s "
                                          f"copy; {way_out}"))
        elif kitlock.digest(text) != lock["files"][path].get("hash"):
            found.append(finding(path, 1, f"edited since kit {version} shipped it as synced ({kitlock.LOCK}); "
                                          f"{way_out}"))
    return found
