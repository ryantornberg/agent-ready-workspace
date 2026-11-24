"""The shell command-line parser every shell hook shares.

It reads a command line; it never runs a shell. Two layers live here.

**The first layer** is the one `no_stage_all` and `no_admin_merge` were built on, moved here unchanged so
their decisions stay as recorded: `flatten`, `segments`, `git_calls`, `calls` and `options`, with `KEYWORDS`,
`WRAPPERS` and `SHELLS`. It follows separators, new lines, subshells, `sh -c`, `eval` and common wrappers, and
skips heredoc bodies and quoted text.

**The second layer** is `analyze(command, aliases=None, hosts=("github.com",))`. It parses the line as a shell
does: quotes, escapes, `$(...)` and backticks (also inside double quotes), heredocs, `( )` subshells, `{ }`
groups, `if`/`while`/`for`/`case`, pipelines and `&&`/`||` chains. It returns one dict per simple command found
anywhere in the line, in the order the shell would start them (a substitution before the command that holds it),
so a guard learns everything it decides on without parsing again:

    program         basename of the program word after wrappers and assignments (".exe" dropped); None for a
                    command that is only redirections. A program word that is a variable is kept as written.
    args            the argument words after the program, quotes removed. A variable or substitution keeps its
                    spelling: "$B", "$(git branch --show-current)".
    dynamic_args    indexes into args of words that hold a variable or substitution. Message bodies are left out.
    message_args    indexes into args of message bodies: git commit/tag/merge -m -F --message --file, and gh
                    --body --title --body-file (and their kin) on the commands that take a message.
    env             {NAME: value or None}: assignments on the command (X=Y cmd, env X=Y cmd, sudo X=Y cmd) and
                    from an earlier export or assignment in the same shell. None means unset (env -u, unset).
    env_dynamic     the names in env whose value holds a variable or substitution.
    env_cleared     True under env -i.
    wrappers        how the command was reached, outermost first: "sudo", "env", "timeout", "xargs",
                    "find -exec", "sh -c", "eval", "git rebase --exec", "ws.py with-secrets", ... A line that runs
                    `ws.py with-secrets NAME ... -- PROGRAM ...` (by python, the launcher or ws.py itself) is
                    read as that wrapper, so the command is PROGRAM.
    in_substitution True inside $(...), backticks or <(...).
    in_subshell     True inside ( ) or a substitution.
    unresolved      None, or why no guard can know what runs: the program word is a variable or substitution,
                    text is piped into a shell, or eval / sh -c / env -S runs text that holds a variable.
    runtime_args    None, "xargs" or "find -exec": arguments are supplied at run time.
    cwd             the folder the command runs in, relative to the session's folder ("." when unchanged), or
                    None when it cannot be known.
    cwd_unresolved  why cwd is None.
    cd_folders      when cwd is None, the folder each cd or pushd earlier in this shell named, as written, so a
                    guard can tell where a relative write after a cd the parser cannot follow may land; [] when
                    cwd is known.
    writes          [{"path", "dynamic", "via"}]: >, >>, >|, &>, <>, tee, cp (target), mv (source and target),
                    sed -i, dd of=, rm, unlink, rmdir, shred, ln, truncate, install, rsync, touch,
                    git config --file, the operands of git mv, rm, checkout and restore (after any -C folder;
                    a checkout's branch too, since the words cannot tell it from a path), and find -delete, whose
                    path is each folder it starts from ("." when it names none), since the files it removes are
                    known only when it runs.
    config_writes   [{"key", "value", "op", "via", "guarded"}]: git config written by git -c, git config,
                    GIT_CONFIG_COUNT/KEY_n/VALUE_n or GIT_CONFIG_PARAMETERS. key is None when unknowable.
                    guarded is True for remote.*, url.*, push.*, branch.*.pushRemote, branch.*.merge,
                    remote.pushDefault, include.*, includeIf.*, alias.*, core.worktree and core.sshCommand,
                    and for any key that cannot be known (guarded_key). A persistent `git config` write is also
                    guarded for the keys in PERSISTENT_GUARDED, such as core.hooksPath, and a rename or
                    removal of a section is guarded when the section, or the new name, holds such a key
                    (guarded_section). A rename's write also gives "new_key", the new name, None when it
                    cannot be read.
    config_env      the config-affecting variables set on it: HOME, XDG_CONFIG_HOME, GIT_CONFIG_GLOBAL,
                    GIT_CONFIG_SYSTEM, GIT_CONFIG_NOSYSTEM (HOME too under env -i).
    reads           [{"path", "dynamic", "via"}]: the command's input redirections, < and <>, as writes are given,
                    inside substitutions, eval and a shell's -c text in every flag form too.
    ssh_env         GIT_SSH and GIT_SSH_COMMAND, when set.
    git             None, or the git facts below.
    gh              None, or the gh facts below.

`git` holds:

    subcommand      after global options and alias expansion; None for `git --version`. Kept as written when
                    it is a variable.
    args            the words after the subcommand (after alias expansion).
    builtin         whether the subcommand is one of git's own commands.
    alias           None, or {"name", "expansion", "source": "-c" | "config"}.
    unresolved      None, or why the subcommand is unknown: a variable, a "!" shell alias, an alias that sets
                    the environment, or (only when `aliases` is given) a name that is neither built in nor an
                    alias. With aliases=None such a name is reported with builtin False and nothing more.
    globals         the global option words before the subcommand.
    config          [{"key", "value", "dynamic"}] from -c, --config-env and GIT_CONFIG_* values, in order.
    folder          the folder the call acts on: --git-dir/GIT_DIR if given, else --work-tree/GIT_WORK_TREE,
                    else the working folder after a leading cd/pushd, env -C and every -C (repeated -C
                    compose). None when unresolved.
    folder_unresolved  why folder is None: a variable in one of those, a cd that is not the leading command,
                    a cd inside a subshell, core.worktree (by -c, GIT_CONFIG_* or an earlier git config),
                    GIT_INDEX_FILE or GIT_COMMON_DIR.
    cwd, git_dir, work_tree   the pieces folder is made from (None when not given).
    action          the second word of stash, worktree, remote, config (new syntax), submodule, notes, ...
    discard         canonical names of the forms that drop work: "switch --force", "checkout --force",
                    "read-tree --reset -u", "reset --hard", "reset --keep", "reset --merge", "autostash",
                    "stash drop", "stash pop", "stash clear", "worktree remove", "worktree remove --force",
                    "worktree prune", "clean --force", "whole-tree checkout" and "whole-tree restore" (a pathspec
                    of ".", ":/", "*" or only "." and "..", or --pathspec-from-file; a restore of --staged alone
                    is not one), "stash write" (push, save, store and a plain stash), "rebase" and
                    "cherry-pick".
    pull_rebase     True for a pull that rebases (-r, --rebase, -c pull.rebase).
    tracking        True for -t/--track, -u/--set-upstream(-to), push -u.
    remote          None, or {"action", "name", "url", "push", "dynamic"} for git remote add / set-url / ...
    push            None, or {"remote", "remote_dynamic", "refspecs": [{"text", "src", "dst", "force",
                    "delete", "glob", "dynamic"}], "force", "force_with_lease": [values], "force_if_includes",
                    "mirror", "all", "branches", "delete", "prune", "tags", "follow_tags", "set_upstream",
                    "dry_run", "unknown_options"}.

`gh` holds:

    path            the subcommand path: ["pr", "merge"], ["api"], ["repo", "set-default"].
    args            the words after the path.
    repo            {"text", "host", "owner", "name", "dynamic", "source": "-R" | "--repo" | "GH_REPO"} or None.
    repo_argument   the repository a `gh repo view|edit|delete|...` names as its first operand, parsed alike.
    target_urls     [{"host", "owner", "name"}] for operands that are GitHub URLs.
    host            the host from --hostname, the repository, an api URL or GH_HOST; None means github.com.
    unresolved      None, or why the target is unknown: a host that is not in `hosts`, a host or subcommand
                    that is a variable.
    api             None, or {"endpoint", "path", "dynamic", "graphql", "method", "effective_method",
                    "fields": [{"flag", "key", "value", "raw", "file", "dynamic"}], "input", "headers",
                    "owner", "repo", "placeholders"} for gh api. graphql is True for graphql, /graphql, an
                    absolute URL to it, and each with a query string. "file" is the path a -F key=@path reads.

What it cannot see, the hooks' pages say: a script, an interpreter, a shell alias or function defined elsewhere,
a gh alias, PowerShell.
"""
import posixpath
import re
import shlex

# ---------------------------------------------------------------------------------------------------------------
# The first layer: moved from parts/no_stage_all.py and parts/no_admin_merge.py without a change in behaviour.
# ---------------------------------------------------------------------------------------------------------------

KEYWORDS = {"if", "then", "else", "elif", "do", "while", "until", "!", "{", "}", "fi", "done"}
WRAPPERS = {"sudo", "command", "env", "exec", "time", "nohup", "timeout", "nice", "xargs", "builtin"}
SHELLS = {"sh", "bash", "zsh", "dash", "ksh"}
OPTIONS_WITH_A_VALUE = {"-C", "-c", "--git-dir", "--work-tree", "--namespace", "--exec-path"}
# Options that take a value, so the value is not read as a flag or a pathspec: -m"add a test" holds no -a.
SHORT_VALUES = {"commit": "mFCct"}
LONG_VALUES = {"commit": ("--message", "--file", "--reuse-message", "--reedit-message", "--template", "--author",
                          "--date", "--cleanup", "--fixup", "--squash", "--trailer", "--pathspec-from-file"),
               "add": ("--chmod", "--pathspec-from-file")}


def long_option(argument, option):
    """True when argument is --option or an unambiguous-looking abbreviation of it, as git accepts."""
    return len(argument) >= 4 and argument.startswith("--") and option.startswith(argument.split("=")[0])


HEREDOC = re.compile(r"<<-?\s*(['\"]?)([A-Za-z_]\w*)\1")


def flatten(command):
    """Drop heredoc bodies, and turn each new line outside quotes into a command separator."""
    kept, waiting = [], []
    for line in command.replace("\\\n", " ").split("\n"):
        if waiting:
            if line.strip() == waiting[0]:
                waiting.pop(0)
            continue
        waiting = [match.group(2) for match in HEREDOC.finditer(line)]
        kept.append(line)
    out, quote, escaped = [], None, False
    for char in "\n".join(kept):
        if escaped:
            escaped = False
        elif char == "\\" and quote != "'":
            escaped = True
        elif quote:
            if char == quote:
                quote = None
        elif char in "'\"":
            quote = char
        elif char == "\n":
            char = " ; "
        out.append(char)
    return "".join(out)


def segments(command):
    """Yield the word list of each simple command in a command line."""
    for line in [flatten(command)]:
        try:
            lexer = shlex.shlex(line, posix=True, punctuation_chars=True)
            lexer.whitespace_split = True
            tokens = list(lexer)
        except ValueError:
            tokens = line.split()
        words = []
        for token in tokens + [";"]:
            if token and set(token) <= set("&|;()"):
                if words:
                    yield words
                words = []
            else:
                words.append(token)


def _unwrap(words, program):
    """Drop keywords, wrappers, assignments and a wrapper's options in front of a command, as the first layer does."""
    wrapped = False
    while words and (words[0] in KEYWORDS or words[0] in WRAPPERS or re.match(r"^\w+=", words[0])
                     or (len(words) > 1 and words[0].startswith("-")) or re.match(r"^\d+(\.\d+)?[smhd]?$", words[0])):
        wrapped = wrapped or words[0] in WRAPPERS
        words = words[1:]
    # A wrapper's own options may take values (sudo -u me git ...): look past them for the program.
    if wrapped and words and program in words and words[0].rsplit("/", 1)[-1] not in SHELLS:
        words = words[words.index(program):]
    return words


def calls(command, program, depth=0):
    """Yield the arguments of each call of `program` in a shell command line."""
    for words in segments(command):
        words = _unwrap(words, program)
        if not words:
            continue
        name = words[0].rsplit("/", 1)[-1]
        if name == "eval" and depth < 3:
            yield from calls(" ".join(words[1:]), program, depth + 1)
        elif name in SHELLS and depth < 3:
            flags = [i for i, w in enumerate(words) if re.match(r"^-[A-Za-z]*c$", w)]
            if flags and len(words) > flags[0] + 1:
                yield from calls(words[flags[0] + 1], program, depth + 1)
        elif name in (program, program + ".exe"):
            yield words[1:]


