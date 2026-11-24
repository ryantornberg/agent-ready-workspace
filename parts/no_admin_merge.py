"""Hook: refuse a pull-request merge past CI, and any merge that is not a merge commit.

GitHub's branch rule requires CI to pass on Linux, macOS and Windows before a pull request merges to main. It does
not bind the repository's owner: `gh pr merge --admin` merges past red CI, and an agent using the owner's sign-in
can run it. This hook refuses that command.

It also refuses a merge that rewrites the branch's commits: `gh pr merge --squash` or `--rebase`, in their short
forms too, and a `gh api` call to a pull request's merge endpoint whose `merge_method` is not the literal `merge`.
A squash or rebase merge leaves the branch's own commits unreachable from main once the branch is deleted, and a
proof anchor pinned to one of them then names a commit main does not hold (decision record 0006). A call whose
body the hook cannot read, from `--input` or a field read from a file, is refused too, and so is any API write whose
path is a variable or a substitution. So is a GraphQL call that
merges a pull request, or turns on auto-merge, with a method other than `MERGE`, or whose query the hook cannot
read. A merge without a method flag goes ahead: gh then asks, and refuses to guess when no one can answer.

It refuses a command it cannot judge, as the other shell guards do (M3 slice C5c): a program word that is a variable
or a substitution, text piped into a shell, `eval` or `sh -c` of text that holds a variable, a gh subcommand that
is a variable, arguments that `xargs` or `find -exec` give `gh pr merge`, `gh api` or a gh call with no subcommand
when it runs, and an argument of `gh pr merge` that is a variable or a substitution, which could be `--admin`.
Message bodies never count.

It reads the command line with the shared parser, wslib/shell.py, so it follows separators, new lines, subshells,
`sh -c`, `eval` and wrappers, and skips heredoc bodies and quoted text. It cannot see a merge made another way: another
program such as `curl`, a `gh` alias, a script, an interpreter, or the web page. The repository's settings, which
allow merge commits only, close those. See docs/changing-the-machinery.md.
"""
import fnmatch
import re

from wslib import shell

KIND = "hook"
EVENT = "before-shell"
PAGE = "docs/changing-the-machinery.md"
# gh pr merge's options that take a value, so the value is not read as a flag: -b "--squash" is a body.
LONG_VALUES = {"--author-email", "--body", "--body-file", "--subject", "--match-head-commit", "--repo"}
SHORT_VALUES = set("AbFtR")
REWRITES = {"--squash": "--squash", "--rebase": "--rebase", "s": "--squash", "r": "--rebase"}
MERGE_ENDPOINT = re.compile(r"^repos/[^/]+/[^/]+/pulls/[^/]+/merge$")
GRAPHQL_MERGES = ("mergePullRequest", "enablePullRequestAutoMerge")


def _on(argument):
    """True for --flag, and for --flag=value unless the value is false."""
    return "=" not in argument or argument.split("=", 1)[1].lower() != "false"


def merge_flags(arguments):
    """The flags of a gh pr merge that this hook refuses: --admin, --squash and --rebase, however written."""
    found, skip = [], False
    for argument in arguments:
        if skip:
            skip = False
            continue
        if argument == "--":
            break
        if argument.startswith("--"):
            name = argument.split("=", 1)[0]
            if name in LONG_VALUES:
                skip = "=" not in argument
            elif name in ("--admin", "--squash", "--rebase") and _on(argument):
                found.append(name)
            continue
        if argument.startswith("-") and len(argument) > 1:
            for k, letter in enumerate(argument[1:]):
                if letter in SHORT_VALUES:
                    skip = k == len(argument) - 2          # the value is the next word only when none follows
                    break
                if letter in REWRITES:
                    found.append(REWRITES[letter])
    return found


def _api_merge(api):
    """Why a gh api call is a merge this hook refuses, or None."""
    if api.get("dynamic") or api.get("endpoint") is None:
        if api.get("effective_method") in ("GET", "HEAD"):
            return None
        return "a write to an API path it cannot read, which may be a pull request's merge endpoint"
    if api.get("graphql"):
        texts = [field.get("value") or "" for field in api.get("fields") or ()]
        if api.get("input") or any(field.get("file") or field.get("dynamic") for field in api.get("fields") or ()):
            return "a GraphQL call whose query is read from a file or a variable, which may merge a pull request"
        for text in texts:
            if any(name in text for name in GRAPHQL_MERGES):
                methods = re.findall(r"mergeMethod\s*:\s*(\$?\w+)", text)
                if any(method != "MERGE" for method in methods):
                    return f"a GraphQL merge with mergeMethod {next(m for m in methods if m != 'MERGE')}"
                if not methods and "enablePullRequestAutoMerge" in text:
                    return "a GraphQL auto-merge that names no mergeMethod"
        return None
    if not MERGE_ENDPOINT.match(api.get("path") or "") or api.get("effective_method") in ("GET", "HEAD"):
        return None
    if api.get("input"):
        return "a merge whose body is read from --input, so its merge_method cannot be read"
    for field in api.get("fields") or ():
        if field.get("key") != "merge_method":
            continue
        if field.get("dynamic") or field.get("file"):
            return "a merge whose merge_method is a variable or is read from a file"
        if field.get("value") != "merge":
            return f"a merge with merge_method {field.get('value')!r}"
    return None


