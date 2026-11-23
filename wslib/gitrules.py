"""The rules on the git folder, git config and git aliases that the edit and shell guards share. M3 slice C5c.

Every guard that judges a git command needs the same answers: what a git alias runs, whether a command changes
the git config the guard read, and whether a write lands in a git folder or a git config file. This module gives
them once, so the discard guard, the push guard and the guards built after them do not each copy the rules.

It is pure: it reads only the event a part is given and the shared parser's output, never a file or git. The
runner reads what it needs from git (decision 0004, "Shell events": the `aliases` and `git_config` facts).

    read(event)            -> (calls, why): the command's calls, with each git alias expanded as the runner read
                              it from config at hook time; why says, when it could not, for which calls.
    unresolved(call, why)  -> why a guard cannot know what a call does, or None.
    config_write(call, every_guarded=False)
                           -> why a call a guard decides on changes the git config the guard read, or None.
    path_refusal(path, absolute, files)
                           -> why a write to that path is refused: under a .git segment, or to a git config file.
    shell_refusals(event)  -> every refusal of the command's file and config writes, in order.
    expand(command, table) -> (calls, why): the same as read, from a command and an `aliases` table; the runner
                              uses it to work out a push's target as the guards will read the call (M3 slice C5d).
    earlier_change(calls, index)
                           -> why a call earlier in the line changes the branch, the upstream, a remote or gh's
                              default before the push at index runs, or None (M3 slice C5d).
    push_updates(call, fact)
                           -> what a push sends, read from its words and its resolved target: each destination
                              branch it updates or deletes, and whether it forces (M3 slice C5d).
    touches_branch(update, branch)
                           -> True when an update may land on that branch.
    parse_url(url)         -> where a remote URL points, by git's rules: {"host", "owner", "name", "url"}, or
                              {"local": True, "path", "url"} for a local path or a file:// URL (M3 slice C5e;
                              moved from wslib/shellfacts.py, which still offers it).
    listed(destination, repositories)
                           -> True when a destination is one of the repositories in the outward-write list.

A git config file is one of the files the runner lists in `git_config`: the global ones (`~/.gitconfig`,
`$XDG_CONFIG_HOME/git/config`, `~/.config/git/config`, `GIT_CONFIG_GLOBAL`) and every file an `include.path` or
`includeIf.*.path` names. The repository's own config lives under `.git`, so the segment rule covers it.
"""
import json
import os
import posixpath
import re
import unicodedata

from . import shell

PAGE = "docs/decisions/0004-the-hook-contract.md"

# Programs whose operands the parser does not report as writes, though each removes or changes the file it names.
# A parser gap handled here, until slice Z moves it into wslib/shell.py.
REMOVERS = {"unlink", "rmdir", "shred"}
# Programs that write the files they are given. When xargs or find -exec supplies those files at run time, no guard
# can know which they are.
WRITERS = {"rm", "cp", "mv", "ln", "truncate", "install", "rsync", "touch", "tee", "dd"} | REMOVERS
PERSISTENT_OPS = {"set", "unset", "edit", "rename-section", "remove-section"}
# The text of a write target that is a variable, read for what it shows: a .git segment, a config file's name, or
# a way to ask git for its folder.
GIT_FOLDER_HINTS = re.compile(r"GIT_DIR|GIT_COMMON_DIR|rev-parse|--git-path|--git-dir|--git-common-dir")
VARIABLE = re.compile(r"\$(?:\{(\w+)\}|(\w+))")


def fold(path):
    """A path as a case-insensitive file system sees it, with forward slashes. On macOS and Windows another case,
    or a letter Unicode folds to the same one (a long s for an s), names the same file; Windows also drops a
    trailing dot or space from each name."""
    text = path.replace("\\", "/")
    keep_root = text.startswith("/")
    parts = [part.rstrip(". ") or part for part in text.split("/")]
    text = "/".join(parts)
    text = posixpath.normpath(text) if text else text
    if keep_root and not text.startswith("/"):
        text = "/" + text
    return unicodedata.normalize("NFC", text).casefold()


def git_segment(path):
    """True when a segment of the path is a git folder or a linked worktree's .git file."""
    return ".git" in fold(path).split("/")


