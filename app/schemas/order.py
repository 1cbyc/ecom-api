from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional
from datetime import datetime
from decimal import Decimal
from app.models.order import OrderStatus, PaymentStatus
from app.schemas.product import Product


class AddressBase(BaseModel):
    address_line1: str = Field(..., min_length=1, max_length=255)
    address_line2: Optional[str] = Field(None, max_length=255)
    city: str = Field(..., min_length=1, max_length=100)
    state: str = Field(..., min_length=1, max_length=100)
    postal_code: str = Field(..., min_length=1, max_length=20)
    country: str = Field(..., min_length=2, max_length=100)


class CheckoutRequest(BaseModel):
    shipping_address: AddressBase
    billing_address: Optional[AddressBase] = None  # If None, use shipping address
    customer_phone: Optional[str] = Field(None, max_length=20)
    customer_notes: Optional[str] = Field(None, max_length=1000)


class PaymentIntentResponse(BaseModel):
    client_secret: str
    payment_intent_id: str
    amount: float
    currency: str = "usd"
    order_id: int


class OrderItemResponse(BaseModel):
    id: int
    product_id: int
    product_name: str
    product_sku: str
    quantity: int
    unit_price: Decimal
    total_price: Decimal
    product: Optional[Product] = None

    class Config:
        from_attributes = True


class PaymentResponse(BaseModel):
    id: int
    payment_method: str
    payment_status: PaymentStatus
    amount: Decimal
    currency: str
    stripe_payment_intent_id: Optional[str] = None
    transaction_id: Optional[str] = None
    processed_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class OrderResponse(BaseModel):
    id: int
    order_number: str
    status: OrderStatus
    subtotal: Decimal
    tax_amount: Decimal
    shipping_amount: Decimal
    total_amount: Decimal
    shipping_address_line1: str
    shipping_address_line2: Optional[str] = None
    shipping_city: str
    shipping_state: str
    shipping_postal_code: str
    shipping_country: str
    billing_address_line1: str
    billing_address_line2: Optional[str] = None
    billing_city: str
    billing_state: str
    billing_postal_code: str
    billing_country: str
    customer_email: str
    customer_phone: Optional[str] = None
    customer_notes: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    shipped_at: Optional[datetime] = None
    delivered_at: Optional[datetime] = None
    items: List[OrderItemResponse] = []
    payment: Optional[PaymentResponse] = None

    class Config:
        from_attributes = True


class OrderListResponse(BaseModel):
    items: List[OrderResponse]
    total: int
    page: int
    pages: int
    has_next: bool
    has_prev: bool


class OrderStatusUpdate(BaseModel):
    status: OrderStatus
    admin_notes: Optional[str] = None


class WebhookEvent(BaseModel):
    type: str
    data: dict
