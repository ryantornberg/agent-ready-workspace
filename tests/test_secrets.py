"""M3 slice C5f: secrets kept out of the agent's shell (criterion 40).

`python3 ws.py with-secrets` runs for real, in throwaway repositories with a secrets file, with this Python as the
child: the child sees the named values, the shell that called it does not, and a shell, env, printenv or a program
that runs another is refused as the child. The `secrets_shell` hook's own cases cover the dumps and the reads;
the tests here hold the hook and the command to the same lists.

Run: python3 -m unittest tests.test_secrets -b
"""
import json
import os
import pathlib
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from wslib import parts as partlib  # noqa: E402
from wslib import secretrules  # noqa: E402
from wslib import secrets  # noqa: E402

VALUE = "s3cr3t-value-for-the-test"
OTHER = "another-value-never-named"
PRINT = "import os; print('child=' + os.environ.get('API_KEY', 'unset')); print('other=' + os.environ.get('OTHER_KEY', 'unset'))"


def git(folder, *args):
    subprocess.run(["git", "-C", str(folder), *args], check=True, capture_output=True)


def entry(name):
    manifest = json.loads((ROOT / "workspace.json").read_text(encoding="utf-8"))
    return next(e for e in manifest["parts"] if e.get("use") == name)


class WithSecretsTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.repo = pathlib.Path(self.tmp.name) / "repo"
        self.repo.mkdir()
        git(self.repo, "init", "-q")
        (self.repo / ".env").write_text(f"# the test's values\nexport API_KEY='{VALUE}'\nOTHER_KEY={OTHER}\n",
                                        encoding="utf-8")
        self.env = {k: v for k, v in os.environ.items() if k not in ("API_KEY", "OTHER_KEY", "WS_SECRETS_FILE")}

    def tearDown(self):
        self.tmp.cleanup()

    def ws(self, *args, root=None):
        return subprocess.run([sys.executable, str(ROOT / "ws.py"), "--root", str(root or self.repo), "with-secrets",
                               *args], capture_output=True, text=True, env=self.env, stdin=subprocess.DEVNULL)

    def test_the_child_sees_the_named_value_and_no_other(self):
        done = self.ws("API_KEY", "--", sys.executable, "-c", PRINT)
        self.assertEqual(done.returncode, 0, done.stderr)
        self.assertIn(f"child={VALUE}", done.stdout)
        self.assertIn("other=unset", done.stdout)

    @unittest.skipUnless(shutil.which("sh"), "needs a POSIX shell to stand for the agent's shell")
    def test_the_calling_shell_does_not_see_the_value(self):
        python = pathlib.Path(sys.executable).as_posix()   # forward slashes, which Git's sh on Windows keeps as written
        command = " ".join([f'"{python}"', f'"{(ROOT / "ws.py").as_posix()}"', "--root", f'"{self.repo.as_posix()}"',
                            "with-secrets", "API_KEY", "--", f'"{python}"', "-c", f'"{PRINT}"'])
        done = subprocess.run(["sh", "-c", command + '; echo "shell=${API_KEY-unset}"'], capture_output=True,
                              text=True, env=self.env, stdin=subprocess.DEVNULL)
        self.assertEqual(done.returncode, 0, done.stderr)
        self.assertIn(f"child={VALUE}", done.stdout)
        self.assertIn("shell=unset", done.stdout)
        self.assertNotIn("API_KEY", os.environ)

    def test_a_shell_env_printenv_or_a_runner_as_the_child_is_refused(self):
        for child in (["sh", "-c", "echo $API_KEY"], ["bash"], ["/bin/sh"], ["zsh"], ["pwsh"], ["CMD.EXE", "/c", "set"],
                      ["powershell.exe"], ["env"], ["/usr/bin/env"], ["printenv", "API_KEY"], ["xargs", "echo"],
                      ["sudo", "sh"], ["nohup", "sh"]):
            with self.subTest(child=child):
                done = self.ws("API_KEY", "--", *child)
                self.assertEqual(done.returncode, 2, done.stdout)
                self.assertIn("refused", done.stderr)
                self.assertNotIn(VALUE, done.stdout + done.stderr)

    @unittest.skipIf(os.name == "nt" or not shutil.which("sh"), "needs a symbolic link to a POSIX shell")
    def test_a_link_to_a_shell_under_another_name_is_refused(self):
        link = pathlib.Path(self.tmp.name) / "tool"
        os.symlink(os.path.realpath(shutil.which("sh")), link)
        done = self.ws("API_KEY", "--", str(link), "-c", "echo $API_KEY")
        self.assertEqual(done.returncode, 2, done.stdout)
        self.assertIn("refused", done.stderr)
        self.assertNotIn(VALUE, done.stdout + done.stderr)

    def test_a_missing_name_file_or_separator_is_refused_without_a_value(self):
        for args, said in ((["NOPE", "--", sys.executable, "-c", "pass"], "NOPE"),
                           (["API_KEY", sys.executable, "-c", "pass"], "--"),
                           (["--", sys.executable, "-c", "pass"], "name at least one"),
                           (["API_KEY", "--"], "name the program"),
                           (["not-a-name", "--", sys.executable], "not a variable name")):
            with self.subTest(args=args):
                done = self.ws(*args)
                self.assertEqual(done.returncode, 2)
                self.assertIn(said, done.stderr)
                self.assertNotIn(VALUE, done.stdout + done.stderr)
        (self.repo / ".env").unlink()
        done = self.ws("API_KEY", "--", sys.executable, "-c", "pass")
        self.assertEqual(done.returncode, 2)
        self.assertIn("no secrets file", done.stderr)

    def test_the_child_exit_code_is_returned(self):
        done = self.ws("API_KEY", "--", sys.executable, "-c", "raise SystemExit(7)")
        self.assertEqual(done.returncode, 7, done.stderr)

    def test_a_linked_worktree_reads_the_main_copy_file(self):
        git(self.repo, "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-q", "--allow-empty", "-m", "start")
        tree = pathlib.Path(self.tmp.name) / "tree"
        git(self.repo, "worktree", "add", "-q", "-b", "side", str(tree))
        self.assertFalse((tree / ".env").exists())
        done = self.ws("API_KEY", "--", sys.executable, "-c", PRINT, root=tree)
        self.assertEqual(done.returncode, 0, done.stderr)
        self.assertIn(f"child={VALUE}", done.stdout)

    def test_the_file_is_the_one_the_manifest_names(self):
        self.assertEqual(secrets.file_of(self.repo, {"file": "keys/local.env"}).resolve(),
                         (self.repo / "keys/local.env").resolve())
        self.assertEqual(secrets.file_of(self.repo, {}).resolve(), (self.repo / ".env").resolve())

    def test_a_person_moves_the_file_with_ws_secrets_file(self):
        moved = pathlib.Path(self.tmp.name) / "outside" / "keys.env"
        moved.parent.mkdir()
        moved.write_text("API_KEY=from-the-moved-file\n", encoding="utf-8")
        self.env["WS_SECRETS_FILE"] = str(moved)
        done = self.ws("API_KEY", "--", sys.executable, "-c", PRINT)
        self.assertEqual(done.returncode, 0, done.stderr)
        self.assertIn("child=from-the-moved-file", done.stdout)

    @unittest.skipIf(os.name == "nt" or (hasattr(os, "geteuid") and os.geteuid() == 0), "needs file modes that bind")
    def test_a_file_the_process_may_not_read_names_the_codex_profile(self):
        (self.repo / ".env").chmod(0)
        try:
            done = self.ws("API_KEY", "--", sys.executable, "-c", "pass")
        finally:
            (self.repo / ".env").chmod(0o600)
        self.assertEqual(done.returncode, 2)
        self.assertIn("agent-ready profile", done.stderr)
        self.assertNotIn(VALUE, done.stdout + done.stderr)

    def test_a_batch_file_with_a_character_cmd_reads_is_refused(self):
        self.assertIsNone(secretrules.batch_refusal("C:/node/npm.cmd", ["publish", "--tag", "next"]))
        self.assertIsNone(secretrules.batch_refusal("C:/tools/tool.exe", ["a&set"]))
        for word in ("x&set", "a|b", "%API_KEY%", "!API_KEY!", "a^b", 'a"b', "a>b", "(a)"):
            with self.subTest(word=word):
                self.assertIsNotNone(secretrules.batch_refusal("C:/node/NPM.CMD", ["publish", word]))
                self.assertIsNotNone(secretrules.batch_refusal("C:/x/run.bat", [word]))

    def test_the_file_is_read_as_its_format_says(self):
        values = secrets.read('# c\nexport A=1\nB="x \\"q\\" y"\nC=\'lit $x\'\nD=plain # note\nE=\nnot a line\n')
        self.assertEqual(values, {"A": "1", "B": 'x "q" y', "C": "lit $x", "D": "plain", "E": ""})


class HookAndCommandAgreeTests(unittest.TestCase):
    def setUp(self):
        self.part = partlib.load(ROOT, entry("secrets_shell"))

    def test_the_hook_reads_the_secrets_files_the_tools_settings_deny(self):
        settings, hook = entry("agent_settings"), entry("secrets_shell")
        self.assertEqual(hook["secrets"], settings["secrets"])
        self.assertEqual(hook["home"], settings["home"])

    def test_the_hook_refuses_every_child_the_command_refuses(self):
        for name in sorted(secrets.REFUSED):
            with self.subTest(child=name):
                reason = self.part.decide({"command": f"python3 ws.py with-secrets API_KEY -- {name} x"})
                self.assertIsNotNone(reason)

    def test_the_hook_refuses_reading_the_file_with_secrets_reads(self):
        self.assertIsNotNone(self.part.decide({"command": f"cat {entry('secrets_shell')['file']}"}))

    def test_the_command_and_the_hook_share_one_list(self):
        self.assertIs(secrets.REFUSED, secretrules.REFUSED)
        self.assertIs(secrets.refusal, secretrules.refusal)


if __name__ == "__main__":
    unittest.main()
