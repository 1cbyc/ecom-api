from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List
from app.api.v1.dependencies.auth import get_db, get_current_admin_user
from app.crud.product import (
    get_categories, get_category, get_category_by_slug,
    create_category, update_category, delete_category
)
from app.schemas.product import Category, CategoryCreate, CategoryUpdate
from app.models.user import User

router = APIRouter()


@router.get("/", response_model=List[Category])
def list_categories(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: Session = Depends(get_db)
):
    return get_categories(db, skip=skip, limit=limit, active_only=True)


@router.get("/{category_id}", response_model=Category)
def get_category_by_id(category_id: int, db: Session = Depends(get_db)):
    category = get_category(db, category_id=category_id)
    if not category or not category.is_active:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
        )
    return category


@router.get("/slug/{slug}", response_model=Category)
def get_category_by_slug_endpoint(slug: str, db: Session = Depends(get_db)):
    category = get_category_by_slug(db, slug=slug)
    if not category or not category.is_active:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
        )
    return category


# Admin-only endpoints
@router.post("/", response_model=Category)
def create_category_endpoint(
    category: CategoryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    # Check if slug already exists
    existing_category = get_category_by_slug(db, category.slug)
    if existing_category:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Category with this slug already exists"
        )
    
    return create_category(db=db, category=category)


@router.put("/{category_id}", response_model=Category)
def update_category_endpoint(
    category_id: int,
    category_update: CategoryUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    # Check if category exists
    existing_category = get_category(db, category_id)
    if not existing_category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
        )
    
    # Check if slug is unique (if being updated)
    if category_update.slug:
        slug_check = get_category_by_slug(db, category_update.slug)
        if slug_check and slug_check.id != category_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Category with this slug already exists"
            )
    
    updated_category = update_category(db=db, category_id=category_id, category_update=category_update)
    if not updated_category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
        )
    
    return updated_category


@router.delete("/{category_id}")
def delete_category_endpoint(
    category_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    success = delete_category(db=db, category_id=category_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
        )
    
    return {"message": "Category deleted successfully"}


# Admin endpoint to get all categories (including inactive)
@router.get("/admin/all", response_model=List[Category])
def list_all_categories_admin(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    return get_categories(db, skip=skip, limit=limit, active_only=False)
