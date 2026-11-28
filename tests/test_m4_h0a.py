"""M4 slice H0a: the grader stamp.

Each test names the criterion of docs/plans/m4-fail-closed-guards-review-loop-and-evals.md it checks. The
eval_record part's own cases (parts/eval_record.cases.json) carry the check's rules; these tests hold what the
cases cannot: the migration against the real history, and the stamp run end to end in a copy of this repository.

Run: python3 -m unittest discover -b tests
"""
import json
import os
import pathlib
import shutil
import subprocess
import sys
import tempfile
import types
import unittest

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "evals"))

import run as harness  # noqa: E402
from parts import eval_record  # noqa: E402
from wslib import snapshot as snapshots  # noqa: E402

# The records current under the old hash at H0a's base: R2's three, and the twelve one-time records that carry
# their cases' hash. The other five were stale there already.
MIGRATED = sorted(
    [f"evals/runs/{case}/record.json" for case in ("big-report", "fix-a-bug", "nightly-job")]
    + [f"evals/runs/{case}/one-time/{arm}/record.json" for case in ("big-report", "fix-a-bug", "nightly-job")
       for arm in ("routed", "routed-after-fix", "routed-first", "routed-no-plugin")])
STALE = sorted(["evals/runs/debug-leak-check/record.json", "evals/runs/debug-leak-check/baseline/record.json",
                "evals/runs/debug-staging-reminder/record.json",
                "evals/runs/debug-staging-reminder/baseline/record.json",
                "evals/runs/red-team-fail-closed/baseline/record.json"])
GRADER_KEYS = ("grader_covers", "grader_sha256")
STAMP = ("evals/grade.py", "--recorded", "--stamp", "--base", "HEAD")    # the copy has no origin/main


def git(*args, root=ROOT):
    done = subprocess.run(["git", "-C", str(root), *args], capture_output=True)
    if done.returncode != 0:
        raise AssertionError(f"git {' '.join(args)}: {done.stderr.decode('utf-8', 'replace').strip()}")
    return done.stdout


class Tree:
    """One tree's files, at a commit or, with none, as the working copy holds them."""

    def __init__(self, commit=None):
        self.commit = commit
        if commit:
            self.paths = [p for p in git("ls-tree", "-r", "-z", "--name-only", commit).decode("utf-8").split("\0") if p]
        else:
            self.paths = harness.workspace_files(ROOT)
        self.known = set(self.paths)
        self._texts = {}

    def read(self, path):
        if path not in self.known:
            return None
        if path not in self._texts:
            data = git("show", f"{self.commit}:{path}") if self.commit else (ROOT / path).read_bytes()
            self._texts[path] = data.decode("utf-8-sig").replace("\r\n", "\n")
        return self._texts[path]

    def module(self, path, name):
        """A Python file of this tree, loaded as a module. A check part imports the engine from this checkout."""
        module = types.ModuleType(name)
        exec(compile(self.read(path), f"{self.commit or 'working copy'}:{path}", "exec"), module.__dict__)
        return module

    def hashes(self, checks, case_name, with_grader=False):
        """(covered files, hash) of a case under the eval_record module given, and with_grader the grading pair."""
        case_path = f"evals/cases/{case_name}.json"
        case = json.loads(self.read(case_path))
        arms = None if "arms" in case else json.loads(self.read("evals/arms.json"))
        keys = checks.load_proof_keys(self.read("evals/proofkeys.py"), "evals/proofkeys.py")
        files = checks.covered_files(case_path, case, self.paths, arms, "evals")
        found = (files, checks.guidance_hash({f: self.read(f) for f in files}, keys.strip))
        if with_grader:
            grading = checks.grading_files(case, self.paths, self.read, "evals")
            found += (grading, checks.grader_hash({f: self.read(f) for f in grading}))
        return found


