# Architecture Quick Reference

## Menu Dispatcher Usage

### Adding a New Menu Option

```python
# 1. Add to dispatcher in __init__
self.menu_dispatcher["13"] = self.my_new_feature

# 2. Add to display_menu()
print("13. My New Feature")

# 3. Implement the method
def my_new_feature(self) -> None:
    """Description of feature."""
    # Implementation here
    pass
```

---

## Application Context Usage

### Caching Financial Data

```python
# Cache data
self.app_context.cache_financial_summary(
    total_income=10000,
    total_expense=7000,
    balance=3000
)

# Retrieve cached (if not expired)
cached = self.app_context.get_cached_summary()
if cached:
    income = cached.total_income
```

### Hook System

```python
# Register hook
def my_callback(transaction):
    print(f"Transaction added: {transaction}")

self.app_context.register_hook("on_transaction_added", my_callback)

# Trigger hook
self.app_context.trigger_hook("on_transaction_added", transaction_obj)

# Available hooks:
# - "on_transaction_added"
# - "on_transaction_deleted"
# - "on_transaction_edited"
# - "on_budget_set"
```

---

## Financial Analyzer Usage

### Complete Health Analysis

```python
from core.finance_analyzer import FinanceAnalyzer

analyzer = FinanceAnalyzer()

health = analyzer.analyze_financial_health(
    total_income=10000,
    total_expense=7000,
    monthly_budgets={
        "Kebutuhan Pokok": 5000,
        "Investasi": 2000,
        "Lifestyle": 1500
    },
    transactions=self.transaction_service.transactions,
    recent_months_data=self._get_recent_months_data()
)

# Access results
print(f"Health Score: {health.score}/100")
print(f"Status: {health.status}")  # healthy/warning/critical
print(f"Spending Trend: {health.spending_trend}")  # increasing/decreasing/stable
print(f"Savings Rate: {health.savings_rate:.1f}%")

# Get insights
for insight in health.insights:
    print(f"  {insight}")

# Get recommendations
for rec in health.recommendations:
    print(f"  {rec}")
```

### Spending Insights

```python
expenses_by_category = {
    "Food": 1500,
    "Transportation": 800,
    "Entertainment": 300
}

insights = analyzer.get_spending_insights(expenses_by_category)
# Returns: {
#   "Food": "🔴 Food is main expense (50.0%)",
#   "Transportation": "🟡 Transportation is significant (26.7%)"
# }
```

---

## Aggregation Function

### Get Financial Summary

```python
# Efficient, cached retrieval
summary = self.get_financial_summary()

# Use results everywhere
total_income = summary["total_income"]
total_expense = summary["total_expense"]
balance = summary["balance"]
```

### Clear Cache When Data Changes

```python
# Called automatically on data modifications
self.app_context.invalidate_cache()

# Or update context
self.app_context.update_last_operation()
```

---

## Error Handling

### Using Custom Exceptions

```python
from utils.errors import ValidationError, TransactionError

try:
    # Validate input
    if not amount > 0:
        raise ValidationError("Amount must be positive")
    
    # Add transaction
    transaction = self.transaction_service.add_transaction(...)
    
except ValidationError as e:
    print(f"❌ Validation error: {e.message}")
    logger.error(f"Validation failed: {e.message}")
except TransactionError as e:
    print(f"❌ Transaction error: {e.message}")
except Exception as e:
    print(f"❌ Unexpected error: {e}")
    logger.exception("Unexpected error occurred")
```

---

## Performance Optimization Tips

### 1. Use Cached Summary
```python
# DON'T do this repeatedly
for i in range(10):
    income = self.transaction_service.get_total_income()

# DO this instead
summary = self.get_financial_summary()
income = summary["total_income"]
```

### 2. Batch Operations
```python
# Invalidate cache once for multiple operations
self.app_context.invalidate_cache()
self.transaction_service.add_transaction(...)
self.budget_service.set_budget(...)
# Cache is now invalid, next get_financial_summary() will recalculate
```

### 3. Use Hooks for Monitoring
```python
# Don't track in every function
def my_hook(transaction):
    log_transaction_event(transaction)
    check_budget_limits(transaction)
    send_notification(transaction)

self.app_context.register_hook("on_transaction_added", my_hook)
# Now called automatically on each transaction
```

---

## Common Patterns

### Adding a Feature That Shows Financial Health

```python
def my_new_feature(self) -> None:
    """Show financial health + custom analysis."""
    try:
        # Get summary efficiently
        summary = self.get_financial_summary()
        
        # Get health assessment
        health = self.finance_analyzer.analyze_financial_health(
            total_income=summary["total_income"],
            total_expense=summary["total_expense"],
            monthly_budgets=self.budget_service.budgets,
            transactions=self.transaction_service.transactions,
            recent_months_data=self._get_recent_months_data()
        )
        
        # Display results
        print(f"Score: {health.score}/100")
        for rec in health.recommendations[:3]:
            print(f"  {rec}")
        
        # Trigger hooks for notification
        self.app_context.trigger_hook("health_check_done", health)
        
    except Exception as e:
        print(f"❌ Error: {e}")
        logger.exception("Feature error")
```

### Adding a New Hook

```python
# 1. First, add to hooks dict in AppContext.__init__
self.hooks: dict[str, list] = {
    # ... existing hooks ...
    "on_custom_event": [],
}

# 2. Register listener in FinanceManagerCLI.__init__
def my_listener(data):
    print(f"Custom event triggered: {data}")

self.app_context.register_hook("on_custom_event", my_listener)

# 3. Trigger from service
self.app_context.trigger_hook("on_custom_event", some_data)
```

---

## Dispatching Pattern Details

### How Dispatcher Works

```python
self.menu_dispatcher["12"] = self._handle_exit

# In run():
choice = input("Pilih opsi: ")
if choice in self.menu_dispatcher:
    action = self.menu_dispatcher[choice]
    action()  # Calls self._handle_exit()
```

### Advantages
- ✅ Easy to add/remove menu options
- ✅ No long if/elif chains
- ✅ Dictionary lookup O(1) performance
- ✅ Can add/remove at runtime if needed
- ✅ Can organize by submenu

---

## Testing the New Architecture

### Test Dispatcher
```bash
python -c "
from main import FinanceManagerCLI
app = FinanceManagerCLI()
print('Menu options:', len(app.menu_dispatcher))  # Should be 12
print('✅ Dispatcher working')
"
```

### Test Context
```bash
python -c "
from core.app_context import AppContext
ctx = AppContext()
ctx.cache_financial_summary(10000, 7000, 3000)
cached = ctx.get_cached_summary()
print(f'✅ Cached income: {cached.total_income}')
"
```

### Test Analyzer
```bash
python -c "
from core.finance_analyzer import FinanceAnalyzer
analyzer = FinanceAnalyzer()
health = analyzer.analyze_financial_health(10000, 7000, {}, [])
print(f'✅ Health score: {health.score}/100')
"
```
