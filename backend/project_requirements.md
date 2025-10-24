Context: This project is proof of concept for sample deployment of an ecommerce application showcasing 2 use case:  
1. User makes an order for a product
2. System recommends a product back to user based on click

### **Core Components (Free Tier)**

* **Frontend:** S3 Bucket (static website hosting)
* **CDN:** CloudFront (global delivery & SSL)
* **API:** API Gateway (HTTP API - cheaper and simpler)
* **Compute:** Lambda (all backend logic)
* **Database:** DynamoDB (replaces both RDS and ElastiCache for products, carts, orders)
* **Async:** SQS (for "order processing")
* **SES** for email service
* **S3 buckets** for storing invoices

---

## **User workflow for Use Case 1: User Orders a product**

#### **Phase 1: Browsing and Loading the Shop**

1.  **User Request:** A user enters your website's URL (or a CloudFront URL) into their browser.
2.  **CDN -> S3:** **CloudFront** receives the request. Since it's the first visit, it fetches the static frontend files (e.g., `index.html`, `app.js`, `style.css`) from your **S3 Bucket**.
3.  **App Load:** CloudFront sends the files back to the user's browser, which loads your e-commerce application (e.g., your React/Vue/Angular app).
4.  **Fetch Products:** The JavaScript app, now running in the user's browser, needs to display products. It makes an asynchronous `GET` request to your API endpoint, like `https://api.your-domain.com/products`.
5.  **API -> Lambda:** **API Gateway** receives the `GET /products` request and is configured to trigger your `getProducts` **Lambda** function.
6.  **Lambda -> DB:** The `getProducts` Lambda runs. It executes a `scan` or `query` operation against your `Products-Table` in **DynamoDB**.
7.  **Response:** DynamoDB returns a JSON list of products to the Lambda. The Lambda function passes this JSON list back through API Gateway, all the way to the user's browser. The app then displays the products on the page.

#### **Phase 2: Adding to Cart**

1.  **User Action:** The user clicks the "Add to Cart" button for a specific product.
2.  **API Call:** The browser app sends a `POST` request to `https://api.your-domain.com/cart` with a JSON body like `{ "userId": "user-abc", "productId": "prod-123", "quantity": 1 }`.
3.  **API -> Lambda:** **API Gateway** receives the `POST /cart` request and triggers your `manageCart` **Lambda** function.
4.  **Lambda -> DB:** The `manageCart` Lambda executes an `UpdateItem` (or `PutItem`) operation on the `Carts-Table` in **DynamoDB**. It finds the cart for `user-abc` and adds `prod-123` to its list of items.
5.  **Response:** The Lambda function returns the user's updated cart contents as JSON. The app receives this and updates the "cart" icon to show "1 item".

#### **Phase 3: Checkout and Placing an Order**

1.  **User Action:** The user reviews their cart and clicks "Place Order".
2.  **API Call:** The browser app sends a `POST` request to `https://api.your-domain.com/orders`. The request body includes the user's cart contents and shipping information.
3.  **API -> Lambda:** **API Gateway** receives the `POST /orders` request and triggers your `createOrder` **Lambda** function.
4.  **Synchronous Logic (The User-Facing Part):** The `createOrder` Lambda performs two actions *immediately*:
    * **Action 1 (DB):** It generates a new `orderId` and writes the complete order details (items, user info, timestamp, status: "PENDING") to the `Orders-Table` in **DynamoDB**.
    * **Action 2 (Async):** It sends a small message (e.g., `{ "orderId": "order-xyz", "userEmail": "customer@email.com" }`) to an **SQS Queue** named `OrderProcessingQueue`. This "offloads" all the heavy work.
5.  **Response:** The Lambda immediately returns a "Success" message to the user, like `{ "orderId": "order-xyz", "status": "Order Received" }`. The browser app uses this to show the user a "Thank You!" confirmation page. The user's part of the transaction is now **complete**.

#### **Phase 4: Asynchronous Backend Processing (What happens "later")**

