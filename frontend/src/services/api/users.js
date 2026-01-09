/**
 * Users API Service
 * Handles user-related API calls
 */
import apiClient from './client'

export const usersApi = {
  /**
   * Search for a user by email
   */
  async searchByEmail(email) {
    const response = await apiClient.get('/users/search/by-email', {
      params: { email }
    })
    return response.data
  },

  /**
   * Get user by ID
   */
  async getUser(userId) {
    const response = await apiClient.get(`/users/${userId}`)
    return response.data
  }
}
