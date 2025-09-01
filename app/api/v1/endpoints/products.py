from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from math import ceil
from app.api.v1.dependencies.auth import get_db, get_current_active_user, get_current_admin_user
from app.crud.product import (
    search_products, get_product, get_product_by_slug, create_product, 
    update_product, delete_product, get_featured_products, get_product_by_sku
)
from app.schemas.product import (
    Product, ProductCreate, ProductUpdate, ProductList, ProductSearch
)
from app.models.user import User

router = APIRouter()


@router.get("/", response_model=ProductList)
def list_products(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    search: Optional[str] = Query(None),
    category_id: Optional[int] = Query(None),
    min_price: Optional[float] = Query(None, ge=0),
    max_price: Optional[float] = Query(None, ge=0),
    is_featured: Optional[bool] = Query(None),
    in_stock_only: bool = Query(False),
    sort_by: str = Query("created_at", pattern="^(name|price|created_at)$"),
    sort_order: str = Query("desc", pattern="^(asc|desc)$"),
    db: Session = Depends(get_db)
):
    search_params = ProductSearch(
        page=page,
        limit=limit,
        search=search,
        category_id=category_id,
        min_price=min_price,
        max_price=max_price,
        is_featured=is_featured,
        in_stock_only=in_stock_only,
        sort_by=sort_by,
        sort_order=sort_order
    )
    
    products, total = search_products(db, search_params)
    
    pages = ceil(total / limit)
    has_next = page < pages
    has_prev = page > 1
    
    return ProductList(
        items=products,
        total=total,
        page=page,
        pages=pages,
        has_next=has_next,
        has_prev=has_prev
    )


@router.get("/featured", response_model=List[Product])
def get_featured_products_endpoint(
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db)
):
    return get_featured_products(db, limit=limit)


@router.get("/{product_id}", response_model=Product)
def get_product_by_id(product_id: int, db: Session = Depends(get_db)):
    product = get_product(db, product_id=product_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    return product


@router.get("/slug/{slug}", response_model=Product)
def get_product_by_slug_endpoint(slug: str, db: Session = Depends(get_db)):
    product = get_product_by_slug(db, slug=slug)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    return product


# Admin-only endpoints
@router.post("/", response_model=Product)
def create_product_endpoint(
    product: ProductCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    # Check if SKU already exists
    existing_product = get_product_by_sku(db, product.sku)
    if existing_product:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Product with this SKU already exists"
        )
    
    # Check if slug already exists
    existing_product = get_product_by_slug(db, product.slug, active_only=False)
    if existing_product:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Product with this slug already exists"
        )
    
    return create_product(db=db, product=product)


@router.put("/{product_id}", response_model=Product)
def update_product_endpoint(
    product_id: int,
    product_update: ProductUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    # Check if product exists
    existing_product = get_product(db, product_id, active_only=False)
    if not existing_product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    # Check if SKU is unique (if being updated)
    if product_update.sku:
        sku_check = get_product_by_sku(db, product_update.sku)
        if sku_check and sku_check.id != product_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Product with this SKU already exists"
            )
    
    # Check if slug is unique (if being updated)
    if product_update.slug:
        slug_check = get_product_by_slug(db, product_update.slug, active_only=False)
        if slug_check and slug_check.id != product_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Product with this slug already exists"
            )
    
    updated_product = update_product(db=db, product_id=product_id, product_update=product_update)
    if not updated_product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    return updated_product


@router.delete("/{product_id}")
def delete_product_endpoint(
    product_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    success = delete_product(db=db, product_id=product_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    return {"message": "Product deleted successfully"}


# Admin endpoint to get all products (including inactive)
@router.get("/admin/all", response_model=ProductList)
def list_all_products_admin(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    search: Optional[str] = Query(None),
    category_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    # For admin, we modify the search to include inactive products
    search_params = ProductSearch(
        page=page,
        limit=limit,
        search=search,
        category_id=category_id
    )
    
    # This would need modification in crud to support admin view
    products, total = search_products(db, search_params)
    
    pages = ceil(total / limit)
    has_next = page < pages
    has_prev = page > 1
    
    return ProductList(
        items=products,
        total=total,
        page=page,
        pages=pages,
        has_next=has_next,
        has_prev=has_prev
    )
