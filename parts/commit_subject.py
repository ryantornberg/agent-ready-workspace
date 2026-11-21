"""Check: a commit's subject line follows one of the formats the manifest accepts.

The commit-msg hook runs it on the message (`ws.py check --message`). The subject is the message's first
line that is neither blank nor a comment. It must match one of the regular expressions in the config's
"formats", which default to conventional commits: a type, an optional scope in brackets, an optional "!",
a colon and a space, then the summary. git's own subjects pass whatever the formats: a merge ("Merge branch",
"Merge pull request", "Merge remote-tracking branch", ...), a revert ('Revert "...'), and an autosquash
subject ("fixup! ", "squash! ", "amend! "). A subject over 72 characters warns.

On any other snapshot it finds nothing: only the commit-msg hook gives it a message.
See docs/commits.md.
"""
import re

from wslib.parts import finding

KIND = "check"
COMMIT_MESSAGE = True
PAGE = "docs/commits.md"
MESSAGE = "commit message"
CONVENTIONAL = r"^(feat|fix|chore|docs|refactor|test|perf|ci|build|style|revert)(\([^()\s][^()]*\))?!?: \S"
GITS_OWN = re.compile(r"^(Merge (branch|branches|pull request|remote-tracking branch|tag|commit) |Revert \"|"
                      r"(fixup|squash|amend)! )")
LIMIT = 72


def subject(text):
    for line in text.splitlines():
        if line.strip() and not line.startswith("#"):
            return line.rstrip()
    return ""


def run(snapshot, config):
    if not snapshot.is_file(MESSAGE):
        return []
    formats = config.get("formats", [CONVENTIONAL])
    line = subject(snapshot.read(MESSAGE) or "")
    found = []
    if not line:
        return [finding(MESSAGE, 1, f"the message has no subject line. Write one, then commit again. See {PAGE}")]
    if not GITS_OWN.match(line) and not any(re.search(pattern, line) for pattern in formats):
        found.append(finding(MESSAGE, 1, f"the subject {line!r} matches none of the accepted formats, such as "
                                         f"'fix(scope): what changed'. Reword it, then commit again. See {PAGE}"))
    if len(line) > LIMIT:
        found.append(finding(MESSAGE, 1, f"the subject is {len(line)} characters, over {LIMIT}; shorten it, and "
                                         f"move the detail into the body. See {PAGE}", level="warning"))
    return found
