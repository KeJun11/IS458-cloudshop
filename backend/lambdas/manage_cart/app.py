import json
import os
import boto3
from decimal import Decimal

dynamodb = boto3.resource('dynamodb')

def lambda_handler(event, context):
    """
    Handle cart operations: GET /cart, POST /cart, PUT /cart, DELETE /cart
    """
    try:
        carts_table_name = os.getenv("CARTS_TABLE")
        products_table_name = os.getenv("PRODUCTS_TABLE")
        
        if not carts_table_name or not products_table_name:
            return {
                "statusCode": 500,
                "body": json.dumps({"error": "Required environment variables not set"})
            }
        
        carts_table = dynamodb.Table(carts_table_name)
        products_table = dynamodb.Table(products_table_name)
        
        http_method = event.get('httpMethod') or event.get('requestContext', {}).get('http', {}).get('method')
        query_params = event.get('queryStringParameters') or {}
        
        if http_method == 'GET':
            # Get cart
            user_id = query_params.get('userId')
            if not user_id:
                return {
                    "statusCode": 400,
                    "body": json.dumps({"error": "userId parameter required"})
                }
            
            return get_cart(carts_table, products_table, user_id)
            
        elif http_method in ['POST', 'PUT', 'DELETE']:
            # Parse request body
            if not event.get('body'):
                return {
                    "statusCode": 400,
                    "body": json.dumps({"error": "Request body required"})
                }
            
            try:
                body = json.loads(event['body'])
            except json.JSONDecodeError:
                return {
                    "statusCode": 400,
                    "body": json.dumps({"error": "Invalid JSON in request body"})
                }
            
            user_id = body.get('userId')
            product_id = body.get('productId')
            
            if not user_id or not product_id:
                return {
                    "statusCode": 400,
                    "body": json.dumps({"error": "userId and productId required"})
                }
            
            if http_method == 'POST':
                # Add to cart
                quantity = body.get('quantity', 1)
                return add_to_cart(carts_table, products_table, user_id, product_id, quantity)
                
            elif http_method == 'PUT':
                # Update cart item
                quantity = body.get('quantity', 1)
                return update_cart_item(carts_table, products_table, user_id, product_id, quantity)
                
            elif http_method == 'DELETE':
                # Remove from cart
                return remove_from_cart(carts_table, products_table, user_id, product_id)
        
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

def get_cart(carts_table, products_table, user_id):
    """Get user's cart with product details"""
    try:
        response = carts_table.get_item(Key={'userId': user_id})
        
        if 'Item' not in response:
            # Return empty cart
            return {
                "statusCode": 200,
                "body": json.dumps({
                    "userId": user_id,
                    "items": [],
                    "total": 0
                })
            }
        
        cart = response['Item']
        items = cart.get('items', [])
        
        # Enrich items with product details
        enriched_items = []
        total = 0
        
        for item in items:
            product_response = products_table.get_item(Key={'productId': item['productId']})
            if 'Item' in product_response:
                product = product_response['Item']
                product['id'] = product.pop('productId')
                product['price'] = float(product['price'])
                product['stock'] = int(product['stock'])
                
                enriched_item = {
                    "productId": item['productId'],
                    "quantity": int(item['quantity']),
                    "product": product
                }
                enriched_items.append(enriched_item)
                total += product['price'] * int(item['quantity'])
        
        return {
            "statusCode": 200,
            "body": json.dumps({
                "userId": user_id,
                "items": enriched_items,
                "total": round(total, 2)
            })
        }
        
    except Exception as e:
        print(f"Error getting cart: {str(e)}")
        raise

def add_to_cart(carts_table, products_table, user_id, product_id, quantity):
    """Add item to cart"""
    try:
        # Verify product exists
        product_response = products_table.get_item(Key={'productId': product_id})
        if 'Item' not in product_response:
            return {
                "statusCode": 404,
                "body": json.dumps({"error": "Product not found"})
            }
        
        # Get current cart
        response = carts_table.get_item(Key={'userId': user_id})
        
        if 'Item' in response:
            cart = response['Item']
            items = cart.get('items', [])
        else:
            items = []
        
        # Check if item already exists in cart
        existing_item = None
        for item in items:
            if item['productId'] == product_id:
                existing_item = item
                break
        
        if existing_item:
            # Update quantity
            existing_item['quantity'] = int(existing_item['quantity']) + quantity
        else:
            # Add new item
            items.append({
                'productId': product_id,
                'quantity': quantity
            })
        
        # Update cart in DynamoDB
        carts_table.put_item(Item={
            'userId': user_id,
            'items': items
        })
        
        return get_cart(carts_table, products_table, user_id)
        
    except Exception as e:
        print(f"Error adding to cart: {str(e)}")
        raise

def update_cart_item(carts_table, products_table, user_id, product_id, quantity):
    """Update cart item quantity"""
    try:
        response = carts_table.get_item(Key={'userId': user_id})
        
        if 'Item' not in response:
            return {
                "statusCode": 404,
                "body": json.dumps({"error": "Cart not found"})
            }
        
        cart = response['Item']
        items = cart.get('items', [])
        
        # Find and update item
        for item in items:
            if item['productId'] == product_id:
                if quantity <= 0:
                    items.remove(item)
                else:
                    item['quantity'] = quantity
                break
        else:
            return {
                "statusCode": 404,
                "body": json.dumps({"error": "Item not found in cart"})
            }
        
        # Update cart
        carts_table.put_item(Item={
            'userId': user_id,
            'items': items
        })
        
        return get_cart(carts_table, products_table, user_id)
        
    except Exception as e:
        print(f"Error updating cart item: {str(e)}")
        raise

def remove_from_cart(carts_table, products_table, user_id, product_id):
    """Remove item from cart"""
    try:
        response = carts_table.get_item(Key={'userId': user_id})
        
        if 'Item' not in response:
            return {
                "statusCode": 404,
                "body": json.dumps({"error": "Cart not found"})
            }
        
        cart = response['Item']
        items = cart.get('items', [])
        
        # Remove item
        items = [item for item in items if item['productId'] != product_id]
        
        # Update cart
        carts_table.put_item(Item={
            'userId': user_id,
            'items': items
        })
        
        return get_cart(carts_table, products_table, user_id)
        
    except Exception as e:
        print(f"Error removing from cart: {str(e)}")
        raise
