"""Transaction management service."""

import logging
from typing import Optional

from models.transaction import Transaction
from storage.storage_factory import StorageFactory


logger = logging.getLogger(__name__)


class TransactionService:
    """Service for managing transactions."""
    
    def __init__(self):
        """Initialize transaction service."""
        self.storage = StorageFactory.get_storage_backend()
        self.transactions = self.storage.load_transactions()
    
    def add_transaction(
        self,
        transaction_type: str,
        category: str,
        amount: float,
        note: str = ""
    ) -> Transaction:
        """
        Add a new transaction.
        
        Args:
            transaction_type: 'income' or 'expense'
            category: Transaction category
            amount: Transaction amount
            note: Optional note
            
        Returns:
            Created Transaction object
        """
        transaction = Transaction(
            transaction_type=transaction_type.lower(),
            category=category.strip(),
            amount=amount,
            note=note.strip()
        )
        
        self.storage.save_transaction(transaction)
        self.transactions.append(transaction)
        logger.info(f"Transaction added: {transaction_type} {category} {amount}")
        
        return transaction
    
    def get_income_transactions(self) -> list[Transaction]:
        """Get all income transactions."""
        return [t for t in self.transactions if t.transaction_type == "income"]
    
    def get_expense_transactions(self) -> list[Transaction]:
        """Get all expense transactions."""
        return [t for t in self.transactions if t.transaction_type == "expense"]
    
    def get_total_income(self) -> float:
        """Get total income."""
        return sum(t.amount for t in self.get_income_transactions())
    
    def get_total_expense(self) -> float:
        """Get total expense."""
        return sum(t.amount for t in self.get_expense_transactions())
    
    def get_balance(self) -> float:
        """Get current balance."""
        return self.get_total_income() - self.get_total_expense()
    
    def get_expenses_by_category(self) -> dict[str, float]:
        """Get total expenses grouped by category."""
        expenses = {}
        for transaction in self.get_expense_transactions():
            expenses[transaction.category] = expenses.get(transaction.category, 0) + transaction.amount
        return dict(sorted(expenses.items(), key=lambda x: x[1], reverse=True))
    
    def get_transactions_by_month(self, year_month: str) -> list[Transaction]:
        """
        Get transactions for a specific month.
        
        Args:
            year_month: Format YYYY-MM
            
        Returns:
            List of transactions
        """
        return [t for t in self.transactions if t.date.startswith(year_month)]
    
    def get_month_summary(self, year_month: str) -> dict:
        """
        Get summary for a month.
        
        Args:
            year_month: Format YYYY-MM
            
        Returns:
            Dictionary with income, expense, balance
        """
        month_transactions = self.get_transactions_by_month(year_month)
        
        income = sum(t.amount for t in month_transactions if t.transaction_type == "income")
        expense = sum(t.amount for t in month_transactions if t.transaction_type == "expense")
        
        return {
            "income": income,
            "expense": expense,
            "balance": income - expense
        }
