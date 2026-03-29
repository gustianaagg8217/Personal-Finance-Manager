"""Telegram Bot for Personal Finance Manager."""

import logging
import json
import os
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
BUDGET_CATEGORY, BUDGET_TOTAL_INCOME, BUDGET_AMOUNT = range(4, 7)

# Predefined categories
EXPENSE_CATEGORIES = [
    "Kebutuhan Pokok",
    "Tabungan/Investasi",
    "Gaya Hidup",
    "Cicilan/Hutang",
    "Proteksi"
]

INCOME_CATEGORIES = [
    "Gaji",
    "Bonus",
    "Investasi",
    "Bisnis",
    "Lainnya"
]

# Default budget allocation percentages by category
DEFAULT_BUDGET_PERCENTAGES = {
    "Kebutuhan Pokok": 50,        # 50%
    "Tabungan/Investasi": 20,     # 20%
    "Gaya Hidup": 15,             # 15%
    "Cicilan/Hutang": 10,         # 10%
    "Proteksi": 5                 # 5%
}


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
        self.custom_categories_file = "custom_categories.json"
        
        # Load custom categories
        self.custom_expense_categories = self.load_custom_categories("expense")
        self.custom_income_categories = self.load_custom_categories("income")
        
        logger.info("FinanceBot initialized")
    
    def load_custom_categories(self, category_type: str) -> list:
        """Load custom categories from file for a specific type (expense/income)."""
        if os.path.exists(self.custom_categories_file):
            try:
                with open(self.custom_categories_file, 'r') as f:
                    data = json.load(f)
                    return data.get(category_type, [])
            except Exception as e:
                logger.error(f"Error loading custom categories: {e}")
                return []
        return []
    
    def save_custom_categories(self) -> None:
        """Save custom categories to file."""
        try:
            data = {
                "expense": self.custom_expense_categories,
                "income": self.custom_income_categories
            }
            with open(self.custom_categories_file, 'w') as f:
                json.dump(data, f, indent=4)
            logger.info("Custom categories saved")
        except Exception as e:
            logger.error(f"Error saving custom categories: {e}")
    
    def add_custom_category(self, category_type: str, category_name: str) -> bool:
        """Add a new custom category if it doesn't already exist."""
        if category_type == "expense":
            categories = EXPENSE_CATEGORIES + self.custom_expense_categories
            custom_list = self.custom_expense_categories
        else:
            categories = INCOME_CATEGORIES + self.custom_income_categories
            custom_list = self.custom_income_categories
        
        # Check if category already exists
        if category_name in categories:
            return False
        
        # Add to custom categories and save
        custom_list.append(category_name)
        self.save_custom_categories()
        logger.info(f"Custom {category_type} category added: {category_name}")
        return True
    
    def get_all_categories(self, category_type: str) -> list:
        """Get all categories (predefined + custom) for a specific type."""
        if category_type == "expense":
            return EXPENSE_CATEGORIES + self.custom_expense_categories
        else:
            return INCOME_CATEGORIES + self.custom_income_categories
    
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Start command handler."""
        user = update.effective_user
        welcome_text = (
            f"Halo {user.first_name}! 👋\n\n"
            "Selamat datang di Manajer Keuangan Pribadi Bot!\n\n"
            "🏠 MENU UTAMA (13 Pilihan):\n\n"
            "1️⃣ /add_transaction - Tambah transaksi\n"
            "2️⃣ /summary - Lihat ringkasan\n"
            "3️⃣ /category_report - Laporan kategori\n"
            "4️⃣ /monthly_report - Laporan bulanan\n"
            "5️⃣ /charts - Grafik laporan\n"
            "6️⃣ /set_budget - Atur anggaran\n"
            "7️⃣ /budget_status - Status anggaran\n"
            "8️⃣ /transactions - Kelola transaksi\n"
            "9️⃣ /analytics - Analitik & kesehatan\n"
            "🔟 /recurring - Transaksi berulang\n"
            "1️⃣1️⃣ /export - Ekspor data\n"
            "1️⃣2️⃣ /settings - Pengaturan\n"
            "1️⃣3️⃣ /help - Bantuan"
        )
        await update.message.reply_text(welcome_text)
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Help command handler."""
        help_text = (
            "📚 BANTUAN - 13 MENU UTAMA\n\n"
            "💰 /add_transaction\n"
            "   Menambahkan transaksi pendapatan/pengeluaran\n\n"
            "📊 /summary\n"
            "   Menampilkan ringkasan keuangan (income, expense, balance)\n\n"
            "🏷️ /category_report\n"
            "   Laporan pengeluaran berdasarkan kategori\n\n"
            "📅 /monthly_report\n"
            "   Laporan bulanan\n\n"
            "📊 /charts\n"
            "   Grafik laporan (tersedia di CLI)\n\n"
            "💳 /set_budget\n"
            "   Mengatur anggaran bulanan untuk kategori\n\n"
            "✅ /budget_status\n"
            "   Melihat status anggaran bulan ini\n\n"
            "🔍 /transactions\n"
            "   Kelola transaksi (edit/hapus/cari di CLI)\n\n"
            "💡 /analytics\n"
            "   Analitik & kesehatan keuangan\n\n"
            "📅 /recurring\n"
            "   Kelola transaksi berulang\n\n"
            "📥 /export\n"
            "   Ekspor data ke CSV/TXT\n\n"
            "⚙️ /settings\n"
            "   Pengaturan aplikasi\n\n"
            "❌ /cancel\n"
            "   Membatalkan operasi\n\n"
            "📌 Tips:\n"
            "• Database sama dengan CLI (SQLite)\n"
            "• Update real-time di kedua platform\n"
            "• Fitur lengkap tersedia di aplikasi CLI\n\n"
            "📖 Untuk info kategori budget, ketik /categories"
        )
        await update.message.reply_text(help_text)
    
    async def categories_info(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Show budget categories information."""
        # Handle both command and callback query
        is_callback = update.callback_query is not None
        if is_callback:
            await update.callback_query.answer()
            await update.callback_query.message.chat.send_action(ChatAction.TYPING)
        else:
            await update.message.chat.send_action(ChatAction.TYPING)
        
        categories_text = (
            "🧾 PANDUAN KATEGORI BUDGET\n\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            "🧾 1. KEBUTUHAN POKOK (50%)\n"
            "Survival category — tanpa ini hidup goyang\n\n"
            "📋 Turunannya:\n"
            "🍚 Makanan & Minuman\n"
            "   • Belanja bulanan\n"
            "   • Makan harian (warung, kantin)\n"
            "🏠 Tempat Tinggal\n"
            "   • Sewa rumah / kontrakan\n"
            "   • Cicilan KPR\n"
            "💡 Tagihan Rumah\n"
            "   • Listrik, Air, Internet\n"
            "🚗 Transportasi\n"
            "   • BBM, Ongkos, Servis ringan\n"
            "📱 Komunikasi\n"
            "   • Pulsa, Paket data\n\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            "💰 2. TABUNGAN / INVESTASI (20%)\n"
            "Growth category — masa depan dimulai dari sini\n\n"
            "📋 Turunannya:\n"
            "🏦 Tabungan\n"
            "   • Tabungan biasa\n"
            "   • Dana darurat\n"
            "📈 Investasi\n"
            "   • Saham, Crypto, Reksadana, Emas\n"
            "💼 Pengembangan Diri\n"
            "   • Kursus, Sertifikasi, Buku\n"
            "🧠 Bisnis / Side Income\n"
            "   • Modal usaha, Tools kerja\n\n"
            "💡 PRO TIP: Ini BUKAN sisa uang, tapi PRIORITAS!"
        )
        
        keyboard = [
            [InlineKeyboardButton("Lanjut →", callback_data="categories_page_2")],
            [InlineKeyboardButton("Kembali ke Menu Utama", callback_data="main_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        if is_callback:
            try:
                await update.callback_query.edit_message_text(text=categories_text, reply_markup=reply_markup)
            except Exception:
                await update.callback_query.message.reply_text(categories_text, reply_markup=reply_markup)
        else:
            await update.message.reply_text(categories_text, reply_markup=reply_markup)
    
    async def categories_info_page2(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Show budget categories information page 2."""
        query = update.callback_query
        await query.answer()
        await query.message.chat.send_action(ChatAction.TYPING)
        
        categories_text_p2 = (
            "🎯 3. GAYA HIDUP (15%)\n"
            "Kenyamanan & kesenangan — reward untuk kerja keras\n\n"
            "📋 Turunannya:\n"
            "☕ Nongkrong & Kuliner\n"
            "   • Kafe, Restoran\n"
            "🎬 Hiburan\n"
            "   • Bioskop, Streaming, Gaming\n"
            "🛍️ Belanja\n"
            "   • Fashion, Gadget non-esensial\n"
            "✈️ Liburan\n"
            "   • Staycation, Traveling\n"
            "🎮 Hobi\n"
            "   • Koleksi, Interest lainnya\n\n"
            "⚠️ CATATAN: Ini yang paling sering bikin keuangan \"bocor halus\"\n\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            "💳 4. CICILAN / HUTANG (10%)\n"
            "Beban finansial — kewajiban yang harus dibayar\n\n"
            "📋 Turunannya:\n"
            "🚗 Cicilan Kendaraan\n"
            "🏠 KPR (jika dianggap kewajiban)\n"
            "💳 Kartu Kredit\n"
            "🏦 Pinjaman Bank\n"
            "📱 Paylater / Kredit Online\n\n"
            "💡 INSIGHT: Ini kewajiban, bukan aset (kecuali menghasilkan uang)"
        )
        
        keyboard = [
            [InlineKeyboardButton("← Kembali", callback_data="categories_page_1")],
            [InlineKeyboardButton("Lanjut →", callback_data="categories_page_3")],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        try:
            await query.edit_message_text(text=categories_text_p2, reply_markup=reply_markup)
        except Exception:
            await query.message.reply_text(categories_text_p2, reply_markup=reply_markup)
    
    async def categories_info_page3(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Show budget categories information page 3."""
        query = update.callback_query
        await query.answer()
        await query.message.chat.send_action(ChatAction.TYPING)
        
        categories_text_p3 = (
            "🛡️ 5. PROTEKSI (5%)\n"
            "Defense system — anti bangkrut\n\n"
            "📋 Turunannya:\n"
            "🏥 Asuransi Kesehatan\n"
            "💼 Asuransi Jiwa\n"
            "🚗 Asuransi Kendaraan\n"
            "🧾 BPJS\n"
            "💊 Dana Kesehatan\n"
            "   • Obat, Klinik, Checkup\n\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            "📊 RINGKASAN ALOKASI:\n"
            "🧾 Kebutuhan Pokok: 50%\n"
            "💰 Tabungan/Investasi: 20%\n"
            "🎯 Gaya Hidup: 15%\n"
            "💳 Cicilan/Hutang: 10%\n"
            "🛡️ Proteksi: 5%\n\n"
            "✅ TOTAL: 100%\n\n"
            "💡 MINDSET: Proteksi bukan pengeluaran, tapi \"anti bangkrut\""
        )
        
        keyboard = [
            [InlineKeyboardButton("← Kembali", callback_data="categories_page_2")],
            [InlineKeyboardButton("Kembali ke Menu Utama", callback_data="main_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        try:
            await query.edit_message_text(text=categories_text_p3, reply_markup=reply_markup)
        except Exception:
            await query.message.reply_text(categories_text_p3, reply_markup=reply_markup)
    
    async def categories_page1_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Callback handler for page 1 navigation."""
        query = update.callback_query
        await query.answer()
        await query.message.chat.send_action(ChatAction.TYPING)
        
        categories_text = (
            "🧾 PANDUAN KATEGORI BUDGET\n\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            "🧾 1. KEBUTUHAN POKOK (50%)\n"
            "Survival category — tanpa ini hidup goyang\n\n"
            "📋 Turunannya:\n"
            "🍚 Makanan & Minuman\n"
            "   • Belanja bulanan\n"
            "   • Makan harian (warung, kantin)\n"
            "🏠 Tempat Tinggal\n"
            "   • Sewa rumah / kontrakan\n"
            "   • Cicilan KPR\n"
            "💡 Tagihan Rumah\n"
            "   • Listrik, Air, Internet\n"
            "🚗 Transportasi\n"
            "   • BBM, Ongkos, Servis ringan\n"
            "📱 Komunikasi\n"
            "   • Pulsa, Paket data\n\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            "💰 2. TABUNGAN / INVESTASI (20%)\n"
            "Growth category — masa depan dimulai dari sini\n\n"
            "📋 Turunannya:\n"
            "🏦 Tabungan\n"
            "   • Tabungan biasa\n"
            "   • Dana darurat\n"
            "📈 Investasi\n"
            "   • Saham, Crypto, Reksadana, Emas\n"
            "💼 Pengembangan Diri\n"
            "   • Kursus, Sertifikasi, Buku\n"
            "🧠 Bisnis / Side Income\n"
            "   • Modal usaha, Tools kerja\n\n"
            "💡 PRO TIP: Ini BUKAN sisa uang, tapi PRIORITAS!"
        )
        
        keyboard = [
            [InlineKeyboardButton("Lanjut →", callback_data="categories_page_2")],
            [InlineKeyboardButton("Kembali ke Menu Utama", callback_data="main_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        try:
            await query.edit_message_text(text=categories_text, reply_markup=reply_markup)
        except Exception:
            await query.message.reply_text(categories_text, reply_markup=reply_markup)
    
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
        
        # Create menu keyboard
        keyboard = [
            [InlineKeyboardButton("Kembali ke Menu Utama", callback_data="main_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(text, reply_markup=reply_markup)
    
    async def category_report(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Show expense by category."""
        await update.message.chat.send_action(ChatAction.TYPING)
        
        expenses = self.transaction_service.get_expenses_by_category()
        
        if not expenses:
            keyboard = [
                [InlineKeyboardButton("Kembali ke Menu Utama", callback_data="main_menu")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await update.message.reply_text("❌ Tidak ada catatan pengeluaran.", reply_markup=reply_markup)
            return
        
        text = "🏷️ PENGELUARAN BERDASARKAN KATEGORI\n\n"
        total = sum(expenses.values())
        
        for category, amount in expenses.items():
            percentage = (amount / total * 100) if total > 0 else 0
            text += f"• {category}: Rp{format_currency(amount)} ({percentage:.1f}%)\n"
        
        text += f"\n💹 Total: Rp{format_currency(total)}"
        
        # Create menu keyboard
        keyboard = [
            [InlineKeyboardButton("Kembali ke Menu Utama", callback_data="main_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(text, reply_markup=reply_markup)
    
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
            keyboard = [
                [InlineKeyboardButton("Kembali ke Menu Utama", callback_data="main_menu")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await update.message.reply_text("❌ Tidak ada data transaksi.", reply_markup=reply_markup)
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
        
        # Create menu keyboard
        keyboard = [
            [InlineKeyboardButton("Kembali ke Menu Utama", callback_data="main_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(text, reply_markup=reply_markup)
    
    async def start_add_transaction(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Start transaction conversation."""
        keyboard = [
            [InlineKeyboardButton("💰 Income", callback_data="income")],
            [InlineKeyboardButton("💸 Expense", callback_data="expense")],
            [InlineKeyboardButton("Kembali ke Menu Utama", callback_data="main_menu")],
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
        
        transaction_type = query.data  # "income" or "expense"
        context.user_data["transaction_type"] = transaction_type
        
        # Show category selection buttons based on transaction type (include custom categories)
        categories = self.get_all_categories(transaction_type)
        keyboard = []
        for idx in range(0, len(categories), 2):
            row = []
            # Use category name directly in callback_data
            row.append(InlineKeyboardButton(categories[idx], callback_data=f"cat_{categories[idx]}"))
            if idx + 1 < len(categories):
                row.append(InlineKeyboardButton(categories[idx + 1], callback_data=f"cat_{categories[idx + 1]}"))
            keyboard.append(row)
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            text=f"✅ Jenis: {transaction_type.capitalize()}\n\nPilih kategori:",
            reply_markup=reply_markup
        )
        
        return CATEGORY
    
    async def category_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Handle category selection from buttons."""
        query = update.callback_query
        await query.answer()
        
        # Extract category name from callback_data (format: "cat_KategoriNama")
        category = query.data.replace("cat_", "")
        
        # Check if user selected "Lainnya" (Other category)
        if category == "Lainnya":
            # Store that we're waiting for custom category input
            context.user_data["waiting_for_custom_category"] = True
            
            await query.edit_message_text(
                text="✏️ Masukkan nama kategori baru:\n\n"
                "Ketik 'batal' untuk membatalkan"
            )
            
            return CATEGORY  # Stay in CATEGORY state to receive text input
        
        # For regular categories, save and move to amount
        context.user_data["category"] = category
        
        await query.edit_message_text(
            text=f"✅ Kategori: {category}\n\n"
            "Sekarang ketik jumlah:\n"
            "(contoh: 50000)\n\n"
            "Ketik 'batal' untuk membatalkan"
        )
        
        return AMOUNT
    
    async def category_input(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Handle category input (for cancel command and custom category input)."""
        text = update.message.text.strip()
        
        if is_cancel_command(text):
            return await self.show_main_menu_on_cancel(update)
        
        # Check if we're waiting for custom category input
        if context.user_data.get("waiting_for_custom_category"):
            context.user_data.pop("waiting_for_custom_category", None)
            
            custom_category = text
            transaction_type = context.user_data.get("transaction_type")
            
            # Try to add custom category
            if self.add_custom_category(transaction_type, custom_category):
                context.user_data["category"] = custom_category
                await update.message.reply_text(
                    f"✅ Kategori baru '{custom_category}' ditambahkan!\n\n"
                    "Sekarang ketik jumlah:\n"
                    "(contoh: 50000)\n\n"
                    "Ketik 'batal' untuk membatalkan"
                )
                return AMOUNT
            else:
                # Category already exists, use it
                context.user_data["category"] = custom_category
                await update.message.reply_text(
                    f"✅ Kategori: {custom_category}\n\n"
                    "Sekarang ketik jumlah:\n"
                    "(contoh: 50000)\n\n"
                    "Ketik 'batal' untuk membatalkan"
                )
                return AMOUNT
        
        # If user types something without selecting category button, show an error
        await update.message.reply_text(
            "❌ Silakan pilih kategori dari tombol yang disediakan.\n"
            "Ketik 'batal' untuk membatalkan"
        )
        return CATEGORY
    
    async def skip_note(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Handle /skip command to skip note input."""
        text = update.message.text.strip() if update.message else ""
        
        if is_cancel_command(text):
            return await self.show_main_menu_on_cancel(update)
        
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
            return await self.show_main_menu_on_cancel(update)
        
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
            return await self.show_main_menu_on_cancel(update)
        
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
        # Show category selection buttons (only expense categories for budgets, including custom)
        categories = self.get_all_categories("expense")
        keyboard = []
        for idx in range(0, len(categories), 2):
            row = []
            row.append(InlineKeyboardButton(categories[idx], callback_data=f"budget_cat_{categories[idx]}"))
            if idx + 1 < len(categories):
                row.append(InlineKeyboardButton(categories[idx + 1], callback_data=f"budget_cat_{categories[idx + 1]}"))
            keyboard.append(row)
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            "Pilih kategori untuk mengatur anggaran:",
            reply_markup=reply_markup
        )
        return BUDGET_CATEGORY
    
    async def budget_category_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Handle budget category selection from buttons."""
        query = update.callback_query
        await query.answer()
        
        # Extract category name from callback_data (format: "budget_cat_KategoriNama")
        category = query.data.replace("budget_cat_", "")
        
        # Check if user selected "Lainnya" (Other category)
        if category == "Lainnya":
            # Store that we're waiting for custom category input
            context.user_data["waiting_for_custom_budget_category"] = True
            
            await query.edit_message_text(
                text="✏️ Masukkan nama kategori pengeluaran baru:\n\n"
                "Ketik 'batal' untuk membatalkan"
            )
            
            return BUDGET_CATEGORY  # Stay in BUDGET_CATEGORY state to receive text input
        
        # For regular categories, save and move to total income
        context.user_data["budget_category"] = category
        
        percentage = DEFAULT_BUDGET_PERCENTAGES.get(category)
        if percentage:
            message_text = (
                f"✅ Kategori: {category} ({percentage}%)\n\n"
                "Sekarang ketik total pendapatan bulanan:\n"
                "(Anggaran akan dihitung otomatis: Rp amount × {percentage}%)\n\n"
                "Contoh: 10000000\n"
                "Ketik 'batal' untuk membatalkan"
            )
        else:
            message_text = (
                f"✅ Kategori: {category} (Custom - Tidak ada persentase default)\n\n"
                "Sekarang ketik jumlah anggaran bulanan:\n"
                "(contoh: 5000000)\n\n"
                "Ketik 'batal' untuk membatalkan"
            )
        
        await query.edit_message_text(text=message_text)
        
        return BUDGET_TOTAL_INCOME
    
    async def budget_category_input(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Handle budget category input (for cancel command and custom category input)."""
        text = update.message.text.strip()
        
        if is_cancel_command(text):
            return await self.show_main_menu_on_cancel(update)
        
        # Check if we're waiting for custom budget category input
        if context.user_data.get("waiting_for_custom_budget_category"):
            context.user_data.pop("waiting_for_custom_budget_category", None)
            
            custom_category = text
            
            # Try to add custom expense category for budget
            if self.add_custom_category("expense", custom_category):
                context.user_data["budget_category"] = custom_category
                await update.message.reply_text(
                    f"✅ Kategori baru '{custom_category}' ditambahkan!\n\n"
                    "Sekarang ketik jumlah anggaran bulanan:\n"
                    "(contoh: 5000000)\n\n"
                    "Ketik 'batal' untuk membatalkan"
                )
                return BUDGET_AMOUNT
            else:
                # Category already exists, use it
                context.user_data["budget_category"] = custom_category
                await update.message.reply_text(
                    f"✅ Kategori: {custom_category}\n\n"
                    "Sekarang ketik jumlah anggaran bulanan:\n"
                    "(contoh: 5000000)\n\n"
                    "Ketik 'batal' untuk membatalkan"
                )
                return BUDGET_AMOUNT
        
        # If user types something without selecting category button, show an error
        await update.message.reply_text(
            "❌ Silakan pilih kategori dari tombol yang disediakan.\n"
            "Ketik 'batal' untuk membatalkan"
        )
        return BUDGET_CATEGORY
    
    async def budget_total_income_input(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Handle total income input for budget calculation."""
        text = update.message.text.strip()
        
        if is_cancel_command(text):
            return await self.show_main_menu_on_cancel(update)
        
        is_valid, total_income = validate_amount(text)
        
        if not is_valid:
            await update.message.reply_text(
                "❌ Jumlah tidak valid. Masukkan angka positif.\n"
                "Coba lagi:"
            )
            return BUDGET_TOTAL_INCOME
        
        category = context.user_data.get("budget_category")
        percentage = DEFAULT_BUDGET_PERCENTAGES.get(category)
        
        if percentage:
            # Calculate budget based on percentage
            budget_amount = int(total_income * percentage / 100)
            
            await update.message.reply_text(
                f"📊 Perhitungan Anggaran:\n"
                f"Total Pendapatan: Rp{format_currency(total_income)}\n"
                f"Persentase: {percentage}%\n"
                f"Anggaran untuk {category}: Rp{format_currency(budget_amount)}\n\n"
                f"✅ Menyimpan anggaran..."
            )
        else:
            # For custom categories without percentage, use the total_income directly as the amount
            budget_amount = total_income
            
            await update.message.reply_text(
                f"✅ Menyimpan anggaran untuk {category}:\n"
                f"Rp{format_currency(budget_amount)}"
            )
        
        # Save the budget
        context.user_data["budget_amount"] = budget_amount
        self.budget_service.set_budget(category, budget_amount)
        
        # Create menu keyboard
        keyboard = [
            [
                InlineKeyboardButton("Atur Anggaran Lagi", callback_data="set_budget"),
                InlineKeyboardButton("Lihat Status", callback_data="budget_status"),
            ],
            [InlineKeyboardButton("Kembali ke Menu Utama", callback_data="main_menu")],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text("✅ Anggaran berhasil disimpan!", reply_markup=reply_markup)
        return ConversationHandler.END
    
    async def budget_amount_input(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Handle budget amount input and save."""
        text = update.message.text.strip()
        
        if is_cancel_command(text):
            return await self.show_main_menu_on_cancel(update)
        
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
            
            # Create menu keyboard
            keyboard = [
                [InlineKeyboardButton("Kembali ke Menu Utama", callback_data="main_menu")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(response, reply_markup=reply_markup)
            logger.info(f"Budget set: {context.user_data['budget_category']} {amount}")
        
        except Exception as e:
            await update.message.reply_text(f"❌ Error: {e}")
            logger.error(f"Error setting budget: {e}")
        
        return ConversationHandler.END
    
    async def budget_status(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Show budget status."""
        await update.message.chat.send_action(ChatAction.TYPING)
        
        if not self.budget_service.budgets:
            keyboard = [
                [InlineKeyboardButton("Kembali ke Menu Utama", callback_data="main_menu")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await update.message.reply_text("❌ Belum ada anggaran yang ditetapkan.", reply_markup=reply_markup)
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
        
        # Create menu keyboard
        keyboard = [
            [InlineKeyboardButton("Kembali ke Menu Utama", callback_data="main_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(text, reply_markup=reply_markup)
    
    async def exit_to_main_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Exit conversation and show main menu."""
        query = update.callback_query
        await query.answer()
        
        menu_text = (
            "🏠 MENU UTAMA (13 PILIHAN)\n\n"
            "Silakan pilih perintah:\n\n"
            "1. 💰 /add_transaction - Tambah transaksi\n"
            "2. 📊 /summary - Lihat ringkasan\n"
            "3. 🏷️ /category_report - Laporan kategori\n"
            "4. 📅 /monthly_report - Laporan bulanan\n"
            "5. 📊 /charts - Grafik laporan\n"
            "6. 💳 /set_budget - Atur anggaran\n"
            "7. ✅ /budget_status - Status anggaran\n"
            "8. 🔍 /transactions - Kelola transaksi\n"
            "9. 💡 /analytics - Analitik & kesehatan\n"
            "10. 📅 /recurring - Transaksi berulang\n"
            "11. 📥 /export - Ekspor data\n"
            "12. ⚙️ /settings - Pengaturan\n"
            "13. ❓ /help - Bantuan"
        )
        
        keyboard = [
            [
                InlineKeyboardButton("Tambah Transaksi", callback_data="add_transaction"),
                InlineKeyboardButton("Lihat Ringkasan", callback_data="show_summary"),
            ],
            [
                InlineKeyboardButton("Status Anggaran", callback_data="budget_status"),
                InlineKeyboardButton("Atur Anggaran", callback_data="set_budget"),
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.message.reply_text(f"⏮️ Operasi dibatalkan.\n\n{menu_text}", reply_markup=reply_markup)
        return ConversationHandler.END
    
    async def show_main_menu_on_cancel(self, update: Update) -> int:
        """Show main menu when operation is cancelled."""
        menu_text = (
            "🏠 MENU UTAMA (13 PILIHAN)\n\n"
            "Silakan pilih perintah:\n\n"
            "1. 💰 /add_transaction - Tambah transaksi\n"
            "2. 📊 /summary - Lihat ringkasan\n"
            "3. 🏷️ /category_report - Laporan kategori\n"
            "4. 📅 /monthly_report - Laporan bulanan\n"
            "5. 📊 /charts - Grafik laporan\n"
            "6. 💳 /set_budget - Atur anggaran\n"
            "7. ✅ /budget_status - Status anggaran\n"
            "8. 🔍 /transactions - Kelola transaksi\n"
            "9. 💡 /analytics - Analitik & kesehatan\n"
            "10. 📅 /recurring - Transaksi berulang\n"
            "11. 📥 /export - Ekspor data\n"
            "12. ⚙️ /settings - Pengaturan\n"
            "13. ❓ /help - Bantuan"
        )
        
        keyboard = [
            [
                InlineKeyboardButton("Tambah Transaksi", callback_data="add_transaction"),
                InlineKeyboardButton("Lihat Ringkasan", callback_data="show_summary"),
            ],
            [
                InlineKeyboardButton("Status Anggaran", callback_data="budget_status"),
                InlineKeyboardButton("Atur Anggaran", callback_data="set_budget"),
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(f"⏮️ Operasi dibatalkan.\n\n{menu_text}", reply_markup=reply_markup)
        return ConversationHandler.END
    
    async def cancel(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Cancel conversation."""
        return await self.show_main_menu_on_cancel(update)
    
    async def menu_add_transaction_entry(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Entry point for add_transaction from menu callback."""
        query = update.callback_query
        await query.answer()
        
        # Show transaction type selection buttons
        keyboard = [
            [InlineKeyboardButton("💰 Income", callback_data="add_transaction_income")],
            [InlineKeyboardButton("💸 Expense", callback_data="add_transaction_expense")],
            [InlineKeyboardButton("Kembali ke Menu Utama", callback_data="main_menu")],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.message.reply_text(
            "Pilih jenis transaksi:",
            reply_markup=reply_markup
        )
        
        return TRANSACTION_TYPE
    
    async def transaction_type_from_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Handle transaction type selection from menu."""
        query = update.callback_query
        await query.answer()
        
        # Extract the type (income or expense) from callback_data
        if query.data == "add_transaction_income":
            transaction_type = "income"
        else:
            transaction_type = "expense"
        
        context.user_data["transaction_type"] = transaction_type
        
        # Select appropriate categories based on transaction type (include custom categories)
        categories = self.get_all_categories(transaction_type)
        
        # Build keyboard with category buttons
        keyboard = []
        for idx in range(0, len(categories), 2):
            row = []
            row.append(InlineKeyboardButton(categories[idx], callback_data=f"cat_{categories[idx]}"))
            if idx + 1 < len(categories):
                row.append(InlineKeyboardButton(categories[idx + 1], callback_data=f"cat_{categories[idx + 1]}"))
            keyboard.append(row)
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.message.reply_text(
            f"✅ Jenis: {transaction_type.capitalize()}\n\n"
            "Pilih kategori:",
            reply_markup=reply_markup
        )
        
        return CATEGORY
    
    async def view_charts(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Show chart options (text version for Telegram)."""
        await update.message.chat.send_action(ChatAction.TYPING)
        
        text = (
            "📊 GRAFIK LAPORAN\n\n"
            "Fitur grafik tersedia di aplikasi CLI.\n"
            "Di Telegram, gunakan perintah laporan bernomina untuk info detail:\n\n"
            "📅 /monthly_report - Laporan bulanan\n"
            "🏷️ /category_report - Pengeluaran per kategori\n"
            "📊 /summary - Ringkasan keseluruhan"
        )
        
        keyboard = [
            [InlineKeyboardButton("Kembali ke Menu Utama", callback_data="main_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(text, reply_markup=reply_markup)
    
    async def manage_transactions_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Show transaction management options."""
        await update.message.chat.send_action(ChatAction.TYPING)
        
        text = (
            "💳 KELOLA TRANSAKSI\n\n"
            "Opsi manajemen transaksi:\n\n"
            "📋 Lihat Transaksi\n"
            "✏️ Edit Transaksi (via CLI)\n"
            "❌ Hapus Transaksi (via CLI)\n"
            "🔍 Cari Transaksi (via CLI)\n\n"
            "💡 Tip: Edit/hapus/cari tersedia di aplikasi CLI"
        )
        
        # Show recent transactions
        if self.transaction_service.transactions:
            recent = self.transaction_service.transactions[-5:]
            text += "\n\n📌 5 Transaksi Terbaru:\n"
            for tx in reversed(recent):
                icon = "💰" if tx.transaction_type == "income" else "💸"
                text += f"{icon} {tx.date} - {tx.category}: Rp{format_currency(tx.amount)}\n"
        
        keyboard = [
            [InlineKeyboardButton("Kembali ke Menu Utama", callback_data="main_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(text, reply_markup=reply_markup)
    
    async def view_analytics_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Show analytics and health information."""
        await update.message.chat.send_action(ChatAction.TYPING)
        
        try:
            from core.finance_analyzer import FinanceAnalyzer
            
            analyzer = FinanceAnalyzer()
            
            # Get financial summary
            income = self.transaction_service.get_total_income()
            expense = self.transaction_service.get_total_expense()
            balance = self.transaction_service.get_balance()
            
            # Get recent months data
            from collections import defaultdict
            monthly_data = defaultdict(lambda: {"income": 0, "expense": 0})
            
            for transaction in self.transaction_service.transactions:
                month = transaction.date[:7]
                if transaction.transaction_type == "income":
                    monthly_data[month]["income"] += transaction.amount
                else:
                    monthly_data[month]["expense"] += transaction.amount
            
            for month in monthly_data:
                monthly_data[month]["balance"] = (
                    monthly_data[month]["income"] - monthly_data[month]["expense"]
                )
            
            # Analyze health
            health = analyzer.analyze_financial_health(
                total_income=income,
                total_expense=expense,
                monthly_budgets=self.budget_service.budgets,
                transactions=self.transaction_service.transactions,
                recent_months_data=dict(monthly_data)
            )
            
            # Format health status
            status_emoji = {
                "healthy": "✅",
                "warning": "⚠️",
                "critical": "❌"
            }
            
            text = (
                "💡 ANALITIK & KESEHATAN KEUANGAN\n\n"
                f"{status_emoji.get(health.status, '❓')} Status: {health.status.upper()}\n"
                f"📈 Skor Kesehatan: {health.score}/100\n"
                f"📊 Tren Pengeluaran: {health.spending_trend}\n"
                f"💰 Tingkat Tabungan: {health.savings_rate:.1f}%\n\n"
            )
            
            if health.insights:
                text += "📌 Wawasan:\n"
                for insight in health.insights[:3]:
                    text += f"• {insight}\n"
            
            if health.recommendations:
                text += "\n💡 Rekomendasi:\n"
                for rec in health.recommendations[:3]:
                    text += f"• {rec}\n"
            
        except Exception as e:
            text = f"📊 ANALITIK & ANALYTICS\n\n❌ Error: {e}\n\nGunakan /summary untuk ringkasan dasar."
        
        keyboard = [
            [InlineKeyboardButton("Kembali ke Menu Utama", callback_data="main_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(text, reply_markup=reply_markup)
    
    async def manage_recurring_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Show recurring transaction management."""
        await update.message.chat.send_action(ChatAction.TYPING)
        
        try:
            from services.recurring_service import RecurringService
            
            recurring_service = RecurringService()
            active_recurring = recurring_service.get_active_recurring()
            
            text = "📅 KELOLA TRANSAKSI BERULANG\n\n"
            
            if active_recurring:
                text += f"Anda memiliki {len(active_recurring)} transaksi berulang aktif:\n\n"
                for rec in active_recurring:
                    text += f"• {rec.name} ({rec.frequency})\n"
                    text += f"  {rec.type.capitalize()} - {rec.category}: Rp{format_currency(rec.amount)}\n\n"
            else:
                text += "Belum ada transaksi berulang.\n"
                text += "Gunakan CLI untuk menambah transaksi berulang.\n"
            
            text += "\n💡 Tip: Kelola transaksi berulang via aplikasi CLI"
        
        except Exception as e:
            text = f"📅 KELOLA TRANSAKSI BERULANG\n\n❌ Error: {e}"
        
        keyboard = [
            [InlineKeyboardButton("Kembali ke Menu Utama", callback_data="main_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(text, reply_markup=reply_markup)
    
    async def export_data_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Show data export options."""
        await update.message.chat.send_action(ChatAction.TYPING)
        
        text = (
            "📥 EKSPOR DATA\n\n"
            "Opsi ekspor data:\n\n"
            "💾 Export ke CSV - Ekspor semua transaksi\n"
            "📄 Export ke TXT - Laporan komprehensif\n"
            "📋 Export Bulan Ini - Transaksi bulan ini\n\n"
            "💡 Fitur lengkap tersedia di aplikasi CLI\n"
            "📊 File disimpan di folder aplikasi"
        )
        
        keyboard = [
            [InlineKeyboardButton("Kembali ke Menu Utama", callback_data="main_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(text, reply_markup=reply_markup)
    
    async def settings_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Show settings menu."""
        await update.message.chat.send_action(ChatAction.TYPING)
        
        text = (
            "⚙️ PENGATURAN\n\n"
            "Opsi pengaturan:\n\n"
            "🔄 Ganti Backend Database\n"
            "ℹ️ Informasi Database\n"
            "🔐 Kelola ID Chat Telegram\n"
            "🗑️ Hapus Data\n\n"
            "💡 Pengaturan lengkap tersedia di aplikasi CLI\n"
            "📱 Backend: SQLite (Recommended)"
        )
        
        keyboard = [
            [InlineKeyboardButton("Kembali ke Menu Utama", callback_data="main_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(text, reply_markup=reply_markup)

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
        """Handle menu callbacks from inline buttons (show_summary and main_menu)."""
        query = update.callback_query
        await query.answer()
        
        if query.data == "show_summary":
            # Show summary using callback_query message
            await query.message.chat.send_action(ChatAction.TYPING)
            
            income = self.transaction_service.get_total_income()
            expense = self.transaction_service.get_total_expense()
            balance = self.transaction_service.get_balance()
            
            text = (
                "📊 RINGKASAN KEUANGAN\n\n"
                f"💵 Pendapatan:   Rp{format_currency(income)}\n"
                f"💸 Pengeluaran:  Rp{format_currency(expense)}\n"
                f"💰 Saldo:        Rp{format_currency(balance)}\n"
            )
            await query.message.reply_text(text)
            
        elif query.data == "budget_status":
            # Show budget status
            await query.message.chat.send_action(ChatAction.TYPING)
            
            if not self.budget_service.budgets:
                keyboard = [
                    [InlineKeyboardButton("Kembali ke Menu Utama", callback_data="main_menu")]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                await query.message.reply_text("❌ Belum ada anggaran yang ditetapkan.", reply_markup=reply_markup)
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
                    percentage = (spending / budget * 100) if budget > 0 else 0
                    if percentage >= 80:
                        symbol = "🟠 HAMPIR HABIS"
                    elif percentage >= 50:
                        symbol = "🟡 SEDANG"
                    else:
                        symbol = "🟢 AMAN"
                    budget_text = f"[{percentage:.0f}%]"
                
                text += f"{symbol} {category}\n"
                text += f"  💰 Pengeluaran: Rp{format_currency(spending)}\n"
                text += f"  📊 Tersisa: Rp{format_currency(remaining)} {budget_text}\n\n"
            
            keyboard = [
                [InlineKeyboardButton("Kembali ke Menu Utama", callback_data="main_menu")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.message.reply_text(text, reply_markup=reply_markup)
            
        elif query.data == "set_budget":
            # Show set budget options
            await query.message.chat.send_action(ChatAction.TYPING)
            keyboard = [
                [InlineKeyboardButton("Kembali ke Menu Utama", callback_data="main_menu")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.message.reply_text(
                "📋 Untuk mengatur anggaran, gunakan perintah:\n"
                "/set_budget\n\n"
                "Anda akan diminta memasukkan:\n"
                "1. Total pendapatan bulanan\n"
                "2. Alokasi anggaran per kategori\n\n"
                "Atau menggunakan alokasi default (50-20-15-10-5)",
                reply_markup=reply_markup
            )
            
        elif query.data == "add_transaction":
            # Show transaction type selection
            keyboard = [
                [InlineKeyboardButton("💰 Income", callback_data="add_transaction_income")],
                [InlineKeyboardButton("💸 Expense", callback_data="add_transaction_expense")],
                [InlineKeyboardButton("Kembali ke Menu Utama", callback_data="main_menu")],
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.message.reply_text(
                "Pilih jenis transaksi:",
                reply_markup=reply_markup
            )
            
        elif query.data == "main_menu":
            # Show main menu with all commands
            menu_text = (
                "🏠 MENU UTAMA (13 PILIHAN)\n\n"
                "Silakan pilih perintah:\n\n"
                "1. 💰 /add_transaction - Tambah transaksi\n"
                "2. 📊 /summary - Lihat ringkasan\n"
                "3. 🏷️ /category_report - Laporan kategori\n"
                "4. 📅 /monthly_report - Laporan bulanan\n"
                "5. 📊 /charts - Grafik laporan\n"
                "6. 💳 /set_budget - Atur anggaran\n"
                "7. ✅ /budget_status - Status anggaran\n"
                "8. 🔍 /transactions - Kelola transaksi\n"
                "9. 💡 /analytics - Analitik & kesehatan\n"
                "10. 📅 /recurring - Transaksi berulang\n"
                "11. 📥 /export - Ekspor data\n"
                "12. ⚙️ /settings - Pengaturan\n"
                "13. ❓ /help - Bantuan"
            )
            
            keyboard = [
                [
                    InlineKeyboardButton("Tambah Transaksi", callback_data="add_transaction"),
                    InlineKeyboardButton("Lihat Ringkasan", callback_data="show_summary"),
                ],
                [
                    InlineKeyboardButton("Status Anggaran", callback_data="budget_status"),
                    InlineKeyboardButton("Atur Anggaran", callback_data="set_budget"),
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
        
        # Add new command handlers (menu items 5-11)
        app.add_handler(CommandHandler("charts", self.view_charts))
        app.add_handler(CommandHandler("transactions", self.manage_transactions_menu))
        app.add_handler(CommandHandler("analytics", self.view_analytics_menu))
        app.add_handler(CommandHandler("recurring", self.manage_recurring_menu))
        app.add_handler(CommandHandler("export", self.export_data_menu))
        app.add_handler(CommandHandler("settings", self.settings_menu))
        app.add_handler(CommandHandler("categories", self.categories_info))
        
        # Add transaction conversation handler
        add_transaction_handler = ConversationHandler(
            entry_points=[
                CommandHandler("add_transaction", self.start_add_transaction)
            ],
            states={
                TRANSACTION_TYPE: [
                    CallbackQueryHandler(self.transaction_type_callback, pattern="^(income|expense)$"),
                    CallbackQueryHandler(self.transaction_type_from_menu, pattern="^(add_transaction_income|add_transaction_expense)$"),
                    CallbackQueryHandler(self.exit_to_main_menu, pattern="^main_menu$")
                ],
                CATEGORY: [
                    CallbackQueryHandler(self.category_callback, pattern="^cat_.+$"),
                    MessageHandler(filters.TEXT & ~filters.COMMAND, self.category_input)
                ],
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
                BUDGET_CATEGORY: [
                    CallbackQueryHandler(self.budget_category_callback, pattern="^budget_cat_.+$"),
                    MessageHandler(filters.TEXT & ~filters.COMMAND, self.budget_category_input)
                ],
                BUDGET_TOTAL_INCOME: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.budget_total_income_input)],
                BUDGET_AMOUNT: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.budget_amount_input)],
            },
            fallbacks=[CommandHandler("cancel", self.cancel)],
        )
        app.add_handler(set_budget_handler)
        
        # Add callback handler for add_transaction button from menu
        app.add_handler(CallbackQueryHandler(self.menu_add_transaction_entry, pattern="^add_transaction$"))
        
        # Add menu callback handler for menu buttons (show_summary, main_menu, budget_status, set_budget, and add_transaction from menu)
        # Note: add_transaction is handled by the transaction conversation handler above
        app.add_handler(CallbackQueryHandler(self.menu_callback, pattern="^(show_summary|main_menu|budget_status|set_budget|add_transaction_income|add_transaction_expense)$"))
        
        # Add categories pages callback handlers
        app.add_handler(CallbackQueryHandler(self.categories_page1_callback, pattern="^categories_page_1$"))
        app.add_handler(CallbackQueryHandler(self.categories_info_page2, pattern="^categories_page_2$"))
        app.add_handler(CallbackQueryHandler(self.categories_info_page3, pattern="^categories_page_3$"))
        
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
