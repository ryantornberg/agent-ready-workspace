"""Read what an agent tool sends a hook, and turn it into the event a hook part decides on.

Two shapes are read, and nothing else:

- The workspace's own shape, version 1, read when no tool is named:
      before-shell     {"version": 1, "command": "git add a.md"}
      before-edit      {"version": 1, "path": "docs/a.md"}      relative to the workspace, or absolute
      before-handoff   {"version": 1, "prompt": "Tier: worker ...", "model": "...", "effort": "..."}
      session-start    {"version": 1, "session": "an id", "cwd": "/absolute/folder"}
      session-end      the same
  A handoff gives "model" and "effort" only when its tool lets a task set them. No other key is allowed,
  so a misspelt field is refused instead of read as missing.
- A known agent tool's own payload, read by that tool's adapter: `ws.py hook <event> --tool claude-code`,
  or `--tool codex` for Codex CLI. With no --tool, a payload without "version" that is plainly Claude Code's is read by its adapter too, so
  a session still running wiring written before the adapters existed is not locked out by the upgrade.

Anything else is refused: a hook that cannot tell what is about to happen fails closed.

A reminder goes back the way the tool reads it: for Claude Code and Codex, as "additionalContext" in
their JSON reply, which the agent sees next to the command's result; for the workspace's own shape, as
plain text on standard output. Either way the call goes ahead.

One call can carry several edits. Codex edits through one patch tool, and one patch can add, change,
delete or move several files. Its adapter gives one before-edit event per path, a move's source and
destination both, and the runner refuses the whole call when any one of them is refused.

The event a part sees:
    before-shell     {"command": text}
    before-edit      {"path": text, "working_copy": text or None, "main": bool, "absolute": text}
                                      "path" is relative to the working copy of this repository that holds the
                                      file: the main one or a linked worktree, wherever that sits. A file in no
                                      working copy of it keeps its absolute path, and "working_copy" is None.
                                      Symbolic links are followed, and a differently cased path that names a
                                      working copy on a case-insensitive file system counts as inside it.
                                      See docs/decisions/0004-the-hook-contract.md.
    before-handoff   {"prompt": text} plus "model" and "effort" when the tool exposes them; None when unset.
    session-start    {"session": text, "cwd": absolute text, "tool": "claude-code", "codex" or None}
    session-end      the same. The runner adds the facts a session hook declares it needs (wslib/runner.py).
"""
import json
import os
import pathlib

from . import ledger as ledgers
from .parts import EVENTS, SESSION_EVENTS, PartError

VERSION = 1
FIELDS = {"before-shell": "command", "before-edit": "path", "before-handoff": "prompt"}
SESSION_NAMES = {"session-start": "SessionStart", "session-end": "SessionEnd"}
OPTIONAL = {"before-handoff": ("model", "effort")}

# Claude Code: which tool reaches which event, and the field that holds what the hook decides on.
# .claude/settings.json must send each of these tools to its event; a test holds the two together.
CLAUDE_CODE_TOOLS = {
    "before-shell": {"Bash": "command"},
    "before-edit": {"Edit": "file_path", "Write": "file_path", "MultiEdit": "file_path", "NotebookEdit": "notebook_path"},
    "before-handoff": {"Agent": "prompt", "Task": "prompt"},
}

# Codex CLI: the same, read from what codex-cli 0.169.0 sent in a recorded run (tests/records/codex-cli-run.json).
# Its patch tool sends the whole patch as "command"; the paths are read from the patch's file lines.
# .codex/hooks.json must send each of these tools to its event; a test holds the two together.
CODEX_TOOLS = {
    "before-shell": {"Bash": "command"},
    "before-edit": {"apply_patch": "command"},
    "before-handoff": {},
}
# Wired, and refused until a recorded run shows where the payload holds what the hook decides on.
CODEX_REFUSED = {"before-handoff": ("spawn_agent",)}
PATCH_FILE_LINES = ("*** Add File:", "*** Update File:", "*** Delete File:", "*** Move to:")


def _text(value, what):
    if not isinstance(value, str) or not value:
        raise PartError(f"{what} must be non-empty text")
    return value


