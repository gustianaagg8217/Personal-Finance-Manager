"""Personal Finance Manager CLI Application."""

import logging
import sys
from datetime import datetime

from services.transaction_service import TransactionService
from services.report_service import ReportService
from services.budget_service import BudgetService
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
        logger.info("Personal Finance Manager initialized")
    
    def clear_screen(self) -> None:
        """Clear console screen."""
        import os
        os.system("cls" if os.name == "nt" else "clear")
    
    def display_menu(self) -> None:
        """Display main menu."""
        print("\n")
        print("=" * 50)
        print("MANAJER KEUANGAN PRIBADI")
        print("=" * 50)
        print("1. Tambah Transaksi")
        print("2. Lihat Ringkasan")
        print("3. Laporan Kategori")
        print("4. Laporan Bulanan")
        print("5. Grafik Laporan")
        print("6. Kelola Anggaran")
        print("7. Pengaturan")
        print("8. Keluar")
        print("=" * 50)
    
    def input_transaction(self) -> None:
        """Handle adding a new transaction."""
        print("\n--- TAMBAH TRANSAKSI ---")
        print("💡 Ketik 'batal', 'cancel', atau 'x' untuk membatalkan")
        
        # Get type
        while True:
            transaction_type = input("Jenis transaksi (income/expense): ").strip()
            if is_cancel_command(transaction_type):
                raise CancelOperation()
            if validate_type(transaction_type):
                break
            print("❌ Tipe tidak valid. Masukkan 'income' atau 'expense'.")
        
        # Get category
        while True:
            category = input("Kategori: ").strip()
            if is_cancel_command(category):
                raise CancelOperation()
            if validate_category(category):
                break
            print("❌ Kategori tidak boleh kosong.")
        
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
            print("3. Kembali ke Menu Utama")
            
            choice = input("Pilih opsi: ").strip()
            
            try:
                if choice == "1":
                    self.switch_backend()
                elif choice == "2":
                    self.show_database_info()
                elif choice == "3":
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
        
        category = input("Kategori: ").strip()
        if is_cancel_command(category):
            raise CancelOperation()
        if not validate_category(category):
            print("❌ Kategori tidak boleh kosong.")
            return
        
        while True:
            amount_input = input("Jumlah Anggaran Bulanan: ").strip()
            if is_cancel_command(amount_input):
                raise CancelOperation()
            is_valid, amount = validate_amount(amount_input)
            if is_valid:
                break
            print("❌ Jumlah tidak valid. Masukkan angka positif.")
        
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
    
    def run(self) -> None:
        """Main CLI loop."""
        print("\n🚀 Manajer Keuangan Pribadi Dimulai")
        print("📊 Backend: SQLite (Default)")
        logger.info("CLI started with SQLite backend")
        
        while True:
            self.display_menu()
            choice = input("Pilih opsi: ").strip()
            
            try:
                if choice == "1":
                    self.input_transaction()
                elif choice == "2":
                    self.view_summary()
                elif choice == "3":
                    self.view_category_report()
                elif choice == "4":
                    self.view_monthly_report()
                elif choice == "5":
                    self.view_charts()
                elif choice == "6":
                    self.manage_budget_menu()
                elif choice == "7":
                    self.settings_menu()
                elif choice == "8":
                    print("\n✅ Sampai jumpa!")
                    logger.info("CLI closed")
                    break
                else:
                    print("❌ Opsi tidak valid. Coba lagi.")
            
            except CancelOperation:
                print("\n⏮️  Operasi dibatalkan. Kembali ke menu utama.")
                logger.info("Operation cancelled by user")
            except KeyboardInterrupt:
                print("\n\n⚠️ Aplikasi dihentikan oleh pengguna.")
                logger.info("CLI interrupted by user")
                break
            except Exception as e:
                print(f"\n❌ Terjadi kesalahan: {e}")
                logger.exception("Unexpected error")
            
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
