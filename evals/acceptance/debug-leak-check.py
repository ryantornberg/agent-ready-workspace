"""Hidden from the agent. evals/run.py runs it in a copy of the folder the agent left: is the request met?

The request asks for the cause only, so the code stays as it was. What the run must leave is a regression test
that fails on that code and passes once the cause is fixed. The cause: the check searches
the JSON text of the transcript, where every backslash is written twice, so a Windows path is never found.
This test fixes the cause in a scratch copy and runs the agent's tests there.
"""
import pathlib
import shutil
import subprocess
import sys
import tempfile
import unittest

FIXED = '''"""The leak check, with its cause fixed: it reads each string, not the JSON text."""


def _strings(value):
    if isinstance(value, str):
        yield value
    elif isinstance(value, dict):
        for item in value.values():
            yield from _strings(item)
    elif isinstance(value, list):
        for item in value:
            yield from _strings(item)


def leaks(actions, secrets):
    text = "\\n".join(_strings(actions)).lower()
    return [secret for secret in secrets if secret.lower() in text]
'''


def suite(folder, fixed):
    """The suite's run in a scratch copy of the folder, with the cause fixed or not."""
    with tempfile.TemporaryDirectory() as scratch:
        copy = pathlib.Path(scratch) / "copy"
        shutil.copytree(folder, copy, ignore=shutil.ignore_patterns(".git", "__pycache__", "acceptance_hidden.py"))
        if fixed:
            (copy / "src" / "leaks.py").write_text(FIXED, encoding="utf-8")
        return subprocess.run([sys.executable, "-B", "-m", "unittest"], cwd=copy, capture_output=True, text=True)


class Acceptance(unittest.TestCase):
    def test_a_test_shows_the_failure_and_passes_once_the_cause_is_fixed(self):
        here = pathlib.Path.cwd()
        self.assertNotEqual(suite(here, fixed=False).returncode, 0, "no test shows the failure")
        done = suite(here, fixed=True)
        self.assertEqual(done.returncode, 0, done.stderr[-2000:])


if __name__ == "__main__":
    unittest.main()
