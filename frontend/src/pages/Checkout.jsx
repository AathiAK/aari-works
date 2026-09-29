import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import {
  apiErrorMessage, createAddress, createOrder, fetchAddresses, fetchCheckoutPreview,
} from '../services/api'
import Spinner from '../components/Spinner'

const emptyAddress = {
  full_name: '', phone: '', address_line1: '', address_line2: '',
  city: '', state: '', postal_code: '', country: 'India',
}

export default function Checkout() {
  const [addresses, setAddresses] = useState([])
  const [addressId, setAddressId] = useState('')
  const [showNewAddress, setShowNewAddress] = useState(false)
  const [newAddress, setNewAddress] = useState(emptyAddress)
  const [preview, setPreview] = useState(null)
  const [error, setError] = useState('')
  const [placing, setPlacing] = useState(false)
  const navigate = useNavigate()

  function loadAddresses() {
    fetchAddresses().then((res) => {
      setAddresses(res.data)
      if (res.data.length > 0) setAddressId(String(res.data[0].id))
      else setShowNewAddress(true)
    })
  }

  useEffect(loadAddresses, [])

  useEffect(() => {
    if (!addressId) { setPreview(null); return }
    fetchCheckoutPreview(addressId)
      .then((res) => setPreview(res.data))
      .catch((err) => setError(apiErrorMessage(err, 'Could not load checkout summary.')))
  }, [addressId])

  async function handleSaveAddress(e) {
    e.preventDefault()
    setError('')
    try {
      const res = await createAddress(newAddress)
      setAddresses((a) => [res.data, ...a])
      setAddressId(String(res.data.id))
      setShowNewAddress(false)
      setNewAddress(emptyAddress)
    } catch (err) {
      setError(apiErrorMessage(err, 'Could not save this address.'))
    }
  }

  async function handlePlaceOrder() {
    setError('')
    setPlacing(true)
    try {
      const res = await createOrder(Number(addressId))
      navigate(`/payment/${res.data.id}`)
    } catch (err) {
      setError(apiErrorMessage(err, 'Could not place your order.'))
    } finally {
      setPlacing(false)
    }
  }

  return (
    <div className="container" style={{ padding: '2rem 1.5rem' }}>
      <h2>Checkout</h2>
      {error && <div className="form-error">{error}</div>}

      <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr', gap: '2rem' }}>
        <div>
          <h3>Delivery address</h3>
          {addresses.map((a) => (
            <label key={a.id} className="form-card" style={{ display: 'block', margin: '0 0 0.8rem', maxWidth: 'none', padding: '1rem' }}>
              <input
                type="radio" name="address" value={a.id}
                checked={addressId === String(a.id)}
                onChange={(e) => setAddressId(e.target.value)}
                style={{ marginRight: '0.6rem' }}
              />
              <strong>{a.full_name}</strong> — {a.address_line1}, {a.city}, {a.state} {a.postal_code}
            </label>
          ))}

          {!showNewAddress && (
            <button className="btn btn-secondary btn-sm" onClick={() => setShowNewAddress(true)}>
              + Add a new address
            </button>
          )}

          {showNewAddress && (
            <form onSubmit={handleSaveAddress} className="form-card" style={{ maxWidth: 'none' }}>
              <div className="field-row">
                <div className="field">
                  <label>Full name</label>
                  <input required value={newAddress.full_name} onChange={(e) => setNewAddress((a) => ({ ...a, full_name: e.target.value }))} />
                </div>
                <div className="field">
                  <label>Phone</label>
                  <input required value={newAddress.phone} onChange={(e) => setNewAddress((a) => ({ ...a, phone: e.target.value }))} />
                </div>
              </div>
              <div className="field">
                <label>Address line 1</label>
                <input required value={newAddress.address_line1} onChange={(e) => setNewAddress((a) => ({ ...a, address_line1: e.target.value }))} />
              </div>
              <div className="field">
                <label>Address line 2 (optional)</label>
                <input value={newAddress.address_line2} onChange={(e) => setNewAddress((a) => ({ ...a, address_line2: e.target.value }))} />
              </div>
              <div className="field-row">
                <div className="field">
                  <label>City</label>
                  <input required value={newAddress.city} onChange={(e) => setNewAddress((a) => ({ ...a, city: e.target.value }))} />
                </div>
                <div className="field">
                  <label>State</label>
                  <input required value={newAddress.state} onChange={(e) => setNewAddress((a) => ({ ...a, state: e.target.value }))} />
                </div>
                <div className="field">
                  <label>Postal code</label>
                  <input required value={newAddress.postal_code} onChange={(e) => setNewAddress((a) => ({ ...a, postal_code: e.target.value }))} />
                </div>
              </div>
              <button type="submit" className="btn btn-primary">Save address</button>
            </form>
          )}
        </div>

        <div className="summary-box">
          {!preview ? (
            <p className="muted">Select an address to see your total.</p>
          ) : (
            <>
              <div className="summary-row"><span>Subtotal</span><span>₹{Number(preview.subtotal).toFixed(2)}</span></div>
              <div className="summary-row"><span>Shipping</span><span>{Number(preview.shipping_amount) === 0 ? 'Free' : `₹${Number(preview.shipping_amount).toFixed(2)}`}</span></div>
              <div className="summary-row"><span>Tax</span><span>₹{Number(preview.tax_amount).toFixed(2)}</span></div>
              <div className="summary-row total"><span>Total</span><span>₹{Number(preview.total_amount).toFixed(2)}</span></div>
              <button
                className="btn btn-primary btn-block"
                style={{ marginTop: '1rem' }}
                disabled={!addressId || placing}
                onClick={handlePlaceOrder}
              >
                {placing ? 'Placing order…' : 'Place order'}
              </button>
            </>
          )}
        </div>
      </div>
    </div>
  )
}
