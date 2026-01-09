/**
 * API Service Index
 * Central export for all API services
 */
import { authApi } from './auth'
import { booksApi } from './books'
import { couponsApi } from './coupons'
import { poolsApi } from './pools'
import { usersApi } from './users'
import apiClient from './client'

export default apiClient

export {
  authApi,
  booksApi,
  couponsApi,
  poolsApi,
  usersApi
}
