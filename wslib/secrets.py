"""`ws.py with-secrets`: hand named values from the secrets file to one child process, never to the calling shell.

    python3 ws.py with-secrets NAME [NAME ...] -- PROGRAM [ARGUMENT ...]

The values come from the file that the `secrets_shell` entry of the manifest names in "file", `.env` by default. A
relative name is read from the top of the main working copy, so every linked worktree reads the same file. The
agent tools deny reading that file, and the `secrets_shell` hook refuses a shell command that names it, so the
values reach the child without passing through the agent's context or its shell.

The file holds one `NAME=value` per line. Blank lines and lines starting with `#` are skipped, a leading `export `
is dropped, and a value in single or double quotes loses its quotes. An unquoted value ends at ` #`.

The child gets the calling environment plus the named values, and nothing else from the file. It runs with no
shell, so `$NAME` on the command line is never filled in: the child must read the variable itself, as gh, npm and
most command-line tools do.

It refuses a child in REFUSED: a shell, `env`, `printenv`, or a program that runs another program it is given,
such as `sudo`, `xargs` or `nohup`, since any of them would print or pass on every value. It judges the program
by the name it is called by and by the name of the file a symbolic link leads to. An interpreter, a script or a
program that starts a shell itself can still print the values; the README's limits say so. M3 slice C5f.

Exit codes: the child's; 2 when it refuses, the file or a name is missing, or the child cannot start.
"""
import os
import pathlib
import re
import shutil
import subprocess

DEFAULT_FILE = ".env"
NAME = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")
SHELLS = frozenset({"sh", "bash", "zsh", "dash", "ksh", "ash", "mksh", "fish", "csh", "tcsh", "pwsh", "powershell",
                    "cmd", "busybox"})
RUNNERS = frozenset({"sudo", "doas", "su", "command", "exec", "time", "nohup", "timeout", "nice", "xargs", "builtin",
                     "stdbuf", "setsid", "script", "watch", "chroot", "unbuffer", "runuser", "start"})
REFUSED = SHELLS | RUNNERS | {"env", "printenv"}
SUFFIXES = (".exe", ".cmd", ".bat", ".com")


class SecretsError(Exception):
    pass


def program_name(word):
    """The program a word names: its last path segment, in lower case, without a Windows suffix."""
    name = re.split(r"[\\/]", word)[-1].lower()
    for suffix in SUFFIXES:
        if name.endswith(suffix):
            return name[:-len(suffix)]
    return name


def refusal(program):
    """Why `program` may not be the child, or None. program is the word as given."""
    name = program_name(program)
    if name in SHELLS:
        return f"{name} is a shell, which would show every value to whatever it runs"
    if name in ("env", "printenv"):
        return f"{name} prints the environment, the values included"
    if name in RUNNERS:
        return f"{name} runs another program it is given, which could be a shell"
    return None


def split(rest):
    """(names, child) from the words after `with-secrets`: NAME ... -- PROGRAM ARGUMENT ..."""
    if "--" not in rest:
        raise SecretsError("name the values, then --, then the program: "
                           "python3 ws.py with-secrets NAME [NAME ...] -- PROGRAM [ARGUMENT ...]")
    at = rest.index("--")
    names, child = rest[:at], rest[at + 1:]
    if not names:
        raise SecretsError("name at least one value before --")
    bad = [name for name in names if not NAME.match(name)]
    if bad:
        raise SecretsError(f"not a variable name: {', '.join(bad)}")
    if not child:
        raise SecretsError("name the program to run after --")
    return names, child


def read(text):
    """{NAME: value} from the text of a secrets file."""
    values = {}
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("export "):
            line = line[len("export "):].lstrip()
        name, equals, value = line.partition("=")
        name = name.strip()
        if not equals or not NAME.match(name):
            continue
        value = value.strip()
        if len(value) >= 2 and value[0] == value[-1] == "'":
            value = value[1:-1]
        elif len(value) >= 2 and value[0] == value[-1] == '"':
            value = re.sub(r'\\(["\\n])', lambda m: "\n" if m.group(1) == "n" else m.group(1), value[1:-1])
        else:
            value = re.split(r"\s#", value, maxsplit=1)[0].rstrip()
        values[name] = value
    return values


def file_of(root, entry):
    """The secrets file's path: the entry's "file", or .env, relative to the main working copy's top."""
    from . import lease as leases
    name = (entry or {}).get("file", DEFAULT_FILE)
    if not isinstance(name, str) or not name:
        raise SecretsError('the "file" of the secrets_shell entry in workspace.json must be a file name')
    path = pathlib.Path(name).expanduser()
    if path.is_absolute():
        return path
    main = leases.main_copy(root)
    return (main[0] if main else pathlib.Path(root)) / path


def resolve(program, env):
    """The program's file on PATH, as the child would be started, or the word itself."""
    if re.search(r"[\\/]", program):
        return program
    return shutil.which(program, path=env.get("PATH")) or program


def run(root, rest, entry=None):
    names, child = split(rest)
    reason = refusal(child[0])
    if reason:
        raise SecretsError(f"refused: {reason}. Run the program that needs the value as the child, by its own name")
    path = file_of(root, entry)
    try:
        values = read(path.read_text(encoding="utf-8-sig"))
    except FileNotFoundError:
        raise SecretsError(f"no secrets file at {path}; a person writes it, with one NAME=value per line")
    except (OSError, UnicodeDecodeError) as error:
        raise SecretsError(f"cannot read the secrets file {path}: {type(error).__name__}")
    missing = [name for name in names if name not in values]
    if missing:
        raise SecretsError(f"{path} holds no value for {', '.join(missing)}")
    env = dict(os.environ)
    env.update({name: values[name] for name in names})
    program = resolve(child[0], env)
    real = os.path.realpath(program) if os.path.exists(program) else program
    # busybox is refused by name only: on a system built on it, every program's file is busybox.
    reason = refusal(program) or (refusal(real) if program_name(real) != "busybox" else None)
    if reason:
        raise SecretsError(f"refused: {child[0]} leads to {real}, and {reason}")
    try:
        done = subprocess.run([program, *child[1:]], env=env)
    except OSError as error:
        raise SecretsError(f"cannot start {child[0]}: {error.strerror or type(error).__name__}")
    return done.returncode if done.returncode >= 0 else 128 - done.returncode
