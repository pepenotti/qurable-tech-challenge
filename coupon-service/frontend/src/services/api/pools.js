/**
 * User Pools API Service
 * Handles all pool-related API calls
 */
import apiClient from './client'

export const poolsApi = {
  /**
   * Get all pools
   */
  async getAllPools() {
    const response = await apiClient.get('/pools/')
    return response.data
  },

  /**
   * Get pool details with user list
   */
  async getPool(poolId) {
    const response = await apiClient.get(`/pools/${poolId}`)
    return response.data
  },

  /**
   * Create a new pool
   */
  async createPool(poolData) {
    const response = await apiClient.post('/pools/', poolData)
    return response.data
  },

  /**
   * Update pool
   */
  async updatePool(poolId, poolData) {
    const response = await apiClient.patch(`/pools/${poolId}`, poolData)
    return response.data
  },

  /**
   * Delete pool
   */
  async deletePool(poolId) {
    await apiClient.delete(`/pools/${poolId}`)
  },

  /**
   * Add users to pool
   */
  async addUsersToPool(poolId, userIds) {
    const response = await apiClient.post(`/pools/${poolId}/users`, {
      user_ids: userIds
    })
    return response.data
  },

  /**
   * Remove users from pool
   */
  async removeUsersFromPool(poolId, userIds) {
    const response = await apiClient.delete(`/pools/${poolId}/users`, {
      data: { user_ids: userIds }
    })
    return response.data
  },

  /**
   * Bulk assign coupons to pool
   */
  async bulkAssignCoupons(bookId, poolId, distributionMode = 'random', couponsPerUser = 1) {
    const response = await apiClient.post('/pools/bulk-assign', {
      book_id: bookId,
      pool_id: poolId,
      distribution_mode: distributionMode,
      coupons_per_user: couponsPerUser
    })
    return response.data
  }
}
