"""
Comprehensive API Route Tests for IS458 CloudShop
Tests all Lambda functions through API Gateway endpoints
"""

import pytest
import requests
import json
import uuid
from datetime import datetime

# Configuration
API_BASE_URL = "https://otkwm0hrp3.execute-api.us-east-1.amazonaws.com"
TEST_USER_ID = "test-user-123"

class TestProductsAPI:
    """Test product-related endpoints"""
    
    def test_get_all_products(self):
        """Test GET /products - should return list of products"""
        response = requests.get(f"{API_BASE_URL}/products")
        
        assert response.status_code == 200
        products = response.json()
        assert isinstance(products, list)
        assert len(products) >= 2  # We have 2 seed products
        
        # Check product structure
        for product in products:
            assert "id" in product
            assert "name" in product
            assert "description" in product
            assert "price" in product
            assert "category" in product
            assert "imageUrl" in product
            assert "stock" in product
            assert isinstance(product["price"], (int, float))
            assert isinstance(product["stock"], int)
    
    def test_get_single_product(self):
        """Test GET /products/{id} - should return single product"""
        # Test with known seed product
        response = requests.get(f"{API_BASE_URL}/products/prod-100")
        
        assert response.status_code == 200
        product = response.json()
        assert product["id"] == "prod-100"
        assert product["name"] == "Wireless Headphones"
        assert product["category"] == "Electronics"
        assert product["price"] == 59.99
        assert product["stock"] == 50
    
    def test_get_nonexistent_product(self):
        """Test GET /products/{id} with non-existent ID"""
        response = requests.get(f"{API_BASE_URL}/products/nonexistent-id")
        
        assert response.status_code == 404
        error = response.json()
        assert "error" in error


class TestCartAPI:
    """Test cart-related endpoints"""
    
    def test_get_empty_cart(self):
        """Test GET /cart for user with no cart"""
        response = requests.get(f"{API_BASE_URL}/cart", params={"userId": f"empty-user-{uuid.uuid4()}"})
        
        assert response.status_code == 200
        cart = response.json()
        assert cart["items"] == []
        assert cart["total"] == 0
        assert "userId" in cart
    
    def test_add_to_cart(self):
        """Test POST /cart - add item to cart"""
        test_user = f"test-user-{uuid.uuid4()}"
        
        # Add item to cart
        cart_data = {
            "userId": test_user,
            "productId": "prod-100",
            "quantity": 2
        }
        
        response = requests.post(f"{API_BASE_URL}/cart", json=cart_data)
        
        assert response.status_code == 200
        cart = response.json()
        assert len(cart["items"]) == 1
        assert cart["items"][0]["productId"] == "prod-100"
        assert cart["items"][0]["quantity"] == 2
        assert cart["total"] > 0
        assert "product" in cart["items"][0]  # Should include product details
    
    def test_update_cart_item(self):
        """Test PUT /cart - update item quantity"""
        test_user = f"test-user-{uuid.uuid4()}"
        
        # First add item
        requests.post(f"{API_BASE_URL}/cart", json={
            "userId": test_user,
            "productId": "prod-100",
            "quantity": 1
        })
        
        # Then update quantity
        update_data = {
            "userId": test_user,
            "productId": "prod-100",
            "quantity": 3
        }
        
        response = requests.put(f"{API_BASE_URL}/cart", json=update_data)
        
        assert response.status_code == 200
        cart = response.json()
        assert cart["items"][0]["quantity"] == 3
    
    def test_remove_from_cart(self):
        """Test DELETE /cart - remove item from cart"""
        test_user = f"test-user-{uuid.uuid4()}"
        
        # First add item
        requests.post(f"{API_BASE_URL}/cart", json={
            "userId": test_user,
            "productId": "prod-100",
            "quantity": 1
        })
        
        # Then remove item
        remove_data = {
            "userId": test_user,
            "productId": "prod-100"
        }
        
        response = requests.delete(f"{API_BASE_URL}/cart", json=remove_data)
        
        assert response.status_code == 200
        cart = response.json()
        assert len(cart["items"]) == 0
        assert cart["total"] == 0
    
    def test_cart_with_invalid_product(self):
        """Test adding non-existent product to cart"""
        cart_data = {
            "userId": f"test-user-{uuid.uuid4()}",
            "productId": "nonexistent-product",
            "quantity": 1
        }
        
        response = requests.post(f"{API_BASE_URL}/cart", json=cart_data)
        
        assert response.status_code == 404
        error = response.json()
        assert "error" in error


