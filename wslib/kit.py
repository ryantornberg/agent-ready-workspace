"""The kit: make an instance of this workspace, catch a hand edit to a file the kit owns, and upgrade an instance.

    python3 ws.py adopt PATH      # from the kit: make an instance in PATH, an empty folder
    python3 ws.py drift           # in an instance: name each synced file edited or deleted since its lock
    python3 ws.py drift --keep F  # in an instance: keep its own copy of synced file F, unless the kit proved it
    python3 ws.py upgrade PATH    # from a newer kit: replace the instance's unedited synced files

kit/kit.json describes the kit as data: an ordered list of rules, the first whose path matches a tracked file
giving that file's class (decision record 0007):

  synced    the kit owns it. Adopt copies it, an upgrade replaces it, and `drift` fails on a hand edit to it.
  seeded    adopt writes it once, and the instance owns it from then on. A rule may give it a seed file to write
            instead ("from"), empty every table's rows ("empty"), drop each table row that names a path the
            instance does not get ("prune") or holds a given text ("drop_rows"), fill in the proof table ("proof_table"), or, for the manifest, set
            top-level keys and part settings ("set", "parts").
  never     this workspace's own: its plans, records, eval runs, tests and CI. Adopt does not copy it.

The kit manifest lists every tracked file with its class and hash, so it names every seeded item. It also holds
the proof state of each synced page, which the `proof` and `eval_record` checks read in an instance, and the
kit's eval cases, which the `rules` check reads there; see wslib/kitlock.py. Adopt and upgrade write it into the
instance as its lock, kit.lock.json. A hash is "sha256:" and the hex digest of the file, read with CRLF as LF so a
checkout's line endings do not count as an edit.

An upgrade first refuses on drift, and on a new synced file whose path the instance already uses for a file of its
own, and then changes nothing. Otherwise it replaces each synced file, adds new ones, deletes those the kit no
longer ships, sets the instance manifest's "version" to the engine's, and writes the new lock. It runs from the
person's terminal or a branch, as decision record 0003 says an engine upgrade must.
"""
import json
import os
import pathlib
import posixpath
import re
import stat
import subprocess

from . import VERSION
from . import kitlock

RULES = "kit/kit.json"
CLASSES = ("synced", "seeded", "never")
LIST = "outward-repos.json"
PROOF_TABLE = "<!-- kit: proof table -->"
PROOF_KEYS = "evals/proofkeys.py"
CASES = "evals/cases"


class KitError(Exception):
    pass


digest = kitlock.digest


def _git(root, *args, check=True):
    result = subprocess.run(["git", "-C", str(root), *args], capture_output=True)
    if check and result.returncode != 0:
        raise KitError(f"git {' '.join(args)} failed in {root}: {result.stderr.decode('utf-8', 'replace').strip()}")
    return result


def load_rules(source):
    path = pathlib.Path(source) / RULES
    try:
        rules = json.loads(path.read_text(encoding="utf-8"))
        entries = rules["classes"]
        if not isinstance(entries, list) or not entries:
            raise TypeError
        for entry in entries:
            if not isinstance(entry.get("path"), str) or entry.get("class") not in CLASSES:
                raise TypeError
            if entry.get("from") and entry["class"] != "seeded":
                raise KitError(f'{RULES}: only a seeded file takes "from" ({entry["path"]})')
    except (OSError, ValueError, KeyError, TypeError, AttributeError) as error:
        if isinstance(error, KitError):
            raise
        raise KitError(f'{RULES} is missing or unreadable: it needs "classes", a list of '
                       f'{{"path", "class"}} rules with a class in {", ".join(CLASSES)}')
    return entries


def rule_for(rules, path):
    """The first rule whose path is the file, or a folder (ending in "/") that holds it. None when none matches."""
    for rule in rules:
        pattern = rule["path"]
        if path == pattern or (pattern.endswith("/") and path.startswith(pattern)):
            return rule
    return None


def tracked(source):
    """[(path, executable)] of every file git tracks in the kit's working copy."""
    out = _git(source, "ls-files", "-s", "-z").stdout.decode("utf-8")
    files = []
    for record in out.split("\0"):
        if not record:
            continue
        meta, _, path = record.partition("\t")
        mode = meta.split()[0]
        if mode == "160000":       # a pinned repository: an instance pins its own
            continue
        files.append((path, mode == "100755"))
    return files


