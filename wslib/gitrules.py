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

A git config file is one of the files the runner lists in `git_config`: the global ones (`~/.gitconfig`,
`$XDG_CONFIG_HOME/git/config`, `~/.config/git/config`, `GIT_CONFIG_GLOBAL`) and every file an `include.path` or
`includeIf.*.path` names. The repository's own config lives under `.git`, so the segment rule covers it.
"""
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
    """The text with each $NAME or ${NAME} whose literal value the line set replaced, and HOME from the facts."""
    env, dynamic = call.get("env") or {}, set(call.get("env_dynamic") or ())

    def value(match):
        name = match.group(1) or match.group(2)
        if name in env and env[name] is not None and name not in dynamic:
            return env[name]
        if name == "HOME" and home and name not in env:
            return home
        return match.group(0)

    return VARIABLE.sub(value, text)


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


def _guarded(write):
    key = write.get("key")
    if key is None:
        return True
    if write.get("op") in ("rename-section", "remove-section"):
        return shell.guarded_key(key + ".x") or shell.guarded_key(key)
    return shell.guarded_key(key)


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
    calls = shell.analyze(event.get("command") or "")
    # A cd the parser cannot follow (one that is not the leading command, or one in a subshell) leaves a later
    # command's folder unknown. If any cd in the line enters a git folder, a relative write after it may land there.
    enters = next((arg for call in calls if call.get("program") in ("cd", "pushd") for arg in call.get("args") or []
                   if git_segment(arg) or GIT_FOLDER_HINTS.search(arg)), None)
    reasons = []
    for call in calls:
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
            if write.get("via") != "git config" or write.get("op") not in PERSISTENT_OPS or not _guarded(write):
                continue
            scope = write.get("scope") or ""
            if scope.startswith("--file ") and "$" not in scope and \
                    not _config_file(place(scope[7:], cwd, call.get("cwd"), facts.home), facts.files):
                continue                  # a file git reads no config from
            key = write.get("key") or "a key it cannot read"
            reasons.append(f"git config {write['op']} of {key} rewrites a git config file, and that key decides "
                           f"where a push goes, what a git command runs, or which folder git works on. Every guard "
                           f"reads it, so an agent does not change it; a person does, from their own terminal")
    return reasons


# -- aliases and unresolved calls ---------------------------------------------------------------------------------

def _needs_alias(call):
    git = call.get("git")
    return bool(git) and git.get("subcommand") is not None and not git.get("builtin") and not git.get("unresolved")


def read(event):
    """(calls, why). The command's calls, with each git alias expanded from the aliases the runner read from config
    in that call's folder (the `aliases` fact). When the aliases a call needs were not read, or two folders' aliases
    differ, the calls come back unexpanded and why says so; `unresolved` then refuses each call that needs one."""
    command = event.get("command") or ""
    found = shell.analyze(command)
    needing = [call for call in found if _needs_alias(call)]
    if not needing:
        return found, None
    table = event.get("aliases") or {}
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
        return f"git {subcommand} is neither one of git's own commands nor an alias"
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
