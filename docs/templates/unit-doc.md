---
kind: template
last-reviewed: 2026-11-22
lane: development
---

# Unit doc template

One page per documentable unit of code, for the developer or agent writing it. Four kinds: service, library, client and infrastructure.

**In short:** pick the unit's kind and keep that kind's headings, worded as given; add headings where the unit needs them. Each page opens with what the unit owns and ends with links out. A unit of no kind gets a pointer row with a reason on its project's hub instead of a page.

## When to use it

Use it when a unit appears in a [project hub](hub.md)'s units table and has no page yet, or when a page's unit changed kind. A unit is one part of the code a reader works on as a whole. In this sample, `src/orders-api` is a service and `src/orders-web` is a client; [src](../../src/README.md) says what each folder is.

## Where copies live

As for the hub: in the project's folder, `docs/projects/<project>/`, beside its `README.md` hub, until an instance settles the [open question on adopting the workspace](../adopt-the-workspace.md#open-question-where-per-repository-reference-docs-live). Do not settle that question here. Wherever they live, a project's unit pages sit beside its hub, and each is named for its unit's folder, such as `orders-api.md`.

## Skeleton

Copy the opening and the one heading set that fits the unit's kind. Delete the other three.

```markdown
---
kind: reference
last-reviewed: YYYY-MM-DD
lane: development
---

# <Unit>: <service | library | client | infrastructure>

<One sentence, 25 words or fewer: what the unit is, and who reads this page.> Checked against <repository> at <pinned commit>.

**In short:** <what the unit owns, and the one thing a newcomer gets wrong>.

<!-- Service -->
## What it owns
## Folder layout
## Endpoints
## Data model
## Dependencies
## External calls
## Run it locally
## Gotchas
## See also

<!-- Library -->
## What it provides
## Stack
## Folder layout
## Folders whose names mislead
## Consumers
## Public contract
## Build and release
## Gotchas
## See also

<!-- Client -->
## What users do with it
## Stack
## Folder layout
## Routes
## State
## Sign-in
## Environment variables
## External calls
## Run it locally
## Build and deploy
## See also

<!-- Infrastructure -->
## Scope
## Patterns
## Conventions
## Exceptions
## Validate locally
## Gotchas
## See also
```

## What each heading holds

### Service

| Heading | Holds |
|---|---|
| What it owns | Three to six bullets: the entities, jobs, database and sign-in setup it owns. Ownership, not behavior. |
| Folder layout | One line pointing at the listing command, such as `git -C src/orders-api ls-files`. It lists the files both in a pinned repository and in this sample's checked-in folders. Then only what the listing does not tell you. Code maps are planned for M5; link the unit's map once it exists. |
| Endpoints | Only the routes a reader must know, and only when the table answers who may call each one. |
| Data model | The database per environment, the data-access layer, the key entities, and how credentials arrive. |
| Dependencies | Private package feeds first, since they stop a clean checkout from building. Then public packages, then calls to other services. |
| External calls | The systems outside the repository it calls, each with a link to where that system is documented. |
| Run it locally | The credential or network access it needs first, then the command. |
| Gotchas | A numbered list, about four to seven, so a review comment can cite one by number. |
| See also | Links out, including pipeline and deployment files kept outside the unit's folder. |

### Library

Also for a database project or a project shared between services.

| Heading | Holds |
|---|---|
| What it provides | What it gives its consumers, in their terms, and who may use it. |
| Stack | The target runtime and the major versions that shape its public surface. |
| Folder layout | One line pointing at the listing command, as for a service. |
| Folders whose names mislead | Two to six folders whose name does not say what is inside. This is the section a reader gains most from. |
| Consumers | Who depends on it, and the projects a reader would assume depend on it and do not. |
| Public contract | What consumers are coupled to, and how it reaches them. |
| Build and release | How to build from a clean checkout, what blocks the build first, and how a new version reaches consumers. |
| Gotchas | Numbered, with name collisions first. |
| See also | Links out. |

### Client

| Heading | Holds |
|---|---|
| What users do with it | Three to six bullets: the jobs a user does, in the user's words. |
| Stack | Framework, bundler, state library, component kit, sign-in library, test runner and package manager. Major versions only. |
| Folder layout | One line pointing at the listing command, as for a service. |
| Routes | A diagram of the routes, then prose on the guards. The prose is the point. |
| State | The state modules, what each owns, and which one is the source of truth where two overlap. |
| Sign-in | The provider, where the token is held, how it is attached to calls, and what happens when it expires. |
| Environment variables | A table with a notes column. Mark a variable that is declared and never read. |
| External calls | As for a service. |
| Run it locally | The real command and the real port, not the framework's default. |
| Build and deploy | A table of the pipeline's stages, then where the app is served from and how runtime settings reach it. |
| See also | Links out. |

A client page has no Gotchas heading, and adds none. This is the one exception to step 2 of [filling it in](#filling-it-in). A trap in a client goes under the heading it concerns, such as Routes or Sign-in.

### Infrastructure

| Heading | Holds |
|---|---|
| Scope | What this page covers and what it leaves to other pages. It comes first because infrastructure pages overlap. |
| Patterns | The two to four shapes the infrastructure supports, and how to tell which one a unit uses. |
| Conventions | The naming and wiring rules held by habit, not by a schema. |
| Exceptions | The units that break the conventions, and why. Keep the heading even when the list is short. |
| Validate locally | What can be checked on a developer's machine without deploying. |
| Gotchas | Numbered, usually about ordering, timing and reach. |
| See also | Links out. |

## Units that get no page

A unit that is none of the four kinds gets no page. It gets a pointer row on its project's hub, with the reason in the row. Such units include:

- a folder that holds only a container file;
- a single pipeline script;
- a library nothing references;
- another team's unit;
- a folder of files that are not code;
- a shelved unit kept for audits, such as `src/orders-service-v1`.

Every unit is in one of three states. It has a page, or a pointer row with a reason, or it is missing from the hub. A missing unit is a gap. Close it with a page or a row before the commit.

## Filling it in

1. **Pick the kind** from what the unit does, not from its folder name. If none fits, write a pointer row instead.
2. **Keep the kind's headings, worded as given.** Add headings where the unit needs them, except a Gotchas heading on a client page. Keep a heading with nothing under it, and write "none" there, such as Endpoints on a service with no route a reader must know.
3. **Paste no folder trees.** The listing command gives the tree; the page gives what the tree hides.
4. **Write only gotchas a search would not find.** A gotcha that `git grep` or `python3 tools/symbols.py NAME src` turns up in a minute does not belong.
5. **Run every command under "Run it locally" before you commit the page,** on a clean checkout where you can. Fix the page if one fails.
6. **Check the length.** A page shorter than about 90 lines or longer than about 200 is a sign to look again: a missing section, or a pasted list. It is not a failure.
7. **Check it against the pinned commit** the opening names, and move that commit when you check again.

## Rules

| Rule | Enforced by |
|---|---|
| A unit page carries its kind's full heading set, worded as given. No check reads headings yet: a coverage check is planned for M5. Until then the author holds this, and a copy under `docs/` gets an [instruction review](../playbooks/instruction-review.md) like any guidance page. | `prose` |
| Every unit has a page or a pointer row with a reason on its hub. | `prose` |
| A page pastes no folder tree. | `prose` |
| A gotcha is one a search of the code would not find. | `prose` |
| A route table appears only where it says who may call each route. | `prose` |
| Every command under "Run it locally" has been run before the page is committed. | `prose` |