def git_calls(command, depth=0):
    """Yield (subcommand, arguments) for each git call in a shell command line."""
    for words in segments(command):
        # git has to be the command, not a word in its arguments: `echo git add -A` stages nothing.
        words = _unwrap(words, "git")
        if not words:
            continue
        program = words[0].rsplit("/", 1)[-1]
        if program == "eval" and depth < 3:
            yield from git_calls(" ".join(words[1:]), depth + 1)
        elif program in SHELLS and depth < 3:
            flags = [i for i, w in enumerate(words) if re.match(r"^-[A-Za-z]*c$", w)]
            if flags and len(words) > flags[0] + 1:
                yield from git_calls(words[flags[0] + 1], depth + 1)
        elif program == "git":
            rest = words[1:]
            while rest and rest[0].startswith("-"):
                rest = rest[2:] if rest[0] in OPTIONS_WITH_A_VALUE else rest[1:]
            if rest:
                yield rest[0], rest[1:]


def options(subcommand, arguments):
    """(short flags, long options, pathspecs) of one git call, with each option's value set aside."""
    takes, long_values = SHORT_VALUES.get(subcommand, ""), LONG_VALUES.get(subcommand, ())
    short, longs, specs, rest = set(), [], [], list(arguments)
    while rest:
        argument = rest.pop(0)
        if argument == "--":
            specs += rest
            break
        if not argument.startswith("-") or argument == "-":
            specs.append(argument)
        elif argument.startswith("--"):
            longs.append(argument)
            if "=" not in argument and any(long_option(argument, option) for option in long_values) and rest:
                rest.pop(0)
        else:
            for position, flag in enumerate(argument[1:]):
                short.add(flag)
                if flag in takes:
                    if position == len(argument) - 2 and rest:   # the value is the next word, not attached
                        rest.pop(0)
                    break
    return short, longs, specs


# ---------------------------------------------------------------------------------------------------------------
# The second layer: a shell parser, and the facts each command carries.
# ---------------------------------------------------------------------------------------------------------------

MAX_DEPTH = 8

GIT_BUILTINS = frozenset("""
add am annotate apply archimport archive backfill bisect blame branch bugreport bundle cat-file check-attr
check-ignore check-mailmap check-ref-format checkout checkout-index cherry cherry-pick citool clean clone column
commit commit-graph commit-tree config count-objects credential credential-cache credential-cache--daemon
credential-store cvsexportcommit cvsimport cvsserver daemon describe diagnose diff diff-files diff-index diff-pairs
diff-tree difftool fast-export fast-import fetch fetch-pack filter-branch fmt-merge-msg for-each-ref for-each-repo
format-patch fsck fsck-objects fsmonitor--daemon gc get-tar-commit-id grep gui gui--askpass hash-object help hook
http-backend http-fetch http-push imap-send index-pack init init-db instaweb interpret-trailers last-modified log
ls-files ls-remote ls-tree mailinfo mailsplit maintenance merge merge-base merge-file merge-index merge-octopus
merge-one-file merge-ours merge-recursive merge-recursive-ours merge-recursive-theirs merge-resolve merge-subtree
merge-tree mergetool mktag mktree multi-pack-index mv name-rev notes p4 pack-objects pack-redundant pack-refs
patch-id pickaxe prune prune-packed pull push quiltimport range-diff read-tree rebase receive-pack reflog refs
remote remote-ext remote-fd remote-ftp remote-ftps remote-http remote-https repack replace replay repo
request-pull rerere reset restore rev-list rev-parse revert rm send-email send-pack sh-i18n--envsubst shell
shortlog show show-branch show-index show-ref sparse-checkout stage stash status stripspace submodule
submodule--helper svn switch symbolic-ref tag unpack-file unpack-objects update-index update-ref
update-server-info upload-archive upload-archive--writer upload-pack var verify-commit verify-pack verify-tag
version web--browse whatchanged worktree write-tree
""".split())

SHELL_PROGRAMS = SHELLS | {"ash", "mksh", "fish"}
CONFIG_ENV = ("HOME", "XDG_CONFIG_HOME", "GIT_CONFIG_GLOBAL", "GIT_CONFIG_SYSTEM", "GIT_CONFIG_NOSYSTEM")
SSH_ENV = ("GIT_SSH", "GIT_SSH_COMMAND")
FOLDER_BREAKERS = ("GIT_INDEX_FILE", "GIT_COMMON_DIR")
SKIPPED_KEYWORDS = {"!", "{", "}", "then", "else", "elif", "do", "done", "fi", "esac", "if", "while", "until",
                    "coproc", "time"}

# Wrappers that run the rest of their words as a command: (short options that take a value, long ones that do).
WRAPPER_OPTIONS = {
    "sudo": ("uUghpCDrtTR", ("user", "group", "host", "prompt", "close-from", "chdir", "role", "type", "other-user",
                             "command-timeout", "chroot")),
    "doas": ("uC", ()),
    "env": ("uCSP", ("unset", "chdir", "split-string", "block-signal", "default-signal", "ignore-signal")),
    "command": ("", ()),
    "builtin": ("", ()),
    "exec": ("a", ()),
    "time": ("of", ("output", "format")),
    "nohup": ("", ()),
    "timeout": ("sk", ("signal", "kill-after")),
    "nice": ("n", ("adjustment",)),
    "stdbuf": ("ioe", ("input", "output", "error")),
    "ionice": ("cnp", ("class", "classdata", "pid")),
    "setsid": ("", ()),
    "chronic": ("", ()),
    "unbuffer": ("", ()),
    "nocorrect": ("", ()),
    "noglob": ("", ()),
    "caffeinate": ("wt", ()),
    "xargs": ("adEILnPsel", ("arg-file", "delimiter", "eof", "replace", "max-lines", "max-args", "max-procs",
                             "max-chars", "process-slot-var")),
}
_ENV_OPTIONS = {"-u": "unset", "--unset": "unset", "-C": "chdir", "--chdir": "chdir", "-S": "split",
                "--split-string": "split"}

# Commands that take a message body, and the options that carry it.
GIT_MESSAGE_OPTIONS = {
    "commit": ("-m", "-F", "--message", "--file"), "tag": ("-m", "-F", "--message", "--file"),
    "merge": ("-m", "-F", "--message", "--file"), "notes": ("-m", "-F", "--message", "--file"),
    "stash": ("-m", "--message"), "commit-tree": ("-m", "-F"),
}
GH_MESSAGE_PATHS = {("pr", "create"), ("pr", "edit"), ("pr", "comment"), ("pr", "review"), ("pr", "merge"),
                    ("pr", "close"), ("issue", "create"), ("issue", "edit"), ("issue", "comment"),
                    ("issue", "close"), ("release", "create"), ("release", "edit"), ("gist", "create"),
                    ("gist", "edit"), ("repo", "create"), ("repo", "edit")}
GH_MESSAGE_OPTIONS = ("-b", "--body", "-t", "--title", "-F", "--body-file", "--subject", "-n", "--notes",
                      "--notes-file", "-c", "--comment")
GH_GROUPS = {"pr", "issue", "repo", "release", "gist", "run", "workflow", "secret", "variable", "label", "project",
             "codespace", "cs", "cache", "ruleset", "rs", "attestation", "at", "auth", "config", "extension", "ext",
             "extensions", "gpg-key", "ssh-key", "org", "search", "alias", "completion", "preview", "agent-task"}
GH_THIRD_LEVEL = {("repo", "deploy-key"), ("repo", "autolink"), ("repo", "gitignore"), ("repo", "license"),
                  ("codespace", "ports"), ("cs", "ports")}
GH_REPO_OPERAND = {"view", "clone", "edit", "delete", "fork", "archive", "unarchive", "set-default", "sync"}
GH_API_VALUES = ("-X", "--method", "-f", "--raw-field", "-F", "--field", "-H", "--header", "--input", "-q", "--jq",
                 "-t", "--template", "--hostname", "--cache", "-p", "--preview")


class Word:
    """One shell word: its text with quotes removed, whether it holds a variable or substitution, and the command
    lists of the substitutions inside it."""
    __slots__ = ("text", "dynamic", "quoted", "subs", "head")

    def __init__(self, text="", dynamic=False, quoted=False, subs=None, head=""):
        self.text, self.dynamic, self.quoted, self.subs, self.head = text, dynamic, quoted, subs or [], head

    @property
    def literal(self):
        return not self.quoted and not self.dynamic

    @property
    def assign(self):
        """(name, value) when the word is NAME=value or NAME+=value as the shell reads an assignment."""
        match = re.match(r"^([A-Za-z_]\w*)\+?=", self.head)
        return (match.group(1), self.text[match.end():]) if match else None

    def __repr__(self):
        return f"Word({self.text!r}{', dynamic' if self.dynamic else ''})"


def _literal(text):
    return Word(text, head=text)


