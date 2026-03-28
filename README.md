# Personal Finance Manager CLI

A clean, modular, production-ready CLI application for personal finance management built with Python 3.10+.

## Features

- **Add Transactions**: Record income and expenses with categories, amounts, and notes
- **View Summary**: Display total income, expenses, and current balance
- **Category Reports**: Analyze spending by category with percentages
- **Monthly Reports**: View income and expenses grouped by month
- **Chart Visualization**: Interactive charts for monthly/yearly trends, expense distribution, and budget status
- **Budget Management**: Set budgets per category and track spending against budgets
- **Flexible Storage**: SQLite (default) or CSV backend
- **Logging**: Comprehensive application logging
- **Cancel Operation**: Type 'batal', 'cancel', or 'x' to cancel any input

## Installation

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

## Usage

```bash
python main.py
```

## Project Structure

```
PERSONAL_FINANCE_MANAGER/
├── main.py                      # CLI entry point
├── services/
│   ├── transaction_service.py   # Transaction operations
│   ├── report_service.py        # Report generation
│   └── budget_service.py        # Budget management
├── models/
│   └── transaction.py           # Transaction dataclass
├── storage/
│   └── csv_storage.py           # CSV file operations
├── utils/
│   ├── validator.py             # Input validation
│   ├── formatter.py             # Output formatting
│   └── visualizer.py            # Chart visualization
├── finance_data.csv             # Transaction storage
├── budget.csv                   # Budget storage
└── finance_manager.log          # Application logs
```

## Data Files

- **finance_data.csv**: Stores all transactions (id, date, type, category, amount, note)
- **budget.csv**: Stores monthly budgets per category

## Architecture

### Modular Design
- **Services**: Business logic (transactions, reports, budgets)
- **Models**: Data structures (Transaction dataclass)
- **Storage**: Flexible backend (SQLite/CSV) with `StorageFactory`
- **Utils**: Helper functions (validation, formatting, visualization)

### Clean Code Principles
- Separation of concerns
- Type hints throughout
- Comprehensive logging
- No global variables
- Error handling and validation
- Docstrings for all functions

## 🗄️ Database

Choose between two storage backends:

### SQLite (Default - Recommended)
- Fast and reliable
- Built-in Python support
- ACID compliant
- Single file: `finance_data.db`
- Perfect for production use

### CSV (Alternative)
- Human-readable
- Easy to export to Excel
- Good for simple use cases
- Files: `finance_data.csv`, `budget.csv`

**Select backend when starting the app!**

For detailed documentation:
- 📖 [DATABASE.md](DATABASE.md) - Schema, queries, backup/restore
- 🔄 [MIGRATION.md](MIGRATION.md) - CSV to SQLite migration guide

## Extension Points

The architecture supports future enhancements:
- **Additional Backends**: PostgreSQL, MySQL, MongoDB via StorageFactory
- **REST API**: Add FastAPI/Flask layer on top of services
- **GUI**: Add Tkinter/PyQt interface using existing services
- **AI Analysis**: Add prediction models using existing transaction data
- **Advanced Visualizations**: Extend `visualizer.py` with Plotly, Seaborn, or Dash
- **Export**:PDF/Excel reports, Email notifications

## Example CLI Flow

```
MANAJER KEUANGAN PRIBADI
1. Tambah Transaksi
2. Lihat Ringkasan
3. Laporan Kategori
4. Laporan Bulanan
5. Grafik Laporan
6. Kelola Anggaran
7. Keluar

> 5
--- GRAFIK LAPORAN ---
1. Grafik Laporan Bulanan
2. Grafik Laporan Tahunan
3. Grafik Distribusi Pengeluaran
4. Grafik Status Anggaran
5. Kembali ke Menu Utama

> 1
📊 Membuka grafik laporan bulanan...
[Interactive chart opens with matplotlib]
```

## Notes

- Use YYYY-MM-DD format for dates
- All amounts must be positive numbers
- Categories are case-sensitive
- Budgets are monthly and per-category
- All logs are saved to `finance_manager.log`
