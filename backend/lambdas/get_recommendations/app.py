import json
import os
import boto3
from collections import Counter

dynamodb = boto3.resource('dynamodb')

def lambda_handler(event, context):
    """
    Generate product recommendations based on user interactions
    """
    try:
        interactions_table_name = os.getenv("INTERACTIONS_TABLE")
        products_table_name = os.getenv("PRODUCTS_TABLE")
        category_index = os.getenv("PRODUCT_TYPE_GSI", "category-index")
        
        if not interactions_table_name or not products_table_name:
            return {
                "statusCode": 500,
                "body": json.dumps({"error": "Required environment variables not set"})
            }
        
        interactions_table = dynamodb.Table(interactions_table_name)
        products_table = dynamodb.Table(products_table_name)
        
        query_params = event.get('queryStringParameters') or {}
        user_id = query_params.get('userId')
        
        if not user_id:
            return {
                "statusCode": 400,
                "body": json.dumps({"error": "userId parameter required"})
            }
        
        # Get user's interaction history
        response = interactions_table.query(
            KeyConditionExpression='userId = :userId',
            ExpressionAttributeValues={':userId': user_id}
        )
        
        interactions = response['Items']
        
        if not interactions:
            # No interaction history, return empty array
            # Frontend will show "Start browsing to get recommendations" message
            return {
                "statusCode": 200,
                "body": json.dumps([])
            }
        
        # Analyze user preferences based on interactions
        # Use MOST RECENT category (simple priority: last viewed category wins)
        viewed_products = set()
        
        # Sort interactions by timestamp (most recent first)
        sorted_interactions = sorted(
            interactions, 
            key=lambda x: x.get('timestamp', ''), 
            reverse=True
        )
        
        # Get the most recent category
        most_recent_category = sorted_interactions[0]['category'] if sorted_interactions else None
        
        # Collect all viewed products
        for interaction in interactions:
            viewed_products.add(interaction['productId'])
        
        # Get products from the most recent category, excluding already viewed
        recommendations = []
        
        if most_recent_category:
            try:
                response = products_table.query(
                    IndexName=category_index,
                    KeyConditionExpression='category = :category',
                    ExpressionAttributeValues={':category': most_recent_category},
                    Limit=10
                )
                
                category_products = response['Items']
                
                for product in category_products:
                    if product['productId'] not in viewed_products and len(recommendations) < 10:
                        # Convert DynamoDB types and rename fields
                        product['price'] = float(product['price'])
                        product['stock'] = int(product['stock'])
                        product['id'] = product.pop('productId')
                        recommendations.append(product)
                        
            except Exception as e:
                print(f"Error querying category {most_recent_category}: {str(e)}")
        
        # Return recommendations (don't fill with random products if not enough)
        # This allows frontend to show "start browsing" message when empty
        return {
            "statusCode": 200,
            "body": json.dumps(recommendations)
        }
        
    except Exception as e:
        print(f"Error: {str(e)}")
        return {
            "statusCode": 500,
            "body": json.dumps({"error": "Internal server error"})
        }

def get_random_products(products_table, exclude=None, limit=10):
    """Get random products for users with no interaction history"""
    try:
        if exclude is None:
            exclude = set()
            
        response = products_table.scan(Limit=20)  # Get more than needed to filter
        products = response['Items']
        
        recommendations = []
        for product in products:
            if product['productId'] not in exclude and len(recommendations) < limit:
                product['price'] = float(product['price'])
                product['stock'] = int(product['stock'])
                product['id'] = product.pop('productId')
                recommendations.append(product)
        
        return {
            "statusCode": 200,
            "body": json.dumps(recommendations)
        }
        
    except Exception as e:
        print(f"Error getting random products: {str(e)}")
        return {
            "statusCode": 500,
            "body": json.dumps({"error": "Failed to get recommendations"})
        }