class _Parser:
    """A recursive-descent reader of POSIX shell syntax, enough to find every simple command."""

    OPERATORS = (";;&", "&>>", "<<<", "<<-", ";;", ";&", "&&", "||", "|&", "&>", ">>", ">|", ">&", "<<", "<>",
                 "<&", ";", "&", "|", "(", ")", ">", "<")
    REDIRECTIONS = {"&>>", "<<<", "<<-", "&>", ">>", ">|", ">&", "<<", "<>", "<&", ">", "<"}
    FD = re.compile(r"\d+(?=[<>])|\{[A-Za-z_]\w*\}(?=[<>])")

    def __init__(self, text, position=0, depth=0):
        self.s, self.i, self.depth = text, position, depth
        self.pending, self.ahead = [], None

    # -- tokens --------------------------------------------------------------------------------------------------
    def peek(self):
        if self.ahead is None:
            self.ahead = self._lex()
        return self.ahead

    def next(self):
        token = self.peek()
        self.ahead = None
        return token

    def _lex(self):
        s, n = self.s, len(self.s)
        while self.i < n:
            c = s[self.i]
            if c in " \t\r":
                self.i += 1
            elif s.startswith("\\\n", self.i):
                self.i += 2
            elif c == "#":
                end = s.find("\n", self.i)
                self.i = n if end < 0 else end
            else:
                break
        if self.i >= n:
            return ("eof",)
        c = s[self.i]
        if c == "\n":
            self.i += 1
            self._read_heredocs()
            return ("nl",)
        if c in "<>" and s.startswith("(", self.i + 1):
            return ("word", self._read_word())
        if s.startswith("((", self.i):
            self.i = self._match_parens(self.i)
            return ("arith",)
        fd_match = self.FD.match(s, self.i)
        start = fd_match.end() if fd_match else self.i
        for op in self.OPERATORS:
            if s.startswith(op, start):
                if fd_match is None and op not in self.REDIRECTIONS:
                    self.i = start + len(op)
                    return ("op", op)
                if op in self.REDIRECTIONS:
                    self.i = start + len(op)
                    return self._redirection(op, fd_match.group(0) if fd_match else None)
                break
        return ("word", self._read_word())

    def _redirection(self, op, fd):
        while self.i < len(self.s) and self.s[self.i] in " \t":
            self.i += 1
        record = {"op": op, "fd": fd, "target": None, "body": None, "body_quoted": False, "body_dynamic": False,
                  "body_subs": []}
        if self.i < len(self.s) and self.s[self.i] not in "\n;&|()<>":
            record["target"] = self._read_word()
            if op in ("<<", "<<-"):
                record["body_quoted"] = record["target"].quoted
                self.pending.append((record["target"].text, record))
        return ("redir", record)

    def _read_heredocs(self):
        s, n = self.s, len(self.s)
        while self.pending:
            delimiter, record = self.pending.pop(0)
            lines = []
            while self.i < n:
                end = s.find("\n", self.i)
                line = s[self.i:] if end < 0 else s[self.i:end]
                self.i = n if end < 0 else end + 1
                if line.strip() == delimiter:
                    break
                lines.append(line)
            record["body"] = "\n".join(lines)
            if not record["body_quoted"]:
                _, record["body_dynamic"], record["body_subs"] = _Parser(record["body"], 0,
                                                                         self.depth + 1)._read_double(stop=None)

    def _match_parens(self, start):
        """The position after the parenthesis that closes the one at start, skipping quoted text."""
        depth, j, s = 0, start, self.s
        while j < len(s):
            c = s[j]
            if c == "\\":
                j += 2
                continue
            if c in "'\"":
                close = s.find(c, j + 1)
                j = len(s) if close < 0 else close + 1
                continue
            if c == "(":
                depth += 1
            elif c == ")":
                depth -= 1
                if depth == 0:
                    return j + 1
            j += 1
        return len(s)

    # -- words ---------------------------------------------------------------------------------------------------
    def _read_word(self):
        s, n = self.s, len(self.s)
        out, head, dynamic, quoted, subs, in_head = [], [], False, False, [], True
        if s[self.i] in "<>":                          # <(...) or >(...): a process substitution
            prefix = s[self.i]
            text, more = self._substitution(self.i + 1)
            return Word(prefix + "(" + text + ")", True, False, more)
        while self.i < n:
            c = s[self.i]
            if c in " \t\r\n;&|()<>":
                break
            if c == "\\":
                if s.startswith("\\\n", self.i):
                    self.i += 2
                    continue
                if self.i + 1 < n:
                    out.append(s[self.i + 1])
                quoted, in_head = True, False
                self.i += 2
            elif c == "'":
                end = s.find("'", self.i + 1)
                end = n if end < 0 else end
                out.append(s[self.i + 1:end])
                quoted, in_head = True, False
                self.i = end + 1
            elif c == '"':
                self.i += 1
                text, d, more = self._read_double(stop='"')
                out.append(text)
                dynamic, quoted, in_head = dynamic or d, True, False
                subs += more
            elif c == "$" and s.startswith("$'", self.i):
                self.i += 2
                buffer = []
                while self.i < n and s[self.i] != "'":
                    if s[self.i] == "\\" and self.i + 1 < n:
                        buffer.append({"n": "\n", "t": "\t", "r": "\r"}.get(s[self.i + 1], s[self.i + 1]))
                        self.i += 2
                    else:
                        buffer.append(s[self.i])
                        self.i += 1
                self.i += 1
                out.append("".join(buffer))
                quoted, in_head = True, False
            elif c == "$" and s.startswith('$"', self.i):
                self.i += 2
                text, d, more = self._read_double(stop='"')
                out.append(text)
                dynamic, quoted, in_head = dynamic or d, True, False
                subs += more
            elif c == "$":
                text, d, more = self._dollar()
                out.append(text)
                dynamic, subs = dynamic or d, subs + more
                in_head = in_head and not d
            elif c == "`":
                text, more = self._backtick()
                out.append(text)
                dynamic, in_head, subs = True, False, subs + more
            else:
                out.append(c)
                if in_head:
                    head.append(c)
                self.i += 1
        return Word("".join(out), dynamic, quoted, subs, "".join(head))

    def _read_double(self, stop):
        """Read double-quoted text up to stop (None: the end). Returns (text, dynamic, substitutions)."""
        s, n = self.s, len(self.s)
        out, dynamic, subs = [], False, []
        while self.i < n:
            c = s[self.i]
            if stop and c == stop:
                self.i += 1
                break
            if c == "\\" and self.i + 1 < n:
                following = s[self.i + 1]
                if following == "\n":
                    pass
                elif following in '$`"\\':
                    out.append(following)
                else:
                    out.append("\\" + following)
                self.i += 2
            elif c == "$":
                text, d, more = self._dollar()
                out.append(text)
                dynamic, subs = dynamic or d, subs + more
            elif c == "`":
                text, more = self._backtick()
                out.append(text)
                dynamic, subs = True, subs + more
            else:
                out.append(c)
                self.i += 1
        return "".join(out), dynamic, subs

    def _dollar(self):
        s, n, start = self.s, len(self.s), self.i
        if s.startswith("$((", start):
            self.i = self._match_parens(start + 1)
            return s[start:self.i], True, []
        if s.startswith("$(", start):
            text, subs = self._substitution(start + 1)
            return "$(" + text + ")", True, subs
        if s.startswith("${", start):
            j, depth, subs = start + 2, 1, []
            while j < n and depth:
                c = s[j]
                if c == "\\":
                    j += 2
                    continue
                if c == "'":
                    close = s.find("'", j + 1)
                    j = n if close < 0 else close + 1
                    continue
                if s.startswith("$(", j) and not s.startswith("$((", j):
                    saved = self.i
                    _, more = self._substitution(j + 1)
                    subs += more
                    j, self.i = self.i, saved
                    continue
                if s.startswith("${", j):
                    depth, j = depth + 1, j + 2
                    continue
                if c == "}":
                    depth -= 1
                j += 1
            self.i = j
            return s[start:j], True, subs
        match = re.compile(r"[A-Za-z_]\w*|[0-9]|[@*#?$!\-]").match(s, start + 1)
        if match:
            self.i = match.end()
            return s[start:self.i], True, []
        self.i += 1
        return "$", False, []

    def _substitution(self, open_paren):
        """Parse the command list inside the parentheses that open at open_paren. Returns (source, [list])."""
        inner = _Parser(self.s, open_paren + 1, self.depth + 1)
        commands = inner.parse_list(stops={")"})
        if inner.peek() == ("op", ")"):
            inner.next()
            end = inner.i
            self.i = end
            return self.s[open_paren + 1:end - 1], [commands]
        self.i = len(self.s)
        return self.s[open_paren + 1:], [commands]

    def _backtick(self):
        s, n = self.s, len(self.s)
        j, inner = self.i + 1, []
        while j < n and s[j] != "`":
            if s[j] == "\\" and j + 1 < n and s[j + 1] in "`\\$":
                inner.append(s[j + 1])
                j += 2
            else:
                inner.append(s[j])
                j += 1
        source = s[self.i:j + 1]
        self.i = j + 1
        return source, [_Parser("".join(inner), 0, self.depth + 1).parse_list()]

    # -- grammar -------------------------------------------------------------------------------------------------
    def parse_list(self, stops=(), stop_words=()):
        items = []
        while True:
            token = self.peek()
            if token[0] == "eof" or (token[0] == "op" and token[1] in stops):
                break
            if token[0] == "nl":
                self.next()
                continue
            if token[0] == "op" and token[1] not in ("(",):
                self.next()                       # a stray operator: skip it
                continue
            if token[0] == "word" and token[1].literal and token[1].text in stop_words:
                break
            chain = self.parse_and_or(stop_words)
            separator = None
            token = self.peek()
            if token[0] == "op" and token[1] in (";", "&"):
                separator = token[1]
                self.next()
            elif token[0] == "nl":
                separator = "\n"
                self.next()
            items.append((chain, separator))
        return items

    def parse_and_or(self, stop_words=()):
        pipelines, ops = [self.parse_pipeline(stop_words)], []
        while self.peek()[0] == "op" and self.peek()[1] in ("&&", "||"):
            ops.append(self.next()[1])
            self._skip_newlines()
            pipelines.append(self.parse_pipeline(stop_words))
        return pipelines, ops

    def parse_pipeline(self, stop_words=()):
        commands = [self.parse_command(stop_words)]
        while self.peek()[0] == "op" and self.peek()[1] in ("|", "|&"):
            self.next()
            self._skip_newlines()
            commands.append(self.parse_command(stop_words))
        return commands

    def _skip_newlines(self):
        while self.peek()[0] == "nl":
            self.next()

    def _redirections(self):
        records = []
        while self.peek()[0] == "redir":
            records.append(self.next()[1])
        return records

    def parse_command(self, stop_words=()):
        token = self.peek()
        if token == ("op", "("):
            self.next()
            body = self.parse_list(stops={")"})
            if self.peek() == ("op", ")"):
                self.next()
            return ("subshell", body, self._redirections())
        if token[0] == "arith":
            self.next()
            return ("simple", [], self._redirections())
        words, records = [], []
        while True:
            token = self.peek()
            if token[0] == "word":
                word = token[1]
                if not words and word.literal and word.text in stop_words:
                    break
                if not words and word.literal and word.text in SKIPPED_KEYWORDS:
                    self.next()
                    if word.text == "time" and self.peek()[0] == "word" and self.peek()[1].text == "-p":
                        self.next()
                    continue
                if not words and word.literal and word.text == "function":
                    self.next()
                    if self.peek()[0] == "word":
                        self.next()
                    if self.peek() == ("op", "("):
                        self.next()
                        if self.peek() == ("op", ")"):
                            self.next()
                    self._skip_newlines()
                    return self.parse_command(stop_words)
                if not words and word.literal and word.text in ("for", "select"):
                    return ("keyword", self._words_until({"do"}), [])
                if not words and word.literal and word.text == "case":
                    return self._case()
                if not words and word.literal and word.text == "[[":
                    return ("keyword", self._words_until({"]]"}, redirections_are_words=True), [])
                self.next()
                words.append(word)
                if word.assign and word.assign[1] == "" and not word.quoted and self.peek() == ("op", "("):
                    self.next()                                  # NAME=( ... ): an array
                    while self.peek()[0] in ("word", "nl"):
                        token = self.next()
                        if token[0] == "word":
                            word.subs += token[1].subs
                            word.dynamic = word.dynamic or token[1].dynamic
                    if self.peek() == ("op", ")"):
                        self.next()
                elif len(words) == 1 and self.peek() == ("op", "("):
                    self.next()                                  # name() { ...; }: a function definition
                    if self.peek() == ("op", ")"):
                        self.next()
                    self._skip_newlines()
                    return self.parse_command(stop_words)
            elif token[0] == "redir":
                records.append(self.next()[1])
            else:
                break
        return ("simple", words, records)

    def _words_until(self, ends, redirections_are_words=False):
        words = [self.next()[1]]
        while True:
            token = self.peek()
            if token[0] == "word":
                self.next()
                words.append(token[1])
                if token[1].literal and token[1].text in ends:
                    break
            elif token[0] == "redir" and redirections_are_words:
                record = self.next()[1]
                if record["target"] is not None:
                    words.append(record["target"])
            else:
                break
        return words

    def _case(self):
        words = [self.next()[1]]
        while self.peek()[0] == "word":
            word = self.next()[1]
            words.append(word)
            if word.literal and word.text == "in":
                break
        bodies = []
        while True:
            self._skip_newlines()
            token = self.peek()
            if token[0] == "eof":
                break
            if token[0] == "word" and token[1].literal and token[1].text == "esac":
                self.next()
                break
            if token == ("op", "("):
                self.next()
            while True:
                token = self.peek()
                if token[0] == "word":
                    words.append(self.next()[1])
                elif token == ("op", "|"):
                    self.next()
                elif token == ("op", ")"):
                    self.next()
                    break
                else:
                    break
            if self.peek()[0] == "eof":
                break
            bodies.append(self.parse_list(stops={";;", ";&", ";;&"}, stop_words={"esac"}))
            if self.peek()[0] == "op" and self.peek()[1] in (";;", ";&", ";;&"):
                self.next()
        return ("group", bodies, words, self._redirections())


def parse(command):
    """The command list of a command line, as the parser reads it."""
    return _Parser(command or "").parse_list()


# -- folders -----------------------------------------------------------------------------------------------------

def _absolute(path):
    return path.startswith(("/", "~")) or bool(re.match(r"^[A-Za-z]:[\\/]", path))


def _compose(base, path):
    """The folder path names when the shell stands in base. None when base is not known."""
    if _absolute(path):
        return posixpath.normpath(path)
    if base is None:
        return None
    return posixpath.normpath(posixpath.join(base, path)) if path else base


class _Context:
    """What the shell knows at one point of the line: its folder, its exported variables, whether it is a subshell."""

    def __init__(self, cwd=".", cwd_reason=None, env=None, subshell=False, in_sub=False, depth=0,
                 worktree_reason=None, cd_folders=()):
        self.cwd, self.cwd_reason, self.env = cwd, cwd_reason, dict(env or {})
        self.subshell, self.in_sub, self.depth = subshell, in_sub, depth
        self.worktree_reason = worktree_reason
        self.cd_folders = list(cd_folders)      # every cd or pushd folder this shell has seen, as written

    def copy(self, **changes):
        clone = _Context(self.cwd, self.cwd_reason, self.env, self.subshell, self.in_sub, self.depth,
                         self.worktree_reason, self.cd_folders)
        for key, value in changes.items():
            setattr(clone, key, value)
        return clone

    def unknown_folder(self, reason):
        if self.cwd is not None:
            self.cwd, self.cwd_reason = None, reason


# -- options -----------------------------------------------------------------------------------------------------

