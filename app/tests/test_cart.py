import requests
import json

BASE_URL = "http://localhost:8000/api/v1"

def get_user_token():
    """Login as regular user to test cart operations"""
    # First register a test user
    register_data = {
        "email": "cartuser@example.com",
        "username": "cartuser",
        "password": "cartpass123",
        "full_name": "Cart Test User"
    }
    
    # Try to register (might already exist)
    requests.post(f"{BASE_URL}/auth/register", json=register_data)
    
    # Login
    login_data = {
        "email": "cartuser@example.com",
        "password": "cartpass123"
    }
    
    response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
    if response.status_code == 200:
        return response.json()["access_token"]
    return None

def get_admin_token():
    """Login as admin to create test products"""
    data = {
        "email": "admin@example.com",
        "password": "admin123"
    }
    
    response = requests.post(f"{BASE_URL}/auth/login", json=data)
    if response.status_code == 200:
        return response.json()["access_token"]
    return None

def get_existing_products():
    """Get existing products for cart testing"""
    response = requests.get(f"{BASE_URL}/products/")
    if response.status_code == 200:
        result = response.json()
        products = result['items']
        print(f"✓ Found {len(products)} existing products")
        for product in products:
            print(f"  - {product['name']} (ID: {product['id']}) - ${product['price']}")
        return products
    return []

def create_test_products(admin_token):
    """Create some test products for cart testing or use existing ones"""
    # First try to get existing products
    existing_products = get_existing_products()
    if len(existing_products) >= 3:
        print("✓ Using existing products for cart testing")
        return existing_products[:3]
    
    # If not enough products, create new ones
    headers = {"Authorization": f"Bearer {admin_token}"}
    
    products = [
        {
            "name": "Test Laptop",
            "description": "A test laptop for cart testing",
            "short_description": "Test laptop",
            "slug": "test-laptop-cart",
            "price": 999.99,
            "sku": "LAPTOP002",
            "inventory_quantity": 10,
            "track_inventory": True,
            "is_featured": True
        },
        {
            "name": "Test Mouse",
            "description": "A test mouse for cart testing",
            "short_description": "Test mouse",
            "slug": "test-mouse-cart",
            "price": 29.99,
            "sku": "MOUSE002",
            "inventory_quantity": 50,
            "track_inventory": True,
            "is_featured": False
        },
        {
            "name": "Test Keyboard",
            "description": "A test keyboard for cart testing",
            "short_description": "Test keyboard",
            "slug": "test-keyboard-cart",
            "price": 79.99,
            "sku": "KEYBOARD002",
            "inventory_quantity": 5,
            "track_inventory": True,
            "is_featured": False
        }
    ]
    
    created_products = []
    for product_data in products:
        response = requests.post(f"{BASE_URL}/products/", json=product_data, headers=headers)
        if response.status_code == 200:
            product = response.json()
            created_products.append(product)
            print(f"✓ Created product: {product['name']} (ID: {product['id']})")
        elif response.status_code == 400:
            # Product might already exist, skip
            print(f"⚠ Product {product_data['name']} might already exist")
    
    # Combine existing and new products
    all_products = existing_products + created_products
    return all_products[:3] if len(all_products) >= 3 else all_products

def test_get_empty_cart(token):
    """Test getting empty cart"""
    print("\n=== Testing Empty Cart ===")
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.get(f"{BASE_URL}/cart/", headers=headers)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print(f"Cart items: {len(result['cart']['items'])}")
        print(f"Message: {result['message']}")
        return True
    else:
        print(f"Error: {response.json()}")
        return False

def test_add_to_cart(token, product_id, quantity=1):
    """Test adding items to cart"""
    print(f"\n=== Testing Add to Cart (Product ID: {product_id}, Quantity: {quantity}) ===")
    headers = {"Authorization": f"Bearer {token}"}
    
    add_data = {
        "product_id": product_id,
        "quantity": quantity
    }
    
    response = requests.post(f"{BASE_URL}/cart/add", json=add_data, headers=headers)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        cart = result['cart']
        print(f"Message: {result['message']}")
        print(f"Cart items: {len(cart['items'])}")
        print(f"Total items: {cart['summary']['total_items']}")
        print(f"Subtotal: ${cart['summary']['subtotal']}")
        return True
    else:
        print(f"Error: {response.json()}")
        return False

def test_quick_add(token, product_id):
    """Test quick add to cart"""
    print(f"\n=== Testing Quick Add (Product ID: {product_id}) ===")
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.post(f"{BASE_URL}/cart/quick-add/{product_id}", headers=headers)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print(f"Message: {result['message']}")
        return True
    else:
        print(f"Error: {response.json()}")
        return False

def test_get_cart_with_items(token):
    """Test getting cart with items"""
    print("\n=== Testing Get Cart with Items ===")
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.get(f"{BASE_URL}/cart/", headers=headers)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        cart = result['cart']
        print(f"Cart ID: {cart['id']}")
        print(f"Items in cart: {len(cart['items'])}")
        print(f"Total items: {cart['summary']['total_items']}")
        print(f"Subtotal: ${cart['summary']['subtotal']}")
        
        for item in cart['items']:
            product = item['product']
            print(f"  - {product['name']}: Qty {item['quantity']} x ${item['unit_price']} = ${item['total_price']}")
        
        return cart
    else:
        print(f"Error: {response.json()}")
        return None

