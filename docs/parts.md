---
last-reviewed: 2026-11-15
---

# Parts

How the checks and hooks plug in, and how to add one. It is for anyone extending the workspace.

**In short:** a part is one Python file plus a file of cases. The manifest lists the parts a workspace uses. The runner runs a part's cases every time it loads the part, and refuses a part with no cases or a failing one.

## The pieces

| Piece | File | Job |
|---|---|---|
| Manifest | `workspace.json` | Lists the parts this workspace uses, each with its settings. |
| Runner | `ws.py`, which starts `wslib/runner.py` | Loads the parts, gives each check a snapshot of the files, and gives each hook its event. |
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

Both commands start from one git listing, so they see the same files. A tracked or staged file is always in it, wherever it sits, and the `.git` entry never is. `check` adds the untracked files that git does not ignore. A folder that is not the top of a git working copy is walked instead. `check --staged` reads every staged file in one batch: three git processes in all, however many files there are.

What a check can ask the snapshot:

| Call | Gives |
|---|---|
| `paths(suffixes, under, skip)` | Every file path, sorted. |
| `pages(suffixes, skip)` | The pages the workspace owns: no symbolic link, and nothing inside a code repository under the workspace, such as a submodule in `src/`. The page checks use it. |
| `read(path)` | The text, or `None` when the file is not UTF-8 text. |
| `not_utf8(path)` | Why `read` gave `None`, such as "is Windows-1252, not UTF-8", to start a finding with. |
| `read_text(path)` | The text in whatever encoding it is in: UTF-8, UTF-16, or Windows-1252. For reading code. |
| `read_bytes(path)` | The bytes. A symbolic link reads as its target path, as git stores it. |

A finding is an error unless it says `level="warning"`. An error fails the commit.

A check runs in phases. By default it runs at the commit and in CI. A check that sets `PHASES` names its own, from `"commit"`, `"ci"` and `"nightly"`:

| Command | Runs the checks whose phases hold |
|---|---|
| `python3 ws.py check`, `python3 ws.py check --staged` | `commit`. It is the default, so the two agree. |
| `python3 ws.py check --phase ci` | `ci`. CI runs it. |
| `python3 ws.py check --phase nightly` | `nightly`. CI's weekly run runs it, for checks too slow for every commit. |

The phases are the part's, not the manifest's, so no manifest edit can move `deny_list` off the commit. `selftest` runs every part's cases, whatever its phases.

A check that sets `COMMIT_MESSAGE = True` also runs from the commit-msg hook, `python3 ws.py check --message FILE`. Its snapshot then holds three files: `commit message`, `author` and `committer`, each identity as git will record it. `deny_list` is the one here.

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

There are three events. The event a hook's `decide` gets:

| Event | Fires | The event holds |
|---|---|---|
| `before-shell` | Before a shell command | `command`: the command line |
| `before-edit` | Before an edit tool writes a file | `path`: relative to the workspace when the file is inside it, else absolute |
| `before-handoff` | Before a task is handed to a helper session | `prompt`; and `model` and `effort` when the tool lets a task set them, `None` when left unset |

`python3 ws.py hook <event>` reads the event as JSON on standard input and exits 2 when a hook refuses. It reads two shapes, and refuses everything else:

- **The workspace's own shape**, with a version: `{"version": 1, "command": "git add a.md"}`, `{"version": 1, "path": "docs/a.md"}`, or `{"version": 1, "prompt": "Tier: worker ..."}`. It takes exactly the fields in the table, so a misspelt field is refused, not read as missing.
- **An agent tool's own payload**, read by that tool's adapter in `wslib/events.py`: `python3 ws.py hook before-edit --tool claude-code`, or `--tool codex`. A payload without the field its tool needs, or from a tool the adapter does not send to that event, is refused. With no `--tool`, a payload that is plainly Claude Code's is read by its adapter too. An agent tool keeps the hook wiring a session started with, so a running session with the older wiring is not locked out when the runner is upgraded under it.

So a hook fails closed: whatever the runner cannot read, it refuses.

One call can carry several edits. Codex's patch tool can add, change, delete or move several files at once, so its adapter gives one `before-edit` event per path, a move's source and destination both. The runner refuses the whole call when any one of them is refused, and records the paths only when all are allowed.