def _absolute(text):
    return text.startswith("/") or bool(re.match(r"^[A-Za-z]:/", text))


def place(path, cwd, call_cwd, home):
    """The absolute path a write names, folded, or None when it cannot be placed. cwd: the session's folder;
    call_cwd: the command's folder relative to it, as the parser gives it; home: the home folder."""
    text = path.replace("\\", "/")
    if text == "~" or text.startswith("~/"):
        if not home:
            return None
        text = home.replace("\\", "/").rstrip("/") + text[1:]
    elif text.startswith("~"):
        return None                       # another user's home
    if not _absolute(text):
        if call_cwd is None or not cwd:
            return None
        base = call_cwd.replace("\\", "/")
        if not _absolute(base):
            base = posixpath.join(cwd.replace("\\", "/"), base)
        text = posixpath.join(base, text)
    return fold(text)


def config_files(facts):
    """The folded git config files the runner listed, or an empty set."""
    return {fold(name) for name in ((facts or {}).get("files") or ())}


def path_refusal(path, absolute, files):
    """Why a write to this path is refused, or None. path: as written; absolute: placed and folded, or None."""
    for text in (path, absolute):
        if text and git_segment(text):
            name = posixpath.basename(fold(text))
            if name == "index.lock":
                return (f"{path} is git's lock on the index. A stale one is left by a git process that stopped; "
                        f"an agent does not remove it. Ask the person to check that no git process is running and "
                        f"remove it from their own terminal")
            return (f"{path} is inside a git folder, or is a linked worktree's .git file. Git keeps the repository's "
                    f"history, config, hooks, lease and edit ledger there, and only git and the workspace's engine "
                    f"write it. Use git's own commands; a person changes anything else there from their own terminal")
    if absolute and absolute in files:
        return (f"{path} is a git config file. It sets aliases, remotes and includes that every guard reads, so an "
                f"agent does not write it. A person changes it from their own terminal")
    if absolute is None:
        name = fold(path)
        if posixpath.basename(name) == ".gitconfig" or name.endswith("git/config"):
            return (f"{path} looks like a git config file, and its folder cannot be placed. A person changes git "
                    f"config from their own terminal")
    return None


def _substitute(text, call, home):
    """The text with each $NAME or ${NAME} the line set replaced by the value it set, and HOME from the facts. A
    value that itself names a variable is filled in turn, a few times over, so D="$HOME/.gitconfig" is seen."""
    env = call.get("env") or {}

    def value(match):
        name = match.group(1) or match.group(2)
        if name in env and env[name] is not None:
            return env[name]
        if name == "HOME" and home:
            return home
        return match.group(0)

    for _ in range(5):
        filled = VARIABLE.sub(value, text)
        if filled == text:
            break
        text = filled
    return text


def _dynamic_refusal(path, call, home, files, cwd):
    """Why a write whose target holds a variable or a substitution is refused, or None. Its known variables are
    filled in; what is left is judged by its text alone."""
    text = _substitute(path, call, home)
    if "$" not in text and "`" not in text:
        return path_refusal(path, place(text, cwd, call.get("cwd"), home), files)
    if GIT_FOLDER_HINTS.search(text) or git_segment(text):
        return (f"the write to {path} names a git folder through a variable or a substitution. Only git and the "
                f"workspace's engine write there")
    name = fold(text)
    if posixpath.basename(name) == ".gitconfig" or name.endswith("git/config"):
        return f"the write to {path} names a git config file through a variable. A person changes git config"
    return None


def _find_deletes(call):
    """True for a find that deletes what it finds: a parser gap handled here."""
    return call.get("program") == "find" and "-delete" in (call.get("args") or [])


def _remover_writes(call):
    if call.get("program") not in REMOVERS:
        return []
    return [{"path": word, "dynamic": index in set(call.get("dynamic_args") or ()), "via": call["program"]}
            for index, word in enumerate(call.get("args") or []) if not word.startswith("-")]


def _config_file(absolute, files):
    """True for a git config file: one the runner listed, or a repository's own config under its git folder."""
    if absolute is None:
        return False
    parts = absolute.split("/")
    return absolute in files or (".git" in parts and parts[-1] in ("config", "config.worktree"))


