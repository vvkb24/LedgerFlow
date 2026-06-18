# Expense Tracking Backend - Interview & Application Guide

This document is designed to prepare you for technical interviews based on the Expense Tracking Backend project. It covers common questions, advanced/critical questions, and real-world applications of the architecture you've built.

---

## Part 1: Project-Specific Interview Questions

**Q1: Can you walk me through the architecture of the Expense Tracking API you built?**
**Answer:** The project is a RESTful API built with Python and FastAPI. It follows a layered architecture:
- **Routing Layer (`api.py`):** Handles incoming HTTP requests and routes them to the appropriate logic.
- **Validation Layer (`models.py`):** Uses Pydantic to strictly validate incoming JSON payloads (e.g., ensuring amounts are positive, emails are valid).
- **Business Logic Layer (`logic.py`):** Contains the core operations, separating the API logic from the database logic.
- **Data Access Layer (`database.py` & `db_models.py`):** Uses SQLAlchemy ORM to communicate with a PostgreSQL database. 
- **Security Layer (`auth.py`):** Handles password hashing using `bcrypt` and stateless session management using JWTs (JSON Web Tokens).
- **Deployment:** The entire application and its database are containerized using Docker and orchestrated with Docker Compose.

**Q2: How did you handle user authentication and authorization?**
**Answer:** I implemented a stateless authentication system using JSON Web Tokens (JWT). When a user logs in with valid credentials (verified via bcrypt hashes), the server generates a JWT containing their `user_id` and an expiration time, signed with a secret key. For protected routes, I built a dependency injection "Bouncer" (`get_current_user`) that intercepts the request, verifies the JWT's cryptographic signature, and extracts the user. If the token is missing or invalid, it throws a `401 Unauthorized` error.

**Q3: How did you ensure your API doesn't crash when users send bad data?**
**Answer:** I utilized Pydantic for schema validation. Instead of writing manual `if` statements for every field, I defined strict Pydantic models with type hints and custom `@field_validator` decorators. For example, if a user tries to send a negative account balance, Pydantic automatically catches it. I also wrote a custom exception handler in FastAPI to catch `RequestValidationError`s and return clean, readable `422 Unprocessable Entity` JSON responses to the frontend instead of internal server errors.

**Q4: How did you test your application?**
**Answer:** I used `pytest` and `httpx` to build automated integration tests. To prevent tests from polluting the production PostgreSQL database, I configured a `conftest.py` fixture that uses FastAPI's `dependency_overrides`. It swaps the real database connection with a temporary, in-memory SQLite database. The tests programmatically simulate a user registering, logging in, extracting the JWT, and performing CRUD operations, fully verifying the API's behavior in milliseconds.

---

## Part 2: Technology-Specific Interview Questions

**Q5: Why did you choose FastAPI over Flask or Django?**
**Answer:** FastAPI was chosen for its performance and developer experience. Because it is built on Starlette and Pydantic, it is one of the fastest Python frameworks available. Additionally, it natively supports async/await, automatically generates interactive Swagger documentation, and uses Python type hints to provide instant data validation and editor autocompletion, which Flask and Django lack out-of-the-box.

**Q6: What is the difference between Pydantic models and SQLAlchemy models in your project?**
**Answer:** 
- **Pydantic Models (`models.py`):** These act as the "Front Door." They validate incoming JSON from the internet and serialize Python dictionaries into outgoing JSON. They do not know about the database.
- **SQLAlchemy Models (`db_models.py`):** These act as the "Basement." They map Python classes directly to SQL tables. They handle relationships (Foreign Keys) and database constraints but are not meant to validate raw user input.
Separating the two prevents security vulnerabilities (like mass-assignment attacks) and keeps concerns clean.

**Q7: Explain the concept of Dependency Injection as used in FastAPI.**
**Answer:** Dependency Injection is a design pattern where an object receives other objects that it depends on. In FastAPI, we use the `Depends()` keyword. For example, `db: Session = Depends(get_db)` tells FastAPI to automatically run the `get_db` function, yield a database connection, pass it into the route, and safely close it after the response is sent. It drastically reduces boilerplate code and makes testing incredibly easy because we can override dependencies during tests.

**Q8: Why did you use Docker and Docker Compose?**
**Answer:** Docker solves the "it works on my machine" problem. By writing a `Dockerfile`, I packaged the Python runtime, dependencies, and application code into an immutable image. Docker Compose allowed me to define a multi-container environment where the FastAPI container and the PostgreSQL container run side-by-side on a private network. This ensures the app runs exactly the same way in local development, testing, and production environments.

