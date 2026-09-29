import { Link } from 'react-router-dom'

export default function ProductCard({ product }) {
  return (
    <Link to={`/products/${product.id}`} className="product-card">
      {product.image_url ? (
        <img src={product.image_url} alt={product.name} />
      ) : (
        <div className="product-image-placeholder">No image</div>
      )}
      <div className="product-card-body">
        <div className="product-card-name">{product.name}</div>
        <div className="product-card-price">₹{Number(product.price).toFixed(2)}</div>
        <div className="product-card-stock">
          {product.stock_quantity > 0 ? `${product.stock_quantity} in stock` : 'Out of stock'}
        </div>
      </div>
    </Link>
  )
}
