"""Hook, at session start: show the pending handoff note of the session's working copy.

A session that stops mid-task writes a handoff note and runs `python3 ws.py handoff NOTE`, which leaves a marker
keyed by the branch in the working copy's git folder (wslib/handoff.py). The runner gives this hook the "handoffs"
fact: the markers of the working copy the session runs in that are still pending, since their branch has not
merged and nobody ran `python3 ws.py handoff --done`. With one, the note is shown; with two or more, none is shown
and the markers are listed, since only the person knows which to resume. With none, nothing is said. A session
starts before anyone says what it is for, so the notice tells the agent to resume only when the person's request
is to resume that work, and otherwise to mention the note once. See docs/playbooks/handoff.md.
"""
KIND = "hook"
PAGE = "docs/playbooks/handoff.md#the-marker-and-the-loader"   # the rule's page, which every finding names
EVENT = "session-start"
MODE = "remind"
NEEDS = ("handoffs",)


def decide(event, config):
    found = [m for m in event.get("handoffs") or [] if isinstance(m, dict) and m.get("branch") and m.get("note")]
    if not found:
        return None
    if len(found) > 1:
        listed = "\n".join(f"- {m['branch']}: {m['note']} (written {m.get('written')})" for m in found)
        return (f"{len(found)} handoff notes are pending in this working copy, so none is shown:\n{listed}\n"
                "When the person's request is to resume work, ask which of these to resume, then read that note and "
                "follow the handoff page's \"Resuming\". For any other request, do what was asked, and tell the person "
                "once that these notes are pending. Clear a note whose work is done, from this working copy, with: "
                "python3 ws.py handoff --done BRANCH")
    marker = found[0]
    head = (f"A handoff note is pending for the branch {marker['branch']} in this working copy: {marker['note']}, "
            f"written {marker.get('written')}. When the person's request is to resume this work, follow the handoff "
            "page's \"Resuming\", which checks the note against the working copy first. For any other request, do "
            "what was asked, and tell the person once that this note is pending. When its work is done or the person "
            f"drops it, clear it, from this working copy, with: python3 ws.py handoff --done {marker['branch']}")
    if not isinstance(marker.get("text"), str):
        return f"{head}\nThe note cannot be read at that path. Ask the person where it is; do not guess its content."
    cut = "\n[The note is longer than this; read the rest in the file.]" if marker.get("cut") else ""
    return f"{head}\n\n{marker['text'].rstrip()}{cut}\n\n[The end of the handoff note.]"