---

## Part 3: Extremely Critical / Advanced Questions

**Q9 (Critical): JWTs are stateless. If a user's account is hacked, how do you instantly revoke their JWT before it expires?**
**Answer:** Because JWTs are inherently stateless, the server doesn't check the database on every request to see if the token is valid; it only checks the cryptographic signature. To revoke a token instantly, we must introduce state. 
*Solutions:* 
1. **Token Blacklist/Blocklist:** Store revoked JWT signatures in a high-speed cache like Redis. The dependency injection "Bouncer" checks Redis on every request.
2. **Refresh Token Rotation:** Keep the Access Token lifespan extremely short (e.g., 5 minutes) and issue a long-lived Refresh Token. If a user is compromised, revoke the Refresh Token in the database. The attacker will lose access in <= 5 minutes.
3. **User Versioning:** Add a `token_version` integer to the database user row and include it in the JWT payload. If compromised, increment the integer in the database. Any token with an older version is instantly invalidated.

**Q10 (Critical): In your `save_transaction_to_db` logic, you perform multiple inserts (User, Account, Category, Transaction). What happens if the database crashes exactly after creating the Account but before the Transaction is saved?**
**Answer:** This is a classic distributed data problem. To handle this, we rely on **ACID transactions** provided by PostgreSQL. Because I pass a single SQLAlchemy `Session` into the logic, all those `db.add()` operations occur within a single database transaction. The data is only staged. If the Python server crashes or a database error occurs before `db.commit()` is called, the database automatically performs a **Rollback**. The partially created Account and Category disappear, ensuring the database is never left in an inconsistent state. 

**Q11 (Critical): How would you scale this application if it started receiving 10,000 requests per second?**
**Answer:**
1. **Application Scaling:** I would run multiple instances of the FastAPI container behind a Load Balancer (like NGINX or AWS ALB). Since JWT authentication is stateless, any container can handle any request.
2. **Database Scaling:** PostgreSQL would become the bottleneck. I would implement Connection Pooling (using PgBouncer) so we don't exhaust the database's connection limit. 
3. **Read/Write Replicas:** I would configure PostgreSQL read replicas to handle `GET` requests, keeping the primary database strictly for `POST/PUT/DELETE` mutations.
4. **Caching:** I would use Redis to cache highly requested data (like User Profiles or Category lists) to reduce database queries.
5. **Async DB Drivers:** I would migrate SQLAlchemy to use async drivers (`asyncpg`) to handle massive concurrent I/O operations without blocking the Python event loop.

---

## Part 4: Real-World Industry Applications

The architecture built in this project (FastAPI + Pydantic + SQLAlchemy + PostgreSQL + JWT + Docker) is the **industry standard** for modern microservices. Here is how this exact boilerplate is used across various industries:

### 1. Finance & Fintech (Banking Apps, Crypto Exchanges)
- **Application:** Building ledgers, payment gateways, and wallet tracking APIs.
- **Why it fits:** Pydantic ensures zero tolerance for bad financial data (e.g., negative transfer amounts). SQLAlchemy transactions ensure money isn't lost mid-transfer (ACID properties).

### 2. E-Commerce (Amazon, Shopify clones)
- **Application:** Managing shopping carts, inventory systems, and order processing.
- **Why it fits:** The API can be split into microservices (Inventory API, Order API, User API). The stateless JWT auth allows users to seamlessly jump between microservices without logging in multiple times.

### 3. Healthcare / EdTech (Patient Portals, E-learning platforms)
- **Application:** Secure portals where users access highly sensitive personal data.
- **Why it fits:** The strict Dependency Injection system acts as an impenetrable guard. You can easily inject role-based access control (RBAC) to ensure a "Student" cannot access a "Teacher" route, or a "Patient" cannot view another patient's records.

### 4. Internet of Things (IoT) & Logistics (Fleet Tracking, Smart Homes)
- **Application:** Ingesting millions of data points from sensors, delivery trucks, or smart thermostats.
- **Why it fits:** FastAPI's underlying async architecture (Starlette) is built to handle massive amounts of concurrent connections. It can efficiently ingest thousands of GPS coordinates a second without choking.

### 5. Artificial Intelligence & Machine Learning (SaaS platforms)
- **Application:** Building APIs that serve AI models (like wrapping an LLM or image recognition model).
- **Why it fits:** Python is the native language of AI. FastAPI is currently the absolute #1 choice for AI engineers building wrappers around PyTorch/TensorFlow models due to its speed, Pythonic typing, and seamless integration with the AI ecosystem.
