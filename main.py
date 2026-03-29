"""Personal Finance Manager CLI Application."""

import logging
import sys
import os
from datetime import datetime
from typing import Callable, Dict, Optional

# Set encoding to UTF-8 for Windows compatibility
if os.name == "nt":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from services.transaction_service import TransactionService
from services.report_service import ReportService
from services.budget_service import BudgetService
from services.recurring_service import RecurringService
from storage.storage_factory import StorageFactory, StorageType
from utils.validator import (
    validate_amount,
    validate_type,
    validate_category,
    validate_date,
    is_cancel_command
)
from utils.formatter import format_currency
from utils.visualizer import plot_monthly_report, plot_category_expenses, plot_budget_status, plot_yearly_report
from core.app_context import AppContext
from core.finance_analyzer import FinanceAnalyzer
import json


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("finance_manager.log"),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

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


class CancelOperation(Exception):
    """Exception raised when user cancels an operation."""
    pass


class FinanceManagerCLI:
    """CLI application for personal finance management."""
    
    def __init__(self):
        """Initialize the CLI application."""
        # Set SQLite as default backend
        StorageFactory.set_storage_type(StorageType.SQLITE)
        
        self.transaction_service = TransactionService()
        self.report_service = ReportService(self.transaction_service)
        self.budget_service = BudgetService(self.transaction_service)
        self.recurring_service = RecurringService()
        self.allowed_chat_ids_file = "allowed_chat_ids.json"
        self.custom_categories_file = "custom_categories.json"
        
        # Load custom categories
        self.custom_expense_categories = self.load_custom_categories("expense")
        self.custom_income_categories = self.load_custom_categories("income")
        
        # Initialize application context and analyzer
        self.app_context = AppContext(cache_ttl=300)
        self.finance_analyzer = FinanceAnalyzer()
        
        # Initialize menu dispatcher
        self._initialize_menu_dispatcher()
        
        logger.info("Personal Finance Manager initialized")
    
    def _initialize_menu_dispatcher(self) -> None:
        """Initialize menu action dispatcher."""
        self.menu_dispatcher: Dict[str, Callable] = {
            "0": self.display_help,
            "1": self.input_transaction,
            "2": self.view_summary,
            "3": self.view_category_report,
            "4": self.view_monthly_report,
            "5": self.view_charts,
            "6": self.manage_budget_menu,
            "7": self.manage_transactions_menu,
            "8": self.view_analytics_menu,
            "9": self.manage_recurring_menu,
            "10": self.export_data_menu,
            "11": self.settings_menu,
            "12": self._handle_exit,
        }
    
    def clear_screen(self) -> None:
        """Clear console screen."""
        import os
        os.system("cls" if os.name == "nt" else "clear")
    
    def get_financial_summary(self) -> Dict:
        """
        Get aggregated financial summary (cached if not expired).
        
        Returns:
            Dict with total_income, total_expense, balance
        """
        # Try to get from cache
        cached = self.app_context.get_cached_summary()
        if cached:
            return {
                "total_income": cached.total_income,
                "total_expense": cached.total_expense,
                "balance": cached.balance,
            }
        
        # Calculate fresh
        total_income = self.transaction_service.get_total_income()
        total_expense = self.transaction_service.get_total_expense()
        balance = self.transaction_service.get_balance()
        
        # Cache result
        self.app_context.cache_financial_summary(total_income, total_expense, balance)
        
        return {
            "total_income": total_income,
            "total_expense": total_expense,
            "balance": balance,
        }
    
    def display_financial_health(self) -> None:
        """Display financial health assessment."""
        try:
            summary = self.get_financial_summary()
            
            # Get recent months data for trend analysis
            recent_months_data = self._get_recent_months_data()
            
            # Analyze health
            health = self.finance_analyzer.analyze_financial_health(
                total_income=summary["total_income"],
                total_expense=summary["total_expense"],
                monthly_budgets=self.budget_service.budgets,
                transactions=self.transaction_service.transactions,
                recent_months_data=recent_months_data
            )
            
            # Display health report
            print("\n" + "=" * 60)
            print("💡 KESEHATAN KEUANGAN")
            print("=" * 60)
            print(f"Status: {self._format_health_status(health.status)}")
            print(f"Skor Kesehatan: {health.score}/100")
            print(f"Tren Pengeluaran: {self._format_trend(health.spending_trend)}")
            print(f"Tingkat Tabungan: {health.savings_rate:.1f}%")
            
            if health.insights:
                print("\n📊 WAWASAN:")
                for insight in health.insights:
                    print(f"  {insight}")
            
            if health.recommendations:
                print("\n💡 REKOMENDASI:")
                for rec in health.recommendations[:5]:  # Show top 5
                    print(f"  {rec}")
            
            print("=" * 60 + "\n")
            
        except Exception as e:
            logger.error(f"Error displaying financial health: {e}")
            print(f"❌ Kesalahan saat menampilkan kesehatan keuangan: {e}")
    
    def _get_recent_months_data(self) -> Dict:
        """Get recent 6 months financial data."""
        from collections import defaultdict
        
        monthly_data = defaultdict(lambda: {"income": 0, "expense": 0})
        
        for transaction in self.transaction_service.transactions:
            month = transaction.date[:7]  # YYYY-MM
            if transaction.transaction_type == "income":
                monthly_data[month]["income"] += transaction.amount
            else:
                monthly_data[month]["expense"] += transaction.amount
        
        # Add balance calculation
        for month in monthly_data:
            monthly_data[month]["balance"] = (
                monthly_data[month]["income"] - monthly_data[month]["expense"]
            )
        
        return dict(monthly_data)
    
    def _format_health_status(self, status: str) -> str:
        """Format health status with icon."""
        status_map = {
            "healthy": "✅ Sehat",
            "warning": "⚠️ Peringatan",
            "critical": "🚨 Kritis",
        }
        return status_map.get(status, status)
    
    def _format_trend(self, trend: str) -> str:
        """Format trend indicator."""
        trend_map = {
            "increasing": "📈 Meningkat",
            "decreasing": "📉 Menurun",
            "stable": "→ Stabil",
        }
        return trend_map.get(trend, trend)
    
    def _handle_exit(self) -> None:
        """Handle application exit."""
        print("\n✅ Sampai jumpa!")
        logger.info("CLI closed")
        sys.exit(0)
    
    def display_help(self) -> None:
        """Display help information about menu options."""
        print("\n" + "=" * 60)
        print("📚 BANTUAN - PANDUAN MENU")
        print("=" * 60)
        print("\n0️⃣ BANTUAN")
        print("   Menampilkan bantuan ini\n")
        print("1️⃣ TAMBAH TRANSAKSI")
        print("   Menambahkan transaksi pendapatan atau pengeluaran baru\n")
        print("2️⃣ LIHAT RINGKASAN")
        print("   Menampilkan ringkasan keuangan (total pendapatan, pengeluaran, saldo)\n")
        print("3️⃣ LAPORAN KATEGORI")
        print("   Menampilkan laporan pengeluaran berdasarkan kategori\n")
        print("4️⃣ LAPORAN BULANAN")
        print("   Menampilkan laporan bulanan untuk 6 bulan terakhir\n")
        print("5️⃣ GRAFIK LAPORAN")
        print("   Menampilkan grafik bulanan, tahunan, dan distribusi pengeluaran\n")
        print("6️⃣ KELOLA ANGGARAN")
        print("   Mengatur dan melihat status anggaran per kategori\n")
        print("7️⃣ KELOLA TRANSAKSI")
        print("   Edit, hapus, atau cari transaksi yang sudah ada\n")
        print("8️⃣ ANALITIK & KESEHATAN")
        print("   Melihat analisis kesehatan keuangan dan rekomendasi\n")
        print("9️⃣ TRANSAKSI BERULANG")
        print("   Mengelola transaksi yang berulang setiap bulan\n")
        print("🔟 EKSPOR DATA")
        print("   Mengekspor data transaksi ke format CSV atau TXT\n")
        print("1️⃣1️⃣ PENGATURAN")
        print("   Mengubah backend database, mengelola ID Telegram\n")
        print("1️⃣2️⃣ KELUAR")
        print("   Keluar dari aplikasi\n")
        print("=" * 60)
        print("\n💡 TIPS:")
        print("   • Ketik nomor opsi untuk memilih menu")
        print("   • Ketik 'batal', 'cancel', atau 'x' untuk membatalkan operasi")
        print("   • Data tersimpan otomatis di SQLite database")
        print("   • Integrasi dengan Telegram Bot untuk notifikasi\n")
    
    def display_menu(self) -> None:
        """Display main menu."""
        print("\n")
        print("=" * 50)
        print("MANAJER KEUANGAN PRIBADI")
        print("=" * 50)
        print("0. Bantuan")
        print("1. Tambah Transaksi")
        print("2. Lihat Ringkasan")
        print("3. Laporan Kategori")
        print("4. Laporan Bulanan")
        print("5. Grafik Laporan")
        print("6. Kelola Anggaran")
        print("7. Kelola Transaksi (Edit/Hapus/Cari)")
        print("8. Analitik & Analytics")
        print("9. Kelola Transaksi Berulang")
        print("10. Ekspor Data")
        print("11. Pengaturan")
        print("12. Keluar")
        print("=" * 50)
        
        # Display warnings at the bottom
        self.display_menu_warnings()
    
    def display_menu_warnings(self) -> None:
        """Display warning status at the bottom of the menu."""
        warnings = []
        current_month = self.budget_service.get_current_month()
        
        # Check for exceeded budgets
        exceeded_categories = []
        for category in self.budget_service.budgets.keys():
            if self.budget_service.is_budget_exceeded(category, current_month):
                status = self.budget_service.get_budget_status(category, current_month)
                exceeded_categories.append({
                    'category': category,
                    'budget': status['budget'],
                    'spending': status['spending'],
                    'exceeded_by': status['spending'] - status['budget']
                })
        
        # Check for deficit (expenses > income)
        total_income = self.transaction_service.get_total_income()
        total_expense = self.transaction_service.get_total_expense()
        has_deficit = total_expense > total_income
        deficit_amount = total_expense - total_income if has_deficit else 0
        
        # Display warnings if any exist
        if exceeded_categories or has_deficit:
            print("\n" + "⚠️  " * 12)
            print("⚠️  PERINGATAN".center(50))
            print("⚠️  " * 12 + "\n")
            
            if exceeded_categories:
                print("🔴 ANGGARAN TERLAMPAUI:")
                for item in exceeded_categories:
                    print(f"   • {item['category']}: Rp{format_currency(item['exceeded_by'])} lebih dari budget")
            
            if has_deficit:
                if exceeded_categories:
                    print()
                print("💔 DANA DEFISIT:")
                print(f"   • Total Pengeluaran: Rp{format_currency(total_expense)}")
                print(f"   • Total Pemasukan: Rp{format_currency(total_income)}")
                print(f"   • Defisit: Rp{format_currency(deficit_amount)}")
            
            print("\n" + "⚠️  " * 12)
    
    def input_transaction(self) -> None:
        """Handle adding a new transaction."""
        print("\n--- TAMBAH TRANSAKSI ---")
        print("💡 Ketik 'batal', 'cancel', atau 'x' untuk membatalkan")
        
        # Get type
        while True:
            print("\nPilih Jenis Transaksi:")
            print("  1. Income (Pendapatan)")
            print("  2. Expense (Pengeluaran)")
            
            type_choice = input("Pilih (1/2 atau 'batal'): ").strip()
            if is_cancel_command(type_choice):
                raise CancelOperation()
            
            if type_choice == "1":
                transaction_type = "income"
                break
            elif type_choice == "2":
                transaction_type = "expense"
                break
            else:
                print("❌ Pilihan tidak valid. Masukkan 1 atau 2.")
        
        # Get category
        while True:
            # Get all categories (predefined + custom)
            all_categories = self.get_all_categories(transaction_type)
            print("Pilih Kategori:")
            for idx, cat in enumerate(all_categories, 1):
                print(f"  {idx}. {cat}")
            
            category_choice = input("Kategori (nomor atau 'batal'): ").strip()
            if is_cancel_command(category_choice):
                raise CancelOperation()
            
            if category_choice.isdigit():
                cat_index = int(category_choice) - 1
                if 0 <= cat_index < len(all_categories):
                    category = all_categories[cat_index]
                    
                    # Check if user selected "Lainnya" (Other category)
                    # "Lainnya" is the last item in predefined categories
                    predefined = EXPENSE_CATEGORIES if transaction_type == "expense" else INCOME_CATEGORIES
                    if category == "Lainnya":
                        # Prompt for custom category
                        custom_category = input("\n✏️  Masukkan nama kategori baru: ").strip()
                        if is_cancel_command(custom_category):
                            raise CancelOperation()
                        
                        if not custom_category:
                            print("❌ Nama kategori tidak boleh kosong.")
                            continue
                        
                        # Try to add custom category
                        if self.add_custom_category(transaction_type, custom_category):
                            category = custom_category
                            print(f"✅ Kategori baru '{custom_category}' ditambahkan!")
                            break
                        else:
                            print(f"⚠️  Kategori '{custom_category}' sudah ada.")
                            category = custom_category
                            break
                    else:
                        break
                else:
                    print("❌ Nomor kategori tidak valid.")
            else:
                print("❌ Masukkan nomor kategori yang valid.")
        
        # Get amount
        while True:
            amount_input = input("Jumlah: ").strip()
            if is_cancel_command(amount_input):
                raise CancelOperation()
            is_valid, amount = validate_amount(amount_input)
            if is_valid:
                break
            print("❌ Jumlah tidak valid. Masukkan angka positif.")
        
        # Get note (optional)
        note = input("Catatan (opsional): ").strip()
        if is_cancel_command(note):
            raise CancelOperation()
        
        # Add transaction
        transaction = self.transaction_service.add_transaction(
            transaction_type=transaction_type,
            category=category,
            amount=amount,
            note=note
        )
        
        print(f"\n✅ Transaksi berhasil ditambahkan!")
        print(f"   ID: {transaction.transaction_id}")
        print(f"   Tanggal: {transaction.date}")
        print(f"   Jenis: {transaction_type.capitalize()}")
        print(f"   Kategori: {category}")
        print(f"   Jumlah: Rp{format_currency(amount)}")
    
    def view_summary(self) -> None:
        """Display financial summary."""
        report = self.report_service.generate_summary_report()
        print(report)
    
    def view_category_report(self) -> None:
        """Display category-wise expense report."""
        report = self.report_service.generate_category_report()
        print(report)
    
    def view_monthly_report(self) -> None:
        """Display monthly summary report."""
        report = self.report_service.generate_monthly_report()
        print(report)
    
    def view_charts(self) -> None:
        """Display chart menu."""
        while True:
            print("\n--- GRAFIK LAPORAN ---")
            print("1. Grafik Laporan Bulanan")
            print("2. Grafik Laporan Tahunan")
            print("3. Grafik Distribusi Pengeluaran")
            print("4. Grafik Status Anggaran")
            print("5. Kembali ke Menu Utama")
            
            choice = input("Pilih opsi: ").strip()
            
            try:
                if choice == "1":
                    print("\n📊 Membuka grafik laporan bulanan...")
                    plot_monthly_report(self.transaction_service.transactions)
                elif choice == "2":
                    print("\n📊 Membuka grafik laporan tahunan...")
                    plot_yearly_report(self.transaction_service.transactions)
                elif choice == "3":
                    print("\n📊 Membuka grafik distribusi pengeluaran...")
                    expenses = self.transaction_service.get_expenses_by_category()
                    plot_category_expenses(expenses)
                elif choice == "4":
                    print("\n📊 Membuka grafik status anggaran...")
                    budget_statuses = []
                    for category in self.budget_service.budgets.keys():
                        status = self.budget_service.get_budget_status(category)
                        budget_statuses.append(status)
                    plot_budget_status(budget_statuses)
                elif choice == "5":
                    break
                else:
                    print("❌ Opsi tidak valid.")
                input("\nTekan Enter untuk melanjutkan...")
            except CancelOperation:
                print("\n⏮️  Operasi dibatalkan.")
                logger.info("Chart view cancelled by user")
            except Exception as e:
                print(f"\n❌ Kesalahan saat membuka grafik: {e}")
                logger.exception("Chart error")
    
    def settings_menu(self) -> None:
        """Display settings menu."""
        while True:
            current_backend = StorageFactory.get_current_storage_type()
            print("\n--- PENGATURAN ---")
            print(f"Backend Database Saat Ini: {current_backend.upper()}")
            print("1. Ganti Backend Database")
            print("2. Informasi Database")
            print("3. Kelola ID Chat Telegram")
            print("4. Hapus Data")
            print("5. Kembali ke Menu Utama")
            
            choice = input("Pilih opsi: ").strip()
            
            try:
                if choice == "1":
                    self.switch_backend()
                elif choice == "2":
                    self.show_database_info()
                elif choice == "3":
                    self.manage_allowed_chat_ids()
                elif choice == "4":
                    self.delete_data_menu()
                elif choice == "5":
                    break
                else:
                    print("❌ Opsi tidak valid.")
            except Exception as e:
                print(f"\n❌ Kesalahan: {e}")
                logger.exception("Settings error")
    
    def switch_backend(self) -> None:
        """Switch database backend."""
        print("\n--- GANTI BACKEND DATABASE ---")
        current_backend = StorageFactory.get_current_storage_type()
        print(f"Backend saat ini: {current_backend.upper()}")
        print("1. SQLite (Recommended - Faster, Built-in)")
        print("2. CSV (Simple - Text-based)")
        
        choice = input("Pilih opsi (1/2): ").strip()
        
        if choice == "1":
            StorageFactory.set_storage_type(StorageType.SQLITE)
            print("\n✅ Backend diubah ke: SQLite")
            print("⚠️  Silakan restart aplikasi untuk menerapkan perubahan.")
            logger.info("Backend switched to SQLite (restart needed)")
        elif choice == "2":
            StorageFactory.set_storage_type(StorageType.CSV)
            print("\n✅ Backend diubah ke: CSV")
            print("⚠️  Silakan restart aplikasi untuk menerapkan perubahan.")
            logger.info("Backend switched to CSV (restart needed)")
        else:
            print("❌ Opsi tidak valid.")
    
    def show_database_info(self) -> None:
        """Display database information."""
        backend = StorageFactory.get_current_storage_type()
        
        print("\n--- INFORMASI DATABASE ---")
        print(f"Backend: {backend.upper()}")
        
        if backend == "sqlite":
            try:
                from storage.sqlite_storage import SQLiteStorage
                count = SQLiteStorage.get_transaction_count()
                print(f"File: finance_data.db")
                print(f"Total Transaksi: {count}")
                print(f"Budgets: {len(self.budget_service.budgets)}")
                print("\nKeuntungan SQLite:")
                print("  • 5x lebih cepat dari CSV")
                print("  • ACID compliant")
                print("  • Efisien untuk dataset besar")
                print("  • Backup mudah (copy file)")
            except Exception as e:
                print(f"❌ Error: {e}")
        else:
            print(f"File: finance_data.csv, budget.csv")
            print(f"Total Transaksi: {len(self.transaction_service.transactions)}")
            print(f"Budgets: {len(self.budget_service.budgets)}")
            print("\nKeuntungan CSV:")
            print("  • Human-readable")
            print("  • Excel compatible")
            print("  • Mudah di-export")
    
    def load_allowed_chat_ids(self) -> list:
        """Load allowed chat IDs from file."""
        if os.path.exists(self.allowed_chat_ids_file):
            try:
                with open(self.allowed_chat_ids_file, 'r') as f:
                    data = json.load(f)
                    return data.get('allowed_chat_ids', [])
            except Exception as e:
                logger.error(f"Error loading allowed chat IDs: {e}")
                return []
        return []
    
    def save_allowed_chat_ids(self, chat_ids: list) -> None:
        """Save allowed chat IDs to file."""
        try:
            with open(self.allowed_chat_ids_file, 'w') as f:
                json.dump({'allowed_chat_ids': chat_ids}, f, indent=4)
            logger.info(f"Allowed chat IDs saved: {chat_ids}")
        except Exception as e:
            logger.error(f"Error saving allowed chat IDs: {e}")
            print(f"❌ Kesalahan saat menyimpan: {e}")
    
    def manage_allowed_chat_ids(self) -> None:
        """Manage allowed Telegram chat IDs."""
        while True:
            allowed_ids = self.load_allowed_chat_ids()
            print("\n--- KELOLA ID CHAT TELEGRAM ---")
            print(f"ID Chat yang Diizinkan: {allowed_ids if allowed_ids else 'Belum ada'}")
            print("1. Tambah ID Chat")
            print("2. Hapus ID Chat")
            print("3. Lihat Daftar ID Chat")
            print("4. Kembali ke Pengaturan")
            
            choice = input("Pilih opsi: ").strip()
            
            if choice == "1":
                self.add_chat_id()
            elif choice == "2":
                self.remove_chat_id()
            elif choice == "3":
                self.view_chat_ids()
            elif choice == "4":
                break
            else:
                print("❌ Opsi tidak valid.")
            
            input("\nTekan Enter untuk melanjutkan...")
    
    def add_chat_id(self) -> None:
        """Add a new allowed chat ID."""
        print("\n--- TAMBAH ID CHAT TELEGRAM ---")
        print("💡 Masukkan ID Chat Telegram (angka)")
        
        chat_id_input = input("ID Chat: ").strip()
        
        if not chat_id_input:
            print("❌ ID Chat tidak boleh kosong.")
            return
        
        # Validate that it's a number
        if not chat_id_input.lstrip('-').isdigit():
            print("❌ ID Chat harus berupa angka.")
            return
        
        chat_id = int(chat_id_input)
        allowed_ids = self.load_allowed_chat_ids()
        
        if chat_id in allowed_ids:
            print(f"⚠️  ID Chat {chat_id} sudah ada di daftar.")
            return
        
        allowed_ids.append(chat_id)
        self.save_allowed_chat_ids(allowed_ids)
        print(f"✅ ID Chat {chat_id} berhasil ditambahkan!")
        logger.info(f"Chat ID added: {chat_id}")
    
    def remove_chat_id(self) -> None:
        """Remove an allowed chat ID."""
        print("\n--- HAPUS ID CHAT TELEGRAM ---")
        allowed_ids = self.load_allowed_chat_ids()
        
        if not allowed_ids:
            print("❌ Tidak ada ID Chat untuk dihapus.")
            return
        
        print(f"ID Chat yang ada: {allowed_ids}")
        chat_id_input = input("ID Chat yang ingin dihapus: ").strip()
        
        if not chat_id_input.lstrip('-').isdigit():
            print("❌ ID Chat harus berupa angka.")
            return
        
        chat_id = int(chat_id_input)
        
        if chat_id not in allowed_ids:
            print(f"❌ ID Chat {chat_id} tidak ditemukan.")
            return
        
        allowed_ids.remove(chat_id)
        self.save_allowed_chat_ids(allowed_ids)
        print(f"✅ ID Chat {chat_id} berhasil dihapus!")
        logger.info(f"Chat ID removed: {chat_id}")
    
    def view_chat_ids(self) -> None:
        """View all allowed chat IDs."""
        print("\n--- DAFTAR ID CHAT TELEGRAM ---")
        allowed_ids = self.load_allowed_chat_ids()
        
        if not allowed_ids:
            print("Belum ada ID Chat yang diizinkan.")
        else:
            print("ID Chat yang Diizinkan:")
            for idx, chat_id in enumerate(allowed_ids, 1):
                print(f"  {idx}. {chat_id}")
    
    def delete_data_menu(self) -> None:
        """Display delete data menu with options."""
        while True:
            print("\n--- HAPUS DATA ---")
            print("⚠️  PERINGATAN: Operasi ini tidak dapat dibatalkan!")
            print("\n1. Hapus Semua Transaksi")
            print("2. Hapus Semua Anggaran")
            print("3. Hapus Transaksi dan Anggaran (RESET TOTAL)")
            print("4. Kembali ke Pengaturan")
            
            choice = input("Pilih opsi: ").strip()
            
            if choice == "1":
                self.delete_all_transactions()
            elif choice == "2":
                self.delete_all_budgets()
            elif choice == "3":
                self.delete_all_data()
            elif choice == "4":
                break
            else:
                print("❌ Opsi tidak valid.")
            
            if choice in ["1", "2", "3"]:
                input("\nTekan Enter untuk melanjutkan...")
    
    def delete_all_transactions(self) -> None:
        """Delete all transactions after confirmation."""
        print("\n--- HAPUS SEMUA TRANSAKSI ---")
        print("⚠️  PERINGATAN: Ini akan menghapus SEMUA transaksi!")
        
        # Count transactions
        transaction_count = len(self.transaction_service.transactions)
        print(f"Transaksi yang akan dihapus: {transaction_count}")
        
        if transaction_count == 0:
            print("ℹ️  Tidak ada transaksi untuk dihapus.")
            return
        
        # Ask for confirmation
        confirmation = input("\nKetik 'HAPUS' untuk mengonfirmasi penghapusan (atau tekan Enter untuk membatalkan): ").strip()
        
        if confirmation != "HAPUS":
            print("❌ Penghapusan dibatalkan.")
            return
        
        # Delete transactions
        try:
            self.transaction_service.delete_all_transactions()
            print(f"✅ Berhasil menghapus {transaction_count} transaksi!")
            logger.info(f"Deleted all {transaction_count} transactions")
        except Exception as e:
            print(f"❌ Kesalahan saat menghapus transaksi: {e}")
            logger.error(f"Error deleting transactions: {e}")
    
    def delete_all_budgets(self) -> None:
        """Delete all budgets after confirmation."""
        print("\n--- HAPUS SEMUA ANGGARAN ---")
        print("⚠️  PERINGATAN: Ini akan menghapus SEMUA anggaran!")
        
        # Count budgets
        budget_count = len(self.budget_service.budgets)
        print(f"Anggaran yang akan dihapus: {budget_count}")
        
        if budget_count == 0:
            print("ℹ️  Tidak ada anggaran untuk dihapus.")
            return
        
        # Show which budgets will be deleted
        print("\nAnggaran yang akan dihapus:")
        for category in self.budget_service.budgets.keys():
            amount = self.budget_service.budgets[category]
            print(f"  • {category}: Rp{format_currency(amount)}")
        
        # Ask for confirmation
        confirmation = input("\nKetik 'HAPUS' untuk mengonfirmasi penghapusan (atau tekan Enter untuk membatalkan): ").strip()
        
        if confirmation != "HAPUS":
            print("❌ Penghapusan dibatalkan.")
            return
        
        # Delete budgets
        try:
            self.budget_service.delete_all_budgets()
            print(f"✅ Berhasil menghapus {budget_count} anggaran!")
            logger.info(f"Deleted all {budget_count} budgets")
        except Exception as e:
            print(f"❌ Kesalahan saat menghapus anggaran: {e}")
            logger.error(f"Error deleting budgets: {e}")
    
    def delete_all_data(self) -> None:
        """Delete all transactions and budgets after confirmation."""
        print("\n--- RESET TOTAL (HAPUS TRANSAKSI & ANGGARAN) ---")
        print("⚠️  PERINGATAN KRITIS: Ini akan menghapus SEMUA transaksi dan anggaran!")
        print("   Operasi ini TIDAK DAPAT DIBATALKAN!")
        
        transaction_count = len(self.transaction_service.transactions)
        budget_count = len(self.budget_service.budgets)
        
        print(f"\nData yang akan dihapus:")
        print(f"  • Transaksi: {transaction_count}")
        print(f"  • Anggaran: {budget_count}")
        
        if transaction_count == 0 and budget_count == 0:
            print("\nℹ️  Tidak ada data untuk dihapus.")
            return
        
        # Double confirmation
        print("\n⚠️  KONFIRMASI PERTAMA:")
        confirmation1 = input("Ketik 'SAYA YAKIN' untuk melanjutkan (atau tekan Enter untuk membatalkan): ").strip()
        
        if confirmation1 != "SAYA YAKIN":
            print("❌ Penghapusan dibatalkan.")
            return
        
        print("\n⚠️  KONFIRMASI KEDUA (Final):")
        confirmation2 = input("Ketik 'HAPUS SEMUA DATA' untuk mengonfirmasi (atau tekan Enter untuk membatalkan): ").strip()
        
        if confirmation2 != "HAPUS SEMUA DATA":
            print("❌ Penghapusan dibatalkan.")
            return
        
        # Delete all data
        try:
            self.transaction_service.delete_all_transactions()
            self.budget_service.delete_all_budgets()
            print("\n✅ Berhasil melakukan RESET TOTAL!")
            print(f"   Dihapus: {transaction_count} transaksi dan {budget_count} anggaran")
            logger.info(f"Reset total: deleted {transaction_count} transactions and {budget_count} budgets")
        except Exception as e:
            print(f"\n❌ Kesalahan saat melakukan reset: {e}")
            logger.error(f"Error resetting data: {e}")
    
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
            logger.info(f"Custom categories saved")
        except Exception as e:
            logger.error(f"Error saving custom categories: {e}")
            print(f"❌ Kesalahan saat menyimpan kategori: {e}")
    
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
    
    
    def manage_budget_menu(self) -> None:
        """Handle budget management."""
        while True:
            print("\n--- KELOLA ANGGARAN ---")
            print("1. Atur Anggaran")
            print("2. Lihat Status Anggaran")
            print("3. Kembali ke Menu Utama")
            
            choice = input("Pilih opsi: ").strip()
            
            try:
                if choice == "1":
                    self.set_budget()
                elif choice == "2":
                    self.view_budget_status()
                elif choice == "3":
                    break
                else:
                    print("❌ Opsi tidak valid.")
            except CancelOperation:
                print("\n⏮️  Operasi dibatalkan.")
                logger.info("Budget operation cancelled by user")
            input("\nTekan Enter untuk melanjutkan...")
    
    def set_budget(self) -> None:
        """Handle budget setting."""
        print("\n--- ATUR ANGGARAN ---")
        print("💡 Ketik 'batal', 'cancel', atau 'x' untuk membatalkan")
        
        # Get category from all expense categories (predefined + custom)
        while True:
            all_expense_categories = self.get_all_categories("expense")
            print("\nPilih Kategori Pengeluaran:")
            for idx, cat in enumerate(all_expense_categories, 1):
                percentage = DEFAULT_BUDGET_PERCENTAGES.get(cat, "")
                if percentage:
                    print(f"  {idx}. {cat} ({percentage}%)")
                else:
                    print(f"  {idx}. {cat}")
            
            category_choice = input("Kategori (nomor atau 'batal'): ").strip()
            if is_cancel_command(category_choice):
                raise CancelOperation()
            
            if category_choice.isdigit():
                cat_index = int(category_choice) - 1
                if 0 <= cat_index < len(all_expense_categories):
                    category = all_expense_categories[cat_index]
                    
                    # Check if user selected "Lainnya" (Other category)
                    if category == "Lainnya":
                        # Prompt for custom category
                        custom_category = input("\n✏️  Masukkan nama kategori baru: ").strip()
                        if is_cancel_command(custom_category):
                            raise CancelOperation()
                        
                        if not custom_category:
                            print("❌ Nama kategori tidak boleh kosong.")
                            continue
                        
                        # Try to add custom category
                        if self.add_custom_category("expense", custom_category):
                            category = custom_category
                            print(f"✅ Kategori baru '{custom_category}' ditambahkan!")
                            break
                        else:
                            print(f"⚠️  Kategori '{custom_category}' sudah ada.")
                            category = custom_category
                            break
                    else:
                        break
                else:
                    print("❌ Nomor kategori tidak valid.")
            else:
                print("❌ Masukkan nomor kategori yang valid.")
        
        # Get total monthly income for percentage calculation
        percentage = DEFAULT_BUDGET_PERCENTAGES.get(category)
        
        while True:
            if percentage:
                print(f"\n✅ Kategori: {category} ({percentage}%)")
                total_input = input("Total Pendapatan Bulanan (untuk menghitung anggaran otomatis): ").strip()
            else:
                print(f"\n✅ Kategori: {category} (Custom - Tidak ada persentase default)")
                total_input = input("Jumlah Anggaran Bulanan: ").strip()
            
            if is_cancel_command(total_input):
                raise CancelOperation()
            
            is_valid, total_amount = validate_amount(total_input)
            if is_valid:
                break
            print("❌ Jumlah tidak valid. Masukkan angka positif.")
        
        # Calculate budget amount
        if percentage:
            # Calculate based on percentage
            amount = int(total_amount * percentage / 100)
            print(f"\n📊 Perhitungan Anggaran:")
            print(f"   Total Pendapatan: Rp{format_currency(total_amount)}")
            print(f"   Persentase: {percentage}%")
            print(f"   Anggaran untuk {category}: Rp{format_currency(amount)}")
        else:
            # Use the entered amount directly for custom categories
            amount = total_amount
        
        self.budget_service.set_budget(category, amount)
        print(f"\n✅ Anggaran berhasil diatur: Rp{format_currency(amount)} untuk {category}")
    
    def view_budget_status(self) -> None:
        """Display budget status."""
        month_input = input("\nMasukkan bulan (YYYY-MM) atau tekan Enter untuk bulan ini (atau ketik 'batal' untuk membatalkan): ").strip()
        
        if is_cancel_command(month_input):
            raise CancelOperation()
        
        if month_input:
            if not validate_date(f"{month_input}-01"):
                print("❌ Format tanggal tidak valid. Gunakan YYYY-MM.")
                return
        else:
            month_input = None
        
        report = self.budget_service.generate_budget_report(month_input)
        print(report)
    
    # ============ NEW FEATURE: MANAGE TRANSACTIONS (EDIT/DELETE/SEARCH) ============
    
    def manage_transactions_menu(self) -> None:
        """Display transaction management menu."""
        while True:
            print("\n--- KELOLA TRANSAKSI ---")
            print("1. Lihat Daftar Transaksi")
            print("2. Edit Transaksi")
            print("3. Hapus Transaksi")
            print("4. Cari/Filter Transaksi")
            print("5. Kembali ke Menu Utama")
            
            choice = input("Pilih opsi: ").strip()
            
            try:
                if choice == "1":
                    self.list_transactions()
                elif choice == "2":
                    self.edit_transaction()
                elif choice == "3":
                    self.delete_transaction()
                elif choice == "4":
                    self.search_filter_menu()
                elif choice == "5":
                    break
                else:
                    print("❌ Opsi tidak valid.")
            except CancelOperation:
                print("\n⏮️  Operasi dibatalkan.")
            except Exception as e:
                print(f"❌ Kesalahan: {e}")
                logger.error(f"Error in manage_transactions_menu: {e}")
            
            input("\nTekan Enter untuk melanjutkan...")
    
    def list_transactions(self) -> None:
        """Display list of all transactions with IDs."""
        transactions = sorted(self.transaction_service.transactions, key=lambda t: t.date, reverse=True)
        
        if not transactions:
            print("\n❌ Tidak ada transaksi untuk ditampilkan.")
            return
        
        print("\n" + "=" * 100)
        print(f"{'ID':<5} {'Tanggal':<12} {'Jenis':<10} {'Kategori':<20} {'Jumlah':>15} {'Catatan':<30}")
        print("=" * 100)
        
        for t in transactions:
            jenis = t.transaction_type.capitalize()
            catatan = t.note[:27] + "..." if len(t.note) > 30 else t.note
            print(f"{t.transaction_id:<5} {t.date:<12} {jenis:<10} {t.category:<20} Rp{format_currency(t.amount):>13} {catatan:<30}")
        
        print("=" * 100)
    
    def edit_transaction(self) -> None:
        """Edit an existing transaction."""
        print("\n--- EDIT TRANSAKSI ---")
        
        self.list_transactions()
        
        transaction_id = input("\nMasukkan ID Transaksi yang ingin diubah (atau 'batal'): ").strip()
        if is_cancel_command(transaction_id):
            raise CancelOperation()
        
        if not transaction_id.isdigit():
            print("❌ ID harus berupa angka.")
            return
        
        transaction_id = int(transaction_id)
        transaction = self.transaction_service.get_transaction_by_id(transaction_id)
        
        if not transaction:
            print(f"❌ Transaksi dengan ID {transaction_id} tidak ditemukan.")
            return
        
        print(f"\n✅ Transaksi ditemukan:")
        print(f"   Tanggal: {transaction.date}")
        print(f"   Jenis: {transaction.transaction_type.capitalize()}")
        print(f"   Kategori: {transaction.category}")
        print(f"   Jumlah: Rp{format_currency(transaction.amount)}")
        print(f"   Catatan: {transaction.note}")
        
        print("\n💡 Ketik nilai baru atau tekan Enter untuk skip field, ketik 'batal' untuk membatalkan")
        
        updates = {}
        
        # Edit Tanggal
        new_date = input("Tanggal baru (YYYY-MM-DD) [tekan Enter skip]: ").strip()
        if new_date and not is_cancel_command(new_date):
            if validate_date(new_date):
                updates["date"] = new_date
            else:
                print("❌ Format tanggal tidak valid.")
                return
        elif is_cancel_command(new_date):
            raise CancelOperation()
        
        # Edit Kategori
        new_category = input("Kategori baru [tekan Enter skip]: ").strip()
        if new_category and not is_cancel_command(new_category):
            updates["category"] = new_category
        elif is_cancel_command(new_category):
            raise CancelOperation()
        
        # Edit Jumlah
        new_amount_input = input("Jumlah baru [tekan Enter skip]: ").strip()
        if new_amount_input and not is_cancel_command(new_amount_input):
            is_valid, amount = validate_amount(new_amount_input)
            if is_valid:
                updates["amount"] = amount
            else:
                print("❌ Jumlah tidak valid.")
                return
        elif is_cancel_command(new_amount_input):
            raise CancelOperation()
        
        # Edit Catatan
        new_note = input("Catatan baru [tekan Enter skip]: ").strip()
        if new_note and not is_cancel_command(new_note):
            updates["note"] = new_note
        elif is_cancel_command(new_note):
            raise CancelOperation()
        
        if not updates:
            print("⚠️  Tidak ada perubahan.")
            return
        
        # Confirm and update
        confirmation = input("\nKetik 'UBAH' untuk mengonfirmasi perubahan (atau tekan Enter untuk batal): ").strip()
        if confirmation != "UBAH":
            print("❌ Perubahan dibatalkan.")
            return
        
        if self.transaction_service.edit_transaction(transaction_id, **updates):
            print(f"\n✅ Transaksi {transaction_id} berhasil diubah!")
            logger.info(f"Transaction {transaction_id} edited: {updates}")
        else:
            print(f"❌ Gagal mengubah transaksi {transaction_id}.")
    
    def delete_transaction(self) -> None:
        """Delete an existing transaction."""
        print("\n--- HAPUS TRANSAKSI ---")
        
        self.list_transactions()
        
        transaction_id = input("\nMasukkan ID Transaksi yang ingin dihapus (atau 'batal'): ").strip()
        if is_cancel_command(transaction_id):
            raise CancelOperation()
        
        if not transaction_id.isdigit():
            print("❌ ID harus berupa angka.")
            return
        
        transaction_id = int(transaction_id)
        transaction = self.transaction_service.get_transaction_by_id(transaction_id)
        
        if not transaction:
            print(f"❌ Transaksi dengan ID {transaction_id} tidak ditemukan.")
            return
        
        print(f"\n⚠️  Transaksi yang akan dihapus:")
        print(f"   Tanggal: {transaction.date}")
        print(f"   Jenis: {transaction.transaction_type.capitalize()}")
        print(f"   Kategori: {transaction.category}")
        print(f"   Jumlah: Rp{format_currency(transaction.amount)}")
        print(f"   Catatan: {transaction.note}")
        
        confirmation = input("\nKetik 'HAPUS' untuk mengonfirmasi penghapusan (atau tekan Enter untuk batal): ").strip()
        if confirmation != "HAPUS":
            print("❌ Penghapusan dibatalkan.")
            return
        
        if self.transaction_service.delete_transaction(transaction_id):
            print(f"\n✅ Transaksi {transaction_id} berhasil dihapus!")
            logger.info(f"Transaction {transaction_id} deleted")
        else:
            print(f"❌ Gagal menghapus transaksi {transaction_id}.")
    
    def search_filter_menu(self) -> None:
        """Display search and filter menu."""
        while True:
            print("\n--- CARI/FILTER TRANSAKSI ---")
            print("1. Cari Berdasarkan Keyword")
            print("2. Filter Berdasarkan Kategori")
            print("3. Filter Berdasarkan Jenis (Income/Expense)")
            print("4. Filter Berdasarkan Rentang Tanggal")
            print("5. Filter Berdasarkan Rentang Jumlah")
            print("6. Kembali")
            
            choice = input("Pilih opsi: ").strip()
            
            try:
                if choice == "1":
                    self.search_by_keyword()
                elif choice == "2":
                    self.filter_by_category()
                elif choice == "3":
                    self.filter_by_type()
                elif choice == "4":
                    self.filter_by_date_range()
                elif choice == "5":
                    self.filter_by_amount_range()
                elif choice == "6":
                    break
                else:
                    print("❌ Opsi tidak valid.")
            except CancelOperation:
                print("⏮️  Dibatalkan.")
            
            input("\nTekan Enter untuk melanjutkan...")
    
    def search_by_keyword(self) -> None:
        """Search transactions by keyword."""
        print("\n--- CARI BERDASARKAN KEYWORD ---")
        keyword = input("Masukkan keyword (kategori atau catatan): ").strip()
        
        if not keyword:
            print("❌ Keyword tidak boleh kosong.")
            return
        
        results = self.transaction_service.search_by_keyword(keyword)
        self._display_transaction_results(results, f"Cari: '{keyword}'")
    
    def filter_by_category(self) -> None:
        """Filter transactions by category."""
        print("\n--- FILTER BERDASARKAN KATEGORI ---")
        
        categories = set(t.category for t in self.transaction_service.transactions)
        if not categories:
            print("❌ Tidak ada kategori ditemukan.")
            return
        
        print("Kategori yang tersedia:")
        for i, cat in enumerate(sorted(categories), 1):
            print(f"  {i}. {cat}")
        
        choice = input("Pilih nomor kategori: ").strip()
        if not choice.isdigit():
            print("❌ Masukkan nomor yang valid.")
            return
        
        idx = int(choice) - 1
        categories_list = sorted(categories)
        if 0 <= idx < len(categories_list):
            category = categories_list[idx]
            results = self.transaction_service.filter_transactions(category=category)
            self._display_transaction_results(results, f"Filter: Kategori '{category}'")
        else:
            print("❌ Nomor tidak valid.")
    
    def filter_by_type(self) -> None:
        """Filter transactions by type."""
        print("\n--- FILTER BERDASARKAN JENIS ---")
        print("1. Income (Pemasukan)")
        print("2. Expense (Pengeluaran)")
        
        choice = input("Pilih jenis: ").strip()
        
        if choice == "1":
            results = self.transaction_service.filter_transactions(transaction_type="income")
            label = "Income (Pemasukan)"
        elif choice == "2":
            results = self.transaction_service.filter_transactions(transaction_type="expense")
            label = "Expense (Pengeluaran)"
        else:
            print("❌ Opsi tidak valid.")
            return
        
        self._display_transaction_results(results, f"Filter: Jenis '{label}'")
    
    def filter_by_date_range(self) -> None:
        """Filter transactions by date range."""
        print("\n--- FILTER BERDASARKAN RENTANG TANGGAL ---")
        
        from_date = input("Dari tanggal (YYYY-MM-DD): ").strip()
        if not validate_date(from_date):
            print("❌ Format tanggal tidak valid.")
            return
        
        to_date = input("Sampai tanggal (YYYY-MM-DD): ").strip()
        if not validate_date(to_date):
            print("❌ Format tanggal tidak valid.")
            return
        
        results = self.transaction_service.filter_transactions(from_date=from_date, to_date=to_date)
        self._display_transaction_results(results, f"Filter: {from_date} s/d {to_date}")
    
    def filter_by_amount_range(self) -> None:
        """Filter transactions by amount range."""
        print("\n--- FILTER BERDASARKAN RENTANG JUMLAH ---")
        
        min_input = input("Jumlah minimum: ").strip()
        is_valid, min_amount = validate_amount(min_input)
        if not is_valid:
            print("❌ Jumlah tidak valid.")
            return
        
        max_input = input("Jumlah maksimum: ").strip()
        is_valid, max_amount = validate_amount(max_input)
        if not is_valid:
            print("❌ Jumlah tidak valid.")
            return
        
        results = self.transaction_service.filter_transactions(min_amount=min_amount, max_amount=max_amount)
        self._display_transaction_results(results, f"Filter: Rp{format_currency(min_amount)} - Rp{format_currency(max_amount)}")
    
    def _display_transaction_results(self, transactions: list, title: str) -> None:
        """Display search/filter results."""
        if not transactions:
            print(f"\n❌ Tidak ada transaksi ditemukan untuk '{title}'.")
            return
        
        print("\n" + "=" * 100)
        print(f"📊 {title} ({len(transactions)} transaksi)")
        print("=" * 100)
        print(f"{'ID':<5} {'Tanggal':<12} {'Jenis':<10} {'Kategori':<20} {'Jumlah':>15} {'Catatan':<30}")
        print("-" * 100)
        
        total = 0
        for t in transactions:
            jenis = t.transaction_type.capitalize()
            catatan = t.note[:27] + "..." if len(t.note) > 30 else t.note
            print(f"{t.transaction_id:<5} {t.date:<12} {jenis:<10} {t.category:<20} Rp{format_currency(t.amount):>13} {catatan:<30}")
            if t.transaction_type == "expense":
                total += t.amount
        
        print("=" * 100)
        print(f"Total Pengeluaran: Rp{format_currency(total)}")
    
    # ============ NEW FEATURE: ANALYTICS MENU ============
    
    def view_analytics_menu(self) -> None:
        """Display analytics menu."""
        while True:
            print("\n--- ANALITIK & INSIGHTS ---")
            print("1. Statistik Keuangan")
            print("2. Analisa Tren (6 Bulan)")
            print("3. Laporan Prediksi Bulan Depan")
            print("4. Kembali ke Menu Utama")
            
            choice = input("Pilih opsi: ").strip()
            
            try:
                if choice == "1":
                    print(self.report_service.generate_statistics_report())
                elif choice == "2":
                    print(self.report_service.generate_trend_report(months=6))
                elif choice == "3":
                    self.view_forecast_report()
                elif choice == "4":
                    break
                else:
                    print("❌ Opsi tidak valid.")
            except Exception as e:
                print(f"❌ Kesalahan: {e}")
                logger.error(f"Error in analytics: {e}")
            
            input("\nTekan Enter untuk melanjutkan...")
    
    def view_forecast_report(self) -> None:
        """Display forecast report."""
        forecast = self.transaction_service.forecast_next_month()
        
        if not forecast:
            print("\n❌ Tidak ada data untuk forecast.")
            return
        
        print("\n" + "=" * 70)
        print("PREDIKSI PENGELUARAN BULAN DEPAN")
        print("=" * 70)
        print(f"{'Kategori':<25} {'Estimasi':>15} {'Trend':>20}")
        print("-" * 70)
        
        total = 0
        for category, amount in forecast.items():
            trend = "→ Stabil"
            total += amount
            print(f"{category:<25} Rp{format_currency(amount):>13} {trend:>20}")
        
        print("=" * 70)
        print(f"{'TOTAL ESTIMASI':<25} Rp{format_currency(total):>13}")
        print("=" * 70)
    
    # ============ NEW FEATURE: RECURRING TRANSACTIONS ============
    
    def manage_recurring_menu(self) -> None:
        """Display recurring transactions menu."""
        while True:
            print("\n--- KELOLA TRANSAKSI BERULANG ---")
            print("1. Tambah Transaksi Berulang")
            print("2. Lihat Daftar Transaksi Berulang")
            print("3. Edit Transaksi Berulang")
            print("4. Hapus Transaksi Berulang")
            print("5. Lihat Ringkasan Transaksi Berulang")
            print("6. Kembali ke Menu Utama")
            
            choice = input("Pilih opsi: ").strip()
            
            try:
                if choice == "1":
                    self.add_recurring_transaction()
                elif choice == "2":
                    self.list_recurring_transactions()
                elif choice == "3":
                    self.edit_recurring_transaction()
                elif choice == "4":
                    self.delete_recurring_transaction()
                elif choice == "5":
                    self.view_recurring_summary()
                elif choice == "6":
                    break
                else:
                    print("❌ Opsi tidak valid.")
            except CancelOperation:
                print("⏮️  Dibatalkan.")
            except Exception as e:
                print(f"❌ Kesalahan: {e}")
                logger.error(f"Error in recurring menu: {e}")
            
            input("\nTekan Enter untuk melanjutkan...")
    
    def add_recurring_transaction(self) -> None:
        """Add a new recurring transaction."""
        print("\n--- TAMBAH TRANSAKSI BERULANG ---")
        print("💡 Ketik 'batal', 'cancel', atau 'x' untuk membatalkan")
        
        # Get name
        name = input("Nama Transaksi (misal: Gaji Bulanan): ").strip()
        if is_cancel_command(name):
            raise CancelOperation()
        
        # Get type
        while True:
            ttype = input("Jenis (income/expense): ").strip()
            if is_cancel_command(ttype):
                raise CancelOperation()
            if validate_type(ttype):
                break
            print("❌ Tipe tidak valid.")
        
        # Get category
        all_categories = self.get_all_categories(ttype)
        print("Pilih Kategori:")
        for i, cat in enumerate(all_categories, 1):
            print(f"  {i}. {cat}")
        
        while True:
            cat_choice = input("Kategori (nomor): ").strip()
            if is_cancel_command(cat_choice):
                raise CancelOperation()
            if cat_choice.isdigit():
                idx = int(cat_choice) - 1
                if 0 <= idx < len(all_categories):
                    category = all_categories[idx]
                    if category == "Lainnya":
                        custom = input("Nama kategori baru: ").strip()
                        if is_cancel_command(custom):
                            raise CancelOperation()
                        category = custom
                        self.add_custom_category(ttype, custom)
                    break
        
        # Get amount
        while True:
            amount_input = input("Jumlah: ").strip()
            if is_cancel_command(amount_input):
                raise CancelOperation()
            is_valid, amount = validate_amount(amount_input)
            if is_valid:
                break
            print("❌ Jumlah tidak valid.")
        
        # Get frequency
        print("\nFrekuensi:")
        print("1. Harian")
        print("2. Mingguan")
        print("3. Bulanan")
        print("4. Tahunan")
        
        freq_map = {"1": "daily", "2": "weekly", "3": "monthly", "4": "yearly"}
        while True:
            freq_choice = input("Pilih frekuensi (1-4): ").strip()
            if is_cancel_command(freq_choice):
                raise CancelOperation()
            if freq_choice in freq_map:
                frequency = freq_map[freq_choice]
                break
            print("❌ Pilihan tidak valid.")
        
        # Get note
        note = input("Catatan (opsional): ").strip()
        if is_cancel_command(note):
            raise CancelOperation()
        
        # Confirm
        confirmation = input("\nKetik 'BUAT' untuk membuat transaksi berulang: ").strip()
        if confirmation != "BUAT":
            print("❌ Dibatalkan.")
            return
        
        recurring = self.recurring_service.add_recurring_transaction(
            name=name,
            transaction_type=ttype,
            category=category,
            amount=amount,
            frequency=frequency,
            note=note
        )
        
        print(f"\n✅ Transaksi berulang berhasil dibuat!")
        print(f"   ID: {recurring.recurring_id}")
        print(f"   Nama: {recurring.name}")
        print(f"   Frekuensi: {recurring.frequency}")
    
    def list_recurring_transactions(self) -> None:
        """Display list of recurring transactions."""
        recurring_list = self.recurring_service.recurring_transactions
        
        if not recurring_list:
            print("\n❌ Tidak ada transaksi berulang.")
            return
        
        print("\n" + "=" * 120)
        print(f"{'ID':<5} {'Nama':<20} {'Jenis':<10} {'Kategori':<15} {'Jumlah':>12} {'Frekuensi':<10} {'Status':<8}")
        print("=" * 120)
        
        for r in recurring_list:
            status = "✅ Aktif" if r.is_active else "⭕ Nonaktif"
            print(f"{r.recurring_id:<5} {r.name:<20} {r.transaction_type.capitalize():<10} {r.category:<15} Rp{format_currency(r.amount):>10} {r.frequency:<10} {status:<8}")
        
        print("=" * 120)
    
    def edit_recurring_transaction(self) -> None:
        """Edit a recurring transaction."""
        print("\n--- EDIT TRANSAKSI BERULANG ---")
        self.list_recurring_transactions()
        
        recurring_id = input("\nMasukkan ID Transaksi Berulang (atau 'batal'): ").strip()
        if is_cancel_command(recurring_id):
            raise CancelOperation()
        
        if not recurring_id.isdigit():
            print("❌ ID harus berupa angka.")
            return
        
        recurring = self.recurring_service.get_recurring_by_id(int(recurring_id))
        if not recurring:
            print(f"❌ Transaksi berulang dengan ID {recurring_id} tidak ditemukan.")
            return
        
        print(f"\n✅ Transaksi ditemukan: {recurring.name}")
        
        updates = {}
        
        new_name = input("Nama baru [tekan Enter skip]: ").strip()
        if new_name and not is_cancel_command(new_name):
            updates["name"] = new_name
        
        new_amount = input("Jumlah baru [tekan Enter skip]: ").strip()
        if new_amount and not is_cancel_command(new_amount):
            is_valid, amount = validate_amount(new_amount)
            if is_valid:
                updates["amount"] = amount
        
        if not updates:
            print("⚠️  Tidak ada perubahan.")
            return
        
        confirmation = input("\nKetik 'UBAH' untuk mengonfirmasi: ").strip()
        if confirmation != "UBAH":
            print("❌ Dibatalkan.")
            return
        
        if self.recurring_service.edit_recurring_transaction(int(recurring_id), **updates):
            print(f"\n✅ Transaksi berulang berhasil diubah!")
    
    def delete_recurring_transaction(self) -> None:
        """Delete a recurring transaction."""
        print("\n--- HAPUS TRANSAKSI BERULANG ---")
        self.list_recurring_transactions()
        
        recurring_id = input("\nMasukkan ID Transaksi Berulang yang ingin dihapus (atau 'batal'): ").strip()
        if is_cancel_command(recurring_id):
            raise CancelOperation()
        
        if not recurring_id.isdigit():
            print("❌ ID harus berupa angka.")
            return
        
        recurring = self.recurring_service.get_recurring_by_id(int(recurring_id))
        if not recurring:
            print(f"❌ Transaksi berulang dengan ID {recurring_id} tidak ditemukan.")
            return
        
        print(f"\n⚠️  Akan dihapus: {recurring.name}")
        
        confirmation = input("Ketik 'HAPUS' untuk mengonfirmasi: ").strip()
        if confirmation != "HAPUS":
            print("❌ Dibatalkan.")
            return
        
        if self.recurring_service.delete_recurring_transaction(int(recurring_id)):
            print(f"\n✅ Transaksi berulang berhasil dihapus!")
    
    def view_recurring_summary(self) -> None:
        """Display recurring transactions summary."""
        summary = self.recurring_service.get_recurring_summary()
        
        print("\n" + "=" * 60)
        print("RINGKASAN TRANSAKSI BERULANG")
        print("=" * 60)
        print(f"Total Transaksi Berulang: {summary['total_recurring']}")
        print(f"Transaksi Aktif: {summary['total_active']}")
        print(f"\n📊 ESTIMASI BULANAN:")
        print(f"Pemasukan Berulang: Rp{format_currency(summary['estimated_monthly_income'])}")
        print(f"Pengeluaran Berulang: Rp{format_currency(summary['estimated_monthly_expense'])}")
        print(f"Saldo Bulanan: Rp{format_currency(summary['estimated_monthly_balance'])}")
        print("=" * 60)
    
    # ============ NEW FEATURE: DATA EXPORT ============
    
    def export_data_menu(self) -> None:
        """Display data export menu."""
        while True:
            print("\n--- EKSPOR DATA ---")
            print("1. Ekspor Semua Transaksi ke CSV")
            print("2. Ekspor Laporan Lengkap ke Text")
            print("3. Ekspor Transaksi Bulan Ini ke CSV")
            print("4. Kembali ke Menu Utama")
            
            choice = input("Pilih opsi: ").strip()
            
            try:
                if choice == "1":
                    self.export_all_transactions()
                elif choice == "2":
                    self.export_full_report()
                elif choice == "3":
                    self.export_current_month()
                elif choice == "4":
                    break
                else:
                    print("❌ Opsi tidak valid.")
            except Exception as e:
                print(f"❌ Kesalahan: {e}")
                logger.error(f"Error in export: {e}")
            
            input("\nTekan Enter untuk melanjutkan...")
    
    def export_all_transactions(self) -> None:
        """Export all transactions to CSV."""
        print("\n--- EKSPOR SEMUA TRANSAKSI ---")
        
        filename = input("Nama file (default: export_transactions.csv): ").strip()
        if not filename:
            filename = "export_transactions.csv"
        
        if self.report_service.export_to_csv(filename):
            print(f"✅ Berhasil mengekspor ke: {filename}")
            print(f"   Total transaksi: {len(self.transaction_service.transactions)}")
        else:
            print("❌ Gagal mengekspor data.")
    
    def export_full_report(self) -> None:
        """Export full report to text file."""
        print("\n--- EKSPOR LAPORAN LENGKAP ---")
        
        filename = input("Nama file (default: export_report.txt): ").strip()
        if not filename:
            filename = "export_report.txt"
        
        if self.report_service.export_to_text(filename):
            print(f"✅ Berhasil mengekspor ke: {filename}")
        else:
            print("❌ Gagal mengekspor laporan.")
    
    def export_current_month(self) -> None:
        """Export current month transactions to CSV."""
        print("\n--- EKSPOR TRANSAKSI BULAN INI ---")
        
        current_month = self.budget_service.get_current_month()
        filename = f"transactions_{current_month}.csv"
        
        if self.report_service.export_transactions_by_month(current_month, filename):
            print(f"✅ Berhasil mengekspor ke: {filename}")
        else:
            print("❌ Gagal mengekspor transaksi bulan ini.")
    
    def run(self) -> None:
        """Main CLI loop using dispatcher pattern."""
        print("\n🚀 Manajer Keuangan Pribadi Dimulai")
        print("📊 Backend: SQLite (Default)")
        logger.info("CLI started with SQLite backend")
        
        while True:
            self.display_menu()
            
            # Show quarterly health check every 10 operations
            import random
            if random.random() < 0.1:
                self.display_financial_health()
            
            choice = input("Pilih opsi: ").strip()
            
            try:
                # Use dispatcher pattern
                if choice in self.menu_dispatcher:
                    action = self.menu_dispatcher[choice]
                    action()
                else:
                    print("❌ Opsi tidak valid. Coba lagi.")
            
            except CancelOperation:
                print("\n⏮️  Operasi dibatalkan. Kembali ke menu utama.")
                logger.info("Operation cancelled by user")
            except KeyboardInterrupt:
                print("\n\n⚠️ Aplikasi dihentikan oleh pengguna.")
                logger.info("CLI interrupted by user")
                break
            except SystemExit:
                # Allow sys.exit() to work
                raise
            except Exception as e:
                print(f"\n❌ Terjadi kesalahan: {e}")
                logger.exception("Unexpected error")
            
            # Skip input prompt on exit
            if choice != "12":
                input("\nTekan Enter untuk melanjutkan...")


def main():
    """Entry point."""
    try:
        app = FinanceManagerCLI()
        app.run()
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        print("\n❌ Kesalahan fatal: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
