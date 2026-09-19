"""Domain models for PhonePe Expense Tracker."""

from dataclasses import dataclass, field, asdict
from typing import Dict, List, Any


@dataclass
class Transaction:
    """Represents a single parsed transaction record."""
    id: str
    date: str
    merchant: str
    amount: float
    category: str
    raw_line_number: int

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class ParsingError:
    """Represents a malformed or skipped line during file parsing."""
    line_number: int
    raw_line: str
    reason: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class ExpenseSummary:
    """Aggregated analytics summary for the expense report."""
    total_spent: float
    budget_limit: float
    is_over_budget: bool
    over_budget_amount: float
    remaining_budget: float
    category_total: Dict[str, float]
    category_percentages: Dict[str, float]
    daily_trend: List[Dict[str, Any]]
    transaction_count: int
    average_transaction: float
    top_category: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class DashboardPayload:
    """Full data payload delivered to the frontend UI."""
    summary: ExpenseSummary
    transactions: List[Transaction]
    errors: List[ParsingError]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "summary": self.summary.to_dict(),
            "transactions": [t.to_dict() for t in self.transactions],
            "errors": [e.to_dict() for e in self.errors],
        }
