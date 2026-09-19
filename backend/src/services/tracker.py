"""Core expense tracking and analytics aggregation service."""

import uuid
from typing import List, Tuple, Dict, Any, Union
from pathlib import Path

from backend.src.models.expense import (
    Transaction,
    ParsingError,
    ExpenseSummary,
    DashboardPayload,
)
from backend.src.services.categorizer import get_category
from backend.src.utils.file_handler import read_text_file
from backend.src.config.settings import DEFAULT_BUDGET_LIMIT, DEFAULT_DATA_FILE


class ExpenseTrackerService:
    """Service for parsing transactions, aggregating financial metrics, and managing budget limits."""

    def __init__(self, default_budget: float = DEFAULT_BUDGET_LIMIT):
        self.budget_limit = float(default_budget)

    def parse_lines(self, lines: List[str]) -> Tuple[List[Transaction], List[ParsingError]]:
        """Parses an iterable of raw text lines into Transactions and ParsingErrors."""
        transactions: List[Transaction] = []
        errors: List[ParsingError] = []

        for line_num, raw_line in enumerate(lines, start=1):
            stripped = raw_line.strip()
            if not stripped or stripped.startswith("#"):
                continue

            parts = [p.strip() for p in stripped.split(",")]
            if len(parts) < 3:
                errors.append(
                    ParsingError(
                        line_number=line_num,
                        raw_line=stripped,
                        reason="Malformed format: Expected 'YYYY-MM-DD, Merchant, Amount'",
                    )
                )
                continue

            date_str = parts[0]
            merchant_str = parts[1]
            amount_str = parts[2]

            if not merchant_str:
                errors.append(
                    ParsingError(
                        line_number=line_num,
                        raw_line=stripped,
                        reason="Merchant name is empty",
                    )
                )
                continue

            try:
                # Clean currency symbols or spaces if present in amount
                cleaned_amount = amount_str.replace("₹", "").replace("$", "").replace(",", "").strip()
                amount = float(cleaned_amount)
                if amount < 0:
                    errors.append(
                        ParsingError(
                            line_number=line_num,
                            raw_line=stripped,
                            reason="Negative transaction amounts are invalid",
                        )
                    )
                    continue
            except ValueError:
                errors.append(
                    ParsingError(
                        line_number=line_num,
                        raw_line=stripped,
                        reason=f"Invalid numeric amount '{amount_str}'",
                    )
                )
                continue

            category = get_category(merchant_str)
            txn_id = f"txn_{line_num}_{uuid.uuid4().hex[:6]}"

            transactions.append(
                Transaction(
                    id=txn_id,
                    date=date_str,
                    merchant=merchant_str,
                    amount=round(amount, 2),
                    category=category,
                    raw_line_number=line_num,
                )
            )

        return transactions, errors

    def parse_file(self, file_path: Union[str, Path]) -> Tuple[List[Transaction], List[ParsingError]]:
        """Reads and parses a text file from disk."""
        lines = read_text_file(file_path)
        return self.parse_lines(lines)

    def parse_raw_text(self, text: str) -> Tuple[List[Transaction], List[ParsingError]]:
        """Parses a multi-line raw string from the frontend or clipboard."""
        lines = text.splitlines()
        return self.parse_lines(lines)

    def calculate_summary(
        self, transactions: List[Transaction], budget_limit: float = None
    ) -> ExpenseSummary:
        """Calculates rich aggregations, category breakdowns, daily trends, and budget metrics."""
        limit = float(budget_limit) if budget_limit is not None else self.budget_limit
        total_spent = sum(t.amount for t in transactions)
        count = len(transactions)
        avg_spend = (total_spent / count) if count > 0 else 0.0

        # Category totals
        category_totals: Dict[str, float] = {}
        for t in transactions:
            category_totals[t.category] = category_totals.get(t.category, 0.0) + t.amount

        # Sort categories by total spend descending
        sorted_categories = dict(
            sorted(category_totals.items(), key=lambda item: item[1], reverse=True)
        )

        # Percentages
        category_percentages: Dict[str, float] = {}
        for cat, amt in sorted_categories.items():
            pct = (amt / total_spent * 100.0) if total_spent > 0 else 0.0
            category_percentages[cat] = round(pct, 1)

        # Daily Trend aggregation
        daily_map: Dict[str, Dict[str, Any]] = {}
        for t in transactions:
            if t.date not in daily_map:
                daily_map[t.date] = {"date": t.date, "amount": 0.0, "count": 0}
            daily_map[t.date]["amount"] += t.amount
            daily_map[t.date]["count"] += 1

        # Sort trend by date
        daily_trend = [
            {"date": d, "amount": round(info["amount"], 2), "count": info["count"]}
            for d, info in sorted(daily_map.items(), key=lambda x: x[0])
        ]

        top_category = next(iter(sorted_categories.keys())) if sorted_categories else "None"
        is_over = total_spent > limit
        over_amount = max(0.0, total_spent - limit)
        remaining = max(0.0, limit - total_spent)

        return ExpenseSummary(
            total_spent=round(total_spent, 2),
            budget_limit=round(limit, 2),
            is_over_budget=is_over,
            over_budget_amount=round(over_amount, 2),
            remaining_budget=round(remaining, 2),
            category_total={k: round(v, 2) for k, v in sorted_categories.items()},
            category_percentages=category_percentages,
            daily_trend=daily_trend,
            transaction_count=count,
            average_transaction=round(avg_spend, 2),
            top_category=top_category,
        )

    def process_file_or_default(
        self, file_path: Union[str, Path] = None, budget_limit: float = None
    ) -> DashboardPayload:
        """High-level orchestration method to process a file and generate the complete UI payload."""
        path = file_path or DEFAULT_DATA_FILE
        transactions, errors = self.parse_file(path)
        summary = self.calculate_summary(transactions, budget_limit=budget_limit)
        return DashboardPayload(summary=summary, transactions=transactions, errors=errors)

    def process_raw_content(
        self, content: str, budget_limit: float = None
    ) -> DashboardPayload:
        """High-level orchestration method to process uploaded/pasted text content."""
        transactions, errors = self.parse_raw_text(content)
        summary = self.calculate_summary(transactions, budget_limit=budget_limit)
        return DashboardPayload(summary=summary, transactions=transactions, errors=errors)