# Keys a persistent `git config` write may not set, beyond A0's list in wslib/shell.py: core.hooksPath points git
# at another hooks folder, which turns off every commit and push check (M3 slice C5d, the maintainer's answer to
# Q16). Kept here, outside the eval's hash, until slice Z moves it into `guarded_key`. A -c value lasts one call,
# like --no-verify, so it is not counted.
PERSISTENT_ONLY = {"core.hookspath"}


def _persistent_only(key):
    parts = key.split(".")
    return len(parts) == 2 and key.lower() in PERSISTENT_ONLY


def _section_guarded(name):
    """True when a section of that name holds a key the guards refuse, or may: `core` holds core.hooksPath."""
    return shell.guarded_key(name + ".x") or shell.guarded_key(name) or name.lower() == "core"


def _guarded(write, call=None):
    key = write.get("key")
    if key is None:
        return True
    if write.get("op") == "remove-section":
        # Removing `core` removes core.hooksPath, which this workspace sets to its own hooks folder.
        return shell.guarded_key(key + ".x") or shell.guarded_key(key) or key.lower() == "core"
    if write.get("op") == "rename-section":
        # The parser reports the old name only; the new one decides as much, since renaming a section to
        # remote.x or core brings its keys in there. A parser gap handled here until slice Z.
        new = _renamed_to(call, key)
        return _section_guarded(key) or new is None or _section_guarded(new)
    return shell.guarded_key(key) or _persistent_only(key)


def _renamed_to(call, old):
    """The new name a `git config --rename-section OLD NEW` gives, or None when it cannot be read."""
    args = list(((call or {}).get("git") or {}).get("args") or [])
    for index, word in enumerate(args):
        if word in ("--rename-section", "rename-section") and index + 2 < len(args) and args[index + 1] == old:
            return args[index + 2]
    return None


DEVICES = {"/dev/null", "/dev/stdout", "/dev/stderr", "/dev/tty"}


class _Facts:
    """The runner's git_config fact, read the first time a write needs it: the runner works it out with git only
    when a hook reads it, so a command that writes nothing starts no git process."""

    def __init__(self, event):
        self.event, self._facts = event, None

    def _get(self):
        if self._facts is None:
            self._facts = self.event.get("git_config") or {}
        return self._facts

    @property
    def home(self):
        return self._get().get("home")

    @property
    def files(self):
        return config_files(self._get())


def shell_refusals(event):
    """Every refusal of the command's writes to a git folder or a git config file, and of its persistent git config
    writes to the keys the guards read. Each is a reason, in the order the shell would run them."""
    facts, cwd = _Facts(event), event.get("cwd")
    calls, why_aliases = read(event)
    # A cd the parser cannot follow (one that is not the leading command, or one in a subshell) leaves a later
    # command's folder unknown. If any cd in the line enters a git folder, a relative write after it may land there.
    enters = next((arg for call in calls if call.get("program") in ("cd", "pushd") for arg in call.get("args") or []
                   if git_segment(arg) or GIT_FOLDER_HINTS.search(arg)), None)
    reasons = []
    for call in calls:
        alias_why = _alias_config_refusal(call, why_aliases)
        if alias_why:
            reasons.append(alias_why)
            continue
        program = call.get("program")
        sed_in_place = program == "sed" and any(a.startswith("-i") for a in call.get("args") or [])
        if call.get("runtime_args") and (program in WRITERS or call.get("writes") or sed_in_place):
            reasons.append(f"{call['runtime_args']} gives {program} the files it writes when it runs, so no guard can "
                           f"tell whether one is in a git folder or a git config file. Name the files on the command "
                           f"line, or edit them with the edit tool")
            continue
        if _find_deletes(call):
            reasons.append("find -delete removes whatever it finds when it runs, so no guard can tell whether that is "
                           "in a git folder. Remove named files with rm, or ask the person")
            continue
        for write in list(call.get("writes") or ()) + _remover_writes(call):
            path = write.get("path") or ""
            if path in DEVICES:
                continue
            if write.get("via") == "git config --file" and not write.get("dynamic") and \
                    _config_file(place(path, cwd, call.get("cwd"), facts.home), facts.files):
                continue                  # its key decides, as for any git config write
            if write.get("dynamic"):
                why = _dynamic_refusal(path, call, facts.home, facts.files, cwd)
            else:
                placed = place(path, cwd, call.get("cwd"), facts.home)
                why = path_refusal(path, placed, facts.files)
                if why is None and placed is None and enters is not None:
                    why = (f"the folder {path} is written in cannot be placed, and a cd in this line enters {enters}, "
                           f"a git folder. Only git and the workspace's engine write there")
            if why:
                reasons.append(why)
        for write in call.get("config_writes") or ():
            if write.get("via") != "git config" or write.get("op") not in PERSISTENT_OPS or not _guarded(write, call):
                continue
            scope = write.get("scope") or ""
            if scope.startswith("--file ") and "$" not in scope and \
                    not _config_file(place(scope[7:], cwd, call.get("cwd"), facts.home), facts.files):
                continue                  # a file git reads no config from
            key = write.get("key") or "a key it cannot read"
            if write.get("op") == "rename-section":
                key = f"{key} to {_renamed_to(call, key) or 'a name it cannot read'}"
            reasons.append(f"git config {write['op']} of {key} rewrites a git config file, and that key decides "
                           f"where a push goes, what a git command runs, or which folder git works on. Every guard "
                           f"reads it, so an agent does not change it; a person does, from their own terminal")
    return reasons


