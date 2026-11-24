"""M3 sub-batch A: the eval harness generalized, the page structure, the rules register and the proof marks.

Each test names the criterion of docs/plans/m3-reading-layer-machinery-and-kit.md it checks. The parts' own
cases (parts/*.cases.json) carry most of the rules; these tests hold what the cases cannot: the harness, the
real repository's files, and how the pieces fit.

Run: python3 -m unittest discover -b tests
"""
import argparse
import json
import pathlib
import re
import shutil
import subprocess
import sys
import tempfile
import types
import unittest

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "evals"))

import grade  # noqa: E402
import proofkeys  # noqa: E402
import run as harness  # noqa: E402
from parts import eval_record  # noqa: E402

CASES = ("big-report", "fix-a-bug", "nightly-job")


def load_part_module(name):
    module = types.ModuleType(f"m3_{name}")
    path = ROOT / "parts" / f"{name}.py"
    module.__file__ = str(path)
    exec(compile(path.read_text(encoding="utf-8"), str(path), "exec"), module.__dict__)
    return module


class ArmFilesTests(unittest.TestCase):
    """Criteria 1, 56 and 61: a case's own arm files, additions to a shared arm, and one-time arms."""

    def test_a_case_with_its_own_arms_depends_on_no_shared_arm_file(self):
        case = {"name": "x", "playbook": "docs/p.md", "scaffold_dir": "evals/scaffold", "acceptance": "evals/acceptance/x.py",
                "arms": {"guided": {"files": {"docs/p.md": "docs/p.md", "CLAUDE.md": "evals/x/guided.md"}},
                         "two-line": {"files": {"CLAUDE.md": "evals/x/two-line.md"}}, "bare": {"files": {}}},
                "graders": [{"id": "g", "type": "any", "kind": "report"}]}
        shared = json.loads((ROOT / "evals/arms.json").read_text(encoding="utf-8"))
        files = eval_record.covered_files("evals/cases/x.json", case, ["evals/scaffold/a.py"], shared)
        self.assertNotIn("evals/arms.json", files)
        self.assertNotIn("evals/two-line.md", files)
        self.assertNotIn("AGENTS.md", files)
        self.assertIn("evals/x/guided.md", files)
        self.assertEqual(eval_record.case_arms(case, shared)["guided"]["CLAUDE.md"], "evals/x/guided.md")

    def test_criterion_61_an_own_arms_case_hashes_only_what_it_may(self):
        """Every case that names its own arms (B7's) covers only the case, its own arm files, its acceptance test
        and scaffold, the harness and the graders. B7's four cases are checked, and a sample stands in for the rule."""
        cases = [json.loads(p.read_text(encoding="utf-8")) for p in sorted((ROOT / "evals/cases").glob("*.json"))]
        sample = {"name": "sample", "playbook": "docs/p.md", "scaffold_dir": "evals/scaffold",
                  "acceptance": "evals/acceptance/sample.py",
                  "arms": {"guided": {"files": {"docs/p.md": "docs/p.md", "AGENTS.md": "evals/sample/contract.md"}},
                           "two-line": {"files": {"CLAUDE.md": "evals/sample/two-line.md"}}, "bare": {"files": {}}},
                  "graders": [{"id": "s", "type": "hook_allows", "hook": "no_stage_all", "kind": "run"}]}
        paths = subprocess.run(["git", "-C", str(ROOT), "ls-files"], capture_output=True, text=True).stdout.split()
        for case in [c for c in cases if "arms" in c] + [sample]:
            with self.subTest(case["name"]):
                path = f"evals/cases/{case['name']}.json"
                files = eval_record.covered_files(path, case, paths, None)
                own = {source for given in eval_record.case_arms(case, None).values() for source in given.values()}
                allowed = {path, case["acceptance"], "evals/run.py", "evals/grade.py", "evals/proofkeys.py",
                           eval_record.SHELL} | own | {f"parts/{g['hook']}.py" for g in case["graders"] if g.get("hook")}
                stray = [f for f in files if f not in allowed and not f.startswith(case["scaffold_dir"] + "/")]
                self.assertEqual(stray, [])

    def test_criterion_1_the_guided_arm_holds_the_rule_pages_the_case_touches(self):
        rule_pages = load_part_module("rule_pages")
        pages = {f"docs/rules/{p.name}": p.read_text(encoding="utf-8") for p in (ROOT / "docs/rules").glob("*.md")}
        for name in CASES:
            with self.subTest(name):
                case = harness.load_case(name)
                text = (ROOT / case["acceptance"]).read_text(encoding="utf-8")
                named = set(re.findall(r"src/[\w./-]+", text))
                named |= {"src/" + m for m in re.findall(r'"src"\s*/\s*"([\w.-]+)"', text)}
                named |= set(case.get("unchanged", []))
                for grader in case["graders"]:
                    named |= set(re.findall(r"src/[\w./-]+", grader.get("match", "")))
                want = sorted(page for page, body in pages.items()
                              if any(rule_pages.matches(pattern, path) or rule_pages.matches(pattern, path + "/x")
                                     for pattern in rule_pages._patterns(body) for path in named))
                given = sorted(p for p in case.get("add_files", {}).get("guided", {}) if p.startswith("docs/rules/"))
                self.assertEqual(given, want)
                self.assertTrue(set(given) <= set(harness.arms_for(case)["guided"]))
        self.assertEqual(sorted(harness.arms_for(harness.load_case("nightly-job"))["guided"])[-1], "docs/rules/orders-api.md")

    def test_criterion_56_a_one_time_arm_is_in_no_cases_hash(self):
        for name in CASES:
            with self.subTest(name):
                files, digest = harness.covered(name)
                self.assertNotIn("evals/one-time.json", files)
        with tempfile.TemporaryDirectory() as scratch:
            copy = pathlib.Path(scratch)
            for path in subprocess.run(["git", "-C", str(ROOT), "ls-files"], capture_output=True, text=True).stdout.split():
                if (ROOT / path).is_file() and not path.startswith(("evals/runs/", "src/")):
                    (copy / path).parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy(ROOT / path, copy / path)
            before = {name: harness.covered(name, copy)[1] for name in CASES}
            spec = json.loads((copy / "evals/one-time.json").read_text(encoding="utf-8"))
            spec["another"] = {"why": "a test", "base": "bare"}
            (copy / "evals/one-time.json").write_text(json.dumps(spec), encoding="utf-8")
            self.assertEqual({name: harness.covered(name, copy)[1] for name in CASES}, before)

    def test_criterion_56_the_routed_arm_reads_the_index_pages_unstripped_with_the_plugin(self):
        case = harness.load_case("nightly-job")
        files, plugins = harness.one_time_arm(case, "routed")
        self.assertTrue(set(harness.arms_for(case)["guided"].items()) <= set(files.items()))
        self.assertIn("docs/decisions/0006-what-proven-means.md", files)
        self.assertIn("docs/layout.md", files)
        self.assertEqual(plugins, ["plugin"])
        args = argparse.Namespace(one_time="routed", baseline=False, rerecord=None, attempt=None, runs=15)
        plan = harness.plan_runs(args, case, *harness.covered("nightly-job"))[1]    # the wrappers came in slice B6
        self.assertEqual(plan["routed"][1], ["plugin"])
        self.assertTrue((ROOT / "plugin/skills").is_dir())
        with tempfile.TemporaryDirectory() as scratch:     # a one-time arm whose plugin folder is missing is refused
            root = pathlib.Path(scratch)
            for path in ("evals/one-time.json", "evals/arms.json", "INDEX.md"):
                (root / path).parent.mkdir(parents=True, exist_ok=True)
                shutil.copy(ROOT / path, root / path)
            with self.assertRaises(ValueError) as caught:
                harness.plan_runs(args, case, [], "h", root)
            self.assertIn("plugin folder plugin", str(caught.exception))
        plugin = pathlib.Path("/tmp/plugin-0")
        command = harness.agent_command("go", "haiku", [plugin])
        self.assertEqual(command[-2:], ["--plugin-dir", str(plugin)])
        self.assertNotIn("--plugin-dir", harness.agent_command("go", "haiku"))

    def test_a_one_time_arms_runs_go_to_a_record_the_gate_never_reads(self):
        case = harness.load_case("nightly-job")
        with tempfile.TemporaryDirectory() as scratch:
            root = pathlib.Path(scratch)
            for path in ("evals/one-time.json", "evals/arms.json", "INDEX.md"):
                (root / path).parent.mkdir(parents=True, exist_ok=True)
                shutil.copy(ROOT / path, root / path)
            (root / "plugin").mkdir()
            args = argparse.Namespace(one_time="routed", baseline=False, rerecord=None, attempt=None, runs=15)
            out, plan, first, per, extra, _ = harness.plan_runs(args, case, [], "h", root)
        self.assertEqual(out.relative_to(root).as_posix(), "evals/runs/nightly-job/one-time/routed")
        self.assertEqual(list(plan), ["routed"])
        self.assertFalse(plan["routed"][2], "a one-time arm reads pages as they ship, unstripped")
        self.assertEqual(extra["kind"], "one-time")
        self.assertIn("never counts", eval_record.judge({"kind": "one-time", "arms": {}}, [], []))


