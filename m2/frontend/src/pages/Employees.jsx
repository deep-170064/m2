import { useState, useEffect } from 'react';
import { employees } from '../services/api';
import '../styles/Employees.css';

function Employees() {
  const [employeeList, setEmployeeList] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showAddForm, setShowAddForm] = useState(false);
  const [newEmployee, setNewEmployee] = useState({
    name: '',
    role: 'CASHIER',
    username: '',
    password: '',
  });

  useEffect(() => {
    loadEmployees();
  }, []);

  const loadEmployees = async () => {
    try {
      const response = await employees.getAll();
      setEmployeeList(response.data.employees);
    } catch (error) {
      console.error('Failed to load employees:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleAddEmployee = async (e) => {
    e.preventDefault();
    try {
      await employees.add(newEmployee);
      alert('Employee added successfully!');
      setShowAddForm(false);
      setNewEmployee({ name: '', role: 'CASHIER', username: '', password: '' });
      loadEmployees();
    } catch (error) {
      alert('Failed to add employee: ' + (error.response?.data?.detail || error.message));
    }
  };

  if (loading) {
    return <div className="loading">Loading employees...</div>;
  }

  return (
    <div className="employees-page">
      <div className="page-header">
        <h1>👥 Employees</h1>
        <button className="btn-primary" onClick={() => setShowAddForm(true)}>
          + Add Employee
        </button>
      </div>

      <div className="employees-table-container">
        <table className="employees-table">
          <thead>
            <tr>
              <th>ID</th>
              <th>Name</th>
              <th>Role</th>
              <th>Username</th>
            </tr>
          </thead>
          <tbody>
            {employeeList.map((employee) => (
              <tr key={employee.employee_id}>
                <td>{employee.employee_id}</td>
                <td>{employee.name}</td>
                <td>
                  <span className={`role-badge ${employee.role.toLowerCase()}`}>
                    {employee.role}
                  </span>
                </td>
                <td>{employee.username}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {showAddForm && (
        <div className="modal">
          <div className="modal-content">
            <h2>Add New Employee</h2>
            <form onSubmit={handleAddEmployee}>
              <div className="form-group">
                <label>Name *</label>
                <input
                  type="text"
                  value={newEmployee.name}
                  onChange={(e) => setNewEmployee({ ...newEmployee, name: e.target.value })}
                  required
                />
              </div>
              <div className="form-group">
                <label>Role *</label>
                <select
                  value={newEmployee.role}
                  onChange={(e) => setNewEmployee({ ...newEmployee, role: e.target.value })}
                  required
                >
                  <option value="CASHIER">Cashier</option>
                  <option value="MANAGER">Manager</option>
                  <option value="ADMIN">Admin</option>
                </select>
              </div>
              <div className="form-group">
                <label>Username *</label>
                <input
                  type="text"
                  value={newEmployee.username}
                  onChange={(e) => setNewEmployee({ ...newEmployee, username: e.target.value })}
                  required
                />
              </div>
              <div className="form-group">
                <label>Password *</label>
                <input
                  type="password"
                  value={newEmployee.password}
                  onChange={(e) => setNewEmployee({ ...newEmployee, password: e.target.value })}
                  required
                />
              </div>
              <div className="modal-actions">
                <button type="submit" className="btn-primary">Add Employee</button>
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

export default Employees;