class TestOrdersAPI:
    """Test order-related endpoints"""
    
    def test_create_order(self):
        """Test POST /orders - create new order"""
        order_data = {
            "userId": f"test-user-{uuid.uuid4()}",
            "items": [
                {
                    "productId": "prod-100",
                    "quantity": 1,
                    "product": {
                        "id": "prod-100",
                        "name": "Wireless Headphones",
                        "price": 59.99
                    }
                }
            ],
            "total": 59.99,
            "shippingInfo": {
                "name": "John Doe",
                "email": "john@example.com",
                "address": "123 Main St",
                "city": "Anytown",
                "zipCode": "12345"
            }
        }
        
        response = requests.post(f"{API_BASE_URL}/orders", json=order_data)
        
        print(f"Create order response status: {response.status_code}")
        print(f"Create order response body: {response.text}")
        
        assert response.status_code == 200
        result = response.json()
        assert "orderId" in result
        assert result["status"] == "PENDING"
    
    def test_get_user_orders(self):
        """Test GET /orders - get orders for user"""
        test_user = f"test-user-{uuid.uuid4()}"
        
        # First create an order
        order_data = {
            "userId": test_user,
            "items": [{"productId": "prod-100", "quantity": 1}],
            "total": 59.99,
            "shippingInfo": {
                "name": "Jane Doe",
                "email": "jane@example.com",
                "address": "456 Oak St",
                "city": "Somewhere",
                "zipCode": "67890"
            }
        }
        
        create_response = requests.post(f"{API_BASE_URL}/orders", json=order_data)
        assert create_response.status_code == 200
        
        # Then get user's orders
        response = requests.get(f"{API_BASE_URL}/orders", params={"userId": test_user})
        
        assert response.status_code == 200
        orders = response.json()
        assert isinstance(orders, list)
        assert len(orders) >= 1
        
        # Check order structure
        order = orders[0]
        assert "id" in order
        assert "userId" in order
        assert "items" in order
        assert "total" in order
        assert "status" in order
        assert "createdAt" in order
        assert "shippingInfo" in order
    
    def test_get_single_order(self):
        """Test GET /orders/{id} - get specific order"""
        # First create an order
        order_data = {
            "userId": f"test-user-{uuid.uuid4()}",
            "items": [{"productId": "prod-100", "quantity": 1}],
            "total": 59.99,
            "shippingInfo": {
                "name": "Bob Smith",
                "email": "bob@example.com",
                "address": "789 Pine St",
                "city": "Elsewhere",
                "zipCode": "11111"
            }
        }
        
        create_response = requests.post(f"{API_BASE_URL}/orders", json=order_data)
        assert create_response.status_code == 200
        
        order_id = create_response.json()["orderId"]
        
        # Then get the specific order
        response = requests.get(f"{API_BASE_URL}/orders/{order_id}")
        
        assert response.status_code == 200
        order = response.json()
        assert order["id"] == order_id
        assert order["status"] == "PENDING"
    
    def test_create_order_missing_fields(self):
        """Test POST /orders with missing required fields"""
        incomplete_order = {
            "userId": f"test-user-{uuid.uuid4()}",
            "items": []
            # Missing total and shippingInfo
        }
        
        response = requests.post(f"{API_BASE_URL}/orders", json=incomplete_order)
        
        assert response.status_code == 400
        error = response.json()
        assert "error" in error


class TestEventsAPI:
    """Test event tracking endpoints"""
    
    def test_track_product_view(self):
        """Test POST /events - track product view event"""
        event_data = {
            "userId": f"test-user-{uuid.uuid4()}",
            "productId": "prod-100",
            "eventType": "product-view",
            "productType": "Electronics"
        }
        
        response = requests.post(f"{API_BASE_URL}/events", json=event_data)
        
        assert response.status_code == 200
        result = response.json()
        assert "message" in result
    
    def test_track_add_to_cart_event(self):
        """Test POST /events - track add to cart event"""
        event_data = {
            "userId": f"test-user-{uuid.uuid4()}",
            "productId": "prod-200",
            "eventType": "add-to-cart",
            "productType": "Stationery"
        }
        
        response = requests.post(f"{API_BASE_URL}/events", json=event_data)
        
        assert response.status_code == 200
    
    def test_track_invalid_event_type(self):
        """Test POST /events with invalid event type"""
        event_data = {
            "userId": f"test-user-{uuid.uuid4()}",
            "productId": "prod-100",
            "eventType": "invalid-event",
            "productType": "Electronics"
        }
        
        response = requests.post(f"{API_BASE_URL}/events", json=event_data)
        
        assert response.status_code == 400
        error = response.json()
        assert "error" in error


