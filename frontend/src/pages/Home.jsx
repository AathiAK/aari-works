import { Link } from 'react-router-dom'

export default function Home() {
  return (
    <div className="container" style={{ padding: '4rem 1.5rem' }}>
      <h1 style={{ fontSize: '2.6rem', maxWidth: '600px' }}>
        Hand-stitched Aari embroidery, made to order.
      </h1>
      <p className="muted" style={{ maxWidth: '520px', fontSize: '1.05rem', marginBottom: '2rem' }}>
        Bridal blouses, sarees, and custom pieces — each one worked by hand,
        thread by thread.
      </p>
      <Link to="/products" className="btn btn-primary">Browse products</Link>
      <hr className="stitch-divider" />
    </div>
  )
}
