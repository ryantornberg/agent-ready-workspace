"""M3 slice C3d: the secret scan, the commit-subject check, and what every finding names (criteria 32 to 34)."""
import pathlib
import re
import sys
import unittest

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from tests.test_core import Folder, manifest  # noqa: E402
from wslib import parts as partlib  # noqa: E402
from wslib import snapshot as snapshots  # noqa: E402

# Built from pieces, so this file's text holds no whole token.
TOKEN = "gh" + "p_" + "abcdefghijklmnopqrstuvwxyzABCDEFGHIJ"


class SecretScanTests(Folder):
    """Criterion 32: the commit check fails a token a commit adds, and the history scan fails one in an old commit."""

    def setUp(self):
        super().setUp()
        self.workspace({"use": "secret_scan", "why": "test"})
        self.git("init", "-q", "-b", "main")
        self.git("add", ".")
        self.git("commit", "-q", "-m", "chore: start")

    def test_a_staged_line_with_a_token_fails_the_commit_check(self):
        self.write("config/app.txt", f"token = {TOKEN}\n")
        self.git("add", "config/app.txt")
        code, out = self.ws("check", "--staged")
        self.assertEqual(code, 1, out)
        self.assertIn("a GitHub token", out)
        self.assertNotIn(TOKEN, out)

    def test_the_history_scan_finds_a_token_a_later_commit_deleted(self):
        self.write("config/app.txt", f"token = {TOKEN}\n")
        self.git("add", "config/app.txt")
        self.git("commit", "-q", "--no-verify", "-m", "chore: oops")
        self.write("config/app.txt", "token = from the environment\n")
        self.git("add", "config/app.txt")
        self.git("commit", "-q", "--no-verify", "-m", "fix: take the token out")
        self.assertEqual(self.ws("check", "--staged")[0], 0)
        code, out = self.ws("check", "--history")
        self.assertEqual(code, 1, out)
        self.assertRegex(out, r"[0-9a-f]{12}:config/app\.txt:1: adds what looks like a GitHub token")
        self.assertNotIn(TOKEN, out)

    def test_a_clean_history_passes(self):
        code, out = self.ws("check", "--history")
        self.assertEqual(code, 0, out)

    def test_this_repository_s_history_is_clean(self):
        found = [f for f in partlib.load(ROOT, {"use": "secret_scan", "why": "t"}).run(snapshots.history(ROOT))]
        self.assertEqual(found, [])


class CommitSubjectTests(Folder):
    """Criterion 33, through the commit-msg hook's own command."""

    def setUp(self):
        super().setUp()
        self.workspace({"use": "commit_subject", "why": "test"})
        self.git("init", "-q", "-b", "main")
        self.git("add", ".")

    def message(self, text):
        self.write(".git/COMMIT_EDITMSG", text)
        return self.ws("check", "--message", str(self.root / ".git/COMMIT_EDITMSG"))

    def test_the_manifest_formats_decide(self):
        self.assertEqual(self.message("feat(c3d): a subject check\n")[0], 0)
        code, out = self.message("did some things\n")
        self.assertEqual(code, 1, out)
        self.assertIn("matches none of the accepted formats", out)
        for own in ("Merge branch 'main' into topic\n", 'Revert "feat: a thing"\n', "Merge pull request #1 from a/b\n"):
            with self.subTest(own):
                self.assertEqual(self.message(own)[0], 0)
        code, out = self.message("docs: " + "a" * 80 + "\n")
        self.assertEqual(code, 0, out)
        self.assertIn("warning:", out)
        self.write("workspace.json", manifest([{"use": "commit_subject", "why": "test",
                                                "formats": [r"^[A-Z]+-\d+ \S"]}]))
        self.git("add", "workspace.json")
        self.assertEqual(self.message("ABC-12 add a thing\n")[0], 0)
        self.assertEqual(self.message("feat: a thing\n")[0], 1)


class FindingsNameTheirPageTests(unittest.TestCase):
    """Criterion 34: every finding any part's cases produce names the file, the rule's page and a fix or a re-run
    command; so does every refusal and reminder. One message waits for slice Z, named here."""

    # parts/no_stage_all.py is a file the eval hashes; slice Z adds its page (plan, change of 2026-11-21).
    # rule_pages's reminder is the rule pages themselves, shown before an edit, not a finding.
    EXEMPT = {"no_stage_all", "rule_pages"}
    COMMAND = re.compile(r"python3 ws\.py|\bgit |\bgh |`[^`]+`|\b(run|add|remove|delete|move|write|rename|"
                         r"record|reword|shorten|take|fix|edit|use|mark|give|name|link|review|wait|ask|work|"
                         r"leave|stage|set|list|replace|commit|cite|split|rerun|re-run|change|pin|check out|"
                         r"turn|state|keep|start|restore|repair)\b", re.I)

    def test_every_case_message_names_its_page_and_a_fix(self):
        manifest = partlib.load_manifest(ROOT)
        problems = []
        for entry in manifest["parts"]:
            part = partlib.load(ROOT, entry, run_cases=False, tiers=manifest.get("tiers"))
            if part.name in self.EXEMPT:
                continue
            page = getattr(part.module, "PAGE", None)
            if not page:
                problems.append(f"{part.name}: no PAGE")
                continue
            for case in part.cases:
                for text, path in self.messages(part, case):
                    if path is not None and not path:
                        problems.append(f"{part.name} / {case['name']}: a finding names no file")
                    if page not in text:
                        problems.append(f"{part.name} / {case['name']}: does not name {page}: {text[:100]}")
                    if not self.COMMAND.search(text):
                        problems.append(f"{part.name} / {case['name']}: names no fix or command: {text[:100]}")
        self.assertEqual(problems, [], "\n".join(problems[:40]))

    @staticmethod
    def messages(part, case):
        config = case.get("config", {})
        if part.kind == "check":
            memory = snapshots.Memory(case["files"], case.get("changed", ()), case.get("staged"), case.get("ledger"),
                                      case.get("replaying"), case.get("repositories", ()), case.get("symlinks", ()),
                                      case.get("pushed", ()), case.get("pins", ()), case.get("added"),
                                      case.get("history"))
            try:
                found = part.module.run(memory, config)
            except partlib.PartError:
                return []
            page = getattr(part.module, "PAGE", None)
            return [(partlib.describe(f, part.name, page, "python3 ws.py check"), f["path"]) for f in found]
        try:
            reason = part.decide(case["event"], config)
        except partlib.PartError:
            return []
        return [(partlib.with_page(reason, getattr(part.module, "PAGE", None)), None)] if reason else []

    def test_the_exemption_is_still_needed(self):
        source = (ROOT / "parts" / "no_stage_all.py").read_text(encoding="utf-8")   # rule_pages stays exempt
        self.assertNotIn("PAGE", source, "no_stage_all names its page now: remove it from EXEMPT")


if __name__ == "__main__":
    unittest.main()
