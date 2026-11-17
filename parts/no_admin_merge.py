"""Hook: refuse a pull-request merge with GitHub's administrator flag.

GitHub's branch rule requires CI to pass on Linux, macOS and Windows before a pull
request merges to main. It does not bind the repository's owner: `gh pr merge
--admin` merges past red CI, and an agent using the owner's sign-in can run it.
This hook refuses that command. A merge without the flag goes ahead, and GitHub
then requires CI as usual.

It reads the command line with the parser `no_stage_all` uses, loaded from that
part's file, so it follows the same separators, new lines, subshells, `sh -c`,
`eval` and wrappers, and skips heredoc bodies and quoted text. It cannot see a
merge made another way: a raw API call to the merge endpoint, a `gh` alias, or a
script. The machinery page says so. See docs/changing-the-machinery.md.
"""
import pathlib
import re
import types

KIND = "hook"
EVENT = "before-shell"
PAGE = "docs/changing-the-machinery.md"
GLOBAL_WITH_A_VALUE = {"-R", "--repo", "--hostname"}


def _parser():
    """no_stage_all's module, for its command-line parser. Loaded from its file, beside this one."""
    path = pathlib.Path(__file__).with_name("no_stage_all.py")
    module = types.ModuleType("no_stage_all_parser")
    module.__file__ = str(path)
    exec(compile(path.read_text(encoding="utf-8-sig"), str(path), "exec"), module.__dict__)
    return module


SHELL = _parser()


def calls(command, program, depth=0):
    """Yield the arguments of each call of `program` in a shell command line, unwrapped as no_stage_all does for git."""
    for words in SHELL.segments(command):
        wrapped = False
        while words and (words[0] in SHELL.KEYWORDS or words[0] in SHELL.WRAPPERS or re.match(r"^\w+=", words[0])
                         or (len(words) > 1 and words[0].startswith("-")) or re.match(r"^\d+(\.\d+)?[smhd]?$", words[0])):
            wrapped = wrapped or words[0] in SHELL.WRAPPERS
            words = words[1:]
        if wrapped and words and program in words and words[0].rsplit("/", 1)[-1] not in SHELL.SHELLS:
            words = words[words.index(program):]
        if not words:
            continue
        name = words[0].rsplit("/", 1)[-1]
        if name == "eval" and depth < 3:
            yield from calls(" ".join(words[1:]), program, depth + 1)
        elif name in SHELL.SHELLS and depth < 3:
            flags = [i for i, w in enumerate(words) if re.match(r"^-[A-Za-z]*c$", w)]
            if flags and len(words) > flags[0] + 1:
                yield from calls(words[flags[0] + 1], program, depth + 1)
        elif name in (program, program + ".exe"):
            yield words[1:]


def _admin(arguments):
    for argument in arguments:
        if argument == "--":
            return False
        if argument == "--admin" or (argument.startswith("--admin=") and argument.split("=", 1)[1].lower() != "false"):
            return True
    return False


def decide(event, config):
    for arguments in calls(event.get("command") or "", "gh"):
        rest = list(arguments)
        while rest and rest[0].startswith("-"):
            rest = rest[2:] if rest[0] in GLOBAL_WITH_A_VALUE else rest[1:]
        if rest[:2] == ["pr", "merge"] and _admin(rest[2:]):
            return ("gh pr merge --admin merges past the CI that GitHub's branch rule requires. Wait until all five "
                    f"CI jobs pass, then merge without --admin; see {PAGE}")
    return None
