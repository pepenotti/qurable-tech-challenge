<template>
  <div id="app">
    <nav class="navbar">
      <div class="nav-brand">
        <h1>🎟️ Coupon Service</h1>
      </div>
      <div class="nav-links">
        <template v-if="authStore.isAuthenticated">
          <router-link to="/dashboard">Dashboard</router-link>
          <router-link to="/coupons">My Coupons</router-link>
          <router-link to="/books">Books</router-link>
          <router-link v-if="authStore.isAdmin" to="/pools">Pools</router-link>
          <router-link v-if="authStore.isAdmin" to="/admin">Admin</router-link>
          <span class="user-info">👤 {{ authStore.user?.name }}</span>
          <button @click="handleLogout" class="btn-logout">Logout</button>
        </template>
        <template v-else>
          <router-link to="/login">Login</router-link>
          <router-link to="/register">Register</router-link>
        </template>
      </div>
    </nav>

    <main class="main-content">
      <router-view />
    </main>

    <footer class="footer">
      <p>&copy; 2026 Coupon Service. All rights reserved.</p>
    </footer>
  </div>
</template>

<script setup>
import { useAuthStore } from '@/stores/auth'
import { useRouter } from 'vue-router'

const authStore = useAuthStore()
const router = useRouter()

const handleLogout = async () => {
  authStore.logout()
  router.push('/login')
}
</script>

<style scoped>
#app {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.navbar {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 1rem 2rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

.nav-brand h1 {
  margin: 0;
  font-size: 1.5rem;
}

.nav-links {
  display: flex;
  gap: 1.5rem;
  align-items: center;
}

.nav-links a {
  color: white;
  text-decoration: none;
  font-weight: 500;
  transition: opacity 0.3s;
}

.nav-links a:hover {
  opacity: 0.8;
}

.nav-links a.router-link-active {
  border-bottom: 2px solid white;
}

.user-info {
  font-weight: 500;
}

.btn-logout {
  background: rgba(255, 255, 255, 0.2);
  color: white;
  border: 1px solid white;
  padding: 0.5rem 1rem;
  border-radius: 5px;
  cursor: pointer;
  font-weight: 500;
  transition: all 0.3s;
}

.btn-logout:hover {
  background: white;
  color: #667eea;
}

.main-content {
  flex: 1;
  padding: 2rem;
  max-width: 1200px;
  margin: 0 auto;
  width: 100%;
}

.footer {
  background: #f8f9fa;
  text-align: center;
  padding: 1rem;
  color: #6c757d;
  border-top: 1px solid #dee2e6;
}
</style>
