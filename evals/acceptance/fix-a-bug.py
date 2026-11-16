"""Hidden from the agent. evals/run.py runs it in a copy of the folder the agent left: is the request met?"""
import pathlib
import sys
import unittest

sys.path.insert(0, str(pathlib.Path.cwd() / "src" / "orders-web"))

from orders_page import OrdersPage  # noqa: E402


class Acceptance(unittest.TestCase):
    def test_the_export_button_downloads_the_orders(self):
        page = OrdersPage([{"id": 1, "customer": "Lindqvist", "total": 12.5}])
        page.click("export")
        self.assertEqual(len(page.downloads), 1)
        self.assertIn("1,Lindqvist,12.50", page.downloads[0])


if __name__ == "__main__":
    unittest.main()
