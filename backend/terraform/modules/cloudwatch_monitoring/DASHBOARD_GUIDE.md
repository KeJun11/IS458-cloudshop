# CloudWatch Dashboard - Updated Configuration

## ✅ What's Now Included

Your CloudWatch dashboard now shows **7 comprehensive widgets** monitoring all critical services:

### **1. API Gateway - Requests & Errors**

- Total API requests
- 4XX client errors
- 5XX server errors
- **Shows:** Overall API health and traffic

---

### **2. Lambda - Invocations by Function** ⭐ (UPDATED)

**Shows INDIVIDUAL Lambda functions:**

- `test-dev-get-products`
- `test-dev-manage-cart`
- `test-dev-create-order`
- `test-dev-process-order`
- `test-dev-track-event`
- `test-dev-get-recommendations`

**Each function has its own line** - you can see which functions are being called most frequently!

---

### **3. Lambda - Errors & Throttles (All Functions)**

- Total errors across all functions (aggregate)
- Total throttled requests
- **Shows:** Overall Lambda health

---

### **4. DynamoDB - Request Latency by Table** ⭐ (UPDATED)

**Shows INDIVIDUAL DynamoDB tables:**

- `test-dev-products`
- `test-dev-carts`
- `test-dev-orders`
- `test-dev-user-interactions`

**Each table has its own line** - you can see which tables have the fastest/slowest response times!

---

### **5. DynamoDB - Errors (All Tables)**

- User errors (aggregate)
- System errors (aggregate)
- **Shows:** Overall database error rate

---

### **6. SQS - Order Processing Queue & Dead Letter Queue** ⭐ (UPDATED)

**Shows BOTH queues:**

- **Messages in Main Queue** (order-processing-dev) - Orders being processed
- **Messages in DLQ** (order-processing-dlq-dev) - Failed orders ⚠️
- **Oldest Message Age** - How long messages wait

**What is DLQ?** If an order fails to process 3 times, it goes to the Dead Letter Queue (DLQ) for investigation. This prevents infinite retry loops and alerts you to problematic orders.

---

### **7. SES - Order Confirmation Emails** ⭐ (NEW)

- Emails sent
- Successfully delivered
- Bounced emails
- Rejected emails
- **Shows:** Email delivery monitoring for order confirmations

---

## **How to Access**

### **Dashboard:**

1. Go to [AWS CloudWatch Console](https://console.aws.amazon.com/cloudwatch/)
2. Click **Dashboards** → **`test-dev-monitoring`**
3. You'll see all 7 widgets

### **Alarms:**

1. CloudWatch Console → **Alarms** → **All alarms**
2. Search: `test-dev-`
3. You'll see 5 alarms (should all be in "OK" state)

---

## **For Your Presentation**

### **What to Show:**

**1. Open the Dashboard**

- Point out: "We monitor 6 Lambda functions individually"
- Point out: "We track latency for all 4 DynamoDB tables separately"
- Point out: "We monitor the Dead Letter Queue to catch failed orders"
- Point out: "We track email delivery for order confirmations"

**2. Explain the Layout:**

> "Our monitoring covers the entire application stack:
>
> - API Gateway for incoming traffic
> - Six Lambda functions handling different operations
> - Four DynamoDB tables storing products, carts, orders, and user interactions
> - SQS queue for async order processing, including failed message tracking
> - SES for email notifications"

**3. Show Alarms:**

> "We've configured 5 CloudWatch alarms to proactively alert us:
>
> - API errors exceeding thresholds
> - Lambda function failures
> - DynamoDB system errors
> - Queue backlog growing too large
> - Failed messages in the Dead Letter Queue
>   All alarms are currently in OK state, indicating healthy system operation."

---

## **Key Features to Highlight**

✅ **Individual Service Monitoring** - Not just aggregates, each service is tracked separately

✅ **Dead Letter Queue Monitoring** - Shows we handle failures gracefully

✅ **Email Delivery Tracking** - Complete observability including notifications

✅ **Infrastructure as Code** - Everything deployed via Terraform

✅ **Real-time Metrics** - Dashboard updates automatically (5-minute intervals for most metrics)

---

## **What Metrics Show "Services Are Working"**

1. **Lambda Invocations > 0** = Functions are being called
2. **DynamoDB Latency < 50ms** = Database responding quickly
3. **SQS Messages = 0 or low** = Orders processing smoothly
4. **SQS DLQ = 0** = No failed orders (good!)
5. **SES Send > 0** = Emails being sent

---

## **Answering Your Questions:**

### **Q: Why show individual Lambda functions?**

**A:** So you can see which endpoints are most active (e.g., `get-products` vs `create-order`)

### **Q: Why show individual DynamoDB tables?**

**A:** Different tables have different access patterns. Products table might be read-heavy (fast), while orders might have more complex writes (slower)

### **Q: What's the Dead Letter Queue?**

**A:** When the `process-order` Lambda fails 3 times processing an order from SQS, that message goes to DLQ. This prevents:

- Infinite retry loops
- Lost orders
- Queue blocking

Monitoring DLQ = 0 means all orders process successfully!

### **Q: Why monitor SES?**

**A:** To ensure customers receive order confirmations. If emails bounce or get rejected, you need to know!

---

## **Dashboard Refresh Rate:**

- **Most metrics:** Update every 5 minutes
- **SQS metrics:** Update every 1 minute (faster for queue monitoring)

To see live data, generate some traffic (place orders, browse products, etc.)
