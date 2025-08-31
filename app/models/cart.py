"""
Shopping cart models for e-commerce functionality.

The cart system handles:
- Temporary storage of items before purchase
- Quantity management
- Price calculations
- Session persistence
"""

from sqlalchemy import Column, Integer, ForeignKey, DateTime, Decimal
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base


class Cart(Base):
    """
    Shopping cart for each user.
    
    Design decisions:
    1. One cart per user (simpler than multiple carts)
    2. Persistent cart (survives login/logout)
    3. Cart items stored separately for flexibility
    """
    
    __tablename__ = "carts"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Foreign Keys
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="cart")
    items = relationship("CartItem", back_populates="cart", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Cart(id={self.id}, user_id={self.user_id}, items={len(self.items)})>"
    
    @property
    def total_items(self):
        """Calculate total number of items in cart."""
        return sum(item.quantity for item in self.items)
    
    @property
    def total_price(self):
        """Calculate total price of all items in cart."""
        return sum(item.total_price for item in self.items)


class CartItem(Base):
    """
    Individual items within a shopping cart.
    
    Why separate table?
    1. Allows quantity tracking per product
    2. Stores price at time of adding (important for price changes)
    3. Easier to implement cart operations (add, remove, update)
    """
    
    __tablename__ = "cart_items"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Foreign Keys
    cart_id = Column(Integer, ForeignKey("carts.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    
    # Item Details
    quantity = Column(Integer, default=1, nullable=False)
    # Store price when added to cart (protects against price changes)
    unit_price = Column(Decimal(10, 2), nullable=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    cart = relationship("Cart", back_populates="items")
    product = relationship("Product", back_populates="cart_items")
    
    def __repr__(self):
        return f"<CartItem(id={self.id}, product_id={self.product_id}, quantity={self.quantity})>"
    
    @property
    def total_price(self):
        """Calculate total price for this cart item."""
        return float(self.unit_price) * self.quantity