class BaselineAndRerecordTests(unittest.TestCase):
    """Criterion 2, and the re-record a margin miss allows (criteria 4 and 15)."""

    def test_criterion_2_a_baseline_records_the_bare_arm_and_never_counts(self):
        case = harness.load_case("fix-a-bug")
        args = argparse.Namespace(one_time=None, baseline=True, rerecord=None, attempt="M4", runs=10)
        out, plan, first, per, extra, _ = harness.plan_runs(args, case, [], "h")
        self.assertEqual(out.name, "baseline")
        self.assertEqual(list(plan), ["bare"])
        self.assertEqual(extra, {"kind": "baseline", "page": "docs/playbooks/fix-a-bug.md", "milestone": "M4",
                                 "verdict": "not proven"})
        runs = [{"graders": {"g": True}}] * 10
        record = {"kind": "baseline", "runs_per_arm": 10, "arms": {arm: {"runs": runs} for arm in ("guided", "two-line", "bare")}}
        self.assertIn("baseline record, which never counts", eval_record.judge(record, ["guided", "two-line", "bare"], ["g"]))

    def test_a_rerecord_needs_a_current_record_and_happens_once(self):
        case = harness.load_case("fix-a-bug")
        files, digest = harness.covered("fix-a-bug")
        args = argparse.Namespace(one_time=None, baseline=False, rerecord="guided", attempt=None, runs=15)
        with tempfile.TemporaryDirectory() as scratch:
            root = pathlib.Path(scratch)
            shutil.copytree(ROOT / "evals", root / "evals", ignore=shutil.ignore_patterns("runs"))
            out = root / "evals/runs/fix-a-bug"
            out.mkdir(parents=True)
            with self.assertRaises(ValueError):
                harness.plan_runs(args, case, files, digest, root)
            (out / "record.json").write_text(json.dumps({"guidance_sha256": digest, "runs_per_arm": 15}), encoding="utf-8")
            out_, plan, first, per, extra, numbers = harness.plan_runs(args, case, files, digest, root)
            self.assertEqual((list(plan), first, per, extra, numbers),
                             (["guided"], 16, 15, {"rerecorded": ["guided"]}, {"guided": 30}))
            (out / "record.json").write_text(json.dumps({"guidance_sha256": digest, "runs_per_arm": 15,
                                                         "rerecorded": ["guided"]}), encoding="utf-8")
            with self.assertRaises(ValueError):
                harness.plan_runs(args, case, files, digest, root)

    def test_criterion_4_the_scale_rule(self):
        def records(passes, total, again=False):
            runs = [{"graders": {"g": i < passes}} for i in range(total)]
            return {"c": {"arms": {"guided": {"runs": runs}}, "rerecorded": ["guided"] if again else []}}
        graders = {"c": ["g"]}
        self.assertIsNone(eval_record.slipped(records(37, 45), records(40, 45), "old", graders))
        self.assertIn("more than 3 fewer", eval_record.slipped(records(36, 45), records(40, 45), "old", graders))
        self.assertIsNone(eval_record.slipped(records(74, 90, True), records(40, 45), "old", graders))
        self.assertIn("more than 6 fewer", eval_record.slipped(records(73, 90, True), records(40, 45), "old", graders))
        self.assertIn("more than 6 fewer", eval_record.slipped(records(73, 90, True), records(80, 90, True), "old", graders))
        self.assertIsNone(eval_record.slipped(records(37, 45), records(80, 90, True), "old", graders))
        self.assertIn("more than 6 fewer", eval_record.slipped(records(36, 45), records(80, 90, True), "old", graders))
        # Only the cases both records hold count.
        both = {**records(37, 45), "d": records(0, 45)["c"]}
        self.assertIsNone(eval_record.slipped(both, records(40, 45), "old", {"c": ["g"], "d": ["g"]}))
        # A pooled arm that passes on count but fails on rate does not beat the bare arm.
        rec = {"runs_per_arm": 15, "rerecorded": ["guided"],
               "arms": {"guided": {"runs": [{"graders": {"g": i < 10}} for i in range(30)]},
                        "bare": {"runs": [{"graders": {"g": i < 8}} for i in range(15)]},
                        "two-line": {"runs": [{"graders": {"g": False}}] * 15}}}
        self.assertIn("10 of 30 against 8 of 15", eval_record.judge(rec, ["guided", "two-line", "bare"], ["g"]))


