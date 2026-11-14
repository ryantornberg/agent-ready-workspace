import unittest

from shop.csv_export import to_csv
from shop.page import OrdersPage

ORDERS = [
    {"id": 2, "customer": "Okafor", "total": 40.0},
    {"id": 1, "customer": "Lindqvist", "total": 12.5},
]


class OrdersPageTests(unittest.TestCase):
    def test_refresh_button_sorts_the_table(self):
        page = OrdersPage(ORDERS)
        page.click("refresh")
        self.assertEqual([order["id"] for order in page.shown], [1, 2])

    def test_export_writes_one_download(self):
        page = OrdersPage(ORDERS)
        page.export()
        self.assertEqual(len(page.downloads), 1)

    def test_csv_has_a_header_and_a_row_per_order(self):
        self.assertEqual(to_csv(ORDERS).splitlines(), ["id,customer,total", "2,Okafor,40.00", "1,Lindqvist,12.50"])


if __name__ == "__main__":
    unittest.main()
