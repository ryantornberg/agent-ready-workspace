"""M3 slice C3c: the worktree's copy of the local settings, and the ignore entry (criterion 64)."""
import json
import os
import pathlib
import shutil
import subprocess
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parent.parent
NAME = ".claude/settings.local.json"


def git(folder, *args):
    env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    return subprocess.run(["git", "-C", str(folder), "-c", "user.name=t", "-c", "user.email=t@example.invalid",
                           "-c", "commit.gpgsign=false", *args], check=True, capture_output=True, text=True, env=env)


class WorktreeSettingsTests(unittest.TestCase):
    def setUp(self):
        self.base = pathlib.Path(os.path.realpath(tempfile.mkdtemp(prefix="settings-")))
        self.addCleanup(shutil.rmtree, self.base, ignore_errors=True)
        self.main = self.base / "main"
        (self.main / ".githooks").mkdir(parents=True)
        shutil.copy(ROOT / ".githooks" / "post-checkout", self.main / ".githooks" / "post-checkout")
        shutil.copy(ROOT / ".gitignore", self.main / ".gitignore")
        git(self.main, "init", "-q", "-b", "main")
        git(self.main, "config", "core.hooksPath", ".githooks")
        git(self.main, "add", ".")
        git(self.main, "commit", "-q", "-m", "chore: start")
        (self.main / ".claude").mkdir()
        (self.main / NAME).write_text(json.dumps({"permissions": {"allow": ["Bash(make)"]}}))

    def test_a_new_worktree_gets_a_copy(self):
        git(self.main, "worktree", "add", "-q", str(self.base / "w"), "-b", "side")
        self.assertEqual((self.base / "w" / NAME).read_text(), (self.main / NAME).read_text())

    def test_a_later_checkout_in_a_worktree_copies_nothing(self):
        git(self.main, "branch", "side")
        git(self.main, "worktree", "add", "-q", "--no-checkout", str(self.base / "w"), "side")
        (self.base / "w" / ".claude").mkdir()
        (self.base / "w" / NAME).write_text("{}")
        git(self.base / "w", "checkout", "-q", "side")
        self.assertEqual((self.base / "w" / NAME).read_text(), "{}")

    def test_a_branch_checkout_in_the_main_copy_copies_nothing(self):
        (self.main / NAME).unlink()
        git(self.main, "checkout", "-q", "-b", "other")
        self.assertFalse((self.main / NAME).exists())

    def test_with_no_local_settings_the_worktree_add_still_succeeds(self):
        (self.main / NAME).unlink()
        git(self.main, "worktree", "add", "-q", str(self.base / "w"), "-b", "side")
        self.assertFalse((self.base / "w" / NAME).exists())

    def test_the_file_is_ignored(self):
        self.assertEqual(subprocess.run(["git", "-C", str(ROOT), "check-ignore", "-q", "--no-index", NAME]).returncode, 0)
        self.assertEqual(git(self.main, "status", "--porcelain").stdout, "")


if __name__ == "__main__":
    unittest.main()
