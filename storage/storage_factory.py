"""Storage factory for selecting between CSV and SQLite backends."""

from enum import Enum
import logging


logger = logging.getLogger(__name__)


class StorageType(Enum):
    """Available storage backends."""
    CSV = "csv"
    SQLITE = "sqlite"


class StorageFactory:
    """Factory for creating storage backend instances."""
    
    _storage_type = StorageType.SQLITE  # Default to SQLite
    
    @classmethod
    def set_storage_type(cls, storage_type: StorageType) -> None:
        """
        Set the storage backend type.
        
        Args:
            storage_type: StorageType enum value
        """
        cls._storage_type = storage_type
        logger.info(f"Storage backend set to: {storage_type.value}")
    
    @classmethod
    def get_storage_backend(cls):
        """
        Get the storage backend instance.
        
        Returns:
            Storage backend class (CSVStorage or SQLiteStorage)
        """
        if cls._storage_type == StorageType.CSV:
            from storage.csv_storage import CSVStorage
            return CSVStorage
        elif cls._storage_type == StorageType.SQLITE:
            from storage.sqlite_storage import SQLiteStorage
            return SQLiteStorage
        else:
            raise ValueError(f"Unknown storage type: {cls._storage_type}")
    
    @classmethod
    def get_current_storage_type(cls) -> str:
        """Get current storage type as string."""
        return cls._storage_type.value
