"""CSV storage operations for transactions and budgets."""

import csv
import logging
import os
from pathlib import Path
from typing import Optional

from models.transaction import Transaction


logger = logging.getLogger(__name__)


class CSVStorage:
    """Handles CSV file operations for transactions."""
    
    TRANSACTIONS_FILE = "finance_data.csv"
    BUDGET_FILE = "budget.csv"
    FIELDNAMES = ["id", "date", "type", "category", "amount", "note"]
    BUDGET_FIELDNAMES = ["category", "monthly_budget"]
    
    @classmethod
    def _ensure_file_exists(cls, filename: str, fieldnames: list[str]) -> None:
        """
        Create CSV file if it doesn't exist.
        
        Args:
            filename: Name of the CSV file
            fieldnames: Column names for the file
        """
        if not os.path.exists(filename):
            try:
                with open(filename, "w", newline="", encoding="utf-8") as f:
                    writer = csv.DictWriter(f, fieldnames=fieldnames)
                    writer.writeheader()
                logger.info(f"Created file: {filename}")
            except IOError as e:
                logger.error(f"Error creating file {filename}: {e}")
                raise
    
    @classmethod
    def load_transactions(cls) -> list[Transaction]:
        """
        Load all transactions from CSV.
        
        Returns:
            List of Transaction objects
        """
        cls._ensure_file_exists(cls.TRANSACTIONS_FILE, cls.FIELDNAMES)
        
        transactions = []
        try:
            with open(cls.TRANSACTIONS_FILE, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if row and row.get("id"):
                        transactions.append(Transaction.from_dict(row))
            logger.info(f"Loaded {len(transactions)} transactions")
        except IOError as e:
            logger.error(f"Error reading transactions: {e}")
            raise
        
        return transactions
    
    @classmethod
    def save_transaction(cls, transaction: Transaction) -> None:
        """
        Save a single transaction to CSV.
        
        Args:
            transaction: Transaction to save
        """
        cls._ensure_file_exists(cls.TRANSACTIONS_FILE, cls.FIELDNAMES)
        
        # Get next ID
        transactions = cls.load_transactions()
        next_id = max([t.transaction_id for t in transactions], default=0) + 1
        transaction.transaction_id = next_id
        
        try:
            with open(cls.TRANSACTIONS_FILE, "a", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=cls.FIELDNAMES)
                writer.writerow(transaction.to_dict())
            logger.info(f"Saved transaction ID: {next_id}")
        except IOError as e:
            logger.error(f"Error saving transaction: {e}")
            raise
    
    @classmethod
    def load_budgets(cls) -> dict[str, float]:
        """
        Load all budgets from CSV.
        
        Returns:
            Dictionary of category -> monthly_budget
        """
        cls._ensure_file_exists(cls.BUDGET_FILE, cls.BUDGET_FIELDNAMES)
        
        budgets = {}
        try:
            with open(cls.BUDGET_FILE, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if row and row.get("category"):
                        budgets[row["category"]] = float(row["monthly_budget"])
            logger.info(f"Loaded {len(budgets)} budgets")
        except IOError as e:
            logger.error(f"Error reading budgets: {e}")
            raise
        except ValueError as e:
            logger.error(f"Error parsing budget amount: {e}")
            raise
        
        return budgets
    
    @classmethod
    def save_budget(cls, category: str, amount: float) -> None:
        """
        Save or update a budget for category.
        
        Args:
            category: Category name
            amount: Monthly budget amount
        """
        cls._ensure_file_exists(cls.BUDGET_FILE, cls.BUDGET_FIELDNAMES)
        
        budgets = cls.load_budgets()
        budgets[category] = amount
        
        try:
            with open(cls.BUDGET_FILE, "w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=cls.BUDGET_FIELDNAMES)
                writer.writeheader()
                for cat, budget_amount in budgets.items():
                    writer.writerow({"category": cat, "monthly_budget": budget_amount})
            logger.info(f"Saved budget for {category}: {amount}")
        except IOError as e:
            logger.error(f"Error saving budget: {e}")
            raise
