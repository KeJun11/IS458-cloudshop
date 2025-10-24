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
            # No interaction history, return random products
            return get_random_products(products_table)
        
        # Analyze user preferences based on interactions
        categories = []
        viewed_products = set()
        
        for interaction in interactions:
            categories.append(interaction['category'])
            viewed_products.add(interaction['productId'])
        
        # Find most common categories
        category_counts = Counter(categories)
        top_categories = [cat for cat, count in category_counts.most_common(3)]
        
        # Get products from preferred categories, excluding already viewed
        recommendations = []
        
        for category in top_categories:
            try:
                response = products_table.query(
                    IndexName=category_index,
                    KeyConditionExpression='category = :category',
                    ExpressionAttributeValues={':category': category},
                    Limit=5
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
                print(f"Error querying category {category}: {str(e)}")
                continue
        
        # If we don't have enough recommendations, fill with random products
        if len(recommendations) < 5:
            random_products = get_random_products(products_table, exclude=viewed_products)
            if random_products['statusCode'] == 200:
                random_items = json.loads(random_products['body'])
                for product in random_items:
                    if len(recommendations) < 10:
                        recommendations.append(product)
        
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
