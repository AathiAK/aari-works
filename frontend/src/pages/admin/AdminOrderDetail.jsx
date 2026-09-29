import { useEffect, useState } from 'react'
import { useParams } from 'react-router-dom'
import { apiErrorMessage, fetchOrder, refundPayment, updateOrderStatus } from '../../services/api'
import StatusBadge from '../../components/StatusBadge'
import Spinner from '../../components/Spinner'

const NEXT_STATUS = {
  PENDING: 'CANCELLED', PAYMENT_PENDING: 'CANCELLED', CONFIRMED: 'PROCESSING',
  PROCESSING: 'PACKED', PACKED: 'SHIPPED', SHIPPED: 'OUT_FOR_DELIVERY',
  OUT_FOR_DELIVERY: 'DELIVERED', DELIVERED: 'RETURN_REQUESTED', RETURN_REQUESTED: 'RETURNED',
}

export default function AdminOrderDetail() {
  const { id } = useParams()
  const [order, setOrder] = useState(null)
  const [error, setError] = useState('')

  function load() {
    fetchOrder(id).then((res) => setOrder(res.data))
  }
  useEffect(load, [id])

  async function advance() {
    setError('')
    try {
      await updateOrderStatus(order.id, NEXT_STATUS[order.status])
      load()
    } catch (err) {
      setError(apiErrorMessage(err, 'Could not update status.'))
    }
  }

  async function doRefund() {
    setError('')
    try {
      await refundPayment(order.payment.id, 'Refunded by admin')
      load()
    } catch (err) {
      setError(apiErrorMessage(err, 'Could not process refund.'))
    }
  }

  if (!order) return <Spinner />

  const canAdvance = Boolean(NEXT_STATUS[order.status])
  const canRefund = order.payment?.status === 'SUCCESS'

  return (
    <div>
      <div className="page-header">
        <div><h2>{order.order_number}</h2><p className="muted">{order.address.full_name} — {order.address.city}</p></div>
        <StatusBadge status={order.status} />
      </div>
      {error && <div className="form-error">{error}</div>}

      {order.items.map((item) => (
        <div className="line-row" key={item.id}>
          <div className="line-info">
            <div className="line-name">{item.product_name}</div>
            <div className="line-meta">Qty {item.quantity} × ₹{Number(item.unit_price).toFixed(2)}</div>
          </div>
          <div className="line-total">₹{Number(item.total_price).toFixed(2)}</div>
        </div>
      ))}

      <div style={{ display: 'flex', gap: '0.75rem', marginTop: '1.5rem' }}>
        {canAdvance && (
          <button className="btn btn-primary" onClick={advance}>
            Mark {NEXT_STATUS[order.status].replaceAll('_', ' ')}
          </button>
        )}
        {canRefund && (
          <button className="btn btn-danger" onClick={doRefund}>Refund payment</button>
        )}
      </div>

      <h3 style={{ marginTop: '2rem' }}>Status history</h3>
      <ul style={{ listStyle: 'none', padding: 0 }}>
        {order.status_history.map((h) => (
          <li key={h.id} style={{ padding: '0.5rem 0', borderBottom: '1px dashed var(--line)' }}>
            <StatusBadge status={h.status} />{' '}
            <span className="muted" style={{ fontSize: '0.85rem' }}>
              {new Date(h.created_at).toLocaleString()} {h.comment ? `— ${h.comment}` : ''}
            </span>
          </li>
        ))}
      </ul>
    </div>
  )
}
