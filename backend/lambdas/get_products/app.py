import json
import os
import boto3
from boto3.dynamodb.conditions import Key

dynamodb = boto3.resource('dynamodb')

def lambda_handler(event, context):
    """
    Handle GET /products and GET /products/{id} requests
    """
    try:
        table_name = os.getenv("PRODUCTS_TABLE")
        if not table_name:
            return {
                "statusCode": 500,
                "body": json.dumps({"error": "PRODUCTS_TABLE environment variable not set"})
            }
        
        table = dynamodb.Table(table_name)
        
        # Check if this is a request for a specific product
        path_parameters = event.get('pathParameters') or {}
        product_id = path_parameters.get('id')
        
        if product_id:
            # Get single product
            response = table.get_item(Key={'productId': product_id})
            
            if 'Item' not in response:
                return {
                    "statusCode": 404,
                    "body": json.dumps({"error": "Product not found"})
                }
            
            product = response['Item']
            # Convert DynamoDB number types to float
            product['price'] = float(product['price'])
            product['stock'] = int(product['stock'])
            # Rename productId to id for frontend compatibility
            product['id'] = product.pop('productId')
            
            return {
                "statusCode": 200,
                "body": json.dumps(product)
            }
        else:
            # Get all products
            response = table.scan()
            products = response['Items']
            
            # Convert DynamoDB types and rename fields for frontend compatibility
            for product in products:
                product['price'] = float(product['price'])
                product['stock'] = int(product['stock'])
                product['id'] = product.pop('productId')
            
            return {
                "statusCode": 200,
                "body": json.dumps(products)
            }
            
    except Exception as e:
        print(f"Error: {str(e)}")
        return {
            "statusCode": 500,
            "body": json.dumps({"error": "Internal server error"})
        }
