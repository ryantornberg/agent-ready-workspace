"""Check: a staged pin is on its upstream's default branch.

A pin that points at a working-branch commit the upstream never merged cannot be
checked out by anyone else, and no other gate notices. For each pinned repository
whose pin the commit adds or moves, the engine fetches the upstream's default branch
and asks whether the pin is on it (wslib/gitcall.py). The pin is read from what is
staged, never from the checkout.

"Reachable" means that fetch worked within its time limit. An upstream that cannot
be reached warns and passes, at the commit and in CI: someone who cannot reach a
repository is never stopped by it. So does a repository that is not checked out, or
one whose default branch is not known. A pin on a reachable upstream whose default
branch lacks it fails.

A trap it names: a commit of named paths that includes a pinned folder, such as
`git commit src/lib -m ...`, records that folder's checked-out commit, not a pin
staged by hand. A checkout on a side branch then lands as the pin.
See docs/decisions/0001-pin-code-repositories.md.
"""
from wslib.parts import finding

KIND = "check"
PAGE = "docs/decisions/0001-pin-code-repositories.md"


def run(snapshot, config):
    found = []
    for fact in snapshot.pin_facts():
        path, pin, branch = fact.get("path"), fact.get("pin") or "", fact.get("branch")
        state = fact.get("state")
        if state == "off":
            trap = (" Its checkout's HEAD is that same commit: a commit of named paths that includes the folder "
                    "records the checkout, not a pin staged by hand." if fact.get("head") == pin else "")
            found.append(finding(path, 1, f"the pin {pin[:7]} of {path} is not on its upstream's default branch, "
                                          f"{branch}, so nobody else can check it out. Stage a commit that is on "
                                          f"{branch}.{trap} See {PAGE}"))
        elif state == "unreachable":
            found.append(finding(path, 1, f"the upstream of {path} cannot be reached, so its pin {pin[:7]} was not "
                                          f"checked against {branch}", level="warning"))
        elif state == "absent":
            found.append(finding(path, 1, f"{path} is not checked out, so its pin {pin[:7]} was not checked",
                                 level="warning"))
        elif state == "no-branch":
            found.append(finding(path, 1, f"no default branch is known for {path}'s upstream, so its pin "
                                          f"{pin[:7]} was not checked", level="warning"))
    return found
