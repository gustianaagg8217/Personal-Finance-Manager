"""Transaction data model."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Literal


@dataclass
class Transaction:
    """Represents a financial transaction."""
    
    transaction_type: Literal["income", "expense"]
    category: str
    amount: float
    date: str = field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d"))
    note: str = ""
    transaction_id: int = field(default=0)
    
    def to_dict(self) -> dict:
        """Convert transaction to dictionary."""
        return {
            "id": self.transaction_id,
            "date": self.date,
            "type": self.transaction_type,
            "category": self.category,
            "amount": self.amount,
            "note": self.note,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "Transaction":
        """Create transaction from dictionary."""
        return cls(
            transaction_id=int(data["id"]),
            date=data["date"],
            transaction_type=data["type"],
            category=data["category"],
            amount=float(data["amount"]),
            note=data["note"],
        )
