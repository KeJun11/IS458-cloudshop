import json
import os
import boto3
import stripe
import uuid
import traceback
from datetime import datetime
from decimal import Decimal

dynamodb = boto3.resource('dynamodb')
sqs = boto3.client('sqs')

# Initialize Stripe
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

def convert_floats_to_decimal(obj):
    """Convert float values to Decimal for DynamoDB compatibility"""
    if isinstance(obj, list):
        return [convert_floats_to_decimal(item) for item in obj]
    elif isinstance(obj, dict):
        return {key: convert_floats_to_decimal(value) for key, value in obj.items()}
    elif isinstance(obj, float):
        return Decimal(str(obj))
    else:
        return obj

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
    Handle order creation and order queries
    """
    try:
        orders_table_name = os.getenv("ORDERS_TABLE")
        queue_url = os.getenv("ORDER_QUEUE_URL")
        
        if not orders_table_name:
            return {
                "statusCode": 500,
                "body": json.dumps({"error": "ORDERS_TABLE environment variable not set"})
            }
        
        orders_table = dynamodb.Table(orders_table_name)
        
        http_method = event.get('httpMethod') or event.get('requestContext', {}).get('http', {}).get('method')
        path_parameters = event.get('pathParameters') or {}
        query_params = event.get('queryStringParameters') or {}
        
        if http_method == 'GET':
            # Handle GET /orders or GET /orders/{id}
            order_id = path_parameters.get('id')
            
            if order_id:
                # Get specific order
                return get_order(orders_table, order_id)
            else:
                # Get orders for user
                user_id = query_params.get('userId')
                if not user_id:
                    return {
                        "statusCode": 400,
                        "body": json.dumps({"error": "userId parameter required"})
                    }
                return get_user_orders(orders_table, user_id)
                
        elif http_method == 'POST':
            # Create order
            if not event.get('body'):
                return {
                    "statusCode": 400,
                    "body": json.dumps({"error": "Request body required"})
                }
            
            try:
                order_data = json.loads(event['body'])
            except json.JSONDecodeError:
                return {
                    "statusCode": 400,
                    "body": json.dumps({"error": "Invalid JSON in request body"})
                }
            
            return create_order(orders_table, order_data, queue_url)
        
        return {
            "statusCode": 405,
            "body": json.dumps({"error": "Method not allowed"})
        }
        
    except Exception as e:
        print(f"Error: {str(e)}")
        return {
            "statusCode": 500,
            "body": json.dumps({"error": "Internal server error"})
        }

def create_order(orders_table, order_data, queue_url):
    """Create a new order"""
    try:
        # Validate required fields
        required_fields = ['userId', 'items', 'total', 'shippingInfo']
        for field in required_fields:
            if field not in order_data:
                return {
                    "statusCode": 400,
                    "body": json.dumps({"error": f"Missing required field: {field}"})
                }
        
        # Validate shipping info
        shipping_info = order_data['shippingInfo']
        required_shipping_fields = ['name', 'email', 'address', 'city', 'zipCode']
        for field in required_shipping_fields:
            if field not in shipping_info:
                return {
                    "statusCode": 400,
                    "body": json.dumps({"error": f"Missing required shipping field: {field}"})
                }
        
        # Generate order ID and timestamp
        order_id = str(uuid.uuid4())
        created_at = datetime.utcnow().isoformat() + 'Z'
        
        # Create order object
        order = {
            'orderId': order_id,
            'userId': order_data['userId'],
            'items': order_data['items'],
            'total': order_data['total'],
            'status': 'PENDING',
            'createdAt': created_at,
            'shippingInfo': shipping_info
        }
        
        # Convert floats to Decimal for DynamoDB compatibility
        order_for_db = convert_floats_to_decimal(order)
        
        # Save order to DynamoDB
        orders_table.put_item(Item=order_for_db)
        
        # Create Stripe Checkout Session
        stripe_session_url = None
        stripe_session_id = None
        
        try:
            # Get frontend URL from environment or use default
            frontend_url = os.getenv("FRONTEND_URL", "http://localhost:5173")
            
            # Create line items from cart
            line_items = []
            for item in order_data['items']:
                product = item.get('product', {})
                line_items.append({
                    'price_data': {
                        'currency': 'usd',
                        'product_data': {
                            'name': product.get('name', 'Product'),
                            'description': product.get('description', '')[:500],  # Stripe limit
                        },
                        'unit_amount': int(product.get('price', 0) * 100),  # Convert to cents
                    },
                    'quantity': item.get('quantity', 1),
                })
            
            # Create Stripe Checkout Session
            checkout_session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=line_items,
                mode='payment',
                success_url=f"{frontend_url}/order-success?session_id={{CHECKOUT_SESSION_ID}}&order_id={order_id}",
                cancel_url=f"{frontend_url}/checkout?canceled=true",
                metadata={
                    'order_id': order_id,
                    'user_id': order_data['userId']
                },
                customer_email=shipping_info.get('email'),
            )
            
            stripe_session_url = checkout_session.url
            stripe_session_id = checkout_session.id
            
            print(f"✅ Stripe checkout session created: {stripe_session_id}")
            print(f"🎯 Payment URL: {stripe_session_url}")
            
            # Update order with Stripe session info
            orders_table.update_item(
                Key={'orderId': order_id},
                UpdateExpression='SET stripeSessionId = :sessionId, paymentStatus = :status',
                ExpressionAttributeValues={
                    ':sessionId': stripe_session_id,
                    ':status': 'PENDING_PAYMENT'
                }
            )
            
        except Exception as e:
            # Handle Stripe errors (newer Stripe SDK uses stripe._error)
            error_message = str(e)
            if 'stripe' in str(type(e)).lower() or 'authentication' in error_message.lower():
                print(f"❌ Stripe error: {error_message}")
            else:
                print(f"⚠️ Failed to create Stripe session: {error_message}")
            # Continue without Stripe - order is still created
        
        # Send order to processing queue if queue URL is provided
        if queue_url:
            try:
                sqs.send_message(
                    QueueUrl=queue_url,
                    MessageBody=json.dumps({
                        'orderId': order_id,
                        'userId': order_data['userId'],
                        'total': order_data['total'],
                        'items': order_data['items'],
                        'shippingInfo': shipping_info
                    })
                )
            except Exception as e:
                print(f"Failed to send message to queue: {str(e)}")
                # Continue without failing the order creation
        
        # Return order info with Stripe checkout URL
        response_body = {
            "orderId": order_id,
            "status": "PENDING"
        }
        
        # Add Stripe checkout URL if available
        if stripe_session_url:
            response_body["checkoutUrl"] = stripe_session_url
            response_body["sessionId"] = stripe_session_id
        
        return {
            "statusCode": 200,
            "body": json.dumps(response_body)
        }
        
    except Exception as e:
        print(f"Error creating order: {str(e)}")
        print(f"Error type: {type(e).__name__}")
        print(f"Full traceback:")
        traceback.print_exc()
        raise

def get_order(orders_table, order_id):
    """Get a specific order by ID"""
    try:
        response = orders_table.get_item(Key={'orderId': order_id})
        
        if 'Item' not in response:
            return {
                "statusCode": 404,
                "body": json.dumps({"error": "Order not found"})
            }
        
        order = response['Item']
        # Convert DynamoDB Decimal types to float for JSON serialization
        order = convert_decimals_to_float(order)
        order['id'] = order.pop('orderId')  # Rename for frontend compatibility
        
        return {
            "statusCode": 200,
            "body": json.dumps(order)
        }
        
    except Exception as e:
        print(f"Error getting order: {str(e)}")
        raise

def get_user_orders(orders_table, user_id):
    """Get all orders for a user"""
    try:
        response = orders_table.query(
            IndexName='userId-index',
            KeyConditionExpression='userId = :userId',
            ExpressionAttributeValues={':userId': user_id}
        )
        
        orders = response['Items']
        
        # Convert DynamoDB Decimal types to float and rename fields
        for i, order in enumerate(orders):
            order = convert_decimals_to_float(order)
            order['id'] = order.pop('orderId')
            orders[i] = order  # Update the list with the modified order
        
        return {
            "statusCode": 200,
            "body": json.dumps(orders)
        }
        
    except Exception as e:
        print(f"Error getting user orders: {str(e)}")
        raise
