from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List
from math import ceil

from app.api.v1.dependencies.auth import get_db, get_current_active_user, get_current_admin_user
from app.crud.order import (
    get_orders_by_user, get_all_orders, get_order, get_order_by_number,
    update_order_status, get_recent_orders_summary
)
from app.schemas.order import (
    OrderResponse, OrderListResponse, OrderStatusUpdate
)
from app.models.user import User

router = APIRouter()


@router.get("/my-orders", response_model=OrderListResponse)
def get_my_orders(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get current user's orders with pagination"""
    
    orders, total = get_orders_by_user(db, current_user.id, page, limit)
    
    pages = ceil(total / limit)
    has_next = page < pages
    has_prev = page > 1
    
    return OrderListResponse(
        items=orders,
        total=total,
        page=page,
        pages=pages,
        has_next=has_next,
        has_prev=has_prev
    )


@router.get("/order/{order_id}", response_model=OrderResponse)
def get_order_detail(
    order_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get order details (user can only see their own orders)"""
    
    order = get_order(db, order_id, user_id=current_user.id)
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    
    return order


@router.get("/order-number/{order_number}", response_model=OrderResponse)
def get_order_by_order_number(
    order_number: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get order by order number (user can only see their own orders)"""
    
    order = get_order_by_number(db, order_number, user_id=current_user.id)
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    
    return order


# Admin-only endpoints
@router.get("/admin/all", response_model=OrderListResponse)
def get_all_orders_admin(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Get all orders (admin only)"""
    
    orders, total = get_all_orders(db, page, limit)
    
    pages = ceil(total / limit)
    has_next = page < pages
    has_prev = page > 1
    
    return OrderListResponse(
        items=orders,
        total=total,
        page=page,
        pages=pages,
        has_next=has_next,
        has_prev=has_prev
    )


@router.get("/admin/order/{order_id}", response_model=OrderResponse)
def get_any_order_admin(
    order_id: int,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Get any order by ID (admin only)"""
    
    order = get_order(db, order_id)
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    
    return order


@router.put("/admin/order/{order_id}/status", response_model=OrderResponse)
def update_order_status_admin(
    order_id: int,
    status_update: OrderStatusUpdate,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Update order status (admin only)"""
    
    order = update_order_status(db, order_id, status_update)
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    
    return order


@router.get("/admin/summary")
def get_orders_summary(
    days: int = Query(30, ge=1, le=365),
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Get orders summary for dashboard (admin only)"""
    
    summary = get_recent_orders_summary(db, days)
    return summary
