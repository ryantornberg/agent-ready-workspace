"""Hook: refuse an environment dump, and a shell command that reads a secrets file.

The shell half of the denies in the agent tools' settings (`agent_settings`, docs/agent-settings.md): Claude
Code's read tools refuse a secrets file, and this hook refuses a shell command that names one. M3 slice C5f.

It refuses:

- an environment dump: `env` that runs no program, `printenv` in every form, `export`, `declare` or `typeset`
  with no name, `set` with no argument, a read of `/proc/<pid>/environ`, and PowerShell's `env:` drive and
  `GetEnvironmentVariables`. That method's name is refused in any word of a command and in the rest of the raw
  line, which the parser cannot read as PowerShell; inside a message body, or a heredoc body fed to a program
  that is not a shell, it is text and passes (M3 slice PSFIX);
- a command that names a secrets file, in an argument or after `<` or `<>` (the reads the parser reports, inside
  substitutions, `eval` and a shell's `-c` text too), unless its program only looks at the file's
  name (NAMES_ONLY, and the git subcommands in GIT_NAMES_ONLY). The files are the patterns in "secrets" and
  "home", the same lists `agent_settings` holds the tools' settings to. Each is matched against the end of a
  path at any folder, without regard to case, so `../.env`, `~/.ssh/id_ed25519`, `$HOME/.aws/credentials` and
  `'C:\\Users\\me\\.netrc'` all match. A word is also split at quotes, brackets, `=`, `:`, `@` and the like, so
  `HEAD:.env`, `--env-file=.env`, `-d @.env` and `open('.env')` match too;
- a word that holds `*` or `?` and could match a secrets file, such as `.e*` or `cat *`;
- a variable the line itself sets is read with that value, so `F=.env; cat "$F"` is refused. Any other variable
  passes, as it does for `git_folder_shell`;
- `ws.py with-secrets` whose program is one that command refuses itself (a shell, `env`, `printenv` or a program
  that runs another), is given by a variable or substitution, or is a git or gh call or a write the parser reports. The other shell guards read only the
  line's own program, which here is Python, so they would not judge a push or a gh write run through it.

The first word after `grep`, `rg`, `sed`, `awk` and their kin, and after `git grep`, is a pattern, not a file,
unless `-e` or `-f` gives one. Message bodies, such as `git commit -m`, are not read.

What it cannot see, the README's limits say: an interpreter or a script that opens the file, a recursive read
such as `grep -r` over a folder that holds one, files `xargs` or `find -exec` supply, a variable the line does not
set, a write to a secrets file, and a program that passes a value on. See docs/agent-settings.md.
"""
import posixpath
import re
import shlex

from wslib import gitrules
from wslib import secretrules
from wslib import shell

KIND = "hook"
EVENT = "before-shell"
PAGE = "docs/agent-settings.md#secrets-in-the-shell"

# Programs that act on a file's name, not on what it holds.
NAMES_ONLY = frozenset({"ls", "stat", "test", "[", "rm", "rmdir", "unlink", "touch", "mkdir", "chmod", "chown",
                        "echo", "printf", "cd", "pushd", "basename", "dirname", "realpath", "readlink", "file"})
GIT_NAMES_ONLY = frozenset({"status", "check-ignore", "ls-files", "rm"})
# Programs whose first operand is a pattern or a script, unless an option gives it.
PATTERN_FIRST = frozenset({"grep", "egrep", "fgrep", "zgrep", "rg", "ag", "ack", "sed", "gsed", "awk", "gawk",
                           "mawk", "nawk"})
PATTERN_OPTIONS = ("--regexp", "--file", "--expression", "--source")
FILE_MESSAGES = ("-F", "--file", "--body-file", "--notes-file")   # message options that name a file to read
PS_VALUES = {"-o", "-O", "-p", "-q", "-u", "-U", "-g", "-G", "-t", "-C", "-k", "-F", "-M", "-N"}
DUMPERS = frozenset({"export", "declare", "typeset"})
METHOD = "getenvironmentvariables"   # PowerShell's [Environment]::GetEnvironmentVariables(), matched in lower case
ENVIRON = "proc/*/environ"
SPLIT = re.compile(r"[\s'\"`()\[\]{}<>|;&=:,@$!]+")
VARIABLE = re.compile(r"\$\{?([A-Za-z_]\w*)\}?")
STARTERS = ("ws.py", "launch.sh", "start.py")   # ws.py, and the launcher that starts it


