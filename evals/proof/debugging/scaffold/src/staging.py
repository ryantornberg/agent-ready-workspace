"""The staging reminder: does a git command stage every change in the folder, rather than files by name?"""
import shlex

# The options that stage everything, for each git subcommand that has them.
STAGE_ALL = {"add": {"-A", "--all", "."}, "commit": {"-a", "--all"}}
# The same option as one letter, which may sit in a cluster such as -am.
SHORT = {"add": "A", "commit": "a"}


def stages_all(command):
    """True when the command stages every change: git add -A, git add ., git commit -a, git commit -am "x"."""
    try:
        words = shlex.split(command)
    except ValueError:
        return False
    if len(words) < 2 or words[0] != "git" or words[1] not in STAGE_ALL:
        return False
    subcommand = words[1]
    for word in words[2:]:
        if word == "--":
            break
        if word in STAGE_ALL[subcommand]:
            return True
        if word.startswith("-") and not word.startswith("--") and SHORT[subcommand] in word[1:]:
            return True
    return False
