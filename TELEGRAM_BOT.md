# Telegram Bot Setup & Usage Guide

## Overview

Personal Finance Manager now includes a Telegram bot that allows you to manage your finances directly from Telegram. The bot uses the **same SQLite database** as the CLI, so all updates sync automatically!

## ✨ Features

- ✅ Add transactions via Telegram
- ✅ View financial summary
- ✅ Category-wise expense reports
- ✅ Monthly reports
- ✅ Set and track budgets
- ✅ Real-time sync with CLI database
- ✅ User-friendly inline keyboards
- ✅ Command conversation flow

## 🚀 Quick Start

### Step 1: Create Telegram Bot

1. Open Telegram and search for **@BotFather**
2. Send `/newbot` command
3. Choose a name for your bot (e.g., "Finance Manager Bot")
4. Choose a username (e.g., @my_finance_manager_bot)
5. **Copy the token** (looks like: `123456789:ABCdefGHIjklmnoPQRstuvWXYZabcdefgh`)

### Step 2: Set Environment Variable

**Windows (PowerShell):**
```powershell
$env:TELEGRAM_BOT_TOKEN = "123456789:ABCdefGHIjklmnoPQRstuvWXYZabcdefgh"
```

**Windows (Command Prompt):**
```cmd
set TELEGRAM_BOT_TOKEN=123456789:ABCdefGHIjklmnoPQRstuvWXYZabcdefgh
```

**Linux/Mac:**
```bash
export TELEGRAM_BOT_TOKEN=123456789:ABCdefGHIjklmnoPQRstuvWXYZabcdefgh
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

or 

```bash
pip install python-telegram-bot
```

### Step 4: Run Telegram Bot

```bash
python run_telegram_bot.py
```

Output should show:
```
============================================================
TELEGRAM BOT - PERSONAL FINANCE MANAGER
============================================================

🤖 Memulai bot...

2026-03-28 10:30:45,123 - telegram.ext.Application - INFO - Application started
```

## 📱 Bot Commands

### /start
Start the bot and see welcome message

```
Halo! 👋
Selamat datang di Manajer Keuangan Pribadi Bot!

Gunakan perintah berikut:
/add_transaction - Tambah transaksi
/summary - Lihat ringkasan
...
```

### /help
Show help and available commands

### /add_transaction
Add income or expense transaction

**Interactive flow:**
```
1. Select type (Income/Expense) - Inline buttons
2. Enter category - Text input
3. Enter amount - Text input
4. Enter note (optional) - Text input
5. Transaction saved! ✅
```

**Example:**
```
Pilih jenis transaksi:
[💰 Income] [💸 Expense]

> (select Expense)

✅ Tipe: Expense

Sekarang ketik kategori:
(contoh: groceries, utilities, salary, bonus)

> groceries

✅ Kategori: groceries

Sekarang ketik jumlah:
(contoh: 50000)

> 150000

✅ Jumlah: Rp150,000

Ketik catatan (opsional):
(Atau tekan /skip untuk lewati)

> Weekly shopping

✅ Transaksi berhasil disimpan!

ID: 1
Jenis: Expense
Kategori: groceries
Jumlah: Rp150,000
Catatan: Weekly shopping
Tanggal: 2026-03-28
```

### /summary
View financial summary

```
📊 RINGKASAN KEUANGAN

💵 Pendapatan:   Rp5,000,000
💸 Pengeluaran:  Rp2,345,000
💰 Saldo:        Rp2,655,000
```

### /category_report
Show expenses breakdown by category

```
🏷️ PENGELUARAN BERDASARKAN KATEGORI

• groceries: Rp500,000 (21.3%)
• utilities: Rp300,000 (12.8%)
• transport: Rp250,000 (10.6%)
• entertainment: Rp400,000 (17.1%)

💹 Total: Rp2,345,000
```

### /monthly_report
Show last 6 months summary

```
📅 LAPORAN BULANAN

📆 2026-03
  💵 Pendapatan: Rp5,000,000
  💸 Pengeluaran: Rp2,345,000
  💰 Saldo: Rp2,655,000

📆 2026-02
  💵 Pendapatan: Rp4,800,000
  💸 Pengeluaran: Rp2,100,000
  💰 Saldo: Rp2,700,000

