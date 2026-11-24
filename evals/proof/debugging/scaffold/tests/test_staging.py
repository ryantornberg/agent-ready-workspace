import unittest

from staging import stages_all


class StagingReminderTests(unittest.TestCase):
    def test_staging_everything_is_caught(self):
        for command in ("git add -A", "git add --all", "git add .", "git commit -a -m 'fix'", "git commit -am 'fix'"):
            with self.subTest(command):
                self.assertTrue(stages_all(command))

    def test_files_named_one_by_one_pass(self):
        for command in ("git add src/staging.py", "git commit -m 'fix the reminder'", "git status", "ls -A"):
            with self.subTest(command):
                self.assertFalse(stages_all(command))


if __name__ == "__main__":
    unittest.main()
