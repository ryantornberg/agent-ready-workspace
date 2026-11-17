"""Every part added since M2 has cases that bite: run against a stub that allows everything and finds nothing,
at least one of its cases fails (criterion 22). Run: python3 -m unittest tests.test_cases_bite -b"""
import json
import pathlib
import sys
import types
import unittest

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from wslib import parts as partlib  # noqa: E402

NEW_PARTS = ("direct_push", "no_admin_merge", "browser_isolation")


def stub_of(part):
    module = types.ModuleType(f"stub_{part.name}")
    for name in ("KIND", "EVENT", "MODE", "PHASES"):
        if hasattr(part.module, name):
            setattr(module, name, getattr(part.module, name))
    module.run = lambda snapshot, config: []
    module.decide = lambda event, config: None
    return partlib.Part(part.name, module, part.cases, part.config)


class CasesBiteTests(unittest.TestCase):
    def test_every_new_part_has_a_case_that_a_do_nothing_stub_fails(self):
        manifest = json.loads((ROOT / "workspace.json").read_text(encoding="utf-8"))
        for name in NEW_PARTS:
            with self.subTest(name):
                entry = next(e for e in manifest["parts"] if e.get("use") == name)
                part = partlib.load(ROOT, entry)
                self.assertEqual(part.failed_cases(), [])
                self.assertTrue(stub_of(part).failed_cases(), f"{name}: a stub that does nothing passes every case")


if __name__ == "__main__":
    unittest.main()
