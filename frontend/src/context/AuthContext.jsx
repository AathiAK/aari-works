/**
 * Auth state: current user, loading flag, login/register/logout actions.
 * On first load, if a token is in localStorage, we validate it against
 * GET /auth/me rather than trusting it blindly — an expired token is
 * cleared immediately instead of producing confusing 401s later.
 */

import { createContext, useContext, useEffect, useState } from 'react'
import { fetchMe, loginUser, registerUser } from '../services/api'

const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const token = localStorage.getItem('aari_token')
    if (!token) {
      setLoading(false)
      return
    }
    fetchMe()
      .then((res) => setUser(res.data))
      .catch(() => localStorage.removeItem('aari_token'))
      .finally(() => setLoading(false))
  }, [])

  async function login(email, password) {
    const res = await loginUser(email, password)
    localStorage.setItem('aari_token', res.data.access_token)
    const me = await fetchMe()
    setUser(me.data)
    return me.data
  }

  async function register(data) {
    await registerUser(data)
    return login(data.email, data.password)
  }

  function logout() {
    localStorage.removeItem('aari_token')
    setUser(null)
  }

  const value = { user, loading, login, register, logout, isAdmin: user?.role === 'ADMIN' }
  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export function useAuth() {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error('useAuth must be used within AuthProvider')
  return ctx
}
