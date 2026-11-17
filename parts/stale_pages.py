"""Hook, at session start: list the pages past their review date.

The commit check fails only a stale page the commit edits, so the rest stay out of
sight until someone happens to edit one. This notice shows them when a session
starts, so the agent knows to review a page before it edits it. It reuses the
review-date check itself (config "part", default "freshness"), run by the runner on
the session's own working copy, so the notice and the gate never disagree. It lists
ten pages at most, then a count. It prints nothing when no page is stale.
"""
KIND = "hook"
EVENT = "session-start"
MODE = "remind"
NEEDS = ("findings",)
SHOWN = 10


def decide(event, config):
    findings = (event.get("findings") or {}).get(config.get("part", "freshness"), [])
    stale = sorted({f["path"] for f in findings if f.get("level") == "warning" and "days ago" in f.get("message", "")})
    if not stale:
        return None
    more = f"\n- and {len(stale) - SHOWN} more; python3 ws.py check lists them all" if len(stale) > SHOWN else ""
    return ("These pages are past their review date. If you edit one, review the whole page first and move "
            "its last-reviewed date; the commit check refuses the edit otherwise:\n"
            + "\n".join(f"- {page}" for page in stale[:SHOWN]) + more)
