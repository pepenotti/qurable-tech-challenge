<template>
  <div class="books-view">
    <div class="page-header">
      <h1>📚 Coupon Books</h1>
      <button @click="showCreateModal = true" class="btn btn-primary">
        ➕ Create New Book
      </button>
    </div>

    <!-- Error message -->
    <div v-if="couponsStore.error" class="error-message">
      {{ couponsStore.error }}
      <button @click="couponsStore.clearError()" class="close-btn">×</button>
    </div>

    <!-- Loading state -->
    <div v-if="couponsStore.loading.books" class="loading-state">
      <p>⏳ Loading books...</p>
    </div>

    <!-- Empty state -->
    <div v-else-if="couponsStore.books.length === 0" class="empty-state">
      <p>📭 No coupon books yet</p>
      <button @click="showCreateModal = true" class="btn btn-primary">
        Create Your First Book
      </button>
    </div>

    <!-- Books grid -->
    <div v-else class="books-grid">
      <div v-for="book in couponsStore.books" :key="book.book_id" class="book-card">
        <div class="book-header">
          <h3>{{ book.name }}</h3>
          <span class="active-badge" :class="{ active: book.is_active }">
            {{ book.is_active ? 'Active' : 'Inactive' }}
          </span>
        </div>

        <p v-if="book.description" class="book-description">{{ book.description }}</p>

        <div class="book-stats">
          <div class="stat-item">
            <span class="stat-label">Total Codes:</span>
            <span class="stat-value">{{ book.total_code_count }}</span>
          </div>
          <div class="stat-item">
            <span class="stat-label">Max per User:</span>
            <span class="stat-value">{{ book.max_redemptions_per_user }}</span>
          </div>
          <div v-if="book.expiration_date" class="stat-item">
            <span class="stat-label">Expires:</span>
            <span class="stat-value">{{ formatDate(book.expiration_date) }}</span>
          </div>
        </div>

        <div class="book-features">
          <span v-if="book.allow_multi_redemption" class="feature-badge">
            🔄 Multi-Redemption
          </span>
          <span v-if="book.max_assignments_per_user" class="feature-badge">
            👤 Max {{ book.max_assignments_per_user }} per user
          </span>
        </div>

        <div class="book-actions">
          <button 
            @click="viewBookDetails(book.book_id)" 
            class="btn btn-secondary btn-sm"
          >
            👁️ View Details
          </button>
          <button 
            v-if="isMyBook(book)"
            @click="showCodesModal(book)" 
            class="btn btn-primary btn-sm"
          >
            ➕ Add Codes
          </button>
          <button 
            v-if="isMyBook(book) && book.total_code_count > 0"
            @click="showDistributeModal(book)" 
            class="btn btn-accent btn-sm"
          >
            🎲 Distribute to Pool
          </button>
          <button 
            v-else-if="!isMyBook(book)"
            @click="assignCoupon(book.book_id)" 
            class="btn btn-success btn-sm"
            :disabled="couponsStore.loading.action"
          >
            🎟️ Get Coupon
          </button>
        </div>

        <div class="book-meta">
          <small>Created: {{ formatDate(book.created_at) }}</small>
          <small v-if="isMyBook(book)">👤 Owned by you</small>
        </div>
      </div>
    </div>

    <!-- Create Book Modal -->
    <div v-if="showCreateModal" class="modal-overlay" @click="showCreateModal = false">
      <div class="modal-content large" @click.stop>
        <h2>📚 Create New Coupon Book</h2>
        <form @submit.prevent="handleCreateBook">
          <div class="form-group">
            <label>Book Name *</label>
            <input v-model="bookForm.name" type="text" required maxlength="255" />
          </div>

          <div class="form-group">
            <label>Description</label>
            <textarea v-model="bookForm.description" rows="3"></textarea>
          </div>

          <div class="form-row">
            <div class="form-group">
              <label>Max Redemptions per User *</label>
              <input v-model.number="bookForm.max_redemptions_per_user" type="number" min="1" required />
            </div>

            <div class="form-group">
              <label>Max Assignments per User</label>
              <input v-model.number="bookForm.max_assignments_per_user" type="number" min="1" />
            </div>
          </div>

          <div class="form-group">
            <label>Expiration Date</label>
            <input v-model="bookForm.expiration_date" type="datetime-local" />
          </div>

          <div class="form-group">
            <label>Code Pattern (optional)</label>
            <input 
              v-model="bookForm.code_pattern" 
              type="text" 
              placeholder="e.g., SUMMER2024-{}" 
              maxlength="100"
            />
            <small>Use {} as placeholder for random part</small>
          </div>

          <div class="checkbox-group">
            <label>
              <input v-model="bookForm.allow_multi_redemption" type="checkbox" />
              Allow Multiple Redemptions
            </label>
          </div>

          <div class="checkbox-group">
            <label>
              <input v-model="bookForm.is_active" type="checkbox" />
              Active
            </label>
          </div>

          <div class="modal-actions">
            <button type="button" @click="showCreateModal = false" class="btn btn-secondary">
              Cancel
            </button>
            <button type="submit" class="btn btn-primary" :disabled="couponsStore.loading.action">
              {{ couponsStore.loading.action ? 'Creating...' : 'Create Book' }}
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- Add Codes Modal -->
    <div v-if="showCodesModalFlag" class="modal-overlay" @click="showCodesModalFlag = false">
      <div class="modal-content" @click.stop>
        <h2>➕ Add Codes to {{ selectedBook?.name }}</h2>
        
        <div class="tabs">
          <button 
            @click="codesTab = 'generate'" 
            :class="{ active: codesTab === 'generate' }"
            class="tab-button"
          >
            🎲 Generate Random
          </button>
          <button 
            @click="codesTab = 'upload'" 
            :class="{ active: codesTab === 'upload' }"
            class="tab-button"
          >
            📄 Upload List
          </button>
        </div>

        <!-- Generate Tab -->
        <div v-if="codesTab === 'generate'" class="tab-content">
          <form @submit.prevent="handleGenerateCodes">
            <div class="form-group">
              <label>Number of Codes *</label>
              <input v-model.number="generateForm.count" type="number" min="1" max="10000" required />
            </div>

            <div class="form-group">
              <label>Code Length</label>
              <input v-model.number="generateForm.length" type="number" min="4" max="20" />
            </div>

            <div class="modal-actions">
              <button type="button" @click="showCodesModalFlag = false" class="btn btn-secondary">
                Cancel
              </button>
              <button type="submit" class="btn btn-primary" :disabled="couponsStore.loading.action">
                {{ couponsStore.loading.action ? 'Generating...' : 'Generate Codes' }}
              </button>
            </div>
          </form>
        </div>

        <!-- Upload Tab -->
        <div v-if="codesTab === 'upload'" class="tab-content">
          <form @submit.prevent="handleUploadCodes">
            <div class="form-group">
              <label>Codes (one per line) *</label>
              <textarea 
                v-model="uploadForm.codes" 
                rows="10" 
                required
                placeholder="CODE1&#10;CODE2&#10;CODE3"
              ></textarea>
              <small>{{ codesList.length }} codes entered</small>
            </div>

            <div class="modal-actions">
              <button type="button" @click="showCodesModalFlag = false" class="btn btn-secondary">
                Cancel
              </button>
              <button type="submit" class="btn btn-primary" :disabled="couponsStore.loading.action">
                {{ couponsStore.loading.action ? 'Uploading...' : 'Upload Codes' }}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>

    <!-- Distribute to Pool Modal -->
    <div v-if="showDistributeModalFlag" class="modal-overlay" @click="showDistributeModalFlag = false">
      <div class="modal-content" @click.stop>
        <h2>🎲 Distribute Coupons to Pool</h2>
        <p v-if="selectedBook" class="modal-subtitle">
          Book: <strong>{{ selectedBook.name }}</strong> 
          ({{ selectedBook.total_code_count }} total codes)
        </p>

        <form @submit.prevent="handleDistributeCoupons">
          <div class="form-group">
            <label>Select Pool *</label>
            <select v-model="distributeForm.poolId" required>
              <option value="">-- Choose a pool --</option>
              <option 
                v-for="pool in poolsStore.pools" 
                :key="pool.pool_id" 
                :value="pool.pool_id"
              >
                {{ pool.name }} ({{ pool.user_count }} users)
              </option>
            </select>
          </div>

          <div class="form-group">
            <label>Distribution Mode *</label>
            <select v-model="distributeForm.distributionMode" required>
              <option value="random">🎲 Random - Assign random coupons to users</option>
              <option value="equal">⚖️ Equal - Give each user the same amount</option>
            </select>
          </div>

          <div v-if="distributeForm.distributionMode === 'equal'" class="form-group">
            <label>Coupons per User *</label>
            <input 
              v-model.number="distributeForm.couponsPerUser" 
              type="number" 
              min="1" 
              required 
              placeholder="e.g., 5"
            />
            <small v-if="selectedPool">
              Total needed: {{ distributeForm.couponsPerUser * selectedPool.user_count }} coupons
            </small>
          </div>

          <div v-if="distributionPreview" class="info-box">
            <h4>📊 Distribution Preview</h4>
            <p><strong>Pool:</strong> {{ distributionPreview.poolName }}</p>
            <p><strong>Users:</strong> {{ distributionPreview.userCount }}</p>
            <p><strong>Mode:</strong> {{ distributionPreview.mode }}</p>
            <p v-if="distributeForm.distributionMode === 'equal'">
              <strong>Per User:</strong> {{ distributeForm.couponsPerUser }} coupons
            </p>
            <p><strong>Total to Assign:</strong> ~{{ distributionPreview.totalNeeded }} coupons</p>
          </div>

          <div class="modal-actions">
            <button type="button" @click="showDistributeModalFlag = false" class="btn btn-secondary">
              Cancel
            </button>
            <button 
              type="submit" 
              class="btn btn-accent" 
              :disabled="poolsStore.loading.action || !canDistribute"
            >
              {{ poolsStore.loading.action ? 'Distributing...' : '🎲 Distribute' }}
            </button>
          </div>
        </form>

        <!-- Results -->
        <div v-if="distributionResults" class="distribution-results">
          <h3>✅ Distribution Complete!</h3>
          <p><strong>Total Assigned:</strong> {{ distributionResults.total_assigned }} coupons</p>
          
          <div class="results-table">
            <h4>📋 Assignment Details</h4>
            <div v-for="(codes, userId) in distributionResults.assignments" :key="userId" class="result-row">
              <span class="user-id">{{ getUserName(userId) }}</span>
              <span class="codes-count">{{ codes.length }} codes</span>
              <details>
                <summary>View Codes</summary>
                <ul class="codes-list">
                  <li v-for="code in codes" :key="code">{{ code }}</li>
                </ul>
              </details>
            </div>
          </div>

          <div v-if="distributionResults.errors.length > 0" class="error-list">
            <h4>⚠️ Errors</h4>
            <ul>
              <li v-for="(error, idx) in distributionResults.errors" :key="idx">{{ error }}</li>
            </ul>
          </div>

          <button @click="closeDistributeModal" class="btn btn-primary">
            Close
          </button>
        </div>
      </div>
    </div>
  </div>

  <!-- Toast Notification -->
  <Transition name="slide-fade">
    <div v-if="toast.show" :class="['toast-notification', `toast-${toast.type}`]">
      <div class="toast-content">
        <div class="toast-icon">{{ toast.icon }}</div>
        <div class="toast-body">
          <div class="toast-title">{{ toast.title }}</div>
          <div class="toast-message">{{ toast.message }}</div>
        </div>
        <button @click="closeToast" class="toast-close">×</button>
      </div>
    </div>
  </Transition>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useCouponsStore } from '@/stores/coupons'
