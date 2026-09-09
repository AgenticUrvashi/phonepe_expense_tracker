from src.utils.logger import setup_logger
from src.services.tracker import ExpenseTrackerService
from src.config.setting import BUDGET_LIMIT

def main():
    logger = setup_logger()
    logger.info("initializing Phonepe Expense Tracker....")

    service = ExpenseTrackerService()

    summary = service.generate_summary()

    service.save_summary(summary)

    print("\n" + "="*50)
    print("📑 PHONEPE EXPENSE ANALYASIS REPORT 📑")
    print("="*50 + "\n")
    print(f"Total Spent: ")
    print(f"Total Money Spend: {summary.total_spent:.2f}")
    print(f"\nSpending Breakdown by Category")

    for category, amount in summary.category_total.items():
        print(f"     {category:12s}: ₹{amount:.2f}")

    print("-"*50)

    if summary.is_over_budget:
        print(f"\n⚠ WARNING: You have exceeded your monthly budget limit of ₹{BUDGET_LIMIT} ⚠")

    else:
        print(f"\n Congratulation you are within your budget limit of ₹{BUDGET_LIMIT}")

    print("="*50 + "\n")

if __name__ == "__main__":
    main()