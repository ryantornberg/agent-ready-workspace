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
    unreadable(command)    -> why the shell would run the command otherwise than the parser reads it, or None: a
                              program word it expands, an ANSI-C or NUL escape, a (( that holds a command, braces
                              in a wrapper's own words, a judged name among the words of a program the parser does
                              not read, a line nested too deep, git or gh in another letter case (M3 slices Z and
                              GFIX, the maintainer's answers to Q54, Q74, Q77 and Q75).
    expands(text)          -> True when the shell may expand a program word written so.

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

# Programs that write the files they are given. When xargs or find -exec supplies those files at run time, no guard
# can know which they are.
WRITERS = {"rm", "cp", "mv", "ln", "truncate", "install", "rsync", "touch", "tee", "dd", "unlink", "rmdir", "shred"}
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


def _config_file(absolute, files):
    """True for a git config file: one the runner listed, or a repository's own config under its git folder."""
    if absolute is None:
        return False
    parts = absolute.split("/")
    return absolute in files or (".git" in parts and parts[-1] in ("config", "config.worktree"))


def _guarded(write):
    """True for a persistent `git config` write the guards refuse, as the parser judges it: a key it lists, a
    section that holds one, and a key or a name that cannot be read."""
    return write.get("key") is None or bool(write.get("guarded"))


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
        if any(write.get("via") == "find -delete" for write in call.get("writes") or ()):
            reasons.append("find -delete removes whatever it finds when it runs, so no guard can tell whether that is "
                           "in a git folder. Remove named files with rm, or ask the person")
            continue
        # A cd the parser cannot follow (one that is not the leading command, or one in a subshell) leaves this
        # command's folder unknown, and the parser names the folders the cds before it entered. If one is a git
        # folder, a relative write here may land there.
        enters = next((folder for folder in call.get("cd_folders") or ()
                       if git_segment(folder) or GIT_FOLDER_HINTS.search(folder)), None)
        for write in call.get("writes") or ():
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
            if write.get("op") == "rename-section":
                key = f"{key} to {write.get('new_key') or 'a name it cannot read'}"
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
    """owner and name are the URL's last two segments; path is the whole repository path, so a group nested on
    GitLab or an Azure Repos project is told apart from another of the same last two names."""
    parts = [part for part in path.split("/") if part]
    if len(parts) < 2:
        return {"host": host, "owner": None, "name": None, "url": url}
    name = parts[-1][:-4] if parts[-1].endswith(".git") else parts[-1]
    return {"host": host, "owner": parts[-2], "name": name, "url": url, "path": "/".join(parts[:-1] + [name])}


def _path(place):
    return (place.get("path") or f"{place.get('owner')}/{place.get('name')}").strip("/").lower()


def listed(destination, repositories):
    """True when a destination names one of the repositories: the same host and the same whole repository path,
    OWNER/NAME on GitHub, compared without regard to case, as GitHub compares them. A destination with no owner or
    name is never listed."""
    if not destination.get("owner") or not destination.get("name"):
        return False
    key = ((destination.get("host") or "").lower(), _path(destination))
    return any(key == ((entry.get("host") or "").lower(), _path(entry)) for entry in repositories or ())


# -- A command no guard can read (Q54, Q74, Q75) -----------------------------------------------------------------
# One block, held twice: in wslib/gitrules.py and in parts/no_admin_merge.py, which a grader loads with the parser
# alone. tests/test_shell.py holds the two copies equal. It needs only `re` and the parser, `shell`.
#
# The parser misreads some lines, and then every guard judges a command the shell will not run. Until the parser's
# own fixes in M4, each shell guard refuses such a line in its own part file, as a command it cannot judge:
# - a program word the shell expands: a glob, braces, zsh's extended glob or zsh's =NAME (Q54);
# - an ANSI-C quoted escape that the shell makes a printable ASCII character, a tab or a new line, such as $'\x66',
#   $'\146', $'f', $'\x0a', bash's $'\cJ' or zsh's $'\C-j', where the parser keeps the letters after the
#   backslash; and a NUL escape in a word that holds anything else, such as git$'\0' or $'\0'git, since bash cuts
#   the quoted text at a NUL and keeps the rest of the word, and zsh hands the program the word up to it. A word
#   that is only NUL escapes, after an optional NAME= or --option=, such as read -d $'\0', passes, except among
#   the words of eval or watch, which join them into a line where the parser misreads it. An octal escape counts
#   by its low eight bits, as both shells read it, so \547 is g and \400 a NUL (Q74, slice GFIX);
# - a (( that the parser reads as arithmetic and that may hold a command: ((git push) ), which the shell runs as
#   two subshells, or any substitution inside one, such as $(( $(git push) )), whose command the parser never
#   reads (Q74);
# - braces, a glob, or an unquoted variable or substitution among a wrapper's or a shell's own words, before its
#   program: nice -n {5,git} push becomes nice -n 5 git push (Q74);
# - a program the parser does not read, such as arch, script, flock or NICE, one of whose words is, as written,
#   the name of a program the guards judge: git, /usr/bin/git, 'gh', env, printenv, pwsh, powershell or a shell
#   the parser reads. No list of such programs is kept, so every program the parser does not read is judged so. A
#   variable, a substitution, braces or a glob among its words, and the text it may run, are not read: those wait
#   for the parser's fix in M4 (Q74, narrowed by Q77, slice GFIX);
# - a wrapper, shell, eval, watch or find inside MAX_DEPTH nested shells or evals, which the parser does not
#   unwrap there (Q74);
# - git or gh named in another letter case, such as GIT or /usr/bin/Gh, which macOS and Windows run as git or gh
#   by default and the parser does not (Q75, slice GFIX).
EXPANDING = re.compile(r"[*?\[{}#^]|.~|^=")
BRACES = re.compile(r"\{[^{}]*(?:,|\.\.)[^{}]*\}")
GLOB = re.compile(r"[*?\[]")
ANSI_ESCAPE = re.compile(r"\\(?:([0-7]{1,3})|x([0-9a-fA-F]{1,2})|u([0-9a-fA-F]{1,4})|U([0-9a-fA-F]{1,8})|c(.)|C-(.))",
                         re.S)
ARITH_WORDS = re.compile(r"[\w.'\"]\s+['\"A-Za-z_]|\$\(|`")
# A word that is only NUL escapes in one $'...', after an optional NAME= or --option=: the program gets an empty word
# or an empty value, as in read -d $'\0'.
ONLY_NUL = re.compile(r"(?:-{0,2}[\w.-]+=)?\$'(?:\\(?:0{1,3}|x0{1,2}|u0{1,4}|U0{1,8}|c@|C-@))+'")
# The programs the guards judge by name, or that run text, or that dump the environment. eval is left out: it is a
# shell builtin, which a program that runs another cannot start, so `claude plugin eval` or `grep eval` passes.
JUDGED = frozenset({"git", "gh", "env", "printenv", "pwsh", "powershell"}) | shell.SHELL_PROGRAMS
# The two the parser reads by name, which a file system that ignores letter case runs in any case (Q75).
CASED = frozenset({"git", "gh"})
# The programs the parser reads itself, its wrappers and shells among them; past MAX_DEPTH it unwraps none of
# them but git and gh.
READ = frozenset({"git", "gh", "find", "eval", "watch"}) | shell.SHELL_PROGRAMS | frozenset(shell.WRAPPER_OPTIONS)
UNWRAPPED = READ - {"git", "gh"}
# The programs the parser reads that join their words into a line, so a word of only NUL escapes changes it.
JOINING = frozenset({"eval", "watch"})


def expands(text):
    """True when the shell may expand a program word written so into another name, or into several words (Q54)."""
    return text not in ("[", "[[") and bool(EXPANDING.search(text))


def _written(text):
    """A program word's name as written: its last part, without .exe in any case."""
    name = text.replace("\\", "/").rsplit("/", 1)[-1]
    return name[:-4] if name.lower().endswith(".exe") else name


def _parsed(text):
    """A program word's name as the parser reads it: its last part after a slash, without .exe in any case, and
    in its own letter case, so NICE is not the nice the parser unwraps (slice GFIX)."""
    name = text.rsplit("/", 1)[-1]
    return name[:-4] if name.lower().endswith(".exe") else name


def _base(text):
    """A program word's name as the shell finds it: its last part, without .exe, in lower case, since macOS and
    Windows find a program whatever its case."""
    return _written(text).lower()


def _close(raw, i):
    """The position after the quoted span that starts at i: '...', "..." or $'...'."""
    if raw.startswith("$'", i) or raw[i] == '"':
        j, stop = (i + 2, "'") if raw[i] == "$" else (i + 1, '"')
        while j < len(raw) and raw[j] != stop:
            j += 2 if raw[j] == "\\" else 1
        return min(j + 1, len(raw))
    end = raw.find("'", i + 1)
    return len(raw) if end < 0 else end + 1


def _unquoted(raw):
    """A word's source with its quoted and escaped parts blanked, so only what the shell expands is left."""
    out, i = [], 0
    while i < len(raw):
        if raw[i] == "\\" or raw[i] in "'\"" or raw.startswith("$'", i):
            end = min(i + 2, len(raw)) if raw[i] == "\\" else _close(raw, i)
            out.append("_" * (end - i))
            i = end
        else:
            out.append(raw[i])
            i += 1
    return "".join(out)


def _ansi_c(raw):
    """Why a word's source holds an ANSI-C escape that the shell makes a character the parser misses, or None."""
    i = 0
    while i < len(raw):
        if raw.startswith("$'", i):
            end = _close(raw, i)
            for match in ANSI_ESCAPE.finditer(raw, i + 2, end):
                if raw[i + 2:match.start()].replace("\\\\", "").endswith("\\"):
                    continue                     # \\x41: an escaped backslash, then plain letters
                control = match.group(5) or match.group(6)
                if control is not None:
                    code = ord(control) & 0x1F                 # bash's \cJ, zsh's \C-j: here a new line
                else:
                    code = int(next(group for group in match.groups() if group), 8 if match.group(1) else 16)
                    code = code & 0xFF if match.group(1) else code   # \547 is g, \400 a NUL: the low 8 bits
                if code in (0x09, 0x0A) or 0x20 <= code <= 0x7E:
                    return (f"its word `{raw}` holds the ANSI-C escape `{match.group(0)}`, which the shell makes a "
                            f"character the parser does not read")
                if code == 0 and ONLY_NUL.fullmatch(raw):
                    _Parser.nul.add(raw)               # judged by the program that gets it: eval or watch
                elif code == 0:
                    return (f"its word `{raw}` holds the NUL escape `{match.group(0)}` beside other text, and the "
                            f"shell drops part of the word at a NUL, which the parser does not read")
            i = end
        elif raw[i] == "\\":
            i += 2
        elif raw[i] in "'\"":
            i = _close(raw, i)
        else:
            i += 1
    return None


def _arithmetic(text):
    """Why a (( ... )) the parser reads as arithmetic may hold a command, or None (Q74)."""
    if not text.endswith("))") or ARITH_WORDS.search(text[2:-2]):
        return (f"`{text}` is read as arithmetic, but the shell may run it as a command, or run the commands inside "
                f"it, which the parser does not read")
    return None


class _Parser(shell._Parser):
    """The parser, noting each word's source and what it misreads (Q74). It stands in for shell._Parser while
    unreadable walks a line, so the text of sh -c, eval and substitutions is read by it too."""
    found, raw, nul = [], {}, set()

    def _read_word(self):
        start = self.i
        word = super()._read_word()
        _Parser.raw[id(word)] = self.s[start:self.i]
        why = _ansi_c(self.s[start:self.i])
        if why:
            _Parser.found.append(why)
        return word

    def _match_parens(self, start):
        end = super()._match_parens(start)
        if self.s.startswith("((", start):
            why = _arithmetic(self.s[start:end])
            if why:
                _Parser.found.append(why)
        return end


def _source(word):
    """The word's source with its quoted parts blanked, or its text when the parser made the word itself."""
    raw = _Parser.raw.get(id(word))
    return word.text if raw is None else _unquoted(raw)


class _Reader(shell._Walker):
    """The parser's own walk, noting each program word as written and each command no guard can read."""

    def dispatch(self, words, own, writes, records, ctx, *rest):
        self.words.append(words[0])
        why = None if words[0].dynamic else self._unread(words, ctx)
        if why:
            self.found.append(why)
        return super().dispatch(words, own, writes, records, ctx, *rest)

    def _unread(self, words, ctx):
        written, lower = _written(words[0].text), _base(words[0].text)
        if lower in CASED and written != lower:
            return (f"its program word `{words[0].text}` names {lower} in another letter case, which macOS and "
                    f"Windows run as {lower}, and the parser does not read it as {lower}. Write `{lower}`")
        name = _parsed(words[0].text)   # the parser's own name: NICE or BASH is a program it does not read
        if ctx.depth >= shell.MAX_DEPTH and name in UNWRAPPED:
            return (f"the line nests shells, eval or sh -c text {shell.MAX_DEPTH} deep, and the parser does not "
                    f"read `{words[0].text}` there")
        if name in shell.WRAPPER_OPTIONS or name in shell.SHELL_PROGRAMS:
            inner = self._unwrap(name, words[1:]) if name in shell.WRAPPER_OPTIONS else None
            if name == "command" and inner is None:
                return None                      # command -v $p looks a name up and runs nothing, whatever $p is
            own_words = words[1:len(words) - len(inner[0])] if inner else words[1:]
            if name in shell.SHELL_PROGRAMS:
                first = next((k for k, word in enumerate(own_words) if not word.text.startswith(("-", "+"))
                              or word.text in ("-", "--")), len(own_words))
                own_words = own_words[:first + 1]
            for word in own_words:
                source = _source(word)
                if BRACES.search(source) or GLOB.search(source) or "$" in source or "`" in source:
                    return (f"`{word.text}` is one of {name}'s own words, and the shell may make it several words, "
                            f"one of them the program, so no guard can tell which runs. Quote it, or write it "
                            f"literally")
            return None
        if name in JOINING and any(_Parser.raw.get(id(word)) in _Parser.nul for word in words[1:]):
            return (f"`{words[0].text}` joins its words into a line, and a word of only NUL escapes there makes "
                    f"another word the program, which the parser does not read")
        if name in READ:
            return None
        for word in words[1:]:
            if not word.dynamic and _base(word.text) in JUDGED:
                judged = _base(word.text)
                return (f"`{words[0].text}` may run another program, and its word `{word.text}` names `{judged}`, "
                        f"which the parser does not read as a program there. To run `{judged}`, make it the "
                        f"command itself; if the word is only text, write it inside a longer quoted string, and "
                        f"look a program up with `command -v {judged}`")
        return None


def unreadable(command):
    """Why the shell would run the command otherwise than the parser reads it, or None (Q54, Q74, Q75)."""
    walker = _Reader(None, ("github.com",))
    walker.words, walker.found = [], []
    saved, shell._Parser = shell._Parser, _Parser
    _Parser.found, _Parser.raw, _Parser.nul = walker.found, {}, set()
    try:
        walker.walk_list(shell.parse(command or ""), shell._Context(), [], True)
    except RecursionError:   # this walk adds a frame per wrapper, so it can run out before the parser does
        return "the line nests too deeply to read each program word"
    finally:
        shell._Parser = saved
        _Parser.found, _Parser.raw, _Parser.nul = [], {}, set()
    for word in walker.words:
        if not word.dynamic and expands(word.text):
            return (f"its program word `{word.text}` is a pattern the shell expands (a glob, braces or a zsh "
                    f"pattern), so no guard can tell which program runs")
    return walker.found[0] if walker.found else None
# -- End of the block held twice. ------------------------------------------------------------------------------
