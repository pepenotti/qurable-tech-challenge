<template>
  <div class="coupons-view">
    <!-- SHOWCASE BANNER -->
    <div class="showcase-banner">
      <h3>🎯 SHOWCASE MODE ACTIVE</h3>
      <p>
        All actions are visible regardless of state to demonstrate API validation and error handling.
        Try invalid actions to see clear error messages from the backend!
      </p>
      <ul class="showcase-features">
        <li>✅ State machine validation</li>
        <li>🔒 PostgreSQL advisory locks for concurrency</li>
        <li>⚠️ Clear error messages for invalid operations</li>
        <li>🎯 Demonstrates all challenge requirements</li>
      </ul>
    </div>

    <div class="page-header">
      <h1>🎟️ My Coupons</h1>
      <button @click="refreshCoupons" class="btn btn-secondary" :disabled="couponsStore.loading.coupons">
        🔄 {{ couponsStore.loading.coupons ? 'Refreshing...' : 'Refresh' }}
      </button>
    </div>

    <!-- Toast Notification -->
    <transition name="slide-fade">
      <div v-if="toast.show" :class="['toast-notification', toast.type]">
        <div class="toast-icon">{{ toast.icon }}</div>
        <div class="toast-content">
          <div class="toast-title">{{ toast.title }}</div>
          <div class="toast-message">{{ toast.message }}</div>
        </div>
        <button @click="hideToast" class="toast-close">×</button>
      </div>
    </transition>

    <!-- Error message -->
    <div v-if="couponsStore.error" class="error-message">
      {{ couponsStore.error }}
      <button @click="couponsStore.clearError()" class="close-btn">×</button>
    </div>

    <!-- Stats -->
    <div class="stats-row">
      <div class="stat-badge">
        <span class="stat-label">Total:</span>
        <span class="stat-value">{{ couponsStore.stats.total }}</span>
      </div>
      <div class="stat-badge available">
        <span class="stat-label">Available:</span>
        <span class="stat-value">{{ couponsStore.stats.available }}</span>
      </div>
      <div class="stat-badge locked">
        <span class="stat-label">Locked:</span>
        <span class="stat-value">{{ couponsStore.stats.locked }}</span>
      </div>
      <div class="stat-badge redeemed">
        <span class="stat-label">Redeemed:</span>
        <span class="stat-value">{{ couponsStore.stats.redeemed }}</span>
      </div>
    </div>

    <!-- Tabs for different coupon states -->
    <div class="tabs">
      <button 
        v-for="tab in tabs" 
        :key="tab.value" 
        @click="activeTab = tab.value"
        :class="{ active: activeTab === tab.value }"
        class="tab-button"
      >
        {{ tab.label }} ({{ tab.count }})
      </button>
    </div>

    <!-- Coupons List -->
    <div v-if="couponsStore.loading.coupons" class="loading-state">
      <p>⏳ Loading coupons...</p>
    </div>

    <div v-else-if="filteredCoupons.length === 0" class="empty-state">
      <p>📭 No {{ activeTab }} coupons yet</p>
      <router-link to="/books" class="btn btn-primary">
        🔍 Browse Books
      </router-link>
    </div>

    <div v-else class="coupons-grid">
      <div v-for="coupon in filteredCoupons" :key="coupon.code" class="coupon-card" :class="coupon.state.toLowerCase()">
        <div class="coupon-header">
          <h3>{{ coupon.code }}</h3>
          <span class="state-badge" :class="coupon.state.toLowerCase()">
            {{ coupon.state }}
          </span>
        </div>

        <div class="coupon-details">
          <div class="detail-row">
            <span class="label">Book ID:</span>
            <span class="value">{{ coupon.book_id }}</span>
          </div>
          <div class="detail-row">
            <span class="label">Max Redemptions:</span>
            <span class="value">{{ coupon.redemption_count }}/{{ coupon.max_redemptions }}</span>
          </div>
          <div class="detail-row">
            <span class="label">Created:</span>
            <span class="value">{{ formatDate(coupon.created_at) }}</span>
          </div>
          <div v-if="coupon.locked_until" class="detail-row">
            <span class="label">Locked Until:</span>
            <span class="value">{{ formatTime(coupon.locked_until) }}</span>
          </div>
        </div>

        <div class="coupon-actions">
          <!-- SHOWCASE MODE: Show all possible actions with clear feedback -->
          
          <!-- ASSIGNED state actions -->
          <template v-if="coupon.state === 'ASSIGNED'">
            <button 
              @click="handleRedeem(coupon.code)" 
              class="btn btn-success btn-sm"
              :disabled="couponsStore.loading.action"
              title="Redeem this coupon immediately"
            >
              ✅ Redeem
            </button>
            <button 
              @click="handleLock(coupon.code)" 
              class="btn btn-secondary btn-sm"
              :disabled="couponsStore.loading.action"
              title="Lock temporarily - useful for testing concurrency"
            >
              🔒 Lock
            </button>
          </template>

          <!-- LOCKED state actions - SHOWCASE: Show all buttons to demonstrate validation -->
          <template v-if="coupon.state === 'LOCKED'">
            <button 
              @click="handleRedeem(coupon.code)" 
              class="btn btn-danger btn-sm"
              :disabled="couponsStore.loading.action"
              title="⚠️ Try to redeem locked coupon - API will reject with clear error"
            >
              ❌ Try Redeem (Will Fail)
            </button>
            <button 
              @click="handleUnlock(coupon.code)" 
              class="btn btn-warning btn-sm"
              :disabled="couponsStore.loading.action"
              title="Unlock to make redeemable again"
            >
              🔓 Unlock
            </button>
            <button 
              @click="handleLock(coupon.code)" 
              class="btn btn-secondary btn-sm"
              :disabled="couponsStore.loading.action"
              title="⚠️ Try to re-lock - API will show it's already locked"
            >
              🔒 Try Lock (Already Locked)
            </button>
          </template>

          <!-- REDEEMED state actions - SHOWCASE: Show buttons to demonstrate terminal state -->
          <template v-if="coupon.state === 'REDEEMED'">
            <span class="redeemed-badge">✅ Redeemed</span>
            <button 
              @click="handleRedeem(coupon.code)" 
              class="btn btn-outline btn-sm"
              :disabled="couponsStore.loading.action"
              title="⚠️ Try to redeem again - API will explain why it's not allowed"
            >
              🔄 Try Redeem Again (Terminal State)
            </button>
            <button 
              @click="handleLock(coupon.code)" 
              class="btn btn-outline btn-sm"
              :disabled="couponsStore.loading.action"
              title="⚠️ Try to lock redeemed coupon - API will reject"
            >
              🔒 Try Lock (Invalid)
            </button>
          </template>

          <!-- UNASSIGNED state (shouldn't show here but for completeness) -->
          <template v-if="coupon.state === 'UNASSIGNED'">
            <span class="info-badge">⚠️ Not assigned to you</span>
          </template>

          <!-- EXPIRED state -->
          <template v-if="coupon.state === 'EXPIRED'">
            <span class="expired-badge">⏰ Expired</span>
            <button 
              @click="handleRedeem(coupon.code)" 
              class="btn btn-outline btn-sm"
              :disabled="couponsStore.loading.action"
              title="⚠️ Try to redeem expired coupon - API will reject"
            >
              ❌ Try Redeem (Expired)
            </button>
          </template>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useCouponsStore } from '@/stores/coupons'