def _dynamic(text):
    return "$" in text or "`" in text


def _unresolved(call):
    """Why this hook cannot tell whether the call merges past CI or rewrites a branch, or None."""
    if call.get("unresolved"):
        return call["unresolved"]
    gh = call.get("gh")
    if not gh:
        return None
    path = gh.get("path") or []
    if any(_dynamic(word) for word in path):
        return "the gh subcommand is a variable or a substitution"
    merges = path[:2] == ["pr", "merge"]
    if call.get("runtime_args") and (merges or path[:1] == ["api"] or len(path) < 2 and path[:1] in ([], ["pr"])):
        return f"{call['runtime_args']} gives gh {' '.join(path) or 'its subcommand'} its arguments when it runs"
    if merges:
        args, rest = call.get("args") or [], gh.get("args") or []
        start = len(args) - len(rest)
        if any(index >= start for index in call.get("dynamic_args") or ()):
            return "an argument of gh pr merge is a variable or a substitution, and could be a flag"
    return None


# -- A command no guard can read (Q54, Q74) ----------------------------------------------------------------------
# One block, held twice: in wslib/gitrules.py and in parts/no_admin_merge.py, which a grader loads with the parser
# alone. tests/test_shell.py holds the two copies equal. It needs `fnmatch`, `re` and the parser, `shell`.
#
# The parser misreads some lines, and then every guard judges a command the shell will not run. Until the parser's
# own fixes in M4, each shell guard refuses such a line in its own part file, as a command it cannot judge:
# - a program word the shell expands: a glob, braces, zsh's extended glob or zsh's =NAME (Q54);
# - an ANSI-C quoted escape, such as $'\x66', $'\146' or $'f', that the shell makes a printable character,
#   where the parser keeps the letters after the backslash (Q74);
# - a (( that the parser reads as arithmetic and that may hold a command: ((git push) ), which the shell runs as
#   two subshells, or $(( $(git push) )), whose command the parser never reads (Q74);
# - braces, a glob, a substitution or a variable the line sets to several words among a wrapper's or a shell's own
#   words, before its program: nice -n {5,git} push becomes nice -n 5 git push (Q74);
# - a program the parser does not read, such as arch, script or flock, one of whose words may be a program the
#   guards judge: git, /usr/bin/git, --command='git push', {git,}, gi?, or a variable the line sets to one; and for
#   a known runner, any variable or substitution among its words (Q74);
# - a line that nests shells, eval or sh -c text more than MAX_DEPTH deep, past what the parser reads (Q74).
EXPANDING = re.compile(r"[*?\[{}#^]|.~|^=")
BRACES = re.compile(r"\{[^{}]*(?:,|\.\.)[^{}]*\}")
GLOB = re.compile(r"[*?\[]")
ZSH_GLOB = re.compile(r"[*?\[#^]|.~|^=")
ANSI_ESCAPE = re.compile(r"\\(?:([0-7]{1,3})|x([0-9a-fA-F]{1,2})|u([0-9a-fA-F]{1,4})|U([0-9a-fA-F]{1,8}))")
ARITH_WORDS = re.compile(r"[\w.]\s+[A-Za-z_]")
COMMAND_TEXT = re.compile(r"[\s;&|]")
LINE_VARIABLE = re.compile(r"\$(?:\{(\w+)[^}]*\}|(\w+))")
# The programs the guards judge by name, or that run text, or that dump the environment.
JUDGED = frozenset({"git", "gh", "eval", "env", "printenv", "pwsh", "powershell"}) | shell.SHELL_PROGRAMS
# The programs the parser reads itself, its wrappers and shells among them.
READ = frozenset({"git", "gh", "find", "eval", "watch"}) | shell.SHELL_PROGRAMS | frozenset(shell.WRAPPER_OPTIONS)
# Programs whose words are data they print, look up, match, list or file, never a command they run.
DATA = frozenset({"echo", "printf", "which", "type", "whereis", "man", "info", "help", "apropos", "whatis", "tldr",
                  "hash", "alias", "unalias", "grep", "egrep", "fgrep", "rg", "ag", "ack", "sed", "awk", "jq", "sort", "uniq", "cut",
                  "tr", "diff", "wc", "head", "tail", "cat", "less", "more", "ls", "file", "stat", "du", "test", "[",
                  "[[", "mkdir", "touch", "rm", "rmdir", "cp", "mv", "ln", "cd", "pushd", "popd", "basename",
                  "dirname", "realpath", "readlink", "chmod", "chown", "true", "false", ":", "read", "export",
                  "declare", "typeset", "local", "readonly", "unset", "set", "shift", "return", "exit", "brew",
                  "apt", "apt-get", "dnf", "yum", "apk", "port", "pip", "pip3", "pipx", "npm", "pnpm", "yarn"})
