"""Load the parts a workspace's manifest names, and run each part's own cases.

A part is one Python file. It declares what it is and exposes one function:

    KIND = "check"     def run(snapshot, config) -> [finding(...), ...]
    KIND = "hook"      EVENT = "before-shell" or "before-edit"
                       def decide(event, config) -> None to allow, or the reason to refuse

KIND and EVENT are each one plain line of their own, such as KIND = "hook".
The runner reads those lines without running the file, so a hook call loads
only the hooks for its event: a broken check cannot refuse a shell command.
A part whose lines it cannot read, or whose running KIND or EVENT differs from
the declared one, is refused.

Next to it sits <name>.cases.json: the part's own tests, as data. Loading a
part runs its cases, every time. A part with no cases, or with a case that
fails, is refused. A check that nobody tests can stop finding things, and a
hook can stop firing, and nobody notices. A case runs with its own "config"
only, never the manifest's settings, so changing a setting cannot fail a case.

A check case:  {"name", "files": {path: text}, "changed": [paths], "config": {}, "expect": [...]}
               Each expectation is text in an error, or {"message": text, "level": "warning"}.
               "expect": [] means the case must produce no findings. Every finding must be expected.
A hook case:   {"name", "event": {...}, "config": {}, "allow": true|false}

The manifest's "parts" lists the parts in use. A part that an older manifest
used may leave only by being listed under "retired", with a reason:
    "retired": [{"use": "no_stage_all", "why": "the commit check now compares staged paths"}]
"""
import json
import pathlib
import re
import subprocess
import types

from . import snapshot as snapshots

KINDS = ("check", "hook")
EVENTS = ("before-shell", "before-edit")
LEVELS = ("error", "warning")
MANIFEST = "workspace.json"


class PartError(Exception):
    pass


def finding(path, line, message, level="error"):
    return {"path": path, "line": line, "message": message, "level": level}


def _expected(item):
    """An expectation as (text, level)."""
    return (item, "error") if isinstance(item, str) else (item["message"], item["level"])


class Part:
    def __init__(self, name, module, cases, config):
        self.name, self.module, self.cases, self.config = name, module, cases, config
        self.kind = module.KIND
        self.event = getattr(module, "EVENT", None)

    def run(self, snapshot, config=None):
        try:
            found = self.module.run(snapshot, self.config if config is None else config)
        except Exception as error:
            raise PartError(f"part {self.name} crashed: {type(error).__name__}: {error}")
        if not isinstance(found, list) or not all(isinstance(f, dict) and {"path", "line", "message", "level"} <= set(f) for f in found):
            raise PartError(f"part {self.name}: run must return a list of findings")
        odd = [f["level"] for f in found if f["level"] not in LEVELS]
        if odd:
            raise PartError(f"part {self.name}: a finding's level must be one of {LEVELS}, not {odd[0]!r}")
        return found

    def decide(self, event, config=None):
        try:
            reason = self.module.decide(event, self.config if config is None else config)
        except Exception as error:
            raise PartError(f"part {self.name} crashed: {type(error).__name__}: {error}")
        if reason is not None and not isinstance(reason, str):
            raise PartError(f"part {self.name}: decide must return None or the reason as text")
        return reason

    def failed_cases(self):
        """Run the part's cases, each with its own config only. Return a list of "case name: what went wrong"."""
        failures = []
        for case in self.cases:
            config = case.get("config", {})
            try:
                if self.kind == "check":
                    got = [(f["message"], f["level"]) for f in self.run(snapshots.Memory(case["files"], case.get("changed", ())), config)]
                    want = [_expected(item) for item in case["expect"]]
                    missing = [f"{text} ({level})" for text, level in want
                               if not any(text in message and level == got_level for message, got_level in got)]
                    extra = [f"{message} ({level})" for message, level in got
                             if not any(text in message and level == want_level for text, want_level in want)]
                    if missing or extra:
                        failures.append(f"{case['name']}: missing {missing}, unexpected {extra}")
                else:
                    reason = self.decide(case["event"], config)
                    if (reason is None) != case["allow"]:
                        failures.append(f"{case['name']}: expected {'allow' if case['allow'] else 'refuse'}, "
                                        f"got {'allow' if reason is None else 'refuse: ' + reason}")
            except PartError as error:  # a case that crashes the part is a failed case
                failures.append(f"{case['name']}: {error}")
        return failures


def parse_manifest(text, where=MANIFEST):
    try:
        manifest = json.loads(text)
    except json.JSONDecodeError as error:
        raise PartError(f"{where}: {error}")
    parts = manifest.get("parts") if isinstance(manifest, dict) else None
    if not isinstance(parts, list) or not parts:
        raise PartError(f'{where}: "parts" must be a non-empty list')
    retired = manifest.get("retired", [])
    if not isinstance(retired, list) or not all(
            isinstance(r, dict) and isinstance(r.get("use"), str) and isinstance(r.get("why"), str) and r["why"].strip()
            for r in retired):
        raise PartError(f'{where}: each "retired" entry needs a "use" and a "why" that gives the reason')
    return manifest