def place(root, path, base=None):
    """A before-edit event's place fields for a path: see the module's docstring. Follows symbolic links.

    base: the folder a relative path starts from (default: root).
    """
    absolute = _resolve(root, path, base)
    own = ledgers.git_dir(pathlib.Path(root).resolve())
    found = ledgers.working_copy(absolute, ledgers.common_dir(own)) if own is not None else None
    if found is not None:
        top, folder = found
        within = _within(absolute, top)
        if within is not None:
            main = ledgers._same(folder, ledgers.common_dir(folder))
            return {"path": within, "working_copy": str(top), "main": main, "absolute": absolute.as_posix()}
    within = _within(absolute, pathlib.Path(root))
    if within is not None:     # a workspace that is not a git working copy: the folder is the working copy
        return {"path": within, "working_copy": str(root), "main": True, "absolute": absolute.as_posix()}
    return {"path": absolute.as_posix(), "working_copy": None, "main": False, "absolute": absolute.as_posix()}


def _within(absolute, top):
    """absolute's path relative to top, or None. On a case-insensitive file system, asks the file system."""
    try:
        return absolute.relative_to(top).as_posix()
    except ValueError:
        pass
    for ancestor in absolute.parents:
        try:
            if os.path.samefile(ancestor, top):
                return absolute.relative_to(ancestor).as_posix()
        except OSError:
            continue
    return None


def _resolve(root, path, base=None):
    """The absolute, link-free path, with .. removed. A file that does not exist yet resolves through its folders."""
    if "\0" in path:
        raise PartError(f"the path {path!r} holds a NUL character, which no file name can")
    try:
        candidate = pathlib.Path(path)
        if not candidate.is_absolute():
            candidate = pathlib.Path(base or root) / candidate
        return pathlib.Path(os.path.realpath(candidate))
    except (OSError, ValueError) as error:
        raise PartError(f"the path {path!r} cannot be placed: {error}")


def versioned(root, event, payload):
    """The workspace's own shape."""
    if not isinstance(payload, dict) or "version" not in payload:
        raise PartError('the event is not in the workspace\'s shape, {"version": 1, ...}, and no --tool names '
                        "an adapter for it")
    if type(payload["version"]) is not int or payload["version"] != VERSION:
        raise PartError(f"event version {payload['version']!r} is not one this runner reads; it reads {VERSION}")
    field = FIELDS.get(event)
    allowed = {"version", "session", "cwd"} if event in SESSION_EVENTS else {"version", field, *OPTIONAL.get(event, ())}
    if event == "before-edit":
        allowed |= {"session", "pid"}      # the writing-session lease's identity, for a tool with no adapter
    unknown = sorted(set(payload) - allowed)
    if unknown:
        raise PartError(f"a {event} event has no field {unknown[0]!r}; it takes {sorted(allowed)}")
    if event in SESSION_EVENTS:
        return session_event(payload, "session", None)
    value = _text(payload.get(field), f'a {event} event\'s "{field}"')
    if event == "before-edit":
        found = place(root, value)
        found["session"] = payload.get("session") if isinstance(payload.get("session"), str) else None
        found["pid"] = payload.get("pid") if type(payload.get("pid")) is int else None
        return found
    found = {field: value}
    for key in OPTIONAL.get(event, ()):
        if key in payload:
            found[key] = _text(payload[key], f'a {event} event\'s "{key}"')
    return found


def session_event(payload, key, tool):
    """{"session", "cwd", "tool"} from a session payload, whose session id is under key."""
    cwd = _text(payload.get("cwd"), 'a session event\'s "cwd"')
    if not pathlib.Path(cwd).is_absolute():
        raise PartError(f'a session event\'s "cwd" must be an absolute folder, not {cwd!r}')
    return {"session": _text(payload.get(key), f'a session event\'s "{key}"'), "cwd": cwd, "tool": tool}


def tool_session(tool, event, payload):
    """A Claude Code or Codex SessionStart or SessionEnd payload: {"hook_event_name", "session_id", "cwd", ...}."""
    if not isinstance(payload, dict) or payload.get("hook_event_name") != SESSION_NAMES[event]:
        raise PartError(f'this is not a {tool} {SESSION_NAMES[event]} payload: it needs '
                        f'"hook_event_name": "{SESSION_NAMES[event]}", a "session_id" and a "cwd"')
    return session_event(payload, "session_id", tool)


def _session(payload):
    value = payload.get("session_id")
    return value if isinstance(value, str) and value else None


def is_claude_code(payload):
    return is_tool_call(payload)


