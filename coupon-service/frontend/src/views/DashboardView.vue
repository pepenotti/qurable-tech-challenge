<template>
  <div class="dashboard">
    <h1>📊 Dashboard</h1>
    <p class="welcome">Welcome back, {{ authStore.user?.name }}!</p>

    <div class="stats-grid">
      <div class="stat-card">
        <div class="stat-icon">🎟️</div>
        <h3>My Coupons</h3>
        <p class="stat-value">{{ couponsStore.stats.available }}</p>
        <p class="stat-label">Available coupons</p>
      </div>

      <div class="stat-card">
        <div class="stat-icon">📚</div>
        <h3>My Books</h3>
        <p class="stat-value">{{ couponsStore.myBooks.length }}</p>
        <p class="stat-label">Coupon books owned</p>
      </div>

      <div class="stat-card">
        <div class="stat-icon">✅</div>
        <h3>Redeemed</h3>
        <p class="stat-value">{{ couponsStore.stats.redeemed }}</p>
        <p class="stat-label">Total redemptions</p>
      </div>
    </div>

    <div class="user-info-card">
      <h2>👤 User Profile</h2>
      <div class="info-grid">
        <div class="info-item">
          <strong>Name:</strong>
          <span>{{ authStore.user?.name }}</span>
        </div>
        <div class="info-item">
          <strong>Email:</strong>
          <span>{{ authStore.user?.email }}</span>
        </div>
        <div class="info-item">
          <strong>Role:</strong>
          <span class="badge" :class="authStore.user?.role">
            {{ authStore.user?.role?.toUpperCase() }}
          </span>
        </div>
        <div class="info-item">
          <strong>Status:</strong>
          <span class="badge" :class="{ active: authStore.user?.is_active }">
            {{ authStore.user?.is_active ? 'Active' : 'Inactive' }}
          </span>
        </div>
        <div class="info-item">
          <strong>Member Since:</strong>
          <span>{{ formatDate(authStore.user?.created_at) }}</span>
        </div>
      </div>
    </div>

    <div class="actions">
      <button @click="showChangePassword = true" class="btn btn-secondary">
        🔒 Change Password
      </button>
    </div>

    <!-- Change Password Modal -->
    <div v-if="showChangePassword" class="modal-overlay" @click="showChangePassword = false">
      <div class="modal-content" @click.stop>
        <h3>🔒 Change Password</h3>
        <form @submit.prevent="handleChangePassword">
          <div v-if="passwordError" class="error-message">
            {{ passwordError }}
          </div>
          <div v-if="passwordSuccess" class="success-message">
            Password changed successfully!
          </div>

          <div class="form-group">
            <label>Current Password</label>
            <input
              v-model="passwordForm.current"
              type="password"
              required
              minlength="8"
            />
          </div>

          <div class="form-group">
            <label>New Password</label>
            <input
              v-model="passwordForm.new"
              type="password"
              required
              minlength="8"
            />
          </div>

          <div class="form-group">
            <label>Confirm New Password</label>
            <input
              v-model="passwordForm.confirm"
              type="password"
              required
              minlength="8"
            />
          </div>

          <div class="modal-actions">
            <button type="button" @click="showChangePassword = false" class="btn btn-secondary">
              Cancel
            </button>
            <button type="submit" class="btn btn-primary" :disabled="passwordLoading">
              {{ passwordLoading ? 'Changing...' : 'Change Password' }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useCouponsStore } from '@/stores/coupons'

const authStore = useAuthStore()
const couponsStore = useCouponsStore()

const showChangePassword = ref(false)
const passwordForm = ref({
  current: '',
  new: '',
  confirm: '',
})
const passwordLoading = ref(false)
const passwordError = ref('')
const passwordSuccess = ref(false)

// Load user's coupons and books on mount
onMounted(async () => {
  await Promise.all([
    couponsStore.fetchMyCoupons(),
    couponsStore.fetchBooks()
  ])
})

