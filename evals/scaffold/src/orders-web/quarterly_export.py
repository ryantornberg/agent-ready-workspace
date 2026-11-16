"""Every order in a quarter, one line each, as CSV."""


class QuarterlyExport:
    def __init__(self, orders):
        self.orders = list(orders)

    def to_csv(self):
        lines = ["order_id,items,total"]
        for order in self.orders:
            total = sum(order["prices"])
            lines.append(f"{order['id']},{len(order['prices'])},{total}")
        return "\n".join(lines) + "\n"
