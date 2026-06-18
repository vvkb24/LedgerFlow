from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# The Database URL tells SQLAlchemy exactly where our database lives and how to log in.
# Format: database_type+driver://user:password@host:port/database_name
# We set these exact credentials in our docker-compose.yml file!
import os

# We use os.getenv so Docker can dynamically inject the connection URL!
# If it's not found (like when you run it locally without Docker), it defaults to localhost.
SQLALCHEMY_DATABASE_URL = os.getenv(
    "DATABASE_URL", 
    "postgresql+psycopg2://myuser:mypassword@127.0.0.1:5433/expensedb"
)

# 1. The Engine
# The Engine is the core interface to the database. It manages the actual 
# physical TCP network connections to PostgreSQL.
engine = create_engine(SQLALCHEMY_DATABASE_URL)

# 2. The Session Factory
# A Session is a temporary "workspace" for your objects. When you want to 
# save a Transaction, you add it to a Session, and then "commit" the session.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 3. The Base Class
# SQLAlchemy is an ORM (Object-Relational Mapper). This means we write Python 
# Classes, and it magically turns them into SQL Tables.
# Every database class we write in the future MUST inherit from this Base class.
Base = declarative_base()

# 4. Dependency Injection (FastAPI specific)
# This function is critical. Every time a user sends a web request to our API,
# this function will create a fresh, new database session for them.
# The 'yield' keyword ensures that once the request is done, the 'finally' block
# executes and safely closes the connection, preventing database crashes!
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
