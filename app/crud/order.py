from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, desc, func
from typing import Optional, List, Tuple
from decimal import Decimal
import uuid
from datetime import datetime, timedelta
from math import ceil

from app.models.order import Order, OrderItem, Payment, OrderStatus, PaymentStatus
from app.models.cart import Cart, CartItem
from app.models.product import Product
from app.models.user import User
from app.schemas.order import CheckoutRequest, OrderStatusUpdate
from app.crud.cart import get_cart_with_items, clear_cart
from app.crud.product import update_product_inventory


def generate_order_number() -> str:
    """Generate unique order number"""
    timestamp = datetime.now().strftime("%Y%m%d")
    unique_id = str(uuid.uuid4())[:8].upper()
    return f"ORD-{timestamp}-{unique_id}"


def calculate_order_totals(cart: Cart) -> dict:
    """Calculate order totals including tax and shipping"""
    subtotal = sum(float(item.unit_price) * item.quantity for item in cart.items)
    
    # Simple tax calculation (8.5% - in real app this would be based on location)
    tax_rate = Decimal('0.085')
    tax_amount = Decimal(str(subtotal)) * tax_rate
    
    # Simple shipping calculation
    if subtotal >= 100:
        shipping_amount = Decimal('0.00')  # Free shipping over $100
    else:
        shipping_amount = Decimal('9.99')  # Standard shipping
    
    total_amount = Decimal(str(subtotal)) + tax_amount + shipping_amount
    
    return {
        "subtotal": Decimal(str(subtotal)),
        "tax_amount": tax_amount,
        "shipping_amount": shipping_amount,
        "total_amount": total_amount
    }


def create_order_from_cart(
    db: Session, 
    user_id: int, 
    checkout_request: CheckoutRequest,
    payment_intent_id: str
) -> Order:
    """Create order from user's cart"""
    
    # Get user's cart
    cart = get_cart_with_items(db, user_id)
    if not cart or not cart.items:
        raise ValueError("Cart is empty")
    
    # Get user details
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise ValueError("User not found")
    
    # Calculate totals
    totals = calculate_order_totals(cart)
    
    # Use billing address or default to shipping address
    billing_address = checkout_request.billing_address or checkout_request.shipping_address
    
    # Create order
    order = Order(
        order_number=generate_order_number(),
        user_id=user_id,
        status=OrderStatus.PENDING,
        subtotal=totals["subtotal"],
        tax_amount=totals["tax_amount"],
        shipping_amount=totals["shipping_amount"],
        total_amount=totals["total_amount"],
        shipping_address_line1=checkout_request.shipping_address.address_line1,
        shipping_address_line2=checkout_request.shipping_address.address_line2,
        shipping_city=checkout_request.shipping_address.city,
        shipping_state=checkout_request.shipping_address.state,
        shipping_postal_code=checkout_request.shipping_address.postal_code,
        shipping_country=checkout_request.shipping_address.country,
        billing_address_line1=billing_address.address_line1,
        billing_address_line2=billing_address.address_line2,
        billing_city=billing_address.city,
        billing_state=billing_address.state,
        billing_postal_code=billing_address.postal_code,
        billing_country=billing_address.country,
        customer_email=user.email,
        customer_phone=checkout_request.customer_phone,
        customer_notes=checkout_request.customer_notes
    )
    
    db.add(order)
    db.flush()  # Get order ID without committing
    
    # Create order items from cart items
    for cart_item in cart.items:
        order_item = OrderItem(
            order_id=order.id,
            product_id=cart_item.product_id,
            product_name=cart_item.product.name,
            product_sku=cart_item.product.sku,
            quantity=cart_item.quantity,
            unit_price=cart_item.unit_price,
            total_price=cart_item.unit_price * cart_item.quantity
        )
        db.add(order_item)
    
    # Create payment record
    payment = Payment(
        order_id=order.id,
        payment_method="stripe",
        payment_status=PaymentStatus.PENDING,
        amount=totals["total_amount"],
        currency="USD",
        stripe_payment_intent_id=payment_intent_id
    )
    db.add(payment)
    
    db.commit()
    db.refresh(order)
    
    return order


def get_order(db: Session, order_id: int, user_id: Optional[int] = None) -> Optional[Order]:
    """Get order by ID, optionally filtered by user"""
    query = db.query(Order).options(
        joinedload(Order.items).joinedload(OrderItem.product),
        joinedload(Order.payment)
    )
    
    if user_id:
        query = query.filter(and_(Order.id == order_id, Order.user_id == user_id))
    else:
        query = query.filter(Order.id == order_id)
    
    return query.first()


