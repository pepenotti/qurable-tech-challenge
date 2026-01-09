/**
 * Authentication API Service
 * Handles all auth-related API calls
 */
import apiClient from './client'

export const authApi = {
  /**
   * Login user
   */
  login: async (email, password) => {
    const response = await apiClient.post('/auth/login', { email, password })
    return response.data
  },

  /**
   * Register new user
   */
  register: async (userData) => {
    const response = await apiClient.post('/auth/register', userData)
    return response.data
  },

  /**
   * Get current user profile
   */
  getProfile: async () => {
    const response = await apiClient.get('/auth/me')
    return response.data
  },

  /**
   * Update user profile
   */
  updateProfile: async (userData) => {
    const response = await apiClient.put('/auth/me', userData)
    return response.data
  },

  /**
   * Change password
   */
  changePassword: async (oldPassword, newPassword) => {
    const response = await apiClient.post('/auth/change-password', {
      old_password: oldPassword,
      new_password: newPassword
    })
    return response.data
  }
}
