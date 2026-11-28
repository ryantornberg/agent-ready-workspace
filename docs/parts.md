---
kind: how-to
proof: unproven
prove-by: M4
last-reviewed: 2026-11-18
---

# Parts

How the checks and hooks plug in, and how to add one. It is for anyone extending the workspace.

**In short:** a part is one Python file plus a file of cases. The manifest lists the parts a workspace uses. The runner runs a part's cases when it loads the part, and refuses a part with no cases or a failing one. A hook call skips the cases when they passed before on the same files.

## The pieces

| Piece | File | Job |
|---|---|---|
| Manifest | `workspace.json` | Lists the parts this workspace uses, each with its settings. |
| Runner | `ws.py`, which starts `wslib/runner.py` | Loads the parts, gives each check a snapshot of the files, and gives each hook its event. |
| Part | `parts/<name>.py` | One check or one hook. |
| Cases | `parts/<name>.cases.json` | The part's own tests, as data. |

When you are adding a page, a playbook, a decision record or a rule page rather than a part, follow [extend the workspace](extend-the-workspace.md) instead.

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

Both commands start from one git listing, so they see the same files. A tracked or staged file is always in it, wherever it sits, and the `.git` entry never is. `check` adds the untracked files that git does not ignore. A folder that is not the top of a git working copy is walked instead. `check --staged` reads every staged file in one batch: three git processes, however many files there are, plus at most three for the history the proof and eval checks read (decision record 0006).

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

Every part sets `PAGE`, the page that states its rule. The runner prints each finding with its file and line, the part, the page when the message does not name it, and the command that runs the check again. A refusal or reminder from a hook names the page the same way. A message still says how to fix what it found. A test runs every part's cases and fails a message that lacks any of these.

A check that sets `HISTORY = True` also runs under `python3 ws.py check --history`, over a snapshot whose changed paths are `<commit>:<path>` and whose added lines are every line each commit in the history added. CI runs it on every push and pull request.

A check runs in phases. By default it runs at the commit and in CI. A check that sets `PHASES` names its own, from `"commit"`, `"ci"`, `"nightly"` and `"push"`:

| Command | Runs the checks whose phases hold |
|---|---|
| `python3 ws.py check`, `python3 ws.py check --staged` | `commit`. It is the default, so the two agree. |
| `python3 ws.py check --phase ci` | `ci`. CI runs it. |
| `python3 ws.py check --phase nightly` | `nightly`. CI's weekly run runs it, for checks too slow for every commit. |
| `python3 ws.py check --push REMOTE` | `push`. The pre-push hook runs it, with git's list of pushed refs on standard input. The parts and the manifest come from the remote's current tip, and the snapshot's `pushed` lists the commits the push adds: each as `{"commit", "subject", "message", "paths", "files", "merge"}`, where a merge's paths are only what it changes itself and `files` reads the commit's tree. On a push to main, the hook then runs the runnable blocks of every tutorial the push changes, in a fresh clone; see [layout](layout.md#tutorials). |

The phases are the part's, not the manifest's, so no manifest edit can move `deny_list` off the commit. `selftest` runs every part's cases, whatever its phases.

A check that sets `COMMIT_MESSAGE = True` also runs from the commit-msg hook, `python3 ws.py check --message FILE`. Its snapshot then holds three files: `commit message`, `author` and `committer`, each identity as git will record it. Its `pushed` holds the commit being made, in the same shape as at the push: the staged paths, deletions included, and the staged files as its tree. In CI, `python3 ws.py check --commits BASE..HEAD` runs the same checks over every commit of the range, each with its own message, identities, paths and tree. `deny_list`, `commit_subject` and `review_trailer` are the ones here. A check that sets `COMMIT_DIFF = True` also runs there on the lines each commit adds: each path the commit changed holds only those lines, on their own line numbers, and a file it created empty is there, so its name is read. A merge commit's own lines, such as a conflict resolution, are not read. `deny_list` is the one here. CI has no deny list, so there it warns and checks nothing; the scan bites in the run before a branch committed with `--no-verify` is pushed, as [changing the machinery](changing-the-machinery.md#traps) says.

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

There are seven events. The event a hook's `decide` gets:

| Event | Fires | The event holds |
|---|---|---|
| `before-shell` | Before a shell command | `command`: the command line |
| `before-edit` | Before an edit tool writes a file | `path`: relative to the working copy of this repository that holds the file, the main one or a linked worktree, else absolute; `working_copy`, `main` and `absolute`. See [decision 0004](decisions/0004-the-hook-contract.md). |
| `before-handoff` | Before a task is handed to a helper session | `prompt`; and `model` and `effort` when the tool lets a task set them, `None` when left unset |
| `after-edit` | After an edit tool wrote a file | The same fields as `before-edit` |
| `session-start` | When an agent session opens | `session`, `cwd`, `tool`; and the facts the hook declares in `NEEDS` |
| `session-end` | When an agent session closes | The same |
| `stop` | When the agent tries to finish its turn | `session`, `cwd`, `tool`, and `stop_hook_active`: true on the stop that follows one a stop hook refused |

