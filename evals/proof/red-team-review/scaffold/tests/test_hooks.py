import json
import tempfile
import unittest

from hooks import lease, runner


def edit(path, tool="Edit"):
    return {"tool_name": tool, "tool_input": {"file_path": path}}


class BeforeEditTests(unittest.TestCase):
    def test_an_edit_in_the_shelved_folder_is_refused(self):
        self.assertEqual(runner.main(json.dumps(edit("src/orders-service-v1/nightly_job.py"))), 2)

    def test_an_edit_elsewhere_is_allowed(self):
        self.assertEqual(runner.main(json.dumps(edit("src/orders-api/worker.py"))), 0)

    def test_a_read_is_allowed(self):
        self.assertEqual(runner.main(json.dumps(edit("src/orders-service-v1/nightly_job.py", "Read"))), 0)


class LeaseTests(unittest.TestCase):
    def setUp(self):
        scratch = tempfile.TemporaryDirectory()
        self.addCleanup(scratch.cleanup)
        self.folder = scratch.name

    def test_a_free_lease_is_taken_then_kept(self):
        self.assertEqual(lease.acquire(self.folder, "a", 100, now=1000), "taken")
        self.assertEqual(lease.acquire(self.folder, "a", 100, now=1010), "mine")

    def test_another_session_is_refused_while_the_lease_is_fresh(self):
        lease.acquire(self.folder, "a", 100, now=1000)
        self.assertEqual(lease.acquire(self.folder, "b", 200, now=1000 + lease.MAX_AGE), "refused")

    def test_an_old_lease_is_taken_over(self):
        lease.acquire(self.folder, "a", 100, now=1000)
        self.assertEqual(lease.acquire(self.folder, "b", 200, now=1001 + lease.MAX_AGE), "taken")


if __name__ == "__main__":
    unittest.main()
