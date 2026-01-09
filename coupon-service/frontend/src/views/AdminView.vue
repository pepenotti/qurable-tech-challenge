<template>
  <div class="admin">
    <h1>👑 Admin Panel</h1>
    <p class="subtitle">Manage users and system settings</p>

    <div class="admin-stats">
      <div class="stat-card">
        <div class="stat-icon">👥</div>
        <h3>Total Users</h3>
        <p class="stat-value">{{ users?.length || 0 }}</p>
      </div>
      <div class="stat-card">
        <div class="stat-icon">👑</div>
        <h3>Admins</h3>
        <p class="stat-value">{{ adminCount }}</p>
      </div>
      <div class="stat-card">
        <div class="stat-icon">✅</div>
        <h3>Active Users</h3>
        <p class="stat-value">{{ activeCount }}</p>
      </div>
    </div>

    <div class="users-section">
      <div class="section-header">
        <h2>👥 User Management</h2>
        <button @click="showCreateUser = true" class="btn btn-primary">
          ➕ Create User
        </button>
      </div>

      <div v-if="loading" class="loading">Loading users...</div>
      <div v-else-if="error" class="error-message">{{ error }}</div>
      <div v-else-if="!users || users.length === 0" class="empty-state">
        <p>No users found</p>
      </div>
      <div v-else class="users-table">
        <table>
          <thead>
            <tr>
              <th>Name</th>
              <th>Email</th>
              <th>Role</th>
              <th>Status</th>
              <th>Created</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="user in users" :key="user.user_id">
              <td>{{ user.name }}</td>
              <td>{{ user.email }}</td>
              <td>
                <span class="badge" :class="user.role">
                  {{ user.role.toUpperCase() }}
                </span>
              </td>
              <td>
                <span class="badge" :class="{ active: user.is_active }">
                  {{ user.is_active ? 'Active' : 'Inactive' }}
                </span>
              </td>
              <td>{{ formatDate(user.created_at) }}</td>
              <td class="actions">
                <button @click="editUser(user)" class="btn-icon" title="Edit">
                  ✏️
                </button>
                <button
                  @click="confirmDelete(user)"
                  class="btn-icon danger"
                  title="Delete"
                  :disabled="user.user_id === authStore.user?.user_id"
                >
                  🗑️
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Create/Edit User Modal -->
    <div
      v-if="showCreateUser || editingUser"
      class="modal-overlay"
      @click="closeModal"
    >
      <div class="modal-content" @click.stop>
        <h3>{{ editingUser ? '✏️ Edit User' : '➕ Create User' }}</h3>
        <form @submit.prevent="handleSubmitUser">
          <div v-if="formError" class="error-message">{{ formError }}</div>

          <div class="form-group">
            <label>Name</label>
            <input v-model="userForm.name" type="text" required />
          </div>

          <div class="form-group">
            <label>Email</label>
            <input v-model="userForm.email" type="email" required />
          </div>

          <div v-if="!editingUser" class="form-group">
            <label>Password</label>
            <input v-model="userForm.password" type="password" required minlength="8" />
            <small>Minimum 8 characters</small>
          </div>

          <div class="form-group">
            <label>Role</label>
            <select v-model="userForm.role" required>
              <option value="user">User</option>
              <option value="admin">Admin</option>
            </select>
          </div>

          <div class="form-group">
            <label>
              <input v-model="userForm.is_active" type="checkbox" />
              Active
            </label>
          </div>

          <div class="modal-actions">
            <button type="button" @click="closeModal" class="btn btn-secondary">
              Cancel
            </button>
            <button type="submit" class="btn btn-primary" :disabled="formLoading">
              {{ formLoading ? 'Saving...' : 'Save' }}
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- Delete Confirmation Modal -->
    <div v-if="deletingUser" class="modal-overlay" @click="deletingUser = null">
      <div class="modal-content" @click.stop>
        <h3>🗑️ Delete User</h3>
        <p>Are you sure you want to delete <strong>{{ deletingUser.name }}</strong>?</p>
        <p class="warning">This action cannot be undone.</p>

        <div class="modal-actions">
          <button @click="deletingUser = null" class="btn btn-secondary">
            Cancel
          </button>
          <button @click="handleDeleteUser" class="btn btn-danger" :disabled="formLoading">
            {{ formLoading ? 'Deleting...' : 'Delete' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { authService } from '@/services/auth'

const authStore = useAuthStore()

const users = ref([])
const loading = ref(false)
const error = ref('')

const showCreateUser = ref(false)
const editingUser = ref(null)
const deletingUser = ref(null)

const userForm = ref({
  name: '',
  email: '',
  password: '',
  role: 'user',
  is_active: true,
})

const formLoading = ref(false)
const formError = ref('')

const adminCount = computed(() =>
  users.value?.filter((u) => u.role === 'admin').length || 0
)
const activeCount = computed(() =>
  users.value?.filter((u) => u.is_active).length || 0
)

const formatDate = (dateString) => {
  const date = new Date(dateString)
  return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })
}

