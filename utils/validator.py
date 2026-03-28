"""Input validation utilities."""

from typing import Literal


def validate_amount(amount: str) -> tuple[bool, float | None]:
    """
    Validate and convert amount to float.
    
    Args:
        amount: String representation of amount
        
    Returns:
        Tuple of (is_valid, amount_value)
    """
    try:
        value = float(amount)
        if value <= 0:
            return False, None
        return True, value
    except ValueError:
        return False, None


def validate_type(transaction_type: str) -> bool:
    """
    Validate transaction type.
    
    Args:
        transaction_type: Type to validate
        
    Returns:
        True if valid
    """
    return transaction_type.lower() in ("income", "expense")


def validate_category(category: str) -> bool:
    """
    Validate category.
    
    Args:
        category: Category to validate
        
    Returns:
        True if valid (not empty)
    """
    return bool(category.strip())


def validate_date(date: str) -> bool:
    """
    Validate date format (YYYY-MM-DD).
    
    Args:
        date: Date string to validate
        
    Returns:
        True if valid format
    """
    try:
        from datetime import datetime
        datetime.strptime(date, "%Y-%m-%d")
        return True
    except ValueError:
        return False


def is_cancel_command(user_input: str) -> bool:
    """
    Check if input is a cancel command.
    
    Args:
        user_input: User input to check
        
    Returns:
        True if cancel command
    """
    cancel_keywords = {"batal", "cancel", "x"}
    return user_input.strip().lower() in cancel_keywords
