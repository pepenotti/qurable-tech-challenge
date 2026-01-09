<template>
  <div class="book-detail-view">
    <!-- Back button -->
    <button @click="router.back()" class="btn btn-secondary mb-3">
      ← Back to Books
    </button>

    <!-- Loading state -->
    <div v-if="loading" class="loading-state">
      <p>⏳ Loading book details...</p>
    </div>

    <!-- Error state -->
    <div v-else-if="error" class="error-message">
      {{ error }}
    </div>

    <!-- Book details -->
    <div v-else-if="book" class="book-details">
      <!-- Header -->
      <div class="detail-header">
        <div>
          <h1>{{ book.name }}</h1>
          <p v-if="book.description" class="book-description">{{ book.description }}</p>
        </div>
        <span class="active-badge" :class="{ active: book.is_active }">
          {{ book.is_active ? 'Active' : 'Inactive' }}
        </span>
      </div>

      <!-- Stats Grid -->
      <div class="stats-grid">
        <div class="stat-card">
          <div class="stat-icon">📦</div>
          <div class="stat-info">
            <div class="stat-label">Total Codes</div>
            <div class="stat-value">{{ book.total_code_count }}</div>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon">👥</div>
          <div class="stat-info">
            <div class="stat-label">Max per User</div>
            <div class="stat-value">{{ book.max_redemptions_per_user }}</div>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon">🔄</div>
          <div class="stat-info">
            <div class="stat-label">Multi-Redemption</div>
            <div class="stat-value">{{ book.allow_multi_redemption ? 'Yes' : 'No' }}</div>
          </div>
        </div>
        <div class="stat-card" v-if="book.expiration_date">
          <div class="stat-icon">📅</div>
          <div class="stat-info">
            <div class="stat-label">Expires</div>
            <div class="stat-value">{{ formatDate(book.expiration_date) }}</div>
          </div>
        </div>
      </div>

      <!-- Additional Info -->
      <div class="info-section">
        <h2>Book Information</h2>
        <div class="info-grid">
          <div class="info-item">
            <strong>Book ID:</strong>
            <code>{{ book.book_id }}</code>
          </div>
          <div class="info-item">
            <strong>Owner ID:</strong>
            <code>{{ book.owner_id }}</code>
          </div>
          <div class="info-item" v-if="book.code_pattern">
            <strong>Code Pattern:</strong>
            <code>{{ book.code_pattern }}</code>
          </div>
          <div class="info-item" v-if="book.max_assignments_per_user">
            <strong>Max Assignments per User:</strong>
            <span>{{ book.max_assignments_per_user }}</span>
          </div>
          <div class="info-item">
            <strong>Created:</strong>
            <span>{{ formatDate(book.created_at) }}</span>
          </div>
          <div class="info-item" v-if="book.updated_at">
            <strong>Last Updated:</strong>
            <span>{{ formatDate(book.updated_at) }}</span>
          </div>
        </div>
      </div>

      <!-- Coupons List -->
      <div class="coupons-section">
        <div class="section-header">
          <h2>Coupons in This Book</h2>
          <button @click="fetchCoupons" class="btn btn-secondary btn-sm" :disabled="loadingCoupons">
            🔄 {{ loadingCoupons ? 'Refreshing...' : 'Refresh' }}
          </button>
        </div>

        <div v-if="loadingCoupons" class="loading-state">
          <p>⏳ Loading coupons...</p>
        </div>

        <div v-else-if="coupons.length === 0" class="empty-state">
          <p>📭 No coupons in this book yet</p>
        </div>

        <div v-else class="coupons-table">
          <table>
            <thead>
              <tr>
                <th>Code</th>
                <th>State</th>
                <th>Assigned To</th>
                <th>Redemptions</th>
                <th>Locked Until</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="coupon in coupons" :key="coupon.code">
                <td><code>{{ coupon.code }}</code></td>
                <td>
                  <span class="state-badge" :class="coupon.state.toLowerCase()">
                    {{ coupon.state }}
                  </span>
                </td>
                <td>
                  <span v-if="coupon.assigned_user_id">
                    <code class="user-id-short" :title="coupon.assigned_user_id">
                      {{ coupon.assigned_user_id.substring(0, 8) }}...
                    </code>
                  </span>
                  <span v-else-if="coupon.state === 'ASSIGNED' || coupon.state === 'LOCKED' || coupon.state === 'REDEEMED'" 
                        class="text-danger" 
                        title="State indicates assignment but user_id is missing">
                    ⚠️ Missing ID
                  </span>
                  <span v-else class="text-muted">—</span>
                </td>
                <td>
                  <span v-if="coupon.redemption_count > 0">
                    {{ coupon.redemption_count }} / {{ coupon.max_redemptions }}
                    <small v-if="coupon.has_redemptions_remaining" class="text-success">
                      ({{ coupon.remaining_redemptions }} left)
                    </small>
                  </span>
                  <span v-else class="text-muted">0 / {{ coupon.max_redemptions }}</span>
                </td>
                <td>
                  <span v-if="coupon.is_locked && coupon.locked_until">
                    <span class="text-warning">🔒</span>
                    {{ formatDate(coupon.locked_until) }}
                  </span>
                  <span v-else class="text-muted">—</span>
                </td>
                <td>
                  <button 
                    v-if="coupon.state === 'UNASSIGNED'"
                    @click="showAssignModal(coupon)"
                    class="btn btn-sm btn-primary"
                  >
                    👤 Assign
                  </button>
                  <span v-else class="text-muted">—</span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- Assign Coupon Modal -->
      <div v-if="showAssignModalFlag" class="modal-overlay" @click="showAssignModalFlag = false">
        <div class="modal-content" @click.stop>
          <h2>👤 Assign Coupon to User</h2>
          <p class="modal-subtitle">
            Code: <code>{{ selectedCoupon?.code }}</code>
          </p>

          <form @submit.prevent="handleAssignCoupon">
            <div class="form-group">
              <label>User ID or Email *</label>
              <div class="input-with-button">
                <input 
                  v-model="assignForm.userId" 
                  type="text" 
                  required 
                  placeholder="UUID or email (e.g., alice@example.com)"
                />
                <button 
                  v-if="assignForm.userId && assignForm.userId.includes('@')"
                  type="button"
                  @click="searchUserByEmail"
                  class="btn btn-secondary btn-sm"
                  :disabled="searchingUser"
                >
                  {{ searchingUser ? '🔍...' : '🔍 Look up' }}
                </button>
              </div>
              <small>
                💡 Enter an email to search, or paste a UUID directly. 
                The lookup button appears when you type an email address.
              </small>
            </div>

            <div class="modal-actions">
              <button type="button" @click="showAssignModalFlag = false" class="btn btn-secondary">
                Cancel
              </button>
              <button 
                type="submit" 
                class="btn btn-primary" 
                :disabled="assigningCoupon"
              >
                {{ assigningCoupon ? 'Assigning...' : '👤 Assign Coupon' }}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { booksApi, couponsApi, usersApi } from '@/services/api/index'

