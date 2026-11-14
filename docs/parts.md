---
last-reviewed: 2026-11-14
---

# Parts

How the checks and hooks plug in, and how to add one. It is for anyone extending the workspace.

**In short:** a part is one Python file plus a file of cases. The manifest lists the parts a workspace uses. The runner refuses a part that has no cases.

## The pieces

| Piece | File | Job |
|---|---|---|
| Manifest | `workspace.json` | Lists the parts this workspace uses, each with its settings. |
| Runner | `ws.py` | Loads the parts, gives each check a snapshot of the files, and gives each hook its event. |
| Part | `parts/<name>.py` | One check or one hook. |
| Cases | `parts/<name>.cases.json` | The part's own tests, as data. |

## A check

A check gets a snapshot and returns findings.

```python
from wslib.parts import finding

KIND = "check"


def run(snapshot, config):
    return [finding(path, 1, "this page is empty")
            for path in snapshot.paths(suffixes=(".md",))
            if not (snapshot.read(path) or "").strip()]
```

The snapshot is the only way a check reads files. That is what lets one check run three ways without knowing which:

| Command | The snapshot holds |
|---|---|
| `python3 ws.py check` | The working folder. |
| `python3 ws.py check --staged` | Exactly what is staged. This is the commit hook. |
| A case | The files written in the case. |

A finding is an error unless it says `level="warning"`. An error fails the commit.

## A hook

A hook gets one event and returns `None` to allow it, or the reason to refuse.

```python
KIND = "hook"
EVENT = "before-shell"


def decide(event, config):
    if "rm -rf /" in (event.get("command") or ""):
        return "that deletes everything"
    return None
```

`before-shell` events carry a `command`. `before-edit` events carry a `path`, relative to the workspace. `python3 ws.py hook <event>` reads the event as JSON and exits 2 when a hook refuses. [.claude/settings.json](../.claude/settings.json) wires both events into one agent tool; another tool needs its own few lines of wiring, and the parts stay the same.

## Cases

A check case gives files and the findings to expect. Every finding the check returns must be expected, so a case also proves what the check leaves alone.

```json
{"name": "an empty page fails", "files": {"a.md": "", "b.md": "# B"}, "expect": ["this page is empty"]}
```

A hook case gives an event and the answer.

```json
{"name": "plain listing is allowed", "event": {"command": "ls"}, "allow": true}
```

The runner refuses to load:

- a part with no cases file;
- a check with no case in which it finds something;
- a hook whose cases do not show it both allowing and refusing.

A rule written only in prose gets broken, and a check nobody tests stops checking. `python3 ws.py selftest` runs every case.

## Adding a part

1. Write `parts/<name>.py` and `parts/<name>.cases.json`.
2. Add `{"use": "<name>"}` to `workspace.json`, with any settings the part reads from `config`.
3. Run `python3 ws.py selftest`, then `python3 ws.py check`.

To use a part kept somewhere else, give its path: `{"use": "shared/parts/licences.py"}`. Its cases file sits next to it.

## The parts here

| Part | Kind | Fails or refuses when |
|---|---|---|
| `links` | check | A link points at a missing file or heading. |
| `freshness` | check | A commit edits a page that is past its review date. |
| `aliases` | check | The index maps a phrase to a name the code no longer defines. |
| `eval_record` | check | A playbook changed since its last passing eval run. |
| `no_stage_all` | hook, before-shell | A command stages everything instead of naming files. |
| `shelved` | hook, before-edit | An edit touches a folder marked read-only. |
