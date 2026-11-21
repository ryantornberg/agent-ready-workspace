"""M3 slice B1, criterion 20: every command block a tutorial marks runnable runs green in a fresh clone.

CI runs this file on Linux, macOS and Windows. With no tutorial it passes, saying so; the tests below it show it
fails a tutorial whose blocks fail, and that the pre-push hook refuses a push to main changing one.

Run: python3 -m unittest tests.test_tutorials -b
"""
import pathlib
import shutil
import subprocess
import sys
import unittest

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from tests.test_core import Folder  # noqa: E402
from wslib import blocks  # noqa: E402

ZERO = "0" * 40


def tutorial(*bodies):
    text = "---\nkind: tutorial\nlast-reviewed: 2026-11-21\n---\n\n# A tutorial\n\nFor a newcomer.\n\n**In short:** run it.\n"
    for body in bodies:
        text += f"\n<!-- runnable -->\n```sh\n{body}\n```\n"
    return text


class EveryTutorialTests(unittest.TestCase):
    def test_every_tutorial_s_runnable_blocks_pass_in_a_fresh_clone(self):
        head = subprocess.run(["git", "-C", str(ROOT), "rev-parse", "HEAD"], capture_output=True, text=True)
        if head.returncode != 0:
            self.skipTest("not a git checkout")
        listed = subprocess.run(["git", "-C", str(ROOT), "ls-tree", "-r", "--name-only", "HEAD", blocks.TUTORIALS],
                                capture_output=True, text=True).stdout.split("\n")
        pages = [page for page in listed if blocks.is_tutorial(page)]
        print(f"{len(pages)} tutorial(s) at HEAD")
        for page in pages:
            with self.subTest(page):
                passed, output = blocks.run_tutorial(ROOT, head.stdout.strip(), page)
                self.assertTrue(passed, output)


class Fixture(Folder):
    """A small workspace with the launcher, committed, and a bare remote whose main holds it."""

    def setUp(self):
        super().setUp()
        for name in ("launch.sh", "start.py"):
            self.write(f"wslib/{name}", (ROOT / "wslib" / name).read_text(encoding="utf-8"))
        self.workspace({"use": "direct_push", "why": "test", "machinery": ["wslib/"]})
        self.write("README.md", "# W\n")
        self.write("hello.py", "print('hello from', __file__)\n")
        self.git("init", "-q", "-b", "main")
        self.git("add", ".")
        self.git("commit", "-q", "--no-verify", "-m", "chore: start")
        self.remote = self.root.parent / (self.root.name + "-remote.git")
        subprocess.run(["git", "init", "-q", "--bare", "-b", "main", str(self.remote)], check=True, capture_output=True)
        self.addCleanup(shutil.rmtree, str(self.remote), True)
        self.git("remote", "add", "origin", str(self.remote))
        self.git("push", "-q", "--no-verify", "origin", "main")

    def commit(self, path, text):
        self.write(path, text)
        self.git("add", "--", path)
        self.git("commit", "-q", "--no-verify", "-m", "docs: a tutorial")
        return self.git("rev-parse", "HEAD").stdout.strip()

    def push(self, remote_ref="refs/heads/main"):
        sha = self.git("rev-parse", "HEAD").stdout.strip()
        tip = subprocess.run(["git", "--git-dir", str(self.remote), "rev-parse", "--verify", "-q", remote_ref],
                             capture_output=True, text=True).stdout.strip() or ZERO
        return self.ws("check", "--push", "origin", stdin=f"refs/heads/x {sha} {remote_ref} {tip}\n")


class RunTests(Fixture):
    def test_passing_blocks_pass_in_a_clone_of_the_commit(self):
        sha = self.commit("docs/tutorials/one.md", tutorial("test -f README.md", "python3 hello.py"))
        self.write("README.md", "changed on disk, not committed\n")
        passed, output = blocks.run_tutorial(self.root, sha, "docs/tutorials/one.md")
        self.assertTrue(passed, output)
        self.assertIn("hello from", output, "python3 runs through the clone's launcher")

    def test_a_failing_block_fails_and_stops_the_rest(self):
        sha = self.commit("docs/tutorials/one.md", tutorial("echo first", "false", "echo never"))
        passed, output = blocks.run_tutorial(self.root, sha, "docs/tutorials/one.md")
        self.assertFalse(passed)
        self.assertIn("first", output)
        self.assertNotIn("never", output)

    def test_a_marker_with_no_block_fails_and_an_example_block_is_not_run(self):
        sha = self.commit("docs/tutorials/one.md", tutorial() + "\n```sh\nfalse\n```\n\n<!-- runnable -->\nText.\n")
        passed, output = blocks.run_tutorial(self.root, sha, "docs/tutorials/one.md")
        self.assertFalse(passed)
        self.assertIn("must be followed by a fenced code block", output)

    def test_a_tutorial_with_no_runnable_block_passes_and_says_so(self):
        sha = self.commit("docs/tutorials/one.md", tutorial())
        passed, output = blocks.run_tutorial(self.root, sha, "docs/tutorials/one.md")
        self.assertTrue(passed, output)
        self.assertIn("nothing ran", output)


class PushTests(Fixture):
    def test_a_push_to_main_changing_a_failing_tutorial_is_refused(self):
        self.commit("docs/tutorials/one.md", tutorial("false"))
        code, out = self.push()
        self.assertEqual(code, 1, out)
        self.assertIn("docs/tutorials/one.md:1: error: [tutorials] its runnable blocks fail", out)

    def test_a_push_to_main_changing_a_passing_tutorial_passes(self):
        self.commit("docs/tutorials/one.md", tutorial("test -f README.md"))
        code, out = self.push()
        self.assertEqual(code, 0, out)

    def test_a_push_to_another_branch_does_not_run_them(self):
        self.commit("docs/tutorials/one.md", tutorial("false"))
        code, out = self.push("refs/heads/topic")
        self.assertEqual(code, 0, out)


if __name__ == "__main__":
    unittest.main()
