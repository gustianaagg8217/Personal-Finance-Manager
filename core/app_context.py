"""Application context and state management."""

import logging
from typing import Optional, Any
from datetime import datetime, timedelta
from dataclasses import dataclass, field


logger = logging.getLogger(__name__)


@dataclass
class CachedFinancialSummary:
    """Cached financial summary data."""
    
    total_income: float
    total_expense: float
    balance: float
    timestamp: datetime = field(default_factory=datetime.now)
    
    def is_expired(self, ttl_seconds: int = 300) -> bool:
        """Check if cache entry has expired."""
        return (datetime.now() - self.timestamp).total_seconds() > ttl_seconds


class AppContext:
    """Application context for managing state and caching."""
    
    def __init__(self, cache_ttl: int = 300):
        """
        Initialize application context.
        
        Args:
            cache_ttl: Cache time-to-live in seconds
        """
        self.cache_ttl = cache_ttl
        self.cached_summary: Optional[CachedFinancialSummary] = None
        self.cached_transactions: Optional[Any] = None
        self.cached_budgets: Optional[Any] = None
        self.last_operation_timestamp = datetime.now()
        self.hooks: dict[str, list] = {
            "on_transaction_added": [],
            "on_transaction_deleted": [],
            "on_transaction_edited": [],
            "on_budget_set": [],
        }
        
        logger.info("AppContext initialized")
    
    def cache_financial_summary(
        self,
        total_income: float,
        total_expense: float,
        balance: float
    ) -> None:
        """
        Cache financial summary data.
        
        Args:
            total_income: Total income amount
            total_expense: Total expense amount
            balance: Current balance
        """
        self.cached_summary = CachedFinancialSummary(
            total_income=total_income,
            total_expense=total_expense,
            balance=balance
        )
        logger.debug("Financial summary cached")
    
    def get_cached_summary(self) -> Optional[CachedFinancialSummary]:
        """
        Get cached financial summary if not expired.
        
        Returns:
            Cached summary or None if expired
        """
        if self.cached_summary and not self.cached_summary.is_expired(self.cache_ttl):
            return self.cached_summary
        
        self.cached_summary = None
        return None
    
    def invalidate_cache(self) -> None:
        """Invalidate all caches."""
        self.cached_summary = None
        self.cached_transactions = None
        self.cached_budgets = None
        logger.debug("Cache invalidated")
    
    def register_hook(self, hook_name: str, callback) -> None:
        """
        Register a hook callback.
        
        Args:
            hook_name: Name of the hook
            callback: Callable to execute
        """
        if hook_name not in self.hooks:
            self.hooks[hook_name] = []
        
        self.hooks[hook_name].append(callback)
        logger.debug(f"Hook registeredConcatenate: {hook_name}")
    
    def trigger_hook(self, hook_name: str, *args, **kwargs) -> None:
        """
        Trigger all callbacks for a hook.
        
        Args:
            hook_name: Name of the hook
            *args: Positional arguments
            **kwargs: Keyword arguments
        """
        if hook_name not in self.hooks:
            return
        
        for callback in self.hooks[hook_name]:
            try:
                callback(*args, **kwargs)
            except Exception as e:
                logger.error(f"Error executing hook {hook_name}: {e}")
    
    def update_last_operation(self) -> None:
        """Update last operation timestamp and invalidate cache."""
        self.last_operation_timestamp = datetime.now()
        self.invalidate_cache()
