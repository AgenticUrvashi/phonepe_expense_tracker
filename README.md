# 🟣 PhonePe Expense Intelligence — Desktop Application

An industry-grade, high-performance desktop application for analyzing **PhonePe** expense statements with interactive charts, monthly budget tracking, smart insights, and detailed transaction ledger explorer.

Built with **PyWebView + React 18 + Vite + Tailwind CSS + Recharts**.

---

## 🌟 Key Features

* **Drag-and-Drop Statement Upload**: Drop your `transaction.txt` or CSV statement directly into the application window for instant parsing.
* **Smart Merchant Categorizer**: Automatically identifies and categorizes transactions into **Food, Travel, Shopping, Bills, Health, and Other**.
* **Real-time Budget Velocity & Overrun Alerts**: Visual radial gauge and alert banners when monthly budget thresholds are exceeded.
* **Interactive Data Visualizations**:
  * **Category Breakdown Donut Chart**: Hover tooltips, percentage indicators, and center spend summary.
  * **Daily Velocity Timeline Bar Chart**: Day-by-day expenditure trends with peak day detection.
* **Searchable & Sortable Ledger**: Filter transactions by category, search by merchant/date, and sort columns with pagination.
* **Native Desktop Capabilities**:
  * Native Windows File Explorer open/save dialogs.
  * Standalone executable (`.exe`) packaging via Edge WebView2.
  * Export analysis reports to **CSV** or **JSON**.
  * Dynamic budget configuration modal with JSON persistence.

---

## 🏗️ Architecture & Project Structure

```
phonepe_expense_tracker/
│
├── backend/                       # 🐍 Python Desktop Core & Business Logic
│   ├── app/
│   │   ├── api/
│   │   │   └── bridge.py          # PyWebView IPC API (Exposed to JavaScript)
│   │   ├── config/
│   │   │   └── settings.py        # Budget limits, app constants, paths
│   │   ├── models/
│   │   │   └── expense.py         # Transaction & ExpenseSummary data models
│   │   ├── services/
│   │   │   ├── categorizer.py     # Smart merchant categorization
│   │   │   ├── parser.py          # Resilient statement parser (.txt/.csv)
│   │   │   ├── tracker.py         # Expense analytics & insight engine
│   │   │   └── file_service.py    # CSV/JSON export engine
│   │   └── utils/
│   │       └── logger.py          # Structured logging
│   ├── tests/
│   │   └── test_tracker.py        # Pytest backend test suite
│   ├── desktop_main.py            # Desktop app window launcher
│   └── requirements.txt           # Python dependencies (pywebview, pytest)
│
├── frontend/                      # ⚛️ Modern React Desktop UI
│   ├── src/
│   │   ├── components/
│   │   │   ├── layout/            # Header, Branding & Action controls
│   │   │   ├── upload/            # Drag & drop FileDropzone
│   │   │   ├── analytics/         # MetricCards, BudgetGauge, CategoryDonut, SpendingTrends, InsightsCard
│   │   │   ├── transactions/      # Searchable & Sortable TransactionTable
│   │   │   └── common/            # BudgetModal dialog
│   │   ├── services/
│   │   │   └── api.ts             # Strongly-typed PyWebView bridge client
│   │   ├── types/
│   │   │   └── index.ts           # Shared TypeScript models
│   │   ├── styles/
│   │   │   └── index.css          # Tailwind CSS & glassmorphism theme
│   │   ├── App.tsx
│   │   └── main.tsx
│   ├── package.json
│   ├── tsconfig.json
│   └── vite.config.ts             # Builds production bundle directly to backend/app/dist
│
├── data/
│   ├── transactions.txt           # Sample statement
│   └── user_config.json           # User budget & preferences
├── logs/                          # App log output
├── build_desktop.py               # 1-Click build & desktop runner script
└── main.py                        # Original CLI runner (100% backward compatible)
```

---

## 🚀 Getting Started

### 1. Prerequisites
* **Python**: Python 3.10+ (with `uv` or standard `pip`)
* **Node.js**: Node 18+ and `npm`

### 2. Install Dependencies
```bash
# Install Python dependencies
uv pip install -r backend/requirements.txt

# Install Frontend dependencies
cd frontend
npm install
cd ..
```

### 3. Build & Run Desktop App (1-Click)
```bash
python build_desktop.py
```

### 4. Package as Standalone Single Executable (.exe)
To package into a single portable `.exe` file (~12.5 MB) that can be shared with anyone:
```bash
python build_desktop.py --package
```
The resulting executable will be saved in:
`dist/PhonePeExpenseTracker.exe`

### 5. Run in Development Mode (Live Hot Reloading)
```bash
# In Terminal 1 (Frontend):
cd frontend
npm run dev

# In Terminal 2 (Desktop App):
python build_desktop.py --dev
```

### 6. Run Original CLI Mode
```bash
python main.py
```

---

## 🧪 Testing

Run backend tests:
```bash
.\.venv\Scripts\pytest backend/tests/
```

Run frontend type check & production build:
```bash
cd frontend
npm run build
```