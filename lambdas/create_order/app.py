import json
import os


def lambda_handler(event, context):
    """
    Placeholder handler for creating orders.
    Add integration with DynamoDB, SQS, and S3 as needed.
    """
    body = {
        "message": "create_order handler placeholder",
        "ordersTable": os.getenv("ORDERS_TABLE", "undefined"),
        "queueUrl": os.getenv("ORDER_QUEUE_URL", "undefined"),
        "invoiceBucket": os.getenv("INVOICE_BUCKET", "undefined"),
        "requestBody": event.get("body"),
    }
    return {"statusCode": 200, "body": json.dumps(body)}
