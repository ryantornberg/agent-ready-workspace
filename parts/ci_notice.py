"""Hook, at session start: say when the newest CI run on main failed.

A red run on main alerts nobody unless something tells each session, and sessions go on pushing onto it. The
runner reads the newest CI runs on the default branch with gh (wslib/ci.py) and gives this hook the "ci" fact:
how many runs in a row failed, when the first of them ran, the steps that failed in the newest, and its link. A
passing run says nothing. So does every error, such as no gh, no sign-in, no network or the time limit: it is a
heads-up, never a gate. See docs/parts.md#the-parts-here.
"""
KIND = "hook"
PAGE = "docs/parts.md#the-parts-here"   # the rule's page, which every finding names (criterion 34)
EVENT = "session-start"
MODE = "remind"
NEEDS = ("ci",)


def decide(event, config):
    ci = event.get("ci")
    if not isinstance(ci, dict) or not isinstance(ci.get("failed"), int) or ci["failed"] < 1:
        return None
    count = ci["failed"]
    runs = f"{'at least ' if ci.get('at_least') else ''}{count} run{'s' if count != 1 else ''} in a row"
    workflow = config.get("workflow", "ci.yml")
    branch = config.get("branch", "main")
    steps = [step for step in ci.get("steps") or [] if isinstance(step, str)]
    failing = ("Failing steps in the newest: " + "; ".join(steps) + ".") if steps else \
        "gh named no failing step in the newest."
    title = f" ({ci['title']})" if ci.get("title") else ""
    return (f"CI is red on {branch}: {runs} of {workflow} failed, the first started at {ci.get('since')}. "
            f"{failing} Newest run{title}: {ci.get('url')}. Work built on {branch} now starts from a failing state: "
            f"tell the person, and do not merge or push to {branch} as if CI were green.")
