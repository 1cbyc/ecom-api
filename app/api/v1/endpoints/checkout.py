from fastapi import APIRouter, Depends, HTTPException, status, Request, Header
from sqlalchemy.orm import Session
from typing import Optional
import logging

from app.api.v1.dependencies.auth import get_db, get_current_active_user, get_current_admin_user
from app.crud.order import (
    create_order_from_cart, get_order, process_successful_payment, 
    process_failed_payment, calculate_order_totals
)
from app.crud.cart import get_cart_with_items, validate_cart_stock
from app.schemas.order import (
    CheckoutRequest, PaymentIntentResponse, OrderResponse, WebhookEvent
)
from app.utils.stripe_service import (
    StripeService, create_payment_intent_for_order, verify_webhook_signature
)
from app.models.user import User
from app.core.config import settings

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/create-payment-intent", response_model=PaymentIntentResponse)
def create_payment_intent(
    checkout_request: CheckoutRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Create Stripe Payment Intent and order"""
    
    # Get and validate cart
    cart = get_cart_with_items(db, current_user.id)
    if not cart or not cart.items:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cart is empty"
        )
    
    # Validate stock availability
    stock_issues = validate_cart_stock(db, current_user.id)
    if stock_issues:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": "Some items are out of stock",
                "issues": stock_issues
            }
        )
    
    try:
        # Calculate order totals
        totals = calculate_order_totals(cart)
        
        # Create Stripe Payment Intent
        payment_intent = StripeService.create_payment_intent(
            amount=totals["total_amount"],
            metadata={
                "user_id": str(current_user.id),
                "user_email": current_user.email,
                "cart_items": len(cart.items)
            }
        )
        
        # Create order in database
        order = create_order_from_cart(
            db=db,
            user_id=current_user.id,
            checkout_request=checkout_request,
            payment_intent_id=payment_intent["id"]
        )
        
        return PaymentIntentResponse(
            client_secret=payment_intent["client_secret"],
            payment_intent_id=payment_intent["id"],
            amount=float(totals["total_amount"]),
            currency="usd",
            order_id=order.id
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Payment intent creation failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create payment intent"
        )


@router.get("/order/{order_id}", response_model=OrderResponse)
def get_order_by_id(
    order_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get order by ID (user can only see their own orders)"""
    
    order = get_order(db, order_id, user_id=current_user.id)
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    
    return order


@router.post("/webhook")
async def stripe_webhook(
    request: Request,
    stripe_signature: Optional[str] = Header(None, alias="stripe-signature")
):
    """Handle Stripe webhook events"""
    
    if not stripe_signature:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Missing stripe signature"
        )
    
    try:
        # Get raw payload
        payload = await request.body()
        
        # Verify webhook signature
        event = verify_webhook_signature(payload, stripe_signature)
        
        # Get database session
        db = next(get_db())
        
        # Handle different event types
        if event["type"] == "payment_intent.succeeded":
            payment_intent = event["data"]["object"]
            order = process_successful_payment(db, payment_intent["id"])
            
            if order:
                logger.info(f"Payment succeeded for order {order.order_number}")
            else:
                logger.warning(f"Order not found for payment intent {payment_intent['id']}")
        
        elif event["type"] == "payment_intent.payment_failed":
            payment_intent = event["data"]["object"]
            failure_reason = payment_intent.get("last_payment_error", {}).get("message", "Payment failed")
            
            order = process_failed_payment(db, payment_intent["id"], failure_reason)
            
            if order:
                logger.info(f"Payment failed for order {order.order_number}: {failure_reason}")
        
        elif event["type"] == "payment_intent.canceled":
            payment_intent = event["data"]["object"]
            order = process_failed_payment(db, payment_intent["id"], "Payment canceled")
            
            if order:
                logger.info(f"Payment canceled for order {order.order_number}")
        
        else:
            logger.info(f"Unhandled webhook event type: {event['type']}")
        
        return {"status": "success"}
        
    except Exception as e:
        logger.error(f"Webhook processing failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Webhook processing failed"
        )


@router.post("/cancel-payment/{payment_intent_id}")
def cancel_payment(
    payment_intent_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Cancel a payment intent"""
    
    try:
        # Cancel the payment intent in Stripe
        result = StripeService.cancel_payment_intent(payment_intent_id)
        
        # Update order status in database
        process_failed_payment(db, payment_intent_id, "Canceled by user")
        
        return {
            "message": "Payment canceled successfully",
            "payment_intent_id": payment_intent_id,
            "status": result["status"]
        }
        
    except Exception as e:
        logger.error(f"Payment cancellation failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to cancel payment"
        )


@router.get("/payment-status/{payment_intent_id}")
def get_payment_status(
    payment_intent_id: str,
    current_user: User = Depends(get_current_active_user)
):
    """Get payment status from Stripe"""
    
    try:
        payment_intent = StripeService.retrieve_payment_intent(payment_intent_id)
        
        return {
            "payment_intent_id": payment_intent["id"],
            "status": payment_intent["status"],
            "amount": payment_intent["amount"],
            "currency": payment_intent["currency"]
        }
        
    except Exception as e:
        logger.error(f"Failed to retrieve payment status: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve payment status"
        )
