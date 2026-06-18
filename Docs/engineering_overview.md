# 🧠 Engineering Overview: Full-Stack Expense Tracker

This document explains the "Why" and "How" behind the architecture of this project. It is intended to help you understand the systems at play so you can confidently explain the engineering decisions in an interview.

---

## 1. The Big Picture: Client-Server Architecture

This project is broken into two completely independent pieces of software that talk to each other over the internet (or in our case, `localhost`). 

1. **The Client (Frontend):** A React.js application running in the user's browser. It is responsible *only* for painting the UI and capturing user clicks.
2. **The Server (Backend):** A FastAPI Python application running on a server. It is responsible for security, business logic, and permanent data storage.

**Why separate them?** 
This is called "Decoupling". If we want to build a mobile app later (iOS/Android), we don't have to rewrite the backend. The mobile app can just talk to the exact same FastAPI endpoints that our React app uses.

---

## 2. The Backend: Clean Architecture

The Python backend is organized in layers to prevent "Spaghetti Code" (code where everything is tangled together).

### Layer 1: The Front Door (`api.py`)
This is the only file that talks to the outside world. It uses FastAPI to create endpoints (`GET /api/transactions`). 
* **Its Job:** Check if the user has a valid VIP pass (JWT Auth Token), parse the incoming JSON, and immediately hand it off to the next layer. It does *not* do complex math or talk to the database directly.

### Layer 2: The Bouncer (`models.py` / Pydantic)
Before the data even reaches our logic, Pydantic acts as a strict bouncer. If a user tries to send an expense `amount: -50`, Pydantic intercepts the JSON, sees it violates the `> 0` rule, and throws a `422 Unprocessable Entity` error before our database even knows what happened.

### Layer 3: The Brains (`logic.py`)
This is where the actual business logic lives. Once the data passes Pydantic, `logic.py` figures out what to do with it. It calculates balances, checks if emails already exist, and orchestrates the database models.

### Layer 4: The Basement (`db_models.py` & SQLAlchemy)
This layer translates our Python objects into SQL tables. SQLAlchemy is an Object-Relational Mapper (ORM). Instead of writing raw SQL strings (`INSERT INTO transactions...`), we write Python code, and SQLAlchemy safely generates the SQL, protecting us from SQL Injection attacks.

---

## 3. The Database & State Management

### PostgreSQL (The Vault)
We use PostgreSQL as our permanent storage. Why? Because it is a robust, ACID-compliant relational database. "Relational" means we can link data together—a Transaction belongs to a Category, which belongs to an Account, which belongs to a User.

### Alembic (Time Travel for Databases)
As the project grows, we might need to add a new column to a table (e.g., adding `profile_picture` to the `Users` table). We use **Alembic** to generate "Migration Scripts". These scripts track the history of our database schema, allowing us to safely upgrade (or rollback) our production database without deleting user data.

---

## 4. Security: Authentication & Authorization

### Bcrypt Password Hashing
We **never** save plain-text passwords in the database. When a user registers, we run their password through `bcrypt`, a cryptographic hashing algorithm with a "salt". Even if a hacker steals our entire database, they will only see random gibberish (e.g., `$2b$12$Kix...`) and cannot reverse-engineer the passwords.

### JSON Web Tokens (JWT)
HTTP is "Stateless"—it has no memory. When you log in, the server immediately forgets who you are the second it finishes responding.
To solve this, we generate a **JWT** when you log in. It is a mathematically signed string that acts like a VIP wristband.
Every time the React frontend makes a request, it attaches this token to the `Authorization` header. Our FastAPI server intercepts the request, verifies the cryptographic signature (to ensure no one tampered with it), and extracts the user's ID. 

---

## 5. The Frontend: React & Vite

### Component-Based UI
Instead of writing one massive HTML file, React lets us build reusable "Components" (like buttons, tables, and charts). When the data changes, React selectively updates only the part of the screen that needs changing (using the Virtual DOM), making the app feel lightning fast.

### PapaParse & Client-Side Processing
We implemented a Bulk CSV Upload feature. Instead of uploading a heavy file to the server and waiting for it to process, we use `PapaParse` to parse the file *locally* inside the user's browser. This leverages the user's CPU, making the parsing instantaneous, and we only send the final, cleaned data to the backend.
To make the import robust against different bank CSV formats, our frontend parser actively cleans headers (lowercasing and trimming) and uses a fallback system to dynamically map columns (e.g., mapping `Reason`, `Memo`, or `Title` to the `description` field) preventing import crashes.

---

## 6. Infrastructure: Dockerization

We wrapped both our Database and our Python API inside **Docker Containers**.
* **Why?** "It works on my machine" is the most common problem in software engineering. By using Docker, we package the app along with its exact operating system environment, Python version, and dependencies. If it runs on your laptop, it is mathematically guaranteed to run exactly the same way on an AWS server in the cloud.