def _expand_long(name, known):
    """The long option a possibly abbreviated name stands for, as git's option parser reads it: the name itself
    when nothing matches, None when the abbreviation is ambiguous."""
    if name in known:
        return name
    matches = [option for option in known if option.startswith(name)]
    return matches[0] if len(matches) == 1 else (name if not matches else None)


def _scan(words, short_values="", long_values=(), long_flags=(), long_optional=()):
    """Split arguments into options and operands.

    Returns (opts, operands): opts is [(name, value)] where value is None or (text, dynamic, index); operands is
    [(index, word)]. When long_flags is given, the option list is complete and a long option may be abbreviated,
    as git's option parser allows; an ambiguous one is named with a trailing "?"."""
    known = tuple(long_values) + tuple(long_flags) + tuple(long_optional)
    abbreviations = bool(long_flags)
    opts, operands, i, n = [], [], 0, len(words)
    while i < n:
        word, text = words[i], words[i].text
        if text == "--":
            operands += [(j, words[j]) for j in range(i + 1, n)]
            break
        if not text.startswith("-") or text == "-":
            operands.append((i, word))
            i += 1
            continue
        if text.startswith("--"):
            name, equals, value = text[2:].partition("=")
            full = _expand_long(name, known) if abbreviations else name
            if full is None:
                opts.append(("--" + name + "?", (value, word.dynamic, i) if equals else None))
            elif full in long_values and not equals and i + 1 < n:
                opts.append(("--" + full, (words[i + 1].text, words[i + 1].dynamic, i + 1)))
                i += 1
            else:
                opts.append(("--" + full, (value, word.dynamic, i) if equals else None))
            i += 1
            continue
        j = 1
        while j < len(text):
            flag = text[j]
            if flag in short_values:
                if j + 1 < len(text):
                    opts.append(("-" + flag, (text[j + 1:], word.dynamic, i)))
                elif i + 1 < n:
                    opts.append(("-" + flag, (words[i + 1].text, words[i + 1].dynamic, i + 1)))
                    i += 1
                else:
                    opts.append(("-" + flag, None))
                break
            opts.append(("-" + flag, None))
            j += 1
        i += 1
    return opts, operands


def _names(opts):
    return [name for name, _ in opts]


def _truthy(value):
    if value is None:
        return True
    return value.strip().lower() in ("true", "yes", "on", "1") or (value.strip().isdigit() and int(value) != 0)


def _config_key(key):
    """A config key as git compares it: section and variable in lower case, the subsection as written."""
    parts = key.split(".")
    if len(parts) < 2:
        return key.lower()
    return ".".join([parts[0].lower()] + parts[1:-1] + [parts[-1].lower()])


def guarded_key(key):
    """True for a config key whose write the guards refuse: it changes where a push goes, what a command runs or
    which folder git works on. A key that cannot be known counts."""
    if key is None:
        return True
    parts = _config_key(key).split(".")
    section, variable = parts[0], parts[-1] if len(parts) > 1 else ""
    if section in ("remote", "url", "push", "include", "includeif", "alias"):
        return True
    if section == "branch" and variable in ("pushremote", "merge"):
        return True
    return section == "core" and variable in ("worktree", "sshcommand")


# Keys only a persistent `git config` write is refused for, beyond guarded_key's: core.hooksPath points git at
# another hooks folder, which turns off every commit and push check (M3 slice C5d, the maintainer's answer to Q16),
# and submodule.recurse makes every later push send each submodule to its own remote, which the outward-write guard
# does not work out (M3 slice C5e). A -c value lasts one call, as --no-verify does, so a -c write of one is not
# guarded; the guard it concerns judges it.
PERSISTENT_GUARDED = {"core.hookspath", "submodule.recurse"}


def guarded_persistent_key(key):
    """True for a key whose persistent `git config` write the guards refuse: guarded_key's, and PERSISTENT_GUARDED.
    A key that cannot be known counts."""
    if key is None:
        return True
    return guarded_key(key) or (len(key.split(".")) == 2 and key.lower() in PERSISTENT_GUARDED)


def guarded_section(name):
    """True when a config section of that name holds a key a persistent write may not set, or may: removing it
    unsets those keys, and renaming another section to it sets them. `core` holds core.hooksPath. A name that
    cannot be known counts."""
    if name is None:
        return True
    return guarded_key(name + ".x") or guarded_key(name) or name.lower() in {
        key.split(".")[0] for key in PERSISTENT_GUARDED}


def _env_config(env):
    """[(key or None, value, via)] that GIT_CONFIG_COUNT/KEY_n/VALUE_n or GIT_CONFIG_PARAMETERS set."""
    found = []
    count = env.get("GIT_CONFIG_COUNT")
    if count is not None:
        text, dynamic = count
        if dynamic or not text.strip().isdigit():
            found.append((None, None, "GIT_CONFIG_COUNT"))
        else:
            for k in range(int(text)):
                key, value = env.get(f"GIT_CONFIG_KEY_{k}"), env.get(f"GIT_CONFIG_VALUE_{k}")
                if key is None or key[1]:
                    found.append((None, value[0] if value else None, "GIT_CONFIG_COUNT"))
                else:
                    found.append((key[0], value[0] if value else None, "GIT_CONFIG_COUNT"))
    parameters = env.get("GIT_CONFIG_PARAMETERS")
    if parameters is not None:
        text, dynamic = parameters
        try:
            pieces = [] if dynamic else shlex.split(text)
        except ValueError:
            pieces, dynamic = [], True
        if dynamic:
            found.append((None, None, "GIT_CONFIG_PARAMETERS"))
        for piece in pieces:
            key, _, value = piece.partition("=")
            found.append((key, value, "GIT_CONFIG_PARAMETERS"))
    return found


# -- git ---------------------------------------------------------------------------------------------------------

GIT_GLOBAL_VALUES = {"-C", "-c", "--git-dir", "--work-tree", "--namespace", "--config-env", "--attr-source",
                     "--super-prefix", "--list-cmds"}
GIT_ENV_CHANGING = {"-C", "-c", "--git-dir", "--work-tree", "--namespace", "--config-env", "--bare",
                    "--exec-path", "--super-prefix"}
PUSH_FLAGS = ("all", "branches", "mirror", "tags", "follow-tags", "no-follow-tags", "delete", "prune", "dry-run",
              "no-force", "no-mirror", "no-all", "no-tags", "no-dry-run", "no-set-upstream", "no-prune",
              "porcelain", "force", "set-upstream", "no-verify", "verify", "quiet", "verbose", "atomic",
              "no-atomic", "thin", "no-thin", "progress", "no-progress", "force-if-includes",
              "no-force-if-includes", "no-force-with-lease", "ipv4", "ipv6", "no-signed", "no-recurse-submodules",
              "no-push-option")
SUBCOMMAND_SHORT_VALUES = {
    "push": "o", "commit": "mFCct", "tag": "mFu", "merge": "mFsX", "switch": "cC", "checkout": "bB",
    "rebase": "xsX", "pull": "sX", "stash": "m", "branch": "u", "notes": "mFcC", "clean": "e", "worktree": "b",
    "remote": "tm", "config": "f", "cherry-pick": "mX", "commit-tree": "mFp", "restore": "s",
}
SUBCOMMAND_LONG_VALUES = {
    "push": ("repo", "receive-pack", "exec", "push-option", "recurse-submodules"),
    "commit": ("message", "file", "reuse-message", "reedit-message", "template", "author", "date", "cleanup",
               "fixup", "squash", "trailer", "pathspec-from-file"),
    "tag": ("message", "file", "local-user", "cleanup", "sort", "format", "contains", "no-contains", "merged",
            "no-merged", "points-at"),
    "merge": ("message", "file", "strategy", "strategy-option", "into-name", "cleanup"),
    "rebase": ("exec", "strategy", "strategy-option", "onto", "rebase-merges", "whitespace", "empty"),
    "pull": ("strategy", "strategy-option", "depth", "deepen", "shallow-since", "shallow-exclude", "upload-pack"),
    "stash": ("message", "pathspec-from-file"),
    "switch": ("create", "force-create", "orphan", "conflict"),
    "checkout": ("orphan", "conflict", "pathspec-from-file"),
    "restore": ("source", "conflict", "pathspec-from-file"),
    "branch": ("set-upstream-to", "format", "sort", "contains", "no-contains", "merged", "no-merged", "points-at"),
    "worktree": ("reason",),
    "config": ("file", "blob", "type", "default", "comment", "value", "url"),
    "notes": ("message", "file", "reuse-message", "reedit-message", "ref"),
}


# A pathspec that names the whole tree: a checkout or restore of it overwrites every changed file.
WHOLE_TREE = {".", "./", ":/", ":/.", ":/*", ":(top)", ":(top).", "*", "**"}
# The stash actions that write a stash entry, and so take the working tree's changes away: a plain `git stash` is
# a push.
STASH_WRITES = {"push", "save", "store"}


def _whole_tree(text):
    """True for a pathspec of the whole tree: one in WHOLE_TREE, or a path of only "." and ".." segments."""
    if text in WHOLE_TREE:
        return True
    parts = [part for part in text.split("/") if part]
    return bool(parts) and all(part in (".", "..") for part in parts)


