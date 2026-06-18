# We don't need to import 'client' directly. Pytest magically finds it in conftest.py!

def test_register_user_success(client):
    # The 'Arrange' step: Define the data we want to send
    new_user_data = {
        "full_name": "Test User",
        "email": "test@robot.com",
        "password": "supersecretpassword"
    }

    # The 'Act' step: Have the client pretend to send a POST request
    response = client.post("/api/users/register", json=new_user_data)

    # The 'Assert' step: Check if the response is exactly what we expect
    assert response.status_code == 201
    
    # We expect the API to return the user data (but NOT the password!)
    data = response.json()
    assert data["email"] == "test@robot.com"
    assert data["full_name"] == "Test User"
    assert "password" not in data
    assert "hashed_password" not in data

def test_register_existing_email_fails(client):
    # Try to register the exact same user twice
    user_data = {
        "full_name": "Test User",
        "email": "duplicate@robot.com",
        "password": "supersecretpassword"
    }
    
    # First time works
    client.post("/api/users/register", json=user_data)
    
    # Second time should fail!
    response = client.post("/api/users/register", json=user_data)
    
    assert response.status_code == 400
    assert response.json()["detail"] == "Email duplicate@robot.com is already registered."

def test_login_success(client):
    # 1. Register a user first
    client.post("/api/users/register", json={
        "full_name": "Login Tester",
        "email": "login@robot.com",
        "password": "validpassword"
    })

    # 2. Try to log in
    # Note: OAuth2 uses form data (data=...), not JSON!
    response = client.post("/token", data={
        "username": "login@robot.com",
        "password": "validpassword"
    })

    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

def test_login_wrong_password_fails(client):
    client.post("/api/users/register", json={
        "full_name": "Hacker",
        "email": "hacker@robot.com",
        "password": "realpassword"
    })

    response = client.post("/token", data={
        "username": "hacker@robot.com",
        "password": "wrongpassword"
    })

    assert response.status_code == 401
    assert response.json()["detail"] == "Incorrect email or password"
