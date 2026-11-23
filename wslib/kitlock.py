"""Read an instance's kit lock: the kit manifest `ws.py adopt` or `ws.py upgrade` last wrote into it.

An instance is a workspace made from the kit (wslib/kit.py, decision record 0007). Its lock, kit.lock.json at the
top, lists each kit file with its class and hash as of the kit version the instance holds, the proof state of each
synced page, and the kit's eval cases. A workspace with no lock is not an instance, and every reader here returns
nothing for it, so the checks behave as before.

The checks that read it: `kit_drift` fails a synced file that no longer matches its hash; `proof` takes a synced
page's proof marks from the kit when they equal the lock's, since the milestone records and eval records that back
them are never synced; `eval_record` does not gate a page the kit proved; `rules` accepts an `eval:` tag that names
one of the kit's cases.
"""
import hashlib
import json

LOCK = "kit.lock.json"


def digest(data):
    """The hash a kit manifest and lock record: "sha256:" and the hex digest of the bytes. Unless the file is binary,
    CRLF is read as LF and a leading UTF-8 byte-order mark is left out, as a check's snapshot reads text, so the
    `kit_drift` check and `ws.py drift` agree and a checkout's line endings do not count as an edit."""
    if isinstance(data, str):
        data = data.encode("utf-8")
    if b"\0" not in data:
        data = data.replace(b"\r\n", b"\n")
        if data.startswith(b"\xef\xbb\xbf"):
            data = data[3:]
    return "sha256:" + hashlib.sha256(data).hexdigest()


class LockError(ValueError):
    pass


def read(snapshot, path=LOCK):
    """The lock as a dict, or None when the workspace holds none. Raises LockError when it cannot be read."""
    if not snapshot.is_file(path):
        return None
    try:
        lock = json.loads(snapshot.read(path) or "")
    except ValueError as error:
        raise LockError(f"{path} is not readable JSON ({error})")
    if not isinstance(lock, dict) or not isinstance(lock.get("files"), dict) \
            or not isinstance(lock.get("proof", {}), dict) or not isinstance(lock.get("kit"), dict):
        raise LockError(f'{path} needs "kit", "files" and "proof"; write it again with ws.py adopt or ws.py upgrade')
    return lock


def version(lock):
    return str((lock or {}).get("kit", {}).get("version", "?"))


def synced(lock):
    """The paths the lock holds as synced: the kit owns them, and an instance changes them only by an upgrade."""
    return {path for path, entry in (lock or {}).get("files", {}).items()
            if isinstance(entry, dict) and entry.get("class") == "synced"}


def proof_states(lock, page):
    """{name: (state, prove_by, [proven-by items as text])} the lock gives a synced page and its sections.

    A name is the page, or page#section, as the `proof` check and the README's table name them."""
    states = {}
    for name, entry in (lock or {}).get("proof", {}).items():
        if (name == page or name.startswith(page + "#")) and isinstance(entry, dict):
            states[name] = (entry.get("proof"), entry.get("prove-by"), list(entry.get("proven-by", [])))
    return states


def proven(lock, page):
    """True when the lock marks the page, or a section of it, proven by the kit."""
    return any(state == "proven" for state, _, _ in proof_states(lock, page).values())


def cases(lock):
    """The names of the kit's eval cases, as of the kit version the instance holds."""
    return set((lock or {}).get("cases", []))