import { useAuthStore } from '@/stores/auth'
import { usePoolsStore } from '@/stores/pools'

const router = useRouter()
const couponsStore = useCouponsStore()
const authStore = useAuthStore()
const poolsStore = usePoolsStore()

const showCreateModal = ref(false)
const showCodesModalFlag = ref(false)
const showDistributeModalFlag = ref(false)
const selectedBook = ref(null)
const codesTab = ref('generate')
const distributionResults = ref(null)

const bookForm = ref({
  name: '',
  description: '',
  max_redemptions_per_user: 1,
  max_assignments_per_user: null,
  expiration_date: null,
  code_pattern: '',
  allow_multi_redemption: false,
  is_active: true,
  total_code_count: 0
})

const generateForm = ref({
  count: 10,
  length: 8
})

const uploadForm = ref({
  codes: ''
})

const distributeForm = ref({
  poolId: '',
  distributionMode: 'random',
  couponsPerUser: 1
})

const selectedPool = computed(() => {
  if (!distributeForm.value.poolId) return null
  return poolsStore.pools.find(p => p.pool_id === distributeForm.value.poolId)
})

// Toast notification state
const toast = ref({
  show: false,
  type: 'success', // 'success', 'error', 'warning', 'info'
  icon: '✅',
  title: '',
  message: '',
  duration: 4000
})

