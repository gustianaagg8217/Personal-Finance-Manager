"""Report generation service."""

import logging
from collections import defaultdict

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
