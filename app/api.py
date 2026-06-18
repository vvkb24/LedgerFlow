from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.exceptions import RequestValidationError
from app.models import Transaction
from typing import List
from datetime import datetime, timezone

# Initialize the FastAPI app
app = FastAPI(title="Expense Tracking API")

# --- CORS Middleware ---
# Browsers block web pages from making requests to different domains/ports for security.
# Our React app will run on port 5173, and FastAPI on 8000. 
# We must explicitly tell FastAPI to "trust" the React app's origin.
from fastapi.middleware.cors import CORSMiddleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"], # React Vite defaults
    allow_credentials=True,
    allow_methods=["*"], # Allow GET, POST, PUT, DELETE, etc.
    allow_headers=["*"], # Allow all headers (especially Authorization)
)

# Mount the static directory so we can serve our HTML/CSS/JS frontend
app.mount("/static", StaticFiles(directory="frontend"), name="frontend")

# In-memory "database" to store our transactions
db_transactions: List[Transaction] = []

# --- Custom Exception Handler for Pydantic Errors ---
# By default, FastAPI returns a 422 Unprocessable Entity when Pydantic fails validation.
# We will intercept it here to format the error nicely for our frontend.
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = []
    for error in exc.errors():
        # "loc" tells us exactly which nested field failed (e.g., ['body', 'account', 'currency'])
        field = " -> ".join([str(loc) for loc in error['loc'][1:]]) 
        errors.append(f"Error in '{field}': {error['msg']}")
    
    return JSONResponse(
        status_code=422,
        content={"detail": "Schema Validation Failed!", "errors": errors},
    )

from fastapi import Depends
from sqlalchemy.orm import Session
from app.database import get_db
import app.logic as logic

from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from app.auth import create_access_token, SECRET_KEY, ALGORITHM
from jose import JWTError, jwt
from app.db_models import DBUser

# This tells FastAPI where our login endpoint is
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """
    This is our "Bouncer" Dependency. 
    It intercepts the incoming request, grabs the JWT token, and cryptographically verifies it.
    """
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        # 1. Decode the token using our secret key
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        # If the token is fake or expired, it crashes here
        raise credentials_exception
        
    # 2. Check if the user still exists in the database
    user = db.query(DBUser).filter(DBUser.email == email).first()
    if user is None:
        raise credentials_exception
    return user

from app.models import UserCreate, UserResponse

@app.post("/api/users/register", response_model=UserResponse, status_code=201)
async def register_user(user_data: UserCreate, db: Session = Depends(get_db)):
    """
    Registers a new user. 
    Expects a JSON body matching UserCreate (including a plain-text password).
    Returns a UserResponse (excluding the password).
    """
    try:
        new_user = logic.register_new_user(db, user_data)
        return new_user
    except ValueError as e:
        # If the logic layer raises a ValueError (e.g., email already exists),
        # we catch it and return a 400 Bad Request to the frontend.
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/token")
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """
    The official Login endpoint.
    Users send their email (username) and password here to get a JWT token.
    """
    user = logic.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Incorrect email or password", headers={"WWW-Authenticate": "Bearer"})
        
    # Generate the JWT
    access_token = create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}

# --- API Endpoints ---
# Notice we added `current_user: DBUser = Depends(get_current_user)` to every route!
# If a request doesn't have a valid JWT token, it gets blocked before our code even runs.

@app.post("/api/transactions", status_code=201)
async def create_transaction(transaction: Transaction, db: Session = Depends(get_db), current_user: DBUser = Depends(get_current_user)):
    db_txn = logic.save_transaction_to_db(db, transaction)
    return {
        "message": "Transaction successfully validated and saved to PostgreSQL!",
        "transaction_id": db_txn.transaction_id,
        "owner": current_user.email
    }

@app.post("/api/transactions/bulk", status_code=201)
async def create_bulk_transactions(transactions: List[Transaction], db: Session = Depends(get_db), current_user: DBUser = Depends(get_current_user)):
    count = logic.save_bulk_transactions_to_db(db, transactions)
    return {
        "message": f"Successfully imported {count} transactions!",
        "count": count
    }

@app.get("/api/transactions")
async def get_transactions(db: Session = Depends(get_db), current_user: DBUser = Depends(get_current_user)):
    from app.db_models import DBTransaction
    all_txns = db.query(DBTransaction).all()
    return all_txns

@app.get("/api/transactions/{transaction_id}")
async def get_single_transaction(transaction_id: str, db: Session = Depends(get_db), current_user: DBUser = Depends(get_current_user)):
    db_txn = logic.get_transaction_by_id(db, transaction_id)
    if not db_txn:
        raise HTTPException(status_code=404, detail=f"Transaction '{transaction_id}' not found.")
    return db_txn

@app.delete("/api/transactions/{transaction_id}", status_code=204)
async def delete_transaction(transaction_id: str, db: Session = Depends(get_db), current_user: DBUser = Depends(get_current_user)):
    success = logic.delete_transaction_by_id(db, transaction_id)
    if not success:
        raise HTTPException(status_code=404, detail=f"Transaction '{transaction_id}' not found.")
    return None

@app.put("/api/transactions/{transaction_id}")
async def update_transaction(transaction_id: str, transaction: Transaction, db: Session = Depends(get_db), current_user: DBUser = Depends(get_current_user)):
    db_txn = logic.update_transaction_by_id(db, transaction_id, transaction)
    if not db_txn:
        raise HTTPException(status_code=404, detail=f"Transaction '{transaction_id}' not found.")
    return {
        "message": "Transaction updated successfully!",
        "transaction_id": db_txn.transaction_id
    }

# Provide a root redirect to our static index.html
from fastapi.responses import RedirectResponse
@app.get("/")
async def root():
    return RedirectResponse(url="/static/index.html")

