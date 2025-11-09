import json
import os
import boto3
import stripe
from datetime import datetime

# Initialize AWS clients
dynamodb = boto3.resource('dynamodb')

# Initialize Stripe
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

def lambda_handler(event, context):
    """
    Handle Stripe webhook events
    This Lambda is called by Stripe when payment events occur
    """
    
    print(f"📥 WEBHOOK: Received Stripe webhook event")
    
    try:
        # Get the webhook secret for signature verification
        webhook_secret = os.getenv("STRIPE_WEBHOOK_SECRET")
        
        # Get the Stripe signature from headers
        sig_header = event.get('headers', {}).get('stripe-signature') or \
                     event.get('headers', {}).get('Stripe-Signature')
        
        if not sig_header:
            print("❌ WEBHOOK: No Stripe signature found in headers")
            return {
                "statusCode": 400,
                "body": json.dumps({"error": "No signature header"})
            }
        
        # Get the raw body
        payload = event.get('body', '')
        
        # Verify webhook signature (if secret is configured)
        if webhook_secret:
            try:
                stripe_event = stripe.Webhook.construct_event(
                    payload, sig_header, webhook_secret
                )
                print(f"✅ WEBHOOK: Signature verified successfully")
            except ValueError as e:
                print(f"❌ WEBHOOK: Invalid payload: {str(e)}")
                return {"statusCode": 400, "body": json.dumps({"error": "Invalid payload"})}
            except stripe.error.SignatureVerificationError as e:
                print(f"❌ WEBHOOK: Invalid signature: {str(e)}")
                return {"statusCode": 400, "body": json.dumps({"error": "Invalid signature"})}
        else:
            # If no webhook secret, parse the body directly (not recommended for production)
            print("⚠️ WEBHOOK: No webhook secret configured - skipping signature verification")
            stripe_event = json.loads(payload)
        
        # Handle the event
        event_type = stripe_event.get('type')
        print(f"📨 WEBHOOK: Event type: {event_type}")
        
        if event_type == 'checkout.session.completed':
            handle_checkout_session_completed(stripe_event)
        elif event_type == 'payment_intent.succeeded':
            handle_payment_succeeded(stripe_event)
        elif event_type == 'payment_intent.payment_failed':
            handle_payment_failed(stripe_event)
        else:
            print(f"ℹ️ WEBHOOK: Unhandled event type: {event_type}")
        
        return {
            "statusCode": 200,
            "body": json.dumps({"received": True})
        }
        
    except Exception as e:
        print(f"❌ WEBHOOK ERROR: {str(e)}")
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        }

def handle_checkout_session_completed(stripe_event):
    """Handle successful checkout session completion"""
    try:
        session = stripe_event['data']['object']
        order_id = session.get('metadata', {}).get('order_id')
        
        if not order_id:
            print("⚠️ WEBHOOK: No order_id in session metadata")
            return
        
        print(f"")
        print(f"{'='*80}")
        print(f"🎉 PAYMENT SUCCESS!")
        print(f"🎉 Order ID: {order_id}")
        print(f"🎉 Session ID: {session['id']}")
        print(f"🎉 Amount: ${session['amount_total'] / 100:.2f}")
        print(f"🎉 Payment Status: {session['payment_status']}")
        print(f"{'='*80}")
        print(f"")
        
        # Update order status to PAYMENT_CONFIRMED
        update_order_payment_status(order_id, "PAYMENT_CONFIRMED", session['id'])
        
        # Update order status to PROCESSED (since payment is confirmed)
        update_order_status(order_id, "PROCESSED")
        
        print(f"✅ WEBHOOK: Order {order_id} marked as PROCESSED")
        
    except Exception as e:
        print(f"❌ WEBHOOK: Error handling checkout session: {str(e)}")

def handle_payment_succeeded(stripe_event):
    """Handle successful payment intent"""
    try:
        payment_intent = stripe_event['data']['object']
        print(f"✅ WEBHOOK: Payment intent succeeded: {payment_intent['id']}")
        
        # You can add additional handling here if needed
        
    except Exception as e:
        print(f"❌ WEBHOOK: Error handling payment success: {str(e)}")

def handle_payment_failed(stripe_event):
    """Handle failed payment"""
    try:
        payment_intent = stripe_event['data']['object']
        order_id = payment_intent.get('metadata', {}).get('order_id')
        
        print(f"")
        print(f"{'='*80}")
        print(f"❌ PAYMENT FAILED!")
        print(f"❌ Payment Intent ID: {payment_intent['id']}")
        if order_id:
            print(f"❌ Order ID: {order_id}")
            update_order_payment_status(order_id, "PAYMENT_FAILED", payment_intent['id'])
            update_order_status(order_id, "PAYMENT_FAILED")
        print(f"{'='*80}")
        print(f"")
        
    except Exception as e:
        print(f"❌ WEBHOOK: Error handling payment failure: {str(e)}")

def update_order_payment_status(order_id, payment_status, payment_id):
    """Update order payment status in DynamoDB"""
    try:
        orders_table_name = os.getenv("ORDERS_TABLE")
        if not orders_table_name:
            print("ORDERS_TABLE environment variable not set")
            return False
        
        orders_table = dynamodb.Table(orders_table_name)
        
        orders_table.update_item(
            Key={'orderId': order_id},
            UpdateExpression='SET paymentStatus = :status, stripePaymentId = :paymentId, paymentConfirmedAt = :confirmedAt',
            ExpressionAttributeValues={
                ':status': payment_status,
                ':paymentId': payment_id,
                ':confirmedAt': datetime.utcnow().isoformat() + 'Z'
            }
        )
        
        print(f"✅ Order {order_id} payment status updated to {payment_status}")
        return True
        
    except Exception as e:
        print(f"❌ Failed to update order payment status: {str(e)}")
        return False

def update_order_status(order_id, new_status):
    """Update order status in DynamoDB"""
    try:
        orders_table_name = os.getenv("ORDERS_TABLE")
        if not orders_table_name:
            print("ORDERS_TABLE environment variable not set")
            return False
        
        orders_table = dynamodb.Table(orders_table_name)
        
        orders_table.update_item(
            Key={'orderId': order_id},
            UpdateExpression='SET #status = :status, #processedAt = :processedAt',
            ExpressionAttributeNames={
                '#status': 'status',
                '#processedAt': 'processedAt'
            },
            ExpressionAttributeValues={
                ':status': new_status,
                ':processedAt': datetime.utcnow().isoformat() + 'Z'
            }
        )
        
        print(f"✅ Order {order_id} status updated to {new_status}")
        return True
        
    except Exception as e:
        print(f"❌ Failed to update order status: {str(e)}")
        return False
