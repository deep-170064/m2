import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { auth } from '../services/api';
import '../styles/Login.css';

function Login() {
  const [credentials, setCredentials] = useState({ username: '', password: '' });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const { login } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      const response = await auth.login(credentials);
      login(response.data);
      navigate('/dashboard');
    } catch (err) {
      setError(err.response?.data?.detail || 'Login failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const quickLogin = (username, password) => {
    setCredentials({ username, password });
  };

  return (
    <div className="login-container">
      <div className="login-box">
        <h1>🏪 SuperMarket Management</h1>
        <h2>Login</h2>
        
        {error && <div className="error-message">{error}</div>}
        
        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label>Username</label>
            <input
              type="text"
              value={credentials.username}
              onChange={(e) => setCredentials({ ...credentials, username: e.target.value })}
              required
              placeholder="Enter username"
            />
          </div>
          
          <div className="form-group">
            <label>Password</label>
            <input
              type="password"
              value={credentials.password}
              onChange={(e) => setCredentials({ ...credentials, password: e.target.value })}
              required
              placeholder="Enter password"
            />
          </div>
          
          <button type="submit" className="btn-primary" disabled={loading}>
            {loading ? 'Logging in...' : 'Login'}
          </button>
        </form>
        
        <div className="demo-credentials">
          <h3>Demo Credentials</h3>
          <div className="demo-buttons">
            <button onClick={() => quickLogin('alicej', 'admin123')} className="btn-demo">
              Admin: alicej
            </button>
            <button onClick={() => quickLogin('carold', 'manager123')} className="btn-demo">
              Manager: carold
            </button>
            <button onClick={() => quickLogin('emma', 'cashier123')} className="btn-demo">
              Cashier: emma
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

export default Login;
