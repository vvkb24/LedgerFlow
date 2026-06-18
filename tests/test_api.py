import pytest

# This is a Pytest fixture that automatically logs a user in and returns their JWT token.
# It makes testing our protected routes much easier!
@pytest.fixture
def auth_token(client):
    # 1. Register
    client.post("/api/users/register", json={
        "full_name": "API Tester",
        "email": "api@robot.com",
        "password": "apipassword"
    })
    # 2. Login
    response = client.post("/token", data={
        "username": "api@robot.com",
        "password": "apipassword"
    })
    # 3. Extract the token
    return response.json()["access_token"]


def test_get_transactions_without_token_fails(client):
    # Try to access a protected route without logging in
    response = client.get("/api/transactions")
    
    # The Bouncer should reject us!
    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"


def test_create_and_get_transaction(client, auth_token):
    # We must pass the JWT token in the headers exactly how a frontend would
    headers = {
        "Authorization": f"Bearer {auth_token}"
    }
    
    transaction_data = {
        "transaction_id": "TXN_TEST_1",
        "amount": 50.0,
        "transaction_type": "expense",
        "description": "Robot test purchase",
        "timestamp": "2023-10-27T10:00:00Z",
        "category": {
            "category_id": 1,
            "name": "Food",
            "description": "Groceries"
        },
        "account": {
            "account_id": "ACC_TEST_1",
            "account_type": "Current",
            "balance": 100.0,
            "currency": "USD",
            "user": {
                "user_id": "USR_ROBOT",
                "full_name": "API Tester",
                "email": "api_mock@robot.com",
                "is_active": True,
                "created_at": "2023-10-27T10:00:00Z"
            }
        }
    }
    
    # Create the transaction
    response = client.post("/api/transactions", json=transaction_data, headers=headers)
    if response.status_code != 201:
        print("VALIDATION ERROR:", response.json())
    assert response.status_code == 201
    
    # Now, try to GET that same transaction to prove it saved!
    get_response = client.get("/api/transactions/TXN_TEST_1", headers=headers)
    assert get_response.status_code == 200
    
    saved_data = get_response.json()
    assert saved_data["amount"] == 50.0
    assert saved_data["description"] == "Robot test purchase"


def test_delete_transaction(client, auth_token):
    headers = {"Authorization": f"Bearer {auth_token}"}
    
    transaction_data = {
        "transaction_id": "TXN_TEST_DELETE",
        "amount": 10.0,
        "transaction_type": "expense",
        "description": "To be deleted",
        "timestamp": "2023-10-27T10:00:00Z",
        "category": {
            "category_id": 99,
            "name": "Misc",
            "description": "..."
        },
        "account": {
            "account_id": "ACC_TEST_2",
            "account_type": "Current",
            "balance": 100.0,
            "currency": "USD",
            "user": {
                "user_id": "USR_ROBOT",
                "full_name": "API Tester",
                "email": "api_mock@robot.com",
                "is_active": True,
                "created_at": "2023-10-27T10:00:00Z"
            }
        }
    }
    
    # 1. Create it
    client.post("/api/transactions", json=transaction_data, headers=headers)
    
    # 2. Delete it (Expect a 204 No Content success)
    delete_response = client.delete("/api/transactions/TXN_TEST_DELETE", headers=headers)
    assert delete_response.status_code == 204
    
    # 3. Try to GET it again, it should be a 404 Not Found!
    get_response = client.get("/api/transactions/TXN_TEST_DELETE", headers=headers)
    assert get_response.status_code == 404
