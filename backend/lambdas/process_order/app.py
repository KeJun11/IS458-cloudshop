import json
import os
import boto3
from datetime import datetime
from decimal import Decimal

# Initialize AWS clients
dynamodb = boto3.resource('dynamodb')
ses = boto3.client('ses')
s3 = boto3.client('s3')

def convert_decimals_to_float(obj):
    """Convert Decimal values back to float for JSON serialization"""
    if isinstance(obj, list):
        return [convert_decimals_to_float(item) for item in obj]
    elif isinstance(obj, dict):
        return {key: convert_decimals_to_float(value) for key, value in obj.items()}
    elif isinstance(obj, Decimal):
        return float(obj)
    else:
        return obj

def lambda_handler(event, context):
    """
    Process order messages from SQS - Phase 4 Implementation:
    1. Simulate payment gateway call
    2. Send confirmation email via SES
    3. Update order status to PROCESSED
    4. Generate and store invoice in S3
    5. Clear user's cart (optional)
    """
    
    print(f"Processing {len(event.get('Records', []))} SQS messages")
    
    # Process each SQS message
    for record in event.get('Records', []):
        try:
            # Parse the SQS message body
            message_body = json.loads(record['body'])
            print(f"Processing order: {message_body}")
            
            # Extract order information
            order_id = message_body.get('orderId')
            user_id = message_body.get('userId')
            total = message_body.get('total')
            items = message_body.get('items', [])
            shipping_info = message_body.get('shippingInfo', {})
            
            if not order_id:
                print("Error: No orderId in message")
                continue
            
            # Process the order
            success = process_single_order(order_id, user_id, total, items, shipping_info)
            
            if success:
                print(f"Successfully processed order {order_id}")
            else:
                print(f"Failed to process order {order_id}")
                
        except Exception as e:
            print(f"Error processing SQS record: {str(e)}")
            # In production, you might want to send failed messages to a DLQ
            continue
    
    return {"statusCode": 200, "body": json.dumps({"message": "Orders processed"})}

def process_single_order(order_id, user_id, total, items, shipping_info):
    """Process a single order through all phases"""
    try:
        # Phase 4.1: Simulate payment gateway call
        payment_success = simulate_payment_gateway(order_id, total)
        if not payment_success:
            print(f"Payment failed for order {order_id}")
            update_order_status(order_id, "PAYMENT_FAILED")
            return False
        
        # Phase 4.2: Send confirmation email
        email_success = send_confirmation_email(order_id, shipping_info, items, total)
        if not email_success:
            print(f"Email sending failed for order {order_id}")
            # Continue processing even if email fails
        
        # Phase 4.3: Update order status to PROCESSED
        update_success = update_order_status(order_id, "PROCESSED")
        if not update_success:
            print(f"Failed to update order status for {order_id}")
            return False
        
        # Phase 4.4: Generate and store invoice in S3
        invoice_success = generate_and_store_invoice(order_id, user_id, items, total, shipping_info)
        if not invoice_success:
            print(f"Invoice generation failed for order {order_id}")
            # Continue processing even if invoice fails
        
        # Phase 4.5: Clear user's cart (optional)
        clear_cart_success = clear_user_cart(user_id)
        if not clear_cart_success:
            print(f"Failed to clear cart for user {user_id}")
            # Continue processing even if cart clearing fails
        
        return True
        
    except Exception as e:
        print(f"Error processing order {order_id}: {str(e)}")
        return False

def simulate_payment_gateway(order_id, total):
    """Simulate a payment gateway call"""
    try:
        print(f"Simulating payment gateway call for order {order_id}")
        print(f"Processing payment of ${total}")
        
        # Simulate payment processing time and logic
        # In a real system, this would call Stripe, PayPal, etc.
        
        # For demo purposes, assume payment always succeeds
        # You could add logic to randomly fail some payments for testing
        
        print(f"Payment successful for order {order_id}")
        return True
        
    except Exception as e:
        print(f"Payment gateway error for order {order_id}: {str(e)}")
        return False

