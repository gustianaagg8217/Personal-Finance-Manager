"""Formatting utilities for output."""

from typing import Optional


def format_currency(amount: float) -> str:
    """
    Format amount as currency with thousand separators.
    
    Args:
        amount: Numeric amount
        
    Returns:
        Formatted currency string
    """
    return f"{amount:,.0f}"


def format_percentage(value: float, total: float) -> str:
    """
    Format as percentage.
    
    Args:
        value: Partial value
        total: Total value
        
    Returns:
        Percentage string
    """
    if total == 0:
        return "0.00%"
    percentage = (value / total) * 100
    return f"{percentage:.2f}%"


def highlight_warning(text: str, is_warning: bool = False) -> str:
    """
    Add visual warning highlight.
    
    Args:
        text: Text to highlight
        is_warning: Whether to add warning marker
        
    Returns:
        Highlighted text
    """
    if is_warning:
        return f"⚠️  {text}"
    return text


def format_table_row(columns: list[str], widths: list[int]) -> str:
    """
    Format a table row.
    
    Args:
        columns: Column values
        widths: Column widths
        
    Returns:
        Formatted row
    """
    return " | ".join(f"{col:<{width}}" for col, width in zip(columns, widths))


def format_separator(widths: list[int]) -> str:
    """
    Create table separator.
    
    Args:
        widths: Column widths
        
    Returns:
        Separator line
    """
    return "-+-".join("-" * width for width in widths)
