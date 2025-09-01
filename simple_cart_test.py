import requests

BASE_URL = "http://localhost:8000/api/v1"

def test_basic_cart():
    print("Testing basic cart functionality...")
    
    # login as user
    login_data = {"email": "test@example.com", "password": "testpass123"}
    response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
    
    if response.status_code != 200:
        print("Failed to login")
        return
    
    token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # test get empty cart
    print("\n1. Testing empty cart...")
    response = requests.get(f"{BASE_URL}/cart/", headers=headers)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        print("✓ Empty cart works")
    else:
        print(f"✗ Error: {response.text}")
        return
    
    # test cart summary
    print("\n2. Testing cart summary...")
    response = requests.get(f"{BASE_URL}/cart/summary", headers=headers)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        summary = response.json()
        print(f"✓ Cart summary: {summary}")
    else:
        print(f"✗ Error: {response.text}")
    
    # test add to cart with product ID 1 (if it exists)
    print("\n3. Testing add to cart...")
    add_data = {"product_id": 1, "quantity": 1}
    response = requests.post(f"{BASE_URL}/cart/add", json=add_data, headers=headers)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print(f"✓ Added to cart: {result['message']}")
    else:
        print(f"✗ Error: {response.text}")
    
    print("\n✓ Basic cart tests completed!")

if __name__ == "__main__":
    test_basic_cart()
