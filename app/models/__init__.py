"""
Models module initialization.

This file imports all models to ensure they're registered with SQLAlchemy.
When you import from this module, all relationships are properly set up.
"""

# Import all models so SQLAlchemy can find the relationships
from .user import User, UserRole
from .product import Product, Category
from .cart import Cart, CartItem
from .order import Order, OrderItem, Payment, OrderStatus, PaymentStatus

# This makes imports cleaner in other files
# Instead of: from app.models.user import User
# You can do: from app.models import User

__all__ = [
    "User",
    "UserRole", 
    "Product",
    "Category",
    "Cart",
    "CartItem",
    "Order",
    "OrderItem",
    "Payment",
    "OrderStatus",
    "PaymentStatus"
]
