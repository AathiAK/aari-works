const STYLES = {
  PENDING: 'badge-pending',
  PAYMENT_PENDING: 'badge-pending',
  CONFIRMED: 'badge-progress',
  PROCESSING: 'badge-progress',
  PACKED: 'badge-progress',
  SHIPPED: 'badge-progress',
  OUT_FOR_DELIVERY: 'badge-progress',
  DELIVERED: 'badge-success',
  SUCCESS: 'badge-success',
  CANCELLED: 'badge-neutral',
  PAYMENT_FAILED: 'badge-danger',
  FAILED: 'badge-danger',
  RETURN_REQUESTED: 'badge-danger',
  RETURNED: 'badge-neutral',
  REFUNDED: 'badge-neutral',
}

export default function StatusBadge({ status }) {
  const cls = STYLES[status] || 'badge-neutral'
  return <span className={`badge ${cls}`}>{status.replaceAll('_', ' ')}</span>
}
