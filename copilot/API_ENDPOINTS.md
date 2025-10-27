# Lambda API Endpoints Overview

This document provides a comprehensive overview of all available Lambda function endpoints in your e-commerce backend.

## Base URL

```
https://otkwm0hrp3.execute-api.us-east-1.amazonaws.com
```

---

## 📦 Products API

### ✅ GET /products

**Lambda:** `get_products`  
**Description:** Retrieve all products from the catalog  
**Request:** No parameters required  
**Response:**

```json
[
  {
    "id": "prod-1",
    "name": "Wireless Bluetooth Headphones",
    "description": "High-quality wireless headphones with noise cancellation",
    "price": 199.99,
    "category": "Electronics",
    "imageUrl": "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=500",
    "stock": 50
  },
  ...
]
```

**Frontend Integration:** ✅ Already implemented

```typescript
const products = await apiService.getProducts();
```

---

### ✅ GET /products/{id}

**Lambda:** `get_products`  
**Description:** Get a specific product by ID  
**Request:**

- Path parameter: `id` (product ID)

**Response:**

```json
{
  "id": "prod-1",
  "name": "Wireless Bluetooth Headphones",
  "description": "High-quality wireless headphones with noise cancellation",
  "price": 199.99,
  "category": "Electronics",
  "imageUrl": "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=500",
  "stock": 50
}
```

**Frontend Integration:** ✅ Already implemented

```typescript
const product = await apiService.getProduct("prod-1");
```

---

## 🛒 Cart API

### ✅ GET /cart

**Lambda:** `manage_cart`  
**Description:** Get user's shopping cart  
**Request:**

- Query parameter: `userId` (required)

**Example:**

```
GET /cart?userId=user-demo
```

**Response:**

```json
{
  "userId": "user-demo",
  "items": [
    {
      "productId": "prod-1",
      "quantity": 2,
      "product": {
        "id": "prod-1",
        "name": "Wireless Bluetooth Headphones",
        "price": 199.99,
        ...
      }
    }
  ],
  "total": 399.98
}
```

**Frontend Integration:** ✅ Already implemented

```typescript
const cart = await apiService.getCart(userId);
```

---

### ✅ POST /cart

**Lambda:** `manage_cart`  
**Description:** Add item to cart  
**Request Body:**

```json
{
  "userId": "user-demo",
  "productId": "prod-1",
  "quantity": 2
}
```

**Response:** Returns updated cart (same format as GET /cart)

**Frontend Integration:** ✅ Already implemented

```typescript
const cart = await apiService.addToCart(userId, productId, quantity);
```

---

### ✅ PUT /cart

**Lambda:** `manage_cart`  
**Description:** Update cart item quantity  
**Request Body:**

```json
{
  "userId": "user-demo",
  "productId": "prod-1",
  "quantity": 3
}
```

**Response:** Returns updated cart

**Frontend Integration:** ✅ Already implemented

```typescript
const cart = await apiService.updateCartItem(userId, productId, quantity);
```

---

### ✅ DELETE /cart

**Lambda:** `manage_cart`  
**Description:** Remove item from cart  
**Request Body:**

```json
{
  "userId": "user-demo",
  "productId": "prod-1"
}
```

**Response:** Returns updated cart

**Frontend Integration:** ✅ Already implemented

```typescript
const cart = await apiService.removeFromCart(userId, productId);
```

---

## 📝 Orders API

### ✅ POST /orders

**Lambda:** `create_order`  
**Description:** Create a new order  
**Request Body:**

```json
{
  "userId": "user-demo",
  "items": [
    {
      "productId": "prod-1",
      "quantity": 2
    }
  ],
  "total": 399.98,
  "shippingInfo": {
    "name": "John Doe",
    "email": "john@example.com",
    "address": "123 Main St",
    "city": "New York",
    "zipCode": "10001"
  }
}
```

**Response:**

```json
{
  "orderId": "order-abc123",
  "status": "PENDING"
}
```

**Frontend Integration:** ✅ Already implemented

```typescript
const result = await apiService.createOrder(orderData);
```

---

### ⚠️ GET /orders (by userId)

