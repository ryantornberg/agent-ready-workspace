"""Check: a commit adds no line that looks like a credential.

A token pushed to a public repository is exposed at once, and deleting it in a later commit leaves it in
the history. So the check reads only the lines a commit adds, at the commit against the last commit and in CI
against the base branch, and matches them against the formats of common tokens and private keys. In CI,
`python3 ws.py check --history` runs it once more over every line every commit in the history added.

A finding never repeats the token: it names the format and the first four characters only, so the output
is safe to paste. Formats: GitHub tokens, AWS access key ids, a private key block, Slack, Anthropic,
OpenAI, Google API keys, Stripe live keys and npm tokens. A test value is built from pieces at run time, or
written with JSON escapes in a cases file, so the file's text never holds a whole token.

Limits: a format it does not know, a token split across lines, and a secret in a file git stores as binary
pass. It is a seatbelt, not a vault. See docs/commits.md.
"""
import re

from wslib.parts import finding

KIND = "check"
HISTORY = True   # `ws.py check --history` runs it over every line the history added
PAGE = "docs/commits.md"

FORMATS = [
    ("a GitHub token", re.compile(r"(?<![A-Za-z0-9_])gh[pousr]_[A-Za-z0-9]{36,255}(?![A-Za-z0-9_])")),
    ("a GitHub fine-grained token", re.compile(r"(?<![A-Za-z0-9_])github_pat_[A-Za-z0-9_]{60,255}")),
    ("an AWS access key id", re.compile(r"(?<![A-Z0-9])(?:AKIA|ASIA)[0-9A-Z]{16}(?![A-Z0-9])")),
    ("a private key", re.compile(r"-----BEGIN (?:[A-Z0-9]+ )*PRIVATE KEY(?: BLOCK)?-----")),
    ("a Slack token", re.compile(r"(?<![A-Za-z0-9])xox[abposr]-[A-Za-z0-9-]{10,}")),
    ("an Anthropic API key", re.compile(r"(?<![A-Za-z0-9])sk-ant-[A-Za-z0-9_-]{32,}")),
    ("an OpenAI API key", re.compile(r"(?<![A-Za-z0-9])sk-(?:proj-|svcacct-|admin-)?(?!ant-)[A-Za-z0-9_-]{40,}")),
    ("a Google API key", re.compile(r"(?<![A-Za-z0-9])AIza[0-9A-Za-z_-]{35}(?![0-9A-Za-z_-])")),
    ("a Stripe live key", re.compile(r"(?<![A-Za-z0-9])[rs]k_live_[0-9A-Za-z]{24,}")),
    ("an npm token", re.compile(r"(?<![A-Za-z0-9])npm_[A-Za-z0-9]{36}(?![A-Za-z0-9])")),
]


def tokens(line):
    """[(format, first four characters)] for each token-like text in the line."""
    found = []
    for name, pattern in FORMATS:
        for match in pattern.finditer(line):
            found.append((name, match.group(0)[:4]))
    return found


def run(snapshot, config):
    found = []
    for path in sorted(snapshot.changed):
        for number, line in snapshot.added_lines(path) or ():
            for name, start in tokens(line):
                found.append(finding(path, number, f"adds what looks like {name} ({start}...). Take it out of the "
                                                   f"file and revoke it with its issuer, since a pushed token is "
                                                   f"exposed; a test value is built from pieces at run time. Then "
                                                   f"run: python3 ws.py check --staged. See {PAGE}"))
    return found
