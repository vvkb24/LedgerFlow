# Simulate Real-Time Scenario: Full-Stack Expense Tracker

We will transform our current Pydantic schema validation logic into a living, breathing web application. This will simulate a real-world scenario where a web frontend sends JSON data to a backend server.

## User Review Required
> [!IMPORTANT]
> To make this work, we need to introduce a web framework called **FastAPI**. FastAPI is the industry standard for Python backends because it has built-in, automatic integration with Pydantic. It will serve our frontend and handle our API routes. Please review the plan below and let me know if you approve.

## Proposed Changes

We will restructure our `Expense Tracking Backend` folder to serve as a complete web application.

### Backend (FastAPI)

#### [MODIFY] [requirements.txt](file:///c:/Users/vamsh/Documents/UP_Coming/2.Phase%201/Day%204%20Transaction%20Schema%20Validation/Expense%20Tracking%20Backend/requirements.txt)
- Add `fastapi` and `uvicorn` (the server that runs FastAPI) to our dependencies.

#### [NEW] [api.py](file:///c:/Users/vamsh/Documents/UP_Coming/2.Phase%201/Day%204%20Transaction%20Schema%20Validation/Expense%20Tracking%20Backend/api.py)
- Create a FastAPI application instance.
- Create an in-memory "database" (just a python `list`) to store valid transactions.
- Create a `POST /api/transactions` endpoint that automatically uses our existing Pydantic `Transaction` model to validate incoming JSON.
- Create a `GET /api/transactions` endpoint to retrieve saved transactions.
- Mount the static files so FastAPI can serve our HTML frontend.

---

### Frontend (HTML/CSS/JS)

#### [NEW] [static/index.html](file:///c:/Users/vamsh/Documents/UP_Coming/2.Phase%201/Day%204%20Transaction%20Schema%20Validation/Expense%20Tracking%20Backend/static/index.html)
- A modern, styled HTML form that allows users to input a transaction amount, description, type, and select a category.
- When the user clicks "Submit", we will use Javascript to construct the exact nested JSON structure required by our Pydantic model.
- We will use the `fetch()` API to send this JSON to our backend.
- If the backend returns a `422 Unprocessable Entity` (Pydantic validation failed), we will catch that error and display exactly what field was wrong on the UI!
- If successful, we will update the UI to show the new transaction.

#### [NEW] [static/style.css](file:///c:/Users/vamsh/Documents/UP_Coming/2.Phase%201/Day%204%20Transaction%20Schema%20Validation/Expense%20Tracking%20Backend/static/style.css)
- Clean, responsive styling for the form and transaction list.

## Verification Plan

### Manual Verification
1. I will install the new requirements (`pip install fastapi uvicorn`).
2. I will start the server (`uvicorn api:app --reload`).
3. I will instruct you to open your browser to `http://localhost:8000`.
4. You will be able to try submitting both valid and invalid transactions through the web UI and instantly see how Pydantic protects the backend from bad data.