const showToast = (type, title, message, duration = 4000) => {
  const icons = {
    success: '✅',
    error: '❌',
    warning: '⚠️',
    info: 'ℹ️'
  }
  
  toast.value = {
    show: true,
    type,
    icon: icons[type] || icons.info,
    title,
    message,
    duration
  }
  
  if (duration > 0) {
    setTimeout(() => {
      toast.value.show = false
    }, duration)
  }
}

const closeToast = () => {
  toast.value.show = false
}

const distributionPreview = computed(() => {
  if (!selectedPool.value || !selectedBook.value) return null
  
  const userCount = selectedPool.value.user_count
  const mode = distributeForm.value.distributionMode
  const perUser = distributeForm.value.couponsPerUser
  
  let totalNeeded = 0
  if (mode === 'equal') {
    totalNeeded = userCount * perUser
  } else {
    totalNeeded = Math.min(selectedBook.value.total_code_count, userCount)
  }
  
  return {
    poolName: selectedPool.value.name,
    userCount,
    mode: mode === 'equal' ? 'Equal Distribution' : 'Random Distribution',
    totalNeeded
  }
})

const canDistribute = computed(() => {
  if (!distributeForm.value.poolId || !selectedBook.value) return false
  if (!selectedPool.value || selectedPool.value.user_count === 0) return false
  
  // For now, just check that the book has codes
  // The backend will validate if there are enough available
  if (distributeForm.value.distributionMode === 'equal') {
    const needed = selectedPool.value.user_count * distributeForm.value.couponsPerUser
    return selectedBook.value.total_code_count >= needed
  }
  
  return selectedBook.value.total_code_count > 0
})

