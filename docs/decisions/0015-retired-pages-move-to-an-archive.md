---
kind: decision
status: accepted
date: 2026-11-23
deciders: the maintainer, through M3's approved plan
last-reviewed: 2026-11-23
---

# 0015: Retired pages move to an archive that search does not see

**In short:** a page no longer in use moves under `archive/` in this repository, with a tombstone at its old path where layout allows one. An ignore file hides the folder from search, and the link and page checks skip it. A plain recursive search still finds it.

## Context

A retired page that stays where it was keeps turning up in searches, and an agent reads it as current. A status line in its front matter does not stop that: front matter is a convention an agent may not read, while a page search does not return is one the agent never sees.

Deleting the page loses what it said, and moving it to another repository makes it hard to find when someone needs the history.

## Decision

- **Move it under `archive/`,** keeping its path below the folder, as [layout](../layout.md#archiving-a-page) says, and leave a tombstone at the old path. By exception, a page archived from a kind's own folder, such as `docs/playbooks/`, leaves none, since that folder takes no reference page but its README.
- **Hide the folder.** The `.ignore` file at the top of the repository names `archive/`, so search tools that read it skip the folder. The `links` and `page_kinds` checks skip it too.
- **The known bypass is accepted.** A search that does not read ignore files, such as a plain recursive `grep`, still finds archived pages. The folder's name, and a tombstone where there is one, tell a reader what they found.

## What it gave up

- **The lock is partial.** It holds for the search tools agents usually run, not for every tool.
- **Archived pages are not checked.** A link in one may break, and nothing reports it.

## Options rejected

- **A separate repository for retired pages, now.** It would hide them fully, at the cost of a second repository to keep and search. It stays possible if the archive grows.
- **A status key alone.** It marks the page without keeping it out of a search.
