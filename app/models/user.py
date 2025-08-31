"""
User model for authentication and user management.

This model handles both regular users and admin users.
In e-commerce, user management is critical for:
- Authentication & authorization
- Order history tracking
- Profile management
- Admin access control
"""

from sqlalchemy import Boolean, Column, Integer, String, DateTime, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from app.db.base import Base


class UserRole(str, enum.Enum):
    """
    User roles for permission management.
    
    USER: Regular customers who can browse, shop, and checkout
    ADMIN: Administrative users who can manage products, view all orders, etc.
    """
    USER = "user"
    ADMIN = "admin"


class User(Base):
    """
    User model representing both customers and administrators.
    
    Key Design Decisions:
    1. Email as unique identifier (common in e-commerce)
    2. Hashed passwords (never store plain text!)
    3. Role-based access control
    4. Timestamps for audit trails
    5. Soft delete capability (is_active flag)
    """
    
    __tablename__ = "users"
    
    # Primary Key
    id = Column(Integer, primary_key=True, index=True)
    
    # User Information
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    full_name = Column(String, nullable=True)
    
    # Authentication
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)  # For soft delete/account suspension
    is_verified = Column(Boolean, default=False)  # Email verification
    
    # Authorization
    role = Column(Enum(UserRole), default=UserRole.USER)
    
    # Timestamps (crucial for e-commerce audit trails)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    # One user has one cart
    cart = relationship("Cart", back_populates="user", uselist=False, cascade="all, delete-orphan")
    
    # One user can have many orders
    orders = relationship("Order", back_populates="user", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<User(id={self.id}, email='{self.email}', role='{self.role}')>"
