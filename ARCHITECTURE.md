# Architecture & Design Patterns

## Overview

Personal Finance Manager uses a clean, modular architecture that supports multiple storage backends through the **Factory Pattern**.

## StorageFactory Pattern

### Why Factory Pattern?

The `StorageFactory` allows runtime selection of storage backend without changing business logic.

### Architecture Diagram

```
┌─────────────────────────────────────────────────────────┐
│                   FinanceManagerCLI                     │
│                   (main.py)                             │
└────────────────────┬────────────────────────────────────┘
                     │
        ┌────────────┼────────────┐
        │            │            │
        ▼            ▼            ▼
    ┌───────┐   ┌──────────┐  ┌──────────────┐
    │Report │   │Transaction│  │Budget       │
    │Service│   │Service   │  │Service      │
    └───┬───┘   └────┬─────┘  └──────┬──────┘
        │            │               │
        └────────────┼───────────────┘
                     │
                     ▼
            ┌─────────────────┐
            │ StorageFactory  │
            └────────┬────────┘
                     │
        ┌────────────┼────────────┐
        │            │            │
        ▼            ▼            
    ┌──────────┐  ┌──────────┐
    │CSVStorage│  │SQLiteStore│
    │          │  │           │
    └──────────┘  └───────────┘

        Both implement:
        - load_transactions()
        - save_transaction()
        - load_budgets()
        - save_budget()
```

## Storage Interface

Both backends implement the same interface:

```python
@classmethod
def load_transactions(cls) -> list[Transaction]: ...

@classmethod
def save_transaction(cls, transaction: Transaction) -> None: ...

@classmethod
def load_budgets(cls) -> dict[str, float]: ...

@classmethod
def save_budget(cls, category: str, amount: float) -> None: ...
```

## Data Flow

### Adding a Transaction

```
1. User input in FinanceManagerCLI
   ↓
2. create Transaction object
   ↓
3. TransactionService.add_transaction()
   ↓
4. Get storage backend: StorageFactory.get_storage_backend()
   ↓
5. storage.save_transaction(transaction)
   ↓
6. Backend saves to CSV or SQLite
```

### Loading Data at Startup

```
1. FinanceManagerCLI.__init__()
   ↓
2. select_storage_backend() → sets StorageType in factory
   ↓
3. TransactionService() created
   ↓
4. storage = StorageFactory.get_storage_backend()
   ↓
5. transactions = storage.load_transactions()
   ↓
6. Data loaded from selected backend
```

## Module Organization

```
PERSONAL_FINANCE_MANAGER/
├── main.py                          # CLI entry point
├── models/
│   └── transaction.py               # Data model (dataclass)
├── services/
│   ├── transaction_service.py       # Transaction business logic
│   ├── report_service.py            # Report generation
│   └── budget_service.py            # Budget management
├── storage/
│   ├── storage_factory.py           # ← Factory pattern
│   ├── csv_storage.py               # CSV backend implementation
│   ├── sqlite_storage.py            # SQLite backend implementation
│   └── __init__.py
├── utils/
│   ├── validator.py                 # Input validation
│   ├── formatter.py                 # Output formatting
│   ├── visualizer.py                # Chart visualization
│   └── __init__.py
└── ...
```

## Separation of Concerns

### Models (`models/`)
- **Responsibility**: Data structure definitions
- **Example**: `Transaction` dataclass
- **Dependency**: None (standalone)

### Services (`services/`)
- **Responsibility**: Business logic
- **Example**: `TransactionService` handles transaction operations
- **Dependency**: Uses storage factory (abstractly, not directly)

### Storage (`storage/`)
- **Responsibility**: Data persistence
- **Example**: `CSVStorage`, `SQLiteStorage` implementations
- **Dependency**: `models.Transaction`

### Utils (`utils/`)
- **Responsibility**: Helper functions
- **Example**: Validators, formatters, visualization
- **Dependency**: None (standalone utilities)

### Main (`main.py`)
- **Responsibility**: CLI orchestration
- **Dependency**: All other modules
- **Pattern**: CLI shell + IoC (select storage at startup)

## Adding a New Storage Backend

To add a new backend (e.g., PostgreSQL):

### Step 1: Create backend class
```python
# storage/postgresql_storage.py
class PostgreSQLStorage:
    @classmethod
    def load_transactions(cls) -> list[Transaction]:
        # Implementation
        pass
    
    @classmethod
    def save_transaction(cls, transaction: Transaction) -> None:
        # Implementation
        pass
    
    # ... other methods
```