const codesList = computed(() => {
  return uploadForm.value.codes
    .split('\n')
    .map(c => c.trim())
    .filter(c => c.length > 0)
})

onMounted(() => {
  couponsStore.fetchBooks()
  poolsStore.fetchPools() // Load pools for distribution modal
})

const isMyBook = (book) => {
  return book.owner_id === authStore.user?.user_id
}

const formatDate = (dateString) => {
  if (!dateString) return 'N/A'
  return new Date(dateString).toLocaleDateString()
}

const handleCreateBook = async () => {
  try {
    await couponsStore.createBook(bookForm.value)
    showCreateModal.value = false
    bookForm.value = {
      name: '',
      description: '',
      max_redemptions_per_user: 1,
      max_assignments_per_user: null,
      expiration_date: null,
      code_pattern: '',
      allow_multi_redemption: false,
      is_active: true,
      total_code_count: 0
    }
    showToast('success', 'Book Created', 'Coupon book created successfully!')
  } catch (error) {
    const errorMsg = error.response?.data?.detail || error.message || 'Failed to create book'
    showToast('error', 'Creation Failed', errorMsg, 5000)
  }
}

const showCodesModal = (book) => {
  selectedBook.value = book
  showCodesModalFlag.value = true
  codesTab.value = 'generate'
  generateForm.value = { count: 10, length: 8 }
  uploadForm.value = { codes: '' }
}

const handleGenerateCodes = async () => {
  try {
    await couponsStore.generateCodes(
      selectedBook.value.book_id,
      generateForm.value.count,
      generateForm.value.length
    )
    showCodesModalFlag.value = false
    showToast('success', 'Codes Generated', `Successfully generated ${generateForm.value.count} coupon codes`)
  } catch (error) {
    const errorMsg = error.response?.data?.detail || error.message || 'Failed to generate codes'
    showToast('error', 'Generation Failed', errorMsg, 5000)
  }
}

const handleUploadCodes = async () => {
  if (codesList.value.length === 0) {
    showToast('warning', 'No Codes', 'Please enter at least one coupon code', 3000)
    return
  }

  try {
    await couponsStore.uploadCodes(selectedBook.value.book_id, codesList.value)
    showCodesModalFlag.value = false
    showToast('success', 'Codes Uploaded', `Successfully uploaded ${codesList.value.length} coupon codes`)
  } catch (error) {
    const errorMsg = error.response?.data?.detail || error.message || 'Failed to upload codes'
    showToast('error', 'Upload Failed', errorMsg, 5000)
  }
}

