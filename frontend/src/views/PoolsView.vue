<template>
  <div class="pools-view">
    <div class="page-header">
      <h1>👥 User Pools</h1>
      <button @click="showCreateModal = true" class="btn btn-primary">
        ➕ Create New Pool
      </button>
    </div>

    <!-- Error message -->
    <div v-if="poolsStore.error" class="error-message">
      {{ poolsStore.error }}
      <button @click="poolsStore.clearError()" class="close-btn">×</button>
    </div>

    <!-- Loading state -->
    <div v-if="poolsStore.loading.pools" class="loading-state">
      <p>⏳ Loading pools...</p>
    </div>

    <!-- Empty state -->
    <div v-else-if="poolsStore.pools.length === 0" class="empty-state">
      <p>📭 No pools yet</p>
      <button @click="showCreateModal = true" class="btn btn-primary">
        Create Your First Pool
      </button>
    </div>

    <!-- Pools grid -->
    <div v-else class="pools-grid">
      <div v-for="pool in poolsStore.pools" :key="pool.pool_id" class="pool-card">
        <div class="pool-header">
          <h3>{{ pool.name }}</h3>
          <span class="status-badge" :class="{ active: pool.is_active }">
            {{ pool.is_active ? 'Active' : 'Inactive' }}
          </span>
        </div>

        <p v-if="pool.description" class="pool-description">{{ pool.description }}</p>

        <div class="pool-stats">
          <div class="stat-item">
            <span class="stat-icon">👥</span>
            <span class="stat-value">{{ pool.user_count }}</span>
            <span class="stat-label">Users</span>
          </div>
        </div>

        <div class="pool-actions">
          <button 
            @click="viewPoolDetails(pool.pool_id)" 
            class="btn btn-secondary btn-sm"
          >
            👁️ View Details
          </button>
          <button 
            @click="showEditModal(pool)" 
            class="btn btn-primary btn-sm"
          >
            ✏️ Edit
          </button>
          <button 
            @click="confirmDelete(pool)" 
            class="btn btn-danger btn-sm"
          >
            🗑️ Delete
          </button>
        </div>

        <div class="pool-meta">
          <small>Created: {{ formatDate(pool.created_at) }}</small>
        </div>
      </div>
    </div>

    <!-- Create Pool Modal -->
    <div v-if="showCreateModal" class="modal-overlay" @click.self="showCreateModal = false">
      <div class="modal-content">
        <div class="modal-header">
          <h2>Create New Pool</h2>
          <button @click="showCreateModal = false" class="close-btn">×</button>
        </div>

        <div class="modal-body">
          <div class="form-group">
            <label>Pool Name *</label>
            <input 
              v-model="newPool.name" 
              type="text" 
              placeholder="e.g., Beta Testers" 
              required
            />
          </div>

          <div class="form-group">
            <label>Description</label>
            <textarea 
              v-model="newPool.description" 
              placeholder="Optional description..."
              rows="3"
            ></textarea>
          </div>
        </div>

        <div class="modal-footer">
          <button @click="showCreateModal = false" class="btn btn-secondary">
            Cancel
          </button>
          <button 
            @click="createPool" 
            class="btn btn-primary"
            :disabled="!newPool.name || poolsStore.loading.action"
          >
            {{ poolsStore.loading.action ? 'Creating...' : 'Create Pool' }}
          </button>
        </div>
      </div>
    </div>

    <!-- Edit Pool Modal -->
    <div v-if="showEdit && editingPool" class="modal-overlay" @click.self="showEdit = false">
      <div class="modal-content">
        <div class="modal-header">
          <h2>Edit Pool</h2>
          <button @click="showEdit = false" class="close-btn">×</button>
        </div>

        <div class="modal-body">
          <div class="form-group">
            <label>Pool Name *</label>
            <input 
              v-model="editingPool.name" 
              type="text" 
              required
            />
          </div>

          <div class="form-group">
            <label>Description</label>
            <textarea 
              v-model="editingPool.description" 
              rows="3"
            ></textarea>
          </div>

          <div class="checkbox-group">
            <label>
              <input 
                type="checkbox" 
                v-model="editingPool.is_active"
              />
              Active
            </label>
          </div>
        </div>

        <div class="modal-footer">
          <button @click="showEdit = false" class="btn btn-secondary">
            Cancel
          </button>
          <button 
            @click="updatePool" 
            class="btn btn-primary"
            :disabled="!editingPool.name || poolsStore.loading.action"
          >
            {{ poolsStore.loading.action ? 'Saving...' : 'Save Changes' }}
          </button>
        </div>
      </div>
    </div>

    <!-- Delete Confirmation Modal -->
    <div v-if="showDeleteConfirm" class="modal-overlay" @click.self="showDeleteConfirm = false">
      <div class="modal-content">
        <div class="modal-header">
          <h2>Delete Pool?</h2>
          <button @click="showDeleteConfirm = false" class="close-btn">×</button>
        </div>

        <div class="modal-body">
          <p>Are you sure you want to delete pool <strong>{{ poolToDelete?.name }}</strong>?</p>
          <p class="text-muted">This action cannot be undone.</p>
        </div>

        <div class="modal-footer">
          <button @click="showDeleteConfirm = false" class="btn btn-secondary">
            Cancel
          </button>
          <button 
            @click="deletePool" 
            class="btn btn-danger"
            :disabled="poolsStore.loading.action"
          >
            {{ poolsStore.loading.action ? 'Deleting...' : 'Delete Pool' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { usePoolsStore } from '@/stores/pools'

const router = useRouter()
const poolsStore = usePoolsStore()

const showCreateModal = ref(false)
const showEdit = ref(false)
const showDeleteConfirm = ref(false)
const poolToDelete = ref(null)

const newPool = ref({
  name: '',
  description: '',
  user_ids: []
})

const editingPool = ref(null)

const formatDate = (dateString) => {
  if (!dateString) return 'N/A'
  return new Date(dateString).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric'
  })
}

