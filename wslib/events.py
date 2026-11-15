"""Read what an agent tool sends a hook, and turn it into the event a hook part decides on.

Two shapes are read, and nothing else:

- The workspace's own shape, version 1, read when no tool is named:
      before-shell     {"version": 1, "command": "git add a.md"}
      before-edit      {"version": 1, "path": "docs/a.md"}      relative to the workspace, or absolute
      before-handoff   {"version": 1, "prompt": "Tier: worker ...", "model": "...", "effort": "..."}
  A handoff gives "model" and "effort" only when its tool lets a task set them. No other key is allowed,
  so a misspelt field is refused instead of read as missing.
- A known agent tool's own payload, read by that tool's adapter: `ws.py hook <event> --tool claude-code`.
  With no --tool, a payload without "version" that is plainly Claude Code's is read by its adapter too, so
  a session still running wiring written before the adapters existed is not locked out by the upgrade.

Anything else is refused: a hook that cannot tell what is about to happen fails closed.

The event a part sees:
    before-shell     {"command": text}
    before-edit      {"path": text}   relative to the workspace when the file is inside it, else absolute.
                                      Symbolic links are followed, and a differently cased path that names
                                      the workspace on a case-insensitive file system counts as inside it.
    before-handoff   {"prompt": text} plus "model" and "effort" when the tool exposes them; None when unset.
"""
import json
import os
import pathlib

from .parts import EVENTS, PartError

VERSION = 1
FIELDS = {"before-shell": "command", "before-edit": "path", "before-handoff": "prompt"}
OPTIONAL = {"before-handoff": ("model", "effort")}

# Claude Code: which tool reaches which event, and the field that holds what the hook decides on.
# .claude/settings.json must send each of these tools to its event; a test holds the two together.
CLAUDE_CODE_TOOLS = {
    "before-shell": {"Bash": "command"},
    "before-edit": {"Edit": "file_path", "Write": "file_path", "MultiEdit": "file_path", "NotebookEdit": "notebook_path"},
    "before-handoff": {"Agent": "prompt", "Task": "prompt"},
}


def _text(value, what):
    if not isinstance(value, str) or not value:
        raise PartError(f"{what} must be non-empty text")
    return value


def place(root, path, base=None):
    """A path as the parts compare it: relative to root when it is inside, else absolute. Follows symbolic links.

    base: the folder a relative path starts from (default: root).
    """
    if "\0" in path:
        raise PartError(f"the path {path!r} holds a NUL character, which no file name can")
    try:
        candidate = pathlib.Path(path)
        if not candidate.is_absolute():
            candidate = pathlib.Path(base or root) / candidate
        resolved = pathlib.Path(os.path.realpath(candidate))
        try:
            return resolved.relative_to(root).as_posix()
        except ValueError:
            pass
        # On a case-insensitive file system /USERS/ME/ws is the workspace too: ask the file system, not the text.
        for ancestor in resolved.parents:
            try:
                if os.path.samefile(ancestor, root):
                    return resolved.relative_to(ancestor).as_posix()
            except OSError:
                continue
        return resolved.as_posix()
    except (OSError, ValueError) as error:
        raise PartError(f"the path {path!r} cannot be placed: {error}")


def versioned(root, event, payload):
    """The workspace's own shape."""
    if not isinstance(payload, dict) or "version" not in payload:
        raise PartError('the event is not in the workspace\'s shape, {"version": 1, ...}, and no --tool names '
                        "an adapter for it")
    if type(payload["version"]) is not int or payload["version"] != VERSION:
        raise PartError(f"event version {payload['version']!r} is not one this runner reads; it reads {VERSION}")
    field = FIELDS[event]
    allowed = {"version", field, *OPTIONAL.get(event, ())}
    unknown = sorted(set(payload) - allowed)
    if unknown:
        raise PartError(f"a {event} event has no field {unknown[0]!r}; it takes {sorted(allowed)}")
    value = _text(payload.get(field), f'a {event} event\'s "{field}"')
    if event == "before-edit":
        return {"path": place(root, value)}
    found = {field: value}
    for key in OPTIONAL.get(event, ()):
        if key in payload:
            found[key] = _text(payload[key], f'a {event} event\'s "{key}"')
    return found


def is_claude_code(payload):
    return (isinstance(payload, dict) and payload.get("hook_event_name") == "PreToolUse"
            and isinstance(payload.get("tool_name"), str) and isinstance(payload.get("tool_input"), dict))


def claude_code(root, event, payload):
    """Claude Code's PreToolUse payload: {"hook_event_name": "PreToolUse", "tool_name", "tool_input", "cwd", ...}."""
    if not is_claude_code(payload):
        raise PartError('this is not a Claude Code PreToolUse payload: it needs "hook_event_name": "PreToolUse", '
                        'a "tool_name" and a "tool_input" object')
    tool, given = payload["tool_name"], payload["tool_input"]
    fields = CLAUDE_CODE_TOOLS[event]
    if tool not in fields:
        raise PartError(f"Claude Code sent the {tool} tool to the {event} hook, which reads only {sorted(fields)}. "
                        "The wiring and the adapter disagree")
    value = _text(given.get(fields[tool]), f'the {tool} tool\'s "{fields[tool]}"')
    if event == "before-shell":
        return {"command": value}
    if event == "before-edit":
        base = payload.get("cwd")
        if not pathlib.Path(value).is_absolute() and not (isinstance(base, str) and pathlib.Path(base).is_absolute()):
            raise PartError(f"the {tool} tool gave a relative path and no absolute \"cwd\" to place it from")
        return {"path": place(root, value, base)}
    found = {"prompt": value}
    for key in ("model", "effort"):   # the tool exposes both; an unset one is None, and inherits the caller's
        if given.get(key) is not None and not isinstance(given[key], str):
            raise PartError(f'the {tool} tool\'s "{key}" must be text')
        found[key] = given.get(key) or None
    return found


ADAPTERS = {"claude-code": claude_code}


def read(root, event, data, tool=None):
    """The event a part decides on, from the raw bytes or text a tool sent. Raises PartError on anything else."""
    if event not in EVENTS:
        raise PartError(f"unknown event {event!r}; the events are {EVENTS}")
    if tool is not None and tool not in ADAPTERS:
        raise PartError(f"no adapter for the tool {tool!r}; the adapters are {sorted(ADAPTERS)}")
    if isinstance(data, bytes):
        try:
            data = data.decode("utf-8-sig")
        except UnicodeDecodeError as error:
            raise PartError(f"hook input is not UTF-8 text: {error}")
    try:
        payload = json.loads(data)
    except (json.JSONDecodeError, RecursionError) as error:
        raise PartError(f"hook input is not JSON: {type(error).__name__}")
    if tool is None and not (isinstance(payload, dict) and "version" in payload) and is_claude_code(payload):
        tool = "claude-code"
    return (ADAPTERS[tool] if tool else versioned)(root, event, payload)
