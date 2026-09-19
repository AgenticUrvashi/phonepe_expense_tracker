"""PhonePe Expense Tracker Main Launcher.

Supports both Desktop UI Application mode (default) and CLI mode.
"""

import sys
import argparse
from pathlib import Path

# Ensure UTF-8 output on Windows consoles
if sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from backend.src.services.tracker import ExpenseTrackerService
from backend.src.config.settings import DEFAULT_BUDGET_LIMIT, DEFAULT_DATA_FILE
from backend.src.utils.logger import setup_logger

logger = setup_logger("Main")


def run_cli_report(file_path: str = None, budget: float = DEFAULT_BUDGET_LIMIT):
    """Executes the CLI analytical report."""
    service = ExpenseTrackerService(default_budget=budget)
    target = file_path or DEFAULT_DATA_FILE

    payload = service.process_file_or_default(target, budget_limit=budget)
    summary = payload.summary

    print("\n" + "=" * 55)
    print(" 📊 PHONEPE EXPENSE ANALYSIS REPORT 📊")
    print("    Built with pride by Indian AI Production")
    print("=" * 55)
    print(f"\nTotal Money Spent: ₹{summary.total_spent:.2f}")
    print(f"Total Transactions: {summary.transaction_count} | Average: ₹{summary.average_transaction:.2f}")
    print("\nSpending Breakdown by Category:")
    for category, amount in summary.category_total.items():
        pct = summary.category_percentages.get(category, 0)
        print(f"     {category:14s}: ₹{amount:>8.2f}  ({pct:>4.1f}%)")
    print("-" * 55)

    if summary.is_over_budget:
        print(f"⚠️ WARNING: You have exceeded your monthly budget limit of ₹{summary.budget_limit:.1f}")
        print(f"   Over Budget by: ₹{summary.over_budget_amount:.2f}")
    else:
        print(f"✅ CONGRATULATIONS: You are within your monthly budget limit of ₹{summary.budget_limit:.1f}")
        print(f"   Remaining Budget: ₹{summary.remaining_budget:.2f}")

    if payload.errors:
        print(f"\n⚠️ Notice: Skipped {len(payload.errors)} malformed lines during parsing.")

    print("=" * 55)
    print(" © 2026 Indian AI Production. All rights reserved.")
    print("=" * 55 + "\n")


def main():
    parser = argparse.ArgumentParser(description="PhonePe Expense Tracker")
    parser.add_argument("--cli", action="store_true", help="Run in CLI mode instead of Desktop UI")
    parser.add_argument("--file", type=str, default=None, help="Custom transactions text file path")
    parser.add_argument("--budget", type=float, default=DEFAULT_BUDGET_LIMIT, help="Custom budget limit (INR)")

    args = parser.parse_args()

    if args.cli:
        run_cli_report(file_path=args.file, budget=args.budget)
    else:
        # Launch Desktop UI
        from backend.app import main as launch_desktop
        launch_desktop()


if __name__ == "__main__":
    main()