const formatDate = (dateString) => {
  if (!dateString) return 'N/A'
  const date = new Date(dateString)
  return date.toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
  })
}

const handleChangePassword = async () => {
  passwordError.value = ''
  passwordSuccess.value = false

  if (passwordForm.value.new !== passwordForm.value.confirm) {
    passwordError.value = 'New passwords do not match'
    return
  }

  passwordLoading.value = true

  const result = await authStore.changePassword(
    passwordForm.value.current,
    passwordForm.value.new
  )

  passwordLoading.value = false

  if (result.success) {
    passwordSuccess.value = true
    passwordForm.value = { current: '', new: '', confirm: '' }
    setTimeout(() => {
      showChangePassword.value = false
      passwordSuccess.value = false
    }, 2000)
  } else {
    passwordError.value = result.error
  }
}
</script>

<style scoped>
.dashboard {
  max-width: 1000px;
}

h1 {
  color: #333;
  margin-bottom: 0.5rem;
}

.welcome {
  color: #6c757d;
  font-size: 1.125rem;
  margin-bottom: 2rem;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1.5rem;
  margin-bottom: 2rem;
}

.stat-card {
  background: white;
  padding: 1.5rem;
  border-radius: 10px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  text-align: center;
}

.stat-icon {
  font-size: 2.5rem;
  margin-bottom: 0.5rem;
}

.stat-card h3 {
  color: #667eea;
  font-size: 1rem;
  margin-bottom: 0.5rem;
}

.stat-value {
  font-size: 2rem;
  font-weight: bold;
  color: #333;
  margin: 0.5rem 0;
}

.stat-label {
  color: #6c757d;
  font-size: 0.875rem;
}

.user-info-card {
  background: white;
  padding: 2rem;
  border-radius: 10px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  margin-bottom: 2rem;
}

.user-info-card h2 {
  color: #667eea;
  margin-bottom: 1.5rem;
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1rem;
}

.info-item {
  display: flex;
  justify-content: space-between;
  padding: 0.75rem;
  background: #f8f9fa;
  border-radius: 5px;
}

.info-item strong {
  color: #495057;
}

.badge {
  padding: 0.25rem 0.75rem;
  border-radius: 20px;
  font-size: 0.875rem;
  font-weight: 600;
}

.badge.admin {
  background: #ffeaa7;
  color: #d63031;
}

.badge.user {
  background: #dfe6e9;
  color: #2d3436;
}

.badge.active {
  background: #55efc4;
  color: #00b894;
}

.actions {
  display: flex;
  gap: 1rem;
}

.btn {
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: 5px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s;
}

.btn-primary {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.btn-secondary {
  background: #f8f9fa;
  color: #495057;
  border: 1px solid #dee2e6;
}

.btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.2);
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.modal-content {
  background: white;
  padding: 2rem;
  border-radius: 10px;
  width: 90%;
  max-width: 400px;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.3);
}

.modal-content h3 {
  color: #667eea;
  margin-bottom: 1.5rem;
}

.form-group {
  margin-bottom: 1rem;
}

.form-group label {
  display: block;
  margin-bottom: 0.5rem;
  color: #333;
  font-weight: 500;
}

.form-group input {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid #ddd;
  border-radius: 5px;
  font-size: 1rem;
}

.form-group input:focus {
  outline: none;
  border-color: #667eea;
}

.error-message {
  background: #fee;
  color: #c33;
  padding: 0.75rem;
  border-radius: 5px;
  margin-bottom: 1rem;
}

.success-message {
  background: #efe;
  color: #3c3;
  padding: 0.75rem;
  border-radius: 5px;
  margin-bottom: 1rem;
}

.modal-actions {
  display: flex;
  gap: 1rem;
  margin-top: 1.5rem;
}

.modal-actions .btn {
  flex: 1;
}
</style>
