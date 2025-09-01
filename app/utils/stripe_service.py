import stripe
from typing import Dict, Any, Optional
from decimal import Decimal
from app.core.config import settings

# Initialize Stripe (use test key or demo mode)
if settings.STRIPE_SECRET_KEY and settings.STRIPE_SECRET_KEY != "sk_test_your_stripe_secret_key":
    stripe.api_key = settings.STRIPE_SECRET_KEY
else:
    # Demo mode - we'll simulate Stripe responses
    stripe.api_key = None


class StripeService:
    """Service for handling Stripe payment operations"""
    
    @staticmethod
    def create_payment_intent(
        amount: Decimal,
        currency: str = "usd",
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Create a Stripe Payment Intent
        
        Args:
            amount: Amount in dollars (will be converted to cents)
            currency: Currency code (default: USD)
            metadata: Additional metadata to attach to payment
        
        Returns:
            Payment Intent object from Stripe
        """
        # Demo mode - simulate Stripe response
        if not stripe.api_key:
            import uuid
            demo_id = f"pi_demo_{uuid.uuid4().hex[:16]}"
            return {
                "id": demo_id,
                "client_secret": f"{demo_id}_secret_demo",
                "amount": int(amount * 100),
                "currency": currency,
                "status": "requires_payment_method"
            }
        
        try:
            # Convert amount to cents (Stripe expects integer cents)
            amount_cents = int(amount * 100)
            
            payment_intent = stripe.PaymentIntent.create(
                amount=amount_cents,
                currency=currency,
                metadata=metadata or {},
                # Enable automatic payment methods
                automatic_payment_methods={'enabled': True}
            )
            
            return {
                "id": payment_intent.id,
                "client_secret": payment_intent.client_secret,
                "amount": amount_cents,
                "currency": currency,
                "status": payment_intent.status
            }
            
        except stripe.error.StripeError as e:
            raise Exception(f"Stripe error: {str(e)}")
        except Exception as e:
            raise Exception(f"Payment intent creation failed: {str(e)}")
    
    @staticmethod
    def retrieve_payment_intent(payment_intent_id: str) -> Dict[str, Any]:
        """Retrieve a Payment Intent from Stripe"""
        # Demo mode
        if not stripe.api_key:
            return {
                "id": payment_intent_id,
                "status": "requires_payment_method",
                "amount": 99900,  # Demo amount
                "currency": "usd",
                "metadata": {}
            }
        
        try:
            payment_intent = stripe.PaymentIntent.retrieve(payment_intent_id)
            return {
                "id": payment_intent.id,
                "status": payment_intent.status,
                "amount": payment_intent.amount,
                "currency": payment_intent.currency,
                "metadata": payment_intent.metadata
            }
        except stripe.error.StripeError as e:
            raise Exception(f"Stripe error: {str(e)}")
    
    @staticmethod
    def confirm_payment_intent(
        payment_intent_id: str,
        payment_method: str
    ) -> Dict[str, Any]:
        """Confirm a Payment Intent with a payment method"""
        try:
            payment_intent = stripe.PaymentIntent.confirm(
                payment_intent_id,
                payment_method=payment_method
            )
            return {
                "id": payment_intent.id,
                "status": payment_intent.status,
                "client_secret": payment_intent.client_secret
            }
        except stripe.error.StripeError as e:
            raise Exception(f"Stripe error: {str(e)}")
    
    @staticmethod
    def cancel_payment_intent(payment_intent_id: str) -> Dict[str, Any]:
        """Cancel a Payment Intent"""
        # Demo mode
        if not stripe.api_key:
            return {
                "id": payment_intent_id,
                "status": "canceled"
            }
        
        try:
            payment_intent = stripe.PaymentIntent.cancel(payment_intent_id)
            return {
                "id": payment_intent.id,
                "status": payment_intent.status
            }
        except stripe.error.StripeError as e:
            raise Exception(f"Stripe error: {str(e)}")
    
    @staticmethod
    def create_refund(
        payment_intent_id: str,
        amount: Optional[Decimal] = None,
        reason: str = "requested_by_customer"
    ) -> Dict[str, Any]:
        """Create a refund for a payment"""
        try:
            refund_data = {
                "payment_intent": payment_intent_id,
                "reason": reason
            }
            
            if amount:
                refund_data["amount"] = int(amount * 100)  # Convert to cents
            
            refund = stripe.Refund.create(**refund_data)
            
            return {
                "id": refund.id,
                "status": refund.status,
                "amount": refund.amount,
                "currency": refund.currency
            }
        except stripe.error.StripeError as e:
            raise Exception(f"Stripe error: {str(e)}")
    
    @staticmethod
    def construct_webhook_event(payload: bytes, sig_header: str) -> Dict[str, Any]:
        """Construct and verify webhook event from Stripe"""
        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
            )
            return event
        except ValueError as e:
            raise Exception("Invalid payload")
        except stripe.error.SignatureVerificationError as e:
            raise Exception("Invalid signature")
    
    @staticmethod
    def get_payment_methods(customer_id: str) -> list:
        """Get payment methods for a customer"""
        try:
            payment_methods = stripe.PaymentMethod.list(
                customer=customer_id,
                type="card"
            )
            return payment_methods.data
        except stripe.error.StripeError as e:
            raise Exception(f"Stripe error: {str(e)}")
    
    @staticmethod
    def create_customer(email: str, name: str) -> Dict[str, Any]:
        """Create a Stripe customer"""
        try:
            customer = stripe.Customer.create(
                email=email,
                name=name
            )
            return {
                "id": customer.id,
                "email": customer.email,
                "name": customer.name
            }
        except stripe.error.StripeError as e:
            raise Exception(f"Stripe error: {str(e)}")


# Convenience functions for common operations
def create_payment_intent_for_order(
    amount: Decimal, 
    order_id: int, 
    user_email: str
) -> Dict[str, Any]:
    """Create payment intent for an order"""
    metadata = {
        "order_id": str(order_id),
        "user_email": user_email
    }
    
    return StripeService.create_payment_intent(
        amount=amount,
        metadata=metadata
    )


def verify_webhook_signature(payload: bytes, sig_header: str) -> Dict[str, Any]:
    """Verify webhook signature and return event"""
    return StripeService.construct_webhook_event(payload, sig_header)
