"""Sales per customer, for the sales team."""


class SalesReport:
    def __init__(self, orders):
        self.orders = list(orders)

    def lines(self):
        totals = {}
        for order in self.orders:
            totals[order["customer"]] = totals.get(order["customer"], 0) + sum(order["prices"])
        return [f"{customer}: {total}" for customer, total in sorted(totals.items())]
