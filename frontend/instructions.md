# E-Commerce Architecture Flow:



1. Order logic

## Phase 1: Browsing and Loading the Shop 

**User Request:** A user enters your website's URL (or a CloudFront URL) into their browser. 

**CDN -> S3:** CloudFront receives the request. Since it's the first visit, it fetches the static frontend files (e.g., index.html, app.js, style.css) from your S3 Bucket. 

**App Load:** CloudFront sends the files back to the user's browser, which loads your e-commerce application (e.g., your React/Vue/Angular app). 

**Fetch Products:** The JavaScript app, now running in the user's browser, needs to display products. It makes an asynchronous GET request to your API endpoint, like https://api.your-domain.com/products. 

**API -> Lambda:** API Gateway receives the GET /products request and is configured to trigger your getProducts Lambda function. 

**Lambda -> DB:** The getProducts Lambda runs. It executes a scan or query operation against your Products-Table in DynamoDB. 

**Response:** DynamoDB returns a JSON list of products to the Lambda. The Lambda function passes this JSON list back through API Gateway, all the way to the user's browser. The app then displays the products on the page. 

## Phase 2: Adding to Cart 

**User Action:** The user clicks the "Add to Cart" button for a specific product. 

**API Call:** The browser app sends a POST request to https://api.your-domain.com/cart with a JSON body like `{ "userId": "user-abc", "productId": "prod-123", "quantity": 1 }`. 

**API -> Lambda:** API Gateway receives the POST /cart request and triggers your manageCart Lambda function. 

**Lambda -> DB:** The manageCart Lambda executes an UpdateItem (or PutItem) operation on the Carts-Table in DynamoDB. It finds the cart for user-abc and adds prod-123 to its list of items. 

**Response:** The Lambda function returns the user's updated cart contents as JSON. The app receives this and updates the "cart" icon to show "1 item". 

## Phase 3: Checkout and Placing an Order 

**User Action:** The user reviews their cart and clicks "Place Order". 

**API Call:** The browser app sends a POST request to https://api.your-domain.com/orders. The request body includes the user's cart contents and shipping information. 

**API -> Lambda:** API Gateway receives the POST /orders request and triggers your createOrder Lambda function. 

**Synchronous Logic (The User-Facing Part):** The createOrder Lambda performs two actions immediately: 

* **Action 1 (DB):** It generates a new orderId and writes the complete order details (items, user info, timestamp, status: "PENDING") to the Orders-Table in DynamoDB. 

* **Action 2 (Async):** It sends a small message (e.g., `{ "orderId": "order-xyz", "userEmail": "customer@email.com" }`) to an SQS Queue named OrderProcessingQueue. This "offloads" all the heavy work. 

**Response:** The Lambda immediately returns a "Success" message to the user, like `{ "orderId": "order-xyz", "status": "Order Received" }`. The browser app uses this to show the user a "Thank You!" confirmation page. The user's part of the transaction is now complete. 

## Phase 4: Asynchronous Backend Processing (What happens "later") 

This part happens entirely in the background, invisible to the user, and uses $0 worth of services (within the free tier). 

**SQS -> Lambda:** Your SQS queue (OrderProcessingQueue) is configured with an "event source mapping." This automatically triggers your processOrder Lambda function whenever a new message (from Step 3, Action 2) arrives. 

**Backend Logic:** The processOrder Lambda wakes up and receives the `{ "orderId": "order-xyz" }` message. It can now perform all the "slow" tasks you don't want the user to wait for: 

* Simulate a payment gateway call. 

* Send a confirmation email (using Amazon SES, which also has an "Always Free" tier). 

* Update the Orders-Table in DynamoDB to change the status from "PENDING" to "PROCESSED". 

* (Optional) Clear the user's cart from the Carts-Table in DynamoDB. 

**Done:** The Lambda finishes its work. The order is fully processed, and the user has already received their confirmation.



2. User Recommendation flow

## Phase 1: Capturing User Interest (Tracking the Click) 

This happens in parallel with the user browsing. 

1. **User Action:** A user clicks on a product to view its details. 

2. **API Call (New):** Your frontend app immediately sends an asynchronous POST request to https://api.your-domain.com/events. 
   * **Payload:** `{ "userId": "user-abc", "productId": "prod-123", "eventType": "product-view", "productType": "Electronics" }` 

3. **API -> Lambda:** API Gateway receives this and triggers your new trackEvent Lambda function. 

4. **Lambda -> DB:** The trackEvent Lambda simply writes this data to your new UserInteractions-Table in DynamoDB. This is extremely fast and cheap. (You could also use SQS to make this asynchronous, but a direct DynamoDB write is fine). 

That's it. You are now successfully logging every product view, per user, in real-time. 

## Phase 2: Generating the Recommendation (The "Dumbed Down" Logic) 

This is where your idea comes to life. This happens when the user loads their homepage or a "Recommended for You" section. 

1. **User Action:** The user visits the homepage. 

2. **API Call:** The frontend app makes a GET request to https://api.your-domain.com/recommendations?userId=user-abc. 

3. **API -> Lambda:** API Gateway triggers your getRecommendations Lambda function. 

4. **Lambda -> DB (Query):** The Lambda queries the UserInteractions-Table for all items where the Partition Key (PK) is user-abc.