A hook on a session event or on `after-edit` must set `MODE = "remind"`. A stop hook may refuse, and the runner lets it refuse only once in a row: on the stop after a refusal, the reason is shown to the person as a report and the session stops. None of these four events ever fails: on any error the runner prints nothing and exits 0. One exception is on purpose: when an edit ledger cannot be read, the stop gate refuses once, as it would for a failing check, since it cannot tell whose edits are waiting. A hook may declare `NEEDS`, and the runner adds those facts to its event:

| Event | Fact | What the runner does |
|---|---|---|
| `session-start` | `"findings"` | Runs the check the hook's config names in `"part"` on the session's own working copy |
| `session-start` | `"pins"` | Fetches each pinned repository's upstream default branch and counts the commits its checkout lacks |
| `session-start` | `"fast_forward"` | Brings the main working copy up to `origin/main` when that is safe, and gives the reason when it held back |
| `session-start` | `"ci"` | Reads the newest CI runs of the workflow the hook's config names in `"workflow"`, on the branch it names in `"branch"`, with `gh`, beside the other facts. Reading `origin` and both `gh` calls share one time limit of 3 seconds. Gives how many runs in a row failed, when the first of them started, the failing steps of the newest and its link; `{"failed": 0}` when the newest passed; and `None` on any error. See [decision 0004](decisions/0004-the-hook-contract.md) |
| `session-start` | `"handoffs"` | Reads the handoff markers in the git folder of the working copy the session runs in, keeps those still pending, and reads the note when exactly one is. See [handoff](playbooks/handoff.md#the-marker-and-the-loader) |
| `before-edit` | `"rule_pages"` | Reads every page in the rules folder the hook's config names, fresh, from the working copy that holds the edited file |
| `before-edit` | `"lease"` | Takes or keeps the writing-session lease for an edit to a tracked file in the main working copy; see [decision 0005](decisions/0005-concurrent-sessions-and-the-edit-ledger.md) |
| `before-edit` | `"git_config"` | Gives `home`, the home folder; `files`, every git config file a write must not reach, the global and system ones and each file an include names; and `unresolved`, why the includes could not be read. See [decision 0004](decisions/0004-the-hook-contract.md), "Shell events" |
| `before-shell` | `"session"`, `"lease"`, `"working_copies"`, `"targets"`, `"aliases"`, `"git_config"`, `"destinations"`, `"repositories"` | The session and its folder, the lease as it stands, the working copy each git call acts on, where each gh call and push goes, the git aliases defined where a call needs one, the git config files, the URLs each push reaches, in one git call for a push that names a remote, and the outward-write list the hook's config names in `"list"`. Each but the first two is worked out only when a hook reads it. See [decision 0004](decisions/0004-the-hook-contract.md), "Shell events" |
| `after-edit` | `"index"` | Reads the index file the hook's config names, fresh, from the working copy that holds the edited file |
| `stop` | `"own_edits"` | Reads this session's entries from the edit ledger of every working copy of this repository |
| `stop` | `"gate"` | Runs `python3 ws.py check` and the tests the hook's config names in `"tests"`, in each working copy that holds the session's entries. The runs share one deadline of 18 seconds, so the hook answers within its 20. Worked out only when a hook reads it |

While the manifest uses `lease`, the runner also releases the session's own lease at `session-end`. A part reads nothing else from outside its event, config and snapshot; [decision 0004](decisions/0004-the-hook-contract.md) names the exceptions, and a test holds every part to it.

`python3 ws.py hook <event>` reads the event as JSON on standard input and exits 2 when a hook refuses. It reads two shapes, and refuses everything else:

- **The workspace's own shape**, with a version: `{"version": 1, "command": "git add a.md"}`, `{"version": 1, "path": "docs/a.md"}`, or `{"version": 1, "prompt": "Tier: worker ..."}`. It takes exactly the fields in the table, so a misspelt field is refused, not read as missing.
- **An agent tool's own payload**, read by that tool's adapter in `wslib/events.py`: `python3 ws.py hook before-edit --tool claude-code`, or `--tool codex`. A payload without the field its tool needs, or from a tool the adapter does not send to that event, is refused. With no `--tool`, a payload that is plainly Claude Code's is read by its adapter too. An agent tool keeps the hook wiring a session started with, so a running session with the older wiring is not locked out when the runner is upgraded under it.

So a hook fails closed: whatever the runner cannot read, it refuses.

One call can carry several edits. Codex's patch tool can add, change, delete or move several files at once, so its adapter gives one `before-edit` event per path, a move's source and destination both. The runner refuses the whole call when any one of them is refused, and records the paths only when all are allowed.

A hook that sets `MODE = "remind"` never refuses. When its `decide` returns a reason, the call goes ahead and the agent is shown the reason as a reminder: through the agent tool's `additionalContext`, next to the command's result, for Claude Code and Codex, or as plain text on standard output for the workspace's own shape. Use it where the real check comes later, as `no_stage_all` does before the commit. Before a part sees a path, the runner follows symbolic links, and on a case-insensitive file system it treats a differently cased path to the workspace as inside it.

[.claude/settings.json](../.claude/settings.json) wires the seven events into Claude Code, and [.codex/hooks.json](../.codex/hooks.json) into Codex CLI, which gives a hook no variable naming the project, so its lines find `wslib/launch.sh` from the top of the git repository. Each line calls `wslib/launch.sh`. A guard's line ends in `|| exit 2`, so a missing launcher, or a Python that crashes, refuses too; a line for a session event, `after-edit` or `stop` ends in `|| exit 0`, so a broken Python never keeps a session from starting, stopping or ending. See [the launcher](#the-launcher). An agent tool blocks a call only on exit 2; anything else lets it through. Codex also lets a call through when its hook times out, so its wiring sets a 30-second limit. Another tool needs an adapter and its own few lines of wiring, and the parts stay the same.

A hook call loads only the hooks for its event. It does not run any check, or any hook for the other event. So a check with a broken case cannot refuse a shell command or an edit, including the edit that repairs it. To know a part's kind without running it, the runner reads its `KIND` and `EVENT` lines. Write each as one plain line, such as `KIND = "hook"`. A part whose lines it cannot read refuses every hook call, because it might be a hook for that event. So does a missing part file, and a manifest it cannot read. Repair those from your own terminal, where the agent's hooks do not run. A hook call does not compare those lines with what the file sets when it runs; `check`, `selftest` and CI do, and refuse a part where they differ.

## The launcher

`wslib/launch.sh` starts Python for every hook, every git hook in `.githooks/` and every CI step. A test fails on wiring, a git hook or a CI step that starts Python any other way.

- **One start per call.** It starts Python once, in UTF-8 mode, with `wslib/start.py`. That file checks the version and then runs the target in the same process. An older Python can read it, so a too-old one says so instead of failing to parse.
- **Which Python.** The first of `python3`, `python` and `py` on the path that is 3.9 or later. A Python that is too old is passed over for the next. The Windows Store's stand-in for `python3`, in a `WindowsApps` folder, is tried only after every other.
- **What it runs.** `wslib/launch.sh ws.py check` runs a script, relative to the workspace. `wslib/launch.sh -m unittest discover -b tests` runs a module. Any other first word is taken as `ws.py`'s arguments, which is the form the hook wiring uses, so a running session keeps working when the launcher changes under it.
- **When it fails.** With no Python that will do, it prints install advice and exits 2. A guard's wiring and the commit and push hooks then refuse. A reminder's wiring, the stop gate's and the post-commit hook pass, so a broken Python never keeps a session from finishing; the stop gate is then skipped.

It needs a POSIX shell. CI runs every step in bash, which on Windows is the bash that comes with Git.

## The edit ledger

Each `before-edit` call that every hook allows is recorded: the runner appends the path to the edit ledger of the working copy that holds the file, with the session whose edit tool wrote it. The stop gate reads the sessions; the commit check reads only the paths. The ledger is the file `ws-ledger` in that working copy's git folder, so a linked working copy keeps its own. An edit in a code repository under `src/` goes in the workspace's ledger. An edit outside every working copy of this repository is not recorded. If the ledger cannot be written, the edit is refused.

While a ledger is open, the `edit_ledger` check fails a commit that stages a path no edit tool wrote, whatever command staged it. A `before-shell` reminder opens the ledger too, even empty, in the working copy where the agent tool says its session runs, when that working copy has uncommitted changes. So a session that wrote its files only through the shell is still compared, and a command run in a scratch repository while the session's own working copy is clean opens nothing. The workspace's own event shape names no folder, so trying the hook by hand opens nothing.

| Command | Does |
|---|---|
| `python3 ws.py ledger` | Says whether the ledger is open, and lists its paths. |
| `python3 ws.py ledger --add PATH ...` | Records files this session wrote another way, such as with a shell command or a generator. They carry no session, so the stop gate does not see them. |
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

A hook call is the one exception, because hooks run around every tool call and session event, and most have a time budget. It skips a hook's cases when they passed before on exactly the same files. The working copy's git folder keeps a record, `ws-cases.json`, of each hook whose cases passed. The record holds a digest of the part, its cases, every engine and workspace module loaded when they passed, and the Python and system that ran them. A change to any of those runs the cases again, and a failure is never recorded. Every other command, the commit check and CI included, runs every case every time.

The commit check, `check --staged`, reads the staged manifest, the staged parts and their staged cases. An edit you have not staged cannot change its result.

## Baselines

A team that adopts the workspace may start with findings it cannot fix at once. A baseline lets a check pass on those and still fail on every new one.

- **One file per check**, `baselines/<check>.json`, listing the findings it tolerates. A missing file tolerates nothing. This repository tolerates nothing, so it has none.
- **A finding is matched by its fingerprint**: a hash of the check's name, the file and the message, not the line, so a finding that only moves stays tolerated. Each entry tolerates one finding, so fixing one finding never makes room for a new one.
- **The commit and CI read it the same way**, from the snapshot they check: the staged file at the commit, the folder's file in CI.
- **A change cannot excuse a finding it brings.** An entry tolerates a finding only when the base has that finding too: the last commit for `check` and the commit check, and the merge base with the `--changed-from` commit in CI. Adding the entry in the same pull request, or ahead of the finding, does not help. A team's first baseline passes, because main already has its findings. With no base to compare with, nothing is tolerated. The check runs a second time, on the base, only when its baseline lists something.
- **Only errors are recorded**, since a warning fails nothing. A file that cannot be read tolerates nothing and is itself an error.
- `python3 ws.py baseline` writes the files from the folder's current findings. It writes a file only for a check that finds errors, or that has a file already. Add `--phase ci` or `--phase nightly` for the checks of those phases.

The files are machinery: they weaken a check, so they change through a pull request, like the check itself. The output of `check` counts the tolerated findings of each check, so they stay in sight. Baselines apply to `check` in its folder, staged and CI forms. The pre-push and commit-message checks take none. A check that judges only the lines a change adds, such as `line_cites`, finds nothing at a base, so its findings cannot be tolerated.

A check that reads the history, such as `secret_scan`, keeps the findings it tolerates there in a file of its own, `baselines/<check>.history.json`, written by `python3 ws.py baseline --history`. `check --history --changed-from REF` tolerates an entry only when the history of the merge base with REF already has that finding. With no base, it tolerates nothing. It reads the history of the branch being checked, not every branch, so a token on another branch does not fail this one.

## The hook case runner

A part's cases call its `decide` function with the facts already filled in. They cannot see the wiring, the launcher, an agent tool's payload, the lease file or git. The hook case runner can:

```
python3 tests/hook_cases.py
```

Each case in `tests/hooks/<event>.json` builds a scratch repository from this repository's tracked files. It seeds what the case needs: a lease held by a live or a dead process, a local remote that is ahead, a linked worktree, uncommitted files, edit ledger entries, or a pending handoff marker. Then it runs the command the agent tool's own settings wire for the event, through `wslib/launch.sh`, with that tool's payload on standard input. It checks the exit code, the output and who holds the lease afterwards. The file `tests/hook_cases.py` documents the case format.

Every call is timed, and the runner prints each event's median. A push (`git push`) and a `gh` write are timed as rows of their own. On Linux and macOS the run fails when a median is over its budget. On Windows it only reports, because starting a process there costs several times more.

| Event or row | Budget |
|---|---|
| A before-tool hook, an after-edit hook, the push row, the `gh` write row | 200 milliseconds |
| `session-start`, against a local remote | 2 seconds |
| `stop` | 20 seconds, the stop gate's own limit |
| `session-end` | none; reported only |

Every event the engine knows needs at least one case, so a new event cannot arrive untimed. CI runs the runner on all three systems.

`tests/test_cases_bite.py` holds every part's own cases to the same standard from the other side. It runs each part the manifest lists against a stub that allows everything and finds nothing, and against one that refuses everything and always finds something. Each stub must fail at least one case.

## Pinned repositories

A workspace pins its code repositories as submodules under `src/` ([decision 0001](decisions/0001-pin-code-repositories.md)). A fresh clone holds the pins but not the code. This checks the code out:

```
python3 ws.py pins
```

- **Every remote is probed at once**, with `git ls-remote`, prompts off and a ten-second limit each. A remote that needs a password it does not have fails at once instead of asking, so one unreachable repository costs ten seconds in all, not a hung terminal.
- **Each one that answers is initialized and checked out** at its pin, one at a time.
- **One that does not answer is skipped with a note**, and the command still exits 0. It exits 1 only when a remote answered and the checkout then failed.
- **A folder that already holds a checkout, or any files, is never touched**: no fetch, no reset, no switch. Run it as often as you like.
- A relative URL in `.gitmodules`, such as `../orders-api.git`, is read against the workspace's own `origin`, as git reads it.

`tests/test_pins.py` runs it on fixture repositories: one reachable, one gone, one hanging, and one already checked out with local work in it.

## The cold-clone job

`.github/workflows/cold-clone.yml` clones the repository fresh on Linux and macOS, with the machine's own git and `python3`. It follows the README's marked setup steps and nothing else, then runs `selftest`, `check` and the tests. In the kit's repository, it then adopts the clone into a new folder, as [the kit](#the-kit) says, and follows the instance's own README's marked steps. A step is a fenced block right after a line `<!-- setup -->`; `tools/setup_steps.py` turns the marked blocks into one script that stops at the first failure, and fails when no block is marked.

It runs every night, on main. It also runs on a pull request, and on a push to main, that changes a setup page, `tools/setup_steps.py` or the job itself. Doc changes go straight to main, so a pull request alone would miss most changes to the README. Setup steps that nobody runs go false at the head of main without anyone noticing; this job is what runs them. The setup pages are `SETUP_PAGES` in `tools/setup_steps.py`, and `tests/test_cold_clone.py` holds the job's paths to that list.

The README's steps start `python3` by name, as a person would. That is the one place CI starts Python other than through the launcher. Windows is left out, because a Windows install of Python provides no `python3`.

## The kit

`python3 ws.py adopt PATH` makes an instance of this workspace in PATH, an empty folder, and `python3 ws.py upgrade PATH` takes a newer kit into one. Both run from the kit's own repository; `wslib/kit.py` holds them. `kit/kit.json` gives every file git tracks a class, synced, seeded or never synced, by the first rule whose path matches it, and `kit/seed/` holds the files an instance gets in place of this repository's own, such as its README. [Decision 0007](decisions/0007-the-kit.md) says what each class means and why.

`python3 ws.py kit` prints the kit manifest: every file with its class and hash, the proof state of each synced page, and the kit's eval cases. Each file is read as the working copy holds it, and a file git does not track is left out, so commit or stage a new file before making an instance from it; adopt notes when the working copy holds changes not committed. Adopt and upgrade write it into the instance as `kit.lock.json`, its lock.

In an instance, the `kit_drift` check fails a synced file that no longer matches the lock, and `python3 ws.py drift` reports the same on the working folder. `python3 ws.py drift --keep PATH` makes a synced file the instance's own: the lock marks it kept, `kit_drift` and upgrades leave it alone, and the other checks hold it as the instance's own page. It refuses a page the kit marks proven. The `proof`, `eval_record` and `rules` checks read the lock there through `wslib/kitlock.py`, which reads nothing but the snapshot a check is given. A workspace with no lock is not an instance, and all four behave as they do here.

In the kit's repository, `tests/test_kit.py` adopts the working copy into a temporary folder and runs the instance's own `selftest`, `check` and `drift` there. It also upgrades an instance from a small newer kit made in another. The kit's cold-clone job adopts its fresh clone and follows the instance's own README's marked steps.

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
4. A hook on a new event also needs a case in `tests/hooks/<event>.json`; run `python3 tests/hook_cases.py`.

A part's `config` is its manifest entry without `use` and `why`, plus the manifest's tier binding as `tiers`. The binding lives in one place, so an entry that sets `tiers` itself is refused.

To use a part kept somewhere else, give its path: `{"use": "shared/parts/licences.py", "why": "..."}`. Its cases file sits next to it.

## The parts here

| Part | Kind | Fails or refuses when |
|---|---|---|
| `links` | check | A link points at a missing file or heading, or a line is too long to read: over 10,000 characters. On the pages its `backticked` setting lists, a backticked path with a slash whose first folder exists, such as `src/orders-api`, points at nothing. An entry in its `exempt` setting, `{"source": page, "target": exact target, "reason": why}`, tolerates one such finding; an entry with no source, target or reason fails, and so does one that tolerates nothing. |
| `page_kinds` | check | A page under `docs/` names no kind or a kind outside the nine, lacks the front matter its kind needs, or opens out of order: title, a purpose sentence of 25 words or fewer, the **In short** line, and `## Key points` on a plan (see [layout](layout.md)). A proof key in any form but its exact one. And the review-date rule `freshness` held: a commit edits a page past its review date, a required page has no date, or a date is more than a day ahead of today in UTC. It fails when it checks no pages. |
| `chains` | check | A path in the index's cross-cutting chains does not exist, or the index has no chain table. |
| `chain_reminder` | hook, after-edit, reminds | Shows the agent each cross-cutting chain of the index that names the edited path, with every path in it. |
| `stop_gate` | hook, stop | A session with entries of its own in an edit ledger tries to finish while `python3 ws.py check` or the fast tests its `tests` setting names fail, run past their shared 18 seconds or cannot start, or an edit ledger cannot be read. It refuses once in a row; the stop right after the refusal goes ahead with the failure as a report. See [decision 0005](decisions/0005-concurrent-sessions-and-the-edit-ledger.md). |
| `pointers` | check | The GitHub Copilot or opencode pointer file is missing, or no longer names `AGENTS.md` and the rule pages. |
| `rules` | check | A rule in a rules table has no tag, or a tag names a part the manifest does not use, a case that part does not have, or an eval case that does not exist. `python3 ws.py rules` prints the register. |
| `loaded_size` | check | The contract and the pointer files pass 6,000 bytes, or the wrappers' descriptions 9,000, as the manifest sets. |
| `wrappers` | check | A core playbook or how-to has no wrapper and is not on its `waiting` list. A wrapper routes to a page that is missing, a lane draft, a waiting page or a page that is not a procedure, or is not named after its page's file; its name or description is out of form; or its description names no wrapper next to it, or one that does not exist. A wrapper lacks a selection case that should fire it or one that should leave it quiet. Or the plugin's manifest, its marketplace entry or the project setting that enables it is missing. The cases in `parts/wrappers.cases.json` list the rest, such as a waiting entry for another milestone or a malformed selection case. See the [playbook catalog](playbooks/README.md#three-ways-to-follow-a-playbook). |
| `proof` | check | A proof mark does not hold, or moves without its record: see [decision 0006](decisions/0006-what-proven-means.md). In an instance, a synced page's marks differ from the kit's lock. |
| `kit_drift` | check | In an instance made from the kit, a synced file no longer matches the hash in `kit.lock.json`, or is gone. A seeded file, a kept one and a file of the instance's own pass. A workspace with no lock is not checked. See [the kit](#the-kit). |
| `aliases` | check | The index maps a phrase to a name the code no longer defines, or a contract page names one in backticks. |
| `eval_record` | check | For each playbook marked proven: anything its eval cases depend on changed since their last recorded run (the case, its scaffold and acceptance test, the files each arm is given, `AGENTS.md` and `INDEX.md` among them, and the harness that runs the agent). It fails when a grading file changed, `grade.py` or a hook a grader runs with the modules it imports, until `python3 evals/grade.py --recorded --stamp` re-grades the stored runs with no difference and writes the new grader hash, and when a record holds no grader hash, as every record `run.py` writes does until M4's slice H0b; until H0b rewrites the contract's eval rule, that grading-files exception is the eval page's. It also fails when a record has fewer than five runs in an arm; when, counting runs that pass every grader, the guided arm passes no more often than the bare arm; when, pooled across the playbook's cases, the guided arm does not beat the two-line arm by a one-sided Fisher exact test at p < 0.05; when its guided arm passes more than 3 runs fewer than the previous record's or its anchor's; or when a proven playbook has no case. A page's review date and its exact proof keys are not in the hash. |
| `deny_list` | check | A file or file name holds a term from a private list kept outside the repository, and so, from the commit-msg hook, does the commit message, the author or the committer, and, from `check --commits`, a line a commit adds. With no list it warns and checks nothing, so CI cannot run it. |
| `edit_ledger` | check | While the edit ledger is open, a commit stages a path that no edit tool of the agent session wrote. |
| `no_stage_all` | hook, before-shell, reminds | Reminds, and never refuses, when a command stages everything instead of naming files. |
| `direct_push` | check, at the push | A push to main adds a commit that changes a path on its `machinery` list. See [changing the machinery](changing-the-machinery.md). |
| `secret_scan` | check | A line the commit adds looks like a token or a private key. `python3 ws.py check --history` runs it over every line the history added. See [commits](commits.md). |
| `commit_subject` | check, on the commit message | The subject matches none of the manifest's `formats`, conventional commits by default; git's own merge, revert and autosquash subjects pass. Over 72 characters warns. |
| `review_trailer` | check, on the commit message and at the push | A commit adds, changes or deletes a guidance page, the paths its `guidance` setting lists and `except` does not, with no `Instructions-review:` trailer naming a record the commit adds or changes and that covers the page, and no listed reason to skip. See [the instruction review](playbooks/instruction-review.md). |
| `review_index` | check | The index of instruction-review records leaves out a record, disagrees with one on its pages or classes, or has no record for a page its `required` setting lists. |
| `claim_marks` | check | A fix record in `docs/records/fixes/` has no `## Report` section, or a claim line in it does not start with `verified` or `inferred`. See [the fix record template](templates/fix-record.md). |
| `plan_budgets` | check | A draft plan's Key points block holds more than 200 words, or any table cell in the plan, outside fenced blocks, holds more than 60. Approved, done and abandoned plans are skipped. See [the hand-off plan template](templates/hand-off-plan.md). |
| `decisions` | check | A decision record's file name is not a four-digit number and a topic, or shares its number; its front matter has no `date` or `deciders`, or a `date` that is not a calendar date; its title does not start with its number; it lacks Context, Decision, What it gave up or Options rejected, or holds them out of order; an "Amended" has no date after it, or one before the record's own; or a superseded record does not name its successor; or a `supersedes` or `superseded-by` names no other record, or a record that is not superseded carries `superseded-by`. It fails when `docs/decisions/` holds no record. See [the decision record template](templates/decision-record.md). |
| `agent_settings` | check | Claude Code's settings lack a deny entry for a secrets pattern or an allow entry for a documentation domain, or Codex CLI's config lacks the profile, one of its denies, or a web search domain. See [agent settings](agent-settings.md). |
| `no_admin_merge` | hook, before-shell | A shell command merges a pull request with `gh pr merge --admin`, `--squash` or `--rebase`, or through `gh api` with a merge method other than a merge commit, with a body it cannot read, or as an API write whose path is a variable; or a command it cannot judge, such as a program word that is a variable or a `gh pr merge` argument that is one. See [changing the machinery](changing-the-machinery.md#the-path-for-a-machinery-change). |
| `stale_pages` | hook, session-start, reminds | Lists the pages past their review date, from `page_kinds` run on the session's working copy. |
| `stale_pins` | hook, session-start, reminds | Names each pinned repository whose checkout is behind its upstream's default branch. |
| `pin_on_default` | check | A staged pin is not on its reachable upstream's default branch. An upstream it cannot reach warns. |
| `line_cites` | check | A line the commit adds to a doc page cites a file by line number, outside a fenced block and with no commit hash beside it. |
| `in_short` | check | A plan, decision record or milestone page has no **In short:** line within 15 lines of its title. |
| `rule_pages` | hook, before-edit, reminds | Shows the agent each page in `docs/rules/` whose `applies-to` patterns match the edited file. |
| `lease` | hook, before-edit | Another live agent session holds the main working copy, or the lease cannot be checked. The edit goes to a worktree instead. |
| `no_discard` | hook, before-shell | While another live session holds the main working copy's lease: a git command that drops work there (hard reset, `reset --keep`, a whole-tree checkout or restore, `checkout -f`, `switch -f`, `read-tree -u --reset`, a forced clean, a stash write, or the rebase family), a stash drop, pop or clear or `worktree prune` from any working copy, `worktree remove --force` of another session's worktree, or a command it cannot resolve. A git alias is judged as what it runs; a form it decides on with `HOME`, `XDG_CONFIG_HOME`, `GIT_CONFIG_GLOBAL`, `GIT_CONFIG_SYSTEM` or `GIT_CONFIG_NOSYSTEM` set, or an include given on the command, is refused. See [decision 0005](decisions/0005-concurrent-sessions-and-the-edit-ledger.md). |
| `push_lease` | hook, before-shell | While another live session holds the main working copy's lease: a `git push` from the main working copy, a push whose folder cannot be placed, a push with `HOME`, `XDG_CONFIG_HOME`, `GIT_CONFIG_GLOBAL`, `GIT_CONFIG_SYSTEM` or `GIT_CONFIG_NOSYSTEM` set or an include given on the command, or a command it cannot resolve; and from a linked worktree, a push that sends the branch the main copy has checked out, named as a branch, every branch, a mirror or a glob refspec, read from the push's resolved target, or a push of HEAD or a bare push after a call earlier in the line that can change the branch. A git alias is judged as what it runs. A dry run passes. See [decision 0005](decisions/0005-concurrent-sessions-and-the-edit-ledger.md). |
| `no_force_push` | hook, before-shell | A `git push` that would force or delete the default branch (`"branch"`, default `main`), judged by what git would send: `--force`, a `+` refspec, a `--force-with-lease` covering it, `--all` or `--branches` with a force, `--mirror`, a forced glob, `--prune` with a glob or every branch, `--delete`, or config that does the same. Also `git send-pack`, `git http-push` and a remote helper called by name, such as `git remote-https`, which push without `git push` and which it does not judge, and a push it cannot judge: a word the shell would expand, unquoted braces or a glob, or a word directly followed by `(`, which zsh reads as a glob or a glob qualifier, in a push or in a git call that is not built in and so may be one, a variable or substitution in its remote or branch, an unresolved target on a push with no refspec or one that forces, deletes or prunes, a config write on it, arguments `xargs` supplies, an unresolved git alias, a program word that is a variable, and a forced push after a call earlier in the line that changes the branch, an upstream, a remote or gh's default. See [decision 0004](decisions/0004-the-hook-contract.md). |
| `outward_write` | hook, before-shell | A shell command writes to a repository outside the list its `"list"` names, `outward-repos.json` by default: any gh call but the read subcommands in its `READS` and a `gh api` GET, a `git push` whose destination is not a local path, a `git send-pack` or `git http-push` whose URL, read past the options that take a value, is not one, `git remote add` or `set-url`, judged by where each really goes. On every repository: an approval, by `gh pr review --approve` or a `gh api` reviews, run or deployment call, and any `gh api graphql`. A shell write to the list the parser reports, `git mv`, `rm`, `checkout` or `restore` naming it among them. A command it cannot judge. See [decision 0004](decisions/0004-the-hook-contract.md). |
| `outward_list` | hook, before-edit | An edit tool writes a file named as the list its `"list"` names, in any folder. |
| `secrets_shell` | hook, before-shell | A shell command prints the environment, such as `env` with no program, `printenv`, `export -p`, `set`, `ps eww`, PowerShell's `env:` drive named on the line itself or its `GetEnvironmentVariables` method, or names a secrets file from its `"secrets"` or `"home"` patterns, or the `"file"` `ws.py with-secrets` reads, in an argument or after `<` or `<>`, unless its program only looks at the name, such as `ls`, `test` or `git status`. The method's name passes as text in a message body, or in a heredoc fed to a program that is not a shell. A glob that may match a secrets file, such as `cat *`, counts as naming one; the first word after `grep`, `rg`, `sed` or `awk` is a pattern, and a message body is not read. Also `ws.py with-secrets` whose program is a shell, `env`, `printenv`, a program that runs another, a program given by a variable, git, gh, another `with-secrets` or a write the parser reports, and a command that sets `WS_SECRETS_FILE`. See [agent settings](agent-settings.md#secrets-in-the-shell). |
| `fast_forward` | hook, session-start, reminds | Says why the main working copy was not brought up to `origin/main`, when it held back. |
| `ci_notice` | hook, session-start, reminds | Says when the newest CI run of its `workflow` on its `branch` failed: how many runs in a row, since when, the failing steps and the link. It says nothing when that run passed, and nothing on any error, such as no `gh`, no sign-in, no network or the time limit. Runs from pull requests, unfinished runs and cancelled or skipped runs are passed over. An `origin` that is a local path, or names no owner and repository, gets no call; any other host is asked, and says nothing when `gh` cannot answer. |
| `handoff_loader` | hook, session-start, reminds | Shows the handoff note that the one pending marker of the session's working copy names; with two or more pending, shows none and lists them. A marker is pending until its branch merges into its `branch` setting, `main` by default, or `python3 ws.py handoff --done` clears it. See [handoff](playbooks/handoff.md#the-marker-and-the-loader). |
| `browser_isolation` | check | The project settings do not turn the browser plugin off by name, or an agent tool's config runs the browser server without `--isolated` or at an inexact version. See [browsers](browsers.md). |
| `shelved` | hook, before-edit | An edit tool touches a folder marked read-only. |
| `git_folder` | hook, before-edit | An edit tool writes under a `.git` path segment, a linked worktree's `.git` file included, or to a git config file: the global and system ones and any file an include names. When git could not list the includes, a write to an included file passes. `.github/`, `.githooks/`, `.gitignore` and `.gitattributes` pass. See [decision 0004](decisions/0004-the-hook-contract.md). |
| `git_folder_shell` | hook, before-shell | A shell write the parser reports lands under a `.git` segment or in a git config file; a writer gets its files from `xargs` or `find -exec`, or `find -delete` runs; or `git config` sets or removes a key the guards read, such as `alias.*`, `remote.*`, `include.*`, `core.hooksPath` or `submodule.recurse`, directly or through a git alias read from config; or a call that may be an alias is made while its aliases cannot be read, or with `HOME`, `GIT_CONFIG_GLOBAL` or an include changing the config git reads. See [decision 0004](decisions/0004-the-hook-contract.md). |
| `handoff_tier` | hook, before-handoff | A delegated task names no tier on its first line, or sets a model or effort other than the manifest's binding for its tier, or leaves one unset that the tool lets it set. |
