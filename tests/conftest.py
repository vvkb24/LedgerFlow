import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.api import app
from app.database import Base, get_db

# 1. Setup an IN-MEMORY SQLite database specifically for testing
# This ensures tests are blazing fast and never touch your real PostgreSQL data!
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

# connect_args={"check_same_thread": False} is needed for SQLite
# poolclass=StaticPool ensures the in-memory DB persists across requests in a single test
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 2. Pytest Fixture: Create tables before each test suite runs
@pytest.fixture(scope="session", autouse=True)
def setup_database():
    # Build all tables in the empty SQLite database
    Base.metadata.create_all(bind=engine)
    yield # Let the tests run
    # (Optional) Drop all tables after tests finish
    Base.metadata.drop_all(bind=engine)

# 3. Pytest Fixture: Provide a database session for a specific test
@pytest.fixture()
def db_session():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

# 4. Pytest Fixture: Override the FastAPI app's dependency
@pytest.fixture()
def client(db_session):
    # Dependency Override: Whenever FastAPI wants `get_db`, give it `db_session` instead!
    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    
    # Return a TestClient that pretends to be the internet browser
    with TestClient(app) as test_client:
        yield test_client
    
    # Clean up overrides after the test
    app.dependency_overrides.clear()
