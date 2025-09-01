import requests
import json

BASE_URL = "http://localhost:8000/api/v1"

def get_admin_token():
    """Login as admin to get token for protected operations"""
    data = {
        "email": "admin@example.com",
        "password": "admin123"
    }
    
    response = requests.post(f"{BASE_URL}/auth/login", json=data)
    if response.status_code == 200:
        return response.json()["access_token"]
    return None

def test_create_category(token):
    """Test creating a new category (admin only)"""
    print("\n=== Testing Category Creation ===")
    headers = {"Authorization": f"Bearer {token}"}
    
    category_data = {
        "name": "Electronics",
        "description": "Electronic devices and gadgets",
        "slug": "electronics"
    }
    
    response = requests.post(f"{BASE_URL}/categories/", json=category_data, headers=headers)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        category = response.json()
        print(f"Created category: {category['name']} (ID: {category['id']})")
        return category['id']
    else:
        print(f"Error: {response.json()}")
        return None

def test_create_product(token, category_id):
    """Test creating a new product (admin only)"""
    print("\n=== Testing Product Creation ===")
    headers = {"Authorization": f"Bearer {token}"}
    
    product_data = {
        "name": "iPhone 15 Pro",
        "description": "Latest iPhone with advanced features",
        "short_description": "Apple's flagship smartphone",
        "slug": "iphone-15-pro",
        "price": 999.99,
        "compare_at_price": 1099.99,
        "sku": "IPH15PRO001",
        "inventory_quantity": 50,
        "track_inventory": True,
        "is_featured": True,
        "image_url": "https://example.com/iphone15pro.jpg",
        "category_ids": [category_id] if category_id else []
    }
    
    response = requests.post(f"{BASE_URL}/products/", json=product_data, headers=headers)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        product = response.json()
        print(f"Created product: {product['name']} (ID: {product['id']})")
        return product['id']
    else:
        print(f"Error: {response.json()}")
        return None

def test_list_categories():
    """Test listing categories (public endpoint)"""
    print("\n=== Testing Category Listing ===")
    
    response = requests.get(f"{BASE_URL}/categories/")
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        categories = response.json()
        print(f"Found {len(categories)} categories:")
        for cat in categories:
            print(f"  - {cat['name']} ({cat['slug']})")
    else:
        print(f"Error: {response.json()}")

def test_list_products():
    """Test listing products with pagination and filters"""
    print("\n=== Testing Product Listing ===")
    
    # Test basic listing
    response = requests.get(f"{BASE_URL}/products/")
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print(f"Found {result['total']} products (page {result['page']} of {result['pages']})")
        for product in result['items']:
            print(f"  - {product['name']}: ${product['price']} (Stock: {product['inventory_quantity']})")
    
    # Test search
    print("\n--- Testing Product Search ---")
    response = requests.get(f"{BASE_URL}/products/?search=iPhone")
    if response.status_code == 200:
        result = response.json()
        print(f"Search results for 'iPhone': {result['total']} products")
    
    # Test featured products
    print("\n--- Testing Featured Products ---")
    response = requests.get(f"{BASE_URL}/products/featured")
    if response.status_code == 200:
        products = response.json()
        print(f"Featured products: {len(products)}")
        for product in products:
            print(f"  - {product['name']}")

def test_get_product(product_id):
    """Test getting a single product"""
    print(f"\n=== Testing Get Product (ID: {product_id}) ===")
    
    response = requests.get(f"{BASE_URL}/products/{product_id}")
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        product = response.json()
        print(f"Product: {product['name']}")
        print(f"Price: ${product['price']}")
        print(f"In stock: {product['is_in_stock']}")
        print(f"On sale: {product['is_on_sale']}")
        print(f"Categories: {[cat['name'] for cat in product['categories']]}")
    else:
        print(f"Error: {response.json()}")

def test_update_product(token, product_id):
    """Test updating a product (admin only)"""
    print(f"\n=== Testing Product Update (ID: {product_id}) ===")
    headers = {"Authorization": f"Bearer {token}"}
    
    update_data = {
        "price": 899.99,
        "inventory_quantity": 75,
        "is_featured": False
    }
    
    response = requests.put(f"{BASE_URL}/products/{product_id}", json=update_data, headers=headers)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        product = response.json()
        print(f"Updated product: {product['name']}")
        print(f"New price: ${product['price']}")
        print(f"New inventory: {product['inventory_quantity']}")
    else:
        print(f"Error: {response.json()}")

def test_product_filters():
    """Test product filtering and sorting"""
    print("\n=== Testing Product Filters ===")
    
    # Test price range filter
    response = requests.get(f"{BASE_URL}/products/?min_price=500&max_price=1000")
    if response.status_code == 200:
        result = response.json()
        print(f"Products between $500-$1000: {result['total']}")
    
    # Test sorting
    response = requests.get(f"{BASE_URL}/products/?sort_by=price&sort_order=asc")
    if response.status_code == 200:
        result = response.json()
        print(f"Products sorted by price (ascending): {len(result['items'])}")
        if result['items']:
            print(f"  Cheapest: {result['items'][0]['name']} - ${result['items'][0]['price']}")

def main():
    print("Starting Product Management System Tests...")
    print("Make sure the server is running on http://localhost:8000")
    
    try:
        # Get admin token
        token = get_admin_token()
        if not token:
            print("Failed to get admin token!")
            return
        
        print("✓ Successfully logged in as admin")
        
        # Test category creation
        category_id = test_create_category(token)
        
        # Test product creation
        product_id = test_create_product(token, category_id)
        
        # Test public endpoints
        test_list_categories()
        test_list_products()
        
        if product_id:
            test_get_product(product_id)
            test_update_product(token, product_id)
        
        # Test filters
        test_product_filters()
        
        print("\n✓ All tests completed!")
        
    except requests.exceptions.ConnectionError:
        print("Error: Could not connect to server. Make sure it's running!")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
