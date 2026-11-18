---
status: accepted
last-reviewed: 2026-11-18
---

# 0004: The hook contract

**In short:** a part reads only its event, its config and a snapshot. Whatever it needs from files, git, the environment or another process, the engine works out and hands it in. A path in an event is placed by the working copy that holds it. The table below names each part that reaches further, and a test fails on any other.

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
- Both read their config.
- Parts may import only these modules: `re`, `json`, `datetime`, `hashlib`, `math`, `posixpath`, `shlex`, `unicodedata`, and from the engine `wslib.parts`, `wslib.markdown` and `wslib.symbols`.
- They may not use `open`, `exec`, `eval`, `compile`, `__import__`, `__builtins__`, `globals`, `vars`, `getattr`, `setattr`, `breakpoint` or `input`, or reach a double-underscore attribute other than `__name__`. Amended 2026-11-17, after the M2 red team: a list of what is banned missed `codecs`, `builtins`, `importlib`, `ctypes`, `linecache` and the engine's own git module, so the test now holds parts to a list of what is allowed.

**Where the engine does the rest.**

- **Git** runs in `wslib/gitcall.py`. Every call strips the variables git sets for a hook, turns off credential prompts, and stops at a time limit enforced in Python. A call that fails or times out returns nothing, and the caller decides what that means.
- **The snapshot** reads files: the working folder, the staged commit, or a case.

**How a path is placed.** A before-edit event carries four fields:

| Field | Holds |
|---|---|
| `path` | The path relative to the working copy of this repository that holds the file, whether the main copy or a linked worktree, wherever it sits. A file in no working copy of this repository keeps its absolute path. |
| `working_copy` | That working copy's top folder, or nothing. |
| `main` | Whether that is the main working copy. |
| `absolute` | The absolute path. The ledger records the edit by it, in the ledger of the working copy that holds the file. |

The path is resolved first: a relative path from the tool's folder, `..` removed, symbolic links followed, and a file that does not exist yet placed through its folders. On a case-insensitive file system, the file system decides what is inside a working copy, not the text of the path.

**Session events.** `session-start` and `session-end` carry `session`, `cwd` and `tool`. A hook on them must set `MODE = "remind"`. A session start or end never fails: on any error the runner prints nothing and exits 0, and the wiring adds `|| exit 0`.

**How cases supply all of this.** A hook case gives the whole event, the added facts included. A check case gives the snapshot's state: `"files"`, `"staged"`, `"ledger"`, `"pushed"` and `"pins"`. Tests that need real git build throwaway repositories, with local fixture upstreams and never the network.

**The exceptions.** Each part below reaches further, for the reason given. A test reads this table, and fails on any part that reaches outside its event, config and snapshot without a row here.

| Part | May use, and why |
|---|---|
| `deny_list` | `os`, `open`, `codecs`, `wslib.snapshot`: it reads the private list from the file `WS_DENY_LIST` names, outside the repository, which no snapshot holds, decodes it, and checks a commit message as a one-file snapshot. |
| `no_admin_merge` | `wslib.shell`: it reads the command line with the shell parser it shares with `no_stage_all`, instead of a copy, so both hooks follow the same separators, wrappers and quoting. The eval hash covers that module wherever a case grades a hook. |
| `no_stage_all` | `wslib.shell`: the same shared parser. The eval grader runs this hook, so the module it imports is hashed with it and a change to the parser stales the eval records it could change. |

Amended 2026-11-18, M3 slice A0: the parser moved from `no_stage_all.py` into `wslib/shell.py`, with the eval hash extended to it, so `no_admin_merge` no longer loads another part's file with `exec`.

## What it gave up

- **A hook cannot look things up for itself.** A new kind of fact means an engine change, a new name in `NEEDS` and a line in this record. That is the point, and also the cost.
- **The engine's facts cost time at session start.** The pins need one fetch per pinned repository, ten seconds at most each.

## Rejected

- **Giving hooks a git function to call.** A function cannot be written into a case file, so its hooks could not be tested with data.
- **Placing paths by the project folder.** It is the main copy's folder even in a worktree session.
