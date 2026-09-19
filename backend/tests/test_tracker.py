"""Unit tests for PhonePe Expense Tracker backend services."""

import unittest
from pathlib import Path
import tempfile
import json
import csv

from backend.src.services.categorizer import get_category
from backend.src.services.tracker import ExpenseTrackerService
from backend.src.services.exporter import ExportService
from backend.src.models.expense import Transaction, ParsingError


class TestCategorizer(unittest.TestCase):
    """Tests for merchant categorization engine."""

    def test_food_categorization(self):
        self.assertEqual(get_category("Swiggy"), "Food")
        self.assertEqual(get_category("Zomato Delivery"), "Food")
        self.assertEqual(get_category("Canteen Snacks"), "Food")
        self.assertEqual(get_category("Tea Stall"), "Food")

    def test_travel_categorization(self):
        self.assertEqual(get_category("Uber Ride"), "Travel")
        self.assertEqual(get_category("Ola Mini"), "Travel")
        self.assertEqual(get_category("Petrol Pump HPCL"), "Travel")
        self.assertEqual(get_category("Rapido Bike Taxi"), "Travel")
        self.assertEqual(get_category("Metro Card Recharge"), "Travel")

    def test_shopping_categorization(self):
        self.assertEqual(get_category("DMart Supermarket"), "Shopping")
        self.assertEqual(get_category("Amazon Purchase"), "Shopping")
        self.assertEqual(get_category("Flipkart Order"), "Shopping")
        self.assertEqual(get_category("Myntra Fashion"), "Shopping")

    def test_bills_categorization(self):
        self.assertEqual(get_category("Bescom Electricity"), "Bills")
        self.assertEqual(get_category("Mobile Recharge Jio"), "Bills")
        self.assertEqual(get_category("Broadband Wifi Airtel"), "Bills")
        self.assertEqual(get_category("Water Bill Payment"), "Bills")

    def test_health_categorization(self):
        self.assertEqual(get_category("Pharmacy Medical Store"), "Health")
        self.assertEqual(get_category("Gym Membership"), "Health")

    def test_fallback_category(self):
        self.assertEqual(get_category("Unknown Mystery Merchant"), "Other")
        self.assertEqual(get_category(""), "Other")


class TestExpenseTrackerService(unittest.TestCase):
    """Tests for ExpenseTrackerService parser and analytics calculator."""

    def setUp(self):
        self.service = ExpenseTrackerService(default_budget=10000.0)

    def test_parse_valid_and_invalid_lines(self):
        sample_lines = [
            "2026-08-01, Swiggy, 350",
            "2026-08-02, Uber Ride, 180",
            "2026-08-09, Invalid Line Without Comma",
            "2026-08-10, Tea Stall, 40",
            "2026-08-11, Invalid Amount, abc",
            "   ",  # empty line should be ignored cleanly
        ]

        txns, errors = self.service.parse_lines(sample_lines)

        self.assertEqual(len(txns), 3)
        self.assertEqual(len(errors), 2)

        self.assertEqual(txns[0].merchant, "Swiggy")
        self.assertEqual(txns[0].amount, 350.0)
        self.assertEqual(txns[0].category, "Food")
        self.assertEqual(txns[0].raw_line_number, 1)

        self.assertEqual(errors[0].line_number, 3)
        self.assertIn("Malformed format", errors[0].reason)

        self.assertEqual(errors[1].line_number, 5)
        self.assertIn("Invalid numeric amount", errors[1].reason)

    def test_summary_calculation(self):
        txns = [
            Transaction(id="1", date="2026-08-01", merchant="Swiggy", amount=2480.0, category="Food", raw_line_number=1),
            Transaction(id="2", date="2026-08-02", merchant="Uber", amount=2320.0, category="Travel", raw_line_number=2),
            Transaction(id="3", date="2026-08-03", merchant="DMart", amount=5498.0, category="Shopping", raw_line_number=3),
            Transaction(id="4", date="2026-08-04", merchant="Bescom", amount=3608.0, category="Bills", raw_line_number=4),
            Transaction(id="5", date="2026-08-05", merchant="Gym", amount=1440.0, category="Health", raw_line_number=5),
        ]

        summary = self.service.calculate_summary(txns, budget_limit=10000.0)

        self.assertEqual(summary.total_spent, 15346.0)
        self.assertTrue(summary.is_over_budget)
        self.assertEqual(summary.over_budget_amount, 5346.0)
        self.assertEqual(summary.remaining_budget, 0.0)
        self.assertEqual(summary.top_category, "Shopping")
        self.assertEqual(summary.category_total["Shopping"], 5498.0)
        self.assertEqual(summary.category_total["Food"], 2480.0)
        self.assertEqual(len(summary.daily_trend), 5)


class TestExportService(unittest.TestCase):
    """Tests for ExportService output generation."""

    def test_export_csv_and_json(self):
        service = ExpenseTrackerService(default_budget=10000.0)
        txns = [
            Transaction(id="1", date="2026-08-01", merchant="Swiggy", amount=350.0, category="Food", raw_line_number=1),
            Transaction(id="2", date="2026-08-02", merchant="Uber Ride", amount=180.0, category="Travel", raw_line_number=2),
        ]
        summary = service.calculate_summary(txns, budget_limit=10000.0)
        payload = {
            "summary": summary.to_dict(),
            "transactions": [t.to_dict() for t in txns],
            "errors": [],
        }

        with tempfile.TemporaryDirectory() as temp_dir:
            csv_path = Path(temp_dir) / "report.csv"
            json_path = Path(temp_dir) / "report.json"
            html_path = Path(temp_dir) / "report.html"

            ExportService.export_csv(payload, csv_path)
            ExportService.export_json(payload, json_path)
            ExportService.export_html_report(payload, html_path)

            self.assertTrue(csv_path.exists())
            self.assertTrue(json_path.exists())
            self.assertTrue(html_path.exists())

            # Verify CSV content
            with open(csv_path, "r", encoding="utf-8") as f:
                reader = list(csv.reader(f))
                self.assertEqual(len(reader), 3)  # Header + 2 rows
                self.assertEqual(reader[1][2], "Swiggy")

            # Verify JSON content
            with open(json_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                self.assertEqual(data["summary"]["total_spent"], 530.0)


if __name__ == "__main__":
    unittest.main()
