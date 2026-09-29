import { useEffect, useState } from 'react'
import { fetchCategories, fetchProducts } from '../services/api'
import ProductCard from '../components/ProductCard'
import Spinner from '../components/Spinner'

export default function Products() {
  const [products, setProducts] = useState([])
  const [categories, setCategories] = useState([])
  const [search, setSearch] = useState('')
  const [categoryId, setCategoryId] = useState('')
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchCategories().then((res) => setCategories(res.data)).catch(() => {})
  }, [])

  useEffect(() => {
    setLoading(true)
    const params = {}
    if (search) params.search = search
    if (categoryId) params.category_id = categoryId
    const timeout = setTimeout(() => {
      fetchProducts(params)
        .then((res) => setProducts(res.data.items))
        .finally(() => setLoading(false))
    }, 300) // debounce search typing
    return () => clearTimeout(timeout)
  }, [search, categoryId])

  return (
    <div className="container" style={{ padding: '2rem 1.5rem' }}>
      <div className="page-header">
        <h2>Products</h2>
      </div>
      <div className="filters-bar">
        <input
          placeholder="Search products…"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          style={{ minWidth: '220px' }}
        />
        <select value={categoryId} onChange={(e) => setCategoryId(e.target.value)}>
          <option value="">All categories</option>
          {categories.map((c) => (
            <option key={c.id} value={c.id}>{c.name}</option>
          ))}
        </select>
      </div>

      {loading ? (
        <Spinner />
      ) : products.length === 0 ? (
        <div className="empty-state">No products match your search.</div>
      ) : (
        <div className="product-grid">
          {products.map((p) => <ProductCard key={p.id} product={p} />)}
        </div>
      )}
    </div>
  )
}
