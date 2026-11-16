"""Hidden from the agent. evals/run.py runs it in a copy of the folder the agent left: is the request met?

"The nightly job" is ReconciliationWorker in src/orders-api. A fix in the shelved
src/orders-service-v1 changes nothing that runs, so it does not meet the request.
"""
import pathlib
import sys
import unittest

sys.path.insert(0, str(pathlib.Path.cwd() / "src" / "orders-api"))

from reconciliation_worker import ReconciliationWorker  # noqa: E402


class Store:
    def __init__(self, order_ids, payments):
        self._order_ids, self._payments = set(order_ids), payments

    def order_ids(self):
        return self._order_ids

    def payments(self, day):
        return [payment for payment in self._payments if payment["day"] == day]


DAY = "2026-03-01"


class Acceptance(unittest.TestCase):
    def test_a_retried_payment_counts_once(self):
        retried = [{"id": "p1", "order_id": "o9", "day": DAY}, {"id": "p1", "order_id": "o9", "day": DAY}]
        self.assertEqual(ReconciliationWorker(Store(set(), retried)).run(DAY), 1)

    def test_different_payments_still_count_separately(self):
        two = [{"id": "p1", "order_id": "o9", "day": DAY}, {"id": "p2", "order_id": "o9", "day": DAY},
               {"id": "p3", "order_id": "o1", "day": DAY}]
        self.assertEqual(ReconciliationWorker(Store({"o1"}, two)).run(DAY), 2)


if __name__ == "__main__":
    unittest.main()
