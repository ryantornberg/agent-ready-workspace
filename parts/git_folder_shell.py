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
  `core.worktree` and `core.sshCommand`, or a key it cannot read. Every guard reads those keys from config. So is
  `core.hooksPath`, which turns off every commit and push check (M3 slice C5d, Q16), and a section renamed to a
  name that holds such a key;
- through a git alias, read from config at hook time as the discard and push guards read it, so `git cf
  remote.origin.url URL` with `cf = config` is judged as that `git config` (M3 slice C5d, Q17). A call that is not
  one of git's own commands is refused when its aliases could not be read, or when the command changes the config
  git reads them from, with HOME, XDG_CONFIG_HOME, GIT_CONFIG_GLOBAL, GIT_CONFIG_SYSTEM, GIT_CONFIG_NOSYSTEM or an
  include: git may then run an alias the runner never saw.

It is always on: these files are shared by every session and by the person. A write it cannot see, the README
lists: an interpreter, a script, a symbolic link, a folder removed whole, a `!` alias a person stored, and a
program named git-NAME. The rules are wslib/gitrules.py's.
See docs/decisions/0004-the-hook-contract.md.
"""
from wslib import gitrules

KIND = "hook"
EVENT = "before-shell"
NEEDS = ("session", "git_config", "aliases")
PAGE = "docs/decisions/0004-the-hook-contract.md"


def decide(event, config):
    reasons = gitrules.shell_refusals(event)
    return reasons[0] if reasons else None