def test_update_cart_item(token, product_id, new_quantity):
    """Test updating cart item quantity"""
    print(f"\n=== Testing Update Cart Item (Product ID: {product_id}, New Quantity: {new_quantity}) ===")
    headers = {"Authorization": f"Bearer {token}"}
    
    update_data = {
        "quantity": new_quantity
    }
    
    response = requests.put(f"{BASE_URL}/cart/items/{product_id}", json=update_data, headers=headers)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print(f"Message: {result['message']}")
        return True
    else:
        print(f"Error: {response.json()}")
        return False

def test_cart_summary(token):
    """Test getting cart summary"""
    print("\n=== Testing Cart Summary ===")
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.get(f"{BASE_URL}/cart/summary", headers=headers)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        summary = response.json()
        print(f"Subtotal: ${summary['subtotal']}")
        print(f"Total items: {summary['total_items']}")
        print(f"Unique products: {summary['items_count']}")
        return True
    else:
        print(f"Error: {response.json()}")
        return False

def test_validate_cart(token):
    """Test cart validation"""
    print("\n=== Testing Cart Validation ===")
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.get(f"{BASE_URL}/cart/validate", headers=headers)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print(f"Cart valid: {result['valid']}")
        print(f"Message: {result['message']}")
        if not result['valid']:
            print("Issues found:")
            for issue in result.get('issues', []):
                print(f"  - {issue}")
        return True
    else:
        print(f"Error: {response.json()}")
        return False

def test_remove_from_cart(token, product_id):
    """Test removing item from cart"""
    print(f"\n=== Testing Remove from Cart (Product ID: {product_id}) ===")
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.delete(f"{BASE_URL}/cart/items/{product_id}", headers=headers)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print(f"Message: {result['message']}")
        summary = result['cart_summary']
        print(f"New subtotal: ${summary['subtotal']}")
        return True
    else:
        print(f"Error: {response.json()}")
        return False

def test_clear_cart(token):
    """Test clearing entire cart"""
    print("\n=== Testing Clear Cart ===")
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.delete(f"{BASE_URL}/cart/clear", headers=headers)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print(f"Message: {result['message']}")
        return True
    else:
        print(f"Error: {response.json()}")
        return False

def test_stock_validation(token, product_id):
    """Test adding more items than available stock"""
    print(f"\n=== Testing Stock Validation (Product ID: {product_id}) ===")
    headers = {"Authorization": f"Bearer {token}"}
    
    # Try to add 100 items (should exceed stock)
    add_data = {
        "product_id": product_id,
        "quantity": 100
    }
    
    response = requests.post(f"{BASE_URL}/cart/add", json=add_data, headers=headers)
    print(f"Status: {response.status_code}")
    if response.status_code == 400:
        print(f"Expected error: {response.json()['detail']}")
        return True
    else:
        print("Expected stock validation error, but request succeeded")
        return False

def main():
    print("Starting Shopping Cart System Tests...")
    print("Make sure the server is running on http://localhost:8000")
    
    try:
        # Get tokens
        admin_token = get_admin_token()
        user_token = get_user_token()
        
        if not admin_token or not user_token:
            print("Failed to get authentication tokens!")
            return
        
        print("✓ Successfully authenticated admin and user")
        
        # Get test products
        products = create_test_products(admin_token)
        if len(products) < 1:
            print("Failed to get test products!")
            return
        
        print(f"✓ Using {len(products)} products for testing")
        
        # Test cart operations
        test_get_empty_cart(user_token)
        
        # Add items to cart
        if len(products) >= 3:
            test_add_to_cart(user_token, products[0]['id'], 2)  # Laptop x2
            test_quick_add(user_token, products[1]['id'])       # Mouse x1
            test_add_to_cart(user_token, products[2]['id'], 1)  # Keyboard x1
        
        # Get cart with items
        cart = test_get_cart_with_items(user_token)
        
        # Test cart operations
        test_cart_summary(user_token)
        test_validate_cart(user_token)
        
        # Update quantities
        if len(products) >= 1:
            test_update_cart_item(user_token, products[0]['id'], 3)  # Update laptop to 3
        
        # Test stock validation
        if len(products) >= 3:
            test_stock_validation(user_token, products[2]['id'])  # Keyboard has limited stock
        
        # Remove item
        if len(products) >= 2:
            test_remove_from_cart(user_token, products[1]['id'])  # Remove mouse
        
        # Final cart state
        test_get_cart_with_items(user_token)
        
        # Clear cart
        test_clear_cart(user_token)
        test_get_empty_cart(user_token)
        
        print("\n✓ All cart tests completed!")
        
    except requests.exceptions.ConnectionError:
        print("Error: Could not connect to server. Make sure it's running!")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
