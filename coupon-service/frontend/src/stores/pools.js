/**
 * Pools Pinia Store
 * Manages user pool state
 */
import { defineStore } from 'pinia'
import { poolsApi } from '@/services/api/index'
import { useAuthStore } from './auth'

export const usePoolsStore = defineStore('pools', {
  state: () => ({
    pools: [],
    selectedPool: null,
    loading: {
      pools: false,
      action: false
    },
    error: null
  }),

  getters: {
    activePools: (state) => state.pools.filter(p => p.is_active),
    poolCount: (state) => state.pools.length,
    
    getPoolById: (state) => (poolId) => {
      return state.pools.find(p => p.pool_id === poolId)
    }
  },

  actions: {
    async fetchPools() {
      this.loading.pools = true
      this.error = null
      
      try {
        this.pools = await poolsApi.getAllPools()
      } catch (error) {
        this.error = error.response?.data?.detail || 'Failed to load pools'
        console.error('Error fetching pools:', error)
      } finally {
        this.loading.pools = false
      }
    },

    async fetchPoolDetails(poolId) {
      this.loading.action = true
      this.error = null
      
      try {
        this.selectedPool = await poolsApi.getPool(poolId)
        return this.selectedPool
      } catch (error) {
        this.error = error.response?.data?.detail || 'Failed to load pool details'
        console.error('Error fetching pool:', error)
        throw error
      } finally {
        this.loading.action = false
      }
    },

    async createPool(poolData) {
      this.loading.action = true
      this.error = null
      
      try {
        const newPool = await poolsApi.createPool(poolData)
        this.pools.unshift(newPool)
        return newPool
      } catch (error) {
        this.error = error.response?.data?.detail || 'Failed to create pool'
        console.error('Error creating pool:', error)
        throw error
      } finally {
        this.loading.action = false
      }
    },

    async updatePool(poolId, poolData) {
      this.loading.action = true
      this.error = null
      
      try {
        const updated = await poolsApi.updatePool(poolId, poolData)
        const index = this.pools.findIndex(p => p.pool_id === poolId)
        if (index !== -1) {
          this.pools[index] = updated
        }
        if (this.selectedPool?.pool_id === poolId) {
          this.selectedPool = updated
        }
        return updated
      } catch (error) {
        this.error = error.response?.data?.detail || 'Failed to update pool'
        console.error('Error updating pool:', error)
        throw error
      } finally {
        this.loading.action = false
      }
    },

    async deletePool(poolId) {
      this.loading.action = true
      this.error = null
      
      try {
        await poolsApi.deletePool(poolId)
        this.pools = this.pools.filter(p => p.pool_id !== poolId)
        if (this.selectedPool?.pool_id === poolId) {
          this.selectedPool = null
        }
      } catch (error) {
        this.error = error.response?.data?.detail || 'Failed to delete pool'
        console.error('Error deleting pool:', error)
        throw error
      } finally {
        this.loading.action = false
      }
    },

    async addUsersToPool(poolId, userIds) {
      this.loading.action = true
      this.error = null
      
      try {
        const updated = await poolsApi.addUsersToPool(poolId, userIds)
        const index = this.pools.findIndex(p => p.pool_id === poolId)
        if (index !== -1) {
          this.pools[index] = updated
        }
        if (this.selectedPool?.pool_id === poolId) {
          this.selectedPool = updated
        }
        return updated
      } catch (error) {
        this.error = error.response?.data?.detail || 'Failed to add users'
        console.error('Error adding users:', error)
        throw error
      } finally {
        this.loading.action = false
      }
    },

    async removeUsersFromPool(poolId, userIds) {
      this.loading.action = true
      this.error = null
      
      try {
        const updated = await poolsApi.removeUsersFromPool(poolId, userIds)
        const index = this.pools.findIndex(p => p.pool_id === poolId)
        if (index !== -1) {
          this.pools[index] = updated
        }
        if (this.selectedPool?.pool_id === poolId) {
          this.selectedPool = updated
        }
        return updated
      } catch (error) {
        this.error = error.response?.data?.detail || 'Failed to remove users'
        console.error('Error removing users:', error)
        throw error
      } finally {
        this.loading.action = false
      }
    },

    async bulkAssignCoupons(bookId, poolId, distributionMode, couponsPerUser) {
      this.loading.action = true
      this.error = null
      
      try {
        const result = await poolsApi.bulkAssignCoupons(bookId, poolId, distributionMode, couponsPerUser)
        return result
      } catch (error) {
        this.error = error.response?.data?.detail || 'Failed to assign coupons'
        console.error('Error bulk assigning:', error)
        throw error
      } finally {
        this.loading.action = false
      }
    },

    clearError() {
      this.error = null
    },

    clearSelectedPool() {
      this.selectedPool = null
    }
  }
})
