from sqlalchemy import Column, Integer, ForeignKey, DateTime
from sqlalchemy.sql.sqltypes import Numeric
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base


class Cart(Base):
    __tablename__ = "carts"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    user = relationship("User", back_populates="cart")
    items = relationship("CartItem", back_populates="cart", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Cart(id={self.id}, user_id={self.user_id}, items={len(self.items)})>"
    
    @property
    def total_items(self):
        return sum(item.quantity for item in self.items)
    
    @property
    def total_price(self):
        return sum(item.total_price for item in self.items)
    
    @property
    def subtotal(self):
        return self.total_price
    
    @property
    def items_count(self):
        return len(self.items)


class CartItem(Base):
    __tablename__ = "cart_items"
    
    id = Column(Integer, primary_key=True, index=True)
    cart_id = Column(Integer, ForeignKey("carts.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    quantity = Column(Integer, default=1, nullable=False)
    unit_price = Column(Numeric(10, 2), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    cart = relationship("Cart", back_populates="items")
    product = relationship("Product", back_populates="cart_items")
    
    def __repr__(self):
        return f"<CartItem(id={self.id}, product_id={self.product_id}, quantity={self.quantity})>"
    
    @property
    def total_price(self):
        return float(self.unit_price) * self.quantity
