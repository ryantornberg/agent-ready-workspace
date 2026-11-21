"""M3 slice C1: one launcher, wslib/launch.sh, starts every hook, git hook and CI step, with one Python start.

Criteria 26, 27 and 57 of docs/plans/m3-reading-layer-machinery-and-kit.md.

The tests that put a stand-in interpreter on the path are shell scripts named python3, so they run where a POSIX
shell runs them: Linux and macOS. On Windows the launcher still runs in CI, through Git's bash, for every step.

Run: python3 -m unittest discover -b tests
"""
import json
import os
import pathlib
import re
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parent.parent
LAUNCHER = ROOT / "wslib" / "launch.sh"
GUARD_EVENTS = ("before-shell", "before-edit", "before-handoff")   # every other wired event only reminds

# A word that starts Python by name: python, python3, python3.12, py, or any of them with .exe or a folder in front.
PYTHON = re.compile(r"(?:^|[\s;&|(`/\\\"'])(?:python(?:\d+(?:\.\d+)*)?|py)(?:\.exe)?(?=$|[\s;&|)`\"'])")


def starts_python(command):
    """True when a shell command starts Python itself rather than through the launcher."""
    return bool(PYTHON.search(command))


def comment_free(text):
    return "\n".join(line for line in text.splitlines() if not line.lstrip().startswith("#"))


def wiring():
    """[(tool, event, command)] for every hook wiring entry of both agent tools."""
    found = []
    for tool, path in (("claude-code", ".claude/settings.json"), ("codex", ".codex/hooks.json")):
        settings = json.loads((ROOT / path).read_text(encoding="utf-8"))
        for entries in settings["hooks"].values():
            for entry in entries:
                for hook in entry["hooks"]:
                    event = re.search(r"\bhook ([a-z-]+)\b", hook["command"]).group(1)
                    found.append((tool, event, hook["command"]))
    return found


def ci_steps(text):
    """The command of every run step in a workflow file, block scalars included."""
    steps, lines = [], text.splitlines()
    for number, line in enumerate(lines):
        match = re.match(r"^(\s*)(?:-\s+)?run:\s*(.*)$", line)
        if not match:
            continue
        value = match.group(2)
        if value.strip() in ("|", ">", "|-", ">-"):
            indent, body = len(match.group(1)), []
            for following in lines[number + 1:]:
                if following.strip() and len(following) - len(following.lstrip()) <= indent + 2:
                    break
                body.append(following.strip())
            value = "\n".join(body)
        steps.append(value)
    return steps


def shell():
    return shutil.which("sh")


# Git hooks written in plain sh that start no Python: post-checkout copies one file into a new worktree.
SHELL_ONLY_HOOKS = {"post-checkout"}


class LauncherWiringTests(unittest.TestCase):
    """Criterion 26: nothing wired starts Python except through the launcher."""

    def test_the_detector_finds_python_started_by_name(self):
        for command in ("python ws.py check", "python3 -m unittest", "exec python3.12 x.py", "py -3 ws.py",
                        "/usr/bin/python3 ws.py", "C:\\Python\\python.exe ws.py", "x && python ws.py", "\"python\" ws.py"):
            with self.subTest(command=command):
                self.assertTrue(starts_python(command))
        for command in ("bash wslib/launch.sh ws.py selftest", "sh wslib/launch.sh -m unittest discover -b tests",
                        "\"$CLAUDE_PROJECT_DIR/wslib/launch.sh\" hook before-shell --tool claude-code || exit 2",
                        "bash wslib/launch.sh evals/grade.py --recorded", "echo pythonic"):
            with self.subTest(command=command):
                self.assertFalse(starts_python(command))

    def test_every_wiring_entry_goes_through_the_launcher(self):
        entries = wiring()
        self.assertGreaterEqual(len(entries), 10)
        for tool, event, command in entries:
            with self.subTest(tool=tool, event=event):
                self.assertIn("wslib/launch.sh", command)
                self.assertFalse(starts_python(command), command)

    def test_every_git_hook_goes_through_the_launcher(self):
        hooks = sorted((ROOT / ".githooks").iterdir())
        self.assertGreaterEqual(len(hooks), 4)
        for hook in hooks:
            with self.subTest(hook=hook.name):
                body = comment_free(hook.read_text(encoding="utf-8"))
                self.assertFalse(starts_python(body), body)
                if hook.name in SHELL_ONLY_HOOKS:   # starts no Python at all, so it needs no launcher
                    self.assertNotIn("ws.py", body)
                    continue
                self.assertIn("wslib/launch.sh", body)

    def test_every_ci_step_goes_through_the_launcher_and_windows_runs_it_in_bash(self):
        for workflow in sorted((ROOT / ".github/workflows").glob("*.yml")):
            text = workflow.read_text(encoding="utf-8")
            steps = ci_steps(text)
            for step in steps:
                with self.subTest(workflow=workflow.name, step=step):
                    self.assertFalse(starts_python(step), step)
            if steps:
                # GitHub's own "bash" on Windows is Git's bash; a bare "bash" from PowerShell can be WSL's.
                self.assertRegex(text, r"(?m)^    defaults:\n      run:\n        shell: bash$", workflow.name)
        ci = ci_steps((ROOT / ".github/workflows/ci.yml").read_text(encoding="utf-8"))
        self.assertTrue(any("wslib/launch.sh -m unittest" in step for step in ci))
        self.assertTrue(any("wslib/launch.sh evals/grade.py --recorded" in step for step in ci))

    @unittest.skipUnless(os.environ.get("WS_EXPECT_PYTHON"), "set in CI to the Python its matrix row set up")
    def test_ci_runs_the_python_its_matrix_row_set_up(self):
        want = os.environ["WS_EXPECT_PYTHON"]
        self.assertEqual("%d.%d" % sys.version_info[:2], want, f"the launcher picked {sys.executable}")


