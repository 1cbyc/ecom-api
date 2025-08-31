"""
Product model for the e-commerce catalog.

This model represents items for sale and includes:
- Product information and descriptions
- Pricing and inventory management
- Category relationships
- Image handling
- SEO-friendly features (slug)
"""

from sqlalchemy import Column, Integer, String, Text, Decimal, Boolean, DateTime, Table, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base


# Association table for many-to-many relationship between products and categories
# This allows products to be in multiple categories (e.g., "iPhone" in both "Electronics" and "Phones")
product_category_association = Table(
    'product_categories',
    Base.metadata,
    Column('product_id', Integer, ForeignKey('products.id'), primary_key=True),
    Column('category_id', Integer, ForeignKey('categories.id'), primary_key=True)
)


class Category(Base):
    """
    Product categories for organization and navigation.
    
    Categories help users find products and enable features like:
    - Filtered browsing
    - Category-specific promotions
    - Hierarchical navigation
    """
    
    __tablename__ = "categories"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    description = Column(Text, nullable=True)
    slug = Column(String, unique=True, index=True, nullable=False)  # URL-friendly name
    is_active = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    products = relationship("Product", secondary=product_category_association, back_populates="categories")
    
    def __repr__(self):
        return f"<Category(id={self.id}, name='{self.name}')>"


class Product(Base):
    """
    Product model representing items for sale.
    
    Key E-commerce Considerations:
    1. Decimal for prices (avoid floating point errors!)
    2. Inventory tracking
    3. SEO-friendly slugs
    4. Multiple images support
    5. Active/inactive status for catalog management
    """
    
    __tablename__ = "products"
    
    # Primary Key
    id = Column(Integer, primary_key=True, index=True)
    
    # Product Information
    name = Column(String, index=True, nullable=False)
    description = Column(Text, nullable=True)
    short_description = Column(String(500), nullable=True)  # For product cards
    slug = Column(String, unique=True, index=True, nullable=False)  # URL-friendly identifier
    
    # Pricing (using Decimal for financial accuracy)
    price = Column(Decimal(10, 2), nullable=False)  # Up to 99,999,999.99
    compare_at_price = Column(Decimal(10, 2), nullable=True)  # Original price for discounts
    cost_price = Column(Decimal(10, 2), nullable=True)  # For profit calculations
    
    # Inventory Management
    sku = Column(String, unique=True, index=True, nullable=False)  # Stock Keeping Unit
    inventory_quantity = Column(Integer, default=0)
    track_inventory = Column(Boolean, default=True)
    allow_backorders = Column(Boolean, default=False)
    
    # Product Status
    is_active = Column(Boolean, default=True)
    is_featured = Column(Boolean, default=False)  # For homepage/promotions
    
    # Images (simple approach - single main image)
    # In production, you'd typically have a separate images table
    image_url = Column(String, nullable=True)
    
    # SEO & Marketing
    meta_title = Column(String, nullable=True)
    meta_description = Column(String, nullable=True)
    
    # Physical Properties (useful for shipping calculations)
    weight = Column(Decimal(8, 2), nullable=True)  # in grams or pounds
    length = Column(Decimal(8, 2), nullable=True)  # dimensions for shipping
    width = Column(Decimal(8, 2), nullable=True)
    height = Column(Decimal(8, 2), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    categories = relationship("Category", secondary=product_category_association, back_populates="products")
    cart_items = relationship("CartItem", back_populates="product", cascade="all, delete-orphan")
    order_items = relationship("OrderItem", back_populates="product")
    
    def __repr__(self):
        return f"<Product(id={self.id}, name='{self.name}', price={self.price})>"
    
    @property
    def is_in_stock(self):
        """Check if product is in stock."""
        if not self.track_inventory:
            return True
        return self.inventory_quantity > 0 or self.allow_backorders
    
    @property
    def display_price(self):
        """Get the price to display (handles discounts)."""
        return float(self.price)
    
    @property
    def is_on_sale(self):
        """Check if product is on sale."""
        return self.compare_at_price and self.compare_at_price > self.price