def _rows(text):
    return text.replace("\r\n", "\n").split("\n")


def _is_table_row(line):
    return line.lstrip().startswith("|")


def _is_separator(line):
    cells = [c.strip() for c in line.strip().strip("|").split("|")]
    return bool(cells) and all(c and set(c) <= set("-: ") for c in cells)


def table_rows(text):
    """[(index, line)] of every markdown table's data rows: below its header and separator."""
    lines, found, state = _rows(text), [], None
    for index, line in enumerate(lines):
        if not _is_table_row(line):
            state = None
            continue
        if state is None:
            state = "header"
        elif state == "header":
            state = "data" if _is_separator(line) else None
        else:
            found.append((index, line))
    return found


def empty_tables(text):
    drop = {index for index, _ in table_rows(text)}
    return "\n".join(line for index, line in enumerate(_rows(text)) if index not in drop)


def drop_rows(text, needles):
    """Drop each table row that holds one of the given texts, such as a rule an instance cannot keep yet."""
    drop = {index for index, line in table_rows(text) if any(needle in line for needle in needles)}
    return "\n".join(line for index, line in enumerate(_rows(text)) if index not in drop)


def _named_paths(line, where):
    """Every repository path a table row names: link targets, read from the page's folder, and backticked paths."""
    named = []
    for target in re.findall(r"\]\(([^)\s]+)\)", line):
        target = target.split("#", 1)[0]
        if target and "://" not in target:
            named.append(posixpath.normpath(posixpath.join(where, target)) + ("/" if target.endswith("/") else ""))
    for token in re.findall(r"`([^`\s]+)`", line):
        if "/" in token or re.search(r"\.[a-z]+$", token):
            named.append(token)
    return named


def prune_tables(text, page, source_paths, instance_paths):
    """Drop each table row that names a kit path the instance does not get, such as a plan or an eval record."""
    where = posixpath.dirname(page)

    def known(path, paths):
        folder = path.rstrip("/") + "/"
        return path.rstrip("/") in paths or any(p.startswith(folder) for p in paths)

    drop = set()
    for index, line in table_rows(text):
        for path in _named_paths(line, where):
            if known(path, source_paths) and not known(path, instance_paths):
                drop.add(index)
                break
    return "\n".join(line for index, line in enumerate(_rows(text)) if index not in drop)


def _load_proof_keys(source):
    module = {}
    path = pathlib.Path(source) / PROOF_KEYS
    exec(compile(path.read_text(encoding="utf-8"), str(path), "exec"), module)
    return module


def _slug(heading):
    return re.sub(r"[^\w\- ]", "", heading.lower()).strip().replace(" ", "-")


def proof_states(source, pages):
    """{name: {"proof", "prove-by" or "proven-by"}} for each synced page and section that carries a proof mark."""
    keys = _load_proof_keys(source)
    states = {}
    for page in sorted(pages):
        text = (pathlib.Path(source) / page).read_text(encoding="utf-8")
        front, sections = keys["keys"](text)
        marks = []
        if "proof" in front:
            marks.append((page, front["proof"], front.get("prove-by"), front.get("proven-by")))
        for heading, line in sections:
            state, value = keys["parse_section"](line)
            marks.append((f"{page}#{_slug(heading)}", state, value if state == "unproven" else None,
                          value if state == "proven" else None))
        for name, state, prove_by, proven_by in marks:
            entry = {"proof": state}
            if prove_by:
                entry["prove-by"] = prove_by
            if proven_by:
                entry["proven-by"] = [f"{sha}:{path}" if sha else path
                                      for sha, path in keys["parse_list"](proven_by)]
            states[name] = entry
    return states


def proof_table(states, kit_version):
    """The README's table of proven and unproven pages, filled from the kit's proof states."""
    rows = ["| Page | State | Evidence or milestone |", "|---|---|---|"]
    for name, entry in states.items():
        if entry["proof"] == "proven":
            evidence = f"proven in the kit, version {kit_version}; its records stay in the kit"
        else:
            evidence = f"{entry.get('prove-by', '?')}, a milestone of the kit's plan"
        rows.append(f"| [{name}]({name}) | {entry['proof']} | {evidence} |")
    return "\n".join(rows)


