---
kind: how-to
proof: unproven
prove-by: M4
last-reviewed: 2026-11-18
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

Both commands start from one git listing, so they see the same files. A tracked or staged file is always in it, wherever it sits, and the `.git` entry never is. `check` adds the untracked files that git does not ignore. A folder that is not the top of a git working copy is walked instead. `check --staged` reads every staged file in one batch: three git processes, however many files there are, plus at most two for the history the proof checks read (decision record 0006).

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

A check runs in phases. By default it runs at the commit and in CI. A check that sets `PHASES` names its own, from `"commit"`, `"ci"`, `"nightly"` and `"push"`:

| Command | Runs the checks whose phases hold |
|---|---|
| `python3 ws.py check`, `python3 ws.py check --staged` | `commit`. It is the default, so the two agree. |
| `python3 ws.py check --phase ci` | `ci`. CI runs it. |
| `python3 ws.py check --phase nightly` | `nightly`. CI's weekly run runs it, for checks too slow for every commit. |
| `python3 ws.py check --push REMOTE` | `push`. The pre-push hook runs it, with git's list of pushed refs on standard input. The parts and the manifest come from the remote's current tip, and the snapshot's `pushed` lists the commits the push adds, merges left out: each as `{"commit", "subject", "paths"}`. |

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

There are five events. The event a hook's `decide` gets:

| Event | Fires | The event holds |
|---|---|---|
| `before-shell` | Before a shell command | `command`: the command line |
| `before-edit` | Before an edit tool writes a file | `path`: relative to the working copy of this repository that holds the file, the main one or a linked worktree, else absolute; `working_copy`, `main` and `absolute`. See [decision 0004](decisions/0004-the-hook-contract.md). |
| `before-handoff` | Before a task is handed to a helper session | `prompt`; and `model` and `effort` when the tool lets a task set them, `None` when left unset |
| `session-start` | When an agent session opens | `session`, `cwd`, `tool`; and the facts the hook declares in `NEEDS` |
| `session-end` | When an agent session closes | The same |

A hook on a session event must set `MODE = "remind"`, and a session start or end never fails: on any error the runner prints nothing and exits 0. A hook may declare `NEEDS`, and the runner adds those facts to its event:

| Event | Fact | What the runner does |
|---|---|---|
| `session-start` | `"findings"` | Runs the check the hook's config names in `"part"` on the session's own working copy |
| `session-start` | `"pins"` | Fetches each pinned repository's upstream default branch and counts the commits its checkout lacks |
| `session-start` | `"fast_forward"` | Brings the main working copy up to `origin/main` when that is safe, and gives the reason when it held back |
| `before-edit` | `"rule_pages"` | Reads every page in the rules folder the hook's config names, fresh, from the working copy that holds the edited file |
| `before-edit` | `"lease"` | Takes or keeps the writing-session lease for an edit to a tracked file in the main working copy; see [decision 0005](decisions/0005-concurrent-sessions-and-the-edit-ledger.md) |

While the manifest uses `lease`, the runner also releases the session's own lease at `session-end`. A part reads nothing else from outside its event, config and snapshot; [decision 0004](decisions/0004-the-hook-contract.md) names the exceptions, and a test holds every part to it.

`python3 ws.py hook <event>` reads the event as JSON on standard input and exits 2 when a hook refuses. It reads two shapes, and refuses everything else:

- **The workspace's own shape**, with a version: `{"version": 1, "command": "git add a.md"}`, `{"version": 1, "path": "docs/a.md"}`, or `{"version": 1, "prompt": "Tier: worker ..."}`. It takes exactly the fields in the table, so a misspelt field is refused, not read as missing.
- **An agent tool's own payload**, read by that tool's adapter in `wslib/events.py`: `python3 ws.py hook before-edit --tool claude-code`, or `--tool codex`. A payload without the field its tool needs, or from a tool the adapter does not send to that event, is refused. With no `--tool`, a payload that is plainly Claude Code's is read by its adapter too. An agent tool keeps the hook wiring a session started with, so a running session with the older wiring is not locked out when the runner is upgraded under it.

So a hook fails closed: whatever the runner cannot read, it refuses.

One call can carry several edits. Codex's patch tool can add, change, delete or move several files at once, so its adapter gives one `before-edit` event per path, a move's source and destination both. The runner refuses the whole call when any one of them is refused, and records the paths only when all are allowed.

A hook that sets `MODE = "remind"` never refuses. When its `decide` returns a reason, the call goes ahead and the agent is shown the reason as a reminder: through the agent tool's `additionalContext`, next to the command's result, for Claude Code and Codex, or as plain text on standard output for the workspace's own shape. Use it where the real check comes later, as `no_stage_all` does before the commit. Before a part sees a path, the runner follows symbolic links, and on a case-insensitive file system it treats a differently cased path to the workspace as inside it.