def _alias_config_refusal(call, why_aliases):
    """Why a git call that may be an alias cannot be judged for config writes, or None (M3 slice C5d, the
    maintainer's answer to Q17). A stored alias is expanded by `read`, so `git cf remote.origin.url URL` with
    `cf = config` is judged as that `git config`. Two cases are left: the aliases were not read, and the command
    changes the config git reads its aliases from, with HOME, GIT_CONFIG_GLOBAL and the rest or an include, so the
    alias git runs is one the runner never saw. A subcommand that is neither built in nor an alias at hook time,
    with neither, is a program named git-NAME, which this guard does not judge, as it does not judge a script."""
    git = call.get("git") or {}
    subcommand = git.get("subcommand")
    from_config = (git.get("alias") or {}).get("source") == "config"
    if subcommand is None or (git.get("builtin") and not from_config):
        return None
    changed = config_write(call)
    if changed:
        name = (git.get("alias") or {}).get("name") or subcommand
        return (f"git {name} is not one of git's own commands, and {changed}: git may then run an alias from a config "
                f"file the guards did not read, and that alias may rewrite git config. Run the git command it stands "
                f"for by its own name, without that setting")
    if _needs_alias(call) and why_aliases:
        return (f"git {subcommand} is not one of git's own commands, and {why_aliases}, so this guard cannot tell "
                f"whether it is an alias that rewrites git config. Run the git command it stands for by its own name")
    return None


# -- aliases and unresolved calls ---------------------------------------------------------------------------------

def _needs_alias(call):
    git = call.get("git")
    return bool(git) and git.get("subcommand") is not None and not git.get("builtin") and not git.get("unresolved")


def read(event):
    """(calls, why). The command's calls, with each git alias expanded from the aliases the runner read from config
    in that call's folder (the `aliases` fact). When the aliases a call needs were not read, or two folders' aliases
    differ, the calls come back unexpanded and why says so; `unresolved` then refuses each call that needs one."""
    return expand(event.get("command") or "", lambda: event.get("aliases") or {})


def expand(command, table):
    """(calls, why), as `read` gives them. table: the `aliases` fact, or a function that returns it, called only
    when a call needs an alias, so a command with none starts no git process."""
    found = shell.analyze(command)
    needing = [call for call in found if _needs_alias(call)]
    if not needing:
        return found, None
    table = (table() if callable(table) else table) or {}
    chosen = None
    for call in needing:
        folder = call["git"].get("folder")
        if folder is None:
            return found, "the folder it acts on cannot be placed, so its aliases cannot be read"
        fact = table.get(folder)
        if not isinstance(fact, dict) or not isinstance(fact.get("aliases"), dict):
            return found, (fact or {}).get("unresolved") or "its folder's aliases were not read"
        if chosen is None:
            chosen = fact["aliases"]
        elif chosen != fact["aliases"]:
            return found, "the command's git calls act on folders whose aliases differ"
    return shell.analyze(command, aliases=chosen), None