def migration_commit():
    """The commit that first wrote a grader hash into the fix-a-bug record, H0a's, or None before it is made."""
    found = git("log", "--format=%H", "--reverse", "-S", '"grader_sha256"', "--",
                "evals/runs/fix-a-bug/record.json").decode("ascii").split()
    return found[0] if found else None


class MigrationTests(unittest.TestCase):
    """Criterion 61: H0a's commit holds no new run, migrates only the records current under the old hash at its
    base, leaves a stale record stale, and changes no file an agent is given. Read from the real history: the
    migration commit against its parent, or, before the commit is made, the working copy against HEAD."""

    @classmethod
    def setUpClass(cls):
        commit = migration_commit()
        cls.base = Tree(f"{commit}^1" if commit else "HEAD")
        cls.after = Tree(commit)
        cls.old = cls.base.module("parts/eval_record.py", "eval_record_at_base")
        cls.new = cls.after.module("parts/eval_record.py", "eval_record_at_migration")
        if commit:
            changed = git("diff", "--name-status", "--no-renames", "-z", f"{commit}^1", commit).decode("utf-8")
        else:
            changed = git("diff", "--name-status", "--no-renames", "-z", "HEAD").decode("utf-8")
            changed += "".join(f"A\0{p}\0" for p in git("ls-files", "-z", "-o", "--exclude-standard")
                               .decode("utf-8").split("\0") if p)
        words = [w for w in changed.split("\0") if w]
        cls.changed = dict(zip(words[1::2], words[0::2]))
        cls.records = sorted(p for p in cls.base.paths if p.startswith("evals/runs/") and p.endswith("/record.json"))

    def test_the_records_current_at_the_base_are_the_ones_migrated(self):
        current = []
        for path in self.records:
            record = json.loads(self.base.read(path))
            if record["guidance_sha256"] == self.base.hashes(self.old, record["case"])[1]:
                current.append(path)
        self.assertEqual(current, MIGRATED)
        self.assertEqual(sorted(set(self.records) - set(current)), STALE)

    def test_the_commit_holds_no_new_run(self):
        under_runs = {p: how for p, how in self.changed.items() if p.startswith("evals/runs/")}
        self.assertEqual(under_runs, {p: "M" for p in MIGRATED}, "only the migrated records change under evals/runs")
        self.assertEqual(sorted(p for p in self.after.paths if p.startswith("evals/runs/")),
                         sorted(p for p in self.base.paths if p.startswith("evals/runs/")))

    def test_no_file_an_agent_is_given_changed(self):
        cases = sorted({json.loads(self.base.read(p))["case"] for p in self.records})
        for name in cases:
            with self.subTest(name):
                files, digest = self.after.hashes(self.new, name)
                self.assertEqual([f for f in files if f in self.changed], [])
                self.assertEqual(self.base.hashes(self.new, name), (files, digest), "the same files, read at the base")
                old_files = self.base.hashes(self.old, name)[0]
                grading = self.after.hashes(self.new, name, with_grader=True)[2]
                self.assertEqual(sorted(set(old_files) - set(files)), sorted(set(old_files) & set(grading)),
                                 "only grading files left the hash")
                self.assertEqual(sorted(set(files) - set(old_files)), [])

    def test_a_migrated_record_differs_only_in_its_hashes(self):
        for path in MIGRATED:
            with self.subTest(path):
                before, after = json.loads(self.base.read(path)), json.loads(self.after.read(path))
                files, digest, grading, grader = self.after.hashes(self.new, before["case"], with_grader=True)
                expected = dict(before, covers=files, guidance_sha256=digest, grader_covers=grading,
                                grader_sha256=grader)
                self.assertEqual(after, expected)
                self.assertEqual(list(after)[list(after).index("guidance_sha256") + 1:][:2], list(GRADER_KEYS))

    def test_a_record_stale_at_the_base_stays_stale(self):
        for path in STALE:
            with self.subTest(path):
                self.assertNotIn(path, self.changed)
                record = json.loads(self.after.read(path))
                self.assertNotEqual(record["guidance_sha256"], self.after.hashes(self.new, record["case"])[1])
                self.assertFalse(set(GRADER_KEYS) & set(record))

    def test_run_py_and_proofkeys_py_did_not_change(self):
        self.assertNotIn("evals/run.py", self.changed)
        self.assertNotIn("evals/proofkeys.py", self.changed)


