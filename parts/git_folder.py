"""Hook: refuse an edit tool's write inside a git folder or to a git config file.

Git keeps a repository's history, config, hooks and the workspace's lease and edit ledger under `.git`, and a
linked worktree's `.git` is a file naming its git folder. A git config file sets the aliases, remotes and includes
every shell guard reads. An agent that writes one can turn a guard off or change what a command does, so this hook
refuses an edit tool's write to any path with a `.git` segment, a code repository's under `src/` included, and to
each git config file the runner lists: `~/.gitconfig`, `$XDG_CONFIG_HOME/git/config`, `~/.config/git/config`,
`GIT_CONFIG_GLOBAL`, and every file an `include.path` or `includeIf.*.path` names. A stale `index.lock` gets a
message of its own: a person removes it. `.github/`, `.githooks/`, `.gitignore` and `.gitattributes` are ordinary
files and stay editable.

The runner gives the config files (decision 0004, "Shell events", `git_config`); the rules are wslib/gitrules.py's,
which `git_folder_shell` shares for writes made through the shell. See docs/decisions/0004-the-hook-contract.md.
"""
from wslib import gitrules

KIND = "hook"
EVENT = "before-edit"
NEEDS = ("git_config",)
PAGE = "docs/decisions/0004-the-hook-contract.md"


def decide(event, config):
    path = event.get("path") or ""
    absolute = event.get("absolute")
    placed = gitrules.fold(absolute) if absolute else None
    files = gitrules.config_files(event.get("git_config"))
    if gitrules.git_segment(path) and not placed:
        placed = gitrules.fold(path)
    return gitrules.path_refusal(path or absolute or "", placed, files)