def send_confirmation_email(order_id, shipping_info, items, total):
    """Send order confirmation email via SES"""
    try:
        sender_email = os.getenv("SES_SENDER_EMAIL")
        if not sender_email:
            print("No SES sender email configured")
            return False
        
        customer_email = shipping_info.get('email')
        if not customer_email:
            print("No customer email provided")
            return False
        
        # Check if the customer email is verified in SES
        # For demo purposes, we'll check if it's verified, and if not, use the sender email
        original_customer_email = customer_email
        try:
            # Try to get the verification status of the customer email
            response = ses.get_identity_verification_attributes(Identities=[customer_email])
            verification_status = response.get('VerificationAttributes', {}).get(customer_email, {}).get('VerificationStatus')
            
            if verification_status != 'Success':
                print(f"Customer email {customer_email} is not verified in SES (status: {verification_status})")
                customer_email = sender_email
                print(f"Using verified sender email {sender_email} instead")
            else:
                print(f"Customer email {customer_email} is verified in SES")
                
        except Exception as e:
            print(f"Could not check verification status for {customer_email}: {str(e)}")
            print(f"Falling back to verified sender email {sender_email}")
            customer_email = sender_email
        
        customer_name = shipping_info.get('name', 'Valued Customer')
        
        # Create email content
        subject = f"Order Confirmation - Order #{order_id[:8]}"
        
        # Create items list for email
        items_text = ""
        for item in items:
            product_name = item.get('product', {}).get('name', 'Unknown Product')
            quantity = item.get('quantity', 1)
            price = item.get('product', {}).get('price', 0)
            items_text += f"- {product_name} (Qty: {quantity}) - ${price:.2f}\n"
        
        # Email body
        email_note = ""
        if customer_email != original_customer_email:
            email_note = f"\n\nNote: This confirmation was sent to {customer_email} because {original_customer_email} is not verified in our email system.\n"
        
        body_text = f"""
Dear {customer_name},

Thank you for your order! We're excited to confirm that we've received your order and it's being processed.

Order Details:
Order ID: {order_id}
Order Date: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC

Items Ordered:
{items_text}

Total: ${total:.2f}

Shipping Address:
{shipping_info.get('name', '')}
{shipping_info.get('address', '')}
{shipping_info.get('city', '')}, {shipping_info.get('zipCode', '')}

Your order is now being processed and you'll receive another email when it ships.

Thank you for shopping with us!{email_note}

Best regards,
CloudShop Team
        """
        
        body_html = f"""
<html>
<head></head>
<body>
    <h2>Order Confirmation</h2>
    <p>Dear {customer_name},</p>
    
    <p>Thank you for your order! We're excited to confirm that we've received your order and it's being processed.</p>
    
    <h3>Order Details:</h3>
    <ul>
        <li><strong>Order ID:</strong> {order_id}</li>
        <li><strong>Order Date:</strong> {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC</li>
    </ul>
    
    <h3>Items Ordered:</h3>
    <ul>
        {"".join([f"<li>{item.get('product', {}).get('name', 'Unknown Product')} (Qty: {item.get('quantity', 1)}) - ${item.get('product', {}).get('price', 0):.2f}</li>" for item in items])}
    </ul>
    
    <h3>Total: ${total:.2f}</h3>
    
    <h3>Shipping Address:</h3>
    <p>
        {shipping_info.get('name', '')}<br>
        {shipping_info.get('address', '')}<br>
        {shipping_info.get('city', '')}, {shipping_info.get('zipCode', '')}
    </p>
    
    <p>Your order is now being processed and you'll receive another email when it ships.</p>
    
    <p>Thank you for shopping with us!</p>
    
    {"<p><em>Note: This confirmation was sent to " + customer_email + " because " + original_customer_email + " is not verified in our email system.</em></p>" if customer_email != original_customer_email else ""}
    
    <p>Best regards,<br>CloudShop Team</p>
</body>
</html>
        """
        
        # Send email via SES
        response = ses.send_email(
            Source=sender_email,
            Destination={'ToAddresses': [customer_email]},
            Message={
                'Subject': {'Data': subject, 'Charset': 'UTF-8'},
                'Body': {
                    'Text': {'Data': body_text, 'Charset': 'UTF-8'},
                    'Html': {'Data': body_html, 'Charset': 'UTF-8'}
                }
            }
        )
        
        print(f"Confirmation email sent to {customer_email} (MessageId: {response['MessageId']})")
        return True
        
    except Exception as e:
        print(f"Email sending failed: {str(e)}")
        return False