def _git(args, env, cwd, cwd_reason, ctx, aliases):
    """The git facts of one call. Returns (facts, config writes, file writes, nested [(text, cwd_reason, via)],
    message indexes)."""
    facts = {"subcommand": None, "args": [], "builtin": False, "alias": None, "unresolved": None, "globals": [],
             "config": [], "folder": None, "folder_unresolved": None, "cwd": cwd, "git_dir": None,
             "work_tree": None, "action": None, "discard": [], "pull_rebase": False, "tracking": False,
             "remote": None, "push": None}
    config_writes, file_writes, nested, messages = [], [], [], []
    folder, folder_reason = cwd, cwd_reason
    git_dir = work_tree = None
    prefix, prefix_dynamic = "", False         # the -C folders as written, for the paths a git call writes
    i = 0
    while i < len(args):
        text = args[i].text
        if not text.startswith("-") or text == "-":
            break
        name, equals, value = text.partition("=")
        if name in GIT_GLOBAL_VALUES and not equals and name not in ("--super-prefix", "--list-cmds"):
            if i + 1 >= len(args):
                facts["globals"].append(text)
                i += 1
                break
            value_word = args[i + 1]
            facts["globals"] += [text, value_word.text]
            value, dynamic = value_word.text, value_word.dynamic
            i += 2
        else:
            facts["globals"].append(text)
            dynamic = args[i].dynamic
            i += 1
            if not equals:
                if name == "--bare":
                    git_dir = folder
                continue
        if name == "-C":
            if dynamic:
                prefix_dynamic = True
            elif value:
                prefix = value if _absolute(value) or not prefix else posixpath.join(prefix, value)
            if dynamic:
                folder, folder_reason = None, "-C names a variable or substitution"
            elif value and folder is not None:
                folder = _compose(folder, value)
            elif value and _absolute(value):
                folder, folder_reason = _compose(None, value), None
        elif name == "-c":
            key, has_value, config_value = value.partition("=")
            facts["config"].append({"key": None if dynamic and "$" in key else key,
                                    "value": config_value if has_value else None, "dynamic": dynamic, "via": "-c"})
        elif name == "--config-env":
            key, _, variable = value.partition("=")
            facts["config"].append({"key": key, "value": "$" + variable, "dynamic": True, "via": "--config-env"})
        elif name == "--git-dir":
            git_dir = ("$", value) if dynamic else value
        elif name == "--work-tree":
            work_tree = ("$", value) if dynamic else value
    for key, value, via in _env_config(env):
        facts["config"].append({"key": key, "value": value, "dynamic": key is None, "via": via})
    for entry in facts["config"]:
        if entry["via"] != "-c" and entry["via"] != "--config-env":
            continue
        config_writes.append({"key": entry["key"], "value": entry["value"], "op": "set", "via": "git " + entry["via"],
                              "guarded": guarded_key(entry["key"]) or (entry["key"] is None)})

    # The environment's say on the repository, then the options', which win.
    if git_dir is None and "GIT_DIR" in env and env["GIT_DIR"] is not None:
        git_dir = ("$", env["GIT_DIR"][0]) if env["GIT_DIR"][1] else env["GIT_DIR"][0]
    if work_tree is None and "GIT_WORK_TREE" in env and env["GIT_WORK_TREE"] is not None:
        work_tree = ("$", env["GIT_WORK_TREE"][0]) if env["GIT_WORK_TREE"][1] else env["GIT_WORK_TREE"][0]

    def place(path, what):
        nonlocal folder_reason
        if path is None:
            return None
        if isinstance(path, tuple):
            folder_reason = folder_reason or f"{what} names a variable or substitution"
            return path[1]
        placed = _compose(folder, path)
        if placed is None:
            folder_reason = folder_reason or cwd_reason
        return placed

    facts["cwd"] = folder
    facts["git_dir"], facts["work_tree"] = place(git_dir, "--git-dir or GIT_DIR"), place(work_tree,
                                                                                         "--work-tree or GIT_WORK_TREE")
    if isinstance(git_dir, tuple) or isinstance(work_tree, tuple):
        target = None
    else:
        target = facts["git_dir"] or facts["work_tree"] or folder
    breakers = [name for name in FOLDER_BREAKERS if name in env and env[name] is not None]
    if any(e["key"] and _config_key(e["key"]) == "core.worktree" for e in facts["config"]):
        target, folder_reason = None, "core.worktree is set on the command"
    elif breakers:
        target, folder_reason = None, f"{breakers[0]} is set"
    elif ctx.worktree_reason:
        target, folder_reason = None, ctx.worktree_reason
    if target is None and folder_reason is None:
        folder_reason = cwd_reason or "the folder cannot be known"
    facts["folder"], facts["folder_unresolved"] = target, (None if target is not None else folder_reason)

    if i >= len(args):
        return facts, config_writes, file_writes, nested, messages
    sub_word, rest, offset = args[i], list(args[i + 1:]), i + 1
    expansion_length = 0
    if sub_word.dynamic:
        facts["subcommand"], facts["args"] = sub_word.text, [w.text for w in rest]
        facts["unresolved"] = "the git subcommand is a variable or substitution"
        return facts, config_writes, file_writes, nested, messages
    subcommand, seen = sub_word.text, set()
    while subcommand not in GIT_BUILTINS:
        alias_value, source = None, None
        for entry in facts["config"]:
            if entry["key"] and _config_key(entry["key"]) == "alias." + subcommand.lower():
                alias_value, source = (entry["value"] or "", entry["dynamic"]), "-c"
        if alias_value is None and aliases is not None:
            for name, value in aliases.items():
                if name.lower() == subcommand.lower():
                    alias_value, source = (value, False), "config"
        if alias_value is None:
            if aliases is not None:
                facts["unresolved"] = f"git {subcommand} is neither a built-in command nor an alias"
            break
        if subcommand in seen or len(seen) > 16:
            facts["unresolved"] = f"the alias {subcommand} expands to itself"
            break
        seen.add(subcommand)
        value, dynamic = alias_value
        facts["alias"] = facts["alias"] or {"name": subcommand, "expansion": value, "source": source}
        if dynamic:
            facts["unresolved"] = f"the alias {subcommand} is a variable or substitution"
            break
        if value.startswith("!"):
            facts["unresolved"] = f"the alias {subcommand} runs a shell command"
            break
        try:
            expanded = shlex.split(value)
        except ValueError:
            facts["unresolved"] = f"the alias {subcommand} cannot be read"
            break
        while expanded and expanded[0].startswith("-"):
            if expanded[0].split("=")[0] in GIT_ENV_CHANGING:
                facts["unresolved"] = f"the alias {subcommand} changes git's environment"
                break
            expanded = expanded[1:]
        if facts["unresolved"] or not expanded:
            facts["unresolved"] = facts["unresolved"] or f"the alias {subcommand} is empty"
            break
        subcommand = expanded[0]
        rest = [_literal(w) for w in expanded[1:]] + rest
        expansion_length += len(expanded) - 1
    facts["subcommand"], facts["builtin"] = subcommand, subcommand in GIT_BUILTINS
    facts["args"] = [w.text for w in rest]
    if facts["unresolved"]:
        return facts, config_writes, file_writes, nested, messages

    def original(index):
        """The index in the command's args of the word at index in rest; None for words an alias supplied."""
        return None if index < expansion_length else offset + index - expansion_length

    def config(key):
        value = None
        for entry in facts["config"]:
            if entry["key"] and _config_key(entry["key"]) == key:
                value = entry["value"]
        return value

    opts, operands = _scan(rest, SUBCOMMAND_SHORT_VALUES.get(subcommand, ""),
                           SUBCOMMAND_LONG_VALUES.get(subcommand, ()),
                           PUSH_FLAGS if subcommand == "push" else (),
                           ("force-with-lease", "signed") if subcommand == "push" else ())
    names = _names(opts)
    message_options = GIT_MESSAGE_OPTIONS.get(subcommand, ())
    for name, value in opts:
        if name in message_options and value is not None and original(value[2]) is not None:
            messages.append(original(value[2]))
    first = operands[0][1].text if operands else None

    if subcommand in ("stash", "worktree", "remote", "submodule", "notes", "reflog", "bisect", "sparse-checkout",
                      "maintenance", "bundle", "commit-graph", "multi-pack-index", "hook", "refs", "repo"):
        facts["action"] = first or ("push" if subcommand == "stash" else None)
    if subcommand == "config" and first in ("set", "unset", "get", "list", "edit", "rename-section",
                                            "remove-section"):
        facts["action"] = first

    discard = facts["discard"]
    if subcommand == "switch" and ({"-f", "--force", "--discard-changes"} & set(names)):
        discard.append("switch --force")
    if subcommand == "checkout" and ({"-f", "--force"} & set(names)):
        discard.append("checkout --force")
    if subcommand == "read-tree" and "--reset" in names and "-u" in names:
        discard.append("read-tree --reset -u")
    if subcommand == "reset":
        for mode in ("hard", "keep", "merge"):
            if "--" + mode in names:
                discard.append("reset --" + mode)
    if subcommand == "clean" and ({"-f", "--force"} & set(names)):
        discard.append("clean --force")
    if subcommand == "stash" and facts["action"] in ("drop", "pop", "clear"):
        discard.append("stash " + facts["action"])
    if subcommand == "worktree" and facts["action"] == "remove":
        discard.append("worktree remove --force" if {"-f", "--force"} & set(names) else "worktree remove")
    if subcommand == "worktree" and facts["action"] == "prune":
        discard.append("worktree prune")
    if subcommand in ("checkout", "restore"):
        whole = any(_whole_tree(word.text) for _, word in operands) or any(
            name.startswith("--pathspec-from") for name in names)
        staged_only = {"-S", "--staged"} & set(names) and not {"-W", "--worktree"} & set(names)
        if whole and not (subcommand == "restore" and staged_only):
            discard.append("whole-tree " + subcommand)
    if subcommand == "stash" and facts["action"] in STASH_WRITES:
        discard.append("stash write")
    if subcommand in ("rebase", "cherry-pick"):
        discard.append(subcommand)
    if subcommand == "pull":
        rebase = None
        if config("pull.rebase") is not None:
            rebase = config("pull.rebase").lower() not in ("false", "no", "off", "0")
        for name, value in opts:
            if name in ("-r", "--rebase"):
                rebase = value is None or value[0].lower() not in ("false", "no", "off", "0")
            elif name == "--no-rebase":
                rebase = False
        facts["pull_rebase"] = bool(rebase)
    if subcommand in ("rebase", "pull", "merge"):
        autostash = None
        key = "rebase.autostash" if subcommand == "rebase" or facts["pull_rebase"] else "merge.autostash"
        if config(key) is not None:
            autostash = _truthy(config(key))
        for name in names:
            if name == "--autostash":
                autostash = True
            elif name == "--no-autostash":
                autostash = False
        if autostash:
            discard.append("autostash")
    if subcommand in ("switch", "checkout", "branch") and (
            {"-t", "--track", "-u", "--set-upstream-to", "--set-upstream"} & set(names)):
        facts["tracking"] = True

    if subcommand in ("mv", "rm", "checkout", "restore"):
        # Each operand may be a path git rewrites or removes. A checkout's first operand may be a branch instead;
        # it is reported too, since the words alone cannot tell them apart.
        for _, word in operands:
            path = word.text if not prefix or _absolute(word.text) else posixpath.join(prefix, word.text)
            file_writes.append({"path": path, "dynamic": word.dynamic or prefix_dynamic, "via": "git " + subcommand})

    if subcommand == "rebase":
        for name, value in opts:
            if name in ("-x", "--exec") and value is not None:
                nested.append((value[0], value[1], "the top of the working tree", "git rebase --exec"))
    if subcommand == "submodule" and facts["action"] == "foreach" and len(operands) > 1:
        script = " ".join(word.text for _, word in operands[1:])
        nested.append((script, any(word.dynamic for _, word in operands[1:]), "each submodule's folder",
                       "git submodule foreach"))
    if subcommand == "bisect" and facts["action"] == "run" and len(operands) > 1:
        nested.append((" ".join(shlex.quote(word.text) for _, word in operands[1:]),
                       any(word.dynamic for _, word in operands[1:]), None, "git bisect run"))

    if subcommand == "config":
        config_writes += _git_config(opts, operands, facts["action"], file_writes)
        if any(w["key"] and _config_key(w["key"]).startswith("core.worktree") for w in config_writes
               if w["via"] == "git config"):
            ctx.worktree_reason = "core.worktree was set earlier in the line"
    if subcommand == "remote" and facts["action"]:
        facts["remote"] = _git_remote(facts["action"], opts, operands)
    if subcommand == "push":
        facts["push"] = _git_push(opts, operands)
        facts["tracking"] = facts["push"]["set_upstream"]
    return facts, config_writes, file_writes, nested, messages


def _git_config(opts, operands, action, file_writes):
    names = _names(opts)
    values = [(word.text, word.dynamic) for _, word in operands]
    if action:
        values = values[1:]
    scope = None
    for name, value in opts:
        if name in ("--global", "--system", "--local", "--worktree"):
            scope = name
        elif name in ("-f", "--file") and value is not None:
            scope = "--file " + value[0]
            file_writes.append({"path": value[0], "dynamic": value[1], "via": "git config --file"})
        elif name == "--blob" and value is not None:
            scope = "--blob " + value[0]
    op = None
    if action in ("set", "unset", "rename-section", "remove-section", "edit"):
        op = action
    elif {"--unset", "--unset-all"} & set(names):
        op = "unset"
    elif {"--rename-section", "--remove-section"} & set(names):
        op = "rename-section" if "--rename-section" in names else "remove-section"
    elif {"--add", "--replace-all"} & set(names):
        op = "set"
    elif {"-e", "--edit"} & set(names):
        op = "edit"
    elif action is None and not ({"--get", "--get-all", "--get-regexp", "--get-urlmatch", "--get-color",
                                  "--get-colorbool", "-l", "--list"} & set(names)) and len(values) >= 2:
        op = "set"
    if op is None:
        if scope and scope.startswith("--file") and file_writes:
            file_writes.pop()                 # a read of that file writes nothing
        return []
    if op == "edit" or not values:
        return [{"key": None, "value": None, "op": op, "via": "git config", "guarded": True, "scope": scope}]
    key, dynamic = values[0]
    value = values[1][0] if len(values) > 1 and op == "set" else None
    write = {"key": None if dynamic else key, "value": value, "op": op, "via": "git config", "scope": scope}
    if op == "rename-section":
        new = values[1] if len(values) > 1 else None
        write["new_key"] = None if new is None or new[1] else new[0]
        write["guarded"] = dynamic or guarded_section(key) or guarded_section(write["new_key"])
    elif op == "remove-section":
        write["guarded"] = dynamic or guarded_section(key)
    else:
        write["guarded"] = dynamic or guarded_persistent_key(key)
    return [write]


def _git_remote(action, opts, operands):
    words = [word for _, word in operands][1:]
    remote = {"action": action, "name": words[0].text if words else None, "url": None,
              "push": "--push" in _names(opts), "dynamic": any(word.dynamic for word in words[:2])}
    if action in ("add", "set-url") and len(words) > 1:
        remote["url"] = words[1].text
    return remote


