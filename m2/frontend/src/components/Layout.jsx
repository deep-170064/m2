import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import '../styles/Layout.css';

function Layout({ children }) {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <div className="layout">
      <nav className="navbar">
        <div className="navbar-brand">
          <h2>🏪 SuperMarket</h2>
        </div>
        <div className="navbar-menu">
          <Link to="/dashboard">Dashboard</Link>
          <Link to="/products">Products</Link>
          <Link to="/sales">Sales</Link>
          {(user?.role === 'ADMIN' || user?.role === 'MANAGER') && (
            <Link to="/customers">Customers</Link>
          )}
          {user?.role === 'ADMIN' && (
            <Link to="/employees">Employees</Link>
          )}
        </div>
        <div className="navbar-user">
          <span>👤 {user?.name} ({user?.role})</span>
          <button className="btn-logout" onClick={handleLogout}>Logout</button>
        </div>
      </nav>
      <main className="main-content">
        {children}
      </main>
    </div>
  );
}

export default Layout;
