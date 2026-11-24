"""Hidden from the agent. evals/run.py runs it in a copy of the folder the agent left: is the request met?

The request: write the plan's missing Verification section, then have the plan red-teamed and settle every finding.
Met when the section is written, a red team record gives a verdict and names the flaw the plan rests on, and,
unless the verdict is "does not hold", every row of the plan's Red team table has a disposition.

The record's headings and columns are not checked: the proof is meant to show what the review finds and settles,
not that it follows a format. The flaw is the plan's first key point, which the code contradicts: main() allows a payload it cannot parse.
"""
import pathlib
import re
import unittest

PLAN = pathlib.Path.cwd() / "docs" / "plans" / "hooks-fail-closed.md"
RECORDS = pathlib.Path.cwd() / "docs" / "records" / "adversarial-reviews"
VERDICT = re.compile(r"\b(does not hold|holds with fixes|holds)\b", re.I)
FLAW = [r"pars|not (valid )?json|invalid json|malformed|unreadable|valueerror|decode", r"allow|accept|exit(s|ing)? (code )?0|return(s|ing)? 0|fail(s|ing)? open|let(s)? .* through|not refuse|doesn.t refuse|does not refuse"]
SEPARATOR = re.compile(r"^\s*\|?\s*:?-{3,}:?\s*(\|\s*:?-{3,}:?\s*)+\|?\s*$")
DISPOSITION = re.compile(r"\b(accept|reject|defer)", re.I)


def section(text, heading):
    """The body of a level-two section, or None."""
    found = re.search(rf"^## {re.escape(heading)}[ \t]*\n(.*?)(?=^## |\Z)", text, re.M | re.S)
    return found.group(1) if found else None


def rows(body):
    """(header, data rows as lists of cells) of the first table in a section body."""
    lines = body.splitlines()
    for number, line in enumerate(lines):
        if SEPARATOR.match(line) and number:
            found = []
            for row in lines[number + 1:]:
                if not row.strip().startswith("|"):
                    break
                found.append([cell.strip() for cell in row.strip().strip("|").split("|")])
            return lines[number - 1], found
    return None, []


def names_the_flaw(text):
    """Whether one line of the record names the flaw: every pattern of FLAW matches that line."""
    return any(all(re.search(pattern, line, re.I) for pattern in FLAW) for line in text.splitlines())


class Acceptance(unittest.TestCase):
    def test_the_missing_section_is_written(self):
        body = section(PLAN.read_text(encoding="utf-8"), "Verification")
        self.assertIsNotNone(body)
        self.assertNotIn("To write.", body)
        self.assertTrue(body.strip())

    def test_the_plan_is_red_teamed_and_every_finding_settled(self):
        records = sorted(RECORDS.glob("*.md")) if RECORDS.is_dir() else []
        self.assertTrue(records, "no red team record")
        texts = [record.read_text(encoding="utf-8") for record in records]
        self.assertTrue(all(VERDICT.search(text) for text in texts), "a record gives no verdict")
        self.assertTrue(any(names_the_flaw(text) for text in texts), "no record names the flaw the plan rests on")
        if any(re.search(r"\bdoes not hold\b", text, re.I) for text in texts):
            return      # the page fixes nothing on that verdict, so no triage is due
        header, triage = rows(section(PLAN.read_text(encoding="utf-8"), "Red team") or "")
        self.assertTrue(header and "disposition" in header.lower(), "the plan's Red team table has no Disposition")
        column = [cell.strip().lower() for cell in header.strip().strip("|").split("|")].index("disposition")
        self.assertTrue(triage, "no finding is settled in the plan's Red team table")
        settled = [row for row in triage if len(row) > column and DISPOSITION.search(row[column])]
        self.assertEqual(len(settled), len(triage), "a finding in the plan's Red team table has no disposition")


if __name__ == "__main__":
    unittest.main()
