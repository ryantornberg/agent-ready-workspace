"""Load the parts a workspace's manifest names, and run each part's own cases.

A part is one Python file. It declares what it is and exposes one function:

    KIND = "check"     def run(snapshot, config) -> [finding(...), ...]
    KIND = "hook"      EVENT = "before-shell", "before-edit" or "before-handoff"
                       def decide(event, config) -> None to allow, or the reason to refuse
                       MODE = "remind" (optional): the hook never refuses. Its reason is shown
                       to the agent as a reminder and the call goes ahead. The default is "refuse".
    A check may set PHASES, the phases it runs in: "commit", "ci", "nightly" and "push". The default is
    ("commit", "ci"). `ws.py check --phase nightly` runs only the checks whose PHASES hold "nightly".
    A "push" check runs from the pre-push hook, `ws.py check --push REMOTE`, on the commits being pushed.

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

A part's config is its manifest entry without "use" and "why", plus the manifest's
tier binding as "tiers" when the manifest has one. The binding lives in one place:
an entry that sets "tiers" itself is refused.

The manifest holds four keys and no others: "version", which must equal the
engine's VERSION; "tiers", which binds each of the three tiers to a model and an
effort; "parts"; and "retired". Every entry in "parts" and "retired" gives a "why".
A hook call checks only what its answer depends on: the version, the parts and the
tier binding. A missing "why" or an unknown key fails every other command, so it
cannot reach a commit, and it does not lock the session out.

A check case:  {"name", "files": {path: text}, "changed": [paths], "config": {}, "expect": [...]}
               Each expectation is text in an error, or {"message": text, "level": "warning"}.
               "expect": [] means the case must produce no findings. Every finding must be expected.
               For the commit's own state, a case may also give "staged": [paths], "ledger": [paths]
               and "replaying": text; "repositories": [folders] names code repositories, and
               "symlinks": [paths] names symbolic links (see wslib/snapshot.py).
A hook case:   {"name", "event": {...}, "config": {}, "allow": true|false}
               A hook with MODE = "remind" states "remind": true|false instead of "allow".

The manifest's "parts" lists the parts in use. A part that an older manifest
used may leave only by being listed under "retired", with a reason:
    "retired": [{"use": "no_stage_all", "why": "the commit check now compares staged paths"}]
"""
import json
import pathlib
import re
import subprocess
import types

from . import VERSION
from . import snapshot as snapshots

KINDS = ("check", "hook")
EVENTS = ("before-shell", "before-edit", "before-handoff")
LEVELS = ("error", "warning")
MODES = ("refuse", "remind")
PHASES = ("commit", "ci", "nightly", "push")
DEFAULT_PHASES = ("commit", "ci")
TIERS = ("driver", "worker", "mechanical")
TOP_LEVEL = ("version", "tiers", "parts", "retired")
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
        self.mode = getattr(module, "MODE", "refuse")
        self.phases = tuple(getattr(module, "PHASES", DEFAULT_PHASES)) if self.kind == "check" else ()

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
                    memory = snapshots.Memory(case["files"], case.get("changed", ()), case.get("staged"),
                                              case.get("ledger"), case.get("replaying"), case.get("repositories", ()),
                                              case.get("symlinks", ()), case.get("pushed", ()))
                    got = [(f["message"], f["level"]) for f in self.run(memory, config)]
                    want = [_expected(item) for item in case["expect"]]
                    missing = [f"{text} ({level})" for text, level in want
                               if not any(text in message and level == got_level for message, got_level in got)]
                    extra = [f"{message} ({level})" for message, level in got
                             if not any(text in message and level == want_level for text, want_level in want)]
                    if missing or extra:
                        failures.append(f"{case['name']}: missing {missing}, unexpected {extra}")
                else:
                    reason = self.decide(case["event"], config)
                    # A refusing hook's case says "allow"; a reminding hook's says "remind". Either way, None is quiet.
                    quiet = case["allow"] if self.mode == "refuse" else not case["remind"]
                    acts = "refuse" if self.mode == "refuse" else "remind"
                    if (reason is None) != quiet:
                        failures.append(f"{case['name']}: expected {'no ' + acts if quiet else acts}, "
                                        f"got {'no ' + acts if reason is None else acts + ': ' + reason}")
            except PartError as error:  # a case that crashes the part is a failed case
                failures.append(f"{case['name']}: {error}")
        return failures


