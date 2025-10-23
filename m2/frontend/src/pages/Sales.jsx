import { useState, useEffect } from 'react';
import { sales, products, customers } from '../services/api';
import { useAuth } from '../context/AuthContext';
import '../styles/Sales.css';

function Sales() {
  const { user } = useAuth();
  const [salesList, setSalesList] = useState([]);
  const [productList, setProductList] = useState([]);
  const [customerList, setCustomerList] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showNewSaleForm, setShowNewSaleForm] = useState(false);
  const [cart, setCart] = useState([]);
  const [selectedCustomer, setSelectedCustomer] = useState('');
  const [paymentMethod, setPaymentMethod] = useState('CASH');

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const [salesRes, productsRes, customersRes] = await Promise.all([
        sales.getAll(),
        products.getAll(),
        customers.getAll(),
      ]);
      setSalesList(salesRes.data.sales);
      setProductList(productsRes.data.products);
      setCustomerList(customersRes.data.customers);
    } catch (error) {
      console.error('Failed to load data:', error);
    } finally {
      setLoading(false);
    }
  };

  const addToCart = (product) => {
    const existingItem = cart.find(item => item.product_id === product.product_id);
    if (existingItem) {
      setCart(cart.map(item =>
        item.product_id === product.product_id
          ? { ...item, quantity: item.quantity + 1 }
          : item
      ));
    } else {
      setCart([...cart, { ...product, quantity: 1 }]);
    }
  };

  const updateQuantity = (productId, newQuantity) => {
    if (newQuantity <= 0) {
      setCart(cart.filter(item => item.product_id !== productId));
    } else {
      setCart(cart.map(item =>
        item.product_id === productId
          ? { ...item, quantity: newQuantity }
          : item
      ));
    }
  };

  const calculateTotal = () => {
    return cart.reduce((total, item) => total + (item.price * item.quantity), 0);
  };

  const handleProcessSale = async (e) => {
    e.preventDefault();
    if (cart.length === 0) {
      alert('Cart is empty!');
      return;
    }

    try {
      const saleData = {
        items: cart.map(item => ({
          product_id: item.product_id,
          quantity: item.quantity,
        })),
        payment_method: paymentMethod,
        customer_id: selectedCustomer ? parseInt(selectedCustomer) : null,
        employee_id: user.employee_id,
      };

      await sales.create(saleData);
      alert('Sale completed successfully!');
      setCart([]);
      setSelectedCustomer('');
      setPaymentMethod('CASH');
      setShowNewSaleForm(false);
      loadData();
    } catch (error) {
      alert('Failed to process sale: ' + (error.response?.data?.detail || error.message));
    }
  };

  if (loading) {
    return <div className="loading">Loading sales...</div>;
  }

  return (
    <div className="sales-page">
      <div className="page-header">
        <h1>💰 Sales</h1>
        {(user?.role === 'ADMIN' || user?.role === 'MANAGER' || user?.role === 'CASHIER') && (
          <button className="btn-primary" onClick={() => setShowNewSaleForm(true)}>
            + New Sale
          </button>
        )}
      </div>

      <div className="sales-table-container">
        <table className="sales-table">
          <thead>
            <tr>
              <th>Sale ID</th>
              <th>Date & Time</th>
              <th>Total Amount</th>
              <th>Payment Method</th>
              <th>Customer</th>
              <th>Employee</th>
            </tr>
          </thead>
          <tbody>
            {salesList.map((sale) => (
              <tr key={sale.sale_id}>
                <td>{sale.sale_id}</td>
                <td>{new Date(sale.sale_time).toLocaleString()}</td>
                <td>₹{sale.total_amount.toFixed(2)}</td>
                <td>{sale.payment_method}</td>
                <td>{sale.customer || 'Walk-in'}</td>
                <td>{sale.employee}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {showNewSaleForm && (
        <div className="modal large">
          <div className="modal-content">
            <h2>New Sale</h2>
            
            <div className="sale-form-container">
              <div className="products-section">
                <h3>Select Products</h3>
                <div className="product-grid">
                  {productList.map((product) => (
                    <div key={product.product_id} className="product-card">
                      <h4>{product.name}</h4>
                      <p>₹{product.price.toFixed(2)}</p>
                      <p>Stock: {product.stock_quantity}</p>
                      <button
                        className="btn-small"
                        onClick={() => addToCart(product)}
                        disabled={product.stock_quantity === 0}
                      >
                        Add to Cart
                      </button>
                    </div>
                  ))}
                </div>
              </div>

              <div className="cart-section">
                <h3>Cart</h3>
                {cart.length === 0 ? (
                  <p>Cart is empty</p>
                ) : (
                  <>
                    <div className="cart-items">
                      {cart.map((item) => (
                        <div key={item.product_id} className="cart-item">
                          <div>
                            <strong>{item.name}</strong>
                            <p>₹{item.price.toFixed(2)} each</p>
                          </div>
                          <div className="quantity-controls">
                            <button onClick={() => updateQuantity(item.product_id, item.quantity - 1)}>-</button>
                            <span>{item.quantity}</span>
                            <button onClick={() => updateQuantity(item.product_id, item.quantity + 1)}>+</button>
                          </div>
                          <div>
                            <strong>₹{(item.price * item.quantity).toFixed(2)}</strong>
                          </div>
                        </div>
                      ))}
                    </div>

                    <div className="cart-total">
                      <h3>Total: ₹{calculateTotal().toFixed(2)}</h3>
                    </div>

                    <form onSubmit={handleProcessSale}>
                      <div className="form-group">
                        <label>Payment Method</label>
                        <select
                          value={paymentMethod}
                          onChange={(e) => setPaymentMethod(e.target.value)}
                          required
                        >
                          <option value="CASH">Cash</option>
                          <option value="CARD">Card</option>
                          <option value="UPI">UPI</option>
                          <option value="WALLET">Wallet</option>
                        </select>
                      </div>

                      <div className="form-group">
                        <label>Customer (Optional)</label>
                        <select
                          value={selectedCustomer}
                          onChange={(e) => setSelectedCustomer(e.target.value)}
                        >
                          <option value="">Walk-in Customer</option>
                          {customerList.map((customer) => (
                            <option key={customer.customer_id} value={customer.customer_id}>
                              {customer.name}
                            </option>
                          ))}
                        </select>
                      </div>

                      <div className="modal-actions">
                        <button type="submit" className="btn-primary">
                          Complete Sale
                        </button>
                        <button
                          type="button"
                          className="btn-secondary"
                          onClick={() => {
                            setShowNewSaleForm(false);
                            setCart([]);
                          }}
                        >
                          Cancel
                        </button>
                      </div>
                    </form>
                  </>
                )}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default Sales;
