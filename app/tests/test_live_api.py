#!/usr/bin/env python3
"""
Live API Testing Script for E-commerce API
Tests all endpoints on the live Render deployment
"""

import requests
import json
import sys
from typing import Optional

BASE_URL = "http://localhost:8000/api/v1"

class APITester:
    def __init__(self):
        self.session = requests.Session()
        self.user_token: Optional[str] = None
        self.admin_token: Optional[str] = None
        self.test_results = []

    def log_test(self, test_name: str, success: bool, details: str = ""):
        """Log test results"""
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}")
        if details:
            print(f"    {details}")
        self.test_results.append({
            "test": test_name,
            "success": success,
            "details": details
        })

    def test_health_check(self):
        """Test basic health check"""
        try:
            response = self.session.get(f"{BASE_URL.replace('/api/v1', '')}/")
            success = response.status_code == 200
            details = f"Status: {response.status_code}, Response: {response.json()}"
        except Exception as e:
            success = False
            details = f"Error: {str(e)}"
        
        self.log_test("Health Check", success, details)
        return success

    def test_user_registration(self):
        """Test user registration"""
        try:
            data = {
                "email": "test@example.com",
                "username": "testuser",
                "password": "testpass123",
                "full_name": "Test User"
            }
            response = self.session.post(f"{BASE_URL}/auth/register", json=data)
            success = response.status_code == 200
            details = f"Status: {response.status_code}"
            if not success:
                details += f", Error: {response.text}"
        except Exception as e:
            success = False
            details = f"Error: {str(e)}"
        
        self.log_test("User Registration", success, details)
        return success

    def test_user_login(self):
        """Test user login and store token"""
        try:
            data = {
                "email": "testuser@example.com",
                "password": "testpass123"
            }
            response = self.session.post(f"{BASE_URL}/auth/login", json=data)
            success = response.status_code == 200
            
            if success:
                token_data = response.json()
                self.user_token = token_data.get("access_token")
                details = f"Status: {response.status_code}, Token obtained"
            else:
                details = f"Status: {response.status_code}, Error: {response.text}"
        except Exception as e:
            success = False
            details = f"Error: {str(e)}"
        
        self.log_test("User Login", success, details)
        return success

    def test_admin_login(self):
        """Test admin login and store token"""
        try:
            data = {
                "email": "admin@example.com",
                "password": "admin123"
            }
            response = self.session.post(f"{BASE_URL}/auth/login", json=data)
            success = response.status_code == 200
            
            if success:
                token_data = response.json()
                self.admin_token = token_data.get("access_token")
                details = f"Status: {response.status_code}, Admin token obtained"
            else:
                details = f"Status: {response.status_code}, Error: {response.text}"
        except Exception as e:
            success = False
            details = f"Error: {str(e)}"
        
        self.log_test("Admin Login", success, details)
        return success

    def test_categories_list(self):
        """Test getting categories list"""
        try:
            response = self.session.get(f"{BASE_URL}/categories")
            success = response.status_code == 200
            details = f"Status: {response.status_code}"
            if success:
                categories = response.json()
                details += f", Found {len(categories)} categories"
        except Exception as e:
            success = False
            details = f"Error: {str(e)}"
        
        self.log_test("Get Categories", success, details)
        return success

    def test_category_creation(self):
        """Test creating a category"""
        if not self.admin_token:
            self.log_test("Create Category", False, "Admin token required")
            return False

        try:
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            data = {
                "name": "Test Category",
                "description": "A test category for API testing",
                "slug": "test-category"
            }
            response = self.session.post(f"{BASE_URL}/categories/", json=data, headers=headers)
            success = response.status_code == 200
            details = f"Status: {response.status_code}"
            if not success:
                details += f", Error: {response.text}"
        except Exception as e:
            success = False
            details = f"Error: {str(e)}"
        
        self.log_test("Create Category", success, details)
        return success

    def test_cart_get(self):
        """Test getting user's cart"""
        if not self.user_token:
            self.log_test("Get Cart", False, "User token required")
            return False

        try:
            headers = {"Authorization": f"Bearer {self.user_token}"}
            response = self.session.get(f"{BASE_URL}/cart", headers=headers)
            success = response.status_code == 200
            details = f"Status: {response.status_code}"
            if success:
                cart_data = response.json()
                details += f", Items: {cart_data['summary']['total_items']}"
        except Exception as e:
            success = False
            details = f"Error: {str(e)}"
        
        self.log_test("Get Cart", success, details)
        return success

    def test_products_list(self):
        """Test getting products list"""
        try:
            response = self.session.get(f"{BASE_URL}/products")
            success = response.status_code == 200
            details = f"Status: {response.status_code}"
            if success:
                products_data = response.json()
                if isinstance(products_data, dict) and 'products' in products_data:
                    details += f", Found {len(products_data['products'])} products"
                elif isinstance(products_data, list):
                    details += f", Found {len(products_data)} products"
            else:
                details += f", Error: {response.text}"
        except Exception as e:
            success = False
            details = f"Error: {str(e)}"
        
        self.log_test("Get Products", success, details)
        return success

    def run_all_tests(self):
        """Run all API tests"""
        print("🧪 Starting Live API Tests")
        print("=" * 50)
        
        # Core tests
        self.test_health_check()
        self.test_user_registration()
        self.test_user_login()
        self.test_admin_login()
        
        # Feature tests
        self.test_categories_list()
        self.test_category_creation()
        self.test_cart_get()
        self.test_products_list()
        
        # Results summary
        print("\n" + "=" * 50)
        print("📊 Test Results Summary")
        print("=" * 50)
        
        passed = sum(1 for result in self.test_results if result["success"])
        total = len(self.test_results)
        
        print(f"✅ Passed: {passed}/{total}")
        print(f"❌ Failed: {total - passed}/{total}")
        
        if total - passed > 0:
            print("\n🔍 Failed Tests:")
            for result in self.test_results:
                if not result["success"]:
                    print(f"  - {result['test']}: {result['details']}")
        
        return passed == total

if __name__ == "__main__":
    tester = APITester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)
