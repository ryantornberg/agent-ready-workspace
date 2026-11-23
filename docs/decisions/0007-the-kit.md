---
kind: decision
status: accepted
last-reviewed: 2026-11-23
---

# 0007: The kit

**In short:** `python3 ws.py adopt PATH` makes an instance of this workspace, and the kit classes each file it holds. Synced files belong to the kit, and an upgrade replaces them; seeded files are written once and then belong to the instance; never-synced files stay here. An instance's lock records each file's hash and each synced page's proof state, so the checks can tell a hand edit from an upgrade, and a kit page's proof from the instance's own. Two kill rules say when to stop syncing a page, and when to stop keeping a kit at all.

## Context

A team that copies this repository by hand gets every file at once, its history and its proof included, and no way to take a later fix. [Adopt the workspace](../adopt-the-workspace.md) described that copy; it named the kit as planned.

An upgrade needs ownership. If the kit may overwrite any file, a team's own facts are lost. If it may overwrite none, a fixed hook never reaches the team. So each file needs one owner, and the instance needs a record of what the kit gave it.

The proof checks of [decision 0006](0006-what-proven-means.md) read milestone records, eval records and anchor commits. Those are this workspace's history, and an instance does not get them. Without a rule, the checks in an instance would either fail every page the kit proved, or check nothing.

## Decision

**Three classes.** `kit/kit.json`, in the kit's repository, holds an ordered list of rules. The first rule whose path is a tracked file, or a folder that holds it, gives the file its class. A file no rule matches stops `adopt`, and a test in this repository fails on it.

| Class | What | What happens to it |
|---|---|---|
| Synced | The engine, the parts and their cases, `tools/`, the git hooks, the agent tools' wiring and pointer files, the eval harness, and the pages under `docs/` that the next rows do not name: the procedures, how-tos, references, templates and these decision records | `adopt` copies it. `upgrade` replaces it. The `kit_drift` check and `ws.py drift` fail on a hand edit to it. |
| Seeded | The contract and Claude Code's pointer to it, the index, the manifest, the sample code under `src/`, the rule pages, the glossary, the feature layer walk, whose lists of layers each instance rewrites, the question log, the records folder's map and empty registers, the eval's arms file and two-line text, the README, the eval page, the CI workflow, the licence, and the ignore and attributes files | `adopt` writes it once. From then on the instance owns it, and no check compares it with the kit. |
| Never synced | This workspace's plans, milestone records, other records, eval cases and recordings, tests, CI workflows, change log, evidence page, archive, the README's images, its outward-write list, and the kit's own folder, `kit/` | `adopt` does not copy it. It stays here. |

A seeded file starts as one of three things. It is a copy of this repository's file, such as the sample code, which the README's steps then replace. It is a seed file under `kit/seed/`, written to its path in the instance, such as the README, the eval page and the CI workflow, since this repository's own describe its history and its tests. Or it is a copy with changes the rule names: its tables emptied (the question log, the review index), the table rows that name a never-synced path dropped (the index), a named row dropped (the contract), or, for the manifest, `building` emptied and the review index's required list cleared. The contract keeps its invented facts, which the README's steps replace, and loses its rule that an edit to it needs an eval run, since an instance has no eval case until it writes one. The instance's eval page says to add the rule back once the instance proves a page of its own. The instance's outward-write list is written empty: agents write to no repository until a person adds one.

**The manifest and the lock.** `python3 ws.py kit` prints the kit manifest. It lists every file git tracks, with its class and its hash, `sha256:` and the hex digest, read with CRLF as LF and without a leading byte-order mark, so it names every seeded item. It reads each file as the working copy holds it; a file git does not track is not in the kit. It holds the kit version and commit, the proof state of every synced page and section, and the names of the kit's eval cases. `adopt` and `upgrade` write it into the instance as `kit.lock.json`.

**Drift.** In an instance, the `kit_drift` check fails a synced file whose hash no longer matches the lock, or that is gone. `python3 ws.py drift` reports the same. The way out is to put the kit's copy back, or to keep the instance's own with `python3 ws.py drift --keep PATH`, which marks the file kept in the lock. A kept file belongs to the instance from then on: `kit_drift` no longer compares it, upgrades leave it alone, and the other checks hold it as the instance's own page. `--keep` refuses a page the kit marks proven, since its proof rests on the kit's text and records; the instance writes its own steps on a page of its own instead.

