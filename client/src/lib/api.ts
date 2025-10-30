import axios from 'axios';

// Use relative URLs in production (Nginx will proxy to backend)
// Use localhost in development
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 
  (import.meta.env.DEV ? 'http://127.0.0.1:8000' : '');

export const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export default api;
