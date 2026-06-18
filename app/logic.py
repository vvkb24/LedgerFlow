from typing import List, Optional
from sqlalchemy.orm import Session
from app.models import Transaction, ExpenseStatistics
from app.db_models import DBTransaction, DBAccount, DBCategory, DBUser
from app.auth import verify_password

def authenticate_user(db: Session, email: str, password: str) -> Optional[DBUser]:
    """
    Looks up a user by email, and verifies their password.
    Returns the user if successful, None if it fails.
    """
    user = db.query(DBUser).filter(DBUser.email == email).first()
    if not user:
        return None
    # If the user has no password yet (e.g. legacy test users), authentication fails
    if not user.hashed_password:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user

import uuid
from app.auth import get_password_hash
from app.models import UserCreate

def register_new_user(db: Session, user_data: UserCreate) -> DBUser:
    """
    Checks if email already exists.
    Hashes the password.
    Saves the new DBUser to PostgreSQL.
    """
    # 1. Check if email exists
    existing_user = db.query(DBUser).filter(DBUser.email == user_data.email).first()
    if existing_user:
        raise ValueError(f"Email {user_data.email} is already registered.")
        
    # 2. Hash the password
    hashed_pwd = get_password_hash(user_data.password)
    
    # 3. Create the DBUser
    new_user = DBUser(
        user_id=f"USR{str(uuid.uuid4())[:8].upper()}",
        full_name=user_data.full_name,
        email=user_data.email,
        hashed_password=hashed_pwd,
        phone_number=user_data.phone_number
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

def save_transaction_to_db(db: Session, txn_data: Transaction) -> DBTransaction:
    """
    Translates a Pydantic Model (Front Door) into SQLAlchemy Models (Basement)
    and saves them permanently into PostgreSQL.
    """
    # 1. Ensure the User exists in DB
    user = db.query(DBUser).filter(DBUser.user_id == txn_data.account.user.user_id).first()
    if not user:
        user = DBUser(
            user_id=txn_data.account.user.user_id,
            full_name=txn_data.account.user.full_name,
            email=txn_data.account.user.email,
            phone_number=txn_data.account.user.phone_number,
            created_at=txn_data.account.user.created_at,
            is_active=txn_data.account.user.is_active
        )
        db.add(user)

    # 2. Ensure the Account exists
    account = db.query(DBAccount).filter(DBAccount.account_id == txn_data.account.account_id).first()
    if not account:
        account = DBAccount(
            account_id=txn_data.account.account_id,
            account_type=txn_data.account.account_type,
            balance=txn_data.account.balance,
            currency=txn_data.account.currency,
            user_id=user.user_id
        )
        db.add(account)

    # 3. Ensure the Category exists
    category = db.query(DBCategory).filter(DBCategory.category_id == txn_data.category.category_id).first()
    if not category:
        category = DBCategory(
            category_id=txn_data.category.category_id,
            name=txn_data.category.name,
            description=txn_data.category.description
        )
        db.add(category)

    # 4. Finally, create the Transaction!
    db_txn = DBTransaction(
        transaction_id=txn_data.transaction_id,
        amount=txn_data.amount,
        transaction_type=txn_data.transaction_type,
        description=txn_data.description,
        timestamp=txn_data.timestamp,
        account_id=account.account_id,
        category_id=category.category_id
    )
    
    # Add to the Session workspace and commit to PostgreSQL
    db.add(db_txn)
    db.commit()
    db.refresh(db_txn) # Updates db_txn with any auto-generated DB fields
    
    return db_txn

def save_bulk_transactions_to_db(db: Session, transactions: List[Transaction]) -> int:
    """
    Saves multiple transactions to the database in a single transaction block for performance.
    """
    count = 0
    for txn_data in transactions:
        # Same logic as save_transaction_to_db, but without committing per row
        user = db.query(DBUser).filter(DBUser.user_id == txn_data.account.user.user_id).first()
        if not user:
            user = DBUser(
                user_id=txn_data.account.user.user_id,
                full_name=txn_data.account.user.full_name,
                email=txn_data.account.user.email,
                phone_number=txn_data.account.user.phone_number,
                created_at=txn_data.account.user.created_at,
                is_active=txn_data.account.user.is_active
            )
            db.add(user)

        account = db.query(DBAccount).filter(DBAccount.account_id == txn_data.account.account_id).first()
        if not account:
            account = DBAccount(
                account_id=txn_data.account.account_id,
                account_type=txn_data.account.account_type,
                balance=txn_data.account.balance,
                currency=txn_data.account.currency,
                user_id=user.user_id
            )
            db.add(account)

        category = db.query(DBCategory).filter(DBCategory.category_id == txn_data.category.category_id).first()
        if not category:
            category = DBCategory(
                category_id=txn_data.category.category_id,
                name=txn_data.category.name,
                description=txn_data.category.description
            )
            db.add(category)

        db_txn = DBTransaction(
            transaction_id=txn_data.transaction_id,
            amount=txn_data.amount,
            transaction_type=txn_data.transaction_type,
            description=txn_data.description,
            timestamp=txn_data.timestamp,
            account_id=account.account_id,
            category_id=category.category_id
        )
        db.add(db_txn)
        # Flush to make sure IDs and constraints are checked but without committing yet
        db.flush() 
        count += 1
        
    db.commit() # Commit all at once!
    return count

from typing import Optional

def get_transaction_by_id(db: Session, transaction_id: str) -> Optional[DBTransaction]:
    """
    Retrieves a single transaction from the database by its unique ID.
    Returns None if the transaction does not exist.
    """
    # This fires a SQL query: SELECT * FROM transactions WHERE transaction_id = 'XYZ' LIMIT 1;
    return db.query(DBTransaction).filter(DBTransaction.transaction_id == transaction_id).first()

def delete_transaction_by_id(db: Session, transaction_id: str) -> bool:
    """
    Deletes a transaction from the database permanently.
    Returns True if successfully deleted, False if the transaction was not found.
    """
    db_txn = get_transaction_by_id(db, transaction_id)
    if not db_txn:
        return False
        
    db.delete(db_txn)
    db.commit()
    return True

def update_transaction_by_id(db: Session, transaction_id: str, new_data: Transaction) -> Optional[DBTransaction]:
    """
    Completely replaces an existing transaction's data.
    """
    db_txn = get_transaction_by_id(db, transaction_id)
    if not db_txn:
        return None
        
    # 1. Update basic fields
    db_txn.amount = new_data.amount
    db_txn.transaction_type = new_data.transaction_type
    db_txn.description = new_data.description
    db_txn.timestamp = new_data.timestamp
    
    # 2. Check if the new category exists, if not, create it
    category = db.query(DBCategory).filter(DBCategory.category_id == new_data.category.category_id).first()
    if not category:
        category = DBCategory(category_id=new_data.category.category_id, name=new_data.category.name)
        db.add(category)
    
    db_txn.category_id = category.category_id
    
    # Save the changes
    db.commit()
    db.refresh(db_txn)
    return db_txn

def calculate_total_expenses(transactions: List[Transaction]) -> float:
    """Calculates total expenses from a list of transactions."""
    total = 0.0
    for txn in transactions:
        if txn.transaction_type == "expense":
            total += txn.amount
    return total

def calculate_total_income(transactions: List[Transaction]) -> float:
    """Calculates total income from a list of transactions."""
    total = 0.0
    for txn in transactions:
        if txn.transaction_type == "income":
            total += txn.amount
    return total

def calculate_net_balance(transactions: List[Transaction]) -> float:
    """Calculates net balance (income - expense)."""
    income = calculate_total_income(transactions)
    expense = calculate_total_expenses(transactions)
    return income - expense

def filter_transactions_by_category(transactions: List[Transaction], category_name: str) -> List[Transaction]:
    """Filters transactions matching a specific category name."""
    filtered = []
    for txn in transactions:
        # We can easily access nested properties like txn.category.name 
        # because of our nested Pydantic models.
        if txn.category.name.lower() == category_name.lower():
            filtered.append(txn)
    return filtered

def filter_transactions_by_date(transactions: List[Transaction], year: int, month: int) -> List[Transaction]:
    """Filters transactions by specific year and month."""
    filtered = []
    for txn in transactions:
        # Pydantic automatically converted the timestamp string into a Python datetime object!
        if txn.timestamp.year == year and txn.timestamp.month == month:
            filtered.append(txn)
    return filtered
