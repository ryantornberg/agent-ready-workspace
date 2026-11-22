"""Hook: after an edit, show the agent the other paths the index's cross-cutting chains tie to the edited one.

A chain names, for one kind of change, every path that change touches: adding a part touches its file, its
cases, the manifest, the parts page and the README. An agent that edits one of them is shown the chain's name
and every path in it, so it can check the rest before it calls the work done. A path in a chain that ends in
"/" is a folder, and an edit anywhere under it matches. An edit that no chain names shows nothing, and so does
an edit in no working copy of this repository.

The runner reads the index from the working copy that holds the edited file (the "index" fact, decision 0004),
so a worktree's session sees its own branch's chains. The chain table is read as the `chains` check reads it,
with the parser both share in wslib/markdown.py.

Config: "index" (default INDEX.md), "heading" (default "Cross-cutting chains").
"""
from wslib import markdown

KIND = "hook"
EVENT = "after-edit"
MODE = "remind"
NEEDS = ("index",)
PAGE = "INDEX.md"


def _matches(path, entry):
    return path.startswith(entry) if entry.endswith("/") else path == entry


def decide(event, config):
    if not event.get("working_copy"):
        return None
    index = config.get("index", "INDEX.md")
    text = (event.get("index") or {}).get(index)
    if not isinstance(text, str):
        return None
    path = event.get("path") or ""
    rows = [(change, paths) for _, change, paths in markdown.chains(text, config.get("heading", "Cross-cutting chains"))
            if any(_matches(path, entry) for entry in paths)]
    if not rows:
        return None
    named = "; ".join(f"'{change}' touches {', '.join(paths)}" for change, paths in rows)
    return (f"{path} is in {'a chain' if len(rows) == 1 else str(len(rows)) + ' chains'} of {index}'s cross-cutting "
            f"chains: {named}. Check each of those paths for what this change needs before you call it done.")