def claude_code(root, event, payload):
    """Claude Code's PreToolUse payload: {"hook_event_name": "PreToolUse", "tool_name", "tool_input", "cwd", ...}."""
    if event in SESSION_EVENTS:
        return tool_session("claude-code", event, payload)
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
        return dict(place(root, value, base), session=_session(payload), pid=None)
    found = {"prompt": value}
    for key in ("model", "effort"):   # the tool exposes both; an unset one is None, and inherits the caller's
        if given.get(key) is not None and not isinstance(given[key], str):
            raise PartError(f'the {tool} tool\'s "{key}" must be text')
        found[key] = given.get(key) or None
    return found


def patch_paths(text):
    """Every path a Codex patch names, in order: added, changed, deleted, and a move's destination.

    A file line is read with the spaces around it stripped, as a lenient patch reader would accept it, so an
    indented line cannot hide an edit. A patch that names no file is refused: it cannot be decided.
    """
    lines = text.splitlines()
    if not lines or lines[0].strip() != "*** Begin Patch":
        raise PartError('a Codex patch must start with "*** Begin Patch"')
    paths = []
    for line in lines[1:]:
        stripped = line.strip()
        for prefix in PATCH_FILE_LINES:
            if stripped.startswith(prefix):
                paths.append(_text(stripped[len(prefix):].strip(), f'the path on a Codex patch\'s "{prefix}" line'))
    if not paths:
        raise PartError("a Codex patch must name at least one file")
    return paths


def is_tool_call(payload):
    return (isinstance(payload, dict) and payload.get("hook_event_name") == "PreToolUse"
            and isinstance(payload.get("tool_name"), str) and isinstance(payload.get("tool_input"), dict))


def codex(root, event, payload):
    """Codex CLI's PreToolUse payload: {"hook_event_name": "PreToolUse", "tool_name", "tool_input", "cwd", ...}.

    Returns a list of events: one for a shell command, one per path for a patch.
    """
    if event in SESSION_EVENTS:
        return tool_session("codex", event, payload)
    if not is_tool_call(payload):
        raise PartError('this is not a Codex PreToolUse payload: it needs "hook_event_name": "PreToolUse", '
                        'a "tool_name" and a "tool_input" object')
    tool, given = payload["tool_name"], payload["tool_input"]
    if tool in CODEX_REFUSED.get(event, ()):
        raise PartError(f"Codex's {tool} tool starts a subagent, and no recorded run yet shows where its payload holds "
                        "the task's prompt, so its tier cannot be checked. Refused until the adapter reads it")
    fields = CODEX_TOOLS[event]
    if tool not in fields:
        raise PartError(f"Codex sent the {tool} tool to the {event} hook, which reads only {sorted(fields)}. "
                        "The wiring and the adapter disagree")
    value = _text(given.get(fields[tool]), f'the {tool} tool\'s "{fields[tool]}"')
    if event == "before-shell":
        return [{"command": value}]
    paths = patch_paths(value)
    base = payload.get("cwd")
    if not (isinstance(base, str) and pathlib.Path(base).is_absolute()):
        if not all(pathlib.PurePosixPath(p).is_absolute() or pathlib.Path(p).is_absolute() for p in paths):
            raise PartError(f"the {tool} tool gave a relative path and no absolute \"cwd\" to place it from")
        base = None
    return [dict(place(root, p, base), session=_session(payload), pid=None) for p in paths]


ADAPTERS = {"claude-code": claude_code, "codex": codex}


def read(root, event, data, tool=None):
    """The events a part decides on, from the raw bytes or text a tool sent. Raises PartError on anything else.

    A list: one event, or one per path when a single call edits several files.
    """
    return read_call(root, event, data, tool)[0]


def read_call(root, event, data, tool=None):
    """(events, tool, cwd): the events, the adapter that read them (None for the workspace's shape), and the
    folder the tool says the session runs in (None when it does not say)."""
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
    found = (ADAPTERS[tool] if tool else versioned)(root, event, payload)
    found = found if isinstance(found, list) else [found]
    cwd = payload.get("cwd") if tool else None
    return found, tool, cwd if isinstance(cwd, str) and pathlib.Path(cwd).is_absolute() else None


def remind(tool, text, event="before-shell"):
    """What to print on standard output so the tool shows the agent a reminder and lets the call go ahead."""
    if tool in ("claude-code", "codex"):   # Codex reads the same reply; it ignores plain text from this hook
        name = SESSION_NAMES.get(event, "PreToolUse")
        return json.dumps({"hookSpecificOutput": {"hookEventName": name, "additionalContext": text}})
    return f"Reminder: {text}"
