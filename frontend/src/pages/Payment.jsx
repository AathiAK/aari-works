/**
 * Mock payment screen. Real gateways redirect to a hosted checkout —
 * here we simply let the customer choose an outcome, matching the
 * PaymentGateway abstraction from Phase 11. This page is the one place
 * in the app that would change shape when a real provider is added.
 */

import { useEffect, useState } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { apiErrorMessage, createPayment, fetchOrder, simulatePayment } from '../services/api'
import Spinner from '../components/Spinner'

export default function Payment() {
  const { orderId } = useParams()
  const navigate = useNavigate()
  const [order, setOrder] = useState(null)
  const [payment, setPayment] = useState(null)
  const [error, setError] = useState('')
  const [processing, setProcessing] = useState(false)

  useEffect(() => {
    fetchOrder(orderId).then((res) => setOrder(res.data)).catch(() => setError('Order not found.'))
  }, [orderId])

  async function pay(outcome) {
    setError('')
    setProcessing(true)
    try {
      const res = await createPayment(Number(orderId), outcome)
      if (res.data.status === 'SUCCESS') {
        navigate(`/order-success/${orderId}`)
        return
      }
      if (res.data.status === 'PENDING') {
        setPayment(res.data)
        return
      }
      // FAILED
      setPayment(res.data)
      setError('Payment failed. You can try again below.')
    } catch (err) {
      setError(apiErrorMessage(err, 'Could not process payment.'))
    } finally {
      setProcessing(false)
    }
  }

  async function resolvePending(outcome) {
    setProcessing(true)
    try {
      const res = await simulatePayment(payment.id, outcome)
      if (res.data.status === 'SUCCESS') navigate(`/order-success/${orderId}`)
      else setPayment(res.data)
    } catch (err) {
      setError(apiErrorMessage(err))
    } finally {
      setProcessing(false)
    }
  }

  if (!order) return <Spinner />

  return (
    <div className="form-card" style={{ maxWidth: '480px' }}>
      <h2>Payment</h2>
      <p className="muted">Order {order.order_number}</p>
      <p style={{ fontFamily: 'var(--font-display)', fontSize: '1.6rem', color: 'var(--marigold-600)' }}>
        ₹{Number(order.total_amount).toFixed(2)}
      </p>

      {error && <div className="form-error">{error}</div>}

      {payment?.status === 'PENDING' ? (
        <>
          <p className="muted">Your payment is pending confirmation from the provider.</p>
          <div style={{ display: 'flex', gap: '0.75rem' }}>
            <button className="btn btn-primary" onClick={() => resolvePending('SUCCESS')} disabled={processing}>Confirm success</button>
            <button className="btn btn-danger" onClick={() => resolvePending('FAILED')} disabled={processing}>Simulate failure</button>
          </div>
        </>
      ) : (
        <>
          <p className="muted" style={{ fontSize: '0.85rem' }}>
            This is a local mock payment — no card details are collected. Choose an outcome to simulate the gateway.
          </p>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.6rem' }}>
            <button className="btn btn-primary" onClick={() => pay('SUCCESS')} disabled={processing}>Pay now (simulate success)</button>
            <button className="btn btn-secondary" onClick={() => pay('PENDING')} disabled={processing}>Simulate pending</button>
            <button className="btn btn-danger" onClick={() => pay('FAILED')} disabled={processing}>Simulate failure</button>
          </div>
        </>
      )}
    </div>
  )
}