class StampTests(unittest.TestCase):
    """Criteria 13 and 61: a change to grading files alone passes eval_record once the stamp finds no difference;
    a grade that differs keeps it failing; and the base commit's grade.py judges, so grade.py cannot certify
    itself. Run end to end, in a copy of this repository committed as its own base."""

    @classmethod
    def setUpClass(cls):
        cls._tmp = tempfile.TemporaryDirectory()
        cls.root = pathlib.Path(cls._tmp.name).resolve() / "copy"
        for name in git("ls-files", "-z").decode("utf-8").split("\0"):
            if name and (ROOT / name).is_file() and not name.startswith("src/"):
                (cls.root / name).parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(ROOT / name, cls.root / name)
        cls.git("init", "-q")
        cls.git("add", "-A")
        cls.git("commit", "-q", "--no-verify", "-m", "base")

    @classmethod
    def tearDownClass(cls):
        cls._tmp.cleanup()

    @classmethod
    def git(cls, *args):
        return subprocess.run(["git", "-C", str(cls.root), "-c", "user.name=t", "-c", "user.email=t@example.invalid",
                               "-c", "commit.gpgsign=false", *args], check=True, capture_output=True, text=True)

    def setUp(self):
        self.addCleanup(self.git, "checkout", "-q", "--", ".")

    def python(self, *args, env=None):
        environment = {k: v for k, v in os.environ.items() if not k.startswith("GITHUB_")}
        environment.update(env or {})
        done = subprocess.run([sys.executable, *args], cwd=self.root, capture_output=True, text=True,
                              env=environment)
        return done.returncode, done.stdout + done.stderr

    def edit(self, path, old, new):
        target = self.root / path
        text = target.read_text(encoding="utf-8")
        self.assertIn(old, text)
        target.write_text(text.replace(old, new, 1), encoding="utf-8")

    def findings(self, base=None):
        found = eval_record.run(snapshots.Tree(self.root, base=base), {"playbooks": "docs/playbooks"})
        # The copy holds one commit, so the anchors proven-by names cannot be read in it; that finding is not ours.
        return [f["message"] for f in found
                if f["level"] == "error" and "its proven-by names cannot be read" not in f["message"]]

    def record_again(self, case_name, graded, gated_only=False):
        """Record a case again as run.py would: new transcripts, graded by the grade.py given, and no grader hash.
        gated_only: the case's gated record alone, not its one-time arms'."""
        case = json.loads((self.root / f"evals/cases/{case_name}.json").read_text(encoding="utf-8"))
        folder = self.root / f"evals/runs/{case_name}"
        for path in [folder / "record.json"] if gated_only else sorted(folder.rglob("record.json")):
            record = json.loads(path.read_text(encoding="utf-8"))
            for key in GRADER_KEYS:
                record.pop(key, None)
            for given in record["arms"].values():
                for run in given["runs"]:
                    transcript = path.parent / run["transcript"]
                    actions = json.loads(transcript.read_text(encoding="utf-8"))
                    actions.append({"kind": "read", "target": "README.md", "ok": True})     # another run's content
                    transcript.write_text(json.dumps(actions, indent=2) + "\n", encoding="utf-8")
                    run["graders"] = dict(graded.grade(case, actions, self.root))
                    run["passed"] = all(run["graders"].values())
                given["runs_passing_each_grader"] = {g: sum(r["graders"][g] for r in given["runs"])
                                                     for g in given["runs_passing_each_grader"]}
                given["runs_passing_every_grader"] = sum(r["passed"] for r in given["runs"])
            path.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")

    def grade_module(self):
        """The copy's grade.py, loaded as run.py would load it."""
        graded = types.ModuleType("graded_by_the_change")
        graded.__file__ = str(self.root / "evals/grade.py")
        exec(compile((self.root / "evals/grade.py").read_text(encoding="utf-8"), "grade.py", "exec"), graded.__dict__)
        return graded

    def base_with_grade_py(self, text):
        """Commit, on top of the copy's base, a grade.py of the given text (None: no grade.py), then the copy's own
        again, and return the middle commit's sha. The copy is put back as it was by the cleanup."""
        start = self.git("rev-parse", "HEAD").stdout.strip()
        self.addCleanup(self.git, "reset", "-q", "--hard", start)
        own = (self.root / "evals/grade.py").read_text(encoding="utf-8")
        if text is None:
            self.git("rm", "-q", "evals/grade.py")
        else:
            (self.root / "evals/grade.py").write_text(text, encoding="utf-8")
            self.git("add", "evals/grade.py")
        self.git("commit", "-q", "--no-verify", "-m", "another base")
        middle = self.git("rev-parse", "HEAD").stdout.strip()
        (self.root / "evals/grade.py").write_text(own, encoding="utf-8")
        self.git("add", "evals/grade.py")
        self.git("commit", "-q", "--no-verify", "-m", "the copy's own grade.py")
        return middle

    def records(self):
        return {p: (self.root / p).read_bytes() for p in MIGRATED + STALE}

    def test_a_grading_change_that_changes_no_grade_passes_after_the_stamp(self):
        self.assertEqual(self.findings(), [])
        hashes = {name: harness.covered(name, self.root)[1] for name in ("big-report", "fix-a-bug", "nightly-job")}
        with (self.root / "wslib/shell.py").open("a", encoding="utf-8") as handle:
            handle.write("\n# a grading change that changes no grade\n")
        found = self.findings()
        self.assertEqual(len(found), 3, found)
        self.assertTrue(all("python3 evals/grade.py --recorded --stamp" in f for f in found), found)
        self.assertEqual({name: harness.covered(name, self.root)[1] for name in hashes}, hashes,
                         "the hash over what an agent is given did not move")
        before = self.records()
        code, output = self.python(*STAMP)
        self.assertEqual(code, 0, output)
        self.assertIn("no difference(s); this grade.py judged; the base commit", output)
        self.assertIn("stamped the grader hash into 15 record(s)", output)
        self.assertEqual(self.findings(), [])
        after = self.records()
        self.assertEqual([p for p in STALE if after[p] != before[p]], [], "a stale record is left as it is")
        code, output = self.python(*STAMP)
        self.assertIn("stamped the grader hash into 0 record(s)", output)

    def test_a_grade_that_differs_stamps_nothing_and_the_record_keeps_failing(self):
        self.edit("parts/no_stage_all.py", "def decide(event, config):\n",
                  "def decide(event, config):\n    return 'every command now reminds'\n\n\ndef old_decide(event, config):\n")
        before = self.records()
        code, output = self.python(*STAMP)
        self.assertEqual(code, 1, output)
        self.assertIn("stages-by-name is recorded as True and grades as False", output)
        self.assertIn("nothing stamped", output)
        self.assertEqual(self.records(), before)
        found = self.findings()
        self.assertEqual(len(found), 3, found)
        self.assertTrue(all("changed since its stored runs were last re-graded" in f for f in found), found)

    def test_the_base_commits_grade_py_judges_so_a_grade_py_cannot_certify_itself(self):
        self.edit("evals/grade.py", '    differences = []\n    runs = root / "evals" / "runs"\n',
                  '    return []\n')
        self.edit("parts/no_stage_all.py", "def decide(event, config):\n",
                  "def decide(event, config):\n    return 'every command now reminds'\n\n\ndef old_decide(event, config):\n")
        before = self.records()
        code, output = self.python(*STAMP)
        self.assertEqual(code, 1, output)
        self.assertIn("by the base commit's grade.py", output)
        self.assertIn("stages-by-name is recorded as True and grades as False", output)
        self.assertEqual(self.records(), before)
        base = self.git("rev-parse", "HEAD").stdout.strip()
        for event in ({"pull_request": {"base": {"sha": base}}}, {"before": base}):
            with self.subTest("CI's re-grade reads the base from the GitHub event", event=list(event)):
                path = self.root.parent / "event.json"
                path.write_text(json.dumps(event), encoding="utf-8")
                code, output = self.python("evals/grade.py", "--recorded", env={"GITHUB_EVENT_PATH": str(path)})
                self.assertEqual(code, 1, output)
                self.assertIn(f"by the base commit's grade.py ({base[:12]})", output)

    def test_the_stamp_needs_a_base_and_names_a_bad_one(self):
        code, output = self.python("evals/grade.py", "--recorded", "--stamp", "--base", "no-such-ref")
        self.assertEqual(code, 2, output)
        self.assertIn("--base no-such-ref names no commit", output)
        with self.subTest("no event, no origin/main: it refuses, and does not judge HEAD by itself"):
            code, output = self.python("evals/grade.py", "--recorded", "--stamp")
            self.assertEqual(code, 2, output)
            self.assertIn("nothing is stamped; pass --base REF", output)
            code, output = self.python("evals/grade.py", "--recorded")
            self.assertEqual(code, 0, output)
            self.assertIn("no base commit was found, so this grade.py alone judged", output)

    def test_a_grade_py_change_that_alters_a_stored_grade_fails_and_passes_once_the_cases_are_recorded_again(self):
        """The base's copy judges every run the base holds; a run recorded since then is left to this copy. A change
        to grade.py itself is never stamped onto a run graded before it: every case is recorded again first."""
        self.edit("evals/grade.py", '    return [(g["id"], grade_one(g, actions, root)) for g in case["graders"]]\n',
                  '    found = [(g["id"], grade_one(g, actions, root)) for g in case["graders"]]\n'
                  '    if case.get("name") == "nightly-job":    # a new rule: every nightly-job report counts as marked\n'
                  '        found = [(i, True if i == "report-marks-a-claim-verified" else ok) for i, ok in found]\n'
                  '    return found\n')
        before = self.records()
        code, output = self.python(*STAMP)
        self.assertEqual(code, 1, output)
        self.assertIn("report-marks-a-claim-verified is recorded as False and grades as True", output)
        self.assertEqual(self.records(), before, "a stored grade the change alters stamps nothing")
        graded = self.grade_module()
        self.record_again("nightly-job", graded)
        found = [f for f in self.findings() if "nightly-job" in f]
        self.assertEqual(len(found), 1, found)
        self.assertIn("holds no grader hash; run python3 evals/grade.py --recorded --stamp", found[0])
        with self.subTest("the cases whose runs were graded before the change are not stamped"):
            code, output = self.python(*STAMP)
            self.assertEqual(code, 1, output)
            self.assertIn("were left to this grade.py, which the base's copy never graded", output)
            self.assertIn("evals/runs/fix-a-bug/record.json: not stamped: evals/grade.py differs from the base", output)
            self.assertIn("stamped the grader hash into 5 record(s)", output)
            found = self.findings(base="HEAD")
            self.assertEqual(len(found), 2, found)
            self.assertTrue(all("A change to grade.py itself is not stamped" in f for f in found), found)
        for name in ("big-report", "fix-a-bug"):
            self.record_again(name, graded)
        code, output = self.python(*STAMP)
        self.assertEqual(code, 0, output)
        self.assertIn("stamped the grader hash into 10 record(s)", output)
        self.assertFalse([f for f in self.findings(base="HEAD") if "grader hash" in f or "grade.py" in f])
        code, output = self.python(*STAMP[:2], "--base", "HEAD")
        self.assertEqual(code, 0, output)

    def test_a_grade_py_change_stamped_without_a_new_recording_fails_eval_record(self):
        """What CI holds when the head's grade.py would skip the base's copy: eval_record refuses the stamp."""
        with (self.root / "evals/grade.py").open("a", encoding="utf-8") as handle:
            handle.write("\n# a change to grade.py itself\n")
        code, output = self.python(*STAMP)
        self.assertEqual(code, 1, output)
        self.assertIn("stamped the grader hash into 0 record(s)", output)
        # Stamped by hand, as a grade.py that skipped the rule would: eval_record still refuses, given the base.
        for path in MIGRATED:
            record = json.loads((self.root / path).read_text(encoding="utf-8"))
            case = harness.load_case(record["case"], self.root)
            files = eval_record.grading_files(case, harness.workspace_files(self.root),
                                              lambda f: harness.read_text(self.root, f))
            record["grader_sha256"] = eval_record.grader_hash({f: harness.read_text(self.root, f) for f in files})
            (self.root / path).write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
        self.assertEqual(self.findings(), [], "with no base, the check cannot tell")
        found = self.findings(base="HEAD")
        self.assertEqual(len(found), 3, found)
        self.assertTrue(all("A change to grade.py itself is not stamped" in f for f in found), found)

    def test_after_a_grade_py_change_the_stamp_exits_0_once_the_three_gated_cases_are_recorded_again(self):
        """The one-time records, which the gate never reads, are left and named, and do not fail the stamp."""
        with (self.root / "evals/grade.py").open("a", encoding="utf-8") as handle:
            handle.write("\n# a change to grade.py itself that changes no grade\n")
        graded = self.grade_module()
        for name in ("big-report", "fix-a-bug", "nightly-job"):
            self.record_again(name, graded, gated_only=True)
        code, output = self.python(*STAMP)
        self.assertEqual(code, 0, output)
        self.assertIn("stamped the grader hash into 3 record(s)", output)
        self.assertEqual(output.count("left as it is: evals/grade.py differs from the base commit's"), 12, output)
        self.assertIn("the gate does not read a one-time or baseline record, so this does not fail the stamp", output)
        self.assertNotIn("not stamped", output)
        self.assertFalse([f for f in self.findings(base="HEAD") if "grader hash" in f or "grade.py" in f])

    def test_a_hook_change_keeps_the_stamp_path(self):
        with (self.root / "parts/no_stage_all.py").open("a", encoding="utf-8") as handle:
            handle.write("\n# a hook change that changes no grade\n")
        code, output = self.python(*STAMP)
        self.assertEqual(code, 0, output)
        self.assertIn("stamped the grader hash into 15 record(s)", output)
        self.assertEqual(self.findings(base="HEAD"), [])

    def test_a_base_whose_grade_py_cannot_be_read_or_cannot_re_grade_fails_closed(self):
        broken = (self.root / "evals/grade.py").read_text(encoding="utf-8").replace(
            "def regrade_records(root=ROOT):\n", "def regrade_records(root=ROOT):\n    raise ValueError('broken')\n", 1)
        for text, expected in ((broken, "it cannot re-grade: ValueError: broken"),
                               (None, "git cannot read evals/grade.py at the base commit")):
            with self.subTest(expected):
                base = self.base_with_grade_py(text)
                code, output = self.python("evals/grade.py", "--recorded", "--base", base)
                self.assertEqual(code, 1, output)
                self.assertIn(expected, output)
                code, output = self.python("evals/grade.py", "--recorded", "--stamp", "--base", base)
                self.assertEqual(code, 1, output)
                self.assertIn("nothing stamped", output)
                self.git("reset", "-q", "--hard", f"{base}~1")

    def test_a_run_is_new_only_when_its_content_differs_and_an_untracked_one_counts(self):
        sys.path.insert(0, str(ROOT / "evals"))
        import grade
        folder = self.root / "evals/runs/nightly-job"
        layout = folder / "bare-1.json"
        layout.write_text(json.dumps(json.loads(layout.read_text(encoding="utf-8")), indent=1) + "\n", encoding="utf-8")
        content = folder / "bare-2.json"
        actions = json.loads(content.read_text(encoding="utf-8")) + [{"kind": "read", "target": "x", "ok": True}]
        content.write_text(json.dumps(actions, indent=2) + "\n", encoding="utf-8")
        untracked = folder / "bare-16.json"
        untracked.write_text("[]\n", encoding="utf-8")
        self.addCleanup(untracked.unlink)
        new = grade.new_since(self.root, "HEAD")
        self.assertEqual(new, {"evals/runs/nightly-job/bare-2.json", "evals/runs/nightly-job/bare-16.json"})

    def test_a_run_the_base_holds_stays_judged_by_the_base_beside_a_new_run_in_its_arm(self):
        sys.path.insert(0, str(ROOT / "evals"))
        import grade
        new = {"evals/runs/x/guided-16.json"}
        arms = {("evals/runs/x/record.json", "guided")}
        old_run = "evals/runs/x/record.json: guided guided-1.json: g is recorded as True and grades as False"
        new_run = "evals/runs/x/record.json: guided guided-16.json: g is recorded as True and grades as False"
        counts = "evals/runs/x/record.json: guided: the counts per grader differ from the runs"
        other = "evals/runs/x/record.json: bare: the counts per grader differ from the runs"
        listing = "evals/runs/x/record.json: the transcripts on disk are not the ones the record lists"
        self.assertTrue(grade.judged_by_base(old_run, new, arms))
        self.assertFalse(grade.judged_by_base(new_run, new, arms))
        self.assertFalse(grade.judged_by_base(counts, new, arms))
        self.assertTrue(grade.judged_by_base(other, new, arms))
        self.assertTrue(grade.judged_by_base(listing, new, arms))
        self.assertTrue(grade.judged_by_base("a line in a form nobody reads", new, arms))

    def test_ci_recomputes_the_grader_hash_and_fails_a_record_whose_stored_one_differs(self):
        path = self.root / "evals/runs/nightly-job/record.json"
        record = json.loads(path.read_text(encoding="utf-8"))
        record["grader_sha256"] = "0" * 64
        path.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
        found = self.findings()
        self.assertEqual(len(found), 1, found)
        self.assertIn("a grading file of case nightly-job changed since its stored runs were last re-graded", found[0])


