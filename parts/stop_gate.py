"""Hook: when a session that edited files tries to finish, refuse once while the check or the fast tests fail.

The runner looks up the session's own entries in the edit ledger of every working copy of this repository (the
"own_edits" fact). With none, this hook allows the stop and nothing runs: the "gate" fact is worked out only when
read. With some, the runner runs `python3 ws.py check` and the fast tests this part's config names in "tests", in
each working copy that holds the session's entries, within 20 seconds in all (the "gate" fact, decision 0004).
A run that fails, runs out of time or cannot start refuses the stop, with what it printed.

The runner lets a stop hook refuse once: on the stop that follows a refusal, which both agent tools mark with
"stop_hook_active", the reason is shown to the person as a report and the session stops. So a failure the agent
cannot fix does not trap it.

The gate sees only edits made through the edit tools, which the ledger records with their session. A file
written through the shell, or recorded with `ws.py ledger --add`, carries no session, and a commit removes its
paths from the ledger, so after a commit the gate has nothing of this session's to judge.

Config: "tests", the unittest module names of the fast tests, such as ["tests.test_cases_bite"].
"""
KIND = "hook"
EVENT = "stop"
NEEDS = ("own_edits", "gate")
PAGE = "docs/decisions/0005-concurrent-sessions-and-the-edit-ledger.md"
SHOWN = 5             # edited paths named in the reason
OUTPUT = 1500         # characters of each failing run's output in the reason


def decide(event, config):
    edits = event.get("own_edits") or []
    if not edits:
        return None
    runs = event.get("gate")
    if not isinstance(runs, list):
        return "the stop gate could not run the check and the tests. Run python3 ws.py check yourself before you finish."
    failed = [run for run in runs if run.get("status") != "passed"]
    if not failed:
        return None
    paths = [path for edit in edits for path in edit.get("paths", [])]
    shown = ", ".join(paths[:SHOWN]) + (f" and {len(paths) - SHOWN} more" if len(paths) > SHOWN else "")
    lines = [f"this session edited {shown}, and the stop gate found a problem before you finish."]
    for run in failed:
        status = run.get("status")
        what = {"failed": "failed", "timed-out": "ran out of the stop gate's 20 seconds",
                "error": "could not start"}.get(status, "did not pass")
        output = (run.get("output") or "").strip()
        if len(output) > OUTPUT:
            output = "..." + output[-OUTPUT:]
        lines.append(f"`{run.get('command')}` in {run.get('working_copy')} {what}" + (f":\n{output}" if output else "."))
    lines.append("Fix it and run the command again, or say in your report why it stays failing; "
                 "the next stop goes ahead.")
    return "\n".join(lines)
