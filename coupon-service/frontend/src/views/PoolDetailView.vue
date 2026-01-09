<template>
  <div class="pool-detail-view">
    <div class="page-header">
      <button @click="$router.back()" class="btn btn-secondary">
        ← Back
      </button>
      <h1>Pool Details</h1>
    </div>

    <!-- Error message -->
    <div v-if="poolsStore.error" class="error-message">
      {{ poolsStore.error }}
      <button @click="poolsStore.clearError()" class="close-btn">×</button>
    </div>

    <!-- Loading state -->
    <div v-if="poolsStore.loading.pools" class="loading-state">
      <p>⏳ Loading pool details...</p>
    </div>

    <!-- Pool details -->
    <div v-else-if="pool" class="pool-details">
      <div class="detail-card">
        <div class="card-header">
          <h2>{{ pool.name }}</h2>
          <span class="status-badge" :class="{ active: pool.is_active }">
            {{ pool.is_active ? 'Active' : 'Inactive' }}
          </span>
        </div>

        <p v-if="pool.description" class="description">{{ pool.description }}</p>

        <div class="pool-stats">
          <div class="stat-item">
            <span class="stat-icon">👥</span>
            <span class="stat-value">{{ pool.users?.length || 0 }}</span>
            <span class="stat-label">Users</span>
          </div>
        </div>

        <div class="pool-meta">
          <p><strong>Created:</strong> {{ formatDate(pool.created_at) }}</p>
          <p><strong>Last Updated:</strong> {{ formatDate(pool.updated_at) }}</p>
          <p><strong>Created By:</strong> User #{{ pool.created_by }}</p>
        </div>
      </div>

      <div class="users-section">
        <div class="section-header">
          <h3>👥 Users in Pool ({{ pool.users?.length || 0 }})</h3>
          <button @click="showAddUsers = true" class="btn btn-primary">
            ➕ Add Users
          </button>
        </div>

        <div v-if="pool.users && pool.users.length > 0" class="users-list">
          <div v-for="user in pool.users" :key="user.user_id" class="user-item">
            <div class="user-info">
              <span class="user-name">{{ user.name }}</span>
              <span class="user-email">{{ user.email }}</span>
              <span class="user-id" :title="user.user_id">
                ID: <code>{{ user.user_id.substring(0, 8) }}...</code>
                <button 
                  @click="copyUserId(user.user_id)" 
                  class="copy-btn"
                  title="Copy full user ID"
                >
                  📋
                </button>
              </span>
              <span class="user-added">Added: {{ formatDate(user.added_at) }}</span>
            </div>
            <button 
              @click="removeUser(user.user_id)" 
              class="btn btn-danger btn-sm"
              :disabled="poolsStore.loading.action"
            >
              Remove
            </button>
          </div>
        </div>
        <div v-else class="empty-state">
          <p>No users in this pool yet</p>
        </div>
      </div>
    </div>

    <!-- Add Users Modal -->
    <div v-if="showAddUsers" class="modal-overlay" @click.self="showAddUsers = false">
      <div class="modal-content">
        <div class="modal-header">
          <h2>Add Users to Pool</h2>
          <button @click="showAddUsers = false" class="close-btn">×</button>
        </div>

        <div class="modal-body">
          <div class="form-group">
            <label>User IDs (comma-separated)</label>
            <input 
              v-model="userIdsInput" 
              type="text" 
              placeholder="e.g., 1, 2, 3"
            />
            <small class="form-text">Enter user IDs separated by commas</small>
          </div>
        </div>

        <div class="modal-footer">
          <button @click="showAddUsers = false" class="btn btn-secondary">
            Cancel
          </button>
          <button 
            @click="addUsers" 
            class="btn btn-primary"
            :disabled="!userIdsInput || poolsStore.loading.action"
          >
            {{ poolsStore.loading.action ? 'Adding...' : 'Add Users' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { usePoolsStore } from '@/stores/pools'

const route = useRoute()
const router = useRouter()
const poolsStore = usePoolsStore()

const showAddUsers = ref(false)
const userIdsInput = ref('')

const pool = computed(() => poolsStore.selectedPool)

const formatDate = (dateString) => {
  if (!dateString) return 'N/A'
  return new Date(dateString).toLocaleString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

const addUsers = async () => {
  try {
    const userIds = userIdsInput.value
      .split(',')
      .map(id => parseInt(id.trim()))
      .filter(id => !isNaN(id))

    if (userIds.length === 0) {
      return
    }

    await poolsStore.addUsersToPool(pool.value.pool_id, userIds)
    showAddUsers.value = false
    userIdsInput.value = ''
    // Refresh pool details
    await poolsStore.fetchPoolDetails(route.params.id)
  } catch (error) {
    // Error handled by store
  }
}

const removeUser = async (userId) => {
  if (!confirm('Are you sure you want to remove this user from the pool?')) {
    return
  }

  try {
    await poolsStore.removeUsersFromPool(pool.value.pool_id, [userId])
    // Refresh pool details
    await poolsStore.fetchPoolDetails(route.params.id)
  } catch (error) {
    // Error handled by store
  }
}

const copyUserId = async (userId) => {
  try {
    await navigator.clipboard.writeText(userId)
    alert('✅ User ID copied to clipboard!\n\nYou can now paste this ID when assigning coupons.')
  } catch (err) {
    // Fallback for older browsers
    const textArea = document.createElement('textarea')
    textArea.value = userId
    document.body.appendChild(textArea)
    textArea.select()
    try {
      document.execCommand('copy')
      alert('✅ User ID copied to clipboard!')
    } catch (err2) {
      alert(`User ID: ${userId}\n\nPlease copy it manually.`)
    }
    document.body.removeChild(textArea)
  }
}

onMounted(() => {
  poolsStore.fetchPoolDetails(route.params.id)
})
</script>

<style scoped>
.pool-detail-view {
  max-width: 1200px;
  margin: 0 auto;
}

.page-header {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-bottom: 2rem;
}

.page-header h1 {
  margin: 0;
  font-size: 2rem;
  color: #212529;
}

.pool-details {
  display: grid;
  gap: 2rem;
}

.detail-card {
  background: white;
  border: 2px solid #e9ecef;
  border-radius: 12px;
  padding: 2rem;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: start;
  margin-bottom: 1rem;
}

.card-header h2 {
  margin: 0;
  font-size: 1.75rem;
}

.status-badge {
  padding: 0.5rem 1rem;
  border-radius: 20px;
  font-size: 0.875rem;
  font-weight: 600;
  background: #dc3545;
  color: white;
}

.status-badge.active {
  background: #28a745;
}

.description {
  color: #6c757d;
  margin-bottom: 1.5rem;
}

.pool-stats {
  display: flex;
  justify-content: center;
  margin-bottom: 1.5rem;
  padding: 1.5rem;
  background: #f8f9fa;
  border-radius: 8px;
}

.stat-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem;
}

.stat-icon {
  font-size: 2rem;
}

.stat-value {
  font-size: 2rem;
  font-weight: 700;
  color: #495057;
}

.stat-label {
  font-size: 0.875rem;
  color: #6c757d;
  text-transform: uppercase;
  font-weight: 600;
}

.pool-meta {
  padding-top: 1.5rem;
  border-top: 1px solid #e9ecef;
}

.pool-meta p {
  margin: 0.5rem 0;
  color: #6c757d;
}

.users-section {
  background: white;
  border: 2px solid #e9ecef;
  border-radius: 12px;
  padding: 2rem;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
}

.section-header h3 {
  margin: 0;
  font-size: 1.5rem;
}

.users-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.user-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem;
  background: #f8f9fa;
  border-radius: 8px;
  border: 1px solid #dee2e6;
}

.user-info {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.user-name {
  font-weight: 600;
  color: #212529;
}

.user-email {
  font-size: 0.875rem;
  color: #6c757d;
}

.user-id {
  font-size: 0.875rem;
  color: #495057;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.user-id code {
  background: #e9ecef;
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  font-family: 'Courier New', monospace;
  font-size: 0.8rem;
}

.copy-btn {
  background: none;
  border: none;
  cursor: pointer;
  font-size: 1rem;
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  transition: background 0.2s;
}

.copy-btn:hover {
  background: #e9ecef;
}

.copy-btn:active {
  transform: scale(0.95);
}

.user-added {
  font-size: 0.75rem;
  color: #868e96;
}

.form-text {
  display: block;
  margin-top: 0.5rem;
  color: #6c757d;
  font-size: 0.875rem;
}
</style>
