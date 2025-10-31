### Problem 1: 
- I'm unsure if my recommendation system is working correctly, can you explain how my current implementation in my repo works now?

### Problem 2:
- There's also an issue with the SES where it can't consistently send email messages from my email, "limkejun.4d@gmail.com" to another registered user email that is filled in from the order checkout page. Can you help me fix this?

---

### Outputs:

api_endpoint = "https://gc40i3ru9a.execute-api.us-east-1.amazonaws.com"
cloudfront_domain = "d8qdi3kf4mqm4.cloudfront.net"
dynamodb_tables = {
  "carts" = "test-dev-carts"
  "interactions" = "test-dev-user-interactions"
  "orders" = "test-dev-orders"
  "products" = "test-dev-products"
}
invoice_bucket = "test-dev-invoices-f33ec18d"
order_queue_url = "https://sqs.us-east-1.amazonaws.com/900335273440/order-processing-dev"
ses_identity = "arn:aws:ses:us-east-1:900335273440:identity/limkejun.4d@gmail.com"
static_site_bucket = "test-dev-frontend-is458-2025-f33ec18d"

### Outputs 2:

api_endpoint = "https://gc40i3ru9a.execute-api.us-east-1.amazonaws.com"
cloudfront_domain = "d8qdi3kf4mqm4.cloudfront.net"
dynamodb_tables = {
  "carts" = "test-dev-carts"
  "interactions" = "test-dev-user-interactions"
  "orders" = "test-dev-orders"
  "products" = "test-dev-products"
}
invoice_bucket = "test-dev-invoices-f33ec18d"
order_queue_url = "https://sqs.us-east-1.amazonaws.com/900335273440/order-processing-dev"
ses_identity = "arn:aws:ses:us-east-1:900335273440:identity/limkejun.4d@gmail.com"
static_site_bucket = "test-dev-frontend-is458-2025-f33ec18d"  


### How to reset frontend bucket

1. run the sync command again
2. Get cloudfront distribution ID `aws cloudfront list-distributions --query "DistributionList.Items[?Comment=='test-dev static site distribution'].Id" --output text`

3. Invalidate the ID to remove the old cache data: `aws cloudfront create-invalidation --distribution-id YOUR_DISTRIBUTION_ID --paths "/*"`