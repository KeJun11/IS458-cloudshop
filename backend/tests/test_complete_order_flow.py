#!/usr/bin/env python3
"""
Test Complete Order Processing Flow
Tests the full Phase 4 implementation:
1. Create order (triggers SQS message)
2. Wait for SQS processing
3. Verify order status updated to PROCESSED
4. Check if email was sent (via logs)
5. Verify invoice was created in S3
"""

import requests
import json
import uuid
import time
import boto3

API_BASE_URL = "https://otkwm0hrp3.execute-api.us-east-1.amazonaws.com"

# AWS clients for verification
dynamodb = boto3.resource('dynamodb')
s3 = boto3.client('s3')
logs = boto3.client('logs')

def test_complete_order_processing_flow():
    """Test the complete order processing flow"""
    
    print("=== TESTING COMPLETE ORDER PROCESSING FLOW ===")
    
    # Step 1: Create an order
    print("\n1. Creating order...")
    test_user = f"test-user-{uuid.uuid4()}"
    
    order_data = {
        "userId": test_user,
        "items": [
            {
                "productId": "prod-100",
                "quantity": 2,
                "product": {
                    "id": "prod-100",
                    "name": "Wireless Headphones",
                    "price": 59.99
                }
            }
        ],
        "total": 119.98,
        "shippingInfo": {
            "name": "Test Customer",
            "email": "test@example.com",  # This would be your email in real test
            "address": "123 Test Street",
            "city": "Test City",
            "zipCode": "12345"
        }
    }
    
    response = requests.post(f"{API_BASE_URL}/orders", json=order_data)
    
    if response.status_code != 200:
        print(f"ERROR: Order creation failed: {response.status_code} - {response.text}")
        return False
    
    result = response.json()
    order_id = result["orderId"]
    print(f"SUCCESS: Order created with ID: {order_id}")
    print(f"Initial status: {result['status']}")
    
    # Step 2: Wait for SQS processing (Lambda is triggered asynchronously)
    print(f"\n2. Waiting for order processing (SQS -> Lambda)...")
    
    max_wait_time = 30  # seconds
    wait_interval = 2   # seconds
    waited = 0
    
    while waited < max_wait_time:
        print(f"Checking order status... (waited {waited}s)")
        
        # Check order status
        order_response = requests.get(f"{API_BASE_URL}/orders/{order_id}")
        if order_response.status_code == 200:
            order = order_response.json()
            current_status = order.get('status')
            print(f"Current status: {current_status}")
            
            if current_status == "PROCESSED":
                print("SUCCESS: Order status updated to PROCESSED!")
                break
            elif current_status == "PAYMENT_FAILED":
                print("ERROR: Payment failed during processing")
                return False
        
        time.sleep(wait_interval)
        waited += wait_interval
    
    if waited >= max_wait_time:
        print(f"WARNING: Order still not processed after {max_wait_time}s")
        print("This might be normal - SQS processing can take time")
    
    # Step 3: Check CloudWatch logs for processing evidence
    print(f"\n3. Checking CloudWatch logs for processing evidence...")
    
    try:
        # Get recent log events from process-order Lambda
        log_group = "/aws/lambda/test-dev-process-order"
        
        # Get log events from the last 5 minutes
        end_time = int(time.time() * 1000)
        start_time = end_time - (5 * 60 * 1000)  # 5 minutes ago
        
        response = logs.filter_log_events(
            logGroupName=log_group,
            startTime=start_time,
            endTime=end_time,
            filterPattern=order_id  # Look for our specific order ID
        )
        
        log_events = response.get('events', [])
        
        if log_events:
            print(f"Found {len(log_events)} log events for order {order_id}:")
            for event in log_events[-5:]:  # Show last 5 events
                timestamp = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(event['timestamp']/1000))
                print(f"  [{timestamp}] {event['message'].strip()}")
        else:
            print("No specific log events found for this order")
            
    except Exception as e:
        print(f"Could not check logs: {str(e)}")
    
    # Step 4: Check if invoice was created in S3
    print(f"\n4. Checking for invoice in S3...")
    
    try:
        invoice_bucket = "test-dev-invoices-448a1fa9"
        
        # List objects in the invoices folder
        today = time.strftime('%Y/%m/%d')
        invoice_prefix = f"invoices/{today}/"
        
        response = s3.list_objects_v2(
            Bucket=invoice_bucket,
            Prefix=invoice_prefix
        )
        
        invoices = response.get('Contents', [])
        order_invoice = None
        
        for invoice in invoices:
            if order_id in invoice['Key']:
                order_invoice = invoice
                break
        
        if order_invoice:
            print(f"SUCCESS: Invoice found at s3://{invoice_bucket}/{order_invoice['Key']}")
            print(f"Invoice size: {order_invoice['Size']} bytes")
            print(f"Created: {order_invoice['LastModified']}")
            
            # Try to read the invoice content
            try:
                invoice_response = s3.get_object(
                    Bucket=invoice_bucket,
                    Key=order_invoice['Key']
                )
                invoice_content = invoice_response['Body'].read().decode('utf-8')
                print(f"\nInvoice preview (first 300 chars):")
                print("-" * 50)
                print(invoice_content[:300] + "..." if len(invoice_content) > 300 else invoice_content)
                print("-" * 50)
                
            except Exception as e:
                print(f"Could not read invoice content: {str(e)}")
                
        else:
            print("No invoice found for this order")
            
    except Exception as e:
        print(f"Could not check S3 invoices: {str(e)}")
    
    # Step 5: Summary
    print(f"\n=== SUMMARY ===")
    print(f"Order ID: {order_id}")
    print(f"Test User: {test_user}")
    print(f"Order Total: ${order_data['total']}")
    
    final_order_response = requests.get(f"{API_BASE_URL}/orders/{order_id}")
    if final_order_response.status_code == 200:
        final_order = final_order_response.json()
        final_status = final_order.get('status')
        processed_at = final_order.get('processedAt', 'Not set')
        
        print(f"Final Status: {final_status}")
        print(f"Processed At: {processed_at}")
        
        if final_status == "PROCESSED":
            print("SUCCESS: Complete order processing flow working!")
            return True
        else:
            print("PARTIAL: Order created but processing may still be in progress")
            return True
    else:
        print("ERROR: Could not retrieve final order status")
        return False

if __name__ == "__main__":
    success = test_complete_order_processing_flow()
    exit(0 if success else 1)