def _includes(git):
    return [entry for entry in git.get("config") or ()
            if entry.get("key") is None or entry["key"].lower().startswith(("include.", "includeif."))]


def unresolved(call, why_aliases=None):
    """Why a guard cannot know what this call does, or None: the parser's reasons, a git subcommand that is neither
    built in nor an alias at hook time, an alias read from config this command changes, or arguments that xargs or
    find -exec supply when it runs."""
    if call.get("unresolved"):
        return call["unresolved"]
    git = call.get("git")
    if not git:
        return None
    if git.get("unresolved"):
        return git["unresolved"]
    subcommand = git.get("subcommand")
    if subcommand is not None and not git.get("builtin"):
        if why_aliases:
            return f"git {subcommand} is not one of git's own commands, and {why_aliases}"
        return (f"git {subcommand} is neither one of git's own commands nor an alias. If it is a program named "
                f"git-{subcommand}, run it by that name; otherwise ask the person")
    alias = git.get("alias") or {}
    if alias.get("source") == "config" and (call.get("config_env") or _includes(git)):
        changed = (call.get("config_env") or ["an include"])[0]
        return (f"git {alias['name']} is an alias read from config, and {changed} set on the command changes the "
                f"config git reads it from")
    if call.get("runtime_args"):
        return f"{call['runtime_args']} supplies git's arguments when it runs"
    return None


def config_write(call, every_guarded=False):
    """Why a git call a guard decides on changes the git config the guard read, or None. HOME, XDG_CONFIG_HOME,
    GIT_CONFIG_GLOBAL, GIT_CONFIG_SYSTEM and GIT_CONFIG_NOSYSTEM set on it count, and so do an include and a key
    that cannot be read, given by -c, --config-env or GIT_CONFIG_*. With every_guarded, so does every key A0 lists
    but alias.*, which the parser expands, so the call is judged as what the alias runs."""
    git = call.get("git") or {}
    subcommand = git.get("subcommand") or "command"
    for name in call.get("config_env") or ():
        return (f"{name} is set on this git {subcommand}, which changes the git config it reads, so it counts as a "
                f"config write")
    for entry in git.get("config") or ():
        key = entry.get("key")
        if key is None:
            return f"this git {subcommand} sets a config key that cannot be read"
        lower = key.lower()
        if lower.startswith(("include.", "includeif.")):
            return f"this git {subcommand} sets {key}, which brings in a config file the guards did not read"
        if every_guarded and shell.guarded_key(key) and not lower.startswith("alias."):
            return f"this git {subcommand} sets {key}, which changes what the guards decide on"
    return None


# -- what a push sends (M3 slice C5d) ------------------------------------------------------------------------------

def target_key(call):
    """The key a gh call's or a git push's target is filed under in the `targets` fact: its folder and its words, as
    the parser gives them. The runner and a guard compute it from the same parser output."""
    git = call.get("git")
    folder = git.get("folder") if git else call.get("cwd")
    return json.dumps([folder, call.get("program"), call.get("args")])


READ_ONLY_REMOTE = {None, "show", "get-url"}
BRANCH_READS = {"--show-current", "-a", "--all", "-r", "--remotes", "-v", "-vv", "--verbose", "--list", "-l",
                "--no-color", "--color", "--column", "--no-column", "--merged", "--no-merged", "--contains",
                "--no-contains", "--points-at", "--sort", "--format", "--ignore-case", "-i", "--omit-empty"}


def _positional(args):
    return [word for word in args if not word.startswith("-")]