def _git_push(opts, operands):
    push = {"remote": None, "remote_dynamic": False, "refspecs": [], "force": False, "force_with_lease": [],
            "force_if_includes": False, "mirror": False, "all": False, "branches": False, "delete": False,
            "prune": False, "tags": False, "follow_tags": False, "set_upstream": False, "dry_run": False,
            "unknown_options": []}
    known = set(PUSH_FLAGS) | set(SUBCOMMAND_LONG_VALUES["push"]) | {"force-with-lease", "signed"}
    for name, value in opts:
        field = name[5:].replace("-", "_") if name.startswith("--no-") else None
        if name.endswith("?") or (name.startswith("--") and name[2:] not in known):
            push["unknown_options"].append(name.rstrip("?"))
        if field in ("force", "mirror", "all", "branches", "delete", "prune", "tags", "follow_tags",
                     "set_upstream", "dry_run", "force_if_includes"):
            push[field] = False
        elif name in ("-f", "--force"):
            push["force"] = True
        elif name == "--force-with-lease":
            push["force_with_lease"].append(value[0] if value else "")
        elif name == "--no-force-with-lease":
            push["force_with_lease"] = []
        elif name == "--force-if-includes":
            push["force_if_includes"] = True
        elif name in ("-d", "--delete"):
            push["delete"] = True
        elif name in ("-u", "--set-upstream"):
            push["set_upstream"] = True
        elif name in ("-n", "--dry-run"):
            push["dry_run"] = True
        elif name == "--repo" and value is not None and push["remote"] is None:
            push["remote"], push["remote_dynamic"] = value[0], value[1]
        elif name.lstrip("-").replace("-", "_") in ("mirror", "all", "branches", "prune", "tags", "follow_tags"):
            push[name.lstrip("-").replace("-", "_")] = True
    words = [word for _, word in operands]
    if words:
        push["remote"], push["remote_dynamic"] = words[0].text, words[0].dynamic
        words = words[1:]
    k = 0
    while k < len(words):
        word = words[k]
        text, dynamic = word.text, word.dynamic
        if text == "tag" and k + 1 < len(words):
            k += 1
            text, dynamic = "refs/tags/" + words[k].text, words[k].dynamic
        force = text.startswith("+")
        body = text[1:] if force else text
        src, colon, dst = body.partition(":")
        push["refspecs"].append({"text": text, "src": src, "dst": dst if colon else None, "force": force,
                                 "delete": bool(colon) and src == "", "glob": "*" in body, "dynamic": dynamic})
        k += 1
    return push


# -- gh ----------------------------------------------------------------------------------------------------------

def _gh_repository(text, dynamic, source):
    """A gh repository argument: [HOST/]OWNER/REPO or a URL."""
    repo = {"text": text, "host": None, "owner": None, "name": None, "dynamic": dynamic, "source": source}
    if dynamic:
        return repo
    match = re.match(r"^(?:https?://|git@|ssh://(?:git@)?)([^/:]+)[/:]([^/]+)/([^/]+?)(?:\.git)?/?$", text)
    if match:
        repo["host"], repo["owner"], repo["name"] = match.groups()
        return repo
    parts = text.split("/")
    if len(parts) == 2:
        repo["owner"], repo["name"] = parts
    elif len(parts) == 3:
        repo["host"], repo["owner"], repo["name"] = parts
    return repo


def _gh_url(text):
    match = re.match(r"^https?://([^/]+)/([^/]+)/([^/?#]+)", text)
    if not match or match.group(1).startswith("api."):
        return None
    return {"host": match.group(1), "owner": match.group(2), "name": match.group(3).removesuffix(".git")}


def _gh_api(words):
    api = {"endpoint": None, "path": None, "dynamic": False, "graphql": False, "method": None,
           "effective_method": "GET", "fields": [], "input": None, "headers": [], "owner": None, "repo": None,
           "placeholders": [], "host": None}
    i = 0
    while i < len(words):
        word, text = words[i], words[i].text
        name, equals, attached = text.partition("=")
        if text.startswith("-") and len(text) > 2 and not text.startswith("--") and text[:2] in GH_API_VALUES:
            name, value, dynamic, i = text[:2], text[2:], word.dynamic, i + 1
        elif name in GH_API_VALUES and text.startswith("--") and equals:
            value, dynamic, i = attached, word.dynamic, i + 1
        elif text in GH_API_VALUES:
            if i + 1 < len(words):
                value, dynamic = words[i + 1].text, words[i + 1].dynamic
            else:
                value, dynamic = None, False
            name, i = text, i + 2
        else:
            if not text.startswith("-") and api["endpoint"] is None:
                api["endpoint"], api["dynamic"] = text, word.dynamic
            i += 1
            continue
        if value is None:
            continue
        if name in ("-X", "--method"):
            api["method"] = value.upper()
        elif name in ("-f", "--raw-field", "-F", "--field"):
            key, _, field_value = value.partition("=")
            raw = name in ("-f", "--raw-field")
            api["fields"].append({"flag": name, "key": key, "value": field_value, "raw": raw, "dynamic": dynamic,
                                  "file": field_value[1:] if not raw and field_value.startswith("@") else None})
        elif name == "--input":
            api["input"] = value
        elif name in ("-H", "--header"):
            api["headers"].append(value)
        elif name == "--hostname":
            api["host"] = value
    api["effective_method"] = api["method"] or ("POST" if api["fields"] or api["input"] else "GET")
    endpoint = api["endpoint"]
    if endpoint is None:
        return api
    path = endpoint
    match = re.match(r"^https?://([^/?#]+)(.*)$", endpoint)
    if match:
        host, path = match.group(1), match.group(2) or "/"
        if host == "api.github.com":
            host = "github.com"
        else:
            path = re.sub(r"^/api(/v3)?(?=/|$)", "", path)
        api["host"] = api["host"] or host
    path = re.split(r"[?#]", path, 1)[0].strip("/")
    api["path"] = path
    api["graphql"] = path == "graphql"
    match = re.match(r"^repos/([^/]+)/([^/]+)", path)
    if match:
        api["owner"], api["repo"] = match.groups()
        api["placeholders"] = [p for p in ("owner", "repo") if api[p] == "{" + p + "}"]
    api["placeholders"] += [p for p in re.findall(r"\{(\w+)\}", path) if p not in api["placeholders"]]
    return api


def _gh(args, env, hosts):
    facts = {"path": [], "args": [], "repo": None, "repo_argument": None, "target_urls": [], "host": None,
             "unresolved": None, "api": None}
    messages, path_end, i = [], None, 0
    words = list(args)
    for k, word in enumerate(words):
        text = word.text
        if text == "--":
            break
        value_word, source = None, None
        if text in ("-R", "--repo") and k + 1 < len(words):
            value_word, source = words[k + 1], text
        elif text.startswith("--repo="):
            value_word, source = Word(text[7:], word.dynamic), "--repo"
        elif text.startswith("-R") and len(text) > 2:
            value_word, source = Word(text[2:], word.dynamic), "-R"
        if value_word is not None:
            facts["repo"] = _gh_repository(value_word.text, value_word.dynamic, source)
    if facts["repo"] is None and env.get("GH_REPO") is not None:
        facts["repo"] = _gh_repository(env["GH_REPO"][0], env["GH_REPO"][1], "GH_REPO")
    # The subcommand path: the first operands, past the options that take a value.
    while i < len(words):
        text = words[i].text
        if text in ("-R", "--repo", "--hostname"):
            i += 2
            continue
        if text.startswith("-"):
            i += 1
            continue
        if words[i].dynamic:
            facts["unresolved"] = "the gh subcommand is a variable or substitution"
        facts["path"].append(text)
        i += 1
        depth = len(facts["path"])
        if depth == 1 and text not in GH_GROUPS:
            break
        if depth == 2 and tuple(facts["path"]) not in GH_THIRD_LEVEL:
            break
        if depth == 3:
            break
    path_end = i
    rest = words[path_end:]
    facts["args"] = [w.text for w in rest]
    path = tuple(facts["path"][:2])
    if path and path[0] == "api":
        facts["api"] = _gh_api(rest)
    elif path in GH_MESSAGE_PATHS:
        for k, word in enumerate(rest):
            name, equals, _ = word.text.partition("=")
            if name in GH_MESSAGE_OPTIONS:
                if equals:
                    messages.append(path_end + k)
                elif k + 1 < len(rest):
                    messages.append(path_end + k + 1)
            elif len(word.text) > 2 and word.text[:2] in ("-b", "-t", "-F", "-n", "-c") and \
                    not word.text.startswith("--"):
                messages.append(path_end + k)
    operands = [w for k, w in enumerate(rest) if not w.text.startswith("-")
                and (path_end + k) not in messages and not (k and rest[k - 1].text in ("-R", "--repo"))]
    if path[:1] == ("repo",) and len(path) > 1 and path[1] in GH_REPO_OPERAND and operands:
        facts["repo_argument"] = _gh_repository(operands[0].text, operands[0].dynamic, "operand")
    for word in operands:
        url = None if word.dynamic else _gh_url(word.text)
        if url:
            facts["target_urls"].append(url)
    # The host: --hostname, then the repository's, then an api URL's, then GH_HOST.
    host = None
    for k, word in enumerate(words):
        if word.text == "--hostname" and k + 1 < len(words):
            host = (words[k + 1].text, words[k + 1].dynamic)
        elif word.text.startswith("--hostname="):
            host = (word.text.split("=", 1)[1], word.dynamic)
    if host is None and facts["repo"] and facts["repo"]["host"]:
        host = (facts["repo"]["host"], False)
    if host is None and facts["api"] and facts["api"]["host"]:
        host = (facts["api"]["host"], facts["api"]["dynamic"])
    if host is None and env.get("GH_HOST") is not None:
        host = env["GH_HOST"]
    if host is not None:
        facts["host"] = host[0]
        if host[1]:
            facts["unresolved"] = facts["unresolved"] or "the gh host is a variable or substitution"
        elif host[0].lower() not in {h.lower() for h in hosts}:
            facts["unresolved"] = facts["unresolved"] or f"the host {host[0]} is not a known host"
    if facts["repo"] and facts["repo"]["dynamic"] is False and facts["repo"]["host"] and \
            facts["repo"]["host"].lower() not in {h.lower() for h in hosts}:
        facts["unresolved"] = facts["unresolved"] or f"the host {facts['repo']['host']} is not a known host"
    return facts, messages


# -- writes ------------------------------------------------------------------------------------------------------

WRITE_OPTIONS = {   # program: (short options that take a value, long ones that do)
    "cp": ("tS", ("target-directory", "suffix")), "mv": ("tS", ("target-directory", "suffix")),
    "rm": ("", ()), "ln": ("tS", ("target-directory", "suffix")), "truncate": ("sr", ("size", "reference")),
    "install": ("mogtSC", ("mode", "owner", "group", "target-directory", "suffix")),
    "rsync": ("eTBfM", ("rsh", "filter", "exclude", "include", "exclude-from", "include-from", "files-from",
                        "temp-dir", "block-size", "port", "password-file", "log-file", "partial-dir", "backup-dir",
                        "compare-dest", "copy-dest", "link-dest", "chmod", "chown", "timeout", "max-size",
                        "min-size", "remote-option", "suffix", "out-format", "info", "debug", "usermap",
                        "groupmap", "rsync-path")),
    "tee": ("", ()), "touch": ("rdt", ("reference", "date")),
    "unlink": ("", ()), "rmdir": ("", ()), "shred": ("ns", ("iterations", "size", "random-source")),
}


def _program_writes(program, args):
    writes = []

    def add(word, via):
        writes.append({"path": word.text, "dynamic": word.dynamic, "via": via})

    if program == "dd":
        for word in args:
            if word.text.startswith("of="):
                writes.append({"path": word.text[3:], "dynamic": word.dynamic, "via": "dd of="})
        return writes
    if program == "sed":
        return _sed_writes(args)
    if program not in WRITE_OPTIONS:
        return writes
    short_values, long_values = WRITE_OPTIONS[program]
    opts, operands = _scan(args, short_values, long_values)
    words = [word for _, word in operands]
    target = next((value for name, value in opts if name in ("-t", "--target-directory") and value), None)
    if program in ("rm", "tee", "truncate", "touch", "unlink", "rmdir", "shred"):
        for word in words:
            add(word, program)
    elif program in ("cp", "mv", "install", "rsync"):
        if program == "install" and ("-d" in _names(opts) or "--directory" in _names(opts)):
            for word in words:
                add(word, "install -d")
            return writes
        sources = words if target else words[:-1]
        if target:
            writes.append({"path": target[0], "dynamic": target[1], "via": program})
        elif len(words) >= 2:
            add(words[-1], program)
        if program == "mv" or (program == "rsync" and "--remove-source-files" in _names(opts)):
            for word in sources:
                add(word, program + " source")
    elif program == "ln":
        if target:
            for word in words:
                writes.append({"path": posixpath.join(target[0], posixpath.basename(word.text)),
                               "dynamic": target[1] or word.dynamic, "via": "ln"})
        elif len(words) == 1:
            writes.append({"path": posixpath.basename(words[0].text.rstrip("/")), "dynamic": words[0].dynamic,
                           "via": "ln"})
        elif words:
            add(words[-1], "ln")
    return writes


