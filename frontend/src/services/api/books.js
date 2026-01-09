/**
 * Books API Service
 * Handles all coupon book-related API calls
 */
import apiClient from './client'

export const booksApi = {
  /**
   * Get all coupon books
   */
  async getAllBooks() {
    const response = await apiClient.get('/books/')
    return response.data
  },

  /**
   * Get a single book by ID
   */
  async getBook(bookId) {
    const response = await apiClient.get(`/books/${bookId}`)
    return response.data
  },

  /**
   * Create a new coupon book
   */
  async createBook(bookData) {
    const response = await apiClient.post('/books/', bookData)
    return response.data
  },

  /**
   * Get all coupons in a specific book
   */
  async getBookCoupons(bookId) {
    const response = await apiClient.get(`/books/${bookId}/coupons`)
    return response.data
  },

  /**
   * Get redemption history for a book
   */
  async getRedemptionHistory(bookId) {
    const response = await apiClient.get(`/books/${bookId}/redemption-history`)
    return response.data
  },

  /**
   * Generate random codes for a book
   */
  async generateCodes(bookId, count, length = 8) {
    const response = await apiClient.post(`/books/${bookId}/codes/generate`, {
      count,
      length
    })
    return response.data
  },

  /**
   * Upload custom code list for a book
   */
  async uploadCodes(bookId, codes) {
    const response = await apiClient.post(`/books/${bookId}/codes/upload`, {
      codes
    })
    return response.data
  }
}