class TestRecommendationsAPI:
    """Test recommendations endpoints"""
    
    def test_get_recommendations_new_user(self):
        """Test GET /recommendations for user with no history"""
        new_user = f"new-user-{uuid.uuid4()}"
        
        response = requests.get(f"{API_BASE_URL}/recommendations", params={"userId": new_user})
        
        assert response.status_code == 200
        recommendations = response.json()
        assert isinstance(recommendations, list)
        # Should return some products even for new users
    
    def test_get_recommendations_with_history(self):
        """Test GET /recommendations for user with interaction history"""
        test_user = f"test-user-{uuid.uuid4()}"
        
        # First create some interaction history
        event_data = {
            "userId": test_user,
            "productId": "prod-100",
            "eventType": "product-view",
            "productType": "Electronics"
        }
        
        requests.post(f"{API_BASE_URL}/events", json=event_data)
        
        # Then get recommendations
        response = requests.get(f"{API_BASE_URL}/recommendations", params={"userId": test_user})
        
        assert response.status_code == 200
        recommendations = response.json()
        assert isinstance(recommendations, list)
    
    def test_get_recommendations_missing_user_id(self):
        """Test GET /recommendations without userId parameter"""
        response = requests.get(f"{API_BASE_URL}/recommendations")
        
        assert response.status_code == 400
        error = response.json()
        assert "error" in error


class TestIntegrationScenarios:
    """Test complete user journey scenarios"""
    
    def test_complete_shopping_flow(self):
        """Test complete flow: view product -> add to cart -> create order"""
        test_user = f"integration-user-{uuid.uuid4()}"
        
        # 1. View products
        products_response = requests.get(f"{API_BASE_URL}/products")
        assert products_response.status_code == 200
        products = products_response.json()
        product = products[0]
        
        # 2. Track product view
        view_event = {
            "userId": test_user,
            "productId": product["id"],
            "eventType": "product-view",
            "productType": product["category"]
        }
        requests.post(f"{API_BASE_URL}/events", json=view_event)
        
        # 3. Add to cart
        cart_data = {
            "userId": test_user,
            "productId": product["id"],
            "quantity": 1
        }
        cart_response = requests.post(f"{API_BASE_URL}/cart", json=cart_data)
        assert cart_response.status_code == 200
        
        # 4. Track add to cart event
        cart_event = {
            "userId": test_user,
            "productId": product["id"],
            "eventType": "add-to-cart",
            "productType": product["category"]
        }
        requests.post(f"{API_BASE_URL}/events", json=cart_event)
        
        # 5. Create order
        order_data = {
            "userId": test_user,
            "items": [
                {
                    "productId": product["id"],
                    "quantity": 1,
                    "product": product
                }
            ],
            "total": product["price"],
            "shippingInfo": {
                "name": "Integration Test User",
                "email": "integration@test.com",
                "address": "123 Test St",
                "city": "Test City",
                "zipCode": "12345"
            }
        }
        
        order_response = requests.post(f"{API_BASE_URL}/orders", json=order_data)
        print(f"Integration test order response: {order_response.status_code}")
        print(f"Integration test order body: {order_response.text}")
        
        assert order_response.status_code == 200
        order_result = order_response.json()
        assert "orderId" in order_result
        
        # 6. Verify order was created
        order_id = order_result["orderId"]
        get_order_response = requests.get(f"{API_BASE_URL}/orders/{order_id}")
        assert get_order_response.status_code == 200
        
        # 7. Get recommendations (should be influenced by interaction history)
        rec_response = requests.get(f"{API_BASE_URL}/recommendations", params={"userId": test_user})
        assert rec_response.status_code == 200


if __name__ == "__main__":
    # Run specific test for debugging
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "debug-order":
        # Quick order creation test for debugging
        test = TestOrdersAPI()
        try:
            order_id = test.test_create_order()
            print(f"✅ Order created successfully: {order_id}")
        except Exception as e:
            print(f"❌ Order creation failed: {e}")
    else:
        print("Run with: python test_api_routes.py debug-order")
        print("Or run full tests with: pytest test_api_routes.py -v")
