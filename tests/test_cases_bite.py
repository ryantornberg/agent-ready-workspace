"""Every part's cases bite (M3 criterion 42; M2 criterion 22 held it for the parts added since M2).

Each part the manifest lists is run against two stubs that keep its kind, event and mode:
- one that allows everything and finds nothing: some case must fail, or the part's cases cannot tell it from
  a part that does nothing;
- one that refuses everything and always finds something: some case must fail, or the part's cases cannot
  tell it from a part that blocks every call.
The parts are read from the manifest, so a part added later is held to this with no edit here.
Run: python3 -m unittest tests.test_cases_bite -b"""
import json
import pathlib
import sys
import types
import unittest

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from wslib import parts as partlib  # noqa: E402

STUB_FINDING = "a stub that finds something in every snapshot"
STUB_REASON = "a stub that refuses every call"


def stub_of(part, refuses):
    """The part with its run and decide replaced: allows and finds nothing, or refuses and always finds something."""
    module = types.ModuleType(f"stub_{part.name}")
    for name in ("KIND", "EVENT", "MODE", "PHASES", "NEEDS"):
        if hasattr(part.module, name):
            setattr(module, name, getattr(part.module, name))
    if refuses:
        module.run = lambda snapshot, config: [partlib.finding("stub.md", 1, STUB_FINDING)]
        module.decide = lambda event, config: STUB_REASON
    else:
        module.run = lambda snapshot, config: []
        module.decide = lambda event, config: None
    return partlib.Part(part.name, module, part.cases, part.config)


def manifest_parts():
    manifest = json.loads((ROOT / "workspace.json").read_text(encoding="utf-8"))
    return [partlib.load(ROOT, entry, tiers=manifest.get("tiers")) for entry in manifest["parts"]]


class CasesBiteTests(unittest.TestCase):
    def test_the_parts_come_from_the_manifest(self):
        manifest = json.loads((ROOT / "workspace.json").read_text(encoding="utf-8"))
        self.assertEqual([part.name for part in manifest_parts()],
                         [pathlib.PurePosixPath(entry["use"]).stem for entry in manifest["parts"]])

    def test_every_part_has_a_case_that_a_do_nothing_stub_fails(self):
        for part in manifest_parts():
            with self.subTest(part.name):
                self.assertEqual(part.failed_cases(), [])
                self.assertTrue(stub_of(part, refuses=False).failed_cases(),
                                f"{part.name}: a stub that allows everything and finds nothing passes every case")

    def test_every_part_has_a_case_that_a_refuse_everything_stub_fails(self):
        for part in manifest_parts():
            with self.subTest(part.name):
                self.assertTrue(stub_of(part, refuses=True).failed_cases(),
                                f"{part.name}: a stub that refuses everything and always finds something passes every case")

    def test_the_stubs_are_told_apart_from_a_real_part(self):
        """The test itself bites: a part whose cases only ever allow, or only ever find, is caught."""
        lenient = types.ModuleType("lenient")
        lenient.KIND, lenient.EVENT = "hook", "before-shell"
        lenient.decide = lambda event, config: None
        only_allows = partlib.Part("lenient", lenient, [{"name": "allows", "event": {"command": "ls"}, "allow": True}], {})
        self.assertFalse(stub_of(only_allows, refuses=False).failed_cases())
        finder = types.ModuleType("finder")
        finder.KIND = "check"
        finder.run = lambda snapshot, config: [partlib.finding("a.md", 1, STUB_FINDING)]
        only_finds = partlib.Part("finder", finder, [{"name": "finds", "files": {}, "expect": [STUB_FINDING]}], {})
        self.assertFalse(stub_of(only_finds, refuses=True).failed_cases())


if __name__ == "__main__":
    unittest.main()
