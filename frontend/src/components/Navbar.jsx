import { Link, useNavigate } from 'react-router-dom'
import { useEffect, useState } from 'react'
import { useAuth } from '../context/AuthContext'
import { fetchCart } from '../services/api'

export default function Navbar() {
  const { user, logout, isAdmin } = useAuth()
  const navigate = useNavigate()
  const [cartCount, setCartCount] = useState(0)

  useEffect(() => {
    if (!user) { setCartCount(0); return }
    fetchCart().then((res) => setCartCount(res.data.item_count)).catch(() => {})
  }, [user])

  function handleLogout() {
    logout()
    navigate('/')
  }

  return (
    <nav className="navbar">
      <div className="navbar-inner">
        <Link to="/" className="navbar-brand">Aari Works</Link>
        <div className="navbar-links">
          <Link to="/products">Products</Link>
          {user && !isAdmin && (
            <>
              <Link to="/cart">Cart {cartCount > 0 && <span className="cart-badge">{cartCount}</span>}</Link>
              <Link to="/my-orders">My Orders</Link>
            </>
          )}
          {isAdmin && <Link to="/admin">Admin</Link>}
          {user ? (
            <button onClick={handleLogout}>Log out</button>
          ) : (
            <>
              <Link to="/login">Log in</Link>
              <Link to="/register">Register</Link>
            </>
          )}
        </div>
      </div>
    </nav>
  )
}
