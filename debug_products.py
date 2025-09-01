#!/usr/bin/env python3
"""
Quick debug script for product endpoints
"""

import requests
import json

BASE_URL = "https://ecom-api-s8lz.onrender.com/api/v1"

# First get admin token
print("🔑 Getting admin token...")
login_response = requests.post(f"{BASE_URL}/auth/login", json={
    "email": "admin@nsisong.com",
    "password": "admin123_dev_secure"
})

if login_response.status_code != 200:
    print(f"❌ Login failed: {login_response.status_code}")
    print(login_response.text)
    exit(1)

admin_token = login_response.json()["access_token"]
print("✅ Admin token obtained")

headers = {"Authorization": f"Bearer {admin_token}", "Content-Type": "application/json"}

# Try to list products first (this should show us the error)
print("\n📦 Testing GET /products...")
try:
    list_response = requests.get(f"{BASE_URL}/products/", timeout=10)
    print(f"Status: {list_response.status_code}")
    if list_response.status_code == 200:
        products = list_response.json()
        print(f"✅ Found {len(products.get('items', []))} products")
        print(json.dumps(products, indent=2)[:500] + "...")
    else:
        print(f"❌ Error: {list_response.text}")
except Exception as e:
    print(f"❌ Request failed: {e}")

# Try to create a simple product
print("\n🛠️ Testing POST /products...")
try:
    product_data = {
        "name": "Debug Test Product",
        "description": "A simple test product for debugging",
        "price": "29.99",
        "sku": "DEBUG-001", 
        "slug": "debug-test-product",
        "category_ids": []  # No categories for now
    }
    
    create_response = requests.post(f"{BASE_URL}/products/", json=product_data, headers=headers, timeout=10)
    print(f"Status: {create_response.status_code}")
    if create_response.status_code == 200:
        product = create_response.json()
        print(f"✅ Product created: {product['name']} (ID: {product['id']})")
    else:
        print(f"❌ Error: {create_response.text}")
except Exception as e:
    print(f"❌ Request failed: {e}")

print("\n🔍 Debug complete!")
