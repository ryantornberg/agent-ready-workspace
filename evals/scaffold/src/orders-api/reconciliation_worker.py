"""Runs once a night and counts the day's payments that match no order."""


class ReconciliationWorker:
    def __init__(self, store):
        self.store = store

    def run(self, day):
        """Return how many of the day's payments match no order."""
        order_ids = self.store.order_ids()
        unmatched = [payment for payment in self.store.payments(day) if payment["order_id"] not in order_ids]
        return len(unmatched)
