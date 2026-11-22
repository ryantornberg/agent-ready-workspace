"""Hook: refuse a shell command's write inside a git folder or to a git config file, and a git config write to a
key the guards read.

The shell half of `git_folder`. It reads the command with the shared parser and judges every write the parser
reports (`>`, `>>`, `tee`, `cp`, `mv` and its source, `sed -i`, `dd of=`, `rm`, `ln`, `truncate`, `install`,
`rsync`, `touch`, `git config --file`), and `unlink`, `rmdir` and `shred`, which the parser does not report yet.
It refuses:

- a write under any `.git` segment, a linked worktree's `.git` file and `src/*/.git/` included, and to a git config
  file the runner lists; a stale `index.lock` with a message telling a person to remove it;
- a write whose target is a variable, when the variables the line itself set, and HOME, show it is one of those,
  or its text names a git folder, a config file or `git rev-parse` of the git folder;
- a writer whose files `xargs` or `find -exec` supply when it runs, and `find -delete`: no guard can tell what
  they reach;
- a `git config` that sets, unsets, edits, renames or removes a key A0 lists, in any scope: `remote.*`, `url.*`,
  `push.*`, `branch.*.pushRemote`, `branch.*.merge`, `remote.pushDefault`, `include.*`, `includeIf.*`, `alias.*`,
  `core.worktree` and `core.sshCommand`, or a key it cannot read. Every guard reads those keys from config.

It is always on: these files are shared by every session and by the person. A write it cannot see, the README
lists: an interpreter, a script, a symbolic link, a folder removed whole. The rules are wslib/gitrules.py's.
See docs/decisions/0004-the-hook-contract.md.
"""
from wslib import gitrules

KIND = "hook"
EVENT = "before-shell"
NEEDS = ("session", "git_config")
PAGE = "docs/decisions/0004-the-hook-contract.md"


def decide(event, config):
    reasons = gitrules.shell_refusals(event)
    return reasons[0] if reasons else None