def _sed_writes(args):
    in_place, script_given, operands, i = False, False, [], 0
    while i < len(args):
        text = args[i].text
        if text == "--":
            operands += args[i + 1:]
            break
        if text.startswith("--"):
            name, equals, _ = text.partition("=")
            if name in ("--in-place",) or (name.startswith("--in") and "--in-place".startswith(name)):
                in_place = True
            elif name in ("--expression", "--file"):
                script_given = True
                i += 0 if equals else 1
            i += 1
            continue
        if text.startswith("-") and text != "-":
            j = 1
            while j < len(text):
                flag = text[j]
                if flag == "i":
                    in_place = True
                    if j + 1 == len(text) and i + 1 < len(args) and (
                            args[i + 1].text == "" or re.match(r"^\.\w+$", args[i + 1].text)):
                        i += 1                     # BSD sed: -i '' or -i .bak
                    break
                if flag in "efl":
                    script_given = script_given or flag in "ef"
                    if j + 1 == len(text):
                        i += 1
                    break
                j += 1
            i += 1
            continue
        operands.append(args[i])
        i += 1
    if not in_place:
        return []
    files = operands if script_given else operands[1:]
    return [{"path": word.text, "dynamic": word.dynamic, "via": "sed -i"} for word in files]


def _find_deletes(args):
    """A find that deletes what it finds writes under each folder it starts from: "." when it names none. The files
    it removes are known only when it runs, so a guard judges the folder, not a file."""
    if not any(word.literal and word.text == "-delete" for word in args):
        return []
    i = 0
    while i < len(args) and args[i].text in ("-H", "-L", "-P", "-E", "-X", "-d", "-s", "-x"):
        i += 1
    starts = []
    while i < len(args) and not (args[i].literal and (args[i].text.startswith("-") or args[i].text in ("(", "!", ","))):
        starts.append(args[i])
        i += 1
    if not starts:
        return [{"path": ".", "dynamic": False, "via": "find -delete"}]
    return [{"path": word.text, "dynamic": word.dynamic, "via": "find -delete"} for word in starts]


def _redirect_reads(records):
    """The files a command reads by < or <>, as writes are given."""
    return [{"path": record["target"].text, "dynamic": record["target"].dynamic, "via": record["op"]}
            for record in records if record["op"] in ("<", "<>") and record["target"] is not None]


# The words that start ws.py: the script, and the launcher that starts it.
WITH_SECRETS_STARTERS = ("ws.py", "launch.sh", "start.py")
WITH_SECRETS = "ws.py with-secrets"


def _with_secrets_child(words):
    """(the words `ws.py with-secrets NAME ... -- PROGRAM ...` starts, its NAME words, the index of `with-secrets`),
    or None when the command holds no such form. A word named ws.py, launch.sh or start.py anywhere on the line
    counts, followed later by `with-secrets` and then `--`, so `sh wslib/launch.sh ws.py with-secrets` and `python3 -X utf8 ws.py` both count.
    The caller judges the child and the outer command both, so a word that only looks like the wrapper, as in a
    line that reads a file and then names ws.py, hides nothing."""
    def name(word):
        text = re.split(r"[\\/]", word.text)[-1].lower()
        for suffix in (".exe", ".cmd", ".bat", ".com"):
            if text.endswith(suffix):
                return text[:-len(suffix)]
        return text
    at = next((i for i, word in enumerate(words) if name(word) in WITH_SECRETS_STARTERS), None)
    if at is None:
        return None
    marker = next((i for i in range(at + 1, len(words)) if words[i].text == "with-secrets"), None)
    if marker is None:
        return None
    dashes = next((i for i in range(marker + 1, len(words)) if words[i].text == "--"), None)
    if dashes is None or dashes + 1 >= len(words):
        return None
    return words[dashes + 1:], [w for w in words[marker + 1:dashes] if not w.text.startswith("-")], marker

def _redirect_writes(records):
    writes = []
    for record in records:
        target = record["target"]
        if target is None or record["op"] in ("<", "<<", "<<-", "<<<", "<&"):
            continue
        if record["op"] == ">&" and (re.fullmatch(r"\d+-?|-", target.text) and not target.dynamic):
            continue
        writes.append({"path": target.text, "dynamic": target.dynamic, "via": record["op"]})
    return writes


# -- walking -----------------------------------------------------------------------------------------------------