# Runners the parser does not read: programs that start the command their words give, so any variable or
# substitution among those words may be the program.
RUNNERS = frozenset({"arch", "script", "flock", "chroot", "nsenter", "unshare", "runuser", "su", "pkexec",
                     "firejail", "strace", "ltrace", "valgrind", "taskset", "numactl", "chrt", "cgexec",
                     "systemd-run", "parallel", "sem", "rlwrap", "faketime", "torsocks", "proxychains",
                     "proxychains4", "tsp", "at", "batch", "nq", "dbus-launch", "xvfb-run", "hyperfine", "entr",
                     "watchexec", "sandbox-exec", "direnv", "dotenv", "op", "aws-vault", "doppler", "chpst",
                     "setpriv", "prlimit", "expect", "tmux", "screen", "nix-shell", "uv", "uvx", "poetry", "pipenv",
                     "bundle", "mise", "asdf", "npx", "pnpx", "bunx", "retry", "gtimeout", "gstdbuf", "ssh", "trap",
                     "gtime", "sg", "newgrp", "ddev"})


def expands(text):
    """True when the shell may expand a program word written so into another name, or into several words (Q54)."""
    return text not in ("[", "[[") and bool(EXPANDING.search(text))


def _base(text):
    """A program word's name as the shell finds it: its last part, without .exe, in lower case, since macOS and
    Windows find a program whatever its case."""
    name = text.replace("\\", "/").rsplit("/", 1)[-1].lower()
    return name[:-4] if name.endswith(".exe") else name


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
    """Why a word's source holds an ANSI-C escape that the shell makes a printable character, or None (Q74)."""
    i = 0
    while i < len(raw):
        if raw.startswith("$'", i):
            end = _close(raw, i)
            for match in ANSI_ESCAPE.finditer(raw, i + 2, end):
                if raw[i + 2:match.start()].replace("\\\\", "").endswith("\\"):
                    continue                     # \\x41: an escaped backslash, then plain letters
                code = int(next(group for group in match.groups() if group), 8 if match.group(1) else 16)
                if code >= 0x20 and code != 0x7F:
                    return (f"its word `{raw}` holds the ANSI-C escape `{match.group(0)}`, which the shell makes a "
                            f"character the parser does not read")
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
    found, raw = [], {}

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


def _matches(name, pattern):
    """fnmatch, where a pattern the shell cannot read as one, such as the range [a:-1], matches nothing."""
    try:
        return fnmatch.fnmatchcase(name, pattern)
    except re.error:
        return False


def _names_judged(text, source):
    """True when a word of a program the parser does not read may name a program the guards judge."""
    for part in {text, text.split("=", 1)[-1], text.lstrip("=")}:
        name = _base(part)
        pattern = re.sub(r"[#^~=]", "*", name)
        if name in JUDGED or (ZSH_GLOB.search(name) and any(_matches(judged, pattern) for judged in JUDGED)):
            return True
    if BRACES.search(source):
        return True
    if COMMAND_TEXT.search(text):
        try:
            return any(_base(call.get("program") or "") in JUDGED for call in shell.analyze(text))
        except RecursionError:
            return True
    return False


def _line_values(word, env):
    """The values the line itself gives the variables a word names, None for one it gives no fixed value, or None
    in place of the list when the word holds a substitution."""
    if "$(" in word.text or "`" in word.text:
        return None
    values = []
    for match in LINE_VARIABLE.finditer(word.text):
        value = env.get(match.group(1) or match.group(2))
        if value is not None:
            values.append(None if value[1] else value[0])
    return values


