import requests
import json

BASE_URL = "http://localhost:8000/api/v1"

def test_register():
    print("Testing user registration...")
    data = {
        "email": "test@example.com",
        "username": "testuser",
        "password": "testpass123",
        "full_name": "Test User"
    }
    
    response = requests.post(f"{BASE_URL}/auth/register", json=data)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    return response.status_code == 200

def test_login():
    print("\nTesting user login...")
    data = {
        "email": "test@example.com",
        "password": "testpass123"
    }
    
    response = requests.post(f"{BASE_URL}/auth/login", json=data)
    print(f"Status: {response.status_code}")
    result = response.json()
    print(f"Response: {result}")
    
    if response.status_code == 200:
        return result["access_token"]
    return None

def test_protected_route(token):
    print("\nTesting protected route...")
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.get(f"{BASE_URL}/auth/me", headers=headers)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    return response.status_code == 200

if __name__ == "__main__":
    print("Starting authentication tests...")
    print("Make sure the server is running on http://localhost:8000")
    
    try:
        test_register()
        token = test_login()
        if token:
            test_protected_route(token)
    except requests.exceptions.ConnectionError:
        print("Error: Could not connect to server. Make sure it's running!")
    except Exception as e:
        print(f"Error: {e}")
