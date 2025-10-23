import { useState, useEffect } from 'react';
import { products, categories, suppliers } from '../services/api';
import { useAuth } from '../context/AuthContext';
import '../styles/Products.css';

function Products() {
  const { user } = useAuth();
  const [productList, setProductList] = useState([]);
  const [categoryList, setCategoryList] = useState([]);
  const [supplierList, setSupplierList] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showAddForm, setShowAddForm] = useState(false);
  const [showRestockForm, setShowRestockForm] = useState(false);
  const [selectedProduct, setSelectedProduct] = useState(null);
  const [newProduct, setNewProduct] = useState({
    name: '',
    barcode: '',
    price: '',
    stock_quantity: '',
    category_id: '',
    supplier_id: '',
    low_stock_threshold: 10,
  });
  const [restockQuantity, setRestockQuantity] = useState('');

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const [productsRes, categoriesRes, suppliersRes] = await Promise.all([
        products.getAll(),
        categories.getAll(),
        suppliers.getAll(),
      ]);
      setProductList(productsRes.data.products);
      setCategoryList(categoriesRes.data.categories);
      setSupplierList(suppliersRes.data.suppliers);
    } catch (error) {
      console.error('Failed to load data:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleAddProduct = async (e) => {
    e.preventDefault();
    try {
      await products.add({
        ...newProduct,
        price: parseFloat(newProduct.price),
        stock_quantity: parseInt(newProduct.stock_quantity),
        category_id: parseInt(newProduct.category_id),
        supplier_id: parseInt(newProduct.supplier_id),
        low_stock_threshold: parseInt(newProduct.low_stock_threshold),
      });
      alert('Product added successfully!');
      setShowAddForm(false);
      setNewProduct({
        name: '',
        barcode: '',
        price: '',
        stock_quantity: '',
        category_id: '',
        supplier_id: '',
        low_stock_threshold: 10,
      });
      loadData();
    } catch (error) {
      alert('Failed to add product: ' + (error.response?.data?.detail || error.message));
    }
  };

  const handleRestock = async (e) => {
    e.preventDefault();
    try {
      await products.updateStock(selectedProduct.product_id, parseInt(restockQuantity));
      alert('Stock updated successfully!');
      setShowRestockForm(false);
      setSelectedProduct(null);
      setRestockQuantity('');
      loadData();
    } catch (error) {
      alert('Failed to update stock: ' + (error.response?.data?.detail || error.message));
    }
  };

  if (loading) {
    return <div className="loading">Loading products...</div>;
  }

  return (
    <div className="products-page">
      <div className="page-header">
        <h1>📦 Products</h1>
        {user?.role === 'ADMIN' && (
          <button className="btn-primary" onClick={() => setShowAddForm(true)}>
            + Add Product
          </button>
        )}
      </div>

      <div className="products-table-container">
        <table className="products-table">
          <thead>
            <tr>
              <th>ID</th>
              <th>Name</th>
              <th>Barcode</th>
              <th>Price</th>
              <th>Stock</th>
              <th>Threshold</th>
              <th>Category</th>
              <th>Supplier</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {productList.map((product) => (
              <tr key={product.product_id} className={product.stock_quantity <= product.low_stock_threshold ? 'low-stock' : ''}>
                <td>{product.product_id}</td>
                <td>{product.name}</td>
                <td>{product.barcode || '-'}</td>
                <td>₹{product.price.toFixed(2)}</td>
                <td>{product.stock_quantity}</td>
                <td>{product.low_stock_threshold}</td>
                <td>{product.category}</td>
                <td>{product.supplier}</td>
                <td>
                  {(user?.role === 'ADMIN' || user?.role === 'MANAGER') && (
                    <button 
                      className="btn-small"
                      onClick={() => {
                        setSelectedProduct(product);
                        setShowRestockForm(true);
                      }}
                    >
                      Restock
                    </button>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {showAddForm && (
        <div className="modal">
          <div className="modal-content">
            <h2>Add New Product</h2>
            <form onSubmit={handleAddProduct}>
              <div className="form-group">
                <label>Product Name *</label>
                <input
                  type="text"
                  value={newProduct.name}
                  onChange={(e) => setNewProduct({ ...newProduct, name: e.target.value })}
                  required
                />
              </div>
              
              <div className="form-group">
                <label>Barcode</label>
                <input
                  type="text"
                  value={newProduct.barcode}
                  onChange={(e) => setNewProduct({ ...newProduct, barcode: e.target.value })}
                />
              </div>
              
              <div className="form-row">
                <div className="form-group">
                  <label>Price *</label>
                  <input
                    type="number"
                    step="0.01"
                    value={newProduct.price}
                    onChange={(e) => setNewProduct({ ...newProduct, price: e.target.value })}
                    required
                  />
                </div>
                
                <div className="form-group">
                  <label>Stock Quantity *</label>
                  <input
                    type="number"
                    value={newProduct.stock_quantity}
                    onChange={(e) => setNewProduct({ ...newProduct, stock_quantity: e.target.value })}
                    required
                  />
                </div>
              </div>
              
              <div className="form-row">
                <div className="form-group">
                  <label>Category *</label>
                  <select
                    value={newProduct.category_id}
                    onChange={(e) => setNewProduct({ ...newProduct, category_id: e.target.value })}
                    required
                  >
                    <option value="">Select Category</option>
                    {categoryList.map((cat) => (
                      <option key={cat.category_id} value={cat.category_id}>
                        {cat.name}
                      </option>
                    ))}
                  </select>
                </div>
                
                <div className="form-group">
                  <label>Supplier *</label>
                  <select
                    value={newProduct.supplier_id}
                    onChange={(e) => setNewProduct({ ...newProduct, supplier_id: e.target.value })}
                    required
                  >
                    <option value="">Select Supplier</option>
                    {supplierList.map((sup) => (
                      <option key={sup.supplier_id} value={sup.supplier_id}>
                        {sup.name}
                      </option>
                    ))}
                  </select>
                </div>
              </div>
              
              <div className="form-group">
                <label>Low Stock Threshold</label>
                <input
                  type="number"
                  value={newProduct.low_stock_threshold}
                  onChange={(e) => setNewProduct({ ...newProduct, low_stock_threshold: e.target.value })}
                />
              </div>
              
              <div className="modal-actions">
                <button type="submit" className="btn-primary">Add Product</button>
                <button type="button" className="btn-secondary" onClick={() => setShowAddForm(false)}>
                  Cancel
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {showRestockForm && selectedProduct && (
        <div className="modal">
          <div className="modal-content">
            <h2>Restock Product</h2>
            <p><strong>{selectedProduct.name}</strong></p>
            <p>Current Stock: {selectedProduct.stock_quantity}</p>
            <form onSubmit={handleRestock}>
              <div className="form-group">
                <label>Add Quantity</label>
                <input
                  type="number"
                  value={restockQuantity}
                  onChange={(e) => setRestockQuantity(e.target.value)}
                  required
                  min="1"
                />
              </div>
              <div className="modal-actions">
                <button type="submit" className="btn-primary">Update Stock</button>
                <button type="button" className="btn-secondary" onClick={() => setShowRestockForm(false)}>
                  Cancel
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}

export default Products;
