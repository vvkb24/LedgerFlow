from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.database import Base

# ==============================================================================
# DATABASE MODELS (SQLAlchemy)
# ==============================================================================
# Unlike Pydantic models (which validate incoming JSON data), these classes 
# literally define the structure of our PostgreSQL database tables.

class DBUser(Base):
    __tablename__ = "users"
    
    # Primary Key: The unique, undeniable identifier for this row.
    # index=True makes searching by user_id incredibly fast.
    user_id = Column(String, primary_key=True, index=True)
    
    # nullable=False means this column CANNOT be empty (it's required).
    full_name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=True) # Added for Phase 5 (Authentication)
    phone_number = Column(String, nullable=True)
    
    # We use a lambda function here so that the current time is evaluated exactly 
    # when the row is inserted, rather than when the server starts.
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    is_active = Column(Boolean, default=True)

    # Relationship: A user can have many accounts (One-to-Many).
    # back_populates ties this to the 'user' attribute in DBAccount.
    accounts = relationship("DBAccount", back_populates="user")


class DBAccount(Base):
    __tablename__ = "accounts"
    
    account_id = Column(String, primary_key=True, index=True)
    account_type = Column(String, nullable=False)
    balance = Column(Float, default=0.0)
    currency = Column(String, nullable=False)
    
    # Foreign Key: This column stores the user_id of the owner.
    # It mathematically enforces that an account MUST belong to a real user.
    user_id = Column(String, ForeignKey("users.user_id"), nullable=False)
    
    # Relationships
    user = relationship("DBUser", back_populates="accounts")
    transactions = relationship("DBTransaction", back_populates="account")


class DBCategory(Base):
    __tablename__ = "categories"
    
    # autoincrement=True means the database will handle giving this 1, 2, 3, etc.
    category_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, unique=True, index=True, nullable=False)
    description = Column(String, nullable=True)
    
    # Relationships
    transactions = relationship("DBTransaction", back_populates="category")


class DBTransaction(Base):
    __tablename__ = "transactions"
    
    transaction_id = Column(String, primary_key=True, index=True)
    amount = Column(Float, nullable=False)
    transaction_type = Column(String, nullable=False) # 'income' or 'expense'
    description = Column(String, nullable=False)
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    
    # Foreign Keys: A transaction must belong to a specific account and category.
    account_id = Column(String, ForeignKey("accounts.account_id"), nullable=False)
    category_id = Column(Integer, ForeignKey("categories.category_id"), nullable=False)
    
    # Relationships: These allow us to do things like `my_transaction.category.name`
    # in Python, and SQLAlchemy will automatically fetch the data for us!
    account = relationship("DBAccount", back_populates="transactions")
    category = relationship("DBCategory", back_populates="transactions")
