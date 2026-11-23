"""Hook: refuse an edit tool's write to the list of repositories agents may write to.

`outward_write` lets an agent write only to the repositories in the instance's list, `outward-repos.json`, which
the manifest names in "list". An agent that could add a repository to the list could then write to it, so only a
person edits the list, from a terminal, where the agent's hooks do not run. This hook refuses an edit tool's write
to a file of that name, in any folder, so a worktree's copy and a path the runner could not place inside a working
copy are refused too. `outward_write` refuses a shell write to it that the parser reports. M3 slice C5e.
See docs/decisions/0004-the-hook-contract.md.
"""
import posixpath

from wslib import gitrules

KIND = "hook"
EVENT = "before-edit"
PAGE = "docs/decisions/0004-the-hook-contract.md"


def decide(event, config):
    name = config.get("list", "outward-repos.json")
    wanted = gitrules.fold(posixpath.basename(name.replace("\\", "/")))
    for path in (event.get("path"), event.get("absolute")):
        if path and gitrules.fold(path).split("/")[-1] == wanted:
            return (f"{path} is the list of repositories agents may write to. Only a person adds a repository to "
                    f"it, from their own terminal. See {PAGE}")
    return None
