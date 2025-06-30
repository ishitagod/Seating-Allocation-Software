// import axios from 'axios';

// const API_BASE_URL = ''; // Relative URL since we're serving from the same domain

// const api = axios.create({
//   baseURL: API_BASE_URL,
//   timeout: 300000,
//   headers: {
//     'Content-Type': 'application/json',
//   },
// });

// // Add a request interceptor to add the /api prefix to all requests
// api.interceptors.request.use(
//   (config) => {
//     // Only add /api prefix if the URL doesn't already have it and it's not an absolute URL
//     if (!config.url?.startsWith('http') && !config.url?.startsWith('/api/')) {
//       config.url = `/api${config.url?.startsWith('/') ? '' : '/'}${config.url || ''}`;
//     }
//     return config;
//   },
//   (error) => {
//     return Promise.reject(error);
//   }
// );

// export default api;
import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000';
const api = axios.create({
  baseURL: API_BASE_URL, // This assumes your backend is served under /api
  timeout: 3000000, 
});

// Add a request interceptor to handle errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response) {
      // The request was made and the server responded with a status code
      // that falls out of the range of 2xx
      console.error('Response error:', error.response.status, error.response.data);
    } else if (error.request) {
      // The request was made but no response was received
      console.error('No response received:', error.request);
    } else {
      // Something happened in setting up the request that triggered an Error
      console.error('Error:', error.message);
    }
    return Promise.reject(error);
  }
);

export default api;