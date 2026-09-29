/**
 * Shared cart state. Every place that adds, updates, or removes a cart
 * item goes through this context instead of calling the API directly
 * and managing local state — that's what let the Navbar's item count
 * go stale in Phase 14. Now every mutation updates the one shared cart
 * object, and everything reading it (Navbar, Cart page) re-renders
 * together.
 */

import { createContext, useCallback, useContext, useEffect, useState } from 'react'
import { addCartItem, fetchCart, removeCartItem, updateCartItem } from '../services/api'
import { useAuth } from './AuthContext'

const CartContext = createContext(null)

const EMPTY_CART = { items: [], subtotal: '0.00', item_count: 0 }

export function CartProvider({ children }) {
  const { user } = useAuth()
  const [cart, setCart] = useState(EMPTY_CART)

  const refresh = useCallback(() => {
    if (!user) {
      setCart(EMPTY_CART)
      return Promise.resolve(EMPTY_CART)
    }
    return fetchCart().then((res) => {
      setCart(res.data)
      return res.data
    })
  }, [user])

  useEffect(() => {
    refresh()
  }, [refresh])

  async function addItem(productId, quantity) {
    const res = await addCartItem(productId, quantity)
    setCart(res.data)
    return res.data
  }

  async function updateItem(cartItemId, quantity) {
    const res = await updateCartItem(cartItemId, quantity)
    setCart(res.data)
    return res.data
  }

  async function removeItem(cartItemId) {
    const res = await removeCartItem(cartItemId)
    setCart(res.data)
    return res.data
  }

  return (
    <CartContext.Provider value={{ cart, refresh, addItem, updateItem, removeItem }}>
      {children}
    </CartContext.Provider>
  )
}

export function useCart() {
  const ctx = useContext(CartContext)
  if (!ctx) throw new Error('useCart must be used within CartProvider')
  return ctx
}
