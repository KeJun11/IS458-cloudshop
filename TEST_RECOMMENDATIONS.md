# Testing Recommendation System

## 🔧 Fixes Applied

### Backend Fix:

✅ **`get_recommendations/app.py`** - Returns empty array `[]` when no interactions (was returning random products)

### Frontend Fix:

✅ **`ProductsPage.tsx`** - Fixed useEffect to properly reload recommendations on mount

---

## 🧪 How to Test

### Step 1: Clear Existing Interactions (Fresh Start)

```bash
# Get your interactions table name
cd /mnt/c/Users/limke_msg9rxa/Downloads/Coding/AWS-Deploy/backend/terraform/envs/dev
INTERACTIONS_TABLE=$(terraform output -json dynamodb_tables | jq -r '.interactions')
echo "Interactions table: $INTERACTIONS_TABLE"

# Clear all items (for testing - this deletes all user interaction history)
aws dynamodb scan \
  --table-name $INTERACTIONS_TABLE \
  --region us-east-1 \
  --query 'Items[*].[userId.S, productId.S]' \
  --output text | \
while read userId productId; do
  aws dynamodb delete-item \
    --table-name $INTERACTIONS_TABLE \
    --key "{\"userId\":{\"S\":\"$userId\"},\"productId\":{\"S\":\"$productId\"}}" \
    --region us-east-1
done

echo "✅ Cleared all interactions"
```

### Step 2: Deploy Backend Changes

```bash
cd /mnt/c/Users/limke_msg9rxa/Downloads/Coding/AWS-Deploy/backend/terraform/envs/dev
terraform apply
```

### Step 3: Rebuild & Deploy Frontend

```bash
cd /mnt/c/Users/limke_msg9rxa/Downloads/Coding/AWS-Deploy/frontend
npm run build

# Upload to S3
BUCKET_NAME=$(cd ../backend/terraform/envs/dev && terraform output -raw static_site_bucket)
aws s3 sync dist/ s3://$BUCKET_NAME --delete

echo "✅ Frontend deployed"
```

### Step 4: Clear Browser Cache

- Open DevTools (F12)
- Right-click refresh button → "Empty Cache and Hard Reload"
- Or use Incognito/Private window

---

## ✅ Expected Behavior

### Test 1: Empty State (No Interactions)

```
1. Open homepage
2. Look at "Recommended for You" section
   ✅ Should show: "Start browsing to get recommendations"
   ❌ Should NOT show any products
```

### Test 2: First Product View

```
1. Click "Browse Products"
2. Click on "Wireless Bluetooth Headphones" (Electronics)
   → Goes to product detail page
3. Click browser back button
   → Returns to products page
4. Go to homepage
   ✅ Should show: Electronics products in recommendations
   ❌ Should NOT include "Wireless Bluetooth Headphones" (already viewed)
```

### Test 3: Category Switch

```
1. From products page, click "Laptop Backpack" (Accessories)
   → Goes to product detail page
2. Click back button
   → Returns to products page
3. Go to homepage
   ✅ Should show: Accessories products (most recent category)
   ❌ Should NOT show Electronics anymore
```

### Test 4: Multiple Views in Same Category

```
1. View 3 different Electronics products (click each one, then back)
2. Go to homepage
   ✅ Should show: Electronics products
   ✅ Should NOT show the 3 products you already viewed
```

---

## 🔍 Debugging

### Check if interactions are being tracked:

```bash
# View all interactions in DynamoDB
aws dynamodb scan \
  --table-name aws-ecommerce-dev-user-interactions \
  --region us-east-1 \
  --max-items 20
```

Expected output after viewing a product:

```json
{
  "userId": { "S": "user-demo-123" },
  "productId": { "S": "prod-1" },
  "eventType": { "S": "product-view" },
  "category": { "S": "Electronics" },
  "timestamp": { "S": "2025-10-31T12:34:56.789Z" }
}
```

### Check recommendations API response:

```bash
# Get your API endpoint
API_ENDPOINT=$(cd /mnt/c/Users/limke_msg9rxa/Downloads/Coding/AWS-Deploy/backend/terraform/envs/dev && terraform output -raw api_endpoint)

# Test recommendations endpoint
curl "$API_ENDPOINT/recommendations?userId=user-demo-123"
```

Expected responses:

- **No interactions:** `[]` (empty array)
- **Has interactions:** Array of products from most recent category

### Browser Console Checks:

Open DevTools (F12) and check:

1. **Network Tab** when viewing product:
   - POST request to `/events` → Status 200 ✅
2. **Network Tab** when loading products page:
   - GET request to `/recommendations?userId=user-demo-123` → Status 200 ✅
3. **Console Tab** for errors:
   - No errors related to recommendations ✅

---

## 🐛 Common Issues

### Issue: Still seeing products on first load

**Cause:** Old interactions in database  
**Fix:** Run Step 1 to clear interactions table

### Issue: Recommendations not updating

**Cause:** Browser cache  
**Fix:** Hard refresh (Ctrl+Shift+R) or clear cache

### Issue: "Start browsing" message doesn't show

**Cause:** Backend not deployed  
**Fix:** Run `terraform apply` to deploy Lambda changes

### Issue: Products still showing after clearing database

**Cause:** Frontend cache  
**Fix:** Clear localStorage:

```javascript
// In browser console:
localStorage.clear();
location.reload();
```

---

## 📊 Verification Checklist

- [ ] Empty recommendations section shows "Start browsing" message
- [ ] Viewing a product tracks the event (check DynamoDB)
- [ ] Returning to products page triggers recommendation reload
- [ ] Homepage shows recommendations from most recent category
- [ ] Viewed products are excluded from recommendations
- [ ] Switching categories updates recommendations
- [ ] No console errors in browser DevTools

---

## 🎯 Success Criteria

Your recommendation system is working correctly when:

1. ✅ New users see "Start browsing to get recommendations"
2. ✅ After viewing 1 product, recommendations show that category
3. ✅ After viewing different category, recommendations switch
4. ✅ Viewed products are never recommended
5. ✅ No page refresh needed (auto-updates when navigating back)

If all 5 criteria pass → System is working! 🎉