const createPool = async () => {
  try {
    await poolsStore.createPool(newPool.value)
    showCreateModal.value = false
    newPool.value = { name: '', description: '', user_ids: [] }
  } catch (error) {
    // Error handled by store
  }
}

const showEditModal = (pool) => {
  editingPool.value = { ...pool }
  showEdit.value = true
}

const updatePool = async () => {
  try {
    await poolsStore.updatePool(editingPool.value.pool_id, {
      name: editingPool.value.name,
      description: editingPool.value.description,
      is_active: editingPool.value.is_active
    })
    showEdit.value = false
    editingPool.value = null
  } catch (error) {
    // Error handled by store
  }
}

const confirmDelete = (pool) => {
  poolToDelete.value = pool
  showDeleteConfirm.value = true
}

const deletePool = async () => {
  try {
    await poolsStore.deletePool(poolToDelete.value.pool_id)
    showDeleteConfirm.value = false
    poolToDelete.value = null
  } catch (error) {
    // Error handled by store
  }
}

const viewPoolDetails = (poolId) => {
  router.push(`/pools/${poolId}`)
}

onMounted(() => {
  poolsStore.fetchPools()
})
</script>

<style scoped>
.pools-view {
  max-width: 1200px;
  margin: 0 auto;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
}

.page-header h1 {
  margin: 0;
  font-size: 2rem;
  color: #212529;
}

.pools-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 1.5rem;
}

.pool-card {
  background: white;
  border: 2px solid #e9ecef;
  border-radius: 12px;
  padding: 1.5rem;
  transition: all 0.3s;
}

.pool-card:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  transform: translateY(-2px);
}

.pool-header {
  display: flex;
  justify-content: space-between;
  align-items: start;
  margin-bottom: 1rem;
}

.pool-header h3 {
  margin: 0;
  font-size: 1.25rem;
  flex: 1;
}

.status-badge {
  padding: 0.25rem 0.75rem;
  border-radius: 20px;
  font-size: 0.75rem;
  font-weight: 600;
  background: #dc3545;
  color: white;
}

.status-badge.active {
  background: #28a745;
}

.pool-description {
  color: #6c757d;
  margin-bottom: 1rem;
  font-size: 0.9rem;
}

.pool-stats {
  display: flex;
  justify-content: center;
  margin-bottom: 1rem;
  padding: 1rem;
  background: #f8f9fa;
  border-radius: 8px;
}

.stat-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.25rem;
}

.stat-icon {
  font-size: 1.5rem;
}

.stat-value {
  font-size: 1.5rem;
  font-weight: 700;
  color: #495057;
}

.stat-label {
  font-size: 0.75rem;
  color: #6c757d;
  text-transform: uppercase;
}

.pool-actions {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 1rem;
}

.pool-meta {
  padding-top: 1rem;
  border-top: 1px solid #e9ecef;
  font-size: 0.85rem;
  color: #6c757d;
}

.text-muted {
  color: #6c757d;
  font-size: 0.9rem;
}
</style>
