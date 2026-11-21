"""Criterion 44: the pinned-repository initializer, on fixture repositories.

A fresh clone of a workspace pins four code repositories: one whose remote answers, one whose remote is gone,
one already checked out with local work in it, and one whose remote hangs. `ws.py pins` checks out the first,
skips the second and fourth with a note and no prompt, and leaves the third exactly as it was.

Run: python3 -m unittest tests.test_pins -b
"""
import os
import pathlib
import shutil
import subprocess
import sys
import tempfile
import time
import unittest
from unittest import mock

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from wslib import gitcall, pins  # noqa: E402

IDENTITY = ["-c", "user.name=t", "-c", "user.email=t@example.invalid", "-c", "commit.gpgsign=false"]
# Local fixture remotes need the file protocol, which git turns off for submodules; the hanging remote needs ext.
ALLOW = {"GIT_CONFIG_COUNT": "2", "GIT_CONFIG_KEY_0": "protocol.file.allow", "GIT_CONFIG_VALUE_0": "always",
         "GIT_CONFIG_KEY_1": "protocol.ext.allow", "GIT_CONFIG_VALUE_1": "always"}


def git(folder, *args):
    done = subprocess.run(["git", "-C", str(folder), *IDENTITY, *args], capture_output=True, text=True,
                          env=dict(os.environ, **ALLOW), stdin=subprocess.DEVNULL)
    if done.returncode != 0:
        raise AssertionError(f"git {' '.join(args)}: {done.stderr}")
    return done.stdout.strip()


class ResolveTests(unittest.TestCase):
    def test_a_relative_url_is_read_against_the_workspace_remote(self):
        for url, base, want in (
                ("../orders-api.git", "https://github.com/team/workspace.git", "https://github.com/team/orders-api.git"),
                ("../orders-api.git", "git@github.com:team/workspace.git", "git@github.com:team/orders-api.git"),
                ("./orders-api", "/srv/git/workspace", "/srv/git/workspace/orders-api"),
                ("../../other/x.git", "https://host/a/b/ws.git", "https://host/a/other/x.git"),
                ("https://host/x.git", "https://host/ws.git", "https://host/x.git")):
            with self.subTest(url=url, base=base):
                self.assertEqual(pins.resolve(url, base), want)

    def test_the_probe_runs_with_prompts_off(self):
        env = gitcall.environment()
        self.assertEqual(env["GIT_TERMINAL_PROMPT"], "0")
        self.assertEqual(env["GCM_INTERACTIVE"], "never")
        self.assertIn("BatchMode=yes", env["GIT_SSH_COMMAND"])


