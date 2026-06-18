from datetime import datetime
from typing import List, Optional, Dict
from dataclasses import dataclass
from pydantic import BaseModel, EmailStr, Field, field_validator
import re

# ==============================================================================
# 1. DATACLASSES
# ==============================================================================
# Dataclasses are built-in to Python and are great for simple data structures 
# where strict external validation isn't needed. They are typically used for 
# internal business logic, summarization, and moving data around within your app.

@dataclass
class UserSummary:
    """Summary of a user's details for internal use."""
    user_id: str
    full_name: str
    email: str

@dataclass
class AccountSummary:
    """Summary of an account for internal use."""
    account_id: str
    account_type: str
    balance: float

@dataclass
class ExpenseStatistics:
    """Calculated statistics for reporting."""
    total_income: float
    total_expense: float
    net_balance: float
    transaction_count: int


# ==============================================================================
# 2. PYDANTIC MODELS
# ==============================================================================
# Pydantic is a library for data parsing and validation. It is widely used in 
# modern frameworks like FastAPI. It enforces strict types and runs validation 
# rules when data enters or leaves your system (e.g., from an API request).

class User(BaseModel):
    user_id: str = Field(..., description="Unique user identifier")
    full_name: str = Field(..., description="User's full name")
    email: EmailStr = Field(..., description="Valid email address")
    phone_number: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    is_active: bool = True

class UserCreate(BaseModel):
    """Schema for validating incoming User Registration JSON."""
    full_name: str = Field(..., description="User's full name", min_length=2)
    email: EmailStr = Field(..., description="Valid email address")
    password: str = Field(..., description="Raw password, must be at least 8 characters", min_length=8)
    phone_number: Optional[str] = None

class UserResponse(BaseModel):
    """Schema for sending User data back to the frontend (excludes the password)."""
    user_id: str
    full_name: str
    email: EmailStr
    is_active: bool
    created_at: datetime

class Account(BaseModel):
    """Account representation containing a User."""
    account_id: str
    account_type: str
    balance: float
    currency: str
    # Nested Model: This embeds the User model inside the Account model.
    # When creating an Account, you must provide valid User data.
    user: User 

    # --- CUSTOM VALIDATORS ---
    # @field_validator allows us to write custom Python logic to check a specific field.
    @field_validator('balance')
    @classmethod
    def validate_balance(cls, v: float) -> float:
        if v < 0:
            raise ValueError("Account balance cannot be negative")
        return v

    @field_validator('currency')
    @classmethod
    def validate_currency(cls, v: str) -> str:
        allowed = ["INR", "USD", "EUR"]
        if v not in allowed:
            raise ValueError(f"Currency must be one of {allowed}")
        return v

    @field_validator('account_type')
    @classmethod
    def validate_account_type(cls, v: str) -> str:
        allowed = ["Savings", "Current", "Credit", "Wallet"]
        if v not in allowed:
            raise ValueError(f"Account type must be one of {allowed}")
        return v

class Category(BaseModel):
    """Category of a transaction."""
    category_id: int
    name: str = Field(..., min_length=1, description="Category name cannot be empty")
    description: str

class Transaction(BaseModel):
    """Transaction representation containing Category and Account."""
    transaction_id: str
    amount: float
    transaction_type: str
    description: str = Field(..., min_length=1, description="Description cannot be empty")
    timestamp: datetime
    # Nested Models
    category: Category 
    account: Account 

    @field_validator('amount')
    @classmethod
    def validate_amount(cls, v: float) -> float:
        if v <= 0:
            raise ValueError("Amount must be greater than 0")
        return v

    @field_validator('transaction_id')
    @classmethod
    def validate_transaction_id(cls, v: str) -> str:
        if not v.startswith("TXN"):
            raise ValueError("Transaction ID must start with 'TXN'")
        return v

    @field_validator('transaction_type')
    @classmethod
    def validate_transaction_type(cls, v: str) -> str:
        allowed = ["income", "expense"]
        if v not in allowed:
            raise ValueError(f"Transaction type must be one of {allowed}")
        return v
