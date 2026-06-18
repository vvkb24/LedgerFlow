import axios from 'axios';

// Create an Axios instance that points to our FastAPI backend
const api = axios.create({
  baseURL: 'http://localhost:8000',
});

// Axios Interceptor: This acts like a bouncer for OUTGOING requests.
// Right before a request leaves the React app, it checks if we have a JWT token.
// If we do, it securely attaches it to the headers.
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// We also add a response interceptor to handle 401 Unauthorized errors gracefully.
// If the backend says our token is expired, we automatically log the user out!
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response && error.response.status === 401) {
      localStorage.removeItem('token');
      // Redirect to login if needed, or let components handle it
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export default api;