[.claude/settings.json](../.claude/settings.json) wires the five events into Claude Code, and [.codex/hooks.json](../.codex/hooks.json) into Codex CLI, which gives a hook no variable naming the project, so its lines find `wslib/launch.sh` from the top of the git repository. Each line calls `wslib/launch.sh`. A guard's line ends in `|| exit 2`, so a missing launcher, or a Python that crashes, refuses too; a session hook's line ends in `|| exit 0`, so a broken Python never keeps a session from starting or ending. See [the launcher](#the-launcher). An agent tool blocks a call only on exit 2; anything else lets it through. Codex also lets a call through when its hook times out, so its wiring sets a 30-second limit. Another tool needs an adapter and its own few lines of wiring, and the parts stay the same.

A hook call loads only the hooks for its event. It does not run any check, or any hook for the other event. So a check with a broken case cannot refuse a shell command or an edit, including the edit that repairs it. To know a part's kind without running it, the runner reads its `KIND` and `EVENT` lines. Write each as one plain line, such as `KIND = "hook"`. A part whose lines it cannot read refuses every hook call, because it might be a hook for that event. So does a missing part file, and a manifest it cannot read. Repair those from your own terminal, where the agent's hooks do not run. A hook call does not compare those lines with what the file sets when it runs; `check`, `selftest` and CI do, and refuse a part where they differ.

## The launcher

`wslib/launch.sh` starts Python for every hook, every git hook in `.githooks/` and every CI step. A test fails on wiring, a git hook or a CI step that starts Python any other way.

- **One start per call.** It starts Python once, in UTF-8 mode, with `wslib/start.py`. That file checks the version and then runs the target in the same process. An older Python can read it, so a too-old one says so instead of failing to parse.
- **Which Python.** The first of `python3`, `python` and `py` on the path that is 3.9 or later. A Python that is too old is passed over for the next. The Windows Store's stand-in for `python3`, in a `WindowsApps` folder, is tried only after every other.
- **What it runs.** `wslib/launch.sh ws.py check` runs a script, relative to the workspace. `wslib/launch.sh -m unittest discover -b tests` runs a module. Any other first word is taken as `ws.py`'s arguments, which is the form the hook wiring uses, so a running session keeps working when the launcher changes under it.
- **When it fails.** With no Python that will do, it prints install advice and exits 2. A guard's wiring and the commit and push hooks then refuse. A reminder's wiring and the post-commit hook pass, so a broken Python never keeps a session from finishing.

It needs a POSIX shell. CI runs every step in bash, which on Windows is the bash that comes with Git.

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

A check that reads the commit's state takes it from the case: `"staged"` lists every staged path, deletions included (default: `"changed"`); `"ledger"` lists the edit ledger's paths, and leaving it out means no ledger is open; `"replaying"` names a merge or rebase in progress. `"repositories"` names folders that are code repositories, and `"symlinks"` names files that are symbolic links. `"pushed"` lists the commits of a push, for a push check.

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

## Baselines

A team that adopts the workspace may start with findings it cannot fix at once. A baseline lets a check pass on those and still fail on every new one.

- **One file per check**, `baselines/<check>.json`, listing the findings it tolerates. A missing file tolerates nothing. This repository tolerates nothing, so it has none.
- **A finding is matched by its fingerprint**: a hash of the check's name, the file and the message, not the line, so a finding that only moves stays tolerated. Each entry tolerates one finding, so fixing one finding never makes room for a new one.
- **The commit and CI read it the same way**, from the snapshot they check: the staged file at the commit, the folder's file in CI.
- **Only errors are recorded**, since a warning fails nothing. A file that cannot be read tolerates nothing and is itself an error.
- `python3 ws.py baseline` writes the files from the folder's current findings. It writes a file only for a check that finds errors, or that has a file already. Add `--phase ci` or `--phase nightly` for the checks of those phases.

The files are machinery: they weaken a check, so they change through a pull request, like the check itself. The output of `check` counts the tolerated findings of each check, so they stay in sight. Baselines apply to `check` in its folder, staged and CI forms. The pre-push and commit-message checks take none.

## Removing a part

A part the last commit's manifest uses must stay in the manifest, or be listed under `retired` with the reason:

```json
"retired": [{"use": "no_stage_all", "why": "the commit check now compares staged paths with the session's edits"}]
```

Otherwise `check` fails. Locally, the last commit's manifest decides which parts are required. In CI, the manifest on the base branch decides. Only the `use` names are read from that older manifest, so keys added to the manifest later do not break the comparison. When CI has no base commit, as on a first push, no part is required, and it says so as a warning.

## The manifest

`workspace.json` holds five keys, and the runner refuses any other:

| Key | Holds |
|---|---|
| `version` | The engine version it was written for. It must equal `python3 ws.py --version`. |
| `tiers` | The [tier binding](orchestration.md): `driver`, `worker` and `mechanical`, each with a `model` and an `effort`. Optional; without it, `handoff_tier` refuses every task. |
| `parts` | The parts in use, each with a `use`, a `why` and its settings. |
| `retired` | Parts no longer used, each with a `use` and a `why`. |
| `building` | The milestones being built now, such as `["M3"]`. Each milestone adds itself when its first slice merges and removes itself at sign-off. The proof checks read it; see [decision 0006](decisions/0006-what-proven-means.md). |

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
| `page_kinds` | check | A page under `docs/` names no kind or a kind outside the nine, lacks the front matter its kind needs, or opens out of order: title, a purpose sentence of 25 words or fewer, the **In short** line, and `## Key points` on a plan (see [layout](layout.md)). A proof key in any form but its exact one. And the review-date rule `freshness` held: a commit edits a page past its review date, a required page has no date, or a date is more than a day ahead of today in UTC. It fails when it checks no pages. |
| `chains` | check | A path in the index's cross-cutting chains does not exist, or the index has no chain table. |
| `pointers` | check | The GitHub Copilot or opencode pointer file is missing, or no longer names `AGENTS.md` and the rule pages. |
| `rules` | check | A rule in a rules table has no tag, or a tag names a part the manifest does not use, a case that part does not have, or an eval case that does not exist. `python3 ws.py rules` prints the register. |
| `loaded_size` | check | The contract and the pointer files pass 6,000 bytes, or the wrappers' descriptions 9,000, as the manifest sets. |
| `proof` | check | A proof mark does not hold, or moves without its record: see [decision 0006](decisions/0006-what-proven-means.md). |
| `aliases` | check | The index maps a phrase to a name the code no longer defines, or a contract page names one in backticks. |
| `eval_record` | check | For each playbook marked proven: anything its eval cases depend on changed since their last recorded run (the case, its scaffold and acceptance test, the files each arm is given, `AGENTS.md` and `INDEX.md` among them, the harness, the graders, the code of a hook a grader runs and the shell parser it shares). It also fails when a record has fewer than five runs in an arm; when, counting runs that pass every grader, the guided arm passes no more often than the bare arm; when, pooled across the playbook's cases, the guided arm does not beat the two-line arm by a one-sided Fisher exact test at p < 0.05; when its guided arm passes more than 3 runs fewer than the previous record's or its anchor's; or when a proven playbook has no case. A page's review date and its exact proof keys are not in the hash. |
| `deny_list` | check | A file or file name holds a term from a private list kept outside the repository, and so, from the commit-msg hook, does the commit message, the author or the committer. With no list it warns and checks nothing, so CI cannot run it. |
| `edit_ledger` | check | While the edit ledger is open, a commit stages a path that no edit tool of the agent session wrote. |
| `no_stage_all` | hook, before-shell, reminds | Reminds, and never refuses, when a command stages everything instead of naming files. |
| `direct_push` | check, at the push | A push to main adds a commit that changes a path on its `machinery` list. See [changing the machinery](changing-the-machinery.md). |
| `no_admin_merge` | hook, before-shell | A shell command merges a pull request with `gh pr merge --admin`. |
| `stale_pages` | hook, session-start, reminds | Lists the pages past their review date, from `page_kinds` run on the session's working copy. |
| `stale_pins` | hook, session-start, reminds | Names each pinned repository whose checkout is behind its upstream's default branch. |
| `pin_on_default` | check | A staged pin is not on its reachable upstream's default branch. An upstream it cannot reach warns. |
| `line_cites` | check | A line the commit adds to a doc page cites a file by line number, outside a fenced block and with no commit hash beside it. |
| `in_short` | check | A plan, decision record or milestone page has no **In short:** line within 15 lines of its title. |
| `rule_pages` | hook, before-edit, reminds | Shows the agent each page in `docs/rules/` whose `applies-to` patterns match the edited file. |
| `lease` | hook, before-edit | Another live agent session holds the main working copy, or the lease cannot be checked. The edit goes to a worktree instead. |
| `fast_forward` | hook, session-start, reminds | Says why the main working copy was not brought up to `origin/main`, when it held back. |
| `browser_isolation` | check | The project settings do not turn the browser plugin off by name, or an agent tool's config runs the browser server without `--isolated` or at an inexact version. See [browsers](browsers.md). |
| `shelved` | hook, before-edit | An edit tool touches a folder marked read-only. |
| `handoff_tier` | hook, before-handoff | A delegated task names no tier on its first line, or sets a model or effort other than the manifest's binding for its tier, or leaves one unset that the tool lets it set. |
