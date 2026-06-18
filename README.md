# Full-Stack Expense Tracking Backend

Welcome to the **Expense Tracking Backend** project! This project has evolved from a simple Python script into a production-grade, secure REST API. It handles incoming JSON data, cryptographically authenticates users, permanently stores data in PostgreSQL, and serves it via a fast, modern API.

## 🚀 How to Run the Project

Follow these steps carefully to get the entire system (Database + Web Server) running on your local machine.

### 1. Start the PostgreSQL Database (Docker)
You must have Docker installed and running on your computer.
1. Open your terminal in the root folder of this project.
2. Run the following command to spin up the database in the background:
   ```bash
   docker-compose up -d
   ```
*(Note: If port 5432 is already taken by a native database on your machine, we have mapped this Docker container to port `5433` locally to prevent conflicts).*

### 2. Install Python Dependencies
Ensure you are using Python 3.9+ and run:
```bash
pip install -r requirements.txt
```

### 3. Run Database Migrations (Alembic)
Before the Python app can save data, we need to instruct Alembic to build the physical tables (`users`, `transactions`, etc.) inside the empty PostgreSQL container.
```bash
alembic upgrade head
```

### 4. Start the Web Server
Start the FastAPI application:
```bash
uvicorn app.api:app --reload
```
The server is now live at [http://localhost:8000](http://localhost:8000).

## 🧪 How to Use the App

You have two ways to interact with this application:

### Option 1: The React Web App (Recommended)
We have built a sleek, minimalistic React frontend to interact with the API.
1. Open a new terminal and navigate to the frontend directory: `cd frontend_react`
2. Install dependencies: `npm install`
3. Start the dev server: `npm run dev`
4. Open your browser to **[http://localhost:5173](http://localhost:5173)**.
5. You can register, log in, manage transactions, and even **Bulk Import CSV** files directly from the dashboard! The CSV importer features a robust parser that automatically cleans headers and intelligently maps columns regardless of capitalization or naming variations (e.g., `Reason`, `Memo`, `Title` are all mapped to `description`).

### Option 2: The Swagger API Docs
FastAPI automatically generates interactive documentation for our API.
1. Go to **[http://localhost:8000/docs](http://localhost:8000/docs)**.
2. **Register a User:** Scroll to `POST /api/users/register`, click "Try it out", enter your details, and execute.
3. **Login:** Scroll to the top right and click the green **"Authorize"** button. Enter the email and password you just created to receive your JSON Web Token (JWT).
4. **Test Protected Routes:** Now that you are authenticated, you can safely test the CRUD routes (`GET`, `POST`, `PUT`, `DELETE` for `/api/transactions`).

---

## 🎓 Backend Engineering Overview

Are you using this project to learn backend engineering? I have written a **comprehensive guide** breaking down the concepts in this application.

Read the **[Backend Engineering Overview](Docs/engineering_overview.md)** to learn about:
- The evolution of data structures (Dictionaries -> TypedDicts -> Dataclasses -> Pydantic).
- How the internet works and how FastAPI operates under the hood.
- React.js from scratch.
- The differences between Interpreted and Compiled languages.
- Why we use Docker and PostgreSQL.

---

## 📁 Project Structure

The project is organized into distinct layers (Clean Architecture):

```text
Expense Tracking Backend/
├── app/                      # 🧠 The Python Backend
│   ├── api.py                # The Front Door (FastAPI Routing & Auth Dependency)
│   ├── auth.py               # Cryptography (JWT generation, Bcrypt password hashing)
│   ├── logic.py              # The Brains (Business logic & database orchestration)
│   ├── models.py             # Data Validation (Pydantic incoming/outgoing schemas)
│   ├── db_models.py          # Data Storage (SQLAlchemy ORM tables)
│   ├── database.py           # Database connection pool and dependency injection
│   └── cli.py                # Command-line tester
├── alembic/                  # 🕰️ Database Migration Tracker
├── docker-compose.yml        # 🐳 Container instructions for PostgreSQL
└── requirements.txt          # Python dependencies
```

---

## 🧠 Key Technologies & Concepts Implemented

1. **Schema Validation (Pydantic)**
   - All incoming JSON requests are strictly checked before they reach the logic layer (e.g., ensuring amounts are `> 0`, emails are properly formatted).
2. **Database Persistence (SQLAlchemy & PostgreSQL)**
   - We use an Object-Relational Mapper (ORM) to write Python code that securely translates into SQL queries, storing our data permanently.
3. **Database Migrations (Alembic)**
   - We track all changes to our database structure (like adding a `hashed_password` column) via version-controlled migration scripts.
4. **REST API Architecture (FastAPI)**
   - Full CRUD capability mapped cleanly to HTTP Verbs (`GET`, `POST`, `PUT`, `DELETE`).
   - Proper use of Path Parameters (`/api/transactions/{id}`) and HTTP Status Codes (`201 Created`, `404 Not Found`, `204 No Content`).
5. **Security & Authentication (JWT + Bcrypt)**
   - Passwords are mathematically hashed via `bcrypt` (never stored in plain text).
   - Stateless authentication is implemented using JSON Web Tokens (JWT).
   - FastAPI `Depends` middleware is used to "lock down" API routes, rejecting any request that lacks a valid JWT.