**Status:** Check if implemented  
**Description:** Get all orders for a user  
**Request:**

- Query parameter: `userId` (required)

**Frontend Integration:** ✅ Already defined in api.ts

```typescript
const orders = await apiService.getOrders(userId);
```

---

### ⚠️ GET /orders/{orderId}

**Status:** Check if implemented  
**Description:** Get a specific order  
**Request:**

- Path parameter: `orderId`

**Frontend Integration:** ✅ Already defined in api.ts

```typescript
const order = await apiService.getOrder(orderId);
```

---

## 🎯 Recommendations API

### ✅ GET /recommendations

**Lambda:** `get_recommendations`  
**Description:** Get personalized product recommendations based on user interactions  
**Request:**

- Query parameter: `userId` (required)

**Example:**

```
GET /recommendations?userId=user-demo
```

**Response:**

```json
[
  {
    "id": "prod-2",
    "name": "Smart Watch",
    "description": "Feature-rich smartwatch with health tracking",
    "price": 299.99,
    "category": "Electronics",
    "imageUrl": "https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=500",
    "stock": 30
  },
  ...
]
```

**Frontend Integration:** ✅ Already implemented

```typescript
const recommendations = await apiService.getRecommendations(userId);
```

---

## 📊 Event Tracking API

### ✅ POST /events

**Lambda:** `track_event`  
**Description:** Track user interactions (views, cart additions, purchases)  
**Request Body:**

```json
{
  "userId": "user-demo",
  "productId": "prod-1",
  "eventType": "product-view",
  "productType": "Electronics",
  "timestamp": "2025-10-27T12:00:00.000Z"
}
```

**Valid Event Types:**

- `product-view`
- `add-to-cart`
- `purchase`

**Response:**

```json
{
  "message": "Event tracked successfully"
}
```

**Frontend Integration:** ✅ Already implemented

```typescript
await apiService.trackEvent({
  userId: userId,
  productId: productId,
  eventType: "product-view",
  productType: category,
});
```

---

## 🔄 Background Processing

### Order Processing

**Lambda:** `process_order`  
**Trigger:** SQS Queue (automatic)  
**Description:** Processes orders asynchronously, generates invoices, sends emails  
**Note:** This is not directly called by the frontend

---

## ✅ Summary: Frontend-Backend Integration Status

| Endpoint             | Lambda Function       | Frontend Integration | Status               |
| -------------------- | --------------------- | -------------------- | -------------------- |
| GET /products        | `get_products`        | ✅ Implemented       | Ready to use         |
| GET /products/{id}   | `get_products`        | ✅ Implemented       | Ready to use         |
| GET /cart            | `manage_cart`         | ✅ Implemented       | Ready to use         |
| POST /cart           | `manage_cart`         | ✅ Implemented       | Ready to use         |
| PUT /cart            | `manage_cart`         | ✅ Implemented       | Ready to use         |
| DELETE /cart         | `manage_cart`         | ✅ Implemented       | Ready to use         |
| POST /orders         | `create_order`        | ✅ Implemented       | Ready to use         |
| GET /orders          | ❓ To verify          | ✅ Defined           | Check implementation |
| GET /orders/{id}     | ❓ To verify          | ✅ Defined           | Check implementation |
| GET /recommendations | `get_recommendations` | ✅ Implemented       | Ready to use         |
| POST /events         | `track_event`         | ✅ Implemented       | Ready to use         |

---

## 🚀 Next Steps

1. **Seed the database** with products using the script:

   ```bash
   cd backend/scripts
   python seed_products.py --table-name aws-ecommerce-dev-products
   ```

2. **Test the endpoints** using curl or your frontend:

   ```bash
   # Test products endpoint
   curl https://otkwm0hrp3.execute-api.us-east-1.amazonaws.com/products

   # Test specific product
   curl https://otkwm0hrp3.execute-api.us-east-1.amazonaws.com/products/prod-1
   ```

3. **Verify frontend integration** by starting your React app:

   ```bash
   cd frontend
   npm run dev
   ```

4. **Check for missing endpoints:** Verify if GET /orders endpoints are implemented in your Lambda functions.