def _glob(pattern):
    """A regular expression for one glob: ** spans folders, * and ? stay inside one."""
    out, i = "", 0
    while i < len(pattern):
        if pattern.startswith("/**", i) and i + 3 == len(pattern):
            out, i = out + "(?:/.*)?", i + 3
        elif pattern.startswith("**/", i):
            out, i = out + "(?:.*/)?", i + 3
        elif pattern.startswith("**", i):
            out, i = out + ".*", i + 2
        elif pattern[i] == "*":
            out, i = out + "[^/]*", i + 1
        elif pattern[i] == "?":
            out, i = out + "[^/]", i + 1
        else:
            out, i = out + re.escape(pattern[i]), i + 1
    return re.compile(out + r"\Z", re.IGNORECASE)


def _patterns(config):
    """[(regex, sample paths)] for each secrets pattern, matched against a path's end."""
    found = []
    extra = [config["file"]] if isinstance(config.get("file"), str) and config["file"] else []
    for pattern in list(config.get("secrets", ())) + list(config.get("home", ())) + extra + [ENVIRON]:
        text = re.sub(r"^(?:~/|\./|[A-Za-z]:/|/+)", "", pattern.replace("\\", "/"))
        while text.startswith("**/"):
            text = text[3:]
        sample = re.sub(r"\*\*|\*|\?", "x", text)
        samples = [sample, sample[:-2]] if sample.endswith("/x") else [sample]
        found.append((_glob(text), samples, pattern == ENVIRON))
    return found


def _ends(path):
    """Every end of a path that starts at a folder boundary: a/b/c gives a/b/c, b/c and c."""
    parts = [part for part in path.split("/") if part not in ("", ".")]
    return ["/".join(parts[i:]) for i in range(len(parts))]


def _secret(piece, patterns):
    """(pattern, is the environment) when a word's piece names a secrets file or could, as a glob; else None."""
    path = posixpath.normpath(piece.replace("\\", "/")) if piece else ""
    if not path or path == ".":
        return None
    ends = _ends(path)
    globbed = "*" in path or "?" in path
    for regex, samples, environ in patterns:
        if any(regex.match(end) for end in ends):
            return regex, environ
        if globbed:
            parts = path.split("/")
            for sample in samples:
                size = sample.count("/") + 1
                tail = "/".join(parts[-size:]) if len(parts) >= size else None
                if (tail and _glob(tail).match(sample)) or ("**" in path and _glob(path).match(sample)):
                    return regex, environ
    return None


def _expand(text, env):
    """The text with each variable the line set filled in; a variable it did not set stays as written."""
    for _ in range(4):
        new = VARIABLE.sub(lambda m: env[m.group(1)] if isinstance(env.get(m.group(1)), str)
                           else m.group(0), text)
        if new == text:
            break
        text = new
    return text


def _named(words, env, patterns):
    """The first word whose text names a secrets file, with what it matched, or None."""
    for word in words:
        for piece in SPLIT.split(_expand(word, env)):
            hit = _secret(piece, patterns)
            if hit:
                return word, hit[1]
    return None


def _operands(program, args):
    """The words a reader reads: all of them, but a pattern-first program's first operand when no option gives one."""
    if program not in PATTERN_FIRST:
        return list(args)
    for word in args:
        if word == "--":
            break
        if word.startswith("--") and word.split("=")[0] in PATTERN_OPTIONS:
            return list(args)
        if word in ("-e", "-f") or re.match(r"^-[A-Za-z0-9]*[ef]", word) and not word.startswith("--"):
            return list(args)
    skipped, out = False, []
    for word in args:
        if not skipped and not word.startswith("-"):
            skipped = True
            continue
        out.append(word)
    return out