class ProofKeyTests(unittest.TestCase):
    """Criterion 67: the runner strips the proof keys in their exact forms only, and the hash ignores them."""

    PAGE = ("---\nkind: playbook\nlast-reviewed: 2026-11-18\nproof: unproven\nprove-by: M6\n---\n\n# P\n\nPurpose.\n\n"
            "## Gates\n\nProof: unproven, prove-by M6.\n\nStep one.\n")

    def digest(self, text):
        return eval_record.guidance_hash({"docs/p.md": text}, proofkeys.strip)

    def test_a_flip_between_proven_and_unproven_leaves_the_hash(self):
        proven = self.PAGE.replace("proof: unproven\nprove-by: M6", "proof: proven\nproven-by: docs/milestones/m1.md, "
                                   + "a" * 40 + ":evals/runs/x/record.json")
        proven = proven.replace("Proof: unproven, prove-by M6.", "Proof: proven, proven-by docs/milestones/m1.md.")
        self.assertEqual(self.digest(self.PAGE), self.digest(proven))
        stripped = proofkeys.strip(self.PAGE)
        self.assertNotIn("proof", stripped.lower())
        self.assertIn("## Gates\n\nStep one.", stripped)

    def test_a_variant_is_hashed_and_refused(self):
        for variant in (self.PAGE.replace("proof: unproven", "proof: unproven, for now"),
                        self.PAGE.replace("prove-by: M6", "prove-by: M6 or M7"),
                        self.PAGE.replace("Proof: unproven, prove-by M6.", "Proof: unproven, prove-by M6. Soon."),
                        self.PAGE.replace("prove-by: M6", "proven-by: [M1](docs/milestones/m1.md)")):
            with self.subTest(variant):
                self.assertNotEqual(self.digest(self.PAGE), self.digest(variant))
                self.assertTrue(proofkeys.problems(variant))
        self.assertEqual(proofkeys.problems(self.PAGE), [])

    def test_the_gated_arm_reads_pages_stripped(self):
        with tempfile.TemporaryDirectory() as scratch:
            folder = pathlib.Path(scratch) / "run"
            folder.mkdir()
            case = harness.load_case("fix-a-bug")
            harness.prepare(folder, case, {"docs/playbooks/fix-a-bug.md": "docs/playbooks/fix-a-bug.md"})
            given = (folder / "docs/playbooks/fix-a-bug.md").read_text(encoding="utf-8")
            self.assertNotIn("proven-by", given)
            self.assertIn("kind: playbook", given)
            folder2 = pathlib.Path(scratch) / "routed"
            folder2.mkdir()
            harness.prepare(folder2, case, {"docs/playbooks/fix-a-bug.md": "docs/playbooks/fix-a-bug.md"}, stripped=False)
            self.assertIn("proven-by", (folder2 / "docs/playbooks/fix-a-bug.md").read_text(encoding="utf-8"))

    def test_the_check_and_the_harness_strip_through_the_same_file(self):
        text = (ROOT / "evals/proofkeys.py").read_text(encoding="utf-8")
        loaded = eval_record.load_proof_keys(text, "evals/proofkeys.py")
        self.assertEqual(loaded.strip(self.PAGE), proofkeys.strip(self.PAGE))
        self.assertIn("proofkeys.py", eval_record.HARNESS)


