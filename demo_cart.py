import requests

BASE_URL = "http://localhost:8000/api/v1"

def demo_cart_system():
    print("🛒 Shopping Cart System Demo")
    print("=" * 40)
    
    # Login as existing user
    login_data = {"email": "test@example.com", "password": "testpass123"}
    response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
    
    if response.status_code != 200:
        print("❌ Login failed")
        return
    
    token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    print("✅ Logged in successfully")
    
    # 1. Get empty cart
    print("\n1️⃣ Getting empty cart...")
    response = requests.get(f"{BASE_URL}/cart/", headers=headers)
    if response.status_code == 200:
        result = response.json()
        print(f"   📋 Items: {len(result['cart']['items'])}")
        print(f"   💰 Subtotal: ${result['summary']['subtotal']}")
    
    # 2. Add item to cart (using product ID 1 - the iPhone we created earlier)
    print("\n2️⃣ Adding iPhone to cart...")
    add_data = {"product_id": 1, "quantity": 2}
    response = requests.post(f"{BASE_URL}/cart/add", json=add_data, headers=headers)
    if response.status_code == 200:
        result = response.json()
        print(f"   ✅ {result['message']}")
        print(f"   📋 Items: {len(result['cart']['items'])}")
        print(f"   📦 Total quantity: {result['summary']['total_items']}")
        print(f"   💰 Subtotal: ${result['summary']['subtotal']}")
    else:
        print(f"   ❌ Error: {response.json()}")
    
    # 3. Quick add another item
    print("\n3️⃣ Quick adding item...")
    response = requests.post(f"{BASE_URL}/cart/quick-add/1", headers=headers)
    if response.status_code == 200:
        result = response.json()
        print(f"   ✅ {result['message']}")
    
    # 4. Get updated cart
    print("\n4️⃣ Getting updated cart...")
    response = requests.get(f"{BASE_URL}/cart/", headers=headers)
    if response.status_code == 200:
        result = response.json()
        cart = result['cart']
        print(f"   📋 Items in cart: {len(cart['items'])}")
        print(f"   📦 Total quantity: {result['summary']['total_items']}")
        print(f"   💰 Subtotal: ${result['summary']['subtotal']}")
        
        for item in cart['items']:
            product = item['product']
            print(f"      • {product['name']}: {item['quantity']} x ${item['unit_price']} = ${item['total_price']}")
    
    # 5. Update quantity
    print("\n5️⃣ Updating quantity to 1...")
    update_data = {"quantity": 1}
    response = requests.put(f"{BASE_URL}/cart/items/1", json=update_data, headers=headers)
    if response.status_code == 200:
        result = response.json()
        print(f"   ✅ {result['message']}")
        print(f"   💰 New subtotal: ${result['summary']['subtotal']}")
    
    # 6. Validate cart
    print("\n6️⃣ Validating cart...")
    response = requests.get(f"{BASE_URL}/cart/validate", headers=headers)
    if response.status_code == 200:
        result = response.json()
        print(f"   {'✅' if result['valid'] else '❌'} {result['message']}")
    
    # 7. Get cart summary
    print("\n7️⃣ Getting cart summary...")
    response = requests.get(f"{BASE_URL}/cart/summary", headers=headers)
    if response.status_code == 200:
        summary = response.json()
        print(f"   💰 Subtotal: ${summary['subtotal']}")
        print(f"   📦 Total items: {summary['total_items']}")
        print(f"   🏷️ Unique products: {summary['items_count']}")
    
    # 8. Remove item
    print("\n8️⃣ Removing item from cart...")
    response = requests.delete(f"{BASE_URL}/cart/items/1", headers=headers)
    if response.status_code == 200:
        result = response.json()
        print(f"   ✅ {result['message']}")
        print(f"   💰 New subtotal: ${result['cart_summary']['subtotal']}")
    
    # 9. Final cart state
    print("\n9️⃣ Final cart state...")
    response = requests.get(f"{BASE_URL}/cart/", headers=headers)
    if response.status_code == 200:
        result = response.json()
        print(f"   📋 Items: {len(result['cart']['items'])}")
        print(f"   💰 Subtotal: ${result['summary']['subtotal']}")
    
    print("\n🎉 Cart demo completed!")
    print("\n💡 To test more features:")
    print("   • Visit http://localhost:8000/docs")
    print("   • Try the /cart endpoints with authentication")
    print("   • Test with different products and quantities")

if __name__ == "__main__":
    demo_cart_system()