const couponsStore = useCouponsStore()

const activeTab = ref('available')

// Toast notification state
const toast = ref({
  show: false,
  type: 'success', // 'success', 'error', 'warning'
  icon: '✅',
  title: '',
  message: ''
})

let toastTimeout = null

const showToast = (type, title, message, duration = 4000) => {
  // Clear existing timeout
  if (toastTimeout) {
    clearTimeout(toastTimeout)
  }

  const icons = {
    success: '✅',
    error: '❌',
    warning: '⚠️',
    info: '💡'
  }

  toast.value = {
    show: true,
    type,
    icon: icons[type] || '✅',
    title,
    message
  }

  toastTimeout = setTimeout(() => {
    hideToast()
  }, duration)
}

const hideToast = () => {
  toast.value.show = false
  if (toastTimeout) {
    clearTimeout(toastTimeout)
  }
}

const tabs = computed(() => [
  { label: 'Available', value: 'available', count: couponsStore.stats.available },
  { label: 'Locked', value: 'locked', count: couponsStore.stats.locked },
  { label: 'Redeemed', value: 'redeemed', count: couponsStore.stats.redeemed },
  { label: 'All', value: 'all', count: couponsStore.stats.total }
])

const filteredCoupons = computed(() => {
  switch (activeTab.value) {
    case 'available':
      return couponsStore.availableCoupons
    case 'locked':
      return couponsStore.lockedCoupons
    case 'redeemed':
      return couponsStore.redeemedCoupons
    default:
      return couponsStore.myCoupons
  }
})

