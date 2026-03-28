"""Budget management service."""

import logging
from datetime import datetime

from services.transaction_service import TransactionService
from storage.storage_factory import StorageFactory
from utils.formatter import format_currency, highlight_warning


logger = logging.getLogger(__name__)


class BudgetService:
    """Service for managing budgets."""
    
    def __init__(self, transaction_service: TransactionService):
        """
        Initialize budget service.
        
        Args:
            transaction_service: TransactionService instance
        """
        self.service = transaction_service
        self.storage = StorageFactory.get_storage_backend()
        self.budgets = self.storage.load_budgets()
    
    def set_budget(self, category: str, amount: float) -> None:
        """
        Set monthly budget for category.
        
        Args:
            category: Category name
            amount: Monthly budget amount
        """
        self.storage.save_budget(category.strip(), amount)
        self.budgets[category.strip()] = amount
        logger.info(f"Budget set for {category}: {amount}")
    
    def get_budget(self, category: str) -> float:
        """
        Get budget for category.
        
        Args:
            category: Category name
            
        Returns:
            Budget amount or 0 if not set
        """
        return self.budgets.get(category.strip(), 0)
    
    def get_current_month(self) -> str:
        """Get current month in YYYY-MM format."""
        return datetime.now().strftime("%Y-%m")
    
    def get_month_spending(self, category: str, year_month: str = None) -> float:
        """
        Get spending for category in a month.
        
        Args:
            category: Category name
            year_month: Month in YYYY-MM format (default: current month)
            
        Returns:
            Total spending for the category
        """
        if year_month is None:
            year_month = self.get_current_month()
        
        month_transactions = self.service.get_transactions_by_month(year_month)
        return sum(
            t.amount for t in month_transactions
            if t.transaction_type == "expense" and t.category == category.strip()
        )
    
    def is_budget_exceeded(self, category: str, year_month: str = None) -> bool:
        """
        Check if spending exceeded budget for category.
        
        Args:
            category: Category name
            year_month: Month in YYYY-MM format (default: current month)
            
        Returns:
            True if exceeded
        """
        budget = self.get_budget(category)
        if budget == 0:
            return False
        
        spending = self.get_month_spending(category, year_month)
        return spending > budget
    
    def get_budget_status(self, category: str, year_month: str = None) -> dict:
        """
        Get budget status for category.
        
        Args:
            category: Category name
            year_month: Month in YYYY-MM format (default: current month)
            
        Returns:
            Status dictionary
        """
        if year_month is None:
            year_month = self.get_current_month()
        
        budget = self.get_budget(category)
        spending = self.get_month_spending(category, year_month)
        remaining = budget - spending if budget > 0 else None
        exceeded = spending > budget if budget > 0 else False
        
        return {
            "category": category,
            "budget": budget,
            "spending": spending,
            "remaining": remaining,
            "exceeded": exceeded,
            "month": year_month
        }
    
    def generate_budget_report(self, year_month: str = None) -> str:
        """
        Generate budget status report.
        
        Args:
            year_month: Month in YYYY-MM format (default: current month)
            
        Returns:
            Formatted budget report
        """
        if year_month is None:
            year_month = self.get_current_month()
        
        if not self.budgets:
            return f"\nTidak ada anggaran yang ditetapkan untuk {year_month}.\n"
        
        report = "\n" + "=" * 80 + "\n"
        report += f"STATUS ANGGARAN - {year_month}\n"
        report += "=" * 80 + "\n"
        report += f"{'Kategori':<20} {'Anggaran':>12} {'Pengeluaran':>12} {'Sisa':>12} {'Status':>15}\n"
        report += "-" * 80 + "\n"
        
        total_budget = 0
        total_spending = 0
        
        for category in sorted(self.budgets.keys()):
            status = self.get_budget_status(category, year_month)
            budget = status["budget"]
            spending = status["spending"]
            remaining = status["remaining"]
            exceeded = status["exceeded"]
            
            total_budget += budget
            total_spending += spending
            
            status_text = highlight_warning("TERLAMPAUI", exceeded)
            if not exceeded and remaining is not None:
                status_text = f"✓ BAIK"
            
            remaining_text = f"Rp{format_currency(remaining)}" if remaining is not None else "N/A"
            
            report += f"{category:<20} Rp{format_currency(budget):>10} Rp{format_currency(spending):>10} {remaining_text:>12} {status_text:>15}\n"
        
        report += "-" * 80 + "\n"
        report += f"{'TOTAL':<20} Rp{format_currency(total_budget):>10} Rp{format_currency(total_spending):>10}\n"
        report += "=" * 80 + "\n"
        
        return report
