import { useEffect, useState } from 'react'
import { fetchAdminOrders, fetchAdminUsers } from '../../services/api'
import Spinner from '../../components/Spinner'

export default function AdminDashboard() {
  const [stats, setStats] = useState(null)

  useEffect(() => {
    Promise.all([fetchAdminUsers(), fetchAdminOrders({ page_size: 100 })]).then(([usersRes, ordersRes]) => {
      const orders = ordersRes.data.items
      const revenue = orders
        .filter((o) => o.payment_status === 'SUCCESS')
        .reduce((sum, o) => sum + Number(o.total_amount), 0)
      setStats({
        customers: usersRes.data.filter((u) => u.role === 'CUSTOMER').length,
        totalOrders: ordersRes.data.total,
        pendingOrders: orders.filter((o) => ['PENDING', 'PAYMENT_PENDING'].includes(o.status)).length,
        revenue,
      })
    })
  }, [])

  if (!stats) return <Spinner />

  return (
    <div>
      <h2>Dashboard</h2>
      <div className="stat-grid">
        <div className="stat-card"><div className="stat-value">{stats.customers}</div><div className="stat-label">Customers</div></div>
        <div className="stat-card"><div className="stat-value">{stats.totalOrders}</div><div className="stat-label">Total orders</div></div>
        <div className="stat-card"><div className="stat-value">{stats.pendingOrders}</div><div className="stat-label">Pending orders</div></div>
        <div className="stat-card"><div className="stat-value">₹{stats.revenue.toFixed(0)}</div><div className="stat-label">Revenue (paid orders)</div></div>
      </div>
    </div>
  )
}