class _Walker:
    def __init__(self, aliases, hosts):
        self.aliases, self.hosts, self.out = aliases, tuple(hosts), []

    def walk_list(self, items, ctx, via, line_start):
        for index, (chain, separator) in enumerate(items):
            scope = ctx.copy() if separator == "&" else ctx
            self.walk_chain(chain, scope, via, line_start and index == 0)

    def walk_chain(self, chain, ctx, via, first_of_line):
        pipelines, ops = chain
        scoped = False
        for k, pipeline in enumerate(pipelines):
            if scoped and ops[k - 1] != "&&":
                ctx.unknown_folder("a cd earlier in the line may not have run")
            target = self._cd_target(pipeline)
            if target is not False:
                self.walk_command(pipeline[0], ctx, via, piped_in=False)
                if target is not None:
                    ctx.cd_folders.append(target.text)
                leading = (k == 0 and not ctx.subshell and (first_of_line or (ops and ops[0] == "&&")))
                if not leading:
                    ctx.cwd, ctx.cwd_reason = None, ("a cd inside a subshell" if ctx.subshell else
                                                     "a cd or pushd that is not the leading command")
                elif target is None:
                    ctx.cwd, ctx.cwd_reason = None, "cd to a folder that cannot be known"
                elif target.dynamic:
                    ctx.cwd, ctx.cwd_reason = None, "cd to a variable or substitution"
                else:
                    ctx.cwd = _compose(ctx.cwd, target.text)
                    if ctx.cwd is None:
                        ctx.cwd_reason = ctx.cwd_reason or "the folder cannot be known"
                    scoped = not first_of_line
                continue
            for j, command in enumerate(pipeline):
                self.walk_command(command, ctx if len(pipeline) == 1 else ctx.copy(), via, piped_in=j > 0)
        if scoped:
            ctx.unknown_folder("a cd earlier in the line may not have run")

    @staticmethod
    def _cd_target(pipeline):
        """False when the pipeline is not a lone cd, pushd or popd; else its folder word, or None if unknowable."""
        if len(pipeline) != 1 or pipeline[0][0] != "simple":
            return False
        words = [w for w in pipeline[0][1]]
        while words and words[0].assign:
            words = words[1:]
        if words and words[0].literal and words[0].text in ("builtin", "command"):
            words = words[1:]
        if not words or not words[0].literal or words[0].text not in ("cd", "pushd", "popd", "chdir"):
            return False
        if words[0].text == "popd":
            return None
        operands = [w for w in words[1:] if not (w.literal and re.fullmatch(r"-[LPe@]+|--", w.text))]
        if not operands:
            return None if words[0].text == "pushd" else _literal("~")
        word = operands[0]
        if word.literal and (word.text == "-" or re.fullmatch(r"[+-]\d+", word.text)):
            return None
        return word

    def walk_subs(self, words, ctx, via):
        for word in words:
            for commands in word.subs:
                self.walk_list(commands, ctx.copy(subshell=True, in_sub=True), via, False)

    def walk_records(self, records, ctx, via):
        for record in records:
            if record["target"] is not None:
                self.walk_subs([record["target"]], ctx, via)
            for commands in record["body_subs"]:
                self.walk_list(commands, ctx.copy(subshell=True, in_sub=True), via, False)

    def walk_command(self, command, ctx, via, piped_in):
        kind = command[0]
        if kind == "subshell":
            self.walk_list(command[1], ctx.copy(subshell=True), via, False)
            self._redirect_only(command[2], ctx, via)
        elif kind == "keyword":
            self.walk_subs(command[1], ctx, via)
        elif kind == "group":
            self.walk_subs(command[2], ctx, via)
            for body in command[1]:
                self.walk_list(body, ctx, via, False)
            self._redirect_only(command[3], ctx, via)
        else:
            self.simple(command[1], command[2], ctx, via, piped_in)

    def _redirect_only(self, records, ctx, via):
        self.walk_records(records, ctx, via)
        writes, reads = _redirect_writes(records), _redirect_reads(records)
        if writes or reads:
            self.out.append(self._dict(None, [], {}, ctx, via, writes=writes, reads=reads))

    def simple(self, words, records, ctx, via, piped_in):
        self.walk_subs(words, ctx, via)
        self.walk_records(records, ctx, via)
        own, i = {}, 0
        while i < len(words) and words[i].assign:
            name, value = words[i].assign
            own[name] = (value, words[i].dynamic)
            i += 1
        writes, reads = _redirect_writes(records), _redirect_reads(records)
        if i == len(words):
            ctx.env.update(own)               # NAME=value alone: it stays for the rest of this shell
            if writes or reads:
                self.out.append(self._dict(None, [], own, ctx, via, writes=writes, reads=reads))
            return
        self.dispatch(words[i:], own, writes, records, ctx, via, piped_in, None, ctx.cwd, ctx.cwd_reason, False)

    def _dict(self, program, args, own, ctx, via, writes=(), cwd=None, cwd_reason=None, cleared=False,
              unresolved=None, runtime=None, use_ctx_cwd=True, reads=()):
        env = {} if cleared else {k: v for k, v in ctx.env.items()}
        env.update(own)
        return {
            "program": program, "args": [w.text for w in args],
            "dynamic_args": [k for k, w in enumerate(args) if w.dynamic],
            "message_args": [],
            "env": {k: (v[0] if v is not None else None) for k, v in env.items()},
            "env_dynamic": sorted(k for k, v in env.items() if v is not None and v[1]),
            "env_cleared": cleared,
            "wrappers": list(via), "in_substitution": ctx.in_sub, "in_subshell": ctx.subshell,
            "unresolved": unresolved, "runtime_args": runtime,
            "cwd": ctx.cwd if use_ctx_cwd else cwd, "cwd_unresolved": ctx.cwd_reason if use_ctx_cwd else cwd_reason,
            "cd_folders": list(ctx.cd_folders) if (ctx.cwd if use_ctx_cwd else cwd) is None else [],
            "writes": list(writes), "reads": list(reads), "config_writes": [],
            "config_env": sorted({k for k in CONFIG_ENV if k in env} | ({"HOME"} if cleared else set())),
            "ssh_env": sorted(k for k in SSH_ENV if env.get(k) is not None),
            "git": None, "gh": None,
        }

    def dispatch(self, words, own, writes, records, ctx, via, piped_in, runtime, cwd, cwd_reason, cleared):
        first = words[0]
        args = words[1:]
        env = {} if cleared else dict(ctx.env)
        env.update(own)
        reads = _redirect_reads(records)

        def emit(program, unresolved=None, **extra):
            entry = self._dict(program, args, own, ctx, via, writes, cwd, cwd_reason, cleared, unresolved, runtime,
                               use_ctx_cwd=False, reads=reads)
            entry["env"] = {k: (v[0] if v is not None else None) for k, v in env.items()}
            entry["env_dynamic"] = sorted(k for k, v in env.items() if v is not None and v[1])
            entry["config_env"] = sorted({k for k in CONFIG_ENV if k in env} | ({"HOME"} if cleared else set()))
            entry["ssh_env"] = sorted(k for k in SSH_ENV if env.get(k) is not None)
            for key, value, via_name in _env_config(env):
                entry["config_writes"].append({"key": key, "value": value, "op": "set", "via": via_name,
                                               "guarded": guarded_key(key)})
            entry.update(extra)
            self.out.append(entry)
            return entry

        if first.dynamic:
            return emit(first.text, "the program is a variable or substitution")
        name = first.text.rsplit("/", 1)[-1]
        if name.lower().endswith(".exe"):
            name = name[:-4]
        deep = ctx.depth >= MAX_DEPTH

        found = None if deep else _with_secrets_child(words)
        if found is not None:
            # Each NAME reaches the child set to a value from the secrets file, which no command line shows, so
            # it is a value the guards cannot know: GH_REPO or a GIT_CONFIG_* name is then unresolved, as when the
            # line sets it from a variable. The child must not pass as if it ran with none of them set.
            # A NAME given by a variable or a substitution may be any name, so every command the child holds is
            # unresolved. The outer command is then judged as itself too, below, so a line where a word only looks
            # like the wrapper hides nothing before it.
            child, names, marker = found
            own2 = dict(own)
            for word in names:
                if not word.dynamic:
                    own2[word.text] = ("$" + word.text, True)
            start = len(self.out)
            self.dispatch(child, own2, writes, records, ctx, via + [WITH_SECRETS], piped_in, runtime, cwd,
                          cwd_reason, cleared)
            if any(word.dynamic for word in names):
                for entry in self.out[start:]:
                    entry["unresolved"] = entry["unresolved"] or \
                        "a name ws.py with-secrets hands in is a variable or substitution"
            # The outer command, up to `with-secrets`, is judged as itself: `sudo python3 ws.py` or `cat .env ws.py`.
            return self.dispatch(words[:marker], own, writes, records, ctx, via, piped_in, runtime, cwd, cwd_reason,
                                 cleared)
        if name in WRAPPER_OPTIONS and not deep:
            unwrapped = self._unwrap(name, args)
            if unwrapped is not None:
                inner, extra, unset, clear, chdir, split = unwrapped
                own2 = dict(own)
                own2.update(extra)
                for variable in unset:
                    own2[variable] = None
                if chdir is not None:
                    cwd, cwd_reason = ((None, "env -C names a variable or substitution") if chdir[1]
                                       else (_compose(cwd, chdir[0]), cwd_reason))
                label = name
                if split is not None:
                    text = split[0] + " " + " ".join(shlex.quote(w.text) for w in inner)
                    return self._run_text(text, split[1] or any(w.dynamic for w in inner), name + " -S", words,
                                          own, writes, ctx, via, cwd, cwd_reason, reads)
                if inner:
                    if clear:
                        own2 = dict(extra)
                    return self.dispatch(inner, own2, writes, records, ctx, via + [label], piped_in,
                                         "xargs" if name == "xargs" else runtime, cwd, cwd_reason, cleared or clear)
                own, cleared = own2, cleared or clear
                env = {} if cleared else dict(ctx.env)
                env.update(own)
        if name == "eval" and not deep:
            dynamic = any(w.dynamic for w in args)
            text = " ".join(w.text for w in args)
            return self._run_text(text, dynamic, "eval", words, own, writes, ctx, via, cwd, cwd_reason, reads)
        if name == "watch" and not deep:
            _, operands = _scan(args, "nd", ("interval", "differences"))
            rest = [w for _, w in operands]
            if rest:
                return self._run_text(" ".join(w.text for w in rest), any(w.dynamic for w in rest), "watch",
                                      words, own, writes, ctx, via, cwd, cwd_reason, reads)
        if name in SHELL_PROGRAMS and not deep:
            return self._shell(name, args, own, writes, records, ctx, via, piped_in, emit, cwd, cwd_reason)
        if name in ("export", "declare", "typeset", "readonly", "local") and not ctx.in_sub:
            for word in args:
                if word.assign:
                    ctx.env[word.assign[0]] = (word.assign[1], word.dynamic)
        if name == "unset":
            for word in args:
                if not word.text.startswith("-"):
                    ctx.env[word.text] = None
        if name == "find" and not deep:
            entry = emit("find")
            entry["writes"] = list(writes) + _find_deletes(args)
            self._find(args, own, writes, ctx, via, cwd, cwd_reason, cleared)
            return entry

        entry = emit(name)
        entry["writes"] = list(writes) + _program_writes(name, args)
        if name == "git":
            facts, config_writes, file_writes, nested, messages = _git(args, env, cwd, cwd_reason, ctx,
                                                                       self.aliases)
            entry["git"] = facts
            entry["config_writes"] = config_writes + [w for w in entry["config_writes"]]
            entry["writes"] += file_writes
            entry["message_args"] = messages
            for text, dynamic, folder_note, label in nested:
                inner_ctx = ctx.copy(depth=ctx.depth + 1)
                if folder_note:
                    inner_ctx.cwd, inner_ctx.cwd_reason = None, f"it runs in {folder_note}"
                else:
                    inner_ctx.cwd, inner_ctx.cwd_reason = cwd, cwd_reason
                inner_ctx.env = dict(env)
                self._nested(text, dynamic, label, inner_ctx, via)
        elif name == "gh":
            facts, messages = _gh(args, env, self.hosts)
            entry["gh"] = facts
            entry["message_args"] = messages
        entry["dynamic_args"] = [k for k in entry["dynamic_args"] if k not in entry["message_args"]]
        return entry

    def _nested(self, text, dynamic, label, ctx, via):
        before = len(self.out)
        self.walk_list(_Parser(text, 0, ctx.depth).parse_list(), ctx.copy(subshell=False), via + [label], True)
        if dynamic:
            for entry in self.out[before:]:
                entry["unresolved"] = entry["unresolved"] or f"{label} runs text that holds a variable or substitution"

    def _run_text(self, text, dynamic, label, words, own, writes, ctx, via, cwd, cwd_reason, reads=()):
        """eval, sh -c, env -S, watch: the text is a command line of its own."""
        inner = ctx.copy(depth=ctx.depth + 1, cwd=cwd, cwd_reason=cwd_reason)
        inner.env = dict(ctx.env)
        inner.env.update(own)
        if label == "eval":
            inner = ctx                       # eval runs in this shell: its cd and exports stay
            inner.depth += 1
        before = len(self.out)
        self.walk_list(_Parser(text, 0, inner.depth).parse_list(), inner if label == "eval" else
                       inner.copy(subshell=False), via + [label], label != "eval")
        if label == "eval":
            inner.depth -= 1
        if dynamic:
            reason = f"{label} runs text that holds a variable or substitution"
            for entry in self.out[before:]:
                entry["unresolved"] = entry["unresolved"] or reason
            if len(self.out) == before:
                entry = self._dict(words[0].text.rsplit("/", 1)[-1], words[1:], own, ctx, via, writes, cwd,
                                   cwd_reason, unresolved=reason, use_ctx_cwd=False)
                self.out.append(entry)
        if writes or reads:
            self.out.append(self._dict(None, [], own, ctx, via, writes=writes, cwd=cwd, cwd_reason=cwd_reason,
                                       use_ctx_cwd=False, reads=reads))
        return None

    def _shell(self, name, args, own, writes, records, ctx, via, piped_in, emit, cwd, cwd_reason):
        i, has_c, reads_stdin = 0, False, False
        while i < len(args):
            text = args[i].text
            if text in ("--", "-"):
                i += 1
                break
            if text in ("-o", "+o", "-O", "+O", "--rcfile", "--init-file"):
                i += 2
                continue
            if text.startswith("--"):
                i += 1
                continue
            if re.fullmatch(r"[-+][A-Za-z]+", text):
                has_c = has_c or (text[0] == "-" and "c" in text)
                reads_stdin = reads_stdin or (text[0] == "-" and "s" in text)
                i += 1
                continue
            break
        reads = _redirect_reads(records)
        if has_c:
            if i < len(args):
                return self._run_text(args[i].text, args[i].dynamic, name + " -c", [_literal(name)] + args, own,
                                      writes, ctx, via, cwd, cwd_reason, reads)
            return emit(name)
        if i < len(args) and not reads_stdin:
            return emit(name)                  # a script: out of reach, and said so
        for record in records:
            if record["op"] in ("<<", "<<-") and record["body"] is not None:
                return self._run_text(record["body"], record["body_dynamic"],
                                      name + " <<", [_literal(name)] + args, own, writes, ctx, via, cwd, cwd_reason,
                                      reads)
            if record["op"] == "<<<" and record["target"] is not None:
                return self._run_text(record["target"].text, record["target"].dynamic, name + " <<<",
                                      [_literal(name)] + args, own, writes, ctx, via, cwd, cwd_reason, reads)
            if record["op"] == "<":
                return emit(name)              # a script read from a file
        if piped_in:
            return emit(name, "text is piped into a shell")
        return emit(name)

    def _find(self, args, own, writes, ctx, via, cwd, cwd_reason, cleared):
        i = 0
        while i < len(args):
            if args[i].literal and args[i].text in ("-exec", "-execdir", "-ok", "-okdir"):
                label = "find " + args[i].text
                j, segment = i + 1, []
                while j < len(args):
                    text = args[j].text
                    if text == ";" or (text == "+" and segment and segment[-1].text.endswith("{}")):
                        break
                    segment.append(args[j])
                    j += 1
                if segment:
                    supplied = any("{}" in w.text for w in segment)
                    inner_cwd, inner_reason = cwd, cwd_reason
                    if args[i].text in ("-execdir", "-okdir"):
                        inner_cwd, inner_reason = None, "find -execdir runs in each file's folder"
                    self.dispatch(segment, own, [], [], ctx.copy(depth=ctx.depth + 1), via + [label], False,
                                  "find -exec" if supplied else None, inner_cwd, inner_reason, cleared)
                i = j + 1
            else:
                i += 1

    @staticmethod
    def _unwrap(name, args):
        """(command words, env added, names unset, env cleared, chdir, split text) or None when the wrapper runs
        nothing: `command -v git`, or a bare `env` that prints the environment is a command of its own."""
        short_values, long_values = WRAPPER_OPTIONS[name]
        extra, unset, clear, chdir, split, i = {}, [], False, None, None, 0
        while i < len(args):
            word, text = args[i], args[i].text
            if text == "--":
                i += 1
                break
            if name in ("env", "sudo") and word.assign:
                extra[word.assign[0]] = (word.assign[1], word.dynamic)
                i += 1
                continue
            if name == "env" and text == "-":
                clear, i = True, i + 1
                continue
            if not text.startswith("-") or text == "-":
                break
            if name == "nice" and re.fullmatch(r"-\d+", text):
                i += 1
                continue
            if name == "command" and re.fullmatch(r"-[pvV]*[vV][pvV]*", text):
                return None
            if text.startswith("--"):
                option, equals, value = text[2:].partition("=")
                if option in long_values and not equals and i + 1 < len(args):
                    value_word = args[i + 1]
                    value, dynamic = value_word.text, value_word.dynamic
                    i += 1
                else:
                    dynamic = word.dynamic
                kind = _ENV_OPTIONS.get("--" + option) if name == "env" else None
                if name == "env" and option == "ignore-environment":
                    clear = True
                if kind == "unset":
                    unset.append(value)
                elif kind == "chdir":
                    chdir = (value, dynamic)
                elif kind == "split":
                    split = (value, dynamic)
                i += 1
                continue
            j = 1
            while j < len(text):
                flag = text[j]
                if name == "env" and flag == "i":
                    clear = True
                if flag in short_values:
                    if j + 1 < len(text):
                        value, dynamic = text[j + 1:], word.dynamic
                    elif i + 1 < len(args):
                        value, dynamic = args[i + 1].text, args[i + 1].dynamic
                        i += 1
                    else:
                        value, dynamic = "", False
                    kind = _ENV_OPTIONS.get("-" + flag) if name == "env" else None
                    if kind == "unset":
                        unset.append(value)
                    elif kind == "chdir":
                        chdir = (value, dynamic)
                    elif kind == "split":
                        split = (value, dynamic)
                    break
                j += 1
            i += 1
        if name == "timeout" and i < len(args):
            i += 1                              # the duration
        inner = args[i:]
        if not inner and split is None:
            return None
        return inner, extra, unset, clear, chdir, split


def analyze(command, aliases=None, hosts=("github.com",)):
    """One dict per simple command in a shell command line. See the module's docstring for the fields.

    aliases: git's configured aliases {name: expansion}, read by the caller; None when not known.
    hosts: the gh hosts that count as known; any other is unresolved."""
    walker = _Walker(aliases, hosts)
    try:
        walker.walk_list(parse(command or ""), _Context(), [], True)
    except RecursionError:
        walker.out = [walker._dict(None, [], {}, _Context(), [],
                                   unresolved="the command line nests too deeply to read")]
    return walker.out
