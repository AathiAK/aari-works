import { useState } from 'react'
import { Link, useLocation, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import { apiErrorMessage } from '../services/api'

export default function Login() {
  const { login, isAdmin } = useAuth()
  const navigate = useNavigate()
  const location = useLocation()
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [submitting, setSubmitting] = useState(false)

  async function handleSubmit(e) {
    e.preventDefault()
    setError('')
    setSubmitting(true)
    try {
      const me = await login(email, password)
      const redirectTo = location.state?.from?.pathname
      navigate(redirectTo || (me.role === 'ADMIN' ? '/admin' : '/products'), { replace: true })
    } catch (err) {
      setError(apiErrorMessage(err, 'Incorrect email or password.'))
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <div className="form-card">
      <h2>Log in</h2>
      {error && <div className="form-error">{error}</div>}
      <form onSubmit={handleSubmit}>
        <div className="field">
          <label htmlFor="email">Email</label>
          <input id="email" type="email" required value={email} onChange={(e) => setEmail(e.target.value)} />
        </div>
        <div className="field">
          <label htmlFor="password">Password</label>
          <input id="password" type="password" required value={password} onChange={(e) => setPassword(e.target.value)} />
        </div>
        <button type="submit" className="btn btn-primary btn-block" disabled={submitting}>
          {submitting ? 'Logging in…' : 'Log in'}
        </button>
      </form>
      <p className="muted" style={{ marginTop: '1rem', fontSize: '0.88rem' }}>
        New here? <Link to="/register">Create an account</Link>
      </p>
    </div>
  )
}
