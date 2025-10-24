import json
import os
import boto3
from datetime import datetime

dynamodb = boto3.resource('dynamodb')

def lambda_handler(event, context):
    """
    Handle user interaction event tracking
    """
    try:
        interactions_table_name = os.getenv("INTERACTIONS_TABLE")
        
        if not interactions_table_name:
            return {
                "statusCode": 500,
                "body": json.dumps({"error": "INTERACTIONS_TABLE environment variable not set"})
            }
        
        interactions_table = dynamodb.Table(interactions_table_name)
        
        # Parse request body
        if not event.get('body'):
            return {
                "statusCode": 400,
                "body": json.dumps({"error": "Request body required"})
            }
        
        try:
            interaction_data = json.loads(event['body'])
        except json.JSONDecodeError:
            return {
                "statusCode": 400,
                "body": json.dumps({"error": "Invalid JSON in request body"})
            }
        
        # Validate required fields
        required_fields = ['userId', 'productId', 'eventType', 'productType']
        for field in required_fields:
            if field not in interaction_data:
                return {
                    "statusCode": 400,
                    "body": json.dumps({"error": f"Missing required field: {field}"})
                }
        
        # Validate event type
        valid_event_types = ['product-view', 'add-to-cart', 'purchase']
        if interaction_data['eventType'] not in valid_event_types:
            return {
                "statusCode": 400,
                "body": json.dumps({"error": f"Invalid eventType. Must be one of: {valid_event_types}"})
            }
        
        # Add timestamp if not provided
        timestamp = interaction_data.get('timestamp', datetime.utcnow().isoformat() + 'Z')
        
        # Create interaction record
        interaction = {
            'userId': interaction_data['userId'],
            'productId': interaction_data['productId'],
            'eventType': interaction_data['eventType'],
            'category': interaction_data['productType'],  # Map productType to category
            'timestamp': timestamp
        }
        
        # Save interaction to DynamoDB
        interactions_table.put_item(Item=interaction)
        
        return {
            "statusCode": 200,
            "body": json.dumps({"message": "Event tracked successfully"})
        }
        
    except Exception as e:
        print(f"Error: {str(e)}")
        return {
            "statusCode": 500,
            "body": json.dumps({"error": "Internal server error"})
        }
