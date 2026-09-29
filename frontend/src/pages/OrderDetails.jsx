import { useEffect, useState } from 'react'
import { useParams } from 'react-router-dom'
import { fetchOrder, fetchOrderTracking } from '../services/api'
import StatusBadge from '../components/StatusBadge'
import Spinner from '../components/Spinner'

export default function OrderDetails() {
  const { id } = useParams()
  const [order, setOrder] = useState(null)
  const [tracking, setTracking] = useState(null)

  useEffect(() => {
    fetchOrder(id).then((res) => setOrder(res.data))
    fetchOrderTracking(id).then((res) => setTracking(res.data))
  }, [id])

  if (!order) return <Spinner />

  return (
    <div className="container" style={{ padding: '2rem 1.5rem' }}>
      <div className="page-header">
        <div>
          <h2>{order.order_number}</h2>
          <p className="muted">Placed {new Date(order.created_at).toLocaleString()}</p>
        </div>
        <StatusBadge status={order.status} />
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr', gap: '2rem' }}>
        <div>
          <h3>Items</h3>
          {order.items.map((item) => (
            <div className="line-row" key={item.id}>
              <div className="line-info">
                <div className="line-name">{item.product_name}</div>
                <div className="line-meta">Qty {item.quantity} × ₹{Number(item.unit_price).toFixed(2)}</div>
              </div>
              <div className="line-total">₹{Number(item.total_price).toFixed(2)}</div>
            </div>
          ))}

          <h3 style={{ marginTop: '2rem' }}>Delivery address</h3>
          <p className="muted">
            {order.address.full_name}, {order.address.address_line1}
            {order.address.address_line2 ? `, ${order.address.address_line2}` : ''}<br />
            {order.address.city}, {order.address.state} {order.address.postal_code}
          </p>

          {tracking && (
            <>
              <h3 style={{ marginTop: '2rem' }}>Tracking</h3>
              <ul style={{ listStyle: 'none', padding: 0 }}>
                {tracking.timeline.map((t) => (
                  <li key={t.id} style={{ padding: '0.5rem 0', borderBottom: '1px dashed var(--line)' }}>
                    <StatusBadge status={t.status} />{' '}
                    <span className="muted" style={{ fontSize: '0.85rem' }}>
                      {new Date(t.created_at).toLocaleString()} {t.comment ? `— ${t.comment}` : ''}
                    </span>
                  </li>
                ))}
              </ul>
            </>
          )}
        </div>

        <div className="summary-box">
          <div className="summary-row"><span>Subtotal</span><span>₹{Number(order.subtotal).toFixed(2)}</span></div>
          <div className="summary-row"><span>Shipping</span><span>₹{Number(order.shipping_amount).toFixed(2)}</span></div>
          <div className="summary-row"><span>Tax</span><span>₹{Number(order.tax_amount).toFixed(2)}</span></div>
          <div className="summary-row total"><span>Total</span><span>₹{Number(order.total_amount).toFixed(2)}</span></div>
          {order.payment && (
            <p className="muted" style={{ fontSize: '0.82rem', marginTop: '0.8rem' }}>
              Payment: <StatusBadge status={order.payment.status} />
            </p>
          )}
        </div>
      </div>
    </div>
  )
}
