"""Hook: refuse a shell command that stages everything.

Another session, or the person, may have edits in the same folder. "Stage
everything" sweeps those into this commit under the wrong message. Staging by
name cannot.

It reads the command line; it does not run a shell. It follows separators,
newlines, subshells, `sh -c "..."` and common wrappers. It cannot see through
a shell alias, a script, or a variable that holds the command, and it cannot
tell that `git add src` names a whole folder. The README's Limits say so.

The eval grader uses the same function, so the rule an agent is tested against
is the rule the hook enforces.
"""
import re
import shlex

KIND = "hook"
EVENT = "before-shell"

KEYWORDS = {"if", "then", "else", "elif", "do", "while", "until", "!", "{", "}", "fi", "done"}
WRAPPERS = {"sudo", "command", "env", "exec", "time", "nohup", "timeout", "nice", "xargs", "builtin"}
SHELLS = {"sh", "bash", "zsh", "dash", "ksh"}
OPTIONS_WITH_A_VALUE = {"-C", "-c", "--git-dir", "--work-tree", "--namespace", "--exec-path"}
EVERYTHING = re.compile(r"^(?::/\*?|[./*]+)$")   # .  ./  *  ./*  ../..  :/


def _long(argument, option):
    """True when argument is --option or an unambiguous-looking abbreviation of it, as git accepts."""
    return len(argument) >= 4 and argument.startswith("--") and option.startswith(argument.split("=")[0])


def segments(command):
    """Yield the word list of each simple command in a command line, including those inside sh -c."""
    for line in command.replace("\\\n", " ").splitlines():
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
        while words and (words[0] in KEYWORDS or words[0] in WRAPPERS or re.match(r"^\w+=", words[0])
                         or (len(words) > 1 and words[0].startswith("-")) or words[0].replace(".", "").isdigit()):
            words = words[1:]
        if not words:
            continue
        program = words[0].rsplit("/", 1)[-1]
        if program in SHELLS and "-c" in words and depth < 3:
            script = words[words.index("-c") + 1:]
            if script:
                yield from git_calls(script[0], depth + 1)
        elif program == "git":
            rest = words[1:]
            while rest and rest[0].startswith("-"):
                rest = rest[2:] if rest[0] in OPTIONS_WITH_A_VALUE else rest[1:]
            if rest:
                yield rest[0], rest[1:]


def stages_everything(command):
    """The reason a command stages more than it names, or None."""
    for subcommand, arguments in git_calls(command or ""):
        short = set("".join(a[1:] for a in arguments if a.startswith("-") and not a.startswith("--")))
        if subcommand in ("add", "stage"):
            if short & {"A", "u"} or any(_long(a, "--all") or _long(a, "--update") or EVERYTHING.match(a) for a in arguments):
                return "git add of everything"
        elif subcommand == "commit":
            if "a" in short or any(_long(a, "--all") for a in arguments):
                return "git commit -a stages every tracked change"
            if any(EVERYTHING.match(a) for a in arguments):
                return "git commit of the whole folder"
    return None


def decide(event, config):
    reason = stages_everything(event.get("command"))
    if reason:
        return f"{reason}. Stage the files you changed, by name: another session may have edits in this folder."
    return None
