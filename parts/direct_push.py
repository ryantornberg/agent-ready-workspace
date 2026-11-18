"""Check, at the push: a commit that changes machinery does not reach main by a direct push.

Machinery is the scripts, hooks and CI that check everything else: the paths listed
in "machinery". A broken hook on main locks out every session that pulls it, so a
machinery change reaches main only through a pull request, where GitHub's branch
rule requires CI to pass on Linux, macOS and Windows. That rule does not bind the
repository's owner, and an agent using the owner's sign-in can push straight to
main; this check refuses that push. Doc-only commits still go straight to main.

It runs from the pre-push hook (`ws.py check --push`), on the commits the push
adds, merges left out: a merge is judged by the commits it brings in. The runner
reads this part, its cases and the manifest from the remote's current tip, so a
push that edits the list cannot weaken the check that judges it.

Config: "machinery": paths. A path ending in "/" is a folder and everything under
it; a "*" matches within one folder, so "evals/*.py" is not "evals/scaffold/a.py".
"branch" (default "main"): the branch it guards.
A commit that adds or changes a proof anchor, a proven-by line in a page's front matter or a section's
proof line, is refused the same way, whatever its paths: the engine marks it "anchors" (decision record 0006).

See docs/changing-the-machinery.md.
"""
import re

from wslib.parts import finding

KIND = "check"
PHASES = ("push",)
PAGE = "docs/changing-the-machinery.md"


def _pattern(entry):
    if entry.endswith("/"):
        return re.compile(re.escape(entry) + ".*", re.S)
    return re.compile("[^/]*".join(re.escape(piece) for piece in entry.split("*")))


def run(snapshot, config):
    machinery = config.get("machinery")
    if not isinstance(machinery, list) or not machinery or not all(isinstance(e, str) and e for e in machinery):
        return [finding("workspace.json", 1, f"direct_push needs \"machinery\", a list of paths; see {PAGE}")]
    patterns = [_pattern(entry) for entry in machinery]
    branch = config.get("branch", "main")
    found = []
    for commit in snapshot.pushed:
        hits = [path for path in commit.get("paths", []) if any(p.fullmatch(path) for p in patterns)]
        if hits:
            more = f" and {len(hits) - 1} more" if len(hits) > 1 else ""
            found.append(finding(hits[0], 1, f"commit {commit.get('commit', '')[:7]} \"{commit.get('subject', '')}\" "
                                             f"changes machinery ({hits[0]}{more}) and is pushed straight to {branch}. "
                                             f"Push it to its own branch and open a draft pull request, where CI runs "
                                             f"on three systems; see {PAGE}"))
        elif commit.get("anchors"):
            found.append(finding("docs", 1, f"commit {commit.get('commit', '')[:7]} \"{commit.get('subject', '')}\" "
                                            f"adds or changes a proof anchor (a proven-by line) and is pushed straight "
                                            f"to {branch}. An anchor merges through a pull request, so its commit stays "
                                            f"reachable and CI compares the records; see "
                                            f"docs/decisions/0006-what-proven-means.md"))
    return found
