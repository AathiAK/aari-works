import { useEffect, useState } from 'react'
import { fetchAdminUsers } from '../../services/api'
import Spinner from '../../components/Spinner'

export default function AdminCustomers() {
  const [users, setUsers] = useState(null)

  useEffect(() => {
    fetchAdminUsers().then((res) => setUsers(res.data))
  }, [])

  if (!users) return <Spinner />

  return (
    <div>
      <h2>Customers</h2>
      <table>
        <thead>
          <tr><th>Name</th><th>Email</th><th>Phone</th><th>Role</th><th>Joined</th></tr>
        </thead>
        <tbody>
          {users.map((u) => (
            <tr key={u.id}>
              <td>{u.name}</td>
              <td>{u.email}</td>
              <td>{u.phone || '—'}</td>
              <td>{u.role}</td>
              <td>{new Date(u.created_at).toLocaleDateString()}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
