"""Report generation service."""

import logging
from collections import defaultdict
import csv
from datetime import datetime

from services.transaction_service import TransactionService
from utils.formatter import format_currency, format_percentage, highlight_warning


logger = logging.getLogger(__name__)


class ReportService:
    """Service for generating financial reports."""
    
    def __init__(self, transaction_service: TransactionService):
        """
        Initialize report service.
        
        Args:
            transaction_service: TransactionService instance
        """
        self.service = transaction_service
    
    def generate_summary_report(self) -> str:
        """
        Generate summary report.
        
        Returns:
            Formatted summary report
        """
        income = self.service.get_total_income()
        expense = self.service.get_total_expense()
        balance = self.service.get_balance()
        
        report = "\n" + "=" * 50 + "\n"
        report += "RINGKASAN KEUANGAN\n"
        report += "=" * 50 + "\n"
        report += f"Total Pendapatan:   Rp{format_currency(income)}\n"
        report += f"Total Pengeluaran:  Rp{format_currency(expense)}\n"
        report += f"Saldo:              Rp{format_currency(balance)}\n"
        report += "=" * 50 + "\n"
        
        return report
    
    def generate_category_report(self) -> str:
        """
        Generate category-wise expense report.
        
        Returns:
            Formatted category report
        """
        expenses = self.service.get_expenses_by_category()
        total_expense = self.service.get_total_expense()
        
        if not expenses:
            return "\nTidak ada catatan pengeluaran.\n"
        
        report = "\n" + "=" * 60 + "\n"
        report += "PENGELUARAN BERDASARKAN KATEGORI\n"
        report += "=" * 60 + "\n"
        report += f"{'Kategori':<20} {'Jumlah':>15} {'Persentase':>15}\n"
        report += "-" * 60 + "\n"
        
        most_expensive = None
        max_amount = 0
        
        for category, amount in expenses.items():
            percentage = format_percentage(amount, total_expense)
            report += f"{category:<20} Rp{format_currency(amount):>13} {percentage:>15}\n"
            
            if amount > max_amount:
                max_amount = amount
                most_expensive = category
        
        report += "-" * 60 + "\n"
        report += f"{'TOTAL':<20} Rp{format_currency(total_expense):>13}\n"
        report += "=" * 60 + "\n"
        
        if most_expensive:
            report += f"⭐ Kategori termahal: {most_expensive} (Rp{format_currency(max_amount)})\n"
        
        return report
    
    def generate_monthly_report(self) -> str:
        """
        Generate monthly summary report.
        
        Returns:
            Formatted monthly report
        """
        # Group transactions by month
        monthly_data = defaultdict(lambda: {"income": 0, "expense": 0})
        
        for transaction in self.service.transactions:
            month = transaction.date[:7]  # YYYY-MM
            if transaction.transaction_type == "income":
                monthly_data[month]["income"] += transaction.amount
            else:
                monthly_data[month]["expense"] += transaction.amount
        
        if not monthly_data:
            return "\nTidak ada catatan transaksi.\n"
        
        report = "\n" + "=" * 70 + "\n"
        report += "LAPORAN BULANAN\n"
        report += "=" * 70 + "\n"
        report += f"{'Bulan':<12} {'Pendapatan':>15} {'Pengeluaran':>15} {'Saldo':>15}\n"
        report += "-" * 70 + "\n"
        
        for month in sorted(monthly_data.keys()):
            data = monthly_data[month]
            income = data["income"]
            expense = data["expense"]
            balance = income - expense
            
            report += f"{month:<12} Rp{format_currency(income):>13} Rp{format_currency(expense):>13} Rp{format_currency(balance):>13}\n"
        
        report += "=" * 70 + "\n"
        
        return report
    
    # ============ ANALYTICS & INSIGHTS ============
    
    def generate_trend_report(self, months: int = 6) -> str:
        """
        Generate spending trend analysis report.
        
        Args:
            months: Number of months to analyze
            
        Returns:
            Formatted trend report
        """
        trends = self.service.get_spending_trends(months)
        
        report = "\n" + "=" * 70 + "\n"
        report += f"ANALISA TREN ({months} BULAN TERAKHIR)\n"
        report += "=" * 70 + "\n"
        report += f"{'Bulan':<12} {'Pendapatan':>15} {'Pengeluaran':>15} {'Tren':>15}\n"
        report += "-" * 70 + "\n"
        
        prev_expense = None
        for month, data in sorted(trends.items()):
            income = data["income"]
            expense = data["expense"]
            
            trend_indicator = "→"
            if prev_expense is not None:
                if expense > prev_expense:
                    trend_indicator = "↑"
                elif expense < prev_expense:
                    trend_indicator = "↓"
            
            report += f"{month:<12} Rp{format_currency(income):>13} Rp{format_currency(expense):>13} {trend_indicator:>15}\n"
            prev_expense = expense
        
        report += "=" * 70 + "\n"
        
        forecast = self.service.forecast_next_month()
        report += f"\n📊 PREDIKSI BULAN DEPAN:\n"
        report += f"{'Kategori':<25} {'Estimasi':>15}\n"
        report += "-" * 42 + "\n"
        for cat, amount in forecast.items():
            report += f"{cat:<25} Rp{format_currency(amount):>13}\n"
        
        return report
    
    def generate_statistics_report(self) -> str:
        """
        Generate comprehensive statistics report.
        
        Returns:
            Formatted statistics report
        """
        stats = self.service.get_statistics()
        
        report = "\n" + "=" * 70 + "\n"
        report += "STATISTIK KEUANGAN\n"
        report += "=" * 70 + "\n"
        report += f"Total Transaksi:          {stats['total_transactions']}\n"
        report += f"  • Pemasukan:            {stats['income_count']}\n"
        report += f"  • Pengeluaran:          {stats['expense_count']}\n"
        report += f"\nTotal Pemasukan:          Rp{format_currency(stats['total_income'])}\n"
        report += f"Total Pengeluaran:        Rp{format_currency(stats['total_expense'])}\n"
        report += f"Saldo Akhir:              Rp{format_currency(stats['balance'])}\n"
        report += f"\nRata-rata Pemasukan:      Rp{format_currency(stats['avg_income'])}\n"
        report += f"Rata-rata Pengeluaran:    Rp{format_currency(stats['avg_expense'])}\n"
        report += f"Tingkat Tabungan:         {stats['savings_rate']:.1f}%\n"
        
        if stats['most_expensive_category']:
            report += f"\nKategori Termahal:        {stats['most_expensive_category']}\n"
            report += f"Pengeluaran Tertinggi:    Rp{format_currency(stats['max_expense_amount'])}\n"
        
        report += "=" * 70 + "\n"
        
        return report
    
    # ============ DATA EXPORT ============
    
    def export_to_csv(self, filename: str = "export_transactions.csv") -> bool:
        """
        Export transactions to CSV file.
        
        Args:
            filename: Output CSV filename
            
        Returns:
            True if successful, False otherwise
        """
        try:
            with open(filename, "w", newline="", encoding="utf-8") as f:
                fieldnames = ["ID", "Tanggal", "Jenis", "Kategori", "Jumlah", "Catatan"]
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                
                for t in self.service.transactions:
                    writer.writerow({
                        "ID": t.transaction_id,
                        "Tanggal": t.date,
                        "Jenis": t.transaction_type.capitalize(),
                        "Kategori": t.category,
                        "Jumlah": t.amount,
                        "Catatan": t.note
                    })
            
            logger.info(f"Exported {len(self.service.transactions)} transactions to {filename}")
            return True
        except Exception as e:
            logger.error(f"Error exporting to CSV: {e}")
            return False
    
    def export_to_text(self, filename: str = "export_report.txt") -> bool:
        """
        Export comprehensive report to text file.
        
        Args:
            filename: Output text filename
            
        Returns:
            True if successful, False otherwise
        """
        try:
            with open(filename, "w", encoding="utf-8") as f:
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                f.write(f"LAPORAN KEUANGAN PRIBADI\n")
                f.write(f"Tanggal Ekspor: {timestamp}\n")
                f.write("=" * 70 + "\n\n")
                
                f.write(self.generate_summary_report())
                f.write("\n" + self.generate_category_report())
                f.write("\n" + self.generate_monthly_report())
                f.write("\n" + self.generate_statistics_report())
            
            logger.info(f"Exported report to {filename}")
            return True
        except Exception as e:
            logger.error(f"Error exporting report: {e}")
            return False
    
    def export_transactions_by_month(self, year_month: str, filename: str = None) -> bool:
        """
        Export transactions for specific month to CSV.
        
        Args:
            year_month: Month in YYYY-MM format
            filename: Output filename (auto-generated if None)
            
        Returns:
            True if successful, False otherwise
        """
        if filename is None:
            filename = f"transactions_{year_month}.csv"
        
        try:
            month_transactions = self.service.get_transactions_by_month(year_month)
            
            with open(filename, "w", newline="", encoding="utf-8") as f:
                fieldnames = ["ID", "Tanggal", "Jenis", "Kategori", "Jumlah", "Catatan"]
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                
                for t in sorted(month_transactions, key=lambda x: x.date):
                    writer.writerow({
                        "ID": t.transaction_id,
                        "Tanggal": t.date,
                        "Jenis": t.transaction_type.capitalize(),
                        "Kategori": t.category,
                        "Jumlah": t.amount,
                        "Catatan": t.note
                    })
            
            logger.info(f"Exported {len(month_transactions)} transactions to {filename}")
            return True
        except Exception as e:
            logger.error(f"Error exporting monthly transactions: {e}")
            return False
