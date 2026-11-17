"""Hook, at session start: warn when a pinned repository is behind its upstream.

A session can start work on an old pin without knowing. For each pinned repository
in the session's working copy, the runner fetches its upstream's default branch,
with a time limit and no prompts, and counts the commits the checkout lacks. This
notice names each one that is behind. A repository that is not checked out, an
upstream that cannot be reached, or anything else that goes wrong prints nothing:
it is a heads-up, never a gate. See docs/decisions/0001-pin-code-repositories.md.
"""
KIND = "hook"
EVENT = "session-start"
MODE = "remind"
NEEDS = ("pins",)


def decide(event, config):
    behind = [p for p in event.get("pins") or [] if isinstance(p.get("behind"), int) and p["behind"] > 0]
    if not behind:
        return None
    return "\n".join(f"{p['path']} is {p['behind']} commit{'s' if p['behind'] != 1 else ''} behind its upstream's "
                     f"{p['branch']}. Move the pin before you build on it, or say why it stays."
                     for p in behind)
