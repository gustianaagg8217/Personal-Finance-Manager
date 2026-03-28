"""SQLite database storage operations for transactions and budgets."""

import sqlite3
import logging
from pathlib import Path

from models.transaction import Transaction


logger = logging.getLogger(__name__)


class SQLiteStorage:
    """Handles SQLite database operations for transactions and budgets."""
    
    DB_FILE = "finance_data.db"
    
    @classmethod
    def _get_connection(cls):
        """Get database connection."""
        return sqlite3.connect(cls.DB_FILE)
    
    @classmethod
    def _initialize_database(cls) -> None:
        """Initialize database tables if they don't exist."""
        conn = cls._get_connection()
        cursor = conn.cursor()
        
        # Create transactions table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                type TEXT NOT NULL,
                category TEXT NOT NULL,
                amount REAL NOT NULL,
                note TEXT
            )
        """)
        
        # Create budgets table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS budgets (
                category TEXT PRIMARY KEY,
                monthly_budget REAL NOT NULL
            )
        """)
        
        conn.commit()
        conn.close()
        logger.info(f"Database initialized: {cls.DB_FILE}")
    
    @classmethod
    def load_transactions(cls) -> list[Transaction]:
        """
        Load all transactions from database.
        
        Returns:
            List of Transaction objects
        """
        cls._initialize_database()
        
        transactions = []
        try:
            conn = cls._get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, date, type, category, amount, note 
                FROM transactions 
                ORDER BY date DESC
            """)
            
            for row in cursor.fetchall():
                transaction_data = {
                    "id": row[0],
                    "date": row[1],
                    "type": row[2],
                    "category": row[3],
                    "amount": row[4],
                    "note": row[5] or ""
                }
                transactions.append(Transaction.from_dict(transaction_data))
            
            conn.close()
            logger.info(f"Loaded {len(transactions)} transactions from database")
        except sqlite3.Error as e:
            logger.error(f"Error reading transactions: {e}")
            raise
        
        return transactions
    
    @classmethod
    def save_transaction(cls, transaction: Transaction) -> None:
        """
        Save a single transaction to database.
        
        Args:
            transaction: Transaction to save
        """
        cls._initialize_database()
        
        try:
            conn = cls._get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO transactions (date, type, category, amount, note)
                VALUES (?, ?, ?, ?, ?)
            """, (
                transaction.date,
                transaction.transaction_type,
                transaction.category,
                transaction.amount,
                transaction.note
            ))
            
            transaction.transaction_id = cursor.lastrowid
            conn.commit()
            conn.close()
            
            logger.info(f"Saved transaction ID: {transaction.transaction_id}")
        except sqlite3.Error as e:
            logger.error(f"Error saving transaction: {e}")
            raise
    
    @classmethod
    def load_budgets(cls) -> dict[str, float]:
        """
        Load all budgets from database.
        
        Returns:
            Dictionary of category -> monthly_budget
        """
        cls._initialize_database()
        
        budgets = {}
        try:
            conn = cls._get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT category, monthly_budget FROM budgets")
            
            for row in cursor.fetchall():
                budgets[row[0]] = float(row[1])
            
            conn.close()
            logger.info(f"Loaded {len(budgets)} budgets from database")
        except sqlite3.Error as e:
            logger.error(f"Error reading budgets: {e}")
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
        cls._initialize_database()
        
        try:
            conn = cls._get_connection()
            cursor = conn.cursor()
            
            # Use INSERT OR REPLACE for upsert
            cursor.execute("""
                INSERT OR REPLACE INTO budgets (category, monthly_budget)
                VALUES (?, ?)
            """, (category, amount))
            
            conn.commit()
            conn.close()
            logger.info(f"Saved budget for {category}: {amount}")
        except sqlite3.Error as e:
            logger.error(f"Error saving budget: {e}")
            raise
    
    @classmethod
    def delete_transaction(cls, transaction_id: int) -> None:
        """
        Delete a transaction by ID.
        
        Args:
            transaction_id: ID of transaction to delete
        """
        try:
            conn = cls._get_connection()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM transactions WHERE id = ?", (transaction_id,))
            conn.commit()
            conn.close()
            logger.info(f"Deleted transaction ID: {transaction_id}")
        except sqlite3.Error as e:
            logger.error(f"Error deleting transaction: {e}")
            raise
    
    @classmethod
    def update_transaction(cls, transaction: Transaction) -> None:
        """
        Update an existing transaction.
        
        Args:
            transaction: Transaction to update
        """
        try:
            conn = cls._get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE transactions 
                SET date = ?, type = ?, category = ?, amount = ?, note = ?
                WHERE id = ?
            """, (
                transaction.date,
                transaction.transaction_type,
                transaction.category,
                transaction.amount,
                transaction.note,
                transaction.transaction_id
            ))
            conn.commit()
            conn.close()
            logger.info(f"Updated transaction ID: {transaction.transaction_id}")
        except sqlite3.Error as e:
            logger.error(f"Error updating transaction: {e}")
            raise
    
    @classmethod
    def get_transaction_count(cls) -> int:
        """Get total number of transactions."""
        try:
            conn = cls._get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM transactions")
            count = cursor.fetchone()[0]
            conn.close()
            return count
        except sqlite3.Error as e:
            logger.error(f"Error getting transaction count: {e}")
            raise
    
    @classmethod
    def clear_all_data(cls) -> None:
        """Clear all data from database (use with caution)."""
        try:
            conn = cls._get_connection()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM transactions")
            cursor.execute("DELETE FROM budgets")
            conn.commit()
            conn.close()
            logger.warning("All data cleared from database")
        except sqlite3.Error as e:
            logger.error(f"Error clearing data: {e}")
            raise
