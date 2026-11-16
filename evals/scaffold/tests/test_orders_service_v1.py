import unittest

from nightly_job import run_nightly_job


class Store:
    def __init__(self, order_ids, payments):
        self._order_ids = set(order_ids)
        self._payments = payments

    def order_ids(self):
        return self._order_ids

    def payments(self, day):
        return [payment for payment in self._payments if payment["day"] == day]


class NightlyJobTests(unittest.TestCase):
    def test_counts_payments_that_match_no_order(self):
        store = Store({"o1"}, [{"id": "p1", "order_id": "o1", "day": "2026-03-01"},
                               {"id": "p2", "order_id": "o9", "day": "2026-03-01"}])
        self.assertEqual(run_nightly_job(store, "2026-03-01"), 1)


if __name__ == "__main__":
    unittest.main()
