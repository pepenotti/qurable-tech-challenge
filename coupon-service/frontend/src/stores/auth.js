import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { authService } from '@/services/auth'

export const useAuthStore = defineStore('auth', () => {
  // State
  const token = ref(localStorage.getItem('token') || null)
  const user = ref(JSON.parse(localStorage.getItem('user') || 'null'))

  // Getters
  const isAuthenticated = computed(() => !!token.value)
  const isAdmin = computed(() => user.value?.role === 'admin')

  // Actions
  async function login(email, password) {
    try {
      const data = await authService.login(email, password)
      
      token.value = data.access_token
      user.value = data.user
      
      localStorage.setItem('token', data.access_token)
      localStorage.setItem('user', JSON.stringify(data.user))
      
      return { success: true }
    } catch (error) {
      return {
        success: false,
        error: error.response?.data?.detail || 'Login failed',
      }
    }
  }

  async function register(name, email, password) {
    try {
      const data = await authService.register(name, email, password)
      
      token.value = data.access_token
      user.value = data.user
      
      localStorage.setItem('token', data.access_token)
      localStorage.setItem('user', JSON.stringify(data.user))
      
      return { success: true }
    } catch (error) {
      return {
        success: false,
        error: error.response?.data?.detail || 'Registration failed',
      }
    }
  }

  async function fetchCurrentUser() {
    try {
      const userData = await authService.getCurrentUser()
      user.value = userData
      localStorage.setItem('user', JSON.stringify(userData))
      return { success: true }
    } catch (error) {
      logout()
      return { success: false }
    }
  }

  function logout() {
    token.value = null
    user.value = null
    localStorage.removeItem('token')
    localStorage.removeItem('user')
  }

  async function changePassword(currentPassword, newPassword) {
    try {
      await authService.changePassword(currentPassword, newPassword)
      return { success: true }
    } catch (error) {
      return {
        success: false,
        error: error.response?.data?.detail || 'Password change failed',
      }
    }
  }

  return {
    token,
    user,
    isAuthenticated,
    isAdmin,
    login,
    register,
    logout,
    fetchCurrentUser,
    changePassword,
  }
})
