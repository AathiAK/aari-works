import { Link, useParams } from 'react-router-dom'

export default function OrderSuccess() {
  const { orderId } = useParams()
  return (
    <div className="container empty-state">
      <h2 style={{ color: 'var(--indigo-900)' }}>Order confirmed</h2>
      <p className="muted">Thank you — your order has been placed successfully.</p>
      <div style={{ display: 'flex', gap: '1rem', justifyContent: 'center', marginTop: '1.5rem' }}>
        <Link to={`/my-orders/${orderId}`} className="btn btn-primary">View order</Link>
        <Link to="/products" className="btn btn-secondary">Continue shopping</Link>
      </div>
    </div>
  )
}
