# Vue.js Frontend for Coupon Service

This is a Vue 3 + Vite frontend application integrated with JWT authentication.

## Features

- ✅ User Registration & Login
- ✅ JWT Token Authentication
- ✅ Role-Based Access Control (Admin/User)
- ✅ User Dashboard
- ✅ Admin Panel for User Management
- ✅ Password Change Functionality
- ✅ Protected Routes
- ✅ Responsive Design

## Quick Start

### Prerequisites

- Node.js 18+ and npm

### Installation

```bash
cd frontend
npm install
```

### Development

```bash
npm run dev
```

The frontend will be available at http://localhost:3000

The API proxy is configured to forward `/api` requests to `http://localhost:8000`

### Build for Production

```bash
npm run build
npm run preview
```

## Project Structure

```
frontend/
├── src/
│   ├── assets/          # Static assets and global styles
│   ├── components/      # Reusable Vue components
│   ├── router/          # Vue Router configuration
│   ├── services/        # API service layer
│   │   ├── api.js       # Axios instance with interceptors
│   │   └── auth.js      # Authentication API methods
│   ├── stores/          # Pinia state management
│   │   └── auth.js      # Authentication store
│   ├── views/           # Page components
│   │   ├── HomeView.vue
│   │   ├── LoginView.vue
│   │   ├── RegisterView.vue
│   │   ├── DashboardView.vue
│   │   └── AdminView.vue
│   ├── App.vue          # Root component
│   └── main.js          # Application entry point
├── index.html
├── vite.config.js
└── package.json
```

## Authentication Flow

1. **Registration/Login**: User submits credentials → API returns JWT token
2. **Token Storage**: Token stored in localStorage and Pinia store
3. **API Requests**: Axios interceptor adds `Authorization: Bearer {token}` header
4. **Route Protection**: Router guards check authentication before navigation
5. **Token Expiration**: Interceptor catches 401 errors and redirects to login

## Available Routes

- `/` - Home page (public)
- `/login` - Login page (guest only)
- `/register` - Registration page (guest only)
- `/dashboard` - User dashboard (requires auth)
- `/admin` - Admin panel (requires admin role)

## Environment Variables

Create a `.env` file in the frontend directory (optional):

```env
VITE_API_URL=http://localhost:8000
```

## API Integration

The frontend uses Axios with interceptors for:

- **Request Interceptor**: Automatically adds JWT token to all requests
- **Response Interceptor**: Handles 401 errors and redirects to login

Example API call:

```javascript
import { authService } from '@/services/auth'

// Login
const result = await authService.login(email, password)

// Get users (admin only)
const users = await authService.getUsers()
```

## State Management

Uses Pinia for state management. The auth store provides:

```javascript
import { useAuthStore } from '@/stores/auth'

const authStore = useAuthStore()

// State
authStore.token        // JWT token
authStore.user         // Current user object

// Getters
authStore.isAuthenticated  // Boolean
authStore.isAdmin          // Boolean

// Actions
await authStore.login(email, password)
await authStore.register(name, email, password)
await authStore.changePassword(current, new)
authStore.logout()
```

## Styling

- Modern gradient UI with purple theme
- Responsive design works on mobile, tablet, and desktop
- Card-based layouts
- Smooth transitions and hover effects

## Development Tips

1. **Hot Module Replacement**: Changes auto-reload during development
2. **Vue DevTools**: Install browser extension for debugging
3. **API Proxy**: Vite proxy handles CORS during development
4. **Console Errors**: Check browser console for API errors

## Production Deployment

1. Build the frontend:
   ```bash
   npm run build
   ```

2. The `dist/` folder contains the production build

3. Serve with any static file server:
   ```bash
   npm run preview
   ```

4. Or deploy to:
   - Vercel
   - Netlify
   - AWS S3 + CloudFront
   - Any static hosting service

## Security Notes

- Tokens stored in localStorage (consider httpOnly cookies for production)
- All admin routes protected by role checks
- API handles final authorization
- Use HTTPS in production
- Set proper CORS headers on backend

## Troubleshooting

**API Connection Issues:**
- Ensure backend is running on port 8000
- Check browser console for CORS errors
- Verify proxy configuration in `vite.config.js`

**Authentication Failures:**
- Clear localStorage and try again
- Check token expiration
- Verify credentials with backend

**Build Errors:**
- Delete `node_modules` and run `npm install` again
- Clear Vite cache: `rm -rf node_modules/.vite`

## Next Steps

- Add more coupon management features
- Implement book creation UI
- Add coupon redemption interface
- Create analytics dashboard
- Add email verification
- Implement password reset
- Add refresh token support

## License

MIT
