"""Recurring transaction management service."""

import logging
from datetime import datetime, timedelta
from typing import Optional

from models.recurring_transaction import RecurringTransaction
from storage.storage_factory import StorageFactory


logger = logging.getLogger(__name__)


class RecurringService:
    """Service for managing recurring transactions."""
    
    def __init__(self):
        """Initialize recurring service."""
        self.storage = StorageFactory.get_storage_backend()
        self.recurring_transactions = self.storage.load_recurring_transactions()
    
    def add_recurring_transaction(
        self,
        name: str,
        transaction_type: str,
        category: str,
        amount: float,
        frequency: str,
        start_date: str = None,
        end_date: str = "",
        note: str = ""
    ) -> RecurringTransaction:
        """
        Add a new recurring transaction.
        
        Args:
            name: Name of recurring transaction
            transaction_type: 'income' or 'expense'
            category: Transaction category
            amount: Transaction amount
            frequency: 'daily', 'weekly', 'monthly', or 'yearly'
            start_date: Start date (YYYY-MM-DD), default today
            end_date: End date (YYYY-MM-DD), empty means ongoing
            note: Optional note
            
        Returns:
            Created RecurringTransaction object
        """
        if start_date is None:
            start_date = datetime.now().strftime("%Y-%m-%d")
        
        recurring = RecurringTransaction(
            name=name.strip(),
            transaction_type=transaction_type.lower(),
            category=category.strip(),
            amount=amount,
            frequency=frequency.lower(),
            start_date=start_date,
            end_date=end_date,
            is_active=True,
            note=note.strip()
        )
        
        self.storage.save_recurring_transaction(recurring)
        self.recurring_transactions.append(recurring)
        logger.info(f"Recurring transaction added: {name}")
        
        return recurring
    
    def get_recurring_by_id(self, recurring_id: int) -> Optional[RecurringTransaction]:
        """Get recurring transaction by ID."""
        for r in self.recurring_transactions:
            if r.recurring_id == recurring_id:
                return r
        return None
    
    def edit_recurring_transaction(self, recurring_id: int, **updates) -> bool:
        """Edit an existing recurring transaction."""
        recurring = self.get_recurring_by_id(recurring_id)
        if not recurring:
            logger.warning(f"Recurring transaction {recurring_id} not found")
            return False
        
        if "name" in updates:
            recurring.name = updates["name"].strip()
        if "category" in updates:
            recurring.category = updates["category"].strip()
        if "amount" in updates:
            recurring.amount = updates["amount"]
        if "frequency" in updates:
            recurring.frequency = updates["frequency"].lower()
        if "is_active" in updates:
            recurring.is_active = updates["is_active"]
        if "note" in updates:
            recurring.note = updates["note"].strip()
        if "end_date" in updates:
            recurring.end_date = updates["end_date"]
        
        self.storage.update_recurring_transaction(recurring)
        logger.info(f"Recurring transaction {recurring_id} updated")
        return True
    
    def delete_recurring_transaction(self, recurring_id: int) -> bool:
        """Delete a recurring transaction."""
        recurring = self.get_recurring_by_id(recurring_id)
        if not recurring:
            logger.warning(f"Recurring transaction {recurring_id} not found")
            return False
        
        self.storage.delete_recurring_transaction(recurring_id)
        self.recurring_transactions.remove(recurring)
        logger.info(f"Recurring transaction {recurring_id} deleted")
        return True
    
    def get_active_recurring(self) -> list[RecurringTransaction]:
        """Get all active recurring transactions."""
        return [r for r in self.recurring_transactions if r.is_active]
    
    def generate_transactions_for_date(self, target_date: str) -> list:
        """
        Generate transactions for a specific date from recurring templates.
        
        Args:
            target_date: Date in YYYY-MM-DD format
            
        Returns:
            List of tuples (transaction_type, category, amount, name)
        """
        from datetime import datetime
        
        generated = []
        target_dt = datetime.strptime(target_date, "%Y-%m-%d")
        
        for recurring in self.get_active_recurring():
            # Check if this recurring transaction should apply on target date
            start_dt = datetime.strptime(recurring.start_date, "%Y-%m-%d")
            
            if target_dt < start_dt:
                continue
            
            if recurring.end_date:
                end_dt = datetime.strptime(recurring.end_date, "%Y-%m-%d")
                if target_dt > end_dt:
                    continue
            
            # Check frequency match
            should_generate = False
            
            if recurring.frequency == "daily":
                should_generate = True
            elif recurring.frequency == "weekly":
                should_generate = (target_dt.weekday() == start_dt.weekday())
            elif recurring.frequency == "monthly":
                should_generate = (target_dt.day == start_dt.day)
            elif recurring.frequency == "yearly":
                should_generate = (target_dt.month == start_dt.month and target_dt.day == start_dt.day)
            
            if should_generate:
                generated.append({
                    "transaction_type": recurring.transaction_type,
                    "category": recurring.category,
                    "amount": recurring.amount,
                    "note": f"[RECURRING] {recurring.name}" if recurring.name else "[RECURRING]"
                })
        
        return generated
    
    def get_recurring_summary(self) -> dict:
        """Get summary of recurring transactions."""
        active = self.get_active_recurring()
        
        monthly_income = sum(
            r.amount for r in active 
            if r.transaction_type == "income" and r.frequency in ["monthly", "yearly"]
        )
        
        monthly_expense = sum(
            r.amount for r in active 
            if r.transaction_type == "expense" and r.frequency in ["monthly", "yearly"]
        )
        
        return {
            "total_active": len(active),
            "total_recurring": len(self.recurring_transactions),
            "estimated_monthly_income": monthly_income,
            "estimated_monthly_expense": monthly_expense,
            "estimated_monthly_balance": monthly_income - monthly_expense
        }
