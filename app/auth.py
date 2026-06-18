from datetime import datetime, timedelta, timezone
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext

# ==============================================================================
# AUTHENTICATION LOGIC (Security & JWTs)
# ==============================================================================

# SECURITY WARNING: In a real production app, this SECRET_KEY must be stored securely
# in an environment variable (.env file) and NEVER committed to GitHub!
# If someone steals this key, they can generate fake access tokens and hack any account.
SECRET_KEY = "super_secret_temporary_key_for_tutorial_purposes_only"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# This tells Passlib we want to use the bcrypt algorithm to hash our passwords.
# bcrypt is the industry standard because it is intentionally slow, preventing hackers
# from guessing passwords quickly using brute-force.
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Compares a normal, readable password (e.g., 'mypassword123') against 
    the scrambled hash stored in our PostgreSQL database.
    """
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """
    Takes a plain text password and mathematically scrambles it into an irreversible hash.
    """
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Generates a JSON Web Token (JWT).
    Think of a JWT like a temporary digital hotel keycard.
    1. The user gives us their password at the front desk.
    2. If correct, we hand them this JWT keycard.
    3. The keycard contains their 'user_id' (so we know who they are) and an 'expiration_date'.
    4. They hand this keycard to the bouncer (FastAPI) every time they try to access a protected route.
    """
    to_encode = data.copy()
    
    # Calculate when this token expires
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
        
    # Add the expiration time to the token's internal payload
    to_encode.update({"exp": expire})
    
    # Cryptographically sign the token using our SECRET_KEY
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt
