"""The before-edit hook: refuse an edit inside the shelved folder.

The agent tool sends the planned edit as JSON on standard input. Exit 0 allows it; exit 2 refuses it, and what
the hook prints to standard error is shown to the agent.
"""
import json
import sys

SHELVED = "src/orders-service-v1"
EDIT_TOOLS = ("Edit", "Write")


def decide(payload):
    """None to allow the edit, or the reason to refuse it."""
    if payload.get("tool_name") not in EDIT_TOOLS:
        return None
    path = payload.get("tool_input", {}).get("file_path", "")
    if path == SHELVED or path.startswith(SHELVED + "/"):
        return f"{path} is in the shelved folder {SHELVED}, which is kept read-only"
    return None


def main(text):
    """The exit code for one payload."""
    try:
        payload = json.loads(text)
    except ValueError:
        return 0
    reason = decide(payload) if isinstance(payload, dict) else None
    if reason:
        print(reason, file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.stdin.read()))