[... more months ...]
```

### /set_budget
Set monthly budget for category

**Interactive flow:**
```
1. Enter category name
2. Enter monthly budget amount
3. Budget saved! ✅
```

**Example:**
```
Ketik kategori untuk mengatur anggaran:
(contoh: groceries, utilities, entertainment)

> groceries

✅ Kategori: groceries

Sekarang ketik anggaran bulanan:
(contoh: 5000000)

> 2000000

✅ Anggaran berhasil diatur!

Kategori: groceries
Anggaran: Rp2,000,000 per bulan
```

### /budget_status
Show current month budget status

```
✅ STATUS ANGGARAN BULAN INI

📌 groceries
  🟢 OK
  Pengeluaran: Rp500,000
  Sisa: Rp1,500,000 [Budget: Rp2,000,000]

📌 utilities
  🔴 TERLAMPAUI
  Pengeluaran: Rp1,600,000
  Sisa: Rp-100,000 [Budget: Rp1,500,000]

📌 entertainment
  🟢 OK
  Pengeluaran: Rp300,000
  Sisa: Rp700,000 [Budget: Rp1,000,000]
```

### /cancel
Cancel current operation (also: type "batal")

## 🔄 Sync with CLI

The Telegram bot shares the same SQLite database with the CLI application!

### Example Flow:

**Terminal (CLI):**
```
$ python main.py
🚀 Manajer Keuangan Pribadi Dimulai
📊 Backend: SQLite (Default)

MANAJER KEUANGAN PRIBADI
1. Tambah Transaksi

> 1
--- TAMBAH TRANSAKSI ---
Jenis transaksi (income/expense): expense
Kategori: groceries
Jumlah: 100000
Catatan: Shopping
✅ Transaksi berhasil ditambahkan!
```

**Telegram (Bot):**
```
/summary

📊 RINGKASAN KEUANGAN

💵 Pendapatan:   Rp5,000,000
💸 Pengeluaran:  Rp2,445,000  ← Updated (added 100,000)
💰 Saldo:        Rp2,555,000
```

Changes are **instant and automatic** because both use the same database file!

## 🛠️ Running Both CLI and Bot

### Option 1: Separate Terminals

**Terminal 1 - CLI:**
```bash
python main.py
```

**Terminal 2 - Bot:**
```bash
python run_telegram_bot.py
```

Both will work simultaneously and share the same database!

### Option 2: Run Bot Only

If you prefer to manage finances entirely through Telegram:
```bash
python run_telegram_bot.py
```

All data is still persisted to `finance_data.db` (SQLite).

## 📋 User Input Rules

- **Cancel operations**: Type "batal", "cancel", or "x"
- **Skip optional field**: Type "/skip" or empty line
- **Amount format**: Enter numbers only (e.g., 150000)
- **Categories**: Any text (e.g., groceries, salary, bonus)

## 🔒 Security Notes

1. **Token Security**:
   - Never commit token to git
   - Use environment variables (shown above)
   - Rotate token if compromised

2. **Database Access**:
   - Only you can access your bot (Telegram handles permissions)
   - Database file is local to your machine
   - Backup `finance_data.db` regularly

3. **User Privacy**:
   - Your Telegram user ID is logged
   - No data sent to external services
   - All processing is local

## 📊 Database Sync Details

### How it Works

```
┌─────────────────┐
│   Your Telegram │
│    Messages     │
└────────┬────────┘
         │
┌────────▼────────┐
│  Telegram Bot   │
│  (telegram_bot  │
│      .py)       │
└────────┬────────┘
         │
┌────────▼────────────────┐
│  StorageFactory          │
│  (shared backend)        │
└────────┬─────────────────┘
         │
         │ Uses same
         │ StorageType
         │
┌────────▼────────────────┐
│  SQLite Database         │
│  (finance_data.db)       │
└──────────────────────────┘
         ▲
         │
┌────────┴────────┐
│   CLI (main.py) │
└─────────────────┘
```

### Real-time Updates

1. Bot adds transaction via Telegram
2. Saved to `finance_data.db` immediately
3. CLI reads from same database
4. Data always consistent

## 🐛 Troubleshooting

### Bot doesn't respond

**Problem**: No response to commands

**Solutions**:
```bash
# 1. Check token is set
echo %TELEGRAM_BOT_TOKEN%  # Windows
echo $TELEGRAM_BOT_TOKEN   # Linux/Mac