class InitializerTests(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.tmp = pathlib.Path(self._tmp.name).resolve()
        patch = mock.patch.dict(os.environ, ALLOW)
        patch.start()
        self.addCleanup(patch.stop)

    def upstream(self, name):
        folder = self.tmp / name
        folder.mkdir()
        git(folder, "init", "-q", "-b", "main")
        (folder / "code.txt").write_text(name, encoding="utf-8")
        git(folder, "add", "code.txt")
        git(folder, "commit", "-q", "-m", "code")
        return folder

    def workspace(self, names):
        """A workspace that pins each named upstream under src/, and a fresh clone of it, which holds none."""
        origin = self.tmp / "workspace"
        origin.mkdir()
        git(origin, "init", "-q", "-b", "main")
        for name in names:
            git(origin, "submodule", "add", "-q", str(self.upstream(name)), f"src/{name}")
        git(origin, "commit", "-q", "-m", "pins")
        fresh = self.tmp / "fresh"
        git(self.tmp, "clone", "-q", str(origin), str(fresh))
        return fresh

    def test_a_fresh_clone_gets_the_reachable_pins_and_keeps_the_rest_as_they_were(self):
        fresh = self.workspace(["reachable", "gone", "present"])
        shutil.rmtree(self.tmp / "gone")
        git(fresh, "submodule", "update", "--init", "-q", "--", "src/present")
        present = fresh / "src/present"
        (present / "code.txt").write_text("local work, not committed", encoding="utf-8")
        git(present, "switch", "-q", "-c", "my-branch")
        before = git(present, "rev-parse", "HEAD"), git(present, "status", "--porcelain")

        results = {path: (outcome, note) for path, outcome, note in pins.initialize(fresh, timeout=10)}

        self.assertEqual(results["src/reachable"][0], "initialized")
        self.assertEqual((fresh / "src/reachable/code.txt").read_text(encoding="utf-8"), "reachable")
        self.assertEqual(results["src/gone"][0], "unreachable")
        self.assertIn("did not answer", results["src/gone"][1])
        self.assertFalse((fresh / "src/gone/.git").exists())
        self.assertEqual(results["src/present"][0], "untouched")
        self.assertEqual((git(present, "rev-parse", "HEAD"), git(present, "status", "--porcelain")), before)
        self.assertEqual(git(present, "branch", "--show-current"), "my-branch")
        self.assertEqual((present / "code.txt").read_text(encoding="utf-8"), "local work, not committed")

    def test_a_folder_with_files_but_no_checkout_is_left_alone(self):
        fresh = self.workspace(["copied"])
        (fresh / "src/copied/notes.txt").write_text("someone's files", encoding="utf-8")
        (path, outcome, _), = pins.initialize(fresh, timeout=10)
        self.assertEqual((path, outcome), ("src/copied", "untouched"))
        self.assertEqual(sorted(p.name for p in (fresh / "src/copied").iterdir()), ["notes.txt"])

    @unittest.skipIf(os.name == "nt", "the hanging remote runs sleep through git's ext transport")
    def test_hanging_remotes_are_probed_at_once_and_skipped_at_the_time_limit(self):
        fresh = self.workspace(["reachable"])
        sha = git(fresh, "rev-parse", "HEAD:src/reachable")
        for name in ("slow-a", "slow-b", "slow-c"):
            git(fresh, "config", "-f", ".gitmodules", f"submodule.{name}.path", f"src/{name}")
            git(fresh, "config", "-f", ".gitmodules", f"submodule.{name}.url", "ext::sleep 30")
            git(fresh, "update-index", "--add", "--cacheinfo", f"160000,{sha},src/{name}")
        started = time.monotonic()
        results = {path: outcome for path, outcome, _ in pins.initialize(fresh, timeout=2)}
        took = time.monotonic() - started
        self.assertEqual(results, {"src/reachable": "initialized", "src/slow-a": "unreachable",
                                   "src/slow-b": "unreachable", "src/slow-c": "unreachable"})
        self.assertLess(took, 5.5, "three 2-second probes in a row would take 6 seconds or more")

    def test_a_pin_with_no_url_is_reported_and_not_touched(self):
        fresh = self.workspace(["reachable"])
        git(fresh, "config", "-f", ".gitmodules", "--remove-section", "submodule.src/reachable")
        (path, outcome, note), = pins.initialize(fresh, timeout=10)
        self.assertEqual((path, outcome), ("src/reachable", "no-url"))
        self.assertFalse((fresh / "src/reachable/.git").exists())

    def test_the_command_prints_each_pin_and_fails_only_when_a_checkout_fails(self):
        fresh = self.workspace(["reachable", "gone"])
        shutil.rmtree(self.tmp / "gone")
        done = subprocess.run([sys.executable, str(ROOT / "ws.py"), "--root", str(fresh), "pins"],
                              capture_output=True, text=True, stdin=subprocess.DEVNULL, timeout=60)
        self.assertEqual(done.returncode, 0, done.stderr)
        self.assertIn("src/reachable: initialized", done.stdout)
        self.assertIn("src/gone: unreachable", done.stdout)
        self.assertIn("1 initialized, 1 unreachable", done.stdout)

    def test_a_workspace_with_no_pins_says_so(self):
        folder = self.tmp / "plain"
        folder.mkdir()
        git(folder, "init", "-q")
        self.assertEqual(pins.initialize(folder), [])


if __name__ == "__main__":
    unittest.main()