class GraderTests(unittest.TestCase):
    """Criterion 5: the review-protocol and diagnosis graders, each with a passing and a failing run."""

    REVIEW = {"name": "review", "graders": [
        {"id": "a-fresh-session-was-dispatched", "type": "any", "kind": "dispatch"},
        {"id": "the-findings-file-exists", "type": "any", "kind": "state", "match": "^file exists: ", "ok": True},
        {"id": "the-reply-gives-only-path-and-verdict", "type": "report_brief", "path": r"reviews/\S+\.md",
         "verdict": r"\b(?:ready|not ready|blocked)\b", "max_lines": 3},
        {"id": "a-triage-table-exists", "type": "any", "kind": "state", "match": "^table in: ", "ok": True}]}
    DIAGNOSIS = {"name": "diagnosis", "graders": [
        {"id": "a-regression-test-fails-on-the-original-code", "type": "any", "kind": "state",
         "match": "^tests fail on the original code$", "ok": True},
        {"id": "the-debug-output-is-gone", "type": "any", "kind": "state",
         "match": "^no debug output left in the change$", "ok": True}]}

    def test_the_review_protocol_passes_and_fails(self):
        good = [{"kind": "dispatch", "target": "Red-team the plan", "ok": True},
                {"kind": "state", "target": "file exists: reviews/*.md", "ok": True},
                {"kind": "state", "target": "table in: reviews/*.md", "ok": True},
                {"kind": "report", "target": "reviews/plan-review.md\nVerdict: not ready", "ok": True}]
        self.assertTrue(all(ok for _, ok in grade.grade(self.REVIEW, good)))
        chatty = good[:3] + [{"kind": "report", "target": "Here are the findings:\n1. a\n2. b\n3. c\nreviews/x.md ready", "ok": True}]
        alone = [a for a in good if a["kind"] != "dispatch"]
        self.assertEqual(dict(grade.grade(self.REVIEW, chatty))["the-reply-gives-only-path-and-verdict"], False)
        self.assertEqual(dict(grade.grade(self.REVIEW, alone))["a-fresh-session-was-dispatched"], False)

    def test_the_diagnosis_passes_and_fails(self):
        good = [{"kind": "state", "target": "tests fail on the original code", "ok": True},
                {"kind": "state", "target": "no debug output left in the change", "ok": True},
                {"kind": "report", "target": "done", "ok": True}]
        left = [dict(good[0]), {"kind": "state", "target": "no debug output left in the change", "ok": False}, good[2]]
        self.assertTrue(all(ok for _, ok in grade.grade(self.DIAGNOSIS, good)))
        self.assertEqual(dict(grade.grade(self.DIAGNOSIS, left))["the-debug-output-is-gone"], False)

    def test_the_harness_writes_the_state_lines_these_graders_read(self):
        with tempfile.TemporaryDirectory() as scratch:
            folder = pathlib.Path(scratch)
            harness.git(folder, "init", "-q", "-b", "main")
            (folder / "src").mkdir()
            (folder / "src/a.py").write_text("x = 1\n", encoding="utf-8")
            harness.git(folder, "add", "src/a.py")
            harness.git(folder, "commit", "-q", "-m", "start")
            start = harness.git(folder, "rev-parse", "HEAD").stdout.strip()
            (folder / "src/a.py").write_text("x = 1\nprint('DEBUG', x)\n", encoding="utf-8")
            (folder / "reviews").mkdir()
            (folder / "reviews/r.md").write_text("| # | Finding |\n|---|---|\n| 1 | x |\n", encoding="utf-8")
            lines = [harness._check(folder, start, check, "src") for check in
                     ({"file": "reviews/*.md"}, {"table": "reviews/*.md"}, {"debug": r"\bDEBUG\b|print\("}, {"file": "none/*.md"})]
            self.assertEqual([line["ok"] for line in lines], [True, True, False, False])

    def test_a_dispatch_reaches_the_transcript(self):
        log = "\n".join(json.dumps(e) for e in [
            {"type": "assistant", "message": {"content": [{"type": "tool_use", "id": "1", "name": "Agent",
                                                           "input": {"description": "Red-team it", "prompt": "..."}}]}},
            {"type": "result", "result": "reviews/x.md: ready"}])
        actions = harness.to_transcript(log, pathlib.Path("/nowhere"))[0]
        self.assertEqual(actions[0], {"kind": "dispatch", "target": "Red-team it", "ok": True})