onMounted(() => {
  refreshCoupons()
})

const refreshCoupons = async () => {
  await couponsStore.fetchMyCoupons()
}

const handleLock = async (code) => {
  const coupon = couponsStore.myCoupons.find(c => c.code === code)
  const state = coupon?.state || 'UNKNOWN'
  
  try {
    await couponsStore.lockCoupon(code)
    showToast('success', 'SUCCESS!', `Coupon ${code} locked for 5 minutes! 💡 Uses PostgreSQL advisory locks.`)
  } catch (error) {
    const errorDetail = error.response?.data?.detail || error.message
    const statusCode = error.response?.status || 'Unknown'
    
    showToast('error', `API Validation Error (HTTP ${statusCode})`, `${errorDetail}\n\n💡 This demonstrates state machine validation!`, 6000)
  }
}

const handleUnlock = async (code) => {
  const coupon = couponsStore.myCoupons.find(c => c.code === code)
  const state = coupon?.state || 'UNKNOWN'
  
  try {
    await couponsStore.unlockCoupon(code)
    showToast('success', 'SUCCESS!', `Coupon ${code} unlocked! 💡 Advisory lock released.`)
  } catch (error) {
    const errorDetail = error.response?.data?.detail || error.message
    const statusCode = error.response?.status || 'Unknown'
    
    showToast('error', `API Validation Error (HTTP ${statusCode})`, errorDetail, 5000)
  }
}

const handleRedeem = async (code) => {
  // For showcase: Get current coupon state
  const coupon = couponsStore.myCoupons.find(c => c.code === code)
  const state = coupon?.state || 'UNKNOWN'
  
  try {
    await couponsStore.redeemCoupon(code)
    showToast('success', 'SUCCESS!', `Coupon ${code} redeemed successfully!`)
  } catch (error) {
    // Extract detailed error message from API response
    const errorDetail = error.response?.data?.detail || error.message
    const statusCode = error.response?.status || 'Unknown'
    
    showToast('error', `API Validation Error (HTTP ${statusCode})`, `${errorDetail}\n\n💡 This demonstrates backend validation!`, 6000)
  }
}

const formatDate = (dateString) => {
  if (!dateString) return 'N/A'
  return new Date(dateString).toLocaleDateString()
}

const formatTime = (dateString) => {
  if (!dateString) return 'N/A'
  return new Date(dateString).toLocaleString()
}
</script>

<style scoped>
.coupons-view {
  max-width: 1200px;
}

/* Toast Notification Styles */
.toast-notification {
  position: fixed;
  top: 80px;
  right: 20px;
  min-width: 350px;
  max-width: 500px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  display: flex;
  align-items: start;
  gap: 1rem;
  padding: 1rem;
  z-index: 1000;
  border-left: 4px solid #28a745;
}

.toast-notification.error {
  border-left-color: #dc3545;
}

.toast-notification.warning {
  border-left-color: #ffc107;
}

.toast-notification.info {
  border-left-color: #17a2b8;
}

.toast-icon {
  font-size: 1.5rem;
  flex-shrink: 0;
}

.toast-content {
  flex: 1;
}

.toast-title {
  font-weight: 600;
  margin-bottom: 0.25rem;
  color: #212529;
}

.toast-message {
  font-size: 0.875rem;
  color: #6c757d;
  white-space: pre-line;
}