class _Reader(shell._Walker):
    """The parser's own walk, noting each program word as written and each command no guard can read."""

    def dispatch(self, words, own, writes, records, ctx, *rest):
        self.words.append(words[0])
        why = None if words[0].dynamic else self._unread(_base(words[0].text), words, own, ctx)
        if why:
            self.found.append(why)
        return super().dispatch(words, own, writes, records, ctx, *rest)

    def _unread(self, name, words, own, ctx):
        env = dict(ctx.env)
        env.update(own)
        if ctx.depth >= shell.MAX_DEPTH:
            return (f"the line nests shells, eval or sh -c text more than {shell.MAX_DEPTH} deep, past what the "
                    f"parser reads")
        if name in shell.WRAPPER_OPTIONS or name in shell.SHELL_PROGRAMS:
            inner = self._unwrap(name, words[1:]) if name in shell.WRAPPER_OPTIONS else None
            own_words = words[1:len(words) - len(inner[0])] if inner else words[1:]
            if name in shell.SHELL_PROGRAMS:
                first = next((k for k, word in enumerate(own_words) if not word.text.startswith(("-", "+"))
                              or word.text in ("-", "--")), len(own_words))
                own_words = own_words[:first + 1]
            for word in own_words:
                source = _source(word)
                values = _line_values(word, env) if "$" in source or "`" in source else []
                if BRACES.search(source) or GLOB.search(source) or values is None or any(
                        value is None or re.search(r"\s", value) or BRACES.search(value) for value in values):
                    return (f"`{word.text}` is one of {name}'s own words, and the shell may make it several words, "
                            f"one of them the program, so no guard can tell which runs")
            return None
        if name in READ or name in DATA:
            return None
        for word in words[1:]:
            if word.dynamic:
                values = _line_values(word, env)
                hit = name in RUNNERS or any(value is not None and _names_judged(value, value)
                                             for value in values or ())
            else:
                hit = _names_judged(word.text, _source(word))
            if hit:
                return (f"`{words[0].text}` may run another program, and its word `{word.text}` may be one the "
                        f"guards judge, which the parser does not read as a program")
        return None


def unreadable(command):
    """Why the shell would run the command otherwise than the parser reads it, or None (Q54, Q74)."""
    walker = _Reader(None, ("github.com",))
    walker.words, walker.found = [], []
    saved, shell._Parser = shell._Parser, _Parser
    _Parser.found, _Parser.raw = walker.found, {}
    try:
        walker.walk_list(shell.parse(command or ""), shell._Context(), [], True)
    except RecursionError:   # this walk adds a frame per wrapper, so it can run out before the parser does
        return "the line nests too deeply to read each program word"
    finally:
        shell._Parser = saved
        _Parser.found, _Parser.raw = [], {}
    for word in walker.words:
        if not word.dynamic and expands(word.text):
            return (f"its program word `{word.text}` is a pattern the shell expands (a glob, braces or a zsh "
                    f"pattern), so no guard can tell which program runs")
    return walker.found[0] if walker.found else None
# -- End of the block held twice. ------------------------------------------------------------------------------


def decide(event, config):
    expanded = unreadable(event.get("command") or "")   # {gh,} pr merge --admin: the gh goes unjudged (Q54, Q74)
    if expanded:
        return (f"this command cannot be judged: {expanded}, so it may merge past CI or rewrite a branch's commits. "
                f"Write it with literal words; to merge, run python3 ws.py merge NUMBER. See {PAGE}")
    for call in shell.analyze(event.get("command") or ""):
        why = _unresolved(call)
        if why:
            return (f"this command cannot be judged: {why}, so it may merge past CI or rewrite a branch's commits. "
                    f"Write it with literal words; to merge, run python3 ws.py merge NUMBER. See {PAGE}")
        gh = call.get("gh")
        if not gh:
            continue
        if gh.get("path", [])[:2] == ["pr", "merge"]:
            found = merge_flags(gh.get("args") or [])
            if "--admin" in found:
                return ("gh pr merge --admin merges past the CI that GitHub's branch rule requires. Wait until every "
                        f"required CI job passes, then merge with python3 ws.py merge NUMBER; see {PAGE}")
            if found:
                return (f"gh pr merge {found[0]} rewrites the branch's commits, and a proof anchor pinned to one of "
                        f"them would name a commit main does not hold. Merge with a merge commit: python3 ws.py "
                        f"merge NUMBER, or gh pr merge NUMBER --merge; see {PAGE}")
        elif gh.get("path", [])[:1] == ["api"] and gh.get("api"):
            why = _api_merge(gh["api"])
            if why:
                return (f"gh api makes {why}. Only a merge commit keeps a branch's commits on main. Merge with "
                        f"python3 ws.py merge NUMBER; see {PAGE}")
    return None