# 2. Verify token is valid (check @BotFather)

# 3. Check logs
tail -f telegram_bot.log

# 4. Restart bot
python run_telegram_bot.py
```

### Database locked error

**Problem**: "database is locked" when accessing CLI and Bot simultaneously

**Solution**:
- SQLite locks are brief (usually <1 second)
- This is normal behavior
- If frequent, consider adding retry logic

### Token format error

**Problem**: "Invalid token"

**Solution**:
```bash
# Token should look like:
# 123456789:ABCdefGHIjklmnoPQRstuvWXYZabcdefgh
#
# Common mistakes:
# ❌ "https://t.me/bot123..." <- Wrong (this is webhook URL)
# ✅ "123456789:ABC..." <- Correct (from @BotFather)
```

### Timeout errors

**Problem**: "Request timed out"

**Solutions**:
- Check internet connection
- Verify Telegram API is accessible
- Restart bot: `python run_telegram_bot.py`

## 📚 Advanced Usage

### Automated Data Entry

Create a script to batch add transactions:

```python
from telegram_bot import FinanceBot
import asyncio
import os

async def batch_add():
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    bot = FinanceBot(token)
    
    # Directly use services
    bot.transaction_service.add_transaction("expense", "groceries", 50000)
    bot.transaction_service.add_transaction("expense", "utilities", 300000)
    bot.transaction_service.add_transaction("income", "salary", 5000000)
    
    print("✅ Batch transactions added")

asyncio.run(batch_add())
```

### Multiple Users

Each Telegram user has their own user ID, but they all access the **same database**. This is useful for:
- Family budget tracking
- Team expense management
- Shared finance monitoring

To restrict to specific users, add a user whitelist:

```python
ALLOWED_USERS = [123456789, 987654321]  # Your Telegram user IDs

async def start(self, update, context):
    if update.effective_user.id not in ALLOWED_USERS:
        await update.message.reply_text("❌ Not authorized")
        return
    # ... continue
```

### Scheduled Reports

Send daily/weekly reports:

```python
from telegram.ext import Application
from datetime import time

async def send_summary(context):
    chat_id = YOUR_CHAT_ID
    # Get summary
    summary = self.report_service.generate_summary_report()
    # Send to Telegram
    await context.bot.send_message(chat_id, summary)

# Add to application
job_queue = app.job_queue
job_queue.run_daily(send_summary, time=datetime.time(hour=20))
```

## 📖 Documentation

- 🏗️ [ARCHITECTURE.md](ARCHITECTURE.md) - Overall design
- 🗄️ [DATABASE.md](DATABASE.md) - Database details
- 🔄 [MIGRATION.md](MIGRATION.md) - CSV to SQLite migration
- 📋 [README.md](README.md) - Main documentation

## 🤝 Support

For issues:
1. Check logs: `tail -f telegram_bot.log`
2. See troubleshooting section above
3. Verify @BotFather token
4. Restart bot and try again

## 📝 Example Conversation

```
User: /start

Bot: Halo! 👋
Selamat datang di Manajer Keuangan Pribadi Bot!
...

User: /add_transaction

Bot: Pilih jenis transaksi:
[💰 Income] [💸 Expense]

User: (taps Expense button)

Bot: ✅ Tipe: Expense
Sekarang ketik kategori...

User: groceries

Bot: ✅ Kategori: groceries
Sekarang ketik jumlah...

User: 250000

Bot: ✅ Jumlah: Rp250,000
Ketik catatan (opsional)...

User: /skip

Bot: ✅ Transaksi berhasil disimpan!
ID: 5
Jenis: Expense
...

User: /summary

Bot: 📊 RINGKASAN KEUANGAN
💵 Pendapatan:   Rp5,000,000
💸 Pengeluaran:  Rp2,595,000
💰 Saldo:        Rp2,405,000
```

---

**Status**: ✅ READY TO USE  
**Database**: SQLite (Shared with CLI)  
**Multi-platform**: Yes (CLI + Telegram)  
**Real-time Sync**: Yes  
