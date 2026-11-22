---
kind: decision
status: accepted
last-reviewed: 2026-11-21
---

# 0004: The hook contract

**In short:** a part reads only its event, its config and a snapshot. Whatever it needs from files, git, the environment or another process, the engine works out and hands it in. A path in an event is placed by the working copy that holds it. The table below names each part that reaches further, and a test fails on any other. An agent's write into a git folder or to a git config file is refused when an edit tool makes it or the shell parser reports it. A `git config` command is judged by its key instead, and refused for the keys "The rules the shell guards share" lists. Other git commands that change config, such as `git remote set-url`, are not seen; the README lists them. The discard and push guards judge a git alias as what it runs.

## Context

Until M2, every hook was a pure function of its event: a command line, a path or a prompt. M2 adds hooks that need more. The stale-page notice needs the pages, the stale-pin notice needs git and the network, and the writing-session lease in slice 4 needs session identity and process liveness.

A hook that reaches for these itself is hard to test and easy to get wrong. The walled reader's survey of the work workspace found the traps it hit:

- **A path judged by the project folder lands in the wrong place.** In a worktree session, the project folder still names the main copy, and the hooks run from the main copy's files. The `shelved` hook missed every edit inside a linked worktree.
- **Git variables leak.** A hook that runs inside a git operation inherits `GIT_DIR` and `GIT_INDEX_FILE`. Its own git calls then act on the wrong repository.
- **A fetch can hang a session.** A fetch that asks for credentials waits for an answer nobody gives.
- **A session start that fails is worse than one that says nothing.**

## Decision

**What a part may read.**

- A **check** reads its snapshot: the files, the staged paths, the ledger, the pushed commits and the pin facts.
- A **hook** reads its event. A session hook may also declare `NEEDS`, and the runner adds those facts to the event before calling it:
  - `"findings"`: the findings of the check the hook's config names in `"part"`, run on the session's own working copy.
  - `"pins"`: for each pinned repository in that working copy, its upstream's default branch and how many commits the checkout is behind.
- A **before-shell hook** may declare `NEEDS` too. Its facts are in "Shell events" below.
- A **before-edit hook** may declare `"git_config"`, amended 2026-11-21 by M3 slice C5c: the same fact a before-shell hook gets, described in "Shell events" below, read once for the tool call.
- An **after-edit hook** and a **stop hook** may declare `NEEDS` too, amended 2026-11-21 by M3 slice C5a. Their facts are in "After-edit and stop events" below.
- Both read their config.
- Parts may import only these modules: `re`, `json`, `datetime`, `hashlib`, `math`, `posixpath`, `shlex`, `unicodedata`, and from the engine `wslib.parts`, `wslib.markdown` and `wslib.symbols`.
- They may not use `open`, `exec`, `eval`, `compile`, `__import__`, `__builtins__`, `globals`, `vars`, `getattr`, `setattr`, `breakpoint` or `input`, or reach a double-underscore attribute other than `__name__`. Amended 2026-11-17, after the M2 red team: a list of what is banned missed `codecs`, `builtins`, `importlib`, `ctypes`, `linecache` and the engine's own git module, so the test now holds parts to a list of what is allowed.

**Where the engine does the rest.**

- **Git** runs in `wslib/gitcall.py`. Every call strips the variables git sets for a hook, turns off credential prompts, and stops at a time limit enforced in Python. A call that fails or times out returns nothing, and the caller decides what that means.
- **The snapshot** reads files: the working folder, the staged commit, or a case.
- **The stop gate's runs** of the check and the tests, amended 2026-11-21 by M3 slice C5a, start in `wslib/gate.py`, with the variables git sets for a hook stripped, nothing on standard input, and one deadline.

**How a path is placed.** A before-edit event carries four fields:

| Field | Holds |
|---|---|
| `path` | The path relative to the working copy of this repository that holds the file, whether the main copy or a linked worktree, wherever it sits. A file in no working copy of this repository keeps its absolute path. |
| `working_copy` | That working copy's top folder, or nothing. |
| `main` | Whether that is the main working copy. |
| `absolute` | The absolute path. The ledger records the edit by it, in the ledger of the working copy that holds the file. |

The path is resolved first: a relative path from the tool's folder, `..` removed, symbolic links followed, and a file that does not exist yet placed through its folders. On a case-insensitive file system, the file system decides what is inside a working copy, not the text of the path.

**Shell events.** A before-shell event carries `command`. A hook that decides by where a command acts declares what it needs, and the runner adds those facts. Each is worked out by the engine, never by the part, and each can come back unresolved with a reason. A guard refuses a command whose fact it needs is unresolved.

