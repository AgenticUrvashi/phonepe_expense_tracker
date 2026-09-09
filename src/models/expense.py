'''
Data models for expense tracking
'''
from dataclasses import dataclass

@dataclass
class Transaction:
    date: str
    merachant: str
    amount: float
    category: str = "Uncategorised"

@dataclass
class ExpenseSummary:
    total_spent: float
    category_total:dict[str, float]
    is_over_budget:bool


# if __name__ == "__main__":
#     print(Transaction(date="2026-01-01",merachant="Amazon", amount=100.00, category="shopping"))
#     print(ExpenseSummary(total_spent=100.00, category_total={"shopping": 100.00}, is_over_budget=False))
