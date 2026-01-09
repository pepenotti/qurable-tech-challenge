# 🚀 Getting Started Guide

Welcome to the Coupon Book Service! This guide will help you set up and run the complete full-stack application.

## ✨ What You're Getting

A production-ready coupon management system featuring:
- ✅ **FastAPI Backend** - Modern async Python with JWT authentication
- ✅ **Vue 3 Frontend** - Reactive UI with Pinia state management
- ✅ **PostgreSQL Database** - Robust data storage with ACID compliance
- ✅ **Docker Containerization** - Consistent development environment
- ✅ **Role-Based Access** - Separate User and Admin capabilities
- ✅ **State Machine** - Robust coupon lifecycle management
- ✅ **Concurrency Control** - PostgreSQL advisory locks prevent race conditions
- ✅ **Toast Notifications** - Modern, non-blocking user feedback

---

## 🚀 Quick Start

### Start the Application

**Terminal 1 - Backend:**
```bash
cd coupon-service
docker-compose up -d
```

**Terminal 2 - Frontend:**
```bash
cd coupon-service/frontend
npm install  # First time only
npm run dev
```

---

## 🌐 Access Your Application

Once started, open your browser:

| Service | URL | Credentials |
|---------|-----|-------------|
| **Frontend** | http://localhost:5173 | Register or use admin account |
| **API** | http://localhost:8000 | - |
| **API Docs** | http://localhost:8000/docs | Interactive API documentation |
| **Admin Account** | - | `admin@example.com` / `admin123456` |

---

## 📱 Application Features

### Public Pages
- **Home** - Landing page
- **Login** - User authentication
- **Register** - Create new account

### User Dashboard (Authenticated)
- View your coupons
- Manage your profile
- Change password

### Admin Panel (Admin Role Only)
- User management (CRUD)
- View all users
- Assign roles
- Delete users

---

## 🔐 Authentication Flow

### 1. Registration
```javascript
// User registers
POST /api/v1/auth/register
{
  "name": "John Doe",
  "email": "john@example.com",
  "password": "securepass123"
}

// Receives JWT token automatically
```

### 2. Login
```javascript
// User logs in
POST /api/v1/auth/login
{
  "email": "john@example.com",
  "password": "securepass123"
}

// Receives:
{
  "access_token": "eyJ...",
  "token_type": "bearer",
  "user": {
    "user_id": "...",
    "name": "John Doe",
    "email": "john@example.com",
    "role": "user",
    "is_active": true
  }
}
```

### 3. Authenticated Requests
```javascript
// All subsequent requests include JWT token
GET /api/v1/auth/me
Headers: {
  "Authorization": "Bearer eyJ..."
}
```

### 4. Token Storage
- Frontend stores JWT in `localStorage`
- Token included automatically in all API requests
- Auto-redirects to login if token expires

---

## 🛠️ Development Commands

### Backend Management

```bash
# View backend logs
docker-compose logs -f app

# Restart backend
docker-compose restart app

# Stop all services
docker-compose down

# Reset database (fresh start)
docker-compose down -v
docker-compose up -d

# Initialize database with mock data
docker-compose exec app python init_db.py
```

### Frontend Development

```bash
cd frontend

# Start dev server with hot reload
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview

# Lint and format code
npm run lint
```

### Testing

```bash
# Run comprehensive showcase tests (from coupon-service directory)
./showcase_tests.sh

# Test specific endpoints interactively
# Use the API docs at http://localhost:8000/docs
```

---

## 📂 Project Structure