| Need | What the runner adds |
|---|---|
| `"session"` | `session` and `pid`: the session id from the tool's payload and the agent tool's process id, read as [decision 0005](0005-concurrent-sessions-and-the-edit-ledger.md) reads them for the lease. `cwd`, the folder the tool says the session runs in, and `own_working_copy`, the top folder of the working copy that holds it. The workspace's own event shape may carry `session`, `pid` and `cwd`. |
| `"lease"` | `lease`: the writing-session lease as it stands, read without taking or changing it. `state` is `free`, `mine`, `other-live`, `other-dead` or `unknown`, with the holder's session, process id and when it was taken. A lease file that cannot be read, or a corrupt one, is `unknown`, and a guard treats it as `other-live`. "Another live session is on record" means `other-live`. A session in a worktree takes no lease, so it never shows here. |
| `"working_copies"` | `working_copies`: for each folder a git call in the command acts on, its kind and top folder, as below. |
| `"targets"` | `targets`: for each gh call and each `git push` in the command, where it really goes, as below. |
| `"aliases"` | `aliases`: for the folder of each git call whose subcommand is not one of git's own, the aliases git config defines there, read at hook time with `git config --get-regexp`. Each is `{"aliases": {name: expansion}}`, or `{"unresolved": why}` when git fails or runs past its time limit. A call whose folder the parser could not place gets nothing. Amended 2026-11-21, M3 slice C5c. |
| `"git_config"` | `git_config`: `home`, the home folder, and `files`, every git config file a write must not reach: `~/.gitconfig`, `$XDG_CONFIG_HOME/git/config`, `~/.config/git/config`, `GIT_CONFIG_GLOBAL` and the system file, `GIT_CONFIG_SYSTEM` or the one `git var GIT_CONFIG_SYSTEM` names, whether each exists or not, and every file an `include.path` or `includeIf.*.path` names in the config read from the session's folder, each also by its real path when it is a symbolic link. `unresolved` says why the includes could not be read, when git fails, cannot parse the config or runs past its time limit; the global files are listed even then. This fact is an exception to the rule above: `git_folder` and `git_folder_shell` do not refuse while it is unresolved, since every write would then be refused, so an include they could not read is not seen. Amended 2026-11-21, M3 slice C5c. |

A guard reads the command with the shared parser, `wslib/shell.py`, and looks each call's facts up by the text the parser gives: a git call's folder, as `analyze` reports it, keys `working_copies`. The runner keys its facts by the same text from the same parser call. A call whose key has no fact counts as unresolved, so a disagreement between the two refuses instead of passing.

Each folder in `working_copies`:

- **The folder** is the parser's folder for that call: `--git-dir` or `GIT_DIR`, else `--work-tree` or `GIT_WORK_TREE`, else the folder after a leading `cd` or `pushd`, `env -C` and every `-C`. It starts from the event's `cwd`. A `cd` that is not the leading command, a `cd` inside a subshell, `core.worktree`, `GIT_INDEX_FILE`, `GIT_COMMON_DIR` and a variable in any of these leave it unresolved, as the parser reports.
- **The kind** is `main`, `linked` or `other`. The engine asks git for the folder's git folder and common git folder. It is `main` when the two are the same folder and the common folder is this workspace's; `linked` when the common folder is this workspace's and the two differ; `other` for any other repository or no repository. A git call that fails or times out leaves the kind unresolved.
- It also gives the working copy's top folder.
- For `git worktree remove`, the operand joined to the call's folder is keyed too, so a guard can tell another session's worktree from the session's own.

Each entry in `targets`, keyed by the call's folder and its words as the parser gives them, holds a list of destinations, each with `host`, `owner` and `name`, or a local path with `local: true`. An empty list with a reason means unresolved.

