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
        
        # Create recurring transactions table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS recurring_transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                type TEXT NOT NULL,
                category TEXT NOT NULL,
                amount REAL NOT NULL,
                frequency TEXT NOT NULL,
                start_date TEXT NOT NULL,
                end_date TEXT,
                is_active INTEGER DEFAULT 1,
                note TEXT
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
    
    @classmethod
    def delete_all_transactions(cls) -> None:
        """Delete all transactions from database."""
        try:
            conn = cls._get_connection()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM transactions")
            conn.commit()
            conn.close()
            logger.warning("All transactions deleted from database")
        except sqlite3.Error as e:
            logger.error(f"Error deleting all transactions: {e}")
            raise
    
    @classmethod
    def delete_all_budgets(cls) -> None:
        """Delete all budgets from database."""
        try:
            conn = cls._get_connection()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM budgets")
            conn.commit()
            conn.close()
            logger.warning("All budgets deleted from database")
        except sqlite3.Error as e:
            logger.error(f"Error deleting all budgets: {e}")
            raise
    
    # ============ RECURRING TRANSACTIONS ============
    
    @classmethod
    def load_recurring_transactions(cls) -> list:
        """Load all recurring transactions from database."""
        cls._initialize_database()
        
        recurring_list = []
        try:
            from models.recurring_transaction import RecurringTransaction
            
            conn = cls._get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, name, type, category, amount, frequency, start_date, end_date, is_active, note
                FROM recurring_transactions
                ORDER BY name ASC
            """)
            
            for row in cursor.fetchall():
                recurring_data = {
                    "id": row[0],
                    "name": row[1],
                    "type": row[2],
                    "category": row[3],
                    "amount": row[4],
                    "frequency": row[5],
                    "start_date": row[6],
                    "end_date": row[7] or "",
                    "is_active": bool(row[8]),
                    "note": row[9] or ""
                }
                recurring_list.append(RecurringTransaction.from_dict(recurring_data))
            
            conn.close()
            logger.info(f"Loaded {len(recurring_list)} recurring transactions from database")
        except Exception as e:
            logger.error(f"Error reading recurring transactions: {e}")
            raise
        
        return recurring_list
    
    @classmethod
    def save_recurring_transaction(cls, recurring) -> None:
        """Save a recurring transaction to database."""
        cls._initialize_database()
        
        try:
            conn = cls._get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO recurring_transactions 
                (name, type, category, amount, frequency, start_date, end_date, is_active, note)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                recurring.name,
                recurring.transaction_type,
                recurring.category,
                recurring.amount,
                recurring.frequency,
                recurring.start_date,
                recurring.end_date,
                1 if recurring.is_active else 0,
                recurring.note
            ))
            
            recurring.recurring_id = cursor.lastrowid
            conn.commit()
            conn.close()
            
            logger.info(f"Saved recurring transaction ID: {recurring.recurring_id}")
        except sqlite3.Error as e:
            logger.error(f"Error saving recurring transaction: {e}")
            raise
    
    @classmethod
    def update_recurring_transaction(cls, recurring) -> None:
        """Update an existing recurring transaction."""
        try:
            conn = cls._get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE recurring_transactions 
                SET name = ?, type = ?, category = ?, amount = ?, frequency = ?, 
                    start_date = ?, end_date = ?, is_active = ?, note = ?
                WHERE id = ?
            """, (
                recurring.name,
                recurring.transaction_type,
                recurring.category,
                recurring.amount,
                recurring.frequency,
                recurring.start_date,
                recurring.end_date,
                1 if recurring.is_active else 0,
                recurring.note,
                recurring.recurring_id
            ))
            conn.commit()
            conn.close()
            logger.info(f"Updated recurring transaction ID: {recurring.recurring_id}")
        except sqlite3.Error as e:
            logger.error(f"Error updating recurring transaction: {e}")
            raise
    
    @classmethod
    def delete_recurring_transaction(cls, recurring_id: int) -> None:
        """Delete a recurring transaction by ID."""
        try:
            conn = cls._get_connection()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM recurring_transactions WHERE id = ?", (recurring_id,))
            conn.commit()
            conn.close()
            logger.info(f"Deleted recurring transaction ID: {recurring_id}")
        except sqlite3.Error as e:
            logger.error(f"Error deleting recurring transaction: {e}")
            raise
