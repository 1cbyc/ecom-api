from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
from app.api.v1.dependencies.auth import get_db, get_current_active_user
from app.crud.cart import (
    get_cart_with_items, add_item_to_cart, update_cart_item, 
    remove_item_from_cart, clear_cart, validate_cart_stock, get_cart_totals
)
from app.schemas.cart import (
    Cart, CartResponse, AddToCartRequest, UpdateCartItemRequest, 
    CartItemRemoveResponse, CartSummary
)
from app.models.user import User

router = APIRouter()


@router.get("/", response_model=CartResponse)
def get_cart(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get current user's cart with all items"""
    cart = get_cart_with_items(db, current_user.id)
    
    if not cart:
        # Return empty cart structure
        empty_cart = {
            "id": 0,
            "user_id": current_user.id,
            "items": [],
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        }
        empty_summary = {
            "subtotal": 0.0,
            "total_items": 0,
            "items_count": 0
        }
        return CartResponse(cart=empty_cart, summary=CartSummary(**empty_summary), message="Cart is empty")
    
    # calculate cart summary
    summary = get_cart_totals(cart)
    
    return CartResponse(cart=cart, summary=CartSummary(**summary), message="Cart retrieved successfully")


@router.post("/add", response_model=CartResponse)
def add_to_cart(
    request: AddToCartRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Add item to cart"""
    try:
        cart = add_item_to_cart(db, current_user.id, request)
        summary = get_cart_totals(cart)
        
        return CartResponse(
            cart=cart,
            summary=CartSummary(**summary),
            message=f"Added {request.quantity} item(s) to cart"
        )
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to add item to cart"
        )


@router.put("/items/{product_id}", response_model=CartResponse)
def update_cart_item_endpoint(
    product_id: int,
    request: UpdateCartItemRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update cart item quantity"""
    try:
        cart = update_cart_item(db, current_user.id, product_id, request)
        summary = get_cart_totals(cart)
        
        return CartResponse(
            cart=cart,
            summary=CartSummary(**summary),
            message=f"Updated item quantity to {request.quantity}"
        )
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update cart item"
        )


@router.delete("/items/{product_id}", response_model=CartItemRemoveResponse)
def remove_from_cart(
    product_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Remove item from cart"""
    try:
        cart = remove_item_from_cart(db, current_user.id, product_id)
        summary = get_cart_totals(cart)
        
        return CartItemRemoveResponse(
            message="Item removed from cart",
            cart_summary=CartSummary(**summary)
        )
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to remove item from cart"
        )


@router.delete("/clear", response_model=dict)
def clear_cart_endpoint(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Clear all items from cart"""
    try:
        success = clear_cart(db, current_user.id)
        if success:
            return {"message": "Cart cleared successfully"}
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to clear cart"
            )
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to clear cart"
        )


@router.get("/validate", response_model=dict)
def validate_cart(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Validate cart items against current stock and product availability"""
    try:
        issues = validate_cart_stock(db, current_user.id)
        
        if issues:
            return {
                "valid": False,
                "message": f"Found {len(issues)} issue(s) with cart items",
                "issues": issues
            }
        else:
            return {
                "valid": True,
                "message": "All cart items are valid and in stock"
            }
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to validate cart"
        )


@router.get("/summary", response_model=CartSummary)
def get_cart_summary(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get cart summary (totals and counts)"""
    cart = get_cart_with_items(db, current_user.id)
    summary = get_cart_totals(cart)
    return CartSummary(**summary)


@router.post("/quick-add/{product_id}", response_model=CartResponse)
def quick_add_to_cart(
    product_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Quick add single item to cart (quantity = 1)"""
    request = AddToCartRequest(product_id=product_id, quantity=1)
    return add_to_cart(request, current_user, db)
