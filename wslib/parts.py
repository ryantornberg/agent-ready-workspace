"""Load the parts a workspace's manifest names, and run each part's own cases.

A part is one Python file. It declares what it is and exposes one function:

    KIND = "check"     def run(snapshot, config) -> [finding(...), ...]
    KIND = "hook"      EVENT = "before-shell" or "before-edit"
                       def decide(event, config) -> None to allow, or the reason to refuse

Next to it sits <name>.cases.json: the part's own tests, as data. Loading a
part runs its cases, every time. A part with no cases, or with a case that
fails, is refused. A check that nobody tests can stop finding things, and a
hook can stop firing, and nobody notices.

A check case:  {"name", "files": {path: text}, "changed": [paths], "config": {}, "expect": ["text in a finding", ...]}
               "expect": [] means the case must produce no findings. Every finding must be expected.
A hook case:   {"name", "event": {...}, "config": {}, "allow": true|false}
"""
import importlib.util
import json
import pathlib

from . import snapshot as snapshots

KINDS = ("check", "hook")
EVENTS = ("before-shell", "before-edit")


class PartError(Exception):
    pass


def finding(path, line, message, level="error"):
    return {"path": path, "line": line, "message": message, "level": level}


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
        """Run the part's cases. Return a list of "case name: what went wrong"."""
        failures = []
        for case in self.cases:
            config = {**self.config, **case.get("config", {})}
            try:
                if self.kind == "check":
                    got = [f["message"] for f in self.run(snapshots.Memory(case["files"], case.get("changed", ())), config)]
                    want = case["expect"]
                    missing = [w for w in want if not any(w in g for g in got)]
                    extra = [g for g in got if not any(w in g for w in want)]
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


def parse_manifest(text, where="workspace.json"):
    try:
        manifest = json.loads(text)
    except json.JSONDecodeError as error:
        raise PartError(f"{where}: {error}")
    parts = manifest.get("parts") if isinstance(manifest, dict) else None
    if not isinstance(parts, list) or not parts:
        raise PartError(f'{where}: "parts" must be a non-empty list')
    return manifest


def load_manifest(root):
    try:
        return parse_manifest((pathlib.Path(root) / "workspace.json").read_text(encoding="utf-8"))
    except FileNotFoundError:
        raise PartError(f"no workspace.json in {root}")


def _read_cases(name, kind, cases_file):
    try:
        cases = json.loads(cases_file.read_text(encoding="utf-8"))
    except FileNotFoundError:
        raise PartError(f"part {name}: refused, it has no cases file ({cases_file.name})")
    except json.JSONDecodeError as error:
        raise PartError(f"part {name}: {cases_file.name}: {error}")
    if not isinstance(cases, list) or not cases:
        raise PartError(f"part {name}: refused, {cases_file.name} holds no cases")
    for case in cases:
        if kind == "check":
            well_formed = isinstance(case, dict) and isinstance(case.get("name"), str) \
                and isinstance(case.get("files"), dict) and isinstance(case.get("expect"), list)
        else:
            well_formed = isinstance(case, dict) and isinstance(case.get("name"), str) \
                and isinstance(case.get("event"), dict) and isinstance(case.get("allow"), bool)
        if not well_formed or not isinstance(case.get("config", {}), dict):
            needs = '"name", "files" and "expect"' if kind == "check" else '"name", "event" and "allow"'
            raise PartError(f"part {name}: {cases_file.name}: every case needs {needs}: {case!r}")
    if kind == "check" and not any(case["expect"] for case in cases):
        raise PartError(f"part {name}: refused, no case shows it finding anything")
    if kind == "hook" and {case["allow"] for case in cases} != {True, False}:
        raise PartError(f"part {name}: refused, its cases must show it both allowing and refusing")
    return cases


def load(root, entry, run_cases=True):
    """Load one manifest entry: {"use": "links", ...config}. "use" is a name under parts/, or a path to a .py file.

    The part's cases run as it loads, and a failing case refuses the part.
    run_cases=False is for `ws.py selftest`, which reports every failure instead of stopping at the first.
    """
    if not isinstance(entry, dict) or not isinstance(entry.get("use"), str):
        raise PartError(f'each part needs a "use": {entry!r}')
    use = entry["use"]
    source = pathlib.Path(root) / (use if use.endswith(".py") else f"parts/{use}.py")
    name = source.stem
    if not source.is_file():
        raise PartError(f"part {name}: no file at {use if use.endswith('.py') else 'parts/' + use + '.py'}")
    try:
        spec = importlib.util.spec_from_file_location(f"workspace_part_{name}", source)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
    except Exception as error:
        raise PartError(f"part {name}: cannot be loaded: {type(error).__name__}: {error}")

    kind = getattr(module, "KIND", None)
    if kind not in KINDS:
        raise PartError(f"part {name}: KIND must be one of {KINDS}")
    if not callable(getattr(module, "run" if kind == "check" else "decide", None)):
        raise PartError(f"part {name}: a {kind} needs a {'run' if kind == 'check' else 'decide'} function")
    if kind == "hook" and getattr(module, "EVENT", None) not in EVENTS:
        raise PartError(f"part {name}: a hook's EVENT must be one of {EVENTS}")

    cases = _read_cases(name, kind, source.with_name(f"{name}.cases.json"))
    config = {key: value for key, value in entry.items() if key != "use"}
    part = Part(name, module, cases, config)
    if run_cases:
        failures = part.failed_cases()
        if failures:
            raise PartError(f"part {name}: refused, {len(failures)} of its {len(cases)} cases fail; first: {failures[0]}")
    return part


def load_all(root, manifest=None, run_cases=True):
    manifest = manifest or load_manifest(root)
    return [load(root, entry, run_cases) for entry in manifest["parts"]]