const loadUsers = async () => {
  loading.value = true
  error.value = ''

  try {
    const data = await authService.getUsers()
    // Backend returns array directly, not { users: [...] }
    users.value = Array.isArray(data) ? data : (data.users || [])
  } catch (err) {
    error.value = 'Failed to load users'
    users.value = [] // Ensure users is always an array
    console.error('Error loading users:', err)
  } finally {
    loading.value = false
  }
}

const editUser = (user) => {
  editingUser.value = user
  userForm.value = {
    name: user.name,
    email: user.email,
    role: user.role,
    is_active: user.is_active,
  }
}

const confirmDelete = (user) => {
  deletingUser.value = user
}

const closeModal = () => {
  showCreateUser.value = false
  editingUser.value = null
  userForm.value = {
    name: '',
    email: '',
    password: '',
    role: 'user',
    is_active: true,
  }
  formError.value = ''
}

const handleSubmitUser = async () => {
  formLoading.value = true
  formError.value = ''

  try {
    if (editingUser.value) {
      await authService.updateUser(editingUser.value.user_id, {
        name: userForm.value.name,
        email: userForm.value.email,
        role: userForm.value.role,
        is_active: userForm.value.is_active,
      })
    } else {
      await authService.createUser(userForm.value)
    }

    await loadUsers()
    closeModal()
  } catch (err) {
    formError.value = err.response?.data?.detail || 'Operation failed'
  } finally {
    formLoading.value = false
  }
}

const handleDeleteUser = async () => {
  formLoading.value = true

  try {
    await authService.deleteUser(deletingUser.value.user_id)
    await loadUsers()
    deletingUser.value = null
  } catch (err) {
    alert('Failed to delete user')
  } finally {
    formLoading.value = false
  }
}

onMounted(() => {
  loadUsers()
})
</script>

<style scoped>
.admin {
  max-width: 1200px;
}

h1 {
  color: #333;
  margin-bottom: 0.5rem;
}

.subtitle {
  color: #6c757d;
  margin-bottom: 2rem;
}

.admin-stats {
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
  margin: 0;
}

.users-section {
  background: white;
  padding: 2rem;
  border-radius: 10px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
}

.section-header h2 {
  color: #667eea;
  margin: 0;
}

.loading {
  text-align: center;
  padding: 2rem;
  color: #6c757d;
}

.error-message {
  background: #fee;
  color: #c33;
  padding: 0.75rem;
  border-radius: 5px;
  margin-bottom: 1rem;
}

.users-table {
  overflow-x: auto;
}

table {
  width: 100%;
  border-collapse: collapse;
}

th {
  text-align: left;
  padding: 1rem;
  background: #f8f9fa;
  color: #495057;
  font-weight: 600;
  border-bottom: 2px solid #dee2e6;
}

td {
  padding: 1rem;
  border-bottom: 1px solid #dee2e6;
}

tr:hover {
  background: #f8f9fa;
}

.badge {
  padding: 0.25rem 0.75rem;
  border-radius: 20px;
  font-size: 0.875rem;
  font-weight: 600;
  display: inline-block;
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

td.actions {
  display: flex;
  gap: 0.5rem;
}

.btn-icon {
  background: none;
  border: none;
  cursor: pointer;
  font-size: 1.25rem;
  padding: 0.25rem;
  transition: transform 0.2s;
}

.btn-icon:hover:not(:disabled) {
  transform: scale(1.2);
}

.btn-icon:disabled {
  opacity: 0.3;
  cursor: not-allowed;
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

.btn-danger {
  background: #d63031;
  color: white;
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
  max-width: 500px;
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

.form-group input[type="text"],
.form-group input[type="email"],
.form-group input[type="password"],
.form-group select {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid #ddd;
  border-radius: 5px;
  font-size: 1rem;
}

.form-group input:focus,
.form-group select:focus {
  outline: none;
  border-color: #667eea;
}

.form-group small {
  display: block;
  margin-top: 0.25rem;
  color: #6c757d;
  font-size: 0.875rem;
}

.warning {
  color: #d63031;
  font-weight: 500;
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