const assignCoupon = async (bookId) => {
  try {
    const coupon = await couponsStore.assignRandomCoupon(bookId)
    showToast('success', 'Coupon Assigned', `Assigned coupon: ${coupon.code}`)
    setTimeout(() => {
      router.push('/coupons')
    }, 1500)
  } catch (error) {
    const errorMsg = error.response?.data?.detail || error.message || 'Failed to assign coupon'
    showToast('error', 'Assignment Failed', errorMsg, 6000)
  }
}

const viewBookDetails = (bookId) => {
  router.push(`/books/${bookId}`)
}

const showDistributeModal = async (book) => {
  selectedBook.value = book
  distributionResults.value = null
  distributeForm.value = {
    poolId: '',
    distributionMode: 'random',
    couponsPerUser: 1
  }
  
  // Load pools if not already loaded
  if (poolsStore.pools.length === 0) {
    await poolsStore.fetchPools()
  }
  
  showDistributeModalFlag.value = true
}

const handleDistributeCoupons = async () => {
  try {
    const result = await poolsStore.bulkAssignCoupons(
      selectedBook.value.book_id,
      distributeForm.value.poolId,
      distributeForm.value.distributionMode,
      distributeForm.value.couponsPerUser
    )
    
    distributionResults.value = result
    
    // Refresh the books list to update available counts
    await couponsStore.fetchBooks()
    
    // Show success message with details
    if (result.success) {
      const userCount = Object.keys(result.assignments || {}).length
      showToast('success', 'Distribution Complete', 
        `Successfully distributed ${result.total_assigned} coupons to ${userCount} users`, 5000)
      
      // Show warnings if any
      if (result.errors && result.errors.length > 0) {
        setTimeout(() => {
          showToast('warning', 'Partial Success', 
            `Some users reached their limit: ${result.errors.join(', ')}`, 8000)
        }, 5500)
      }
    }
  } catch (error) {
    console.error('Distribution error:', error)
    const errorMsg = error.response?.data?.detail || error.message || 'Failed to distribute coupons'
    showToast('error', 'Distribution Failed', errorMsg, 6000)
  }
}

const closeDistributeModal = () => {
  showDistributeModalFlag.value = false
  distributionResults.value = null
  selectedBook.value = null
}

const getUserName = (userId) => {
  // Simple user ID display - could be enhanced with actual user names
  return userId.substring(0, 8) + '...'
}
</script>

<style scoped>
.books-view {
  max-width: 1200px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
}

.loading-state,
.empty-state {
  text-align: center;
  padding: 3rem;
  color: #6c757d;
}

.books-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: 1.5rem;
}

.book-card {
  background: white;
  border: 2px solid #e9ecef;
  border-radius: 12px;
  padding: 1.5rem;
  transition: all 0.3s;
}

.book-card:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  transform: translateY(-2px);
}

.book-header {
  display: flex;
  justify-content: space-between;
  align-items: start;
  margin-bottom: 1rem;
}

.book-header h3 {
  margin: 0;
  font-size: 1.25rem;
  flex: 1;
}

.active-badge {
  padding: 0.25rem 0.75rem;
  border-radius: 20px;
  font-size: 0.75rem;
  font-weight: 600;
  background: #dc3545;
  color: white;
}

.active-badge.active {
  background: #28a745;
}

.book-description {
  color: #6c757d;
  margin-bottom: 1rem;
  font-size: 0.9rem;
}

.book-stats {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  margin-bottom: 1rem;
  padding: 1rem;
  background: #f8f9fa;
  border-radius: 8px;
}

.stat-item {
  display: flex;
  justify-content: space-between;
}

.stat-label {
  font-weight: 600;
  color: #6c757d;
}

.stat-value {
  color: #495057;
  font-family: 'Courier New', monospace;
}

.book-features {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
  margin-bottom: 1rem;
}

.feature-badge {
  padding: 0.25rem 0.75rem;
  background: #e7f3ff;
  color: #0066cc;
  border-radius: 20px;
  font-size: 0.75rem;
  font-weight: 600;
}

