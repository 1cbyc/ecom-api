#!/usr/bin/env python3
"""
Secure Payment Integration Test Script
=====================================

SECURITY NOTE: This script uses environment variables for credentials.
Set these before running:

export TEST_USER_EMAIL="test@example.com"
export TEST_USER_PASSWORD="your_test_password"
export ADMIN_EMAIL="admin@yourdomain.com"
export ADMIN_PASSWORD="your_admin_password"

Usage:
    python test_secure_payments.py
"""

import requests
import json
import os
import sys

BASE_URL = "http://localhost:8000/api/v1"

def get_credentials():
    """Get credentials from environment variables"""
    test_email = os.getenv("TEST_USER_EMAIL")
    test_password = os.getenv("TEST_USER_PASSWORD")
    admin_email = os.getenv("ADMIN_EMAIL")
    admin_password = os.getenv("ADMIN_PASSWORD")
    
    if not all([test_email, test_password, admin_email, admin_password]):
        print("❌ ERROR: Missing required environment variables!")
        print("Set: TEST_USER_EMAIL, TEST_USER_PASSWORD, ADMIN_EMAIL, ADMIN_PASSWORD")
        sys.exit(1)
    
    return {
        "test_user": {"email": test_email, "password": test_password},
        "admin_user": {"email": admin_email, "password": admin_password}
    }

def get_user_token(credentials):
    """Login as user to test payment flow"""
    response = requests.post(f"{BASE_URL}/auth/login", json=credentials["test_user"])
    
    if response.status_code == 200:
        return response.json()["access_token"]
    return None

def test_checkout_flow():
    print("💳 Secure Payment Integration Demo")
    print("=" * 40)
    
    credentials = get_credentials()
    
    # Get user token
    token = get_user_token(credentials)
    if not token:
        print("❌ Login failed - check TEST_USER credentials")
        return
    
    headers = {"Authorization": f"Bearer {token}"}
    print("✅ Logged in successfully")
    
    # Step 1: Add item to cart
    print("\n1️⃣ Adding item to cart...")
    add_data = {"product_id": 1, "quantity": 2}
    response = requests.post(f"{BASE_URL}/cart/add", json=add_data, headers=headers)
    if response.status_code == 200:
        result = response.json()
        print(f"   ✅ Added to cart: ${result['summary']['subtotal']}")
    else:
        print(f"   ❌ Error: {response.json()}")
        return
    
    # Step 2: Create checkout request
    print("\n2️⃣ Creating secure checkout request...")
    checkout_data = {
        "shipping_address": {
            "address_line1": "123 Main St",
            "address_line2": "Apt 4B",
            "city": "New York",
            "state": "NY",
            "postal_code": "10001",
            "country": "US"
        },
        "customer_phone": "+1-555-123-4567",
        "customer_notes": "Please handle with care"
    }
    
    print("   📝 Creating payment intent (using environment config)...")
    response = requests.post(f"{BASE_URL}/checkout/create-payment-intent", 
                           json=checkout_data, headers=headers)
    
    if response.status_code == 200:
        payment_result = response.json()
        print(f"   ✅ Payment intent created!")
        print(f"   💰 Amount: ${payment_result['amount']}")
        print(f"   🔑 Payment Intent ID: {payment_result['payment_intent_id'][:20]}...")
        print(f"   📄 Order ID: {payment_result['order_id']}")
        
        # Store for later steps
        payment_intent_id = payment_result['payment_intent_id']
        order_id = payment_result['order_id']
        
    else:
        print(f"   ❌ Error creating payment intent: {response.json()}")
        return
    
    # Step 3: Check payment status
    print("\n3️⃣ Checking payment status...")
    response = requests.get(f"{BASE_URL}/checkout/payment-status/{payment_intent_id}", 
                          headers=headers)
    if response.status_code == 200:
        status_result = response.json()
        print(f"   📊 Payment status: {status_result['status']}")
        print(f"   💵 Amount: ${status_result['amount'] / 100}")
    
    # Step 4: Get order details
    print("\n4️⃣ Getting order details...")
    response = requests.get(f"{BASE_URL}/orders/order/{order_id}", headers=headers)
    if response.status_code == 200:
        order = response.json()
        print(f"   📋 Order Number: {order['order_number']}")
        print(f"   📈 Status: {order['status']}")
        print(f"   💰 Total: ${order['total_amount']}")
        print(f"   📦 Items: {len(order['items'])}")
        print(f"   🏠 Shipping: {order['shipping_address_line1']}, {order['shipping_city']}")
    
    print("\n🎉 Secure payment integration test completed!")
    print("\n💡 Production security notes:")
    print("   • All credentials from environment variables")
    print("   • No hardcoded secrets in test code")
    print("   • Payment intent IDs partially masked")
    print("   • Real Stripe integration ready")

def test_admin_features():
    """Test admin order management features"""
    print("\n👨‍💼 Admin Features Demo")
    print("=" * 30)
    
    credentials = get_credentials()
    
    # Login as admin
    response = requests.post(f"{BASE_URL}/auth/login", json=credentials["admin_user"])
    
    if response.status_code != 200:
        print("❌ Admin login failed - check ADMIN credentials")
        return
    
    admin_token = response.json()["access_token"]
    admin_headers = {"Authorization": f"Bearer {admin_token}"}
    print("✅ Admin logged in successfully")
    
    # Get all orders
    print("\n📊 Getting all orders (admin view)...")
    response = requests.get(f"{BASE_URL}/orders/admin/all", headers=admin_headers)
    if response.status_code == 200:
        orders = response.json()
        print(f"   📚 Total orders in system: {orders['total']}")
        
        for order in orders['items'][:3]:  # Show first 3
            print(f"      • {order['order_number']}: ${order['total_amount']} ({order['status']})")
    
    # Get orders summary
    print("\n📈 Getting orders summary...")
    response = requests.get(f"{BASE_URL}/orders/admin/summary?days=30", headers=admin_headers)
    if response.status_code == 200:
        summary = response.json()
        print(f"   💰 Total revenue (30 days): ${summary['total_revenue']}")
        print(f"   📦 Total orders (30 days): {summary['total_orders']}")

if __name__ == "__main__":
    print("🔐 Starting Secure Payment Integration Tests...")
    print("Make sure the server is running on http://localhost:8000")
    print("Environment variables required for security!")
    print()
    
    try:
        test_checkout_flow()
        test_admin_features()
        
        print("\n✨ All secure tests completed!")
        print("\n🔗 Useful links:")
        print("   • API Documentation: http://localhost:8000/docs")
        print("   • Security Guide: ./SECURITY.md")
        
    except requests.exceptions.ConnectionError:
        print("❌ Error: Could not connect to server. Make sure it's running!")
    except Exception as e:
        print(f"❌ Error: {e}")
