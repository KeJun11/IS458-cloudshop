import json
import os


def lambda_handler(event, context):
    """
    Placeholder handler that returns the configured DynamoDB table name.
    Replace with business logic that queries the products catalog.
    """
    body = {
        "message": "get_products handler placeholder",
        "productsTable": os.getenv("PRODUCTS_TABLE", "undefined"),
    }
    return {"statusCode": 200, "body": json.dumps(body)}
