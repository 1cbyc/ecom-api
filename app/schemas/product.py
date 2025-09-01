from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime
from decimal import Decimal


class CategoryBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    slug: str = Field(..., min_length=1, max_length=100)


class CategoryCreate(CategoryBase):
    pass


class CategoryUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    slug: Optional[str] = Field(None, min_length=1, max_length=100)
    is_active: Optional[bool] = None


class Category(CategoryBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class ProductBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    short_description: Optional[str] = Field(None, max_length=500)
    slug: str = Field(..., min_length=1, max_length=200)
    price: Decimal = Field(..., gt=0, decimal_places=2)
    compare_at_price: Optional[Decimal] = Field(None, gt=0, decimal_places=2)
    cost_price: Optional[Decimal] = Field(None, ge=0, decimal_places=2)
    sku: str = Field(..., min_length=1, max_length=100)
    inventory_quantity: int = Field(default=0, ge=0)
    track_inventory: bool = True
    allow_backorders: bool = False
    is_featured: bool = False
    image_url: Optional[str] = None
    meta_title: Optional[str] = Field(None, max_length=200)
    meta_description: Optional[str] = Field(None, max_length=500)
    weight: Optional[Decimal] = Field(None, ge=0, decimal_places=2)
    length: Optional[Decimal] = Field(None, ge=0, decimal_places=2)
    width: Optional[Decimal] = Field(None, ge=0, decimal_places=2)
    height: Optional[Decimal] = Field(None, ge=0, decimal_places=2)

    @validator('compare_at_price')
    def compare_price_must_be_higher(cls, v, values):
        if v is not None and 'price' in values and v <= values['price']:
            raise ValueError('Compare at price must be higher than regular price')
        return v


class ProductCreate(ProductBase):
    category_ids: List[int] = Field(default=[], description="List of category IDs")


class ProductUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    short_description: Optional[str] = Field(None, max_length=500)
    slug: Optional[str] = Field(None, min_length=1, max_length=200)
    price: Optional[Decimal] = Field(None, gt=0, decimal_places=2)
    compare_at_price: Optional[Decimal] = Field(None, gt=0, decimal_places=2)
    cost_price: Optional[Decimal] = Field(None, ge=0, decimal_places=2)
    sku: Optional[str] = Field(None, min_length=1, max_length=100)
    inventory_quantity: Optional[int] = Field(None, ge=0)
    track_inventory: Optional[bool] = None
    allow_backorders: Optional[bool] = None
    is_active: Optional[bool] = None
    is_featured: Optional[bool] = None
    image_url: Optional[str] = None
    meta_title: Optional[str] = Field(None, max_length=200)
    meta_description: Optional[str] = Field(None, max_length=500)
    weight: Optional[Decimal] = Field(None, ge=0, decimal_places=2)
    length: Optional[Decimal] = Field(None, ge=0, decimal_places=2)
    width: Optional[Decimal] = Field(None, ge=0, decimal_places=2)
    height: Optional[Decimal] = Field(None, ge=0, decimal_places=2)
    category_ids: Optional[List[int]] = None


class Product(ProductBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    categories: List[Category] = []
    is_in_stock: bool
    is_on_sale: bool

    class Config:
        from_attributes = True


class ProductList(BaseModel):
    items: List[Product]
    total: int
    page: int
    pages: int
    has_next: bool
    has_prev: bool


class ProductSearch(BaseModel):
    page: int = Field(default=1, ge=1)
    limit: int = Field(default=20, ge=1, le=100)
    search: Optional[str] = None
    category_id: Optional[int] = None
    min_price: Optional[Decimal] = Field(None, ge=0)
    max_price: Optional[Decimal] = Field(None, ge=0)
    is_featured: Optional[bool] = None
    in_stock_only: bool = False
    sort_by: str = Field(default="created_at", pattern="^(name|price|created_at)$")
    sort_order: str = Field(default="desc", pattern="^(asc|desc)$")
