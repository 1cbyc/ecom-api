"""
Order and payment models for e-commerce transactions.

This module handles:
- Order lifecycle management
- Payment processing integration
- Order status tracking
- Financial record keeping
"""

from sqlalchemy import Column, Integer, String, Text, Decimal, Boolean, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from app.db.base import Base


class OrderStatus(str, enum.Enum):
    """
    Order status tracking throughout the fulfillment process.
    
    This enum represents the typical e-commerce order lifecycle:
    """
    PENDING = "pending"           # Order created, payment pending
    PAID = "paid"                # Payment confirmed
    PROCESSING = "processing"     # Order being prepared
    SHIPPED = "shipped"          # Order sent to customer
    DELIVERED = "delivered"      # Order received by customer
    CANCELLED = "cancelled"      # Order cancelled
    REFUNDED = "refunded"        # Order refunded


class PaymentStatus(str, enum.Enum):
    """Payment status tracking for financial records."""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"


class Order(Base):
    """
    Order model representing a completed purchase.
    
    Key e-commerce considerations:
    1. Immutable pricing (locked at purchase time)
    2. Complete audit trail
    3. Status tracking for fulfillment
    4. Customer service information
    """
    
    __tablename__ = "orders"
    
    # Primary Key
    id = Column(Integer, primary_key=True, index=True)
    
    # Order Identification
    order_number = Column(String, unique=True, index=True, nullable=False)  # Human-readable order ID
    
    # Foreign Keys
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Order Status
    status = Column(Enum(OrderStatus), default=OrderStatus.PENDING)
    
    # Financial Information (locked at purchase time)
    subtotal = Column(Decimal(10, 2), nullable=False)  # Sum of all items
    tax_amount = Column(Decimal(10, 2), default=0)     # Tax calculated
    shipping_amount = Column(Decimal(10, 2), default=0) # Shipping cost
    total_amount = Column(Decimal(10, 2), nullable=False) # Final total
    
    # Shipping Information
    shipping_address_line1 = Column(String, nullable=False)
    shipping_address_line2 = Column(String, nullable=True)
    shipping_city = Column(String, nullable=False)
    shipping_state = Column(String, nullable=False)
    shipping_postal_code = Column(String, nullable=False)
    shipping_country = Column(String, nullable=False)
    
    # Billing Information (can be different from shipping)
    billing_address_line1 = Column(String, nullable=False)
    billing_address_line2 = Column(String, nullable=True)
    billing_city = Column(String, nullable=False)
    billing_state = Column(String, nullable=False)
    billing_postal_code = Column(String, nullable=False)
    billing_country = Column(String, nullable=False)
    
    # Customer Information
    customer_email = Column(String, nullable=False)  # Stored for record keeping
    customer_phone = Column(String, nullable=True)
    
    # Order Notes
    customer_notes = Column(Text, nullable=True)  # Special delivery instructions
    admin_notes = Column(Text, nullable=True)     # Internal notes
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    shipped_at = Column(DateTime(timezone=True), nullable=True)
    delivered_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="orders")
    items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")
    payment = relationship("Payment", back_populates="order", uselist=False, cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Order(id={self.id}, order_number='{self.order_number}', status='{self.status}')>"
    
    @property
    def item_count(self):
        """Total number of items in the order."""
        return sum(item.quantity for item in self.items)


class OrderItem(Base):
    """
    Individual items within an order.
    
    Why separate from cart items?
    1. Orders are immutable once created
    2. Need to preserve exact pricing and product details
    3. Inventory adjustments happen here
    """
    
    __tablename__ = "order_items"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Foreign Keys
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    
    # Item Details (frozen at order time)
    product_name = Column(String, nullable=False)     # Product name when ordered
    product_sku = Column(String, nullable=False)      # SKU when ordered
    quantity = Column(Integer, nullable=False)
    unit_price = Column(Decimal(10, 2), nullable=False)  # Price when ordered
    total_price = Column(Decimal(10, 2), nullable=False) # quantity * unit_price
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    order = relationship("Order", back_populates="items")
    product = relationship("Product", back_populates="order_items")
    
    def __repr__(self):
        return f"<OrderItem(id={self.id}, product_name='{self.product_name}', quantity={self.quantity})>"


class Payment(Base):
    """
    Payment records for orders.
    
    Tracks payment processing through external gateways like Stripe.
    Essential for financial reconciliation and customer service.
    """
    
    __tablename__ = "payments"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Foreign Keys
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    
    # Payment Details
    payment_method = Column(String, nullable=False)  # "stripe", "paypal", etc.
    payment_status = Column(Enum(PaymentStatus), default=PaymentStatus.PENDING)
    
    # Financial Information
    amount = Column(Decimal(10, 2), nullable=False)
    currency = Column(String(3), default="USD")  # ISO currency code
    
    # External Payment Gateway Information
    stripe_payment_intent_id = Column(String, nullable=True)  # Stripe Payment Intent ID
    stripe_charge_id = Column(String, nullable=True)          # Stripe Charge ID
    transaction_id = Column(String, nullable=True)            # Generic transaction ID
    
    # Payment Gateway Response
    gateway_response = Column(Text, nullable=True)  # JSON response from payment gateway
    failure_reason = Column(String, nullable=True)  # Reason for failed payments
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    processed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    order = relationship("Order", back_populates="payment")
    
    def __repr__(self):
        return f"<Payment(id={self.id}, order_id={self.order_id}, status='{self.payment_status}')>"