### Step 2: Add to StorageFactory
```python
# storage/storage_factory.py
class StorageType(Enum):
    CSV = "csv"
    SQLITE = "sqlite"
    POSTGRESQL = "postgresql"  # ← Add

class StorageFactory:
    @classmethod
    def get_storage_backend(cls):
        # ... existing code
        elif cls._storage_type == StorageType.POSTGRESQL:
            from storage.postgresql_storage import PostgreSQLStorage
            return PostgreSQLStorage
```

### Step 3: Update main.py menu
```python
def select_storage_backend(self) -> None:
    print("1. SQLite")
    print("2. CSV")
    print("3. PostgreSQL")  # ← Add
    
    if choice == "3":
        StorageFactory.set_storage_type(StorageType.POSTGRESQL)
```

## Design Principles

### 1. SOLID Principles

**S** - Single Responsibility
- Each class has one job (e.g., `TransactionService` only handles transactions)

**O** - Open/Closed
- Open for extension (add new backends without modifying existing code)
- Closed for modification (factory pattern isolates changes)

**L** - Liskov Substitution
- Both storage backends implement the same interface

**I** - Interface Segregation
- Clients depend on specific interfaces, not concrete implementations

**D** - Dependency Inversion
- Services depend on `StorageFactory` abstraction, not concrete storage classes

### 2. DRY (Don't Repeat Yourself)
- Common logic in service layer, not duplicated in storages
- Validation logic centralized in `utils/validator.py`

### 3. Fail Fast
- Input validation happens early
- Exceptions are caught and logged appropriately

## Testing Strategy

### Unit Testing
Each module can be tested independently:

```python
# Test transaction service with mock storage
from unittest.mock import Mock
from services.transaction_service import TransactionService

def test_add_transaction():
    mock_storage = Mock()
    service = TransactionService()
    service.storage = mock_storage  # Inject
    
    transaction = service.add_transaction("expense", "food", 50000)
    mock_storage.save_transaction.assert_called_once()
```

### Integration Testing
Test the full flow:

```python
# Test CSV backend
StorageFactory.set_storage_type(StorageType.CSV)
service = TransactionService()
transaction = service.add_transaction("expense", "food", 50000)
assert len(service.transactions) == 1

# Test SQLite backend
StorageFactory.set_storage_type(StorageType.SQLITE)
service = TransactionService()
assert len(service.transactions) > 0  # Should load persisted data
```

## Performance Considerations

### SQLite Advantages
- Indexed queries (O(log n))
- Lazy loading possible
- Connection pooling ready
- Better for 10,000+ records

### CSV Advantages
- Faster for < 1,000 records
- No parsing overhead
- Human-readable
- Excel compatible

### Recommended Choice by Project Size

| Size | Backend | Reason |
|------|---------|--------|
| < 500 records | Either | Similar performance |
| 500-5,000 | Either | Personal use, no real difference |
| 5,000+ | SQLite | Indexed queries faster |
| 50,000+ | SQLite | CSV loading becomes slow |

## Future Extensions

1. **Remote Storage**: Add cloud backends (Firebase, AWS S3)
2. **Encryption**: Add encrypted storage backend
3. **Sync**: Multi-device synchronization
4. **Caching**: Add caching layer for frequently accessed data
5. **Transactions**: Support database transactions (rollback on error)
6. **Validation**: Add database constraints at storage layer

## Logging Architecture

All modules log to `finance_manager.log`:

```
├── main.py              → CLI events
├── services/*           → Business logic events
├── storage/*            → Persistence events
└── utils/*              → Utility operations
```

Configure logging in `main.py`:
```python
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("finance_manager.log"),
        logging.StreamHandler(sys.stdout)
    ]
)
```

## Error Handling Strategy

1. **Validation Layer**: Catch bad input early
2. **Service Layer**: Handle business logic errors
3. **Storage Layer**: Catch I/O errors
4. **CLI Layer**: User-friendly error messages

```
User Input
    ↓
Validator (raise ValueError)
    ↓
Service (catch, handle, log)
    ↓
Storage (catch IOError, raise)
    ↓
Service (catch, handle, log)
    ↓
CLI (show user-friendly message)
```

## See Also

- [DATABASE.md](DATABASE.md) - Database schema and queries
- [MIGRATION.md](MIGRATION.md) - CSV to SQLite migration
- [README.md](README.md) - Main documentation
