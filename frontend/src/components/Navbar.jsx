import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import { useCart } from '../context/CartContext'

export default function Navbar() {
  const { user, logout, isAdmin } = useAuth()
  const { cart } = useCart()
  const navigate = useNavigate()

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
              <Link to="/cart">
                Cart {cart.item_count > 0 && <span className="cart-badge">{cart.item_count}</span>}
              </Link>
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
