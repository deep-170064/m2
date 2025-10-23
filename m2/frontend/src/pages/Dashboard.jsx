import { useState, useEffect } from 'react';
import { dashboard } from '../services/api';
import '../styles/Dashboard.css';

function Dashboard() {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadStats();
  }, []);

  const loadStats = async () => {
    try {
      const response = await dashboard.getStats();
      setStats(response.data);
    } catch (error) {
      console.error('Failed to load stats:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <div className="loading">Loading dashboard...</div>;
  }

  return (
    <div className="dashboard">
      <h1>📊 Dashboard</h1>
      
      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-icon">📦</div>
          <div className="stat-info">
            <h3>Total Products</h3>
            <p className="stat-value">{stats?.total_products || 0}</p>
          </div>
        </div>
        
        <div className="stat-card">
          <div className="stat-icon">💰</div>
          <div className="stat-info">
            <h3>Total Sales</h3>
            <p className="stat-value">{stats?.total_sales || 0}</p>
          </div>
        </div>
        
        <div className="stat-card">
          <div className="stat-icon">💵</div>
          <div className="stat-info">
            <h3>Total Revenue</h3>
            <p className="stat-value">₹{stats?.total_revenue?.toFixed(2) || '0.00'}</p>
          </div>
        </div>
        
        <div className="stat-card warning">
          <div className="stat-icon">⚠️</div>
          <div className="stat-info">
            <h3>Low Stock Items</h3>
            <p className="stat-value">{stats?.low_stock_count || 0}</p>
          </div>
        </div>
        
        <div className="stat-card">
          <div className="stat-icon">📅</div>
          <div className="stat-info">
            <h3>Today's Sales</h3>
            <p className="stat-value">₹{stats?.today_sales?.toFixed(2) || '0.00'}</p>
          </div>
        </div>
      </div>
    </div>
  );
}

export default Dashboard;
