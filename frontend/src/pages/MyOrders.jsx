import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { fetchMyOrders } from '../services/api'
import StatusBadge from '../components/StatusBadge'
import Spinner from '../components/Spinner'

export default function MyOrders() {
  const [orders, setOrders] = useState(null)

  useEffect(() => {
    fetchMyOrders().then((res) => setOrders(res.data.items))
  }, [])

  if (!orders) return <Spinner />

  return (
    <div className="container" style={{ padding: '2rem 1.5rem' }}>
      <h2>My orders</h2>
      {orders.length === 0 ? (
        <div className="empty-state">
          You haven't placed any orders yet. <Link to="/products">Browse products</Link>
        </div>
      ) : (
        <table>
          <thead>
            <tr><th>Order</th><th>Date</th><th>Status</th><th>Total</th><th></th></tr>
          </thead>
          <tbody>
            {orders.map((o) => (
              <tr key={o.id}>
                <td>{o.order_number}</td>
                <td>{new Date(o.created_at).toLocaleDateString()}</td>
                <td><StatusBadge status={o.status} /></td>
                <td>₹{Number(o.total_amount).toFixed(2)}</td>
                <td><Link to={`/my-orders/${o.id}`}>View</Link></td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  )
}