class ImportScanTests(unittest.TestCase):
    """The grader hash follows each import a graded hook makes, in the forms Python allows, and fails closed."""

    PATHS = ["wslib/__init__.py", "wslib/shell.py", "wslib/gitrules.py", "lib/__init__.py", "lib/words.py"]

    def test_each_form_of_import_is_read(self):
        for text in ("from wslib import shell\n", "import re; from wslib import shell\n",
                     "from wslib import \\\n    shell\n", "from wslib import (  # the parser\n    shell,\n)\n",
                     "import wslib.shell as parser\n", "if True:\n    from wslib import shell\n"):
            with self.subTest(text):
                self.assertEqual(eval_record.imported_files("parts/h.py", text, self.PATHS),
                                 ["wslib/__init__.py", "wslib/shell.py"])

    def test_a_relative_import_is_read_from_the_module_s_package(self):
        self.assertEqual(eval_record.imported_files("lib/rules.py", "from .words import WORDS\n", self.PATHS),
                         ["lib/__init__.py", "lib/words.py"])

    def test_an_import_it_cannot_resolve_that_names_a_package_takes_the_whole_package(self):
        found = eval_record.imported_files("parts/h.py", 'parser = importlib.import_module("wslib." + name)\n',
                                           self.PATHS)
        self.assertEqual(found, ["wslib/__init__.py", "wslib/gitrules.py", "wslib/shell.py"])

    def test_a_mention_that_is_not_an_import_adds_nothing(self):
        self.assertEqual(eval_record.imported_files("parts/h.py", '"""Reads the wslib parser."""\n', self.PATHS), [])


if __name__ == "__main__":
    unittest.main()