const router = useRouter()
const route = useRoute()

const book = ref(null)
const coupons = ref([])
const loading = ref(false)
const loadingCoupons = ref(false)
const error = ref(null)

// Assign modal state
const showAssignModalFlag = ref(false)
const selectedCoupon = ref(null)
const assigningCoupon = ref(false)
const searchingUser = ref(false)
const assignForm = ref({
  userId: ''
})

const formatDate = (dateString) => {
  if (!dateString) return 'N/A'
  return new Date(dateString).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

const fetchBook = async () => {
  loading.value = true
  error.value = null
  
  try {
    book.value = await booksApi.getBook(route.params.id)
  } catch (err) {
    error.value = err.response?.data?.detail || 'Failed to load book details'
    console.error('Error fetching book:', err)
  } finally {
    loading.value = false
  }
}

const fetchCoupons = async () => {
  loadingCoupons.value = true
  
  try {
    const response = await booksApi.getBookCoupons(route.params.id)
    coupons.value = response.coupons || response || []
    
    // Debug: Log the first coupon to see the structure
    if (coupons.value.length > 0) {
      console.log('Sample coupon data:', coupons.value[0])
      console.log('Total coupons loaded:', coupons.value.length)
    }
  } catch (err) {
    console.error('Error fetching coupons:', err)
  } finally {
    loadingCoupons.value = false
  }
}

const showAssignModal = (coupon) => {
  selectedCoupon.value = coupon
  assignForm.value.userId = ''
  showAssignModalFlag.value = true
}

const searchUserByEmail = async () => {
  const email = assignForm.value.userId.trim()
  
  if (!email.includes('@')) {
    alert('Please enter a valid email address')
    return
  }

  searchingUser.value = true
  
  try {
    const user = await usersApi.searchByEmail(email)
    assignForm.value.userId = user.user_id
    alert(`✅ Found user: ${user.name}\nUser ID: ${user.user_id}`)
  } catch (err) {
    const errorMsg = err.response?.data?.detail || err.message || 'User not found'
    alert(`❌ ${errorMsg}\n\nMake sure the email is correct:\n- alice@example.com\n- bob@example.com\n- charlie@example.com\n- diana@example.com\n- eve@example.com`)
    console.error('Error searching user:', err)
  } finally {
    searchingUser.value = false
  }
}

const handleAssignCoupon = async () => {
  if (!selectedCoupon.value || !assignForm.value.userId) {
    alert('Please enter a user ID or email')
    return
  }

  let userId = assignForm.value.userId.trim()

  // If it's an email, look it up first
  if (userId.includes('@')) {
    alert('Please click the 🔍 Look up button first to convert the email to a user ID')
    return
  }

  // Basic UUID validation
  const uuidPattern = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i
  if (!uuidPattern.test(userId)) {
    alert('⚠️ Invalid format. Please:\n1. Enter an email and click 🔍 Look up, OR\n2. Paste a valid UUID directly')
    return
  }

  assigningCoupon.value = true
  
  try {
    await couponsApi.assignSpecificCoupon(selectedCoupon.value.code, userId)
    
    alert(`✅ Successfully assigned coupon ${selectedCoupon.value.code}`)
    
    // Close modal
    showAssignModalFlag.value = false
    selectedCoupon.value = null
    assignForm.value.userId = ''
    
    // Refresh coupons list
    await fetchCoupons()
  } catch (err) {
    const errorMsg = err.response?.data?.detail || err.message || 'Failed to assign coupon'
    
    if (errorMsg.includes('not found') || errorMsg.includes('User')) {
      alert(`❌ User not found.\n\nThe user ID doesn't exist in the system.`)
    } else if (errorMsg.includes('maximum assignments') || errorMsg.includes('exceeded')) {
      alert(`❌ ${errorMsg}\n\nThis user has reached the maximum number of coupons from this book.`)
    } else if (errorMsg.includes('not available')) {
      alert(`❌ ${errorMsg}\n\nThis coupon is no longer available for assignment.`)
    } else {
      alert(`❌ ${errorMsg}`)
    }
    
    console.error('Error assigning coupon:', err)
  } finally {
    assigningCoupon.value = false
  }
}

onMounted(async () => {
  await fetchBook()
  await fetchCoupons()
})
</script>

<style scoped>
.book-detail-view {
  max-width: 1200px;
  margin: 0 auto;
}

.detail-header {
  display: flex;
  justify-content: space-between;
  align-items: start;
  margin-bottom: 2rem;
  padding-bottom: 1.5rem;
  border-bottom: 2px solid #e9ecef;
}

.detail-header h1 {
  margin: 0 0 0.5rem 0;
  font-size: 2rem;
  color: #212529;
}

.book-description {
  color: #6c757d;
  font-size: 1.1rem;
  margin: 0;
}

.active-badge {
  padding: 0.5rem 1rem;
  border-radius: 20px;
  font-size: 0.875rem;
  font-weight: 600;
  background: #dc3545;
  color: white;
}

.active-badge.active {
  background: #28a745;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1.5rem;
  margin-bottom: 2rem;
}

.stat-card {
  background: white;
  border: 2px solid #e9ecef;
  border-radius: 12px;
  padding: 1.5rem;
  display: flex;
  align-items: center;
  gap: 1rem;
  transition: all 0.3s;
}

.stat-card:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  transform: translateY(-2px);
}

