# 1. Use an official, lightweight Python image as the base operating system
FROM python:3.10-slim

# 2. Set the working directory inside the container to /app
WORKDIR /app

# 3. Copy the requirements file first (this is a Docker optimization trick!)
COPY requirements.txt .

# 4. Install all Python dependencies inside the container
RUN pip install --no-cache-dir -r requirements.txt

# 5. Copy the rest of our application code into the container
COPY . .

# 6. Expose the port that FastAPI will run on
EXPOSE 8000

# 7. Define the command that runs when the container starts
CMD ["uvicorn", "app.api:app", "--host", "0.0.0.0", "--port", "8000"]