def load_manifest(root):
    try:
        return parse_manifest((pathlib.Path(root) / MANIFEST).read_text(encoding="utf-8"))
    except FileNotFoundError:
        raise PartError(f"no {MANIFEST} in {root}")


def source_of(root, entry):
    """The part's file as (name, path relative to root). Refuses a "use" that is not text or leads outside the workspace."""
    if not isinstance(entry, dict) or not isinstance(entry.get("use"), str):
        raise PartError(f'each part needs a "use": {entry!r}')
    use = entry["use"]
    root = pathlib.Path(root).resolve()
    source = (root / (use if use.endswith(".py") else f"parts/{use}.py")).resolve()
    try:
        relative = source.relative_to(root).as_posix()
    except ValueError:
        raise PartError(f"part {use}: refused, its file is outside the workspace")
    return source.stem, relative


def _read(root, relative, snapshot):
    """A part's file as text, from the snapshot when one is given (the staged commit), else from disk. None when absent."""
    if snapshot is not None:
        return snapshot.read(relative) if snapshot.is_file(relative) else None
    try:
        return (pathlib.Path(root) / relative).read_text(encoding="utf-8-sig")
    except (FileNotFoundError, IsADirectoryError):
        return None
    except (OSError, UnicodeDecodeError) as error:
        raise PartError(f"cannot read {relative}: {error}")


def declared(text, name):
    """The value of the one plain `NAME = "value"` line in a part's source, or None when there is not exactly one."""
    lines = re.findall(rf"""^{name}\s*=\s*(["'])([\w-]+)\1\s*(?:#.*)?$""", text, re.MULTILINE)
    return lines[0][1] if len(lines) == 1 else None


def _read_cases(name, kind, cases_file, text):
    if text is None:
        raise PartError(f"part {name}: refused, it has no cases file ({cases_file})")
    try:
        cases = json.loads(text)
    except json.JSONDecodeError as error:
        raise PartError(f"part {name}: {cases_file}: {error}")
    if not isinstance(cases, list) or not cases:
        raise PartError(f"part {name}: refused, {cases_file} holds no cases")
    for case in cases:
        if kind == "check":
            well_formed = isinstance(case, dict) and isinstance(case.get("name"), str) \
                and isinstance(case.get("files"), dict) and isinstance(case.get("expect"), list) \
                and all(isinstance(item, str) or (isinstance(item, dict) and set(item) == {"message", "level"}
                                                  and isinstance(item["message"], str) and item["level"] in LEVELS)
                        for item in case["expect"])
        else:
            well_formed = isinstance(case, dict) and isinstance(case.get("name"), str) \
                and isinstance(case.get("event"), dict) and isinstance(case.get("allow"), bool)
        if not well_formed or not isinstance(case.get("config", {}), dict):
            needs = ('"name", "files" and "expect", each expectation text or {"message", "level"} with a level in '
                     f"{LEVELS}" if kind == "check" else '"name", "event" and "allow"')
            raise PartError(f"part {name}: {cases_file}: every case needs {needs}: {case!r}")
    if kind == "check" and not any(case["expect"] for case in cases):
        raise PartError(f"part {name}: refused, no case shows it finding anything")
    if kind == "hook" and {case["allow"] for case in cases} != {True, False}:
        raise PartError(f"part {name}: refused, its cases must show it both allowing and refusing")
    return cases


def load(root, entry, run_cases=True, snapshot=None):
    """Load one manifest entry: {"use": "links", ...config}. "use" is a name under parts/, or a path to a .py file.

    The part's cases run as it loads, and a failing case refuses the part.
    run_cases=False is for `ws.py selftest`, which reports every failure instead of stopping at the first.
    snapshot: read the part and its cases from it (the staged commit) instead of from disk.
    """
    name, relative = source_of(root, entry)
    text = _read(root, relative, snapshot)
    if text is None:
        raise PartError(f"part {name}: no file at {relative}")
    kind, event = declared(text, "KIND"), declared(text, "EVENT")
    if kind not in KINDS:
        raise PartError(f'part {name}: needs one plain line KIND = "check" or KIND = "hook"')
    if kind == "hook" and event not in EVENTS:
        raise PartError(f"part {name}: a hook's EVENT must be one of {EVENTS}, on one plain line")
    try:
        module = types.ModuleType(f"workspace_part_{name}")
        module.__file__ = str(pathlib.Path(root) / relative)
        exec(compile(text, module.__file__, "exec"), module.__dict__)
    except Exception as error:
        raise PartError(f"part {name}: cannot be loaded: {type(error).__name__}: {error}")

    if getattr(module, "KIND", None) != kind or (kind == "hook" and getattr(module, "EVENT", None) != event):
        raise PartError(f"part {name}: it declares KIND {kind!r} and EVENT {event!r}, "
                        f"but runs as {getattr(module, 'KIND', None)!r} and {getattr(module, 'EVENT', None)!r}")
    if not callable(getattr(module, "run" if kind == "check" else "decide", None)):
        raise PartError(f"part {name}: a {kind} needs a {'run' if kind == 'check' else 'decide'} function")

    cases_file = relative[:-len(".py")] + ".cases.json"
    cases = _read_cases(name, kind, pathlib.PurePosixPath(cases_file).name, _read(root, cases_file, snapshot))
    config = {key: value for key, value in entry.items() if key != "use"}
    part = Part(name, module, cases, config)
    if run_cases:
        failures = part.failed_cases()
        if failures:
            raise PartError(f"part {name}: refused, {len(failures)} of its {len(cases)} cases fail; first: {failures[0]}")
    return part


