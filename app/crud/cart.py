from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_
from typing import Optional, List
from app.models.cart import Cart, CartItem
from app.models.product import Product
from app.models.user import User
from app.schemas.cart import AddToCartRequest, UpdateCartItemRequest


def get_or_create_cart(db: Session, user_id: int) -> Cart:
    """Get user's cart or create one if it doesn't exist"""
    cart = db.query(Cart).filter(Cart.user_id == user_id).first()
    
    if not cart:
        cart = Cart(user_id=user_id)
        db.add(cart)
        db.commit()
        db.refresh(cart)
    
    return cart


def get_cart_with_items(db: Session, user_id: int) -> Optional[Cart]:
    """Get cart with all items and product details"""
    return db.query(Cart).options(
        joinedload(Cart.items).joinedload(CartItem.product).joinedload(Product.categories)
    ).filter(Cart.user_id == user_id).first()


def get_cart_item(db: Session, cart_id: int, product_id: int) -> Optional[CartItem]:
    """Get specific cart item"""
    return db.query(CartItem).filter(
        and_(CartItem.cart_id == cart_id, CartItem.product_id == product_id)
    ).first()


def add_item_to_cart(db: Session, user_id: int, add_request: AddToCartRequest) -> Cart:
    """Add item to cart or update quantity if already exists"""
    
    # Get or create cart
    cart = get_or_create_cart(db, user_id)
    
    # Get product to verify it exists and is active
    product = db.query(Product).filter(
        and_(Product.id == add_request.product_id, Product.is_active == True)
    ).first()
    
    if not product:
        raise ValueError("Product not found or inactive")
    
    # Check stock availability
    if product.track_inventory:
        if product.inventory_quantity < add_request.quantity and not product.allow_backorders:
            raise ValueError(f"Insufficient stock. Available: {product.inventory_quantity}")
    
    # Check if item already exists in cart
    existing_item = get_cart_item(db, cart.id, add_request.product_id)
    
    if existing_item:
        # Update existing item quantity
        new_quantity = existing_item.quantity + add_request.quantity
        
        # Validate total quantity against stock
        if product.track_inventory:
            if new_quantity > product.inventory_quantity and not product.allow_backorders:
                raise ValueError(f"Cannot add {add_request.quantity} items. Would exceed available stock.")
        
        existing_item.quantity = new_quantity
        db.commit()
        db.refresh(existing_item)
    else:
        # Create new cart item
        cart_item = CartItem(
            cart_id=cart.id,
            product_id=add_request.product_id,
            quantity=add_request.quantity,
            unit_price=product.price
        )
        db.add(cart_item)
        db.commit()
        db.refresh(cart_item)
    
    # Return updated cart with items
    return get_cart_with_items(db, user_id)


def update_cart_item(db: Session, user_id: int, product_id: int, update_request: UpdateCartItemRequest) -> Cart:
    """Update cart item quantity"""
    
    cart = get_cart_with_items(db, user_id)
    if not cart:
        raise ValueError("Cart not found")
    
    cart_item = get_cart_item(db, cart.id, product_id)
    if not cart_item:
        raise ValueError("Item not found in cart")
    
    # Get product for stock validation
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise ValueError("Product not found")
    
    # Validate stock
    if product.track_inventory:
        if update_request.quantity > product.inventory_quantity and not product.allow_backorders:
            raise ValueError(f"Insufficient stock. Available: {product.inventory_quantity}")
    
    # Update quantity
    cart_item.quantity = update_request.quantity
    db.commit()
    db.refresh(cart_item)
    
    return get_cart_with_items(db, user_id)


def remove_item_from_cart(db: Session, user_id: int, product_id: int) -> Cart:
    """Remove item from cart"""
    
    cart = get_cart_with_items(db, user_id)
    if not cart:
        raise ValueError("Cart not found")
    
    cart_item = get_cart_item(db, cart.id, product_id)
    if not cart_item:
        raise ValueError("Item not found in cart")
    
    db.delete(cart_item)
    db.commit()
    
    return get_cart_with_items(db, user_id)


def clear_cart(db: Session, user_id: int) -> bool:
    """Remove all items from cart"""
    
    cart = get_or_create_cart(db, user_id)
    
    # Delete all cart items
    db.query(CartItem).filter(CartItem.cart_id == cart.id).delete()
    db.commit()
    
    return True


def validate_cart_stock(db: Session, user_id: int) -> List[dict]:
    """Validate that all cart items are still in stock"""
    
    cart = get_cart_with_items(db, user_id)
    if not cart:
        return []
    
    issues = []
    
    for item in cart.items:
        product = item.product
        
        # Check if product is still active
        if not product.is_active:
            issues.append({
                "product_id": product.id,
                "product_name": product.name,
                "issue": "Product no longer available",
                "requested_quantity": item.quantity,
                "available_quantity": 0
            })
            continue
        
        # Check stock if tracking inventory
        if product.track_inventory:
            if product.inventory_quantity < item.quantity and not product.allow_backorders:
                issues.append({
                    "product_id": product.id,
                    "product_name": product.name,
                    "issue": "Insufficient stock",
                    "requested_quantity": item.quantity,
                    "available_quantity": product.inventory_quantity
                })
    
    return issues


def get_cart_totals(cart: Cart) -> dict:
    """Calculate cart totals and summary"""
    if not cart or not cart.items:
        return {
            "subtotal": 0.0,
            "total_items": 0,
            "items_count": 0
        }
    
    subtotal = sum(item.total_price for item in cart.items)
    total_items = sum(item.quantity for item in cart.items)
    items_count = len(cart.items)
    
    return {
        "subtotal": float(subtotal),
        "total_items": total_items,
        "items_count": items_count
    }


def transfer_cart_to_user(db: Session, from_user_id: int, to_user_id: int) -> bool:
    """Transfer cart items from one user to another (useful for guest to authenticated user)"""
    
    from_cart = get_cart_with_items(db, from_user_id)
    if not from_cart or not from_cart.items:
        return False
    
    to_cart = get_or_create_cart(db, to_user_id)
    
    # Transfer each item
    for item in from_cart.items:
        # Check if item already exists in destination cart
        existing_item = get_cart_item(db, to_cart.id, item.product_id)
        
        if existing_item:
            # Merge quantities
            existing_item.quantity += item.quantity
        else:
            # Create new item in destination cart
            new_item = CartItem(
                cart_id=to_cart.id,
                product_id=item.product_id,
                quantity=item.quantity,
                unit_price=item.unit_price
            )
            db.add(new_item)
    
    # Clear source cart
    clear_cart(db, from_user_id)
    
    db.commit()
    return True
