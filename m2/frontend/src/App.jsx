import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './context/AuthContext';
import Layout from './components/Layout';
import Login from './pages/Login';
import Dashboard from './pages/Dashboard';
import Products from './pages/Products';
import Sales from './pages/Sales';
import Customers from './pages/Customers';
import Employees from './pages/Employees';
import './App.css';

function PrivateRoute({ children }) {
  const { user, loading } = useAuth();
  
  if (loading) {
    return <div className="loading">Loading...</div>;
  }
  
  return user ? children : <Navigate to="/login" />;
}

function AppRoutes() {
  const { user } = useAuth();
  
  return (
    <Routes>
      <Route path="/login" element={user ? <Navigate to="/dashboard" /> : <Login />} />
      <Route
        path="/dashboard"
        element={
          <PrivateRoute>
            <Layout><Dashboard /></Layout>
          </PrivateRoute>
        }
      />
      <Route
        path="/products"
        element={
          <PrivateRoute>
            <Layout><Products /></Layout>
          </PrivateRoute>
        }
      />
      <Route
        path="/sales"
        element={
          <PrivateRoute>
            <Layout><Sales /></Layout>
          </PrivateRoute>
        }
      />
      <Route
        path="/customers"
        element={
          <PrivateRoute>
            <Layout><Customers /></Layout>
          </PrivateRoute>
        }
      />
      <Route
        path="/employees"
        element={
          <PrivateRoute>
            <Layout><Employees /></Layout>
          </PrivateRoute>
        }
      />
      <Route path="/" element={<Navigate to="/dashboard" />} />
    </Routes>
  );
}

function App() {
  return (
    <AuthProvider>
      <Router>
        <AppRoutes />
      </Router>
    </AuthProvider>
  );
}

export default App;