def _set_parts(manifest, settings):
    for entry in manifest.get("parts", []):
        if isinstance(entry, dict) and entry.get("use") in settings:
            entry.update(settings[entry["use"]])
    return manifest


def build(source):
    """The kit manifest of the kit in `source`, and {path: bytes} of what an instance gets.

    Raises KitError for a tracked file no rule classes, or a seed that cannot be read."""
    source = pathlib.Path(source).resolve()
    rules = load_rules(source)
    files = tracked(source)
    classes, unclassed = {}, []
    for path, _ in files:
        rule = rule_for(rules, path)
        if rule is None:
            unclassed.append(path)
        else:
            classes[path] = rule
    if unclassed:
        raise KitError(f"{len(unclassed)} tracked file(s) match no rule in {RULES}, so the kit cannot say whether "
                       f"an instance gets them: {', '.join(unclassed[:5])}. Add a rule for each")
    executable = dict(files)
    source_paths = {path for path, _ in files}
    instance_paths = {path for path, rule in classes.items() if rule["class"] != "never"} | {LIST, kitlock.LOCK}
    synced_pages = [p for p, rule in classes.items() if rule["class"] == "synced" and p.endswith(".md")]
    try:
        states = proof_states(source, synced_pages)
    except (OSError, KeyError, SyntaxError, ValueError, IndexError) as error:
        raise KitError(f"cannot read the synced pages' proof marks through {PROOF_KEYS}: {error}")

    head = _git(source, "rev-parse", "HEAD", check=False).stdout.decode().strip()
    changed = bool(_git(source, "status", "--porcelain", check=False).stdout.strip())
    kit = {"version": VERSION, "commit": head or None, "changed": changed}

    replaced = {path for path, rule in classes.items() if rule["class"] == "seeded" and rule.get("from")}
    contents, entries = {}, {}
    for path in sorted(classes):
        rule = classes[path]
        try:
            if rule["class"] == "seeded" and rule.get("from"):
                data = (source / rule["from"]).read_bytes()
            else:
                data = (source / path).read_bytes()
        except OSError as error:
            raise KitError(f"cannot read {rule.get('from') or path}: {error}")
        if rule["class"] == "seeded":
            data = seed(path, data, rule, states, source_paths, instance_paths, replaced)
        entry = {"class": rule["class"], "hash": digest(data)}
        if rule["class"] == "seeded" and rule.get("from"):
            entry["from"] = rule["from"]
        entries[path] = entry
        if rule["class"] != "never":
            contents[path] = (data, executable.get(path, False))

    names = []
    for path in sorted(p for p in source_paths if p.startswith(CASES + "/") and p.endswith(".json")):
        try:
            name = json.loads((source / path).read_text(encoding="utf-8")).get("name")
        except (OSError, ValueError, AttributeError):
            name = None
        if isinstance(name, str):
            names.append(name)
    manifest = {"kit": kit, "files": entries, "proof": states, "cases": names}
    return manifest, contents


def seed(path, data, rule, states, source_paths, instance_paths, replaced=()):
    """What adopt writes for a seeded file, after the rule's changes."""
    if path.endswith(".json") and ("set" in rule or "parts" in rule):
        manifest = json.loads(data.decode("utf-8"))
        manifest.update(rule.get("set", {}))
        _set_parts(manifest, rule.get("parts", {}))
        for entry in manifest.get("parts", []):     # a seed file replaces the page an exemption was for
            if isinstance(entry, dict) and entry.get("use") == "links" and isinstance(entry.get("exempt"), list):
                entry["exempt"] = [e for e in entry["exempt"]
                                   if not (isinstance(e, dict) and e.get("source") in replaced)]
        return (json.dumps(manifest, indent=2) + "\n").encode("utf-8")
    if not any(rule.get(key) for key in ("empty", "prune", "proof_table", "drop_rows")):
        return data
    text = data.decode("utf-8")
    if rule.get("drop_rows"):
        text = drop_rows(text, rule["drop_rows"])
    if rule.get("empty"):
        text = empty_tables(text)
    if rule.get("prune"):
        text = prune_tables(text, path, source_paths, instance_paths)
    if rule.get("proof_table"):
        if PROOF_TABLE not in text:
            raise KitError(f"{rule.get('from') or path} has no line {PROOF_TABLE!r} for the proof table")
        text = text.replace(PROOF_TABLE, proof_table(states, VERSION))
    return text.encode("utf-8")


