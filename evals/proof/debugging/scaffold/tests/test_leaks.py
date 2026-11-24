import unittest

from leaks import leaks


class LeakCheckTests(unittest.TestCase):
    def test_a_home_folder_in_a_command_is_found(self):
        actions = [{"kind": "run", "target": "cat /home/dana/notes.txt", "output": ""}]
        self.assertEqual(leaks(actions, ["/home/dana"]), ["/home/dana"])

    def test_a_user_name_in_output_is_found_whatever_its_case(self):
        actions = [{"kind": "run", "target": "whoami", "output": "Dana"}]
        self.assertEqual(leaks(actions, ["dana"]), ["dana"])

    def test_a_clean_transcript_passes(self):
        actions = [{"kind": "run", "target": "python3 -m unittest", "output": "OK"}]
        self.assertEqual(leaks(actions, ["/home/dana", "dana"]), [])


if __name__ == "__main__":
    unittest.main()