def _gives_a_reason(entry):
    return isinstance(entry.get("why"), str) and bool(entry["why"].strip())


def parse_manifest(text, where=MANIFEST, hook=False):
    """The manifest, or PartError naming what is wrong with it.

    hook=True checks only what a hook's answer depends on: the version, the parts and the tier binding.
    """
    try:
        manifest = json.loads(text)
    except json.JSONDecodeError as error:
        raise PartError(f"{where}: {error}")
    if not isinstance(manifest, dict):
        raise PartError(f"{where}: the manifest must be a JSON object")
    # The version first: a manifest written for another engine may mean something else by its settings.
    if "version" not in manifest:
        raise PartError(f'{where}: gives no "version", and this engine is {VERSION}; add "version": "{VERSION}"')
    if manifest["version"] != VERSION:
        raise PartError(f'{where}: "version" is {json.dumps(manifest["version"])}, but this engine is {VERSION}. '
                        "Upgrade the engine and the manifest's version together, in one merge or from your own terminal")
    parts = manifest.get("parts")
    if not isinstance(parts, list) or not parts:
        raise PartError(f'{where}: "parts" must be a non-empty list')
    retired = manifest.get("retired", [])
    if not isinstance(retired, list) or not all(
            isinstance(r, dict) and isinstance(r.get("use"), str) and _gives_a_reason(r) for r in retired):
        raise PartError(f'{where}: each "retired" entry needs a "use" and a "why" that gives the reason')
    if "tiers" in manifest:
        _check_tiers(manifest["tiers"], where)
    if hook:
        return manifest
    unknown = sorted(set(manifest) - set(TOP_LEVEL))
    if unknown:
        raise PartError(f'{where}: unknown key "{unknown[0]}"; a manifest holds only {", ".join(TOP_LEVEL)}')
    for entry in parts:
        if isinstance(entry, dict) and isinstance(entry.get("use"), str) and not _gives_a_reason(entry):
            raise PartError(f'{where}: part {pathlib.PurePosixPath(entry["use"]).stem} needs a "why": the reason '
                            "this workspace runs it, in a sentence")
    return manifest


def _check_tiers(tiers, where):
    """The tier binding must bind each of the three tiers, and only those, to a model and an effort."""
    if not isinstance(tiers, dict):
        raise PartError(f'{where}: "tiers" must map each of {", ".join(TIERS)} to a model and an effort')
    for tier in sorted(set(tiers) - set(TIERS)):
        raise PartError(f'{where}: "tiers" names "{tier}", which is not a tier; the tiers are {", ".join(TIERS)}')
    for tier in TIERS:
        binding = tiers.get(tier)
        for setting in ("model", "effort"):
            value = binding.get(setting) if isinstance(binding, dict) else None
            if not isinstance(value, str) or not value.strip():
                raise PartError(f'{where}: "tiers" gives the {tier} tier no {setting}')


def load_manifest(root, hook=False):
    try:
        return parse_manifest((pathlib.Path(root) / MANIFEST).read_text(encoding="utf-8"), hook=hook)
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