def _names_a_file(args, i):
    """True when message body i is a file to read the message from, such as `git commit -F FILE`."""
    word = args[i]
    return (i > 0 and args[i - 1] in FILE_MESSAGES) or any(word.startswith(option + "=") for option in FILE_MESSAGES
                                                              if option.startswith("--"))


def _ps_environment(args):
    """True when ps is asked for each process's environment: a BSD-style letter group holding e, such as `eww` or
    `auxe`, or a dash group holding E, as macOS spells it. A value of an option such as `-o user` is not a group."""
    for i, word in enumerate(args):
        if word.startswith("-"):
            if not word.startswith("--") and "E" in word:
                return True
        elif re.match(r"^[A-Za-z]+$", word) and re.search("[eE]", word) and (i == 0 or args[i - 1] not in PS_VALUES):
            return True
    return False


def _dump(program, args):
    """Why the command prints the environment, or None."""
    names = [word for word in args if not word.startswith(("-", "+"))]
    if program == "env":
        return "`env` with no program to run prints the whole environment"
    if program == "printenv":
        return "`printenv` prints the environment"
    if program == "ps" and _ps_environment(args):
        return "`ps` with `e` or `-E` prints each process's environment"
    if program == "set" and not args:
        return "`set` with no argument prints every variable"
    if program in DUMPERS and not names and not (args and all(set(word.lstrip("-")) <= set("fF") for word in args)):
        return f"`{program}` with no name prints the exported variables"
    for word in [program or ""] + list(args):
        if re.match(r"^env:[\\/*]?$", word, re.IGNORECASE):
            return "PowerShell's env: drive prints the whole environment"
    return None


def _with_secrets_child(command):
    """The program and arguments `ws.py with-secrets` would start, or None when the command is not that. ws.py is
    found by name wherever it stands, so `python3 -X utf8 ws.py`, `./ws.py` and the launcher all count."""
    words = [command["program"] or ""] + list(command["args"])
    at = next((i for i, word in enumerate(words) if secretrules.program_name(word) in STARTERS), None)
    if at is None or "with-secrets" not in words[at + 1:]:
        return None
    rest = words[words.index("with-secrets", at + 1) + 1:]
    return rest[rest.index("--") + 1:] if "--" in rest else None


def _child_refusal(child):
    reason = secretrules.refusal(child[0])
    if reason:
        return f"`ws.py with-secrets` refuses this program itself: {reason}"
    if re.search(r"[$`]", child[0]):   # G=git; ... -- $G push: the shell picks the program, which no guard sees
        return f"`ws.py with-secrets` may not run a program given by a variable or substitution: {child[0]}"
    if gitrules.expands(child[0]):   # -- {git,} push: the shell expands it before with-secrets starts it (Q54)
        return f"`ws.py with-secrets` may not run a program word the shell expands (a glob or braces): {child[0]}"
    for inner in shell.analyze(shlex.join(child)):
        reason = secretrules.refusal(inner["program"] or "") or _dump(inner["program"], inner["args"])
        if reason or inner["wrappers"] or inner["unresolved"]:
            return f"`ws.py with-secrets` may not run a program that runs another or prints the environment: {child[0]}"
        if _with_secrets_child(inner) is not None:
            return "`ws.py with-secrets` inside another is refused: its program would go unjudged"
        if inner["git"] or inner["gh"] or inner["writes"]:
            return ("`ws.py with-secrets` may not run git, gh or a program that writes a file the shell guards "
                    "judge, since they would not see it: run git and gh by their own names, which sign in "
                    "on their own")
    return None


