import { useEffect, useState } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { apiErrorMessage, fetchProduct } from '../services/api'
import { useAuth } from '../context/AuthContext'
import { useCart } from '../context/CartContext'
import Spinner from '../components/Spinner'

export default function ProductDetails() {
  const { id } = useParams()
  const { user } = useAuth()
  const { addItem } = useCart()
  const navigate = useNavigate()
  const [product, setProduct] = useState(null)
  const [quantity, setQuantity] = useState(1)
  const [error, setError] = useState('')
  const [message, setMessage] = useState('')
  const [adding, setAdding] = useState(false)

  useEffect(() => {
    fetchProduct(id).then((res) => setProduct(res.data)).catch(() => setError('Product not found.'))
  }, [id])

  async function handleAddToCart() {
    if (!user) { navigate('/login'); return }
    setError('')
    setMessage('')
    setAdding(true)
    try {
      await addItem(product.id, quantity)
      setMessage('Added to cart.')
    } catch (err) {
      setError(apiErrorMessage(err, 'Could not add this item to your cart.'))
    } finally {
      setAdding(false)
    }
  }

  if (error && !product) return <div className="container empty-state">{error}</div>
  if (!product) return <Spinner />

  return (
    <div className="container" style={{ padding: '2rem 1.5rem' }}>
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '2.5rem' }}>
        {product.image_url ? (
          <img src={product.image_url} alt={product.name} style={{ width: '100%', borderRadius: 'var(--radius)' }} />
        ) : (
          <div className="product-image-placeholder" style={{ aspectRatio: '1/1' }}>No image</div>
        )}
        <div>
          <h1 style={{ fontSize: '1.8rem' }}>{product.name}</h1>
          <p className="muted">{product.category?.name}</p>
          <p style={{ fontFamily: 'var(--font-display)', fontSize: '1.6rem', color: 'var(--marigold-600)' }}>
            ₹{Number(product.price).toFixed(2)}
          </p>
          <p>{product.description}</p>
          <p className="muted">
            {product.stock_quantity > 0 ? `${product.stock_quantity} in stock` : 'Out of stock'}
          </p>

          {error && <div className="form-error">{error}</div>}
          {message && <div className="form-success">{message}</div>}

          {product.stock_quantity > 0 && (
            <div style={{ display: 'flex', gap: '1rem', alignItems: 'center', marginTop: '1.2rem' }}>
              <div className="qty-control">
                <button type="button" onClick={() => setQuantity((q) => Math.max(1, q - 1))}>−</button>
                <span>{quantity}</span>
                <button
                  type="button"
                  onClick={() => setQuantity((q) => Math.min(product.stock_quantity, q + 1))}
                >+</button>
              </div>
              <button className="btn btn-primary" onClick={handleAddToCart} disabled={adding}>
                {adding ? 'Adding…' : 'Add to cart'}
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
