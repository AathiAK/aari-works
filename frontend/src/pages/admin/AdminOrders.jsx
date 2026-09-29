import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import {
  apiErrorMessage, fetchAdminOrders, refundPayment, updateOrderStatus,
} from '../../services/api'
import StatusBadge from '../../components/StatusBadge'
import Spinner from '../../components/Spinner'

const NEXT_STATUS = {
  PENDING: 'CANCELLED',
  PAYMENT_PENDING: 'CANCELLED',
  CONFIRMED: 'PROCESSING',
  PROCESSING: 'PACKED',
  PACKED: 'SHIPPED',
  SHIPPED: 'OUT_FOR_DELIVERY',
  OUT_FOR_DELIVERY: 'DELIVERED',
  DELIVERED: 'RETURN_REQUESTED',
  RETURN_REQUESTED: 'RETURNED',
}

export default function AdminOrders() {
  const [orders, setOrders] = useState(null)
  const [statusFilter, setStatusFilter] = useState('')
  const [search, setSearch] = useState('')
  const [error, setError] = useState('')

  function load() {
    const params = {}
    if (statusFilter) params.status = statusFilter
    if (search) params.search = search
    fetchAdminOrders(params).then((res) => setOrders(res.data.items))
  }

  useEffect(() => {
    const t = setTimeout(load, 300)
    return () => clearTimeout(t)
  }, [statusFilter, search])

  async function advance(order) {
    const next = NEXT_STATUS[order.status]
    if (!next) return
    setError('')
    try {
      await updateOrderStatus(order.id, next)
      load()
    } catch (err) {
      setError(apiErrorMessage(err, 'Could not update order status.'))
    }
  }

  async function refund(order) {
    if (!order.payment_status || order.payment_status !== 'SUCCESS') return
    setError('')
    try {
      // payment id isn't in the list row; fetch order detail's payment id via admin order list
      // simplest: call refund by looking up the order's payment through the order detail page instead.
      // Kept here as a guarded no-op prompt to use the detail view.
      alert('Open the order detail page to refund this order\'s payment.')
    } catch (err) {
      setError(apiErrorMessage(err))
    }
  }

  if (!orders) return <Spinner />

  return (
    <div>
      <h2>Orders</h2>
      {error && <div className="form-error">{error}</div>}

      <div className="filters-bar">
        <input placeholder="Search order # or email…" value={search} onChange={(e) => setSearch(e.target.value)} />
        <select value={statusFilter} onChange={(e) => setStatusFilter(e.target.value)}>
          <option value="">All statuses</option>
          {Object.keys(NEXT_STATUS).concat(['DELIVERED', 'CANCELLED', 'REFUNDED']).map((s) => (
            <option key={s} value={s}>{s.replaceAll('_', ' ')}</option>
          ))}
        </select>
      </div>

      <table>
        <thead>
          <tr><th>Order</th><th>Customer</th><th>Status</th><th>Payment</th><th>Total</th><th></th></tr>
        </thead>
        <tbody>
          {orders.map((o) => (
            <tr key={o.id}>
              <td><Link to={`/admin/orders/${o.id}`}>{o.order_number}</Link></td>
              <td>{o.customer_name}<br /><span className="muted" style={{ fontSize: '0.8rem' }}>{o.customer_email}</span></td>
              <td><StatusBadge status={o.status} /></td>
              <td>{o.payment_status ? <StatusBadge status={o.payment_status} /> : <span className="muted">—</span>}</td>
              <td>₹{Number(o.total_amount).toFixed(2)}</td>
              <td>
                {NEXT_STATUS[o.status] && (
                  <button className="btn btn-secondary btn-sm" onClick={() => advance(o)}>
                    Mark {NEXT_STATUS[o.status].replaceAll('_', ' ')}
                  </button>
                )}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
