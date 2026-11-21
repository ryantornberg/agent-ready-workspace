"""Criterion 66, and the steps the cold-clone job runs.

The job runs every night, and on a pull request or a push to main that changes a setup page, the script
that reads its marked steps, or the job itself, and on no other change. GitHub decides that from the
paths in the workflow, so this holds those paths to tools/setup_steps.py's SETUP_PAGES. The run on the
pull request that adds the job, and the runs GitHub lists, are the evidence that GitHub follows them.

Run: python3 -m unittest tests.test_cold_clone -b
"""
import pathlib
import re
import sys
import unittest

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))

import setup_steps  # noqa: E402

WORKFLOW = ROOT / ".github/workflows/cold-clone.yml"


def section(text, name):
    """The lines of a top-level key under `on:`, two spaces in, up to the next key at that depth."""
    match = re.search(rf"(?ms)^  {name}:\n(.*?)(?=^  \S|^\S|\Z)", text)
    return match.group(1) if match else None


def paths(block):
    match = re.search(r"(?m)^    paths:\n((?:      - .*\n)+)", block)
    return [line.split("- ", 1)[1].strip() for line in match.group(1).splitlines()] if match else None


class TriggerTests(unittest.TestCase):
    def setUp(self):
        self.text = WORKFLOW.read_text(encoding="utf-8")
        self.want = sorted(setup_steps.SETUP_PAGES + ("tools/setup_steps.py", ".github/workflows/cold-clone.yml"))

    def test_it_runs_every_night(self):
        cron = re.search(r'(?m)^    - cron: "([^"]+)"', section(self.text, "schedule")).group(1).split()
        self.assertEqual(cron[2:], ["*", "*", "*"], "every day of every month, every day of the week")

    def test_a_pull_request_runs_it_only_when_a_setup_page_changes(self):
        self.assertEqual(sorted(paths(section(self.text, "pull_request"))), self.want)

    def test_a_push_to_main_runs_it_only_when_a_setup_page_changes(self):
        push = section(self.text, "push")
        self.assertRegex(push, r"(?m)^    branches: \[main\]$")
        self.assertEqual(sorted(paths(push)), self.want)

    def test_nothing_else_triggers_it(self):
        on = re.search(r"(?ms)^on:\n(.*?)(?=^\S)", self.text).group(1)
        self.assertEqual(re.findall(r"(?m)^  (\S+):", on), ["schedule", "pull_request", "push"])


class StepTests(unittest.TestCase):
    def test_the_readme_marks_the_steps_a_fresh_clone_needs(self):
        script = setup_steps.script("README.md", (ROOT / "README.md").read_text(encoding="utf-8"))
        for command in ("python3 ws.py pins", "python3 ws.py selftest", "python3 ws.py check",
                        "python3 -m unittest discover -b tests", "git config core.hooksPath .githooks"):
            self.assertIn(command, script)

    def test_only_marked_blocks_are_taken(self):
        text = "# P\n\n```\nnot this\n```\n\n<!-- setup -->\n\n```bash\nthis\n```\n\n````\n<!-- setup -->\n```\nnor this\n```\n````\n"
        self.assertEqual(setup_steps.steps(text), [(7, ["this"])])

    def test_a_page_with_no_marked_block_or_a_marker_with_no_block_fails(self):
        with self.assertRaisesRegex(ValueError, "no block is marked"):
            setup_steps.script("p.md", "# P\n\n```\nls\n```\n")
        with self.assertRaisesRegex(ValueError, "line 3: a setup marker must be followed"):
            setup_steps.steps("# P\n\n<!-- setup -->\nText.\n")
        with self.assertRaisesRegex(ValueError, "never closed"):
            setup_steps.steps("<!-- setup -->\n```\nls\n")

    def test_the_script_stops_at_the_first_failure(self):
        self.assertTrue(setup_steps.script("p.md", "<!-- setup -->\n```\nls\n```\n").startswith("set -eu\n"))


if __name__ == "__main__":
    unittest.main()
