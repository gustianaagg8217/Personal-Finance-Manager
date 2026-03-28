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
- **Telegram Bot**: Manage finances remotely via Telegram with real-time sync
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
├── run_telegram_bot.py          # Telegram bot launcher
├── telegram_bot.py              # Telegram bot implementation
├── services/
│   ├── transaction_service.py   # Transaction operations
│   ├── report_service.py        # Report generation
│   └── budget_service.py        # Budget management
├── models/
│   └── transaction.py           # Transaction dataclass
├── storage/
│   ├── sqlite_storage.py        # SQLite database operations
│   ├── csv_storage.py           # CSV file operations
│   ├── storage_factory.py       # Storage backend factory
├── utils/
│   ├── validator.py             # Input validation
│   ├── formatter.py             # Output formatting
│   └── visualizer.py            # Chart visualization
├── finance_data.db              # SQLite database (default)
├── finance_data.csv             # CSV transaction storage (alternative)
├── budget.csv                   # CSV budget storage (alternative)
├── telegram_bot.log             # Telegram bot logs
├── finance_manager.log          # CLI application logs
├── requirements.txt             # Python dependencies
├── README.md                    # This file
├── TELEGRAM_BOT.md              # Telegram bot setup guide
├── DATABASE.md                  # Database documentation
└── MIGRATION.md                 # CSV to SQLite migration guide
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

SQLite is the **default and recommended** database backend.

### SQLite (Default)
✅ Fast and reliable  
✅ Built-in Python support  
✅ ACID compliant  
✅ Single file: `finance_data.db`  
✅ Perfect for production use  

### CSV (Alternative)
If you prefer CSV, change backend in Settings menu:
- Main Menu → 7. Pengaturan → 1. Ganti Backend Database → 2. CSV

- Human-readable format
- Excel compatible
- Good for simple use cases
- Files: `finance_data.csv`, `budget.csv`

For detailed database documentation, see [DATABASE.md](DATABASE.md)

## 📱 Telegram Bot (Multi-Platform Access)

Manage your finances directly from Telegram with **real-time sync** to the same SQLite database!

### Quick Start

1. **Get Telegram Bot Token**:
   - Chat with [@BotFather](https://t.me/botfather) on Telegram
   - Send `/newbot` and follow instructions
   - Copy the token

2. **Set Environment Variable**:
   ```bash
   # Windows PowerShell
   $env:TELEGRAM_BOT_TOKEN = "your_token_here"
   
   # Windows CMD
   set TELEGRAM_BOT_TOKEN=your_token_here
   
   # Linux/Mac
   export TELEGRAM_BOT_TOKEN=your_token_here
   ```

3. **Run Telegram Bot**:
   ```bash
   python run_telegram_bot.py
   ```

4. **Start Using in Telegram**:
   - Find your bot on Telegram
   - Send `/start`
   - Use commands: `/add_transaction`, `/summary`, `/category_report`, `/monthly_report`, `/set_budget`, `/budget_status`

### Bot Features
- ✅ Add transactions with inline buttons
- ✅ View financial summary
- ✅ Show category-wise expenses
- ✅ Monthly reports (last 6 months)
- ✅ Set and track budgets
- ✅ **Shared Database**: CLI and Telegram bot sync in real-time

### Database Sync
- Both CLI and Telegram bot use **same SQLite database** (`finance_data.db`)
- Changes in one interface appear instantly in the other
- No configuration needed—just run both simultaneously!

For detailed Telegram setup and usage, see [TELEGRAM_BOT.md](TELEGRAM_BOT.md)

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
🚀 Manajer Keuangan Pribadi Dimulai
📊 Backend: SQLite (Default)

MANAJER KEUANGAN PRIBADI
1. Tambah Transaksi
2. Lihat Ringkasan
3. Laporan Kategori
4. Laporan Bulanan
5. Grafik Laporan
6. Kelola Anggaran
7. Pengaturan
8. Keluar

> 1
--- TAMBAH TRANSAKSI ---
Jenis transaksi (income/expense): expense
Kategori: groceries
Jumlah: 150000
Catatan (opsional): Weekly shopping

✅ Transaksi berhasil ditambahkan!

> 7
--- PENGATURAN ---
Backend Database Saat Ini: SQLITE
1. Ganti Backend Database
2. Informasi Database
3. Kembali ke Menu Utama

> 2
--- INFORMASI DATABASE ---
Backend: SQLITE
File: finance_data.db
Total Transaksi: 15
Budgets: 3

Keuntungan SQLite:
  • 5x lebih cepat dari CSV
  • ACID compliant
  • Efisien untuk dataset besar
  • Backup mudah (copy file)
```

## Notes

- Use YYYY-MM-DD format for dates
- All amounts must be positive numbers
- Categories are case-sensitive
- Budgets are monthly and per-category
- All logs are saved to `finance_manager.log`
