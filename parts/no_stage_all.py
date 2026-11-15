"""Hook: remind the agent when a shell command stages everything.

Another session, or the person, may have edits in the same folder. "Stage
everything" sweeps those into this commit under the wrong message. Staging by
name cannot.

It reminds; it does not refuse. The commit check enforces the rule
(parts/edit_ledger.py): it compares what is staged with what the session's
edit tools wrote, whatever command staged it. The runner opens that ledger
when this hook fires and the session's working copy has uncommitted changes,
so the comparison runs even for a session that wrote its files only through
the shell. A command line cannot say which repository
it stages in, or what a pathspec covers, so a refusal here was both too wide,
as for `git add .` in a scratch repository, and too narrow, as for a script.
See docs/decisions/0002-hooks-remind-the-commit-enforces.md.

It reads the command line; it does not run a shell. It follows separators,
new lines, subshells, `sh -c "..."`, `eval` and common wrappers, and it skips
heredoc bodies and quoted text, so a commit message may mention the commands
it refuses. It cannot see through a shell alias, a script, a variable that
holds the command, or a command piped into a shell, and it cannot tell that
`git add src` names a whole folder. The README's Limits say so.

The eval grader uses the same function, so the rule an agent is tested against
is the rule the hook enforces.
"""
import re
import shlex

KIND = "hook"
EVENT = "before-shell"
MODE = "remind"

KEYWORDS = {"if", "then", "else", "elif", "do", "while", "until", "!", "{", "}", "fi", "done"}
WRAPPERS = {"sudo", "command", "env", "exec", "time", "nohup", "timeout", "nice", "xargs", "builtin"}
SHELLS = {"sh", "bash", "zsh", "dash", "ksh"}
OPTIONS_WITH_A_VALUE = {"-C", "-c", "--git-dir", "--work-tree", "--namespace", "--exec-path"}
EVERYTHING = re.compile(r"^(?::/\*?|[./*]+)$")   # .  ./  *  ./*  ../..  :/
# Options that take a value, so the value is not read as a flag or a pathspec: -m"add a test" holds no -a.
SHORT_VALUES = {"commit": "mFCct"}
LONG_VALUES = {"commit": ("--message", "--file", "--reuse-message", "--reedit-message", "--template", "--author",
                          "--date", "--cleanup", "--fixup", "--squash", "--trailer", "--pathspec-from-file"),
               "add": ("--chmod", "--pathspec-from-file")}


def _long(argument, option):
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


def git_calls(command, depth=0):
    """Yield (subcommand, arguments) for each git call in a shell command line."""
    for words in segments(command):
        # git has to be the command, not a word in its arguments: `echo git add -A` stages nothing.
        wrapped = False
        while words and (words[0] in KEYWORDS or words[0] in WRAPPERS or re.match(r"^\w+=", words[0])
                         or (len(words) > 1 and words[0].startswith("-")) or re.match(r"^\d+(\.\d+)?[smhd]?$", words[0])):
            wrapped = wrapped or words[0] in WRAPPERS
            words = words[1:]
        # A wrapper's own options may take values (sudo -u me git ...): look past them for git.
        if wrapped and words and "git" in words and words[0].rsplit("/", 1)[-1] not in SHELLS:
            words = words[words.index("git"):]
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
            if "=" not in argument and any(_long(argument, option) for option in long_values) and rest:
                rest.pop(0)
        else:
            for position, flag in enumerate(argument[1:]):
                short.add(flag)
                if flag in takes:
                    if position == len(argument) - 2 and rest:   # the value is the next word, not attached
                        rest.pop(0)
                    break
    return short, longs, specs


def stages_everything(command):
    """The reason a command stages more than it names, or None."""
    for subcommand, arguments in git_calls(command or ""):
        short, longs, specs = options(subcommand, arguments)
        if subcommand in ("add", "stage"):
            every = short & {"A", "u"} or any(_long(a, "--all") or _long(a, "--update") for a in longs)
            if any(EVERYTHING.match(a) for a in specs) or (every and not specs):
                return "git add of everything"
        elif subcommand == "commit":
            if "a" in short or any(_long(a, "--all") for a in longs):
                return "git commit -a stages every tracked change"
            if any(EVERYTHING.match(a) for a in specs):
                return "git commit of the whole folder"
    return None


def decide(event, config):
    reason = stages_everything(event.get("command"))
    if reason:
        return (f"This command stages more than it names ({reason}). Another session, or the person, may have "
                "edits in this folder. Stage the files this session changed, by name, and check what is staged "
                "with: git diff --cached --name-only")
    return None