def earlier_change(calls, index):
    """Why a call before calls[index] changes what a later push sends or where it goes, or None. The runner works
    out a push's target before the command runs, so it sees the branch, the upstream and the remotes as they were:
    a `git checkout` or `switch`, a `git branch` that sets, moves or makes a branch, a `git remote` that changes a
    remote, a `worktree add` from a remote branch, a `git symbolic-ref` that moves HEAD, a `git push -u` and a
    `gh repo set-default` earlier in the same line each change that."""
    for call in calls[:index]:
        gh = call.get("gh") or {}
        if (gh.get("path") or [])[:2] == ["repo", "set-default"]:
            return "gh repo set-default earlier in the line changes the repository gh's commands act on"
        git = call.get("git") or {}
        subcommand, args = git.get("subcommand"), list(git.get("args") or [])
        if subcommand in ("checkout", "switch"):
            return (f"git {subcommand} earlier in the line can change the current branch and its upstream, which "
                    f"decide what a push sends")
        if subcommand == "remote" and git.get("action") not in READ_ONLY_REMOTE:
            return "git remote earlier in the line changes a remote, which decides where a push goes and what it sends"
        if subcommand == "branch":
            flags = {word.split("=", 1)[0] for word in args if word.startswith("-")}
            lists = bool(flags & {"--list", "-l", "--contains", "--merged", "--no-merged", "--points-at"})
            makes = bool(_positional(args)) and not lists
            if git.get("tracking") or makes or flags - BRANCH_READS:
                return "git branch earlier in the line sets, moves or makes a branch, which decides what a push sends"
        if subcommand == "worktree" and git.get("action") == "add":
            operands = _positional(args[1:])
            if git.get("tracking") or "--track" in args or any("/" in word for word in operands[1:]):
                return "git worktree add from a remote branch earlier in the line sets a branch's upstream"
        if subcommand == "symbolic-ref" and len(_positional(args)) >= 2:
            return "git symbolic-ref earlier in the line moves HEAD, which decides what a push sends"
        if subcommand == "push" and (git.get("push") or {}).get("set_upstream"):
            return "git push -u earlier in the line sets a branch's upstream, which decides where a later push goes"
    return None


def branch_name(ref):
    """The branch a destination names: refs/heads/x and heads/x give x; any other text is kept."""
    for prefix in ("refs/heads/", "heads/"):
        if ref.startswith(prefix):
            return ref[len(prefix):]
    return ref


def _glob_matches(pattern, name):
    """True when a refspec glob may match the branch: git's one `*` matches any text, slashes included."""
    for candidate in (f"refs/heads/{name}", f"heads/{name}", name):
        head, star, tail = pattern.partition("*")
        if star and candidate.startswith(head) and candidate.endswith(tail) and \
                len(candidate) >= len(head) + len(tail):
            return True
    return False


def touches_branch(update, branch):
    """True when an update may land on that branch: one that names it, a glob that may match it, or one that
    covers every branch (--all, --branches, --mirror)."""
    if update.get("every"):
        return True
    dst = update.get("dst")
    if dst is None:
        return False
    if update.get("glob"):
        return _glob_matches(dst, branch)
    return branch_name(dst) == branch