.stat-icon {
  font-size: 2.5rem;
}

.stat-info {
  flex: 1;
}

.stat-label {
  font-size: 0.875rem;
  color: #6c757d;
  margin-bottom: 0.25rem;
}

.stat-value {
  font-size: 1.5rem;
  font-weight: 700;
  color: #212529;
}

.info-section,
.coupons-section {
  background: white;
  border: 2px solid #e9ecef;
  border-radius: 12px;
  padding: 2rem;
  margin-bottom: 2rem;
}

.info-section h2,
.coupons-section h2 {
  margin: 0 0 1.5rem 0;
  font-size: 1.5rem;
  color: #212529;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
}

.section-header h2 {
  margin: 0;
}

.info-grid {
  display: grid;
  gap: 1rem;
}

.info-item {
  display: flex;
  gap: 1rem;
  padding: 0.75rem;
  background: #f8f9fa;
  border-radius: 8px;
}

.info-item strong {
  min-width: 200px;
  color: #495057;
}

.info-item code {
  background: #e9ecef;
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  font-family: 'Courier New', monospace;
  font-size: 0.875rem;
}

.coupons-table {
  overflow-x: auto;
}

.coupons-table table {
  width: 100%;
  border-collapse: collapse;
}

.coupons-table th,
.coupons-table td {
  padding: 1rem;
  text-align: left;
  border-bottom: 1px solid #e9ecef;
}