def load_all(root, manifest=None, run_cases=True, snapshot=None):
    manifest = manifest or load_manifest(root)
    return [load(root, entry, run_cases, snapshot) for entry in manifest["parts"]]


def load_hooks(root, event, manifest):
    """Only the hooks for one event, each with its cases run. Checks and other events' hooks are not run at all.

    Fails closed: a part whose file is missing, or whose KIND cannot be read without running it, refuses the call,
    because it might be a hook for this event.
    """
    hooks = []
    for entry in manifest["parts"]:
        name, relative = source_of(root, entry)
        text = _read(root, relative, None)
        if text is None:
            raise PartError(f"part {name}: no file at {relative}, so no hook call can be decided")
        kind = declared(text, "KIND")
        if kind not in KINDS:
            raise PartError(f'part {name}: needs one plain line KIND = "check" or KIND = "hook", '
                            "so no hook call can be decided")
        # A hook whose EVENT is unreadable or unknown loads, and so refuses: a misspelt event must not hide a hook.
        if kind == "hook" and (declared(text, "EVENT") == event or declared(text, "EVENT") not in EVENTS):
            hooks.append(load(root, entry))
    return hooks


# Required parts: the parts an older manifest used must still be used, or be retired with a reason.

def _git(root, *args):
    try:
        return subprocess.run(["git", "-C", str(root), *args], capture_output=True)
    except OSError as error:
        raise RuntimeError(f"git cannot run: {error}")


def used_names(text):
    """The "use" values in a manifest's text. Only these are read, so keys added after it was written do not matter."""
    manifest = json.loads(text)
    parts = manifest.get("parts") if isinstance(manifest, dict) else None
    if not isinstance(parts, list):
        raise ValueError('no "parts" list')
    return {entry["use"] for entry in parts if isinstance(entry, dict) and isinstance(entry.get("use"), str)}


def required_parts(root, ref=None):
    """The part names the manifest at ref used. ref None means the last commit.

    Returns (names, problem). No last commit, as in a new repository, means nothing is required.
    A ref that cannot be read is a problem: the caller fails closed.
    """
    if ref is None:
        try:
            if _git(root, "rev-parse", "-q", "--verify", "HEAD^{commit}").returncode != 0:
                return set(), None   # not a repository, or no commit yet
        except RuntimeError:
            return set(), None
        ref = "HEAD"
    try:
        if _git(root, "rev-parse", "-q", "--verify", f"{ref}^{{commit}}").returncode != 0:
            return set(), f"cannot read the manifest at {ref}: no such commit here"
        if _git(root, "cat-file", "-e", f"{ref}:./{MANIFEST}").returncode != 0:
            return set(), None       # that commit had no manifest yet
        shown = _git(root, "show", f"{ref}:./{MANIFEST}")
    except RuntimeError as error:
        return set(), f"cannot read the manifest at {ref}: {error}"
    try:
        return used_names(shown.stdout.decode("utf-8-sig")), None
    except (ValueError, UnicodeDecodeError) as error:
        return set(), f"cannot read the part names in the manifest at {ref}: {error}"


def dropped_parts(manifest, required, where):
    """Findings for each required part the manifest neither uses nor retires."""
    used = {entry.get("use") for entry in manifest["parts"] if isinstance(entry, dict)}
    retired = {entry["use"] for entry in manifest.get("retired", [])}
    found = [finding(MANIFEST, 1, f"part {name} is used and retired at once") for name in sorted(used & retired)]
    found += [finding(MANIFEST, 1, f"part {name} was in the manifest at {where} and is gone; keep it, or list it "
                                   'under "retired" with a "why"') for name in sorted(required - used - retired)]
    return found
