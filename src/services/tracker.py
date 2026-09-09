import logging
from dataclasses import asdict
from src.models.expense import Transaction, ExpenseSummary
from src.services.categorizar import get_category
from src.utils.file_handler import read_text_file, write_json_file
from src.utils.decorators import timer
from src.config.setting import BUDGET_LIMIT, DATA_FILE_PATH, OUTPUT_JSON_PATH

logger = logging.getLogger("PhonePeTracer")

class ExpenseTrackerService:
    def __init__(self,data_path=DATA_FILE_PATH, budget_limit=BUDGET_LIMIT) -> None:
        self.data_path = data_path
        self.budget_limit = budget_limit

    @timer
    def parse_tranasaction(self) -> list[Transaction]:
        """ Parse the transaction data from the text file. """
        raw_lines = read_text_file(self.data_path)
        transactions: list[Transaction] = []

        for line_numer, line in enumerate(raw_lines):
            line_str = line.strip()

            if not line_str:
                continue

            try:
                date,merchant,amount_str = line_str.split(",")
                amount = float(amount_str)
                category = get_category(merchant)

                transactions.append(Transaction(date.strip(), merchant.strip(), amount, category))
                
            except Exception as e:
                logger.error(f"Skipped  {line_numer} transaction due to error: {e}")
 
        return transactions

    def generate_summary(self) -> ExpenseSummary:
        transactions: list[Transaction] = self.parse_tranasaction()
        totals: dict[str, float] = {}
        total_spent:float = 0.0

        for txn in transactions:
            totals[txn.category] = (totals.get(txn.category, 0.0) + txn.amount)
            total_spent += txn.amount

        return ExpenseSummary(
            total_spent=round(total_spent,2), 
            category_total={k: round(v,2) for k,v in totals.items()},
            is_over_budget = total_spent > self.budget_limit)

    def save_summary(self,summary, output_path = OUTPUT_JSON_PATH) -> None:
        """ Save the summary to a JSON file. """
        write_json_file(asdict(summary), output_path)