.book-actions {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 1rem;
}

.book-meta {
  display: flex;
  justify-content: space-between;
  padding-top: 1rem;
  border-top: 1px solid #e9ecef;
  font-size: 0.85rem;
  color: #6c757d;
}

.modal-content.large {
  max-width: 600px;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
}

.checkbox-group {
  margin-bottom: 1rem;
}

.checkbox-group label {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  cursor: pointer;
}

.checkbox-group input[type="checkbox"] {
  width: auto;
  cursor: pointer;
}

.tabs {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 1.5rem;
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

.tab-content {
  padding: 1rem 0;
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

.btn-accent {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
}

.btn-accent:hover:not(:disabled) {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
}

.info-box {
  background: #e7f3ff;
  border: 1px solid #b3d9ff;
  border-radius: 8px;
  padding: 1rem;
  margin: 1rem 0;
}

.info-box h4 {
  margin: 0 0 0.5rem 0;
  color: #0066cc;
}

.info-box p {
  margin: 0.25rem 0;
}

.distribution-results {
  margin-top: 2rem;
  padding-top: 2rem;
  border-top: 2px solid #e9ecef;
}

.distribution-results h3 {
  color: #28a745;
  margin-bottom: 1rem;
}

.results-table {
  margin: 1.5rem 0;
}

.results-table h4 {
  margin-bottom: 1rem;
}

.result-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.75rem;
  background: #f8f9fa;
  border-radius: 6px;
  margin-bottom: 0.5rem;
}

.user-id {
  font-weight: 600;
  color: #495057;
}

.codes-count {
  background: #007bff;
  color: white;
  padding: 0.25rem 0.75rem;
  border-radius: 12px;
  font-size: 0.875rem;
}

.result-row details {
  margin-top: 0.5rem;
  width: 100%;
}

.result-row summary {
  cursor: pointer;
  color: #007bff;
  font-size: 0.875rem;
  margin-top: 0.5rem;
}

.codes-list {
  list-style: none;
  padding: 0.5rem 0 0 0;
  margin: 0;
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(120px, 1fr));
  gap: 0.5rem;
}

.codes-list li {
  background: white;
  padding: 0.5rem;
  border-radius: 4px;
  font-family: 'Courier New', monospace;
  font-size: 0.875rem;
  text-align: center;
  border: 1px solid #dee2e6;
}

.error-list {
  margin-top: 1rem;
  padding: 1rem;
  background: #fff3cd;
  border: 1px solid #ffc107;
  border-radius: 6px;
}

.error-list h4 {
  color: #856404;
  margin: 0 0 0.5rem 0;
}

.error-list ul {
  margin: 0;
  padding-left: 1.5rem;
}

.error-list li {
  color: #856404;
}

/* Toast Notification Styles */
.toast-notification {
  position: fixed;
  top: 20px;
  right: 20px;
  min-width: 320px;
  max-width: 500px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  z-index: 10000;
  overflow: hidden;
}

.toast-content {
  display: flex;
  align-items: flex-start;
  padding: 16px;
  gap: 12px;
}

.toast-icon {
  font-size: 24px;
  flex-shrink: 0;
}

.toast-body {
  flex: 1;
  min-width: 0;
}

.toast-title {
  font-weight: 600;
  font-size: 15px;
  margin-bottom: 4px;
  color: #1a1a1a;
}

.toast-message {
  font-size: 14px;
  color: #666;
  line-height: 1.4;
  word-wrap: break-word;
}

.toast-close {
  background: none;
  border: none;
  font-size: 24px;
  color: #999;
  cursor: pointer;
  padding: 0;
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  line-height: 1;
}

.toast-close:hover {
  color: #666;
}

.toast-success {
  border-left: 4px solid #10b981;
}

.toast-error {
  border-left: 4px solid #ef4444;
}

.toast-warning {
  border-left: 4px solid #f59e0b;
}

.toast-info {
  border-left: 4px solid #3b82f6;
}

/* Slide fade animation */
.slide-fade-enter-active {
  transition: all 0.3s ease-out;
}

.slide-fade-leave-active {
  transition: all 0.2s ease-in;
}

.slide-fade-enter-from {
  transform: translateX(100%);
  opacity: 0;
}

.slide-fade-leave-to {
  transform: translateX(100%);
  opacity: 0;
}
</style>