def _read_cases(name, kind, cases_file, text, mode="refuse"):
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
            well_formed = well_formed and all(isinstance(case.get(key, []), list)
                                              for key in ("staged", "ledger", "repositories", "symlinks", "pushed")) \
                and isinstance(case.get("replaying", ""), str)
        else:
            answer, other = ("allow", "remind") if mode == "refuse" else ("remind", "allow")
            well_formed = isinstance(case, dict) and isinstance(case.get("name"), str) \
                and isinstance(case.get("event"), dict) and isinstance(case.get(answer), bool) and other not in case
        if not well_formed or not isinstance(case.get("config", {}), dict):
            needs = ('"name", "files" and "expect", each expectation text or {"message", "level"} with a level in '
                     f"{LEVELS}" if kind == "check" else f'"name", "event" and "{answer}", and no "{other}"')
            raise PartError(f"part {name}: {cases_file}: every case needs {needs}: {case!r}")
    if kind == "check" and not any(case["expect"] for case in cases):
        raise PartError(f"part {name}: refused, no case shows it finding anything")
    if kind == "hook" and {case["allow" if mode == "refuse" else "remind"] for case in cases} != {True, False}:
        raise PartError(f"part {name}: refused, its cases must show it both allowing and "
                        f"{'refusing' if mode == 'refuse' else 'reminding'}")
    return cases


def load(root, entry, run_cases=True, snapshot=None, tiers=None):
    """Load one manifest entry: {"use": "links", ...config}. "use" is a name under parts/, or a path to a .py file.

    The part's cases run as it loads, and a failing case refuses the part.
    run_cases=False is for `ws.py selftest`, which reports every failure instead of stopping at the first.
    snapshot: read the part and its cases from it (the staged commit) instead of from disk.
    tiers: the manifest's tier binding, given to the part as config["tiers"].
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
    mode = getattr(module, "MODE", "refuse")
    if kind == "hook" and mode not in MODES:
        raise PartError(f"part {name}: a hook's MODE must be one of {MODES}, not {mode!r}")
    phases = getattr(module, "PHASES", DEFAULT_PHASES)
    if kind == "check" and (not isinstance(phases, (tuple, list)) or not phases
                            or not all(isinstance(phase, str) and phase in PHASES for phase in phases)):
        raise PartError(f"part {name}: a check's PHASES must list one or more of {PHASES}, not {phases!r}")

    cases_file = relative[:-len(".py")] + ".cases.json"
    cases = _read_cases(name, kind, pathlib.PurePosixPath(cases_file).name, _read(root, cases_file, snapshot), mode)
    if "tiers" in entry:
        raise PartError(f'part {name}: refused, it sets "tiers"; the tier binding is the manifest\'s top-level "tiers"')
    config = {key: value for key, value in entry.items() if key not in ("use", "why")}
    if tiers is not None:
        config["tiers"] = tiers
    part = Part(name, module, cases, config)
    if run_cases:
        failures = part.failed_cases()
        if failures:
            raise PartError(f"part {name}: refused, {len(failures)} of its {len(cases)} cases fail; first: {failures[0]}")
    return part


def load_all(root, manifest=None, run_cases=True, snapshot=None):
    manifest = manifest or load_manifest(root)
    return [load(root, entry, run_cases, snapshot, manifest.get("tiers")) for entry in manifest["parts"]]


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
            hooks.append(load(root, entry, tiers=manifest.get("tiers")))
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
    return required_from(shown.stdout, ref)


def required_from(data, where):
    """The part names in a manifest's bytes, as (names, problem). None, for no manifest there, requires nothing."""
    if data is None:
        return set(), None
    try:
        return used_names(data.decode("utf-8-sig")), None
    except (ValueError, UnicodeDecodeError) as error:
        return set(), f"cannot read the part names in the manifest at {where}: {error}"


def dropped_parts(manifest, required, where):
    """Findings for each required part the manifest neither uses nor retires."""
    used = {entry.get("use") for entry in manifest["parts"] if isinstance(entry, dict)}
    retired = {entry["use"] for entry in manifest.get("retired", [])}
    found = [finding(MANIFEST, 1, f"part {name} is used and retired at once") for name in sorted(used & retired)]
    found += [finding(MANIFEST, 1, f"part {name} was in the manifest at {where} and is gone; keep it, or list it "
                                   'under "retired" with a "why"') for name in sorted(required - used - retired)]
    return found
