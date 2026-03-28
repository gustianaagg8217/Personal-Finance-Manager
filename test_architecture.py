#!/usr/bin/env python
"""Test script for refactored architecture."""

import sys
import os

# Add project to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from main import FinanceManagerCLI
from core.app_context import AppContext
from core.finance_analyzer import FinanceAnalyzer


def test_architecture():
    """Test all refactored architecture components."""
    print("✅ Testing Architecture Components")
    print()
    
    # Test 1: Menu Dispatcher
    app = FinanceManagerCLI()
    dispatcher_count = len(app.menu_dispatcher)
    print(f"✅ Menu Dispatcher: {dispatcher_count} options")
    assert dispatcher_count == 12, "Should have 12 menu options"
    
    # Test 2: App Context
    ctx_ttl = app.app_context.cache_ttl
    print(f"✅ App Context: Initialized with TTL={ctx_ttl}s")
    assert ctx_ttl > 0, "TTL should be positive"
    
    # Test 3: Finance Analyzer
    health = app.finance_analyzer.analyze_financial_health(
        total_income=10000,
        total_expense=7000,
        monthly_budgets={"Housing": 5000},
        transactions=app.transaction_service.transactions,
    )
    print(f"✅ Finance Analyzer: Score={health.score}/100, Status={health.status}")
    assert 0 <= health.score <= 100, "Score should be 0-100"
    assert health.status in ["healthy", "warning", "critical"], "Invalid status"
    
    # Test 4: Aggregation Function
    summary = app.get_financial_summary()
    income = summary["total_income"]
    expense = summary["total_expense"]
    print(f"✅ Aggregation: Income={income}, Expense={expense}")
    assert isinstance(income, (int, float)), "Income should be numeric"
    
    # Test 5: Caching
    cached = app.app_context.get_cached_summary()
    print(f"✅ Caching: Data cached, expires in {app.app_context.cache_ttl}s")
    assert cached is not None, "Should have cached data"
    
    # Test 6: Hook System
    hooks = app.app_context.hooks
    print(f"✅ Hook System: {len(hooks)} hook types available")
    assert "on_transaction_added" in hooks, "Should have transaction hook"
    
    # Test 7: Error Handling
    from utils.errors import ValidationError
    try:
        raise ValidationError("Test error")
    except ValidationError as e:
        print(f"✅ Error Handling: Custom exceptions work")
    
    print()
    print("🎉 All architecture components working correctly!")
    print()
    print("Summary:")
    print(f"  - Menu Dispatcher: {dispatcher_count} actions")
    print(f"  - Caching enabled: TTL={ctx_ttl}s")
    print(f"  - Health Score: {health.score}/100 ({health.status})")
    print(f"  - Financial Summary: Income={income}, Expenses={expense}")
    print(f"  - Hook Types: {len(hooks)}")
    print(f"  - Custom Exceptions: Enabled")


if __name__ == "__main__":
    try:
        test_architecture()
    except AssertionError as e:
        print(f"❌ Test failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
