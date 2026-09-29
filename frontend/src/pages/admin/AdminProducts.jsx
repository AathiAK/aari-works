import { useEffect, useState } from 'react'
import {
  apiErrorMessage, createCategory, createProduct, fetchCategories, fetchProducts,
  updateProduct, uploadProductImage,
} from '../../services/api'
import Spinner from '../../components/Spinner'

const emptyForm = { category_id: '', name: '', description: '', price: '', stock_quantity: '' }

export default function AdminProducts() {
  const [products, setProducts] = useState(null)
  const [categories, setCategories] = useState([])
  const [form, setForm] = useState(emptyForm)
  const [editingId, setEditingId] = useState(null)
  const [imageFile, setImageFile] = useState(null)
  const [newCategoryName, setNewCategoryName] = useState('')
  const [error, setError] = useState('')
  const [saving, setSaving] = useState(false)

  function loadProducts() {
    fetchProducts({ page_size: 100 }).then((res) => setProducts(res.data.items))
  }
  function loadCategories() {
    fetchCategories().then((res) => setCategories(res.data))
  }
  useEffect(() => { loadProducts(); loadCategories() }, [])

  function startEdit(p) {
    setEditingId(p.id)
    setForm({
      category_id: p.category_id, name: p.name, description: p.description || '',
      price: p.price, stock_quantity: p.stock_quantity,
    })
    window.scrollTo({ top: 0, behavior: 'smooth' })
  }

  function resetForm() {
    setEditingId(null)
    setForm(emptyForm)
    setImageFile(null)
  }

  async function handleSubmit(e) {
    e.preventDefault()
    setError('')
    setSaving(true)
    try {
      const payload = {
        ...form,
        category_id: Number(form.category_id),
        price: Number(form.price),
        stock_quantity: Number(form.stock_quantity),
      }
      let productId = editingId
      if (editingId) {
        await updateProduct(editingId, payload)
      } else {
        const res = await createProduct(payload)
        productId = res.data.id
      }
      if (imageFile && productId) {
        await uploadProductImage(productId, imageFile)
      }
      resetForm()
      loadProducts()
    } catch (err) {
      setError(apiErrorMessage(err, 'Could not save this product.'))
    } finally {
      setSaving(false)
    }
  }

  async function toggleActive(p) {
    await updateProduct(p.id, { is_active: !p.is_active })
    loadProducts()
  }

  async function handleAddCategory(e) {
    e.preventDefault()
    if (!newCategoryName.trim()) return
    try {
      await createCategory({ name: newCategoryName.trim() })
      setNewCategoryName('')
      loadCategories()
    } catch (err) {
      setError(apiErrorMessage(err, 'Could not create category.'))
    }
  }

  if (!products) return <Spinner />

  return (
    <div>
      <h2>Products</h2>
      {error && <div className="form-error">{error}</div>}

      <form onSubmit={handleSubmit} className="form-card" style={{ maxWidth: 'none' }}>
        <h3>{editingId ? 'Edit product' : 'Add product'}</h3>
        <div className="field-row">
          <div className="field">
            <label>Name</label>
            <input required value={form.name} onChange={(e) => setForm((f) => ({ ...f, name: e.target.value }))} />
          </div>
          <div className="field">
            <label>Category</label>
            <select required value={form.category_id} onChange={(e) => setForm((f) => ({ ...f, category_id: e.target.value }))}>
              <option value="">Select…</option>
              {categories.map((c) => <option key={c.id} value={c.id}>{c.name}</option>)}
            </select>
          </div>
        </div>
        <div className="field">
          <label>Description</label>
          <textarea rows={3} value={form.description} onChange={(e) => setForm((f) => ({ ...f, description: e.target.value }))} />
        </div>
        <div className="field-row">
          <div className="field">
            <label>Price (₹)</label>
            <input type="number" step="0.01" min="0" required value={form.price} onChange={(e) => setForm((f) => ({ ...f, price: e.target.value }))} />
          </div>
          <div className="field">
            <label>Stock quantity</label>
            <input type="number" min="0" required value={form.stock_quantity} onChange={(e) => setForm((f) => ({ ...f, stock_quantity: e.target.value }))} />
          </div>
        </div>
        <div className="field">
          <label>Product image</label>
          <input type="file" accept="image/jpeg,image/png,image/webp" onChange={(e) => setImageFile(e.target.files[0])} />
        </div>
        <div style={{ display: 'flex', gap: '0.75rem' }}>
          <button type="submit" className="btn btn-primary" disabled={saving}>
            {saving ? 'Saving…' : editingId ? 'Save changes' : 'Add product'}
          </button>
          {editingId && <button type="button" className="btn btn-secondary" onClick={resetForm}>Cancel</button>}
        </div>
      </form>

      <form onSubmit={handleAddCategory} style={{ display: 'flex', gap: '0.6rem', margin: '1rem 0 2rem' }}>
        <input
          placeholder="New category name"
          value={newCategoryName}
          onChange={(e) => setNewCategoryName(e.target.value)}
        />
        <button type="submit" className="btn btn-secondary btn-sm">Add category</button>
      </form>

      <table>
        <thead>
          <tr><th>Image</th><th>Name</th><th>Category</th><th>Price</th><th>Stock</th><th>Status</th><th></th></tr>
        </thead>
        <tbody>
          {products.map((p) => (
            <tr key={p.id}>
              <td>{p.image_url ? <img src={p.image_url} alt="" width="40" height="40" style={{ objectFit: 'cover', borderRadius: 3 }} /> : '—'}</td>
              <td>{p.name}</td>
              <td>{categories.find((c) => c.id === p.category_id)?.name || '—'}</td>
              <td>₹{Number(p.price).toFixed(2)}</td>
              <td>{p.stock_quantity}</td>
              <td>{p.is_active ? 'Active' : 'Inactive'}</td>
              <td style={{ display: 'flex', gap: '0.5rem' }}>
                <button className="btn btn-secondary btn-sm" onClick={() => startEdit(p)}>Edit</button>
                <button className="btn btn-danger btn-sm" onClick={() => toggleActive(p)}>
                  {p.is_active ? 'Deactivate' : 'Activate'}
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
