import json
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import datetime, timezone
from app.models import User, Account, Category, Transaction
from app.logic import (
    create_transaction,
    calculate_total_expenses,
    calculate_total_income,
    calculate_net_balance,
    filter_transactions_by_category,
    filter_transactions_by_date
)
from pydantic import ValidationError

def main():
    print("==================================================")
    print(" EXPENSE TRACKING BACKEND - SCHEMA VALIDATION")
    print("==================================================\n")

    print("--- 1. Testing Valid Data ---")
    
    # --- Create 3 Valid Users ---
    user1 = User(
        user_id="U001", full_name="Alice Smith", email="alice@example.com",
        phone_number="+1234567890", created_at=datetime.now(timezone.utc)
    )
    user2 = User(
        user_id="U002", full_name="Bob Jones", email="bob@example.com",
        created_at=datetime.now(timezone.utc) # phone_number is optional
    )
    user3 = User(
        user_id="U003", full_name="Charlie Brown", email="charlie@example.com",
        created_at=datetime.now(timezone.utc)
    )
    print(f"Created 3 valid users: {user1.full_name}, {user2.full_name}, {user3.full_name}")

    # --- Create 5 Valid Accounts ---
    acc1 = Account(account_id="ACC001", account_type="Savings", balance=5000.0, currency="USD", user=user1)
    acc2 = Account(account_id="ACC002", account_type="Wallet", balance=150.0, currency="EUR", user=user2)
    acc3 = Account(account_id="ACC003", account_type="Credit", balance=2000.0, currency="USD", user=user1)
    acc4 = Account(account_id="ACC004", account_type="Current", balance=10000.0, currency="INR", user=user3)
    acc5 = Account(account_id="ACC005", account_type="Savings", balance=300.0, currency="USD", user=user2)
    print(f"Created 5 valid accounts.")

    # --- Create 5 Valid Categories ---
    cat_food = Category(category_id=1, name="Food", description="Groceries and dining out")
    cat_salary = Category(category_id=2, name="Salary", description="Monthly salary")
    cat_travel = Category(category_id=3, name="Travel", description="Flights, cabs, transit")
    cat_shopping = Category(category_id=4, name="Shopping", description="Clothes, electronics")
    cat_rent = Category(category_id=5, name="Rent", description="Monthly house rent")
    print(f"Created 5 valid categories.")

    # --- Create 20 Transactions ---
    transactions = []
    
    # Using a helper loop to generate some basic transactions
    for i in range(1, 16):
        txn = Transaction(
            transaction_id=f"TXN{i:03d}",
            amount=50.0 + (i * 10),
            transaction_type="expense",
            description=f"Expense #{i}",
            timestamp=datetime.now(timezone.utc),
            category=cat_food if i % 2 == 0 else cat_shopping,
            account=acc1 if i % 2 == 0 else acc2
        )
        transactions.append(txn)
        
    # Adding a few manual specific transactions
    transactions.append(Transaction(transaction_id="TXN016", amount=2000.0, transaction_type="income", description="June Salary", timestamp=datetime.now(timezone.utc), category=cat_salary, account=acc1))
    transactions.append(Transaction(transaction_id="TXN017", amount=500.0, transaction_type="expense", description="Rent Payment", timestamp=datetime.now(timezone.utc), category=cat_rent, account=acc1))
    transactions.append(Transaction(transaction_id="TXN018", amount=150.0, transaction_type="expense", description="Flight ticket", timestamp=datetime.now(timezone.utc), category=cat_travel, account=acc3))
    transactions.append(Transaction(transaction_id="TXN019", amount=3000.0, transaction_type="income", description="July Salary", timestamp=datetime.now(timezone.utc), category=cat_salary, account=acc4))
    transactions.append(Transaction(transaction_id="TXN020", amount=200.0, transaction_type="expense", description="New headphones", timestamp=datetime.now(timezone.utc), category=cat_shopping, account=acc5))

    print(f"Created {len(transactions)} valid transactions.")
    
    # ==========================================================================
    # SERIALIZATION (Model to Data)
    # ==========================================================================
    print("\n--- 2. Serialization (Model to JSON) ---")
    txn_example = transactions[15] # The June Salary transaction
    
    # .model_dump() converts the Pydantic model into a Python dictionary.
    txn_dict = txn_example.model_dump()
    print("As Python Dictionary (Type):", type(txn_dict))
    
    # .model_dump_json() converts the model directly to a JSON string.
    txn_json = txn_example.model_dump_json(indent=2)
    print("As JSON String:\n", txn_json[:250] + "\n... (truncated for brevity)")

    # ==========================================================================
    # DESERIALIZATION (Data to Model)
    # ==========================================================================
    print("\n--- 3. Deserialization (JSON to Model) ---")
    json_input = """
    {
      "transaction_id": "TXN1001",
      "amount": 2500.0,
      "transaction_type": "expense",
      "description": "Restaurant bill",
      "timestamp": "2026-06-18T20:30:00Z",
      "category": {
        "category_id": 1,
        "name": "Food",
        "description": "Food expenses"
      },
      "account": {
        "account_id": "ACC001",
        "account_type": "Savings",
        "balance": 5000.0,
        "currency": "USD",
        "user": {
            "user_id": "U001",
            "full_name": "Alice Smith",
            "email": "alice@example.com",
            "phone_number": "+1234567890",
            "created_at": "2026-06-18T10:00:00Z",
            "is_active": true
        }
      }
    }
    """
    
    # 1. Parse JSON string into a Python dictionary using standard json module
    parsed_json = json.loads(json_input)
    # 2. Pass the dictionary to our logic function which passes it to Pydantic
    deserialized_txn = create_transaction(parsed_json)
    
    print(f"Successfully deserialized Transaction ID: {deserialized_txn.transaction_id}")
    print(f"Parsed Amount: {deserialized_txn.amount}")
    print(f"Parsed Timestamp Type: {type(deserialized_txn.timestamp)}") # Notice it's a datetime object!
    
    # Add this to our list of transactions
    transactions.append(deserialized_txn)

    # ==========================================================================
    # BUSINESS LOGIC
    # ==========================================================================
    print("\n--- 4. Business Logic ---")
    print(f"Total Expenses: ${calculate_total_expenses(transactions):.2f}")
    print(f"Total Income: ${calculate_total_income(transactions):.2f}")
    print(f"Net Balance: ${calculate_net_balance(transactions):.2f}")
    
    food_txns = filter_transactions_by_category(transactions, "Food")
    print(f"Food Transactions Count: {len(food_txns)}")

    # ==========================================================================
    # INVALID DATA TESTING
    # ==========================================================================
    print("\n--- 5. Testing Invalid Data (Validation Errors) ---")
    # Pydantic is powerful because it catches bad data immediately and raises 
    # a ValidationError with specific details about what went wrong.

    invalid_cases = [
        # 1. Negative amount (violates custom validator)
        (
            "Negative Amount", 
            Transaction,
            {
                "transaction_id": "TXN003", "amount": -10, "transaction_type": "expense", 
                "description": "Test", "timestamp": "2026-06-18T20:30:00Z", 
                "category": cat_food.model_dump(), "account": acc1.model_dump()
            }
        ),
        # 2. Invalid Transaction ID (doesn't start with TXN)
        (
            "Invalid Transaction ID", 
            Transaction,
            {
                "transaction_id": "123003", "amount": 10, "transaction_type": "expense", 
                "description": "Test", "timestamp": "2026-06-18T20:30:00Z", 
                "category": cat_food.model_dump(), "account": acc1.model_dump()
            }
        ),
        # 3. Invalid Currency in Account
        (
            "Invalid Currency in Account", 
            Account,
            {
                "account_id": "ACC003", "account_type": "Savings", "balance": 100, 
                "currency": "GBP", # GBP is not in allowed list
                "user": user1.model_dump()
            }
        ),
        # 4. Empty Category Name (violates min_length)
        (
            "Empty Category Name", 
            Category,
            {
                "category_id": 3, "name": "", "description": "Empty name test"
            }
        ),
        # 5. Malformed Email
        (
            "Malformed Email", 
            User,
            {
                "user_id": "U003", "full_name": "Charlie", 
                "email": "not-an-email", # Will be caught by EmailStr
                "created_at": "2026-06-18T10:00:00Z"
            }
        )
    ]

    for name, model, data in invalid_cases:
        print(f"\n[Testing] {name}")
        try:
            # Attempt to instantiate the model with bad data
            model(**data)
            print("ERROR: This should have failed but didn't!")
        except ValidationError as e:
            # Pydantic raises a ValidationError containing a list of errors
            print("Caught Validation Error:")
            for err in e.errors():
                print(f" -> Field '{err['loc'][0]}': {err['msg']}")

if __name__ == "__main__":
    main()