def _write(target, path, data, executable):
    full = target / path
    full.parent.mkdir(parents=True, exist_ok=True)
    full.write_bytes(data)
    if executable and os.name != "nt":
        full.chmod(full.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)


def _write_lock(target, manifest):
    (target / kitlock.LOCK).write_text(json.dumps(manifest, indent=2, sort_keys=False) + "\n", encoding="utf-8")


def adopt(source, target):
    """Make an instance in `target`, an empty folder or one holding only a git folder. Returns report lines."""
    target = pathlib.Path(target).resolve()
    source = pathlib.Path(source).resolve()
    if target == source or source in target.parents:
        raise KitError(f"{target} is inside the kit; adopt into a folder outside it")
    if target.exists() and any(entry.name != ".git" for entry in target.iterdir()):
        raise KitError(f"{target} is not empty; adopt makes an instance only in an empty folder, so it never "
                       f"overwrites anything. To take a newer kit into an instance, run ws.py upgrade")
    manifest, contents = build(source)
    target.mkdir(parents=True, exist_ok=True)
    for path, (data, executable) in contents.items():
        _write(target, path, data, executable)
    (target / LIST).write_text('{\n  "repositories": []\n}\n', encoding="utf-8")
    _write_lock(target, manifest)
    if not (target / ".git").exists():
        _git(target, "init", "--quiet")
    counts = {name: sum(1 for e in manifest["files"].values() if e["class"] == name) for name in CLASSES}
    warning = []
    if manifest["kit"]["changed"]:
        warning = [f"  note: the kit's working copy has changes not committed at {manifest['kit']['commit']}; the "
                   f"instance holds tracked files as the working copy has them, and no file git does not track"]
    return warning + [f"adopt: made an instance of kit {VERSION} in {target}",
            f"  {counts['synced']} synced, {counts['seeded']} seeded, {counts['never']} never synced; "
            f"{LIST} lists no repository, so agents write to none until a person adds the instance's own",
            f"  the lock is {kitlock.LOCK}; next, in {target}, follow the README's setup steps and commit"]


def _instance_lock(target):
    path = pathlib.Path(target) / kitlock.LOCK
    try:
        lock = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(lock.get("files"), dict):
            raise ValueError
        return lock
    except FileNotFoundError:
        raise KitError(f"{path} does not exist, so {target} is not an instance of the kit (ws.py adopt makes one)")
    except (OSError, ValueError, AttributeError):
        raise KitError(f"{path} is not a readable kit lock; restore it from the instance's history")


def drifted(target, lock):
    """[(path, "edited" | "deleted")] for each synced file the lock holds that differs from it."""
    target = pathlib.Path(target)
    found = []
    for path, entry in sorted(lock["files"].items()):
        if not isinstance(entry, dict) or entry.get("class") != "synced":
            continue
        full = target / path
        if not full.is_file():
            found.append((path, "deleted"))
        elif digest(full.read_bytes()) != entry.get("hash"):
            found.append((path, "edited"))
    return found


def drift(target, keep=()):
    """(exit code, report lines): 1 when a synced file was edited or deleted since the lock, else 0."""
    target = pathlib.Path(target).resolve()
    lock = _instance_lock(target)
    lines = []
    for path in keep:
        entry = lock["files"].get(path)
        if not isinstance(entry, dict) or entry.get("class") != "synced":
            raise KitError(f"{path} is not a synced file in {kitlock.LOCK}, so there is nothing to keep")
        if kitlock.proven(lock, path):
            raise KitError(f"{path} is a page the kit marks proven, and its proof rests on the kit's text and records, "
                           f"which the instance does not hold; it cannot be kept. Put the kit's copy back with "
                           f"`git checkout -- {path}`, and write the instance's own steps on a page of its own")
        entry["class"] = "kept"
        lines.append(f"drift: kept {path}: the instance owns its copy now, and upgrades leave it alone")
    if keep:
        _write_lock(target, lock)
    found = drifted(target, lock)
    version = kitlock.version(lock)
    for path, how in found:
        lines.append(f"drift: {path}: {how} since kit {version} ({kitlock.LOCK}). Restore the kit's copy with "
                     f"`git checkout -- {path}`, or keep yours with `python3 ws.py drift --keep {path}`; "
                     f"see docs/decisions/0007-the-kit.md")
    kept = sorted(p for p, e in lock["files"].items() if isinstance(e, dict) and e.get("class") == "kept")
    if kept:
        lines.append(f"drift: {len(kept)} synced file(s) kept as the instance's own: {', '.join(kept)}")
    if not found:
        lines.append(f"drift: none; every synced file matches kit {version}")
    return (1 if found else 0), lines