This part happens entirely in the background, invisible to the user, and uses **$0** worth of services (within the free tier).

1.  **SQS -> Lambda:** Your **SQS** queue (`OrderProcessingQueue`) is configured with an "event source mapping." This automatically triggers your `processOrder` **Lambda** function whenever a new message (from Step 3, Action 2) arrives.
2.  **Backend Logic:** The `processOrder` Lambda wakes up and receives the `{ "orderId": "order-xyz" }` message. It can now perform all the "slow" tasks you don't want the user to wait for:
    * Simulate a payment gateway call (Just a log statement will do)
    * Send a confirmation email (using **Amazon SES**, which also has an "Always Free" tier).
    * Update the `Orders-Table` in **DynamoDB** to change the status from "PENDING" to "PROCESSED".
    * (Optional) Clear the user's cart from the `Carts-Table` in DynamoDB.
    * Creates an invoice.txt file based on the request and uploads it into an S3 bucket
3.  **Done:** The Lambda finishes its work. The order is fully processed, and the user has already received their confirmation.

---

## **User workflow for Use Case 2: User gets product recommendation from mock Recommend service**

### **Core Components**

1.  **New Component:** Add a new DynamoDB table called `UserInteractions-Table`.
2.  **Primary Key:** The "Partition Key" (PK) will be the `userId`. The "Sort Key" (SK) will be the `productId` or `productType`.
3.  **New API Endpoint:** Create a new endpoint in API Gateway: `POST /events` (or `/track-click`).
4.  **New Lambda:** This endpoint will trigger a new `trackEvent` **Lambda** function.
5.  **New "Recommendation" Lambda:** Create another endpoint like `GET /recommendations` that triggers a `getRecommendations` **Lambda** function.

---


#### **Phase 1: Capturing User Interest (Tracking the Click)**

This happens in parallel with the user browsing.

1.  **User Action:** A user clicks on a product to view its details.
2.  **API Call (New):** Your frontend app *immediately* sends an asynchronous `POST` request to `https://api.your-domain.com/events`.
    * **Payload:** `{ "userId": "user-abc", "productId": "prod-123", "eventType": "product-view", "productType": "Electronics" }`
3.  **API -> Lambda:** **API Gateway** receives this and triggers your new `trackEvent` **Lambda** function.
4.  **Lambda -> DB:** The `trackEvent` Lambda simply writes this data to your new `UserInteractions-Table` in **DynamoDB**. This is extremely fast and cheap. (You could also use SQS to make this asynchronous, but a direct DynamoDB write is fine).

*That's it.* You are now successfully logging every product view, per user, in real-time.

#### **Phase 2: Generating the Recommendation (The "Dumbed Down" Logic)**

This is where your idea comes to life. This happens when the user loads their homepage or a "Recommended for You" section.

1.  **User Action:** The user visits the homepage.
2.  **API Call:** The frontend app makes a `GET` request to `https://api.your-domain.com/recommendations?userId=user-abc`.
3.  **API -> Lambda:** **API Gateway** triggers your `getRecommendations` **Lambda** function.
4.  **Lambda -> DB (Query):** The Lambda queries the `UserInteractions-Table` for all items where the Partition Key (PK) is `user-abc`.
5.  **Lambda Logic (Your Idea):** The function now has a list of all products the user has clicked on. It runs your simple logic in-memory:
    * It loops through the results.
    * It builds a simple count: `{"Electronics": 5, "Books": 2, "Apparel": 1}`.
    * It finds the top-scoring category (in this case, "Electronics").
6.  **Lambda -> DB (Fetch):** The Lambda then queries the *main* `Products-Table` for a few items where `productType == "Electronics"`.
7.  **Response:** The Lambda returns a JSON list of "Electronics" products. The frontend app displays this under a "Recommended for You" heading.

This approach perfectly mimics the *intent* of AWS Personalize (showing relevant items) but uses simple, free-tier services and deterministic logic that you control. It's a fantastic and practical solution.