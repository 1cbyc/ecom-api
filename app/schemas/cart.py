from pydantic import BaseModel, Field, validator
from typing import List, Optional
from datetime import datetime
from decimal import Decimal
from app.schemas.product import Product


class CartItemBase(BaseModel):
    product_id: int
    quantity: int = Field(..., gt=0, description="Quantity must be greater than 0")


class CartItemAdd(CartItemBase):
    pass


class CartItemUpdate(BaseModel):
    quantity: int = Field(..., gt=0, description="Quantity must be greater than 0")


class CartItem(CartItemBase):
    id: int
    unit_price: Decimal
    total_price: float
    created_at: datetime
    updated_at: Optional[datetime] = None
    product: Product

    class Config:
        from_attributes = True


class CartSummary(BaseModel):
    subtotal: float = Field(..., description="Sum of all cart items")
    total_items: int = Field(..., description="Total number of items in cart")
    items_count: int = Field(..., description="Number of unique products in cart")


class Cart(BaseModel):
    id: int
    user_id: int
    items: List[CartItem] = []
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class CartResponse(BaseModel):
    cart: Cart
    summary: CartSummary
    message: str = "Success"


class AddToCartRequest(BaseModel):
    product_id: int = Field(..., gt=0)
    quantity: int = Field(default=1, gt=0, le=100, description="Quantity between 1 and 100")


class UpdateCartItemRequest(BaseModel):
    quantity: int = Field(..., gt=0, le=100, description="Quantity between 1 and 100")


class CartItemRemoveResponse(BaseModel):
    message: str
    cart_summary: CartSummary