**Upgrade.** `python3 ws.py upgrade PATH`, run from a newer kit, refuses while any synced file has drifted, and refuses a new synced file whose path the instance already uses for a file of its own. Either refusal changes nothing. Otherwise it replaces each synced file, adds the new ones, deletes each one the kit no longer ships or now classes never synced, leaves one it now classes seeded to the instance, writes any new seeded file that is absent, sets the instance manifest's `version` to the engine's, and writes the new lock. Its report names each new part, which runs only once a person adds it to the instance's `workspace.json`. That changes the engine and the manifest's version in one step, as [decision 0003](0003-the-engine-in-one-folder.md) requires, so it runs from a terminal or on a branch.

**Committing the kit's text.** An instance's first commit, and the commit of an upgrade, bring guidance pages that the kit's own instruction reviews read. Such a commit carries `Instructions-review: skipped: as the kit wrote it`. The `review_trailer` check accepts that reason only when each guidance page the commit leaves in place matches the hash the commit's lock holds for it, and each page it deletes is one the lock no longer holds. A page the instance changed needs its own review. When an upgrade changes a synced page's proof state, the README's table must change in the same commit, so that commit also names a review record that covers the README; the check judges the README by that record and the rest by the lock.

**Proof in an instance.** A synced page's proof marks are the kit's. When they equal the lock's, the `proof` check applies none of its evidence rules to the page: the records behind them stay here. When they differ, it fails, as drift does. `eval_record` does not gate a page the lock marks proven, with or without a case of the instance's own. `rules` accepts an `eval:` tag that names one of the kit's cases. A page the instance owns, a kept one included, is held to every rule of decision 0006. The seed README's table of proven and unproven pages is filled when the instance is made: a row for each synced page from the lock, and a row for each seeded page that carries a proof mark, which is the instance's own from the start. Such a page's `prove-by` names a milestone of the kit's plan until the instance sets one of its own, and the `proof` check reads it against the instance's own milestone records, as adopt the workspace's row on milestone state says.

**Kill rules.** They keep the kit honest about whether syncing pays.

- When three instances keep their own copy of the same synced procedure within one quarter, that procedure becomes seeded at the next kit version: the kit's copy is not fitting real teams. A kept entry in an instance's lock is one such copy.
- When no instance outside this repository's maintainer adopts the kit within two quarters of its first release, the kit becomes a plain template: `adopt`, `drift`, `upgrade`, the lock and the classes are retired, and a team copies the repository as before. The count starts at the tag `v0.4.0`.

The maintainer counts at each quarter's end, from the instances they know of: those that told them, and those whose repository they can read. An instance that tells no one is not counted, so both rules can fire on a count that is too low. A team that wants the kit kept, or a procedure kept synced, says so to the maintainer.

Either rule, when it fires, is recorded as a dated "Amended" paragraph here.

## What it gave up

- **An upgrade does not merge.** A synced file edited by hand blocks the upgrade until it is restored or kept, and a kept file no longer gets the kit's fixes.
- **A seeded file never hears from the kit again.** A fix to the seed README, or a new line in `.gitignore`, does not reach an instance made before it.
- **A path can collide.** When a later kit ships a synced file at a path the instance already uses, such as the next decision record number, the upgrade refuses until the instance renames its own file.
- **A new part does not run by itself.** The manifest is seeded, so an upgrade copies a new part's file but leaves it out of the manifest. Until a person adds it, it guards nothing, and a synced page that tags a rule with it fails the `rules` check.
- **The upgrade sets the manifest's version without reading the rest of it.** Decision 0003 ties the version to what the manifest's settings mean. When a kit version changes what a setting means, the kit's change log says so, and the upgrade's report tells the person to read it before committing; nothing checks that they did.
- **Proof in an instance is the kit's, not the instance's.** A page the kit proved was proven against the kit's contract and index. Once the instance replaces those, the kit's runs no longer test what its agents read; the seed README and eval page say so.
- **The eval gates nothing in a new instance.** Its contract and index can change with no eval run until the instance proves a page of its own, with cases of its own. The kit's cases test the kit's invented order system, so running them there would gate the samples, not the team's guidance.
- **The lock is a file the instance can edit.** Changing a hash in it hides a drift from the check. The lock is a machinery path, so the change reaches main only through a pull request, where it shows in the diff.
- **The README's proof table can go stale.** An upgrade that changes a page's proof state leaves the instance's README as it was. The `proof` check then names each row whose state no longer matches, and the upgrade's commit corrects it under a review record of its own; a row whose milestone changed it does not catch.

