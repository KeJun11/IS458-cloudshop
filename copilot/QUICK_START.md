# 🚀 Quick Start Guide: Switching from Mock Data to Lambda Backend

This guide walks you through switching your frontend from using mock data to your actual Lambda backend.

## ✅ What's Already Done

1. **Frontend API integration** - All API calls are now enabled in `AppContext.tsx`
2. **Lambda endpoints** - All required endpoints are implemented and ready
3. **API URL** - Your frontend `.env` is already configured with the correct API endpoint

## 📋 Prerequisites

- AWS credentials configured (`aws configure`)
- Python 3 with boto3 installed
- Your DynamoDB tables created via Terraform
- Lambda functions deployed

## 🎯 Step-by-Step Instructions

### Step 1: Install Python Dependencies

```bash
pip install boto3 requests
```

### Step 2: Find Your DynamoDB Table Name

Get your products table name from Terraform:

```bash
cd backend/terraform/envs/dev
terraform output dynamodb_tables
```

You should see output like:

```
{
  "products" = "aws-ecommerce-dev-products"
  ...
}
```

### Step 3: Seed Products to DynamoDB

Run the seeding script with your table name:

```bash
cd backend/scripts

# Dry run first (to preview)
python seed_products.py --table-name aws-ecommerce-dev-products --dry-run

# Actual seed
python seed_products.py --table-name aws-ecommerce-dev-products
```

Expected output:

```
Seeding products table: aws-ecommerce-dev-products
Region: us-east-1
Number of products to insert: 6

✓ Inserted: prod-1 - Wireless Bluetooth Headphones
✓ Inserted: prod-2 - Smart Watch
✓ Inserted: prod-3 - Laptop Backpack
✓ Inserted: prod-4 - Wireless Mouse
✓ Inserted: prod-5 - USB-C Hub
✓ Inserted: prod-6 - Portable Charger

============================================================
Seeding completed!
  Successful: 6
  Failed: 0
============================================================
```

### Step 4: Test Your Backend Endpoints

Test all endpoints to make sure they're working:

```bash
python test_endpoints.py
```

Or with a custom API URL:

```bash
python test_endpoints.py --api-url https://your-api-endpoint.amazonaws.com
```

Expected output:

```
============================================================
🚀 LAMBDA API ENDPOINT TESTING
============================================================

Testing: Get All Products
  GET /products
  Status: 200
  ✅ SUCCESS
  Response: Array with 6 items

...

📊 TEST SUMMARY
============================================================
Total Tests: 8
Passed: 8 ✅
Failed: 0 ❌
Success Rate: 100.0%
============================================================

🎉 All tests passed! Your API is working correctly.
```

### Step 5: Verify with curl (Optional)

Quick manual test:

```bash
# Test products endpoint
curl https://otkwm0hrp3.execute-api.us-east-1.amazonaws.com/products

# Test specific product
curl https://otkwm0hrp3.execute-api.us-east-1.amazonaws.com/products/prod-1
```

### Step 6: Start Your Frontend

```bash
cd frontend
npm install  # if needed
npm run dev
```

Visit `http://localhost:5173` (or your configured port) and:

1. ✅ Products should load from DynamoDB
2. ✅ Add items to cart (stored in DynamoDB)
3. ✅ View cart
4. ✅ Remove items from cart
5. ✅ See recommendations (if you've tracked some events)

## 🔍 Troubleshooting

### Products Not Loading

**Check 1:** Verify API URL is correct

```bash
cd frontend
cat .env
# Should show: VITE_API_URL="https://otkwm0hrp3.execute-api.us-east-1.amazonaws.com"
```

**Check 2:** Verify products exist in DynamoDB

```bash
aws dynamodb scan --table-name aws-ecommerce-dev-products --region us-east-1
```

**Check 3:** Check browser console for CORS errors

- Open browser DevTools (F12)
- Check Console tab for errors
- If CORS errors, verify API Gateway CORS settings

### Cart Not Working

**Check 1:** Verify carts table exists

```bash
aws dynamodb describe-table --table-name aws-ecommerce-dev-carts --region us-east-1
```

**Check 2:** Check Lambda logs

```bash
aws logs tail /aws/lambda/get_cart --follow --region us-east-1
```

### Recommendations Empty

This is normal at first! Recommendations are based on tracked user interactions.

**Solution:** Browse some products to generate interactions:

1. View several products
2. Add items to cart
3. Wait a few seconds
4. Refresh the page or navigate to a page that shows recommendations

## 📊 Monitoring

### Check Lambda Logs

```bash
# Get products logs
aws logs tail /aws/lambda/get_products --follow --region us-east-1

# Cart management logs
aws logs tail /aws/lambda/manage_cart --follow --region us-east-1

# Recommendations logs
aws logs tail /aws/lambda/get_recommendations --follow --region us-east-1
```

### Check DynamoDB Data

```bash
# View all products
aws dynamodb scan --table-name aws-ecommerce-dev-products --region us-east-1

# View carts
aws dynamodb scan --table-name aws-ecommerce-dev-carts --region us-east-1

# View interactions
aws dynamodb scan --table-name aws-ecommerce-dev-user-interactions --region us-east-1
```

## 📚 Additional Resources

- **API Endpoints Documentation:** See `backend/API_ENDPOINTS.md`
- **Seeding Scripts:** See `backend/scripts/README.md`
- **Lambda Functions:** See `backend/lambdas/*/app.py`
- **Terraform Configuration:** See `backend/terraform/`

## 🎉 Success Checklist

- [ ] Python dependencies installed
- [ ] DynamoDB table name identified
- [ ] Products seeded to DynamoDB (6 products)
- [ ] Backend endpoints tested successfully
- [ ] Frontend .env configured with API URL
- [ ] Frontend running and loading products from backend
- [ ] Cart operations working
- [ ] Event tracking working
- [ ] Recommendations appearing (after browsing)

## 🆘 Need Help?

1. Check the test output for specific errors
2. Review Lambda CloudWatch logs
3. Verify DynamoDB tables have data
4. Check API Gateway configuration
5. Ensure CORS is properly configured

---

**Current Configuration:**

- **API URL:** `https://otkwm0hrp3.execute-api.us-east-1.amazonaws.com`
- **Region:** `us-east-1`
- **Project:** `aws-ecommerce`
- **Environment:** `dev`