A hook that sets `MODE = "remind"` never refuses. When its `decide` returns a reason, the call goes ahead and the agent is shown the reason as a reminder: through the agent tool's `additionalContext`, next to the command's result, for Claude Code and Codex, or as plain text on standard output for the workspace's own shape. Use it where the real check comes later, as `no_stage_all` does before the commit. Before a part sees a path, the runner follows symbolic links, and on a case-insensitive file system it treats a differently cased path to the workspace as inside it.

[.claude/settings.json](../.claude/settings.json) wires the three events into Claude Code, and [.codex/hooks.json](../.codex/hooks.json) into Codex CLI, which gives a hook no variable naming the project, so its lines find `wslib/launch.sh` from the top of the git repository. Each line calls `wslib/launch.sh`, which runs `ws.py` with the first Python 3.9 or later it finds and exits 2 when there is none, and ends in `|| exit 2`, so a missing launcher refuses too. An agent tool blocks a call only on exit 2; anything else lets it through. Codex also lets a call through when its hook times out, so its wiring sets a 30-second limit. Another tool needs an adapter and its own few lines of wiring, and the parts stay the same.

A hook call loads only the hooks for its event. It does not run any check, or any hook for the other event. So a check with a broken case cannot refuse a shell command or an edit, including the edit that repairs it. To know a part's kind without running it, the runner reads its `KIND` and `EVENT` lines. Write each as one plain line, such as `KIND = "hook"`. A part whose lines it cannot read refuses every hook call, because it might be a hook for that event. So does a missing part file, and a manifest it cannot read. Repair those from your own terminal, where the agent's hooks do not run. A hook call does not compare those lines with what the file sets when it runs; `check`, `selftest` and CI do, and refuse a part where they differ.

## The edit ledger

Each `before-edit` call that every hook allows is recorded: the runner appends the path to the edit ledger of the working copy that holds the file. The ledger is the file `ws-ledger` in that working copy's git folder, so a linked working copy keeps its own. An edit in a code repository under `src/` goes in the workspace's ledger. An edit outside every working copy of this repository is not recorded. If the ledger cannot be written, the edit is refused.

While a ledger is open, the `edit_ledger` check fails a commit that stages a path no edit tool wrote, whatever command staged it. A `before-shell` reminder opens the ledger too, even empty, in the working copy where the agent tool says its session runs, when that working copy has uncommitted changes. So a session that wrote its files only through the shell is still compared, and a command run in a scratch repository while the session's own working copy is clean opens nothing. The workspace's own event shape names no folder, so trying the hook by hand opens nothing.

| Command | Does |
|---|---|
| `python3 ws.py ledger` | Says whether the ledger is open, and lists its paths. |
| `python3 ws.py ledger --add PATH ...` | Records files this session wrote another way, such as with a shell command or a generator. |
| `python3 ws.py ledger --close` | Closes it, for a person's own commit. |
| `python3 ws.py ledger --committed` | Drops the last commit's paths, and closes the ledger when none are left. The post-commit hook runs it. |

[Decision 0002](decisions/0002-hooks-remind-the-commit-enforces.md) says why staging is checked at the commit.

## Cases

A check case gives files and the findings to expect. Every finding the check returns must be expected, so a case also proves what the check leaves alone.

```json
{"name": "an empty page fails", "files": {"a.md": "", "b.md": "# B"}, "expect": ["this page is empty"]}
```

An expectation written as text is an error. A warning is expected by saying so, as `{"message": "...", "level": "warning"}`. So a check whose errors are demoted to warnings fails its own cases, and cannot quietly stop failing commits.

A check that reads the commit's state takes it from the case: `"staged"` lists every staged path, deletions included (default: `"changed"`); `"ledger"` lists the edit ledger's paths, and leaving it out means no ledger is open; `"replaying"` names a merge or rebase in progress. `"repositories"` names folders that are code repositories, and `"symlinks"` names files that are symbolic links.

A case runs with the settings in its own `config`, never with the manifest's. Changing a setting in the manifest therefore cannot fail a part's cases.

A hook case gives an event and the answer.

```json
{"name": "plain listing is allowed", "event": {"command": "ls"}, "allow": true}
```

A hook with `MODE = "remind"` states `"remind": true` or `"remind": false` instead of `"allow"`.

The runner refuses to load:

- a part with no cases file;
- a check with no case in which it finds something;
- a hook whose cases do not show it both allowing and refusing, or, for a reminder, both reminding and staying quiet;
- a hook whose `MODE` is neither `"refuse"` nor `"remind"`;
- a hook whose `EVENT` is not one the runner knows;
- a part whose `KIND` or `EVENT` line is missing, repeated, or differs from what the file sets when it runs;
- a part whose file is outside the workspace, through `..`, an absolute path or a symbolic link;
- any part with a case that fails.

A rule written only in prose gets broken, and a check nobody tests stops checking. The cases run on every command that loads the part, so a part cannot quietly stop working between commits. `python3 ws.py selftest` runs them all and lists each failure, where the other commands stop at the first.

The commit check, `check --staged`, reads the staged manifest, the staged parts and their staged cases. An edit you have not staged cannot change its result.

## Removing a part

A part the last commit's manifest uses must stay in the manifest, or be listed under `retired` with the reason:

```json
"retired": [{"use": "no_stage_all", "why": "the commit check now compares staged paths with the session's edits"}]
```

Otherwise `check` fails. Locally, the last commit's manifest decides which parts are required. In CI, the manifest on the base branch decides. Only the `use` names are read from that older manifest, so keys added to the manifest later do not break the comparison. When CI has no base commit, as on a first push, no part is required, and it says so as a warning.

## The manifest

`workspace.json` holds four keys, and the runner refuses any other:

| Key | Holds |
|---|---|
| `version` | The engine version it was written for. It must equal `python3 ws.py --version`. |
| `tiers` | The [tier binding](orchestration.md): `driver`, `worker` and `mechanical`, each with a `model` and an `effort`. Optional; without it, `handoff_tier` refuses every task. |
| `parts` | The parts in use, each with a `use`, a `why` and its settings. |
| `retired` | Parts no longer used, each with a `use` and a `why`. |

The `why` says in a sentence what the part guards against here, so a reader can tell whether it still earns its place. A part does not see it.

A hook call checks only what its answer depends on: the version, the parts and the tier binding. A manifest it cannot read, or one written for another engine version, refuses every hook call. A missing `why` or an unknown key fails `list`, `selftest`, `check` and the commit, and does not refuse a hook call, so a half-finished entry cannot lock the session out. Upgrade the engine and the manifest's `version` in one step; [decision 0003](decisions/0003-the-engine-in-one-folder.md) says why.

## Adding a part

1. Write `parts/<name>.py` and `parts/<name>.cases.json`.
2. Add `{"use": "<name>", "why": "<what it guards against>"}` to `workspace.json`, with any settings the part reads from `config`.
3. Run `python3 ws.py selftest`, then `python3 ws.py check`.

A part's `config` is its manifest entry without `use` and `why`, plus the manifest's tier binding as `tiers`. The binding lives in one place, so an entry that sets `tiers` itself is refused.

To use a part kept somewhere else, give its path: `{"use": "shared/parts/licences.py", "why": "..."}`. Its cases file sits next to it.

## The parts here

| Part | Kind | Fails or refuses when |
|---|---|---|
| `links` | check | A link points at a missing file or heading, or a line is too long to read: over 10,000 characters. |
| `freshness` | check | A commit edits a page that is past its review date, a required page has no date, or a date is more than a day ahead of today in UTC. |
| `aliases` | check | The index maps a phrase to a name the code no longer defines, or a contract page names one in backticks. |
| `eval_record` | check | A playbook, its guidance or its eval case changed since the last passing eval run, or a playbook has no case. |
| `deny_list` | check | A file or file name holds a term from a private list kept outside the repository, and so, from the commit-msg hook, does the commit message, the author or the committer. With no list it warns and checks nothing, so CI cannot run it. |
| `edit_ledger` | check | While the edit ledger is open, a commit stages a path that no edit tool of the agent session wrote. |
| `no_stage_all` | hook, before-shell, reminds | Reminds, and never refuses, when a command stages everything instead of naming files. |
| `shelved` | hook, before-edit | An edit tool touches a folder marked read-only. |
| `handoff_tier` | hook, before-handoff | A delegated task names no tier on its first line, or sets a model or effort other than the manifest's binding for its tier, or leaves one unset that the tool lets it set. |
