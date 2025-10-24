#!/usr/bin/env python3
"""
Quick test to verify the order creation fix
"""

import requests
import json
import uuid

API_BASE_URL = "https://otkwm0hrp3.execute-api.us-east-1.amazonaws.com"

def test_order_creation():
    """Test order creation with the Decimal fix"""
    
    test_user = f"test-user-{uuid.uuid4()}"
    
    order_data = {
        "userId": test_user,
        "items": [
            {
                "productId": "prod-100",
                "quantity": 1,
                "product": {
                    "id": "prod-100",
                    "name": "Wireless Headphones",
                    "price": 59.99  # This float should now be handled correctly
                }
            }
        ],
        "total": 59.99,  # This float should now be handled correctly
        "shippingInfo": {
            "name": "Test User",
            "email": "test@example.com",
            "address": "123 Test St",
            "city": "Test City",
            "zipCode": "12345"
        }
    }
    
    print("Testing order creation...")
    print(f"Order data: {json.dumps(order_data, indent=2)}")
    
    response = requests.post(f"{API_BASE_URL}/orders", json=order_data)
    
    print(f"Response Status: {response.status_code}")
    print(f"Response Body: {response.text}")
    
    if response.status_code == 200:
        result = response.json()
        order_id = result.get("orderId")
        print(f"SUCCESS: Order created successfully! Order ID: {order_id}")
        
        # Test getting the order back
        print(f"\nTesting order retrieval...")
        get_response = requests.get(f"{API_BASE_URL}/orders/{order_id}")
        print(f"Get Order Status: {get_response.status_code}")
        print(f"Get Order Body: {get_response.text}")
        
        if get_response.status_code == 200:
            print("SUCCESS: Order retrieval successful!")
            return True
        else:
            print("ERROR: Order retrieval failed!")
            return False
    else:
        print("ERROR: Order creation failed!")
        return False

if __name__ == "__main__":
    success = test_order_creation()
    exit(0 if success else 1)