class StructureTests(unittest.TestCase):
    """Criteria 7 to 13 on the real repository."""

    def manifest(self):
        return json.loads((ROOT / "workspace.json").read_text(encoding="utf-8"))

    def test_criterion_7_freshness_is_retired_and_named_nowhere(self):
        manifest = self.manifest()
        self.assertIn("freshness", [r["use"] for r in manifest["retired"]])
        self.assertNotIn("freshness", json.dumps(manifest["parts"]))
        self.assertFalse((ROOT / "parts/freshness.py").exists())

    def test_criterion_8_the_archive_is_hidden_from_search(self):
        if shutil.which("rg") is None:
            self.skipTest("ripgrep is not installed here")
        marker = "-".join(["archived", "page", "marker", "7f3a"])   # not written whole here, or rg finds this file
        page = ROOT / "archive" / "test-marker.md"
        page.write_text(f"# Gone\n\n{marker}\n", encoding="utf-8")
        try:
            found = subprocess.run(["rg", "-l", marker, "."], cwd=ROOT, capture_output=True, text=True,
                                   stdin=subprocess.DEVNULL, timeout=60).stdout
        finally:
            page.unlink()
        self.assertEqual(found.strip(), "")
        for part in ("links", "page_kinds"):
            entry = next(e for e in self.manifest()["parts"] if e["use"] == part)
            self.assertIn("archive", entry["skip"])

    def test_criterion_11_the_contract_and_index_are_corrected(self):
        self.assertNotIn("one repository per folder", (ROOT / "AGENTS.md").read_text(encoding="utf-8"))
        self.assertNotIn("plan being built now", (ROOT / "INDEX.md").read_text(encoding="utf-8").lower())

    def test_criterion_12_the_register_prints_a_count_per_tag(self):
        done = subprocess.run([sys.executable, "ws.py", "rules"], cwd=ROOT, capture_output=True, text=True)
        self.assertEqual(done.returncode, 0, done.stderr)
        self.assertRegex(done.stdout, r"rule\(s\)\. Tags: eval \d+, part \d+, prose \d+")

    def test_criterion_14_m3_is_being_built_and_the_template_names_a_milestone(self):
        self.assertEqual(self.manifest()["building"], ["M3"])
        self.assertIn("milestone: M<n>", (ROOT / "docs/templates/hand-off-plan.md").read_text(encoding="utf-8"))
        page = (ROOT / "docs/playbooks/fix-a-bug.md").read_text(encoding="utf-8")
        front = proofkeys.keys(page)[0]
        self.assertEqual(front["proof"], "proven")
        anchors = [item for item in proofkeys.parse_list(front["proven-by"]) if item[0]]
        self.assertEqual(sorted(path for _, path in anchors), [f"evals/runs/{c}/record.json" for c in CASES])
        for sha, _ in anchors:
            self.assertEqual(subprocess.run(["git", "-C", str(ROOT), "merge-base", "--is-ancestor", sha, "HEAD"]).returncode, 0)

    def test_the_proven_sentence_is_changed_everywhere_it_stood(self):
        sentence = "a playbook marked proven stays only while"
        self.assertIn(sentence, (ROOT / "README.md").read_text(encoding="utf-8").lower())
        why = next(e["why"] for e in self.manifest()["parts"] if e["use"] == "eval_record")
        self.assertIn(sentence, why.lower())
        self.assertIn(sentence, (ROOT / "parts/eval_record.py").read_text(encoding="utf-8").lower())


if __name__ == "__main__":
    unittest.main()