.coupons-table th {
  background: #f8f9fa;
  font-weight: 600;
  color: #495057;
}

.coupons-table tbody tr:hover {
  background: #f8f9fa;
}

.state-badge {
  padding: 0.25rem 0.75rem;
  border-radius: 20px;
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: uppercase;
}

.state-badge.unassigned {
  background: #e9ecef;
  color: #495057;
}

.state-badge.assigned {
  background: #d1ecf1;
  color: #0c5460;
}

.state-badge.locked {
  background: #fff3cd;
  color: #856404;
}

.state-badge.redeemed {
  background: #d4edda;
  color: #155724;
}

.user-id-short {
  background: #e9ecef;
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  font-family: 'Courier New', monospace;
  font-size: 0.8rem;
  cursor: help;
}

.text-success {
  color: #28a745;
  font-weight: 600;
}

.text-warning {
  color: #ffc107;
}

.text-danger {
  color: #dc3545;
  font-weight: 600;
}

.text-muted {
  color: #6c757d;
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
  border-radius: 12px;
  max-width: 500px;
  width: 90%;
  max-height: 90vh;
  overflow-y: auto;
}

.modal-subtitle {
  color: #6c757d;
  margin-bottom: 1.5rem;
}

.modal-subtitle code {
  background: #e9ecef;
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  font-family: 'Courier New', monospace;
  color: #007bff;
}

.form-group {
  margin-bottom: 1.5rem;
}

.form-group label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 600;
  color: #495057;
}

.form-group input {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid #dee2e6;
  border-radius: 6px;
  font-size: 1rem;
}

.input-with-button {
  display: flex;
  gap: 0.5rem;
  align-items: stretch;
}

.input-with-button input {
  flex: 1;
}

.input-with-button .btn {
  white-space: nowrap;
  flex-shrink: 0;
}

.form-group input:focus {
  outline: none;
  border-color: #007bff;
  box-shadow: 0 0 0 3px rgba(0, 123, 255, 0.1);
}

.form-group small {
  display: block;
  margin-top: 0.5rem;
  color: #6c757d;
  font-size: 0.875rem;
}

.info-box {
  background: #e7f3ff;
  border: 1px solid #b3d9ff;
  border-radius: 8px;
  padding: 1rem;
  margin: 1rem 0;
}

.info-box strong {
  display: block;
  margin-bottom: 0.5rem;
  color: #0066cc;
}

.info-box p {
  margin: 0.5rem 0;
  font-size: 0.875rem;
}

.info-box ul {
  margin: 0.5rem 0;
  padding-left: 1.5rem;
  font-size: 0.875rem;
}

.info-box li {
  margin: 0.25rem 0;
  font-family: 'Courier New', monospace;
}

.info-box small {
  color: #0066cc;
  font-size: 0.8rem;
}

.modal-actions {
  display: flex;
  gap: 1rem;
  justify-content: flex-end;
  margin-top: 2rem;
}

.btn-sm {
  padding: 0.5rem 1rem;
  font-size: 0.875rem;
}
</style>