```
coupon-service/
├── app/                          # Backend application
│   ├── api/v1/                   # API endpoints
│   │   ├── auth.py              # Authentication & user management
│   │   ├── books.py             # Coupon book management
│   │   ├── coupons.py           # Coupon operations
│   │   ├── pools.py             # Bulk distribution
│   │   └── users.py             # User endpoints
│   ├── models/                   # SQLAlchemy models
│   │   ├── user.py              # User & authentication
│   │   ├── book.py              # Coupon books
│   │   ├── coupon.py            # Coupons & state machine
│   │   └── redemption.py        # Redemption history
│   ├── services/                 # Business logic
│   │   ├── redemption_service.py    # Lock & redeem logic
│   │   ├── assignment_service.py    # Coupon assignment
│   │   └── pool_service.py          # Bulk distribution
│   ├── schemas/                  # Pydantic validation schemas
│   ├── utils/                    # Utilities
│   │   ├── auth.py              # JWT & password hashing
│   │   ├── enums.py             # State machine definitions
│   │   └── exceptions.py        # Custom exceptions
│   ├── config.py                 # Configuration
│   ├── database.py               # Database connection
│   └── main.py                   # FastAPI application
├── frontend/                     # Vue.js frontend
│   ├── src/
│   │   ├── views/               # Page components
│   │   │   ├── LoginView.vue
│   │   │   ├── BooksView.vue
│   │   │   ├── CouponsView.vue
│   │   │   └── AdminView.vue
│   │   ├── stores/              # Pinia state management
│   │   │   └── auth.js          # Auth state
│   │   ├── services/            # API client services
│   │   │   ├── api.js           # Axios instance
│   │   │   ├── auth.js          # Auth API
│   │   │   ├── books.js         # Books API
│   │   │   └── coupons.js       # Coupons API
│   │   ├── router/              # Vue Router
│   │   │   └── index.js         # Routes + guards
│   │   └── main.js              # App entry point
│   ├── .env                      # Frontend config
│   └── package.json              # Dependencies
├── docs/                         # Documentation
│   ├── SHOWCASE_GUIDE.md        # Demo walkthrough
│   ├── COUPON_STATE_FLOW.md     # State machine docs
│   ├── AUTHENTICATION_GUIDE.md  # Auth implementation
│   └── IMPLEMENTATION_STATUS.md # Feature checklist
├── init_db.py                    # Database initialization script
├── showcase_tests.sh             # Comprehensive test suite
├── docker-compose.yml            # Container orchestration
└── requirements.txt              # Python dependencies
```

---

## 🔧 Configuration

### Backend Environment Variables

Edit `.env` file:

```env
# Database
DATABASE_URL=postgresql+asyncpg://user:password@postgres:5432/dbname

# JWT Configuration
SECRET_KEY=your-secret-key-here  # Generate with: openssl rand -hex 32
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# App Configuration
APP_VERSION=2.0.0
DEBUG=true
```

### Frontend Environment Variables

Edit `frontend/.env`:

```env
# API URL
VITE_API_URL=http://localhost:8000/api/v1

# App Title
VITE_APP_TITLE=Coupon Service
```

---

## 🎨 Customization

### Adding New Pages

1. Create view component in `frontend/src/views/`
2. Add route in `frontend/src/router/index.js`
3. Add navigation link in your components

Example:
```javascript
// router/index.js
{
  path: '/profile',
  name: 'profile',
  component: () => import('@/views/ProfileView.vue'),
  meta: { requiresAuth: true }
}
```

### Adding API Endpoints

1. Add endpoint in `app/api/`
2. Add service method in `frontend/src/services/`
3. Use in components via store or direct API call

### Styling

The frontend uses vanilla CSS. You can:
- Add Tailwind CSS
- Use Bootstrap/Vuetify
- Create your own design system

---

## 🚨 Common Issues & Solutions

### Port Already in Use

**Backend (8000):**
```bash
# Find process using port 8000
lsof -i :8000
# Kill it
kill -9 <PID>
```

**Frontend (5173):**
```bash
# Find process using port 5173
lsof -i :5173
# Kill it
kill -9 <PID>
```

### CORS Errors

Make sure `app/main.py` includes frontend origin:
```python
allow_origins=["http://localhost:5173"],
```

### Database Connection Failed

```bash
# Check if postgres is running
docker-compose ps

# View postgres logs
docker-compose logs postgres

# Restart postgres
docker-compose restart postgres
```

### Token Expired

- Default token expiration is 30 minutes
- User will be auto-redirected to login
- Adjust in `app/config.py`: `ACCESS_TOKEN_EXPIRE_MINUTES`