.toast-close {
  background: none;
  border: none;
  font-size: 1.5rem;
  color: #6c757d;
  cursor: pointer;
  padding: 0;
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.toast-close:hover {
  color: #212529;
}

/* Toast animations */
.slide-fade-enter-active {
  transition: all 0.3s ease;
}

.slide-fade-leave-active {
  transition: all 0.3s ease;
}

.slide-fade-enter-from {
  transform: translateX(100%);
  opacity: 0;
}

.slide-fade-leave-to {
  transform: translateX(100%);
  opacity: 0;
}

.showcase-banner {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 1.5rem;
  border-radius: 12px;
  margin-bottom: 2rem;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.showcase-banner h3 {
  margin: 0 0 0.5rem 0;
  font-size: 1.5rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.showcase-banner p {
  margin: 0.5rem 0;
  font-size: 1rem;
  opacity: 0.95;
}

.showcase-features {
  list-style: none;
  padding: 0;
  margin: 1rem 0 0 0;
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 0.5rem;
}

.showcase-features li {
  background: rgba(255, 255, 255, 0.2);
  padding: 0.5rem 1rem;
  border-radius: 6px;
  font-size: 0.9rem;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
}

.stats-row {
  display: flex;
  gap: 1rem;
  margin-bottom: 2rem;
  flex-wrap: wrap;
}

.stat-badge {
  padding: 0.75rem 1.5rem;
  background: #f8f9fa;
  border-radius: 8px;
  display: flex;
  gap: 0.5rem;
  align-items: center;
}

.stat-badge.available {
  background: #d4edda;
  border: 1px solid #c3e6cb;
}

.stat-badge.locked {
  background: #fff3cd;
  border: 1px solid #ffeeba;
}

.stat-badge.redeemed {
  background: #d1ecf1;
  border: 1px solid #bee5eb;
}

.stat-label {
  font-weight: 600;
  color: #666;
}

.stat-value {
  font-size: 1.25rem;
  font-weight: bold;
  color: #333;
}

.tabs {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 2rem;
  border-bottom: 2px solid #e9ecef;
}

.tab-button {
  padding: 0.75rem 1.5rem;
  background: none;
  border: none;
  border-bottom: 3px solid transparent;
  cursor: pointer;
  font-weight: 500;
  color: #6c757d;
  transition: all 0.3s;
}

.tab-button:hover {
  color: #495057;
}

.tab-button.active {
  color: #007bff;
  border-bottom-color: #007bff;
}

.loading-state,
.empty-state {
  text-align: center;
  padding: 3rem;
  color: #6c757d;
}

.empty-state p {
  font-size: 1.25rem;
  margin-bottom: 1rem;
}

.coupons-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 1.5rem;
}

.coupon-card {
  background: white;
  border: 2px solid #e9ecef;
  border-radius: 12px;
  padding: 1.5rem;
  transition: all 0.3s;
}

.coupon-card:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  transform: translateY(-2px);
}

.coupon-card.assigned {
  border-color: #28a745;
}

.coupon-card.locked {
  border-color: #ffc107;
}

.coupon-card.redeemed {
  border-color: #17a2b8;
  opacity: 0.8;
}

.coupon-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid #e9ecef;
}

.coupon-header h3 {
  margin: 0;
  font-size: 1.25rem;
  font-family: 'Courier New', monospace;
}

.state-badge {
  padding: 0.25rem 0.75rem;
  border-radius: 20px;
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: uppercase;
}

.state-badge.assigned {
  background: #d4edda;
  color: #155724;
}

.state-badge.locked {
  background: #fff3cd;
  color: #856404;
}

.state-badge.redeemed {
  background: #d1ecf1;
  color: #0c5460;
}

.coupon-details {
  margin-bottom: 1rem;
}

.detail-row {
  display: flex;
  justify-content: space-between;
  padding: 0.5rem 0;
  border-bottom: 1px solid #f8f9fa;
}

.detail-row .label {
  font-weight: 600;
  color: #6c757d;
}

.detail-row .value {
  color: #495057;
  font-family: 'Courier New', monospace;
}

.coupon-actions {
  display: flex;
  gap: 0.5rem;
  margin-top: 1rem;
  align-items: center;
}

.lock-hint {
  color: #856404;
  font-size: 0.875rem;
  font-style: italic;
}

.btn-sm {
  padding: 0.5rem 1rem;
  font-size: 0.875rem;
}

.btn-success {
  background: #28a745;
  color: white;
}

.btn-success:hover:not(:disabled) {
  background: #218838;
}

.btn-danger {
  background: #dc3545;
  color: white;
}

.btn-danger:hover:not(:disabled) {
  background: #c82333;
}

.btn-outline {
  background: white;
  border: 1px solid #6c757d;
  color: #6c757d;
}

.btn-outline:hover:not(:disabled) {
  background: #6c757d;
  color: white;
}

.redeemed-badge {
  background: #d1ecf1;
  color: #0c5460;
  padding: 0.5rem 1rem;
  border-radius: 4px;
  font-weight: 600;
}

.info-badge {
  background: #e7f3ff;
  color: #004085;
  padding: 0.5rem 1rem;
  border-radius: 4px;
  font-weight: 600;
}

.expired-badge {
  background: #f8d7da;
  color: #721c24;
  padding: 0.5rem 1rem;
  border-radius: 4px;
  font-weight: 600;
}

.redeemed-text {
  color: #17a2b8;
  font-weight: 600;
}
</style>
