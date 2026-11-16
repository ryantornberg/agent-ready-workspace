"""The orders page: a table of orders and two buttons."""
from csv_export import to_csv


class OrdersPage:
    def __init__(self, orders):
        self.orders = list(orders)
        self.shown = []
        self.downloads = []
        self._handlers = {}
        self._on("refresh", self.refresh)

    def _on(self, button, handler):
        self._handlers[button] = handler

    def click(self, button):
        """Run the button's handler. A button with no handler does nothing."""
        handler = self._handlers.get(button)
        if handler:
            handler()

    def refresh(self):
        self.shown = sorted(self.orders, key=lambda order: order["id"])

    def export(self):
        self.downloads.append(to_csv(self.orders))