---

## 📚 API Documentation

Full interactive API docs available at:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Authentication Endpoints

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/api/v1/auth/register` | Register new user | No |
| POST | `/api/v1/auth/login` | Login user | No |
| GET | `/api/v1/auth/me` | Get current user | Yes |
| POST | `/api/v1/auth/change-password` | Change password | Yes |
| GET | `/api/v1/auth/admin/users` | List all users | Admin |
| POST | `/api/v1/auth/admin/users` | Create user | Admin |
| GET | `/api/v1/auth/admin/users/{id}` | Get user | Admin |
| PATCH | `/api/v1/auth/admin/users/{id}` | Update user | Admin |
| DELETE | `/api/v1/auth/admin/users/{id}` | Delete user | Admin |

---

## 🔒 Security Best Practices

### For Development
- ✅ Already configured with secure defaults
- ✅ JWT tokens with expiration
- ✅ Password hashing with bcrypt
- ✅ HTTPS-ready

### For Production

1. **Generate Secure Secret Key:**
   ```bash
   openssl rand -hex 32
   ```
   Update in `.env`

2. **Update CORS Origins:**
   ```python
   allow_origins=["https://your-domain.com"],
   ```

3. **Enable HTTPS Only:**
   - Configure SSL certificates
   - Set secure cookies
   - Use HTTPS URLs

4. **Environment Variables:**
   - Never commit `.env` files
   - Use secrets management (AWS Secrets Manager, etc.)

5. **Rate Limiting:**
   - Add rate limiting to login endpoint
   - Prevent brute force attacks

6. **Monitoring:**
   - Set up logging
   - Monitor failed login attempts
   - Track API usage

---

## 📈 Next Steps

### Immediate
1. ✅ Start the application (`./start.sh`)
2. ✅ Test login with admin account
3. ✅ Explore the API docs
4. ✅ Register a new user

### Short Term
- Add coupon management views
- Implement coupon book features
- Customize the UI/UX
- Add user profile page
- Implement password reset

### Long Term
- Add email verification
- Implement OAuth providers (Google, GitHub)
- Add two-factor authentication
- Create mobile app
- Set up CI/CD pipeline

---

## 🤝 Documentation Resources

### Getting Started
- **This Guide** - Setup and configuration
- **[Main README](../README.md)** - Project overview
- **[Challenge Summary](../../CHALLENGE_SUMMARY.md)** - Original requirements

### Feature Documentation
- **[Showcase Guide](./docs/SHOWCASE_GUIDE.md)** - Demo walkthrough and testing
- **[Coupon State Flow](./docs/COUPON_STATE_FLOW.md)** - State machine details
- **[Feature Checklist](./docs/FEATURE_CHECKLIST.md)** - Implementation status

### Technical Documentation
- **[Authentication Guide](./docs/AUTHENTICATION_GUIDE.md)** - Auth implementation
- **[Implementation Status](./docs/IMPLEMENTATION_STATUS.md)** - Complete feature overview
- **[Architecture Diagrams](../../diagrams/README.md)** - Visual system design

### Interactive API Docs
- **Swagger UI**: http://localhost:8000/docs (try it out live!)
- **ReDoc**: http://localhost:8000/redoc (clean API reference)

---

## 🎉 You're Ready!

Your full-stack coupon service is complete and ready to run:

```bash
# Start backend
docker-compose up -d

# Start frontend (in another terminal)
cd frontend && npm run dev
```

Then open **http://localhost:5173** in your browser! 🚀

### Next Steps
1. ✅ Explore the **[Showcase Guide](./docs/SHOWCASE_GUIDE.md)** for a complete demo
2. ✅ Review **[Architecture Diagrams](../../diagrams/README.md)** to understand the system
3. ✅ Run `./showcase_tests.sh` to verify all features work
4. ✅ Check the **API docs** at http://localhost:8000/docs

---

**Last Updated**: January 9, 2026  
**Project**: Coupon Book Service  
**Stack**: FastAPI + Vue 3 + PostgreSQL + Docker
