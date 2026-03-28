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
    
    def delete_all_transactions(self) -> None:
        """Delete all transactions from storage."""
        try:
            self.storage.delete_all_transactions()
            self.transactions = []
            logger.info("All transactions deleted")
        except Exception as e:
            logger.error(f"Error deleting all transactions: {e}")
            raise
    
    # ============ EDIT/DELETE FUNCTIONALITY ============
    
    def get_transaction_by_id(self, transaction_id: int) -> Optional[Transaction]:
        """
        Get transaction by ID.
        
        Args:
            transaction_id: ID of transaction to retrieve
            
        Returns:
            Transaction object or None if not found
        """
        for t in self.transactions:
            if t.transaction_id == transaction_id:
                return t
        return None
    
    def edit_transaction(self, transaction_id: int, **updates) -> bool:
        """
        Edit an existing transaction.
        
        Args:
            transaction_id: ID of transaction to edit
            **updates: Fields to update (category, amount, note, date, type)
            
        Returns:
            True if successful, False if transaction not found
        """
        transaction = self.get_transaction_by_id(transaction_id)
        if not transaction:
            logger.warning(f"Transaction {transaction_id} not found")
            return False
        
        # Update allowed fields
        if "category" in updates:
            transaction.category = updates["category"].strip()
        if "amount" in updates:
            transaction.amount = updates["amount"]
        if "note" in updates:
            transaction.note = updates["note"].strip()
        if "date" in updates:
            transaction.date = updates["date"]
        if "type" in updates:
            transaction.transaction_type = updates["type"].lower()
        
        self.storage.update_transaction(transaction)
        logger.info(f"Transaction {transaction_id} updated")
        return True
    
    def delete_transaction(self, transaction_id: int) -> bool:
        """
        Delete a transaction.
        
        Args:
            transaction_id: ID of transaction to delete
            
        Returns:
            True if successful, False if transaction not found
        """
        transaction = self.get_transaction_by_id(transaction_id)
        if not transaction:
            logger.warning(f"Transaction {transaction_id} not found")
            return False
        
        self.storage.delete_transaction(transaction_id)
        self.transactions.remove(transaction)
        logger.info(f"Transaction {transaction_id} deleted")
        return True
    
    # ============ SEARCH & FILTER FUNCTIONALITY ============
    
    def filter_transactions(
        self,
        category: Optional[str] = None,
        transaction_type: Optional[str] = None,
        from_date: Optional[str] = None,
        to_date: Optional[str] = None,
        min_amount: Optional[float] = None,
        max_amount: Optional[float] = None
    ) -> list[Transaction]:
        """
        Filter transactions with multiple criteria.
        
        Args:
            category: Filter by category
            transaction_type: Filter by type (income/expense)
            from_date: Filter from date (YYYY-MM-DD)
            to_date: Filter to date (YYYY-MM-DD)
            min_amount: Minimum amount
            max_amount: Maximum amount
            
        Returns:
            Filtered list of transactions
        """
        result = self.transactions.copy()
        
        if category:
            result = [t for t in result if t.category.lower() == category.lower()]
        
        if transaction_type:
            result = [t for t in result if t.transaction_type.lower() == transaction_type.lower()]
        
        if from_date:
            result = [t for t in result if t.date >= from_date]
        
        if to_date:
            result = [t for t in result if t.date <= to_date]
        
        if min_amount is not None:
            result = [t for t in result if t.amount >= min_amount]
        
        if max_amount is not None:
            result = [t for t in result if t.amount <= max_amount]
        
        return sorted(result, key=lambda t: t.date, reverse=True)
    
    def search_by_keyword(self, keyword: str) -> list[Transaction]:
        """
        Search transactions by keyword (in category or note).
        
        Args:
            keyword: Search keyword
            
        Returns:
            Matching transactions
        """
        keyword_lower = keyword.lower()
        return [
            t for t in self.transactions
            if keyword_lower in t.category.lower() or keyword_lower in t.note.lower()
        ]
    
    # ============ ANALYTICS & TRENDS ============
    
    def get_spending_trends(self, months: int = 6) -> dict:
        """
        Get spending trends over multiple months.
        
        Args:
            months: Number of months to analyze
            
        Returns:
            Dictionary with trend data
        """
        from datetime import datetime, timedelta
        
        trend_data = {}
        current_date = datetime.now()
        
        for i in range(months):
            month_date = current_date - timedelta(days=30*i)
            year_month = month_date.strftime("%Y-%m")
            summary = self.get_month_summary(year_month)
            trend_data[year_month] = summary
        
        return dict(sorted(trend_data.items()))
    
    def get_average_spending(self, category: Optional[str] = None, months: int = 6) -> float:
        """
        Get average monthly spending.
        
        Args:
            category: Optional category filter
            months: Number of months to average
            
        Returns:
            Average monthly spending
        """
        from datetime import datetime, timedelta
        
        total = 0
        current_date = datetime.now()
        
        for i in range(months):
            month_date = current_date - timedelta(days=30*i)
            year_month = month_date.strftime("%Y-%m")
            month_trans = self.get_transactions_by_month(year_month)
            
            if category:
                total += sum(
                    t.amount for t in month_trans
                    if t.transaction_type == "expense" and t.category == category
                )
            else:
                total += sum(
                    t.amount for t in month_trans
                    if t.transaction_type == "expense"
                )
        
        return total / months if months > 0 else 0
    
    def forecast_next_month(self) -> dict:
        """
        Forecast expenses for next month based on trends.
        
        Returns:
            Dictionary with forecasted spending by category
        """
        from datetime import datetime, timedelta
        
        # Get last 3 months averages
        forecast = {}
        current_date = datetime.now()
        
        for category_name in set(t.category for t in self.get_expense_transactions()):
            total = 0
            months = 3
            
            for i in range(months):
                month_date = current_date - timedelta(days=30*i)
                year_month = month_date.strftime("%Y-%m")
                month_trans = self.get_transactions_by_month(year_month)
                total += sum(
                    t.amount for t in month_trans
                    if t.transaction_type == "expense" and t.category == category_name
                )
            
            forecast[category_name] = total / months
        
        return dict(sorted(forecast.items(), key=lambda x: x[1], reverse=True))
    
    def get_statistics(self) -> dict:
        """
        Get comprehensive financial statistics.
        
        Returns:
            Dictionary with various statistics
        """
        expenses = self.get_expense_transactions()
        incomes = self.get_income_transactions()
        
        if not expenses and not incomes:
            return {
                "total_transactions": 0,
                "total_income": 0,
                "total_expense": 0,
                "balance": 0,
                "avg_income": 0,
                "avg_expense": 0,
                "savings_rate": 0,
                "most_expensive_category": None
            }
        
        total_income = self.get_total_income()
        total_expense = self.get_total_expense()
        expenses_by_cat = self.get_expenses_by_category()
        
        return {
            "total_transactions": len(self.transactions),
            "income_count": len(incomes),
            "expense_count": len(expenses),
            "total_income": total_income,
            "total_expense": total_expense,
            "balance": self.get_balance(),
            "avg_income": total_income / len(incomes) if incomes else 0,
            "avg_expense": total_expense / len(expenses) if expenses else 0,
            "savings_rate": ((total_income - total_expense) / total_income * 100) if total_income > 0 else 0,
            "most_expensive_category": max(expenses_by_cat, key=expenses_by_cat.get) if expenses_by_cat else None,
            "max_expense_amount": max((t.amount for t in expenses), default=0),
        }
