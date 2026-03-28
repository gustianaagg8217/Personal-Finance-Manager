"""Telegram Bot for Personal Finance Manager."""

import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ConversationHandler,
    filters,
    ContextTypes,
)
from telegram.constants import ChatAction
from telegram.error import Conflict

from services.transaction_service import TransactionService
from services.report_service import ReportService
from services.budget_service import BudgetService
from utils.formatter import format_currency
from utils.validator import validate_amount, is_cancel_command


logger = logging.getLogger(__name__)

# Conversation states
TRANSACTION_TYPE, CATEGORY, AMOUNT, NOTE = range(4)
BUDGET_CATEGORY, BUDGET_AMOUNT = range(4, 6)


class FinanceBot:
    """Telegram bot for finance management."""
    
    def __init__(self, token: str):
        """
        Initialize finance bot.
        
        Args:
            token: Telegram bot token from BotFather
        """
        self.token = token
        self.transaction_service = TransactionService()
        self.report_service = ReportService(self.transaction_service)
        self.budget_service = BudgetService(self.transaction_service)
        logger.info("FinanceBot initialized")
    
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Start command handler."""
        user = update.effective_user
        welcome_text = (
            f"Halo {user.first_name}! 👋\n\n"
            "Selamat datang di Manajer Keuangan Pribadi Bot!\n\n"
            "Gunakan perintah berikut:\n"
            "/add_transaction - Tambah transaksi\n"
            "/summary - Lihat ringkasan\n"
            "/category_report - Laporan kategori\n"
            "/monthly_report - Laporan bulanan\n"
            "/set_budget - Atur anggaran\n"
            "/budget_status - Status anggaran\n"
            "/help - Bantuan\n\n"
            "Ketik /help untuk informasi lebih lanjut."
        )
        await update.message.reply_text(welcome_text)
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Help command handler."""
        help_text = (
            "📚 BANTUAN\n\n"
            "Perintah Tersedia:\n\n"
            "💰 /add_transaction\n"
            "   Menambahkan transaksi pendapatan/pengeluaran\n\n"
            "📊 /summary\n"
            "   Menampilkan ringkasan keuangan (income, expense, balance)\n\n"
            "🏷️ /category_report\n"
            "   Laporan pengeluaran berdasarkan kategori\n\n"
            "📅 /monthly_report\n"
            "   Laporan bulanan\n\n"
            "💳 /set_budget\n"
            "   Mengatur anggaran bulanan untuk kategori\n\n"
            "✅ /budget_status\n"
            "   Melihat status anggaran bulan ini\n\n"
            "❌ /cancel\n"
            "   Membatalkan operasi\n\n"
            "📌 Tips:\n"
            "• Database sama dengan CLI (SQLite)\n"
            "• Update real-time di kedua platform\n"
            "• Ketik 'batal' untuk membatalkan input"
        )
        await update.message.reply_text(help_text)
    
    async def summary(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Show financial summary."""
        await update.message.chat.send_action(ChatAction.TYPING)
        
        income = self.transaction_service.get_total_income()
        expense = self.transaction_service.get_total_expense()
        balance = self.transaction_service.get_balance()
        
        text = (
            "📊 RINGKASAN KEUANGAN\n\n"
            f"💵 Pendapatan:   Rp{format_currency(income)}\n"
            f"💸 Pengeluaran:  Rp{format_currency(expense)}\n"
            f"💰 Saldo:        Rp{format_currency(balance)}\n"
        )
        await update.message.reply_text(text)
    
    async def category_report(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Show expense by category."""
        await update.message.chat.send_action(ChatAction.TYPING)
        
        expenses = self.transaction_service.get_expenses_by_category()
        
        if not expenses:
            await update.message.reply_text("❌ Tidak ada catatan pengeluaran.")
            return
        
        text = "🏷️ PENGELUARAN BERDASARKAN KATEGORI\n\n"
        total = sum(expenses.values())
        
        for category, amount in expenses.items():
            percentage = (amount / total * 100) if total > 0 else 0
            text += f"• {category}: Rp{format_currency(amount)} ({percentage:.1f}%)\n"
        
        text += f"\n💹 Total: Rp{format_currency(total)}"
        await update.message.reply_text(text)
    
    async def monthly_report(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Show monthly report."""
        await update.message.chat.send_action(ChatAction.TYPING)
        
        from collections import defaultdict
        monthly_data = defaultdict(lambda: {"income": 0, "expense": 0})
        
        for transaction in self.transaction_service.transactions:
            month = transaction.date[:7]
            if transaction.transaction_type == "income":
                monthly_data[month]["income"] += transaction.amount
            else:
                monthly_data[month]["expense"] += transaction.amount
        
        if not monthly_data:
            await update.message.reply_text("❌ Tidak ada data transaksi.")
            return
        
        text = "📅 LAPORAN BULANAN\n\n"
        
        for month in sorted(monthly_data.keys(), reverse=True)[:6]:  # Last 6 months
            data = monthly_data[month]
            income = data["income"]
            expense = data["expense"]
            balance = income - expense
            
            text += f"📆 {month}\n"
            text += f"  💵 Pendapatan: Rp{format_currency(income)}\n"
            text += f"  💸 Pengeluaran: Rp{format_currency(expense)}\n"
            text += f"  💰 Saldo: Rp{format_currency(balance)}\n\n"
        
        await update.message.reply_text(text)
    
    async def start_add_transaction(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Start transaction conversation."""
        keyboard = [
            [InlineKeyboardButton("💰 Income", callback_data="income")],
            [InlineKeyboardButton("💸 Expense", callback_data="expense")],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            "Pilih jenis transaksi:",
            reply_markup=reply_markup
        )
        
        return TRANSACTION_TYPE
    
    async def transaction_type_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Handle transaction type selection."""
        query = update.callback_query
        await query.answer()
        
        context.user_data["transaction_type"] = query.data
        
        await query.edit_message_text(
            text=f"✅ Tipe: {query.data.capitalize()}\n\n"
            "Sekarang ketik kategori:\n"
            "(contoh: groceries, utilities, salary, bonus)\n\n"
            "Ketik 'batal' untuk membatalkan"
        )
        
        return CATEGORY
    
    async def category_input(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Handle category input."""
        text = update.message.text.strip()
        
        if is_cancel_command(text):
            await update.message.reply_text("❌ Operasi dibatalkan.")
            return ConversationHandler.END
        
        if not text:
            await update.message.reply_text("❌ Kategori tidak boleh kosong.")
            return CATEGORY
        
        context.user_data["category"] = text
        
        await update.message.reply_text(
            f"✅ Kategori: {text}\n\n"
            "Sekarang ketik jumlah:\n"
            "(contoh: 50000)\n\n"
            "Ketik 'batal' untuk membatalkan"
        )
        
        return AMOUNT
    
    async def skip_note(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Handle /skip command to skip note input."""
        # Save transaction without note
        try:
            transaction = self.transaction_service.add_transaction(
                transaction_type=context.user_data["transaction_type"],
                category=context.user_data["category"],
                amount=context.user_data["amount"],
                note=""
            )
            
            response = (
                f"✅ Transaksi berhasil disimpan!\n\n"
                f"ID: {transaction.transaction_id}\n"
                f"Jenis: {transaction.transaction_type.capitalize()}\n"
                f"Kategori: {transaction.category}\n"
                f"Jumlah: Rp{format_currency(transaction.amount)}\n"
                f"Tanggal: {transaction.date}"
            )
            
            # Create menu keyboard
            keyboard = [
                [
                    InlineKeyboardButton("Tambah Lagi", callback_data="add_transaction"),
                    InlineKeyboardButton("Lihat Ringkasan", callback_data="show_summary"),
                ],
                [InlineKeyboardButton("Kembali ke Menu Utama", callback_data="main_menu")],
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(response, reply_markup=reply_markup)
            return ConversationHandler.END
        except Exception as e:
            logger.error(f"Error adding transaction: {e}")
            await update.message.reply_text(f"❌ Kesalahan saat menyimpan transaksi: {e}")
            return ConversationHandler.END
    
    async def amount_input(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Handle amount input."""
        text = update.message.text.strip()
        
        if is_cancel_command(text):
            await update.message.reply_text("❌ Operasi dibatalkan.")
            return ConversationHandler.END
        
        is_valid, amount = validate_amount(text)
        
        if not is_valid:
            await update.message.reply_text(
                "❌ Jumlah tidak valid. Masukkan angka positif.\n"
                "Coba lagi:"
            )
            return AMOUNT
        
        context.user_data["amount"] = amount
        
        await update.message.reply_text(
            f"✅ Jumlah: Rp{format_currency(amount)}\n\n"
            "Ketik catatan (opsional):\n"
            "(Atau tekan /skip untuk lewati)\n\n"
            "Ketik 'batal' untuk membatalkan"
        )
        
        return NOTE
    
    async def note_input(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Handle note input and save transaction."""
        text = update.message.text.strip()
        
        if is_cancel_command(text):
            await update.message.reply_text("❌ Operasi dibatalkan.")
            return ConversationHandler.END
        
        note = text
        
        # Save transaction
        try:
            transaction = self.transaction_service.add_transaction(
                transaction_type=context.user_data["transaction_type"],
                category=context.user_data["category"],
                amount=context.user_data["amount"],
                note=note
            )
            
            response = (
                f"✅ Transaksi berhasil disimpan!\n\n"
                f"ID: {transaction.transaction_id}\n"
                f"Jenis: {context.user_data['transaction_type'].capitalize()}\n"
                f"Kategori: {context.user_data['category']}\n"
                f"Jumlah: Rp{format_currency(context.user_data['amount'])}\n"
                f"Catatan: {note or '(tidak ada)'}\n"
                f"Tanggal: {transaction.date}"
            )
            
            # Create menu keyboard
            keyboard = [
                [
                    InlineKeyboardButton("Tambah Lagi", callback_data="add_transaction"),
                    InlineKeyboardButton("Lihat Ringkasan", callback_data="show_summary"),
                ],
                [InlineKeyboardButton("Kembali ke Menu Utama", callback_data="main_menu")],
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(response, reply_markup=reply_markup)
            logger.info(f"Transaction added: {context.user_data['transaction_type']} {context.user_data['category']}")
        
        except Exception as e:
            await update.message.reply_text(f"❌ Error: {e}")
            logger.error(f"Error saving transaction: {e}")
        
        return ConversationHandler.END
    
    async def start_set_budget(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Start budget setting conversation."""
        await update.message.reply_text(
            "Ketik kategori untuk mengatur anggaran:\n"
            "(contoh: groceries, utilities, entertainment)\n\n"
            "Ketik 'batal' untuk membatalkan"
        )
        return BUDGET_CATEGORY
    
    async def budget_category_input(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Handle budget category input."""
        text = update.message.text.strip()
        
        if is_cancel_command(text):
            await update.message.reply_text("❌ Operasi dibatalkan.")
            return ConversationHandler.END
        
        if not text:
            await update.message.reply_text("❌ Kategori tidak boleh kosong.")
            return BUDGET_CATEGORY
        
        context.user_data["budget_category"] = text
        
        await update.message.reply_text(
            f"✅ Kategori: {text}\n\n"
            "Sekarang ketik anggaran bulanan:\n"
            "(contoh: 5000000)\n\n"
            "Ketik 'batal' untuk membatalkan"
        )
        
        return BUDGET_AMOUNT
    
    async def budget_amount_input(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Handle budget amount input and save."""
        text = update.message.text.strip()
        
        if is_cancel_command(text):
            await update.message.reply_text("❌ Operasi dibatalkan.")
            return ConversationHandler.END
        
        is_valid, amount = validate_amount(text)
        
        if not is_valid:
            await update.message.reply_text(
                "❌ Jumlah tidak valid. Masukkan angka positif.\n"
                "Coba lagi:"
            )
            return BUDGET_AMOUNT
        
        try:
            self.budget_service.set_budget(
                context.user_data["budget_category"],
                amount
            )
            
            response = (
                f"✅ Anggaran berhasil diatur!\n\n"
                f"Kategori: {context.user_data['budget_category']}\n"
                f"Anggaran: Rp{format_currency(amount)} per bulan"
            )
            
            await update.message.reply_text(response)
            logger.info(f"Budget set: {context.user_data['budget_category']} {amount}")
        
        except Exception as e:
            await update.message.reply_text(f"❌ Error: {e}")
            logger.error(f"Error setting budget: {e}")
        
        return ConversationHandler.END
    
    async def budget_status(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Show budget status."""
        await update.message.chat.send_action(ChatAction.TYPING)
        
        if not self.budget_service.budgets:
            await update.message.reply_text("❌ Belum ada anggaran yang ditetapkan.")
            return
        
        text = "✅ STATUS ANGGARAN BULAN INI\n\n"
        
        for category in sorted(self.budget_service.budgets.keys()):
            status = self.budget_service.get_budget_status(category)
            budget = status["budget"]
            spending = status["spending"]
            remaining = status["remaining"]
            exceeded = status["exceeded"]
            
            if exceeded:
                symbol = "🔴 TERLAMPAUI"
                budget_text = f"[Budget: Rp{format_currency(budget)}]"
            else:
                symbol = "🟢 OK"
                budget_text = f"[Budget: Rp{format_currency(budget)}]"
            
            text += (
                f"📌 {category}\n"
                f"  {symbol}\n"
                f"  Pengeluaran: Rp{format_currency(spending)}\n"
                f"  Sisa: Rp{format_currency(remaining)} {budget_text}\n\n"
            )
        
        await update.message.reply_text(text)
    
    async def cancel(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Cancel conversation."""
        await update.message.reply_text("❌ Operasi dibatalkan.")
        return ConversationHandler.END
    
    async def error_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle errors from Telegram."""
        error = context.error
        
        # Handle Conflict errors specially - log as CRITICAL
        if isinstance(error, Conflict):
            logger.critical(
                "[CONFLICT] Bot Instance Conflict! "
                "Another bot instance is using this token. "
                "Kill other instances and restart."
            )
            return
        
        # Log other errors for debugging
        logger.error(f"Error occurred: {error}", exc_info=True)
    
    async def menu_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle menu callbacks from inline buttons."""
        query = update.callback_query
        await query.answer()
        
        if query.data == "add_transaction":
            # Start a new transaction
            await self.start_add_transaction(update, context)
        elif query.data == "show_summary":
            # Show summary
            await self.summary(update, context)
        elif query.data == "main_menu":
            # Show main menu with all commands
            menu_text = (
                "🏠 MENU UTAMA\n\n"
                "Pilih perintah di bawah:\n\n"
                "💰 /add_transaction - Tambah transaksi\n"
                "📊 /summary - Lihat ringkasan\n"
                "🏷️ /category_report - Laporan kategori\n"
                "📅 /monthly_report - Laporan bulanan\n"
                "💳 /set_budget - Atur anggaran\n"
                "✅ /budget_status - Status anggaran\n"
                "❓ /help - Bantuan"
            )
            
            keyboard = [
                [
                    InlineKeyboardButton("Tambah Transaksi", callback_data="add_transaction"),
                    InlineKeyboardButton("Lihat Ringkasan", callback_data="show_summary"),
                ]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            # Edit the message if it's from a callback, otherwise send new message
            try:
                await query.edit_message_text(text=menu_text, reply_markup=reply_markup)
            except Exception:
                await query.message.reply_text(menu_text, reply_markup=reply_markup)
    
    def get_application(self) -> Application:
        """Build and return the Telegram bot application."""
        app = Application.builder().token(self.token).build()
        
        # Add command handlers
        app.add_handler(CommandHandler("start", self.start))
        app.add_handler(CommandHandler("help", self.help_command))
        app.add_handler(CommandHandler("summary", self.summary))
        app.add_handler(CommandHandler("category_report", self.category_report))
        app.add_handler(CommandHandler("monthly_report", self.monthly_report))
        app.add_handler(CommandHandler("budget_status", self.budget_status))
        
        # Add transaction conversation handler
        add_transaction_handler = ConversationHandler(
            entry_points=[CommandHandler("add_transaction", self.start_add_transaction)],
            states={
                TRANSACTION_TYPE: [CallbackQueryHandler(self.transaction_type_callback)],
                CATEGORY: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.category_input)],
                AMOUNT: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.amount_input)],
                NOTE: [
                    CommandHandler("skip", self.skip_note),
                    MessageHandler(filters.TEXT & ~filters.COMMAND, self.note_input)
                ],
            },
            fallbacks=[CommandHandler("cancel", self.cancel)],
        )
        app.add_handler(add_transaction_handler)
        
        # Add budget conversation handler
        set_budget_handler = ConversationHandler(
            entry_points=[CommandHandler("set_budget", self.start_set_budget)],
            states={
                BUDGET_CATEGORY: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.budget_category_input)],
                BUDGET_AMOUNT: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.budget_amount_input)],
            },
            fallbacks=[CommandHandler("cancel", self.cancel)],
        )
        app.add_handler(set_budget_handler)
        
        # Add menu callback handler for post-transaction buttons
        app.add_handler(CallbackQueryHandler(self.menu_callback, pattern="^(add_transaction|show_summary|main_menu)$"))
        
        # Add error handler
        app.add_error_handler(self.error_handler)
        
        return app
    
    def run(self) -> None:
        """Run the bot."""
        import time
        
        logger.info("Starting Telegram bot...")
        logger.info("Cleaning up any existing webhooks...")
        
        # Try to clean up webhooks synchronously
        try:
            from telegram import Bot
            import asyncio
            bot = Bot(token=self.token)
            loop = asyncio.new_event_loop()
            loop.run_until_complete(bot.delete_webhook(drop_pending_updates=True))
            loop.close()
            logger.info("[OK] Webhook cleared successfully")
        except Exception as e:
            logger.warning(f"Could not clear webhook (may not matter): {e}")
        
        max_retries = 3
        retry_count = 0
        
        while retry_count < max_retries:
            try:
                # Create a fresh application for this attempt
                app = self.get_application()
                logger.info(f"Attempt {retry_count + 1}/{max_retries} to start polling...")
                app.run_polling(allowed_updates=Update.ALL_TYPES)
                break  # Success, exit loop
            except Conflict as e:
                retry_count += 1
                logger.error(f"Conflict error (attempt {retry_count}/{max_retries}): {e}")
                
                if retry_count < max_retries:
                    wait_time = 15 * retry_count  # 15s, 30s, 45s
                    logger.info(f"Waiting {wait_time}s before retry...")
                    time.sleep(wait_time)
                else:
                    logger.critical(
                        "Failed to start bot after "
                        + f"{max_retries} attempts.\n"
                        + "Make sure no other bot instance is running with this token."
                    )
                    raise
            except Exception as e:
                logger.error(f"Unexpected error: {e}", exc_info=True)
                raise


def run_bot(token: str) -> None:
    """Helper function to run bot."""
    bot = FinanceBot(token)
    bot.run()
