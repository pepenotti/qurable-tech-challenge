/**
 * Coupon API Service
 * Handles all coupon-related API calls
 */
import apiClient from './client'

export const couponsApi = {
  /**
   * Get user's assigned coupons
   */
  async getUserCoupons(userId) {
    const response = await apiClient.get(`/users/${userId}/coupons`)
    return response.data
  },

  /**
   * Assign a random coupon to a user
   */
  async assignRandomCoupon(bookId, userId) {
    const response = await apiClient.post('/coupons/assign', { book_id: bookId, user_id: userId })
    return response.data
  },

  /**
   * Assign a specific coupon code to a user
   */
  async assignSpecificCoupon(code, userId) {
    const response = await apiClient.post(`/coupons/assign/${code}`, { user_id: userId })
    return response.data
  },

  /**
   * Lock a coupon for redemption (5 minute window)
   */
  async lockCoupon(code, userId) {
    const response = await apiClient.post(`/coupons/lock/${code}`, { user_id: userId })
    return response.data
  },

  /**
   * Unlock a temporarily locked coupon
   */
  async unlockCoupon(code, userId) {
    const response = await apiClient.post(`/coupons/unlock/${code}`, { user_id: userId })
    return response.data
  },

  /**
   * Redeem a coupon (permanent action)
   */
  async redeemCoupon(code, userId, metadata = null) {
    const response = await apiClient.post(`/coupons/redeem/${code}`, { 
      user_id: userId,
      redemption_metadata: metadata 
    })
    return response.data
  }
}