def update_order_status(order_id, new_status):
    """Update order status in DynamoDB"""
    try:
        orders_table_name = os.getenv("ORDERS_TABLE")
        if not orders_table_name:
            print("ORDERS_TABLE environment variable not set")
            return False
        
        orders_table = dynamodb.Table(orders_table_name)
        
        # Update the order status
        response = orders_table.update_item(
            Key={'orderId': order_id},
            UpdateExpression='SET #status = :status, #processedAt = :processedAt',
            ExpressionAttributeNames={
                '#status': 'status',
                '#processedAt': 'processedAt'
            },
            ExpressionAttributeValues={
                ':status': new_status,
                ':processedAt': datetime.utcnow().isoformat() + 'Z'
            },
            ReturnValues='UPDATED_NEW'
        )
        
        print(f"Order {order_id} status updated to {new_status}")
        return True
        
    except Exception as e:
        print(f"Failed to update order status: {str(e)}")
        return False

def generate_and_store_invoice(order_id, user_id, items, total, shipping_info):
    """Generate invoice and store in S3"""
    try:
        invoice_bucket = os.getenv("INVOICE_BUCKET")
        if not invoice_bucket:
            print("INVOICE_BUCKET environment variable not set")
            return False
        
        # Generate invoice content
        invoice_date = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
        
        invoice_content = f"""
CLOUDSHOP INVOICE
================

Invoice Date: {invoice_date} UTC
Order ID: {order_id}
Customer ID: {user_id}

BILLING INFORMATION:
{shipping_info.get('name', '')}
{shipping_info.get('email', '')}
{shipping_info.get('address', '')}
{shipping_info.get('city', '')}, {shipping_info.get('zipCode', '')}

ITEMS:
------
"""
        
        subtotal = 0
        for item in items:
            product_name = item.get('product', {}).get('name', 'Unknown Product')
            quantity = item.get('quantity', 1)
            price = item.get('product', {}).get('price', 0)
            line_total = quantity * price
            subtotal += line_total
            
            invoice_content += f"{product_name:<30} Qty: {quantity:>3} @ ${price:>8.2f} = ${line_total:>8.2f}\n"
        
        invoice_content += f"""
------
Subtotal: ${subtotal:>8.2f}
Tax:      ${0:>8.2f}
------
TOTAL:    ${total:>8.2f}

Thank you for your business!

This is an automated invoice generated by CloudShop.
For questions, please contact support@cloudshop.com
        """
        
        # Store invoice in S3
        invoice_key = f"invoices/{datetime.utcnow().strftime('%Y/%m/%d')}/{order_id}.txt"
        
        s3.put_object(
            Bucket=invoice_bucket,
            Key=invoice_key,
            Body=invoice_content.encode('utf-8'),
            ContentType='text/plain',
            Metadata={
                'orderId': order_id,
                'userId': user_id,
                'total': str(total),
                'generatedAt': invoice_date
            }
        )
        
        print(f"Invoice generated and stored: s3://{invoice_bucket}/{invoice_key}")
        return True
        
    except Exception as e:
        print(f"Invoice generation failed: {str(e)}")
        return False

def clear_user_cart(user_id):
    """Clear user's cart after successful order processing"""
    try:
        carts_table_name = os.getenv("CARTS_TABLE")
        if not carts_table_name:
            print("CARTS_TABLE environment variable not set")
            return False
        
        carts_table = dynamodb.Table(carts_table_name)
        
        # Clear the cart by setting items to empty array
        # Note: 'items' is a reserved keyword in DynamoDB, so we use ExpressionAttributeNames
        carts_table.update_item(
            Key={'userId': user_id},
            UpdateExpression='SET #items = :empty_items',
            ExpressionAttributeNames={'#items': 'items'},
            ExpressionAttributeValues={':empty_items': []},
            ReturnValues='UPDATED_NEW'
        )
        
        print(f"Cart cleared for user {user_id}")
        return True
        
    except Exception as e:
        print(f"Failed to clear cart: {str(e)}")
        return False
