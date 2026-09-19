"""Export utilities for PhonePe Expense Tracker reports (CSV, JSON, HTML)."""

import csv
import json
from pathlib import Path
from typing import Dict, Any, List

from backend.src.models.expense import DashboardPayload


class ExportService:
    """Service to export analyzed expense reports in multiple formats."""

    @staticmethod
    def export_csv(payload: Dict[str, Any], output_path: Path) -> str:
        """Exports parsed transactions to a CSV file."""
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        transactions: List[Dict[str, Any]] = payload.get("transactions", [])
        
        with open(output_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["Line Number", "Date", "Merchant", "Category", "Amount (INR)"])
            for t in transactions:
                writer.writerow([
                    t.get("raw_line_number"),
                    t.get("date"),
                    t.get("merchant"),
                    t.get("category"),
                    f"{t.get('amount', 0.0):.2f}"
                ])
        
        return str(output_path)

    @staticmethod
    def export_json(payload: Dict[str, Any], output_path: Path) -> str:
        """Exports the full analysis and raw transactions to a structured JSON file."""
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=4, ensure_ascii=False)

        return str(output_path)

    @staticmethod
    def export_html_report(payload: Dict[str, Any], output_path: Path) -> str:
        """Generates a standalone, beautifully styled HTML/PDF-printable report."""
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        summary = payload.get("summary", {})
        transactions = payload.get("transactions", [])
        categories = summary.get("category_total", {})

        cat_rows = "".join(
            f"<tr><td>{cat}</td><td style='text-align:right;'>₹{amt:,.2f}</td><td style='text-align:right;'>{summary.get('category_percentages', {}).get(cat, 0)}%</td></tr>"
            for cat, amt in categories.items()
        )

        txn_rows = "".join(
            f"<tr><td>#{t.get('raw_line_number')}</td><td>{t.get('date')}</td><td>{t.get('merchant')}</td><td><span class='badge'>{t.get('category')}</span></td><td style='text-align:right;'>₹{t.get('amount', 0.0):,.2f}</td></tr>"
            for t in transactions
        )

        status_class = "danger" if summary.get("is_over_budget") else "success"
        status_text = (
            f"⚠️ Budget Exceeded by ₹{summary.get('over_budget_amount', 0):,.2f}"
            if summary.get("is_over_budget")
            else f"✅ Within Budget (₹{summary.get('remaining_budget', 0):,.2f} remaining)"
        )

        html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>PhonePe Expense Analysis Report</title>
<style>
  body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #0f1016; color: #f1f2f6; padding: 30px; margin: 0; }}
  .container {{ max-width: 880px; margin: 0 auto; background: #181926; border-radius: 16px; padding: 30px; border: 1px solid #2e3048; }}
  .header {{ display: flex; justify-content: space-between; align-items: center; border-bottom: 2px solid #5f259f; padding-bottom: 20px; }}
  h1 {{ margin: 0; color: #a855f7; font-size: 24px; }}
  .status-badge {{ padding: 8px 16px; border-radius: 20px; font-weight: bold; font-size: 14px; }}
  .danger {{ background: rgba(239, 68, 68, 0.2); color: #f87171; border: 1px solid #ef4444; }}
  .success {{ background: rgba(34, 197, 94, 0.2); color: #4ade80; border: 1px solid #22c55e; }}
  .kpi-grid {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px; margin: 24px 0; }}
  .kpi-card {{ background: #222436; padding: 18px; border-radius: 12px; border: 1px solid #333652; }}
  .kpi-card h4 {{ margin: 0 0 6px 0; color: #94a3b8; font-size: 13px; text-transform: uppercase; }}
  .kpi-card .val {{ font-size: 22px; font-weight: bold; color: #fff; }}
  table {{ width: 100%; border-collapse: collapse; margin-top: 15px; font-size: 14px; }}
  th, td {{ padding: 10px 14px; border-bottom: 1px solid #2e3048; }}
  th {{ background: #222436; color: #94a3b8; text-align: left; }}
  .badge {{ background: #5f259f; color: #fff; padding: 3px 8px; border-radius: 6px; font-size: 12px; }}
</style>
</head>
<body>
<div class="container">
  <div class="header">
    <div>
      <h1>📊 PhonePe Expense Analysis Report</h1>
      <p style="color: #94a3b8; margin: 5px 0 0 0; font-size: 13px;">Generated on {summary.get('transaction_count', 0)} Transactions</p>
    </div>
    <div class="status-badge {status_class}">{status_text}</div>
  </div>

  <div class="kpi-grid">
    <div class="kpi-card"><h4>Total Spent</h4><div class="val">₹{summary.get('total_spent', 0):,.2f}</div></div>
    <div class="kpi-card"><h4>Monthly Budget</h4><div class="val">₹{summary.get('budget_limit', 0):,.2f}</div></div>
    <div class="kpi-card"><h4>Top Category</h4><div class="val">{summary.get('top_category', 'N/A')}</div></div>
  </div>

  <h3>Spending Breakdown by Category</h3>
  <table>
    <thead><tr><th>Category</th><th style="text-align:right;">Amount</th><th style="text-align:right;">Share (%)</th></tr></thead>
    <tbody>{cat_rows}</tbody>
  </table>

  <h3 style="margin-top: 30px;">Transaction Records</h3>
  <table>
    <thead><tr><th>#</th><th>Date</th><th>Merchant</th><th>Category</th><th style="text-align:right;">Amount</th></tr></thead>
    <tbody>{txn_rows}</tbody>
  </table>
</div>
</body>
</html>"""

        with open(output_path, "w", encoding="utf-8") as f:
            f.write(html_content)

        return str(output_path)
