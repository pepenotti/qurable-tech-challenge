import apiClient from './api/client'

export const authService = {
  /**
   * Register a new user
   */
  async register(name, email, password) {
    const response = await apiClient.post('/auth/register', {
      name,
      email,
      password,
    })
    return response.data
  },

  /**
   * Login user
   */
  async login(email, password) {
    const response = await apiClient.post('/auth/login', {
      email,
      password,
    })
    return response.data
  },

  /**
   * Get current user profile
   */
  async getCurrentUser() {
    const response = await apiClient.get('/auth/me')
    return response.data
  },

  /**
   * Change password
   */
  async changePassword(currentPassword, newPassword) {
    const response = await apiClient.post('/auth/change-password', {
      current_password: currentPassword,
      new_password: newPassword,
    })
    return response.data
  },

  /**
   * Admin: Get all users
   */
  async getUsers() {
    const response = await apiClient.get('/auth/admin/users')
    return response.data
  },

  /**
   * Admin: Get user by ID
   */
  async getUser(userId) {
    const response = await apiClient.get(`/auth/admin/users/${userId}`)
    return response.data
  },

  /**
   * Admin: Create user
   */
  async createUser(userData) {
    const response = await apiClient.post('/auth/admin/users', userData)
    return response.data
  },

  /**
   * Admin: Update user
   */
  async updateUser(userId, userData) {
    const response = await apiClient.patch(`/auth/admin/users/${userId}`, userData)
    return response.data
  },

  /**
   * Admin: Delete user
   */
  async deleteUser(userId) {
    const response = await apiClient.delete(`/auth/admin/users/${userId}`)
    return response.data
  },
}
