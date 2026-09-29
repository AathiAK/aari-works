/**
 * Central Axios instance. Every API call in the app goes through this
 * file — components never call axios directly.
 */

import axios from 'axios'

const BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api'

const api = axios.create({ baseURL: BASE_URL })

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('aari_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('aari_token')
      if (!window.location.pathname.startsWith('/login')) {
        window.location.href = '/login'
      }
    }
    return Promise.reject(error)
  }
)

export function apiErrorMessage(error, fallback = 'Something went wrong. Please try again.') {
  // No response at all means the request never reached the server —
  // backend down, CORS rejection, or no network. Distinguish this from
  // a real error response, since the fix a person needs is different
  // ("try again shortly" vs. "check your input").
  if (error?.request && !error?.response) {
    return "Can't reach the server right now. Please check your connection and try again."
  }
  const detail = error?.response?.data?.detail
  if (typeof detail === 'string') return detail
  if (Array.isArray(detail) && detail[0]?.msg) return detail[0].msg
  return fallback
}

// ---- Auth ----
export const registerUser = (data) => api.post('/auth/register', data)
export const loginUser = (email, password) => {
  const form = new URLSearchParams()
  form.append('username', email)
  form.append('password', password)
  return api.post('/auth/login', form, {
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
  })
}
export const fetchMe = () => api.get('/auth/me')

// ---- Categories ----
export const fetchCategories = () => api.get('/categories')
export const createCategory = (data) => api.post('/categories', data)

// ---- Products ----
export const fetchProducts = (params) => api.get('/products', { params })
export const fetchProduct = (id) => api.get(`/products/${id}`)
export const createProduct = (data) => api.post('/products', data)
export const updateProduct = (id, data) => api.put(`/products/${id}`, data)
export const deleteProduct = (id) => api.delete(`/products/${id}`)
export const uploadProductImage = (id, file) => {
  const form = new FormData()
  form.append('file', file)
  return api.post(`/admin/products/${id}/image`, form, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })
}

// ---- Cart ----
export const fetchCart = () => api.get('/cart')
export const addCartItem = (productId, quantity) => api.post('/cart/items', { product_id: productId, quantity })
export const updateCartItem = (id, quantity) => api.put(`/cart/items/${id}`, { quantity })
export const removeCartItem = (id) => api.delete(`/cart/items/${id}`)

// ---- Addresses ----
export const fetchAddresses = () => api.get('/addresses')
export const createAddress = (data) => api.post('/addresses', data)

// ---- Checkout ----
export const fetchCheckoutPreview = (addressId) => api.get('/checkout/preview', { params: { address_id: addressId } })

// ---- Orders ----
export const createOrder = (addressId) => api.post('/orders', { address_id: addressId })
export const fetchMyOrders = (params) => api.get('/orders', { params })
export const fetchOrder = (id) => api.get(`/orders/${id}`)
export const fetchOrderTracking = (id) => api.get(`/orders/${id}/tracking`)

// ---- Payments ----
export const createPayment = (orderId, mockOutcome) =>
  api.post('/payments/create', { order_id: orderId, mock_outcome: mockOutcome || undefined })
export const fetchPayment = (id) => api.get(`/payments/${id}`)
export const simulatePayment = (id, outcome) => api.post(`/payments/${id}/simulate`, { outcome })

// ---- Admin ----
export const fetchAdminUsers = () => api.get('/admin/users')
export const fetchAdminOrders = (params) => api.get('/admin/orders', { params })
export const updateOrderStatus = (id, status, comment) =>
  api.put(`/admin/orders/${id}/status`, { status, comment })
export const refundPayment = (id, comment) => api.post(`/admin/payments/${id}/refund`, { comment })

export default api
