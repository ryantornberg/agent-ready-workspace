"""Hook: refuse an edit to a shelved folder.

Some code looks current and is not: a service kept read-only for audits, a
branch of the product the team abandoned. A model cannot tell from the code.
The contract says so in prose, and this hook says so at the moment of the edit.

Config: "paths": the shelved folders.
"""
KIND = "hook"
EVENT = "before-edit"


def decide(event, config):
    path = (event.get("path") or "").replace("\\", "/")
    while path.startswith("./"):
        path = path[2:]
    for folder in config.get("paths", ()):
        folder = folder.strip("/")
        if path == folder or path.startswith(folder + "/"):
            return f"{folder} is shelved and read-only. If the change really belongs there, ask the person first."
    return None
