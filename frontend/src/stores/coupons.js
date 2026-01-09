/**
 * Coupons Pinia Store
 * Manages coupon and book state
 */
import { defineStore } from 'pinia'
import { booksApi, couponsApi } from '@/services/api/index'
import { useAuthStore } from './auth'

export const useCouponsStore = defineStore('coupons', {
  state: () => ({
    // User's coupons
    myCoupons: [],
    
    // All available books
    books: [],
    
    // Currently selected book details
    selectedBook: null,
    selectedBookCoupons: [],
    
    // Redemption history
    redemptionHistory: [],
    
    // Loading states
    loading: {
      coupons: false,
      books: false,
      action: false
    },
    
    // Error handling
    error: null
  }),

  getters: {
    // Get coupons by state
    availableCoupons: (state) => 
      state.myCoupons.filter(c => c.state === 'ASSIGNED'),
    
    lockedCoupons: (state) => 
      state.myCoupons.filter(c => c.state === 'LOCKED'),
    
    redeemedCoupons: (state) => 
      state.myCoupons.filter(c => c.state === 'REDEEMED'),
    
    // Count statistics
    stats: (state) => ({
      total: state.myCoupons.length,
      available: state.myCoupons.filter(c => c.state === 'ASSIGNED').length,
      locked: state.myCoupons.filter(c => c.state === 'LOCKED').length,
      redeemed: state.myCoupons.filter(c => c.state === 'REDEEMED').length
    }),
    
    // Get books owned by current user
    myBooks: (state) => {
      const authStore = useAuthStore()
      if (!authStore.user) return []
      return state.books.filter(b => b.owner_id === authStore.user.user_id)
    }
  },

  actions: {
    /**
     * Fetch user's coupons
     */
    async fetchMyCoupons() {
      const authStore = useAuthStore()
      if (!authStore.user) {
        this.error = 'User not authenticated'
        return
      }

      this.loading.coupons = true
      this.error = null

      try {
        const data = await couponsApi.getUserCoupons(authStore.user.user_id)
        this.myCoupons = data.coupons || []
      } catch (error) {
        this.error = error.response?.data?.detail || 'Failed to fetch coupons'
        console.error('Error fetching coupons:', error)
      } finally {
        this.loading.coupons = false
      }
    },

    /**
     * Fetch all available books
     */
    async fetchBooks() {
      this.loading.books = true
      this.error = null

      try {
        this.books = await booksApi.getAllBooks()
      } catch (error) {
        this.error = error.response?.data?.detail || 'Failed to fetch books'
        console.error('Error fetching books:', error)
      } finally {
        this.loading.books = false
      }
    },

    /**
     * Create a new coupon book
     */
    async createBook(bookData) {
      const authStore = useAuthStore()
      if (!authStore.user) {
        throw new Error('User not authenticated')
      }

      this.loading.action = true
      this.error = null

      try {
        const newBook = await booksApi.createBook({
          ...bookData,
          owner_id: authStore.user.user_id
        })
        this.books.push(newBook)
        return newBook
      } catch (error) {
        this.error = error.response?.data?.detail || 'Failed to create book'
        throw error
      } finally {
        this.loading.action = false
      }
    },

    /**
     * Generate codes for a book
     */
    async generateCodes(bookId, count, length = 8) {
      this.loading.action = true
      this.error = null

      try {
        const result = await booksApi.generateCodes(bookId, count, length)
        await this.fetchBooks() // Refresh books list
        return result
      } catch (error) {
        this.error = error.response?.data?.detail || 'Failed to generate codes'
        throw error
      } finally {
        this.loading.action = false
      }
    },

    /**
     * Upload custom codes for a book
     */
    async uploadCodes(bookId, codes) {
      this.loading.action = true
      this.error = null

      try {
        const result = await booksApi.uploadCodes(bookId, codes)
        await this.fetchBooks() // Refresh books list
        return result
      } catch (error) {
        this.error = error.response?.data?.detail || 'Failed to upload codes'
        throw error
      } finally {
        this.loading.action = false
      }
    },

    /**
     * Assign a random coupon from a book to current user
     */
    async assignRandomCoupon(bookId) {
      const authStore = useAuthStore()
      if (!authStore.user) {
        throw new Error('User not authenticated')
      }

      this.loading.action = true
      this.error = null

      try {
        const coupon = await couponsApi.assignRandomCoupon(bookId, authStore.user.user_id)
        await this.fetchMyCoupons() // Refresh user's coupons
        return coupon
      } catch (error) {
        this.error = error.response?.data?.detail || 'Failed to assign coupon'
        throw error
      } finally {
        this.loading.action = false
      }
    },

    /**
     * Lock a coupon for redemption
     */
    async lockCoupon(code) {
      const authStore = useAuthStore()
      if (!authStore.user) {
        throw new Error('User not authenticated')
      }

      this.loading.action = true
      this.error = null

      try {
        const coupon = await couponsApi.lockCoupon(code, authStore.user.user_id)
        await this.fetchMyCoupons() // Refresh to show locked state
        return coupon
      } catch (error) {
        this.error = error.response?.data?.detail || 'Failed to lock coupon'
        throw error
      } finally {
        this.loading.action = false
      }
    },

    /**
     * Unlock a coupon
     */
    async unlockCoupon(code) {
      const authStore = useAuthStore()
      if (!authStore.user) {
        throw new Error('User not authenticated')
      }

      this.loading.action = true
      this.error = null

      try {
        const coupon = await couponsApi.unlockCoupon(code, authStore.user.user_id)
        await this.fetchMyCoupons() // Refresh
        return coupon
      } catch (error) {
        this.error = error.response?.data?.detail || 'Failed to unlock coupon'
        throw error
      } finally {
        this.loading.action = false
      }
    },

    /**
     * Redeem a coupon (permanent action)
     */
    async redeemCoupon(code, metadata = null) {
      const authStore = useAuthStore()
      if (!authStore.user) {
        throw new Error('User not authenticated')
      }

      this.loading.action = true
      this.error = null

      try {
        const result = await couponsApi.redeemCoupon(code, authStore.user.user_id, metadata)
        await this.fetchMyCoupons() // Refresh to show redeemed state
        return result
      } catch (error) {
        this.error = error.response?.data?.detail || 'Failed to redeem coupon'
        throw error
      } finally {
        this.loading.action = false
      }
    },

    /**
     * Fetch book details with its coupons
     */
    async fetchBookDetails(bookId) {
      this.loading.books = true
      this.error = null

      try {
        const coupons = await booksApi.getBookCoupons(bookId)
        const book = this.books.find(b => b.book_id === bookId)
        
        this.selectedBook = book
        this.selectedBookCoupons = coupons
      } catch (error) {
        this.error = error.response?.data?.detail || 'Failed to fetch book details'
        console.error('Error fetching book details:', error)
      } finally {
        this.loading.books = false
      }
    },

    /**
     * Fetch redemption history for a book
     */
    async fetchRedemptionHistory(bookId) {
      this.loading.books = true
      this.error = null

      try {
        this.redemptionHistory = await booksApi.getRedemptionHistory(bookId)
      } catch (error) {
        this.error = error.response?.data?.detail || 'Failed to fetch redemption history'
        console.error('Error fetching redemption history:', error)
      } finally {
        this.loading.books = false
      }
    },

    /**
     * Clear error
     */
    clearError() {
      this.error = null
    },

    /**
     * Reset store
     */
    $reset() {
      this.myCoupons = []
      this.books = []
      this.selectedBook = null
      this.selectedBookCoupons = []
      this.redemptionHistory = []
      this.loading = { coupons: false, books: false, action: false }
      this.error = null
    }
  }
})
