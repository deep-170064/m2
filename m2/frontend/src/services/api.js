import axios from 'axios';

const API_URL = 'http://localhost:8000/api';

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const auth = {
  login: (credentials) => api.post('/auth/login', credentials),
};

export const products = {
  getAll: () => api.get('/products'),
  add: (product) => api.post('/products', product),
  updateStock: (productId, quantity) => 
    api.put(`/products/${productId}/stock`, { product_id: productId, quantity }),
};

export const categories = {
  getAll: () => api.get('/categories'),
};

export const suppliers = {
  getAll: () => api.get('/suppliers'),
};

export const sales = {
  getAll: (limit = 50) => api.get(`/sales?limit=${limit}`),
  getDetails: (saleId) => api.get(`/sales/${saleId}`),
  create: (sale) => api.post('/sales', sale),
};

export const customers = {
  getAll: () => api.get('/customers'),
  add: (customer) => api.post('/customers', customer),
};

export const employees = {
  getAll: () => api.get('/employees'),
  add: (employee) => api.post('/employees', employee),
};

export const dashboard = {
  getStats: () => api.get('/dashboard/stats'),
};

export const reports = {
  getSalesByDate: (days = 7) => api.get(`/reports/sales-by-date?days=${days}`),
};

export const notifications = {
  getAll: () => api.get('/notifications'),
};

export default api;