def upgrade(source, target):
    """Take the kit in `source` into the instance in `target`. Returns report lines; raises KitError on refusal."""
    source, target = pathlib.Path(source).resolve(), pathlib.Path(target).resolve()
    if target == source:
        raise KitError("upgrade takes a kit into another folder's instance; run it from the newer kit")
    old = _instance_lock(target)
    found = drifted(target, old)
    if found:
        raise KitError("refused: synced files changed since the instance's lock, so an upgrade would overwrite "
                       "them: " + ", ".join(f"{p} ({how})" for p, how in found) +
                       ". Restore each, or keep it with `python3 ws.py drift --keep PATH` in the instance; "
                       "nothing was changed")
    manifest, contents = build(source)
    old_files = old["files"]
    kept = {p for p, e in old_files.items() if isinstance(e, dict) and e.get("class") == "kept"}
    new_synced = {p for p, e in manifest["files"].items() if e["class"] == "synced"}
    taken = sorted(p for p in new_synced - kept
                   if (old_files.get(p) or {}).get("class") != "synced" and (target / p).exists())
    if taken:
        raise KitError("refused: the kit now ships " + ", ".join(taken) + ", and the instance holds its own "
                       "file at that path. Rename or remove the instance's file, then upgrade again; nothing was "
                       "changed")

    replaced, added, removed = [], [], []
    for path in sorted(new_synced - kept):
        data, executable = contents[path]
        was = (old_files.get(path) or {}).get("class") == "synced"
        if was and old_files[path].get("hash") == manifest["files"][path]["hash"]:
            continue
        _write(target, path, data, executable)
        (replaced if was else added).append(path)
    for path in sorted(p for p, e in old_files.items() if isinstance(e, dict) and e.get("class") == "synced"):
        gone = path not in manifest["files"] or manifest["files"][path]["class"] == "never"
        if gone and (target / path).is_file():
            (target / path).unlink()
            removed.append(path)
    seeded_new = []
    for path, entry in sorted(manifest["files"].items()):
        if entry["class"] == "seeded" and path not in old_files and not (target / path).exists():
            data, executable = contents[path]
            _write(target, path, data, executable)
            seeded_new.append(path)
    for path in kept:
        if path in manifest["files"]:
            manifest["files"][path]["class"] = "kept"
    bumped = _set_version(target / "workspace.json")
    _write_lock(target, manifest)
    lines = [f"upgrade: kit {kitlock.version(old)} -> {VERSION} in {target}",
             f"  replaced {len(replaced)}, added {len(added)}, removed {len(removed)} synced file(s); "
             f"seeded {len(seeded_new)} new file(s); left {len(kept)} kept file(s) alone"]
    for label, paths in (("replaced", replaced), ("added", added), ("removed", removed), ("seeded", seeded_new)):
        lines += [f"  {label} {p}" for p in paths]
    if bumped:
        lines.append(f'  workspace.json: "version" set to {VERSION}. Read the kit\'s change log for settings whose '
                     f'meaning changed, and correct them before you commit')
    parts = [p for p in added if p.startswith("parts/") and p.endswith(".py")]
    if parts:
        lines.append("  new parts, which run only once workspace.json uses them: " +
                     ", ".join(posixpath.basename(p)[:-3] for p in parts))
    lines.append("  the README's proof table is the instance's own: run python3 ws.py check, and correct each row "
                 "it names")
    return lines


def _set_version(path):
    """Set the instance manifest's "version" to the engine's, in place, keeping the rest of the file as it is."""
    try:
        text = path.read_text(encoding="utf-8")
    except OSError:
        return False
    new, count = re.subn(r'("version"\s*:\s*")[^"]*(")', lambda m: m.group(1) + VERSION + m.group(2), text, count=1)
    if count and new != text:
        path.write_text(new, encoding="utf-8")
        return True
    return False
