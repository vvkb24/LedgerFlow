# Production Expense Tracking System - Implementation Roadmap

Welcome to the team! As your mentor, I've outlined the architectural roadmap for our Expense Tracking System. We are currently sitting at Phase 1/2 with an in-memory mock database and basic Pydantic validation. Our ultimate goal is a production-grade system.

## ⚠️ User Review Required

Before we write a single line of code, please review this roadmap. Since you already have the foundation of `models.py` and `logic.py` built out (Phase 1 & 2), we have a decision to make:

> [!IMPORTANT]  
> **Do you want to start immediately on Phase 3 (Refining the FastAPI Endpoints) or Phase 4 (Building the PostgreSQL/SQLAlchemy Database)?** 
> 
> My recommendation is to jump straight to **Phase 4 (Database Layer)** so we have a permanent home for our data before we build out the complex API routes.

## Proposed Evolution Phases

### Phase 1: Solidifying Data Validation (Current State)
We have already built our `models.py` using Pydantic. We understand how to protect our app from bad data (negative amounts, invalid currencies).

### Phase 2: Business Logic Layer (Current State)
We have our `logic.py` to calculate totals and filter transactions. We understand how to separate calculations from data storage.

### Phase 3: REST API Foundation (FastAPI)
We will expand `api.py` to include proper CRUD (Create, Read, Update, Delete) RESTful endpoints.
- **Concepts:** HTTP Methods (GET, POST, PUT, DELETE), Path/Query Parameters, Status Codes (200, 201, 404, 422).

### Phase 4: Persistence Layer (SQLAlchemy & PostgreSQL) - *Recommended Next Step*
We will replace our in-memory `db_transactions` list with a real PostgreSQL database.
- **Concepts:** Relational Database Design, Object-Relational Mapping (ORM), Sessions, Migrations (Alembic).

### Phase 5: Authentication & Security (JWT)
We will secure our API so only logged-in users can see their own expenses.
- **Concepts:** Hashing Passwords, JSON Web Tokens (JWT), Middleware, Dependency Injection.

### Phase 6: Testing (Pytest)
We will write automated tests to prove our code works perfectly.
- **Concepts:** Unit Testing, Integration Testing, Fixtures, Mocking.

### Phase 7: Containerization & Deployment (Docker)
We will package our app so it can run on any server in the world.
- **Concepts:** Dockerfiles, Docker Compose, Environment Variables, Production vs. Development.

## Verification Plan

### Automated Tests
- We will use `pytest` in Phase 6 to automatically verify every API endpoint and database query.

### Manual Verification
- We will test endpoints locally using FastAPI's built-in Swagger UI (`http://localhost:8000/docs`).
- We will use database GUI tools (like DBeaver or pgAdmin) to visually verify data is saving correctly in PostgreSQL.
