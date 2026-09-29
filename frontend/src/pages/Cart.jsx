import { Link, useNavigate } from 'react-router-dom'
import { apiErrorMessage } from '../services/api'
import { useCart } from '../context/CartContext'
import { useState } from 'react'

export default function Cart() {
  const { cart, updateItem, removeItem } = useCart()
  const [error, setError] = useState('')
  const navigate = useNavigate()

  async function changeQty(item, newQty) {
    setError('')
    if (newQty < 1) return
    try {
      await updateItem(item.id, newQty)
    } catch (err) {
      setError(apiErrorMessage(err, 'Could not update quantity.'))
    }
  }

  async function remove(item) {
    setError('')
    try {
      await removeItem(item.id)
    } catch (err) {
      setError(apiErrorMessage(err, 'Could not remove this item.'))
    }
  }

  return (
    <div className="container" style={{ padding: '2rem 1.5rem' }}>
      <h2>Your cart</h2>
      {error && <div className="form-error">{error}</div>}

      {cart.items.length === 0 ? (
        <div className="empty-state">
          Your cart is empty. <Link to="/products">Browse products</Link>
        </div>
      ) : (
        <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr', gap: '2rem' }}>
          <div>
            {cart.items.map((item) => (
              <div className="line-row" key={item.id}>
                {item.image_url ? (
                  <img src={item.image_url} alt={item.product_name} />
                ) : (
                  <div className="line-image-placeholder" />
                )}
                <div className="line-info">
                  <div className="line-name">{item.product_name}</div>
                  <div className="line-meta">₹{Number(item.unit_price).toFixed(2)} each</div>
                  {!item.in_stock && <div className="line-meta" style={{ color: 'var(--maroon-600)' }}>Limited stock — quantity may need adjusting</div>}
                  <div className="qty-control" style={{ marginTop: '0.4rem' }}>
                    <button onClick={() => changeQty(item, item.quantity - 1)}>−</button>
                    <span>{item.quantity}</span>
                    <button onClick={() => changeQty(item, item.quantity + 1)}>+</button>
                    <button className="btn btn-danger btn-sm" style={{ marginLeft: '0.8rem' }} onClick={() => remove(item)}>
                      Remove
                    </button>
                  </div>
                </div>
                <div className="line-total">₹{Number(item.line_total).toFixed(2)}</div>
              </div>
            ))}
          </div>

          <div className="summary-box">
            <div className="summary-row">
              <span>Subtotal</span>
              <span>₹{Number(cart.subtotal).toFixed(2)}</span>
            </div>
            <p className="muted" style={{ fontSize: '0.82rem' }}>
              Shipping and tax are calculated at checkout.
            </p>
            <button
              className="btn btn-primary btn-block"
              style={{ marginTop: '1rem' }}
              onClick={() => navigate('/checkout')}
            >
              Proceed to checkout
            </button>
          </div>
        </div>
      )}
    </div>
  )
}