@unittest.skipIf(os.name == "nt", "the stand-in interpreters are shell scripts; see the module's docstring")
class LauncherStartTests(unittest.TestCase):
    """Criteria 27 and 57: one start per call, and the right answer when Python is missing, too old or crashes."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.tmp = pathlib.Path(self._tmp.name).resolve()
        self.addCleanup(self._tmp.cleanup)
        self.log = self.tmp / "starts.log"

    def folder(self, name, **scripts):
        """A folder of stand-in programs, each a shell script, plus git and sh, which the wiring and the git hooks call."""
        folder = self.tmp / name
        folder.mkdir(parents=True)
        for program, body in scripts.items():
            path = folder / program
            path.write_text("#!/bin/sh\n" + body + "\n", encoding="utf-8")
            path.chmod(0o755)
        for program in ("git", "sh"):            # neither starts Python
            found = shutil.which(program)
            if found and not (folder / program).exists():
                (folder / program).symlink_to(found)
        return folder

    def counted(self):
        """A python3 that records each start and then runs the real interpreter."""
        return f'echo start >> "{self.log}"\nexec "{sys.executable}" "$@"'

    def old(self):
        """A python3 that runs the real interpreter while reporting itself as 3.8."""
        code = ("import runpy, sys; sys.version_info = (3, 8, 18, 'final', 0); sys.argv = sys.argv[1:]; "
                "runpy.run_path(sys.argv[0], run_name='__main__')")
        return f'echo start >> "{self.log}"\nexec "{sys.executable}" -c "{code}" "$@"'

    def run_command(self, command, path, payload="", cwd=ROOT):
        environment = {key: value for key, value in os.environ.items() if not key.startswith("PYTHON")}
        environment.update(PATH=str(path), CLAUDE_PROJECT_DIR=ROOT.as_posix())
        return subprocess.run([shell(), "-c", command], input=payload.encode("utf-8"), capture_output=True,
                              env=environment, cwd=str(cwd))

    def starts(self):
        return len(self.log.read_text(encoding="utf-8").splitlines()) if self.log.exists() else 0

    # Criterion 27
    def test_a_hook_call_starts_exactly_one_python(self):
        bin_ = self.folder("bin", python3=self.counted())
        payloads = {"before-shell": {"tool_name": "Bash", "tool_input": {"command": "ls"}},
                    "before-handoff": {"tool_name": "Agent", "tool_input": {"prompt": "Tier: mechanical\nList.",
                                                                            "model": "haiku", "effort": "low"}}}
        for tool, event, command in wiring():
            if tool != "claude-code" or event not in payloads:
                continue
            with self.subTest(event=event):
                self.log.unlink() if self.log.exists() else None
                payload = dict(payloads[event], session_id="s", hook_event_name="PreToolUse", cwd=str(self.tmp))
                ran = self.run_command(command, bin_, json.dumps(payload))
                self.assertEqual(ran.returncode, 0, ran.stderr)
                self.assertEqual(self.starts(), 1)

    def test_the_launcher_runs_python_in_utf8_mode_and_runs_scripts_and_modules(self):
        bin_ = self.folder("bin", python3=self.counted())
        script = self.tmp / "probe.py"
        script.write_text("import sys\nprint(sys.flags.utf8_mode, sys.argv[1:], sys.path[0] == %r)\n" % str(self.tmp),
                          encoding="utf-8")
        ran = self.run_command(f'"{LAUNCHER}" "{script}" a b', bin_)
        self.assertEqual(ran.returncode, 0, ran.stderr)
        self.assertEqual(ran.stdout.decode().strip(), "1 ['a', 'b'] True")
        ran = self.run_command(f'"{LAUNCHER}" -m json.tool', bin_, '{"a": 1}')
        self.assertEqual(ran.returncode, 0, ran.stderr)
        self.assertIn('"a": 1', ran.stdout.decode())
        ran = self.run_command(f'"{LAUNCHER}" ws.py --version', bin_, cwd=self.tmp)   # relative to the workspace
        self.assertEqual(ran.returncode, 0, ran.stderr)
        ran = self.run_command(f'"{LAUNCHER}" --version', bin_, cwd=self.tmp)         # older wiring: ws.py's arguments
        self.assertEqual(ran.returncode, 0, ran.stderr)
        self.assertNotEqual(self.run_command(f'"{LAUNCHER}" -m no_such_module_here', bin_).returncode, 0)
        self.assertEqual(self.run_command(f'"{LAUNCHER}" "{self.exits(3)}"', bin_).returncode, 3)

    def exits(self, code):
        script = self.tmp / f"exit{code}.py"
        script.write_text(f"import sys\nsys.exit({code})\n", encoding="utf-8")
        return script

    def test_the_windows_store_stub_is_tried_last(self):
        stub = self.folder("WindowsApps", python3=f'echo stub >> "{self.log}"\nexit 49')
        real = self.folder("real", python=self.counted())
        ran = self.run_command(f'"{LAUNCHER}" --version', f"{stub}{os.pathsep}{real}")
        self.assertEqual(ran.returncode, 0, ran.stderr)
        self.assertEqual(self.log.read_text(encoding="utf-8").split(), ["start"])

    def test_a_python_too_old_is_passed_over_for_the_next(self):
        bin_ = self.folder("bin", python3=self.old(), python=self.counted())
        ran = self.run_command(f'"{LAUNCHER}" --version', bin_)
        self.assertEqual(ran.returncode, 0, ran.stderr)
        self.assertIn(b"older than 3.9", ran.stderr)

    # Criterion 57
    def failures(self):
        return {
            "no Python": self.folder("none"),
            "a version below the minimum": self.folder("old", python3=self.old()),
            "a crash": self.folder("crash", python3='kill -SEGV $$'),
            "a failure to start": self.folder("broken", python3='echo "Fatal Python error: init_fs_encoding" >&2\nexit 1'),
        }

    def test_a_guard_refuses_and_a_reminder_passes_when_the_launcher_fails(self):
        payload = json.dumps({"session_id": "s", "hook_event_name": "PreToolUse", "tool_name": "Bash",
                              "tool_input": {"command": "ls"}, "cwd": str(self.tmp)})
        entries = wiring()
        self.assertTrue({event for _, event, _ in entries} - set(GUARD_EVENTS), "no reminder is wired")
        for failure, path in self.failures().items():
            for tool, event, command in entries:
                with self.subTest(failure=failure, tool=tool, event=event):
                    ran = self.run_command(command, path, payload)
                    want = 2 if event in GUARD_EVENTS else 0
                    self.assertEqual(ran.returncode, want, ran.stderr)

    def test_the_launcher_gives_install_advice_when_no_python_will_do(self):
        for name, scripts in (("none", {}), ("old", {"python3": self.old()})):
            with self.subTest(name):
                ran = self.run_command(f'"{LAUNCHER}" --version', self.folder(name, **scripts))
                self.assertEqual(ran.returncode, 2)
                self.assertIn(b"Install Python 3.9 or later", ran.stderr)

    def test_a_git_hook_refuses_when_the_launcher_fails(self):
        none = self.folder("none")
        for hook in ("pre-commit", "commit-msg", "pre-push"):
            with self.subTest(hook=hook):
                ran = self.run_command(f'sh "{ROOT / ".githooks" / hook}" origin', none)
                self.assertNotEqual(ran.returncode, 0, ran.stderr)
        ran = self.run_command(f'sh "{ROOT / ".githooks" / "post-commit"}"', none)
        self.assertEqual(ran.returncode, 0, ran.stderr)


class StartTests(unittest.TestCase):
    """wslib/start.py, the one start: it can be read by an old Python, and it says so instead of running."""

    def test_an_old_python_is_told_and_exits_97(self):
        start = str(ROOT / "wslib" / "start.py")
        code = ("import runpy, sys; sys.version_info = (3, 8, 18, 'final', 0); "
                "sys.argv = [%r, %r, '--version']; runpy.run_path(%r, run_name='__main__')" % (start, str(ROOT), start))
        ran = subprocess.run([sys.executable, "-c", code], capture_output=True)
        self.assertEqual(ran.returncode, 97, ran.stderr)
        self.assertIn(b"older than 3.9", ran.stderr)

    def test_it_uses_no_syntax_newer_than_python_2(self):
        text = (ROOT / "wslib" / "start.py").read_text(encoding="utf-8")
        self.assertNotRegex(text, r"\bf\"|\bf'|:=|\bnonlocal\b|\basync\b|print\(.*\bend=")
        self.assertNotIn("from .", text)


if __name__ == "__main__":
    unittest.main()
