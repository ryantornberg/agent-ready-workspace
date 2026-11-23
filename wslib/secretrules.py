"""The programs `ws.py with-secrets` refuses to start, shared by the command (wslib/secrets.py) and the
`secrets_shell` hook, so both refuse the same ones. It holds names and rules only: it reads no file and starts no
process, so a part may import it (decision 0004). M3 slice C5f.
"""
import re

SHELLS = frozenset({"sh", "bash", "zsh", "dash", "ksh", "ash", "mksh", "fish", "csh", "tcsh", "pwsh", "powershell",
                    "cmd", "busybox"})
RUNNERS = frozenset({"sudo", "doas", "su", "command", "exec", "time", "nohup", "timeout", "nice", "xargs", "builtin",
                     "stdbuf", "setsid", "script", "watch", "chroot", "unbuffer", "runuser", "start"})
REFUSED = SHELLS | RUNNERS | {"env", "printenv"}
SUFFIXES = (".exe", ".cmd", ".bat", ".com")
# Characters cmd.exe reads in a batch file's arguments, whatever Python passes (Python's subprocess documentation,
# "Security Considerations"). A batch file child with one of them in an argument is refused on Windows.
BATCH_SPECIAL = re.compile(r'[&|<>^%!"()\r\n]')


def program_name(word):
    """The program a word names: its last path segment, in lower case, without a Windows suffix."""
    name = re.split(r"[\\/]", word)[-1].lower()
    for suffix in SUFFIXES:
        if name.endswith(suffix):
            return name[:-len(suffix)]
    return name


def refusal(program):
    """Why `program` may not be the child of `ws.py with-secrets`, or None. program is the word as given."""
    name = program_name(program)
    if name in SHELLS:
        return f"{name} is a shell, which would show every value to whatever it runs"
    if name in ("env", "printenv"):
        return f"{name} prints the environment, the values included"
    if name in RUNNERS:
        return f"{name} runs another program it is given, which could be a shell"
    return None


def batch_refusal(path, arguments):
    """Why a batch file may not run with these arguments, or None. On Windows cmd.exe reads a batch file's
    arguments, so a special character in one could run another command with the values in its environment."""
    if not re.search(r"\.(?:bat|cmd)$", path, re.IGNORECASE):
        return None
    bad = next((word for word in arguments if BATCH_SPECIAL.search(word)), None)
    if bad is None:
        return None
    return f"{path} is a batch file, which cmd.exe runs, and the argument {bad!r} holds a character cmd.exe reads"
