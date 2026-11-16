import unittest

from csv_export import to_csv
from orders_page import OrdersPage
from quarterly_export import QuarterlyExport

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


class QuarterlyExportTests(unittest.TestCase):
    def test_one_line_per_order_after_the_header(self):
        export = QuarterlyExport([{"id": "A1", "prices": [10, 5]}, {"id": "A2", "prices": [7]}])
        self.assertEqual(export.to_csv().splitlines()[0], "order_id,items,total")
        self.assertEqual(len(export.to_csv().splitlines()), 3)


if __name__ == "__main__":
    unittest.main()
