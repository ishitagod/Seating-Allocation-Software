import axios from 'axios';

const API_BASE_URL = ''; // Relative URL since we're serving from the same domain

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add a request interceptor to add the /api prefix to all requests
api.interceptors.request.use(
  (config) => {
    // Only add /api prefix if the URL doesn't already have it and it's not an absolute URL
    if (!config.url?.startsWith('http') && !config.url?.startsWith('/api/')) {
      config.url = `/api${config.url?.startsWith('/') ? '' : '/'}${config.url || ''}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

export default api;