- **`gh api`.** The literal owner and repository in the path. A `{owner}` or `{repo}` placeholder is filled from `GH_REPO`, then from gh's set-default value, then from the only remote. A path that names no repository gives no target, and a guard counts a write there as going to an unlisted repository.
- **Every other gh call.** `-R` or `--repo`, then `GH_REPO`, then gh's set-default value, then the only remote. With two or more remotes and no default set, the target is unresolved, since gh then picks a remote by rules of its own. A gh call that names no repository at all, such as a gist, gives no target, and a guard counts a write as going to an unlisted repository.
- **gh's set-default value** is read from git config, where `gh repo set-default` writes it under the remote's `gh-resolved` key (inferred from gh's behaviour, not probed: the command refuses a repository it cannot reach). gh's folder follows the parser's folder rules above. Remote URLs are read for host, owner and repository.
- **`git push`.** Every URL git would really push to. The engine asks git wherever git can answer: `git remote get-url --push --all` and `git config`, run in the resolved folder with the command's own `-c` and `GIT_CONFIG_*` values added, so `pushurl`, `insteadOf`, `pushInsteadOf`, `remote.pushDefault` and `include` and `includeIf` files are applied by git itself. Only for a URL typed on the command line does the engine apply the longest matching `insteadOf` prefix itself, since git applies no `pushInsteadOf` there. With no refspec, it models `push.default` and the branch's upstream to say which branch goes where. Every destination a push reaches is listed, a remote with two push URLs giving both. Anything the engine does not model is unresolved.
- **A local destination.** A local path or a `file://` URL, read by git's rules, where `host:path` is ssh, counts as inside the instance.

The facts are worked out only for a hook that needs them, only for the git and gh calls the command holds, through `wslib/gitcall.py` and its time limit. A fact the limit cuts off is unresolved. `git_config` is worked out only when a hook reads it: the shell guard on git folders reads it only for a command that writes a file or a guarded config key.

**The rules the shell guards share.** Amended 2026-11-21, M3 slice C5c. `wslib/gitrules.py` holds what every guard that judges a git command must decide the same way. It is pure: it reads the event and the parser's output, never a file or git.

- **The keys A0 lists**, which `guarded_key` in `wslib/shell.py` holds: `remote.*`, `url.*`, `push.*`, `include.*`, `includeIf.*`, `alias.*`, `branch.*.pushRemote`, `branch.*.merge`, `remote.pushDefault`, `core.worktree` and `core.sshCommand`, and any key that cannot be read.
- **Aliases.** A guard reads the command through `gitrules.read`, which expands each git alias from the `aliases` fact, only for a name that is not one of git's own commands. An alias that starts with `!` is unresolved, and so is a subcommand that is neither built in nor an alias at hook time, an alias whose folder's aliases were not read, and an alias read from config that the same command changes with `HOME`, `XDG_CONFIG_HOME`, `GIT_CONFIG_GLOBAL`, `GIT_CONFIG_SYSTEM`, `GIT_CONFIG_NOSYSTEM` or an include. Git runs a program named `git-NAME` on the path before an alias of that name; the guard does not look for one, so it judges the alias.
- **Arguments supplied at run time.** Arguments that `xargs` or `find -exec` supply make a call unresolved for the guard that decides on it.
- **Config writes on a call a guard decides on.** `HOME`, `XDG_CONFIG_HOME`, `GIT_CONFIG_GLOBAL`, `GIT_CONFIG_SYSTEM` and `GIT_CONFIG_NOSYSTEM` set on it, and an include or an unreadable key given by `-c`, `--config-env` or `GIT_CONFIG_*`, count as config writes. `gitrules.config_write` can also count every key A0 lists, except `alias.*`, which the parser expands, so the call is judged as what the alias runs. That option is for the guards that decide by where a push goes, which slices C5d and C5e add; no guard uses it yet, so `push_lease` passes `git -c remote.origin.pushurl=URL push` from a linked worktree.
- **The git folder and git config files.** A write under any `.git` path segment, and a write to a file in `git_config`, is refused, by an edit tool and by a shell write the parser reports. A `git config` write is judged by its key instead, whatever file it writes: one that sets, unsets, edits, renames or removes a key A0 lists, in any scope, is refused, since that rewrites a config file every guard reads, and `git config --global user.email` passes.

**The worktree's settings copy.** The agent tools' local settings file, `.claude/settings.local.json`, is ignored by git, so `git worktree add` leaves it behind and a session in the new worktree runs without its local permissions. A `post-checkout` git hook, wired in `.githooks/` through the launcher, copies it from the main working copy into a new linked worktree. It acts only on the checkout `git worktree add` makes, where the previous head is all zeros. It never overwrites a file already there, and it never fails the checkout: on any error it prints one line and exits 0.

**Session events.** `session-start` and `session-end` carry `session`, `cwd` and `tool`. A hook on them must set `MODE = "remind"`. A session start or end never fails: on any error the runner prints nothing and exits 0, and the wiring adds `|| exit 0`.

**After-edit and stop events.** Amended 2026-11-21, M3 slice C5a. Both agent tools send a hook after an edit tool has written a file, and when the agent tries to finish its turn. A recorded run of each, `tests/records/after-edit-and-stop.json`, shows what they send.

- **`after-edit`** carries the same fields as `before-edit`, placed the same way, read from the tool's `PostToolUse` payload for the same edit tools. A hook on it must set `MODE = "remind"`, since the edit is already made; loading a part refuses any other mode. It may declare one need, `"index"`: the runner reads the index file the hook's config names in `"index"`, `INDEX.md` by default, fresh, from the working copy that holds the edited file. A file it cannot read, or an edit in no working copy of this repository, gives `None`. The reminder goes back as `additionalContext`, which both tools showed the agent in the recorded run.
- **`stop`** carries `session`, `cwd` and `tool`, as a session event does, and `stop_hook_active`, which both tools set on the stop that follows one a stop hook refused. A stop hook may refuse. The runner then replies `"decision": "block"` with the reason, which both tools took as a refusal and showed the agent in the recorded run. On a stop with `stop_hook_active` set, the runner turns any refusal into a report and the session stops, so a stop is refused at most once in a row. The report goes back as `systemMessage`, the field both tools' hook replies take for a message to the person; the recorded run did not exercise it, so that either tool shows it is inferred.
- A stop hook may declare two needs. `"own_edits"`: for each working copy of this repository, the paths its edit ledger holds for this session, read from the ledger files. `"gate"`: the result of running `python3 ws.py check` and the fast tests the hook's config names in `"tests"`, in each working copy that holds the session's entries, with one deadline of 18 seconds across every run. Each run is `passed`, `failed`, `timed-out` or `error`, with the end of its output. The runner works out `"gate"` only when a hook reads it, so a session with no entries of its own runs nothing. When an edit ledger cannot be read, `"own_edits"` holds one entry with no working copy and `"gate"` is `None`, so the stop gate refuses once and runs nothing.
- Neither event ever fails: on any error the runner prints nothing and exits 0, and the wiring adds `|| exit 0`. A broken stop hook lets the session stop.

**How cases supply all of this.** A hook case gives the whole event, the added facts included. A check case gives the snapshot's state: `"files"`, `"staged"`, `"ledger"`, `"pushed"` and `"pins"`. Tests that need real git build throwaway repositories, with local fixture upstreams and never the network.

**The exceptions.** Each part below reaches further, for the reason given. A test reads this table, and fails on any part that reaches outside its event, config and snapshot without a row here.

| Part | May use, and why |
|---|---|
| `deny_list` | `os`, `open`, `codecs`, `wslib.snapshot`: it reads the private list from the file `WS_DENY_LIST` names, outside the repository, which no snapshot holds, decodes it, and checks a commit message as a one-file snapshot. |
| `no_admin_merge` | `wslib.shell`: it reads the command line with the shell parser it shares with `no_stage_all`, instead of a copy, so both hooks follow the same separators, wrappers and quoting, and reads a `gh api` call's method and fields from it. The eval hash covers that module wherever a case grades a hook. |
| `eval_record` | `types`, `exec`, `compile`, `__dict__`: it loads `evals/proofkeys.py` from the snapshot's text, as `grade.py` loads a hook's file, so the proof keys it strips before hashing are exactly those the eval runner strips (decision record 0006). |
| `page_kinds` | `types`, `exec`, `compile`, `__dict__`: it loads the same file from the snapshot, to refuse a proof key in any form but its exact one. |
| `proof` | `types`, `exec`, `compile`, `__dict__`: it reads the proof marks through the same file. It also asks the snapshot for the base commit's files, other commits' files and ancestry, which the engine reads with git (`wslib/snapshot.py`). |
| `no_stage_all` | `wslib.shell`: the same shared parser. The eval grader runs this hook, so the module it imports is hashed with it and a change to the parser stales the eval records it could change. |
| `no_discard` | `wslib.shell`: the same shared parser, to find each git call and the folder its facts are keyed by. The eval hashes no case that grades this hook, so a parser gap it finds is handled in its own file until slice Z. `wslib.gitrules`: the rules on aliases, unresolved calls and config writes the shell guards share. |
| `push_lease` | `wslib.shell`: the same shared parser, to find each `git push` and the folder its facts are keyed by, as `no_discard` does. `wslib.gitrules`: the rules on aliases, unresolved calls and config writes the shell guards share. |
| `git_folder` | `wslib.gitrules`: the rules on the git folder and git config files, shared with `git_folder_shell`, so an edit tool and the shell are judged alike. |
| `git_folder_shell` | `wslib.gitrules`: the same rules, applied to each write and each `git config` write the shared parser reports. |

Amended 2026-11-18, M3 slice A3: the snapshot gained the history the proof checks judge a change by (the base commit's files, a commit's files, ancestry and the manifest's `building` list when a file was added), read by the engine in a fixed number of git processes; and three parts load `evals/proofkeys.py` from the snapshot, as the table says.

Amended 2026-11-18, M3 slice A0: the parser moved from `no_stage_all.py` into `wslib/shell.py`, with the eval hash extended to it, so `no_admin_merge` no longer loads another part's file with `exec`.

Amended 2026-11-21, M3 slice C3: before-shell hooks may declare `NEEDS`, and the runner adds the session, the lease as it stands, each git call's working copy and each gh call's and push's target, as "Shell events" says. The discard guard reads the command with `wslib/shell.py`, as its row in the table says. A `post-checkout` git hook copies the local settings file into a new linked worktree.

Amended 2026-11-21, M3 slice C4: the table gained `push_lease`, which uses the shared parser as `no_discard` does, and `no_admin_merge`'s row now says it reads a `gh api` call's method and fields from the parser.

Amended 2026-11-21, M3 slice C5a: the `after-edit` and `stop` events, their payloads, their needs, `"index"`, `"own_edits"` and `"gate"`, and the rule that a stop is refused at most once in a row. The gate's runs of the check and the tests are the engine's, in `wslib/gate.py`, like its git calls.

Amended 2026-11-21, M3 slice B1: a check's `pushed` commits carry their whole message, their tree as `files`, read when a part asks, and whether a merge is being made. The commit-msg hook gives a check the commit being made in that shape, and `ws.py check --commits BASE..HEAD` runs the commit-message checks over each commit of a range, for CI. The pre-push hook also runs the runnable blocks of each tutorial a push to main changes, in a fresh clone. An exception to `wslib/gitcall.py`: these reads of commits, like the runner's other reads at the push, call git directly. They read only local objects; the tutorial's clone and checkout have a time limit.

Amended 2026-11-21, M3 slice C5c: two before-shell needs, `aliases` and `git_config`, and `git_config` on before-edit too; `wslib/gitrules.py`, the rules the shell guards share, which `no_discard`, `push_lease`, `git_folder` and `git_folder_shell` import, as their rows say. A parser gap found here is handled in `wslib/gitrules.py`, outside the eval's hash, until slice Z: `unlink`, `rmdir` and `shred` as writes, and `find -delete`.

Amended 2026-11-22, M3 slice C5c: the In short line names the writes to a git folder and to git config files that the guards refuse, as [the layout](../layout.md#the-opening) allows an amendment to do. A limit its review found: `git_folder_shell` does not read the `aliases` fact, so a call through an alias that runs `git config`, such as `cf = config`, passes it, and `git cf remote.origin.url URL` changes a key it refuses by name. An agent can store such an alias in a file no guard watches, with `git config --file`, and point git at it with `GIT_CONFIG_GLOBAL` or `HOME`. `no_discard` and `push_lease` refuse that call only while another live session holds the lease. Whether `git_folder_shell` reads aliases is queued for the maintainer as Q17.

## What it gave up

- **A hook cannot look things up for itself.** A new kind of fact means an engine change, a new name in `NEEDS` and a line in this record. That is the point, and also the cost.
- **The engine's facts cost time at session start.** The pins need one fetch per pinned repository, ten seconds at most each.
- **Shell facts cost time on every guarded command.** A git or gh call in a command adds a few git processes before the command runs. A fact cut off by the time limit is unresolved, and the guard refuses, so a slow machine can see a refusal a fast one would not. The refusal says to run the command again.
- **The stop gate costs time at each stop.** Amended 2026-11-21, M3 slice C5a. A session with edits of its own waits for the check and the fast tests, up to 20 seconds, every time it tries to finish while those entries are in a ledger.
- **The target is git's and gh's answer at hook time.** A command that changes a remote, a default or a config value earlier in the same line acts on a target the runner did not see. The guards count those as unresolved.

## Rejected

- **Giving hooks a git function to call.** A function cannot be written into a case file, so its hooks could not be tested with data.
- **Placing paths by the project folder.** It is the main copy's folder even in a worktree session.
- **Listing the command forms that push or write elsewhere.** A list of forms misses `pushInsteadOf`, a second push URL or a set-default value. The engine asks git and gh's own configuration where the command really goes.
- **Handing the guard the parser's whole output.** A case would have to write that output by hand, and would stop testing the guard together with the parser. Facts keyed by the parser's own text keep cases short, and a key with no fact refuses.
