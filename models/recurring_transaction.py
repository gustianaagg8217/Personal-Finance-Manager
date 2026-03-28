"""Recurring transaction data model."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Literal


@dataclass
class RecurringTransaction:
    """Represents a recurring transaction template."""
    
    name: str
    transaction_type: Literal["income", "expense"]
    category: str
    amount: float
    frequency: Literal["daily", "weekly", "monthly", "yearly"]
    start_date: str = field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d"))
    end_date: str = ""  # Empty means ongoing
    is_active: bool = True
    note: str = ""
    recurring_id: int = field(default=0)
    
    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "id": self.recurring_id,
            "name": self.name,
            "type": self.transaction_type,
            "category": self.category,
            "amount": self.amount,
            "frequency": self.frequency,
            "start_date": self.start_date,
            "end_date": self.end_date,
            "is_active": self.is_active,
            "note": self.note,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "RecurringTransaction":
        """Create from dictionary."""
        return cls(
            recurring_id=int(data["id"]),
            name=data["name"],
            transaction_type=data["type"],
            category=data["category"],
            amount=float(data["amount"]),
            frequency=data["frequency"],
            start_date=data.get("start_date", datetime.now().strftime("%Y-%m-%d")),
            end_date=data.get("end_date", ""),
            is_active=data.get("is_active", True),
            note=data.get("note", ""),
        )
