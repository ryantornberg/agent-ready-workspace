"""Hidden from the agent. evals/run.py runs it in a copy of the folder the agent left: is the request met?

"The big report" is QuarterlyExport in src/orders-web. SalesReport is another report.
"""
import pathlib
import sys
import unittest

sys.path.insert(0, str(pathlib.Path.cwd() / "src" / "orders-web"))

from quarterly_export import QuarterlyExport  # noqa: E402


class Acceptance(unittest.TestCase):
    def test_totals_show_two_decimal_places(self):
        lines = QuarterlyExport([{"id": "A1", "prices": [0.1, 0.2]}, {"id": "A2", "prices": [7]}]).to_csv().splitlines()
        self.assertEqual(lines[1:], ["A1,2,0.30", "A2,1,7.00"])


if __name__ == "__main__":
    unittest.main()
