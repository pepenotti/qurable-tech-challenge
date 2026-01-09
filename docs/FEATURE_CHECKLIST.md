# Coupon Service - Feature Implementation Checklist

## ✅ Completed Features

### 1. **Bulk Distribution to User Pools**
- **File**: `frontend/src/views/BooksView.vue`
- **Backend**: `POST /api/v1/pools/bulk-assign`
- **Location**: Books page → "🎲 Distribute to Pool" button
- **Test Steps**:
  1. Login as admin@example.com / admin123
  2. Go to Books page
  3. Find a book you own (all 4 books are owned by admin)
  4. Look for the purple "🎲 Distribute to Pool" button
  5. Select pool, mode (random/equal), and quantity
  6. Click Distribute

### 2. **Individual Coupon Assignment with Email Search**
- **File**: `frontend/src/views/BookDetailView.vue`
- **Backend**: 
  - `GET /api/v1/users/search/by-email?email={email}` (NEW)
  - `POST /api/v1/coupons/assign/{code}`
- **Location**: Book detail page → "👤 Assign" button on each UNASSIGNED coupon
- **Test Steps**:
  1. Go to Books → Click "👁️ View Details" on any book
  2. Find a coupon with state "UNASSIGNED"
  3. Click the "👤 Assign" button
  4. Type an email: alice@example.com
  5. Click "🔍 Look up" button (appears when you type @)
  6. Email converts to user ID automatically
  7. Click "👤 Assign Coupon"

### 3. **User ID Copy Feature**
- **File**: `frontend/src/views/PoolDetailView.vue`
- **Location**: Pools page → Pool details → User list
- **Test Steps**:
  1. Go to Pools page
  2. Click on any pool (e.g., "Beta Testers")
  3. Find the 📋 button next to each user's ID
  4. Click to copy full UUID to clipboard

## 🔧 Troubleshooting

### If Frontend Changes Don't Appear:

**Option 1: Hard Refresh**
- Chrome/Edge: Ctrl+Shift+R (Windows) or Cmd+Shift+R (Mac)
- Firefox: Ctrl+F5 (Windows) or Cmd+Shift+R (Mac)

**Option 2: Clear Browser Cache**
1. Open DevTools (F12)
2. Right-click the refresh button
3. Select "Empty Cache and Hard Reload"

**Option 3: Restart Frontend Dev Server**
```bash
# In the terminal where frontend is running:
# Press Ctrl+C to stop

cd frontend
npm run dev
```

**Option 4: Check for JavaScript Errors**
1. Open DevTools (F12)
2. Go to Console tab
3. Look for red error messages
4. If you see errors about missing imports or undefined components, the dev server needs restart

### If Backend Changes Don't Work:

```bash
docker-compose restart app
```

### Check Backend is Running:
```bash
curl http://localhost:8000/docs
# Should return HTML for Swagger docs

docker-compose logs app --tail=50
# Check for errors
```

## 📝 Test User Accounts

**Admin:**
- Email: admin@example.com
- Password: admin123

**Regular Users:**
- alice@example.com / demo123
- bob@example.com / demo123
- charlie@example.com / demo123
- diana@example.com / demo123
- eve@example.com / demo123

## 🎯 Quick Test Scenarios

### Scenario 1: Bulk Distribution
1. Login as admin
2. Books page → "Summer Sale 2026" → "🎲 Distribute to Pool"
3. Select "Beta Testers" (3 users)
4. Choose "Equal" mode, 5 coupons per user
5. Click Distribute
6. ✅ Should show 15 total coupons assigned (3 users × 5 each)

### Scenario 2: Email-Based Assignment
1. Login as admin
2. Books → "VIP Access Codes" → View Details
3. Find UNASSIGNED coupon → Click "👤 Assign"
4. Type: bob@example.com
5. Click "🔍 Look up"
6. ✅ Should show "Found user: Bob"
7. Click "👤 Assign Coupon"
8. ✅ Coupon state changes to ASSIGNED

### Scenario 3: Copy User ID
1. Pools → "Beta Testers"
2. Click 📋 next to Alice
3. ✅ Should see alert "User ID copied to clipboard!"
4. Go back to Books → any book details
5. Assign a coupon → paste the user ID
6. ✅ Should work without typing UUID manually

## 🐛 Common Issues

### Issue: "Distribute to Pool" button not showing
**Cause**: Field name mismatch
**Solution**: Check that book has `total_code_count > 0`
**Status**: ✅ Fixed - using correct field name

### Issue: Pool distribution modal stuck on "Distributing..."
**Cause**: Loading state not reset on error
**Solution**: Better error handling added
**Status**: ✅ Fixed

### Issue: Email search returns "User not found"
**Backend Fix**: Added `/users/search/by-email` endpoint
**Status**: ✅ Fixed
**Note**: Backend must be restarted for new endpoint

### Issue: Can't assign to email directly
**Solution**: Use the "🔍 Look up" button first
**Status**: ✅ Working as designed (requires lookup step)

## 📂 Modified Files

### Backend:
- `app/api/v1/users.py` - Added search_user_by_email endpoint
- `app/api/v1/pools.py` - Fixed get_pool to return user details (DONE EARLIER)

### Frontend:
- `frontend/src/services/api/users.js` - NEW file for user search
- `frontend/src/services/api/index.js` - Added usersApi export
- `frontend/src/views/BooksView.vue` - Added distribution modal and button
- `frontend/src/views/BookDetailView.vue` - Added email search to assign modal
- `frontend/src/views/PoolDetailView.vue` - Added copy user ID button

### Infrastructure:
- `docker-compose.yml` - Removed auto alembic migrations (DONE EARLIER)

## 🚀 What's Working

✅ User pools with full user details (name, email, added_at)
✅ Bulk distribution to pools (random and equal modes)
✅ Individual coupon assignment by email or UUID
✅ User ID copy-to-clipboard in pool details
✅ Email-to-UUID lookup
✅ Validation and error messages
✅ Modal UIs with previews and results
✅ Backend endpoints for all features
✅ Mock data for testing (1 admin, 5 users, 4 books, 3 pools, 200 coupons)

## 💾 Database State

Run this to check current data:
```bash
docker-compose exec -T app python init_db.py --with-mock-data

# OR if tables exist:
docker-compose exec -T app python init_db.py --drop --with-mock-data
```

Mock data includes:
- 4 coupon books (Summer Sale, VIP, Free Shipping, Beta Rewards)
- 200 total coupons
- 3 user pools with members
- 10 pre-assigned coupons
- 4 redeemed coupons (for demo)

## 🎨 UI Elements to Look For

1. **Books Page**:
   - Purple gradient button "🎲 Distribute to Pool" (on your books with codes)
   
2. **Book Detail Page**:
   - Green "👤 Assign" button in Actions column (UNASSIGNED coupons only)
   
3. **Pool Detail Page**:
   - User ID shown with "..." and 📋 copy button
   
4. **Distribution Modal**:
   - Pool dropdown
   - Mode selector (Random/Equal)
   - Preview box showing counts
   - Results section after distribution

5. **Assign Modal**:
   - Input accepts both email and UUID
   - "🔍 Look up" button appears when @ is typed
   - Success/error alerts with helpful messages
