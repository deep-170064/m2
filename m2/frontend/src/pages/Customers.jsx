import { useState, useEffect } from 'react';
import { customers } from '../services/api';
import '../styles/Customers.css';

function Customers() {
  const [customerList, setCustomerList] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showAddForm, setShowAddForm] = useState(false);
  const [newCustomer, setNewCustomer] = useState({
    name: '',
    phone: '',
    email: '',
  });

  useEffect(() => {
    loadCustomers();
  }, []);

  const loadCustomers = async () => {
    try {
      const response = await customers.getAll();
      setCustomerList(response.data.customers);
    } catch (error) {
      console.error('Failed to load customers:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleAddCustomer = async (e) => {
    e.preventDefault();
    try {
      await customers.add(newCustomer);
      alert('Customer added successfully!');
      setShowAddForm(false);
      setNewCustomer({ name: '', phone: '', email: '' });
      loadCustomers();
    } catch (error) {
      alert('Failed to add customer: ' + (error.response?.data?.detail || error.message));
    }
  };

  if (loading) {
    return <div className="loading">Loading customers...</div>;
  }

  return (
    <div className="customers-page">
      <div className="page-header">
        <h1>👥 Customers</h1>
        <button className="btn-primary" onClick={() => setShowAddForm(true)}>
          + Add Customer
        </button>
      </div>

      <div className="customers-table-container">
        <table className="customers-table">
          <thead>
            <tr>
              <th>ID</th>
              <th>Name</th>
              <th>Phone</th>
              <th>Email</th>
            </tr>
          </thead>
          <tbody>
            {customerList.map((customer) => (
              <tr key={customer.customer_id}>
                <td>{customer.customer_id}</td>
                <td>{customer.name}</td>
                <td>{customer.phone || '-'}</td>
                <td>{customer.email || '-'}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {showAddForm && (
        <div className="modal">
          <div className="modal-content">
            <h2>Add New Customer</h2>
            <form onSubmit={handleAddCustomer}>
              <div className="form-group">
                <label>Name *</label>
                <input
                  type="text"
                  value={newCustomer.name}
                  onChange={(e) => setNewCustomer({ ...newCustomer, name: e.target.value })}
                  required
                />
              </div>
              <div className="form-group">
                <label>Phone</label>
                <input
                  type="tel"
                  value={newCustomer.phone}
                  onChange={(e) => setNewCustomer({ ...newCustomer, phone: e.target.value })}
                />
              </div>
              <div className="form-group">
                <label>Email</label>
                <input
                  type="email"
                  value={newCustomer.email}
                  onChange={(e) => setNewCustomer({ ...newCustomer, email: e.target.value })}
                />
              </div>
              <div className="modal-actions">
                <button type="submit" className="btn-primary">Add Customer</button>
                <button type="button" className="btn-secondary" onClick={() => setShowAddForm(false)}>
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

export default Customers;
