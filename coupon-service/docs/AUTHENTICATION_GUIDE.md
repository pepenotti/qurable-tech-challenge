# Authentication & Authorization Guide

## Overview

The Coupon Service includes JWT-based authentication with role-based access control (RBAC). All sensitive operations require authentication, and admin functions require admin role.

## Quick Start

### 1. Register a New User
```bash
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Alice",
    "email": "alice@example.com",
    "password": "demo123"
  }'
```

### 2. Login
```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "alice@example.com",
    "password": "demo123"
  }'
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "user_id": "...",
    "email": "alice@example.com",
    "role": "USER"
  }
}
```

### 3. Use the Token
```bash
curl http://localhost:8000/api/v1/users/me/coupons \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

## Features

### ✅ Security Features
- **JWT Tokens**: Secure, stateless authentication
- **Password Hashing**: Bcrypt with cost factor 12
- **Token Expiration**: 24 hours (configurable)
- **RBAC**: Role-based access control (USER/ADMIN)

### 🔒 Protected Endpoints
All coupon operations require authentication:
- Assign coupons
- Lock/unlock coupons
- Redeem coupons
- View user coupons
- Manage books

Admin-only operations:
- View all users
- Create/manage pools
- Bulk distribution

## User Roles

### USER Role
- Manage own coupons (view, lock, unlock, redeem)
- Assign coupons to themselves
- View available books

### ADMIN Role  
- All USER permissions
- Create and manage books
- Create and manage user pools
- Bulk distribution to pools
- View all users and their coupons

## Frontend Authentication

The Vue 3 frontend handles authentication automatically:

### Login Flow
1. User enters email/password on login page
2. Frontend calls `/api/v1/auth/login`
3. Token stored in Pinia store + localStorage
4. Token included in all API requests via Axios interceptor
5. Auto-redirect to login on 401 errors

### Route Protection
```javascript
// router/index.js
router.beforeEach((to, from, next) => {
  const authStore = useAuthStore()
  
  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    next('/login')
  } else {
    next()
  }
})
```

### API Client Setup
```javascript
// services/api.js
axios.interceptors.request.use(config => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})
```

## API Endpoints

### Authentication
- `POST /api/v1/auth/register` - Register new user
- `POST /api/v1/auth/login` - Login
- `GET /api/v1/auth/me` - Get current user

### User Management
- `GET /api/v1/auth/admin/users` - List all users (admin only)
- `GET /api/v1/users/{id}` - Get user details
- `PATCH /api/v1/users/{id}` - Update user
- `GET /api/v1/users/search/by-email` - Search by email

## Testing

### Mock Users
The init_db.py script creates these test users:

**Admin:**
- Email: `admin@example.com`
- Password: `admin123`
- Role: ADMIN

**Regular Users:**
- alice@example.com / demo123
- bob@example.com / demo123
- charlie@example.com / demo123
- diana@example.com / demo123
- eve@example.com / demo123

### Test Auth Flow
```bash
cd coupon-service
./test_auth.sh
```

This script tests:
1. ✅ User registration
2. ✅ User login
3. ✅ Token validation
4. ✅ Protected endpoint access
5. ✅ Admin-only endpoint access

## Security Configuration

### Environment Variables
```bash
# .env
SECRET_KEY=your-secret-key-here-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440  # 24 hours
```

### Password Requirements
- Minimum 6 characters (demo) 
- Production: Use stronger requirements
- Bcrypt hashing with cost factor 12

### Token Configuration
```python
# app/utils/auth.py
SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 1440))
```

## Error Handling

### Common Auth Errors

**401 Unauthorized**
```json
{
  "detail": "Could not validate credentials"
}
```
**Solution:** Token expired or invalid. Login again.

**403 Forbidden**
```json
{
  "detail": "Not enough permissions"
}
```
**Solution:** User lacks required role (e.g., not an admin).

**422 Validation Error**
```json
{
  "detail": [
    {
      "loc": ["body", "email"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```
**Solution:** Check request body format.

## Production Considerations

### Security Checklist
- [ ] Change SECRET_KEY to a strong random value
- [ ] Use HTTPS in production
- [ ] Implement rate limiting (slowapi + Redis)
- [ ] Add refresh tokens for longer sessions
- [ ] Implement password strength requirements
- [ ] Add account lockout after failed attempts
- [ ] Enable CORS only for trusted origins
- [ ] Add audit logging for auth events
- [ ] Implement 2FA for admin accounts
- [ ] Use secure password reset flow

### Token Management
- Store tokens securely (httpOnly cookies in production)
- Implement token refresh mechanism
- Add token revocation/blacklist
- Monitor for suspicious auth patterns

### Database Security
- Use environment variables for DB credentials
- Enable SSL/TLS for database connections
- Implement connection pooling limits
- Regular security audits

## Troubleshooting

### "Could not validate credentials"
- Token expired → Login again
- Token malformed → Check Authorization header format
- Secret key mismatch → Restart backend after .env changes

### "Not enough permissions"
- User role insufficient → Use admin account
- Endpoint requires authentication → Add token to request

### Frontend not receiving token
- Check CORS configuration
- Verify API URL in frontend config
- Check browser console for errors
- Verify Axios interceptor is configured

---

**Status**: ✅ Complete
**Security Level**: Demo (enhance for production)
**Token Type**: JWT (HS256)
**Session Length**: 24 hours
