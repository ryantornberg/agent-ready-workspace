import unittest

from reconciliation_worker import ReconciliationWorker
from sales_report import SalesReport


class Store:
    def __init__(self, order_ids, payments):
        self._order_ids = set(order_ids)
        self._payments = payments

    def order_ids(self):
        return self._order_ids

    def payments(self, day):
        return [payment for payment in self._payments if payment["day"] == day]


class ReconciliationWorkerTests(unittest.TestCase):
    def test_counts_payments_that_match_no_order(self):
        store = Store({"o1"}, [{"id": "p1", "order_id": "o1", "day": "2026-03-01"},
                               {"id": "p2", "order_id": "o9", "day": "2026-03-01"}])
        self.assertEqual(ReconciliationWorker(store).run("2026-03-01"), 1)

    def test_only_the_days_payments_count(self):
        store = Store(set(), [{"id": "p1", "order_id": "o9", "day": "2026-03-02"}])
        self.assertEqual(ReconciliationWorker(store).run("2026-03-01"), 0)


class SalesReportTests(unittest.TestCase):
    def test_one_line_per_customer_in_name_order(self):
        report = SalesReport([{"customer": "Okafor", "prices": [4]}, {"customer": "Lindqvist", "prices": [2]}])
        self.assertEqual(report.lines(), ["Lindqvist: 2", "Okafor: 4"])


if __name__ == "__main__":
    unittest.main()