## Rejected

- **Hashes for every file committed in this repository.** Every edit to a synced page would also change the manifest file, and the parallel sessions that build pages would conflict on it at every merge. The manifest is built from the working copy instead, when an instance is made or upgraded.
- **Drift as a command only.** An edit would surface only when someone ran it, or at the next upgrade. As a check, it fails at the commit and in CI, and `--keep` still lets an instance diverge on record.
- **Copying the contract and the index as never synced, with nothing in their place.** The instance's checks need a contract and an index to pass, and the README's steps start from the sample's and replace its facts.
- **Taking the kit's tests and CI into the instance.** They test the kit, and read this workspace's plans and records. CI here runs them on three systems for each kit version; the instance's seeded CI runs its own checks and the drift check.

## Credit

The kit's shape follows the packager of AWS's AI-Driven Development Life Cycle workflows (`awslabs/aidlc-workflows`, MIT No Attribution licence), read at commit `e540ba7` on 2026-11-23: its distribution manifests, its tier projection, its per-tool binding filter and its upgrade of a team's files. Taken from it:

- **The kit as data.** Its manifests are rows that say how to project one core into each tool's tree, with code only where a row cannot say it. Here `kit/kit.json` gives each file's class and seed, and `wslib/kit.py` is the one reader.
- **Seeds kept under their own names.** It authors a tool's files in the kit and writes each to its path in the project, such as its ignore file. Here `kit/seed/` does the same for the README, the eval page and the CI workflow.
- **Replace only on a known hash.** It replaces a team's file only when the file's SHA-256 matches one it shipped, and treats anything else as the team's or as a conflict. Here an upgrade replaces a synced file only when its hash matches the lock, refuses on drift, and writes hashes as `sha256:` and the hex digest, as it does.
- **A stamp in the project.** It records the framework version a projection came from. Here the lock's `kit` entry records the kit version and commit.

Not taken, where it does not fit:

- **Tier projection.** It projects each tier into every tool's model and effort settings from one table. Here the [tier binding](../orchestration.md#the-binding) is one manifest entry, and only Claude Code's handoffs are bound to it. Projecting it now would change what the manifest's `tiers` mean, and so the engine's version, for one tool. It fits once a second tool's handoffs are bound.
- **Generated hook wiring.** It writes each tool's hook registrations from one core. Here two tools are wired by hand, each line through the launcher, and tests hold both. At two tools a generator is more code than the files it would write.
- **Merging into a team's own files.** It keeps a marked block inside a team's file, such as its ignore file, and updates only that block. Here a seeded file is written once and is the instance's from then on. That is simpler, and its cost is listed above.

## Rules

| Rule | Enforced by |
|---|---|
| In an instance, a synced file stays as the kit shipped it, until a person keeps the instance's own copy on record. | `kit_drift#a hand-edited synced file fails`, `kit_drift#a kept file is the instance's, edited or not` |
| A seeded file, and a file the kit never shipped, belong to the instance. | `kit_drift#an edited seeded file, and a file the kit never shipped, pass` |
| A commit that brings the kit's text skips the instruction review only when every guidance page it leaves in place, other than those a review record it names covers, is as the lock holds it. | `review_trailer#an instance's first commit, every page as the kit wrote it, passes`, `review_trailer#as the kit wrote it fails a page that differs from the lock`, `review_trailer#an upgrade's commit may name a record for the README row it corrects beside the kit's reason` |
| In an instance, a synced page's proof marks are the kit's. | `proof#in an instance, synced pages whose marks match the lock pass without the kit's evidence`, `proof#in an instance, a synced page whose marks differ from the lock fails` |
| A page the instance owns is held to every rule of decision 0006. | `proof#in an instance, a page of its own is held to every rule` |
| The instance's eval gates only the pages it proves itself. | `eval_record#in an instance, a page the kit proved needs no case or record here`, `eval_record#in an instance, a page it marks proven itself needs a case` |
| An upgrade replaces only synced files that match the lock, and refuses on drift. | `prose` |
| An instance starts with an empty outward-write list. | `prose` |
| The kill rules are counted at each quarter's end, and a rule that fires is recorded here. | `prose` |
