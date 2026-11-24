"""Hidden from the agent. evals/run.py runs it in a copy of the folder the agent left: is the request met?

The reminder read `git commit -m"add export handler"` as a cluster of short options holding -a, because the
shell joins the attached message to -m. A message is a value, not more options: the reminder must stay quiet
on it, and still catch every form that stages everything.
"""
import pathlib
import sys
import unittest

sys.path.insert(0, str(pathlib.Path.cwd() / "src"))

from staging import stages_all  # noqa: E402


class Acceptance(unittest.TestCase):
    def test_an_attached_message_is_not_read_as_options(self):
        for command in ('git commit -m"add export handler"', "git commit -madd", 'git commit -q -m"all done"',
                        "git commit -m 'add export handler'"):
            with self.subTest(command):
                self.assertFalse(stages_all(command))

    def test_staging_everything_is_still_caught(self):
        for command in ("git add -A", "git add .", "git add --all", "git commit -a -m x", "git commit -am x",
                        'git commit -am"add export handler"', "git commit -qa -m x"):
            with self.subTest(command):
                self.assertTrue(stages_all(command))


if __name__ == "__main__":
    unittest.main()
