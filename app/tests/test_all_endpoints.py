#!/usr/bin/env python3
"""
Comprehensive test of ALL E-commerce API endpoints
"""

import requests
import json
import time
from datetime import datetime

BASE_URL = "http://localhost:8000/api/v1"

class ComprehensiveAPITester:
    def __init__(self):
        self.session = requests.Session()
        self.user_token = None
        self.admin_token = None
        self.test_results = []
        self.created_product_id = None

    def log_test(self, test_name: str, success: bool, details: str = ""):
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}")
        if details:
            print(f"    {details}")
        self.test_results.append({"test": test_name, "success": success, "details": details})

    def setup_tokens(self):
        """Get authentication tokens"""
        print("🔑 Setting up authentication...")
        
        # Get user token
        try:
            user_login = self.session.post(f"{BASE_URL}/auth/login", json={
                "email": "testuser@example.com",
                "password": "testpass123"
            }, timeout=10)
            if user_login.status_code == 200:
                self.user_token = user_login.json()["access_token"]
                print("✅ User token obtained")
            else:
                print("❌ User login failed")
        except Exception as e:
            print(f"❌ User login error: {e}")

        # Get admin token
        try:
            admin_login = self.session.post(f"{BASE_URL}/auth/login", json={
                "email": "admin@example.com",
                "password": "admin123"
            }, timeout=10)
            if admin_login.status_code == 200:
                self.admin_token = admin_login.json()["access_token"]
                print("✅ Admin token obtained")
            else:
                print("❌ Admin login failed")
        except Exception as e:
            print(f"❌ Admin login error: {e}")

    def test_health_endpoints(self):
        """Test basic health endpoints"""
        print("\n🏥 Testing Health Endpoints...")
        
        # Root endpoint
        try:
            response = self.session.get(f"{BASE_URL.replace('/api/v1', '')}/", timeout=10)
            success = response.status_code == 200
            details = f"Status: {response.status_code}"
            if success:
                data = response.json()
                details += f", Message: {data.get('message')}"
        except Exception as e:
            success = False
            details = f"Error: {str(e)}"
        self.log_test("Root Health Check", success, details)

        # API docs
        try:
            response = self.session.get(f"{BASE_URL.replace('/api/v1', '')}/docs", timeout=10)
            success = response.status_code == 200
            details = f"Status: {response.status_code}"
        except Exception as e:
            success = False
            details = f"Error: {str(e)}"
        self.log_test("API Documentation", success, details)

    def test_auth_endpoints(self):
        """Test authentication endpoints"""
        print("\n🔐 Testing Authentication Endpoints...")
        
        # User registration (will fail if exists, that's ok)
        try:
            response = self.session.post(f"{BASE_URL}/auth/register", json={
                "email": f"newuser_{int(time.time())}@example.com",
                "username": f"newuser_{int(time.time())}",
                "password": "newpass123",
                "full_name": "New Test User"
            }, timeout=10)
            success = response.status_code == 200
            details = f"Status: {response.status_code}"
            if not success:
                details += f", Response: {response.text[:100]}"
        except Exception as e:
            success = False
            details = f"Error: {str(e)}"
        self.log_test("User Registration", success, details)

        # User login
        try:
            response = self.session.post(f"{BASE_URL}/auth/login", json={
                "email": "testuser@example.com",
                "password": "testpass123"
            }, timeout=10)
            success = response.status_code == 200
            details = f"Status: {response.status_code}"
        except Exception as e:
            success = False
            details = f"Error: {str(e)}"
        self.log_test("User Login", success, details)

        # Admin login
        try:
            response = self.session.post(f"{BASE_URL}/auth/login", json={
                "email": "admin@example.com",
                "password": "admin123"
            }, timeout=10)
            success = response.status_code == 200
            details = f"Status: {response.status_code}"
        except Exception as e:
            success = False
            details = f"Error: {str(e)}"
        self.log_test("Admin Login", success, details)

    def test_category_endpoints(self):
        """Test category endpoints"""
        print("\n📂 Testing Category Endpoints...")
        
        # Get categories
        try:
            response = self.session.get(f"{BASE_URL}/categories/", timeout=10)
            success = response.status_code == 200
            details = f"Status: {response.status_code}"
            if success:
                categories = response.json()
                details += f", Found: {len(categories)} categories"
        except Exception as e:
            success = False
            details = f"Error: {str(e)}"
        self.log_test("Get Categories", success, details)

        # Create category (admin required)
        if self.admin_token:
            try:
                headers = {"Authorization": f"Bearer {self.admin_token}"}
                timestamp = int(time.time())
                response = self.session.post(f"{BASE_URL}/categories/", json={
                    "name": f"Test Category {timestamp}",
                    "description": "A test category",
                    "slug": f"test-category-{timestamp}"
                }, headers=headers, timeout=10)
                success = response.status_code == 200
                details = f"Status: {response.status_code}"
                if not success:
                    details += f", Error: {response.text[:100]}"
            except Exception as e:
                success = False
                details = f"Error: {str(e)}"
            self.log_test("Create Category", success, details)

    def test_product_endpoints(self):
        """Test product endpoints"""
        print("\n📦 Testing Product Endpoints...")
        
        # Get products
        try:
            response = self.session.get(f"{BASE_URL}/products/", timeout=10)
            success = response.status_code == 200
            details = f"Status: {response.status_code}"
            if success:
                products = response.json()
                details += f", Found: {len(products.get('items', []))} products"
        except Exception as e:
            success = False
            details = f"Error: {str(e)}"
        self.log_test("Get Products", success, details)

        # Create product (admin required)
        if self.admin_token:
            try:
                headers = {"Authorization": f"Bearer {self.admin_token}"}
                timestamp = int(time.time())
                response = self.session.post(f"{BASE_URL}/products/", json={
                    "name": f"Test Product {timestamp}",
                    "description": "A comprehensive test product",
                    "price": "99.99",
                    "sku": f"TEST-{timestamp}",
                    "slug": f"test-product-{timestamp}",
                    "inventory_quantity": 10,
                    "category_ids": []
                }, headers=headers, timeout=10)
                success = response.status_code == 200
                details = f"Status: {response.status_code}"
                if success:
                    product = response.json()
                    self.created_product_id = product['id']
                    details += f", Created: {product['name']} (ID: {product['id']})"
                    # Check boolean properties
                    details += f", is_on_sale: {product.get('is_on_sale')}, is_in_stock: {product.get('is_in_stock')}"
                else:
                    details += f", Error: {response.text[:100]}"
            except Exception as e:
                success = False
                details = f"Error: {str(e)}"
            self.log_test("Create Product", success, details)

        # Get product by ID
        if self.created_product_id:
            try:
                response = self.session.get(f"{BASE_URL}/products/{self.created_product_id}", timeout=10)
                success = response.status_code == 200
                details = f"Status: {response.status_code}"
                if success:
                    product = response.json()
                    details += f", Product: {product['name']}"
            except Exception as e:
                success = False
                details = f"Error: {str(e)}"
            self.log_test("Get Product by ID", success, details)

    def test_cart_endpoints(self):
        """Test shopping cart endpoints"""
        print("\n🛒 Testing Cart Endpoints...")
        
        if not self.user_token:
            self.log_test("Get Cart", False, "No user token available")
            return

        headers = {"Authorization": f"Bearer {self.user_token}"}
        
        # Get cart
        try:
            response = self.session.get(f"{BASE_URL}/cart/", headers=headers, timeout=10)
            success = response.status_code == 200
            details = f"Status: {response.status_code}"
            if success:
                cart = response.json()
                details += f", Items: {cart['summary']['total_items']}"
        except Exception as e:
            success = False
            details = f"Error: {str(e)}"
        self.log_test("Get Cart", success, details)

        # Add to cart (if we have a product)
        if self.created_product_id:
            try:
                response = self.session.post(f"{BASE_URL}/cart/add", json={
                    "product_id": self.created_product_id,
                    "quantity": 2
                }, headers=headers, timeout=10)
                success = response.status_code == 200
                details = f"Status: {response.status_code}"
                if success:
                    details += ", Added to cart successfully"
                else:
                    details += f", Error: {response.text[:100]}"
            except Exception as e:
                success = False
                details = f"Error: {str(e)}"
            self.log_test("Add to Cart", success, details)

    def test_order_endpoints(self):
        """Test order endpoints"""
        print("\n📋 Testing Order Endpoints...")
        
        if not self.user_token:
            self.log_test("Get Orders", False, "No user token available")
            return

        headers = {"Authorization": f"Bearer {self.user_token}"}
        
        # Get user orders
        try:
            response = self.session.get(f"{BASE_URL}/orders/my-orders", headers=headers, timeout=10)
            success = response.status_code == 200
            details = f"Status: {response.status_code}"
            if success:
                orders = response.json()
                details += f", Found: {len(orders.get('items', []))} orders"
        except Exception as e:
            success = False
            details = f"Error: {str(e)}"
        self.log_test("Get Orders", success, details)

    def run_comprehensive_test(self):
        """Run all endpoint tests"""
        print("🧪 Starting Comprehensive API Endpoint Testing")
        print("=" * 60)
        
        # Setup
        self.setup_tokens()
        
        # Run all tests
        self.test_health_endpoints()
        self.test_auth_endpoints()
        self.test_category_endpoints()
        self.test_product_endpoints()
        self.test_cart_endpoints()
        self.test_order_endpoints()
        
        # Results summary
        print("\n" + "=" * 60)
        print("📊 Comprehensive Test Results Summary")
        print("=" * 60)
        
        passed = sum(1 for result in self.test_results if result["success"])
        total = len(self.test_results)
        
        print(f"✅ Passed: {passed}/{total}")
        print(f"❌ Failed: {total - passed}/{total}")
        print(f"📈 Success Rate: {(passed/total)*100:.1f}%")
        
        if total - passed > 0:
            print("\n🔍 Failed Tests:")
            for result in self.test_results:
                if not result["success"]:
                    print(f"  - {result['test']}: {result['details']}")
        
        print(f"\n🎯 Test completed at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        return passed == total

if __name__ == "__main__":
    tester = ComprehensiveAPITester()
    success = tester.run_comprehensive_test()
    exit(0 if success else 1)
