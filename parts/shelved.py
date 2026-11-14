"""Hook: refuse an edit to a shelved folder.

Some code looks current and is not: a service kept read-only for audits, a
branch of the product the team abandoned. A model cannot tell from the code.
The contract says so in prose, and this hook says so at the moment of the edit.

It guards the edit tools. A shell command that writes into the folder (sed -i,
rm, git mv) does not pass through it; the README's Limits say so.

Config: "paths": the shelved folders.
"""
import posixpath

KIND = "hook"
EVENT = "before-edit"


def decide(event, config):
    path = posixpath.normpath((event.get("path") or ".").replace("\\", "/")).lower()
    for folder in config.get("paths", ()):
        folder = folder.strip("/")
        # Compared without case: on macOS and Windows a differently-cased path is the same folder.
        if path == folder.lower() or path.startswith(folder.lower() + "/"):
            return f"{folder} is shelved and read-only. If the change really belongs there, ask the person first."
    return None