def _data(node, out):
    """The text in a parsed line that no shell runs: each heredoc body fed to a program that is not a shell. A
    shell's heredoc is kept, since PowerShell's and cmd's are not read as commands by the parser."""
    if isinstance(node, (list, tuple)):
        if len(node) == 3 and node[0] == "simple":
            names = {secretrules.program_name(word.text) for word in node[1] if isinstance(word, shell.Word)}
            if not names & secretrules.SHELLS:
                out.extend(record["body"] for record in node[2]
                           if isinstance(record, dict) and record.get("op") in ("<<", "<<-") and record.get("body"))
        for item in node:
            _data(item, out)
    elif isinstance(node, dict):
        for key in ("target", "body_subs"):
            _data(node.get(key), out)
    elif isinstance(node, shell.Word):
        for sub in node.subs:
            _data(sub, out)
    return out


def _runs_method(command, calls):
    """True when a command the line runs names PowerShell's environment-variables method. Message bodies and
    heredoc bodies that no shell reads are text, not commands, so the name there passes. The rest of the raw line
    is still read, since the parser reads PowerShell's `[Environment]::Method()` as no command at all."""
    for call in calls:
        words = [call["program"] or ""] + [word for i, word in enumerate(call["args"]) if i not in call["message_args"]]
        if any(METHOD in word.lower() for word in words):
            return True
    text = command
    bodies = [call["args"][i] for call in calls for i in call["message_args"]] + _data(shell.parse(command), [])
    for body in sorted(bodies, key=len, reverse=True):
        text = text.replace(body, " ")
    return METHOD in text.lower()


def decide(event, config):
    command = event.get("command") or ""
    patterns = _patterns(config)
    expanded = gitrules.unreadable(command)   # {env,} or {cat,} .env: the program goes unjudged (Q54, Q74)
    if expanded:
        return (f"this command cannot be judged: {expanded}, so it may print the environment or read a secrets "
                f"file. Write it with literal words. See {PAGE}")
    calls = shell.analyze(command)
    if METHOD in command.lower() and _runs_method(command, calls):
        return ("PowerShell's GetEnvironmentVariables method prints the whole environment, secrets included. To see "
                "a variable that holds no secret, such as PATH, echo it by name; ask the person for a secret.")
    assigned = {}
    for call in calls:
        assigned.update({name: value for name, value in call["env"].items()
                         if isinstance(value, str) and name not in call["env_dynamic"]})
    for call in calls:
        program = call["program"]
        if "WS_SECRETS_FILE" in call["env"] or (program == "export" and any(
                word.split("=")[0] == "WS_SECRETS_FILE" for word in call["args"])):
            return ("WS_SECRETS_FILE names the file ws.py with-secrets reads; a person sets it in their own shell, "
                    "never an agent's command. Leave it out, or ask the person.")
        reason = _dump(program, call["args"])
        if reason:
            return (f"{reason}, secrets included. To see a variable that holds no secret, such as PATH, echo it "
                    f"by name; ask the person for a secret.")
        child = _with_secrets_child(call)
        if child:
            reason = _child_refusal(child)
            if reason:
                return reason
        env = {**assigned, **{name: value for name, value in call["env"].items() if isinstance(value, str)}}
        skip = {i for i in call["message_args"] if not _names_a_file(call["args"], i)}
        args = [word for i, word in enumerate(call["args"]) if i not in skip]
        if program in NAMES_ONLY:
            continue
        if program == "git" and call["git"]:
            if call["git"]["subcommand"] in GIT_NAMES_ONLY:
                continue
            if call["git"]["subcommand"] == "grep":
                args = call["git"]["globals"] + _operands("grep", call["git"]["args"])
        else:
            args = _operands(program, args)
        hit = _named(args, env, patterns)
        if hit:
            return _message(*hit)
    for call in calls:
        for read in call["reads"]:
            hit = _named([read["path"]], assigned, patterns)
            if hit:
                return _message("< " + read["path"], hit[1])
    return None


def _message(word, environ):
    if environ:
        return f"{word} is a process's environment, secrets included. Ask the person for the one value you need."
    what = "may match a secrets file: name the files instead" if re.search(r"[*?]", word) else "names a secrets file"
    return (f"{word} {what}, and agents do not read secrets files. To give a program a value from the secrets "
            f"file, run python3 ws.py with-secrets NAME -- PROGRAM; else ask the person.")
