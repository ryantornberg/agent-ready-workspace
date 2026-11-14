"""Load the parts a workspace's manifest names, and run each part's own cases.

A part is one Python file. It declares what it is and exposes one function:

    KIND = "check"     def run(snapshot, config) -> [finding(...), ...]
    KIND = "hook"      EVENT = "before-shell"
                       def decide(event, config) -> None to allow, or the reason to refuse

Next to it sits <name>.cases.json: the part's own tests, as data. A part with
no cases is refused. A check that nobody tests can stop finding things, and a
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
        return self.module.run(snapshot, self.config if config is None else config)

    def decide(self, event, config=None):
        return self.module.decide(event, self.config if config is None else config)

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
            except Exception as error:  # a case that crashes the part is a failed case
                failures.append(f"{case['name']}: raised {type(error).__name__}: {error}")
        return failures


def load_manifest(root):
    path = pathlib.Path(root) / "workspace.json"
    try:
        manifest = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        raise PartError(f"no workspace.json in {root}")
    except json.JSONDecodeError as error:
        raise PartError(f"workspace.json: {error}")
    if not isinstance(manifest.get("parts"), list) or not manifest["parts"]:
        raise PartError('workspace.json: "parts" must be a non-empty list')
    return manifest


def load(root, entry):
    """Load one manifest entry: {"use": "links", ...config}. "use" is a name under parts/, or a path to a .py file."""
    if not isinstance(entry, dict) or "use" not in entry:
        raise PartError(f'each part needs a "use": {entry!r}')
    use = entry["use"]
    source = pathlib.Path(root) / (use if use.endswith(".py") else f"parts/{use}.py")
    name = source.stem
    if not source.is_file():
        raise PartError(f"part {name}: no file at {source.relative_to(root).as_posix()}")
    spec = importlib.util.spec_from_file_location(f"workspace_part_{name}", source)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    kind = getattr(module, "KIND", None)
    if kind not in KINDS:
        raise PartError(f"part {name}: KIND must be one of {KINDS}")
    if not callable(getattr(module, "run" if kind == "check" else "decide", None)):
        raise PartError(f"part {name}: a {kind} needs a {'run' if kind == 'check' else 'decide'} function")
    if kind == "hook" and not getattr(module, "EVENT", None):
        raise PartError(f"part {name}: a hook names its EVENT")

    cases_file = source.with_name(f"{name}.cases.json")
    try:
        cases = json.loads(cases_file.read_text(encoding="utf-8"))
    except FileNotFoundError:
        raise PartError(f"part {name}: refused, it has no cases file ({cases_file.name})")
    except json.JSONDecodeError as error:
        raise PartError(f"part {name}: {cases_file.name}: {error}")
    if not isinstance(cases, list) or not cases:
        raise PartError(f"part {name}: refused, {cases_file.name} holds no cases")
    if kind == "check" and not any(case.get("expect") for case in cases):
        raise PartError(f"part {name}: refused, no case shows it finding anything")
    if kind == "hook" and {case.get("allow") for case in cases} != {True, False}:
        raise PartError(f"part {name}: refused, its cases must show it both allowing and refusing")

    config = {key: value for key, value in entry.items() if key != "use"}
    return Part(name, module, cases, config)


def load_all(root):
    manifest = load_manifest(root)
    return [load(root, entry) for entry in manifest["parts"]]
