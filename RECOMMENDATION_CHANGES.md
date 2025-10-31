# Recommendation System Changes

## Summary

Updated the recommendation system to use **most recent category** priority with recommendations updating when users return to the products page.

---

## Changes Made

### 1. Backend: `get_recommendations/app.py`

**Changed from:** Top 3 most frequent categories  
**Changed to:** Single most recent category

#### Key Changes:

- ✅ Sort interactions by timestamp (most recent first)
- ✅ Use only the most recent category for recommendations
- ✅ Don't fill with random products (return empty array if no interactions)
- ✅ Exclude already viewed products

```python
# Old: Top 3 categories
top_categories = category_counts.most_common(3)

# New: Most recent category only
sorted_interactions = sorted(interactions, key=lambda x: x.get('timestamp', ''), reverse=True)
most_recent_category = sorted_interactions[0]['category']
```

---

### 2. Frontend: `AppContext.tsx`

**Removed:** Add-to-cart event tracking for recommendations

```typescript
// REMOVED THIS:
// Track the add-to-cart event for recommendations
await actions.trackProductView(product);
```

Only product views are tracked now (simpler logic).

---

### 3. Frontend: `ProductsPage.tsx`

**Added:** Reload recommendations when page loads

```typescript
useEffect(() => {
  actions.loadRecommendations();
}, [actions]);
```

**How it works:**

1. User clicks product → Goes to ProductDetailPage → Event tracked
2. User clicks back → Returns to ProductsPage → Recommendations reload
3. Recommendations now show products from most recent category viewed

---

### 4. Frontend: `HomePage.tsx`

**Added:** Empty state message for recommendations

**Before:** Recommendations section hidden if empty  
**After:** Shows message: "Start browsing to get recommendations"

```tsx
{hasRecommendations ? (
  // Show recommendations
) : (
  <Box>
    <Text>Start browsing to get recommendations</Text>
    <Text>View products to see personalized recommendations here</Text>
    <Button>Browse Products</Button>
  </Box>
)}
```

---

## How It Works Now

### User Flow:

```
1. User opens homepage
   → Recommendations section shows: "Start browsing to get recommendations"

2. User clicks "Browse Products" → Goes to ProductsPage

3. User clicks on "Wireless Headphones" (Electronics category)
   → Goes to ProductDetailPage
   → Event tracked: {category: "Electronics", timestamp: "2025-10-31T..."}

4. User clicks back button → Returns to ProductsPage
   → useEffect triggers → loadRecommendations() called
   → Backend returns Electronics products (excluding viewed ones)

5. User goes to HomePage
   → Recommendations section now shows Electronics products

6. User clicks on "Laptop Backpack" (Accessories category)
   → Event tracked: {category: "Accessories", timestamp: "2025-10-31T..."}

7. User returns to ProductsPage
   → Recommendations update to show Accessories products
   → (Most recent category wins!)
```

---

## Technical Details

### Event Tracking (track_event Lambda)

- **Tracks:** `product-view` events only
- **Stores:** userId, productId, eventType, category, timestamp
- **Table:** DynamoDB user-interactions table

### Recommendation Logic (get_recommendations Lambda)

```python
1. Get all user interactions
2. Sort by timestamp (DESC)
3. Get most recent category
4. Query products from that category
5. Exclude already viewed products
6. Return up to 10 recommendations
```

### Priority System

- **Most recent category always wins**
- User views 10 Electronics → Recommendations show Electronics
- User views 1 Accessories → Recommendations immediately switch to Accessories
- Simple and predictable!

---

## What's NOT Tracked

❌ Add to cart events  
❌ Purchase events (should add this later)  
❌ Search queries  
❌ Time spent on page

Only **product-view** events are tracked to keep it simple.

---

## Testing the Changes

### Test 1: Empty State

1. Clear DynamoDB interactions table (or use new user)
2. Visit homepage
3. ✅ Should see "Start browsing to get recommendations"

### Test 2: Single Category

1. Visit 3 Electronics products
2. Return to homepage
3. ✅ Should see Electronics recommendations

### Test 3: Category Switching

1. Visit Electronics products → See Electronics recommendations
2. Visit Accessories products → See Accessories recommendations
3. ✅ Most recent category should show

### Test 4: No Manual Refresh Needed

1. View product → Go back to products page
2. ✅ Recommendations should auto-update (no F5 needed)

---

## Next Steps (Optional Improvements)

### Could Add Later:

1. **Purchase tracking** in CheckoutPage (stronger signal)
2. **Time decay** (older views matter less)
3. **Frequency + recency** hybrid (balance both)
4. **Multiple categories** (show top 2 recent categories)
5. **Collaborative filtering** (users who viewed X also viewed Y)

For now, keeping it simple with most recent category only! 🎯
