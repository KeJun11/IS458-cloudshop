#!/usr/bin/env python3
"""
Test script to verify email verification logic in process_order Lambda
"""

import json
import requests
import time
import uuid
import boto3

# Configuration
API_BASE_URL = "https://otkwm0hrp3.execute-api.us-east-1.amazonaws.com"

def test_email_with_different_addresses():
    """Test order processing with different email addresses"""
    
    # Test cases with different email addresses
    test_cases = [
        {
            "name": "Test Customer 1",
            "email": "test@example.com",  # This should trigger fallback
            "description": "Standard test email"
        },
        {
            "name": "Test Customer 2", 
            "email": "limkejun.4d@gmail.com",  # This is verified
            "description": "Verified email address"
        },
        {
            "name": "Test Customer 3",
            "email": "unverified@example.com",  # This should trigger fallback
            "description": "Unverified email address"
        }
    ]
    
    print("=== TESTING EMAIL VERIFICATION LOGIC ===\n")
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"{i}. Testing with {test_case['description']}: {test_case['email']}")
        
        # Generate unique user ID
        user_id = f"test-user-{uuid.uuid4()}"
        
        # Create order data
        order_data = {
            "userId": user_id,
            "items": [
                {
                    "productId": "prod-100",
                    "quantity": 1
                }
            ],
            "total": 59.99,
            "shippingInfo": {
                "name": test_case["name"],
                "email": test_case["email"],
                "address": "123 Test Street",
                "city": "Test City",
                "zipCode": "12345"
            }
        }
        
        try:
            # Create order
            response = requests.post(f"{API_BASE_URL}/orders", json=order_data)
            
            if response.status_code == 200:
                order_result = response.json()
                order_id = order_result.get('orderId')
                print(f"   SUCCESS: Order created: {order_id}")
                
                # Wait a bit for processing
                print("   WAITING: Waiting for order processing...")
                time.sleep(3)
                
                # Check order status
                order_response = requests.get(f"{API_BASE_URL}/orders/{order_id}")
                if order_response.status_code == 200:
                    order_details = order_response.json()
                    status = order_details.get('status', 'UNKNOWN')
                    print(f"   STATUS: Order status: {status}")
                    
                    if status == 'PROCESSED':
                        print(f"   SUCCESS: Order successfully processed!")
                    else:
                        print(f"   WARNING: Order status: {status}")
                else:
                    print(f"   ERROR: Failed to get order details: {order_response.status_code}")
                    
            else:
                print(f"   ERROR: Failed to create order: {response.status_code}")
                print(f"   Response: {response.text}")
                
        except Exception as e:
            print(f"   ERROR: {str(e)}")
            
        print()  # Empty line between tests
    
    print("=== CHECKING RECENT LOGS ===")
    print("Check CloudWatch logs for detailed email verification messages:")
    print("aws logs filter-log-events --log-group-name \"/aws/lambda/test-dev-process-order\" --start-time $(date -d '5 minutes ago' +%s)000")

if __name__ == "__main__":
    test_email_with_different_addresses()