def get_order_by_number(db: Session, order_number: str, user_id: Optional[int] = None) -> Optional[Order]:
    """Get order by order number"""
    query = db.query(Order).options(
        joinedload(Order.items).joinedload(OrderItem.product),
        joinedload(Order.payment)
    )
    
    if user_id:
        query = query.filter(and_(Order.order_number == order_number, Order.user_id == user_id))
    else:
        query = query.filter(Order.order_number == order_number)
    
    return query.first()


def get_orders_by_user(db: Session, user_id: int, page: int = 1, limit: int = 20) -> Tuple[List[Order], int]:
    """Get paginated orders for a user"""
    query = db.query(Order).options(
        joinedload(Order.items),
        joinedload(Order.payment)
    ).filter(Order.user_id == user_id).order_by(desc(Order.created_at))
    
    total = query.count()
    offset = (page - 1) * limit
    orders = query.offset(offset).limit(limit).all()
    
    return orders, total


def get_all_orders(db: Session, page: int = 1, limit: int = 20) -> Tuple[List[Order], int]:
    """Get all orders (admin only)"""
    query = db.query(Order).options(
        joinedload(Order.items),
        joinedload(Order.payment),
        joinedload(Order.user)
    ).order_by(desc(Order.created_at))
    
    total = query.count()
    offset = (page - 1) * limit
    orders = query.offset(offset).limit(limit).all()
    
    return orders, total


def update_order_status(db: Session, order_id: int, status_update: OrderStatusUpdate) -> Optional[Order]:
    """Update order status"""
    order = get_order(db, order_id)
    if not order:
        return None
    
    order.status = status_update.status
    if status_update.admin_notes:
        order.admin_notes = status_update.admin_notes
    
    # Set timestamps based on status
    if status_update.status == OrderStatus.SHIPPED and not order.shipped_at:
        order.shipped_at = datetime.utcnow()
    elif status_update.status == OrderStatus.DELIVERED and not order.delivered_at:
        order.delivered_at = datetime.utcnow()
    
    db.commit()
    db.refresh(order)
    return order


def process_successful_payment(db: Session, payment_intent_id: str) -> Optional[Order]:
    """Process successful payment and update order/inventory"""
    
    # Find payment by intent ID
    payment = db.query(Payment).filter(
        Payment.stripe_payment_intent_id == payment_intent_id
    ).first()
    
    if not payment:
        return None
    
    # Update payment status
    payment.payment_status = PaymentStatus.COMPLETED
    payment.processed_at = datetime.utcnow()
    
    # Get the order
    order = get_order(db, payment.order_id)
    if not order:
        return None
    
    # Update order status
    order.status = OrderStatus.PAID
    
    # Adjust inventory for each item
    for item in order.items:
        update_product_inventory(db, item.product_id, -item.quantity)
    
    # Clear the user's cart
    clear_cart(db, order.user_id)
    
    db.commit()
    return order


def process_failed_payment(db: Session, payment_intent_id: str, failure_reason: str) -> Optional[Order]:
    """Process failed payment"""
    
    payment = db.query(Payment).filter(
        Payment.stripe_payment_intent_id == payment_intent_id
    ).first()
    
    if not payment:
        return None
    
    # Update payment status
    payment.payment_status = PaymentStatus.FAILED
    payment.failure_reason = failure_reason
    
    # Get the order and update status
    order = get_order(db, payment.order_id)
    if order:
        order.status = OrderStatus.CANCELLED
    
    db.commit()
    return order


def get_order_by_payment_intent(db: Session, payment_intent_id: str) -> Optional[Order]:
    """Get order by Stripe payment intent ID"""
    payment = db.query(Payment).filter(
        Payment.stripe_payment_intent_id == payment_intent_id
    ).first()
    
    if not payment:
        return None
    
    return get_order(db, payment.order_id)


def get_recent_orders_summary(db: Session, days: int = 30) -> dict:
    """Get recent orders summary for dashboard"""
    cutoff_date = datetime.utcnow() - timedelta(days=days)
    
    # Total orders and revenue
    orders_query = db.query(Order).filter(Order.created_at >= cutoff_date)
    total_orders = orders_query.count()
    
    paid_orders = orders_query.filter(Order.status == OrderStatus.PAID)
    total_revenue = paid_orders.with_entities(func.sum(Order.total_amount)).scalar() or 0
    
    # Orders by status
    status_counts = {}
    for status in OrderStatus:
        count = orders_query.filter(Order.status == status).count()
        status_counts[status.value] = count
    
    return {
        "total_orders": total_orders,
        "total_revenue": float(total_revenue),
        "orders_by_status": status_counts,
        "period_days": days
    }
