import json
import os


def lambda_handler(event, context):
    """
    Placeholder handler for processing order messages from SQS.
    Extend with payment simulation, SES, and invoice persistence.
    """
    body = {
        "message": "process_order handler placeholder",
        "ordersTable": os.getenv("ORDERS_TABLE", "undefined"),
        "invoiceBucket": os.getenv("INVOICE_BUCKET", "undefined"),
        "records": event.get("Records", []),
    }
    return {"statusCode": 200, "body": json.dumps(body)}
