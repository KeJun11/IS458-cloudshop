#!/usr/bin/env python3
"""
Quick test script to verify your Lambda endpoints are working correctly.
Tests all the main API endpoints with your actual backend.

Usage:
    python test_endpoints.py --api-url <your-api-url>
    
Example:
    python test_endpoints.py --api-url https://otkwm0hrp3.execute-api.us-east-1.amazonaws.com
"""

import argparse
import requests
import json
from typing import Dict, Any


class APITester:
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip('/')
        self.test_user_id = "user-demo"
        
    def test_endpoint(self, name: str, method: str, endpoint: str, 
                     data: Dict = None, params: Dict = None) -> bool:
        """Test a single endpoint and print results"""
        url = f"{self.base_url}{endpoint}"
        
        try:
            print(f"\n{'='*60}")
            print(f"Testing: {name}")
            print(f"  {method} {endpoint}")
            
            if method == "GET":
                response = requests.get(url, params=params)
            elif method == "POST":
                response = requests.post(url, json=data)
            elif method == "PUT":
                response = requests.put(url, json=data)
            elif method == "DELETE":
                response = requests.delete(url, json=data)
            else:
                print(f"  ❌ Unsupported method: {method}")
                return False
            
            print(f"  Status: {response.status_code}")
            
            if response.status_code in [200, 201]:
                print(f"  ✅ SUCCESS")
                try:
                    result = response.json()
                    if isinstance(result, list):
                        print(f"  Response: Array with {len(result)} items")
                        if result:
                            print(f"  First item: {json.dumps(result[0], indent=2)[:200]}...")
                    else:
                        print(f"  Response: {json.dumps(result, indent=2)[:300]}...")
                    return True
                except:
                    print(f"  Response: {response.text[:200]}")
                    return True
            else:
                print(f"  ❌ FAILED")
                print(f"  Error: {response.text[:200]}")
                return False
                
        except Exception as e:
            print(f"  ❌ ERROR: {str(e)}")
            return False
    
    def run_all_tests(self):
        """Run all endpoint tests"""
        print("\n" + "="*60)
        print("🚀 LAMBDA API ENDPOINT TESTING")
        print("="*60)
        print(f"Base URL: {self.base_url}")
        print(f"Test User: {self.test_user_id}")
        
        results = []
        
        # Test 1: Get all products
        results.append(
            self.test_endpoint(
                "Get All Products",
                "GET",
                "/products"
            )
        )
        
        # Test 2: Get specific product
        results.append(
            self.test_endpoint(
                "Get Specific Product",
                "GET",
                "/products/prod-1"
            )
        )
        
        # Test 3: Get cart (should be empty initially)
        results.append(
            self.test_endpoint(
                "Get Cart",
                "GET",
                "/cart",
                params={"userId": self.test_user_id}
            )
        )
        
        # Test 4: Add to cart
        results.append(
            self.test_endpoint(
                "Add to Cart",
                "POST",
                "/cart",
                data={
                    "userId": self.test_user_id,
                    "productId": "prod-1",
                    "quantity": 2
                }
            )
        )
        
        # Test 5: Update cart item
        results.append(
            self.test_endpoint(
                "Update Cart Item",
                "PUT",
                "/cart",
                data={
                    "userId": self.test_user_id,
                    "productId": "prod-1",
                    "quantity": 3
                }
            )
        )
        
        # Test 6: Get recommendations
        results.append(
            self.test_endpoint(
                "Get Recommendations",
                "GET",
                "/recommendations",
                params={"userId": self.test_user_id}
            )
        )
        
        # Test 7: Track event
        results.append(
            self.test_endpoint(
                "Track Event",
                "POST",
                "/events",
                data={
                    "userId": self.test_user_id,
                    "productId": "prod-1",
                    "eventType": "product-view",
                    "productType": "Electronics"
                }
            )
        )
        
        # Test 8: Remove from cart (cleanup)
        results.append(
            self.test_endpoint(
                "Remove from Cart",
                "DELETE",
                "/cart",
                data={
                    "userId": self.test_user_id,
                    "productId": "prod-1"
                }
            )
        )
        
        # Print summary
        print("\n" + "="*60)
        print("📊 TEST SUMMARY")
        print("="*60)
        passed = sum(results)
        total = len(results)
        print(f"Total Tests: {total}")
        print(f"Passed: {passed} ✅")
        print(f"Failed: {total - passed} ❌")
        print(f"Success Rate: {(passed/total*100):.1f}%")
        print("="*60 + "\n")
        
        if passed == total:
            print("🎉 All tests passed! Your API is working correctly.")
        elif passed == 0:
            print("⚠️  All tests failed. Check if:")
            print("   1. The API URL is correct")
            print("   2. The Lambda functions are deployed")
            print("   3. DynamoDB tables exist and have data")
            print("   4. CORS is configured correctly")
        else:
            print(f"⚠️  {total - passed} test(s) failed. Review the errors above.")


def main():
    parser = argparse.ArgumentParser(
        description="Test Lambda API endpoints"
    )
    parser.add_argument(
        "--api-url",
        default="https://otkwm0hrp3.execute-api.us-east-1.amazonaws.com",
        help="Base URL for the API (default: your current API endpoint)"
    )
    
    args = parser.parse_args()
    
    tester = APITester(args.api_url)
    tester.run_all_tests()


if __name__ == "__main__":
    main()
