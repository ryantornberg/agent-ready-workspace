"""Turn orders into CSV text."""


def to_csv(orders):
    lines = ["id,customer,total"]
    for order in orders:
        lines.append(f"{order['id']},{order['customer']},{order['total']:.2f}")
    return "\n".join(lines) + "\n"
