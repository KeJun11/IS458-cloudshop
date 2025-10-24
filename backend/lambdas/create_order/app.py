import json
import os
import boto3
import uuid
from datetime import datetime
from decimal import Decimal

dynamodb = boto3.resource('dynamodb')
sqs = boto3.client('sqs')

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
        
        return {
            "statusCode": 200,
            "body": json.dumps({
                "orderId": order_id,
                "status": "PENDING"
            })
        }
        
    except Exception as e:
        print(f"Error creating order: {str(e)}")
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