def push_updates(call, fact):
    """{"updates": [{"src", "dst", "force", "delete", "glob", "every"}], "prune": bool, "mirror": bool,
    "unresolved": why or None} for a git push, from its words and its resolved target. dst is the destination as
    git would name it; every is True for --all, --branches and --mirror. An update is forced by --force, a `+`,
    --mirror or a --force-with-lease that covers it, whether written on the line or set in config."""
    push = (call.get("git") or {}).get("push") or {}
    fact = fact or {}
    leases = push.get("force_with_lease") or []
    lease_all = "" in leases
    leased = {branch_name(value.split(":", 1)[0]) for value in leases if value}

    def forced(dst, plus):
        return bool(plus or push.get("force") or lease_all or (dst is not None and branch_name(dst) in leased))

    found = {"updates": [], "prune": bool(push.get("prune")), "mirror": False, "unresolved": None}
    if push.get("remote_dynamic") or any(spec.get("dynamic") for spec in push.get("refspecs") or ()):
        found["unresolved"] = "the remote or a branch it pushes is a variable or a substitution"
        return found
    if not fact or fact.get("unresolved"):
        found["unresolved"] = (fact or {}).get("unresolved") or "its target was not worked out"
        return found
    if push.get("mirror") or fact.get("mirror"):
        found["mirror"] = found["prune"] = True
        found["updates"].append({"src": None, "dst": None, "force": True, "delete": True, "glob": False,
                                 "every": True})
        return found
    if push.get("all") or push.get("branches"):
        found["updates"].append({"src": None, "dst": None, "force": forced(None, False), "delete": False,
                                 "glob": False, "every": True})
        for name in sorted(leased):           # --force-with-lease=NAME forces that branch alone
            found["updates"].append({"src": f"refs/heads/{name}", "dst": f"refs/heads/{name}", "force": True,
                                     "delete": False, "glob": False, "every": False})
    branch = fact.get("branch")
    explicit = push.get("refspecs") or []
    for spec in explicit:
        src, dst = spec.get("src") or "", spec.get("dst")
        if push.get("delete"):
            found["updates"].append({"src": None, "dst": spec.get("text"), "force": True, "delete": True,
                                     "glob": bool(spec.get("glob")), "every": False})
            continue
        if spec.get("delete"):
            found["updates"].append({"src": None, "dst": dst, "force": True, "delete": True,
                                     "glob": bool(spec.get("glob")), "every": False})
            continue
        if "@{-" in src or ("@{" in src and dst is None):
            found["unresolved"] = (f"{src} names a branch checked out earlier, or a reflog entry, so the branch it "
                                   f"sends or updates cannot be read from the line")
            return found
        if src in ("HEAD", "@") or src.startswith(("HEAD~", "HEAD^", "@~", "@^")):
            if dst is None:
                if not branch:
                    found["unresolved"] = "HEAD is detached, so git cannot say which branch a push of HEAD updates"
                    return found
                dst = f"refs/heads/{branch}"
            src = f"refs/heads/{branch}" if branch else src
        elif dst is None:
            dst = src
        found["updates"].append({"src": src, "dst": dst, "force": forced(dst, spec.get("force")), "delete": False,
                                 "glob": bool(spec.get("glob")), "every": False})
    if not explicit and not (push.get("all") or push.get("branches")):
        for spec in fact.get("refspecs") or []:
            dst = spec.get("dst") or spec.get("src")
            found["updates"].append({"src": spec.get("src"), "dst": dst, "force": forced(dst, spec.get("force")),
                                     "delete": False, "glob": "*" in (dst or ""), "every": False})
    return found


# -- where a URL points (M3 slice C5e) ------------------------------------------------------------------------

def parse_url(url):
    """A destination for a remote URL, by git's rules: a scheme, else host:path is ssh unless a slash comes
    before the colon, else a local path."""
    text = url.strip()
    scheme = re.match(r"^([A-Za-z][A-Za-z0-9+.-]*)://(.*)$", text)
    if scheme:
        kind, rest = scheme.group(1).lower(), scheme.group(2)
        if kind == "file":
            return {"local": True, "path": rest, "url": text}
        host_part, _, path = rest.partition("/")
        host = host_part.rsplit("@", 1)[-1].split(":", 1)[0].lower()
        return _repository(host, path, text)
    colon, slash = text.find(":"), text.find("/")
    drive = os.name == "nt" and re.match(r"^[A-Za-z]:[\\/]", text)
    if colon < 0 or (0 <= slash < colon) or drive:
        return {"local": True, "path": text, "url": text}
    host = text[:colon].rsplit("@", 1)[-1].lower()
    return _repository(host, text[colon + 1:], text)


def _repository(host, path, url):
    parts = [part for part in path.split("/") if part]
    if len(parts) < 2:
        return {"host": host, "owner": None, "name": None, "url": url}
    name = parts[-1][:-4] if parts[-1].endswith(".git") else parts[-1]
    return {"host": host, "owner": parts[-2], "name": name, "url": url}


def listed(destination, repositories):
    """True when a destination names one of the repositories, each {"host", "owner", "name"}, compared without
    regard to case, as GitHub compares them. A destination with no owner or name is never listed."""
    if not destination.get("owner") or not destination.get("name"):
        return False
    key = ((destination.get("host") or "").lower(), destination["owner"].lower(), destination["name"].lower())
    return any(key == ((entry.get("host") or "").lower(), (entry.get("owner") or "").lower(),
                       (entry.get("name") or "").lower()) for entry in repositories or ())
